# Submission Pending

The lakehouse upload for this project failed.

- **Project**: euk_in_prok_correlates
- **Last attempt**: 2026-07-10T16:23:52Z
- **Error**: Lakehouse upload blocked by authorization (not credentials): user mamillerpa has read_only access to the microbialdiscoveryforge MinIO tenant; writes denied ('Insufficient permissions'), reads succeed. A tenant steward (psdehal) must grant read_write on microbialdiscoveryforge, then re-run /submit to retry the upload.
- **Approved at**: 2026-07-10T16:07:02Z    <!-- join key into beril.yaml -->

Status is `complete` (the approval is recorded in `beril.yaml`).
This is an **authorization** block, not a data problem: `mamillerpa` is
`read_only` on the `microbialdiscoveryforge` tenant. A steward (`psdehal`)
must grant `read_write`, then re-run `/submit` to retry the upload only.

## Staging copy (not the official submission)
A full copy of this project was staged to a tenant the author has write access to, as a
backup/preview while the official submission is blocked:
- `s3a://cdm-lake/tenant-general-warehouse/nmdc/projects/euk_in_prok_correlates/` (68 files, 4.34 MiB, staged 2026-07-10)

This is **not** registered as a BERIL submission — the observatory only recognizes archives under
`microbialdiscoveryforge/projects/`. Re-run `/submit` once `read_write` on `microbialdiscoveryforge`
is granted to produce the canonical submission.
