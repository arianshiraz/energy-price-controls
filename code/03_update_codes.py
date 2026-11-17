"""Apply a batch of checked updates to data/classification/regime_measures.csv.

Usage: py -3 code/03_update_codes.py updates.json
Each update is {"match": {"country":..., "product":..., "start_month":..., "code":...}, "set": {column: value, ...}}
or {"add": {full row}}. Every match must hit exactly one row; the script refuses otherwise.
Keeps an audit trail in data/classification/coding_log.csv (date, row key, columns changed, old and new values).
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"


def main(path):
    ups = json.loads(Path(path).read_text(encoding="utf-8"))
    m = pd.read_csv(CLS / "regime_measures.csv", dtype=str).fillna("")
    log = []
    today = dt.date.today().isoformat()
    for u in ups:
        if "add" in u:
            row = {c: "" for c in m.columns} | u["add"]
            m = pd.concat([m, pd.DataFrame([row])], ignore_index=True)
            log.append([today, "|".join(row[k] for k in ("country", "product", "start_month", "code")), "added", "", row["measure"]])
            continue
        sel = pd.Series(True, index=m.index)
        for k, v in u["match"].items():
            sel &= m[k] == v
        assert sel.sum() == 1, (u["match"], int(sel.sum()))
        i = m[sel].index[0]
        key = "|".join(m.at[i, k] for k in ("country", "product", "start_month", "code"))
        for k, v in u["set"].items():
            log.append([today, key, k, m.at[i, k], v])
            m.at[i, k] = v
    m.to_csv(CLS / "regime_measures.csv", index=False, encoding="utf-8")
    new = not (CLS / "coding_log.csv").exists()
    with open(CLS / "coding_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "row", "column", "old", "new"])
        w.writerows(log)
    print(f"applied {len(ups)} updates, {len(log)} changes")


if __name__ == "__main__":
    main(sys.argv[1])
