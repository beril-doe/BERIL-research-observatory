# BERIL Wiki Deployment on SPIN notes

The BERIL wiki ([beril-doe/beril-wiki](https://github.com/beril-doe/beril-wiki)) is a static site, served on the same host as the webapp under `/wiki`: https://beril.kbase.us/wiki (and https://beril-dev.kbase.us/wiki). It runs in its own container. Nothing in this repo builds it or serves it; this page is the SPIN half of that setup.

## Short-short version for re-deployment
1. Merge to `main` in beril-wiki. Its `Build wiki image` workflow pushes both tags to GHCR.
2. Redeploy the `beril-wiki` workload: `beril/beril-wiki` for prod, `knowledge-engine/beril-wiki` for dev.

## Image
`ghcr.io/beril-doe/beril-wiki`, built by `.github/workflows/image.yml` in beril-wiki:
* `:latest` is built for `beril.kbase.us/wiki`. Use it in prod.
* `:develop` is built for `beril-dev.kbase.us/wiki`. Use it in dev.
* `:latest-sha-<sha>` / `:develop-sha-<sha>` pin a specific build.

Each environment needs its own tag because Quartz bakes the host into absolute links (the footer's About link, the sitemap and RSS). In-page links and the search index follow the `/wiki` path, which is the same in both.

The container serves the built site with a small Starlette app, `src/beril_wiki/serve.py` in beril-wiki:
* It listens on **8080** and runs as uid/gid **76761**, the same SPIN account as the webapp.
* It serves everything under `/wiki`. `/wiki` redirects to `/wiki/`, and extensionless URLs resolve to `.html`.
* `/healthz` returns `ok`.
* It needs no secrets, config or volumes.

The GHCR package has to be public, or the workload needs an image pull secret.

## Deployment stack
*Workloads/Deployments*
* `beril-wiki`, with the image described above.
* Container port 8080 (TCP). Set image pull policy to Always so a redeploy picks up the new `:latest`/`:develop`.
* HTTP liveness and readiness checks on `/healthz`, port 8080.
* Security context:
  * run as user 76761, group 76761
  * no privilege escalation
  * drop ALL capabilities
* Exposes a ClusterIP Service, `beril-wiki`, on port 8080.

*Ingress*
* Unlike `/ov`, no path rewrite is needed. The app serves under `/wiki` itself, so the wiki can be a plain path rule on the **existing** beril ingress, and the Rancher UI is enough. No YAML editing or annotations are needed.
* Add this rule on the beril.kbase.us ingress:
  * Path type `Prefix`, path `/wiki`
  * Target service `beril-wiki`, port 8080
  * Do the same on beril-dev.kbase.us.
* Order doesn't matter. Kubernetes picks the longest matching prefix, so `/wiki` wins over the webapp's `/`.

Once deployed, `curl -i https://beril.kbase.us/wiki/` should return `200` with the wiki's home page. `https://beril.kbase.us/wiki/nope` should return the wiki's own 404 page, not the webapp's.

## Locally
`docker compose --profile wiki up -d` adds the wiki to the local stack at http://localhost:8000/wiki/ through the same proxy as `/ov` (`nginx.conf`). Without the profile, `/wiki` is a 502 and the rest of the stack is unaffected.

The `:develop` image's footer and sitemap links point at beril-dev. To use a local build, follow "The SPIN image" in the beril-wiki README and set `BERIL_WIKI_IMAGE=beril-wiki:local`.

## Not yet
* **"Ask the wiki" still uses each reader's own CBORG key.** The key is kept in browser storage, which is now on the webapp's origin.
* **Moving Ask to a Vertex credential.** The plan is a server-side endpoint in the wiki container, with the GCP key as a Secret, as OpenViking has.
* **Nav link from the webapp.** The Atlas naming lint (`ui/tests/test_atlas_lint.py`) has to be narrowed first.
