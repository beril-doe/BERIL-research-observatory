"""Tests for conservative project resolution and atomic runtime sessions."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path

import pytest

from beril_cli import audit_cmd
from beril_cli.audit_cmd import (
    record_session_cost,
    resolve_project,
    run_runtime_snapshot,
)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    # The CLI falls back to these env vars; clear them so a live Claude Code
    # session running the suite can't leak effort / session id into fixtures.
    monkeypatch.delenv("CLAUDE_EFFORT", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    (tmp_path / "PROJECT.md").write_text("# marker\n")
    for name in ("p1", "p2"):
        project = tmp_path / "projects" / name
        project.mkdir(parents=True)
        (project / "beril.yaml").write_text(f"project_id: {name}\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _stdin(monkeypatch, payload):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))


def _snap(repo, monkeypatch, session_id="s1", **extra):
    payload = {
        "session_id": session_id,
        "cwd": str(repo / "projects" / "p1"),
        **extra,
    }
    _stdin(monkeypatch, payload)
    assert run_runtime_snapshot(argparse.Namespace()) == 0
    return json.loads((repo / "projects" / "p1" / "runtime.json").read_text())


def test_explicit_binding_has_highest_precedence(repo):
    payload = {
        "project_id": "p1",
        "transcript_path": str(repo / "projects" / "p2" / "session.jsonl"),
        "cwd": str(repo / "projects" / "p2"),
    }
    assert resolve_project(payload, repo_root=repo, branch="projects/p2") == "p1"


def test_nested_session_binding_is_supported(repo):
    assert (
        resolve_project(
            {"session": {"project_id": "p2"}, "cwd": str(repo)},
            repo_root=repo,
            branch="unknown",
        )
        == "p2"
    )


def test_payload_project_path_precedes_cwd(repo):
    payload = {
        "transcript_path": str(repo / "projects" / "p1" / "session.jsonl"),
        "cwd": str(repo / "projects" / "p2"),
    }
    assert resolve_project(payload, repo_root=repo, branch="projects/p2") == "p1"


def test_ambiguous_payload_paths_return_no_project(repo):
    payload = {
        "transcript_path": str(repo / "projects" / "p1" / "session.jsonl"),
        "other_path": str(repo / "projects" / "p2" / "notes.md"),
        "cwd": str(repo / "projects" / "p1"),
    }
    assert resolve_project(payload, repo_root=repo, branch="projects/p1") is None


def test_cwd_inside_project_precedes_branch(repo):
    payload = {"cwd": str(repo / "projects" / "p2")}
    assert resolve_project(payload, repo_root=repo, branch="projects/p1") == "p2"


def test_repository_root_startup_resolves_exact_project_branch(repo):
    assert (
        resolve_project({"cwd": str(repo)}, repo_root=repo, branch="projects/p1")
        == "p1"
    )


def test_repository_root_startup_resolves_unique_manifest_branch(repo):
    (repo / "projects" / "p2" / "beril.yaml").write_text(
        "project_id: p2\nbranch: feat/p2-analysis\n"
    )
    assert (
        resolve_project({"cwd": str(repo)}, repo_root=repo, branch="feat/p2-analysis")
        == "p2"
    )


def test_ambiguous_branch_mapping_returns_no_project(repo):
    for name in ("p1", "p2"):
        (repo / "projects" / name / "beril.yaml").write_text(
            f"project_id: {name}\nbranch: shared\n"
        )
    assert resolve_project({"cwd": str(repo)}, repo_root=repo, branch="shared") is None


def test_manifest_naming_default_branch_binds_nothing(repo):
    """A lone `branch: main` must not capture every repo-root session on main.

    The ambiguity guard cannot catch this: one such manifest looks exactly like a
    correct unique match.
    """
    (repo / "projects" / "p2" / "beril.yaml").write_text(
        "project_id: p2\nbranch: main\n"
    )
    assert resolve_project({"cwd": str(repo)}, repo_root=repo, branch="main") is None
    assert resolve_project({"cwd": str(repo)}, repo_root=repo, branch="master") is None


def test_default_branch_guard_spares_conventional_form(repo):
    """`projects/<id>` still resolves even for a project literally named `main`."""
    (repo / "projects" / "main").mkdir()
    assert (
        resolve_project({"cwd": str(repo)}, repo_root=repo, branch="projects/main")
        == "main"
    )


def test_unknown_explicit_binding_does_not_fall_through(repo):
    payload = {"project_id": "ghost", "cwd": str(repo / "projects" / "p1")}
    assert resolve_project(payload, repo_root=repo, branch="projects/p1") is None


def test_unknown_branch_and_file_mtimes_do_not_guess(repo):
    os.utime(repo / "projects" / "p2", (2_000_000_000, 2_000_000_000))
    assert (
        resolve_project({"cwd": str(repo)}, repo_root=repo, branch="feat/other") is None
    )


def test_runtime_writes_versioned_atomic_session(repo, monkeypatch):
    data = _snap(
        repo,
        monkeypatch,
        model_id="claude-x",
        permission_mode="auto",
        source="startup",
        effort={"level": "high"},
    )
    assert data["schema_version"] == "2.0"
    assert data["project"] == "p1"
    assert len(data["sessions"]) == 1
    session = data["sessions"][0]
    assert session["session_id"] == "s1"
    assert session["agent"]["model_id"] == "claude-x"
    assert session["agent"]["effort"] == "high"
    assert session["activity"] == {"permission_mode": "auto", "source": "startup"}
    assert session["tenant"]


def test_new_session_never_inherits_prior_model_or_activity(repo, monkeypatch):
    _snap(
        repo,
        monkeypatch,
        session_id="s1",
        model_id="claude-x",
        effort="high",
        source="startup",
    )
    data = _snap(repo, monkeypatch, session_id="s2")
    first, second = data["sessions"]
    assert first["agent"]["model_id"] == "claude-x"
    assert "model_id" not in second["agent"]
    assert "effort" not in second["agent"]
    assert second["activity"] == {}


def _write_transcript(repo, records):
    path = repo / "projects" / "p1" / "transcript.jsonl"
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    return path


def test_model_and_permission_mode_recovered_from_transcript(repo, monkeypatch):
    # The real SessionStart payload carries neither; both live in the transcript.
    transcript = _write_transcript(
        repo,
        [
            {"type": "assistant", "message": {"model": "claude-opus-4-8"}},
            {"type": "permission-mode", "permissionMode": "bypassPermissions"},
        ],
    )
    data = _snap(repo, monkeypatch, transcript_path=str(transcript), source="startup")
    session = data["sessions"][0]
    assert session["agent"]["model_id"] == "claude-opus-4-8"
    assert session["activity"]["permission_mode"] == "bypassPermissions"


def test_transcript_model_reflects_latest_assistant_turn(repo, monkeypatch):
    # A mid-session /model switch: the last assistant turn is the model in effect.
    transcript = _write_transcript(
        repo,
        [
            {"type": "assistant", "message": {"model": "claude-opus-4-8"}},
            {"type": "assistant", "message": {"model": "claude-haiku-4-5"}},
        ],
    )
    data = _snap(repo, monkeypatch, transcript_path=str(transcript))
    assert data["sessions"][0]["agent"]["model_id"] == "claude-haiku-4-5"


def test_missing_or_empty_transcript_omits_model(repo, monkeypatch):
    # Fresh session with no turns yet — omit the model, never fabricate or crash.
    data = _snap(
        repo,
        monkeypatch,
        transcript_path=str(repo / "projects" / "p1" / "does-not-exist.jsonl"),
    )
    assert "model_id" not in data["sessions"][0]["agent"]


def test_payload_model_wins_over_transcript(repo, monkeypatch):
    transcript = _write_transcript(
        repo, [{"type": "assistant", "message": {"model": "claude-transcript"}}]
    )
    data = _snap(
        repo, monkeypatch, model_id="claude-payload", transcript_path=str(transcript)
    )
    assert data["sessions"][0]["agent"]["model_id"] == "claude-payload"


def test_same_session_is_idempotent_and_does_not_rewrite(repo, monkeypatch):
    monkeypatch.setattr("beril_cli.audit_cmd._now_iso", lambda: "2026-01-01T00:00:00Z")
    _snap(repo, monkeypatch, model_id="claude-x")
    path = repo / "projects" / "p1" / "runtime.json"
    first = path.read_text()
    monkeypatch.setattr("beril_cli.audit_cmd._now_iso", lambda: "2026-01-02T00:00:00Z")
    _snap(repo, monkeypatch, model_id="claude-x")
    assert path.read_text() == first


def test_same_session_changed_snapshot_replaces_atomically(repo, monkeypatch):
    _snap(repo, monkeypatch, model_id="claude-x", source="startup")
    data = _snap(repo, monkeypatch, model_id="claude-y")
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["agent"]["model_id"] == "claude-y"
    assert data["sessions"][0]["activity"] == {}


def test_runtime_requires_session_id(repo, monkeypatch):
    _stdin(monkeypatch, {"cwd": str(repo / "projects" / "p1")})
    assert run_runtime_snapshot(argparse.Namespace()) == 0
    assert not (repo / "projects" / "p1" / "runtime.json").exists()


def test_runtime_no_project_writes_nothing(repo, monkeypatch):
    _stdin(monkeypatch, {"session_id": "s1", "cwd": str(repo)})
    assert run_runtime_snapshot(argparse.Namespace()) == 0
    assert not (repo / "projects" / "p1" / "runtime.json").exists()
    assert not (repo / "projects" / "p2" / "runtime.json").exists()


def test_runtime_survives_malformed_stdin(repo, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("not json{"))
    assert run_runtime_snapshot(argparse.Namespace()) == 0


def test_documented_datasets_snapshot_is_hashed_and_session_scoped(repo, monkeypatch):
    report = (
        "# R\n\n## Data\n\n### Sources\n"
        "| Collection | Tables Used | Purpose |\n"
        "|---|---|---|\n"
        "| `kbase_ke_pangenome` | `genome`, `gene_cluster` | pangenome |\n"
    )
    (repo / "projects" / "p1" / "REPORT.md").write_text(report)
    session = _snap(repo, monkeypatch)["sessions"][0]
    snapshot = session["documented_datasets_snapshot"]
    assert (
        snapshot["report_hash"]
        == "sha256:" + hashlib.sha256(report.encode()).hexdigest()
    )
    assert snapshot["observed_at"] == session["observed_at"]
    assert snapshot["datasets"] == [
        {"collection": "kbase_ke_pangenome", "tables": ["genome", "gene_cluster"]}
    ]


def test_runtime_omits_dataset_snapshot_when_report_has_no_parseable_table(
    repo, monkeypatch
):
    assert "documented_datasets_snapshot" not in _snap(repo, monkeypatch)["sessions"][0]


def test_git_state_and_actor_are_inside_session_record(repo, monkeypatch):
    monkeypatch.setattr(
        "beril_cli.audit_cmd._git_info",
        lambda root, ignored_path=None: {"git_sha": "abc", "git_dirty": False},
    )
    monkeypatch.setenv("USER", "dkishore")
    (repo / "projects" / "p1" / "beril.yaml").write_text(
        'authors:\n  - orcid: "0009-0006-4046-889X"\n'
    )
    session = _snap(repo, monkeypatch)["sessions"][0]
    assert session["code"] == {"git_sha": "abc", "git_dirty": False}
    assert session["actor"] == {
        "user": "dkishore",
        "orcid": "0009-0006-4046-889X",
    }


def test_non_v2_runtime_file_is_replaced_with_fresh_v2_state(repo, monkeypatch):
    path = repo / "projects" / "p1" / "runtime.json"
    path.write_text(
        json.dumps({"project": "p1", "agent": {"model_id": "old-model"}}) + "\n"
    )
    data = _snap(repo, monkeypatch, session_id="new-session")
    assert data["schema_version"] == "2.0"
    assert "legacy_snapshot" not in data
    assert [s["session_id"] for s in data["sessions"]] == ["new-session"]


# --- agent cost ------------------------------------------------------------
#
# Cost is observable in exactly one place in this repo — the status line's
# payload. No hook payload carries it (verified against SessionStart,
# PostToolUse and Stop), so `record_session_cost` is what the status line calls,
# and everything downstream reads what it wrote.

def _runtime(repo, project="p1"):
    return json.loads((repo / "projects" / project / "runtime.json").read_text())


def test_cost_lands_on_the_matching_session_record(repo, monkeypatch):
    _snap(repo, monkeypatch, session_id="s1")
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    session = _runtime(repo)["sessions"][0]
    assert session["session_id"] == "s1"
    assert session["cost"]["usd"] == 4.12
    assert session["cost"]["counted_usd"] == 0.0
    assert session["cost"]["observer"] == "claude-code-statusline"


def test_cost_creates_a_record_when_the_hook_has_not_written_one(repo):
    """The status line resolves projects the hook cannot — a session working
    from the repo root binds by runtime.json only *after* a tool write."""
    record_session_cost(repo / "projects" / "p1", "s-new", 0.5)
    data = _runtime(repo)
    assert data["schema_version"] == "2.0"
    assert data["sessions"][0]["session_id"] == "s-new"
    assert data["sessions"][0]["cost"]["usd"] == 0.5


@pytest.mark.parametrize("usd", [0, 0.0, -1.0, None, "free"])
def test_an_unobserved_cost_is_never_recorded_as_zero(repo, monkeypatch, usd):
    """A missing `cost` key is how a genuinely free stage is told apart from an
    unwatched one. Recording 0.00 would erase that distinction."""
    _snap(repo, monkeypatch, session_id="s1")
    record_session_cost(repo / "projects" / "p1", "s1", usd)
    assert "cost" not in _runtime(repo)["sessions"][0]


def test_no_session_id_records_nothing(repo, monkeypatch):
    _snap(repo, monkeypatch, session_id="s1")
    record_session_cost(repo / "projects" / "p1", None, 4.12)
    assert "cost" not in _runtime(repo)["sessions"][0]


def test_an_unchanged_cents_value_does_not_rewrite_the_file(repo, monkeypatch):
    """The status line renders every turn. Rewriting runtime.json each time
    would churn a file the hook also writes, for no new information."""
    _snap(repo, monkeypatch, session_id="s1")
    path = repo / "projects" / "p1" / "runtime.json"
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    before = path.stat().st_mtime_ns
    record_session_cost(repo / "projects" / "p1", "s1", 4.1234)  # same cents
    assert path.stat().st_mtime_ns == before
    record_session_cost(repo / "projects" / "p1", "s1", 4.13)  # a cent more
    assert path.stat().st_mtime_ns != before


def test_updating_cost_preserves_what_has_already_been_stamped(repo, monkeypatch):
    """`counted_usd` is the portion already attributed to a closed stage. A
    session spans stages, so losing it would re-attribute spend twice."""
    _snap(repo, monkeypatch, session_id="s1")
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    data = _runtime(repo)
    data["sessions"][0]["cost"]["counted_usd"] = 4.12
    (repo / "projects" / "p1" / "runtime.json").write_text(json.dumps(data))
    record_session_cost(repo / "projects" / "p1", "s1", 9.80)
    cost = _runtime(repo)["sessions"][0]["cost"]
    assert (cost["usd"], cost["counted_usd"]) == (9.80, 4.12)


def test_a_snapshot_replace_carries_cost_forward(repo, monkeypatch):
    """The two writers of runtime.json must not clobber each other. Only the
    status line can see cost; only the hook can see the model. A re-snapshot
    replaces the whole session record, so it has to keep the half it cannot
    observe or every model switch would erase the session's spend."""
    _snap(repo, monkeypatch, session_id="s1", model="claude-opus-5")
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    session = _snap(repo, monkeypatch, session_id="s1", model="claude-sonnet-5")[
        "sessions"
    ][0]
    assert session["agent"]["model_id"] == "claude-sonnet-5"
    assert session["cost"]["usd"] == 4.12


# --- the per-stage ledger --------------------------------------------------
#
# The boundary is detected here rather than by the skills that perform it,
# because approve_cmd is the ONLY code in the repo that writes beril.yaml and it
# records plan_approval, not status: all six lifecycle transitions are
# agent-written YAML with no code path at all. The PostToolUse hook fires on the
# very edit that performs one, so it is the only automatic witness available.


def _yaml(repo, project="p1"):
    return (repo / "projects" / project / "beril.yaml").read_text()


def _set_status(repo, status, project="p1"):
    """Edit `status:` in place, the way a skill performing a transition does.

    Rewriting the whole manifest instead would silently wipe the ledger being
    tested and make a passing append look like a failing one.
    """
    manifest = repo / "projects" / project / "beril.yaml"
    text = manifest.read_text()
    if re.search(r"^status:", text, re.MULTILINE):
        # Only the value, keeping any trailing comment — that is what an editor
        # performing a transition does, and this test file asserts elsewhere
        # that the ledger writer leaves such comments alone.
        text = re.sub(
            r"^status:(\s*)[^\s#]+",
            rf"status:\g<1>{status}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text += f"status: {status}\n"
    manifest.write_text(text)


def test_the_first_observation_closes_no_stage(repo, monkeypatch):
    """There is no prior stage to close. runtime.json is gitignored, so this is
    also what every fresh worktree does on its first snapshot."""
    _set_status(repo, "exploration")
    assert _snap(repo, monkeypatch)["last_status"] == "exploration"
    assert "agent_cost" not in _yaml(repo)


def test_an_unchanged_status_closes_no_stage(repo, monkeypatch):
    _set_status(repo, "exploration")
    _snap(repo, monkeypatch)
    _snap(repo, monkeypatch, session_id="s2")
    assert "agent_cost" not in _yaml(repo)


def test_a_transition_stamps_the_stage_that_just_ended(repo, monkeypatch):
    _set_status(repo, "exploration")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    _set_status(repo, "proposed")
    data = _snap(repo, monkeypatch)

    text = _yaml(repo)
    assert "agent_cost:" in text
    assert "observed_by: claude-code" in text
    assert "- stage: exploration" in text
    assert "usd: 4.12" in text
    assert "sessions_observed: 1" in text
    # The stage that ENDED is stamped; the new one is now what's being watched.
    assert data["last_status"] == "proposed"
    # ...and its spend is marked consumed so the next stage cannot re-count it.
    assert data["sessions"][0]["cost"]["counted_usd"] == 4.12


def test_a_stage_nobody_watched_omits_usd_rather_than_recording_zero(
    repo, monkeypatch
):
    """`usd: 0.00` reads as "this stage was free". A missing key reads as
    "nobody watched", which is the true statement."""
    _set_status(repo, "exploration")
    _snap(repo, monkeypatch)
    _set_status(repo, "proposed")
    _snap(repo, monkeypatch)
    text = _yaml(repo)
    assert "- stage: exploration" in text
    assert "sessions_observed: 0" in text
    assert "usd:" not in text


def test_a_session_spanning_two_stages_is_never_counted_twice(repo, monkeypatch):
    """One session outlives the stage it started in. Each stage gets the spend
    earned inside it, and the total across stages equals what was observed."""
    _set_status(repo, "exploration")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 4.12)
    _set_status(repo, "proposed")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 9.80)  # same session
    _set_status(repo, "active")
    _snap(repo, monkeypatch)

    stages = re.findall(r"- stage: (\w+)\n.*?\n(?:      usd: ([\d.]+)\n)?", _yaml(repo))
    assert stages == [("exploration", "4.12"), ("proposed", "5.68")]


def test_a_demotion_is_stamped_like_any_other_boundary(repo, monkeypatch):
    """/synthesize and /berdl-review both demote reviewed -> analysis. A stage
    name may therefore repeat; deltas make double-counting impossible anyway."""
    _set_status(repo, "reviewed")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 2.00)
    _set_status(repo, "analysis")
    _snap(repo, monkeypatch)
    assert "- stage: reviewed" in _yaml(repo)
    assert "usd: 2.00" in _yaml(repo)


def test_the_stamp_fires_even_when_the_session_snapshot_is_unchanged(
    repo, monkeypatch
):
    """Nothing in a session snapshot depends on lifecycle status, so the very
    edit that performs a transition usually produces a byte-identical record --
    and that is exactly the event this has to catch. The snapshot writer's
    idempotency short-circuit must not swallow it."""
    _set_status(repo, "active")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 3.00)
    (repo / "projects" / "p1" / "beril.yaml").write_text(
        "project_id: p1\nstatus: analysis\n"
    )
    _snap(repo, monkeypatch)  # identical payload -> identical session record
    assert "- stage: active" in _yaml(repo)


def test_the_ledger_preserves_comments_and_other_blocks(repo, monkeypatch):
    manifest = repo / "projects" / "p1" / "beril.yaml"
    manifest.write_text(
        "project_id: p1\n"
        "status: exploration          # exploration | proposed | active\n"
        "approval:\n"
        '  by: "0000-0001-9076-6066"\n'
        "\n"
        "# trailing note about submissions\n"
        "submissions: []\n"
    )
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 1.50)
    _set_status(repo, "proposed")
    _snap(repo, monkeypatch)

    text = manifest.read_text()
    assert "# exploration | proposed | active" in text
    assert "# trailing note about submissions" in text
    assert '  by: "0000-0001-9076-6066"' in text
    assert "submissions: []" in text
    assert "- stage: exploration" in text


def test_a_second_stage_appends_without_disturbing_the_first(repo, monkeypatch):
    _set_status(repo, "exploration")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 1.00)
    _set_status(repo, "proposed")
    _snap(repo, monkeypatch)
    record_session_cost(repo / "projects" / "p1", "s1", 3.00)
    _set_status(repo, "active")
    _snap(repo, monkeypatch)

    text = _yaml(repo)
    assert text.count("agent_cost:") == 1
    assert text.index("- stage: exploration") < text.index("- stage: proposed")
    assert "usd: 1.00" in text and "usd: 2.00" in text


def test_a_project_with_no_status_stamps_nothing(repo, monkeypatch):
    """61 of 78 projects have no beril.yaml status at all."""
    (repo / "projects" / "p1" / "beril.yaml").write_text("project_id: p1\n")
    data = _snap(repo, monkeypatch)
    assert "last_status" not in data
    assert "agent_cost" not in _yaml(repo)


def test_audit_cmd_does_not_import_the_cli_modules():
    """The hook falls back to a bare `python3` when there is no venv — the BERDL
    pod — so everything this module reaches has to import on the system
    interpreter. `approve_cmd` reaches `tomllib` (3.11+) through its config
    import, and pulling `block_span` from there made every `_append_stage` raise
    ModuleNotFoundError into the blanket `except`: no error, no stamp, on
    exactly the image the fallback exists for. Caught by an end-to-end run, not
    by the unit tests above, which import this module directly.
    """
    import ast

    source = (Path(audit_cmd.__file__)).read_text()
    imported = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    heavy = {name for name in imported if name.startswith("beril_cli.")}
    assert heavy == {"beril_cli.project_resolution"}, (
        f"audit_cmd runs under the hook's bare-python3 fallback; {heavy} may drag"
        " in tomllib/httpx and silently disable stage stamping"
    )
