"""Fetch MGnify samples under every biome whose lineage mentions wastewater.

Uses the public MGnify API (https://www.ebi.ac.uk/metagenomics/api/v1).
Writes to $BERIL_RUN_DIR:
  mgnify_biomes.parquet          all 491 biomes with per-biome sample counts
  mgnify_ww_samples.parquet      one row per sample (accession, biosample, biome, text fields)
  mgnify_ww_sample_metadata.parquet  long table of sample-metadata key/value/unit
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

API = "https://www.ebi.ac.uk/metagenomics/api/v1"
OUT = Path(os.environ.get("BERIL_RUN_DIR", "data/scratch"))
OUT.mkdir(parents=True, exist_ok=True)
KW = ("wastewater", "sewage", "sludge", "sewer", "effluent", "influent")


def get(url: str, tries: int = 6) -> dict:
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            wait = 2 ** k
            print(f"  retry {k+1} after {type(e).__name__}: {str(e)[:100]} ({wait}s)", file=sys.stderr, flush=True)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def paged(url: str):
    while url:
        d = get(url)
        yield from d["data"]
        url = d.get("links", {}).get("next")
        time.sleep(0.2)


# 1. biomes
biomes = []
for b in paged(f"{API}/biomes?page_size=100"):
    a = b["attributes"]
    biomes.append({"biome_id": b["id"], "lineage": a["lineage"], "biome_name": a["biome-name"],
                   "samples_count": a.get("samples-count")})
bdf = pd.DataFrame(biomes)
bdf.to_parquet(OUT / "mgnify_biomes.parquet", index=False)
print(f"{len(bdf)} biomes", flush=True)

targets = bdf[bdf["lineage"].str.lower().str.contains("|".join(KW)) & (bdf["samples_count"].fillna(0) > 0)]
print(f"{len(targets)} target biomes, {int(targets['samples_count'].sum())} samples expected", flush=True)

# 2. samples per target biome
samples, meta = {}, []
for lineage, expected in zip(targets["lineage"], targets["samples_count"]):
    url = f"{API}/biomes/{urllib.parse.quote(lineage, safe=':')}/samples?page_size=100"
    n = 0
    for s in paged(url):
        a = s["attributes"]
        acc = s["id"]
        n += 1
        rel_biome = (s.get("relationships", {}).get("biome", {}).get("data") or {}).get("id")
        row = {
            "accession": acc,
            "biosample": a.get("biosample"),
            "sample_name": a.get("sample-name"),
            "sample_desc": a.get("sample-desc"),
            "sample_alias": a.get("sample-alias"),
            "environment_biome": a.get("environment-biome"),
            "environment_feature": a.get("environment-feature"),
            "environment_material": a.get("environment-material"),
            "species": a.get("species"),
            "geo_loc_name": a.get("geo-loc-name"),
            "latitude": a.get("latitude"),
            "longitude": a.get("longitude"),
            "collection_date": a.get("collection-date"),
            "biome_lineage": rel_biome or lineage,
            "queried_lineage": lineage,
        }
        if acc not in samples:
            samples[acc] = row
            for m in a.get("sample-metadata") or []:
                meta.append({"accession": acc, "key": m.get("key"), "value": m.get("value"), "unit": m.get("unit")})
        else:
            samples[acc]["queried_lineage"] += ";" + lineage
    print(f"{lineage}: {n} samples (expected {expected}); total unique {len(samples)}", flush=True)

sdf = pd.DataFrame(list(samples.values()))
sdf.to_parquet(OUT / "mgnify_ww_samples.parquet", index=False)
pd.DataFrame(meta).to_parquet(OUT / "mgnify_ww_sample_metadata.parquet", index=False)
print(f"wrote {len(sdf)} samples, {len(meta)} metadata rows", flush=True)
