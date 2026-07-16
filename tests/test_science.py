"""Tests for conservative, resolved-artifact claim support."""

from __future__ import annotations

from beril_cli.science import (
    claim_id,
    confidence_mismatch,
    is_result,
    resolved_artifact_support,
)


def _p(
    kind: str,
    locator: str = "",
    *,
    resolution: str = "resolved",
    stream: str | None = None,
) -> dict:
    pointer = {
        "kind": kind,
        "locator": locator,
        "resolution": {"status": resolution},
    }
    if stream is not None:
        pointer["stream"] = stream
    return pointer


def test_is_result_true_only_for_query_and_notebook():
    assert is_result(_p("query"))
    assert is_result(_p("notebook"))
    assert not is_result(_p("paper"))
    assert not is_result(_p("figure"))


def test_unresolved_artifacts_do_not_contribute_support():
    supports = [
        _p("notebook", "notebooks/missing-a.ipynb", resolution="unresolved"),
        _p("notebook", "notebooks/missing-b.ipynb", resolution="unresolved"),
    ]
    assert resolved_artifact_support(supports) == "none"


def test_distinct_artifacts_without_streams_are_one_default_stream():
    supports = [
        _p("notebook", "notebooks/a.ipynb"),
        _p("notebook", "notebooks/b.ipynb"),
    ]
    assert resolved_artifact_support(supports) == "single-stream"


def test_explicit_distinct_streams_can_produce_multiple_stream_support():
    supports = [
        _p("notebook", "notebooks/a.ipynb", stream="field-cohort"),
        _p("notebook", "notebooks/b.ipynb", stream="culture-assay"),
    ]
    assert resolved_artifact_support(supports) == "multiple-streams"


def test_duplicate_explicit_streams_remain_single_stream():
    supports = [
        _p("notebook", "notebooks/a.ipynb", stream="same-dataset"),
        _p("notebook", "notebooks/b.ipynb", stream="same-dataset"),
    ]
    assert resolved_artifact_support(supports) == "single-stream"


def test_non_result_evidence_does_not_contribute_artifact_support():
    assert resolved_artifact_support([_p("paper", "PMID:1")]) == "none"


def test_confidence_mismatch_uses_computed_artifact_support():
    assert confidence_mismatch("high", "single-stream") is True
    assert confidence_mismatch("medium", "none") is True
    assert confidence_mismatch("high", "multiple-streams") is False
    assert confidence_mismatch("low", "none") is False


def test_claim_id_slugifies_and_truncates():
    assert (
        claim_id("Lignin enrichment is higher in soil!")
        == "lignin-enrichment-is-higher-in-soil"
    )
    assert claim_id("a" * 100) == "a" * 56
    assert claim_id("!!!") == "claim"


def test_status_from_reads_leftmost_written_value():
    from beril_cli.science import status_from

    assert status_from("supported   # supported | open | refuted") == "supported"
    assert status_from("refuted then open") == "refuted"


def test_malformed_evidence_is_ignored_safely():
    assert is_result("notadict") is False
    assert (
        resolved_artifact_support(["notadict", _p("notebook", "a")]) == "single-stream"
    )
