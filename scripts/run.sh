#!/usr/bin/env bash
# Run one OpenTOPAS parameter file in the official Docker image.
# Usage: scripts/run.sh topas/runs/E150_B0.txt [output_dir]
# Output CSVs go to output_dir (default: results/<run-name>/). Geant4 data: $G4DATA (default ~/G4DATA).
set -euo pipefail
IMAGE="opentopas/opentopas:v4.3.0-geant4-11.4.2"
G4DATA="${G4DATA:-$HOME/G4DATA}"
run_file="$1"
name="$(basename "$run_file" .txt)"
repo="$(cd "$(dirname "$0")/.." && pwd)"
out="${2:-$repo/results/$name}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"   # docker needs an absolute path for the volume mount
[ -d "$G4DATA" ] || { echo "Geant4 data not found at $G4DATA (run scripts/get_g4data.sh)"; exit 1; }
cp "$run_file" "$out/"
# TOPAS writes its output next to the parameter file, inside /simulations
docker run --rm -v "$G4DATA":/Applications/G4Data:ro -v "$out":/simulations "$IMAGE" "$name.txt" \
  > "$out/log_$name.txt" 2>&1 || { echo "TOPAS failed, see $out/log_$name.txt"; tail -n 20 "$out/log_$name.txt"; exit 1; }
rm "$out/$name.txt"
grep -A1 "Execution:" "$out/log_$name.txt" | head -1
echo "Results in $out"
