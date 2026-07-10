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
