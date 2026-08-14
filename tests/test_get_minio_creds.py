"""Credential-name resolution in scripts/get_minio_creds.py.

BERDL renamed the object-store variables from MINIO_* to S3_* and no consumer was
updated, which is #366. These tests pin the precedence so a future rename does not
silently reintroduce the failure: a missing variable must never be reported as a
rejected credential.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "get_minio_creds.py"


@pytest.fixture(scope="module")
def creds():
    spec = importlib.util.spec_from_file_location("get_minio_creds", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["get_minio_creds"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """No object-store variable leaks in from the developer's own shell."""
    for name in (
        "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_ENDPOINT_URL",
        "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_ENDPOINT_URL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_reads_the_s3_names_a_current_pod_actually_sets(creds, monkeypatch):
    monkeypatch.setenv("S3_ACCESS_KEY", "ak")
    monkeypatch.setenv("S3_SECRET_KEY", "sk")
    monkeypatch.setenv("S3_ENDPOINT_URL", "https://s3.example")

    assert creds.resolve_from_local_env() == {
        "S3_ACCESS_KEY": "ak",
        "S3_SECRET_KEY": "sk",
        "S3_ENDPOINT_URL": "https://s3.example",
        "source": "local-env",
    }


def test_falls_back_to_the_legacy_minio_names(creds, monkeypatch):
    """Older pod images still carry MINIO_*, so they must keep working."""
    monkeypatch.setenv("MINIO_ACCESS_KEY", "old-ak")
    monkeypatch.setenv("MINIO_SECRET_KEY", "old-sk")

    resolved = creds.resolve_from_local_env()

    assert resolved["S3_ACCESS_KEY"] == "old-ak"
    assert resolved["S3_SECRET_KEY"] == "old-sk"


def test_s3_wins_when_both_spellings_are_present(creds, monkeypatch):
    monkeypatch.setenv("S3_ACCESS_KEY", "new")
    monkeypatch.setenv("S3_SECRET_KEY", "new-sk")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "old")
    monkeypatch.setenv("MINIO_SECRET_KEY", "old-sk")

    assert creds.resolve_from_local_env()["S3_ACCESS_KEY"] == "new"


def test_endpoint_defaults_when_neither_spelling_is_set(creds, monkeypatch):
    monkeypatch.setenv("S3_ACCESS_KEY", "ak")
    monkeypatch.setenv("S3_SECRET_KEY", "sk")

    assert creds.resolve_from_local_env()["S3_ENDPOINT_URL"] == creds.DEFAULT_ENDPOINT_URL


def test_an_empty_value_is_treated_as_absent(creds, monkeypatch):
    """An exported-but-empty variable is a common .env artifact and must not win."""
    monkeypatch.setenv("S3_ACCESS_KEY", "")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "old-ak")
    monkeypatch.setenv("S3_SECRET_KEY", "sk")

    assert creds.resolve_from_local_env()["S3_ACCESS_KEY"] == "old-ak"


def test_returns_none_when_no_credentials_exist(creds):
    assert creds.resolve_from_local_env() is None


def test_a_secret_without_an_access_key_is_not_usable(creds, monkeypatch):
    monkeypatch.setenv("S3_SECRET_KEY", "sk")

    assert creds.resolve_from_local_env() is None


def test_the_failure_message_names_every_variable_it_looked_for(creds):
    """The old text said 'could not resolve credentials', which reads as a
    permissions problem and sent at least one person hunting a stale key."""
    searched = creds._searched()

    for name in ("S3_ACCESS_KEY", "S3_SECRET_KEY", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY"):
        assert name in searched


def test_remote_payload_uses_the_same_precedence(creds):
    """The pod is asked for both spellings and the choice is made locally, so the
    rule is not duplicated into a remote one-liner that can drift."""
    payload = {"S3_ACCESS_KEY": "new", "MINIO_ACCESS_KEY": "old"}

    assert creds._first(payload, creds.ACCESS_KEY_NAMES) == "new"
    assert creds._first({"MINIO_ACCESS_KEY": "old"}, creds.ACCESS_KEY_NAMES) == "old"
    assert creds._first({}, creds.ACCESS_KEY_NAMES) is None
