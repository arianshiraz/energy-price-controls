"""Test 1, postpone or prevent (research design, section 6, test 1; Amendments 1 to 3).

For each horizon h in {6, 12, 24, 36, 48}, across countries:
    y(c,h) = a + b1 S_freeze + b2 S_quantity + b3 S_lagged + b4 S_tax + g W + d R + e
HC3 standard errors; permutation p-values from 2,000 permutations of the regime shares across countries
(the four shares permuted together as a block; statistic: the HC3 t-statistic); the formal test
D = b1(48) - b1(12) > 0 with a 95% percentile interval from 2,000 bootstrap resamples of countries
(the same resample at both horizons).

Implementation choices, fixed before running and reported with the results:
  - shares use the main code (the coding rule's precedence 1 > 2 > 3 > 4 > 5 > 6);
  - "with and without" flagged records in a cross-section means dropping countries with any flagged
    month in months 1 to h (special flags, unverified records, low coverage);
  - random seed 20261112.

Outputs: output/tables/test1_*.csv
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DER, TAB = ROOT / "data" / "derived", ROOT / "output" / "tables"
SEED, NPERM, NBOOT = 20261112, 2000, 2000
REGIMES = ["freeze", "quantity", "lagged", "tax"]
AMENDMENT1 = {"EL", "CY", "NO", "LT", "EE"}


def design(d, spec, cur):
    X = d[[f"S_{k}_{spec}" for k in REGIMES]].copy()
    X.columns = [f"S_{k}" for k in REGIMES]
    X["W"] = d[f"W_{spec}_{cur}"]
    X["R"] = d["R"]
    return sm.add_constant(X), d[f"y_{spec}" if spec != "core" else "y_core"]


def fit(X, y):
    return sm.OLS(y, X).fit(cov_type="HC3")


def perm_p(X, y, rng, n=NPERM):
    """Permutation p-values for the four shares: permute the share block across countries."""
    t0 = fit(X, y).tvalues
    cols = [f"S_{k}" for k in REGIMES]
    hits, done = np.zeros(len(cols)), 0
    S = X[cols].to_numpy()
    for _ in range(n):
        Xp = X.copy()
        Xp[cols] = S[rng.permutation(len(S))]
        try:
            tp = fit(Xp, y).tvalues[cols].to_numpy()
        except Exception:
            continue
        if not np.all(np.isfinite(tp)):
            continue
        hits += np.abs(tp) >= np.abs(t0[cols].to_numpy())
        done += 1
    return pd.Series((hits + 1) / (done + 1), index=cols), done


def run(panel, label, spec="main", cur="lc", drop=lambda d: pd.Series(False, index=d.index), outcome=None):
    rng = np.random.default_rng(SEED)
    rows, fits = [], {}
    for h in sorted(panel.h.unique()):
        d = panel[(panel.h == h) & panel[f"W_{spec}_{cur}"].notna()]
        d = d[~drop(d)]
        d = d[d[outcome if outcome is not None else f"y_{spec}"].notna()].set_index("geo")  # e.g. a missing base-month index
        X, y = design(d, spec, cur)
        if outcome is not None:
            y = d[outcome]
        res = fit(X, y)
        pp, nperm = perm_p(X, y, rng)
        fits[h] = (X, y)
        for v in res.params.index:
            rows.append({"spec": label, "h": h, "n": int(res.nobs), "term": v, "coef": res.params[v], "se_hc3": res.bse[v],
                         "p_hc3": res.pvalues[v], "p_perm": pp.get(v, np.nan), "n_perm": nperm if v in pp else np.nan,
                         "r2": res.rsquared})
    # D = b1(48) - b1(12), country bootstrap with the same resample at both horizons
    D, ci, nb = np.nan, (np.nan, np.nan), 0
    if 12 in fits and 48 in fits:
        X12, y12 = fits[12]
        X48, y48 = fits[48]
        common = X12.index.intersection(X48.index)
        X12, y12, X48, y48 = X12.loc[common], y12.loc[common], X48.loc[common], y48.loc[common]
        D = fit(X48, y48).params["S_freeze"] - fit(X12, y12).params["S_freeze"]
        draws = []
        for _ in range(NBOOT):
            idx = rng.choice(common, size=len(common), replace=True)
            try:
                b = fit(X48.loc[idx], y48.loc[idx]).params["S_freeze"] - fit(X12.loc[idx], y12.loc[idx]).params["S_freeze"]
            except Exception:
                continue
            if np.isfinite(b) and X12.loc[idx, "S_freeze"].std() > 0 and X48.loc[idx, "S_freeze"].std() > 0:
                draws.append(b)
        nb = len(draws)
        ci = tuple(np.percentile(draws, [2.5, 97.5]))
        share_pos = float(np.mean(np.array(draws) > 0))
    else:
        share_pos = np.nan
    return pd.DataFrame(rows), {"spec": label, "D": D, "ci_low": ci[0], "ci_high": ci[1], "n_boot": nb,
                                "share_boot_D_positive": share_pos}


def main():
    chk = subprocess.run([sys.executable, str(ROOT / "code" / "05_freeze_regimes.py"), "check"], capture_output=True, text=True)
    if chk.returncode:
        raise SystemExit(chk.stdout + chk.stderr)
    p = pd.read_csv(DER / "panel_test1.csv")
    TAB.mkdir(parents=True, exist_ok=True)
    specs = [
        ("main", dict()),
        ("gas_all (04.5.2)", dict(spec="gas_all")),
        ("euros", dict(cur="eur")),
        ("without special flags", dict(drop=lambda d: d.share_special_main > 0)),
        ("without unverified records", dict(drop=lambda d: d.share_unverified_main > 0)),
        ("without low coverage", dict(drop=lambda d: d.share_lowcov_main > 0)),
        ("without Amendment 1 countries", dict(drop=lambda d: d.geo.isin(AMENDMENT1))),
    ]
    coefs, Ds = [], []
    for label, kw in specs:
        c, dd = run(p, label, **kw)
        coefs.append(c)
        Ds.append(dd)
        print(f"done: {label}")
    c3, d3 = run(p, "test 3: core inflation", outcome="y_core")
    coefs.append(c3)
    Ds.append(d3)
    C = pd.concat(coefs)
    C.to_csv(TAB / "test1_coefficients.csv", index=False)
    pd.DataFrame(Ds).to_csv(TAB / "test1_D.csv", index=False)
    print("saved", TAB / "test1_coefficients.csv", "and test1_D.csv")


if __name__ == "__main__":
    main()
