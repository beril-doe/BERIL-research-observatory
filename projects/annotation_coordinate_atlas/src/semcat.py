"""Shared helpers for the annotation_coordinate_atlas project.

Kept in src/ because four notebooks need the same regexes and the same
accessible-tenant list, and divergent copies would silently change what
"ground truth" means between notebooks.
"""

from __future__ import annotations

SEMCAT = "globalusers.semantic_catalog"

# The 8 tenants this account can read, per berdl_inventory.py (2026-10-02).
ACCESSIBLE_TENANTS = [
    "bervodata", "culturebotai", "kbase", "kescience",
    "mamillerpa", "my", "nmdc", "refdata",
]

# Of those, the ones SemCat actually indexes.
ACCESSIBLE_IN_SEMCAT = ["kbase", "kescience", "nmdc", "refdata"]

# ---------------------------------------------------------------------------
# Facet regexes. Deliberately name-based: these define the SemCat-independent
# ground truth, so they must not consult content_type.
# ---------------------------------------------------------------------------

# Identifier systems that assign a function to a gene/protein.
RX_FUNC_ID = (
    r"pfam|interpro|^ipr$|^ipr_|_ipr$|tigrfam|panther|^smart$|prosite|hamap|"
    r"superfamily|gene3d|sfld|cdd|pirsf|^ko$|^ko_|_ko$|ko_term|kegg|"
    r"^ec$|^ec_|_ec$|ec_number|ec_num|enzyme_commission|"
    r"^go$|^go_|_go$|go_term|go_id|goslim|"
    r"^cog$|^cog_|_cog$|eggnog|ortholog|^og$|"
    r"cazy|dbcan|antismash|mibig|bgc|smcog|"
    r"uniprot|^sp_|swissprot|trembl|metacyc|rhea|reactome|seed|subsystem|"
    r"product|function|annotat|domain|motif|operon|regulon|"
    r"signature|hmm|profile|pathway|module|resfam|^amr|virulence|"
    r"^desc$|description"
)

# A span: a pair of positions delimiting a region.
RX_SPAN = (
    r"^(start|end|stop|begin|beg|from|to|left|right|min|max)$|"
    r"_(start|end|stop|begin|beg|pos|position|coord)$|"
    r"^(start|end|stop|begin|beg)_|"
    r"posfrom|posto|pos_from|pos_to|"
    r"^(aln|ali|env|hmm|model|query|target|subject|sp|res|pdb)_?(start|end|stop|beg|from|to)$|"
    r"position_range|coord_range"
)

RX_STRAND = r"^strand$|_strand$|^strand_|^orientation$|_orientation$|^frame$|^phase$"

# A reference to the sequence the span is measured on.
RX_SEQREF = (
    r"contig|scaffold|^seqid$|seq_id|sequence_id|sequence_name|^chrom|chromosome|"
    r"replicon|^accession$|accession_id|^acc$|assembly|^mag$|^genome$|genome_id|"
    r"^gene_id$|^gene$|locus_tag|^protein_id$|^protein$|uniprot|^md5$|^pdb$|pdb_id|"
    r"^bin_id$|^bgc_id$|gene_cluster_id|^id$"
)

# Geographic coordinates — the thing content_type='coordinate' conflates with
# genomic ones. Matched so it can be excluded from the genomic span facet.
RX_GEO = (
    r"^lat$|^lon$|^long$|latitude|longitude|^lat_|_lat$|^lon_|_lon$|_long$|"
    r"northing|easting|^elev|altitude|bbox|cent_lat|cent_long|dec_lat|dec_long|huc"
)

# Identifier-system labels, for reporting which systems a table uses.
ID_SYSTEMS = {
    "Pfam": r"pfam",
    "InterPro": r"interpro|^ipr",
    "KEGG KO": r"^ko$|^ko_|_ko$|ko_term|kegg_ortho|^kegg$|kegg_id|kegg_gene",
    "KEGG pathway/module": r"kegg_pathway|kegg_module|kegg_reaction|kegg_rclass|kegg_tc",
    "EC": r"^ec$|^ec_|_ec$|ec_number|ec_num|enzyme_commission",
    "GO": r"^go$|^go_|_go$|go_term|go_id|goslim|go_namespace",
    "COG": r"^cog$|^cog_|_cog$",
    "eggNOG": r"eggnog",
    "TIGRFAM": r"tigrfam",
    "PANTHER": r"panther",
    "CAZy/dbCAN": r"cazy|dbcan",
    "antiSMASH/MIBiG": r"antismash|mibig|big_scape|gcf_|^bgc|bgc_",
    "UniProt": r"uniprot|swissprot|trembl|^sp_",
    "MetaCyc": r"metacyc",
    "Rhea": r"rhea",
    "PDB": r"^pdb|pdb_id|pdb_beg|pdb_end",
    "SEED/subsystem": r"seed|subsystem",
    "free-text product/function": r"^product$|product_|^function$|function_|^desc$|description",
}


def rx_or(col: str, pattern: str) -> str:
    """SQL fragment: does lower(col) match pattern?"""
    return f"lower({col}) RLIKE '{pattern}'"


def classify_coordinate_system(column_name, dtype, lower, upper, table_cols):
    """Classify a span column's coordinate system using ONLY SemCat-available fields.

    Returns (system, basis). `system` is one of:
      geographic | nucleotide | amino_acid | hmm_model | ambiguous
    `basis` names which evidence decided it, so the report can state how much
    of the resolution came from the `coordinate` label itself (answer: none).

    table_cols: the other column names in the same table (also from SemCat).
    """
    import re

    name = (column_name or "").lower()
    cols = " ".join(c.lower() for c in (table_cols or []))

    # 1. HMM/profile-model coordinates announce themselves in the name.
    if re.search(r"^(model|hmm|profile)_(start|end|stop|from|to)$|^(model|hmm)_", name):
        return "hmm_model", "column name says model/hmm"

    # 2. Geographic, by name.
    if re.search(RX_GEO, name):
        return "geographic", "column name is a geographic coordinate"

    # 3. Geographic, by type+bounds (double within lat/lon range).
    def num(v):
        # NaN must come back as None, not as float('nan'). SemCat 0.21.6 returns NaN
        # for some bounds where 0.19.28 returned a string; float('nan') passes the
        # `is not None` guards below and then blows up in int()/format().
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        return None if f != f else f

    lo, hi = num(lower), num(upper)
    if dtype in ("double", "float", "decimal") and lo is not None and hi is not None:
        if -180.0 <= lo and hi <= 180.0:
            return "geographic", "double type with bounds inside lat/lon range"

    # 4. Integer spans: nucleotide vs amino-acid, decided by magnitude + sibling refs.
    has_contig = bool(re.search(r"contig|scaffold|chrom|replicon|^mag$|assembly", cols))
    has_protein = bool(re.search(r"protein|uniprot|^md5$|pdb|gene_cluster|seq_len", cols))

    if dtype in ("int", "bigint", "smallint"):
        if hi is not None and hi > 100_000:
            # No protein is 100 kb of residues; this is a nucleotide coordinate.
            return "nucleotide", f"integer span with upper bound {int(hi):,} > 100,000"
        if has_contig and not has_protein:
            return "nucleotide", "sibling contig/scaffold column, no protein column"
        if has_protein and not has_contig:
            return "amino_acid", "sibling protein/md5/seq_len column, no contig column"
        return "ambiguous", (
            f"integer span, upper bound {('unknown' if hi is None else format(int(hi), ','))}, "
            f"contig_sibling={has_contig} protein_sibling={has_protein}"
        )

    # 5. String-typed positions: SemCat often has no bounds at all for these.
    if dtype == "string":
        if has_contig and not has_protein:
            return "ambiguous", "string-typed position, contig sibling but no bounds in SemCat"
        return "ambiguous", "string-typed position with no usable bounds in SemCat"

    return "ambiguous", f"type {dtype}, no decisive evidence in SemCat fields"
