---
name: berdl-review
description: Run an independent AI review of a project or research plan. Use when you want feedback without the full /submit checklist.
allowed-tools: Bash, Read, Write
---

# Project Review Skill

Run an independent AI review of a BERDL analysis project or research plan. `/berdl-review` is the canonical review tool: every artifact identifies the exact subject reviewed. Project reviews preserve the report-hash footer contract that `/submit` consumes; plan reviews carry a plan hash. Use it to iterate on feedback during development before approving the project via `/submit`.

The reviewer hunts **evaluation-integrity** failures (selection bias, metric misuse, and — when a model or threshold is fit — train/test leakage and baseline selection) and reads the **numeric cell outputs** (metrics, split sizes, class balances), not just the source. For an adversarial red-team that actively tries to *break* each Key Finding, run `/berdl-refute` after the review.

## Usage

```
/berdl-review <project_id> [--type project|plan] [--reviewer claude|codex] [--model <model_id>]
```

Options:
- `--type project|plan` — Review type (default: `project`)
- `--reviewer claude|codex` — Reviewer backend (default: `claude`)
- `--model <model_id>` — Model override (default: `claude-sonnet-4-20250514` for claude, `gpt-5.4` for codex)

If no `<project_id>` argument is provided, detect from the current working directory (if inside `projects/{id}/`).

## Workflow

### Step 1: Resolve Project

1. Accept `<project_id>` from the argument, or detect from cwd if inside a `projects/` subdirectory
2. Validate that `projects/{project_id}/` exists in the repository root
3. If the directory does not exist, print an error and stop

### Step 2: Status precondition (project reviews only)

Read `projects/{project_id}/beril.yaml` (skip silently if missing — pre-manifest projects bypass this check). For `--type project` reviews:

- **Allowed starting statuses**: `analysis`, `reviewed`, `complete`. Earlier statuses are rejected — there's no `REPORT.md` to review yet.
  - `exploration` / `proposed` / `active` → `FAIL  No REPORT.md to review yet — run /synthesize first (resume via /berdl_start)`.
- **`complete` precondition**: recompute `sha256sum projects/{project_id}/REPORT.md` and compare to `approval.report_hash` in `beril.yaml`. The stored hash uses the `sha256:<hex>` prefix convention (see `/submit`); apply `unprefixed()` to the stored value before comparing to the bare hex from `sha256sum`, otherwise every approved project will look changed and trigger an unnecessary demote prompt. If mismatch:

  > "REPORT.md has changed since this project was approved ({approval.at}). Producing a review against the new report will leave the project in a confusing state: `complete` with a fresh review for an unapproved report. Demote to `analysis` first (the previous approval will be archived under `previous_approvals`) before running the new review? (y/n)"

  - **Yes**: move `approval` to `previous_approvals: []` (append) with an added `archived_at: "<now>"` field, set `status: analysis`, update `README.md` `## Status` to "Analysis — report drafted, awaiting `/berdl-review` and `/submit`.", delete `projects/{project_id}/REVIEW.md` (the canonical copy of the now-archived review), and delete both `SUBMITTED.md` and `SUBMISSION_FAILED.md` if present (audit lives in `beril.yaml`). Then continue to Step 3.
  - **No**: abort. Tell the user to re-run after deciding (either revert REPORT.md, or accept the demote next time).

For `--type plan` reviews this precondition does not apply (plans are reviewed independent of the lifecycle).

### Step 3: Invoke Reviewer

Run `tools/review.sh` — the script automatically numbers the output file and appends exactly one canonical subject footer: `report_hash` for project reviews and `plan_hash` for plan reviews. It hashes before and after the reviewer and discards output if the subject changes:

```bash
bash tools/review.sh {project_id} --type {type} --reviewer {reviewer} --model {model}
```

- Omit `--type` if reviewing the project (default).
- Omit `--reviewer` and `--model` if using defaults.
- The script claims the next available number immediately (race-condition safe).
- The footer is written automatically — **do not** add your own footer manually. The script also performs a TOCTOU check: if `REPORT.md` changed during review, the output file is discarded and the script aborts.

Run this command from the repository root directory.

### Step 4: Verify Review Completion

After the reviewer subprocess completes:

1. Check that the output file was created **and is non-empty** (more than 0 bytes).
2. Confirm the file ends with `<!-- report_hash: sha256:... -->` for a project review or `<!-- plan_hash: sha256:... -->` for a plan review.
3. If the script aborted because of a TOCTOU mismatch, surface that error and explain which subject changed; let it stabilize and re-run.

### Step 5: Update beril.yaml status and README (project reviews only)

For `--type project` reviews against a project at `status: analysis` (or coming out of the `complete`-with-mismatch demote in Step 2), flip status to `reviewed` after the new review writes successfully:

- Update `projects/{project_id}/beril.yaml`:
  - `status: reviewed`
  - `artifacts.review: true` (a review file now exists; this flag tracks the existence of any `REVIEW_N.md`, set here so it's true as soon as the first review lands rather than only after `/submit` writes the canonical `REVIEW.md`).
  - `last_session_at`: current ISO 8601 timestamp.
- Update `projects/{project_id}/README.md` `## Status` to:
  ```
  ## Status

  Reviewed — REVIEW_N.md drafted; awaiting /submit.
  ```
  (Replace `N` with the numbered review just produced.) This keeps the README's user-facing status in sync with `beril.yaml.status`. Without this, the demote-then-review path leaves README stuck on the `analysis` wording even though `beril.yaml` advances to `reviewed`.

For `reviewed` starting status, refresh `README.md` `## Status` similarly (the `N` updates) and ensure `artifacts.review: true` is still set; leave `beril.yaml.status` unchanged. For `complete` (matching hash) starting status, leave both `beril.yaml` and `README.md` unchanged — re-running `/berdl-review` against an approved project only adds another opinion file; the project remains complete. Plan reviews never touch `beril.yaml` or `README.md`.

### Step 6: Present Summary

Read the review file and present a brief summary to the user:
- Overall assessment (from the Summary section).
- Number of suggestions by priority (critical, important, nice-to-have).
- Key issues to address.

### Step 7: Guidance

Based on the review outcome:

**If the review has no critical or important issues**:
- Note that the project looks ready for `/submit`.
- `/submit` will use the latest review (selected by numeric N order) as the canonical record; the user's explicit approval and lakehouse upload turn it into the formal submission.

**If the review has critical or important issues**:
- List the issues to address.
- Offer to help fix them. If fixes touch `REPORT.md`, re-run `/synthesize` first (which silently demotes to `analysis`); existing `REVIEW_N.md` files become stale via hash mismatch.
- Suggest running `/berdl-review` again after fixes to produce a current review.

## Notes

- Reviews are numbered sequentially: `REVIEW_1.md`, `REVIEW_2.md`, `REVIEW_3.md`, … and are **preserved** across `/submit` runs (they form the review history). The latest by numeric N is what `/submit` consults.
- Plan reviews use `PLAN_REVIEW_N.md`; they end with `<!-- plan_hash: sha256:... -->` and have no effect on the project lifecycle.
- Each project review ends with `<!-- report_hash: sha256:... -->`, proving which `REPORT.md` it covered.
- The reviewer prompt is stored at `.claude/reviewer/SYSTEM_PROMPT.md` (project) or `.claude/reviewer/PLAN_REVIEW_PROMPT.md` (plan) and is not controlled by the author.

## Footer invariant

Anything that produces or modifies `REVIEW_N.md` must preserve exactly one final `<!-- report_hash: sha256:[0-9a-f]{64} -->`; `/submit` rejects any deviation. `PLAN_REVIEW_N.md` similarly preserves exactly one final `<!-- plan_hash: sha256:[0-9a-f]{64} -->`.

## Pitfall Detection

When you encounter errors, unexpected results, retry cycles, performance issues, or data surprises during this task, follow the pitfall-capture protocol. Read `.claude/skills/pitfall-capture/SKILL.md` and follow its instructions to determine whether the issue should be added to the active project's `projects/<id>/memories/pitfalls.md`.
