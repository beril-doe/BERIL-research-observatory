#!/usr/bin/env bash
set -euo pipefail

VENV_PATH="${1:-.venv-berdl}"

if [[ ! -d "${VENV_PATH}" ]]; then
  python3 -m venv "${VENV_PATH}"
fi

# shellcheck source=/dev/null
source "${VENV_PATH}/bin/activate"

python -m pip install --upgrade pip
# spark_connect_remote and berdl_remote are private repos in the KBaseDataLakehouse
# org (renamed from BERDataLakehouse); the install fails without read access.
python -m pip install \
  "git+https://github.com/KBaseDataLakehouse/spark_connect_remote.git" \
  "git+https://github.com/KBaseDataLakehouse/berdl_remote.git" \
  "boto3>=1.34.0" \
  "pproxy" \
  "pandas" \
  "matplotlib" || {
  echo "If the error above is 'Repository not found' or 'could not read Username', you need read access" >&2
  echo "to the private KBaseDataLakehouse repos: https://github.com/beril-doe/BERIL-research-observatory/issues/407" >&2
  exit 1
}

# Make scripts/ importable so notebooks can do:
#   from get_spark_session import get_spark_session
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_PACKAGES="$(python -c 'import site; print(site.getsitepackages()[0])')"
echo "${SCRIPTS_DIR}" > "${SITE_PACKAGES}/berdl-scripts.pth"

echo "Environment is ready."
echo "Activate with: source ${VENV_PATH}/bin/activate"
