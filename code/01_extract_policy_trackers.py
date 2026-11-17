"""Extract the Bruegel policy trackers into measure-level tables used as the checklist for coding regimes.

Inputs (data/raw/bruegel/, see data/raw/README.md):
  bruegel_2021_2023_methodology_figure1_20230731.xlsx  one sheet per country
  bruegel_2026_policy_list_20260616.xlsx               sheet "Measures"
Outputs (data/classification/):
  tracker_measures_2021_2023.csv, tracker_measures_2026.csv
Each row keeps the tracker's own wording. `candidate` marks household price measures that touch
electricity or gas, which the coding rule must examine; nothing here is a regime code.
"""
import re
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "bruegel"
OUT = ROOT / "data" / "classification"
ENERGY = re.compile(r"electric|power|gas|energy|tariff|bill|vat|excise|levy|ticfe|eeg|price cap|price brake|tax", re.I)
FUEL_ONLY = re.compile(r"fuel discount|petrol|diesel|motor fuel|gasoline|mileage|transport|freight", re.I)


def date_or_text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    return str(v).strip()


def tracker_2021_2023():
    wb = openpyxl.load_workbook(RAW / "bruegel_2021_2023_methodology_figure1_20230731.xlsx", read_only=True, data_only=True)
    rows = []
    for ws in wb.worksheets:
        if ws.title in ("Index", "Methodology"):
            continue
        header = None
        for r in ws.iter_rows(values_only=True, max_row=400):
            cells = [c for c in r]
            if header is None:
                if cells and str(cells[0]).strip() == "Measure":
                    header = [str(c).strip() if c is not None else "" for c in cells]
                continue
            if not cells or cells[0] is None or str(cells[0]).strip() == "":
                continue
            name = str(cells[0]).strip()
            if name.upper().startswith(("TOTAL", "PLEASE NOTE")):
                continue
            rec = {h: cells[i] if i < len(cells) else None for i, h in enumerate(header) if h}
            sources = [date_or_text(rec[h]) for h in header if h.lower().startswith("source") and rec.get(h) is not None]
            rows.append({
                "country": ws.title.strip(),
                "measure": re.sub(r"\s+", " ", name),
                "households": date_or_text(rec.get("HH")),
                "firms": date_or_text(rec.get("Firms")),
                "targeted": date_or_text(rec.get("Targeted")),
                "price": date_or_text(rec.get("Price")),
                "income": date_or_text(rec.get("Income")),
                "budget_eur_m": date_or_text(rec.get("Allocated budget (mm €)")),
                "start": date_or_text(rec.get("Date of roll out (start date)")),
                "end": date_or_text(rec.get("Date of roll out (end date)")),
                "announced": date_or_text(rec.get("Date of announcement")),
                "sources": " ; ".join(s for s in sources if s and s.lower() != "nan"),
            })
    d = pd.DataFrame(rows)
    d["candidate"] = ((d.households.str.lower() == "yes") & (d.price.str.lower() == "yes")
                      & d.measure.str.contains(ENERGY) & ~d.measure.str.contains(FUEL_ONLY)).astype(int)
    return d


def tracker_2026():
    d = pd.read_excel(RAW / "bruegel_2026_policy_list_20260616.xlsx", sheet_name="Measures", dtype=str).fillna("")
    d.columns = [c.strip() for c in d.columns]
    d = d[d.Country.str.strip() != ""].copy()
    d["candidate"] = (d["Energy carrier"].str.contains("Electric|Gas|Mixed", case=False)
                      & ~d["Target Group"].str.contains("Transport|industry|Non-household", case=False)
                      & ~d["Specific Measure Type"].str.contains("Non-household", case=False)).astype(int)
    return d


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    a = tracker_2021_2023()
    a.to_csv(OUT / "tracker_measures_2021_2023.csv", index=False, encoding="utf-8")
    b = tracker_2026()
    b.to_csv(OUT / "tracker_measures_2026.csv", index=False, encoding="utf-8")
    print("2021-2023:", len(a), "measures,", a.candidate.sum(), "candidates,", a.country.nunique(), "countries")
    print("2026:", len(b), "measures,", b.candidate.sum(), "candidates,", b.Country.nunique(), "countries")
    print(a[a.candidate == 1].groupby("country").size().to_string())
