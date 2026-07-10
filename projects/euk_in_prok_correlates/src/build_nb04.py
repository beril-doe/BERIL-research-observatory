import sys
sys.path.insert(0, "/tmp/claude-1000/-home-mamillerpa-BERIL-research-observatory/1ebbf684-04cb-41be-9a57-92bca8b08e87/scratchpad")
from mknb import build
NB = "/home/mamillerpa/BERIL-research-observatory/projects/euk_in_prok_correlates/notebooks/04_within_study.ipynb"

cells = [
("md", """# NB04 — Batch-Controlled Within-Study Analysis

NB03 shows the cross-study environment effect does **not** generalise (out-of-study R²<0): environment is
confounded with study/batch across NMDC. The cleanest available control is to look **inside a single large study**,
where sampling protocol, wet-lab handling, and sequencing batch are (largely) constant, and ask whether euk fraction
still varies with the metadata that genuinely varies *within* that study (`env_local_scale`, `ecosystem_subtype`,
geography). If it does, the environment/eukaryote link is not purely batch. We use the dominant soil study."""),
("code", """import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold
DATA=Path('../data'); FIG=Path('../figures')
plt.rcParams.update({'figure.dpi':110,'savefig.bbox':'tight','axes.grid':True,'grid.alpha':.3})
df=pd.read_csv(DATA/'analysis_clean.csv')
S=df['study_id'].value_counts().idxmax()
d=df[df['study_id']==S].copy()
print(f'dominant study {S}: {len(d)} runs')
print('matrix within study:', d['matrix'].unique())
print('euk detection within study:', round((d['gott_euk_frac']>0).mean(),3),
      '| median euk:', round(d['gott_euk_frac'].median(),4))"""),
("md", "## Within-study metadata variation"),
("code", """for col in ['env_local','ecosystem_subtype','geo_loc','samp_collec_device']:
    print(f'{col:20s} {d[col].nunique()} distinct')
print('\\nenv_local_scale distribution:')
print(d['env_local'].value_counts().head(12).to_string())"""),
("md", "## H1a within-study — euk fraction by within-study environment (batch held ~constant)"),
("code", """def kruskal_by(col, minn=15):
    g=d.groupby(col).filter(lambda x:len(x)>=minn)
    levels=[v for v,c in g[col].value_counts().items()]
    if len(levels)<2: return None
    H,p=stats.kruskal(*[g.loc[g[col]==l,'gott_euk_frac'] for l in levels])
    return len(levels),len(g),H,p
for col in ['env_local','ecosystem_subtype']:
    r=kruskal_by(col)
    if r: print(f'{col:20s} Kruskal over {r[0]} levels (n={r[1]}): H={r[2]:.1f}, p={r[3]:.2e}')
    else: print(f'{col:20s} insufficient levels')
# summary table for env_local
tab=d.groupby('env_local')['gott_euk_frac'].agg(n='size',median='median',
     detect=lambda s:(s>0).mean(),gt20=lambda s:(s>0.2).mean()).round(4)
tab=tab[tab['n']>=15].sort_values('median',ascending=False); display(tab)
tab.to_csv(DATA/'nb04_within_study_env_local.csv')"""),
("md", "## Geographic structure within study (spatial ≈ environment, batch-controlled)"),
("code", """geo=d.groupby('geo_loc')['gott_euk_frac'].agg(n='size',median='median').query('n>=15').sort_values('median',ascending=False)
print(f'{len(geo)} geo locations with >=15 runs; euk median range {geo["median"].min():.3f}-{geo["median"].max():.3f}')
display(geo.head(12))
if len(geo)>=2:
    H,p=stats.kruskal(*[d.loc[d.geo_loc==g,'gott_euk_frac'] for g in geo.index])
    print(f'Kruskal euk across {len(geo)} geo locations: H={H:.1f}, p={p:.2e}')"""),
("md", "## Within-study predictability (random KFold, batch fixed)"),
("code", """feat=['env_local','ecosystem_subtype','geo_loc']
X=pd.get_dummies(d[feat].fillna('Unknown'))
y=np.log((d['gott_euk_frac'].values+1e-4)/(1-d['gott_euk_frac'].values+1e-4))
m=HistGradientBoostingRegressor(max_depth=4,learning_rate=.08,max_iter=300,random_state=0)
r2=cross_val_score(m,X,y,cv=KFold(5,shuffle=True,random_state=0),scoring='r2')
print(f'Within-study 5-fold R^2 (euk_logit ~ local env + geography): {r2.mean():.3f} ± {r2.std():.3f}')
print('Contrast with cross-study out-of-study R^2 = -0.30 (NB03).')"""),
("md", "## Figure 4 — Euk fraction by within-study environment"),
("code", """fig,ax=plt.subplots(figsize=(9,5))
order=tab.sort_values('median').index.tolist()
ax.boxplot([d.loc[d.env_local==g,'gott_euk_frac'] for g in order],vert=False,tick_labels=order,showfliers=False)
for i,g in enumerate(order):
    v=d.loc[d.env_local==g,'gott_euk_frac']; ax.scatter(v,np.random.normal(i+1,.07,size=len(v)),s=6,alpha=.25,color='#2c7fb8')
ax.set_xlabel('GOTTCHA euk fraction'); ax.set_title(f'Within dominant soil study ({len(d)} runs)\\neuk by env_local_scale')
plt.tight_layout(); plt.savefig(FIG/'fig04_within_study_env.png'); plt.show(); print('saved fig04')"""),
("md", """## NB04 takeaways (interpretation in REPORT)
- Tests whether euk fraction varies with local environment/geography **inside one study**, where batch is ~constant.
- If within-study Kruskal is significant and within-study R² > 0 (while cross-study R² < 0), the environment↔eukaryote
  association is **partly real, not purely batch** — but only demonstrable at fine scale within a soil study.
- If within-study effects vanish, euk fraction is idiosyncratic at the sample level given fixed protocol — strengthening
  the case that upstream (unmeasured) wet-lab/biomass factors dominate."""),
]
build(NB, cells)
