// Relative timestamps. Inlined into the page by tools/dashboard.py as REL_JS.
//
// The page ships in two halves because it has two transports and only one of
// them can poll. This is the half that always runs, in live mode and in a
// written-out snapshot alike.
//
// Every timestamp renders client-side from `data-epoch` (see the design doc),
// so without this file the readouts are empty elements — which is why the
// snapshot gets this half rather than no script at all. It is also what keeps
// a *stale* snapshot honest: `relTimes` measures age against the reader's
// clock, not the render time, so an abandoned snapshot visibly ages
// green -> amber -> grey instead of freezing on a green dot.
//
// `R` and `tag` are declared here and read by poll.js, which is concatenated
// into the same <script>. `tag` is *reassigned* there, so it is `let`; making
// it `const` compiles fine and then throws inside a promise whose `.catch` is
// empty, i.e. the page polls forever and never repaints, silently.

const R = document.getElementById('root');
let tag = null;

function rel(s) {
  const d = Math.max(0, Date.now() / 1000 - s);
  if (d < 60) return Math.floor(d) + 's ago';
  if (d < 3600) return Math.floor(d / 60) + 'm ago';
  if (d < 86400) return Math.floor(d / 3600) + 'h ago';
  return Math.floor(d / 86400) + 'd ago';
}

function since(s) {
  const d = Math.max(0, Date.now() / 1000 - s);
  if (d < 3600) return Math.floor(d / 60) + 'm';
  if (d < 86400) return Math.floor(d / 3600) + 'h ' + Math.floor((d % 3600) / 60) + 'm';
  return Math.floor(d / 86400) + 'd';
}

function relTimes() {
  const n = document.querySelectorAll('[data-epoch]');
  for (let i = 0; i < n.length; i++) {
    const el = n[i];
    const s = parseFloat(el.dataset.epoch);
    if (!s) {
      el.textContent = '--';
      continue;
    }
    const age = Date.now() / 1000 - s;
    el.textContent = (el.dataset.mode === 'since') ? since(s) : rel(s);
    if (el.dataset.mode !== 'since') {
      el.className = age < 600 ? 'live' : (age < 3600 ? 'idle' : 'cold');
    }
  }
}

setInterval(relTimes, 15000);
relTimes();
