#!/usr/bin/env python3
"""Find, run and summarise the EcoSIM ecosystem model. Standard library only.

    python scripts/ecosim.py check
    python scripts/ecosim.py cases
    python scripts/ecosim.py run --case dryland --days 30 --out DIR
    python scripts/ecosim.py run --case dryland --years 2 --set atm_co2_fix=560.
    python scripts/ecosim.py perturb-forcing IN.nc OUT.nc --temp-add 3 --rain-scale 0.7
    python scripts/ecosim.py summarize DIR [--vars ECO_GPP_col,ECO_RH_col]

Every command prints one JSON object on stdout. Exit status:

    0  the command did what was asked
    1  EcoSIM is installed but the request failed (bad case, model crash, ...)
    2  usage error
    3  EcoSIM is not installed (or a needed part of it is missing)

Status 3 is an answer, not a crash: the JSON says what was searched and how to
install. EcoSIM is optional; nothing else in BERIL depends on it.

Where EcoSIM is looked for, first hit wins:

    $ECOSIM_EXE    path to ecosim.f90.x
    $ECOSIM_HOME   an EcoSIM checkout (default ~/.ecosim/EcoSIM, which is where
                   install_ecosim.sh builds)
    PATH           an `ecosim.f90.x` on PATH

`run` never touches the checkout. It stages the case's namelist in a scratch
mirror that symlinks the input trees at the depth the namelist's relative paths
expect, then runs there.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

EXE_NAME = "ecosim.f90.x"
NOT_INSTALLED = 3
INSTALL_HINT = "bash scripts/install_ecosim.sh"
# Where the executable sits inside a checkout, newest layout first.
_EXE_GLOBS = (
    "build/*/drivers/ecosim/" + EXE_NAME,
    "build/*/local/bin/" + EXE_NAME,
    "build/*/bin/" + EXE_NAME,
    "local/bin/" + EXE_NAME,
)
_STOP = {"days": "ndays", "months": "nmonths", "years": "nyears"}
# History values at or above this are the model's fill sentinel, not data.
_FILL_CUTOFF = 1e30
# Set in the child when a command re-runs itself under uv; stops a loop.
_REEXEC = "ECOSIM_PY_REEXEC"


class EcosimError(Exception):
    """A failure to report as JSON. `code` becomes the exit status."""

    def __init__(self, message: str, code: int = 1, **extra: Any) -> None:
        super().__init__(message)
        self.code = code
        self.extra = extra


def default_home() -> Path:
    # Absolute: `run` symlinks into this tree from a scratch directory, where
    # a relative $ECOSIM_HOME would point at nothing.
    home = Path(os.environ.get("ECOSIM_HOME") or Path.home() / ".ecosim" / "EcoSIM")
    return home.expanduser().absolute()


def locate() -> dict[str, Any]:
    """Describe the EcoSIM installation, or its absence. Never raises."""
    searched: list[str] = []
    home = default_home()
    exe: Path | None = None

    env_exe = os.environ.get("ECOSIM_EXE")
    if env_exe:
        searched.append(f"$ECOSIM_EXE={env_exe}")
        if os.access(env_exe, os.X_OK) and Path(env_exe).is_file():
            exe = Path(env_exe)
    if exe is None:
        searched.append(str(home))
        if home.is_dir():
            hits = [
                p for g in _EXE_GLOBS for p in home.glob(g) if os.access(p, os.X_OK)
            ]
            if hits:
                exe = max(hits, key=lambda p: p.stat().st_mtime)
    if exe is None:
        searched.append("PATH")
        on_path = shutil.which(EXE_NAME)
        if on_path:
            exe = Path(on_path)

    has_examples = (home / "examples" / "run_dir").is_dir() and (
        home / "input_data"
    ).is_dir()
    info: dict[str, Any] = {
        "installed": exe is not None,
        "executable": str(exe) if exe else None,
        "home": str(home) if home.is_dir() else None,
        "examples": has_examples,
        "searched": searched,
    }
    if exe is None:
        info["reason"] = (
            f"no {EXE_NAME} found"
            if not home.is_dir()
            else f"{home} exists but holds no built {EXE_NAME}"
        )
        info["install"] = INSTALL_HINT
    elif home.is_dir():
        info["commit"] = _git_commit(home)
    return info


def _git_commit(home: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(home), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):  # parenthesised: older Pythons
        return None
    return out.stdout.strip() or None


def require(need_examples: bool = False) -> dict[str, Any]:
    info = locate()
    if not info["installed"]:
        raise EcosimError("EcoSIM is not installed", NOT_INSTALLED, **info)
    if need_examples and not info["examples"]:
        raise EcosimError(
            "EcoSIM executable found, but no checkout with examples/ and input_data/; "
            "set ECOSIM_HOME to an EcoSIM checkout",
            NOT_INSTALLED,
            **info,
        )
    return info


def list_cases(home: Path) -> list[dict[str, Any]]:
    cases = []
    for d in sorted((home / "examples" / "run_dir").iterdir()):
        names = sorted(p.stem for p in d.glob("*.namelist")) if d.is_dir() else []
        if names:
            cases.append({"case": d.name, "namelists": names})
    return cases


# ---------------------------------------------------------------- namelist


def set_namelist(text: str, key: str, value: str) -> str:
    """Replace `key = ...` on its own line, or add it to the group that owns it.

    Timer keys live in `&ecosim_time`; everything else goes to `&ecosim`.
    Multi-line values (the `hist_fincl*` lists) are not supported on purpose:
    edit the namelist file and pass it with `--namelist-file` instead.
    """
    pat = re.compile(
        rf"^[ \t]*{re.escape(key)}[ \t]*=.*$", re.MULTILINE | re.IGNORECASE
    )
    line = f"{key}={value}"
    if pat.search(text):
        return pat.sub(lambda _: line, text, count=1)
    timer = {
        "stop_n",
        "stop_option",
        "rest_opt",
        "rest_frq",
        "delta_time",
        "diag_frq",
        "diag_opt",
    }
    group = "ecosim_time" if key.lower() in timer else "ecosim"
    head = re.compile(rf"^[ \t]*&{group}[ \t]*$", re.MULTILINE | re.IGNORECASE)
    m = head.search(text)
    if not m:
        raise EcosimError(f"namelist has no &{group} group to hold {key}")
    return text[: m.end()] + "\n" + line + text[m.end() :]


def get_namelist(text: str, key: str) -> str | None:
    m = re.search(rf"^[ \t]*{re.escape(key)}[ \t]*=[ \t]*([^!\n]*)", text, re.M | re.I)
    return m.group(1).strip() if m else None


def quote(value: str) -> str:
    """Fortran-quote a bare word; leave numbers, logicals and quoted text alone."""
    v = value.strip()
    if re.fullmatch(r"[-+]?(\d+\.?\d*|\.\d+)([eEdD][-+]?\d+)?", v) or v.lower() in {
        ".true.",
        ".false.",
    }:
        return v
    if v[:1] in "'\"" or "," in v:
        return v
    return "'" + v.replace("'", "''") + "'"


# --------------------------------------------------------------------- run


def run_case(a: argparse.Namespace) -> dict[str, Any]:
    info = require(need_examples=True)
    home, exe = Path(info["home"]), Path(info["executable"]).resolve()
    src = home / "examples" / "run_dir" / a.case
    if not src.is_dir():
        raise EcosimError(
            f"no example case {a.case!r}",
            available=[c["case"] for c in list_cases(home)],
        )
    if a.namelist_file:
        nl_src = Path(a.namelist_file)
        if not nl_src.is_file():
            raise EcosimError(f"namelist file not found: {nl_src}")
    else:
        names = sorted(p.stem for p in src.glob("*.namelist"))
        want = a.namelist or (names[0] if len(names) == 1 else None)
        if want not in names:
            raise EcosimError(
                f"case {a.case!r} has several namelists; pick one with --namelist"
                if want is None
                else f"case {a.case!r} has no namelist {want!r}",
                namelists=names,
            )
        nl_src = src / f"{want}.namelist"

    text = nl_src.read_text()
    length = [(k, getattr(a, k)) for k in _STOP if getattr(a, k) is not None]
    if len(length) > 1:
        raise EcosimError("give only one of --days, --months, --years", 2)
    if length:
        unit, n = length[0]
        text = set_namelist(text, "stop_n", str(n))
        text = set_namelist(text, "stop_option", f"'{_STOP[unit]}'")
    # A fresh, self-contained run: no restart pointer to pick up or leave behind.
    text = set_namelist(text, "continue_run", ".false.")
    if not a.keep_restarts:
        text = set_namelist(text, "rest_opt", "'never'")
    for item in a.set or []:
        key, sep, value = item.partition("=")
        if not sep or not key.strip():
            raise EcosimError(f"--set wants key=value, got {item!r}", 2)
        text = set_namelist(text, key.strip(), quote(value))

    if a.out:
        out = Path(a.out)
    else:
        out = Path(tempfile.mkdtemp(prefix="ecosim_run."))
    out = out.resolve()
    # Namelists point at ../../inputs/<case>/ and ../../../input_data/, so the
    # case only resolves at <root>/examples/run_dir/<case>/. Mirror that depth.
    mirror = out / "eco"
    case_dir = mirror / "examples" / "run_dir" / a.case
    if case_dir.exists() and any(case_dir.iterdir()):
        raise EcosimError(f"{case_dir} is not empty; choose another --out")
    case_dir.mkdir(parents=True, exist_ok=True)
    for name, target in (
        ("input_data", home / "input_data"),
        ("examples/inputs", home / "examples" / "inputs"),
    ):
        link = mirror / name
        if not link.exists():
            link.symlink_to(target, target_is_directory=True)
    # A `finidat='./x.nc'` restart lives beside the namelist; bring it along.
    for rel in re.findall(r"finidat\s*=\s*'\./([^']+)'", text):
        if (src / rel).is_file():
            shutil.copy2(src / rel, case_dir / rel)
        else:
            raise EcosimError(
                f"namelist starts from restart {rel!r}, which this checkout does not have; "
                "that case continues another run and cannot start on its own"
            )
    nl = case_dir / nl_src.name
    nl.write_text(text)
    log = out / "ecosim.log"

    start = time.monotonic()
    timed_out = False
    with log.open("wb") as fh:
        try:
            rc = subprocess.run(
                [str(exe), nl.name],
                cwd=case_dir,
                stdout=fh,
                stderr=subprocess.STDOUT,
                timeout=a.timeout,
                check=False,
            ).returncode
        except subprocess.TimeoutExpired:
            rc, timed_out = -1, True
        except OSError as e:
            raise EcosimError(
                f"could not start {exe}: {e}", NOT_INSTALLED, **info
            ) from e
    wall = round(time.monotonic() - start, 1)

    log_text = log.read_text(errors="replace")
    steps = re.findall(r"nstep\s*=?\s*(\d+)", log_text)
    nstep = int(steps[-1]) if steps else None
    history = sorted(str(p) for p in case_dir.rglob("*.ecosim.h*.nc"))
    result: dict[str, Any] = {
        "status": "ok",
        "case": a.case,
        "namelist": str(nl),
        "run_dir": str(case_dir),
        "log": str(log),
        "history_files": history,
        "returncode": rc,
        "nstep": nstep,
        "wall_seconds": wall,
        "executable": str(exe),
        "ecosim_commit": info.get("commit"),
        "stop": [get_namelist(text, "stop_n"), get_namelist(text, "stop_option")],
    }
    problems = []
    if timed_out:
        problems.append(f"stopped after the {a.timeout}s --timeout")
    elif rc != 0:
        problems.append(f"model exited with status {rc}")
    if not history:
        problems.append("no history file was written")
    # Hourly steps are the only cadence where the expected count is knowable
    # here; a model that exits 0 short of it stopped early without saying so.
    dt = get_namelist(text, "delta_time")
    if length and length[0][0] == "days" and dt and float(dt.rstrip(".") or 0) == 3600:
        expect = length[0][1] * 24
        result["expected_nstep"] = expect
        if nstep is not None and nstep < expect:
            problems.append(f"reached nstep {nstep} of {expect}")
    if problems:
        result["status"] = "failed"
        result["problems"] = problems
        result["log_tail"] = log_text[-1500:]
    return result


# ------------------------------------------------------------------ netCDF


def _netcdf() -> tuple[Any, Any]:
    """Import netCDF4 and numpy, or re-run this command under uv with them.

    The packages are not BERIL dependencies, so uv provides them for the one
    command (cached after the first use) and no environment is modified.
    """
    try:
        import netCDF4  # ty: ignore[unresolved-import]
        import numpy as np  # ty: ignore[unresolved-import]
    except ImportError:
        need = (
            "reading or writing EcoSIM NetCDF files needs the netCDF4 and numpy "
            "Python packages"
        )
        uv = shutil.which("uv")
        if not uv or os.environ.get(_REEXEC):
            raise EcosimError(
                f"{need}; install uv, or run this script with a Python that has them",
                NOT_INSTALLED,
            ) from None
        cmd = [uv, "run", "--quiet", "--no-project"]
        cmd += ["--with", "netCDF4", "--with", "numpy"]
        cmd += ["python", __file__, *sys.argv[1:]]
        proc = subprocess.run(
            cmd,
            env={**os.environ, _REEXEC: "1"},
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            json.loads(proc.stdout)
        except ValueError:
            # uv itself failed (offline, no wheel): still answer in JSON.
            raise EcosimError(
                f"{need}, and uv could not provide them",
                NOT_INSTALLED,
                uv_error=proc.stderr.strip()[-600:],
            ) from None
        sys.stdout.write(proc.stdout)
        sys.exit(proc.returncode)
    return netCDF4, np


# Hourly forcing variables and the one change each takes: (flag, kind).
_FORCING = {
    "TMPH": ("temp_add", "add"),
    "RAINH": ("rain_scale", "scale"),
    "SRADH": ("rad_scale", "scale"),
    "WINDH": ("wind_scale", "scale"),
    "DWPTH": ("vp_scale", "scale"),
}


def perturb_forcing(a: argparse.Namespace) -> dict[str, Any]:
    """Copy an hourly climate file with temperature shifted and fluxes scaled.

    This is the working way to pose a warmer, drier or wetter scenario: the
    model reads the edited file as ordinary weather.
    """
    src, dst = Path(a.source), Path(a.dest)
    if not src.is_file():
        raise EcosimError(f"climate file not found: {src}")
    if dst.exists():
        raise EcosimError(f"{dst} already exists; choose a new name")
    changes = {
        var: (kind, getattr(a, flag))
        for var, (flag, kind) in _FORCING.items()
        if getattr(a, flag) is not None
    }
    if not changes:
        raise EcosimError(
            "no change requested; give at least one of --temp-add, --rain-scale, ...", 2
        )
    netCDF4, np = _netcdf()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    done = {}
    try:
        with netCDF4.Dataset(dst, "a") as nc:
            nc.set_auto_mask(False)
            for var, (kind, amount) in changes.items():
                if var not in nc.variables:
                    raise EcosimError(
                        f"{src.name} has no {var}; this command handles hourly files "
                        f"(variables {', '.join(_FORCING)})"
                    )
                v = nc.variables[var]
                data = np.asarray(v[:], dtype=float)
                real = np.isfinite(data) & (
                    np.abs(data) < _FILL_CUTOFF
                )  # leave fill alone
                before = float(data[real].mean()) if real.any() else None
                data[real] = (
                    data[real] + amount if kind == "add" else data[real] * amount
                )
                v[:] = data
                done[var] = {
                    kind: amount,
                    "units": getattr(v, "units", None),
                    "mean_before": before,
                    "mean_after": float(data[real].mean()) if real.any() else None,
                }
    except EcosimError:
        dst.unlink(missing_ok=True)
        raise
    return {
        "status": "ok",
        "source": str(src),
        "dest": str(dst.resolve()),
        "changes": done,
    }


# --------------------------------------------------------------- summarize


def summarize(target: Path, wanted: list[str] | None) -> dict[str, Any]:
    files = (
        [target] if target.is_file() else sorted(target.rglob("*.ecosim.h*.nc"))
    )  # run dirs nest
    if not files:
        raise EcosimError(f"no EcoSIM history files (*.ecosim.h*.nc) under {target}")
    netCDF4, np = _netcdf()

    out_files = []
    for path in files:
        with netCDF4.Dataset(path) as nc:
            # Auto-masking turns the model's ~1e36 fill into NaN and makes
            # every file look broken; handle fill explicitly instead.
            nc.set_auto_mask(False)
            dims = {k: len(v) for k, v in nc.dimensions.items()}
            names = [
                n
                for n, v in nc.variables.items()
                if np.issubdtype(v.dtype, np.floating)
            ]
            unknown = [w for w in wanted or [] if w not in nc.variables]
            variables = {}
            for n in wanted or names:
                if n not in nc.variables:
                    continue
                v = nc.variables[n]
                a = np.asarray(v[:], dtype=float)
                fill = getattr(v, "_FillValue", None)
                keep = ~np.isfinite(a) | (np.abs(a) < _FILL_CUTOFF)
                if fill is not None and not np.isnan(float(fill)):
                    keep &= a != float(fill)
                data = a[keep]
                entry: dict[str, Any] = {
                    "long_name": getattr(v, "long_name", None),
                    "units": getattr(v, "units", None),
                    "dims": list(v.dimensions),
                    "n": int(data.size),
                }
                if data.size:
                    bad = int((~np.isfinite(data)).sum())
                    good = data[np.isfinite(data)]
                    if bad:
                        entry["non_finite"] = bad
                    if good.size:
                        entry.update(
                            min=float(good.min()),
                            mean=float(good.mean()),
                            max=float(good.max()),
                        )
                        if (
                            a.ndim >= 1
                            and a.shape[0] > 1
                            and "time" in v.dimensions[:1]
                        ):
                            first = a[0][keep[0]]
                            last = a[-1][keep[-1]]
                            if first.size and last.size:
                                entry["first"] = float(np.nanmean(first))
                                entry["last"] = float(np.nanmean(last))
                else:
                    entry["all_fill"] = True
                variables[n] = entry
            item: dict[str, Any] = {
                "file": str(path),
                "dims": dims,
                "n_variables": len(names),
            }
            if wanted:
                item["variables"] = variables
                if unknown:
                    item["unknown_variables"] = unknown
            else:
                # The full table is hundreds of rows; list names, flag trouble.
                item["variable_names"] = names
                item["non_finite"] = sorted(
                    n for n, e in variables.items() if e.get("non_finite")
                )
                item["all_fill"] = sorted(
                    n for n, e in variables.items() if e.get("all_fill")
                )
            out_files.append(item)
    return {"status": "ok", "files": out_files}


# -------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check", help="is EcoSIM installed, and where")
    sub.add_parser("cases", help="list the example cases")
    r = sub.add_parser("run", help="run one example case in a scratch mirror")
    r.add_argument("--case", required=True, help="directory under examples/run_dir/")
    r.add_argument("--namelist", help="namelist stem, when the case has several")
    r.add_argument(
        "--namelist-file", help="use this edited namelist instead of the case's own"
    )
    r.add_argument("--days", type=int)
    r.add_argument("--months", type=int)
    r.add_argument("--years", type=int)
    r.add_argument(
        "--set", action="append", metavar="KEY=VALUE", help="override a namelist key"
    )
    r.add_argument(
        "--out", help="output directory (default: a new temporary directory)"
    )
    r.add_argument(
        "--timeout", type=int, default=3600, help="wall-clock seconds (default 3600)"
    )
    r.add_argument(
        "--keep-restarts", action="store_true", help="leave rest_opt as the case set it"
    )
    s = sub.add_parser("summarize", help="summarise history files from a run")
    s.add_argument("path", type=Path)
    s.add_argument(
        "--vars", help="comma-separated variable names to give statistics for"
    )
    f = sub.add_parser(
        "perturb-forcing", help="copy an hourly climate file with changes applied"
    )
    f.add_argument("source", help="the case's clm_hour_file_in")
    f.add_argument(
        "dest", help="new file to write; pass it to run with --set clm_hour_file_in="
    )
    f.add_argument("--temp-add", type=float, help="degrees C added to air temperature")
    f.add_argument("--rain-scale", type=float, help="multiplier on precipitation")
    f.add_argument("--rad-scale", type=float, help="multiplier on solar radiation")
    f.add_argument("--wind-scale", type=float, help="multiplier on wind speed")
    f.add_argument("--vp-scale", type=float, help="multiplier on vapour pressure")
    a = ap.parse_args(argv)

    if not a.cmd:
        ap.error("a command is required")
    try:
        if a.cmd == "check":
            info = locate()
            print(json.dumps(info, indent=2))
            return 0 if info["installed"] else NOT_INSTALLED
        if a.cmd == "cases":
            info = require(need_examples=True)
            out: dict[str, Any] = {
                "home": info["home"],
                "cases": list_cases(Path(info["home"])),
            }
        elif a.cmd == "run":
            out = run_case(a)
        elif a.cmd == "perturb-forcing":
            out = perturb_forcing(a)
        else:
            out = summarize(a.path, [v for v in (a.vars or "").split(",") if v] or None)
    except EcosimError as e:
        print(json.dumps({"status": "error", "error": str(e), **e.extra}, indent=2))
        return e.code
    print(json.dumps(out, indent=2))
    return 0 if out.get("status", "ok") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
