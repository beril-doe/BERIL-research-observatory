"""Tests for `beril context` (context_cmd) and its HTTP client (context_client)."""

from __future__ import annotations

import base64
import hashlib
import json

import httpx
import pytest

from beril_cli import auth_store, context_client
from beril_cli.cli import main
from beril_cli.context_client import Scope

BASE = "https://srv.example.test"
ME = "0000-0001-2345-6789"


@pytest.fixture
def tmp_auth(tmp_path, monkeypatch):
    """Redirect auth_store's on-disk location into tmp_path."""
    monkeypatch.setattr(auth_store, "AUTH_DIR", tmp_path / ".beril")
    monkeypatch.setattr(auth_store, "AUTH_PATH", tmp_path / ".beril" / "auth.json")


@pytest.fixture
def logged_in(tmp_auth):
    auth_store.save(token="beril_abc", base_url=BASE, orcid_id=ME, display_name="Alice")


class FakeBeril:
    """A BERIL server: ``routes`` maps (method, path) to a response, or to a
    callable taking the request. Every request is recorded."""

    def __init__(self, monkeypatch):
        self.routes: dict[tuple[str, str], object] = {}
        self.requests: list[httpx.Request] = []
        real_client = httpx.Client

        def factory(*args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(self._serve)
            return real_client(*args, **kwargs)

        monkeypatch.setattr(context_client.httpx, "Client", factory)

    def on(self, method: str, path: str, body=None, status: int = 200):
        self.routes[(method, path)] = httpx.Response(status, json=body)

    def _serve(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        route = self.routes.get((request.method, request.url.path))
        if route is None:
            return httpx.Response(404, json={"detail": "Not Found"})
        return route(request) if callable(route) else route

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def last_params(self) -> dict:
        return dict(self.last.url.params)

    def last_body(self) -> dict:
        return json.loads(self.last.content)


@pytest.fixture
def beril(monkeypatch):
    return FakeBeril(monkeypatch)


def _hit(address: str, score: float = 0.9, text: str = "abstract", **extra) -> dict:
    return {"address": address, "context_type": "resource", "score": score,
            "text": text, "match_reason": None, "content": None, **extra}


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("address", "scope"),
    [
        ("0009-1/alpha/memories/pitfalls.md",
         Scope(owner="0009-1", project="alpha", path="memories/pitfalls.md")),
        ("0009-1/alpha", Scope(owner="0009-1", project="alpha")),
        ("0009-1/", Scope(owner="0009-1")),
        ("beril/docs/pitfalls", Scope(owner="beril", project="docs", path="pitfalls")),
    ],
)
def test_an_address_splits_into_owner_project_path(address, scope):
    assert Scope.from_address(address) == scope


def test_an_empty_address_is_refused():
    with pytest.raises(ValueError):
        Scope.from_address("/")


# ---------------------------------------------------------------------------
# Login and errors
# ---------------------------------------------------------------------------


def test_reads_require_a_login(tmp_auth, beril, capsys):
    assert main(["context", "find", "x"]) == 1
    assert "beril login" in capsys.readouterr().err
    assert beril.requests == []


def test_requests_carry_the_stored_token(logged_in, beril):
    beril.on("POST", "/api/context/find", {"query": "x", "results": [], "total": 0})
    main(["context", "find", "x"])

    assert beril.last.headers["Authorization"] == "Bearer beril_abc"
    assert str(beril.last.url).startswith(BASE)


def test_a_rejected_token_points_at_login(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", {"detail": "nope"}, status=401)

    assert main(["context", "ls"]) == 1
    assert "beril login" in capsys.readouterr().err


def test_a_validation_error_is_one_readable_line(logged_in, beril, capsys):
    beril.on("POST", "/api/context/find", {"detail": [
        {"loc": ["body", "limit"], "msg": "Input should be greater than or equal to 1"},
    ]}, status=422)

    assert main(["context", "find", "x", "--limit", "0"]) == 1
    assert "limit: Input should be greater than or equal to 1" in capsys.readouterr().err


def test_an_unreachable_server_says_so(logged_in, beril, capsys):
    def down(request):
        raise httpx.ConnectError("refused", request=request)

    beril.routes[("GET", "/api/context/ls")] = down

    assert main(["context", "ls"]) == 1
    assert "could not reach" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Scope flags
# ---------------------------------------------------------------------------


def _find_body(beril, *argv) -> dict:
    beril.on("POST", "/api/context/find", {"query": "q", "results": [], "total": 0})
    assert main(["context", "find", "q", *argv]) == 0
    return beril.last_body()


def test_an_unscoped_find_sends_no_scope(logged_in, beril):
    """The server decides what an unaddressed search spans (the corpus)."""
    assert _find_body(beril) == {"query": "q"}


def test_scope_flags_become_route_fields(logged_in, beril):
    body = _find_body(beril, "--project", "alpha", "--path", "memories", "--limit", "3")
    assert body == {"query": "q", "project": "alpha", "path": "memories", "limit": 3}


def test_docs_scopes_to_the_central_docs(logged_in, beril):
    assert _find_body(beril, "--docs") == {"query": "q", "owner": "beril", "project": "docs"}


def test_an_address_scopes_to_owner_project_path(logged_in, beril):
    body = _find_body(beril, "--address", "0009-1/alpha/REPORT.md")
    assert body == {"query": "q", "owner": "0009-1", "project": "alpha", "path": "REPORT.md"}


@pytest.mark.parametrize(
    "argv",
    [
        ["find", "q", "--address", "0009-1/alpha", "--project", "beta"],
        ["find", "q", "--docs", "--owner", "0009-1"],
        ["ls", "0009-1/alpha", "--all-owners"],
        # Codex stop-gate review: the server 422s these; refuse them locally.
        ["find", "q", "--owner", "0009-1", "--all-owners"],
        ["ls", "--owner", "0009-1", "--all-owners"],
        ["grep", "x", "--path", "memories"],
    ],
)
def test_contradictory_scopes_are_refused_before_any_request(logged_in, beril, capsys, argv):
    assert main(["context", *argv]) == 2
    assert capsys.readouterr().err.startswith("error:")
    assert beril.requests == []


# ---------------------------------------------------------------------------
# find
# ---------------------------------------------------------------------------


def test_find_prints_count_then_address_score_abstract(logged_in, beril, capsys):
    beril.on("POST", "/api/context/find", {
        "query": "q", "total": 1,
        "results": [_hit("beril/docs/pitfalls/a.md", 0.8123, "About A.")],
    })
    main(["context", "find", "q"])

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "1 result(s)", "", "beril/docs/pitfalls/a.md", "score: 0.812", "About A.",
    ]
    assert captured.err == ""


@pytest.mark.parametrize("argv", [[], ["--json"]])
def test_find_notes_when_more_results_lie_past_the_limit(logged_in, beril, capsys, argv):
    """Regression (ISSUE-06): a full page of ranked hits read as the whole
    answer. The count is what is shown; the note says more exist."""
    beril.on("POST", "/api/context/find", {
        "query": "q", "total": 17,
        "results": [_hit(f"0009-1/alpha/f{i}.md") for i in range(10)],
    })
    main(["context", "find", "q", *argv])

    captured = capsys.readouterr()
    assert "showing the top 10; more ranked results lie past the limit" in captured.err
    assert "note" not in captured.out
    if not argv:
        assert captured.out.splitlines()[0] == "10 result(s)"


def test_find_read_content_prints_the_full_text(logged_in, beril, capsys):
    beril.on("POST", "/api/context/find", {
        "query": "q", "total": 1,
        "results": [_hit("0009-1/alpha/REPORT.md", content="# Report\nFull text.")],
    })
    main(["context", "find", "q", "--read-content"])

    assert beril.last_body()["read_content"] is True
    assert "# Report\nFull text." in capsys.readouterr().out


def test_json_prints_the_response_untouched(logged_in, beril, capsys):
    response = {"query": "q", "total": 1, "results": [_hit("0009-1/alpha/REPORT.md")]}
    beril.on("POST", "/api/context/find", response)
    main(["context", "find", "q", "--json"])

    assert json.loads(capsys.readouterr().out) == response


# ---------------------------------------------------------------------------
# ls
# ---------------------------------------------------------------------------


def test_ls_without_an_address_lists_your_projects(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [
        {"name": "alpha", "isDir": True, "address": f"{ME}/alpha"},
        {"name": "notes.md", "isDir": False, "address": f"{ME}/notes.md"},
    ])
    main(["context", "ls"])

    assert beril.last_params() == {}
    assert capsys.readouterr().out.splitlines() == [f"{ME}/alpha/", f"{ME}/notes.md"]


def test_ls_takes_an_address_argument(logged_in, beril):
    beril.on("GET", "/api/context/ls", [])
    main(["context", "ls", "beril/docs/pitfalls", "-r", "--node-limit", "5"])

    assert beril.last_params() == {
        "owner": "beril", "project": "docs", "path": "pitfalls",
        "recursive": "true", "node_limit": "5",
    }


def test_simple_ls_prints_bare_addresses(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", ["0009-1", "beril"])
    main(["context", "ls", "--all-owners", "--simple"])

    assert beril.last_params() == {"all_owners": "true", "simple": "true"}
    assert capsys.readouterr().out.splitlines() == ["0009-1", "beril"]


def test_an_empty_listing_says_so(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [])
    main(["context", "ls", "--project", "alpha"])

    assert capsys.readouterr().out.strip() == "(empty)"


# ---------------------------------------------------------------------------
# grep
# ---------------------------------------------------------------------------


def test_grep_prints_address_line_text_and_a_count(logged_in, beril, capsys):
    beril.on("GET", "/api/context/grep", {
        "matches": [{"address": "beril/docs/performance/p.md", "line": 11,
                     "content": "  ## PySpark-First  "}],
        "count": 1, "match_count": 1, "files_scanned": 4,
    })
    main(["context", "grep", "Spark", "--docs", "-i"])

    assert beril.last_params() == {
        "pattern": "Spark", "owner": "beril", "project": "docs", "case_insensitive": "true",
    }
    assert capsys.readouterr().out.splitlines() == [
        "beril/docs/performance/p.md:11: ## PySpark-First",
        "1 match(es) in 1 file(s)",  # files that matched; not the store's files_scanned
    ]


def _matches(n: int) -> dict:
    return {
        "matches": [{"address": f"0009-1/alpha/f{i}.md", "line": 1, "content": "x"}
                    for i in range(n)],
        "count": n, "match_count": n, "files_scanned": n,
    }


@pytest.mark.parametrize(
    ("argv", "returned", "limit"),
    [([], 256, 256), (["--node-limit", "10"], 10, 10), (["--json"], 256, 256)],
)
def test_grep_warns_when_results_reach_the_limit(logged_in, beril, capsys, argv, returned, limit):
    """Regression (Codex adversarial review): the server stops at the match
    limit and reports only what it returned, so a common token was silently
    truncated."""
    beril.on("GET", "/api/context/grep", _matches(returned))
    main(["context", "grep", "x", "--all-owners", *argv])

    captured = capsys.readouterr()
    assert f"stopped at the {limit}-match limit" in captured.err
    assert "warning" not in captured.out


def test_grep_does_not_warn_below_the_limit(logged_in, beril, capsys):
    beril.on("GET", "/api/context/grep", _matches(255))
    main(["context", "grep", "x", "--all-owners"])

    assert capsys.readouterr().err == ""


def test_grep_exclude_is_an_address(logged_in, beril):
    beril.on("GET", "/api/context/grep", {"matches": [], "count": 0})
    main(["context", "grep", "x", "--all-owners", "--exclude", "0009-1/alpha/memories"])

    assert beril.last_params() == {
        "pattern": "x", "all_owners": "true",
        "exclude_owner": "0009-1", "exclude_project": "alpha", "exclude_path": "memories",
    }


# ---------------------------------------------------------------------------
# pitfalls / discoveries
# ---------------------------------------------------------------------------


def test_pitfalls_without_a_query_lists_them_all(logged_in, beril):
    beril.on("GET", "/api/context/pitfalls", {"results": [], "total": 0})
    main(["context", "pitfalls"])

    assert beril.last_params() == {}


@pytest.mark.parametrize("kind", ["pitfalls", "discoveries"])
def test_documents_can_be_scoped_to_one_owners_projects(logged_in, beril, kind):
    """Regression (Codex review on #458): an owner without a project is a
    supported scope — every one of that owner's projects — not a mistake."""
    beril.on("GET", f"/api/context/{kind}", {"results": [], "total": 0})

    assert main(["context", kind, "spark", "--owner", "0009-1"]) == 0
    assert beril.last_params() == {"q": "spark", "owner": "0009-1"}


def test_pitfalls_prints_documents_with_origin_and_excerpts(logged_in, beril, capsys):
    beril.on("GET", "/api/context/pitfalls", {
        "query": "spark", "total": 3, "fragments_scanned": 9,
        "results": [{
            "address": "0009-1/alpha/memories/pitfalls.md", "origin": "project_memory",
            "project": "alpha", "owner": "0009-1", "score": 0.81,
            "excerpts": ["Spark  OOM\non collect()"],
            "fragment_addresses": [],
        }],
    })
    main(["context", "pitfalls", "spark", "--project", "alpha", "--exact", "--limit", "1"])

    assert beril.last_params() == {
        "q": "spark", "project": "alpha", "exact": "true", "limit": "1",
    }
    assert capsys.readouterr().out.splitlines() == [
        "1 of 3 pitfalls document(s)",
        "",
        "0009-1/alpha/memories/pitfalls.md",
        "origin: project_memory (alpha)  score: 0.810",
        "  > Spark OOM on collect()",
    ]


def test_discoveries_reports_suppressed_duplicates(logged_in, beril, capsys):
    beril.on("GET", "/api/context/discoveries", {
        "query": None, "total": 1, "suppressed": 2,
        "results": [{"address": "beril/docs/discoveries", "origin": "central_background",
                     "project": None, "owner": "beril", "score": None,
                     "excerpts": [], "fragment_addresses": []}],
    })
    main(["context", "discoveries"])

    out = capsys.readouterr().out.splitlines()
    assert out[0] == "1 of 1 discoveries document(s); 2 stale duplicate(s) suppressed"
    assert out[3] == "origin: central_background"


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def _healthy(beril, *, orcid=ME, status="ok"):
    beril.on("GET", "/api/user/whoami", {"orcid_id": orcid, "display_name": "Alice"})
    beril.on("GET", "/api/context/health", {"status": status})


def test_doctor_ok(logged_in, beril, capsys):
    _healthy(beril)

    assert main(["context", "doctor"]) == 0
    out = capsys.readouterr().out
    assert "Context layer: OK" in out
    assert f"Logged in as: {ME}" in out


def test_doctor_without_a_login(tmp_auth, beril, capsys):
    assert main(["context", "doctor"]) == 1
    assert "NOT_LOGGED_IN" in capsys.readouterr().out
    assert beril.requests == []


def test_doctor_with_a_rejected_token(logged_in, beril, capsys):
    beril.on("GET", "/api/user/whoami", {"detail": "no"}, status=401)

    assert main(["context", "doctor"]) == 1
    out = capsys.readouterr().out
    assert "AUTH_FAILED" in out and "beril login" in out


def test_doctor_with_an_unreachable_server(logged_in, beril, capsys):
    def down(request):
        raise httpx.ConnectError("refused", request=request)

    beril.routes[("GET", "/api/user/whoami")] = down

    assert main(["context", "doctor"]) == 1
    assert "UNREACHABLE" in capsys.readouterr().out


def test_doctor_with_the_store_down(logged_in, beril, capsys):
    _healthy(beril, status="unavailable")

    assert main(["context", "doctor"]) == 1
    assert "UNAVAILABLE" in capsys.readouterr().out


def test_doctor_calls_a_failing_context_route_unavailable_once_whoami_answered(
    logged_in, beril, capsys
):
    """BERIL answered whoami, so "unreachable — check your network" would be
    wrong: a gateway error page on the context route is the service's fault."""
    beril.on("GET", "/api/user/whoami", {"orcid_id": ME, "display_name": "Alice"})
    beril.routes[("GET", "/api/context/health")] = httpx.Response(
        502, content=b"<!DOCTYPE html><html>cloudflare</html>",
        headers={"content-type": "text/html"},
    )

    assert main(["context", "doctor", "--json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["verdict"] == "unavailable"
    assert report["user"] == ME
    assert "did not answer" in report["detail"] and "BERIL admin" in report["remedy"]


def test_scope_refuses_an_exclusion_over_every_owner():
    with pytest.raises(ValueError, match="one owner"):
        Scope(project="alpha", all_owners=True).params("exclude_")


def test_doctor_reports_the_servers_identity_not_the_cached_one(logged_in, beril, capsys):
    """Reads default to the token's own projects, so the identity that matters
    is BERIL's — a stale cached ORCiD is flagged, not reported."""
    _healthy(beril, orcid="0009-9999")

    assert main(["context", "doctor"]) == 0
    out = capsys.readouterr().out
    assert "Logged in as: 0009-9999" in out
    assert f"saved as {ME}" in out


def test_doctor_json(logged_in, beril, capsys):
    _healthy(beril)
    main(["context", "doctor", "--json"])

    report = json.loads(capsys.readouterr().out)
    assert report == {"verdict": "ok", "base_url": BASE, "user": ME,
                      "detail": None, "remedy": None}


def test_doctor_never_names_the_backend(logged_in, beril, capsys):
    _healthy(beril, status="unavailable")
    main(["context", "doctor"])

    assert "viking" not in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# Unknown arguments
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        # Codex adversarial review: a misspelled scope flag was dropped, so a
        # one-project search silently ran across the whole corpus.
        ["context", "find", "secret", "--projct", "alpha"],
        ["context", "ls", "--recurse"],
        # The same gap on an existing command: a dropped --relayed records
        # the approval as witnessed.
        ["approve", "alpha", "--relayd"],
    ],
)
def test_unknown_arguments_are_refused_before_anything_runs(logged_in, beril, capsys, argv):
    with pytest.raises(SystemExit) as exited:
        main(argv)

    assert exited.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
    assert beril.requests == []


def test_start_still_forwards_unknown_arguments_to_the_agent(monkeypatch):
    seen = {}

    def fake_run_start(**kwargs):
        seen.update(kwargs)
        return 0

    monkeypatch.setattr("beril_cli.start.run_start", fake_run_start)

    assert main(["start", "--skip-onboard", "--permission-mode", "plan"]) == 0
    assert seen["extra_args"] == ["--permission-mode", "plan"]


# ---------------------------------------------------------------------------
# BERDL hub testing: ls depth (ISSUE-02), grep counts (ISSUE-03), HTML (ISSUE-04)
# ---------------------------------------------------------------------------


def test_ls_depth_is_sent_and_needs_recursive(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [])
    assert main(["context", "ls", "beril/docs", "-r", "--depth", "6"]) == 0
    assert beril.last_params()["depth"] == "6"

    assert main(["context", "ls", "beril/docs", "--depth", "6"]) == 2
    assert "add -r" in capsys.readouterr().err


def test_ls_warns_when_directories_at_the_depth_limit_were_not_expanded(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [
        {"address": "beril/docs/pitfalls", "isDir": True, "rel_path": "pitfalls"},
        {"address": "beril/docs/pitfalls/pitfalls", "isDir": True, "rel_path": "pitfalls/pitfalls"},
    ])
    main(["context", "ls", "beril/docs", "-r", "--depth", "2"])

    assert "depth 2 were not expanded" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [[], ["--json"]])
def test_a_simple_listing_still_warns_at_the_depth_limit(logged_in, beril, capsys, argv):
    """Regression (hub testing): --simple entries have no rel_path, so the
    depth warning went quiet exactly where an agent collects addresses. With
    --depth the full listing is fetched and the addresses taken from it."""
    beril.on("GET", "/api/context/ls", [
        {"address": "beril/docs/pitfalls", "isDir": True, "rel_path": "pitfalls"},
        {"address": "beril/docs/README.md", "isDir": False, "rel_path": "README.md"},
    ])
    assert main(["context", "ls", "beril/docs", "-r", "--depth", "1", "--simple", *argv]) == 0

    captured = capsys.readouterr()
    assert "simple" not in beril.last_params()
    assert "depth 1 were not expanded" in captured.err
    expected = ["beril/docs/pitfalls", "beril/docs/README.md"]
    assert (json.loads(captured.out) if argv else captured.out.splitlines()) == expected


def test_a_simple_listing_without_a_depth_is_asked_for_as_such(logged_in, beril):
    beril.on("GET", "/api/context/ls", ["beril/docs/pitfalls"])
    main(["context", "ls", "beril/docs", "-r", "--simple"])
    assert beril.last_params()["simple"] == "true"


def test_the_find_note_does_not_suggest_raising_a_limit_at_its_cap(logged_in, beril, capsys):
    beril.on("POST", "/api/context/find", {
        "query": "q", "total": 301, "results": [_hit(f"0009-1/a/f{i}.md") for i in range(200)],
    })
    main(["context", "find", "q", "--limit", "200"])

    err = capsys.readouterr().err
    assert "showing the top 200" in err and "grep" in err
    assert "Raise --limit" not in err


def test_ls_warns_when_the_listing_hits_its_entry_limit(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [{"address": f"o/p/f{i}", "isDir": False} for i in range(5)])
    main(["context", "ls", "o/p", "-r", "--node-limit", "5"])

    assert "stopped at the 5-entry limit" in capsys.readouterr().err


def test_a_complete_listing_does_not_warn(logged_in, beril, capsys):
    beril.on("GET", "/api/context/ls", [{"address": "o/p/f", "isDir": False, "rel_path": "f"}])
    main(["context", "ls", "o/p", "-r", "--depth", "3"])

    assert capsys.readouterr().err == ""


def test_grep_counts_the_files_that_matched_itself(logged_in, beril, capsys):
    """Regression (ISSUE-03): ``files_scanned`` is the store's number, and
    sometimes counts matched files, not scanned ones."""
    beril.on("GET", "/api/context/grep", {
        "matches": [{"address": "a", "line": 1, "content": "x"},
                    {"address": "a", "line": 2, "content": "x"},
                    {"address": "b", "line": 1, "content": "x"}],
        "count": 3, "files_scanned": 99,
    })
    main(["context", "grep", "x", "--docs"])

    assert capsys.readouterr().out.splitlines()[-1] == "3 match(es) in 2 file(s)"


def test_a_grep_with_no_matches_does_not_claim_nothing_was_searched(logged_in, beril, capsys):
    beril.on("GET", "/api/context/grep", {"matches": [], "count": 0, "files_scanned": 0})
    main(["context", "grep", "zzz", "--docs"])

    assert capsys.readouterr().out.strip() == "0 match(es)"


def test_a_gateway_error_page_is_summarized_not_printed(logged_in, beril, capsys):
    """Regression (ISSUE-04): a Cloudflare HTML page was dumped verbatim."""
    beril.routes[("POST", "/api/context/find")] = httpx.Response(
        502, text="<!DOCTYPE html>\n<!--[if lt IE 7]> <html class=\"no-js\"> <![endif]-->"
    )

    assert main(["context", "find", "x"]) == 1
    err = capsys.readouterr().err
    assert "<" not in err and "gateway returned an error page" in err and "HTTP 502" in err


# ---------------------------------------------------------------------------
# read
# ---------------------------------------------------------------------------

REPORT = f"{ME}/alpha/REPORT.md"
FIGURE = f"{ME}/alpha/figures/fig1.png"
TEXT = "# Report\n\nA number: 42.\n"
PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(16))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _envelope(content: str, *, encoding="utf-8", sha256=None, **extra) -> dict:
    data = base64.b64decode(content) if encoding == "base64" else content.encode("utf-8")
    return {
        "address": REPORT, "path": "REPORT.md", "size": len(data),
        "sha256": sha256 or _sha(data), "content_type": "text/markdown",
        "encoding": encoding, "content": content, "source": "context",
        "modified_at": "2026-11-12T10:00:00Z", **extra,
    }


def _serve_read(beril, *, text=None, data=None, sha256=None, status=200):
    """Answer /api/context/read in the form the request asks for."""
    def route(request):
        if status != 200:
            return httpx.Response(status, json={"detail": "refused"})
        if request.headers["Accept"] == "application/octet-stream":
            return httpx.Response(200, content=data, headers={
                "Content-Type": "image/png",
                "X-Content-SHA256": sha256 or _sha(data),
                "X-Content-Source": "archive",
            })
        return httpx.Response(200, json=_envelope(text, sha256=sha256))
    beril.routes[("GET", "/api/context/read")] = route


def test_read_prints_the_text_byte_for_byte(logged_in, beril, capsys):
    _serve_read(beril, text=TEXT)

    assert main(["context", "read", REPORT]) == 0

    out = capsys.readouterr().out
    assert out == TEXT  # no trailing newline added
    assert beril.last_params() == {"address": REPORT}
    assert beril.last.headers["Accept"] == "application/json"
    assert beril.last.headers["Authorization"] == "Bearer beril_abc"


def test_read_json_prints_the_envelope(logged_in, beril, capsys):
    _serve_read(beril, text=TEXT)

    assert main(["context", "read", REPORT, "--json"]) == 0

    body = json.loads(capsys.readouterr().out)
    assert body == _envelope(TEXT)
    assert set(body) == {
        "address", "path", "size", "sha256", "content_type", "encoding",
        "content", "source", "modified_at",
    }


def test_read_out_writes_the_bytes_and_confirms_on_stderr(logged_in, beril, capsys, tmp_path):
    _serve_read(beril, data=PNG)
    target = tmp_path / "fig1.png"

    assert main(["context", "read", FIGURE, "--out", str(target)]) == 0

    assert target.read_bytes() == PNG
    assert beril.last.headers["Accept"] == "application/octet-stream"
    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"wrote {len(PNG)} byte(s) to {target}" in captured.err
    assert _sha(PNG) in captured.err and "verified" in captured.err


def test_read_out_fails_loudly_on_a_sha256_mismatch_and_writes_nothing(
    logged_in, beril, capsys, tmp_path,
):
    _serve_read(beril, data=PNG, sha256=_sha(b"tampered"))
    target = tmp_path / "fig1.png"

    assert main(["context", "read", FIGURE, "--out", str(target)]) == 1

    assert not target.exists()
    err = capsys.readouterr().err
    assert "sha256 mismatch" in err and _sha(PNG) in err and _sha(b"tampered") in err


def test_read_of_text_verifies_the_envelope_sha256_too(logged_in, beril, capsys):
    _serve_read(beril, text=TEXT, sha256="0" * 64)

    assert main(["context", "read", REPORT]) == 1

    captured = capsys.readouterr()
    assert captured.out == "" and "sha256 mismatch" in captured.err


def test_read_refuses_to_print_a_binary_file_without_out(logged_in, beril, capsys):
    encoded = base64.b64encode(PNG).decode("ascii")
    beril.on("GET", "/api/context/read",
             _envelope(encoded, encoding="base64", content_type="image/png"))

    assert main(["context", "read", FIGURE]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "binary" in captured.err and "--out" in captured.err


def test_read_json_of_a_binary_file_keeps_it_base64(logged_in, beril, capsys):
    encoded = base64.b64encode(PNG).decode("ascii")
    beril.on("GET", "/api/context/read",
             _envelope(encoded, encoding="base64", content_type="image/png"))

    assert main(["context", "read", FIGURE, "--json"]) == 0

    body = json.loads(capsys.readouterr().out)
    assert body["encoding"] == "base64" and body["content"] == encoded


def test_read_403_names_the_allowlist(logged_in, beril, capsys):
    _serve_read(beril, status=403)

    assert main(["context", "read", f"{ME}/alpha/RESEARCH_PLAN.md"]) == 1

    err = capsys.readouterr().err
    assert "not readable" in err and "403" in err
    for name in ("REPORT.md", "README.md", "beril.yaml", "CORRECTIONS.md",
                 "REFUTATION_<n>.md", "figures/**"):
        assert name in err


def test_read_404_says_no_such_file(logged_in, beril, capsys):
    _serve_read(beril, status=404)

    assert main(["context", "read", f"{ME}/alpha/REPORT.md"]) == 1

    err = capsys.readouterr().err
    assert f"no such file: {ME}/alpha/REPORT.md" in err and "beril context ls" in err


def test_read_401_points_at_login(logged_in, beril, capsys):
    _serve_read(beril, status=401)

    assert main(["context", "read", REPORT]) == 1
    assert "beril login" in capsys.readouterr().err


@pytest.mark.parametrize("address", [ME, f"{ME}/alpha", "/"])
def test_read_needs_a_full_owner_project_path_address(logged_in, beril, capsys, address):
    assert main(["context", "read", address]) == 2
    assert beril.requests == []
    assert "owner" in capsys.readouterr().err


def test_read_out_and_json_are_exclusive(logged_in, beril, capsys):
    with pytest.raises(SystemExit):
        main(["context", "read", REPORT, "--out", "x", "--json"])
    assert beril.requests == []


def test_read_against_an_unreachable_server_says_so(logged_in, beril, capsys):
    def down(request):
        raise httpx.ConnectError("boom")
    beril.routes[("GET", "/api/context/read")] = down

    assert main(["context", "read", REPORT]) == 1
    assert "could not reach" in capsys.readouterr().err


def test_read_help_lists_the_allowlist(capsys):
    with pytest.raises(SystemExit):
        main(["context", "read", "--help"])
    out = capsys.readouterr().out
    assert "REPORT.md" in out and "figures/**" in out and "--out" in out


# ---------------------------------------------------------------------------
# submissions
# ---------------------------------------------------------------------------


def _submission(project: str, at: str, kind: str = "approved", files: int = 2) -> dict:
    return {
        "project": project, "owner_orcid": ME, "address": f"{ME}/{project}",
        "submitted_at": at, "kind": kind, "batch_id": f"batch-{project}",
        "is_public": True,
        "files": [{"path": f"f{i}.md", "sha256": "ab" * 32} for i in range(files)],
    }


def test_submissions_prints_a_table_and_the_cursor_on_stderr(logged_in, beril, capsys):
    beril.on("GET", "/api/context/submissions", {
        "submissions": [
            _submission("alpha", "2026-11-01T00:00:00Z"),
            _submission("beta_long_name", "2026-11-02T00:00:00Z", kind="seeded", files=0),
        ],
        "next_since": "2026-11-02T00:00:00Z",
    })

    assert main(["context", "submissions"]) == 0

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert lines[0].split() == ["project", "owner", "kind", "submitted_at", "files"]
    assert lines[1].split() == ["alpha", ME, "approved", "2026-11-01T00:00:00Z", "2"]
    assert lines[2].split() == ["beta_long_name", ME, "seeded", "2026-11-02T00:00:00Z", "0"]
    assert lines[3] == "2 submission(s)"
    assert "next_since: 2026-11-02T00:00:00Z" in captured.err and "--since" in captured.err
    assert beril.last_params() == {}


def test_submissions_sends_since_kind_and_limit(logged_in, beril):
    beril.on("GET", "/api/context/submissions", {"submissions": [], "next_since": None})

    main(["context", "submissions", "--since", "2026-11-01T00:00:00Z",
          "--kind", "approved,seeded", "--limit", "5"])

    assert beril.last_params() == {
        "since": "2026-11-01T00:00:00Z", "kind": "approved,seeded", "limit": "5",
    }


def test_submissions_json_carries_rows_and_next_since(logged_in, beril, capsys):
    rows = [_submission("alpha", "2026-11-01T00:00:00Z")]
    beril.on("GET", "/api/context/submissions",
             {"submissions": rows, "next_since": "2026-11-01T00:00:00Z"})

    assert main(["context", "submissions", "--json"]) == 0

    captured = capsys.readouterr()
    body = json.loads(captured.out)
    assert body == {"submissions": rows, "next_since": "2026-11-01T00:00:00Z"}
    assert "next_since: 2026-11-01T00:00:00Z" in captured.err


def test_submissions_pages_by_feeding_next_since_back(logged_in, beril, capsys):
    pages = {
        None: ([_submission("a", "2026-11-01T00:00:00Z")], "2026-11-01T00:00:00Z"),
        "2026-11-01T00:00:00Z": ([_submission("b", "2026-11-03T00:00:00Z")], None),
    }

    def route(request):
        rows, nxt = pages[request.url.params.get("since")]
        return httpx.Response(200, json={"submissions": rows, "next_since": nxt})
    beril.routes[("GET", "/api/context/submissions")] = route

    assert main(["context", "submissions", "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert main(["context", "submissions", "--json", "--since", first["next_since"]]) == 0
    captured = capsys.readouterr()
    second = json.loads(captured.out)

    assert [s["project"] for s in first["submissions"]] == ["a"]
    assert [s["project"] for s in second["submissions"]] == ["b"]
    assert second["next_since"] is None and "next_since" not in captured.err


def test_submissions_with_no_rows_says_so(logged_in, beril, capsys):
    beril.on("GET", "/api/context/submissions", {"submissions": []})

    assert main(["context", "submissions"]) == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == "(no submissions)" and captured.err == ""


def test_submissions_refuses_an_unknown_kind_before_any_request(logged_in, beril, capsys):
    assert main(["context", "submissions", "--kind", "approved,rejected"]) == 2
    assert beril.requests == []
    assert "rejected" in capsys.readouterr().err


def test_submissions_server_failure_is_reported(logged_in, beril, capsys):
    beril.on("GET", "/api/context/submissions", {"detail": "feed unavailable"}, status=500)

    assert main(["context", "submissions"]) == 1
    err = capsys.readouterr().err
    assert "HTTP 500" in err and "feed unavailable" in err
