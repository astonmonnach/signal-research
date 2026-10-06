# Ledger rules (frozen 2026-10-04, before any results were seen)

- Every item that a collector or scan flags, or that we post or watch, gets a row. Kills and boring items stay in.
- **Found price** is the close on the day it was found.
- **Entry** is the next session's open, the first price you could actually act on.
- **Now** is the latest close.
- **Control:** IWM from the same entry date to now.
- **Excess** = direction × (return − IWM return). Direction is fixed per category in `build_ledger.py` (CATEGORY_DIRECTION):

| category | direction | reason |
|---|---|---|
| activist 13D | +1 | new holder pushing for change |
| issuer tender/buyback | +1 | company buying its own shares |
| 8-K strategic review/alternatives | +1 | possible sale |
| S1 DoD contract (material) | +1 | under-reaction thesis |
| share registration (S-1) | −1 | new supply |
| registration effective | −1 | supply can now sell |
| 8-K reverse split | −1 | usually precedes dilution |
| merger vote, third-party tender, IPO priced, delisting, spin-off, lock-up, special dividend | 0 | tracked, no directional claim |

- Changing a direction after seeing results is a **new, dated rule**. The old rows keep their old rule.
- Small samples prove nothing. Judge only after 30+ live items per category with 20+ trading days.

## Rule changes (dated)
- **2026-10-04: false positives.** From the 5 Oct scans on, an 8-K whose "strategic alternatives/review" hit is only in a director or officer filing (Item 5.02, with no 8.01/1.01/2.01) is tagged `bio-mention` and isn't counted as a strategic review. The trigger was LWLG on 29 Sep: a new director's bio. That row stays in the ledger as it was recorded.
- **2026-10-05: two more false positives, now caught by the scanner (`watch/scan_market.py`).**
  - An `EFFECT` notice names the form it makes effective. If that form puts no new shares on the market, the row is
    tagged `(not supply: ...)` and isn't counted as `registration_effective`. Those forms are a post-effective amendment
    (POS AM, the HCTI trigger), an F-6 ADR facility, an N-2 closed-end fund, and S-4/F-4 merger shares (all seen in the
    23 Sep scan).
  - A "strategic alternatives/review" hit in a debt financing 8-K (Item 2.03 with no 8.01/2.01) is forward-looking
    boilerplate. It is tagged `financing-mention` and isn't counted as a strategic review. The trigger was CHDN on 28 Sep.
  - Both apply to scans from 6 Oct on. Older rows stay as they were recorded.
- **2026-10-05: the honest scoreboard is the headline.**
  - The old headline ("61/94 beat IWM, +5.0%") was mostly **short bets**: 68 of the 94, including KNRX and WHLR, which "won" by collapsing. We can't take those, because the account can't short and borrow for these names is usually unavailable.
  - From now on the headline counts only **takeable** items: long bets, average daily $ volume ≥ $250k, entry ≥ $1, with **1% taken off for round-trip costs**.
  - A takeable result is **judged** only after **20 trading days** held. `days` was calendar days; `tdays` is now trading days.
  - Short bets stay in the ledger as paper-only, a don't-buy list, and are never counted as wins.
  - Known false positives (LWLG's director bio, CHDN's refinancing boilerplate) aren't takeable: the method says read the filing before any trade, so they were never trades. They don't count as wins or losses.
  - Nothing was deleted or re-scored: every row keeps its direction. Only the headline and the cost basis changed.
- **2026-10-06: signed mergers get their own category.** The scanner now searches 8-Ks for "agreement and plan of merger". A hit is logged as `8k_merger_agreement`, tracked with direction 0 (a signed deal's upside is the arbitrage spread, not a re-rating). The trigger was C.H. Robinson's deal for RXO, which was only caught by the word "spin-off". Applies to scans from 6 Oct on.
- **2026-10-06: a 13D next to a signed merger isn't activism.** If the same company has a merger-agreement 8-K within 3 days, an `activist_13d` row is not takeable. It's usually a big holder's voting agreement (MFN Partners for RXO), not a push for change.
- **2026-10-06: state at the found day is recorded for every item.** The new columns are `rel_volume` (found-day volume / 20-day average), `from_52w_high_pct` and `above_50d`. They are **recorded only**. Any test that uses them (for example "activist 13Ds with relative volume above 2 do better") must be written here, dated, **before** anyone looks at results split by these columns. It is then judged only on items found after that date. Every test tried gets a line here, including the ones that fail, so we can count how many ideas were tried.
- **2026-10-06: exploration first, tests later (his call).** Until **30 Nov 2026**, everything in the ledger, including the state columns, may be looked at freely to come up with test ideas. Nothing seen in that period counts as evidence. On 30 Nov the tests are written down here and dated, and **only items found after that date** can confirm or reject them. Items from the exploration period are never used to judge a test, however good they look. The date can be moved earlier, but not later once ideas have been taken from the data.

