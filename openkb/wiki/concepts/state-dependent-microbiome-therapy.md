---
type: "Concept"
sources: ["summaries/ibd_phage_targeting__REPORT.md"]
description: "Therapy that adapts microbiome targeting to each patient's changing ecological state"
---

# State-Dependent Microbiome Therapy

[[concepts/state-dependent-microbiome-therapy]] is a treatment strategy in which microbiome interventions are selected and revised according to a patient's current ecological state, target carriage, disease activity, and longitudinal microbiome trajectory rather than applied as a fixed cohort-wide regimen. In the Crohn's disease phage-targeting project, the ecological state is represented primarily by a four-class microbiome ecotype framework, with patient-specific target presence and bile-acid coupling cost added before cocktail selection. [src: ibd_phage_targeting]

## Why state dependence is needed

A single pooled CD target list can mismatch individual patients because UC Davis patients occupied multiple ecotypes and differed substantially in Tier-A pathobiont carriage. Among 23 patients, 7 were assigned to E0, 9 to E1, 6 to E3, and 1 had a mixed longitudinal profile; no patient occupied E2. [src: ibd_phage_targeting]

Clinical covariates alone were insufficient for reliable patient-level assignment: a pooled classifier achieved macro AUC 0.799, but agreement with metagenomic ecotype calls in UC Davis was only 41% (9/22 patients). The report therefore treats stool metagenomics, or a future validated rapid proxy, as necessary for initial state assignment. [src: ibd_phage_targeting]

This is an instance of [[concepts/phenotype-resolution-matching]]: the intervention's resolution must match the biological and clinical heterogeneity of the target population. It also depends on [[concepts/microbiome-ecotype-portability]], because the ecotype framework showed cross-study variation even though its operational E1 target list replicated in held-out HMP2 at 88.2% sign concordance. [src: ibd_phage_targeting]

## Operational state variables

The proposed treatment state combines several inputs:

- **Ecotype:** E0, E1, or E3 for the active-CD UC Davis setting; E2 was absent from that cohort. [src: ibd_phage_targeting]
- **Target carriage:** presence of the six actionable Tier-A species in the patient's stool profile. [src: ibd_phage_targeting]
- **Disease activity:** calprotectin is used to distinguish active disease from a reserve-for-flare state, with the report using 250 μg/g as an operational threshold. [src: ibd_phage_targeting]
- **Mechanistic cost:** targeting species involved in bile-acid 7α-dehydroxylation may alter beneficial secondary bile-acid production; this is represented by [[concepts/bile-acid-coupling-cost]]. [src: ibd_phage_targeting]
- **Phage feasibility:** targets are classified by clinical-trial, lytic-literature, temperate-only, or coverage-gap evidence. [src: ibd_phage_targeting]
- **Longitudinal change:** ecotype shifts, target expansion, and treatment response can trigger cocktail reassessment. [src: ibd_phage_targeting]

The decision therefore extends beyond a static abundance ranking. It combines [[concepts/evidence-triangulation]] across taxonomy, metabolites, BGCs, phage susceptibility, and patient-level observations, while retaining explicit uncertainty where evidence is indirect or single-patient. [src: ibd_phage_targeting]

## Proposed dosing logic

The project proposes a provisional workflow:

1. Assign the initial ecotype using stool metagenomics.
2. Identify the patient's Tier-A target species and disease activity.
3. Match each present target to phage availability and ecological cost.
4. Use a hybrid strategy when direct phage coverage is incomplete.
5. Reassess calprotectin and a candidate *Mediterraneibacter gnavus* qPCR proxy every 3–6 months.
6. Trigger full ecotype reassessment after a fivefold change in *M. gnavus* abundance or another substantial state signal. [src: ibd_phage_targeting]

The proposed backbone for active disease is *M. gnavus*, *Hungatella hathewayi*, and *Eggerthella lenta*, which were shared across the E1 and E3 priority sets in the longitudinal example. *Flavonifractor plautii* was treated as E1-specific and *Escherichia coli* as E3-specific, subject to AIEC strain confirmation. [src: ibd_phage_targeting]

These rules illustrate [[concepts/condition-dependent-essentiality]] in a therapeutic rather than gene-essentiality setting: the value and risk of targeting a taxon depend on the surrounding ecological state. They also relate to [[concepts/metabolite-production-utilization-decoupling]], because pathway abundance, metabolite pools, and active biochemical transformation need not change in the same direction. [src: ibd_phage_targeting]

## Hybrid intervention rather than pure phage therapy

State-dependent therapy is necessary partly because phage availability is uneven across targets. The project found a concrete five-phage *E. coli* cocktail—DIJ07_P2, LF73_P1, AL505_Ev3, 55989_P2, and LF110_P2—that covered 94.7% of 188 PhageFoundry-tested strains. However, *H. hathewayi* and *F. plautii* remained coverage gaps, while *M. gnavus* had only temperate-phage evidence. [src: ibd_phage_targeting]

Consequently, all nine E1 patients were judged unsuitable for a complete pure-phage cocktail. The proposed E1 regimen is a three-strategy hybrid: direct phages for feasible targets, non-phage alternatives for coverage gaps or high-cost targets, and engineered or biochemical approaches for limited targets. [src: ibd_phage_targeting]

In particular, *F. plautii* was deprioritized despite its Tier-A score of 3.3 because it combined high carriage, the strongest bile-acid coupling cost, and a phage-coverage gap. The report suggests bile-acid protection or binding co-therapy rather than routine direct depletion, but this remains a precautionary design hypothesis requiring patient-level bile-acid monitoring. [src: ibd_phage_targeting]

## Longitudinal evidence

Patient 6967 provided the project's main biological example of state-dependent redesign. Across two visits, the patient shifted from E1 to E3, while *M. gnavus* expanded 14-fold, from 0.53 to 7.45 reads. *E. lenta*, *F. plautii*, *E. bolteae*, and *H. hathewayi* also increased, and the visit-specific cocktail sets had Jaccard similarity 0.60. [src: ibd_phage_targeting]

Three targets—*H. hathewayi*, *M. gnavus*, and *E. lenta*—were shared between visits. *E. bolteae* and *F. plautii* were present only in the E1 visit, illustrating how an ecotype transition can require targeted cocktail revision without replacing the entire regimen. [src: ibd_phage_targeting]

A technical replicate from patient 1112 had Tier-A rank concordance of Spearman ρ=1.000, supporting the reliability of the taxonomic measurement in that re-sequencing comparison. This validates the technical-noise check, but it does not establish that the proposed dosing rules generalize biologically: the state-transition evidence comes from one longitudinal patient. [src: ibd_phage_targeting]

## Evidence strength and limitations

The state-dependent framework is supported as a computational design proposal, not as a clinically validated dosing protocol. The strongest direct evidence is the observed 6967 trajectory and the reproducibility of the technical replicate; the proposed 3–6-month interval and fivefold qPCR trigger are extrapolations from that single trajectory and should be treated as hypotheses. [src: ibd_phage_targeting]

Important limitations include:

- The longitudinal dosing rule is based on one patient with two visits. [src: ibd_phage_targeting]
- Both 6967 ecotype calls had moderate confidence: 0.64 at visit 1 and 0.41 at visit 2. [src: ibd_phage_targeting]
- The time between visits was unavailable, so the rate of ecological transition is unknown. [src: ibd_phage_targeting]
- The UC Davis cohort contained only 23 patients, and the patient-specific cocktail drafts are templates rather than validated prescriptions. [src: ibd_phage_targeting]
- Bile-acid coupling costs were inferred from paired HMP2 data rather than measured per UC Davis patient. [src: ibd_phage_targeting]
- *M. gnavus* qPCR has not yet been validated as an ecotype proxy. [src: ibd_phage_targeting]
- AIEC strain resolution was unavailable, so *E. coli* phage selection requires confirmation of pks, Yersiniabactin, and Enterobactin-associated features. [src: ibd_phage_targeting]

These limitations make prospective validation essential and connect the concept to [[concepts/coverage-limited-inference]] and [[concepts/method-concordance]]: state transitions should be confirmed using independent measurements where possible, rather than inferred from one classifier or one marker. [src: ibd_phage_targeting]

## Relation to broader microbiome therapy design

State-dependent microbiome therapy is a practical form of [[concepts/multi-omics-integration]]. The report's HMP2 CCA pilot found a dominant joint species–metabolite factor (CC1, r=0.964; CD versus nonIBD cliff δ=+0.498, p=4×10⁻⁴) on which all six actionable species loaded positively. This supports a shared disease axis, but does not eliminate patient-specific ecological differences in which targets are present or safe to remove. [src: ibd_phage_targeting]

The concept also requires attention to [[concepts/functional-redundancy]] and [[concepts/metabolic-support-networks]]. Depleting a taxon should not be assumed to have only a direct effect on that taxon; its metabolites, competitors, and ecological partners may determine whether intervention produces a beneficial or harmful state transition. In this project, paired data weakened the original cross-feeding interpretation involving *Anaerostipes caccae*, shifting the primary ecological-cost annotation toward bile-acid coupling rather than inferred butyrate cross-feeding. [src: ibd_phage_targeting]

## Open Directions

- Validate the proposed fivefold *M. gnavus* qPCR trigger against paired qPCR, metagenomics, calprotectin, and ecotype calls in a prospective longitudinal cohort. [src: ibd_phage_targeting]
- Test whether the 3–6-month reassessment interval captures clinically meaningful ecotype transitions across more than one patient. [src: ibd_phage_targeting]
- Measure patient-level bile-acid panels before and after targeting *F. plautii*, *E. lenta*, or *E. bolteae* to determine whether predicted coupling costs occur. [src: ibd_phage_targeting]
- Compare state-dependent hybrid cocktails with fixed cocktails in an ecotype-stratified clinical pilot, using calprotectin, target abundance, bile-acid profiles, and treatment response as endpoints. [src: ibd_phage_targeting]
- Query INPHARED and IMG/VR for lytic phages against *H. hathewayi*, *M. gnavus*, and *F. plautii* before deciding whether current non-phage alternatives can be replaced. [src: ibd_phage_targeting]

## Source

[[summaries/ibd_phage_targeting__REPORT]]