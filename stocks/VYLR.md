# VYLR: Vylor Inc.
<!-- DEEP DIVE (hand-written; generators never touch this part) -->
*Dossier written 5 Oct 2026 (~16:00 UK). Folds in `ideas/VYLR.md` (30 Sep watch note and day-1 log) and the VYLR part of `research/filings-2026-10-04/watchlist-deep.md`. Prices: Yahoo; "5 Oct" = intraday at ~11:00 ET. Deep dive from before the spin: `research/VYLR-2026-09-29.html`.*

## 1. What it is, and why it's on the watchlist
- Vylor is Corteva's seed business (Pioneer and others), spun off 1:1 to CTVA holders on 1 Oct 2026. About 667.2M shares. 2025 seed net sales $9.90bn; segment operating EBITDA $2.64bn (+19% y/y, margin up ~340bp).
- **Found:** spin-off watch, from the 29 Sep dated-catalyst scan (`research/scans/2026-09-29-dated-catalysts.md`) and the 29 Sep X thread (`posts/2026-09-29-VYLR-thread.md`). Logged at the **day-1 close of $68.26** (1 Oct). 2 Oct close $67.26; 5 Oct ~$69.39.
- **Status: an observation case, not a trade.** The spin-off rule v1 was retired on 30 Sep after the backtest (`strategies/spinoff/backtest-2026-09-30.md`).

## 2. Thesis (the original, and what happened to it)
| step | original thesis (30 Sep) | what the filings show now |
|---|---|---|
| **Event** | 1 Oct distribution. About 667M shares land in accounts that never asked for them. No when-issued market ([24 Sep 8-K, Ex. 99.1](https://www.sec.gov/Archives/edgar/data/2128626/000119312526401621/d118532d8k.htm): "there will not be 'when-issued' trading") | Happened. Day 1: open $66.00, high $74.95, low $65.00, close $68.26 |
| **Reason (who is forced)** | Index funds "may be required to sell" if VYLR isn't in their index; crop-protection and dividend holders | **Mostly gone.** S&P added VYLR **straight into the S&P 500 on 1 Oct**, replacing CTVA ([S&P DJI release](https://www.prnewswire.com/news-releases/vylor-added-to-the-sp-500-twilio-set-to-join-sp-500-others-to-join-sp-midcap-400-and-sp-smallcap-600-302896675.html)). The only index flow left is the **GICS move from Materials to Consumer Staples on 6 Oct**: XLB must sell **4,310,898 VYLR (3.83% of the fund, ~$290m)** at the 5 Oct close, while XLP should buy **~5.8M (~$390m) [estimate]**. Net SPDR flow is about **+1.5M shares bought [estimate]**. **The forced seller in this spin is CTVA, not VYLR** (see `stocks/CTVA.md`) |
| **Confirmation** | Volume back towards normal; 5+ days without a new low; index decision; first dividend; first results | Volume has fallen: 15.0M on day 1, 13.5M on day 2, ~2.8M by 11:00 ET on 5 Oct. The low so far is $65.00 (1 Oct intraday) |
| **Target** | None. Log the day-1 close, the post-spin low and its day, then prices at +60 and +120 trading days | Unchanged |
| **Invalidation** | n/a (observation) | n/a |

## 3. Evidence
**Capital structure** (Information Statement, Ex. 99.1 to [8-K 0001193125-26-402928](https://www.sec.gov/Archives/edgar/data/2128626/000119312526402928/ck0002128626-20260924.htm)):
- Pro forma debt $5,659m (short-term $3,179m, long-term $2,480m) against $1,100m cash; about $3.1bn of the debt is floating. That is about 2.1× EBITDA on June pro forma numbers.
- Facilities: a $3.0bn 5-year RCF and a $1.5bn 364-day RCF. A $2.75bn delayed-draw term loan is a backstop it "does not intend to draw".
- New notes: $550m 5.125% due 2031 and $550m 5.625% due 2036 ([CTVA 8-K 31 Aug](https://www.sec.gov/Archives/edgar/data/1755672/000119312526377055/)). Proceeds went "to make a cash distribution to EIDP".
- Old EIDP notes were swapped into Vylor notes at 87–95% acceptance ([8-K 1 Oct](https://www.sec.gov/Archives/edgar/data/2128626/000119312526409841/d118856d8k.htm)).
- **"New Corteva will retain… historical PFAS and other environmental liabilities"**, so Vylor walks away from them.

**Guidance and policy:**
- 2029 targets: net sales "$11.2 billion to $11.9 billion" (3–4% a year) and operating EBITDA "$3.3 billion to $3.7 billion". Licensing income of more than $500m in 2027 ([Vylor release, 1 Oct](https://www.prnewswire.com/news-releases/vylor-completes-spin-launches-as-a-standalone-advanced-seed-and-genetics-market-leader-302895126.html); press release only, not on EDGAR).
- Dividend: quarterly from Q4 2026, "approximately 15% of annual cash flow from operations" (Information Statement).
- Accounting: Vylor is the "accounting spinnor" and successor to Corteva ([CTVA 8-K, 1 Oct](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000028/ctva-20261001.htm)). **Its first 10-Q will carry Corteva's history and be messy.**
- **Seasonality trap:** the seed segment made $2,705m of operating EBITDA in H1 2025 but $2,636m for the full year, so **H2 2025 was about −$69m**. The first standalone quarters will look like losses.

**Litigation tail:**
- California and 18 other states sought to enjoin the spin as a **fraudulent transfer**. On 30 Sep the Fourth Circuit sent it back and the District Court denied the injunction. The appeals court "expressed no view on the merits", and the board waived the legal-restraints condition ([8-K 30 Sep](https://www.sec.gov/Archives/edgar/data/2128626/000119312526409545/d121693d8k.htm)).
- The Information Statement warns that a court "could void the spin-off… or return… some of our assets or your shares of Vylor".

**Who received VYLR** (latest 13G filings for CTVA, holders above 5%):

| holder | % of CTVA | as of | type |
|---|---|---|---|
| Vanguard Capital Management | 7.56% | 31 Mar 2026 | mostly index |
| Capital World Investors | 6.6% | 30 Jun 2026 | active |
| FMR (Fidelity) | 5.2% | 31 Mar 2026 | mostly active |
| State Street | 5.2% | 30 Sep 2025 | mostly index |

BlackRock has no current 13G (the last was Feb 2024).

## 4. What has already re-rated
- **Day-1 log** (1 Oct, ~20:10 UK, intraday, from `ideas/VYLR.md`): VYLR at $68.13 on 6.86M shares; CTVA (ex-seed) at $12.31. The combined $80.44 was +1.2% against the $79.45 record-date close. Against the right base (30 Sep, $77.65) the day-1 close was +4.1%.
- **Sum of the parts:** VYLR + CTVA was $79.18 on 2 Oct (+2.0% vs $77.65, the last close with the entitlement, on 30 Sep). On 5 Oct it is ~$81.51 (69.39 + 12.12), **+5.0%, against SPY +1.3%** over the same window.
- **Between the halves, the re-rating is large.** VYLR has a ~$46.3bn market cap and an EV of ~$50.9bn, so it trades at **~20× 2025 pro forma operating EBITDA ($2,503m)** and **~14.5× the 2029 target midpoint**. New Corteva trades at ~5–6×. The market puts ~85% of the combined value in Vylor, which has ~66% of the EBITDA. **Seed has already re-rated up.**
- **Since day 1:** VYLR +1.7% (68.26 → 69.39) vs SPY +1.1%, XLP +0.3% and XLB +1.2%. There has been no forced-selling slump.
- Backtest base rate (22 spins): the post-spin low typically came around **day 28 (about 9 Nov here)**, at a median **−14%** from the day-1 close, which would be ~$58.7. Large spins showed no edge.

## 5. Branches
- **Forced flows:** XLB sells and XLP buys at the 5 Oct close; the GICS change takes effect 6 Oct. MSCI-based sector funds (Vanguard, Fidelity) will also follow GICS, but their timing is **[UNVERIFIED]**. Materials-only and income funds face a mandate mismatch.
- **Peers:** Bayer (BAYRY, −9.2% since 30 Sep) owns the competing seed franchise. ADM and BG are now its Staples neighbours (ADM +2.5%). KWS and Syngenta are not US-listed.
- **Commodity:** corn futures −5.8% over 5 days and −0.8% since 1 Oct. Seed pricing lags grain prices by a season.
- **Debt:** stub EIDP noteholders who did not exchange (~$161m) lost "substantially all of the restrictive covenants" ([8-K 20 Aug](https://www.sec.gov/Archives/edgar/data/1755672/000119312526359264/)).
- **Other tickers affected:** CTVA, XLB, XLP, ADM, BG, BAYRY, FMC, OLN, QRVO (the S&P 600 chain).

## 6. METHOD gates and score (event-driven mapping, as in `market-scan-deep.md`)
- **G1: pass.** The spin is 100% of the security.
- **G2: n/a.**
- **G3: fail.** Seed re-rated to ~20× before any forced selling showed up.
- **G4: pass.**
- **G5: pass.** About $1bn a day traded.

| factor | score | why |
|---|---|---|
| Payoff size | 1 | a 5–15% swing is plausible either way |
| Certainty | 0 | no defined payoff |
| Coverage | 0 | mega-cap, widely covered |
| Date visibility | 1 | ~day 28; first results date not yet filed (4 Nov from a secondary listing **[UNVERIFIED]**) |
| Behavioural signal | 0 | nobody has put money in; index flow is net buying |
| **Total** | **2/10** | **kill as a trade; keep as an observation row** |

## 7. Risks and what kills it
- **Fraudulent-transfer claim revived:** assets or shares could be clawed back. This is a tail risk.
- **Floating-rate debt (~$3.1bn) at a 5.28% 10-year yield**, and a first dividend that turns out small.
- **First 10-Q:** H2 seasonal losses plus accounting-successor noise.
- **2029 targets** come from a press release, not a filing. A target of 3–4% a year doesn't justify 20× if it slips.

## 8. Key dates
| date | event |
|---|---|
| **Mon 5 Oct, close** | XLB sells, XLP buys (GICS change effective 6 Oct) |
| Thu 15 Oct | day-10 check (observation; `briefings/2026-10-04.md`) |
| ~4 Nov **[UNVERIFIED]** | Q3 results, the first as Vylor |
| ~9 Nov | day 28 (the backtest's typical low) |
| Q4 2026 | first quarterly dividend declaration |
| 31 Dec 2026 | PHI released as co-borrower under the RCFs (minor) |
| +60 / +120 trading days (~24 Dec / ~24 Mar 2027) | observation log prices |

## 9. Verdict: WATCH (observation only), score 2/10
- The forced-selling thesis doesn't apply: S&P 500 inclusion was immediate and sector funds are net buyers.
- Record the day-1 close ($68.26), the low and its day, and the prices at +60 and +120 days for the spin-off v2 test.
- **What would change it:** a slide of 15% or more below $68.26 without new bad news, plus a fundamental reason to own seed at ~17× (for example a first dividend above policy, or licensing income tracking ahead of target). Even then, the large-spin data say there's no edge.

<!-- AUTO (generated by reports/build_stocks.py; everything below is rewritten on each run) -->
## Status

- **Tracked because:** [watchlist](../watch/watchlist.json); `idea_spinoff` logged 2026-10-01 (first trading day)
- **Latest price:** $74.30 (2026-10-07, ledger)
- **Since first found:** **+8.8%** (found 2026-10-01 via `idea_spinoff` at $68.26). From the next open $68.71: +8.1% vs IWM -1.7% = **+9.8 pts** vs IWM; direction 0, tracked only (5 days)
  - 1 more ledger row: see Performance since found
- **Peers / sympathy:** no flag (self 5d n/a vs peer median -0.1%). Peer groups: seeds / ag (4), SIC 0100 (8) ([market context](../watch/context/latest.json), 2026-10-07)
  - warning: only 5 daily bars (new listing?)
- **Next dated events** ([calendar](../calendar/catalyst-dates.ics)):
  - Thu 15 Oct 2026: VYLR day-10 check (observation)
  - Thu 29 Oct 2026: Re-check the 29 Sep catalyst scan (1 month)
  - Tue 10 Nov 2026: VYLR ~day 28 check (typical spin-off low)
  - Mon 16 Nov 2026: Q3 13F deadline (who bought MTUS/VYLR/ELMT)
  - Mon 30 Nov 2026: Re-check the 29 Sep catalyst scan (2 months)
- **Files:** [thesis](../ideas/VYLR.md) · [ledger](../ledger/LEDGER.md) · [all dossiers](README.md)

## Timeline

Every dated mention, newest first: S1 signals, the market-wide scan, watchlist filings, press releases, ideas and setups logged, triage notes, trades, past calendar events and research notes. One line per date; the date links to that day's scan.

- **[2026-10-05](../scans/2026-10-05.md#market-wide-scan)**: Market scan: 8-K trigger phrase "spin-off" (spin-off) ([filing](https://www.sec.gov/Archives/edgar/data/2128626/000119312526414335/d92652d8k.htm)) · Calendar: Index trades at close: CTVA to MidCap 400 (replaces OLN); VYLR Materials→Staples (XLB sells, XLP buys) ([calendar](../calendar/catalyst-dates.ics))
- **[2026-10-04](../scans/2026-10-04.md)**: Research: Watchlist filings, deep read: VYLR/CTVA, THRM/MOD, TWST, MTUS (1. VYLR (Vylor) / CTVA (New Corteva): spin-off completed 1 Oct 2026) ([note](../research/filings-2026-10-04/watchlist-deep.md))
- **[2026-10-03](../scans/2026-10-03.md#triage-notes)**: Triage: **VYLR / CTVA** (spinoff watch): 8-Ks confirm the distribution completed 1 Oct. **New fact for ideas/VYLR.md:** California sued to delay the spin. ([triage](../watch/digests/2026-10-03-triage.md)) · Filings: `8-K` ×3 1 Oct
- **[2026-10-01](../scans/2026-10-01.md#new-setups)**: Logged as `idea_spinoff` (direction 0): spin-off watch (track); source: first trading day ([manual_calls.csv](../ledger/manual_calls.csv)) · Calendar: VYLR first day of trading (+ THRM/Modine deal closes) ([calendar](../calendar/catalyst-dates.ics))
- **[2026-09-30](../scans/2026-09-30.md#triage-notes)**: Triage, dismissed: **VYLR / CTVA** 8-Ks (30 Sep, same press release): Vylor extended its bond exchange offers for the EIDP notes by one day to 30 Sep. ([triage](../watch/digests/2026-09-30-triage.md))
- **[2026-09-29](../scans/2026-09-29.md)**: Research: Dated-catalyst scan: 2026-09-29 (window 30 Sep – 7 Oct 2026) (→ Deep dive: VYLR-2026-09-29.html (WATCH). Backup: THRM.) ([note](../research/scans/2026-09-29-dated-catalysts.md)) · Research: Vylor Spin-Off (Corteva (CTVA) is spinning off its seed business as Vylor Inc. (NYSE: VYLR). Holders of record at the close…) ([note](../research/VYLR-2026-09-29.html)) · Post: X thread: VYLR spin-off (29 Sep 2026) ([note](../posts/2026-09-29-VYLR-thread.md))

## Performance since found

Every [ledger](../ledger/LEDGER.md) row for VYLR ([rules](../ledger/RULES.md)): found = close on the day it was found; entry = next session's open; IWM over the same entry → now window; excess = direction × (return − IWM).

| found | category | dir | 5d before | found day | $vol/day | found @ | entry @ | now | since found | since entry | IWM | excess | days | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | `idea_spinoff` | 0 |  |  | $1025.0M | $68.26 | $68.71 | $74.30 | +8.8% | +8.1% | -1.7% |  | 5 | live |
| 2026-10-05 | `8k_spin_off` | 0 |  | +9.0% | $1063.4M | $73.33 | $71.91 | $74.30 | +1.3% | +3.3% | -2.4% |  | 1 | live |
