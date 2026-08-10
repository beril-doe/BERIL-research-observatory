> **HISTORICAL** — This scaffolding document was generated at project creation (Feb 2026). For current status see [README.md](README.md) and [RESEARCH_PLAN.md](RESEARCH_PLAN.md).

# Pangenome Openness, Metabolic Pathways & Phylogenetic Distances

## Welcome! 👋

This project investigates how **pangenome characteristics** (open vs. closed) correlate with **metabolic pathway completeness** and **phylogenetic/structural distances** in microbial species.

## Quick Navigation

📘 **[README.md](README.md)** - Detailed research questions and hypotheses
📋 **[ANALYSIS_PLAN.md](ANALYSIS_PLAN.md)** - Five-phase analysis framework
⚡ **[QUICK_START.md](QUICK_START.md)** - Quick reference for common tasks

## What This Project Does

**Question**: Do open pangenomes indicate generalist species with diverse metabolic strategies?

**Hypothesis**:
- **Open pangenomes** = generalists with flexible metabolic capacity
- **Closed pangenomes** = specialists with conserved core pathways

**Data approach**:
- Pangenome metrics from 27,690 species
- Metabolic pathway predictions (GapMind) for 293K genomes
- Structural distances (AlphaEarth embeddings) for ~28% of genomes
- Phylogenetic distances for evolutionary context

## Project Structure

```
pangenome_pathway_ecology/
├── README.md              # Research questions & methodology
├── ANALYSIS_PLAN.md       # Five-phase analysis framework
├── QUICK_START.md         # Quick reference guide
├── START_HERE.md          # This file
│
├── notebooks/
│   ├── 01_data_exploration.ipynb     # Phase 1: Profile data ✓
│   ├── 02_pathway_analysis.ipynb      # Phase 2: Correlations (next)
│   ├── 03_structural_distances.ipynb  # Phase 3: AlphaEarth (planned)
│   ├── 04_phylogenetic_analysis.ipynb # Phase 4: Phylo control (planned)
│   └── 05_ecological_analysis.ipynb   # Phase 5: Environment (planned)
│
├── data/                  # Outputs from analysis
│   ├── species_pangenome_openness.csv
│   ├── species_pathway_openness_merged.csv
│   └── ... (more files as analysis progresses)
│
└── figures/               # Visualizations
    ├── 01_pangenome_openness_overview.png
    ├── 02_pathway_openness_correlations.png
    └── ...
```

## Getting Started

### Option 1: Local Development (Recommended for Planning)
```bash
# Clone or navigate to the repo
cd projects/pangenome_pathway_ecology

# Read the analysis plan
cat ANALYSIS_PLAN.md

# Start with notebook templates
# Edit locally before uploading to BERDL
```

### Option 2: Run on BERDL JupyterHub (For Actual Analysis)
1. Go to https://hub.berdl.kbase.us
2. Log in with your KBase credentials
3. Upload `notebooks/` folder
4. Open `01_data_exploration.ipynb`
5. Kernel → Restart & Run All

## Analysis Phases

| Phase | Notebook | Status | Goal |
|-------|----------|--------|------|
| 1 | `01_data_exploration.ipynb` | ✓ DONE | Profile all data sources |
| 2 | `02_pathway_analysis.ipynb` | 🔄 NEXT | Correlate pathways with openness |
| 3 | `03_structural_distances.ipynb` | 📋 PLANNED | Analyze AlphaEarth embeddings |
| 4 | `04_phylogenetic_analysis.ipynb` | 📋 PLANNED | Control for phylogenetic signal |
| 5 | `05_ecological_analysis.ipynb` | 📋 PLANNED | Link to environmental context |

## Key Data Sources

All data comes from **BERDL**: `kbase_ke_pangenome` database

| Table | Size | Purpose |
|-------|------|---------|
| `pangenome` | 27,690 rows | Pangenome openness metrics |
| `gapmind_pathways` | ~3.2M rows | Metabolic pathway predictions |
| `alphaearth_embeddings_all_years` | ~82K genomes | Structural similarity |
| `phylogenetic_tree_distance_pairs` | Pairwise distances | Evolutionary relationships |
| `genome` | 293,059 rows | Genome metadata |

## Key Metrics You'll Calculate

### Pangenome Openness Score
```
openness = (auxiliary_genes + singleton_genes) / total_genes
```
- 0 = completely closed (all genes core)
- 1 = completely open (no core genes)
- Range: typically 0.2-0.8

### Pathway Metrics
- Mean pathway completion score (0-1)
- Pathway diversity (unique pathways / total)
- Coverage across metabolic categories

### Structural Distance
- Within-species embedding distances (from AlphaEarth)
- Distance variance (structural diversity)

## Expected Outcomes

You'll produce:
- 📊 **Correlation matrices** showing relationships
- 📈 **Scatter plots** with trend lines and p-values
- 🔗 **Network visualizations** of pathway-openness relationships
- 📊 **Phylogenetic tree** colored by pangenome openness
- 🗂️ **CSV datasets** for further analysis

## BERDL Tips

### Query Template (GapMind pathways by species)
```sql
SELECT
  s.GTDB_species,
  AVG(gp.score) as mean_pathway_score,
  COUNT(DISTINCT gp.pathway) as unique_pathways
FROM kbase_ke_pangenome.genome g
JOIN kbase_ke_pangenome.gapmind_pathways gp ON g.genome_id = gp.genome_id
JOIN kbase_ke_pangenome.gtdb_species_clade s ON g.gtdb_species_clade_id = s.gtdb_species_clade_id
GROUP BY s.GTDB_species
ORDER BY mean_pathway_score DESC
```

### Performance Tips
- Filter `genome` table (293K rows) early
- Use `LIMIT` on exploratory queries
- AlphaEarth embeddings table is slow - use WHERE clauses
- For large JOINs, use direct Spark instead of REST API

### Common Gotchas
- Species IDs contain `--` character (e.g., `s__Species--RS_GCF_123`)
- Gene clusters are species-specific (can't compare across species)
- AlphaEarth only covers ~28% of genomes
- Some species have sparse pathway data

## Contributing & Documentation

When you make discoveries, update the central docs:
- **SQL pitfalls** → `../../docs/pitfalls.md`
- **Performance tips** → `../../docs/performance.md`
- **Key findings** → `../../docs/discoveries.md`
- **Interesting ideas** → `../../docs/research_ideas.md`

Tag discoveries with: `[pangenome_pathway_ecology]`

## Related Projects

- `../pangenome_openness/` - Existing open/closed pangenome work
- `../ecotype_analysis/` - Environment and phylogeny effects
- `../cog_analysis/` - Functional category analysis

## Questions?

1. Check **[ANALYSIS_PLAN.md](ANALYSIS_PLAN.md)** for detailed methodology
2. Check **[QUICK_START.md](QUICK_START.md)** for common queries
3. Read `../../docs/pitfalls.md` for BERDL gotchas
4. Review notebook comments for code walkthroughs

## Next Steps

1. ✓ Explore data (Phase 1 - DONE)
2. → Analyze pathway correlations (Phase 2 - NEXT)
3. Explore structural distances (Phase 3)
4. Control for phylogeny (Phase 4)
5. Link to ecology (Phase 5)

---

**Project Status**: Actively developing
**Last Updated**: 2026-02-05
**Lead Researcher**: You! 🚀
