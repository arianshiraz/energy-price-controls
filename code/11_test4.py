"""Test 4, the 2026 shock (research design, section 6, test 4; Amendments 1 to 3). Early evidence.

Base month: the month before the first month in 2026 in which the European gas price (World Bank,
monthly, as published in USD) exceeds its average over the previous 12 months by 50% or more.
Tests 1 and 2 are run at the pre-specified horizons the data allow at the time of estimation
(HICP to 2026-09 on 12 November 2026). Test 3 (core) is run alongside test 1.

Outputs: output/tables/test4_base_month.csv, test4_test1_coefficients.csv, test4_events.csv
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB, DER = ROOT / "output" / "tables", ROOT / "data" / "derived"


def load(name, file):
    s = importlib.util.spec_from_file_location(name, ROOT / "code" / file)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def main():
    chk = subprocess.run([sys.executable, str(ROOT / "code" / "05_freeze_regimes.py"), "check"], capture_output=True, text=True)
    if chk.returncode:
        raise SystemExit(chk.stdout + chk.stderr)
    P = load("panel", "07_build_panel.py")
    x = pd.read_excel(P.RAW / "worldbank" / "CMO-Historical-Data-Monthly_20261112.xlsx", "Monthly Prices", header=None)
    col = x.iloc[4].astype(str).tolist().index("Natural gas, Europe")
    g = pd.Series(pd.to_numeric(x.iloc[6:, col], errors="coerce").values,
                  index=x.iloc[6:, 0].astype(str).str[:4] + "-" + x.iloc[6:, 0].astype(str).str[5:7])
    ratio = g / g.shift(1).rolling(12).mean()
    first = ratio.loc["2026-01":][ratio.loc["2026-01":] >= 1.5].index.min()
    base = str(pd.Period(first, "M") - 1)
    TAB.mkdir(parents=True, exist_ok=True)
    # The World Bank price itself is not written out (third-party, partly Bloomberg-sourced; Amendment 4)
    pd.DataFrame({"month": ratio.loc["2025-10":].index,
                  "ratio_to_prev12_mean": ratio.loc["2025-10":].values}).assign(first_month_ge_1_5=first, base_month=base) \
        .to_csv(TAB / "test4_base_month.csv", index=False)
    print("first month >= 1.5:", first, "| base month:", base)

    last_hicp = "2026-09"
    horizons = [h for h in (6, 12, 24, 36, 48) if str(pd.Period(base, "M") + h + 1) <= "2026-10"
                and str(pd.Period(base, "M") + h) <= last_hicp]
    print("horizons available:", horizons)
    P.BASE, P.HORIZONS = base, horizons
    P.main(suffix="_2026")

    T1 = load("test1", "08_test1.py")
    panel = pd.read_csv(DER / "panel_test1_2026.csv")
    rows = []
    for label, kw in [("main", {}), ("gas_all (04.5.2)", {"spec": "gas_all"}), ("euros", {"cur": "eur"}),
                      ("without special flags", {"drop": lambda d: d.share_special_main > 0})]:
        c, _ = T1.run(panel, label, **kw)
        rows.append(c)
    c, _ = T1.run(panel, "test 3: core inflation", outcome="y_core")
    rows.append(c)
    pd.concat(rows).assign(base_month=base).to_csv(TAB / "test4_test1_coefficients.csv", index=False)

    T2 = load("test2", "09_test2.py")
    ev = T2.events()
    ev = ev[ev.month > base]
    ev.to_csv(TAB / "test4_events.csv", index=False)
    print(f"test 2 events after {base}: {len(ev)}", ev[["country", "product", "month", "type"]].values.tolist())
    print("saved test4 tables")


if __name__ == "__main__":
    main()
