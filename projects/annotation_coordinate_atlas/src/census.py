"""Curated adjudication of BERDL annotation tables.

Every row here was decided by reading the table's live schema and, where the
schema was ambiguous, by sampling values. The `basis` field records which.
Kept as explicit data rather than inferred by regex because the distinctions the
research question asks for -- does this table ASSIGN a function to a gene, or
ANNOTATE A REGION, and in WHICH coordinate frame -- are not recoverable from
column names. Several entries exist precisely because a name-based rule got them
wrong (see EXCLUDED).

Fields
------
category     : gene_function | region | both | reference_vocabulary
region_type  : what kind of region, when category includes region
coords       : yes | packed | no        (packed = coordinates inside a string/JSON column)
coord_system : nucleotide | amino_acid | hmm_model | multiple | none
coord_frame  : what the numbers are measured ALONG -- this is the join key question
seq_ref      : the column identifying that sequence, or None if absent
span         : (start_col, end_col) or None
strand       : strand column or None
id_systems   : identifier systems the table carries
basis        : how the coordinate system was determined
notes        : anything a user would be burned by
"""

CENSUS = [
    # ---------------- domain / motif annotation, amino-acid coordinates ----------------
    dict(fq="kbase.ke_pangenome.interproscan_domains", category="both", region_type="protein domain/motif",
         coords="yes", coord_system="amino_acid", coord_frame="pangenome gene-cluster representative protein",
         seq_ref="gene_cluster_id", span=("start", "stop"), strand=None,
         id_systems=["InterPro", "Pfam", "Gene3D", "SUPERFAMILY", "PANTHER", "PRINTS", "CDD", "NCBIfam",
                     "ProSiteProfiles", "ProSitePatterns", "MobiDBLite", "SMART", "FunFam", "Coils",
                     "Hamap", "PIRSF", "SFLD", "AntiFam"],
         basis="value check: start/stop bounded by seq_len; 18 member DBs enumerated from DISTINCT analysis",
         notes="Richest single annotation table in BERDL: 18 signature databases in one table, selected by "
               "`analysis`. Pfam alone is 145,825,639 rows. Keyed on gene_cluster_id (a CLUSTER REPRESENTATIVE, "
               "not a genome gene), so its coordinates cannot be joined to a contig without a cluster-member "
               "mapping. `analysis` has a 1-row 'Gene3' value that looks like a typo for Gene3D."),
    dict(fq="kbase.ke_pangenome.bakta_pfam_domains", category="both", region_type="protein domain",
         coords="yes", coord_system="amino_acid", coord_frame="pangenome gene-cluster representative protein",
         seq_ref="gene_cluster_id", span=("start", "stop"), strand=None,
         id_systems=["Pfam"], basis="schema: start/stop alongside pfam_id/pfam_name, no contig column",
         notes="Bakta's Pfam calls, parallel to interproscan_domains but single-source."),
    dict(fq="kescience.interpro.protein2ipr", category="both", region_type="protein domain/motif",
         coords="yes", coord_system="amino_acid", coord_frame="UniProt protein",
         seq_ref="uniprot_acc", span=("start", "stop"), strand=None,
         id_systems=["InterPro", "Pfam", "and other InterPro member DB signatures"],
         basis="schema + SemCat bounds (max 45,290 -- protein-scale, not contig-scale)",
         notes="The canonical InterPro-to-protein mapping, 1.18B rows. Frame is UniProt accession, so it "
               "joins to proteins, never directly to genomes."),
    dict(fq="kescience.fitnessbrowser.genedomain", category="both", region_type="protein domain",
         coords="yes", coord_system="amino_acid", coord_frame="Fitness Browser protein (orgId+locusId)",
         seq_ref="locusId", span=("begin", "end"), strand=None,
         id_systems=["Pfam", "TIGRFAM", "EC", "per-row via domainDb"],
         basis="schema: domainDb/domainId with begin/end and no contig column",
         notes="begin/end are STRING-typed -- CAST before any numeric comparison. `domainDb` names the source "
               "database per row, so this table also spans multiple identifier systems."),
    dict(fq="kescience.pdb.pdb_uniprot_mapping", category="both", region_type="structural segment",
         coords="yes", coord_system="multiple", coord_frame="three frames per row: PDB residue numbering, "
                                                            "PDB SEQRES index, UniProt sequence",
         seq_ref="pdb_id + chain / uniprot_accession", span=("res_beg/res_end, sp_beg/sp_end, pdb_beg/pdb_end", ""),
         strand=None, id_systems=["PDB", "UniProt"],
         basis="schema: three distinct begin/end pairs; pdb_beg/pdb_end are string-typed and can be negative",
         notes="Three coordinate systems in one row. pdb_beg lower bound is -1: PDB author numbering is not "
               "guaranteed positive or contiguous. Do not treat as a simple 1-based span."),
    dict(fq="kescience.paperblast.site", category="both", region_type="functional residue/site",
         coords="yes", coord_system="amino_acid", coord_frame="protein sequence (db+id)",
         seq_ref="id", span=("posFrom", "posTo"), strand=None,
         id_systems=["PDB", "UniProt", "ligand IDs", "literature PMIDs"],
         basis="schema: posFrom/posTo plus pdbFrom/pdbTo, ligand and chain columns",
         notes="Residue-level functional sites with literature support. String-typed positions."),

    # ---------------- HMM-model and alignment coordinates ----------------
    dict(fq="nmdc.results.pfam_annotation_gff", category="both", region_type="protein domain",
         coords="yes", coord_system="multiple", coord_frame="two frames per row: the gene's protein "
                                                            "(start/end) and the Pfam HMM profile (model_start/model_end)",
         seq_ref="gene_id", span=("start", "end"), strand=None, id_systems=["Pfam"],
         basis="VALUE CHECK: end-start+1 == alignment_length exactly, so start/end are amino-acid, "
               "not nucleotide, despite the table being named '_gff'",
         notes="Largest annotation table found: 2,684,369,000 rows. The name says GFF, which implies genome "
               "coordinates; the data says protein coordinates. model_start/model_end are positions in the "
               "HMM, which is a third kind of coordinate and not a sequence position at all."),
    dict(fq="nmdc.results.annotation_kegg_orthology", category="both", region_type="alignment segment",
         coords="yes", coord_system="multiple", coord_frame="two frames: query protein (q_start/q_end) and "
                                                            "KO reference protein (s_start/s_end)",
         seq_ref="gene_id", span=("q_start", "q_end"), strand=None, id_systems=["KEGG KO"],
         basis="VALUE CHECK: q_end-q_start+1 == aln_len, so amino-acid coordinates",
         notes="1,831,998,811 rows. These are alignment extents, not domain boundaries -- a KO hit covering "
               "the whole protein gives q_start=1. Useful for coverage filtering, misleading as a 'region'."),
    dict(fq="nmdc.results.annotation_enzyme_commission", category="both", region_type="alignment segment",
         coords="yes", coord_system="multiple", coord_frame="query protein and EC reference protein",
         seq_ref="gene_id", span=("q_start", "q_end"), strand=None, id_systems=["EC"],
         basis="same schema and semantics as annotation_kegg_orthology",
         notes="1,231,453,377 rows."),

    # ---------------- BGC regions ----------------
    dict(fq="kescience.mgnify.gene_bgc", category="both", region_type="biosynthetic gene cluster",
         coords="yes", coord_system="nucleotide", coord_frame="MGnify contig (contig_id)",
         seq_ref="contig_id", span=("start_pos", "end_pos"), strand=None,
         id_systems=["antiSMASH", "MIBiG (nearest_mibig, nearest_mibig_class)"],
         basis="schema: contig_id with integer start_pos/end_pos to 7.3M -- contig scale",
         notes="THE best table for 'genes near a BGC': shares contig_id with kescience.mgnify.gene, so a "
               "genomic-interval join needs no mapping table. Partitioned by biome_id -- filter on it. "
               "Only 35,354 rows, so BGC coverage of MGnify genomes is sparse."),
    dict(fq="refdata.smag.bgc", category="both", region_type="biosynthetic gene cluster",
         coords="yes", coord_system="nucleotide", coord_frame="SMAG MAG contig (accession_id, within mag)",
         seq_ref="accession_id (+ mag)", span=("start", "end"), strand=None,
         id_systems=["antiSMASH (product_prediction)", "BiG-SCAPE (big_scape_class, gcf_class, family_number)"],
         basis="schema: bgc_region/start/end/length with accession_id and mag",
         notes="43,169 rows. Carries BiG-SCAPE gene-cluster-family assignments, so it supports BGC-family "
               "questions the MGnify table cannot. No strand. Joining genes to these regions requires a "
               "gene table in the same MAG/accession frame -- SMAG has no gene table, which is the gap."),
    dict(fq="refdata.microagrobiome.bgc_catalog", category="gene_function", region_type="BGC (no coordinates)",
         coords="no", coord_system="none", coord_frame=None, seq_ref="bgc / anchor / bin", span=None, strand=None,
         id_systems=["BGC identifiers", "host/plant metadata"],
         basis="schema read in full: no start/end column of any kind; latitude/longitude are GEOGRAPHIC",
         notes="139,900 rows. A BGC inventory, NOT a region annotation -- there are no sequence coordinates. "
               "Its only coordinates are lat/long. A user searching for 'BGC tables with coordinates' by "
               "column name would be badly misled by this one."),
    dict(fq="refdata.smag.cas_proteins", category="gene_function", region_type="CRISPR-associated protein",
         coords="no", coord_system="none", coord_frame=None, seq_ref="protein/MAG ids", span=None, strand=None,
         id_systems=["Cas protein typing"], basis="schema: no span columns",
         notes="8,545 rows. Companion to the CRISPR region data in MGnify."),

    # ---------------- other region classes in genome coordinates ----------------
    dict(fq="kescience.mgnify.gene_crispr", category="both", region_type="CRISPR array",
         coords="yes", coord_system="nucleotide", coord_frame="MGnify contig (contig_id)",
         seq_ref="contig_id", span=("crispr_start", "crispr_end"), strand="orientation",
         id_systems=["CRISPR array properties (consensus_repeat, spacer_count)"],
         basis="schema: contig_id with crispr_start/crispr_end",
         notes="42,437 rows. Strand is called `orientation`, not `strand` -- a name-based strand search misses "
               "it unless the pattern includes orientation."),
    dict(fq="kescience.mgnify.gene_defense", category="both", region_type="defense system",
         coords="yes", coord_system="nucleotide", coord_frame="MGnify contig (contig_id)",
         seq_ref="contig_id", span=("system_start", "system_end"), strand=None,
         id_systems=["defense system typing (defense_type, defense_subtype)"],
         basis="schema: contig_id with system_start/system_end, plus gene_id",
         notes="27,858 rows. Has BOTH a region span (the system) and a gene_id -- already does the "
               "gene-to-region linkage that a BGC query has to construct by hand."),
    dict(fq="kescience.mgnify.gene_mobilome", category="both", region_type="mobile genetic element",
         coords="yes", coord_system="nucleotide", coord_frame="MGnify contig (contig_id)",
         seq_ref="contig_id", span=("start_pos", "end_pos"), strand=None,
         id_systems=["mobile element typing (mobile_element_type, tool)"],
         basis="schema: contig_id with start_pos/end_pos",
         notes="171,662 rows. SemCat's bounds show start_pos lower bound of -1, so expect sentinel values."),

    # ---------------- gene / CDS coordinate tables (the join partners) ----------------
    dict(fq="kescience.mgnify.gene", category="both", region_type="gene/CDS",
         coords="yes", coord_system="nucleotide", coord_frame="MGnify contig (contig_id)",
         seq_ref="contig_id", span=("start", "end"), strand="strand",
         id_systems=["gene_type only -- function comes from gene_eggnog / gene_amr / gene_bgc"],
         basis="schema: contig_id, start, end, strand, gene_length",
         notes="142,872,191 rows. The pivot table for MGnify: same contig_id frame as gene_bgc, gene_crispr, "
               "gene_defense, gene_mobilome, and joins by gene_id to gene_eggnog's functional annotation. "
               "This is the one place in BERDL where 'genes near a BGC' is a single clean join."),
    dict(fq="kescience.fitnessbrowser.gene", category="both", region_type="gene/CDS",
         coords="yes", coord_system="nucleotide", coord_frame="Fitness Browser scaffold (scaffoldId within orgId)",
         seq_ref="scaffoldId", span=("begin", "end"), strand="strand",
         id_systems=["free-text desc; function via besthitkegg / seedannotation / besthitmetacyc"],
         basis="schema: scaffoldId with begin/end and strand",
         notes="228,709 rows. begin/end are STRING-typed -- CAST required. Joins to genedomain on "
               "(orgId, locusId), but genedomain's coordinates are amino-acid while these are nucleotide: "
               "the two spans in this one database are in different frames."),
    dict(fq="refdata.bvbrc.bvbrc_feature_fact", category="both", region_type="gene/CDS",
         coords="yes", coord_system="nucleotide", coord_frame="BV-BRC contig (contig within genome_id)",
         seq_ref="contig", span=("start_pos", "end_pos"), strand="strand",
         id_systems=["EC (ec_numbers_json)", "KEGG KO (ko_terms_json)", "protein families (family_ids_json)",
                     "free-text product"],
         basis="schema: contig/start_pos/end_pos/strand alongside product and the JSON identifier columns",
         notes="1,895,015,043 rows -- the largest coordinate-bearing feature table with strand. BUT every "
               "coordinate is STRING-typed and the identifier systems are packed into JSON columns, so both "
               "interval logic and identifier matching need parsing first. Highest-value / highest-friction "
               "table in the census."),
    dict(fq="refdata.jgi_virus.metavr_protein", category="both", region_type="gene/CDS (viral)",
         coords="yes", coord_system="nucleotide", coord_frame="IMG/VR scaffold (scaffold_oid)",
         seq_ref="scaffold_oid", span=("start", "end"), strand="strand",
         id_systems=["Pfam (array-typed)", "protein_cluster", "free-text product"],
         basis="schema: scaffold_oid with start/end/strand and pfam array<string>",
         notes="369,281,941 rows. `pfam` is array<string> -- needs explode(), not equality. One of only a "
               "few tables with nucleotide coordinates, strand, AND a controlled function vocabulary "
               "together, which makes it directly usable for collocation queries."),
    dict(fq="refdata.jgi_mycocosm.features", category="both", region_type="gene/CDS/mRNA (fungal)",
         coords="yes", coord_system="nucleotide", coord_frame="Mycocosm contig (contig_id)",
         seq_ref="contig_id", span=("start", "length_bp -> derived end"), strand="strand",
         id_systems=["free-text functions"],
         basis="schema read in full: there is a `start` and a `length_bp` but NO `end` column",
         notes="17,945,606 rows. End coordinate must be computed as start+length_bp. Any interval query "
               "written against a start/end convention silently fails here."),
    dict(fq="refdata.fungal_db.pombase_gene_coords", category="region", region_type="gene",
         coords="yes", coord_system="nucleotide", coord_frame="S. pombe chromosome",
         seq_ref="chromosome", span=("start", "end"), strand="strand", id_systems=["PomBase gene IDs"],
         basis="schema: chromosome with int start/end/strand",
         notes="12,685 rows. Integer strand encoding. Companions: pombase_cds_coords (5,137), "
               "pombase_exon_coords (18,057) -- a proper exon/CDS/gene hierarchy, rare in BERDL."),
    dict(fq="kbase.genomes.feature", category="region", region_type="gene/CDS",
         coords="yes", coord_system="nucleotide",
         coord_frame="contig, via the kbase.genomes.contig_x_feature bridge",
         seq_ref="contig_id (via contig_x_feature)", span=("start", "end"), strand="strand",
         id_systems=["type, source_database (int codes)",
                     "free-text RAST function via feature_x_protein -> protein.hash -> "
                     "functional_annotation_rast (schema-confirmed, join not executed)"],
         basis="VALUE CHECK (NB04 section 5): in a hash bucket of feature_id, every feature_id is "
               "unique in both feature and contig_x_feature and present in both; features on a "
               "hash bucket of contigs all join to feature and have neighbours within +/-5 kb",
         notes="The largest coordinate-bearing feature table in the census. `feature` has no sequence "
               "column of its own; `kbase.genomes.contig_x_feature` places each feature on a contig, "
               "so collocation works after one join. An earlier census read `feature` in isolation and "
               "recorded the coordinates as unplaceable. `kbase.genomes` also carries "
               "`feature_x_protein`, `protein` (with `hash`) and `functional_annotation_rast` (RAST "
               "free-text function keyed on `protein_hash`); the join from coordinates to function "
               "was not executed, so that chain is schema-confirmed only. "
               "globalusers.kepangenome_parquet_1.feature has the same schema and row count (NB02), "
               "and SemCat does not index it."),
    dict(fq="globalusers.carbon_source_phenotypes.gene_calls_table", category="region", region_type="gene call",
         coords="yes", coord_system="nucleotide", coord_frame="contig",
         seq_ref="contig", span=("start", "end"), strand="strand",
         id_systems=["none directly; KO via kofam_annotation_table on geneid"],
         basis="schema: contig/start/end/strand/frame",
         notes="5,111,055 rows. All coordinate columns STRING-typed with no bounds recorded in SemCat. "
               "Has both `strand` and `frame`."),
    dict(fq="kbase.content.c_<genome>_features", category="both", region_type="gene/CDS",
         coords="packed", coord_system="nucleotide", coord_frame="contig, inside a packed JSON string",
         seq_ref="location[0][0]", span=("location[0][1] + length", ""), strand="location[0][2]",
         id_systems=["SEED Subsystem Ontology (SSO) in ontology_terms JSON", "free-text function"],
         basis="VALUE CHECK: location = [[\"NZ_QSIR01000001.1\",1,\"+\",855]] i.e. "
               "[contig, start, strand, length]; ontology_terms = {\"SSO\":{\"SSO:000009137\":[0,0]}}",
         notes="3,734 rows per genome table, one table family per genome (5 genomes present, each with a "
               "_features and a _cdss table). THE MOST IMPORTANT DISCOVERY-FAILURE CASE IN THE CENSUS: this "
               "table has contig, start, strand AND ontology function assignment, yet not one column name "
               "says start, end, strand, contig, pfam, or go. SemCat misses it and so does any name-based "
               "regex, including the one used to build this census's ground truth. Found only by reading "
               "values of a column called `location`."),

    # ---------------- function assignment without coordinates ----------------
    dict(fq="kbase.ke_pangenome.bakta_annotations", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_cluster_id", span=None, strand=None,
         id_systems=["EC", "GO", "COG", "COG category", "KEGG KO", "RefSeq", "UniParc",
                     "UniRef100/90/50", "free-text product"],
         basis="schema: ten identifier columns keyed on gene_cluster_id, no positional column",
         notes="132,538,155 rows. The widest single-row functional annotation in the pangenome: nine "
               "controlled vocabularies side by side."),
    dict(fq="kbase.ke_pangenome.eggnog_mapper_annotations", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="query_name", span=None, strand=None,
         id_systems=["eggNOG OGs", "COG category", "GO", "EC", "KEGG ko/Pathway/Module/Reaction/rclass/TC",
                     "BRITE", "CAZy", "BiGG Reaction", "Pfam"],
         basis="schema: 14 identifier columns, no positional column",
         notes="93,558,330 rows. Carries the most identifier systems of any single table (14). Pfam here is "
               "a comma-joined string in `PFAMs`, not a span -- so it supports multi-domain membership "
               "queries but NOT domain-order queries."),
    dict(fq="kescience.mgnify.gene_eggnog", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_id", span=None, strand=None,
         id_systems=["eggNOG OGs", "COG category", "GO", "EC", "KEGG ko/pathway/module/reaction",
                     "CAZy", "Pfam"],
         basis="schema: eggNOG-mapper output columns keyed on gene_id, no positional column",
         notes="144,775,367 rows. The functional half of the MGnify pair: joins to mgnify.gene on gene_id, "
               "which HAS coordinates. Together they give function + position without any mapping table."),
    dict(fq="kbase.ke_pangenome.interproscan_go", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_cluster_id", span=None, strand=None,
         id_systems=["GO"], basis="schema: gene_cluster_id + go_id + go_source",
         notes="266,317,724 rows. Carries n_supporting_analyses, so GO calls can be filtered by agreement "
               "across InterProScan member databases."),
    dict(fq="kbase.ke_pangenome.interproscan_pathways", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_cluster_id", span=None, strand=None,
         id_systems=["KEGG", "MetaCyc", "Reactome", "UniPathway (per-row source)"],
         basis="schema: pathway id + source keyed on gene_cluster_id", notes="287,228,475 rows."),
    dict(fq="kbase.ke_pangenome.gapmind_pathways", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_cluster_id / genome", span=None,
         strand=None, id_systems=["GapMind pathway/step"], basis="schema",
         notes="305,471,280 rows. Pathway-step reconstruction rather than term assignment."),
    dict(fq="globalusers.gapmind_pathways.gapmind_pathways", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="genome_id", span=None, strand=None,
         id_systems=["GapMind pathway", "metabolic_category"], basis="schema: genome_id + pathway + score",
         notes="463,729,001 rows but GENOME-level, not gene-level: it scores whether a genome can perform a "
               "pathway. Not a gene-function assignment despite the size. SemCat does not index this database."),
    dict(fq="kbase.ke_pangenome.bakta_amr", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_cluster_id", span=None, strand=None,
         id_systems=["AMR gene names", "reference accession"], basis="schema", notes="83,008 rows."),
    dict(fq="kescience.mgnify.gene_amr", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="gene_id", span=None, strand=None,
         id_systems=["AMRFinder element_type/class/subclass"], basis="schema", notes="8,862 rows."),
    dict(fq="refdata.bvbrc.bvbrc_specialty_gene_fact", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="feature_id", span=None, strand=None,
         id_systems=["specialty gene family (AMR, virulence, drug target)"], basis="schema",
         notes="162,781,795 rows. Joins to bvbrc_feature_fact on feature_id for coordinates."),
    dict(fq="refdata.cazy.annotations", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="protein_accession", span=None, strand=None,
         id_systems=["CAZy family"], basis="schema read in full: 5 columns, no span",
         notes="6,006,576 rows. The authoritative CAZy assignment, but coordinate-free: you cannot ask "
               "where in the protein the CAZy module sits."),
    dict(fq="kescience.pdb.pdb_pfam", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="pdb_id + chain_id", span=None, strand=None,
         id_systems=["Pfam", "UniProt", "PDB"], basis="schema: coverage fraction but no residue span",
         notes="990,166 rows. Has `coverage` but no positions."),
    dict(fq="kbase.nmdc_arkin.proteomics_gold", category="gene_function", region_type=None,
         coords="no", coord_system="none", coord_frame=None, seq_ref="protein identifiers", span=None,
         strand=None, id_systems=["KO", "EC"], basis="schema", notes="345,877 rows."),
    dict(fq="globalusers.carbon_source_phenotypes.kofam_annotation_table", category="gene_function",
         region_type=None, coords="no", coord_system="none", coord_frame=None, seq_ref="geneid", span=None,
         strand=None, id_systems=["KEGG KO"], basis="schema: geneid + koid + genomeid",
         notes="5,235,819 rows. A clean gene->KO assignment whose KO column is named `koid` -- short enough "
               "that a KO-aware regex keyed on 'ko_' or 'ko_term' misses it. SemCat labels it nothing."),
    dict(fq="kescience.fitnessbrowser.besthitkegg", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="orgId + locusId", span=None, strand=None,
         id_systems=["KEGG"], basis="schema", notes="200,074 rows."),
    dict(fq="kescience.fitnessbrowser.seedannotation", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="orgId + locusId", span=None, strand=None,
         id_systems=["SEED subsystem/role"], basis="schema", notes="177,519 rows."),
    dict(fq="kescience.fitnessbrowser.besthitmetacyc", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="orgId + locusId", span=None, strand=None,
         id_systems=["MetaCyc"], basis="schema", notes="59,723 rows."),
    dict(fq="refdata.fungal_db.sgd_go_annotations", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="SGD gene ID", span=None, strand=None,
         id_systems=["GO"], basis="schema", notes="138,996 rows."),
    dict(fq="refdata.merops.uniprot_family_map", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="uniprot accession", span=None, strand=None,
         id_systems=["MEROPS peptidase family", "UniProt"], basis="schema", notes="116,733 rows."),
    dict(fq="refdata.tcdb.acc_to_tcid", category="gene_function", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="accession", span=None, strand=None,
         id_systems=["TCDB TC number"], basis="schema",
         notes="24,691 rows. Transporter classification. Companions tcdb.pfam_xref (8,869) and "
               "tcdb.go_xref (34,497) bridge TC numbers to Pfam and GO."),
    dict(fq="kbase.nmdc_arkin.metatranscriptomics_gold", category="region", region_type="expressed feature",
         coords="no", coord_system="none", coord_frame=None, seq_ref="img_scaffold_oid",
         span=None, strand="strand", id_systems=["expression values"],
         basis="schema: img_scaffold_oid, length and strand, but no start or end column",
         notes="Not coordinate-bearing under the census rule (a table is coordinate-bearing only if "
               "it has a positional span: start+end, start+length, or a packed location). It names "
               "a scaffold and a strand but gives no position on it. One of only two columns SemCat "
               "correctly labels `strand`."),

    # ---------------- reference vocabularies (define terms; assign nothing to a gene) ----------------
    dict(fq="kescience.interpro.entry", category="reference_vocabulary", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref=None, span=None, strand=None,
         id_systems=["InterPro"], basis="schema: entry definitions, no gene/protein reference",
         notes="51,489 rows. Use to resolve ipr_id to a name/type."),
    dict(fq="refdata.interpro.interpro2go", category="reference_vocabulary", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref=None, span=None, strand=None,
         id_systems=["InterPro", "GO"], basis="schema: term-to-term mapping", notes="30,122 rows."),
    dict(fq="refdata.interpro.entry_xref", category="reference_vocabulary", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="protein accession", span=None, strand=None,
         id_systems=["InterPro", "cross-referenced member DBs"], basis="schema",
         notes="626,311,209 rows -- very large for a reference table; it is effectively a "
               "protein-to-entry mapping."),
    dict(fq="nmdc.ref_data.pfam_terms", category="reference_vocabulary", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref=None, span=None, strand=None, id_systems=["Pfam"],
         basis="schema", notes="27,481 rows. Resolves Pfam accessions to names for pfam_annotation_gff."),
    dict(fq="refdata.rhea.rhea2uniprot", category="reference_vocabulary", region_type=None, coords="no",
         coord_system="none", coord_frame=None, seq_ref="uniprot accession", span=None, strand=None,
         id_systems=["Rhea", "UniProt"], basis="schema",
         notes="397,133 rows. With rhea2ec (7,928) and rhea2go (6,957), bridges reactions to EC/GO."),
]

# Tables a name-based rule flagged that are NOT gene/protein function or region annotation.
# Recorded because the false positives are part of the honest answer.
EXCLUDED = [
    ("kbase.nmdc_arkin.metabolomics_gold", "mass spectrometry; 'start'/scan/retention-time columns, "
                                           "'kegg' refers to compound not gene"),
    ("kbase.nmdc_arkin.lipidomics_gold", "mass spectrometry lipid features, not gene annotation"),
    ("kbase.nmdc_arkin.biochemical_features_metadata", "mass-spec feature metadata; all columns string-typed"),
    ("nmdc.metadata.material_processing_set", "laboratory protocol metadata; `stranded_orientation` and "
                                              "`is_stranded` are RNA-seq LIBRARY strandedness, not genomic "
                                              "strand -- and these are two of the six columns SemCat labels "
                                              "`strand`"),
    ("nmdc.metadata.workflow_execution_set", "assembly/workflow statistics; `contigs` is a count"),
    ("nmdc.metadata.biosample_set", "sample metadata; `location` is geographic"),
    ("globalusers.heterotrophicbacteria.whole_table", "12,640 columns of genome-level trait predictions; "
                                                      "no gene-level assignment"),
    ("kbase.content.c_<genome>", "genome-level metadata, one row per genome; the _features and _cdss "
                                 "child tables are the annotation-bearing ones"),
    ("kescience.alphafold.alphafold_msa_depths", "two columns: uniprot_accession and msa_depth; a quality "
                                                 "metric, not a function"),
    ("refdata.fungal_db.sgd_variant", "variant coordinates on a chromosome -- genuine genomic coordinates, "
                                      "but allele/consequence data rather than function annotation"),
    ("refdata.spire.mag_coordinates", "named 'coordinates' but entirely GEOGRAPHIC lat/long"),
    ("bervodata.fao_soils.*, bervodata.hwsd2.*", "soil property tables; matched a function regex on "
                                                 "unrelated column abbreviations"),
    ("nmdc.metadata.genome_feature_set", "EMPTY (0 rows) despite a complete GFF3 schema with "
                                         "seqid/start/end/strand/phase and feature_category_term_id. The "
                                         "schema promises the single best-modelled feature table in BERDL; "
                                         "the table has no data. Its staging copies are empty too."),
]
