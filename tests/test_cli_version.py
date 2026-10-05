"""Tests for the installed CLI distribution version."""

import importlib.metadata
import runpy
import sys
import tomllib
from pathlib import Path

import beril_cli

DISTRIBUTION_NAME = "beril-cli"


def _reload_version(monkeypatch, fake_version):
    """Re-execute beril_cli/__init__.py with a stubbed metadata lookup.

    Returns ``(namespace, queried_names)`` so a test can assert both the version
    that came out and the distribution name that was asked for.
    """
    queried_names = []

    def fake(distribution_name):
        queried_names.append(distribution_name)
        return fake_version

    monkeypatch.setattr(importlib.metadata, "version", fake)
    namespace = runpy.run_path(Path(beril_cli.__file__))
    return namespace, queried_names


def test_version_falls_back_without_distribution_metadata(monkeypatch):
    """A source-only checkout still has a meaningful, PEP 440 version."""

    def missing_distribution(_distribution_name):
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", missing_distribution)

    namespace = runpy.run_path(Path(beril_cli.__file__))

    assert namespace["__version__"] == "0+unknown"


def test_version_comes_from_installed_distribution_metadata(monkeypatch):
    """The success path: an installed distribution's version is used verbatim."""
    namespace, _ = _reload_version(monkeypatch, "1.2.3.dev4+g0abcdef")

    assert namespace["__version__"] == "1.2.3.dev4+g0abcdef"


def test_version_queries_the_name_declared_in_pyproject(monkeypatch):
    """Guards the silent-fallback failure: a wrong distribution name.

    ``version()`` raises ``PackageNotFoundError`` for a name that is not
    installed, so a typo here would make ``beril --version`` report
    ``0+unknown`` forever while the fallback test above still passed. Asserting
    against ``pyproject.toml`` rather than a repeated literal means renaming the
    project in one place fails this test instead of silently degrading the CLI.
    """
    _, queried_names = _reload_version(monkeypatch, "1.2.3")

    pyproject = Path(beril_cli.__file__).resolve().parents[1] / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text())["project"]["name"]

    assert queried_names == [declared]
    assert declared == DISTRIBUTION_NAME


def test_installed_distribution_is_actually_present():
    """The name resolves against the real environment, not just a stub.

    Every other test here stubs ``importlib.metadata.version``, so all of them
    would still pass if the distribution were never installed under this name.
    This one does the unmocked lookup.
    """
    assert importlib.metadata.version(DISTRIBUTION_NAME)
    assert sys.modules["beril_cli"].__version__ != "0+unknown"
