"""Leave-one-country-out check for test 1 (not pre-specified; robustness, 13 November 2026).

Re-estimates the main test 1 regression 27 times at each horizon, dropping one country each time, and
D = b1(48) - b1(12) on each reduced sample. Reports, for each horizon, the range of b1 and the dropped
country that moves it most.

Output: output/tables/test1_leave_one_out.csv
"""
import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("t1", ROOT / "code" / "08_test1.py")
T1 = importlib.util.module_from_spec(s)
s.loader.exec_module(T1)


def main():
    p = pd.read_csv(ROOT / "data" / "derived" / "panel_test1.csv")
    p = p[p.W_main_lc.notna()]
    rows = []
    for geo in ["none"] + sorted(p.geo.unique()):
        b1 = {}
        for h in sorted(p.h.unique()):
            d = p[(p.h == h) & (p.geo != geo)].set_index("geo")
            X, y = T1.design(d, "main", "lc")
            res = T1.fit(X, y)
            b1[h] = res.params["S_freeze"]
            rows.append({"dropped": geo, "h": h, "b1": res.params["S_freeze"], "se_hc3": res.bse["S_freeze"],
                         "n": int(res.nobs)})
        rows.append({"dropped": geo, "h": "D", "b1": b1[48] - b1[12], "se_hc3": float("nan"), "n": int(res.nobs)})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "output" / "tables" / "test1_leave_one_out.csv", index=False)
    full = out[out.dropped == "none"].set_index("h").b1
    loo = out[out.dropped != "none"]
    for h, g in loo.groupby("h", sort=False):
        far = g.loc[(g.b1 - full[h]).abs().idxmax()]
        print(f"h={h}: full {full[h]:+.1f}; leave-one-out range {g.b1.min():+.1f} to {g.b1.max():+.1f}; "
              f"largest change when dropping {far.dropped} ({far.b1:+.1f})")


if __name__ == "__main__":
    main()
