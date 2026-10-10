#!/usr/bin/env bash
# Test of the +0.5 % range offset: 70/150/230 MeV with ICRU 90 data off, and with water of I = 75 eV (as PSTAR).
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
for E in 70 150 230; do
  scripts/run.sh "topas/runs/icru90_off/E${E}_B0_noICRU90.txt" results/icru90_off
  scripts/run.sh "topas/runs/water75/E${E}_B0_water75.txt" results/water75
done
