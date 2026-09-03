#!/usr/bin/env bash
# Build the Quartz site for the OpenKB wiki. Idempotent; first run clones Quartz (~2 min).
#   ./build_quartz.sh            then: cd quartz && npx quartz build --serve
# Serves at http://localhost:8080. The quartz/ clone is gitignored; content is derived.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
QP="$HERE/quartz"

if [ ! -d "$QP" ]; then
  git clone --depth 1 --quiet https://github.com/jackyzha0/quartz.git "$QP"
  npm --prefix "$QP" install --silent
fi

# Quartz 5 reads quartz.config.yaml; derive ours from the shipped default every
# build (idempotent) so theme/config changes here always take effect.
# Palette + type mirror the BERIL workbench themes (apps/web/src/themes.css):
# "paper" light and "observatory" violet-ink dark; Fraunces / IBM Plex.
"$HERE/.venv/bin/python" - "$QP" <<'PY'
import pathlib, sys, yaml
qp = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((qp / "quartz.config.default.yaml").read_text())
c = cfg["configuration"]
c["pageTitle"] = "BERIL Knowledge Wiki"
c["baseUrl"] = "localhost:8080"
c["analytics"] = None
c["theme"]["typography"] = {
    "header": "Fraunces", "body": "IBM Plex Sans", "code": "IBM Plex Mono",
}
c["theme"]["colors"]["lightMode"] = {          # workbench "paper"
    "light": "#faf9f7",        # --background
    "lightgray": "#e5e2db",    # --border
    "gray": "#6f6c7a",         # --muted-foreground
    "darkgray": "#1d1b24",     # --foreground (body text)
    "dark": "#1d1b24",         # headers
    "secondary": "#6d28d9",    # --primary (links, site title)
    "tertiary": "#8b5cf6",     # hover/visited
    "highlight": "rgba(109, 40, 217, 0.08)",
    "textHighlight": "rgba(109, 40, 217, 0.25)",
}
c["theme"]["colors"]["darkMode"] = {           # workbench "observatory"
    "light": "#0b0a10",
    "lightgray": "#272430",
    "gray": "#918e9f",
    "darkgray": "#e7e5ee",
    "dark": "#e7e5ee",
    "secondary": "#a78bfa",
    "tertiary": "#c4b5fd",
    "highlight": "rgba(167, 139, 250, 0.1)",
    "textHighlight": "rgba(167, 139, 250, 0.3)",
}
(qp / "quartz.config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
PY

"$HERE/.venv/bin/python" "$HERE/extra_pages.py"
"$HERE/.venv/bin/python" "$HERE/quartz_ingest.py" "$HERE" "$QP/content"
(cd "$QP" && npx quartz build)
echo
echo "built. serve with:  cd $QP && npx quartz build --serve"
