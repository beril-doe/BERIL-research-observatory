"""Shared regexes and SQL fragments for wastewater evidence flags in NCBI BioSample.

All regexes are applied to lower-cased text. Word boundaries are used so that
`septic` does not match *Bordetella bronchiseptica*, `sewer` does not match
*sewerzowii*, and `digest` does not match `digestive` or `undigested`
(see runs/20261017T011707Z-biosample-evidence for the un-bounded counts).
"""

# Generic wastewater wording (any subtype)
KW_RE = (r"\bwaste ?waters?\b|\bsewage\b|\bsludge\b|\bwwtps?\b|\bsewers?\b|\beffluents?\b|\binfluents?\b|"
         r"anaerobic digest|\bdigesters?\b|\bdigestors?\b|\bdigestate\b|\bbiosolids?\b|"
         r"\bseptic (tank|system)s?\b|\bmixed liquor\b|\bsewage sludge\b")

# NCBI metagenome taxonomy names that denote wastewater subtypes
TAX_STRICT_RE = (r"^(wastewater|sludge|activated sludge|anaerobic digester|bioreactor sludge|biosolids|"
                 r"sewage|biogas fermenter) metagenome$")

# BioSample packages
PKG_RE = r"wastewater|wwsurv"

# Subtype regexes (free text, lower-cased)
SUBTYPE_RE = {
    "influent": r"\binfluents?\b|\braw (sewage|waste ?water)\b|\buntreated (waste ?water|sewage)\b|\bprimary (clarifier|settl\w*|sediment\w*)\b|\bheadworks\b|\binlet\b",
    "effluent": r"\beffluents?\b|\btreated (waste ?water|sewage)\b|\b(final|secondary) clarifier\b|\boutfall\b|\bdischarge\b",
    "activated_sludge": r"\bactivated sludge\b|\baeration (tank|basin)s?\b|\bmixed liquor\b|\bmlss\b|\boxidation ditch\b|\bsequencing batch\b|\bsbr\b",
    "digester": r"anaerobic digest|\bdigesters?\b|\bdigestors?\b|\bdigestate\b|\bbiogas\b|\buasb\b|\begsb\b|\bdigester sludge\b",
    "sewer": r"\bsewers?\b|\bmanholes?\b|\bcollection system\b|\bcombined sewer\b|\bstorm ?water\b",
    "sludge_generic": r"\bsludge\b|\bbiosolids?\b",
}

TEXT_FIELDS = ["isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "sample_type",
               "source_name", "description_title", "description_comment", "description", "project_name",
               "samp_mat_process", "sample_name", "env_package", "host"]


def sql_re(rx: str) -> str:
    """Escape a Java regex for embedding in a Spark SQL single-quoted literal.

    Spark SQL literals process backslash escapes, so '\\b' in the SQL text would
    become a backspace character and silently match nothing. Double them.
    """
    return rx.replace("\\", "\\\\")


KW_RE_SQL = sql_re(KW_RE)
TAX_STRICT_RE_SQL = sql_re(TAX_STRICT_RE)
SUBTYPE_RE_SQL = {k: sql_re(v) for k, v in SUBTYPE_RE.items()}


def kw_case(col: str, alias: str = "b") -> str:
    return f"CASE WHEN lower({alias}.{col}) RLIKE '{KW_RE_SQL}' THEN 1 ELSE 0 END"


def flags_select(alias: str = "b") -> str:
    """SELECT-list fragment producing pkg, tax, kw_<field>..., kw for alias `b`."""
    parts = [
        f"CASE WHEN lower({alias}.package_content) RLIKE '{PKG_RE}' THEN 1 ELSE 0 END AS pkg",
        f"CASE WHEN lower({alias}.taxonomy_name) RLIKE '{TAX_STRICT_RE_SQL}' THEN 1 ELSE 0 END AS tax",
    ]
    parts += [f"{kw_case(c, alias)} AS kw_{c}" for c in TEXT_FIELDS]
    any_expr = " + ".join(kw_case(c, alias) for c in TEXT_FIELDS)
    parts.append(f"CASE WHEN ({any_expr}) > 0 THEN 1 ELSE 0 END AS kw")
    return ",\n  ".join(parts)


ENVO_SEED_LABEL_RE = (r"waste ?water|sewage|sludge|biosolid|anaerobic digest|digester|digestor|sewer|"
                      r"effluent|influent|septic|wastewater")
ENVO_SEED_EXCLUDE_RE = r"digestive|oil sludge|marine sludge"


def envo_views_sql() -> list[str]:
    """Statements creating temp views envo_seed, envo_ww (closure), envo_hits (accession-level)."""
    return [
        f"""CREATE OR REPLACE TEMP VIEW envo_seed AS
            SELECT DISTINCT subject AS id FROM kbase.ontology_source.statements
            WHERE predicate='rdfs:label' AND subject LIKE 'ENVO:%'
              AND lower(value) RLIKE '{ENVO_SEED_LABEL_RE}' AND NOT lower(value) RLIKE '{ENVO_SEED_EXCLUDE_RE}'""",
        """CREATE OR REPLACE TEMP VIEW envo_ww AS
            SELECT id FROM envo_seed
            UNION
            SELECT e.subject AS id FROM kbase.ontology_source.entailed_edge e JOIN envo_seed s ON e.object = s.id
            WHERE e.predicate='rdfs:subClassOf' AND e.subject LIKE 'ENVO:%'""",
        """CREATE OR REPLACE TEMP VIEW envo_hits AS
            SELECT DISTINCT t.accession FROM nmdc.ncbi_biosamples.env_triads_flattened t JOIN envo_ww w ON t.id = w.id""",
    ]
