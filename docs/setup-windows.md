# Setup on Windows (WSL + Docker)

Tested on 9-10 Oct 2026 on a Windows 11 x64 PC with 12 CPU threads. Sources: OpenTOPAS
[WSL guide](https://opentopas.readthedocs.io/en/latest/getting-started/WSL.html) and
[container page](https://opentopas.readthedocs.io/en/latest/getting-started/containers.html), read 2026-10-09.

Route: Ubuntu 24.04 under WSL2, Docker inside Ubuntu, and the official image
`opentopas/opentopas:v4.3.0-geant4-11.4.2` (771 MB download, 3.2 GB on disk). Nothing is compiled.
The image does not contain the Geant4 data sets; you download them once (3.4 GB) and mount them.

## 1. WSL and Ubuntu
In PowerShell as administrator:
```powershell
wsl --install -d Ubuntu-24.04
```
Reboot, open "Ubuntu 24.04", create a user, then `sudo apt-get update && sudo apt-get upgrade -y`.

## 2. Docker inside Ubuntu
```bash
sudo apt-get install -y docker.io git python3-venv
sudo usermod -aG docker $USER      # then close and reopen Ubuntu
docker run --rm hello-world
```
If the daemon is not running: `sudo service docker start`.

## 3. Image, data and this repository
```bash
docker pull opentopas/opentopas:v4.3.0-geant4-11.4.2
git clone https://github.com/vishvamcode/protons-in-a-magnet.git && cd protons-in-a-magnet
mkdir -p ~/G4DATA            # create it yourself BEFORE any docker run (see pitfalls)
bash scripts/get_g4data.sh   # 16 data sets into ~/G4DATA; safe to rerun
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## 4. Smoke test and first run
```bash
scripts/run.sh topas/runs/E150_B0.txt     # about 1 minute with 12 threads
python scripts/plot_depth_dose.py results/E150_B0/DepthDose_E150_B0.csv
```
Set `i:Ts/NumberOfThreads` in the run files to your number of cores (`nproc`).

## Pitfalls we hit
| Symptom | Cause | Fix |
|---|---|---|
| `Permission denied` writing into `~/G4DATA` | a `docker run` mounting `~/G4DATA` before the folder existed made Docker create it as root | `sudo chown -R $USER:$USER ~/G4DATA` |
| `ENSDFSTATE.dat is not found` | Geant4 data missing or in the wrong folder | rerun `scripts/get_g4data.sh`; `ls ~/G4DATA` should show the data folders |
| LEND data set download breaks off | very large optional file | not needed for this project's physics list |
| `NeutronHP: ... Argon ... not found` lines | informational fallbacks in the neutron data | harmless |
| `<you>` in copied commands | placeholder | replace with your Windows username |
