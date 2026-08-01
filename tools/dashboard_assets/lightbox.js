// The figure/document overlay. Inlined into the page by tools/dashboard.py as
// LIGHTBOX_JS, in its own <script>, and self-contained: it reads nothing from
// rel.js, state.js or poll.js.
//
// The overlay is a sibling of #root, and every listener is delegated on
// document, so a trigger stays clickable after the 4s poll swaps #root's
// innerHTML — the trigger elements are replaced, but the handler and the
// overlay are not.
//
// Two modes share one overlay: an <img> for figures, and a scrollable panel
// for markdown fetched from `_doc/` (DOC_ROUTE in dashboard.py, same prefix
// without the leading slash). Sharing it means Esc, the backdrop and the ×
// have exactly one implementation. An <iframe> was the obvious alternative for
// the document mode and was rejected: keystrokes inside an iframe never reach
// the parent document, so Esc would silently stop closing the popup.

(function () {
  const L = document.getElementById('lightbox');
  if (!L) return;
  const I = L.querySelector('img');
  const D = L.querySelector('.lightbox-doc');
  let seq = 0;

  function close() {
    L.classList.remove('active', 'mode-doc');
  }

  function near(t, sel) {
    return t && t.closest ? t.closest(sel) : null;
  }

  function note(cls, msg) {
    D.innerHTML = '<p class="' + cls + '"></p>';
    D.firstChild.textContent = msg;
  }

  document.addEventListener('click', function (e) {
    const fig = near(e.target, '.lightbox-trigger');
    if (fig) {
      I.src = fig.getAttribute('src');
      I.alt = fig.getAttribute('alt') || '';
      L.classList.remove('mode-doc');
      L.classList.add('active');
      return;
    }
    const doc = near(e.target, '.doc-trigger');
    if (doc && e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      const path = doc.getAttribute('data-doc');
      const n = ++seq;
      note('d-empty', 'loading\u2026');
      L.classList.add('active', 'mode-doc');
      D.scrollTop = 0;
      fetch('_doc/' + path.split('/').map(encodeURIComponent).join('/'))
        .then(function (r) {
          return r.ok ? r.text() : r.status;
        })
        .then(function (v) {
          if (n !== seq) return;
          if (typeof v === 'number') {
            note('doc-error', 'could not render ' + path + ' (' + v + ')');
            return;
          }
          D.innerHTML = v;
          D.scrollTop = 0;
        })
        .catch(function () {
          if (n !== seq) return;
          // fetch rejected outright: nothing is serving this page, which is
          // what a written-out dashboard.html opened from disk looks like.
          // Follow the real href instead of leaving an empty overlay open.
          close();
          location.href = doc.getAttribute('href');
        });
      return;
    }
    if (e.target === L || near(e.target, '.lightbox-close')) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') close();
  });
})();
