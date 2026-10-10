#!/usr/bin/env bash
# Stage 3: the five validation energies, no field. Writes to results/stage3/, then the summary table and figures.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
for E in 70 100 150 200 230; do
  echo "== $E MeV"
  scripts/run.sh "topas/runs/E${E}_B0.txt" results/stage3
done
python -m analysis.summarize
python -m analysis.figures
