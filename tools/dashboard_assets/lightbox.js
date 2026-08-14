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
  const overlay = document.getElementById('lightbox');
  if (!overlay) return;
  const img = overlay.querySelector('img');
  const panel = overlay.querySelector('.lightbox-doc');
  let seq = 0;

  function close() {
    overlay.classList.remove('active', 'mode-doc');
  }

  function note(cls, msg) {
    panel.innerHTML = '<p class="' + cls + '"></p>';
    panel.firstChild.textContent = msg;
  }

  document.addEventListener('click', function (e) {
    const t = e.target;
    if (!t || !t.closest) return;
    const fig = t.closest('.lightbox-trigger');
    if (fig) {
      img.src = fig.getAttribute('src');
      img.alt = fig.getAttribute('alt') || '';
      overlay.classList.remove('mode-doc');
      overlay.classList.add('active');
      return;
    }
    const doc = t.closest('.doc-trigger');
    if (doc && e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      const path = doc.getAttribute('data-doc');
      const n = ++seq;
      note('d-empty', 'loading\u2026');
      overlay.classList.add('active', 'mode-doc');
      panel.scrollTop = 0;
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
          panel.innerHTML = v;
          panel.scrollTop = 0;
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
    if (t === overlay || t.closest('.lightbox-close')) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') close();
  });
})();
