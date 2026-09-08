#!/usr/bin/env python3
"""Stage the Streptococcus mutans UA159 gene-annotate results as Parquet for Lakehouse ingest.

Mirrors ``stage_llmagent_parquet.py`` (the 5-organism Fitness Browser staging) so the
output appends cleanly onto the existing ``kbaseincubator.llmagent.*`` tables. S. mutans
differs from the Fitness Browser organisms in three ways handled here:

  * sequence ids are bare locus tags (``SMU_01``) rather than ``orgId:locusId``;
  * it is a single organism, staged under one org_id;
  * there is no ``*_metadata.tsv`` — ``aa_length`` is taken from the FASTA record.

The proteome-edges run (``--string-mode edges`` over the full proteome) is the source;
the hypothetical/named/control subsets under ``data/s-mutans/`` are deliberately excluded.

Four tables are produced in ``data/llmagent_ingest_smutans/`` with the same schema as the
existing Lakehouse tables:

  annotation           one row per annotated protein, evidence columns stripped
  annotation_evidence  long format — one row per (protein, evidence source)
  interproscan         the InterProScan TSV output, given column names
  protein              locus metadata joined to the amino-acid sequence
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

csv.field_size_limit(sys.maxsize)

REPO = Path(__file__).resolve().parent.parent
# The large S. mutans inputs live untracked in the working checkout's data/. When
# this script runs from an isolated worktree, point BERIL_DATA_DIR at that data/.
DATA = Path(os.environ.get("BERIL_DATA_DIR", REPO / "data"))
SMU = DATA / "s-mutans"
EDGES = SMU / "s_mutans_proteome_edges"
OUT = DATA / "llmagent_ingest_smutans"

ORG_ID = "SmutansUA159"

ANNOTATIONS_TSV = EDGES / "s_mutans_proteome_edges_annotations.tsv"
IPR_TSV = EDGES / "s_mutans_proteome_edges_ipr.tsv"
FAA = SMU / "s_mutans_all.faa"

# Columns kept inline on the core annotation table.
CORE_COLS = [
    "sequence_id",
    "organism",
    "model",
    "annotation",
    "evidence",
    "reasoning_trace",
    "tier",
    "reasoning",
]
TOKEN_COLS = ["input_tokens", "output_tokens", "total_tokens", "reasoning_tokens"]

# Columns unpivoted into annotation_evidence. Together with CORE_COLS and
# TOKEN_COLS these account for all 23 columns of the source TSV.
EVIDENCE_COLS = [
    "paperblast_evidence",
    "fitness_evidence",
    "cofitness_evidence",
    "ipr_annotations",
    "gene_neighborhoods",
    "pangenome_neighborhoods",
    "berdl_paperblast_evidence",
    "berdl_pangenome_evidence",
    "berdl_fitness_evidence",
    "string_evidence",
    "evidence_fitnessbrowser_aaseqs",
]

# InterProScan's standard 15-column TSV output, which ships without a header row.
IPR_COLS = [
    "sequence_id",
    "md5",
    "seq_length",
    "analysis",
    "signature_acc",
    "signature_desc",
    "start",
    "stop",
    "evalue",
    "status",
    "date",
    "interpro_acc",
    "interpro_desc",
    "go_terms",
    "pathways",
]

ANNOTATION_SCHEMA = pa.schema(
    [(c, pa.string()) for c in CORE_COLS]
    + [("org_id", pa.string()), ("status", pa.string())]
    + [(c, pa.int64()) for c in TOKEN_COLS]
)

EVIDENCE_SCHEMA = pa.schema([
    ("sequence_id", pa.string()),
    ("org_id", pa.string()),
    ("evidence_source", pa.string()),
    ("evidence_text", pa.string()),
])

IPR_SCHEMA = pa.schema([
    ("sequence_id", pa.string()),
    ("org_id", pa.string()),
    ("md5", pa.string()),
    ("seq_length", pa.int64()),
    ("analysis", pa.string()),
    ("signature_acc", pa.string()),
    ("signature_desc", pa.string()),
    ("start", pa.int64()),
    ("stop", pa.int64()),
    ("evalue", pa.float64()),
    ("status", pa.string()),
    ("date", pa.string()),
    ("interpro_acc", pa.string()),
    ("interpro_desc", pa.string()),
    ("go_terms", pa.string()),
    ("pathways", pa.string()),
])

PROTEIN_SCHEMA = pa.schema([
    ("sequence_id", pa.string()),
    ("org_id", pa.string()),
    ("locus_id", pa.string()),
    ("aa_length", pa.int64()),
    ("aa_sequence", pa.string()),
])


def _int(value: str) -> int | None:
    value = (value or "").strip()
    try:
        return int(value)
    except ValueError:
        return None


def _float(value: str) -> float | None:
    # InterProScan writes "-" where a member database reports no e-value.
    value = (value or "").strip()
    try:
        return float(value)
    except ValueError:
        return None


def _dash_to_none(value: str) -> str | None:
    value = (value or "").strip()
    return None if value in ("", "-") else value


def _blank_to_none(value: str) -> str | None:
    return value if (value or "").strip() else None


# Match the sentinel used by the Fitness Browser staging so a gateway HTML error
# page collapses to a stable marker rather than 78 KB of markup.
ERROR_SENTINEL = "ERROR: model gateway returned an HTML error page; annotation failed"


def _normalize_annotation(value: str) -> str | None:
    if (value or "").startswith("ERROR:"):
        return ERROR_SENTINEL
    return _blank_to_none(value)


def _status(annotation: str | None, n_evidence: int) -> str:
    """Classify why a row does or does not carry an annotation (see sibling script)."""
    if annotation is None:
        return "no_evidence" if n_evidence == 0 else "error"
    if annotation == ERROR_SENTINEL:
        return "error"
    return "annotated"


def _read_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, str] = {}
    seq_id = None
    chunks: list[str] = []
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                if seq_id is not None:
                    seqs[seq_id] = "".join(chunks)
                seq_id = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(line.strip())
    if seq_id is not None:
        seqs[seq_id] = "".join(chunks)
    return seqs


def stage_annotations() -> tuple[int, int, set[str]]:
    """Write annotation.parquet and annotation_evidence.parquet; return seen seq ids."""
    ann_rows: list[dict] = []
    ev_rows: list[dict] = []
    seen: set[str] = set()

    with open(ANNOTATIONS_TSV, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            seq_id = row["sequence_id"]
            seen.add(seq_id)

            rec = {c: _blank_to_none(row.get(c, "")) for c in CORE_COLS}
            rec["annotation"] = _normalize_annotation(row.get("annotation", ""))
            rec["org_id"] = ORG_ID
            rec.update({c: _int(row.get(c, "")) for c in TOKEN_COLS})

            n_evidence = 0
            for col in EVIDENCE_COLS:
                text = row.get(col) or ""
                if text.strip():
                    n_evidence += 1
                    ev_rows.append({
                        "sequence_id": seq_id,
                        "org_id": ORG_ID,
                        "evidence_source": col,
                        "evidence_text": text,
                    })

            rec["status"] = _status(rec["annotation"], n_evidence)
            ann_rows.append(rec)

    print(f"  {ORG_ID:14s} {len(ann_rows):6,d} annotations, {len(ev_rows):,} evidence rows")
    pq.write_table(
        pa.Table.from_pylist(ann_rows, schema=ANNOTATION_SCHEMA),
        OUT / "annotation.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(ev_rows, schema=EVIDENCE_SCHEMA),
        OUT / "annotation_evidence.parquet",
        compression="zstd",
    )
    return len(ann_rows), len(ev_rows), seen


def stage_interproscan() -> int:
    rows: list[dict] = []
    with open(IPR_TSV, newline="") as fh:
        for raw in csv.reader(fh, delimiter="\t"):
            r = dict(zip(IPR_COLS, raw))
            rows.append({
                "sequence_id": r["sequence_id"],
                "org_id": ORG_ID,
                "md5": r["md5"],
                "seq_length": _int(r["seq_length"]),
                "analysis": r["analysis"],
                "signature_acc": r["signature_acc"],
                "signature_desc": _dash_to_none(r["signature_desc"]),
                "start": _int(r["start"]),
                "stop": _int(r["stop"]),
                "evalue": _float(r["evalue"]),
                "status": r["status"],
                "date": r["date"],
                "interpro_acc": _dash_to_none(r["interpro_acc"]),
                "interpro_desc": _dash_to_none(r["interpro_desc"]),
                "go_terms": _dash_to_none(r["go_terms"]),
                "pathways": _dash_to_none(r["pathways"]),
            })
    print(f"  {ORG_ID:14s} {len(rows):6,d} IPR matches")
    pq.write_table(
        pa.Table.from_pylist(rows, schema=IPR_SCHEMA),
        OUT / "interproscan.parquet",
        compression="zstd",
    )
    return len(rows)


def stage_proteins(annotated: set[str]) -> int:
    """Write protein.parquet from the FASTA. No metadata TSV exists for S. mutans,
    so aa_length is the sequence length and locus_id is the (bare) sequence id."""
    seqs = _read_fasta(FAA)
    missing = annotated - set(seqs)
    if missing:
        raise KeyError(
            f"{len(missing)} annotated sequence(s) absent from {FAA.name}: "
            f"{sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}"
        )

    rows = [
        {
            "sequence_id": seq_id,
            "org_id": ORG_ID,
            "locus_id": seq_id,
            "aa_length": len(seq),
            "aa_sequence": seq,
        }
        for seq_id, seq in seqs.items()
    ]
    print(f"  {ORG_ID:14s} {len(rows):6,d} proteins ({len(seqs) - len(annotated):,} beyond the annotated set)")
    pq.write_table(
        pa.Table.from_pylist(rows, schema=PROTEIN_SCHEMA),
        OUT / "protein.parquet",
        compression="zstd",
    )
    return len(rows)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    print("annotation + annotation_evidence:")
    n_ann, n_ev, seen = stage_annotations()
    print("interproscan:")
    n_ipr = stage_interproscan()
    print("protein:")
    n_prot = stage_proteins(seen)

    print("\nStaged to", OUT)
    for name, n in [
        ("annotation", n_ann),
        ("annotation_evidence", n_ev),
        ("interproscan", n_ipr),
        ("protein", n_prot),
    ]:
        size_mb = (OUT / f"{name}.parquet").stat().st_size / 1_048_576
        print(f"  {name:22s} {n:9,d} rows  {size_mb:8.1f} MB")


if __name__ == "__main__":
    main()
