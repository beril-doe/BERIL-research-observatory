// "The agent needs you" — title marker, favicon dot, waiting strip, OS
// notification. Inlined into the page by tools/dashboard.py as STATE_JS, in
// both transports; poll.js calls the exported `window.dashMark` after a swap.
//
// Everything here is client-side for the same reason relative times are: a 304
// freezes whatever the server wrote, and this is the one readout whose whole
// job is to be current. The server emits `#d-state` inside #root carrying
// `data-state` and `data-since`; `mark()` reads them after every swap and
// drives four things off them.
//
// Two channels reach a reader who is not looking at the page — the title marker
// and the favicon — and they are the only two a browser gives a foreground tab.
// A closed tab gets nothing without a service worker and a push service, which
// a stdlib server inside a pod cannot be.
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
  const W = document.getElementById('d-wait');
  const B = document.getElementById('d-alert');
  const F = document.getElementById('d-favicon');
  const BASE = document.title;
  let last = null;
  let hiddenAt = document.hidden ? Date.now() : 0;

  const MARK = {waiting: '\u25cf ', turn_ended: '\u2713 '};

  function icon(c) {
    return 'data:image/svg+xml,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">' +
      '<circle cx="8" cy="8" r="7" fill="' + c + '"/></svg>');
  }

  const ICON = {
    waiting: icon('#d29922'),
    turn_ended: icon('#3fb950'),
    '': icon('#30363d'),
  };

  document.addEventListener('visibilitychange', function () {
    hiddenAt = document.hidden ? Date.now() : 0;
  });

  function alertable(s) {
    // Stop fires at the end of *every* turn. Notifying on each one gets the
    // whole feature muted inside a day, so it only speaks when the reader has
    // actually been away — the case where they cannot already see it happen.
    if (s === 'waiting') return true;
    return s === 'turn_ended' && hiddenAt > 0 && Date.now() - hiddenAt > 60000;
  }

  function notify(s, body) {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;
    if (!alertable(s)) return;
    try {
      new Notification(BASE, {body: body, tag: 'beril-' + BASE});
    } catch (err) {}
  }

  function mark() {
    const c = document.getElementById('d-state');
    const d = document.getElementById('d-detail');
    const s = c ? (c.dataset.state || '') : '';
    const key = s + '|' + (c ? c.dataset.since : '');
    document.title = (MARK[s] || '') + BASE;
    if (F) F.href = ICON[s] || ICON[''];
    if (B) B.hidden = !('Notification' in window) || Notification.permission !== 'default';
    if (key === last) return;
    if (s === 'waiting' && W) {
      W.innerHTML = '<b>The agent is waiting for you.</b> ' + (d ? d.innerHTML : '');
      W.hidden = false;
      W.classList.remove('pulse');
      void W.offsetWidth;
      W.classList.add('pulse');
    } else if (W) {
      W.hidden = true;
      W.innerHTML = '';
    }
    if (last !== null) notify(s, d ? d.textContent : '');
    last = key;
  }

  if (B) {
    B.addEventListener('click', function () {
      Notification.requestPermission().then(function () {
        B.hidden = true;
      });
    });
  }

  window.dashMark = mark;
  mark();
})();
