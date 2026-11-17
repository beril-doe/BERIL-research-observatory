---
name: ecosim
description: Run the EcoSIM ecosystem model, a simulated patch of land with soil, plants, microbes and weather, to test predictions about plant growth, soil carbon, greenhouse gas fluxes, water and nutrients under changed climate or management. Use when the user asks for EcoSIM by name, or when a research question is a what-if about an ecosystem (warmer, drier, more CO2, different site) that a process model can answer and lakehouse data alone cannot. EcoSIM is an optional install; this skill checks for it first and says so plainly when it is absent.
allowed-tools: Bash, Read, Write, Edit
user-invocable: true
---

# EcoSIM: ecosystem simulation

EcoSIM is a process-based biogeochemical model from Berkeley Lab
([ecosim.lbl.gov](https://ecosim.lbl.gov), source at
[EcoSIM-model/EcoSIM](https://github.com/EcoSIM-model/EcoSIM)). Give it a site's
soil profile, plant types, hourly weather and management, and it steps forward
hour by hour: plants grow and die, microbes decompose litter and soil organic
matter, and water, heat, carbon, nitrogen and phosphorus move through canopy,
litter and soil layers. It writes NetCDF history files of pools and fluxes.

## When to use it

- The user asks to run EcoSIM, or names a model experiment ("simulate",
  "what would happen if").
- The question is a counterfactual about an ecosystem that observations cannot
  answer by themselves: the same site warmer, drier, wetter, or under higher
  CO2; the direction and rough size of a response in plant productivity,
  respiration, soil carbon, methane or N2O, evapotranspiration or drainage.
- A hypothesis from lakehouse data makes a prediction a process model can check,
  for example that a microbial or plant response should follow from a change in
  soil moisture.

Do not reach for it when the question is answered by querying data
(`/berdl`), or when the user needs a quantitative forecast
for a real site that has no EcoSIM inputs yet. See [Limits](#limits).

## Step 0: is EcoSIM here?

EcoSIM is not part of BERIL and is often not installed. Check before anything
else, every session:

```bash
python scripts/ecosim.py check
```

Run the scripts from the repository root. Every command of this script prints one JSON object and uses these exit codes:
`0` done, `1` EcoSIM is present but the request failed, `3` EcoSIM (or a part
it needs) is not installed.

**If `check` exits 3, stop and tell the user**, in one or two sentences, that
EcoSIM is not installed in this environment, and offer to install it. Then:

- If they agree, run the installer (next section).
- If they decline, the install fails, or you cannot ask, carry on with the
  rest of the research without EcoSIM. Say in your answer that the simulation
  was not run and why.

Never describe what EcoSIM "would show", and never present expected or
literature values as simulation output. A simulation that did not run produced
no result.

### Installing

```bash
bash scripts/install_ecosim.sh --check   # what is missing; changes nothing
bash scripts/install_ecosim.sh           # clone and build
```

The installer clones EcoSIM into `~/.ecosim/EcoSIM` and builds it there. The
model vendors its own zlib, HDF5 and netCDF, so it needs only git, C, C++ and
Fortran compilers, cmake, make, the autotools and libxml2 headers. Where those
are missing and conda or mamba is available (the BERDL JupyterHub is such a
place), it creates a private conda environment at `~/.ecosim/toolchain`
holding those build tools only, and leaves the base environment alone. It needs network access to GitHub and
conda-forge, never uses elevated privileges, and takes roughly ten minutes.
Run it in the background if your session limits how long one command may take,
and re-run `check` when it finishes. It exits 3 with the list of missing
packages when it cannot provide the tools.

`ECOSIM_HOME` points the scripts at an existing checkout, `ECOSIM_EXE` at an
existing `ecosim.f90.x`, and `ECOSIM_REF` picks the branch, tag or commit to
build. This skill was written against EcoSIM commit `16f9adb` (November 2026);
record the commit `check` reports with any result.

## Step 1: choose a case

A run needs a namelist plus NetCDF inputs: a grid file (site and soil profile),
hourly climate, plant functional type parameters, and optionally plant and soil
management. The checkout ships worked examples:

```bash
python scripts/ecosim.py cases
```

| Case | What it is |
|---|---|
| `dryland` | Rain-fed maize/soybean cropland, 2001 to 2006 weather, plants and microbes on. The best general starting point. |
| `bare_soil` | Soil physics only: no plants, no microbes. Quick check that the model runs. |
| `biocrust`, `biocrust_hillslope` | Moss and lichen crusts on dry soil. |
| `Fen`, `Pond`, `lake`, `DaLake`, `RiceUSTWT` | Fen, pond, lake and rice-paddy settings; relevant to methane. |
| `FireCA`, `blodgett` | A case with a prescribed fire event, and a soil-warming experiment. |

Read the case's namelist under `$ECOSIM_HOME/examples/run_dir/<case>/` before
running: it names every input file, the start date, the forcing years, and
which sub-models (`plant_model`, `microbial_model`, `soichem_model`) are on.
Two shipped namelists do not run by themselves: `dryland/dryland2` continues a
run whose restart file is not in the repository, and `blodgett/Blodget.warming`
needs output from its control case first.

## Step 2: run it

Run from the repository root and keep the output with the project:

```bash
python scripts/ecosim.py run --case dryland --namelist dryland --years 1 \
  --out projects/<id>/data/ecosim/dryland-base
```

The script copies the namelist into a scratch mirror under `--out` and runs
there, so the EcoSIM checkout is never modified. Give each run its own output
directory; the script refuses a used one. Without `--out` it uses a temporary
directory, which is fine for a quick check and wrong for anything you will
report.

Inside a project, launch the run from a notebook cell or a script under
`projects/<id>/`, the same as any other analysis (`/execute-plan` has the
rules), so the command and its JSON result stay inspectable. The history and
restart files are NetCDF and grow with run length (several MB per simulated
year): treat them as large data under the project's `data/` rules and commit
the namelist, `ecosim.log`, the JSON result and a table of the numbers you
report, not the raw model output.

- Length: `--days N`, `--months N` or `--years N`. With none, the namelist's own
  length applies, which for some cases is decades.
- Cost: the `dryland` case takes about ten seconds per simulated month on one
  core, so a year is about two minutes. Start with `--days 30` to prove the
  setup, then run the length the question needs. The default `--timeout` is one
  hour of wall time.
- Any single-line namelist key can be overridden with `--set KEY=VALUE`
  (repeatable). To change a multi-line value such as the `hist_fincl1` output
  list, edit a copy of the namelist and pass `--namelist-file`.

The JSON result has `status`, the model's exit code, the step count reached,
the log path and the history files. `status: failed` comes with `problems` and
the tail of the log; read the log before retrying. A crash in the first steps
is usually an input path or an inconsistent namelist, not something a rerun
fixes. Lines such as `CHECK_VAR: variable ... is not on initial dataset` are
normal.

## Step 3: read the output

```bash
python scripts/ecosim.py summarize <run output dir>            # variable names, problems
python scripts/ecosim.py summarize <run output dir> \
  --vars ECO_GPP_col,ECO_RH_col,AIR_TEMP_col,tPRECIP_col                    # statistics
```

`summarize` and `perturb-forcing` need the `netCDF4` and `numpy` Python
packages. When the Python running the script lacks them, it re-runs itself
through `uv run --with netCDF4 --with numpy`, which changes no environment;
without uv it exits 3 and says so. For anything beyond summary statistics,
open the `*.ecosim.h0.*.nc` file yourself with `netCDF4` or `xarray`.

Reading the numbers correctly:

- History is daily by default (`hist_nhtfrq=-24`). Suffixes give the shape:
  `_col` per column, `_pft` per plant type, `_vr` per soil layer.
- Check `long_name` and `units` for every variable you report. Many carbon
  fluxes are **cumulative** (`ECO_GPP_col`, `ECO_RH_col`, `ECO_NPP_col`), so
  compare end values or differences, not means. Signs follow the atmosphere:
  `ECO_RH_col` is negative for carbon leaving the soil.
- Values near `1e36` are fill for inactive plant slots and soil layers.
  `summarize` excludes them; disable automatic masking and do the same in your
  own code, or every file will look full of missing data.
- A variable listed under `all_fill` was never active in this case (plant
  variables in `bare_soil`). One listed under `non_finite` holds NaN or
  infinity the model produced: treat that run as failed.

## Step 4: scenario experiments

Compare a perturbed run with a baseline that differs in exactly one thing.
Same case, same length, same EcoSIM commit.

**Warmer, cooler, wetter, drier.** Edit the weather the model reads:

```bash
python scripts/ecosim.py perturb-forcing \
  $ECOSIM_HOME/examples/inputs/dryland_maize/dryland_clm_20230203.nc \
  projects/<id>/data/ecosim/dryland_warm_dry.nc --temp-add 3 --rain-scale 0.7

python scripts/ecosim.py run --case dryland --namelist dryland --years 1 \
  --out projects/<id>/data/ecosim/dryland-warm-dry \
  --set clm_hour_file_in=$PWD/projects/<id>/data/ecosim/dryland_warm_dry.nc
```

`perturb-forcing` copies an hourly climate file and shifts air temperature
(`--temp-add`, degrees C) or scales precipitation, radiation, wind or vapour
pressure (`--rain-scale`, `--rad-scale`, `--wind-scale`, `--vp-scale`). Warming
with vapour pressure unchanged also raises the vapour pressure deficit; say
which you did. Pass the new file as an absolute path.

**CO2.** `--set atm_co2_fix=560.` holds atmospheric CO2 at a fixed ppm. The
`atm_ghg_in` key selects a trajectory file instead; `input_data/` holds
historical and SSP2-4.5 and SSP5-8.5 files.

**Sub-models and site.** `plant_model`, `microbial_model` and `soichem_model`
switch whole components. A different site or soil means a different grid file.

**Confirm the perturbation took.** Before interpreting any difference, check
that the forcing itself changed in the output (`AIR_TEMP_col`, `tPRECIP_col`,
`ATM_CO2_col`). An input the model ignores gives a run identical to the
baseline, and "no response" is then the wrong conclusion. Known case: the
`clm_factor_in` climate-change-factor file is read but **not applied** at
commit `16f9adb` (the call that applies it is commented out in
`f90src/Modelforc/WthrMod.F90`), so a run using it matches its baseline to the
last digit. Use `perturb-forcing` instead.

## Using lakehouse data

EcoSIM does not read BERDL tables. To simulate a site from lakehouse data,
its soil profile, weather and vegetation must first be written as EcoSIM
NetCDF inputs. The `.cdl` text files beside the example inputs
(`examples/inputs/<case>/*.nc.cdl`) show the exact variables and dimensions of
each file, and the EcoSIM repository's `ecosim-agent` submodule holds upstream
preprocessing tools for AmeriFlux sites. Building inputs for a new site is real
work with many judgment calls (soil layering, plant types, spin-up); do not
improvise it silently. Say what you would need, and ask.

The cheaper and often sufficient route: pick the shipped case closest to the
system in question, state that choice and why, and use lakehouse data to set
the size of the perturbation or to compare against the model's response.

## Limits

State these with any EcoSIM result:

- **A finished run is not a validated one.** Exit status 0 and finite numbers
  mean the model ran. They say nothing about whether it matches the real site.
- **Example cases are illustrations.** They are not calibrated to the user's
  site; report responses as "in the EcoSIM `dryland` example", not as a
  prediction for a named place.
- **Short runs are transients.** Soil carbon and microbial pools take years to
  decades to equilibrate. Several cases start long before their weather data
  and need spin-up; a few simulated months show the initial adjustment, not a
  long-term response.
- **One run is one realisation** of one parameter set. Without an ensemble or
  sensitivity runs, give direction and rough magnitude, not uncertainty bounds.

A simulation run to test a hypothesis in a frozen `RESEARCH_PLAN.md` follows
that plan like any other analysis (`/research-plan`, `/execute-plan`); one run
outside a plan is exploration and should be labelled so. Follow the
worklog-capture skill to record what was run: case, EcoSIM commit, run length,
the exact change from baseline, and the output directories. Record surprises,
such as an input the model ignored, with the pitfall-capture skill.
