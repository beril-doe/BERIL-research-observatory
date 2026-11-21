"""Summary figures from the recorded runs (no new queries).

Writes to $BERIL_RUN_DIR:
  fig_biosample_evidence_combos.png   BioSample records by combination of evidence channels
  fig_keyword_by_field.png            keyword hits per BioSample field, split by structured co-signal
  fig_external_signal.png             externally labelled samples: % with each BioSample signal, by source/subtype
"""
import glob
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
out = Path(os.environ.get("BERIL_RUN_DIR", "data/scratch"))
out.mkdir(parents=True, exist_ok=True)
BIO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(sorted(glob.glob(str(PROJ / "runs/*-biosample-evidence/out")))[-1])
EXT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sorted(glob.glob(str(PROJ / "runs/*-external-vs-biosample/out")))[-1])

# 1. evidence combinations
ct = pd.read_csv(BIO / "evidence_crosstab.csv")
ct = ct[(ct[["pkg", "envo", "tax", "kw"]].sum(axis=1) > 0)].copy()
ct["combo"] = ct.apply(lambda r: "+".join(n.upper() for n in ["pkg", "envo", "tax", "kw"] if r[n] == 1), axis=1)
ct = ct.sort_values("n_acc", ascending=True)
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.barh(ct["combo"], ct["n_acc"], color=["#c44" if "PKG" not in c and "ENVO" not in c and "TAX" not in c else "#468" for c in ct["combo"]])
ax.set_xscale("log")
ax.set_xlabel("BioSample records (log scale)")
ax.set_title("NCBI BioSample: records with any wastewater evidence, by channel combination\n"
             "PKG = wastewater package, ENVO = ENVO term in closure, TAX = metagenome taxon, KW = keyword in text (bounded regex)")
for y, (c, n) in enumerate(zip(ct["combo"], ct["n_acc"])):
    ax.text(n * 1.05, y, f"{n:,}", va="center", fontsize=8)
fig.tight_layout()
fig.savefig(out / "fig_biosample_evidence_combos.png", dpi=150, bbox_inches="tight")

# 2. keyword hits per field
kf = pd.read_csv(BIO / "keyword_by_field.csv")
kf = kf[kf.n_hits > 0].sort_values("n_hits")
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.barh(kf["field"], kf["n_with_any_structured"], color="#468", label="also has package / ENVO / taxon signal")
ax.barh(kf["field"], kf["n_kw_only"], left=kf["n_with_any_structured"], color="#c44", label="keyword only")
ax.set_xlabel("BioSample records with a wastewater keyword in the field")
ax.set_title("Which BioSample fields carry wastewater wording, and how often it stands alone")
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(out / "fig_keyword_by_field.png", dpi=150, bbox_inches="tight")

# 3. external labels vs BioSample signals
bs = pd.read_csv(EXT / "external_signal_by_subtype.csv")
bs = bs[bs.n_labelled >= 40].copy()
bs["label"] = bs["source"] + ": " + bs["ext_subtype"] + " (n=" + bs["n_labelled"].astype(str) + ")"
bs = bs.sort_values(["source", "pct_any_signal"])
fig, ax = plt.subplots(figsize=(9, 6.5))
y = range(len(bs))
w = 0.2
for i, (c, lab, col) in enumerate([("pct_pkg", "package", "#888"), ("pct_envo", "ENVO term", "#468"),
                                   ("pct_tax", "metagenome taxon", "#6a6"), ("pct_kw", "keyword (any field)", "#c84")]):
    ax.barh([v + (i - 1.5) * w for v in y], bs[c], height=w, label=lab, color=col)
ax.set_yticks(list(y))
ax.set_yticklabels(bs["label"], fontsize=8)
ax.set_xlabel("% of externally labelled samples carrying the BioSample signal")
ax.set_title("Samples labelled wastewater by GOLD ecosystem path, MGnify biome or NMDC:\nhow often each BioSample evidence channel agrees")
ax.legend(loc="lower right", fontsize=8)
ax.set_xlim(0, 100)
fig.tight_layout()
fig.savefig(out / "fig_external_signal.png", dpi=150, bbox_inches="tight")

# 4. transfer and screening
TR = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(sorted(glob.glob(str(PROJ / "runs/*-term-screen/out")))[-1])
sc = pd.read_csv(TR / "screen_effect.csv")
new_unscreened = int(sc[(sc.term_unscreened == 1) & (sc.any_native == 0)].n_acc.sum())
new_screened = int(sc[(sc.term_screened == 1) & (sc.any_native == 0)].n_acc.sum())
native = int(sc[sc.any_native == 1].n_acc.sum())
ts = pd.read_csv(TR / "term_screen.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
a1.bar(["native\nchannels", "+ terms\n(unscreened)", "+ terms\n(screened)"],
       [native, native + new_unscreened, native + new_screened], color=["#468", "#c44", "#6a6"])
a1.set_xlabel("native channels = package, ENVO, metagenome taxon, keyword", fontsize=8)
a1.set_ylabel("BioSample records flagged wastewater")
a1.set_title("Transfer adds records; screening removes about three fifths of them,\nincluding most but not all disputed-group idiom")
for i, v in enumerate([native, native + new_unscreened, native + new_screened]):
    a1.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
a1.set_ylim(0, (native + new_unscreened) * 1.15)
ok = ts[ts.verdict == "accept"]
no = ts[ts.verdict == "reject"]
a2.scatter(no.n_records.clip(lower=1), no.independent_support, s=18, color="#c44", label=f"rejected ({len(no)} terms)")
a2.scatter(ok.n_records.clip(lower=1), ok.independent_support, s=18, color="#6a6", label=f"accepted ({len(ok)} terms)")
a2.axhline(0.10, ls="--", lw=1, color="#555")
a2.set_xscale("log")
a2.set_xlabel("BioSample records carrying the term (log)")
a2.set_ylabel("corroborating support rate")
a2.set_title("Each mined term, screened on corroborating evidence\n(only the package leg is independent of the term's text)")
a2.legend(fontsize=8, loc="center right")
fig.tight_layout()
fig.savefig(out / "fig_transfer_screen.png", dpi=150, bbox_inches="tight")
print("wrote 4 figures to", out)
