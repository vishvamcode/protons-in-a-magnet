"""Quick look at one TOPAS depth-dose CSV: python scripts/plot_depth_dose.py results/stage3/DepthDose_E150_B0.csv [n_histories]"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis.io import read_topas_depth_dose  # noqa: E402
from analysis.metrics import distal_depth_mm, peak_depth_mm, relative_uncertainty_at_peak  # noqa: E402

path = Path(sys.argv[1])
n_histories = int(sys.argv[2]) if len(sys.argv) > 2 else 100_000
dd = read_topas_depth_dose(path, n_histories)
print(f"Peak depth: {peak_depth_mm(dd):.2f} mm, R80: {distal_depth_mm(dd, 0.8):.2f} mm, "
      f"relative uncertainty at peak: {relative_uncertainty_at_peak(dd):.2%}")
plt.plot(dd.depth_mm, dd.dose_Gy / dd.dose_Gy.max())
plt.xlabel("Depth in water (mm)")
plt.ylabel("Relative dose")
plt.title(path.name)
plt.savefig(path.with_suffix(".png"), dpi=150)
print("Saved", path.with_suffix(".png"))
