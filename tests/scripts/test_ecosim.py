"""Tests for scripts/ecosim.py.

EcoSIM itself is never needed: the "installed" cases use a fake model, a shell
script standing in for ecosim.f90.x, so staging, namelist edits and the result
record are checked without a Fortran toolchain.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import ecosim

NAMELIST = (
    "&ecosim\ncase_name='toy'\ncontinue_run=.true.\n/\n"
    "&ecosim_time\nrest_opt='nyears'\ndelta_time=3600.\nstop_n=6\n"
    "stop_option='nyears'\n/\n"
)

# Records the namelist it was given, checks the input trees resolve from the
# run directory, and writes one history file.
FAKE_MODEL = """#!/bin/sh
cat "$1" > seen.namelist
test -d ../../inputs && test -d ../../../input_data || exit 9
grep -q "boom=1" "$1" && { echo crashed; exit 7; }
echo "wrote out restart data at nstep 48"
: > toy.ecosim.h0.2001.nc
"""


@pytest.fixture
def call(capsys):
    """Run one command; return (exit status, parsed JSON)."""

    def _call(*argv: str):
        code = ecosim.main(list(argv))
        return code, json.loads(capsys.readouterr().out)

    return _call


@pytest.fixture
def absent(tmp_path, monkeypatch):
    """No EcoSIM anywhere: not in $ECOSIM_HOME, $ECOSIM_EXE or PATH."""
    monkeypatch.setenv("ECOSIM_HOME", str(tmp_path / "absent"))
    monkeypatch.delenv("ECOSIM_EXE", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "emptybin"))


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    """An EcoSIM checkout with one example case, cloned but not built."""
    home = tmp_path / "EcoSIM"
    case = home / "examples" / "run_dir" / "toy"
    case.mkdir(parents=True)
    (home / "examples" / "inputs").mkdir()
    (home / "input_data").mkdir()
    (case / "toy.namelist").write_text(NAMELIST)
    monkeypatch.setenv("ECOSIM_HOME", str(home))
    monkeypatch.delenv("ECOSIM_EXE", raising=False)
    return home


@pytest.fixture
def installed(checkout):
    """The checkout, with the fake model where a build would put the real one."""
    exe = checkout / "build" / "cfg" / "drivers" / "ecosim" / ecosim.EXE_NAME
    exe.parent.mkdir(parents=True)
    exe.write_text(FAKE_MODEL)
    exe.chmod(0o755)
    return checkout


# ------------------------------------------------------------ not installed


def test_check_reports_not_installed(absent, call):
    code, out = call("check")
    assert code == ecosim.NOT_INSTALLED
    assert out["installed"] is False
    assert out["install"] == ecosim.INSTALL_HINT
    assert "reason" in out


@pytest.mark.parametrize(
    "argv", [("cases",), ("run", "--case", "bare_soil", "--days", "1")]
)
def test_commands_answer_in_json_when_not_installed(absent, call, argv):
    code, out = call(*argv)
    assert code == ecosim.NOT_INSTALLED
    assert out["status"] == "error"
    assert out["install"] == ecosim.INSTALL_HINT


def test_dangling_ecosim_exe_is_not_installed(absent, call, tmp_path, monkeypatch):
    monkeypatch.setenv("ECOSIM_EXE", str(tmp_path / "nope" / ecosim.EXE_NAME))
    assert call("check")[0] == ecosim.NOT_INSTALLED


def test_unbuilt_checkout_is_not_installed(checkout, call, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "emptybin"))
    code, out = call("check")
    assert code == ecosim.NOT_INSTALLED
    assert "holds no built" in out["reason"]


# ---------------------------------------------------------------- installed


def test_check_and_cases(installed, call):
    code, out = call("check")
    assert code == 0 and out["installed"] and out["examples"]
    code, out = call("cases")
    assert out["cases"] == [{"case": "toy", "namelists": ["toy"]}]


def test_run_stages_a_fresh_short_run(installed, call, tmp_path):
    code, out = call("run", "--case", "toy", "--days", "2", "--out", str(tmp_path / "r"))
    assert code == 0 and out["status"] == "ok"
    assert out["nstep"] == 48 and out["expected_nstep"] == 48
    assert len(out["history_files"]) == 1
    seen = (Path(out["run_dir"]) / "seen.namelist").read_text()
    assert "stop_n=2" in seen and "stop_option='ndays'" in seen
    assert "rest_opt='never'" in seen and "continue_run=.false." in seen
    # The checkout must stay untouched.
    assert not list((installed / "examples" / "run_dir" / "toy").glob("*.nc"))


def test_set_adds_keys_and_quotes_bare_words(installed, call, tmp_path):
    code, out = call(
        "run", "--case", "toy", "--days", "2", "--out", str(tmp_path / "r"),
        "--set", "atm_co2_fix=560.", "--set", "clm_factor_in=NO",
    )  # fmt: skip
    seen = (Path(out["run_dir"]) / "seen.namelist").read_text()
    assert "atm_co2_fix=560." in seen and "clm_factor_in='NO'" in seen


def test_run_that_stops_early_is_a_failure(installed, call, tmp_path):
    code, out = call("run", "--case", "toy", "--days", "3", "--out", str(tmp_path / "r"))
    assert code == 1
    assert "reached nstep 48 of 72" in out["problems"]


def test_model_crash_is_reported_with_the_log(installed, call, tmp_path):
    code, out = call(
        "run", "--case", "toy", "--days", "2", "--out", str(tmp_path / "r"),
        "--set", "boom=1",
    )  # fmt: skip
    assert code == 1 and out["returncode"] == 7
    assert "crashed" in out["log_tail"]


def test_unknown_case_lists_the_available_ones(installed, call, tmp_path):
    code, out = call("run", "--case", "missing", "--out", str(tmp_path / "r"))
    assert code == 1 and out["available"] == ["toy"]


def test_used_output_directory_is_refused(installed, call, tmp_path):
    args = ("run", "--case", "toy", "--days", "2", "--out", str(tmp_path / "r"))
    assert call(*args)[0] == 0
    code, out = call(*args)
    assert code == 1 and "not empty" in out["error"]


def test_relative_ecosim_home_still_resolves(installed, call, tmp_path, monkeypatch):
    """`run` symlinks into the checkout from a scratch directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ECOSIM_HOME", "EcoSIM")
    code, out = call("run", "--case", "toy", "--days", "2", "--out", "rel")
    assert code == 0 and out["status"] == "ok"


# ------------------------------------------------------------------ helpers


def test_missing_inputs_are_errors_not_tracebacks(installed, call, tmp_path):
    code, out = call(
        "perturb-forcing", str(tmp_path / "no.nc"), str(tmp_path / "o.nc"), "--temp-add", "3"
    )
    assert code == 1 and "not found" in out["error"]
    code, out = call("summarize", str(tmp_path / "nowhere"))
    assert code == 1 and "no EcoSIM history files" in out["error"]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("NO", "'NO'"),
        ("1.5e3", "1.5e3"),
        (".true.", ".true."),
        ("'x'", "'x'"),
        ("30,30,30", "30,30,30"),
    ],
)
def test_quote(value, expected):
    assert ecosim.quote(value) == expected
