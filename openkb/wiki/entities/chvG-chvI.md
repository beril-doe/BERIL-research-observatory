---
sources: ["summaries/caulobacter_fur_lipida_loss__REPORT.md"]
type: "Gene_Or_Pathway"
description: "Caulobacter envelope-stress two-component regulatory system"
---

# ChvG-ChvI

## Identity

**ChvG-ChvI** is a two-component envelope-stress regulatory system comprising the ChvG sensor kinase and ChvI response regulator in *Caulobacter crescentus*. [src: caulobacter_fur_lipida_loss]

- **ChvG:** sensor kinase; *C. crescentus* locus identity was reported as ChvG in the comparative annotation analysis. [src: caulobacter_fur_lipida_loss]
- **ChvI:** response regulator, locus CCNA_00237. [src: caulobacter_fur_lipida_loss]
- **Aliases:** ChvGI; ChvG–ChvI; ChvG-ChvI two-component system.

ChvG-ChvI is linked to [[entities/caulobacter-crescentus]], [[concepts/envelope-remodeling-under-lipid-stress]], and [[concepts/outer-membrane-lipid-homeostasis]].

## Role in Δ*lpxc* rescue

The report supports a phased ChvI response during Δ*fur* Δ*sspB*-permitted Δ*lpxc* lipid A loss. Published ChvI-induced genes were partitioned into 20 genes unique to the early contrast, 10 genes induced in both early and late contrasts, and 49 genes induced only after lipid A loss. [src: caulobacter_fur_lipida_loss]

ChvI itself belongs to the 10-gene both-phase cohort and shows logFC +1.45 in the 4584-vs-4580 contrast, providing evidence consistent with ChvI autoregulation during the Δ*fur* and Δ*sspB* release phase. [src: caulobacter_fur_lipida_loss]

The early cohort includes the lasso peptide cyclase CCNA_02794, the ApbE iron-sulfur cluster repair protein, and *imuB* SOS DNA polymerase. [src: caulobacter_fur_lipida_loss] The both-phase cohort includes the SIMPL-family protein CCNA_02378 and the amelogenin/CpxP-related protein CCNA_03997. [src: caulobacter_fur_lipida_loss]

The late cohort includes the LolA-family outer-membrane lipoprotein carrier CCNA_03820, the Pal-like Tol-Pal factor CCNA_00784, multiple TBDTs, and other envelope-associated genes. [src: caulobacter_fur_lipida_loss] The induction of CCNA_03820 in both Δ*lpxc* lipid A loss and Δ*spt* sphingolipid loss is consistent with LolA functioning as a general Caulobacter outer-membrane-stress response. [src: caulobacter_fur_lipida_loss]

## Evidence assessment

The phase-structure hypothesis passed its preregistered threshold, with at least 10 genes in each cohort. [src: caulobacter_fur_lipida_loss] The shift from regulator-rich early responses toward envelope-structural late responses is suggestive, but the corresponding Fisher test was not statistically significant (p = 0.243). [src: caulobacter_fur_lipida_loss]

The report did not establish that SigU drives the late ChvI cohort. Caulobacter SigU, CCNA_02977, lacks a substantive published PaperBLAST literature signal, and the late-cohort functional coherence result was 24.5%, below the relaxed 50% criterion. [src: caulobacter_fur_lipida_loss] SigU should therefore be treated as an unresolved regulatory possibility rather than an established upstream driver.

## Comparative distribution

NCBI annotation analysis found ChvG in *C. crescentus* but not in the comparator species *Acinetobacter baumannii*, *Neisseria meningitidis*, or *Moraxella catarrhalis*, with reported counts of 5, 0, 0, and 0, respectively. [src: caulobacter_fur_lipida_loss] The corresponding ChvI counts were 6, 0, 0, and 0. [src: caulobacter_fur_lipida_loss]

This distribution supports the report's conclusion that ChvG-ChvI is Caulobacter-restricted within the tested species panel and contributes to the [[concepts/organism-specificity]] of the Caulobacter lipid A-loss rescue strategy. [src: caulobacter_fur_lipida_loss]

## Related entities and evidence

- [[entities/caulobacter-crescentus]] — host organism in which ChvG-ChvI was analyzed.
- [[entities/sigu]] — uncharacterized candidate regulator considered for the late ChvI cohort.
- [[entities/lpt-transport-apparatus]] — envelope transport machinery discussed alongside the ChvI response.
- [[entities/tol-pal-complex]] — envelope-integrity system represented by late-induced Pal-like CCNA_00784.
- [[entities/lpxC]] — lipid A biosynthesis gene whose loss defines the stress state.
- [[entities/anionic-sphingolipids]] — substitute outer-membrane lipid context for Δ*lpxc* viability.
- [[summaries/caulobacter_fur_lipida_loss__REPORT]] — source report integrating the ChvI phase analysis and comparative distribution.

## Open questions

A SigU-induction RNA-seq experiment is needed to determine whether SigU directly regulates the late ChvI cohort. [src: caulobacter_fur_lipida_loss] ChvG-ChvI target validation across the strain series would also help distinguish direct regulatory effects from downstream consequences of lipid A loss. [src: caulobacter_fur_lipida_loss]