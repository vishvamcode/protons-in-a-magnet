#!/usr/bin/env bash
# Stage 3b: the same five energies with a realistic 1 % (1 sigma) energy spread. Writes to results/stage3_spread1/.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
for E in 70 100 150 200 230; do
  echo "== $E MeV, 1 % spread"
  scripts/run.sh "topas/runs/E${E}_B0_s1.txt" results/stage3_spread1
done
