"""Expand coded measures into the country-product-month regime panel (docs/regime_coding_rule.md).

Input:  data/classification/regime_measures.csv   one row per measure (country, product, code, start, end, ...)
        data/classification/regime_baseline.csv   one row per country and product coded, with the R flag (regulated in July 2021)
Output: data/classification/regimes.csv           country, product, month, main_code, flags, sources
Main code by precedence 1 > 2 > 3 > 4 > 5 > 6 (rule section 2); every code in force is kept as a flag.
"""
from pathlib import Path

import pandas as pd

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"
FIRST, LAST = "2019-01", "2026-10"
PRODUCTS = ("electricity", "gas")


def months(a, b):
    return [str(p) for p in pd.period_range(a, b, freq="M")]


def main():
    m = pd.read_csv(CLS / "regime_measures.csv", dtype=str).fillna("")
    if "special_flags" not in m.columns:
        m["special_flags"] = ""
    base = pd.read_csv(CLS / "regime_baseline.csv", dtype=str).fillna("")
    for c in ("start_month", "end_month"):
        bad = m[~m[c].str.match(r"^\d{4}-\d{2}$") & (m[c] != "")]
        assert bad.empty, f"bad {c}: {bad[['country', 'measure', c]].to_dict('records')}"
    assert m.code.isin(list("12345")).all(), "codes must be 1 to 5"
    rows = []
    for _, b in base.iterrows():
        mm = m[(m.country == b.country) & (m["product"] == b["product"])]
        for mo in months(FIRST, LAST):
            live = mm[(mm.start_month <= mo) & ((mm.end_month == "") | (mm.end_month >= mo))]
            codes = sorted(set(live.code.astype(int)) | {6})  # regulated formulas (code 3) are rows in regime_measures
            rows.append({"country": b.country, "product": b["product"], "month": mo, "main_code": min(codes),
                         "flags": " ".join(str(c) for c in codes), "regulated_2021_07": b.regulated_2021_07,
                         "low_coverage": int(any((live.coverage_share != "") & (pd.to_numeric(live.coverage_share, errors="coerce") < 0.5))),
                         "unverified": int((live.verified != "yes").any()),
                         "special_flags": " ".join(sorted({f for x in live.special_flags for f in x.split()})),
                         "measures": " | ".join(live.measure)})
    out = pd.DataFrame(rows)
    out.to_csv(CLS / "regimes.csv", index=False)
    print(out.groupby(["country", "product", "main_code"]).size().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
