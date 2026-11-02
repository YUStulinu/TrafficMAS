#!/usr/bin/env bash
# Runs every experiment in experiments/ and writes the figures to docs/.
# About 900 simulations; 10-15 minutes on 16 cores.
set -e
cd "$(dirname "$0")/.."
PY=${PYTHON:-.venv/Scripts/python}
[ -x "$PY" ] || PY=.venv/bin/python
for exp in main emergency ablation robustness selfish braess; do
  "$PY" -m trafficmas experiment "experiments/$exp.yaml" --docs docs
done
