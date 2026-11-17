"""Build data/project_data_workbook.xlsx: every dataset used, with source, date and evidence level.

One sheet per dataset. Values taken from a source are blue; Excel formulas are black. Each data
sheet starts with three lines giving the source, the download or read date and the evidence level,
then the table. After saving, the workbook is recalculated in Excel through COM automation and
scanned for formula errors; the script stops if any are found.

Run: py -3 code/06_build_workbook.py   (needs Excel and pywin32)
"""
import csv
from datetime import date
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLS = ROOT / "data" / "classification"
OUT = ROOT / "data" / "project_data_workbook.xlsx"
FONT, BLUE, BLACK = "Arial", "0000FF", "000000"
HEAD_FILL = PatternFill("solid", start_color="1F3864")
DL = "12 November 2026"
MMBTU_PER_MWH = 3.412142  # 1 MWh = 3.412142 MMBtu (conversion constant, stated in the sheet)


def header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="top")


def meta(ws, source, when, evidence):
    for i, (k, v) in enumerate([("Source", source), ("Date", when), ("Evidence", evidence)], start=1):
        ws.cell(row=i, column=1, value=k).font = Font(name=FONT, bold=True)
        ws.cell(row=i, column=2, value=v).font = Font(name=FONT, italic=True)
    return 5  # header row


def table(ws, df, start=None, widths=None, wrap=None, urls=None, formula_cols=None):
    """Write df with its header at row `start`; source values blue, formula columns black."""
    start = start or 1
    formula_cols = formula_cols or set()
    for c, col in enumerate(df.columns, start=1):
        ws.cell(row=start, column=c, value=col)
    header(ws, start, len(df.columns))
    for r, row in enumerate(df.itertuples(index=False), start=start + 1):
        for c, v in enumerate(row, start=1):
            if isinstance(v, float) and pd.isna(v):
                v = None
            cell = ws.cell(row=r, column=c, value=v)
            col = df.columns[c - 1]
            cell.font = Font(name=FONT, color=BLACK if col in formula_cols else BLUE)
            if wrap and col in wrap:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            if urls and col in urls and isinstance(v, str) and v.startswith("http"):
                cell.hyperlink = v
                cell.font = Font(name=FONT, color=BLUE, underline="single")
    for c, col in enumerate(df.columns, start=1):
        ws.column_dimensions[get_column_letter(c)].width = (widths or {}).get(col, 14)
    ws.freeze_panes = ws.cell(row=start + 1, column=1)
    ws.auto_filter.ref = f"A{start}:{get_column_letter(len(df.columns))}{start + len(df)}"


def eurostat(path, item_col):
    d = pd.read_csv(path)
    d = d[["geo", item_col, "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG"]].rename(
        columns={item_col: "item", "TIME_PERIOD": "period", "OBS_VALUE": "value", "OBS_FLAG": "flag"})
    return d.sort_values(["item", "geo", "period"]).reset_index(drop=True)


def readme(wb, sheets):
    ws = wb.active
    ws.title = "README"
    lines = [("Do Energy Price Controls Prevent Inflation or Postpone It? Data workbook", True),
             (f"Built {date.today().isoformat()} by code/06_build_workbook.py from data/raw and data/classification. "
              "Do not edit by hand; edit the sources and rebuild.", False),
             ("The coded regimes were frozen on 12 November 2026 (data/classification/freeze_manifest.csv) before the "
              "price series were downloaded.", False),
             ("", False), ("Legend", True),
             ("Blue text: values taken from a source. Black text: Excel formulas.", False),
             ("Evidence 'primary': the statistical office, regulator or data provider's own file or document. "
              "'secondary': summaries, still to confirm.", False),
             ("", False), ("Sheets", True)]
    for text, bold in lines:
        ws.append([text])
        ws.cell(row=ws.max_row, column=1).font = Font(name=FONT, bold=bold, size=12 if bold else 10)
    for name, desc in sheets:
        ws.append([name, desc])
        ws.cell(row=ws.max_row, column=1).font = Font(name=FONT, bold=True)
        ws.cell(row=ws.max_row, column=2).font = Font(name=FONT)
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 120


def sources(wb):
    s = pd.DataFrame([
        ("Bruegel 2021-2023 tracker", "bruegel/bruegel_2021_2023_methodology_figure1_20230731.xlsx", "https://www.bruegel.org/system/files/2023-07/Methodology%20Figure%201%20-%20with%20split_31%20July%2023.xlsx", "2026-11-08", "secondary", "Policy checklist; codes rest on national sources"),
        ("Bruegel 2026 tracker", "bruegel/bruegel_2026_policy_list_20260616.xlsx", "https://www.bruegel.org/sites/default/files/2026-06/policy_list_20260616.xlsx", "2026-11-08", "secondary", "Policy checklist"),
        ("Eurostat HICP, ECOICOP", "eurostat/prc_hicp_midx_I15_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_midx/default/table", "2026-11-12", "primary", "Index 2015=100, 2019-01 to 2025-12"),
        ("Eurostat HICP, COICOP 2018", "eurostat/prc_hicp_minr_I15_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr/default/table", "2026-11-12", "primary", "Index 2015=100, 2019-01 to 2026-09"),
        ("Eurostat HICP gas split", "eurostat/prc_hicp_m*_I15_gas_split_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr/default/table", "2026-11-12", "primary", "CP04521 natural gas, CP04522 LPG"),
        ("Eurostat HICP item weights", "eurostat/prc_hicp_inw*_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_inw/default/table", "2026-11-12", "primary", "Per mille, 2019 to 2025"),
        ("Eurostat national currencies", "eurostat/ert_bil_eur_m_national_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/ert_bil_eur_m/default/table", "2026-11-12", "primary", "CZK, DKK, GBP, HUF, ISK, NOK, PLN, RON, SEK per EUR, monthly average"),
        ("ECB BGN and HRK", "ecb/EXR_M_BGN_HRK_EUR_SP00_A_20261112.csv", "https://data.ecb.europa.eu/data/datasets/EXR", "2026-11-12", "primary", "BGN to 2025-12, HRK to 2022-12, per EUR, monthly average"),
        ("Eurostat EUR/USD", "eurostat/ert_bil_eur_m_USD_20261112.csv", "https://ec.europa.eu/eurostat/databrowser/view/ert_bil_eur_m/default/table", "2026-11-12", "primary", "Monthly average, USD per EUR"),
        ("ONS MM23", "ons/mm23_20261112.csv", "https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindices", "2026-11-12", "primary", "UK CPI series and weights"),
        ("Ember wholesale prices", "ember/european_wholesale_electricity_price_data_monthly_20261112.csv", "https://ember-energy.org/data/european-wholesale-electricity-price-data/", "2026-11-12", "primary", "Day-ahead EUR/MWh, monthly"),
        ("World Bank Pink Sheet", "worldbank/CMO-Historical-Data-Monthly_20261112.xlsx", "https://www.worldbank.org/en/research/commodity-markets", "2026-11-12", "primary", "Natural gas, Europe, USD/mmbtu"),
    ], columns=["dataset", "file (data/raw/)", "url", "downloaded", "evidence", "note"])
    table(wb.create_sheet("Sources"), s, widths={"dataset": 28, "file (data/raw/)": 60, "url": 60, "note": 40},
          urls={"url"})


def hicp_sheet(wb, name, path, item_col, source, note):
    ws = wb.create_sheet(name)
    h = meta(ws, f"{source}. {note}", f"Downloaded {DL}", "primary (Eurostat API, SDMX-CSV)")
    table(ws, eurostat(path, item_col), start=h, widths={"item": 16, "period": 10})


def ons(wb):
    raw = list(csv.reader(open(RAW / "ons" / "mm23_20261112.csv", encoding="utf-8", errors="replace")))
    titles, cdids = raw[0], raw[1]
    keep = ["D7BT", "D7DT", "D7DU", "L7E9", "DK9T", "DKC6"]
    idx = [cdids.index(k) for k in keep]
    months = [r for r in raw if len(r[0]) == 8 and r[0][:4].isdigit() and r[0][4] == " " and int(r[0][:4]) >= 2019]
    mo = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
    rows = [[f"{r[0][:4]}-{mo[r[0][5:]]:02d}"] + [float(r[i]) if r[i] not in ("", "x") else None for i in idx] for r in months]
    df = pd.DataFrame(rows, columns=["period"] + [f"{k} {titles[i]}" for k, i in zip(keep, idx)])
    ws = wb.create_sheet("ONS_UK_CPI")
    h = meta(ws, "ONS, Consumer price inflation time series (MM23), full dataset mm23.csv; series named by CDID",
             f"Downloaded {DL}", "primary (ONS)")
    table(ws, df, start=h, widths={c: 22 for c in df.columns})
    wkeep = ["CJXA", "CJXB", "L89X"]
    widx = [cdids.index(k) for k in wkeep]
    years = [r for r in raw if len(r[0]) == 4 and r[0].isdigit() and int(r[0]) >= 2019]
    wd = pd.DataFrame([[int(r[0])] + [float(r[i]) if r[i] not in ("", "x") else None for i in widx] for r in years],
                      columns=["year"] + [f"{k} {titles[i]}" for k, i in zip(wkeep, widx)])
    ws2 = wb.create_sheet("ONS_UK_Weights")
    h = meta(ws2, "ONS MM23, CPI item weights (parts per 1,000)", f"Downloaded {DL}", "primary (ONS)")
    table(ws2, wd, start=h, widths={c: 26 for c in wd.columns})


def ember(wb):
    d = pd.read_csv(RAW / "ember" / "european_wholesale_electricity_price_data_monthly_20261112.csv")
    d["period"] = d["Date"].str[:7]
    w = d[d.period >= "2019-01"].pivot(index="period", columns="ISO3 Code", values="Price (EUR/MWhe)").reset_index()
    ws = wb.create_sheet("Ember_Wholesale")
    h = meta(ws, "Ember, European wholesale electricity price data, monthly day-ahead price (EUR/MWh), one column per country (ISO3)",
             f"Downloaded {DL}; latest month partial", "primary (Ember)")
    table(ws, w, start=h, widths={"period": 10})


def gas(wb):
    """World Bank European gas price: source details only. The values are not redistributed (the series is
    partly sourced from Bloomberg Finance L.P.; Amendment 4). code/07_build_panel.py reads them from the
    downloaded file listed in data/raw/README.md."""
    fx = pd.read_csv(RAW / "eurostat" / "ert_bil_eur_m_USD_20261112.csv")[["TIME_PERIOD", "OBS_VALUE"]]
    fx.columns = ["period", "usd_per_eur"]
    fx = fx[fx.period >= "2019-01"].reset_index(drop=True)
    ws = wb.create_sheet("WB_Gas_Europe")
    h = meta(ws, "World Bank Pink Sheet, 'Natural gas, Europe' (USD/mmbtu), updated 3 November 2026. Values not included: "
                 "the series lists Bloomberg Finance L.P. among its sources. Download CMO-Historical-Data-Monthly.xlsx "
                 "(data/raw/README.md) to rebuild. EUR/USD monthly average from Eurostat ert_bil_eur_m is shown.",
             f"Downloaded {DL}", "primary (World Bank; Eurostat)")
    table(ws, fx, start=h, widths={"period": 10, "usd_per_eur": 12})


def fx(wb):
    """National currency per EUR, monthly averages (Amendment 3). BGN and HRK from the ECB; after euro
    adoption (HRK from 2023-01, BGN from 2026-01) the irrevocable conversion rate continues the series."""
    e = pd.read_csv(RAW / "eurostat" / "ert_bil_eur_m_national_20261112.csv")[["currency", "TIME_PERIOD", "OBS_VALUE"]]
    b = pd.read_csv(RAW / "ecb" / "EXR_M_BGN_HRK_EUR_SP00_A_20261112.csv")[["CURRENCY", "TIME_PERIOD", "OBS_VALUE"]]
    b.columns = e.columns
    w = pd.concat([e, b]).pivot(index="TIME_PERIOD", columns="currency", values="OBS_VALUE").reset_index()
    w = w.rename(columns={"TIME_PERIOD": "period"})
    w = w[w.period <= "2026-10"].reset_index(drop=True)
    ws = wb.create_sheet("FX_National")
    h = meta(ws, "National currency per EUR, monthly average: Eurostat ert_bil_eur_m (CZK, DKK, GBP, HUF, ISK, NOK, PLN, RON, SEK); "
                 "ECB EXR M.BGN+HRK.EUR.SP00.A (BGN to 2025-12, HRK to 2022-12)",
             f"Downloaded {DL}", "primary (Eurostat; ECB)")
    rows = range(h + 1, h + 1 + len(w))
    conv = {"BGN": "$P$2", "HRK": "$P$3"}
    cols = list(w.columns)
    for cur, ref in conv.items():
        cl = get_column_letter(cols.index(cur) + 1)
        w[f"{cur}_continued"] = [f'=IF({cl}{r}="",{ref},{cl}{r})' for r in rows]
    table(ws, w, start=h, formula_cols={"BGN_continued", "HRK_continued"}, widths={"period": 10})
    for cell, val, blue in [("O2", "BGN per EUR, irrevocable rate (euro from 1 January 2026)", False), ("P2", 1.95583, True),
                            ("O3", "HRK per EUR, irrevocable rate (euro from 1 January 2023)", False), ("P3", 7.53450, True)]:
        ws[cell] = val
        ws[cell].font = Font(name=FONT, color=BLUE if blue else BLACK, bold=not blue)
    ws.column_dimensions["O"].width = 50


def coded(wb):
    for name, f, src in [("Regime_Measures", "regime_measures.csv", "Hand-coded from national legal texts, regulator decisions and government releases (columns source_url, source_ref)"),
                         ("Regime_Baseline", "regime_baseline.csv", "July 2021 regulation status; ACER/CEER 2021 retail report, Figure 48, and national regulators"),
                         ("Tracker_Reconciliation", "tracker_reconciliation.csv", "Every Bruegel tracker candidate with its disposition")]:
        d = pd.read_csv(CLS / f, dtype=str).fillna("")
        ws = wb.create_sheet(name)
        h = meta(ws, src, "Read 8 to 12 November 2026; frozen 12 November 2026",
                 "per row (column 'evidence'); rows with verified = no rest on secondary sources" if "evidence" in d.columns else "see source column")
        table(ws, d, start=h, wrap={"measure", "source_ref", "notes", "coverage_note", "reason"},
              widths={"measure": 50, "source_ref": 60, "notes": 60, "source_url": 40, "coverage_note": 40, "reason": 60, "regime_rows": 40},
              urls={"source_url"})


def coverage(wb):
    """Observation counts by country and item, as COUNTIFS formulas over the HICP sheets."""
    geos = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU",
            "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "IS"]
    items = ["CP0451", "CP0452", "NRG", "TOT_X_NRG_FOOD"]
    ws = wb.create_sheet("Coverage")
    meta(ws, "Counts of non-empty monthly values in HICP_ECOICOP (to 2025-12) and HICP_COICOP2018 (to 2026-09)",
         "Formulas over the data sheets", "derived")
    cols = ["geo"] + [f"ECOICOP {i}" for i in items] + [f"COICOP2018 {i}" for i in items]
    for c, col in enumerate(cols, start=1):
        ws.cell(row=5, column=c, value=col)
    header(ws, 5, len(cols))
    for r, g in enumerate(geos, start=6):
        ws.cell(row=r, column=1, value=g).font = Font(name=FONT, color=BLUE)
        for k, i in enumerate(items):
            for off, sh in [(2, "HICP_ECOICOP"), (2 + len(items), "HICP_COICOP2018")]:
                cell = ws.cell(row=r, column=off + k,
                               value=f'=COUNTIFS({sh}!$A:$A,$A{r},{sh}!$B:$B,"{i}",{sh}!$D:$D,"<>")')
                cell.font = Font(name=FONT, color=BLACK)
    for c in range(1, len(cols) + 1):
        ws.column_dimensions[get_column_letter(c)].width = 16


def recalc_and_check(path):
    import win32com.client
    xl = win32com.client.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        wb = xl.Workbooks.Open(str(path))
        xl.CalculateFull()
        wb.Save()
        wb.Close(SaveChanges=False)
    finally:
        xl.Quit()
    codes = {"#DIV/0!", "#N/A", "#NAME?", "#REF!", "#VALUE!", "#NUM!", "#NULL!"}
    errs, n = [], 0
    for ws in load_workbook(path, data_only=True).worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value in codes:
                    errs.append(f"{ws.title}!{c.coordinate}")
    for ws in load_workbook(path).worksheets:
        n += sum(1 for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("="))
    if errs:
        raise SystemExit(f"{len(errs)} formula errors, first: {errs[:10]}")
    print(f"recalculated in Excel: {n} formulas, 0 errors")


def main():
    sheets = [("Sources", "Every raw file: source, URL, download date, evidence level."),
              ("HICP_ECOICOP", "Eurostat prc_hicp_midx, index 2015=100: CP00, CP045, CP0451 electricity, CP0452 gas, NRG energy, TOT_X_NRG_FOOD; 2019-01 to 2025-12."),
              ("HICP_COICOP2018", "Eurostat prc_hicp_minr (COICOP 2018), same items with TOTAL for all items; 2019-01 to 2026-09."),
              ("HICP_GasSplit_ECOICOP", "CP04521 natural gas and town gas, CP04522 liquefied hydrocarbons (ECOICOP)."),
              ("HICP_GasSplit_COICOP2018", "The same split on COICOP 2018."),
              ("HICP_Weights", "Eurostat prc_hicp_inw item weights (per mille), CP045, CP0451, CP0452, NRG, 2019 to 2025."),
              ("HICP_Weights_GasSplit", "Item weights for CP04521 and CP04522."),
              ("ONS_UK_CPI", "UK CPI indices (2015=100): all items, electricity, gas, natural gas, energy, excluding energy, food, alcohol and tobacco."),
              ("ONS_UK_Weights", "UK CPI item weights for electricity, gas, natural gas."),
              ("Ember_Wholesale", "Monthly day-ahead wholesale electricity price by country (EUR/MWh)."),
              ("WB_Gas_Europe", "World Bank European natural gas price: source details only (values not redistributed); EUR/USD monthly average."),
              ("FX_National", "National currency per EUR, monthly, for the non-euro countries; BGN and HRK continued at the irrevocable rate after euro adoption (formulas)."),
              ("Regime_Measures", "The frozen coded measures (one row per measure)."),
              ("Regime_Baseline", "The frozen July 2021 baseline by country and product."),
              ("Tracker_Reconciliation", "Disposition of every Bruegel tracker candidate."),
              ("Coverage", "Observation counts per country and item (formulas).")]
    wb = Workbook()
    readme(wb, sheets)
    sources(wb)
    E = RAW / "eurostat"
    hicp_sheet(wb, "HICP_ECOICOP", E / "prc_hicp_midx_I15_20261112.csv", "coicop", "Eurostat prc_hicp_midx", "Index 2015=100 (unit I15)")
    hicp_sheet(wb, "HICP_COICOP2018", E / "prc_hicp_minr_I15_20261112.csv", "coicop18", "Eurostat prc_hicp_minr", "Index 2015=100 (unit I15), COICOP 2018")
    hicp_sheet(wb, "HICP_GasSplit_ECOICOP", E / "prc_hicp_midx_I15_gas_split_20261112.csv", "coicop", "Eurostat prc_hicp_midx", "CP04521 and CP04522")
    hicp_sheet(wb, "HICP_GasSplit_COICOP2018", E / "prc_hicp_minr_I15_gas_split_20261112.csv", "coicop18", "Eurostat prc_hicp_minr", "CP04521 and CP04522")
    hicp_sheet(wb, "HICP_Weights", E / "prc_hicp_inw_20261112.csv", "coicop", "Eurostat prc_hicp_inw", "Item weights, per mille")
    hicp_sheet(wb, "HICP_Weights_GasSplit", E / "prc_hicp_inw_gas_split_20261112.csv", "coicop", "Eurostat prc_hicp_inw", "Item weights, per mille")
    ons(wb)
    ember(wb)
    gas(wb)
    fx(wb)
    coded(wb)
    coverage(wb)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None and c.font.name != FONT:
                    c.font = Font(name=FONT, bold=c.font.bold, italic=c.font.italic, color=c.font.color)
    wb.save(OUT)
    print("saved", OUT)
    recalc_and_check(OUT)


if __name__ == "__main__":
    main()
