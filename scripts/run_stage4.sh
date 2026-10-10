#!/usr/bin/env bash
# Stage 4: 4 energies x 4 fields (0, 0.5, 1.0, 1.5 T). Writes to results/stage4/, then gzips the x-z dose maps.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
for E in 100 150 200 230; do
  for B in 0 0.5 1.0 1.5; do
    echo "== $E MeV, $B T"
    scripts/run.sh "topas/runs/stage4/E${E}_B${B}.txt" results/stage4
  done
done
gzip -9f results/stage4/DoseXZ_*.csv
