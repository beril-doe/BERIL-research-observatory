#!/usr/bin/env bash
# Rebuild the Quartz reader prototype from scratch. Idempotent; ~2 min (npm install dominates).
#   ./build-quartz-proto.sh          then: cd quartz-proto && npx quartz build --serve
# Leaves the Cosma export untouched — the two are meant to be compared side by side.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
QP="$HERE/quartz-proto"
WIKI="$HERE/wiki"

rm -rf "$QP"
git clone -b v4 --depth 1 --quiet https://github.com/jackyzha0/quartz.git "$QP"
npm --prefix "$QP" install --silent

rm -rf "$QP/content"
python3 "$HERE/quartz_ingest.py" "$WIKI" "$QP/content"

# Config: local prototype + the load-bearing bit — our links are real relative paths.
python3 - "$QP/quartz.config.ts" <<'PY'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
edits = [
    ('pageTitle: "Quartz 4"', 'pageTitle: "BERIL Compendium"'),
    ('baseUrl: "quartz.jzhao.xyz"', 'baseUrl: "localhost:8080"'),
    ('ignorePatterns: ["private", "templates", ".obsidian"]',
     'ignorePatterns: ["private", "templates", ".obsidian", ".manifests"]'),
    ('markdownLinkResolution: "shortest"', 'markdownLinkResolution: "relative"'),
    ("      Plugin.CustomOgImages(),\n", ""),  # slow, useless locally
]
for old, new in edits:
    assert old in s, f"quartz.config.ts shape changed: {old!r}"
    s = s.replace(old, new)
s = re.sub(r"analytics:\s*\{[^}]*\},", "analytics: null,", s, count=1)
p.write_text(s)
PY

# Color graph nodes by record type (no Quartz config option exists for this).
python3 - "$QP/quartz/components/scripts/graph.inline.ts" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
old = '''  const color = (d: NodeData) => {
    const isCurrent = d.id === slug
    if (isCurrent) {
      return computedStyleMap["--secondary"]
    } else if (visited.has(d.id) || d.id.startsWith("tags/")) {
      return computedStyleMap["--tertiary"]
    } else {
      return computedStyleMap["--gray"]
    }
  }'''
new = '''  const color = (d: NodeData) => {
    const id = d.id
    if (id === slug) return computedStyleMap["--secondary"]
    if (id === "index" || id === "" || id === "/") return "#b478ff"
    if (id.startsWith("topics/")) return "#5b8cff"
    if (id.startsWith("projects/")) return "#8a94a6"
    if (id.startsWith("authors/")) return "#e0883b"
    if (id.startsWith("data/")) return "#37b98b"
    if (id.startsWith("tags/")) return computedStyleMap["--tertiary"]
    return computedStyleMap["--gray"]
  }'''
assert old in s, "graph.inline.ts color() shape changed"
p.write_text(s.replace(old, new))
PY

# These point outside the wiki tree (../../../projects/*/REPORT.md) and 404.
grep -rl 'Open the full report' "$QP/content/projects" | xargs sed -i '' -E \
  's#\[Open the full report →\]\([^)]*\)#*(Full source report — not in this prototype.)*#'

(cd "$QP" && npx quartz build)
echo
echo "built. serve with:  cd $QP && npx quartz build --serve"
echo "then open:          http://localhost:8080"
