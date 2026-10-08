# CHDN: Churchill Downs Inc
<!-- DEEP DIVE (hand-written; generators never touch this part) -->
*Dossier written 5 Oct 2026 (~16:00 UK). Primary sources: CHDN 8-Ks, 10-Q and earnings releases. Prices: Yahoo; "5 Oct" = intraday at ~11:00 ET.*

## 1. What it is, and why it's on the watchlist
- **Churchill Downs** runs live racing (the Kentucky Derby), historical racing machines (HRMs), TwinSpires online wagering and regional casinos.
- LTM revenue ≈ $2.99bn; **LTM adjusted EBITDA ≈ $1.24bn** (FY25 $1,205.3M plus H1 2026 $734M minus H1 2025 $696M; [FY25 release](https://www.sec.gov/Archives/edgar/data/20212/000002021226000023/ex991pressrelease02-25x26.htm), [Q2 release](https://www.sec.gov/Archives/edgar/data/20212/000002021226000058/ex991pressrelease07-29x26.htm)).
- Net debt ≈ $4.60bn (bank-defined net leverage 3.7×). 69.7M shares, so a ~$5.4bn market cap at $77.75; EV ≈ $10bn, **~8× EBITDA** ([10-Q](https://www.sec.gov/Archives/edgar/data/20212/000002021226000059/chdn-20260630.htm)).
- **Found:** first catalyst scan (X post) and the market scan, 28 Sep, at **$75.72**, tagged "strategic alternatives 8-K". 2 Oct close $76.05; 5 Oct ~$77.75.

## 2. Thesis: the logged catalyst was a false positive
| step | content |
|---|---|
| **Logged event (wrong)** | The [28 Sep 8-K](https://www.sec.gov/Archives/edgar/data/20212/000119312526403885/d166307d8k.htm) (event 25 Sep, Items 1.01 and 2.03) is a **refinancing**. The revolver and term loan A are extended from 2029 to 2031, and a new **$500M term loan B due 2033** is priced at SOFR+175 (issued at 99.875). The [Ex. 99.1](https://www.sec.gov/Archives/edgar/data/20212/000119312526403885/d166307dex991.htm) also covers the **redemption of the $600M 5.50% 2027 notes on 19 Oct**. "Strategic alternative review" appears **only in the risk-factor boilerplate**. This is the scanner's known false-positive pattern (commit 5719ce6). |
| **The real event (old)** | [8-K Item 8.01, 29 Jul 2026](https://www.sec.gov/Archives/edgar/data/20212/000002021226000056/chdn-20260729.htm): "The Company is exploring various options to sell the following wholly owned regional gaming properties". It names nine: Calder, Terre Haute, Hard Rock Iowa, Oxford, Ocean Downs, Harlow's, Riverwalk, del Lago and Presque Isle. "The Company has not set a timetable." There has been no update since. |
| **Reason (who is paid to act)** | Buyers of regional casinos (regional operators, or casino REITs on sale-leasebacks) **[INFERENCE]**, and state gaming regulators. No forced party and no deadline. |
| **Confirmation** | A signed sale with a disclosed multiple; proceeds used to deleverage or restart buybacks ($500M authorised, none bought in H1). |
| **Target** | None. |
| **Invalidation** | No buyer, or sales at low multiples. |

## 3. Evidence
- **For:** a record Q2; maturities pushed out to 2031–33.
- **Against:**
  - Gaming segment adjusted EBITDA grew only +$6M in Q2.
  - HRM venues in central Virginia lost ~$5M of EBITDA to competition (Q2 release).
  - The fixed 5.5% notes are being replaced with floating-rate debt.
  - No buybacks.
  - Insider activity is only director phantom-unit deferrals.
  - Vanguard's 13G (5.01%) is passive.

## 4. What has already re-rated: down, with the sector
| window | CHDN | BYD | PENN | DKNG | XLY | IWM |
|---|---|---|---|---|---|---|
| 29 → 30 Jul (Q2 results and the sale-review 8-K, both 29 Jul) | **−6.6%** (88.53 → 82.69) | | | | | +1.4% |
| 29 Jul → 5 Oct | −12% (to 77.75) | | | | | |
| YTD | **−31.7%** (113.78 → 77.75) | −21% | 0% | −46% | −7.7% | +14.5% |
| 28 Sep → 5 Oct | +2.7% | −1.2% | −1.3% | −5.3% | +1.1% | +0.6% |

- The asset-sale news re-rated the stock **down**, not up. The 28 Sep −5.1% came in a sector-wide fall (BYD −2.9%, PENN −2.6%, DKNG −3.9%), cause **[UNVERIFIED]**.
- The stock is 34% below its 52-week high ($118.35).

## 5. Branches
- **Likely buyers [INFERENCE]:** BYD, PENN, BALY, GDEN (operators); GLPI, VICI (REITs).
- **Equity affiliates:** Rivers Des Plaines, Miami Valley.
- **Forced flows:** none found.
- **Other tickers affected:** GLPI, VICI, BYD, PENN, DKNG (online competitor).

## 6. METHOD gates and score (event-driven mapping)
- **G1:** the nine casinos' share of EBITDA is **[UNVERIFIED]**.
- **G2: n/a.**
- **G3: pass.** It de-rated.
- **G4: FAIL as logged.** The 28 Sep filing doesn't say what the log says.
- **G5: pass.**

| factor | score | why |
|---|---|---|
| Payoff size | 1 | |
| Certainty | 0 | no deal |
| Coverage | 0 | large cap, covered |
| Date visibility | 0 | no timetable |
| Behavioural signal | 0 | no buybacks or insider buys |
| **Total** | **1/10** | **kill** |

## 7. Risks
Sector de-rating (online and HRM competition), floating-rate debt, and no-sale risk. **The idea as logged is wrong on the facts.**

## 8. Key dates
| date | event |
|---|---|
| 19 Oct | $600M 5.50% 2027 notes redeemed (revolver-funded) |
| ~22 Oct **[INFERENCE: last year's date]** | Q3 results: any update on the casino sales |
| 2028 | $700M notes, the next maturity |

## 9. Verdict: AVOID (kill), score 1/10
- Keep the ledger row; it's a useful **false-positive** data point for the scanner. Fix: ignore "strategic alternative(s)" when it appears only in a forward-looking-statements paragraph.
- **What would change it:** a signed sale of the regional casinos at ≥8× EBITDA, with the proceeds going to buybacks. That would be a new, dated event; log it fresh.

<!-- AUTO (generated by reports/build_stocks.py; everything below is rewritten on each run) -->
## Status

- **Tracked because:** [watchlist](../watch/watchlist.json); `idea_catalyst` logged 2026-09-28 (first catalyst scan (X post 28 Sep))
- **Latest price:** $73.82 (2026-10-08, ledger) · 1d -0.1%, 5d -1.3%, 20d -10.7% (market context, 2026-10-08)
- **Since first found:** **-2.5%** (found 2026-09-28 via `8k_strategic_review` at $75.72). From the next open $76.00: -2.9% vs IWM -1.8% = **-1.1 pts** vs IWM; direction +1 → excess -1.1% (9 days)
  - 1 more ledger row: see Performance since found
- **Peers / sympathy:** no flag (self 5d -1.3% vs peer median +0.5%). Peer groups: SIC 7948 (1) ([market context](../watch/context/latest.json), 2026-10-08)
- **Next dated events** ([calendar](../calendar/catalyst-dates.ics)):
  - Mon 28 Dec 2026: Re-check the first scan: WHF, CHDN, RYAM
- **Files:** [ledger](../ledger/LEDGER.md) · [all dossiers](README.md)

## Timeline

Every dated mention, newest first: S1 signals, the market-wide scan, watchlist filings, press releases, ideas and setups logged, triage notes, trades, past calendar events and research notes. One line per date; the date links to that day's scan.

- **[2026-09-28](../scans/2026-09-28.md#new-setups)**: Logged as `idea_catalyst` (direction +1): strategic alternatives 8-K; source: first catalyst scan (X post 28 Sep) ([manual_calls.csv](../ledger/manual_calls.csv)) · Market scan: 8-K trigger phrase "strategic alternatives" (strategic review / alternatives) (5d before -2.6%, found day -5.1%) ([filing](https://www.sec.gov/Archives/edgar/data/20212/000119312526403885/d166307dex991.htm))

## Performance since found

Every [ledger](../ledger/LEDGER.md) row for CHDN ([rules](../ledger/RULES.md)): found = close on the day it was found; entry = next session's open; IWM over the same entry → now window; excess = direction × (return − IWM).

| found | category | dir | 5d before | found day | $vol/day | found @ | entry @ | now | since found | since entry | IWM | excess | days | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-28 | `8k_strategic_review` | +1 | -2.6% | -5.1% | $92.0M | $75.72 | $76.00 | $73.82 | -2.5% | -2.9% | -1.8% | -1.1% | 9 | live |
| 2026-09-28 | `idea_catalyst` | +1 | -2.6% | -5.1% | $92.0M | $75.72 | $76.00 | $73.82 | -2.5% | -2.9% | -1.8% | -1.1% | 9 | live |
