> **HISTORICAL** — This scaffolding document was generated at project creation (Feb 2026). For current status see [README.md](README.md) and [RESEARCH_PLAN.md](RESEARCH_PLAN.md).

# Project Setup Complete

## What Has Been Created

Your new research project **"Pangenome Openness, Metabolic Pathways & Phylogenetic Distances"** has been successfully initialized with a complete analysis framework.

### Project Location
```
projects/pangenome_pathway_ecology/
```

### Files Created

#### 📖 Documentation (5 files)
1. **START_HERE.md** - Welcome guide and navigation
2. **README.md** - Detailed research questions and hypotheses
3. **ANALYSIS_PLAN.md** - Five-phase analysis framework with all details
4. **QUICK_START.md** - Quick reference for common tasks and queries
5. **.gitignore** - Project-specific ignore rules for large data files

#### 📓 Jupyter Notebooks (2 files)
1. **01_data_exploration.ipynb** - PHASE 1: Profile all data sources ✓
   - Pangenome statistics across 27,690 species
   - Calculate openness metrics
   - Assess GapMind pathway availability
   - Check AlphaEarth embedding coverage

2. **02_pathway_analysis.ipynb** - PHASE 2: Pathway correlations (ready to run)
   - Aggregate pathway scores to species level
   - Calculate pathway diversity metrics
   - Correlate with pangenome openness
   - Analyze metabolic categories

#### 📁 Directories
- `data/` - Output files (initially empty, will populate during analysis)
- `figures/` - Visualizations (initially empty)
- `notebooks/` - Analysis notebooks

## Project Scope

### Research Question
**How do pangenome characteristics (open vs. closed) relate to metabolic pathway completeness and phylogenetic/structural distances?**

### Key Hypotheses
1. **Pathway Hypothesis**: Open pangenomes → variable/diverse pathways
2. **Structural Hypothesis**: Open pangenomes → greater structural diversity
3. **Phylogenetic Signal**: Are associations driven by evolution or ecology?
4. **Ecological Context**: Does environment shape pangenome openness?

### Data Sources (BERDL)
- **Pangenome metrics**: 27,690 species from `pangenome` table
- **Metabolic pathways**: GapMind predictions in `gapmind_pathways`
- **Structural distances**: AlphaEarth embeddings (28% coverage)
- **Phylogenetic distances**: From `phylogenetic_tree_distance_pairs`
- **Environmental metadata**: `ncbi_env` table for ecological context

## Five-Phase Analysis Plan

```
Phase 1: Data Exploration ✓ COMPLETE
├─ Profile pangenome statistics
├─ Calculate openness index for all species
├─ Assess data availability across sources
└─ Identify target species for analysis

Phase 2: Pathway Correlations → NEXT
├─ Aggregate pathway scores to species level
├─ Calculate diversity and completeness metrics
├─ Test correlations with pangenome openness
└─ Visualize pathway-openness relationships

Phase 3: Structural Distance Analysis 📋 PLANNED
├─ Extract AlphaEarth embeddings for target species
├─ Compute within-species pairwise distances
├─ Test structural diversity hypothesis
└─ Correlate with openness metrics

Phase 4: Phylogenetic Signal Control 📋 PLANNED
├─ Extract phylogenetic distances
├─ Use PGLS/PIC for phylogenetic correction
├─ Assess evolutionary vs. ecological signal
└─ Generate phylogenetic tree visualizations

Phase 5: Ecological Context Integration 📋 PLANNED
├─ Link species to environmental metadata
├─ Test environmental filtering hypothesis
├─ Analyze niche specialization patterns
└─ Generate integrated findings
```

## Key Metrics

### Pangenome Openness Score
```
openness = (auxiliary_genes + singleton_genes) / total_genes
```
- **0** = Completely closed pangenome
- **1** = Completely open pangenome
- **Typical range**: 0.2 - 0.8 across species

### Expected Outputs
- **Correlation matrices** (openness ↔ pathway completeness/diversity)
- **Scatter plots** showing relationships with p-values
- **Heatmaps** of pathway categories vs. openness groups
- **Distance distribution plots** for structural diversity
- **Phylogenetic tree** colored by openness
- **CSV datasets** for reproducibility

## How to Run

### Option A: Local Planning (Recommended first)
```bash
cd projects/pangenome_pathway_ecology

# Read the documentation
cat START_HERE.md
cat ANALYSIS_PLAN.md
cat QUICK_START.md

# Review notebook templates (they have detailed comments)
# The notebooks are ready to run on BERDL JupyterHub
```

### Option B: Run on BERDL JupyterHub
1. Navigate to https://hub.berdl.kbase.us
2. Login with KBase credentials
3. Create `~/workspace/projects/pangenome_pathway_ecology/` directory
4. Upload `notebooks/` folder
5. Open `notebooks/01_data_exploration.ipynb`
6. Kernel → Restart & Run All
7. Download outputs and commit results

### Option C: Git-based Workflow
```bash
# Clone repo in JupyterHub
git clone <repo-url>
cd BERIL-research-observatory

# Edit and run notebooks in JupyterHub
# Then commit results
git add projects/pangenome_pathway_ecology/data/
git add projects/pangenome_pathway_ecology/figures/
git commit -m "Phase 2 pathway analysis results"
git push
```

## BERDL Connection

All data queries use **BERDL** database: `kbase_ke_pangenome`

**Key tables for this project**:
- `pangenome` (27,690 rows) - Species-level statistics
- `gapmind_pathways` (~3.2M rows) - Metabolic pathway predictions
- `alphaearth_embeddings_all_years` (~82K genomes) - Structural embeddings
- `phylogenetic_tree_distance_pairs` - Evolutionary distances
- `genome` (293,059 rows) - Genome metadata
- `gtdb_species_clade` (27,690 rows) - Species taxonomy

## Data Availability Summary

| Data Type | Coverage | Status |
|-----------|----------|--------|
| Pangenome metrics | 100% (27,690 species) | ✓ Complete |
| GapMind pathways | ~95% (279K/293K genomes) | ✓ Excellent |
| AlphaEarth embeddings | ~28% (82K/293K genomes) | ⚠️ Partial |
| Phylogenetic distances | Species pairs available | ✓ Available |
| Environmental metadata | ~60% (variable by species) | ⚠️ Partial |

## Important Notes

### BERDL Tips
- **Species IDs**: Use exact match `` = 's__Species_name--RS_GCF_123' ``
- **Large tables**: Always filter `genome` (293K rows) before expensive operations
- **AlphaEarth**: Slow table - use WHERE clauses
- **Gene clusters**: Species-specific, cannot compare across species

### Documentation Updates
When you make discoveries, update the central documentation:
- SQL pitfalls → `../../docs/pitfalls.md`
- Performance strategies → `../../docs/performance.md`
- Interesting findings → `../../docs/discoveries.md`
- Future ideas → `../../docs/research_ideas.md`

**Tag with**: `[pangenome_pathway_ecology]`

### Related Projects
- `../pangenome_openness/` - Existing open/closed analysis
- `../ecotype_analysis/` - Environment vs. phylogeny
- `../cog_analysis/` - Functional category distributions

## Notebook Templates

Both notebooks are ready to run with:
- Detailed comments explaining each section
- Common BERDL query patterns
- Visualization code
- Data export to CSV
- Error handling guidance

**To use**:
1. Upload to BERDL JupyterHub
2. Modify SQL WHERE clauses for specific filters
3. Run cells sequentially (Shift+Enter) or all (Kernel → Run All)
4. Download outputs and commit to git

## Success Criteria

- [x] Phase 1: Profile data for all species
- [ ] Phase 2: Calculate pathway correlations
- [ ] Phase 3: Analyze structural distances
- [ ] Phase 4: Control for phylogenetic signal
- [ ] Phase 5: Integrate ecological context
- [ ] Final: Document discoveries in shared docs

## Next Steps

1. **Now**: Review START_HERE.md and ANALYSIS_PLAN.md
2. **Today**: Upload notebooks to BERDL JupyterHub
3. **Week 1**: Run Phase 1 data exploration
4. **Week 2**: Run Phase 2 pathway analysis
5. **Weeks 3-5**: Complete remaining phases
6. **Throughout**: Update shared documentation

## Status

- ✓ Project structure created
- ✓ Documentation complete
- ✓ Notebooks templated and ready
- ✓ BERDL data verified
- ✓ Git repository updated

**Ready to begin analysis!**

---

**Created**: 2026-02-05
**Last Updated**: 2026-02-05
**Committed**: `b1f2c01`

For questions or clarifications, refer to:
- ANALYSIS_PLAN.md (detailed methodology)
- QUICK_START.md (quick reference)
- ../../docs/ (shared knowledge base)
