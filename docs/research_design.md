# Do Energy Price Controls Prevent Inflation or Postpone It? Evidence from Two European Energy Shocks

Research design and pre-specification

**Status:** frozen on 8 November 2026, together with the [regime coding rule](regime_coding_rule.md). Later changes are logged as dated amendments in section 9 and results are reported under both the original and the amended specification. Before freezing, no outcome data were examined. On 8 November 2026, to check availability, the Eurostat API returned the electricity index for France, Germany and Spain for January 2021 to December 2025 and a few 2026 months for France; only the number of values and the date range were printed, not the values themselves.

## 1. Question

When wholesale gas and electricity prices jumped in 2021 and 2022, European governments chose very different responses. France froze regulated tariffs and raised them in steps later. The UK passed costs through a cap reset each quarter. Germany capped the price on 80% of past consumption, which kept the full price at the margin. Others cut taxes or paid lump sums. A second shock in 2026, following the war involving Iran, has prompted a new round of measures.

The paper asks:
1. Do retail price controls lower the total rise in consumer energy prices over a full cycle, or do they move it in time, with the rise arriving when the controls end?
2. Do they change core inflation (prices excluding energy and food), and in which direction?
3. Does the design matter: does a freeze differ from a cap that keeps the marginal price at market level?

## 2. What is known (searched 8 November 2026; every item to be read and its details verified before it is cited in a paper)

- **Pass-through with regulated prices.** An ECB working paper (WP 2968, on gas price shocks) finds that regulated energy markets dampen and slow the pass-through of gas shocks to euro-area inflation. A European Commission discussion paper (DP 197, November 2023) links 2022 inflation differentials across member states to the slow pass-through of energy costs and treats countries with regulated prices as a distinct group.
- **Subsidies and persistence, with conflicting conclusions.** Erceg, Kolasa, Lindé and Pescatori (2024, IMF WP 24/81; CEPR DP 19085) argue that consumer energy subsidies lower headline inflation at first but can make it more persistent, and push up core inflation. Imam and Poghosyan (2026, IMF WP 2026/103) find that countries that expanded subsidies had weaker pass-through from energy prices to headline inflation after COVID.
- **Theory.** Krebs and Weber (2024, IZA DP 17043) argue that price controls can be optimal after an energy shock when self-fulfilling expectations create price uncertainty. Xie and Huang (2026) compare energy price management systems in a DSGE model.
- **Single-country evidence.** A Banque de France bulletin (July 2024) finds that France's tariff shield mainly smoothed the inflation path, with a cumulative effect over 2022 to 2025 of about −0.4 percentage points, and would only have delayed inflation had the shock persisted. INSEE estimates a larger short-run effect. An EsadeEcPol note estimates the effect of Spain's gas cap on 2022 inflation.

**Gap.** No study found compares, across countries and over a full cycle, the path of consumer energy prices under each type of control, from the start of the shock to after the controls end. A cross-country dataset of retail price controls with start and end dates and design features also seems to be missing; an IMF working paper found in the search notes that it could not account for price controls for lack of such data (which paper, and its exact wording, to be checked). The 2026 shock gives a second episode.

## 3. Hypotheses

| | Hypothesis | Test |
|---|---|---|
| P1 | Controls postpone rather than prevent: the gap in cumulative energy inflation between controlled and uncontrolled countries shrinks after controls end. | Section 6, test 1 |
| P2 | Exits and scheduled step-ups produce catch-up jumps in consumer energy prices beyond what wholesale prices imply at that date. | Section 6, test 2 |
| P3 | Controls lower core inflation less than headline inflation, or raise it later (the Erceg et al. prediction), rather than lowering both one for one. | Section 6, test 3 |
| P4 | Designs that keep the marginal price at market level (quantity-based caps) lower the bill without the same catch-up as freezes. | Comparison of regimes in tests 1 and 2 |

What would count against: a cumulative gap that persists to the end of the horizon (controls prevent, not postpone); no excess jump at exits; core inflation reduced as much as headline.

## 4. Sample and data

- **Countries:** EU-27, Norway and Iceland (Eurostat HICP), and the UK (ONS CPI, the UK's HICP-concept index, mapped to the same categories). A country without a wholesale electricity price series (section 6) is dropped from the tests that need it, and the drop is reported.
- **Prices:** monthly HICP indices for electricity, gas, energy, the overall index and the index excluding energy and food, January 2019 to the latest month. Eurostat moved to COICOP 2018 in 2026 (`prc_hicp_minr` from January 2026; `prc_hicp_midx` up to December 2025); the two are linked at December 2025 and the link is documented.
- **Wholesale exposure:** monthly average day-ahead electricity price for each country (Ember's European wholesale price data; ENTSO-E where Ember has no series; for multi-zone countries, the load-weighted average where Ember provides it, otherwise the zone containing the capital), and the monthly European natural gas price from the World Bank Commodity Price Data (Pink Sheet). Sources and any substitutions are recorded in `data/raw/README.md`.
- **Policies:** Bruegel's national policies tracker (September 2021 to 2023) and its 2026 energy crisis tracker, checked against national decisions. The Bruegel pages refuse automated requests; files are downloaded by hand or through a browser.
- **Market structure:** whether retail tariffs were regulated before the shock (ACER and CEER retail monitoring reports).

## 5. Coding the control regimes

The written rule ([regime_coding_rule.md](regime_coding_rule.md)), frozen with this design, classifies each country-month, separately for household electricity and household gas, into one of:
1. **Freeze or cap below cost** on the unit price for all consumption (for example France's regulated tariffs under the shield);
2. **Quantity-based cap** that limits the price on part of consumption and leaves the marginal unit at market price (for example Germany's price brakes in 2023);
3. **Lagged formula cap** that passes costs through with a delay (for example the UK cap reset each quarter);
4. **Tax or levy cuts** on energy bills;
5. **Transfers only** (lump sums with no effect on the unit price);
6. **None**.
For each control, the rule records the start date, end date, scheduled step-ups, coverage (households, small firms) and the source with page or article reference. Countries can combine categories; the coding records each.

## 6. Tests

**Common definitions.** Shock start: base month July 2021 (t = 0), so month h is July 2021 plus h months. Household energy price change: the weighted average of the changes in the HICP indices for electricity (COICOP 04.5.1) and gas (04.5.2), with the weights below, so that prices and regimes cover the same items. Weights: each country's 2021 HICP item weights for electricity and gas, normalised to sum to one within the two. Regime shares: for horizon h and regime k, S_k(c,h) is the share of months 1 to h in which regime k was in force in country c, averaged over electricity and gas with those weights. Wholesale exposure: W(c,h) = w_e · 100 ln(P_e(c,h)/P_e(c,0)) + w_g · 100 ln(P_g(h)/P_g(0)), using 3-month centred averages of the wholesale prices to reduce noise, where P_e is the country's day-ahead electricity price, P_g the European gas price, and w_e, w_g the normalised weights. Pre-shock regulated tariffs: R(c) = 1 if household electricity or gas prices were set or approved by a regulator or government in July 2021 (coded under the same rule).

1. **Postpone or prevent (main).** For each horizon h in {6, 12, 24, 36, 48}, across countries:

   y(c,h) = a + b1 S_freeze(c,h) + b2 S_quantity(c,h) + b3 S_lagged(c,h) + b4 S_tax(c,h) + g W(c,h) + d R(c) + e,

   where y(c,h) = w_e · 100 ln(E(c,h)/E(c,0)) + w_g · 100 ln(G(c,h)/G(c,0)), with E and G the HICP electricity and gas indices. A country with no gas index (no household gas market) uses electricity alone. Standard errors are HC3; p-values also come from 2,000 permutations of the regime shares across countries. P1 predicts b1 < 0 at h = 6 and 12, and b1 at h = 48 closer to zero than at h = 12. The formal test is D = b1(48) − b1(12) > 0, with a 95% interval from 2,000 bootstrap resamples of countries.
2. **Catch-up at exits and step-ups.** Events are the dated exits of, and scheduled increases in, controlled prices recorded under the coding rule, separately for electricity and gas. The outcome is the monthly change in 100 ln of the electricity (or gas) index minus the change predicted by wholesale prices, where the prediction comes from a regression of that monthly change on lags 0 to 12 of the monthly change in 100 ln of the wholesale price, estimated on country-months with no control in force (regime 6 or 5 only). Event window: 3 months before to 6 months after, with the month before the event as reference. Pooled across events with event fixed effects; standard errors clustered by country. P2 predicts a positive excess change in the event month and the following two months.
3. **Core inflation.** Test 1 with y(c,h) computed from the HICP excluding energy, food, alcohol and tobacco.
4. **The 2026 shock.** The base month is the month before the first month in 2026 in which the European gas price (World Bank, monthly) exceeds its average over the previous 12 months by 50% or more. Tests 1 and 2 are run at the horizons the data allow at the time of estimation and reported as early evidence.

The main sample is the 2021 to 2025 cycle (h = 48 reaches July 2025, before the change in Eurostat's classification).

**Threats.** Countries chose their regimes, and those with larger exposure or regulated tariffs before the shock may have chosen controls; the exposure control and pre-shock regulated-tariff indicator address part of this. Long-term supply contracts and nuclear-heavy generation change pass-through regardless of policy. HICP measures prices, not bills paid, so transfers do not appear; that is the point for tests 1 and 2 but limits welfare statements.

## 7. Possible extension (not part of the frozen tests)

Whether freezes slowed household responses that depend on the price signal (rooftop solar, heat pumps), comparing freezes with quantity-based caps. This depends on finding monthly or quarterly installation data by country.

## 8. Target

A field journal such as *Energy Economics*, *Energy Policy* or *The Energy Journal*; possibly *European Economic Review* if the dataset and the 2026 episode make a strong combination.

## 9. Amendments

1. **8 November 2026: subsidies on the unit price** (regime coding rule, Amendment 1). Threshold compensation up to a quantity limit is coded 2, without a binding limit 1, and fixed per-kWh subsidies 4. Adopted before any price index was examined; tests are reported with and without the five countries affected.
2. **11 November 2026: cases from the source checks** (regime coding rule, Amendment 2). Eight coding questions left open by the checks against primary sources were decided before any price index was examined. Months marked `formula_driven` (a levy cut produced by the levy's own formula), `endogenous_trigger` (a rate that switches with the wholesale price or the CPI) or `opt_in` (an optional regulated offer) are reported with and without in tests 1 to 3. The coded files were then frozen on 12 November 2026 (`data/classification/freeze_manifest.csv`).
3. **12 November 2026: gas outcome and currency of the wholesale prices.** Decided after the outcome series were downloaded but before any price value was examined (only counts of observations were printed). Results are reported under both the original and the amended specification.
   - *Gas outcome.* Section 6 used HICP item 04.5.2 (gas), which also includes bottled liquefied hydrocarbons. Their prices follow oil, they were rarely controlled, and in some countries (Malta, Cyprus) they make up the whole item, while the coded regimes refer to piped gas. The main specification now uses 04.5.2.1 (natural gas and town gas), with its own 2021 HICP weight (UK: ONS series L7E9, weight L89X). Countries without that index (Cyprus, Malta, Finland, Norway, Iceland) use electricity alone. Item 04.5.2 is kept as a robustness check.
   - *Currency.* Section 6 did not state a currency. The World Bank gas price is in US dollars and Ember's electricity prices are in euros, while households pay in their own currency. In the main specification both wholesale prices are converted to each country's currency with Eurostat monthly average exchange rates (`ert_bil_eur_m`): the gas price as USD/MMBtu divided by USD per EUR, times national currency per EUR. For countries that adopted the euro during the sample (Croatia on 1 January 2023, Bulgaria on 1 January 2026), the national-currency series is continued at the irrevocable conversion rate. Robustness: both prices in euros for every country. Dollars are not used. Because W(c,h) is a log change from the base month, fixed differences in price levels or income between countries cancel; differences in the importance of energy are carried by the country weights w_e and w_g.
   - *Literature check (13 November 2026).* Every reference in section 2 was checked against its source; results and corrected wording are in [`literature_verification.md`](literature_verification.md). Two descriptions in section 2 are wrong (European Commission DP 197 does not treat regulated-price countries as a group; the Erceg et al. abstract does not say subsidies first lower headline inflation and then make it more persistent), Xie and Huang (2026) could not be located, and the unnamed IMF working paper was not found. Section 2 is to be cited only in the corrected form.
   - *Correction (13 November 2026).* Two statements in this amendment did not match what the code did from the start; no result changes. (a) The gas outcome is used only where the regime coding has a household gas series. Cyprus has an 04.5.2.1 index for 2019 to 2025 but no piped household gas, and Sweden has an index but household gas was coded as negligible, so both enter with electricity alone, as do Malta, Finland, Norway and Iceland. (b) Eurostat no longer serves the lev and kuna; those two exchange rates come from the ECB (series M.BGN.EUR.SP00.A and M.HRK.EUR.SP00.A).
4. **17 November 2026: third-party text and data removed for publication** (regime coding rule, Amendment 4). Bruegel measure names and tracker extracts, and the World Bank European gas prices (sourced partly from Bloomberg), are no longer committed; the code rebuilds them from the downloads listed in `data/raw/README.md`. No test, estimate or code changes.
