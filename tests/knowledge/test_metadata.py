from pathlib import Path

from observatory_context.metadata import (
    ProjectMetadata,
    build_project_metadata,
)


def test_build_project_metadata_from_beril_yaml_and_readme(tmp_path: Path) -> None:
    project_dir = tmp_path / "alpha"
    project_dir.mkdir()
    (project_dir / "beril.yaml").write_text(
        """
project_id: openviking-alpha
status: active
created_at: 2026-01-02
last_session_at: 2026-02-03T04:05:06Z
branch: feature/context
engine:
  name: gpt-5
authors:
  - name: Ada Lovelace
    affiliation: Analytical Society
    orcid: 0000-0001-2345-6789
  - name: Grace Hopper
""".lstrip(),
        encoding="utf-8",
    )
    (project_dir / "README.md").write_text(
        "# OpenViking Alpha\n\n## Status\nIgnored fallback\n",
        encoding="utf-8",
    )
    (project_dir / "claims.json").write_text("{}\n", encoding="utf-8")
    (project_dir / "REFUTATION_2.md").write_text("# Refutation\n", encoding="utf-8")

    metadata = build_project_metadata(project_dir)

    assert metadata == ProjectMetadata(
        project_id="openviking-alpha",
        title="OpenViking Alpha",
        status="active",
        author_names=["Ada Lovelace", "Grace Hopper"],
        markdown=metadata.markdown,
    )
    assert "| Project ID | openviking-alpha |" in metadata.markdown
    assert "| Engine | gpt-5 |" in metadata.markdown
    assert (
        "| Ada Lovelace | Analytical Society | 0000-0001-2345-6789 |"
        in metadata.markdown
    )
    assert "| Grace Hopper |  |  |" in metadata.markdown
    assert "claims.json" in metadata.markdown
    assert "REFUTATION_2.md" in metadata.markdown


def test_readme_fallback_metadata(tmp_path: Path) -> None:
    zeta_dir = tmp_path / "zeta"
    zeta_dir.mkdir()
    (zeta_dir / "README.md").write_text(
        "# Zeta Project\n\n## Status\n\nReady for review\n",
        encoding="utf-8",
    )

    metadata = build_project_metadata(zeta_dir)

    assert metadata.project_id == "zeta"
    assert metadata.title == "Zeta Project"
    assert metadata.status == "Ready for review"
    assert metadata.author_names == []


# --- authors from prose (ISSUE-05) -------------------------------------------

import pytest  # noqa: E402

from observatory_context.metadata import _markdown_authors  # noqa: E402


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("- Paramvir S. Dehal (https://orcid.org/0000-0001-5810-2497), Lawrence Berkeley National Laboratory",
         ("Paramvir S. Dehal", "Lawrence Berkeley National Laboratory", "0000-0001-5810-2497")),
        ("- **Christopher Neely** | ORCID: 0000-0002-2620-8948 | Author",
         ("Christopher Neely", "", "0000-0002-2620-8948")),
        ("- Adam Arkin (ORCID: [0000-0002-4999-2931](https://orcid.org/0000-0002-4999-2931)), U.C. Berkeley",
         ("Adam Arkin", "U.C. Berkeley", "0000-0002-4999-2931")),
        ("- Markus de Raad (LBNL) — ORCID: [0000-0001-8263-9198](https://orcid.org/0000-0001-8263-9198)",
         ("Markus de Raad", "LBNL", "0000-0001-8263-9198")),
        ("- Gazi S. Mahmud (https://orcid.org/0009-0006-4046-889X), LBNL",
         ("Gazi S. Mahmud", "LBNL", "0009-0006-4046-889X")),
        ("- Justin Reese, Lawrence Berkeley National Lab",
         ("Justin Reese", "Lawrence Berkeley National Lab", "")),
    ],
)
def test_author_lines_in_the_formats_the_repo_uses(line, expected) -> None:
    [author] = _markdown_authors(f"# P\n\n## Authors\n\n{line}\n\n## Next\n- not an author\n")
    assert (author["name"], author["affiliation"], author["orcid"]) == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Heather MacGregor", ("Heather MacGregor", "", "")),
        ("Mark Andrew Miller (LBL), ORCID [0000-0001-9076-6066](https://orcid.org/0000-0001-9076-6066)",
         ("Mark Andrew Miller", "LBL", "0000-0001-9076-6066")),
        ("David Lyon (ORCID: [0000-0002-1927-3565](https://orcid.org/0000-0002-1927-3565)) — KBase",
         ("David Lyon", "KBase", "0000-0002-1927-3565")),
    ],
)
def test_a_plain_author_line_with_no_bullet(line, expected) -> None:
    """Regression (Codex adversarial review of #458): five READMEs name their
    author on a bare line under ``## Authors``, which the bullet-only parser
    skipped — so a by-name search found none of that person's projects."""
    [author] = _markdown_authors(f"# P\n\n## Authors\n\n{line}\n\n## Next\nnot an author\n")
    assert (author["name"], author["affiliation"], author["orcid"]) == expected


@pytest.mark.parametrize(
    "line",
    [
        "The following people contributed to this project:",
        "This project was carried out by the BERDL team at LBNL during the 2026 pilot, "
        "with analysis support from several collaborators across the lab.",
        "| Name | ORCID |",
        "> a quote",
    ],
)
def test_prose_under_the_heading_is_not_an_author(line) -> None:
    text = f"## Authors\n{line}\n- Ada Lovelace (https://orcid.org/0000-0001-2345-6789), LBNL\n"
    assert [a["name"] for a in _markdown_authors(text)] == ["Ada Lovelace"]


def test_an_author_split_over_bullets() -> None:
    text = "## Authors\n- **Adam Arkin**\n- ORCID: 0000-0002-4999-2931\n- Affiliation: UC Berkeley\n"
    assert _markdown_authors(text) == [
        {"name": "Adam Arkin", "affiliation": "UC Berkeley", "orcid": "0000-0002-4999-2931"}
    ]


def test_metadata_falls_back_to_readme_authors(tmp_path: Path) -> None:
    """Regression (ISSUE-05): only beril.yaml authors reached
    PROJECT_METADATA.md, so 17 of 78 projects named anyone and a by-author
    search found one of a person's 39 projects."""
    project = tmp_path / "eta"
    project.mkdir()
    (project / "README.md").write_text(
        "# Eta\n\n## Authors\n- Ada Lovelace (https://orcid.org/0000-0001-2345-6789), LBNL\n",
        encoding="utf-8",
    )

    metadata = build_project_metadata(project)

    assert metadata.author_names == ["Ada Lovelace"]
    assert "| Ada Lovelace | LBNL | 0000-0001-2345-6789 |" in metadata.markdown


def test_research_plan_authors_when_the_readme_has_none(tmp_path: Path) -> None:
    project = tmp_path / "theta"
    project.mkdir()
    (project / "README.md").write_text("# Theta\n", encoding="utf-8")
    (project / "RESEARCH_PLAN.md").write_text(
        "# Plan\n\n## Authors\n- Ada Lovelace (ORCID: 0000-0001-2345-6789)\n", encoding="utf-8"
    )
    assert build_project_metadata(project).author_names == ["Ada Lovelace"]


def test_beril_yaml_authors_still_win(tmp_path: Path) -> None:
    project = tmp_path / "iota"
    project.mkdir()
    (project / "beril.yaml").write_text(
        "authors:\n  - {name: From Yaml, orcid: '0000-0009-0000-0001'}\n", encoding="utf-8"
    )
    (project / "README.md").write_text(
        "# Iota\n\n## Authors\n- From Readme (0000-0001-2345-6789)\n", encoding="utf-8"
    )
    assert build_project_metadata(project).author_names == ["From Yaml"]
