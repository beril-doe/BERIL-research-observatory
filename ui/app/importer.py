"""Repo-to-database project importer.

Handles the one-time (and ongoing transition-period) migration of projects
from the git repository filesystem into the database and managed filestore.

Key design points:
- Idempotent: safe to run repeatedly; uses ProjectImportRecord to track state.
- Ownership follows one rule (``owner_orcid``): the first author ORCiD in
  beril.yaml, else in an Authors section of README.md, RESEARCH_PLAN.md, or
  another top-level .md file; the BERIL admin account never owns a project.
- Sentinel user (SENTINEL_ORCID) owns projects with no ORCiD — flagged.
- Known ORCiD IDs get a real BerilUser row created on first import; the
  person adopts it at their first ORCiD login.
- A project whose owner changes under the rule is re-imported (re-owned) even
  when its files have not changed.
- Files are physically copied into the managed volume under the same
  {owner_id}/{slug}/uploads/ structure used by user-uploaded files.
- Re-imports a project if its README/PLAN/REPORT mtime is newer than
  last_synced_at on the import record.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import yaml

from app.content_parser import (
    extract_section,
    parse_notebook_metadata,
    parse_project_fields,
    scan_project_files,
)
from app.db.models import (
    BerilUser,
    ChatSession,
    ContextIngestBatch,
    ProjectCollection,
    ProjectContributor,
    ProjectFile,
    ProjectImportRecord,
    ProjectReview,
    UserProject,
)
from app.storage import LocalFileStorage

logger = logging.getLogger(__name__)

SENTINEL_ORCID = "9999-9999-9999-9999"

# The BERIL admin account, listed as a co-author on some projects. It never
# owns one: ownership falls to the next author, as if it were not listed.
ADMIN_AUTHOR_ORCID = "0009-0007-0287-2979"

# An ORCiD iD: four groups of four, the last character a digit or X.
_ORCID = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ImportResult:
    repo_path: str
    status: str  # imported | skipped | failed
    project_id: str | None = None
    message: str = ""
    # The owner's ORCiD; SENTINEL_ORCID when no author has one (flagged).
    owner_orcid: str | None = None


@dataclass
class MigrationSummary:
    total: int = 0
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[ImportResult] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.results is None:
            self.results = []


# ---------------------------------------------------------------------------
# User resolution
# ---------------------------------------------------------------------------


async def _get_or_create_sentinel(db: AsyncSession) -> BerilUser:
    """Return (creating if needed) the sentinel BerilUser for unowned projects."""
    result = await db.execute(
        select(BerilUser).where(BerilUser.orcid_id == SENTINEL_ORCID)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = BerilUser(
            orcid_id=SENTINEL_ORCID,
            display_name="BERIL Repository (unowned)",
            is_active=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Created sentinel user %s", SENTINEL_ORCID)
    return user


@dataclass(frozen=True)
class OwnerClaim:
    """Who a project's files say owns it, and where that was read."""

    orcid: str
    source: str  # the file it came from, e.g. "beril.yaml" or "README.md"
    name: str | None = None
    affiliation: str | None = None


def _authors_section(text: str) -> str:
    return extract_section(text, "Authors") or extract_section(text, "Contributors") or ""


def _author_line(section: str, orcid: str) -> tuple[str | None, str | None]:
    """Best-effort ``(name, affiliation)`` from the author line naming ``orcid``."""
    for line in section.splitlines():
        if orcid not in line:
            continue
        text = re.sub(r"\(?(?:https?://orcid\.org/|ORCID:\s*)?\[?" + re.escape(orcid) + r"\]?(?:\([^)]*\))?\)?", "", line)
        text = re.sub(r"[*|]", " ", text).strip(" -—,\t")
        parts = [p.strip(" ,()") for p in text.split(",", 1)]
        name = parts[0] or None
        affiliation = parts[1] if len(parts) > 1 and parts[1] else None
        return name, affiliation
    return None, None


def owner_orcid(project_dir: Path) -> OwnerClaim | None:
    """The ORCiD that owns a repo project, or None (flag it) if none is found.

    In order, the first author with an ORCiD in:

    1. ``beril.yaml``'s ``authors`` list;
    2. an ``Authors`` (or ``Contributors``) section of ``README.md``, then
       ``RESEARCH_PLAN.md``, then any other top-level ``.md`` file.

    "First author" means the first one *with an ORCiD* — an owner needs one.
    The BERIL admin account is passed over wherever it appears. Read from the
    files directly rather than through ``parse_contributors``, whose formats
    and ORCiD pattern miss real author lines (and every iD ending in ``X``).
    """
    manifest = project_dir / "beril.yaml"
    if manifest.exists():
        try:
            data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, UnicodeDecodeError, RecursionError):
            data = {}
        authors = data.get("authors") if isinstance(data, dict) else None
        for author in authors if isinstance(authors, list) else []:
            if not isinstance(author, dict):
                continue
            orcid = str(author.get("orcid") or "").strip()
            if _ORCID.fullmatch(orcid) and orcid != ADMIN_AUTHOR_ORCID:
                return OwnerClaim(
                    orcid=orcid,
                    source="beril.yaml",
                    name=author.get("name") or None,
                    affiliation=author.get("affiliation") or None,
                )

    named = [project_dir / "README.md", project_dir / "RESEARCH_PLAN.md"]
    others = sorted(
        p for p in project_dir.glob("*.md") if p.name not in {"README.md", "RESEARCH_PLAN.md"}
    )
    for path in [p for p in named if p.exists()] + others:
        try:
            section = _authors_section(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for orcid in _ORCID.findall(section):
            if orcid != ADMIN_AUTHOR_ORCID:
                name, affiliation = _author_line(section, orcid)
                return OwnerClaim(orcid=orcid, source=path.name, name=name, affiliation=affiliation)
    return None


async def resolve_owner(db: AsyncSession, project_dir: Path) -> BerilUser:
    """Return the BerilUser who should own this project (see ``owner_orcid``).

    Creates a stub account for an ORCiD not yet registered — its person adopts
    it at their first ORCiD login. With no ORCiD, the sentinel user owns it.
    """
    claim = owner_orcid(project_dir)
    if claim is None:
        return await _get_or_create_sentinel(db)
    result = await db.execute(select(BerilUser).where(BerilUser.orcid_id == claim.orcid))
    user = result.scalar_one_or_none()
    if user is not None:
        return user
    user = BerilUser(
        orcid_id=claim.orcid, display_name=claim.name, affiliation=claim.affiliation
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        logger.info("Created user for ORCiD %s (%s)", claim.orcid, claim.name)
        return user
    except IntegrityError:
        await db.rollback()
        # Another concurrent import beat us — fetch the now-existing row.
        result = await db.execute(select(BerilUser).where(BerilUser.orcid_id == claim.orcid))
        user = result.scalar_one_or_none()
        if user is None:
            raise
        return user


# ---------------------------------------------------------------------------
# Import record helpers
# ---------------------------------------------------------------------------


async def _get_import_record(db: AsyncSession, repo_path: str) -> ProjectImportRecord | None:
    result = await db.execute(
        select(ProjectImportRecord).where(ProjectImportRecord.repo_path == repo_path)
    )
    return result.scalar_one_or_none()


async def _upsert_import_record(
    db: AsyncSession,
    repo_path: str,
    *,
    project_id: str | None,
    status: str,
    error_message: str | None = None,
) -> ProjectImportRecord:
    record = await _get_import_record(db, repo_path)
    now = datetime.now(timezone.utc)
    if record is None:
        record = ProjectImportRecord(
            repo_path=repo_path,
            project_id=project_id,
            status=status,
            error_message=error_message,
            imported_at=now,
            last_synced_at=now if status == "imported" else None,
        )
        db.add(record)
    else:
        record.project_id = project_id
        record.status = status
        record.error_message = error_message
        if status == "imported":
            record.last_synced_at = now
    await db.commit()
    await db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Staleness check
# ---------------------------------------------------------------------------


def _source_mtime(project_dir: Path) -> datetime:
    """Return the most recent mtime of any importable file in the project directory."""
    scanned = scan_project_files(project_dir)
    if not scanned:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    return max(pf.mtime for pf in scanned)


def _is_stale(record: ProjectImportRecord, project_dir: Path) -> bool:
    """True if any source file is newer than last_synced_at."""
    if record.last_synced_at is None:
        return True
    synced = record.last_synced_at
    if synced.tzinfo is None:
        synced = synced.replace(tzinfo=timezone.utc)
    return _source_mtime(project_dir) > synced


# ---------------------------------------------------------------------------
# File copy
# ---------------------------------------------------------------------------


async def _copy_project_files(
    project_dir: Path,
    storage: LocalFileStorage,
    owner_id: str,
    slug: str,
    project_id: str,
    db: AsyncSession,
) -> int:
    """Copy all files from project_dir into the managed volume and create DB records.

    Returns the number of files copied.

    Old blobs are deleted only after the rows that stop referencing them are
    committed: a file that moved (the project changed owner) or left the
    source tree keeps its old blob until then, so a failure part-way — which
    rolls the rows back — never leaves a row pointing at a deleted blob. The
    worst a failure leaves is a new copy nothing references yet, which the
    retried import writes over.
    """
    copied = 0
    scanned = scan_project_files(project_dir)
    superseded: list[str] = []

    for pf in scanned:
        src = project_dir / pf.relative_path
        storage_path = f"{owner_id}/{slug}/uploads/{pf.relative_path}"

        # Determine title for notebooks
        title: str | None = None
        description: str | None = None
        if pf.file_type == "notebook":
            nb_meta = parse_notebook_metadata(src)
            title = nb_meta.title
            description = nb_meta.description

        data = src.read_bytes()
        size = await storage.save(data, storage_path)

        # Upsert the DB record (unique on project_id + filename + source)
        result = await db.execute(
            select(ProjectFile).where(
                ProjectFile.project_id == project_id,
                ProjectFile.filename == pf.relative_path,
                ProjectFile.source == "repo_import",
            )
        )
        existing = result.scalar_one_or_none()

        if existing is not None:
            if existing.storage_path != storage_path:
                # The project changed owner, so its files moved. The old copy
                # goes once the new path is committed (below).
                superseded.append(existing.storage_path)
            existing.storage_path = storage_path
            existing.size_bytes = size
            existing.content_type = pf.content_type
            existing.last_updated_at = pf.mtime
            existing.title = title or existing.title
            existing.description = description or existing.description
        else:
            db.add(ProjectFile(
                project_id=project_id,
                file_type=pf.file_type,
                filename=pf.relative_path,
                storage_path=storage_path,
                size_bytes=size,
                content_type=pf.content_type,
                title=title,
                description=description,
                is_public=True,  # repo projects are public by default
                source="repo_import",
                last_updated_at=pf.mtime,
            ))
        copied += 1

    # Delete ProjectFile rows (and storage blobs) for files no longer in the source tree
    scanned_paths = {pf.relative_path for pf in scanned}
    existing_result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.project_id == project_id,
            ProjectFile.source == "repo_import",
        )
    )
    for row in existing_result.scalars().all():
        if row.filename not in scanned_paths:
            superseded.append(row.storage_path)
            await db.delete(row)

    await db.commit()
    # Best-effort: the rows are committed and none references these blobs any
    # more, so a failed delete only leaves an orphaned file. It must not abort
    # the remaining deletes or report a completed import as failed — and no
    # later run would see the path again, so it is logged for manual cleanup.
    for path in superseded:
        try:
            await storage.delete(path)
        except OSError as exc:
            logger.warning("Could not delete superseded blob %s (orphaned): %s", path, exc)
    return copied


# ---------------------------------------------------------------------------
# Reconciling an owner's own row
# ---------------------------------------------------------------------------


async def _merge_into_owners_row(
    db: AsyncSession,
    *,
    repo_row: UserProject | None,
    owners_row: UserProject,
    repo_path: str,
) -> UserProject:
    """Make the owner's own row the repo project's row, folding in the old one.

    The owner's row survives: it holds their own submissions (context records
    under their namespace) and is what their own links point to; public
    project pages are addressed by directory name, so nothing public moves.
    Everything that belonged to the repo row moves onto it — imported files,
    reviews, chat sessions, context records (so a copy under the previous
    owner is still planned for removal), and the import record. Contributors
    and collections are not moved: the import re-syncs them onto the owner's
    row straight after this. Then the repo row is deleted.

    With no repo row yet (first import), the owner's row is simply adopted.
    """
    if repo_row is not None:
        old_id, new_id = repo_row.id, owners_row.id
        for model in (ProjectFile, ProjectReview, ChatSession, ContextIngestBatch, ProjectImportRecord):
            await db.execute(
                update(model).where(model.project_id == old_id).values(project_id=new_id)
            )
        for model in (ProjectContributor, ProjectCollection):
            await db.execute(delete(model).where(model.project_id == old_id))
        owners_row.is_public = owners_row.is_public or repo_row.is_public
        db.expunge(repo_row)
        await db.execute(delete(UserProject).where(UserProject.id == old_id))
        logger.info(
            "Merged repo project %s (%s) into its owner's row %s", repo_path, old_id, new_id
        )
    else:
        # A repo project is public, as one the importer creates would be.
        owners_row.is_public = True
    owners_row.repo_path = repo_path
    owners_row.origin = "repo"
    await db.commit()
    await db.refresh(owners_row)
    return owners_row


# ---------------------------------------------------------------------------
# Single-project import
# ---------------------------------------------------------------------------


async def import_project(
    db: AsyncSession,
    storage: LocalFileStorage,
    project_dir: Path,
    repo_root: Path,
) -> ImportResult:
    """Idempotently import one project directory into the DB and filestore.

    - Skips if already imported and source files haven't changed.
    - Re-imports (upserts) if source files are newer than last_synced_at.
    """
    repo_path = str(project_dir.relative_to(repo_root))  # e.g. "projects/my_project"
    slug = project_dir.name

    readme_path = project_dir / "README.md"
    if not readme_path.exists():
        return ImportResult(repo_path=repo_path, status="skipped", message="No README.md")

    # Check import record. Unchanged files are not enough to skip: the
    # ownership rule may now name a different owner (a rule change, or an
    # author list edited only in beril.yaml), and that re-owns the project.
    record = await _get_import_record(db, repo_path)
    if record is not None and record.status == "imported" and not _is_stale(record, project_dir):
        claim = owner_orcid(project_dir)
        wanted = claim.orcid if claim else SENTINEL_ORCID
        current = await db.execute(
            select(BerilUser.orcid_id)
            .join(UserProject, UserProject.owner_id == BerilUser.id)
            .where(UserProject.repo_path == repo_path)
        )
        if current.scalar_one_or_none() == wanted:
            return ImportResult(
                repo_path=repo_path,
                status="skipped",
                project_id=record.project_id,
                message="Up to date",
                owner_orcid=wanted,
            )

    try:
        # Parse content
        readme = readme_path.read_text(encoding="utf-8")
        plan_path = project_dir / "RESEARCH_PLAN.md"
        report_path = project_dir / "REPORT.md"
        plan = plan_path.read_text(encoding="utf-8") if plan_path.exists() else None
        report = report_path.read_text(encoding="utf-8") if report_path.exists() else None

        parsed = parse_project_fields(readme, plan, report, project_id=slug)

        # Resolve owner
        owner = await resolve_owner(db, project_dir)

        # Upsert UserProject — match on repo_path slug
        result = await db.execute(
            select(UserProject).where(UserProject.repo_path == repo_path)
        )
        project = result.scalar_one_or_none()

        # The owner may already have a row of their own for this slug — they
        # /submit-ted the project while the repo row belonged to someone else
        # (the sentinel, under the old ownership rule). (owner_id, slug) is
        # unique, so fold the repo row into theirs rather than collide.
        own = (
            await db.execute(
                select(UserProject).where(
                    UserProject.owner_id == owner.id, UserProject.slug == slug
                )
            )
        ).scalar_one_or_none()
        if own is not None and (project is None or own.id != project.id):
            project = await _merge_into_owners_row(
                db, repo_row=project, owners_row=own, repo_path=repo_path
            )

        other_sections_json = json.dumps(parsed.other_sections) if parsed.other_sections else None

        if project is None:
            project = UserProject(
                owner_id=owner.id,
                slug=slug,
                title=parsed.title,
                research_question=parsed.research_question,
                status=parsed.status,
                hypothesis=parsed.hypothesis,
                approach=parsed.approach,
                findings=parsed.findings,
                overview=parsed.overview,
                results=parsed.results,
                interpretation=parsed.interpretation,
                limitations=parsed.limitations,
                future_directions=parsed.future_directions,
                data_section=parsed.data_section,
                references_text=parsed.references_text,
                revision_history=parsed.revision_history,
                other_sections=other_sections_json,
                raw_readme=parsed.raw_readme,
                research_plan_raw=parsed.research_plan_raw,
                report_raw=parsed.report_raw,
                origin="repo",
                repo_path=repo_path,
                is_public=True,
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)
        else:
            # Update all parsed fields
            project.owner_id = owner.id
            project.title = parsed.title
            project.research_question = parsed.research_question
            project.status = parsed.status
            project.hypothesis = parsed.hypothesis
            project.approach = parsed.approach
            project.findings = parsed.findings
            project.overview = parsed.overview
            project.results = parsed.results
            project.interpretation = parsed.interpretation
            project.limitations = parsed.limitations
            project.future_directions = parsed.future_directions
            project.data_section = parsed.data_section
            project.references_text = parsed.references_text
            project.revision_history = parsed.revision_history
            project.other_sections = other_sections_json
            project.raw_readme = parsed.raw_readme
            project.research_plan_raw = parsed.research_plan_raw
            project.report_raw = parsed.report_raw
            await db.commit()
            await db.refresh(project)

        # Sync contributors: update/insert parsed names, delete names no longer present
        existing_contribs = await db.execute(
            select(ProjectContributor).where(ProjectContributor.project_id == project.id)
        )
        existing_by_name = {c.name: c for c in existing_contribs.scalars().all()}
        parsed_names = {c.name for c in parsed.contributors}

        for name, ec in existing_by_name.items():
            if name not in parsed_names:
                await db.delete(ec)

        for contrib in parsed.contributors:
            if contrib.name in existing_by_name:
                ec = existing_by_name[contrib.name]
                ec.orcid_id = contrib.orcid or ec.orcid_id
                ec.role = ", ".join(contrib.roles) if contrib.roles else ec.role
            else:
                db.add(ProjectContributor(
                    project_id=project.id,
                    name=contrib.name,
                    orcid_id=contrib.orcid,
                    role=", ".join(contrib.roles) if contrib.roles else "Author",
                ))
        await db.commit()

        # Sync collection references: add new, remove stale
        existing_colls = await db.execute(
            select(ProjectCollection).where(ProjectCollection.project_id == project.id)
        )
        existing_coll_rows = {c.collection_id: c for c in existing_colls.scalars().all()}
        parsed_coll_ids = set(parsed.related_collections)

        for coll_id, row in existing_coll_rows.items():
            if coll_id not in parsed_coll_ids:
                await db.delete(row)

        for coll_id in parsed_coll_ids:
            if coll_id not in existing_coll_rows:
                db.add(ProjectCollection(project_id=project.id, collection_id=coll_id))
        await db.commit()

        # Copy files
        n_files = await _copy_project_files(
            project_dir, storage, owner.id, slug, project.id, db
        )

        await _upsert_import_record(
            db, repo_path, project_id=project.id, status="imported"
        )

        logger.info(
            "Imported project %r → %s (%d files, owner=%s)",
            slug, project.id, n_files, owner.orcid_id,
        )
        message = f"{n_files} files copied"
        if owner.orcid_id == SENTINEL_ORCID:
            message += "; flagged: no author ORCiD found"
        return ImportResult(
            repo_path=repo_path,
            status="imported",
            project_id=project.id,
            message=message,
            owner_orcid=owner.orcid_id,
        )

    except Exception as exc:
        await db.rollback()
        logger.exception("Failed to import project %r", repo_path)
        await _upsert_import_record(
            db, repo_path, project_id=None, status="failed",
            error_message=str(exc)[:1000],
        )
        return ImportResult(
            repo_path=repo_path,
            status="failed",
            message=str(exc),
        )


# ---------------------------------------------------------------------------
# Full migration runner
# ---------------------------------------------------------------------------


async def run_full_migration(
    db: AsyncSession,
    storage: LocalFileStorage,
    projects_root: Path,
) -> MigrationSummary:
    """Import all project directories under projects_root.

    Safe to call repeatedly — already-imported, unchanged projects are skipped.
    """
    summary = MigrationSummary()

    if not projects_root.exists():
        logger.warning("projects_root does not exist: %s", projects_root)
        return summary

    project_dirs = sorted(
        d for d in projects_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    summary.total = len(project_dirs)

    for project_dir in project_dirs:
        result = await import_project(db, storage, project_dir, projects_root.parent)
        summary.results.append(result)
        if result.status == "imported":
            summary.imported += 1
        elif result.status == "skipped":
            summary.skipped += 1
        else:
            summary.failed += 1

    logger.info(
        "Migration complete: %d imported, %d skipped, %d failed (total %d)",
        summary.imported, summary.skipped, summary.failed, summary.total,
    )
    return summary
