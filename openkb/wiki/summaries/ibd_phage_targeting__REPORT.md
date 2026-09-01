---
type: "Summary"
description: "Ecotype-guided, hybrid phage-cocktail design for Crohn's disease"
doc_type: short
full_text: "sources/ibd_phage_targeting__REPORT.md"
---

# Summary: Metagenome-Prioritized Phage Cocktails for Crohn's Disease and IBD

## Overview

This report closes five project pillars for designing [[concepts/microbiome-ecotype-portability|ecotype-guided]] and patient-specific phage cocktails for Crohn's disease (CD). It integrates metagenomics, pathway and BGC analysis, metabolomics, strain adaptation, serology, viromics, phage susceptibility, and longitudinal patient profiling. The central claim is that CD-associated microbiome variation in HMP2 is dominated by one joint species–metabolite direction, while actionable targeting still requires ecotype and patient stratification.

The project analyzed 8,489 curatedMetagenomicData samples, 1,627 externally held-out HMP2 samples, 23 UC Davis CD patients, 468 paired HMP2 metabolomics–metagenomics samples, and multiple reference collections. It produced 31 notebooks, 24 stated novel contributions, six actionable Tier-A targets, a five-phage *E. coli* cocktail, per-patient cocktail drafts, and a four-phase clinical-translation roadmap.

## Core findings

### Four operational ecotypes

A consensus K=4 framework was selected using cross-method adjusted Rand index and parsimony rather than monotonically improving LDA perplexity or GMM BIC. The ecotypes were:

- **E0:** diverse commensal, dominant among healthy controls.
- **E1:** Bacteroides2-transitional, enriched in CD and UC.
- **E2:** *Prevotella copri* enterotype, largely non-Western healthy.
- **E3:** severe Bacteroides-expanded state associated with IBD flare and related dysbiosis.

The 23 UC Davis patients occupied E0 (27%), E1 (42%), and E3 (31%), with no E2 patients; this distribution differed from uniformity (χ²(3)=10.0, p=0.019). Clinical covariates alone were inadequate for patient-level ecotype assignment: a pooled classifier achieved macro AUC 0.799 but only 41% agreement with metagenomic projections in UC Davis. Stool metagenomics therefore remains necessary for operational ecotype assignment.

The framework is useful but not fully stable. Leave-one-substudy-out ecotype stability was modest (mean ARI=0.113; range 0.000–0.282), and the original consensus had only 48.9% LDA–GMM agreement. Held-out HMP2 nonetheless showed disease-stratifying ecotype structure (χ²=15.61, p=0.016), high projection confidence (80.4% of samples above 0.70), and strong replication of the E1 target list.

### Rigor repair and Tier-A targets

The original NB04 within-ecotype analysis was superseded after [[concepts/adversarial-methodological-review|adversarial review]] identified study-confounding and feature-leakage problems. The replacement design used CD-versus-nonIBD contrasts within IBD substudies, followed by within-ecotype stratification and inverse-variance meta-analysis. This avoids both the absence of shared HC/CD studies in curatedMetagenomicData and the circularity of clustering and testing the same taxa.

The replacement analysis found:

- E1 had 51 meta-viable Tier-A candidates, all 100% sign-concordant across two substudies.
- E3 had 40 provisional candidates from one eligible substudy and requires replication.
- Five of six donor-2708 engraftment pathobionts were CD-enriched in the confound-free contrast: *Mediterraneibacter gnavus*, *Eggerthella lenta*, *Escherichia coli*, *Enterocloster bolteae*, and *Hungatella hathewayi*.
- *Clostridium scindens* was CD-enriched in the confound-free design (CLR-Δ=+1.18, FDR=1e-8, 4/4 sign concordance); the prior “paradox resolution” based on within-ecotype nonsignificance was retracted.
- The E1 Tier-A list replicated in held-out HMP2 at 88.2% sign concordance (45/51 candidates).

NB05 scoring produced six actionable targets:

1. *Hungatella hathewayi* — score 4.0
2. *Mediterraneibacter gnavus* — score 3.8
3. *Escherichia coli* — score 3.6
4. *Eggerthella lenta* — score 3.3
5. *Flavonifractor plautii* — score 3.3
6. *Enterocloster bolteae* — score 2.8

These species generally co-clustered in a single pathobiont module across E1 and E3 subnetworks, supporting multi-target ecological intervention and connecting to [[concepts/cofitness-networks|cofitness-network]] reasoning. However, module co-occurrence did not establish cross-feeding: paired metabolomics–metagenomics produced only seven strict candidate triangles, and lactate associations had opposite signs for *Anaerostipes caccae* versus *F. plautii* and *E. bolteae*. The original metabolic-coupling-cost interpretation was therefore reframed as shared-environment co-occurrence.

## Mechanism findings

### Iron and AIEC specialization

The strongest mechanistic narrative centers on an AIEC-associated *E. coli* subset and iron acquisition. Evidence converged across pathway attribution, MetaCyc class enrichment, sample-level co-variation, BGC content, and literature, illustrating [[concepts/evidence-triangulation|evidence triangulation]]:

- Iron/heme pathways were enriched among CD-up pathways (OR=8.11, FDR=7.4e-6; 15 of 52 CD-up pathways).
- *E. coli* had the strongest iron-pathway co-variation (mean ρ=+0.45).
- Tier-A iron-siderophore BGCs were enriched against the full catalog (OR=44.4, FDR=6.5e-56).
- Within the six actionable targets, *E. coli* alone carried the canonical iron/genotoxin MIBiG repertoire: 54 iron BGCs and 25 genotoxin BGCs, including Yersiniabactin, Enterobactin, Colibactin, and Microcin B17.
- The cross-cohort ebf/ecf fatty-acid-amide signal replicated across four cohorts with meta p-values of 1.1e-31 and 5.1e-33.

This supports strain-resolved targeting of AIEC rather than indiscriminate depletion of all *E. coli*. The project could not perform the planned species-by-BGC interaction test because the required raw-read-derived per-sample BGC abundance was unavailable.

### Bile-acid 7α-dehydroxylation

A second cross-corroborated mechanism concerns bile-acid metabolism. Paired HMP2 samples showed a substrate–product pattern consistent with activity by *F. plautii*, *E. lenta*, and *E. bolteae*: associations with primary bile acids were negative while associations with secondary bile acids were positive. Examples include *F. plautii* with cholate (ρ=-0.26) and lithocholate (ρ=+0.15), and *E. bolteae* with deoxycholate (ρ=+0.17) and lithocholate (ρ=+0.18).

HMP2 metabolomics also showed CD-up tauro-α/β-muricholate and free taurine, consistent with altered microbial bile-acid transformation. This made [[concepts/bile-acid-coupling-cost|bile-acid coupling cost]] the primary ecological-cost annotation for cocktail design:

- **Highest cost:** *F. plautii*.
- **Moderate cost:** *E. lenta* and *E. bolteae*.
- **Low cost in this dataset:** *H. hathewayi*, *M. gnavus*, and *E. coli*.

The report consequently recommends caution or deprioritization of *F. plautii* targeting, with bile-acid monitoring and possible UDCA or bile-acid-binding co-therapy. This is a mechanistic hypothesis requiring per-patient bile-acid measurements, not a clinically validated treatment rule.

### Other multi-omics signals

The H3 framework tested pathway, BGC, metabolite, strain, and serology hypotheses:

- Pathway DA identified 52 CD-up pathways and strong *E. coli* pathway attribution.
- *H. hathewayi* showed CD-up biosynthesis and purine/TMA–choline themes.
- Kumbhari strain analysis supported IBD-adaptation enrichment (OR=1.38, p=2.4e-6) and housekeeping depletion (OR=0.62, p=6.4e-20). *F. plautii* had zero FDR-significant strain-adaptation genes, suggesting its CD association is primarily abundance-mediated rather than strain-content-mediated.
- HMP2 metabolomics identified polyamine enrichment (OR=14.6, FDR=0.008) and long-chain PUFA enrichment (OR=7.9, FDR=0.009). Urobilin was CD-depleted and replicated across FRANZOSA_2019 at 100% sign concordance; acyl-carnitines and long-chain PUFAs replicated at 80% and 75%.
- Serology retained canonical CD/UC patterns but did not predict individual target abundance. The strongest target association was ANCA × *M. gnavus* (partial r=+0.31, FDR=0.40), below the prespecified threshold.
- Metabolite-feature clustering failed as a portable ecotype basis: cross-cohort LOSO ARI was 0.000 because PC1 explained 79% of variance through cohort batch effects. Taxonomic ecotypes remain primary.

A two-modality CCA pilot provided an integrative capstone. On 106 paired HMP2 subjects, CC1 had canonical correlation r=0.964, separated CD from nonIBD with cliff δ=+0.498 and p=4e-4, and loaded positively on all six actionable species. Urobilin and secondary bile acids loaded negatively, while polyamines, PUFAs, fatty-acid amides, and cadaverine loaded positively. The report interprets this as a single dominant [[concepts/principal-direction-multi-omics|principal direction in joint species–metabolite space]], while noting that CCA is a pilot and does not replace a full sparse three-modality MOFA+ analysis.

## Phage targetability

The report triangulated three independent evidence layers: curated literature, experimental susceptibility, and endogenous HMP2 phageome observations. This is an application of [[concepts/evidence-triangulation|evidence triangulation]] to therapeutic feasibility.

### Actionable-target phage classes

- *E. coli* AIEC: clinical-trial-stage and experimentally tractable.
- *E. lenta*: lytic-literature support through PMBT5.
- *E. bolteae*: lytic-literature support through PMBT24.
- *M. gnavus*: six known phages, all temperate or limited.
- *H. hathewayi*: coverage gap.
- *F. plautii*: coverage gap and highest bile-acid coupling cost.

The highest-scoring targets were therefore not necessarily the easiest to target. *H. hathewayi* and *F. plautii* had the weakest phage evidence, while *E. coli* had the strongest phage feasibility but only 35% carriage in UC Davis patients.

### Five-phage *E. coli* cocktail

The PhageFoundry matrix contained 96 phages, 188 *E. coli* strains, and 17,672 experimentally tested susceptibility pairs, with a 22% overall susceptibility rate. Greedy minimum-set-cover produced a five-phage cocktail covering 94.7% of the 188 strains:

- DIJ07_P2
- LF73_P1
- AL505_Ev3
- 55989_P2
- LF110_P2

An eight-phage extension reached 98.4% coverage. Sixty-five of 94 phages with phylogroup information were isolated against B2/D hosts, which are relevant to AIEC, but the dataset did not explicitly label all strains as AIEC. The coverage estimate therefore applies to the PhageFoundry strain panel, not directly to UC Davis patient isolates. A per-patient pks/Yersiniabactin/Enterobactin diagnostic is required.

HMP2 endogenous phageome data found Gokushovirus WZ-2015a depletion in CD, particularly in E1 (cliff δ=-0.358, FDR=5e-7), and modest positive correlations between *E. coli* and Podoviridae (ρ=+0.183) or Myoviridae (ρ=+0.125). However, 80% of phage observations were classified as “Unknown,” and no strong endogenous phage signal was found for the anaerobic target gaps.

## Patient-specific cocktail framework

NB15 profiled 23 UC Davis patients. Target carriage was:

- *M. gnavus*: 21/23 (91%)
- *H. hathewayi*: 19/23 (83%)
- *E. bolteae*: 19/23 (83%)
- *F. plautii*: 18/23 (78%)
- *E. lenta*: 16/23 (70%)
- *E. coli*: 8/23 (35%)

Fourteen of 23 patients (61%) received concrete phage-cocktail drafts. All nine E1 patients carried the full five-species E1 pathobiont module, but pure phage treatment was infeasible because *H. hathewayi* and *F. plautii* lacked suitable phage evidence and *M. gnavus* was temperate-only. The proposed E1 design is therefore a three-strategy hybrid:

1. **Direct phage targeting:** *E. coli* AIEC when present, PMBT24 for *E. bolteae*, and PMBT5 for *E. lenta*.
2. **Alternative therapies:** enzyme inhibition for *H. hathewayi* and bile-acid protection or co-therapy for *F. plautii*.
3. **Limited or engineered approaches:** lytic-locked *M. gnavus* phages or biochemical targeting of glucorhamnan synthesis.

The final patient-strategy distribution was 12 reserve-for-flare patients, four E1 hybrid patients without *E. coli*, four E0 limited-strategy patients, one E1 hybrid patient with *E. coli*, one E3 focused patient with *E. coli*, and one state-dependent patient.

## Longitudinal dosing hypothesis

Patient 6967 showed an E1-to-E3 transition between two visits. *M. gnavus* increased 14-fold, from 0.53 to 7.45 reads, while *E. lenta*, *F. plautii*, *E. bolteae*, and *H. hathewayi* also increased. The visit-specific target sets had Jaccard similarity 0.60: three targets were shared, while *E. bolteae* and *F. plautii* were present only in the E1 visit. Patient 1112 technical replicates had Tier-A Spearman ρ=1.000, supporting the technical reliability of the Kaiju calls.

The report proposes five [[concepts/state-dependent-microbiome-therapy|state-dependent dosing]] rules:

- Reassess ecotype every 3–6 months during active disease.
- Drop *F. plautii* targeting after E1-to-E3 transition.
- Consider *E. coli* targeting in E3, contingent on AIEC strain detection.
- Use *M. gnavus*, *H. hathewayi*, and *E. lenta* as a provisional cross-ecotype backbone.
- Test *M. gnavus* qPCR as a low-cost proxy; a fivefold change would trigger full ecotype reassessment.

These rules are hypotheses from one biological longitudinal trajectory, not established clinical practice. The 3–6-month interval and fivefold threshold were not derived from a powered longitudinal study.

## Methodological contributions

The report highlights several reusable lessons for microbiome research:

- Use cross-method ARI and parsimony when conventional clustering fit metrics favor ever-larger K.
- Distinguish classifier AUC from patient-level transfer utility.
- Build a taxonomic synonymy layer using NCBI taxids and version-aware GTDB renames before multi-cohort integration.
- Detect structural study–diagnosis confounding before fitting mixed models, consistent with [[concepts/phylogenetic-confounding|confounding-aware]] study design.
- Avoid feature leakage when clustering and differential abundance use the same taxa.
- Prefer within-substudy, within-ecotype meta-analysis for stratified disease contrasts.
- Use LOSO rather than bootstrap stability for cross-cohort claims.
- Treat pathway flux and metabolite pools as distinct evidence streams, reflecting [[concepts/metabolite-production-utilization-decoupling|production–utilization decoupling]].
- Prefer curator-validated ontologies over pathway-name regexes.
- Triangulate phage feasibility with literature, experimental host range, and in-vivo phageome evidence.
- Expect absolute-intensity metabolomics to require [[concepts/batch-confounding|batch-confounding]] correction before cross-cohort clustering.

## Limitations and next steps

The most important limitations are the marginal cross-study stability of the ecotype framework, provisional single-study E3 evidence, small UC Davis sample size, Kaiju–MetaPhlAn3 classifier mismatch, lack of per-patient bile-acid measurements, absence of AIEC strain resolution, 80% unknown phage-family classification, and the n=1 basis for state-dependent dosing.

The roadmap prioritizes:

1. INPHARED and IMG/VR searches for *H. hathewayi*, lytic *M. gnavus*, and *F. plautii* phages.
2. A per-patient AIEC diagnostic based on pks, Yersiniabactin, and Enterobactin markers.
3. Prospective validation of *M. gnavus* qPCR as an ecotype-state proxy.
4. Targeted qPCR ecotype panels and per-patient bile-acid assays.
5. Multi-cohort serology and expanded longitudinal sampling.
6. Batch-corrected metabolomics clustering and external polyamine replication.
7. Eventually, a clinical pilot of hybrid, ecotype-aware cocktails.

## Final synthesis

The report's final thesis is that CD in HMP2 is represented by a dominant joint species–metabolite direction (CCA CC1 r=0.96), within which six actionable pathobionts and two mechanistic narratives—AIEC iron acquisition and bile-acid 7α-dehydroxylation—support an ecotype-aware, state-dependent, hybrid-cocktail framework. The framework produced concrete drafts for 14 of 23 UC Davis patients, but remains a computational translational plan requiring external phage discovery, strain-level diagnostics, per-patient biochemical monitoring, and prospective clinical validation.

## Related Concepts
- [[concepts/state-dependent-microbiome-therapy]]
- [[concepts/principal-direction-multi-omics]]
- [[concepts/functional-redundancy]]
- [[concepts/organism-specificity]]
- [[concepts/pathway-completeness]]
- [[concepts/pangenome-integration]]
- [[concepts/resource-darkness]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/metabolic-competitive-exclusion]]

## Entities
- [[entities/bacdive]]
- [[entities/kegg]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/gapmind]]
- [[entities/iron]]
- [[entities/pqq]]
