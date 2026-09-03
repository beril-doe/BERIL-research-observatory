"""Guard the canonical NMDC orientation against documentation drift."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NMDC_GUIDE = ROOT / "docs" / "datasets" / "nmdc" / "README.md"


def test_nmdc_guide_identifies_canonical_and_derived_resources():
    guide = NMDC_GUIDE.read_text(encoding="utf-8")

    for resource in ("nmdc.metadata", "nmdc.results", "nmdc.ref_data"):
        assert f"`{resource}`" in guide

    for resource in ("kbase.nmdc_arkin", "kbase.nmdc_mags", "kbase.nmdc_neon"):
        assert f"`{resource}`" in guide

    assert "nmdc.metadata.biosample_to_workflow_run" in guide
    assert "nmdc.results.checkm_statistics" in guide


def test_berdl_start_loads_nmdc_guide_for_nmdc_questions():
    start_skill = (
        ROOT / ".claude" / "skills" / "berdl_start" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "docs/datasets/nmdc/README.md" in start_skill


def test_schema_index_links_to_existing_nmdc_guide():
    schema_index = (ROOT / "docs" / "schema.md").read_text(encoding="utf-8")

    assert "[NMDC](datasets/nmdc/)" in schema_index
    assert NMDC_GUIDE.is_file()
