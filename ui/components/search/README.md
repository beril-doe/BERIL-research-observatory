# Search island

React component for the OpenViking search page. Built with esbuild into a single
ES-module bundle that the Jinja page loads via dynamic `import()`.

## Build

```bash
cd ui/components/search
npm install
npm run build     # -> ui/app/static/search/search.js (+ .map)
```

`npm run watch` rebuilds on change during development.

## How it mounts

`src/index.jsx` installs `window.BERILSearch.mount(root, props)`. The page
`ui/app/templates/search.html` dynamically imports `/static/search/search.js`,
then calls `window.BERILSearch.mount(root, { searchEndpoint: "/api/search" })`.

The component `fetch`es `GET /api/search?q=...&limit=...` (served by
`ui/app/routes/search.py`) and renders each result's summary (abstract). Expected
failures come back as `{error, message}` JSON and render as an inline notice.

## Conventions (this is the reference island)

- Source lives here under `src/`; the built bundle is committed to
  `ui/app/static/search/`; `node_modules/` is gitignored.
- React + esbuild versions are pinned in `package.json` (React 19, esbuild 0.25)
  to match the chat island. Keep them in sync across islands.
