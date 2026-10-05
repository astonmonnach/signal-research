# Long-term nth-order research, 5 Oct 2026 (6–36 month horizon)

*Research with method verdicts. It is not advice. Written 5 Oct 2026 after the US close.*

## Verification and the v3 gates (added after the research run, 5 Oct evening)

**Spot-checked against the primary sources before publishing:**
- **USAspending, stockpile IDIQs:** 21 stockpile (`SP8000`) IDIQs from Aug 2025 to Jul 2026. Their award records give ceilings totalling exactly **$6.29bn**.
- **USAspending, FY2026 funded orders:** they search to **$1.14bn**, which includes a few older-numbered orders. Each of these matches: Glencore $240.3M + $210.3M = $450.6M, ICF $150.0M, Cliffs $100.0M, CBMM $90.1M, Largo $60.1M, UAMY DO4 $30.0M.
- **SEC XBRL, AAON:** cash $0.01M and a $435.0M line of credit at 30 Jun 2026.
- **SEC XBRL, MTUS:** cash $108.6M and H1 2026 revenue of $649.3M.

**Gates LT1–LT6** ([skill v3](../../.claude/skills/nth-order/SKILL.md), [longterm/METHOD.md](../../longterm/METHOD.md)) were written while this run was in progress. Applied to the two "watch" names:
- **MTUS stays watch (7).** LT2 passes: cash $108.6M plus $286.2M of ABL availability ≈ $395M, against 2 × $97.6M of TTM FCF burn ≈ $195M, and there is no debt. LT4 is not met yet, because EV/sales is at the top of its own range. Review at Q3 on 6 Nov.
- **AAON becomes a kill (LT2 fail).** Cash is about $0 and $165M is undrawn on the $600M revolver, against about $238M of FCF burn over two years.
  - The burn is growth capex: operating cash flow is positive.
  - Changing LT2 to use operating cash flow would be a dated rule change for every name, not something to do for one name. Until then the gate stands as written.
  - AAON stays logged in the ledger with its verdict.

So `longterm/candidates.csv` holds **MTUS only (watch)**. All eight names are logged in `ledger/manual_calls.csv` as `longterm_research` with their verdicts.

---

**Method.** The nth-order skill v2 (`.claude/skills/nth-order/SKILL.md`), the METHOD.md gates G1–G5 with the 0–10 card, and the six long-term checks in [`longterm/METHOD.md`](../../longterm/METHOD.md):
1. Is the theme in the reported numbers?
2. Can the balance sheet survive two bad years?
3. How much dilution over 3 years?
4. Has it already run, judged on 1y and 3y moves against SPY and valuation against its own history and two peers?
5. Is it liquid enough?
6. Does it beat SPY and its sector ETF?

**Sources.** Every number comes from an SEC filing, a company release, USAspending or Yahoo daily closes. Numbers I calculated are marked **[computed]**. "Not disclosed" means I looked in the named source and the number isn't there.

## The answer

| ticker | theme | role | score | verdict | the reason in one line |
|---|---|---|---|---|---|
| **MTUS** | A | Sole-source HF-1 shell steel for the stockpile | 7 | **watch** | A funded $125M order, no debt, and no price run against SPY. But defence is only 17% of sales and EV/sales is at the top of its own 5-year range. |
| **AAON** | B | BASX data-centre liquid cooling | 5 | watch → **kill under LT2** (see above) | Data centres are 55% of sales and revenue doubled, yet EV/sales is at the bottom of its own range. Margin guidance was cut, there is no cash, and free cash flow is negative. |
| MOD | B | Data-centre cooling, with a $165M customer deposit | 7 | already run | +308% in 3 years (spin-adjusted, +221 pts vs SPY), in step with VRT. EV/sales is at the top of its own range. |
| VRT | B | The first-order name in data-centre power and cooling | 4 | already run | +540% in 3 years (+453 pts vs SPY), at 8.5× sales against a 5-year median of 3.5×. It fell 17% on the day it raised guidance. |
| MP | A | Rare earths, with a DoW price floor, equity and offtake | 8 | already run | The theme shows up as DoW "price protection" income, but EV/sales is 25.6× against a 10.9× 5-year median. The stock is still +56% above its price before the DoW deal. |
| ELMT | A | Tungsten and molybdenum, with DoW preferred equity | 8 | already run | The DoW money was priced in one session (+32.8% on 14 Sep). Stockpile revenue is a 2029+ story, and 68% of the shares unlock around 19–22 Oct. |
| UAMY | A | Antimony ingots for the stockpile | 9 | kill | It has the best card on paper ($57.3M of funded orders against $36.4M of trailing revenue), but it fails the long-term checks. TTM free cash flow was −$71M against $62M of liquidity, diluted shares rose 41% in 3 years, and antimony fell about 62%. |
| CLF | A→B | Transformer steel (DR-GOES) for the stockpile | 5 | kill | Fails G1: the $100M stockpile order is 0.5% of revenue. Debt is $7.7B and free cash flow is negative. |

**No name reaches "long-term candidate".** The three best theme cards (UAMY 9, MP 8, ELMT 8) all fail the long-term overlay: two are already priced, and one can't fund itself. This is METHOD failure mode 1 (arriving after the re-rating) and failure mode 6 (dilution) together. The names the market has **not** re-rated (MTUS, AAON) each have a dated test before the end of 2026.

## How the numbers were built

- **Prices.** Yahoo chart API, daily closes to 5 Oct 2026.
  - Returns are total returns (Yahoo adjusted close). 1y runs from the close on or before 5 Oct 2025; 3y from the close on or before 6 Oct 2023.
  - "vs SPY" is the stock's return minus SPY's return, in percentage points (pts).
  - Over those windows SPY returned +17.0% (1y) and +87.0% (3y).
- **MOD spin.** Yahoo does not adjust MOD for the 1 Oct 2026 spin. Each MOD share received 0.44619 THRM (×$32.23 = **$14.38**), and that value is added back.
- **EV/sales history [computed].** Calculated at 19 quarter-ends, Dec 2021 to Jun 2026, from SEC companyfacts XBRL: trailing-12-month (TTM) revenue, cash plus short-term investments, total debt, and cover-page shares × the Yahoo close on that date.
  - AAON's 2023 3:2 split is adjusted.
  - "Now" uses the 5 Oct close, the latest cover-page share count, and the latest 10-Q balance sheet and TTM revenue.
- **Dilution.** Diluted weighted-average shares for the quarter to 30 Jun 2023, compared with the quarter to 30 Jun 2026 (XBRL).
- **Free cash flow (FCF).** TTM operating cash flow minus TTM capex (XBRL). Where the XBRL tag is missing, it comes from the 10-K/10-Q cash-flow statement.
- **Liquidity.** Average daily dollar volume over 63 sessions.

---

## Theme A: the build-out of US critical minerals and the National Defense Stockpile

### 1. What it is

- **The money.** P.L. 119-21 §20004(a)(40) puts **$2,000,000,000** into the National Defense Stockpile (NDS) Transaction Fund, available until 30 Sep 2029 ([govinfo](https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm); verified in `stocks/MTUS.md`).
- **The September 2026 awards** (verified in the repo; [DoD, 25 Sep](https://www.war.gov/News/Contracts/Contract/Article/4612013/contracts-for-sept-25-2026/)):
  - ELMT: tungsten, $2bn ceiling with a $150M guaranteed minimum, plus a $35.6M wire contract.
  - MTUS: HF-1 steel, $995M ceiling with a **$125M funded first order**.
  - Rio Tinto: high-purity aluminium, $995M.
- **Department of War (DoW) equity.**
  - ELMT: $200M of preferred (up to $450M), plus warrants for 24.84% of the common ([8-K, 14 Sep](https://www.sec.gov/Archives/edgar/data/2101698/000121390026099734/ea0304682-8k_elmet.htm)).
  - MP: $400M of convertible preferred (13,320,013 shares at $30.03), a warrant for 11,201,659 shares at $30.03, a $150M loan due 2037, and a 10-year NdPr price floor of $110/kg ([MP 10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1801368/000180136826000048/mp-20260630.htm), Notes 3 and 16).
- **New today, from USAspending.** The stockpile office (award IDs `SP8000-…`) signed **21 further IDIQs between Aug 2025 and Jul 2026, with ceilings totalling $6.29bn**. It placed **about $1.06bn of funded delivery orders in FY2026** (Oct 2025 to Jul 2026).
  - Source: USAspending `spending_by_award` and `awards/` endpoints, queried 5 Oct.
  - DoD data there lags by about 90 days, so the August and September orders (including MTUS's $125M) are not in it yet.

### 2. What it means: follow the money

**Largest funded stockpile orders, FY2026 (USAspending)**

| recipient | material | IDIQ ceiling | funded orders | listing | order vs recipient revenue |
|---|---|---|---|---|---|
| Glencore | cobalt | $1,800M (not competed, 14 May 2026) | **$450.6M** (DO1 15 May, DO2 29 Jun) | LSE; no US listing | immaterial (not computed) |
| ICF Mercantile | aerospace rayon | $400M | $150.0M | private | — |
| Cliffs Steel (CLF) | DR-GOES transformer steel | $400M (sole bid) | $100.0M (1 Jul 2026) + $2.0M (Sep 2025) | NYSE | 0.5% of TTM revenue **[computed]** |
| CBMM North America | ferroniobium | $160M | $100.1M | private (Brazil) | — |
| Largo (LGO) | vanadium pentoxide | $125M | $60.1M (Jul 2026) | Nasdaq/TSX | ~34% of annualised Q2 revenue; **going-concern language** |
| US Antimony (UAMY) | antimony ingots | $245M | $57.3M in total (DO1 $9.9M Sep 2025; DO2 $1.9M; DO3 $15.4M; DO4 $30.0M Jun 2026) | NYSE American | 157% of TTM revenue **[computed]** |
| Rio Tinto | scandium oxide; high-purity aluminium | $40M; $995M | $29–54M (one scandium order appears twice, as an original and a "re-award") | NYSE ADR | immaterial |
| Global Advanced Metals | tantalum, niobium | $100M + $150M | $35.3M | private | — |

Evidence: the UAMY IDIQ is [CONT_IDV_SP800025D0007](https://www.usaspending.gov/award/CONT_IDV_SP800025D0007_9700/) and the Cliffs order is [SP800026F0033](https://www.usaspending.gov/award/CONT_AWD_SP800026F0033_9700_SP800025D0008_9700/). Largo's order and liquidity are in its [Q2 MD&A](https://www.sec.gov/Archives/edgar/data/1400438/000106299326004425/exhibit99-2.htm).

**What this means for the theme:**

- **Ceilings are about 4.6× the money.**
  - $6.29bn (Aug 2025 to Jul 2026) + ELMT $2bn + MTUS $995M ≈ **$9.3bn of ceilings against $2bn [computed]**.
  - It is about $8.3bn if the twin Rio Tinto and Arconic $995M aluminium IDIQs share one ceiling. Both came from the same 3-offer competition on 8 May 2026, and Arconic is private.
  - The repo's "≈$4.0bn" counted only the September batch.
- **Funded orders are what matter, and they already use a lot of the pot.**
  - About $1.06bn (FY2026 to July) + MTUS $125M ≈ $1.19bn ordered. Adding ELMT's $150M guaranteed minimum gives ≈$1.34bn committed **[computed]**.
  - If all of it is charged to the $2bn (not verified: the fund has other inflows), **about two-thirds of the pot is committed with three years of availability left**.
  - Second orders for MTUS and ELMT compete with cobalt, rayon, GOES and niobium for the rest.
- **The biggest cheque went to a name a US investor can't usefully own.** Glencore's $450.6M of cobalt is immaterial to Glencore and has no US listing. Most of the other large recipients are private.
- **Orders are priced at market, so the commodity matters.**
  - UAMY's delivery orders are "fixed price with economic price adjustment" (USAspending). Its IDIQ is priced "based on prevailing market rates" ([10-Q](https://www.sec.gov/Archives/edgar/data/101538/000110465926094035/uamy-20260630x10q.htm), Note 1).
  - Antimony spot fell from "exceeded $28 per pound" in late 2025 to "approximately $10.50 per pound" in Q2 2026 ([UAMY Q2 release](https://www.sec.gov/Archives/edgar/data/101538/000110465926094130/tm2622899d1_ex99-1.htm)).
  - No free daily price exists for antimony, tungsten, HF-1 or NdPr (`SOURCES.md`). The steel proxy for HF-1, HRC=F, was $1,321 on 5 Oct, +64% in a year.

### 3. Who is affected (impact −5…+5)

| name | impact | why |
|---|---|---|
| MTUS | +3 | Sole-source, with a funded $125M order. Defence is 17% of sales and growing. Second orders compete for a shrinking pot. |
| ELMT | +3 | DoW equity plus a $150M guaranteed minimum. Already priced; deliveries start only "when sufficient incremental supply becomes available". |
| MP | +2 | The DoW floor is in reported numbers, but the subsidy shrinks as market prices rise toward $110/kg: price-protection income was $42.3M in Q1 and $17.6M in Q2 2026 **[computed from the 10-Q]**. |
| UAMY | +1 | $57.3M of orders, but antimony is down about 62% and the company is burning cash. |
| CLF | +1 | A real chokepoint for transformers, but immaterial at Cliffs' scale. |
| Any later stockpile awardee | −1 | Ceilings are about 4.6× the money. The next order depends on the next appropriation. |

### 4. Near future: dated catalysts

| date | event | names | source |
|---|---|---|---|
| ~19–22 Oct 2026 | ELMT IPO lock-up ends: ~20.6M shares (68% of outstanding) | ELMT | 424B4, via `stocks/ELMT.md` |
| 6 Nov 2026 | MTUS Q3 results and 10-Q: first look at the $125M order in backlog, defence tons and any second order | MTUS | repo calendar |
| by 9 Nov 2026 | MP Q3 10-Q: trend in price-protection income, 10X capex | MP | SEC 40-day deadline |
| by 9–16 Nov 2026 | UAMY Q3 10-Q. The company guided "a minimum of $9.0–$10.0 million of additional sales, all to the US Government" in Q3 | UAMY | [11 Aug release](https://www.sec.gov/Archives/edgar/data/101538/000110465926094130/tm2622899d1_ex99-1.htm) |
| ~13 Nov 2026 | Resale shelf for the DoW warrant shares due | ELMT | 8-K 14 Sep, via `stocks/ELMT.md` |
| 1 Jan 2027 | DFARS restrictions on Chinese-origin tungsten and magnets begin | ELMT, MP | ELMT deck (repo) and METHOD.md calendar; not re-verified here |
| by ~15 Feb 2027 | NDS Annual Materials Plan (quantities by material) | all | repo note; statutory date not re-verified |
| 30 Sep 2029 | The $2bn stops being available | all | P.L. 119-21 |

**Scenarios**
- **Bull.** Congress tops up the Transaction Fund, and ceilings turn into orders.
  - Precedent: the $2bn in P.L. 119-21 itself.
  - Signals: a new appropriation line, a second MTUS delivery order, ELMT's first delivery order.
- **Base.** Orders continue at the FY2026 pace (~$1bn in ten months) until the pot is used up in 2027. Most ceilings stay unused options.
- **Bear.** The pot runs dry first, and market-priced orders shrink with their commodity.
  - Precedent: UAMY cut 2026 revenue guidance from $125M to $60–75M on 11 Aug and fell −24.5% the next day (REMX +0.4%, SPY +0.3%).

**Signals to watch:** USAspending `SP8000-26-F…` orders appearing for MTUS and ELMT; the NDS Annual Materials Plan; antimony and tungsten prices in company releases.

### Candidate table, Theme A

Benchmarks: SPY; sector ETFs SLX (steel), REMX (rare earth and strategic metals) and XME (metals and mining).

| ticker | evidence (primary) | theme exposure | balance sheet (latest 10-Q) | 3y dilution | 1y / 3y vs SPY (vs sector) | valuation vs own history and peers | gates | score | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **MTUS** | [29 Sep release ($125M order)](https://investors.metallus.com/news/news-details/2026/Metallus-Awarded-995-million-Contract-for-Critical-Defense-Applications-from-U-S--Defense-Logistics-Agency-Receives-Initial-125-Million-Delivery-Order/default.aspx); [10-Q Q2](https://www.sec.gov/Archives/edgar/data/1598428/000119312526332244/mtus-20260630.htm) | A&D 17% of H1 2026 sales ($112.0M of $649.3M). HF-1/stockpile revenue not disclosed separately. The order is 10% of TTM revenue **[computed]** | Cash $108.6M; no borrowings; $300M ABL to 30 Jun 2031 ($286.2M available). TTM FCF **−$97.6M** (OCF $6.0M, capex $103.6M; the Army's $99.75M capacity funding is now fully received). **Pass** | **−8.9%** (47.3M → 43.1M) | 1y +7.8 pts (SLX −18.7); 3y **−87.5 pts** (SLX −79.3) | EV/S **0.62×** vs its own 0.30–0.60× (median 0.45×), so at the top of its range. Peers: CMC 1.12×, CRS 6.32× | G1 pass (narrow), G2 pass, G3 pass on price (valuation flag), G4 pass, G5 pass: $7.3M/day, but **small cap, $0.87bn: flag** | **7** (0/2/1/2/2) | **watch** |
| ELMT | [8-K 14 Sep](https://www.sec.gov/Archives/edgar/data/2101698/000121390026099734/ea0304682-8k_elmet.htm); [10-Q (to 3 Jul)](https://www.sec.gov/Archives/edgar/data/2101698/000162828026056460/elmt-20260703.htm) | Aerospace, defence and government 39.3% of Q2 revenue. $150M guaranteed minimum (≈66% of LTM revenue of $228.5M), with no delivery order yet | At 3 Jul: cash $66.1M, debt $10.4M. Then +$200M DoW cash (14 Sep) and −$124.75M for the Masan stake. H1 FCF −$10.7M; no TTM figure (IPO). DoW terms ban dividends and share repurchases | n/a (IPO Apr 2026). Warrants: DoW 7.57M (24.84%), Blue Moon 1.17M, Cantor ~0.15M | Since the 23 Apr first close: +18.9% vs SPY +9.9% and XME −8.3%. +52% vs the $14 IPO price | EV/S ≈2.6× LTM **[computed, 3 Jul balance sheet]**; no 5-year history. Peers: CRS 6.32×, ATI 5.88× | G3 **fail** (+32.8% on 14 Sep on ~42× volume), others pass. **Small cap, ~$0.65bn: flag** | 8 | **already run** |
| MP | [10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1801368/000180136826000048/mp-20260630.htm) | 100% rare-earth products. DoW price-protection income $59.9M in H1 2026 (30% of H1 revenue of $199.1M) | Cash and short-term investments $1.45bn; debt $934.6M ($747.5M of 3.00% convertible notes due **Mar 2030**, conversion price ~$21.74; $150M DoW loan due 2037). TTM FCF **−$504.6M** (capex $420.6M for the 10X magnet plant). Pass, with heavy capex | +0.3% weighted, but this excludes potential shares: 13.32M (preferred), 11.20M (warrant) and ~34.4M (2030 notes) ≈ **+33%** if all convert **[computed]** | 1y −51.5 pts (REMX −22.7); 3y +92.1 pts (REMX +173.3) | EV/S **25.6×** vs its own 6.7–47.0× (median 10.9×). Peers: UUUU 31.4×, UAMY 14.5× | G3 **fail**: +50.6% on the DoW deal day, 10 Jul 2025 (REMX +8.7%), and still +56% above the $30.03 pre-deal close | 8 (2/2/0/2/2) | **already run** |
| UAMY | [Q2 release](https://www.sec.gov/Archives/edgar/data/101538/000110465926094130/tm2622899d1_ex99-1.htm); [10-Q](https://www.sec.gov/Archives/edgar/data/101538/000110465926094035/uamy-20260630x10q.htm); [USAspending IDIQ](https://www.usaspending.gov/award/CONT_IDV_SP800025D0007_9700/) | Antimony is 75% of Q2 revenue. $57.3M of DLA orders against $36.4M of TTM revenue. Only $2.6M recognised so far (July, Q3) | Cash $41.4M + $20.7M of debt securities = $62.1M; debt ~$0.5M. TTM FCF **−$71.3M** (OCF −$28.1M, capex $43.2M). The 10-Q plans to fund needs partly with "capital raised from various investment vehicles". **Fail** | **+41.0%** (107.65M → 151.75M) | 1y −66.1 pts (REMX −37.2); 3y **+941.5 pts** (from $0.35) | EV/S 14.5× vs its own 0.9–32.0× (median 4.1×). Peers: MP 25.6×, UUUU 31.4× | G1, G2, G4 pass. G3 fail on the 3y run. G5 pass ($32.2M/day; **small cap, $0.59bn: flag**). **Overlay fail: balance sheet and dilution** | 9 (2/2/1/2/2) | **kill** |
| CLF | [10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/764065/000076406526000100/clf-20260630.htm); [USAspending order](https://www.usaspending.gov/award/CONT_AWD_SP800026F0033_9700_SP800025D0008_9700/) | "Stainless and electrical steel" is 10.0% of Q2 revenue ($525M of $5,226M). GOES is **not disclosed** separately. The stockpile order is 0.5% of TTM revenue | Cash $70M; debt $7.70bn (ABL $895M due by Jun 2028 at the latest; $1.27bn of notes due 2029). TTM FCF **−$857M**. **Fail** | +11.1% (514M → 571M) | 1y −21.3 pts (SLX −47.9); 3y −108.3 pts | EV/S 0.76× vs its own 0.49–0.98× (median 0.62×). Peers: STLD 1.86×, NUE 1.70× | **G1 fail** | 5 (0/2/0/2/1) | **kill** |

Score order in brackets: revenue exposure / substitution difficulty / coverage / demand visibility / behavioural signal (each 0–2).

### Kills and already-run names in Theme A

- **ELMT: already run.** It has the strongest behavioural signal in the theme: the customer put $200M of equity in.
  - But that was priced in one session: +32.8% on 14 Sep.
  - Stockpile deliveries begin only when new supply exists, which means the Springer APT restart targeted for 1H 2029.
  - About 20.6M shares (68%) unlock around 19–22 Oct.
  - Re-test after the lock-up, on the same evidence (`stocks/ELMT.md`).
- **MP: already run.** The theme is real and in the income statement: $59.9M of H1 price-protection income, plus DoW equity, a loan and an offtake.
  - The price already holds it. EV/sales of 25.6× is 2.3× its own 5-year median.
  - The stock is still +56% above its price before the deal, even after falling 52.5% from the $98.65 peak (14 Oct 2025).
  - The subsidy is shrinking as NdPr prices rise toward the floor.
  - Potential dilution of about 33% sits outside the diluted share count, because those shares are anti-dilutive while MP makes losses.
- **UAMY: kill.** The best theme card in the set, and the clearest long-term failure.
  - The company guided Q3 sales of at least $9–10M, all to the US Government. 2026 revenue guidance was cut from $125M to $60–75M.
  - The CFO was terminated on 30 Sep, and the 2 Oct 8-K says this was "not related" to results ([8-K](https://www.sec.gov/Archives/edgar/data/101538/000110465926113034/tm2626607d2_8k.htm)).
  - A $100M share-repurchase authorisation (8-K, 19 Aug) exceeds its $62.1M of cash and investments.
  - The stock closed on 5 Oct at its 52-week low of $3.95, −77% from the $17.47 peak, yet still 3.5× its own median EV/sales.
- **CLF: kill on G1 and the balance sheet.** This is the cross-theme find: the stockpile is buying transformer steel (Theme B's power chain), and Cliffs' own 10-Q ties transformer shortages to AI. Even so, GOES is a sliver of a $19.2bn steel business carrying $7.7bn of debt and negative FCF. This is METHOD failure mode 3 again: the right node, the wrong instrument.

---

## Theme B: data-centre power and cooling

### 1. What it is

- **MOD (Modine, soon Modexus).**
  - Data Centers sales were $348.6M in Q1 FY27 (+90%), **57% of continuing segment sales** ([Q1 release](https://www.sec.gov/Archives/edgar/data/67347/000110465926088230/mod-20260729xex99d1.htm)).
  - A long-term capacity agreement guarantees capacity for "more than $4 billion" in 2027–2029. The [10-Q](https://www.sec.gov/Archives/edgar/data/67347/000110465926088569/mod-20260630x10q.htm) says MOD "received a $165.0 million up-front deposit". The agreement was entered "during March 2026" and announced on 26 May.
  - The RMT with Gentherm closed on 1 Oct: $156M of cash came in to prepay borrowings.
  - Analyst and Investor Day on **18 Nov**.
- **VRT (Vertiv).**
  - Backlog was **$15.0bn at Dec 2025, against $7.2bn a year earlier** ([10-K](https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm)).
  - FY2026 guidance is $14.0bn of net sales (midpoint) and adjusted EPS of $6.65–6.75 ([29 Jul release](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)).
  - It is acquiring UIG (microgrids and behind-the-meter power) for $1.45bn plus up to $1.15bn of earn-out, with closing expected in Q4 2026 ([8-K, 2 Sep](https://www.sec.gov/Archives/edgar/data/1674101/000119312526379306/d472406dex991.htm)).
- **AAON.**
  - BASX-branded sales were $344.8M, **55% of Q2 2026 sales** of $627.0M.
  - BASX backlog is $1.43bn (+185% y/y) out of $1.97bn in total.
  - The 10-Q says "Our BASX brand is heavily dependent on the data center market" ([10-Q](https://www.sec.gov/Archives/edgar/data/824142/000082414226000055/aaon-20260630.htm)).
- **Third order, on the power side.** Transformers need grain-oriented electrical steel. Cliffs' 10-Q says the transformer shortage "will continue to be exacerbated by the anticipated widespread adoption of AI". The stockpile ordered $100M of DR-GOES on 1 Jul 2026 (Theme A table).

### 2. What it means

- **Demand is in the reported numbers at every link. The issue is price.**
  - VRT is up +540% in 3 years and MOD +308% (spin-adjusted). Both sit at or near the top of their own EV/sales ranges.
  - From their May–June highs, VRT is −32.6%, MOD −35.7% (adjusted) and AAON −43.1%.
- **The 29 Jul test.** VRT raised full-year guidance and fell **−17.3%**.
  - The same day: MOD −14.4%, AAON −9.5%, NVT −5.7%, TT −4.9%, XLI −3.2%, SPY −1.5%.
  - When a guidance raise brings a −17% day, the price was already carrying more than the raise. The selling spread through the whole peer group, which is the skill's contagion rule in action.
- **AAON is the exception.**
  - Revenue doubled (+101% in Q2) while EV/sales fell to the bottom of its own 5-year range.
  - The filings show why:
    - Gross-margin guidance was cut from 27–28% to 25–26%.
    - Backlog fell 7.4% quarter on quarter, which the company attributes to lumpy BASX awards and faster conversion.
    - Customer deposits fell from $80.7M to $12.8M in H1.
    - TTM FCF is −$118.8M, with capex funded by the revolver.
- **Second order: MOD's suppliers.** Q1 margins were hit by "supply chain constraints", but no listed supplier is named in MOD's filings (absence). A full-text EDGAR search for "Modine" as a named customer is the next step. It was not run in this pass.

### 3. Who is affected (impact −5…+5)

| name | impact | why |
|---|---|---|
| VRT | +3 | The first-order name. Backlog doubled and the balance sheet is net cash. Priced. |
| MOD | +3 | A customer paid $165M for capacity. Priced over 3 years. |
| AAON | +2 | The theme is in the numbers. The price is down; margins and cash flow are the question. |
| CLF | +1 | Transformer steel. Immaterial at Cliffs' scale. |
| THRM | 0 | The spun-off auto-parts business. Outside the theme. |

### 4. Near future: dated catalysts

| date | event | names | source |
|---|---|---|---|
| 7 Oct 2026 | MOD pro forma 8-K/A: first clean continuing-business numbers | MOD | 8-K 1 Oct ("four business days after the Closing Date") |
| by 9 Nov 2026 | Q3 10-Qs for VRT and AAON, and MOD's Q2 FY27. Dates not yet announced in the filings I found | VRT, AAON, MOD | SEC 40-day deadline |
| 18 Nov 2026 | MOD Analyst and Investor Day: new financial targets | MOD | [release, 14 Sep](https://www.prnewswire.com/news-releases/modine-to-host-analyst-and-investor-day-on-november-18-2026-302876675.html) |
| Q4 2026 | VRT expected to close the UIG acquisition | VRT | 8-K 2 Sep |
| by ~1 Jan 2027 | MOD special meeting on the name change to Modexus | MOD | release, 10 Sep |
| 2027–2029 | MOD capacity-agreement delivery years | MOD | 10-Q |

**Scenarios**
- **Bull.** AAON delivers the "sequential margin improvement in the second half" it guided. MOD's 18 Nov targets show the capacity agreement ramping.
- **Base.** Demand holds and multiples compress toward peers (NVT 5.9×, TT 4.8× EV/sales).
- **Bear.** A pause in data-centre capex.
  - Precedent: 29 Jul, when a guidance raise still produced a group-wide sell-off.
  - For AAON specifically, a bear case would land on a revolver-funded, cash-negative balance sheet.

### Candidate table, Theme B

Benchmarks: SPY; sector ETF XLI (industrials).

| ticker | evidence (primary) | theme exposure | balance sheet (latest 10-Q) | 3y dilution | 1y / 3y vs SPY (vs XLI) | valuation vs own history and peers | gates | score | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **AAON** | [10-Q Q2](https://www.sec.gov/Archives/edgar/data/824142/000082414226000055/aaon-20260630.htm); [Q2 release](https://www.sec.gov/Archives/edgar/data/824142/000082414226000052/liveaaonpressreleaseexs.htm) | BASX (data-centre cooling) 55% of Q2 sales. BASX backlog $1.43bn | Cash ~$0.01M; revolver $435.0M drawn of $600M (expires 27 May 2030). TTM FCF **−$118.8M** (OCF $86.5M, capex $205.3M). **Borderline pass** (fails LT2 under v3: see the top of this report) | **+0.3%** (83.47M → 83.72M) | 1y −30.9 pts (XLI −25.3); 3y −37.9 pts (XLI −26.9) | EV/S **3.8×** vs its own 3.8–8.2× (median 5.2×), so at the bottom. Peers: TT 4.8×, NVT 5.9×. TTM P/E ≈43.7× **[computed]** | G1 pass; G2 weak pass (many cooling suppliers); G3 pass; G4 pass; G5 pass ($101.7M/day; $6.95bn) | **5** (2/0/1/1/1) | watch → **kill (LT2)** |
| MOD | [Q1 FY27 release](https://www.sec.gov/Archives/edgar/data/67347/000110465926088230/mod-20260729xex99d1.htm); [10-Q](https://www.sec.gov/Archives/edgar/data/67347/000110465926088569/mod-20260630x10q.htm) | Data Centers 57% of continuing segment sales. $165.0M customer deposit | At 30 Jun: cash $95.3M; debt ≈$530M (revolver $250M and term loan $192.5M, both 2031; 5.9% notes $68.8M due 2029). $156M of RMT cash went to debt on 1 Oct. TTM FCF $100.2M, but ≈−$65M without the deposit (whole company before the spin) **[computed]**. Pass | +1.9% (53.0M → 54.0M) | 1y +16.6 pts (XLI +22.2); 3y **+221.3 pts** (XLI +232.3), spin-adjusted | EV/S ≈4.1× continuing run-rate **[inference: Q1 FY27 continuing segments ×4 = $2.44bn; net debt ≈$0.28bn after prepayment]** vs its own 0.38–4.32× (median 1.65×, whole-company basis). Peers: VRT 8.5×, AAON 3.8× | G3 **fail**: moved with the first-order name (VRT) and sits at the top of its own range | 7 (2/1/0/2/2) | **already run** |
| VRT | [10-K](https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm); [10-Q Q2](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050609/vrt-20260630.htm) | "Primarily for data centers". The **% is not disclosed** in the 10-K or 10-Q. Backlog $15.0bn | Cash $2.81bn; debt $2.94bn (nearest: $850M of 4.125% secured notes due 2028). TTM FCF **$2.93bn**. "Net cash position". Pass | +2.7% (382.35M → 392.75M) | 1y +41.5 pts (XLI +47.1); 3y **+453.1 pts** (XLI +464.2) | EV/S **8.5×** vs its own 1.2–11.2× (median 3.45×). Peers: NVT 5.9×, TT 4.8×. P/E ≈37.9× the FY2026 adjusted-EPS guidance midpoint | G3 **fail** | 4 (1/1/0/1/1) | **already run** |

### Already-run names in Theme B

- **VRT: already run.**
  - The best balance sheet in this report, and a backlog that doubled.
  - But the stock is +453 pts against SPY over 3 years, and EV/sales is 2.5× its own median.
  - The −17.3% reaction to a guidance raise on 29 Jul is the market saying the same thing.
- **MOD: already run on the long-term test.** The event-driven dossier (`stocks/MOD.md`) keeps it on **watch 5/10** for the 7 Oct and 18 Nov dates. That is a different horizon, and both views can hold.
  - For 6–36 months the problem is the move itself: +308% in 3 years in step with VRT, and EV/sales that went from 0.4× to about 4×.
  - Re-test with the clean continuing-business numbers from the 7 Oct 8-K/A and the 18 Nov targets.

---

## Theme C: not added

I found no dated primary-source catalyst outside Themes A and B in this pass. The 1 Jan 2027 DFARS date sits inside Theme A, and the stockpile's GOES order links A to B.

## What the filings do not say (absences)

1. **UAMY's 10-Q and its same-day release disagree.**
   - The 10-Q (filed 11 Aug) says the company "received sales orders… totaling approximately $12 million".
   - The release says "$57.3 Million in antimony ingot orders from the DLA on our books today".
   - USAspending matches the release: DO3 ($15.4M, 9 Jun) and DO4 ($30.0M, 26 Jun) are missing from the 10-Q text.
2. **VRT** does not disclose data centres as a % of revenue in its 10-K or 10-Q.
3. **AAON** flags customer concentration as a risk but gives no customer percentage in its 10-K.
4. **MOD's** continuing-business TTM revenue is not disclosed until the 8-K/A due 7 Oct, and its constrained suppliers are not named.
5. **CLF** does not break out GOES revenue. Its 10-K calls Cliffs "a leading producer of electrical steels in the U.S.", not the only one. The sole-source signal comes from DLA's award ("not available for competition", 1 offer), not from Cliffs.
6. **MP's** realised NdPr price per kg was not found in the 10-Q text.
7. **ELMT** has no delivery order disclosed yet under the $150M minimum.
8. **MTUS** does not split HF-1 or stockpile revenue out of A&D. Q3 (6 Nov) is the first look at the order.
9. **USAspending** does not yet show the August–September stockpile orders, so FY2026 funded totals are understated. The 90-day DoD lag is documented in METHOD.md.

## Sources (all fetched 5 Oct 2026)

- **Law:** [P.L. 119-21](https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm).
- **DoD contracts:** [25 Sep 2026](https://www.war.gov/News/Contracts/Contract/Article/4612013/contracts-for-sept-25-2026/).
- **USAspending API** (`/api/v2/search/spending_by_award/`, `/api/v2/awards/{id}/`, `/api/v2/transactions/`), keyword `SP8000`, FY2025–26. Key awards:
  - Glencore cobalt IDIQ: [CONT_IDV_SP800026D0012](https://www.usaspending.gov/award/CONT_IDV_SP800026D0012_9700/)
  - Cliffs DR-GOES IDIQ: [CONT_IDV_SP800025D0008](https://www.usaspending.gov/award/CONT_IDV_SP800025D0008_9700/)
  - UAMY antimony IDIQ: [CONT_IDV_SP800025D0007](https://www.usaspending.gov/award/CONT_IDV_SP800025D0007_9700/)
  - Largo vanadium IDIQ: [CONT_IDV_SP800026D0016](https://www.usaspending.gov/award/CONT_IDV_SP800026D0016_9700/)
  - Arconic aluminium IDIQ: [CONT_IDV_SP800026D0008](https://www.usaspending.gov/award/CONT_IDV_SP800026D0008_9700/)
  - Rio Tinto aluminium IDIQ: [CONT_IDV_SP800026D0009](https://www.usaspending.gov/award/CONT_IDV_SP800026D0009_9700/)
- **SEC filings** (all linked above):
  - MTUS: 10-K FY2025, 10-Q Q2 2026, 8-K 1 Jul 2026.
  - ELMT: 8-K 14 Sep, 10-Q to 3 Jul.
  - UAMY: 10-Q Q2, 8-Ks of 11 Aug (release), 19 Aug and 2 Oct.
  - MP: 10-Q Q2 2026.
  - CLF: 10-Q Q2 2026, 10-K FY2025.
  - MOD: 8-K 29 Jul (Q1 release), 10-Q Q1 FY27.
  - VRT: 10-K FY2025, 10-Q Q2, 8-Ks of 29 Jul, 2 Sep and 24 Sep.
  - AAON: 10-Q Q2, 8-Ks of 10 Aug and 28 Aug, 10-K FY2025.
  - Largo: 6-K exhibit 99.2 (Q2 MD&A), 6-K of 29 Sep, 424B5 of 29 Sep.
- **SEC XBRL companyfacts** (`data.sec.gov/api/xbrl/companyfacts/`): MTUS, ELMT, UAMY, MP, CLF, MOD, VRT, AAON and the peers CMC, CRS, ATI, UUUU, STLD, NUE, NVT, TT. User-Agent as in `collectors/s1_dod.py`.
- **Yahoo chart API** (5y daily) for every ticker above plus SPY, IWM, SLX, REMX, XME, XLI, XAR, THRM, HRC=F and HG=F.
- **Repo context:** `stocks/MTUS.md`, `stocks/ELMT.md`, `stocks/MOD.md`, `ideas/MTUS.md`, `research/filings-2026-10-04/watchlist-deep.md`.
