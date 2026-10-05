# HMH: HMH Holding Inc
<!-- DEEP DIVE (hand-written; generators never touch this part) -->
*Dossier written 5 Oct 2026 (~16:00 UK). Primary sources: HMH S-1, 10-Q and 8-Ks; BKR 8-K/10-Q; Akastor's own reports. First test case of `strategies/overhang/RULES.md`. Prices: Yahoo; "5 Oct" = intraday at ~11:00 ET.*

## 1. What it is, and why it's on the watchlist
- **HMH** makes offshore and onshore drilling equipment: topside packages, BOPs and pressure control, risers. Over 1,100 installations; ~75% of the installed base is offshore. **Aftermarket is ~47% of revenue and spares ~37%** (H1 2026).
  - FY25 revenue $821.8M, adjusted EBITDA $156.2M.
  - Q2 2026 revenue $170.8M (−16% y/y), adjusted EBITDA $33.9M (19.8%).
  - Q2 orders $205M (book-to-bill 1.2×); RPO $414.4M ([8-K 5 Aug](https://www.sec.gov/Archives/edgar/data/2021880/000162828026053339/hmh-20260805.htm), [10-Q](https://www.sec.gov/Archives/edgar/data/2021880/000162828026053385/hmh-20260630.htm)).
  - Net debt ≈ $78M: $200M of 7.875% bonds due Dec 2028, less $119.7M cash.
- **Up-C structure:** 12,201,501 Class A shares plus 31,891,652 Class B, so **44.09M economic shares**. Fully-exchanged market cap ≈ $843M at $19.12; EV ≈ $920M, **~5.9× LTM EBITDA**.
- IPO at **$20** (424B4, 1 Apr 2026).
- **Found:**
  - Market scan, 28 Sep (`share_registration`), at **$19.28**.
  - Watchlist thread, 29 Sep (`idea_overhang`, direction −1, i.e. supply), at **$17.77**.
  - Prices since: 2 Oct $18.31; 5 Oct ~$19.12.

## 2. Thesis (the overhang rule: buy *after* the registered supply is absorbed)
| step | content |
|---|---|
| **Event** | Resale [S-1, 28 Sep](https://www.sec.gov/Archives/edgar/data/2021880/000119312526405527/d32439ds1.htm) (filed after the close) registers **31,891,652 Class A shares**: Baker Hughes 15,945,826 and Akastor 15,945,826. That is **all of both principals' stakes: 72% of economic shares and 2.6× the Class A float**, ~$610M at $19.12. The 180-day lock-up **expired 27 Sep**. Class B can redeem into Class A up to 12× a year. |
| **Reason (who sells)** | Both principals have said they want to monetise. **Akastor** (Q2 presentation, 21 Aug): "transition from value creation to realization and shareholder distribution", and it is "evaluating… a share-based solution linked to HMH shares… as a contingency liquidity source". That could mean a loan backed by the shares rather than a sale. **BKR** lists the HMH IPO under "Executing our portfolio management strategy" (Q1 8-K Ex. 99.1), and its Q2 10-Q doesn't mention HMH. |
| **Confirmation** | The S-1 goes EFFECTIVE, then a 424B prospectus supplement or block trade prints. Then **absorption**: a volume spike, then 5+ sessions with no new low. That is the entry point the overhang rule wants to test. |
| **Target** | n/a until the supply prints. |
| **Invalidation (of the supply thesis)** | Already partly happened: the price has round-tripped to its pre-S-1 level. If BKR and Akastor use share-backed loans or exchangeables instead of sales, the overhang just hangs there. |

## 3. Evidence
- **The S-1 is mandatory, not a sign of imminent sale.** The registration rights agreement requires a resale shelf "not later than 180 days" after signing. The S-1 contains **no statement of intent to sell**.
- **It is NOT effective yet.** EDGAR on 5 Oct shows no EFFECT notice, no S-1/A and no 424B, so nothing can be sold under it. The Rule 144 route is small: ~1.1M shares per holder per 3 months.
- **No company support:** no dividend and no buyback, and the bond covenants restrict both. HMH *may* settle a redemption in cash at the 10-day VWAP if its independent directors agree. Nothing is committed.
- **Who holds the Class A:** T. Rowe Price 24.4%, FMR 11.6%, Wellington 6.7%, BlackRock 6.5%, Schroders 5.3% (13G filings, Jul–Aug). The IPO hedge funds (Point72, Encompass) report 0% at 30 Jun.

## 4. What has already re-rated
| window | HMH | OIH | NOV | IWM |
|---|---|---|---|---|
| IPO $20 → 5 Oct | **−4.4%** (first close 19.28; high 24.26 on 22 May) | | | |
| 1 Apr → 5 Oct | −0.8% | −0.1% | | +12.9% |
| 25 → 29 Sep (S-1) | −7.3% | −3.4% | −4.4% | −1.0% |
| 28 Sep → 5 Oct | −0.8% | +1.6% | +0.1% | +0.6% |
| 2 → 5 Oct | +4.5% | +3.5% | +3.8% | +0.1% |

- **About half of the "S-1 drop" was sector-wide**, and HMH is back at its pre-S-1 level (19.16 on 25 Sep).
- Volume on 29 Sep–2 Oct totalled only 1.26M shares, so no block traded. **No supply has been absorbed, because none has been sold yet.**
- The ledger's short-direction row from $17.77 is ~7.6% underwater.

## 5. Branches
- **BKR:** the stake is ~$305M, **~0.5% of BKR's ~$55.6bn market cap**. A sale is immaterial to BKR (G1 fails for BKR).
- **Akastor (Oslo: AKAST):** HMH was **NOK 2,966M of NOK 4,735M NAV (63%)** at 30 Jun ([H1 report](https://storage.mfn.se/9587076f-0361-452e-a7f2-4cf2ee533b4a/akastor-asa-half-year-report-2026.pdf)), and is ~80% of Akastor's market cap. **It is highly material to Akastor**, but Akastor has no debt and NOK 560M of liquidity, so it is **not a forced seller**. Akastor Q3: 11 Nov.
- **Customers:** offshore drillers. RIG, VAL and NE are −16% to −21% since 1 Apr. In 2025 the top 5 customers were 45% of revenue and the largest was 20.8%.
- **Peers:** NOV, SLB/Cameron, Huisman (private), Canrig.
- **Forced flows:** a full secondary would multiply the Class A float ~3.6×, which would mean an index weight increase **[INFERENCE; Russell and S&P treatment of the Up-C structure UNVERIFIED]**. That is buying against the selling.
- **Other tickers affected:** BKR, AKAST.OL, NOV, RIG, VAL, NE, OIH.

## 6. METHOD gates and score (event-driven mapping)
- **G1: pass.** Supply is 2.6× the float.
- **G2: n/a.**
- **G3: pass.** −4% vs the IPO.
- **G4: pass.**
- **G5: pass.** ~$3.9M/day.

| factor | score | why |
|---|---|---|
| Payoff size | 1 | a post-absorption rebound of 5–15% |
| Certainty | 0 | sellers' timing and mechanism unknown |
| Coverage | 1 | IPO coverage |
| Date visibility | 0 | the S-1 is not effective; no date |
| Behavioural signal | 0 | no buyback; principals want out |
| **Total** | **2/10** | **kill band. Keep only as the overhang rule's first case** |

## 7. Risks
- **Long:** buying before the supply hits. ~$610M is registered against a ~$230M Class A float.
- **Short:** not feasible at this size. The stock already round-tripped, and the sellers may never sell outright.
- **Business:** offshore drilling capex is cyclical, revenue is −16% y/y, and customer concentration is high.

## 8. Key dates
| date | event |
|---|---|
| any day | EFFECT notice / S-1/A for the resale S-1 (watch EDGAR) |
| after effectiveness | 424B prospectus supplement or block trade = the supply prints |
| 11 Nov | Akastor Q3 (any statement on HMH monetisation) |
| ~early Nov (TBD) | HMH Q3 results (Q2 was 5 Aug; no date announced) |
| 90 days after any underwritten resale | the registration rights agreement blocks the next underwritten resale |

## 9. Verdict: WATCH (overhang test case), score 2/10, no trade
- Nothing to do until the S-1 is effective and supply actually prints.
- **What would change it:** a 424B or block at a discount, followed by absorption (volume back to normal, 5 sessions without a new low) at an EV below ~6× EBITDA. That is exactly the overhang rule's buy-after-absorption test. Log it then with an OIH control.

<!-- AUTO (generated by reports/build_stocks.py; everything below is rewritten on each run) -->
## Status

- **Tracked because:** [watchlist](../watch/watchlist.json); `idea_overhang` logged 2026-09-29 (watchlist thread (X 29 Sep))
- **Latest price:** $19.21 (2026-10-05, ledger) · 1d +5.5%, 5d -4.4%, 20d -8.5% (market context, 2026-10-02)
- **Since first found:** **-0.4%** (found 2026-09-28 via `share_registration` at $19.28). From the next open $18.87: +1.8% vs IWM +0.7% = **+1.1 pts** vs IWM; direction -1 → excess -1.1% (6 days)
  - 1 more ledger row: see Performance since found
- **Peers / sympathy:** no flag (self 5d -4.4% vs peer median -4.2%). Peer groups: oilfield equipment (5), SIC 3533 (8) ([market context](../watch/context/latest.json), 2026-10-02)
- **Next dated events** ([calendar](../calendar/catalyst-dates.ics)):
  - Thu 29 Oct 2026: Re-check the 29 Sep catalyst scan (1 month)
  - Mon 30 Nov 2026: Re-check the 29 Sep catalyst scan (2 months)
- **Files:** [ledger](../ledger/LEDGER.md) · [all dossiers](README.md)

## Timeline

Every dated mention, newest first: S1 signals, the market-wide scan, watchlist filings, press releases, ideas and setups logged, triage notes, trades, past calendar events and research notes. One line per date; the date links to that day's scan.

- **[2026-09-30](../scans/2026-09-30.md#triage-notes)**: Triage: **HMH**: resale S-1 (filed 28 Sep). The Selling Stockholders (Principal Stockholders: Baker Hughes and Akastor affiliates) register up to… ([triage](../watch/digests/2026-09-30-triage.md))
- **[2026-09-29](../scans/2026-09-29.md#new-setups)**: Logged as `idea_overhang` (direction -1): resale S-1 31.9M shares (supply); source: watchlist thread (X 29 Sep) ([manual_calls.csv](../ledger/manual_calls.csv)) · Research: Dated-catalyst scan: 2026-09-29 (window 30 Sep – 7 Oct 2026) (HMH 180-day IPO lockup ended 27 Sep; resale S-1 for 31.9M shares (~3× float) filed 28 Sep S-1 effective date…) ([note](../research/scans/2026-09-29-dated-catalysts.md))
- **[2026-09-28](../scans/2026-09-28.md#market-wide-scan)**: Market scan: share registration (S-1) (`S-1`) (5d before +1.6%, found day +0.6%) ([filing](https://www.sec.gov/Archives/edgar/data/2021880/0001193125-26-405527-index.htm))

## Performance since found

Every [ledger](../ledger/LEDGER.md) row for HMH ([rules](../ledger/RULES.md)): found = close on the day it was found; entry = next session's open; IWM over the same entry → now window; excess = direction × (return − IWM).

| found | category | dir | 5d before | found day | $vol/day | found @ | entry @ | now | since found | since entry | IWM | excess | days | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-28 | `share_registration` | -1 | +1.6% | +0.6% | $3.7M | $19.28 | $18.87 | $19.21 | -0.4% | +1.8% | +0.7% | -1.1% | 6 | live |
| 2026-09-29 | `idea_overhang` | -1 | +3.6% | -7.8% | $3.9M | $17.77 | $17.77 | $19.21 | +8.1% | +8.1% | +0.7% | -7.4% | 5 | live |
