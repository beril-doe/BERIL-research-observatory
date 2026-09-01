<!-- tension-hash: e18145522f7b11ff -->
# Does Marker or Gene Presence Establish Pathway Completeness, or Only Suggest It?

Across two independent datasets, high prevalence of a pathway's diagnostic genes is used to argue for near-universal metabolic completeness, while closer inspection of exceptions and corroborating evidence undercuts that conclusion. The disagreement matters because it determines whether "conserved" or "abundant" marker signals can be read as functional completeness claims, or whether they must be treated as provisional until gaps and annotation artifacts are resolved. [[concepts/pathway-completeness]]

## Evidence Sides

**For near-universal completeness from marker/gene prevalence**
- 17 of 18 amino acid pathways were found to be universal within the seven organisms analyzed, supporting strong conservation of pathway completeness. [src: essential_metabolome]
- XoxF outnumbers mxaF by **18.92:1**, suggesting the xoxF-based methylotrophy pathway dominates and is broadly represented across genomes. [src: lanthanide_methylotrophy_atlas]

**Against treating prevalence as proof of complete, verified pathways**
- The serine pathway is the one exception among the 18 amino acid pathways, preventing any claim of strict universality despite the otherwise high conservation. [src: essential_metabolome]
- **897 xoxF-bearing genomes** showed no PQQ evidence from either eggNOG or Bakta, meaning marker prevalence (the 18.92:1 ratio) does not equate to a ratio of experimentally verified complete pathways. [src: lanthanide_methylotrophy_atlas]
- Source-specific calls diverge sharply: eggNOG's `Preferred_name='lanM'` produced **505** likely false positives, while Bakta identified only **62** lanmodulin-positive genomes, restricted to three α-Proteobacterial methylotroph families — showing completeness conclusions shift with the annotation source. [src: lanthanide_methylotrophy_atlas]

## Possible Reconciliations

- **Definitional-scope hypothesis**: "Pathway completeness" may mean different things — presence of one diagnostic marker gene versus full biosynthetic/cofactor pathway verification. The amino acid and xoxF/mxaF claims may both be locally correct once the definition (marker-level vs. pathway-level) is fixed. [src: essential_metabolome][src: lanthanide_methylotrophy_atlas]
- **Ecological-streamlining hypothesis**: The *D. vulgaris* serine exception could reflect real gene loss enabled by environmental nutrient availability rather than a detection failure. [src: essential_metabolome]
- **Annotation-artifact hypothesis**: The 897 PQQ-negative xoxF genomes and the eggNOG/Bakta lanM discrepancy may both stem from incomplete or inconsistent gene models rather than genuine pathway absence. [src: lanthanide_methylotrophy_atlas]

## Resolving Work

- Targeted re-annotation or manual curation of the 897 xoxF-positive, PQQ-negative genomes using additional PQQ synthesis HMMs to distinguish annotation gaps from true absence.
- Experimental (transcriptomic/metabolomic) validation of serine biosynthesis activity in *D. vulgaris* to test streaming vs. artifact explanations.
- Cross-source concordance analysis comparing eggNOG and Bakta calls for lanM (and other markers) across a shared genome set to quantify true/false positive rates against a curated gold-standard set.
- Expansion of the seven-organism amino-acid pathway sample to test whether the serine exception persists across a broader, more diverse taxonomic panel.
