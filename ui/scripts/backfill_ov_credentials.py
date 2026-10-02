"""Provision context credentials for users who predate signup provisioning.

Credentials are now minted when a user is first created. This catches up the
accounts that existed before that — and any whose signup coincided with the
backing store being unreachable. Safe to re-run: a user who already has a
credential is not in the worklist.

Run inside the ``ui`` container, where the database and the backing store are
both reachable::

    python scripts/backfill_ov_credentials.py            # provision
    python scripts/backfill_ov_credentials.py --dry-run  # list only

Serial on purpose. The provisioning race that motivated signup provisioning
was two concurrent first-use requests; one process doing one user at a time
cannot reproduce it.

Exit status is non-zero if any user could not be provisioned, so it can gate a
deploy step.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from app.config import get_settings
from app.context_manager.openviking import backfill_ov_credentials
from app.db.session import close_db, get_db, init_db


async def _run(dry_run: bool) -> int:
    settings = get_settings()
    # Same refusal the app makes at startup — nothing can be stored without it.
    settings.require_ov_credential_key()
    await init_db(settings.db_url)
    try:
        # get_db is FastAPI's dependency, but it is just an async generator
        # yielding one session; consuming it this way keeps session setup in
        # one place instead of duplicating it here.
        async for db in get_db():
            attempted, failed = await backfill_ov_credentials(db, dry_run=dry_run)
    finally:
        await close_db()

    verb = "would provision" if dry_run else "provisioned"
    print(f"{verb}: {len(attempted) - len(failed)} user(s)")
    for orcid in attempted:
        if not any(orcid == f[0] for f in failed):
            print(f"  {orcid}")
    if failed:
        print(f"failed: {len(failed)} user(s)", file=sys.stderr)
        for orcid, reason in failed:
            print(f"  {orcid}: {reason}", file=sys.stderr)
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List users who would be provisioned; change nothing.",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args.dry_run)))


if __name__ == "__main__":
    main()
