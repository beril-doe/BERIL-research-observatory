// The 4s poll. Inlined into the page by tools/dashboard.py as POLL_JS.
//
// DEPENDS ON ITS SIBLINGS, with nothing in the language to say so. Python
// concatenates rel.js, state.js and this file into ONE <script>, in that
// order, so all three share a single top-level scope:
//
//   rootEl, tag, relTimes  <- rel.js   (`tag` is reassigned below, hence `let`)
//   dashMark               <- state.js (exported as window.dashMark)
//
// Nothing reads back out: `timer` and `tick` are this file's own, which is what
// makes `let timer` safe here.
//
// Order and tag count do not matter: top-level let/const/function in *classic*
// scripts land in the realm's global scope, so three separate <script> tags in
// any order behave identically. One tag is a convenience, not a constraint.
//
// Two things sever that scope: an IIFE around a sibling, and `type="module"`.
// Both are checked by
// tests/test_dashboard.py::test_the_live_scripts_parse_and_share_one_scope,
// which compiles the three together and drives one `tick()`.
//
// The two symptoms are not the same, which matters when debugging one: `tag` is
// read synchronously on tick's first line, so losing it throws out of the
// setTimeout callback and the poll stops dead — loud. `rootEl`, `relTimes` and
// `dashMark` are only touched inside the `.then` chain, whose `.catch` is
// empty, so losing one is swallowed: the page keeps polling forever, never
// repaints, and the console stays clean.
//
// Emitted **only in live mode**, and both of the outer statements are why: the
// trailing-slash redirect and the `fetch` are each actively wrong on a
// snapshot.
//
// - The redirect exists so relative asset URLs resolve under `/proxy/<port>`.
//   A snapshot is served at `<prefix>files/<rel>/dashboard.html`, which does
//   not end in `/`, so this line would navigate the page to `dashboard.html/`
//   — a Jupyter 404. The page would destroy itself on load.
// - `files/` responses carry `Content-Security-Policy: sandbox allow-scripts`
//   with no `allow-same-origin` (measured against the live server), so the
//   document has an opaque origin and `fetch` cannot send the hub cookie. The
//   poll could only ever fail, silently, forever.
//
// **A hidden tab still fetches**, at 15s instead of 4s. It used to skip the
// fetch entirely, which is cheaper and wrong: a backgrounded tab is exactly
// the tab that needs to learn the agent is blocked on a permission prompt, and
// one that never fetches can never learn anything — it has only the title and
// the favicon to speak through, and both are painted from the response. The
// cost is small enough to check rather than argue about: a 304 costs one
// `fingerprint()` at 0.25-0.84ms measured across the three largest projects on
// disk, so 15s hidden is under 0.2s of CPU per hour per tab. It used to run a
// whole `scan()` at 6.8ms, which is what this interval was chosen against.
//
// The single `timer` handle is not decoration. `tick` schedules the next tick,
// and the visibilitychange listener calls `tick` directly, so every return to
// the tab used to start a second concurrent chain that never ended.

if (!location.pathname.endsWith('/')) location.replace(location.pathname + '/');

let timer = 0;

function tick() {
  const h = tag ? {'If-None-Match': tag} : {};
  fetch('.', {headers: h}).then(function (r) {
    if (r.status !== 200) return null;
    tag = r.headers.get('ETag');
    return r.text();
  }).then(function (t) {
    if (!t) return;
    const open = [];
    for (const d of rootEl.querySelectorAll('details[open]')) if (d.id) open.push(d.id);
    const doc = new DOMParser().parseFromString(t, 'text/html');
    const next = doc.getElementById('root');
    if (!next) return;
    rootEl.innerHTML = next.innerHTML;
    for (const id of open) {
      const d = rootEl.querySelector('#' + CSS.escape(id));
      if (d) d.open = true;
    }
    relTimes();
    dashMark();
  }).catch(function () {});
  clearTimeout(timer);
  timer = setTimeout(tick, document.hidden ? 15000 : 4000);
}

document.addEventListener('visibilitychange', function () {
  if (document.visibilityState === 'visible') tick();
});

timer = setTimeout(tick, 4000);
