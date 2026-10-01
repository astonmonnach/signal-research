# Signal Lab: plan

The full plan was written 2 Oct 2026 in a separate chat. It lives in that chat and should be pasted in below the review notes. This file holds the **review notes and amendments agreed on 1 Oct 2026**, which take priority where they conflict.

## Review notes and amendments (1 Oct 2026)

1. **Costs are part of every result.** Measured 30 Sep 2026: a ~$60 position costs ~3.5% for a round trip at IBKR (commission minimums + spread). `signals.csv` gets an `est_cost_pct` column, and the scoreboard's "edge ON" test uses **20-day excess return minus est_cost_pct**, not the gross figure.
2. **S1 materiality needs the contract type.** DoD announcements often quote **ceiling values** of IDIQ / multiple-award contracts (shared between many awardees, and drawn down over years) and **modifications or option exercises**. Add `award_type` (definitive / IDIQ_ceiling / modification / option) and `obligated_usd` alongside `value_usd`. Materiality uses `obligated_usd` where it's given, and is flagged as an upper bound where only a ceiling is given.
3. **Forward logging solves the backtest data problem.** The Massive plan only goes back to ~Sep 2024, and free Yahoo data drops delisted stocks. Logging live from detection avoids both problems, so the forward log *is* the main evidence. Backtests are a quick filter, not the verdict.
4. **Count every variant tried.** Already tested and retired before this plan (30 Sep 2026): `taxloss` v1 (median −5.45% net) and `spinoff` v1 (median −11.5% net, 22 spins). See `strategies/`. They count towards the overfitting tally.
5. **The Stage 2 / 30-week MA filter is a variant, not a rule.** Log it as an S3 variant tag and compare it against unfiltered S3.
6. **Expected signal counts before the Mar 2027 checkpoint:** S1 should easily pass 30. S2 probably won't (a handful a month); if it has under 30 by March, the result is "not enough data", not "fail".
7. **Reuse what exists.** `watch/scan_market.py` already does S2's 8-K phrase search plus Form 10s, tender offers, S-1/EFFECT and 13Ds. `watch/check_filings.py` covers watchlist names. The evening scheduled task triages both. S1 (DoD) and S3 (Form 4) are new collectors.
8. **Time budget.** Topstep Combine runs alongside this. Collectors run on their own, so cap hands-on lab time at about 30 min/day. Building is fine, but don't chase variants.
