"""Convert the GOLD public Excel export (goldData.xlsx) to one parquet per sheet.

The export is downloaded from https://gold.jgi.doe.gov/download?mode=site_excel
(public, no login) into data/gold_raw/. Sheets: Readme, Study, Biosample,
Organism, Sequencing Project, Analysis Project. The Organism and Sequencing
Project sheets are >1 GB of XML, so this streams the XML rather than using
openpyxl/pandas.read_excel. All cells are inline strings in this export.

Run with `python -I` (the input is an untrusted download):
    uv run beril run --name gold-parse --input data/gold_raw/<file> -- \
        /opt/conda/bin/python -I src/01_gold_xlsx_to_parquet.py data/gold_raw/<file>
"""
from __future__ import annotations

import os
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CHUNK = 200_000


def col_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def sheet_names(z: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {
        r.attrib["Id"]: r.attrib["Target"]
        for r in rels.iter("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    }
    out = []
    for s in wb.iter(f"{NS}sheet"):
        rid = s.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rid_to_target[rid]
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        out.append((s.attrib["name"], target))
    return out


def iter_rows(z: zipfile.ZipFile, member: str):
    with z.open(member) as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != f"{NS}row":
                continue
            cells: dict[int, str] = {}
            for c in el.iter(f"{NS}c"):
                idx = col_index(c.attrib["r"])
                t = c.attrib.get("t")
                val = ""
                if t == "inlineStr":
                    is_el = c.find(f"{NS}is")
                    if is_el is not None:
                        val = "".join(x.text or "" for x in is_el.iter(f"{NS}t"))
                else:
                    v = c.find(f"{NS}v")
                    val = v.text if v is not None and v.text is not None else ""
                cells[idx] = val
            el.clear()
            yield cells


def convert(xlsx: Path, outdir: Path) -> None:
    z = zipfile.ZipFile(xlsx)
    for name, member in sheet_names(z):
        if name.lower() == "readme":
            continue
        slug = name.lower().replace(" ", "_")
        t0 = time.time()
        rows = iter_rows(z, member)
        header_cells = next(rows)
        ncol = max(header_cells) + 1
        header = [header_cells.get(i, f"col_{i}") for i in range(ncol)]
        header = [h.strip().lower().replace(" ", "_").replace("/", "_") for h in header]
        writer = None
        buf: list[list[str]] = []
        n = 0

        def flush():
            nonlocal writer, buf
            if not buf:
                return
            cols = {h: pa.array([r[i] for r in buf], type=pa.string()) for i, h in enumerate(header)}
            table = pa.table(cols)
            if writer is None:
                writer = pq.ParquetWriter(outdir / f"gold_{slug}.parquet", table.schema, compression="zstd")
            writer.write_table(table)
            buf = []

        for cells in rows:
            if not cells:
                continue
            buf.append([cells.get(i, "") or None for i in range(ncol)])
            n += 1
            if len(buf) >= CHUNK:
                flush()
                print(f"  {name}: {n:,} rows ({time.time()-t0:.0f}s)", flush=True)
        flush()
        if writer is not None:
            writer.close()
        print(f"{name}: {n:,} rows, {ncol} cols -> gold_{slug}.parquet ({time.time()-t0:.0f}s)", flush=True)
        print("  columns:", header, flush=True)


if __name__ == "__main__":
    src = Path(sys.argv[1])
    out = Path(os.environ.get("BERIL_RUN_DIR", "data/scratch"))
    out.mkdir(parents=True, exist_ok=True)
    convert(src, out)
