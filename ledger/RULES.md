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
