// Relative timestamps. Inlined into the page by tools/dashboard.py as REL_JS.
//
// Every timestamp renders client-side from `data-epoch` (see the design doc),
// so without this file the readouts are empty elements — which is why the
// snapshot gets this file rather than no script at all. It is also what keeps
// a *stale* snapshot honest: `relTimes` measures age against the reader's
// clock, not the render time, so an abandoned snapshot visibly ages
// green -> amber -> grey instead of freezing on a green dot.
//
// `rootEl` and `tag` are declared here and read by poll.js, which is
// concatenated into the same <script>. `tag` is *reassigned* there, so it is
// `let`; making it `const` compiles fine and then throws inside a promise whose
// `.catch` is empty, i.e. the page polls forever and never repaints, silently.

const rootEl = document.getElementById('root');
let tag = null;

function age(s) {
  return Math.max(0, Date.now() / 1000 - s);
}

function rel(s) {
  const d = age(s);
  if (d < 60) return Math.floor(d) + 's ago';
  if (d < 3600) return Math.floor(d / 60) + 'm ago';
  if (d < 86400) return Math.floor(d / 3600) + 'h ago';
  return Math.floor(d / 86400) + 'd ago';
}

function since(s) {
  const d = age(s);
  if (d < 3600) return Math.floor(d / 60) + 'm';
  if (d < 86400) return Math.floor(d / 3600) + 'h ' + Math.floor((d % 3600) / 60) + 'm';
  return Math.floor(d / 86400) + 'd';
}

function relTimes() {
  for (const el of document.querySelectorAll('[data-epoch]')) {
    const s = parseFloat(el.dataset.epoch);
    if (!s) {
      el.textContent = '--';
      continue;
    }
    if (el.dataset.mode === 'since') {
      el.textContent = since(s);
      continue;
    }
    const d = age(s);
    el.textContent = rel(s);
    // The liveness colour belongs to this mode only. 10min -> amber, 1h -> grey.
    el.className = d < 600 ? 'live' : (d < 3600 ? 'idle' : 'cold');
  }
}

// Coincidence, not poll.js's hidden cadence: this one repaints text a snapshot
// has no other way to age. A shared constant would be the wrong abstraction.
setInterval(relTimes, 15000);
relTimes();
