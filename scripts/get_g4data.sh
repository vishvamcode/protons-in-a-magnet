#!/usr/bin/env bash
# Downloads the Geant4 11.4.2 data sets into ~/G4DATA (list from the OpenTOPAS v4.3.0 WSL guide, read 2026-10-09)
# Safe to rerun: data sets already unpacked are skipped.
mkdir -p ~/G4DATA && cd ~/G4DATA || exit 1
for f in G4NDL.4.7.1 G4EMLOW.8.8 G4PhotonEvaporation.6.1.2 G4RadioactiveDecay.6.1.2 \
         G4PARTICLEXS.4.2 G4PII.1.3 G4RealSurface.2.2 G4SAIDDATA.2.0 G4ABLA.3.3 \
         G4INCL.1.3 G4ENSDFSTATE.3.0 G4CHANNELING.2.0 G4NUDEXLIB.1.0 G4URRPT.1.1 \
         G4TENDL.1.4 LEND_GNDS2.0_ENDF.BVII.1; do
  if [ -f "$f.done" ]; then echo "== $f already there"; continue; fi
  echo "== $f"
  if curl -fL --retry 3 --progress-bar -o "$f.tar.gz" "https://cern.ch/geant4-data/datasets/$f.tar.gz" \
     && tar zxf "$f.tar.gz"; then
    rm -f "$f.tar.gz"; touch "$f.done"
  else
    echo "!! FAILED: $f (paste this error in the thread)"; rm -f "$f.tar.gz"
  fi
done
ls ~/G4DATA; du -sh ~/G4DATA
