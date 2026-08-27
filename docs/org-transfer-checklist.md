# Org Transfer Checklist: `kbaseincubator` → `beril-doe`

Working checklist for moving `BERIL-research-observatory` between GitHub orgs.

The code and docs changes are already staged on the `org-move-beril-doe` branch
(see [What's already done](#whats-already-done) at the bottom). Everything in
the numbered sections below is **manual work outside the repo** — org settings,
secrets, and the SPIN deployment — that a commit can't do for you.

Ordering matters: the pre-transfer items avoid a window where `main` is
unprotected or CI is broken.

---

## 1. Before the transfer

- [x] ~~**Create the `beril-maintainers` team in `beril-doe`.**~~ Already exists
      with 8 members (`cmungall`, `justaddcoffee`, `nlharris`, `briehl`,
      `mikacashman`, `dileep-kishore`, `psdehal`, `turbomam`). Teams are
      org-scoped and do **not** follow a repo transfer, so this being in place
      already is what makes the CODEOWNERS change safe to merge.
- [ ] **Compare membership against the `kbaseincubator` team** and reconcile any
      difference before the transfer, so review coverage doesn't quietly change.
      As of writing, the `beril-doe` team's only repo grant is
      `beril-doe/beril-workbench` — it has **no** access to this repo yet
      (granted in step 3).
- [ ] **Confirm you have permission to transfer.** You need admin on the repo
      *and* the ability to create repos in `beril-doe`.
- [ ] **Inventory secrets that are inherited from the org rather than set on the
      repo.** Repo-level secrets survive the transfer; org-level ones vanish
      silently. Check Settings → Secrets and variables → Actions and note which
      are "Organization secrets". At minimum these are referenced by workflows:
    - [ ] `SPIN_RANCHER_API_KEY`
    - [ ] `RANCHER_DEV_PROJECT_ID`
    - [ ] `RANCHER_PROD_PROJECT_ID`
    - [ ] `CODECOV_TOKEN`
    - [ ] `DATA_UPDATE_WEBHOOK_URL`
    - [ ] `DATA_UPDATE_WEBHOOK_SECRET`
- [ ] **Record current branch protection rules on `main`** — they do transfer,
      but rules referencing the old team need re-pointing, so screenshot them.
- [ ] **Note the currently deployed image digest** in SPIN, so you can roll back
      if the new image path misbehaves:
      `rancher kubectl -n beril get deploy/observatory-ui -o jsonpath='{.spec.template.spec.containers[*].image}'`

## 2. Do the transfer

- [ ] Settings → General → Danger Zone → Transfer ownership → `beril-doe`.
- [ ] Confirm the redirect works: `git ls-remote https://github.com/kbaseincubator/BERIL-research-observatory` should resolve.

## 3. Immediately after — restore what didn't follow

- [ ] **Grant the `beril-maintainers` team write access to the transferred repo.**
      CODEOWNERS silently no-ops if the team can't be resolved *or* lacks write
      access — there is no error, review enforcement just stops.
- [ ] **Re-add any org-level secrets** identified in step 1 (as `beril-doe` org
      secrets, or repo-level if that's simpler).
- [ ] **Re-enable GitHub Actions if disabled.** Transfers can leave workflows
      paused pending review.
- [ ] **Re-apply branch protection on `main`**, re-pointing any required-reviewer
      rules at `@beril-doe/beril-maintainers`.
- [ ] **Verify CODEOWNERS resolves.** Open a throwaway PR touching `ui/` and
      confirm the team is auto-requested as reviewer. If no reviewer appears,
      the team ref or its access is still wrong.

## 4. Container registry (GHCR)

The published image path changes from
`ghcr.io/kbaseincubator/microbial-data-forge` to
`ghcr.io/beril-doe/microbial-data-forge`.

- [ ] **Confirm the package transferred** and is visible under the `beril-doe`
      org packages.
- [ ] **Check package visibility** (public vs private) survived — this resets
      more often than you'd expect.
- [ ] **Re-link the package to the repo** (package settings → Manage Actions
      access) so `secrets.GITHUB_TOKEN` retains push rights.
- [ ] **Trigger `build-image.yml` manually** (`workflow_dispatch`) and confirm it
      pushes to the new path successfully.

## 5. SPIN / Rancher deployment — the silent-failure one

`deploy-spin-prod.yml` only runs `rollout restart`. It does **not** set the image.
The image lives in the k8s manifest in Rancher, outside this repo. If you don't
update it, the restart will *succeed* while continuing to deploy the old
`kbaseincubator` image — green checkmark, stale code.

- [ ] **Update the image in the prod deployment** (`beril` namespace,
      `observatory-ui`) to `ghcr.io/beril-doe/microbial-data-forge:latest`.
- [ ] **Update the dev deployment** (`knowledge-engine` namespace,
      `beril-develop`) the same way.
- [ ] **Update any imagePullSecrets** if the package is private and the
      credential was scoped to the old org.
- [ ] **Update `BERIL_DATA_REPO_URL`** in the deployment env to
      `https://github.com/beril-doe/BERIL-research-observatory.git`.
      Read at [ui/app/config.py:26](../ui/app/config.py#L26); the old URL will
      keep working via redirect, so this will *not* announce itself as broken.
- [ ] **Run `deploy-spin-dev` manually first** and verify the pod comes up on the
      new image before letting a push to `main` fire the prod path.

## 6. Third-party integrations

- [ ] **Codecov** — re-link the repo under the new owner. The upload token is
      per-repo and Codecov keys off `owner/slug`. Uploads will start failing (or
      silently landing on a dead project) until this is done. Update
      `CODECOV_TOKEN` if it's reissued.
- [ ] **The data-cache webhook.** `build-data-cache.yml` POSTs to
      `DATA_UPDATE_WEBHOOK_URL` with an HMAC signature. Confirm the receiving
      service still trusts the caller and the secret matches.
- [ ] **Any external service pinned to the old clone URL** — CI elsewhere,
      JupyterHub bootstrap scripts, cron jobs on the cluster. Redirects cover
      these for now, but they break permanently if the old name is ever reused.
- [ ] **Local clones** (yours and collaborators'): remotes keep working via
      redirect, but worth updating —
      `git remote set-url origin https://github.com/beril-doe/BERIL-research-observatory.git`

## 7. Verify end to end

- [ ] Open a PR → `run-cli-tests` and `run-webapp-tests` both pass, Codecov
      comments.
- [ ] PR touching `ui/` auto-requests `@beril-doe/beril-maintainers`.
- [ ] Merge to `main` → image builds and pushes to `ghcr.io/beril-doe/...`.
- [ ] `deploy-spin-prod` runs and the pod actually picks up the new image
      (check the running image digest, not just rollout status).
- [ ] `build-data-cache` pushes to the `data-cache` branch and the webhook fires.
- [ ] Run a `beril submit` end to end and confirm `project_metadata.json`
      records `git_repo` as the `beril-doe` URL.

---

## What's already done

Staged on the `org-move-beril-doe` branch — no action needed beyond review and
merge:

| Change | File |
| --- | --- |
| CODEOWNERS team refs → `@beril-doe/beril-maintainers` (5 paths) | [.github/CODEOWNERS](../.github/CODEOWNERS) |
| Image path pinned explicitly instead of derived from `github.repository_owner`, and the previously-dead `IMAGE_NAME` env var wired into the `meta` step | [.github/workflows/build-image.yml](../.github/workflows/build-image.yml) |
| `git_repo` provenance now derived from the actual git remote instead of a hard-coded literal | [tools/lakehouse_upload.py](../tools/lakehouse_upload.py) |
| Setup-wizard clone URL moved to a `CLONE_URL` module constant, pointed at the new org | [beril_cli/setup_cmd.py](../beril_cli/setup_cmd.py) |
| Clone URLs in docs | [README.md](../README.md), [docs/getting_started.md](getting_started.md), [ui/README.md](../ui/README.md) |
| Test fixture org slugs | [tests/beril_cli/test_cli_start.py](../tests/beril_cli/test_cli_start.py) |

### Deliberately left alone

- **`ghcr.io/kbaseincubator/cdm_*` images** in `.claude/skills/remote-compute/`
  are separate CDM tool containers, unrelated to this repo's build artifacts.
- **`beril_cli/start.py`** derives its repo slug from the live git remote and
  hits the GitHub API, which redirects on renamed repos. It picks up the new
  org automatically.
- **Historical absolute paths** (`/home/aparkin/...`) in `DATA_INVENTORY.md`,
  `DATA_QUICK_REFERENCE.txt`, `README_DATA.md`, and `DATA_ACCESS_EXAMPLES.py`
  are unrelated to the org move.
