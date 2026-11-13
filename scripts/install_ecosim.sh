#!/usr/bin/env bash
# Build EcoSIM (https://github.com/EcoSIM-model/EcoSIM) for this user.
#
#   bash scripts/install_ecosim.sh            # clone + build
#   bash scripts/install_ecosim.sh --check    # report what is missing, change nothing
#
# Environment:
#   ECOSIM_HOME       checkout to build in       (default: ~/.ecosim/EcoSIM)
#   ECOSIM_TOOLCHAIN  conda prefix for compilers (default: ~/.ecosim/toolchain)
#   ECOSIM_REF        branch, tag or commit      (default: main)
#   ECOSIM_REPO       git URL                    (default: the public GitHub repo)
#   ECOSIM_JOBS       parallel build jobs        (default: all cores, capped at 32)
#
# EcoSIM vendors zlib, HDF5 and netCDF as submodules and builds them itself, so
# the only requirements are git, a C/C++/Fortran compiler, cmake, make, the
# autotools and the libxml2 headers (netCDF's configure wants xml2-config). When any of those is missing and conda or mamba is on PATH, the
# script creates a private conda environment at $ECOSIM_TOOLCHAIN holding those
# build tools and nothing else (no Python packages; it never touches the base
# environment). conda is used because it can supply a Fortran compiler without
# root, which uv cannot. Without conda it stops and names the missing
# packages; it never uses sudo.
#
# Exit status: 0 built (or --check found everything), 1 build failed,
# 3 a prerequisite is missing and could not be provided.
set -uo pipefail

ECOSIM_HOME="${ECOSIM_HOME:-$HOME/.ecosim/EcoSIM}"
ECOSIM_TOOLCHAIN="${ECOSIM_TOOLCHAIN:-$HOME/.ecosim/toolchain}"
ECOSIM_REF="${ECOSIM_REF:-main}"
ECOSIM_REPO="${ECOSIM_REPO:-https://github.com/EcoSIM-model/EcoSIM.git}"
check_only=0
[ "${1:-}" = "--check" ] && check_only=1
[ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] && { sed -n '2,24p' "$0"; exit 0; }

say() { printf 'install_ecosim: %s\n' "$*"; }
die() { printf 'install_ecosim: %s\n' "$*" >&2; exit "${2:-1}"; }

TOOLS=(gcc g++ gfortran cmake make autoreconf libtoolize xml2-config)
missing_tools() {
  local t out=""
  for t in "${TOOLS[@]}"; do command -v "$t" >/dev/null 2>&1 || out="$out $t"; done
  # macOS ships libtoolize as glibtoolize.
  if [[ $out == *libtoolize* ]] && command -v glibtoolize >/dev/null 2>&1; then
    out="${out// libtoolize/}"
  fi
  printf '%s' "$out"
}

command -v git >/dev/null 2>&1 || die "git is not on PATH; install git first." 3

# ------------------------------------------------------------------ toolchain
conda_bin=""
for c in mamba conda; do command -v "$c" >/dev/null 2>&1 && { conda_bin=$c; break; }; done

use_conda=0
missing=$(missing_tools)
if [ -x "$ECOSIM_TOOLCHAIN/bin/gfortran" ] || [ -n "$(ls "$ECOSIM_TOOLCHAIN"/bin/*-gfortran 2>/dev/null)" ]; then
  use_conda=1                      # a previous run already made the toolchain
elif [ -n "$missing" ]; then
  if [ -n "$conda_bin" ]; then
    use_conda=1
  else
    die "missing build tools:$missing
No conda or mamba on PATH to provide them. Install them with your package manager, e.g.
  Debian/Ubuntu: apt-get install gfortran g++ cmake make autoconf automake libtool libxml2-dev
  Rocky/RHEL:    dnf install gcc-gfortran gcc-c++ cmake make autoconf automake libtool libxml2-devel
  macOS:         brew install gcc cmake autoconf automake libtool
then re-run this script." 3
  fi
fi

if [ "$check_only" -eq 1 ]; then
  if [ "$use_conda" -eq 1 ] && [ ! -d "$ECOSIM_TOOLCHAIN" ]; then
    say "missing build tools:$missing"
    say "would create a conda toolchain at $ECOSIM_TOOLCHAIN with $conda_bin"
  elif [ "$use_conda" -eq 1 ]; then
    say "conda toolchain present at $ECOSIM_TOOLCHAIN"
  else
    say "system build tools are sufficient"
  fi
  say "would build $ECOSIM_REPO@$ECOSIM_REF in $ECOSIM_HOME"
  exit 0
fi

if [ "$use_conda" -eq 1 ]; then
  if [ ! -d "$ECOSIM_TOOLCHAIN/conda-meta" ]; then
    [ -n "$conda_bin" ] || die "toolchain at $ECOSIM_TOOLCHAIN is incomplete and conda is not on PATH." 3
    say "creating conda toolchain at $ECOSIM_TOOLCHAIN (missing:${missing:- none})"
    mkdir -p "$(dirname "$ECOSIM_TOOLCHAIN")"
    # Build tools only. Python packages are not installed here: ecosim.py gets
    # netCDF4 and numpy from uv when it needs them.
    "$conda_bin" create -y -q -p "$ECOSIM_TOOLCHAIN" -c conda-forge \
      c-compiler cxx-compiler fortran-compiler cmake make autoconf automake libtool m4 \
      pkg-config libxml2-devel \
      || die "conda could not create the toolchain environment." 3
  fi
  # Activate without requiring `conda init`: the activation scripts export
  # CC/CXX/FC/CFLAGS/LDFLAGS for the conda compilers.
  export PATH="$ECOSIM_TOOLCHAIN/bin:$PATH"
  export CONDA_PREFIX="$ECOSIM_TOOLCHAIN"
  set +u
  for f in "$ECOSIM_TOOLCHAIN"/etc/conda/activate.d/*.sh; do [ -f "$f" ] && . "$f"; done
  set -u
  CC="${CC:-$(command -v gcc)}"; CXX="${CXX:-$(command -v g++)}"
  FC="${FC:-$(command -v gfortran)}"
else
  CC="${CC:-$(command -v gcc)}"; CXX="${CXX:-$(command -v g++)}"
  FC="${FC:-$(command -v gfortran)}"
fi
[ -n "$FC" ] && [ -n "$CC" ] && [ -n "$CXX" ] || die "no usable compilers after toolchain setup." 3
say "compilers: CC=$CC CXX=$CXX FC=$FC"

# --------------------------------------------------------------------- source
if [ ! -d "$ECOSIM_HOME/.git" ]; then
  say "cloning $ECOSIM_REPO into $ECOSIM_HOME"
  mkdir -p "$(dirname "$ECOSIM_HOME")"
  git clone -q "$ECOSIM_REPO" "$ECOSIM_HOME" || die "git clone failed (no network access to GitHub?)." 3
fi
cd "$ECOSIM_HOME" || die "cannot enter $ECOSIM_HOME"
git fetch -q origin "$ECOSIM_REF" 2>/dev/null || true
git checkout -q "$ECOSIM_REF" 2>/dev/null || git checkout -q FETCH_HEAD \
  || die "cannot check out $ECOSIM_REF"
# Only the vendored libraries: the ecosim-agent submodule uses an SSH URL and
# is not needed to build or run the model.
git submodule update --init --depth 1 \
  3rd-partylibs/hdf5 3rd-partylibs/netcdf-c 3rd-partylibs/netcdf-fortran 3rd-partylibs/zlib \
  || die "could not fetch the vendored libraries." 3
say "source at $(git rev-parse --short HEAD) ($ECOSIM_REF)"

# ---------------------------------------------------------------------- build
jobs="${ECOSIM_JOBS:-$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)}"
[ "$jobs" -gt 32 ] && [ -z "${ECOSIM_JOBS:-}" ] && jobs=32
log="$ECOSIM_HOME/beril-install.log"
say "building with $jobs jobs; this takes several minutes. Log: $log"
if ! bash build_EcoSIM.sh CC="$CC" CXX="$CXX" FC="$FC" --jobs="$jobs" >"$log" 2>&1; then
  tail -25 "$log" >&2
  die "build failed; full log at $log. Third-party logs are under $ECOSIM_HOME/build/*/3rd-partylibs/."
fi
exe=$(find "$ECOSIM_HOME/build" -name 'ecosim.f90.x' -type f 2>/dev/null | head -1)
[ -n "$exe" ] && [ -x "$exe" ] || die "build finished but ecosim.f90.x was not produced; see $log"
say "OK: $exe"
