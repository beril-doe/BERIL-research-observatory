"""Tests for the BERIL webapp health checks added to `beril doctor`.

Covers the three helpers that hit the network — login validation, webapp
availability, and OpenViking ("context manager") availability — by building
real ``httpx.Response`` objects and stubbing ``httpx.get``. The higher-level
``run_doctor`` orchestration and the pre-existing local checks are exercised by
running the command in the other suites; here we pin the new logic.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import httpx

from beril_cli import auth_store, doctor
from beril_cli.auth_store import AuthRecord

BASE_URL = "https://beril.example.test"


def _response(body: dict | str, status: int = 200) -> httpx.Response:
    content = json.dumps(body).encode() if isinstance(body, dict) else body.encode()
    return httpx.Response(status_code=status, content=content)


def _record() -> AuthRecord:
    return AuthRecord(
        token="beril_tok",
        base_url=BASE_URL,
        orcid_id="0000-0001-2345-6789",
        display_name="Alice",
    )


# ---------------------------------------------------------------------------
# _check_beril_login
# ---------------------------------------------------------------------------


class TestCheckLogin:
    def test_not_logged_in(self):
        with patch.object(auth_store, "load", return_value=None):
            status, detail = doctor._check_beril_login()
        assert status == "WARN"
        assert "beril login" in detail

    def test_valid_token_passes(self):
        with patch.object(auth_store, "load", return_value=_record()), \
             patch.object(doctor.httpx, "get", return_value=_response({"orcid_id": "x"})):
            status, detail = doctor._check_beril_login()
        assert status == "PASS"
        assert "Alice" in detail and "0000-0001-2345-6789" in detail

    def test_rejected_token_fails(self):
        with patch.object(auth_store, "load", return_value=_record()), \
             patch.object(doctor.httpx, "get", return_value=_response("nope", status=401)):
            status, detail = doctor._check_beril_login()
        assert status == "FAIL"
        assert "401" in detail

    def test_server_unreachable_warns_not_fails(self):
        with patch.object(auth_store, "load", return_value=_record()), \
             patch.object(doctor.httpx, "get", side_effect=httpx.ConnectError("boom")):
            status, detail = doctor._check_beril_login()
        # Stored login may still be valid; don't hard-fail on a network blip.
        assert status == "WARN"
        assert "Alice" in detail


# ---------------------------------------------------------------------------
# _check_beril_webapp
# ---------------------------------------------------------------------------


class TestCheckWebapp:
    def test_healthy(self):
        with patch.object(doctor.httpx, "get", return_value=_response({"status": "healthy"})):
            status, detail = doctor._check_beril_webapp(BASE_URL)
        assert status == "PASS"
        assert "healthy" in detail

    def test_degraded_warns(self):
        with patch.object(doctor.httpx, "get", return_value=_response({"status": "degraded"})):
            status, detail = doctor._check_beril_webapp(BASE_URL)
        assert status == "WARN"
        assert "degraded" in detail

    def test_non_200_fails(self):
        with patch.object(doctor.httpx, "get", return_value=_response("down", status=503)):
            status, detail = doctor._check_beril_webapp(BASE_URL)
        assert status == "FAIL"
        assert "503" in detail

    def test_unreachable_fails(self):
        with patch.object(doctor.httpx, "get", side_effect=httpx.ConnectError("boom")):
            status, detail = doctor._check_beril_webapp(BASE_URL)
        assert status == "FAIL"
        assert "unreachable" in detail


# ---------------------------------------------------------------------------
# _check_context_manager
# ---------------------------------------------------------------------------


class TestCheckContextManager:
    def test_ok(self):
        with patch.object(doctor.httpx, "get", return_value=_response({"status": "ok"})):
            status, detail = doctor._check_context_manager(BASE_URL)
        assert status == "PASS"
        assert "/ov/health" in detail

    def test_reachable_without_status_field(self):
        # OpenViking's own /health may not use a "status" key; a 200 is enough.
        with patch.object(doctor.httpx, "get", return_value=_response({"uptime": 1})):
            status, _ = doctor._check_context_manager(BASE_URL)
        assert status == "PASS"

    def test_non_200_fails(self):
        with patch.object(doctor.httpx, "get", return_value=_response("down", status=503)):
            status, detail = doctor._check_context_manager(BASE_URL)
        assert status == "FAIL"
        assert "503" in detail

    def test_timeout_fails(self):
        with patch.object(doctor.httpx, "get", side_effect=httpx.TimeoutException("slow")):
            status, detail = doctor._check_context_manager(BASE_URL)
        assert status == "FAIL"
        assert "timed out" in detail
