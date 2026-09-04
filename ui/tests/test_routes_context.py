"""Tests for the context-manager routes (``/api/context/*``).

These exercise the route layer only: auth, credential lookup, decryption of the
stored per-user key, and request/response shaping. ``OpenVikingManager`` is
patched out, so no OpenViking instance is needed. The end-to-end mapping from an
OV payload to ``ContextQueryResults`` is covered in ``test_context_manager.py``.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.clients.openviking import OpenVikingError
from app.config import get_settings
from app.context_manager.base import (
    ContextIngestResults,
    ContextQueryResults,
    IngestResult,
    QueryResult,
)
from app.crypto import encrypt_secret
from app.db.crud import (
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    get_projects_for_user,
)
from app.db.models import BerilUser, OvUserCredential
from app.db.session import get_db
from app.main import create_app

_CREDENTIAL_KEY = Fernet.generate_key().decode()

_ENV = {
    "BERIL_TEST_SKIP_LIFESPAN": "True",
    "BERIL_ORCID_CLIENT_ID": "APP-TESTCLIENTID",
    "BERIL_ORCID_CLIENT_SECRET": "test-secret",
    "BERIL_ORCID_BASE_URL": "https://sandbox.orcid.org",
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
    "BERIL_OV_URL": "http://ov.test:1933",
    "BERIL_OV_ACCOUNT_ID": "beril",
    "BERIL_OV_ADMIN_KEY": "admin-key",
    "BERIL_OV_CREDENTIAL_KEY": _CREDENTIAL_KEY,
}

USER_TOKEN = {
    "access_token": "fake-access-token",
    "token_type": "bearer",
    "orcid": "0000-0001-2345-6789",
    "name": "Alice Researcher",
}

QUERY_RESULTS = ContextQueryResults(
    query="alpha",
    results=[
        QueryResult(
            uri="viking://resources/projects/alpha.md",
            context_type="document",
            score=0.93,
            text="Alpha project overview.",
        )
    ],
)


def _make_mock_oauth_client(token: dict):
    auth_url = "https://sandbox.orcid.org/oauth/authorize?client_id=APP-TESTCLIENTID"
    mock_instance = MagicMock()
    mock_instance.create_authorization_url = MagicMock(return_value=(auth_url, "mock-state"))
    mock_instance.fetch_token = AsyncMock(return_value=token)
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=mock_instance)


def _login(client: TestClient, token: dict = USER_TOKEN) -> None:
    mock_class = _make_mock_oauth_client(token)
    with patch("app.routes.auth.AsyncOAuth2Client", mock_class):
        client.get("/auth/orcid/callback", params={"code": "fake-code"}, follow_redirects=False)


@pytest.fixture
def client(repository_data, app_data_context, db_session):
    with patch.dict(os.environ, _ENV):
        import app.config as cfg

        cfg._settings = None
        app_instance = create_app()

        async def override_get_db() -> AsyncGenerator:
            yield db_session

        app_instance.dependency_overrides[get_db] = override_get_db
        with TestClient(app_instance, raise_server_exceptions=True) as c:
            app_instance.state.repo_data = repository_data
            app_instance.state.base_context = app_data_context
            yield c
        cfg._settings = None


@pytest.fixture
async def user(db_session):
    u = BerilUser(orcid_id=USER_TOKEN["orcid"], display_name=USER_TOKEN["name"])
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest.fixture
async def credentialed_user(db_session, user):
    """A user with a stored, Fernet-encrypted OpenViking key."""
    db_session.add(
        OvUserCredential(
            user_id=user.id,
            account_id="beril",
            ov_user_id=user.orcid_id,
            encrypted_key=encrypt_secret("plain-user-key", _CREDENTIAL_KEY),
        )
    )
    await db_session.commit()
    return user


@pytest.fixture
def manager():
    """Patch OpenVikingManager in the routes module; yields the instance."""
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    inst.list_files = AsyncMock(return_value=["alpha.md", "beta.md"])
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_find_unauthenticated_returns_401(client):
    resp = client.post("/api/context/find", json={"query": "alpha"})
    assert resp.status_code == 401


def test_ls_unauthenticated_returns_401(client):
    assert client.get("/api/context/ls").status_code == 401


# ---------------------------------------------------------------------------
# POST /api/context/find
# ---------------------------------------------------------------------------


async def test_find_returns_mapped_results(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "alpha"
    assert body["results"] == [
        {
            "uri": "viking://resources/projects/alpha.md",
            "context_type": "document",
            "score": 0.93,
            "text": "Alpha project overview.",
        }
    ]


async def test_find_forwards_body_to_manager(client, credentialed_user, manager):
    _login(client)
    resp = client.post(
        "/api/context/find",
        json={
            "query": "alpha",
            "root_path": "viking://resources/projects",
            "limit": 3,
            "score_threshold": 0.5,
        },
    )

    assert resp.status_code == 200
    sent = manager.query.await_args.args[0]
    assert sent.query == "alpha"
    assert sent.root_path == "viking://resources/projects"
    assert sent.limit == 3
    assert sent.score_threshold == 0.5


async def test_find_applies_query_defaults(client, credentialed_user, manager):
    """Only ``query`` is required; the rest come from ContextQuery defaults."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    sent = manager.query.await_args.args[0]
    assert sent.root_path is None
    assert sent.limit == 10
    assert sent.score_threshold is None


async def test_find_decrypts_stored_key_for_manager(client, credentialed_user):
    """The manager is constructed with the decrypted key, not the ciphertext."""
    _login(client)
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    with patch("app.routes.context.OpenVikingManager", return_value=inst) as cls:
        client.post("/api/context/find", json={"query": "alpha"})

    assert cls.call_args.args[1] == "plain-user-key"


async def test_find_rejects_missing_query_field(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={})

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_malformed_limit(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={"query": "a", "limit": "lots"})

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


# ---------------------------------------------------------------------------
# GET /api/context/ls
# ---------------------------------------------------------------------------


async def test_ls_returns_file_listing(client, credentialed_user, manager):
    _login(client)
    resp = client.get("/api/context/ls")

    assert resp.status_code == 200
    assert resp.json() == ["alpha.md", "beta.md"]
    manager.list_files.assert_awaited_once()


async def test_ls_decrypts_stored_key_for_manager(client, credentialed_user):
    _login(client)
    inst = MagicMock()
    inst.list_files = AsyncMock(return_value=[])
    with patch("app.routes.context.OpenVikingManager", return_value=inst) as cls:
        client.get("/api/context/ls")

    assert cls.call_args.args[1] == "plain-user-key"


# ---------------------------------------------------------------------------
# Credential provisioning
#
# ``user`` (not ``credentialed_user``) has no stored credential, so these
# exercise the first-use path through ``get_user_ov_api_key``.
# ---------------------------------------------------------------------------


async def test_find_provisions_credential_on_first_use(client, user, manager):
    """A user with no stored key gets one minted transparently — still a 200."""
    register = AsyncMock(return_value={"user_key": "minted-key"})
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    register.assert_awaited_once_with(USER_TOKEN["orcid"])


async def test_find_uses_freshly_minted_key_for_manager(client, user):
    register = AsyncMock(return_value={"user_key": "minted-key"})
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register), patch(
        "app.routes.context.OpenVikingManager", return_value=inst
    ) as cls:
        client.post("/api/context/find", json={"query": "alpha"})

    assert cls.call_args.args[1] == "minted-key"


async def test_find_returns_502_when_provisioning_fails(client, user, manager):
    """Backend failures surface as a generic 502, never as OV specifics."""
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    detail = resp.json()["detail"]
    assert "openviking" not in detail.lower()
    manager.query.assert_not_awaited()


async def test_ls_returns_502_when_provisioning_fails(client, user, manager):
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.get("/api/context/ls")

    assert resp.status_code == 502
    manager.list_files.assert_not_awaited()


# ---------------------------------------------------------------------------
# POST /api/context/ingest_file
# ---------------------------------------------------------------------------


def _ingest(client, *, project="My Project", files=None):
    files = files if files is not None else [("files", ("notes.md", b"hi", "text/md"))]
    return client.post(
        "/api/context/ingest_file", data={"project": project}, files=files
    )


def _queued(n: int) -> ContextIngestResults:
    return ContextIngestResults(
        results=[
            IngestResult(relative_path=f"f{i}.md", status="queued", uri=f"viking://{i}")
            for i in range(n)
        ],
        queued=n,
        failed=0,
    )


@pytest.fixture
def ingest_manager():
    """Patch OpenVikingManager for the ingest path; yields the instance."""
    inst = MagicMock()
    inst.insert_files = AsyncMock(return_value=_queued(1))
    # Default to "nothing new" so status tests opt in to a refresh explicitly.
    inst.task_statuses = AsyncMock(return_value={})
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


def test_ingest_unauthenticated_returns_401(client):
    assert _ingest(client).status_code == 401


async def test_ingest_queues_file_and_returns_results(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client)

    assert resp.status_code == 200
    body = resp.json()
    assert body["queued"] == 1
    assert body["failed"] == 0
    ingest_manager.insert_files.assert_awaited_once()


async def test_ingest_targets_user_orcid_and_project_slug(
    client, credentialed_user, ingest_manager
):
    """The target root is keyed on the uploader's ORCiD, then the slug."""
    _login(client)
    _ingest(client, project="Acinetobacter ADP1 Explorer")

    root = ingest_manager.insert_files.await_args.kwargs["target_root"]
    assert root == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/acinetobacter_adp1_explorer"
    )


async def test_ingest_forwards_file_content_and_path(
    client, credentialed_user, ingest_manager
):
    _login(client)
    _ingest(
        client,
        files=[("files", ("sub/dir/data.csv", b"a,b\n1,2\n", "text/csv"))],
    )

    sent = ingest_manager.insert_files.await_args.args[0]
    assert len(sent) == 1
    # Nested paths survive so the structure is preserved below the root.
    assert sent[0].relative_path == "sub/dir/data.csv"
    assert sent[0].content == b"a,b\n1,2\n"


async def test_ingest_accepts_multiple_files(client, credentialed_user, ingest_manager):
    ingest_manager.insert_files.return_value = _queued(3)
    _login(client)
    resp = _ingest(
        client,
        files=[
            ("files", ("a.md", b"a", "text/md")),
            ("files", ("b.md", b"b", "text/md")),
            ("files", ("c.md", b"c", "text/md")),
        ],
    )

    assert resp.status_code == 200
    assert resp.json()["queued"] == 3
    assert len(ingest_manager.insert_files.await_args.args[0]) == 3


async def test_ingest_reports_partial_failure_as_200(
    client, credentialed_user, ingest_manager
):
    """A partly-failed batch still returns 200 with the failures named."""
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(relative_path="a.md", status="queued", uri="viking://a"),
            IngestResult(relative_path="b.md", status="failed", reason="rejected"),
        ],
        queued=1,
        failed=1,
    )
    _login(client)
    resp = _ingest(client)

    assert resp.status_code == 200
    body = resp.json()
    assert (body["queued"], body["failed"]) == (1, 1)
    assert body["results"][1]["status"] == "failed"


async def test_ingest_creates_project_when_absent(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    resp = _ingest(client, project="Brand New Project")

    assert resp.status_code == 200
    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created is not None
    # The human-readable form is preserved as the title.
    assert created.title == "Brand New Project"


async def test_ingest_reuses_existing_project(
    client, credentialed_user, ingest_manager, db_session
):
    existing = await create_user_project(
        db_session, credentialed_user.id, title="Existing", slug="existing_project"
    )
    _login(client)
    resp = _ingest(client, project="Existing Project")

    assert resp.status_code == 200
    projects = await get_projects_for_user(db_session, credentialed_user.id)
    assert [p.id for p in projects] == [existing.id]


async def test_ingest_rejects_unusable_project_name(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, project="!!!")

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_sanitizes_traversal_in_filename(
    client, credentialed_user, ingest_manager
):
    """Traversal segments are stripped, not rejected — the file still ingests,
    but below the target root rather than escaping it."""
    _login(client)
    resp = _ingest(
        client, files=[("files", ("../../escape.md", b"b", "text/md"))]
    )

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert sent[0].relative_path == "escape.md"


async def test_ingest_rejects_unusable_filename_without_queueing_any(
    client, credentialed_user, ingest_manager
):
    """A name that sanitizes to nothing fails the whole batch — nothing queued."""
    _login(client)
    resp = _ingest(
        client,
        files=[
            ("files", ("good.md", b"a", "text/md")),
            ("files", ("..", b"b", "text/md")),
        ],
    )

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_enforces_file_count_cap(client, credentialed_user, ingest_manager):
    _login(client)
    with patch.object(get_settings(), "context_max_ingest_files", 2):
        resp = _ingest(
            client,
            files=[
                ("files", (f"f{i}.md", b"x", "text/md")) for i in range(3)
            ],
        )

    assert resp.status_code == 413
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_enforces_file_size_cap(client, credentialed_user, ingest_manager):
    _login(client)
    with patch.object(get_settings(), "context_max_file_bytes", 4):
        resp = _ingest(
            client, files=[("files", ("big.md", b"way too long", "text/md"))]
        )

    assert resp.status_code == 413
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_provisions_credential_on_first_use(client, user, ingest_manager):
    """An uncredentialed user gets a key minted, same as the read paths."""
    register = AsyncMock(return_value={"user_key": "minted-key"})
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = _ingest(client)

    assert resp.status_code == 200
    register.assert_awaited_once_with(USER_TOKEN["orcid"])


async def test_ingest_returns_502_when_provisioning_fails(
    client, user, ingest_manager
):
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = _ingest(client)

    assert resp.status_code == 502
    ingest_manager.insert_files.assert_not_awaited()


# ---------------------------------------------------------------------------
# GET /api/context/ingest_status/{batch_id}
# ---------------------------------------------------------------------------


def _queued_with_tasks(paths_and_tasks) -> ContextIngestResults:
    return ContextIngestResults(
        results=[
            IngestResult(
                relative_path=p,
                status="queued",
                uri=f"viking://root/{p}",
                task_id=t,
            )
            for p, t in paths_and_tasks
        ],
        queued=len(paths_and_tasks),
        failed=0,
    )


async def _start_batch(client, ingest_manager, paths_and_tasks) -> str:
    """Run an ingest and return its batch_id."""
    ingest_manager.insert_files.return_value = _queued_with_tasks(paths_and_tasks)
    resp = _ingest(client)
    assert resp.status_code == 200
    return resp.json()["batch_id"]


async def test_ingest_returns_a_batch_id(client, credentialed_user, ingest_manager):
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    assert batch_id


def test_ingest_status_unauthenticated_returns_401(client):
    assert client.get("/api/context/ingest_status/anything").status_code == 401


async def test_ingest_status_unknown_batch_returns_404(client, credentialed_user):
    _login(client)
    assert client.get("/api/context/ingest_status/nope").status_code == 404


async def test_ingest_status_hides_another_users_batch(
    client, credentialed_user, ingest_manager, db_session
):
    """A foreign batch is 404, not 403 — a probe must not confirm it exists."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    other = BerilUser(orcid_id="0000-0009-8888-7777", display_name="Bob")
    db_session.add(other)
    await db_session.commit()
    batch = await get_ingest_batch(db_session, batch_id)
    batch.user_id = other.id
    await db_session.commit()

    assert client.get(f"/api/context/ingest_status/{batch_id}").status_code == 404


async def test_ingest_status_reports_refreshed_progress(
    client, credentialed_user, ingest_manager
):
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("processing", None)}
    )
    resp = client.get(f"/api/context/ingest_status/{batch_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "processing"
    assert body["counts"]["completed"] == 1
    assert body["counts"]["processing"] == 1
    assert {f["relative_path"]: f["status"] for f in body["files"]} == {
        "a.md": "completed",
        "b.md": "processing",
    }


async def test_ingest_status_completes_when_all_land(
    client, credentialed_user, ingest_manager
):
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("completed", None)}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["status"] == "completed"
    assert body["counts"]["completed"] == 2


async def test_ingest_status_failure_outranks_success(
    client, credentialed_user, ingest_manager
):
    """One failed file makes the batch failed, however many others landed."""
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("failed", "parse blew up")}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["status"] == "failed"
    failed = [f for f in body["files"] if f["status"] == "failed"][0]
    assert failed["error"] == "parse blew up"


async def test_ingest_status_does_not_repoll_terminal_files(
    client, credentialed_user, ingest_manager
):
    """A settled result survives the backend forgetting the task."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    client.get(f"/api/context/ingest_status/{batch_id}")

    # Second poll: nothing is outstanding, so the backend is not consulted.
    ingest_manager.task_statuses.reset_mock()
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    ingest_manager.task_statuses.assert_not_awaited()
    assert body["status"] == "completed"


async def test_ingest_status_keeps_last_known_when_backend_unreachable(
    client, credentialed_user, ingest_manager
):
    """An unreachable backend must not erase what we already recorded."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(return_value={"t1": ("unknown", None)})
    resp = client.get(f"/api/context/ingest_status/{batch_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["files"][0]["status"] == "queued"
    assert body["status"] == "processing"


async def test_ingest_status_reports_submission_failure(
    client, credentialed_user, ingest_manager
):
    """A file that never queued has no task to poll and stays failed."""
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(
                relative_path="a.md", status="failed", reason="rejected", task_id=None
            )
        ],
        queued=0,
        failed=1,
    )
    _login(client)
    batch_id = _ingest(client).json()["batch_id"]

    ingest_manager.task_statuses = AsyncMock(return_value={})
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    ingest_manager.task_statuses.assert_not_awaited()
    assert body["status"] == "failed"
    assert body["files"][0]["error"] == "rejected"


async def test_ingest_status_includes_project_slug(
    client, credentialed_user, ingest_manager
):
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    batch_id = _ingest(client, project="My Test Project").json()["batch_id"]

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["project"] == "my_test_project"


async def test_ingest_status_counts_cover_every_status(
    client, credentialed_user, ingest_manager
):
    """counts always carries all five keys, so clients can index it blindly."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    counts = client.get(f"/api/context/ingest_status/{batch_id}").json()["counts"]

    assert set(counts) == {
        "queued",
        "processing",
        "completed",
        "failed",
        "unknown",
    }
