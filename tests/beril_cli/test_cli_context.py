"""Tests for `beril context` (context_cmd) and its HTTP client (context_client)."""

from __future__ import annotations

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
        "query": "q", "total": 7,
        "results": [_hit("beril/docs/pitfalls/a.md", 0.8123, "About A.")],
    })
    main(["context", "find", "q"])

    assert capsys.readouterr().out.splitlines() == [
        "7 result(s)", "", "beril/docs/pitfalls/a.md", "score: 0.812", "About A.",
    ]


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
        "1 match(es) in 4 file(s) scanned",
    ]


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
