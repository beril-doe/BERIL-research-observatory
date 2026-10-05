import json
from pathlib import Path

import pytest

from observatory_context.config import (
    DOCS_TARGET_URI,
    LEGACY_DOCS_TARGET_URI,
    ContextConfig,
)
from observatory_context.ingest import (
    MANIFEST_FILENAME,
    ingest_all,
    ingest_changed,
    ingest_docs,
    ingest_project,
    ingest_projects,
)


class FakeClient:
    def __init__(self) -> None:
        self.added: list[tuple[str, str]] = []
        self.removed: list[tuple[str, bool]] = []
        self.linked: list[tuple[str, list[str], str]] = []
        self.wait_count = 0

    def add_resource(self, path: str, to: str, reason: str, wait: bool = False):
        self.added.append((path, to))
        return {"root_uri": to}

    def wait_processed(self):
        self.wait_count += 1

    def rm(self, uri: str, recursive: bool = False):
        self.removed.append((uri, recursive))

    def link(self, from_uri: str, to_uris, reason: str = ""):
        self.linked.append((from_uri, list(to_uris), reason))


def write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_config(repo_root: Path) -> ContextConfig:
    return ContextConfig(repo_root=repo_root)


def test_ingest_all_adds_project_and_docs(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "demo" / "README.md", "# Demo\n")
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    client = FakeClient()

    ingest_all(make_config(tmp_path), client)

    targets = [target for _, target in client.added]
    assert "viking://resources/projects/demo/" in targets
    assert f"{DOCS_TARGET_URI}pitfalls/" in targets
    assert client.wait_count == 1


def test_ingest_changed_skips_unchanged_then_ingests_modified(tmp_path: Path) -> None:
    readme = tmp_path / "projects" / "demo" / "README.md"
    write(readme, "# Demo\n")
    config = make_config(tmp_path)
    client = FakeClient()

    ingest_changed(config, client)
    client.added.clear()
    ingest_changed(config, client)
    assert client.added == []

    write(readme, "# Demo changed\n")
    ingest_changed(config, client)

    assert [target for _, target in client.added] == [
        "viking://resources/projects/demo/",
    ]


def test_ingest_changed_removes_deleted_project(tmp_path: Path) -> None:
    project = tmp_path / "projects" / "demo"
    write(project / "README.md", "# Demo\n")
    config = make_config(tmp_path)
    client = FakeClient()

    ingest_changed(config, client)
    client.added.clear()
    project.joinpath("README.md").unlink()
    project.rmdir()
    ingest_changed(config, client)

    assert client.removed == [("viking://resources/projects/demo/", True)]
    assert client.added == []


def test_ingest_projects_uploads_only_listed_projects(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "alpha" / "README.md", "# A\n")
    write(tmp_path / "projects" / "beta" / "README.md", "# B\n")
    write(tmp_path / "projects" / "gamma" / "README.md", "# G\n")
    client = FakeClient()

    ingest_projects(make_config(tmp_path), client, ["alpha", "beta"])

    targets = [target for _, target in client.added]
    assert "viking://resources/projects/alpha/" in targets
    assert "viking://resources/projects/beta/" in targets
    assert "viking://resources/projects/gamma/" not in targets
    assert client.wait_count == 1


def test_ingest_project_keeps_other_pending_changes_visible_to_changed(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "alpha" / "README.md", "# A\n")
    write(tmp_path / "projects" / "beta" / "README.md", "# B\n")
    write(tmp_path / "docs" / "pitfalls.md", "# P\n")
    config = make_config(tmp_path)
    ingest_all(config, FakeClient())

    # Edit beta and the central doc, then ingest ONLY alpha.
    write(tmp_path / "projects" / "beta" / "README.md", "# B changed\n")
    write(tmp_path / "docs" / "pitfalls.md", "# P changed\n")
    ingest_project(config, FakeClient(), "alpha")

    followup = FakeClient()
    ingest_changed(config, followup)
    targets = [target for _, target in followup.added]

    assert "viking://resources/projects/beta/" in targets
    assert f"{DOCS_TARGET_URI}pitfalls/" in targets
    # alpha was just ingested; its manifest entry is current, so it is not re-done.
    assert "viking://resources/projects/alpha/" not in targets


def test_ingest_docs_keeps_pending_project_changes_visible_to_changed(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "alpha" / "README.md", "# A\n")
    write(tmp_path / "docs" / "pitfalls.md", "# P\n")
    config = make_config(tmp_path)
    ingest_all(config, FakeClient())

    write(tmp_path / "projects" / "alpha" / "README.md", "# A changed\n")
    ingest_docs(config, FakeClient())

    followup = FakeClient()
    ingest_changed(config, followup)
    targets = [target for _, target in followup.added]

    assert "viking://resources/projects/alpha/" in targets


def test_ingest_all_with_limit_ingests_first_n_projects_and_skips_docs(tmp_path: Path) -> None:
    for name in ("alpha", "beta", "gamma"):
        write(tmp_path / "projects" / name / "README.md", f"# {name}\n")
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    client = FakeClient()

    ingest_all(make_config(tmp_path), client, limit=2)

    targets = [target for _, target in client.added]
    assert "viking://resources/projects/alpha/" in targets
    assert "viking://resources/projects/beta/" in targets
    assert "viking://resources/projects/gamma/" not in targets
    assert f"{DOCS_TARGET_URI}pitfalls/" not in targets


def test_ingest_all_with_limit_writes_partial_manifest_so_changed_picks_up_remainder(
    tmp_path: Path,
) -> None:
    for name in ("alpha", "beta", "gamma"):
        write(tmp_path / "projects" / name / "README.md", f"# {name}\n")
    config = make_config(tmp_path)

    ingest_all(config, FakeClient(), limit=2)
    followup = FakeClient()
    ingest_changed(config, followup)

    targets = [target for _, target in followup.added]
    assert "viking://resources/projects/gamma/" in targets
    assert "viking://resources/projects/alpha/" not in targets
    assert "viking://resources/projects/beta/" not in targets


def test_ingest_project_links_related_projects_from_beril_yaml(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "alpha" / "README.md", "# A\n")
    write(
        tmp_path / "projects" / "alpha" / "beril.yaml",
        "project_id: alpha\nrelated_projects:\n  - beta\n",
    )
    write(tmp_path / "projects" / "beta" / "README.md", "# B\n")
    client = FakeClient()

    ingest_projects(make_config(tmp_path), client, ["alpha"])

    assert client.linked == [
        (
            "viking://resources/projects/alpha/",
            ["viking://resources/projects/beta/"],
            "beril.yaml related_projects",
        )
    ]


def test_ingest_changed_with_limit_caps_project_targets(tmp_path: Path) -> None:
    for name in ("alpha", "beta", "gamma"):
        write(tmp_path / "projects" / name / "README.md", f"# {name}\n")
    config = make_config(tmp_path)
    client = FakeClient()

    ingest_changed(config, client, limit=2)

    targets = [target for _, target in client.added]
    project_targets = [t for t in targets if t.startswith("viking://resources/projects/")]
    assert len(project_targets) == 2
    assert project_targets == [
        "viking://resources/projects/alpha/",
        "viking://resources/projects/beta/",
    ]




# --- retiring the pre-house-account docs root -------------------------------


class OrderedClient(FakeClient):
    """Records every call in order, to check cleanup comes after processing."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []

    def add_resource(self, path: str, to: str, reason: str, wait: bool = False):
        self.events.append(f"add {to}")
        return super().add_resource(path, to, reason, wait)

    def wait_processed(self):
        self.events.append("wait")
        super().wait_processed()

    def rm(self, uri: str, recursive: bool = False):
        self.events.append(f"rm {uri}")
        super().rm(uri, recursive)


def _seed_manifest(config: ContextConfig, entries: dict) -> None:
    path = config.state_dir / MANIFEST_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries), encoding="utf-8")


def test_ingest_docs_retires_the_legacy_root_after_processing(tmp_path: Path) -> None:
    """The cutover is "run --docs once": the old root is deleted, recursively,
    and only once the new copies are written and processed — the docs are
    never missing from both roots."""
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    client = OrderedClient()

    ingest_docs(make_config(tmp_path), client)

    assert (LEGACY_DOCS_TARGET_URI, True) in client.removed
    legacy = client.events.index(f"rm {LEGACY_DOCS_TARGET_URI}")
    assert client.events.index(f"add {DOCS_TARGET_URI}pitfalls/") < legacy
    assert client.events.index("wait") < legacy


def test_ingest_docs_reconciles_legacy_manifest_entries_away(tmp_path: Path) -> None:
    """Old-root entries the manifest recorded are removed and dropped from the
    manifest; project entries are left untouched."""
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    config = make_config(tmp_path)
    project_uri = "viking://resources/projects/demo/"
    legacy_uri = f"{LEGACY_DOCS_TARGET_URI}pitfalls/"
    _seed_manifest(config, {legacy_uri: {"x": "1"}, project_uri: {"x": "2"}})
    client = FakeClient()
    ingest_docs(config, client)

    assert (legacy_uri, True) in client.removed
    saved = json.loads((config.state_dir / MANIFEST_FILENAME).read_text())
    assert legacy_uri not in saved
    assert saved[project_uri] == {"x": "2"}
    assert f"{DOCS_TARGET_URI}pitfalls/" in saved


def test_ingest_docs_leaves_the_legacy_root_when_ingest_fails(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")

    class Failing(FakeClient):
        def add_resource(self, *args, **kwargs):
            raise RuntimeError("backend down")

    client = Failing()
    with pytest.raises(RuntimeError):
        ingest_docs(make_config(tmp_path), client)

    assert client.removed == []


def test_ingest_all_retires_the_legacy_root(tmp_path: Path) -> None:
    write(tmp_path / "projects" / "demo" / "README.md", "# Demo\n")
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    client = FakeClient()

    ingest_all(make_config(tmp_path), client)

    assert (LEGACY_DOCS_TARGET_URI, True) in client.removed


def test_ingest_all_with_limit_skips_docs_and_their_cleanup(tmp_path: Path) -> None:
    """A limited run writes no docs, so it has no business retiring the old root."""
    write(tmp_path / "projects" / "demo" / "README.md", "# Demo\n")
    write(tmp_path / "docs" / "pitfalls.md", "# Pitfalls\n")
    client = FakeClient()

    ingest_all(make_config(tmp_path), client, limit=1)

    assert all(uri != LEGACY_DOCS_TARGET_URI for uri, _ in client.removed)
