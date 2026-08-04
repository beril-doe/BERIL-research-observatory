// "The agent needs you" — title marker, favicon dot, waiting strip, OS
// notification. Inlined into the page by tools/dashboard.py as STATE_JS, in
// both transports; poll.js calls the exported `window.dashMark` after a swap.
//
// Client-side for the reason rel.js gives about a 304. The server emits
// `#d-state` inside #root carrying `data-state` and `data-since`, plus an
// optional `#d-detail`; that pair is the whole contract, and `mark()` reads it
// after every swap and drives four things off it.
//
// `#d-detail` is agent-authored text, so it is *not* interpolated here. The
// server renders it through the same `inline_md` -> `e()` path as the worklog
// and this copies the resulting node's HTML verbatim; the escaping decision
// stays in one place, in Python, where it is tested. The notification body
// takes `textContent` instead, since it is not markup at all.
//
// The `(state, since)` pair is the debounce key. Without it every 4s re-render
// is a fresh transition: the strip would re-pulse and the OS notification would
// re-fire for one permission prompt, which is how a notification gets muted.
//
// The explicit `window.dashMark = mark` is load-bearing, not style:
// tests/test_dashboard.py runs this file as an ES module under node, where an
// implicit global would be a ReferenceError, and poll.js calls it by name out
// of the shared scope. The IIFE around it is only hygiene — it keeps the dozen
// locals below out of the one scope this file shares with rel.js and poll.js.

(function () {
  const strip = document.getElementById('d-wait');
  const alertBtn = document.getElementById('d-alert');
  const favicon = document.getElementById('d-favicon');
  const BASE = document.title;
  let last = null;
  let hiddenAt = document.hidden ? Date.now() : 0;

  // Long enough that the reader really has left — and the same 60s Claude
  // Code's own `idle_prompt` notification waits after a Stop.
  const AWAY_MS = 60000;

  const MARK = {waiting: '\u25cf ', turn_ended: '\u2713 '};

  function icon(fill) {
    return 'data:image/svg+xml,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">' +
      '<circle cx="8" cy="8" r="7" fill="' + fill + '"/></svg>');
  }

  const ICON = {
    waiting: icon('#d29922'),
    turn_ended: icon('#3fb950'),
    '': icon('#30363d'),
  };

  document.addEventListener('visibilitychange', function () {
    hiddenAt = document.hidden ? Date.now() : 0;
  });

  function alertable(state) {
    // Stop fires at the end of *every* turn. Notifying on each one gets the
    // whole feature muted inside a day, so it only speaks when the reader has
    // actually been away — the case where they cannot already see it happen.
    if (state === 'waiting') return true;
    return state === 'turn_ended' && hiddenAt > 0 && Date.now() - hiddenAt > AWAY_MS;
  }

  function notify(state, body) {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;
    if (!alertable(state)) return;
    try {
      new Notification(BASE, {body: body, tag: 'beril-' + BASE});
    } catch (err) {}
  }

  function mark() {
    const stateEl = document.getElementById('d-state');
    const detailEl = document.getElementById('d-detail');
    const state = stateEl ? (stateEl.dataset.state || '') : '';
    const key = state + '|' + (stateEl ? stateEl.dataset.since : '');
    document.title = (MARK[state] || '') + BASE;
    if (favicon) favicon.href = ICON[state] || ICON[''];
    if (alertBtn) {
      alertBtn.hidden =
        !('Notification' in window) || Notification.permission !== 'default';
    }
    if (key === last) return;
    if (state === 'waiting' && strip) {
      strip.innerHTML = '<b>The agent is waiting for you.</b> ' +
        (detailEl ? detailEl.innerHTML : '');
      strip.hidden = false;
      strip.classList.remove('pulse');
      void strip.offsetWidth;  // forced reflow — the only way to restart the CSS animation
      strip.classList.add('pulse');
    } else if (strip) {
      strip.hidden = true;
      strip.innerHTML = '';
    }
    // Never on first paint: whatever state the page loaded with is not a
    // transition, so announcing it would re-fire on every reload.
    if (last !== null) notify(state, detailEl ? detailEl.textContent : '');
    last = key;
  }

  if (alertBtn) {
    alertBtn.addEventListener('click', function () {
      Notification.requestPermission().then(function () {
        alertBtn.hidden = true;
      });
    });
  }

  window.dashMark = mark;
  mark();
})();
