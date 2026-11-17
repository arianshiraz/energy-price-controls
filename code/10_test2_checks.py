"""Robustness checks for test 2 (not pre-specified; reported as robustness, 12 November 2026).

1. Seasonality. 13 of the 41 events fall in January, when many tariffs reset.
   (a) month_of_year: the pass-through model adds month-of-year dummies (estimated, as before, on
       country-months with main code 5 or 6).
   (b) common_month: in addition, the average excess change of uncontrolled country-months in the same
       calendar month (same product) is subtracted, which removes Europe-wide repricing in that month
       (for example January 2024).
2. Few clusters. Wild cluster restricted bootstrap (WCR) p-values, clustered by country, Webb six-point
   weights, 9,999 draws, seed 20261112, for the event-month coefficient (tau = 0) and for the sum over
   months 0 to 2. The sum is tested by reparametrising: with theta = b0 + b1 + b2, the regressors are
   d0 for theta and (d1 - d0), (d2 - d0) for b1 and b2, so theta = 0 drops one column.

Output: output/tables/test2_checks.csv
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "output" / "tables"
s9 = importlib.util.spec_from_file_location("t2", ROOT / "code" / "09_test2.py")
T2 = importlib.util.module_from_spec(s9)
s9.loader.exec_module(T2)
SEED, B = 20261112, 9999
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
LAGS = [f"dw{l}" for l in range(13)]


def predict(d, seasonal):
    out = []
    for prod, g in d.groupby("product"):
        g = g.copy()
        g["moy"] = g.month.str[5:]
        rhs = " + ".join(LAGS) + (" + C(moy)" if seasonal else "")
        ok = g.dy.notna() & g[LAGS].notna().all(axis=1)
        res = smf.ols("dy ~ " + rhs, data=g[ok & g.code.isin([5, 6])]).fit()
        g.loc[ok, "pred"] = res.predict(g.loc[ok])
        g["ex"] = g.dy - g.pred
        out.append(g)
    return pd.concat(out)


def common_month(d):
    """Subtract the mean excess of uncontrolled country-months in the same calendar month and product."""
    ref = d[d.code.isin([5, 6])].groupby(["product", "month"]).ex.mean().rename("ex_ref")
    d = d.join(ref, on=["product", "month"])
    d["ex"] = d.ex - d.ex_ref.fillna(0.0)
    return d


def stack(d, ev, product):
    rows = []
    for _, e in ev[ev["product"] == product].iterrows():
        g = d[(d.country == e.country) & (d["product"] == product)].set_index("month")
        for tau in T2.WIN:
            mo = str(pd.Period(e.month, "M") + tau)
            if mo in g.index and pd.notna(g.at[mo, "ex"]):
                rows.append({"event_id": e.event_id, "country": e.country, "tau": tau, "ex": g.at[mo, "ex"]})
    s = pd.DataFrame(rows)
    taus = [t for t in T2.WIN if t != -1]
    D = pd.DataFrame({f"d{t}": (s.tau == t).astype(float) for t in taus})
    FE = pd.get_dummies(s.event_id, dtype=float)
    return s, D, FE


def ols(y, X):
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    return b, XtX


def cr1_t(y, X, g, j):
    b, XtX = ols(y, X)
    u = y - X @ b
    G = np.unique(g)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for c in G:
        s = X[g == c].T @ u[g == c]
        meat += np.outer(s, s)
    n, k, m = len(y), X.shape[1], len(G)
    V = (m / (m - 1)) * ((n - 1) / (n - k)) * XtX @ meat @ XtX
    return b[j], np.sqrt(V[j, j]), b[j] / np.sqrt(V[j, j])


def wcr(y, X, g, j, rng):
    coef, se, t0 = cr1_t(y, X, g, j)
    Xr = np.delete(X, j, axis=1)
    br, _ = ols(y, Xr)
    fit_r, ur = Xr @ br, y - Xr @ br
    G, inv = np.unique(g, return_inverse=True)
    hits = 0
    for _ in range(B):
        w = rng.choice(WEBB, size=len(G))[inv]
        ys = fit_r + ur * w
        _, _, ts = cr1_t(ys, X, g, j)
        hits += abs(ts) >= abs(t0)
    return coef, se, t0, (hits + 1) / (B + 1)


def estimate(s, D, FE, rng):
    y, g = s.ex.to_numpy(), s.country.to_numpy()
    base = pd.concat([D, FE], axis=1)
    X = base.to_numpy()
    j0 = list(base.columns).index("d0")
    c0, se0, _, p0 = wcr(y, X, g, j0, rng)
    _, _, _ = cr1_t(y, X, g, j0)
    R = D.copy()
    R["d1"], R["d2"] = D.d1 - D.d0, D.d2 - D.d0  # coefficient on d0 becomes theta = b0 + b1 + b2
    Xs = pd.concat([R, FE], axis=1).to_numpy()
    cs, ses, _, ps = wcr(y, Xs, g, j0, rng)
    p0_cl = 2 * (1 - __import__("scipy").stats.t.cdf(abs(c0 / se0), df=len(np.unique(g)) - 1))
    ps_cl = 2 * (1 - __import__("scipy").stats.t.cdf(abs(cs / ses), df=len(np.unique(g)) - 1))
    return {"coef_tau0": c0, "se_tau0": se0, "p_tau0_cluster_tG1": p0_cl, "p_tau0_wcr": p0,
            "coef_sum02": cs, "se_sum02": ses, "p_sum02_cluster_tG1": ps_cl, "p_sum02_wcr": ps,
            "n_events": s.event_id.nunique(), "n_countries": s.country.nunique(), "n_obs": len(s)}


def main():
    chk = subprocess.run([sys.executable, str(ROOT / "code" / "05_freeze_regimes.py"), "check"], capture_output=True, text=True)
    if chk.returncode:
        raise SystemExit(chk.stdout + chk.stderr)
    ev = T2.events()
    d0 = T2.monthly("CP04521", "lc")
    rows = []
    variants = [("as pre-specified", lambda d: predict(d, False)),
                ("month-of-year dummies", lambda d: predict(d, True)),
                ("month-of-year + common calendar month", lambda d: common_month(predict(d, True)))]
    for label, f in variants:
        d = f(d0)
        for prod in ("electricity", "gas"):
            rng = np.random.default_rng(SEED)
            s, D, FE = stack(d, ev, prod)
            r = estimate(s, D, FE, rng)
            r.update({"variant": label, "product": prod})
            rows.append(r)
            print(f"{label} | {prod}: tau0 {r['coef_tau0']:+.1f} (wcr p {r['p_tau0_wcr']:.3f}); "
                  f"sum0-2 {r['coef_sum02']:+.1f} (wcr p {r['p_sum02_wcr']:.3f})")
    pd.DataFrame(rows).to_csv(TAB / "test2_checks.csv", index=False)
    print("saved", TAB / "test2_checks.csv")


if __name__ == "__main__":
    main()
