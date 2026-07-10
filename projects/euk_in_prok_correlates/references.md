# References: Factors Correlating with Eukaryotic Content/Contamination in Prokaryote-Targeted Shotgun Metagenomes

Focused literature review. TOPIC: What sample collection, processing, and sequencing factors correlate with eukaryotic (host/plant/fungal/protist) contamination or content of samples collected for prokaryotic (bacterial/archaeal) shotgun metagenome analysis?

Compiled 2026-07-10. Priority given to papers that QUANTIFY the eukaryotic fraction and relate it to a measurable metadata variable. Citation counts are as reported by Europe PMC at time of search (noisy; treat as rough).

---

## Thread 1 — Prevalence & quantification of eukaryotic DNA in prokaryote-targeted shotgun metagenomes

- **Eisenhofer R, Alberdi A, Woodcroft BJ. 2026.** "Large-scale estimation of bacterial and archaeal DNA prevalence in metagenomes reveals biome-specific patterns." *mSystems.* DOI: 10.1128/msystems.01062-25. PMID: 41854267; PMCID: PMC13098197. **[MUST-CITE / most directly on-topic]**
  - Introduces **SingleM prokaryotic_fraction (SPF)**, a reference-free algorithm estimating the fraction of reads that are bacterial/archaeal (i.e., the complement of the eukaryotic+viral fraction) and average prokaryotic genome size, applicable to any Illumina metagenome. Applied to **136,284 public metagenomes**; reports **substantial, biome-specific variation in prokaryotic fraction** (host-associated and plant/soil samples show much lower prokaryotic fraction than open-water/engineered samples). Proposes the domain-adjusted mapping rate (DAMR) for genome-recovery QC. Also flags large amounts of un-screened human host DNA in public repositories. **This is the single closest existing large-scale, cross-collection quantification of euk vs prok content and the biome as its primary correlate.**

- **Nayfach S, Roux S, Seshadri R, ... Eloe-Fadrosh EA. 2021.** "A genomic catalog of Earth's microbiomes (GEM)." *Nat Biotechnol.* DOI: 10.1038/s41587-020-0718-6. PMID: 33169036; PMCID: PMC8041624.
  - >10,000 metagenomes across all biomes → 52,515 MAGs. Establishes that MAG recovery (a proxy for usable prokaryotic yield) varies strongly by habitat; host-associated and soil samples are systematically harder. Background/context for how euk content and community complexity depress prokaryotic genome recovery across a public collection. Does not itself report euk read fraction.

- **Orr RJS, Brynildsrud O, Bøifot KO, ... Dybwad M. 2026.** "Spatial and temporal patterns of public transit aerobiomes." *Microbiome.* DOI: 10.1186/s40168-025-02303-7. PMID: 41555453; PMCID: PMC12896060.
  - Low-biomass shotgun aerobiomes; explicitly required stringent trimming + **exogenous-contamination removal** and improved fungal databases to obtain species-level resolution, and publishes a contaminant taxon core. Illustrates that bacteria-vs-fungi partitioning and contaminant load are analysis-pipeline- and biome-dependent.

## Thread 2 — Upstream factors driving eukaryotic read fraction (matrix, extraction, fractionation, platform, depth, library)

- **Sobolev A, Sibiryakina D, ... Isaev A. 2025.** "Benchmarking Cost-Effective DNA Extraction Kits for Diverse Metagenomic Samples." *Int J Mol Sci.* DOI: 10.3390/ijms262311616. PMID: 41373768; PMCID: PMC12692181.
  - Directly assessed **eukaryotic DNA admixture** (plus kitome/"splashome") as an explicit output across 8 kits × 4 matrices (freshwater, sediment, oyster gut, feces). Finds **DNA-extraction kit and sample matrix both drive eukaryotic admixture** and reproducibility; host-associated (oyster) matrices carried more eukaryotic DNA. Effect direction: kit choice and matrix jointly determine euk fraction. Implicates: extraction kit, matrix.

- **Chevokina E, Sibiryakina D, ... Isaev A. 2025.** "Efficient recovery and DNA extraction for algae-associated microbial communities." *Front Plant Sci.* DOI: 10.3389/fpls.2025.1693747. PMID: 41560914; PMCID: PMC12813104.
  - Cell-recovery strategy and extraction kit determine **chloroplast (eukaryotic) contamination**: whole-sample homogenization → high chloroplast contamination; buffer washing of cells → low yield; detergent improves microbial yield. Implicates: pre-extraction cell separation/washing and homogenization method as euk-fraction drivers (host = macroalgae).

- **Jiménez DJ, Jamil T, ... Venkateswaran K. 2025.** "Microbial community characterization in Red Sea-derived samples using a field-deployable DNA extraction system and nanopore sequencing." *Environ Microbiome.* DOI: 10.1186/s40793-025-00819-x. PMID: 41299662; PMCID: PMC12763976.
  - Field-vs-lab extraction and cold storage/transport shift community composition (e.g., cyanobacterial abundance drops after transport-on-ice); coral/mangrove (host-rich) matrices most affected. Implicates: extraction system, storage/transport, matrix. (Reports composition shifts rather than a single euk-fraction number.)

- **Ghathian KSA, Heintz JE, ... Petersen AM. 2025.** "Freezing of Vaginal Swabs Prior to DNA Purification Does Not Statistically Significantly Affect Microbiome Composition." *MicrobiologyOpen.* DOI: 10.1002/mbo3.70053. PMID: 40878290; PMCID: PMC12394732.
  - Host-DNA-depleted (MolYsis Complete5) vaginal swabs profiled by MetaPhlAn4; short-term freezing (-20/-80 °C) had negligible effect on composition, though low-abundance/fragile taxa shifted. Implicates: storage temperature = weak/negligible driver after host depletion.

- **Andriienko V, Buczek M, ... Kolasa MR. 2024.** "Implementing high-throughput insect barcoding in microbiome studies: impact of non-destructive DNA extraction on microbiome reconstruction." *PeerJ.* DOI: 10.7717/peerj.18025. PMID: 39329134; PMCID: PMC11426317.
  - HotSHOT (alkaline) pre-treatment reduced amplifiable microbial template ~15× but had limited effect on composition of abundant taxa. Implicates: lysis/extraction chemistry alters microbial-vs-host template ratio.

## Thread 3 — Host-DNA depletion / decontamination methods and residual eukaryotic fraction

- **Marotz CA, Sanders JG, Zuniga C, Zaramela LS, Knight R, Zengler K. 2018.** "Improving saliva shotgun metagenomics by chemical host DNA depletion." *Microbiome.* DOI: 10.1186/s40168-018-0426-3. PMID: 29482639. **[MUST-CITE — canonical host-depletion benchmark]**
  - Baseline fresh/frozen saliva is **<10% microbial reads**. Compares 3 commercial kits, size filtration, and osmotic lysis + propidium monoazide (lyPMA). lyPMA is cheap/rapid and substantially enriches microbial reads (raises microbial fraction several-fold). Implicates: host-depletion method as a first-order determinant of residual eukaryotic (human) fraction.

- **Wu-Woods NJ, Barlow JT, Trigodet F, ... Ismagilov RF. 2023.** "Microbial-enrichment method enables high-throughput metagenomic characterization from host-rich samples (MEM)." *Nat Methods.* DOI: 10.1038/s41592-023-02025-4. PMID: 37828152; PMCID: PMC10885704.
  - MEM reduces host DNA **>1,000-fold** with ~90% of taxa unchanged; enables MAGs from intestinal biopsies at ≥1% abundance. Quantifies achievable residual host fraction. Implicates: enrichment method.

- **Marchukov D, Li J, Juillerat P, Misselwitz B, Yilmaz B. 2023.** "Benchmarking microbial DNA enrichment protocols from human intestinal biopsies." *Front Genet.* DOI: 10.3389/fgene.2023.1184473. PMID: 37180976; PMCID: PMC10169731.
  - Head-to-head of NEBNext, Molzym Ultra-Deep, QIAamp DNA Microbiome, Zymo HostZERO, and ONT adaptive sampling. Bacterial-read fraction rose from **<1% (AllPrep control) to 24–28%** with NEBNext/QIAamp. Quantifies method-dependent residual host fraction; notes adaptive sampling introduces taxonomic bias (E. coli inflated). Implicates: depletion kit choice; each method's magnitude reported.

- **Cheng WY, Liu WX, ... Yu J. 2023.** "High Sensitivity of Shotgun Metagenomic Sequencing in Colon Tissue Biopsy by Host DNA Depletion." *Genomics Proteomics Bioinformatics.* DOI: 10.1016/j.gpb.2022.09.003. PMID: 36174929; PMCID: PMC11082407.
  - Differential lysis of mammalian vs bacterial cells: bacterial reads up 2.46× (human) / 5.46× (mouse); host reads down 6.8%/10.2%; ~2.4× more species detected. Implicates: differential-lysis host depletion.

- **Wang Y, Yang J, Hou H, ... Liu YX. 2026.** "Advancing Plant Microbiome Research Through Host DNA Depletion Techniques." *Plant Biotechnol J.* DOI: 10.1111/pbi.70379. PMID: 41078118; PMCID: PMC12946469. (Review)
  - Systematic review of plant-host DNA depletion: physical separation (filtration, gradient centrifugation), selective lysis, enzymatic cell-wall treatment, methylation-based enrichment, targeted capture, nanopore adaptive sampling, and proposed CRISPR-Cas9 approaches. Good catalog of the levers that set residual plant (eukaryotic) fraction.

- **Marquet M, Zöllkau J, ... Brandt C. 2022.** "Evaluation of microbiome enrichment and host DNA depletion in human vaginal samples using Oxford Nanopore's adaptive sequencing." *Sci Rep.* DOI: 10.1038/s41598-022-08003-8. PMID: 35256725; PMCID: PMC8901746.
  - Vaginal samples start at **>90% host DNA**; adaptive "human host depletion" gave 1.70× more sequencing depth without composition change. Notes complete host removal not yet achievable. Implicates: sequencing-platform-level (in-silico) depletion; quantifies starting host burden.

- **Jiang Y, Liu J, ... Huang S. 2025.** "High-resolution microbiome analysis of host-rich samples using 2bRAD-M without host depletion." *npj Biofilms Microbiomes.* DOI: 10.1038/s41522-025-00851-2. PMID: 41315331; PMCID: PMC12663593.
  - Reduced-representation approach tolerant of **>90% human DNA**, matching whole-metagenome profiles at 5–10% of the effort. Implicates: library-prep strategy as an alternative to physical euk depletion.

- **mEnrich-seq: Cao L, Kong Y, ... Fang G. 2024.** "mEnrich-seq: methylation-guided enrichment sequencing of bacterial taxa of interest from microbiome." *Nat Methods.* DOI: 10.1038/s41592-023-02125-1. PMID: 38177508; PMCID: PMC11474163.
  - Methylation-sensitive restriction depletes host/background (up to 117× target enrichment). Implicates: methylation/CpG-based enrichment.

- **Sun Y, Cheng Z, ... Xia Y. 2023.** "metaRUpore" *Genome Res.* DOI: 10.1101/gr.277266.122. PMID: 37041035; PMCID: PMC10234302. — Nanopore ReadUntil depletion of high-abundance/host reads to enrich rare taxa (~2× rare-taxon coverage).

- **Ayala-Montaño S, Afolayan AO, ... Reuter S. 2026.** "Mitigation and detection of putative microbial contaminant reads from long-read metagenomic datasets ('Stop-Check-Go')." *Microb Genom.* DOI: 10.1099/mgen.0.001609. PMID: 41569097; PMCID: PMC12828179.
  - Lysis-based host depletion reduced host DNA by **~76% per sample** on average in neonatal swabs; combined lab+bioinformatic decontamination framework for low-biomass long-read data.

- **Moragues-Solanas L, ... Gilmour MW. 2024.** "Rapid detection of bloodstream infection by clinical metagenomics." *BMC Med Genomics.* DOI: 10.1186/s12920-024-01835-5. PMID: 38443925; PMCID: PMC10916079.
  - Optimized **3% saponin** host depletion reduced host chromosomal DNA <10^6-fold and mitochondrial <10^3-fold; residual host **mitochondrial** DNA identified as the stubborn fraction. Implicates: saponin concentration; mitochondrial DNA as depletion-resistant euk signal.

- **CAVEAT — Saponin side effects:** "Saponin treatment for eukaryotic DNA depletion alters the microbial DNA profiles by reducing the abundance of Gram-negative bacteria in metagenomics analyses." 2023. *Microbiome Res Rep.* DOI: 10.20517/mrr.2023.02 (oaepublish). — Host-depletion chemistry itself biases the recovered prokaryotic community (Gram-negative loss), a confounder when using depletion to control euk fraction.

## Thread 4 — Reagent/kit contamination ("kitome") relevant to eukaryotic (and background) signal

- **Salter SJ, Cox MJ, Turek EM, ... Walker AW. 2014.** "Reagent and laboratory contamination can critically impact sequence-based microbiome analyses." *BMC Biology.* DOI: 10.1186/s12915-014-0087-z. PMID: 25387460; PMCID: PMC4228153. (~2,468 citations) **[MUST-CITE — founding kitome paper]**
  - Contaminating DNA is ubiquitous in extraction kits/reagents, varies by kit and batch, and its impact scales inversely with sample microbial biomass — affecting both 16S and shotgun. Establishes **biomass as the master variable**: the lower the true microbial load (often the case in high-euk / host-rich or oligotrophic samples), the larger the fractional contaminant (and relative euk) distortion.

- **Pollock J, Salter SJ, Nixon R, Hutchings MR. 2021.** "Milk microbiome... challenges of low microbial biomass and exogenous contamination." *Anim Microbiome.* DOI: 10.1186/s42523-021-00144-x. PMID: 34794515; PMCID: PMC8600933. — Low-biomass, host-rich (milk) matrix where contamination compromised design; concrete example of biomass × matrix interaction.

- **Ibañez-Lligoña M, ... Quer J. 2026.** "Unveiling pathogens and contaminants: refining metagenomics for clinical diagnostics." *Front Microbiol.* DOI: 10.3389/fmicb.2026.1786985. PMID: 42005844; PMCID: PMC13083213. — Shows **viral/microbial load is the primary determinant of sensitivity**; contamination-aware workflows (negative controls, watchlists, computational filtering) needed for low-biomass samples.

- **Cao Y, ... Wang D. 2025.** "Establishing hospital-specific background microbial libraries to reduce false positives in mNGS diagnosis of PJI." *Front Cell Infect Microbiol.* DOI: 10.3389/fcimb.2025.1668697. PMID: 41668735; PMCID: PMC12883815. — Only 1.13% of reads microbial in near-sterile instrument controls; background composition (incl. 11% fungal) varies by institution. Quantifies contaminant fungal fraction in a low-biomass control.

- **Aggarwal D, ... Harrison EM. 2023.** "Optimization of high-throughput 16S rRNA gene amplicon sequencing." *Microb Genom.* DOI: 10.1099/mgen.0.001115. PMID: 37843887; PMCID: PMC10634443. — Reagent/primer-linked contamination dominates rare-species signal (<0.1%); mitigation via thresholding.

- **Salzberg SL, Chia M, ... Nagarajan N. 2026.** "Setting higher standards for reports of microbial species in human cancers." *Nat Cancer.* DOI: 10.1038/s43018-026-01121-6. PMID: 41714823; PMCID: PMC13180263. — QC/validation standards; notes **reference-genome contamination causes misclassification of human (eukaryotic) reads** as microbial — a bioinformatic (not wet-lab) driver of apparent cross-domain signal.

## Thread 5 — Metadata standards & large-collection QC (NMDC, MIxS/GSC, EMP, JGI, GOLD/IMG, Tara)

- **Hu B, Canon S, Eloe-Fadrosh EA, ... Chain PSG. 2021.** "Challenges in Bioinformatics Workflows for Processing Microbiome Omics Data at Scale." *Front Bioinform.* DOI: 10.3389/fbinf.2021.826370. PMID: 36303775; PMCID: PMC9580927. — Describes the **NMDC** standardized, FAIR processing approach across many samples; the infrastructure that would enable systematic euk-fraction QC across a collection.

- **The National Microbiome Data Collaborative Data Portal (2021).** *Nucleic Acids Res* (portal paper). PMCID: PMC8958897. — NMDC integrated multi-omics resource; substrate for metadata-linked cross-collection QC.

- **Simpson A, Wood-Charlson EM, ... Wilhelm RC. 2024.** "MISIP: a data standard for reuse/reproducibility of SIP-derived sequence." *GigaScience.* DOI: 10.1093/gigascience/giae071. PMID: 39399973; PMCID: PMC11471955. — Extends **MIxS/MIMS**; example of the GSC metadata-checklist machinery relevant to attaching processing metadata (which correlates could be tested against).

- **Zass L, ... Oduaran OH. 2024.** "Microbiome Research Data Toolkit" (MIxS-MIMS + PhenX). *Database (Oxford).* DOI: 10.1093/database/baae062. PMID: 39167718; PMCID: PMC11338178. — Standardizes metadata capture/harmonization; enabling infrastructure.

- **Holm JB, ... Schriml LM. 2025.** "First island-wide, single-day soil collection study on Crete reveals environmental drivers of microbial diversity" (GSC Island Sampling Day). *Environ Microbiome.* DOI: 10.1186/s40793-025-00752-z. PMID: 40708004; PMCID: PMC12291233. — GSC-standardized metadata-rich soil collection; links environmental metadata (elevation, pH, moisture, vegetation, land use) to community variation — a template for metadata→community correlate testing.

- **Anthony WE, ... Blanchard JL. 2024.** "From soil to sequence: filling the critical gap in genome-resolved metagenomics..." *Environ Microbiome.* DOI: 10.1186/s40793-024-00599-w. PMID: 39095861; PMCID: PMC11295382. — Argues soil metagenomes are systematically under-resolved (high complexity + eukaryotic/plant DNA), motivating collection-scale QC.

- **Ortiz-Chura A, Popova M, Morgavi DP. 2024.** "Ruminant microbiome data are skewed and unFAIR..." *Anim Microbiome.* DOI: 10.1186/s42523-024-00348-x. PMID: 39456104; PMCID: PMC11515148. — 47,628 sample metadata mined from INSDC/NCBI; **>40% lacked basic metadata** — quantifies the metadata-completeness ceiling that constrains any cross-collection correlate analysis.

- **Finn RD, ... Batut B. 2024.** "Establishing the ELIXIR Microbiome Community." *F1000Res.* DOI: 10.12688/f1000research.144515.2. PMID: 40970218; PMCID: PMC12441670. — Standards/infrastructure white paper (marine → all biomes).

- *(Foundational, from domain knowledge — not surfaced by these searches but standard cites: Thompson LR et al. 2017 "A communal catalogue reveals Earth's multiscale microbial diversity," Nature (EMP), DOI 10.1038/nature24621; Sunagawa S et al. 2015 Tara Oceans "Structure and function of the global ocean microbiome," Science, DOI 10.1126/science.1261359 — Tara used size-fractionation/filtration to physically partition prokaryotes from protists, the clearest example of a collection-protocol lever on euk fraction; Mukherjee S et al. GOLD and Chen IMA et al. IMG/M for JGI metadata.)*

## Thread 6 — Prior systematic reviews / meta-analyses correlating metadata with contamination across public collections

- **Eisenhofer et al. 2026 (SPF, Thread 1)** is the closest thing to a cross-collection quantitative analysis: 136,284 metagenomes, prokaryotic fraction related to **biome**. However, its published correlate is essentially biome/environment; it does **not** systematically regress euk fraction against processing/wet-lab metadata (extraction kit, depletion method, size fraction, platform, read depth, library prep).
- **Salter et al. 2014 (Thread 4)** is the canonical cross-kit contamination study but targets prokaryotic contaminants and biomass, not eukaryotic fraction per se, and is not a public-collection-scale metadata regression.
- No retrieved paper performs a **large-scale, metadata-linked regression of eukaryotic read fraction against the full set of upstream collection/processing/sequencing metadata fields across a public multi-biome collection.** Method benchmarks (Threads 2–3) are small-N and single-matrix; standards papers (Thread 5) provide the metadata scaffold but do not run the correlate test.

---

## Identified Gap

A **large-scale, metadata-linked, cross-collection test that regresses measured eukaryotic read fraction against upstream sample-collection, processing, and sequencing metadata (matrix/biome, DNA-extraction kit/protocol, host-depletion method, size fractionation/filtration, lysis method, sequencing platform, read depth, library prep) has NOT been published.**

The nearest prior art is Eisenhofer, Alberdi & Woodcroft 2026 (SPF, mSystems, PMID 41854267), which quantifies the prokaryotic fraction across 136,284 public metagenomes but relates it primarily to **biome/environment**, not to the wet-lab and sequencing metadata variables that this project targets. Method-comparison studies (Marotz 2018; Marchukov 2023; Wu-Woods 2023; Sobolev 2025) quantify how individual processing choices change residual eukaryotic/host fraction, but each is small-N, single-matrix, and not linked to a public collection's metadata. Standards/QC infrastructure (NMDC, MIxS/GSC, GOLD/IMG) supplies the metadata scaffold but has not been used to run the correlate analysis.

**Verdict: The cross-collection, metadata-field-resolved correlate analysis of eukaryotic fraction is a genuine, currently-unfilled gap.** The main caveats to filling it are (1) SPF (or an equivalent reference-free euk-fraction estimator) now makes the response variable cheaply computable at scale, so the novelty is in the *metadata-correlate* analysis, not the measurement; and (2) metadata completeness is the binding constraint — Ortiz-Chura 2024 shows >40% of public samples lack basic fields, so any such study must either restrict to well-annotated collections (e.g., NMDC, EMP, Tara, GOLD) or model missingness explicitly.
