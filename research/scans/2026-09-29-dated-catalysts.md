# Dated-catalyst scan: 2026-09-29 (window 30 Sep – 7 Oct 2026)

Question: which stocks have a hard-dated event in the next 7 days where the chain resolves?
Method: three sweeps (FDA / deals & spins / lockups & deadlines), primary filings only.
Prices are Yahoo closes on 2026-09-29, recorded so the scan can be forward-tested.

## Verdict
The dated events in the window are either priced in (merger spreads under 0.6%) or not
tradeable at our size. The opportunity is in the weeks **after** a spin-off.
→ Deep dive: `VYLR-2026-09-29.html` (WATCH). Backup: THRM.

## FDA (PDUFA / adcomm)
No confirmed, still-pending small or mid-cap event.
- BMY Camzyos adolescent sNDA, 30 Sep: large cap, immaterial. $62.86
- MRK Welireg+Lenvima RCC, 4 Oct: large cap, immaterial. $149.28
- Stale aggregator entries, ruled out by filings: SRRK (approved 11 Sep, −17% 1mo since),
  BFRI (approved), PRAX (extended to 27 Dec), rusfertide (approved 28 Aug)
- ROIV/Priovant brepocitinib: filings say only "Q3 2026", so unverified. $36.50, +38% 6mo

## Deals / spins
| ticker | event | date | last | spread / move | verdict |
|---|---|---|---|---|---|
| SMTI | MiMedx merger vote | 30 Sep | 35.09 | 0.34% | priced |
| ACVA | Copart tender expiry | 30 Sep | 10.44 | 0.57% | priced; will extend (HSR refiled, ends 13 Oct) |
| FSEA | merger close | 1 Oct | 17.25 | 0.0% | priced |
| CTVA→VYLR | spin distribution | 1 Oct | 77.87 | −13% since 2 Sep | **deep dive: watch** |
| MOD→THRM | Reverse Morris Trust close | 1 Oct | THRM 33.92 | +24.7% 6mo | **backup: watch for unwanted-share selling** |
| TORO | AI OKTO spin record date | 1 Oct | 5.15 | +45.5% 6mo | partly run |
| BLFS | Repligen merger vote | 5 Oct | 39.22 | 0.22% | priced |
| NFJ | tender at 99% NAV | 5 Oct | 15.05 | ~4.7% gross (NAV unverified) | pass: too small after proration and fees |
| QNCX | share issuance vote | 6 Oct | 31.17 | +54% 6mo | run |
| UTMD | tender at $75 | 7 Oct | 74.95 | 0.07% | priced |
| ATKR | Prysmian merger vote | 7 Oct | 94.73 | 0.29% | priced |

Near misses: MDT/MiniMed exchange offer (expires 9 Oct), GTE vote (9 Oct).

## Lockups / deadlines
Almost no IPOs priced in the 180-day window (27 Mar – 14 Apr). The in-window lockups come from 90-day and 60-day follow-on offerings.

| ticker | event | date | last | vs offer / move | verdict |
|---|---|---|---|---|---|
| TWST | 60-day follow-on lockup ends (execs and directors) | 5 Oct | 186.13 | +94% vs $96 offer | **most stretched; insider Form 144s filed 17–24 Sep (not opened)** |
| RDVT | 60-day follow-on lockup ends | 5 Oct | 79.32 | +32%, at 6mo high | run |
| CLS | 60-day follow-on lockup ends | 5 Oct | 366.47 | +18% | moderate |
| GLOO | 90-day follow-on lockup ends (1.23M insider shares) | 6 Oct | 4.47 | +37.5% | run, small supply |
| SKHY | 90-day ADS lockup ends (issuer and some affiliates) | 7 Oct | 186.68 | +25% | limited overhang (KRX shares already trade) |
| HMH | 180-day IPO lockup ended 27 Sep; resale S-1 for 31.9M shares (~3× float) filed 28 Sep | S-1 effective date TBD | 17.77 | −11% vs $20 IPO | **real overhang, undated: watch** |
| UWMC | $400M rights offering, ex-rights 2 Oct, min price $2.00 | 1–6 Oct | 1.24 | −44% 60d | already crushed |
| CHRS | CVR dividend, record 30 Sep, paid 7 Oct | 7 Oct | 1.18 | −24% 60d | – |
| DBGI | "go-shop" ends on a $77.58 proposal | 5 Oct | 4.56 | −85% 60d | **red flag: market doesn't believe the bid** |
| MYPS / SHFS / VTAK | reverse splits | 30 Sep – 5 Oct | sub-$1 | down | avoid |

Near miss: TMCR direct-listing lockup releases 10% of 44.1M shares around 8 Oct.
Unverified: whether the TWST Form 144s are 10b5-1 sales; locked-vs-float counts for TWST, CLS, RDVT and SKHY.

## Forward-test checkpoint
Re-check VYLR, CTVA and THRM prices on 2026-10-29 and 2026-11-30.

## 1-month check (29 Oct 2026)
Prices: Massive daily closes, 29 Sep vs 28 Oct, adjusted for splits only. Cash and spun-off shares are added back
(`ledger/corporate_actions.csv`). Benchmark: IWM 279.01 to 281.29 (+0.8%); SPY +1.1%.

**The four checkpoint names**

| name | scan verdict | 29 Sep | 28 Oct | total return | vs IWM |
|---|---|---|---|---|---|
| CTVA held through the spin (1 CTVA + 1 VYLR) | — | 77.87 | 11.33 + 72.32 = 83.65 | +7.4% | +6.6 pts |
| VYLR from its first open (1 Oct, $66.00) | WATCH, not a day-one trade | — | 72.32 | +9.6% | +8.2 pts (IWM +1.4% from 1 Oct open) |
| VYLR from its first close ($68.26) | | — | 72.32 | +5.9% | +5.1 pts |
| CTVA after the spin (first close $12.57) | — | — | 11.33 | −9.9% | −10.7 pts |
| THRM (incl. $2.07 special dividend, ex 2 Oct) | backup: watch for unwanted-share selling | 33.92 | 33.16 | +3.9% | +3.1 pts |
| HMH | real overhang, undated: watch | 17.77 | 18.96 | +6.7% | +5.9 pts |

- **VYLR:** the forced selling we waited for lasted one day. The day-one low ($65.00) is still the low of the month.
  It peaked at $76.94 (13 Oct). Waiting cost the trade.
- **THRM:** the selling did come. Former MOD holders got 43.6% of the company. Volume was 6.1M, 5.3M and 10.6M on
  2, 5 and 6 Oct, against 0.6M before. Measured from the ex-dividend level ($31.56), the stock fell 17% to $26.15 on
  22 Oct (Q3 day). Then insiders bought on 23 Oct and it rose 27% in four sessions. We called it AVOID (kill) on
  20 Oct, near the bottom. That was reclassified on 27 Oct as a killed long thesis, not an AVOID.
- **HMH:** the resale S-1 (31.9M shares) went effective on 20 Oct. No sale by Baker Hughes or Akastor has been seen,
  and the stock is up. An overhang that nobody sells into doesn't move the price.

**The rest of the scan**
- **Lock-up expiries:** 4 of 5 fell. TWST −6.8%, CLS −18.2%, GLOO −33.3%, SKHY −11.8%, RDVT +3.9%. The median was
  −11.8% against IWM +0.8%. That fits the supply lens, but it's 5 names over one month.
- **Red flags held up:**
  - DBGI (the market didn't believe the $77.58 bid): −81.6%.
  - Reverse splits: SHFS −93.4%, MYPS +3.6%. VTAK has no 28 Oct price.
  - TMCR (lock-up near miss): −45.4%. It's now public call #4, which started 27 Oct.
- **"Already crushed":** UWMC +21.0% after its rights offering.
- **"Priced" mergers:**
  - ACVA, ATKR, BLFS and FSEA no longer trade (deals closed).
  - SMTI −6.3%: the vote passed, but the FTC issued a Second Request (16 Oct), so a spread of 0.34% didn't price
    the antitrust risk.
  - UTMD −8.2% after its $75 tender: the tender price only applied to the shares accepted.
- **FDA, large caps:** BMY −3.6%, MRK −5.6%. Stale: SRRK −9.4%, ROIV +1.7%.

**What it says (one month, small numbers; no new rule until TF1 and AV1 read)**
1. Spin-offs: both sides of the trade moved, but not the way the timing assumed. VYLR's selling was over in a day.
   THRM's took three weeks, and we read the bottom as a breakdown.
2. Lock-up expiry on a name that has run is the same supply idea as the AVOID register. It's worth adding to the
   AV1 sample, not a new filter.
3. A registered overhang (HMH) only matters once the holder actually sells.

Next checkpoint: 30 Nov (two months).

**Full list: all 34 names in the scan** (29 Sep close to 28 Oct close; IWM +0.8%)

| name | what the scan said | result | did it play out? |
|---|---|---|---|
| VYLR | WATCH: wait for forced selling (the only buy-side idea) | +5.9% from first close | no: it rose without us |
| THRM | watch for unwanted-share selling | +3.9% (−17% to 22 Oct, then +27%) | mixed |
| HMH | real overhang, watch | +6.7% | no |
| TWST | most stretched lock-up | −6.8% | yes |
| DBGI | red flag: market doesn't believe the bid | −81.6% | yes |
| SHFS | reverse split, avoid | −93.4% | yes |
| MYPS | reverse split, avoid | +3.6% | no |
| VTAK | reverse split, avoid | no trades after 2 Oct ($1.51) | unknown |
| TMCR | near miss: lock-up release | −45.4% | yes |
| CLS | lock-up, "moderate" | −18.2% | no view |
| GLOO | lock-up, "run, small supply" | −33.3% | no view |
| SKHY | lock-up, "limited overhang" | −11.8% | no view |
| RDVT | lock-up, "run" | +3.9% | no view |
| UWMC | rights offering, "already crushed" | +21.0% | no view |
| CHRS | CVR dividend | −1.7% | no view |
| SMTI | merger, priced (0.34%) | −6.3% (FTC Second Request) | no |
| ACVA | tender, priced (0.57%) | closed at $10.50, +0.6% | yes |
| ATKR | merger, priced (0.29%) | closed 19 Oct, about +0.3% | yes |
| FSEA | merger, priced (0.0%) | closed, 0% | yes |
| BLFS | merger, priced (0.22%) | last trade 5 Oct, $38.61 (−1.6%) | yes |
| UTMD | issuer tender at $75, priced | −8.2% after the tender | yes (price only for accepted shares) |
| NFJ | pass: too small after proration | −3.7% | yes |
| TORO | partly run | −11.5% | no view |
| QNCX | run | no trades after 9 Oct ($31.73) | no view |
| CTVA | spin parent | −9.9% from first post-spin close | no view |
| MOD | RMT parent (incl. THRM shares) | −13.8% | no view |
| BMY | FDA, large cap, immaterial | −3.6% | no view |
| MRK | FDA, large cap, immaterial | −5.6% | no view |
| SRRK | FDA, stale | −9.4% | no view |
| BFRI | FDA, stale | −18.7% | no view |
| PRAX | FDA, stale | +1.6% | no view |
| ROIV | FDA, unverified date | +1.7% | no view |
| MDT | near miss: MiniMed exchange offer | +8.8% | no view |
| GTE | near miss: vote | +18.7% | no view |

Scorecard: 1 buy-side idea (missed). 8 downside views: 4 right, 2 wrong, 1 mixed, 1 unknown. 7 "priced in / pass":
6 right, SMTI wrong. 18 names had no view.
