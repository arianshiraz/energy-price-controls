"""Test 2, catch-up at exits and step-ups (research design, section 6, test 2; Amendments 1 to 3).

Events (coding rule, section 3): the ends of codes 1 to 3 and the dated scheduled increases (step_ups)
in controlled prices, separately for electricity and gas. An exit occurs in month t when a code 1-3
measure ended in t-1 and the strongest control in force in t is weaker (higher main code); a code 3
row that is followed by another code 3 row is a relabelling, not an exit.

Outcome: monthly change in 100 ln of the price index minus the change predicted by wholesale prices.
Prediction: pooled OLS of the monthly change on a constant and lags 0 to 12 of the monthly change in
100 ln of the wholesale price (electricity: the country's day-ahead price; gas: the European price),
in national currency (Amendment 3), estimated on country-months with main code 5 or 6 only.

Event study: window -3 to +6 months, reference month -1, pooled across events with event fixed effects,
standard errors clustered by country. P2: positive excess change in months 0, 1 and 2.

Implementation choices fixed before running: where two controls end in the same month the event is
labelled with the stronger (lower) code; windows are kept when they run past the last month of data
(unbalanced); specifications: main, all gas (04.5.2) and euros; an exploratory split into exits and
step-ups is labelled as such.

Outputs: output/tables/test2_events.csv, test2_passthrough.csv, test2_eventstudy.csv
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
CLS, TAB = ROOT / "data" / "classification", ROOT / "output" / "tables"
spec7 = importlib.util.spec_from_file_location("panel", ROOT / "code" / "07_build_panel.py")
P = importlib.util.module_from_spec(spec7)
spec7.loader.exec_module(P)

WIN = range(-3, 7)
SPAN = P.months("2015-01", "2026-10")
LAST = "2026-10"


def events():
    m = pd.read_csv(CLS / "regime_measures.csv", dtype=str).fillna("")
    r = pd.read_csv(CLS / "regimes.csv", dtype=str).fillna("")
    mc = r.assign(main_code=r.main_code.astype(int)).set_index(["country", "product", "month"]).main_code
    ev = []
    for _, x in m[m.code.isin(["1", "2", "3"]) & (m.end_month != "")].iterrows():
        t = str(pd.Period(x.end_month, "M") + 1)
        if t > LAST:
            continue
        k, now = int(x.code), mc.get((x.country, x["product"], t))
        if now is not None and now > k:
            ev.append({"country": x.country, "product": x["product"], "month": t, "type": "exit", "code": k,
                       "code_after": int(now), "measure": x.measure})
    for _, x in m[m.step_ups != ""].iterrows():
        for s in x.step_ups.split(";"):
            ev.append({"country": x.country, "product": x["product"], "month": s.split(":")[0].strip(), "type": "step-up",
                       "code": int(x.code), "code_after": np.nan, "measure": f"{x.measure} ({s.strip()})"})
    e = pd.DataFrame(ev).sort_values(["country", "product", "month", "code"])
    e = e.drop_duplicates(["country", "product", "month", "type"], keep="first").reset_index(drop=True)
    e["event_id"] = [f"{c}|{p}|{mo}|{t}" for c, p, mo, t in zip(e.country, e["product"], e.month, e.type)]
    return e


def monthly(gas_item, cur):
    """Country-product-month table: d100ln index, d100ln wholesale lags 0-12, main code."""
    hicp, _ = P.eurostat_indices()
    uk_ind, _ = P.ons()
    pe, pg_eur, fx = P.wholesale()
    reg = P.regimes()
    rows = []
    for name, geo in P.GEO.items():
        rate = fx[P.CURRENCY[geo]].reindex(SPAN) if (geo in P.CURRENCY and cur == "lc") else pd.Series(1.0, index=SPAN)
        iso = P.ISO3[geo]
        whole = {"electricity": (pe[iso].reindex(SPAN) if iso in pe.columns else pd.Series(np.nan, index=SPAN)) * rate,
                 "gas": pg_eur.reindex(SPAN) * rate}
        coded = set(reg[reg.country == name]["product"])
        for prod, item in (("electricity", "CP0451"), ("gas", gas_item)):
            if prod not in coded:
                continue
            if geo == "UK":
                uk_item = {"CP0451": "CP0451", "CP04521": "CP04521", "CP0452": "CP0452"}[item]
                idx = uk_ind[uk_item].reindex(SPAN)
            else:
                idx = hicp[(geo, item)].reindex(SPAN) if (geo, item) in hicp.columns else pd.Series(np.nan, index=SPAN)
            dy = 100 * np.log(idx).diff()
            dw = 100 * np.log(whole[prod]).diff()
            codes = reg[(reg.country == name) & (reg["product"] == prod)].set_index("month").main_code
            d = pd.DataFrame({"country": name, "geo": geo, "product": prod, "month": SPAN, "dy": dy.values,
                              "code": codes.reindex(SPAN).values})
            for l in range(13):
                d[f"dw{l}"] = dw.shift(l).values
            rows.append(d[d.month >= "2019-01"])
    return pd.concat(rows, ignore_index=True)


def passthrough(d):
    out, pred = [], []
    for prod, g in d.groupby("product"):
        lags = [f"dw{l}" for l in range(13)]
        est = g[g.code.isin([5, 6]) & g.dy.notna() & g[lags].notna().all(axis=1)]
        res = smf.ols("dy ~ " + " + ".join(lags), data=est).fit()
        ok = g[lags].notna().all(axis=1)
        g = g.copy()
        g.loc[ok, "pred"] = res.predict(g.loc[ok])
        g["ex"] = g.dy - g.pred
        pred.append(g)
        out.append({"product": prod, "n_obs": int(res.nobs), "n_countries": est.geo.nunique(),
                    "sum_lags_0_12": res.params[lags].sum(), "r2": res.rsquared, "const": res.params["Intercept"]})
    return pd.DataFrame(out), pd.concat(pred)


def eventstudy(d, ev, label):
    stack = []
    for _, e in ev.iterrows():
        g = d[(d.country == e.country) & (d["product"] == e["product"])].set_index("month")
        for tau in WIN:
            mo = str(pd.Period(e.month, "M") + tau)
            if mo in g.index and pd.notna(g.at[mo, "ex"]):
                stack.append({"event_id": e.event_id, "country": e.country, "product": e["product"], "type": e.type,
                              "tau": tau, "ex": g.at[mo, "ex"]})
    s = pd.DataFrame(stack)
    rows = []
    groups = [("electricity", s[s["product"] == "electricity"]), ("gas", s[s["product"] == "gas"])]
    groups += [(f"{p} | {t} only (exploratory)", s[(s["product"] == p) & (s.type == t)])
               for p in ("electricity", "gas") for t in ("exit", "step-up")]
    for grp, g in groups:
        if g.event_id.nunique() < 3 or g.country.nunique() < 3:
            continue
        g = g.copy()
        for tau in WIN:
            if tau != -1:
                g[f"t{tau}".replace("-", "m")] = (g.tau == tau).astype(int)
        terms = [f"t{tau}".replace("-", "m") for tau in WIN if tau != -1]
        res = smf.ols("ex ~ " + " + ".join(terms) + " + C(event_id)", data=g).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(g.country)[0]})
        for tau in WIN:
            if tau == -1:
                rows.append({"spec": label, "group": grp, "tau": -1, "coef": 0.0, "se": np.nan, "p": np.nan})
                continue
            t = f"t{tau}".replace("-", "m")
            rows.append({"spec": label, "group": grp, "tau": tau, "coef": res.params[t], "se": res.bse[t], "p": res.pvalues[t]})
        tt = res.t_test("t0 + t1 + t2 = 0")
        rows.append({"spec": label, "group": grp, "tau": "sum 0-2", "coef": float(tt.effect[0]), "se": float(tt.sd[0][0]),
                     "p": float(tt.pvalue)})
        for r in rows[-(len(WIN) + 1):]:
            r.update({"n_events": g.event_id.nunique(), "n_countries": g.country.nunique(), "n_obs": len(g)})
    return pd.DataFrame(rows)


def main():
    chk = subprocess.run([sys.executable, str(ROOT / "code" / "05_freeze_regimes.py"), "check"], capture_output=True, text=True)
    if chk.returncode:
        raise SystemExit(chk.stdout + chk.stderr)
    TAB.mkdir(parents=True, exist_ok=True)
    ev = events()
    ev.to_csv(TAB / "test2_events.csv", index=False)
    print(f"events: {len(ev)} ({(ev.type == 'exit').sum()} exits, {(ev.type == 'step-up').sum()} step-ups)")
    pts, ess = [], []
    for label, gas_item, cur in [("main", "CP04521", "lc"), ("gas_all (04.5.2)", "CP0452", "lc"), ("euros", "CP04521", "eur")]:
        d = monthly(gas_item, cur)
        pt, d = passthrough(d)
        pts.append(pt.assign(spec=label))
        ess.append(eventstudy(d, ev, label))
        print("done:", label)
    pd.concat(pts).to_csv(TAB / "test2_passthrough.csv", index=False)
    pd.concat(ess).to_csv(TAB / "test2_eventstudy.csv", index=False)
    print("saved test2 tables")


if __name__ == "__main__":
    main()
