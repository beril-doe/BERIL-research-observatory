"""External wastewater labels (GOLD ecosystem paths, MGnify biomes, NMDC) vs BioSample evidence.

Inputs (recorded runs):
  GOLD parquet   runs/<gold-parse>/out/gold_{biosample,sequencing_project}.parquet
  MGnify parquet runs/<mgnify-fetch>/out/mgnify_ww_samples.parquet
  NMDC           nmdc.metadata.biosample_set (Spark)
  BioSample      nmdc.ncbi_biosamples.biosamples_flattened + env_triads_flattened (Spark)

Outputs ($BERIL_RUN_DIR):
  gold_path_counts.csv         every GOLD Engineered path with counts and our ww grouping
  gold_bridge_stats.csv        how many GOLD ww biosamples resolve to an NCBI accession
  nmdc_ecosystem_counts.csv    NMDC biosamples by GOLD-style ecosystem path, ww grouping
  external_label_summary.csv   per source: labelled, bridged, found in BioSample, % with each signal
  external_signal_by_subtype.csv  same, per source x subtype
  external_vocab.csv           per source x subtype x BioSample field: top values (learned vocabulary)
  external_nosignal.csv        externally-labelled samples with no BioSample signal at all: top values
  labelled_samples.parquet     accession-level union of external labels + BioSample flags (seed set)
"""
# %%
import glob
import re
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402
from ww_flags import TEXT_FIELDS, envo_views_sql, flags_select  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
out = run_dir()
T0 = time.time()


def latest(pattern):
    files = sorted(glob.glob(str(PROJ / pattern)))
    if not files:
        raise FileNotFoundError(pattern)
    return files[-1]


def log(msg):
    print(f"[{time.time()-T0:6.0f}s] {msg}", flush=True)


# %% ---------- GOLD ----------
gb = pd.read_parquet(latest("runs/*-gold-parse/out/gold_biosample.parquet"))
gsp = pd.read_parquet(latest("runs/*-gold-parse/out/gold_sequencing_project.parquet"),
                      columns=["project_gold_id", "biosample_gold_id", "ncbi_biosample_accession", "ncbi_bioproject_accession"])
P = ["biosample_ecosystem", "biosample_ecosystem_category", "biosample_ecosystem_type",
     "biosample_ecosystem_subtype", "biosample_specific_ecosystem"]
gb["path"] = gb[P].fillna("").agg(" > ".join, axis=1)


def gold_group(row):
    cat, typ, sub, spec = (row[P[1]] or ""), (row[P[2]] or ""), (row[P[3]] or ""), (row[P[4]] or "")
    s = f"{cat} | {typ} | {sub} | {spec}".lower()
    if row[P[0]] != "Engineered":
        return None
    if cat in ("Wastewater", "WWTP", "Sewage treatment plant") or re.search(r"\bwastewater\b|\bsewage\b", s):
        if re.search(r"activated sludge|mixed liquor|aerobic digester", s):
            return "activated_sludge"
        if re.search(r"anaerobic digest", s):
            return "digester"
        if re.search(r"effluent", s):
            return "effluent"
        if re.search(r"influent", s):
            return "influent"
        if re.search(r"\bsewage\b", s):
            return "sewage"
        if re.search(r"industrial", s):
            return "industrial_ww"
        if re.search(r"\bsludge\b", s):
            return "sludge_generic"
        return "wastewater_other"
    if cat == "Bioreactor" and re.search(r"anaerobic", s) and re.search(r"sludge|digestate|digester", s):
        return "bioreactor_anaerobic_sludge"   # AD-like but not stated as wastewater
    return None


gb["ww_group"] = gb.apply(gold_group, axis=1)
pc = (gb[gb[P[0]] == "Engineered"].groupby(["path", "ww_group"], dropna=False).size()
      .reset_index(name="n_biosamples").sort_values("n_biosamples", ascending=False))
pc.to_csv(out / "gold_path_counts.csv", index=False)
log(f"GOLD: {len(gb)} biosamples, {gb.ww_group.notna().sum()} in ww groups; {len(pc)} Engineered paths")

# bridge GOLD biosample -> NCBI BioSample accession via sequencing projects
gsp = gsp[gsp.biosample_gold_id.notna() & gsp.ncbi_biosample_accession.notna()]
gsp = gsp.assign(acc=gsp.ncbi_biosample_accession.str.split(r"[,;\s]+")).explode("acc")
gsp = gsp[gsp.acc.str.match(r"^SAM[NED]A?\d+$", na=False)]
bridge = gsp[["biosample_gold_id", "acc"]].drop_duplicates()
gold_lab = gb[gb.ww_group.notna()][["biosample_gold_id", "biosample_name", "biosample_ncbi_tax_name", "path", "ww_group"]]
gold_acc = gold_lab.merge(bridge, on="biosample_gold_id", how="left")
pd.DataFrame([{
    "gold_ww_biosamples": len(gold_lab),
    "gold_ww_with_ncbi_acc": gold_acc.acc.notna().groupby(gold_acc.biosample_gold_id).any().sum(),
    "distinct_ncbi_acc": gold_acc.acc.nunique(),
    "all_gold_biosamples_with_ncbi_acc": bridge.biosample_gold_id.nunique(),
}]).to_csv(out / "gold_bridge_stats.csv", index=False)
gold_ext = gold_acc.dropna(subset=["acc"]).rename(columns={"acc": "accession"})
gold_ext["source"] = "GOLD"
gold_ext["ext_label"] = gold_ext["path"]
gold_ext["ext_subtype"] = gold_ext["ww_group"]
log(f"GOLD ww biosamples with NCBI accession: {gold_ext.biosample_gold_id.nunique()} -> {gold_ext.accession.nunique()} accessions")

# %% ---------- MGnify ----------
mg = pd.read_parquet(latest("runs/*-mgnify-fetch/out/mgnify_ww_samples.parquet"))


def mg_group(lin):
    s = lin.lower()
    if "activated sludge" in s:
        return "activated_sludge"
    if "agricultural" in s:
        return "agricultural_ww"
    if "industrial" in s or "terephthalate" in s or "mine water" in s or "petrochemical" in s:
        return "industrial_ww"
    if "nutrient removal" in s:
        return "nutrient_removal_bioreactor"
    if "water and sludge" in s:
        return "water_and_sludge"
    return "wastewater_other"


mg_ext = pd.DataFrame({"accession": mg.biosample, "source": "MGnify", "ext_label": mg.biome_lineage,
                       "ext_subtype": mg.biome_lineage.map(mg_group), "mgnify_sample": mg.accession})
log(f"MGnify: {len(mg_ext)} samples")

# %% ---------- NMDC (Spark) ----------
spark = get_spark("ww-external")
for s in envo_views_sql():
    spark.sql(s)
nmdc = spark.sql("""
SELECT id, name, ecosystem, ecosystem_category, ecosystem_type, ecosystem_subtype, specific_ecosystem,
       env_broad_scale_term_id, env_broad_scale_term_name, env_broad_scale_has_raw_value,
       env_local_scale_term_id, env_local_scale_term_name, env_local_scale_has_raw_value,
       env_medium_term_id, env_medium_term_name, env_medium_has_raw_value,
       env_package, insdc_biosample_identifiers, gold_biosample_identifiers
FROM nmdc.metadata.biosample_set
""").toPandas()
envo_ww_ids = set(spark.sql("SELECT id FROM envo_ww").toPandas()["id"])
nmdc["path"] = nmdc[["ecosystem", "ecosystem_category", "ecosystem_type", "ecosystem_subtype", "specific_ecosystem"]].fillna("").agg(" > ".join, axis=1)
nmdc["envo_ww"] = nmdc[["env_broad_scale_term_id", "env_local_scale_term_id", "env_medium_term_id"]].isin(envo_ww_ids).any(axis=1)
txt = nmdc[["name", "path", "env_broad_scale_has_raw_value", "env_local_scale_has_raw_value", "env_medium_has_raw_value"]].fillna("").agg(" ".join, axis=1).str.lower()
nmdc["kw_ww"] = txt.str.contains(r"\bwaste ?water\b|\bsewage\b|\bsludge\b|\bwwtp\b|anaerobic digest|\bdigester\b|\beffluent\b|\binfluent\b|\bsewer\b", regex=True)
nmdc["path_ww"] = nmdc["path"].str.lower().str.contains(r"wastewater|wwtp|sewage|activated sludge|anaerobic digest", regex=True)
ec = nmdc.groupby(["path", "path_ww"]).agg(n=("id", "size"), n_envo_ww=("envo_ww", "sum"), n_kw_ww=("kw_ww", "sum")).reset_index().sort_values("n", ascending=False)
ec.to_csv(out / "nmdc_ecosystem_counts.csv", index=False)
nmdc_ww = nmdc[nmdc.path_ww | nmdc.envo_ww | nmdc.kw_ww].copy()
nmdc_ww["n_insdc"] = nmdc_ww.insdc_biosample_identifiers.map(lambda a: 0 if a is None else len(a))
pd.DataFrame([{
    "nmdc_biosamples": len(nmdc), "nmdc_ww_any": len(nmdc_ww),
    "nmdc_ww_path": int(nmdc.path_ww.sum()), "nmdc_ww_envo": int(nmdc.envo_ww.sum()), "nmdc_ww_kw": int(nmdc.kw_ww.sum()),
    "nmdc_ww_with_insdc_id": int((nmdc_ww.n_insdc > 0).sum()),
    "nmdc_all_with_insdc_id": int(nmdc.insdc_biosample_identifiers.map(lambda a: a is not None and len(a) > 0).sum()),
    "nmdc_ww_with_gold_id": int(nmdc_ww.gold_biosample_identifiers.map(lambda a: a is not None and len(a) > 0).sum()),
}]).to_csv(out / "nmdc_bridge_stats.csv", index=False)
nmdc_ww[["id", "name", "path", "path_ww", "envo_ww", "kw_ww", "env_broad_scale_term_name", "env_local_scale_term_name",
         "env_medium_term_name", "env_package", "insdc_biosample_identifiers", "gold_biosample_identifiers"]].to_csv(out / "nmdc_ww_samples.csv", index=False)
nmdc_ext = nmdc_ww.explode("insdc_biosample_identifiers").dropna(subset=["insdc_biosample_identifiers"])
nmdc_ext = pd.DataFrame({"accession": nmdc_ext.insdc_biosample_identifiers.str.replace(r"^biosample:", "", regex=True),
                         "source": "NMDC", "ext_label": nmdc_ext.path, "ext_subtype": "nmdc_ww", "nmdc_id": nmdc_ext.id})
log(f"NMDC: {len(nmdc)} biosamples, {len(nmdc_ww)} ww by path/ENVO/keyword, {len(nmdc_ext)} INSDC accessions")

# %% ---------- join all external labels to BioSample ----------
ext = pd.concat([gold_ext[["accession", "source", "ext_label", "ext_subtype"]],
                 mg_ext[["accession", "source", "ext_label", "ext_subtype"]],
                 nmdc_ext[["accession", "source", "ext_label", "ext_subtype"]]], ignore_index=True).drop_duplicates()
# pandas 3 Arrow-backed strings arrive as ChunkedArray, which Spark Connect's
# serializer rejects; hand over plain Python tuples instead. The ingress in
# front of Spark Connect returns HTTP 413 for a single large local relation, so
# send it in small chunks inlined into the plan and union them.
from functools import reduce  # noqa: E402

ext = ext.astype(object).where(ext.notna(), None)
rows_ = [tuple(r) for r in ext.itertuples(index=False)]
CH = 1000
names = []
for i in range(0, len(rows_), CH):
    # one request per chunk; a client-side union of all chunks is one oversized plan (HTTP 413)
    name = f"ext_c{i // CH}"
    spark.createDataFrame(rows_[i:i + CH], schema=list(ext.columns)).createOrReplaceTempView(name)
    names.append(name)
spark.sql("CACHE TABLE ext AS " + " UNION ALL ".join(f"SELECT * FROM {n}" for n in names))
log(f"ext view rows: {spark.sql('SELECT COUNT(*) n FROM ext').toPandas()['n'].iloc[0]}")
log(f"external label rows: {len(ext)}, distinct accessions {ext.accession.nunique()}")

cols = ", ".join(f"b.{c}" for c in ["package_content", "taxonomy_name"] + TEXT_FIELDS)
joined = spark.sql(f"""
SELECT x.accession, x.source, x.ext_label, x.ext_subtype,
       CASE WHEN b.accession IS NULL THEN 0 ELSE 1 END AS found,
       CASE WHEN e.accession IS NULL THEN 0 ELSE 1 END AS envo,
       {flags_select('b')},
       {cols}
FROM ext x
LEFT JOIN nmdc.ncbi_biosamples.biosamples_flattened b ON b.accession = x.accession
LEFT JOIN envo_hits e ON e.accession = x.accession
""").toPandas()
joined.attrs = {}  # pyspark 4.1 attaches PlanMetrics to df.attrs; pandas 3 cannot JSON-serialise it for parquet
joined["any_structured"] = ((joined.pkg + joined.envo + joined.tax) > 0).astype(int)
joined["any_signal"] = ((joined.any_structured + joined.kw) > 0).astype(int)
joined.to_parquet(out / "labelled_samples.parquet", index=False)
log(f"joined rows: {len(joined)}")


def summarize(df, keys):
    g = df.groupby(keys)
    s = g.agg(n_labelled=("accession", "size"), n_found=("found", "sum"))
    f = df[df.found == 1].groupby(keys)
    for c in ["pkg", "envo", "tax", "kw", "any_structured", "any_signal"]:
        s[f"pct_{c}"] = (f[c].mean() * 100).round(1)
    for c in TEXT_FIELDS:
        s[f"pct_kw_{c}"] = (f[f"kw_{c}"].mean() * 100).round(1)
    return s.reset_index()


summarize(joined, ["source"]).to_csv(out / "external_label_summary.csv", index=False)
summarize(joined, ["source", "ext_subtype"]).sort_values(["source", "n_labelled"], ascending=[True, False]).to_csv(out / "external_signal_by_subtype.csv", index=False)

# learned vocabulary: top values per source x subtype x field among found samples
rows = []
for (src, st), g in joined[joined.found == 1].groupby(["source", "ext_subtype"]):
    for c in ["isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "taxonomy_name", "package_content", "sample_type", "description_title"]:
        vc = g[c].str.lower().str.strip().value_counts(dropna=False).head(12)
        for v, n in vc.items():
            rows.append({"source": src, "ext_subtype": st, "field": c, "value": v, "n": int(n), "pct": round(100 * n / len(g), 1)})
pd.DataFrame(rows).to_csv(out / "external_vocab.csv", index=False)

# externally labelled, found, but no BioSample signal
ns = joined[(joined.found == 1) & (joined.any_signal == 0)]
rows = []
for c in ["source", "ext_label", "isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "taxonomy_name", "package_content", "description_title", "sample_type", "host"]:
    vc = ns[c].astype(str).str.lower().value_counts(dropna=False).head(25)
    for v, n in vc.items():
        rows.append({"field": c, "value": v, "n": int(n)})
pd.DataFrame(rows).to_csv(out / "external_nosignal.csv", index=False)
log(f"no-signal externally labelled samples: {len(ns)} of {int(joined.found.sum())} found")
print("done", flush=True)
