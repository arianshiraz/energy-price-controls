"""Reconcile every candidate measure in the Bruegel trackers with the coded files.

Each candidate (candidate == 1 in tracker_measures_2021_2023.csv and tracker_measures_2026.csv)
gets one disposition:
  coded       -> the regime_measures.csv rows that carry it (key country|product|code|start_month)
  not_coded   -> the reason under section 6 of the coding rule or the code definitions
  to_code     -> a household price measure not yet in regime_measures.csv (listed for follow-up)
The script checks that every key exists in regime_measures.csv and every candidate is assigned.
Output: data/classification/tracker_reconciliation.csv (no Bruegel text; Amendment 4)
"""
from pathlib import Path

import pandas as pd

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"

FUEL = "Motor or heating fuels (rule section 6)"
NET = "Network charges, not a tax or levy (see not_coded_measures.csv)"
IBX = "Wholesale intervention (Iberian gas cap; rule section 6)"
FIRMS = "Firms or non-household customers only"
TARGET = "Targeted transfer or social tariff; code 5 at most, not a separate row"

A = {  # tracker_measures_2021_2023.csv row index -> (disposition, keys or reason)
    5: ("coded", "Austria|electricity|4|2022-05; Austria|gas|4|2022-05"),
    35: ("coded", "Austria|electricity|2|2022-12"),
    37: ("not_coded", "Excise raised from April 2023 to offset the permanent 6% VAT; noted on the Belgian code 4 rows"),
    38: ("coded", "Belgium|electricity|4|2022-03"),
    39: ("coded", "Belgium|gas|4|2022-04"),
    43: ("coded", "Belgium|electricity|1|2021-02; Belgium|gas|1|2021-02"),
    48: ("not_coded", "Excise raised from April 2023 to offset the permanent 6% VAT; noted on the Belgian code 4 rows"),
    49: ("coded", "Belgium|electricity|4|2022-03"),
    50: ("coded", "Belgium|gas|4|2022-04"),
    52: ("coded", "Belgium|electricity|1|2021-02; Belgium|gas|1|2021-02"),
    55: ("not_coded", "Collective heating installations, not household supply contracts (rule section 6)"),
    61: ("not_coded", FUEL),
    64: ("not_coded", "Zero excise from July 2022 on 'qualifying' electricity (IEA: generally from renewable sources); household coverage not established, and Bulgarian electricity is code 3 throughout, so a code 4 would only add a flag"),
    65: ("coded", "Bulgaria|gas|4|2022-07"),
    66: ("not_coded", "As row 64 (electricity excise)"),
    69: ("coded", "Croatia|gas|4|2022-04"),
    80: ("coded", "Croatia|electricity|1|2022-10"),
    83: ("not_coded", "District heating (rule section 6)"),
    90: ("coded", "Cyprus|electricity|4|2021-11"),
    91: ("coded", "Cyprus|electricity|4|2022-09"),
    101: ("coded", "Cyprus|electricity|4|2022-09"),
    102: ("coded", "Czechia|electricity|4|2021-11; Czechia|gas|4|2021-11"),
    107: ("coded", "Czechia|electricity|1|2023-01; Czechia|gas|1|2023-01"),
    113: ("coded", "Denmark|electricity|4|2023-01"),
    133: ("not_coded", NET),
    134: ("not_coded", NET),
    141: ("not_coded", FUEL),
    142: ("not_coded", "Deferral of a scheduled excise increase, not a reduction (code 4 requires a cut)"),
    144: ("coded", "Estonia|electricity|1|2022-10"),
    156: ("coded", "Finland|electricity|4|2022-12"),
    165: ("coded", "France|gas|1|2021-11"),
    166: ("coded", "France|electricity|1|2022-02"),
    167: ("coded", "France|electricity|4|2022-02"),
    177: ("coded", "France|gas|1|2021-11"),
    178: ("coded", "France|electricity|1|2022-02"),
    183: ("coded", "Germany|electricity|4|2022-07"),
    192: ("coded", "Germany|gas|4|2022-10"),
    213: ("not_coded", FUEL),
    215: ("coded", "Germany|electricity|2|2023-01; Germany|gas|2|2023-01"),
    226: ("coded", "Greece|electricity|4|2021-09"),
    227: ("not_coded", "Dates and terms not found yet (see not_coded_measures.csv)"),
    236: ("not_coded", FUEL),
    242: ("coded", "Ireland|electricity|4|2022-05; Ireland|gas|4|2022-05"),
    251: ("coded", "Ireland|electricity|4|2022-10"),
    253: ("coded", "Ireland|electricity|4|2022-05; Ireland|gas|4|2022-05"),
    256: ("not_coded", "VAT for hospitality businesses; " + FIRMS),
    261: ("coded", "Italy|electricity|4|2021-10; Italy|gas|4|2021-10"),
    262: ("coded", "Italy|gas|4|2021-10"),
    263: ("coded", "Italy|electricity|4|2021-10"),
    264: ("coded", "Italy|gas|4|2021-10"),
    265: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    268: ("coded", "Italy|gas|4|2021-10"),
    269: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    279: ("not_coded", FUEL), 280: ("not_coded", FUEL), 281: ("not_coded", FUEL), 282: ("not_coded", FUEL),
    283: ("coded", "Italy|electricity|4|2021-10"),
    284: ("coded", "Italy|gas|4|2021-10"),
    285: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    299: ("not_coded", FUEL), 304: ("not_coded", FUEL),
    305: ("coded", "Italy|gas|4|2021-10"),
    307: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    312: ("coded", "Italy|electricity|4|2021-10"),
    322: ("not_coded", FUEL), 326: ("not_coded", FUEL), 327: ("not_coded", FUEL), 329: ("not_coded", FUEL),
    331: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    335: ("coded", "Italy|electricity|4|2021-10"),
    341: ("coded", "Italy|electricity|5|2022-01; Italy|gas|5|2022-01"),
    342: ("coded", "Italy|gas|4|2021-10"),
    347: ("coded", "Latvia|electricity|4|2022-01; Latvia|electricity|4|2022-09"),
    348: ("not_coded", NET),
    349: ("not_coded", "Terms unclear; to classify after reading the decision (see not_coded_measures.csv)"),
    358: ("not_coded", "Terms unclear; to classify after reading the decision (see not_coded_measures.csv)"),
    361: ("coded", "Lithuania|electricity|1|2022-07; Lithuania|gas|1|2022-07"),
    379: ("coded", "Lithuania|electricity|1|2022-07; Lithuania|gas|1|2022-07"),
    381: ("not_coded", NET),
    382: ("not_coded", NET),
    396: ("not_coded", NET),
    397: ("coded", "Luxembourg|gas|1|2022-10"),
    400: ("coded", "Luxembourg|electricity|4|2023-01; Luxembourg|gas|4|2023-01"),
    410: ("coded", "Malta|electricity|1|2022-01"),
    417: ("coded", "Netherlands|electricity|4|2022-01; Netherlands|gas|4|2022-01"),
    421: ("not_coded", FUEL),
    425: ("coded", "Netherlands|electricity|4|2022-01"),
    428: ("coded", "Netherlands|electricity|4|2022-01; Netherlands|gas|4|2022-01"),
    430: ("not_coded", FUEL),
    434: ("coded", "Netherlands|electricity|2|2023-01; Netherlands|gas|2|2023-01"),
    445: ("coded", "Poland|electricity|4|2022-01; Poland|gas|4|2022-01"),
    446: ("coded", "Poland|electricity|4|2022-01; Poland|gas|4|2022-01"),
    452: ("not_coded", FUEL),
    454: ("coded", "Poland|electricity|1|2023-01"),
    461: ("not_coded", FIRMS),
    462: ("not_coded", NET),
    463: ("not_coded", IBX),
    469: ("coded", "Portugal|electricity|4|2022-10"),
    480: ("coded", "Portugal|electricity|4|2022-10"),
    481: ("coded", "Portugal|gas|3|2019-01"),
    493: ("coded", "Romania|electricity|1|2022-04; Romania|gas|1|2022-04"),
    494: ("coded", "Romania|electricity|1|2022-04; Romania|gas|1|2022-04"),
    495: ("not_coded", FIRMS),
    497: ("coded", "Slovenia|electricity|4|2022-02; Slovenia|gas|4|2022-02"),
    500: ("not_coded", FUEL),
    511: ("not_coded", "Cut in electricity system charges financed by a windfall levy; Spain electricity is already code 4 in these months (recorded in the VAT and IEE rows)"),
    513: ("coded", "Spain|electricity|4|2021-10"),
    515: ("coded", "Spain|electricity|4|2021-07"),
    517: ("not_coded", TARGET),
    523: ("coded", "Spain|electricity|4|2021-07; Spain|electricity|4|2021-10"),
    525: ("not_coded", TARGET),
    527: ("not_coded", IBX),
    528: ("coded", "Spain|gas|1|2022-01"),
    532: ("not_coded", "Tax on generators (IVPEE), not a tax on household bills"),
    533: ("not_coded", IBX),
    539: ("coded", "Spain|electricity|4|2021-07"),
    544: ("coded", "Spain|gas|4|2022-10"),
    545: ("coded", "Spain|gas|1|2022-01"),
    547: ("not_coded", "Collective heating installations (homeowners' associations), not household supply contracts"),
    548: ("not_coded", TARGET),
    549: ("not_coded", TARGET),
    550: ("not_coded", FIRMS),
    551: ("not_coded", IBX),
    558: ("coded", "Spain|electricity|4|2021-07; Spain|electricity|4|2021-10"),
    565: ("coded", "Spain|gas|4|2022-10"),
    566: ("coded", "Sweden|electricity|5|2021-12"),
    591: ("coded", "United Kingdom|electricity|1|2022-10; United Kingdom|gas|1|2022-10"),
}
B = {  # tracker_measures_2026.csv row index
    2: ("not_coded", TARGET + "; mainly fossil heating fuels"),
    9: ("not_coded", TARGET),
    10: ("coded", "Cyprus|electricity|4|2021-11"),
    15: ("not_coded", "Permanent low-income energy voucher (chèque énergie), not a crisis measure; " + TARGET),
    30: ("not_coded", "Hardship fund, not a price measure"),
    31: ("not_coded", "Loans for home efficiency, not a price measure"),
    32: ("not_coded", "Efficiency advice programme, not a price measure"),
    33: ("not_coded", "Insulation programme, not a price measure"),
    36: ("not_coded", "Efficiency subsidies, not a price measure"),
    44: ("coded", "Spain|electricity|4|2026-04; Spain|gas|4|2026-04"),
    46: ("not_coded", TARGET),
    48: ("coded", "Sweden|electricity|5|2026-06"),
}


def main():
    m = pd.read_csv(CLS / "regime_measures.csv", dtype=str).fillna("")
    keys = set(m.country + "|" + m["product"] + "|" + m.code + "|" + m.start_month)
    out = []
    for fname, mapping, name_col, ctry_col in [
        ("tracker_measures_2021_2023.csv", A, "measure", "country"),
        ("tracker_measures_2026.csv", B, "Measure Name", "Country"),
    ]:
        t = pd.read_csv(CLS / fname, dtype=str).fillna("")
        cand = set(t.index[t.candidate == "1"])
        assert cand == set(mapping), (fname, sorted(cand ^ set(mapping)))
        for i in sorted(cand):
            disp, txt = mapping[i]
            if disp == "coded":
                missing = [k for k in txt.split("; ") if k not in keys]
                assert not missing, (fname, i, missing)
            # Measure names are not written: Bruegel's trackers are CC BY-ND 4.0 (Amendment 4); the file and row
            # number point to the unaltered source.
            out.append({"tracker_file": fname, "tracker_row": i, "country": t.at[i, ctry_col],
                        "disposition": disp,
                        "regime_rows": txt if disp == "coded" else "", "reason": "" if disp == "coded" else txt})
    o = pd.DataFrame(out)
    o.to_csv(CLS / "tracker_reconciliation.csv", index=False, encoding="utf-8")
    print(o.groupby(["tracker_file", "disposition"]).size())


if __name__ == "__main__":
    main()
