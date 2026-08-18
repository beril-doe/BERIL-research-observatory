# NMDC data in BERDL

Use the `nmdc` tenant for NMDC's canonical metadata and analysis results. Do
not select a database only because its name contains `nmdc`; BERDL also hosts
derived products and external mirrors with that label.

## Canonical resources

| Resource | Role |
|---|---|
| `nmdc.metadata` | Schema-driven NMDC metadata, including biosamples, studies, workflow executions, and provenance side tables |
| `nmdc.results` | NMDC workflow results, including functional annotations, taxonomy reports, and MAG quality statistics |
| `nmdc.ref_data` | Redistributable reference data intentionally co-hosted with the canonical ingest |

`nmdc.ncbi_biosamples` is an external NCBI BioSample mirror. It is useful for
NCBI coverage, but it is not NMDC-native metadata.

## Derived resources

The `kbase.nmdc_*` namespaces are useful derived or scoped products, not the
default representation of all NMDC data:

- `kbase.nmdc_arkin` contains Arkin-group integrations and derived products.
- `kbase.nmdc_mags` is a specific MAG catalog.
- `kbase.nmdc_neon` is scoped to the NSF NEON program.

Start with the canonical tenant, then use a derived resource when its scope or
added transformation is specifically required.

## Standard biosample-to-result join

`nmdc.metadata.biosample_to_workflow_run` is the universal bridge from a
biosample to result tables keyed by `workflow_run_id`. For example, retrieve
canonical CheckM MAG quality metrics with:

```sql
SELECT b2wr.biosample_id,
       quality.completeness,
       quality.contamination,
       quality.strain_heterogeneity
FROM nmdc.metadata.biosample_to_workflow_run AS b2wr
JOIN nmdc.results.checkm_statistics AS quality
  ON quality.workflow_run_id = b2wr.workflow_run_id
```

The same bridge connects biosamples to functional annotations and taxonomy
reports in `nmdc.results`.

## Maintained upstream documentation

The producing repository explains the relational model and provenance joins in
more detail:

- [Guide for BERDL agents](https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/for_berdl_claude.md)
- [`nmdc.metadata` table reference](https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/nmdc_metadata_tables.md)
- [`biosample_to_workflow_run` design and examples](https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/biosample_to_workflow_run.md)

Treat live, access-aware inventory as authoritative for availability. The
upstream repository is authoritative for ingest design and maintenance.
