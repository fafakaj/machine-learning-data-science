#!/usr/bin/env bash
# Rebuild and validate every data file of the app.
# numpy/pandas/scikit-learn versions match Pyodide 314.0.7, so printed outputs are identical in the browser.
set -euo pipefail
cd "$(dirname "$0")/.."
RUN=(uv run --python 3.14 --no-project --with numpy==2.4.6 --with pandas==3.0.2 --with scikit-learn==1.8.0 --with scipy==1.18.0 python)
"${RUN[@]}" tools/build_content.py
"${RUN[@]}" tools/build_plan.py "$@"
"${RUN[@]}" tools/build_anki.py
python3 tools/check_coverage.py
if [[ "${1:-}" == "--problems" ]]; then
  "${RUN[@]}" tools/build_problems.py
fi
