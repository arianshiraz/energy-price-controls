# Raw data provenance

Downloads are not committed. Each source is listed here with its URL and download date, and snapshotted with checksums in the shared data archive (`_data_archive/energy-price-controls-inflation/`).

## Policy trackers (`bruegel/`)

| File | Source | Downloaded | SHA-256 (first 16) | Contents |
|---|---|---|---|---|
| `bruegel_2021_2023_methodology_figure1_20230731.xlsx` | Bruegel, "National fiscal policy responses to the energy crisis" (Sgaravatti, Tagliapietra, Trasi and Zachmann; first published 4 November 2021, latest update 26 June 2023, correction 31 July 2023). Page: https://www.bruegel.org/dataset/national-policies-shield-consumers-rising-energy-prices; file linked as "Download the fiscal tracker methodology (Excel file)": https://www.bruegel.org/system/files/2023-07/Methodology%20Figure%201%20-%20with%20split_31%20July%2023.xlsx | 8 November 2026, through Chrome (the site refuses scripted requests) | 275f6ba2e12f30a8 | One sheet per country (EU-27, Norway, UK): each measure with household/firm, targeted, price or income, utilities flags, allocated budget, roll-out start and end dates, announcement date and sources |
| `bruegel_2026_policy_list_20260616.xlsx` | Bruegel, "2026 European energy crisis fiscal response tracker" (McWilliams, Mramor, Roth and Tagliapietra; first published 28 April 2026, latest update 16 June 2026). Page: https://www.bruegel.org/dataset/2026-european-energy-crisis-fiscal-response-tracker; file: https://www.bruegel.org/sites/default/files/2026-06/policy_list_20260616.xlsx | 8 November 2026, through Chrome | dbacdfe5a062153e | Sheet "Measures" (57 measures: country, dates, status, type, energy carrier, target group, sources) and sheet "GDP" |

The 2026 tracker page dates the shock from the US-Israeli attack on Iran on 28 February 2026 and the subsequent closure of the Strait of Hormuz.

## Price outcomes and wholesale exposure (downloaded 12 November 2026, after the freeze)

The coded regimes were frozen on 12 November 2026 (`data/classification/freeze_manifest.csv`, tag `regimes-frozen-2026-11-12`) before these files were downloaded. All were fetched by script on 12 November 2026.

| File | Source | SHA-256 (first 16) | Contents |
|---|---|---|---|
| `eurostat/prc_hicp_midx_I15_20261112.csv` | Eurostat HICP monthly indices, ECOICOP (`prc_hicp_midx`), SDMX-CSV from https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_midx/M.I15.CP00+CP045+CP0451+CP0452+NRG+TOT_X_NRG_FOOD./?format=SDMX-CSV&startPeriod=2019-01 | 9028513d44f3463a | Index 2015=100, all reporting areas; all items (CP00), electricity, gas and other fuels (CP045), electricity (CP0451), gas (CP0452), energy (NRG), all items excluding energy, food, alcohol and tobacco (TOT_X_NRG_FOOD); 2019-01 to 2025-12 |
| `eurostat/prc_hicp_minr_I15_20261112.csv` | Eurostat HICP monthly indices, COICOP 2018 (`prc_hicp_minr`), same query with TOTAL in place of CP00 | 5629fcf24fd59ef2 | Same items on COICOP 2018, index 2015=100; 2019-01 to 2026-09 |
| `eurostat/prc_hicp_midx_I15_gas_split_20261112.csv`, `eurostat/prc_hicp_minr_I15_gas_split_20261112.csv` | As above, items CP04521 and CP04522 | 3e6003745d568ad8, ad1d54848158d55d | Natural gas and town gas (CP04521) and liquefied hydrocarbons (CP04522) separately |
| `eurostat/prc_hicp_inw_20261112.csv`, `eurostat/prc_hicp_inw_gas_split_20261112.csv` | Eurostat HICP item weights (`prc_hicp_inw`), CP0451, CP0452, CP045, NRG, CP04521, CP04522 | 8bcfe7b752e2616e, 225e822d37ac384a | Annual weights (per mille), 2019 to 2025 |
| `eurostat/ert_bil_eur_m_USD_20261112.csv` | Eurostat euro exchange rates (`ert_bil_eur_m`), monthly average, USD per EUR | d421d66a428f5c62 | 2019-01 to 2026-10; converts the dollar gas price to euros (research design, Amendment 3) |
| `eurostat/ert_bil_eur_m_national_20261112.csv` | Eurostat euro exchange rates (`ert_bil_eur_m`), monthly average, national currency per EUR: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ert_bil_eur_m/M.AVG.NAC.CZK+DKK+HUF+PLN+RON+SEK+NOK+ISK+GBP/?format=SDMX-CSV&startPeriod=2019-01 | 64d37644248e7850 | CZK, DKK, GBP, HUF, ISK, NOK, PLN, RON, SEK, 2019-01 to 2026-10 (research design, Amendment 3). Eurostat no longer serves BGN and HRK |
| `ecb/EXR_M_BGN_HRK_EUR_SP00_A_20261112.csv` | ECB Data Portal, exchange rates (EXR), series M.BGN.EUR.SP00.A and M.HRK.EUR.SP00.A: https://data-api.ecb.europa.eu/service/data/EXR/M.BGN+HRK.EUR.SP00.A?format=csvdata&startPeriod=2019-01 | 0411954015ae72f0 | BGN to 2025-12, HRK to 2022-12, monthly average per EUR; after euro adoption the series continue at the irrevocable rates (BGN 1.95583, HRK 7.53450) |
| `ons/mm23_20261112.csv` | ONS, Consumer price inflation time series (MM23), full dataset: https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/datasets/consumerpriceindices/current/mm23.csv | ed5b20bea47cda76 | UK series used: D7BT (CPI all items), D7DT (04.5.1 electricity), D7DU (04.5.2 gas), L7E9 (04.5.2.1 natural gas), DK9T (energy), DKC6 (excluding energy, food, alcohol and tobacco), all 2015=100; weights CJXA (electricity), CJXB (gas), L89X (natural gas); to 2026 September |
| `ember/european_wholesale_electricity_price_data_monthly_20261112.csv` | Ember, European wholesale electricity price data, monthly: https://files.ember-energy.org/public-downloads/price/outputs/european_wholesale_electricity_price_data_monthly.csv (linked from https://ember-energy.org/data/european-wholesale-electricity-price-data/) | 20d02be83f6b6135 | Day-ahead price, EUR/MWh, one series per country, from 2015 (Bulgaria from 2016-10, UK from 2016-06, Croatia from 2017-10, Ireland from 2018-10) to 2026-11 |
| `worldbank/CMO-Historical-Data-Monthly_20261112.xlsx` | World Bank Commodity Price Data (Pink Sheet), monthly, updated 3 November 2026: https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx | 3c8d9d8dbb48342f | Sheet "Monthly Prices", column "Natural gas, Europe" (USD/mmbtu), 1960M01 to 2026M10 |

Coverage notes, from counts of observations only:
- HICP: all 29 Eurostat countries in the sample have complete series for every item, except where an item does not exist (no gas index for Finland, Norway or Iceland). Eurostat's UK series stop in 2020, so the UK uses ONS. Norway's electricity index on COICOP 2018 has two missing months.
- HICP item 04.5.2 (gas) includes bottled LPG as well as piped natural gas, which is why Malta and Cyprus report a gas index without a household gas network. Since Amendment 3 of the research design, the main gas outcome is piped natural gas (04.5.2.1), with 04.5.2 kept as a robustness check.
- Ember has no series for Cyprus, Malta or Iceland, which have no day-ahead market in the sample period. Under the design (section 4) these countries drop out of the tests that need wholesale exposure, and the drop is reported. How Ember builds one series for multi-zone countries (Norway, Sweden, Denmark, Italy) is still to be read in Ember's methodology. The latest month (2026-11) is partial.

## Licences and redistribution (checked 13 November 2026)

Terms read on each provider's own page:

| Source | Terms | Source of the terms |
|---|---|---|
| Eurostat (HICP, item weights, exchange rates) | Creative Commons Attribution 4.0; data free of charge for reuse, crediting the source and indicating changes | https://ec.europa.eu/eurostat/web/main/help/copyright-notice |
| ONS (MM23) | Open Government Licence (Crown copyright) | https://www.ons.gov.uk/help/termsandconditions |
| Ember (wholesale electricity prices) | Creative Commons Attribution 4.0 ("All content is released under a Creative Commons Attribution Licence (CC-BY-4.0)") | https://ember-energy.org/data/european-wholesale-electricity-price-data/ |
| ECB (BGN and HRK exchange rates) | Free reuse if the source is quoted ("Source: ECB statistics") and the statistics, including metadata, are not modified | https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html |
| World Bank (Pink Sheet) | Creative Commons Attribution 4.0 unless the metadata says otherwise; third-party data may need the original provider's consent. The European gas series lists Bloomberg Finance L.P., World Gas Intelligence and the World Bank as sources (sheet "Description") | https://data.worldbank.org/summary-terms-of-use (linked from the Pink Sheet page as "Data Access and Licensing") |
| Bruegel (policy trackers) | Creative Commons Attribution-NoDerivatives 4.0: reproduction must be unaltered and in the original language; altered versions need Bruegel's written approval | https://www.bruegel.org/datasets ("Republishing and referencing policy") |

What is committed (since Amendment 4 of the coding rule, 17 November 2026):

- `data/project_data_workbook.xlsx` holds Eurostat, ONS, Ember and ECB values, which their licences allow with attribution (given on each sheet). The World Bank sheet holds source details only; its values are not included because the European gas series lists Bloomberg Finance L.P. among its sources.
- `data/classification/tracker_reconciliation.csv` identifies Bruegel candidates by file and row number only. The tracker extracts (`tracker_measures_*.csv`) are rebuilt locally and not committed, because Bruegel's licence (CC BY-ND 4.0) does not allow altered copies.
- `output/tables/test4_base_month.csv` holds the ratio used by the base-month rule, not the World Bank prices.

Everything removed can be rebuilt from the downloads listed above with the scripts in `code/`.
