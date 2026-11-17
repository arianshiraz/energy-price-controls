"""Build the analysis panels for tests 1 to 3 (research design, section 6, with Amendments 1 to 3).

Inputs: the frozen coded regimes (checked against freeze_manifest.csv first) and the raw downloads of
12 November 2026. No regression is run here.

Outputs (data/derived/, not committed):
  panel_monthly.csv   country x month: price indices, wholesale prices, regime codes by product
  panel_test1.csv     country x horizon h in {6, 12, 24, 36, 48}: y, regime shares, W, R, flag shares

Definitions (section 6):
  base month July 2021 (h = 0); month h = July 2021 + h.
  y(c,h)   = w_e 100 ln(E_h/E_0) + w_g 100 ln(G_h/G_0); E electricity (04.5.1), G gas.
  S_k(c,h) = share of months 1..h with main code k, weighted over electricity and gas by w_e, w_g.
  W(c,h)   = w_e 100 ln(Pe_h/Pe_0) + w_g 100 ln(Pg_h/Pg_0), Pe and Pg as 3-month centred averages.
  R(c)     = 1 if household electricity or gas prices were regulated in July 2021.
  w_e, w_g = 2021 HICP item weights of electricity and gas, normalised to sum to one.
Specifications:
  main      gas = 04.5.2.1 natural gas (Amendment 3), wholesale prices in national currency
  gas_all   gas = 04.5.2 all gas (original design)
  eur       wholesale prices in euros for every country (Amendment 3 robustness)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLS, DER = ROOT / "data" / "raw", ROOT / "data" / "classification", ROOT / "data" / "derived"
BASE = "2021-07"
HORIZONS = [6, 12, 24, 36, 48]
LAST_ECOICOP = "2025-12"

GEO = {"Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ",
       "Denmark": "DK", "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE", "Greece": "EL",
       "Hungary": "HU", "Iceland": "IS", "Ireland": "IE", "Italy": "IT", "Latvia": "LV", "Lithuania": "LT",
       "Luxembourg": "LU", "Malta": "MT", "Netherlands": "NL", "Norway": "NO", "Poland": "PL", "Portugal": "PT",
       "Romania": "RO", "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES", "Sweden": "SE", "United Kingdom": "UK"}
ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP", "CZ": "CZE", "DK": "DNK", "EE": "EST",
        "FI": "FIN", "FR": "FRA", "DE": "DEU", "EL": "GRC", "HU": "HUN", "IS": "ISL", "IE": "IRL", "IT": "ITA",
        "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT",
        "RO": "ROU", "SK": "SVK", "SI": "SVN", "ES": "ESP", "SE": "SWE", "UK": "GBR"}
CURRENCY = {"BG": "BGN_continued", "HR": "HRK_continued", "CZ": "CZK", "DK": "DKK", "HU": "HUF", "IS": "ISK",
            "NO": "NOK", "PL": "PLN", "RO": "RON", "SE": "SEK", "UK": "GBP"}  # all others: euro
IRREVOCABLE = {"BGN": 1.95583, "HRK": 7.53450}


def months(a, b):
    return [str(p) for p in pd.period_range(a, b, freq="M")]


def month_plus(m, h):
    return str(pd.Period(m, freq="M") + h)


# ---------- prices ----------
def eurostat_indices():
    """Linked indices by geo and item: ECOICOP to 2025-12, then COICOP 2018 growth (linked at 2025-12)."""
    def load(f, col):
        d = pd.read_csv(RAW / "eurostat" / f)
        return d.rename(columns={col: "item"})[["geo", "item", "TIME_PERIOD", "OBS_VALUE"]]
    old = pd.concat([load("prc_hicp_midx_I15_20261112.csv", "coicop"),
                     load("prc_hicp_midx_I15_gas_split_20261112.csv", "coicop")])
    new = pd.concat([load("prc_hicp_minr_I15_20261112.csv", "coicop18"),
                     load("prc_hicp_minr_I15_gas_split_20261112.csv", "coicop18")])
    new["item"] = new["item"].replace({"TOTAL": "CP00"})
    o = old.pivot_table(index="TIME_PERIOD", columns=["geo", "item"], values="OBS_VALUE")
    n = new.pivot_table(index="TIME_PERIOD", columns=["geo", "item"], values="OBS_VALUE")
    out = o.loc[o.index <= LAST_ECOICOP].copy()
    tail = n.loc[n.index > LAST_ECOICOP]
    link = {}
    for c in out.columns:
        if c in n.columns and pd.notna(n.at[LAST_ECOICOP, c]) and pd.notna(out.at[LAST_ECOICOP, c]):
            link[c] = out.at[LAST_ECOICOP, c] / n.at[LAST_ECOICOP, c]
    ext = pd.DataFrame({c: tail[c] * f for c, f in link.items()}, index=tail.index)
    return pd.concat([out, ext]), link


def eurostat_weights():
    w = pd.concat([pd.read_csv(RAW / "eurostat" / f) for f in
                   ("prc_hicp_inw_20261112.csv", "prc_hicp_inw_gas_split_20261112.csv")])
    w = w[w.TIME_PERIOD == 2021]
    return w.pivot_table(index="geo", columns="coicop", values="OBS_VALUE")


def ons():
    import csv
    raw = list(csv.reader(open(RAW / "ons" / "mm23_20261112.csv", encoding="utf-8", errors="replace")))
    cd = raw[1]
    mo = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
    keep = {"D7DT": "CP0451", "D7DU": "CP0452", "L7E9": "CP04521", "D7BT": "CP00", "DK9T": "NRG", "DKC6": "TOT_X_NRG_FOOD"}
    idx = {k: cd.index(k) for k in keep}
    rows = {}
    for r in raw:
        if len(r[0]) == 8 and r[0][:4].isdigit() and r[0][4] == " " and int(r[0][:4]) >= 2019:
            rows[f"{r[0][:4]}-{mo[r[0][5:]]:02d}"] = {keep[k]: float(r[i]) if r[i] not in ("", "x") else np.nan for k, i in idx.items()}
    ind = pd.DataFrame(rows).T.sort_index()
    wrow = [r for r in raw if r[0] == "2021"][0]
    wts = {"CP0451": float(wrow[cd.index("CJXA")]), "CP0452": float(wrow[cd.index("CJXB")]),
           "CP04521": float(wrow[cd.index("L89X")])}
    return ind, wts


# ---------- wholesale ----------
def wholesale():
    e = pd.read_csv(RAW / "ember" / "european_wholesale_electricity_price_data_monthly_20261112.csv")
    e["period"] = e["Date"].str[:7]
    pe = e.pivot(index="period", columns="ISO3 Code", values="Price (EUR/MWhe)")
    x = pd.read_excel(RAW / "worldbank" / "CMO-Historical-Data-Monthly_20261112.xlsx", "Monthly Prices", header=None)
    col = x.iloc[4].astype(str).tolist().index("Natural gas, Europe")
    g = pd.Series(pd.to_numeric(x.iloc[6:, col], errors="coerce").values,
                  index=x.iloc[6:, 0].astype(str).str[:4] + "-" + x.iloc[6:, 0].astype(str).str[5:7])
    usd = pd.read_csv(RAW / "eurostat" / "ert_bil_eur_m_USD_20261112.csv").set_index("TIME_PERIOD")["OBS_VALUE"]
    pg_eur = (g / usd).dropna()  # EUR per MMBtu; the unit cancels in log changes
    fx = pd.read_csv(RAW / "eurostat" / "ert_bil_eur_m_national_20261112.csv").pivot(
        index="TIME_PERIOD", columns="currency", values="OBS_VALUE")
    b = pd.read_csv(RAW / "ecb" / "EXR_M_BGN_HRK_EUR_SP00_A_20261112.csv").pivot(
        index="TIME_PERIOD", columns="CURRENCY", values="OBS_VALUE")
    fx = fx.join(b, how="outer")
    for cur, rate in IRREVOCABLE.items():
        fx[f"{cur}_continued"] = fx[cur].fillna(rate)
    return pe, pg_eur, fx


def centred(s):
    return s.rolling(3, center=True, min_periods=3).mean()


# ---------- regimes ----------
def regimes():
    r = pd.read_csv(CLS / "regimes.csv", dtype=str).fillna("")
    r["main_code"] = r.main_code.astype(int)
    return r


def main(suffix=""):
    """suffix names the output files; test 4 sets BASE and HORIZONS and passes '_2026'."""
    chk = subprocess.run([sys.executable, str(ROOT / "code" / "05_freeze_regimes.py"), "check"], capture_output=True, text=True)
    if chk.returncode:
        raise SystemExit(chk.stdout + chk.stderr)
    print(chk.stdout.strip())
    DER.mkdir(parents=True, exist_ok=True)

    hicp, link = eurostat_indices()
    wts = eurostat_weights()
    uk_ind, uk_w = ons()
    pe, pg_eur, fx = wholesale()
    reg = regimes()
    base_reg = pd.read_csv(CLS / "regime_baseline.csv", dtype=str).fillna("")

    span = months("2019-01", "2026-10")
    monthly, cross = [], []
    for name, geo in GEO.items():
        # price indices
        def series(item):
            if geo == "UK":
                return uk_ind[item].reindex(span) if item in uk_ind else pd.Series(np.nan, index=span)
            return hicp[(geo, item)].reindex(span) if (geo, item) in hicp.columns else pd.Series(np.nan, index=span)
        E, Gn, Ga = series("CP0451"), series("CP04521"), series("CP0452")
        core, head = series("TOT_X_NRG_FOOD"), series("CP00")
        wsrc = uk_w if geo == "UK" else (wts.loc[geo].to_dict() if geo in wts.index else {})

        coded_gas = bool((reg.country == name).loc[reg["product"] == "gas"].any())

        def weights(gitem, G, need_coded):
            we = wsrc.get("CP0451", np.nan)
            wg = wsrc.get(gitem, np.nan) if G.notna().any() else 0.0
            if not np.isfinite(wg) or wg <= 0 or G.isna().all() or (need_coded and not coded_gas):
                return 1.0, 0.0
            return we / (we + wg), wg / (we + wg)
        # main: piped gas only where the coding has a household gas series (not Cyprus, Malta, Sweden, Finland,
        # Norway, Iceland); gas_all: any 04.5.2 index, with gas uncoded countries treated as code 6 (no control)
        we_n, wg_n = weights("CP04521", Gn, need_coded=True)
        we_a, wg_a = weights("CP0452", Ga, need_coded=False)

        # wholesale, national currency and euro
        iso = ISO3[geo]
        rate = fx[CURRENCY[geo]].reindex(span) if geo in CURRENCY else pd.Series(1.0, index=span)
        pe_eur = pe[iso].reindex(span) if iso in pe.columns else pd.Series(np.nan, index=span)
        pg = pg_eur.reindex(span)
        Pe = {"lc": centred(pe_eur * rate), "eur": centred(pe_eur)}
        Pg = {"lc": centred(pg * rate), "eur": centred(pg)}

        # regimes by product
        rc = reg[reg.country == name].set_index(["product", "month"])
        prods = sorted(reg[reg.country == name]["product"].unique())
        R = int((base_reg[base_reg.country == name].regulated_2021_07 == "1").any())

        for m in span:
            row = {"country": name, "geo": geo, "month": m, "E": E[m], "G_natural": Gn[m], "G_all": Ga[m],
                   "core": core[m], "headline": head[m], "pe_eur": pe_eur[m], "pg_eur": pg[m], "fx_lc_per_eur": rate[m]}
            for p in ("electricity", "gas"):
                row[f"code_{p}"] = int(rc.at[(p, m), "main_code"]) if (p, m) in rc.index else np.nan
            monthly.append(row)

        def lnch(s, h):
            a, b = s.get(BASE), s.get(month_plus(BASE, h))
            return 100 * np.log(b / a) if pd.notna(a) and pd.notna(b) and a > 0 and b > 0 else np.nan

        def share(p, h, test):
            if p not in prods:
                return 0.0  # product not coded for this country: no control (code 6) in every month
            ms = months(month_plus(BASE, 1), month_plus(BASE, h))
            sub = rc.loc[p].reindex(ms)
            return float(test(sub).mean())

        for h in HORIZONS:
            rec = {"country": name, "geo": geo, "h": h, "month_h": month_plus(BASE, h), "R": R,
                   "has_gas_natural": int(wg_n > 0), "has_gas_all": int(wg_a > 0),
                   "w_e": we_n, "w_g": wg_n, "w_e_all": we_a, "w_g_all": wg_a,
                   "has_wholesale": int(pd.notna(Pe["lc"].get(BASE)) and pd.notna(Pe["lc"].get(month_plus(BASE, h))))}
            for spec, (we, wg, G) in {"main": (we_n, wg_n, Gn), "gas_all": (we_a, wg_a, Ga)}.items():
                rec[f"y_{spec}"] = we * lnch(E, h) + (wg * lnch(G, h) if wg > 0 else 0.0)
                for cur in ("lc", "eur"):
                    rec[f"W_{spec}_{cur}"] = we * lnch(Pe[cur], h) + (wg * lnch(Pg[cur], h) if wg > 0 else 0.0)
                for k, lab in [(1, "freeze"), (2, "quantity"), (3, "lagged"), (4, "tax"), (5, "transfer")]:
                    se = share("electricity", h, lambda s: s.main_code == k)
                    sg = share("gas", h, lambda s: s.main_code == k) if wg > 0 else 0.0
                    rec[f"S_{lab}_{spec}"] = we * se + (wg * sg if wg > 0 else 0.0)
                for flag, test in [("unverified", lambda s: s.unverified == "1"), ("lowcov", lambda s: s.low_coverage == "1"),
                                   ("special", lambda s: s.special_flags != "")]:
                    se = share("electricity", h, test)
                    sg = share("gas", h, test) if wg > 0 else 0.0
                    rec[f"share_{flag}_{spec}"] = we * se + (wg * sg if wg > 0 else 0.0)
            rec["y_core"] = lnch(core, h)
            rec["y_headline"] = lnch(head, h)
            cross.append(rec)

    pd.DataFrame(monthly).to_csv(DER / f"panel_monthly{suffix}.csv", index=False)
    t1 = pd.DataFrame(cross)
    t1.to_csv(DER / f"panel_test1{suffix}.csv", index=False)
    pd.Series(link).rename("ecoicop_over_coicop18_at_2025_12").to_csv(DER / "hicp_link_factors.csv")
    print(f"panel_monthly: {len(monthly)} rows; panel_test1: {len(t1)} rows; link factors: {len(link)}")


if __name__ == "__main__":
    main()
