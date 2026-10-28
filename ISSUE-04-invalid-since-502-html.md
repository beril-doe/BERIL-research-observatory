# An invalid `--since` value returns HTTP 502 with a raw HTML error page instead of a validation error

**Severity:** Medium — unactionable error; user cannot tell bad input from an outage
**Area:** CLI error rendering, request validation
**Labels:** bug, context, ux

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-beril-context-cli`, HEAD `2237c9aa` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` (fronted by Cloudflare) |
| Observed | 2026-10-28 |

## Summary

`beril context find --since <unparseable>` fails with HTTP 502 and dumps ~200 characters
of a Cloudflare HTML error page into the terminal. Bad user input is indistinguishable
from a server outage, and the output is unreadable.

This is two separable defects: **(a)** an invalid time bound is not validated, and
**(b)** the CLI renders a non-JSON error body as raw markup.

## Reproduction

```bash
.venv/bin/beril context find "BERIL" --since 1y --limit 2
```

Actual:

```
error: failed to search (HTTP 502): <!DOCTYPE html>
<!--[if lt IE 7]> <html class="no-js ie6 oldie" lang="en-US"> <![endif]-->
<!--[if IE 7]>    <html class="no-js ie7 oldie" lang="en-US"> <![endif]-->
<!--[if IE 8]>    <html class="no-
```

Expected: something along the lines of

```
error: failed to search (HTTP 422): since: not a recognized time bound; use an ISO date (2026-01-31) or a relative form like 7d / 2w
```

## Which values fail

`1y` is genuinely unsupported — `--since`'s help documents only ISO dates and `7d` / `2w`
forms — so rejecting it is correct. The problem is purely *how* it is rejected: a typo
and a server outage look identical.

| `--since` | Result |
|---|---|
| `7d`, `2w`, `30d`, `90d`, `364d`, `365d`, `400d` | OK |
| `2025-01-01`, `2020-01-01` | OK |
| `1y` | **502 + HTML** |
| `2y` | **502 + HTML** |
| `garbage` | **502 + HTML** |

Note `1y` and `garbage` fail identically, while `365d` — the same window — succeeds. So
this is unit parsing, not window size.

## Contrast with a bound that *is* validated

`limit` is declared with bounds on the request model and produces a clean, actionable
error through the exact same code path:

```
find --limit 99999  -> error: failed to search (HTTP 422): limit: Input should be less than or equal to 200
find --since 1y     -> error: failed to search (HTTP 502): <!DOCTYPE html> ...
```

`_detail()` already renders FastAPI 422 bodies well (`beril_cli/context_client.py:186-193`).
The gap is that `since` never reaches that path.

## Root cause

**(a) Validation is deliberately deferred to the backend.** `ContextQuery`
(`ui/app/context_manager/base.py:169-200`) documents this:

> The time bounds accept whatever the backend accepts (an ISO date, or a relative form
> like `7d`); they are validated as non-empty strings here and interpreted downstream, so
> a malformed bound is the backend's to reject.

Combined with `ui/app/routes/context.py:192-195` — a backend that "rejects or cannot
answer the query surfaces as 502 … its error text is logged rather than returned" — a
malformed bound necessarily becomes an opaque 502. The design is self-consistent; it just
produces an error no caller can act on.

**(b) The HTML dump is client-side.** `beril_cli/context_client.py:184-187`:

```python
try:
    body = response.json()
except ValueError:
    return response.text.strip()[:200] or "no detail"
```

When Cloudflare (not the app) generates the 502, the body is an HTML page and those 200
characters are doctype and IE conditional comments.

## Suggested fix

**(a) Validate the time bounds where `limit` is validated.** Add a field validator to
`ContextQuery` accepting an ISO-8601 date/datetime or `^\d+[dwmy]$`, and reject anything
else with a 422 naming the field. If `y` and `m` are not supported downstream, exclude
them from the pattern so the error says so explicitly rather than failing later. Keep the
CLI help (`context_cmd.py:55-56`) and the accepted grammar in agreement.

**(b) Do not print markup.** In `_detail()`, recognise an HTML body and summarise it:

```python
except ValueError:
    text = response.text.strip()
    lowered = text[:20].lower()
    if lowered.startswith("<!doctype html") or lowered.startswith("<html"):
        # A gateway error page, not a BERIL response — the markup tells the user nothing.
        return f"the gateway returned an error page, not a BERIL response (HTTP {response.status_code})"
    return text[:200] or "no detail"
```

(b) is worth doing regardless of (a), since it also improves every other gateway-level
failure — including ISSUE-01, which surfaces the same wall of HTML.

## Acceptance criteria

- [ ] `find --since 1y` returns a 422 naming `since` and stating the accepted forms.
- [ ] `find --since garbage` likewise.
- [ ] No `beril context` error ever prints raw HTML.
- [ ] Tests cover an invalid time bound and a non-JSON error body.
