"""Backend URIs become caller-facing addresses (owner/project/path)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.context_manager.addresses import to_address
from app.context_manager.openviking import context_health
from app.clients.openviking import OpenVikingError
from app.context_manager.base import IngestResult, PitfallHit, QueryResult


@pytest.mark.parametrize(
    ("uri", "address"),
    [
        ("viking://resources/users/0009-1/alpha/REPORT.md", "0009-1/alpha/REPORT.md"),
        ("viking://resources/users/0009-1/alpha/", "0009-1/alpha"),
        ("viking://resources/users/0009-1", "0009-1"),
        (
            "viking://resources/users/beril/docs/pitfalls/x/.abstract.md",
            "beril/docs/pitfalls/x/.abstract.md",
        ),
        ("viking://resources/users/", ""),
        ("viking://resources/users", ""),
    ],
)
def test_corpus_uris_become_owner_project_path(uri, address):
    assert to_address(uri) == address


def test_an_address_maps_to_itself():
    """A response may be serialized more than once on its way out."""
    address = "0009-1/alpha/REPORT.md"
    assert to_address(address) == address


def test_a_uri_outside_the_corpus_loses_its_scheme():
    assert to_address("viking://resources/docs/old.md") == "resources/docs/old.md"


def test_models_serialize_uris_as_addresses_in_json_only():
    """JSON is how a response leaves BERIL; a Python-mode dump stays usable
    inside BERIL, so it keeps the URI."""
    hit = QueryResult(
        uri="viking://resources/users/0009-1/alpha/REPORT.md",
        context_type="document",
        score=0.5,
        text="t",
    )

    assert hit.model_dump(mode="json", by_alias=True)["address"] == "0009-1/alpha/REPORT.md"
    assert hit.model_dump()["uri"] == "viking://resources/users/0009-1/alpha/REPORT.md"
    assert hit.uri == "viking://resources/users/0009-1/alpha/REPORT.md"


def test_fragment_uris_and_optional_uris_serialize_as_addresses():
    hit = PitfallHit(
        uri="viking://resources/users/beril/docs/pitfalls",
        origin="central",
        fragment_uris=["viking://resources/users/beril/docs/pitfalls/a.md"],
    )
    dumped = hit.model_dump(mode="json", by_alias=True)
    assert dumped["fragment_addresses"] == ["beril/docs/pitfalls/a.md"]

    assert IngestResult(relative_path="a", status="failed").model_dump(
        mode="json", by_alias=True
    )["address"] is None


@pytest.mark.parametrize(
    "failure",
    [
        OpenVikingError("unreachable"),
        # Codex stop-gate review: a 200 whose body is not JSON escaped as a 500.
        json.JSONDecodeError("Expecting value", "<html>", 0),
    ],
)
async def test_context_health_reports_any_store_failure_as_unavailable(failure):
    with patch("app.context_manager.openviking.ov_health", AsyncMock(side_effect=failure)):
        assert await context_health() is False


async def test_context_health_reports_a_healthy_store():
    with patch("app.context_manager.openviking.ov_health", AsyncMock(return_value={})):
        assert await context_health() is True
