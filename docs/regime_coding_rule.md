# Rule for coding retail energy price regimes

**Status:** frozen with the research design (date in [research_design.md](research_design.md)). Changes are logged at the end as dated amendments with their reason; results are reported under the original and the amended coding.

## 1. Unit and scope

- One record per country, product and month, for household electricity and household gas separately, January 2019 to the latest month with price data.
- Countries: EU-27, Norway, Iceland and the UK.
- Only measures that apply to households count. Measures for firms only are recorded in a note but do not change the household code.

## 2. Categories

Each country-product-month receives one main code from the list below, plus flags for any other measure in force.

1. **Freeze or cap below cost.** A legal or regulatory limit on the unit price (per kWh) that applies to all of a household's consumption and is set below what the supplier's costs or the regulator's normal formula would give, or a regulated tariff whose scheduled update is suspended or limited by government decision. Example of the type: France's limit on regulated tariff increases under the tariff shield.
2. **Quantity-based cap.** A limit on the unit price for a share of consumption (for example a share of past use) with consumption above that share paid at the contract price. Example of the type: Germany's electricity and gas price brakes in 2023.
3. **Lagged formula cap.** A cap that follows supply costs through a published formula with a delay of at least one month and no government decision to hold it below the formula. Example of the type: the UK's default tariff cap, reset each quarter (each half-year before October 2022).
4. **Tax or levy cut.** A reduction in VAT, excise or a levy on household electricity or gas (including the removal of a renewables levy from the bill).
5. **Transfers only.** Payments or bill credits that do not change the unit price (lump sums, fixed credits per household, income support).
6. **None.**

**Precedence when several measures are in force:** the main code is the first that applies in the order 1, 2, 3, 4, 5, 6. Every other measure in force is recorded as a flag, so tests can use either the main code or the flags.

**Regulated tariffs before the shock.** A regulated or approved tariff that follows its normal formula with no government limit is coded 3 if the formula passes costs through with a lag of at least one month, and 6 otherwise. It becomes code 1 only from the month a government or regulator decision limits it below the formula.

## 3. Dates

- **Start:** the first month in which the measure applies to household bills. A measure that starts on or before the 15th applies to that month; one that starts after the 15th applies from the next month.
- **End:** the last month in which it applies, by the same rule.
- **Scheduled increases:** each dated increase in a controlled price (for example a step-up in a regulated tariff that remains below cost) is recorded with its month and its announced size in percent. These, together with ends of codes 1 to 3, are the events for test 2 of the design.
- Announcement dates are recorded in a separate column but are not used to code the regime.

## 4. Coverage

- **Share of households covered:** where the measure applies only to some contracts (for example regulated-tariff customers only), the share of household customers on those contracts in the last year before the measure, from the national regulator or the ACER/CEER retail monitoring reports. A measure covering less than 50% of household customers is flagged and coded under its type; tests report results with and without such country-months.
- **Social or targeted tariffs** limited to low-income households are coded 5 (transfers) unless they cover more than 50% of households.

## 5. Sources and evidence

- **Order of sources:** (1) the legal text or regulator decision; (2) a government or regulator press release; (3) Bruegel's national policies tracker (2021 to 2023) or its 2026 tracker; (4) IEA, OECD or European Commission summaries; (5) reputable news reports.
- Each record carries the source URL, the page or article reference, the evidence level (primary for 1 and 2, secondary for 3 to 5) and the date the source was read.
- A record supported only by level 5 sources is flagged and checked against a primary source before estimation; if none is found, it is reported as unverified and tests are run with and without it.

## 6. What is not coded

- Measures for district heating, heating oil or motor fuels.
- Wholesale market interventions (for example a cap on inframarginal generator revenue) unless they change the household unit price directly; Spain's and Portugal's gas price cap for power generation is recorded as a flag, with the household code set by what happened to household tariffs.

## 7. Process

1. Draft the coding from sources 1 to 3 for every country, without looking at any price index.
2. Check every code against a primary source where one exists.
3. Freeze the coded file (`data/classification/regimes.csv`) with a dated commit before the outcome series are downloaded for estimation.

## Amendments

**Amendment 1 (8 November 2026): subsidies on the unit price.** While coding, eight measures did not fit section 2: per-kWh subsidies on all consumption (Greece, Cyprus) and state compensation of the part of the price above a threshold (Norway, Lithuania, Estonia). They are classified as follows:
1. Compensation of the price above a threshold that applies only up to a quantity limit, with consumption beyond the limit at the contract price, is code 2 (as a quantity-based cap).
2. The same compensation with no quantity limit, or with a limit above the consumption of most households, is code 1 (it works as a cap on all consumption).
3. A fixed subsidy per kWh on the bill, not tied to a threshold price, is code 4 (treated as a levy cut).

Reason: these measures change the unit price households pay, and without a rule they would be coded 5 or 6, which misstates them. Adopted before any price index was examined. Tests are reported with and without the countries whose codes rest on this amendment (Greece, Cyprus, Norway, Lithuania, Estonia).

**Amendment 2 (11 November 2026): cases left open by the primary-source checks.** Checking every code against primary sources left eight cases that sections 2 to 4 do not settle. They are decided as follows, before any price index was examined:
1. *Permanent tax reforms that offset a crisis cut.* A temporary tax cut made permanent together with an offsetting increase in another tax on the same bill ends as code 4 in the last month before the reform (Belgium electricity and gas: code 4 ends 2023-03).
2. *Formula-driven levy cuts.* A levy on the bill that falls because its own formula responds to high wholesale prices is code 4, with the flag `formula_driven` (Ireland's PSO levy from 2022-10).
3. *Tax relief paid only at annual settlement.* Coded for the months of supply it applies to (Czechia, VAT waiver for 2021-11 and 2021-12), subject to a check of how the statistical office recorded it in the HICP; if it was not recorded in those months, the code is revisited before the freeze.
4. *Optional regulated offers.* An opt-in regulated price below market is coded under its type with the take-up share as coverage, so that a take-up below 50% gets the low-coverage flag (Estonia's universal service from 2022-10; as for Norway's Norgespris).
5. *Measures whose rate depends on the wholesale price or the CPI.* Coded month by month as they applied, with the flag `endogenous_trigger`; tests are reported with and without the flagged country-months (Spain electricity VAT in 2024; Spain's 2026 cuts).
6. *Regulated tariffs found in the baseline check without a coded row.* Coded 3 or 1 from the regulator's tariff decisions once read (Latvia gas).
7. *A state-owned supplier holding its price before any legal limit.* Code 1 from the month a government decision commits to holding the price, if its text confirms it; code 6 before (Croatia electricity: from the April 2022 package, to confirm).
8. *Baseline disagreements with ACER/CEER.* National regulator sources take precedence; where none explain the disagreement, they are sought before the freeze (Greece gas).

The flags `formula_driven` and `endogenous_trigger` are recorded in the column `special_flags` of `regime_measures.csv` and carried to `regimes.csv`.

**Amendment 4 (17 November 2026): third-party text removed for publication.** Bruegel publishes its trackers under Creative Commons Attribution-NoDerivatives 4.0, which does not allow altered copies to be redistributed. `tracker_reconciliation.csv` no longer carries the Bruegel measure names; each candidate is identified by its tracker file and row number, which point to the unaltered Bruegel files cited in `data/raw/README.md`. The extracts `tracker_measures_2021_2023.csv` and `tracker_measures_2026.csv` are regenerated locally by `code/01_extract_policy_trackers.py` and are no longer committed. No code, date or disposition changes, and no estimate uses these files. The freeze manifest is rewritten in a separate commit to record the new checksum of `tracker_reconciliation.csv`; the other four frozen files are unchanged.
