"""Value-based validators for SemCat `content_type` labels.

The audit in NB03 asks: when SemCat says a column holds Pfam accessions, does it?
Answering from the column NAME would re-import the very assumption under test, so
each validator checks sampled VALUES against the format the label claims.

Two label classes are treated differently, and the distinction is the point:

  CHECKABLE  -- the label asserts a format (pfam_id => PF#####). It can be wrong,
                so it can also be informative.
  VACUOUS    -- the label asserts nothing checkable (`identifier`,
                `annotation_text`, `accession`, `name`, `label`, `category`). No
                sample can refute it. Scored separately rather than counted as
                correct: a label that cannot be wrong cannot be useful either.
"""

import re

VACUOUS = {"identifier", "annotation_text", "accession", "name", "label", "category",
           "description", "comment", "free_text", "text"}

# label -> (regex that a valid value must match, human description)
PATTERNS = {
    "pfam_id":            (r"^PF\d{5}(\.\d+)?$", "PF#####"),
    "pfam_name":          (r"^[A-Za-z0-9_\-]{2,}$", "a Pfam short name"),
    "interpro_id":        (r"^IPR\d{6}$", "IPR######"),
    "ko_term":            (r"^(KO:)?K\d{5}$", "K##### or KO:K#####"),
    "kegg_gene_id":       (r"^([a-z]{3,5}:)?[A-Za-z0-9_.\-]+$", "a KEGG gene id"),
    "kegg_id":            (r"^(KO:)?[KkCcRrMm]\d{4,5}$|^[a-z]{3,5}\d{5}$", "a KEGG identifier"),
    "kegg_pathway_id":    (r"^(path:)?(map|ko|ec)?\d{5}$", "a KEGG pathway id"),
    "kegg_module_id":     (r"^(md:)?M\d{5}$", "M#####"),
    "kegg_reaction_id":   (r"^(rn:)?R\d{5}$", "R#####"),
    "kegg_reaction":      (r"^(rn:)?R\d{5}$", "R#####"),
    "ec_number":          (r"^(EC[: ]?)?\d+\.[\d\-]+\.[\d\-]+\.[\dn\-]+$|^\d+\.[\d\-]+\.[\d\-]+$",
                           "an EC number like 1.2.3.4"),
    "go_term":            (r"^GO:\d{7}$", "GO:#######"),
    "go_namespace":       (r"^(biological_process|molecular_function|cellular_component|[PFC])$",
                           "a GO namespace"),
    "cog_id":             (r"^COG\d{4}$", "COG####"),
    "cog_category":       (r"^[A-Z]{1,4}$", "one or more COG category letters"),
    "uniprot_accession":  (r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})"
                           r"(-\d+)?$", "a UniProt accession"),
    "uniprot_id":         (r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})"
                           r"(-\d+)?$|^[A-Z0-9]+_[A-Z0-9]+$", "a UniProt accession or entry name"),
    "rhea_id":            (r"^(RHEA:)?\d{5,6}$", "a Rhea id"),
    "metacyc_protein_id": (r"^[A-Za-z0-9\-_.]+$", "a MetaCyc identifier"),
    "ontology_term_id":   (r"^[A-Za-z][A-Za-z0-9_]*:[A-Za-z0-9]+$", "PREFIX:LOCALID"),
    "ontology_term":      (r"^[A-Za-z][A-Za-z0-9_]*:[A-Za-z0-9]+$", "PREFIX:LOCALID"),
    "strand":             (r"^[+\-]$|^[+-]?1$|^0$|^\.$|^(plus|minus|forward|reverse)$",
                           "+/-, 1/-1, or plus/minus"),
    "coordinate":         (r"^-?\d+(\.\d+)?$", "a number"),
    "operon_id":          (r"^-?\d+$|^[A-Za-z0-9_.\-]+$", "an operon identifier"),
    "domain_id":          (r"^[A-Za-z0-9_.\-]+$", "a domain identifier"),
    "contig_id":          (r"^(?!-?\d+$)[A-Za-z0-9_.\-|:]+$", "a sequence/contig identifier, not a bare int"),
    "sequence_id":        (r"^(?!-?\d+$)[A-Za-z0-9_.\-|:]+$", "a sequence identifier"),
    "locus_tag":          (r"^[A-Za-z0-9_.\-]+$", "a locus tag"),
    "gene_locus_id":      (r"^[A-Za-z0-9_.\-|:]+$", "a gene/locus identifier"),
    "protein_id":         (r"^[A-Za-z0-9_.\-|:]+$", "a protein identifier"),
    "gene_id":            (r"^[A-Za-z0-9_.\-|:]+$", "a gene identifier"),
    "gene_cluster_id":    (r"^[A-Za-z0-9_.\-|:]+$", "a gene-cluster identifier"),
    "genome_id":          (r"^[A-Za-z0-9_.\-|:]+$", "a genome identifier"),
    "taxon_id":           (r"^\d+$", "an NCBI taxid"),
    "length":             (r"^-?\d+(\.\d+)?$", "a number"),
    "gene_name":          (r"^[A-Za-z0-9_.\-()\[\]/' ]+$", "a gene name"),
    "gene_symbol":        (r"^[A-Za-z0-9_.\-()\[\]/' ]+$", "a gene symbol"),
    "latitude":           (r"^-?([0-8]?\d(\.\d+)?|90(\.0+)?)$", "latitude in [-90, 90]"),
    "longitude":          (r"^-?(1[0-7]\d(\.\d+)?|[0-9]?\d(\.\d+)?|180(\.0+)?)$",
                           "longitude in [-180, 180]"),
}

# Which facet family each checkable label belongs to. Used for the RECALL stratum:
# a ground-truth column counts as "labelled" only if SemCat gave it a label in the
# right family -- `annotation_text` on a strand column is not a hit.
FAMILY = {
    "function_id": {"pfam_id", "pfam_name", "interpro_id", "ko_term", "kegg_gene_id", "kegg_id",
                    "kegg_pathway_id", "kegg_module_id", "kegg_reaction_id", "kegg_reaction",
                    "kegg_pathway", "kegg_module", "kegg_term", "kegg_tc", "kegg_rclass",
                    "ec_number", "go_term", "go_namespace", "cog_id", "cog_category",
                    "uniprot_accession", "uniprot_id", "rhea_id", "metacyc_protein_id",
                    "ontology_term_id", "ontology_term", "ontology_term_label",
                    "bgc_region_id", "bgc_class", "operon_id", "domain_id",
                    "protein_family_id", "product_prediction", "functional_group_score"},
    "span":        {"coordinate", "bbox_coordinate", "length"},
    "strand":      {"strand"},
    "seqref":      {"contig_id", "sequence_id", "locus_tag", "gene_locus_id", "protein_id",
                    "gene_id", "gene_cluster_id", "genome_id", "organism_id", "sample_id"},
}
LABEL_TO_FAMILY = {lab: fam for fam, labs in FAMILY.items() for lab in labs}


def validate(content_type, values):
    """Adjudicate a SemCat label against sampled values.

    Returns (verdict, detail). verdict in:
      correct    -- all sampled non-null values match the claimed format
      wrong      -- sampled values do not match the claimed format
      vacuous    -- the label asserts nothing checkable
      no_data    -- no non-null values available to judge
      no_pattern -- label is checkable in principle but no validator defined here
    """
    ct = (content_type or "").strip().lower()
    if ct in VACUOUS:
        return "vacuous", "label asserts no checkable format"
    vals = [str(v).strip() for v in values if v is not None and str(v).strip() != ""]
    if not vals:
        return "no_data", "no non-null sample values"
    if ct not in PATTERNS:
        return "no_pattern", f"no validator for content_type '{ct}'"
    rx, desc = PATTERNS[ct]
    bad = [v for v in vals if not re.match(rx, v, flags=re.IGNORECASE)]
    if not bad:
        return "correct", f"all {len(vals)} sampled values look like {desc}"
    return "wrong", (f"{len(bad)}/{len(vals)} sampled values are not {desc}; "
                     f"e.g. {bad[:3]}")


# ---------------------------------------------------------------------------
# Refined adjudication (added after a first pass showed the single "wrong"
# bucket was conflating three different things).
# ---------------------------------------------------------------------------

SENTINELS = {"-", "--", "", ".", "na", "n/a", "nan", "none", "null", "unknown", "?", "0"}

# Placeholders are content-type specific: "-" and "." are real strand values, and "0" is a
# real strand, coordinate, length or numeric value. For those labels the values are
# adjudicated like any other value instead of being skipped.
NOT_PLACEHOLDER = {
    "strand":    {"-", ".", "0"},
    "coordinate": {"0"},
    "length":    {"0"},
    "latitude":  {"0"},
    "longitude": {"0"},
    "taxon_id":  {"0"},
}

MULTI_DELIMS = [";", ",", "|", " "]


def is_sentinel(v, content_type=None):
    s = str(v).strip().lower()
    ct = (content_type or "").strip().lower()
    return s in SENTINELS and s not in NOT_PLACEHOLDER.get(ct, set())


def validate2(content_type, values):
    """Four-way adjudication of a SemCat label against sampled values.

    Distinguishes failures that are SemCat's from failures that are the audit's:

      correct            -- values match the claimed format
      wrong_cardinality  -- each ELEMENT matches once the value is split on a
                            delimiter, i.e. the vocabulary is right but the column
                            is multi-valued. Consequential for users (equality
                            predicates silently return nothing) but a different
                            defect from naming the wrong vocabulary.
      wrong_label        -- values are not that vocabulary at all. SemCat's error.
      sentinel_only      -- every sampled value is a placeholder ('-', 'nan',
                            'None'). INCONCLUSIVE: the label may be right for
                            populated rows and the LIMIT sample simply missed
                            them. This is the audit's limitation, not evidence
                            against SemCat.
      vacuous / no_data / no_pattern -- as in validate().
    """
    import re as _re
    ct = (content_type or "").strip().lower()
    if ct in VACUOUS:
        return "vacuous", "label asserts no checkable format"
    raw = [str(v).strip() for v in values if v is not None and str(v).strip() != ""]
    if not raw:
        return "no_data", "no non-null sample values"
    if ct not in PATTERNS:
        return "no_pattern", f"no validator for content_type '{ct}'"

    non_sentinel = [v for v in raw if not is_sentinel(v, ct)]
    if not non_sentinel:
        return "sentinel_only", (f"all {len(raw)} sampled values are placeholders "
                                 f"(e.g. {raw[:3]}); cannot judge the label")

    rx, desc = PATTERNS[ct]
    bad = [v for v in non_sentinel if not _re.match(rx, v, flags=_re.IGNORECASE)]
    if not bad:
        return "correct", (f"all {len(non_sentinel)} non-placeholder values look like {desc}"
                           + (f" ({len(raw)-len(non_sentinel)} placeholders skipped)"
                              if len(raw) != len(non_sentinel) else ""))

    # Multi-valued? Try splitting the failures on each delimiter.
    for d in MULTI_DELIMS:
        if all(d in v for v in bad):
            parts = [p.strip() for v in bad for p in v.split(d) if p.strip()]
            if parts and all(_re.match(rx, p, flags=_re.IGNORECASE) for p in parts):
                return "wrong_cardinality", (
                    f"{len(bad)}/{len(non_sentinel)} values are '{d}'-delimited lists whose "
                    f"ELEMENTS are valid {desc}; e.g. {bad[:1]}. Equality predicates on this "
                    f"column silently match nothing.")

    return "wrong_label", (f"{len(bad)}/{len(non_sentinel)} values are not {desc}; "
                           f"e.g. {bad[:3]}")
