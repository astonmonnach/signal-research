# AV1 pre-registration: do our AVOIDs fall more than similar stocks we did not flag?

Written 27 Oct 2026, before any AVOID was compared with a control. Committed before the first comparison is run.

## Why

The trader asked whether the AVOID record is real or "just because it could go either way" (27 Oct). Tiny, struggling stocks fall
most of the time anyway: 57% of the 100 logged movers had a listing-deficiency notice. A raw record against IWM (11 of 14 behind)
cannot separate our reading from that base rate. A matched control can.

## Sample

Every row of `ledger/avoid_register.csv` (the register of every AVOID ever given, built 27 Oct from every note and triage file).
- **Primary group:** supply and distress AVOIDs (`supply_type` ongoing_supply, warrant_supply, distress, holder_selling, deal_dilution).
- **Secondary, description only:** one_off_offering, kill (a long thesis that was killed, labelled AVOID) and other.
- An AVOID counts from the first session that opens after its note date. It is judged at **20 trading days**, or at the close
  before a reversal if the note reversed it earlier (the reversal is part of the record, not a reason to drop the row).

## Control

For each AVOID, up to **10 control stocks**, chosen before their returns are read:
- From the Nasdaq screener universe (`watch/marketcap.json`), US-listed common stock.
- Same price bucket at the entry date: under $1, $1-5, $5-20, $20 or more.
- Market value between half and twice the AVOID's.
- Not in the AVOID register, not on `watch/watchlist.json`, not a fund, ETF, warrant, unit or right.
- Drawn with a fixed seed: Python `random.Random(f"{ticker}{date}")` over the sorted eligible list.

**Excess** = the AVOID's return minus the median control return over the same window, open to close.

## The test

AV1 **passes** only if all three hold in the primary group:
1. The mean excess is below zero.
2. A bootstrap 95% interval on the mean excess is below zero (resample AVOIDs; 2,000 draws; seed 20261027).
3. The mean excess is below zero in both halves, split at the median entry date.

- **When:** the analysis runs once the primary group has 30 rows judged at 20 trading days, or on 31 Dec 2026, whichever comes first.
- **Before then:** progress is reported as description only, with no verdict.

**On a pass:** AVOID calls keep their current form.
**On a fail:** the public AVOID calls stop until a new study (AV2) shows which kind works.

Any change to the sample, the control or the test is a new study, AV2.
