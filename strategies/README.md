# Strategy book

Every trade belongs to one strategy. Every strategy has written rules, a reason it
should work, and a test it has to pass before real money goes in.

## The one question behind every idea
> **Who is selling? → Why are they forced to, not choosing to? → When does it end? → What is the business worth?**

If an idea can't answer all four, it isn't a trade.

## Lifecycle: nothing skips a stage
| stage | what has to happen to move on |
|---|---|
| `IDEA` | Written rules, plus a named reason someone is on the wrong side |
| `BACKTEST` | Tested on past data, net of fees, and the **median** result is positive. The mean alone doesn't count. |
| `PAPER` | 10 paper trades logged by the rules, in real time |
| `LIVE` | Real money at £40–50 per trade. Judged after **20** trades, not before. |
| `RETIRED` | Failed a stage, or stopped working. Keep the file: a dead strategy is a finding. |

## Kill rules, set before we start
- Backtest median net of fees ≤ 0 → retire.
- 20 live trades with negative total P&L after fees → back to `PAPER` with a written post-mortem.
- Broke the rules to take a trade (`followed_plan = N`) twice in 10 → stop that strategy for 2 weeks.

## Strategies
| folder | strategy | forced seller | stage |
|---|---|---|---|
| `spinoff/` | Buy spin-offs after the unwanted shares are sold | Index funds and holders who got shares they didn't choose | **RETIRED v1** 2026-09-30: −11.5% net median over 22 spins. The entry was too early and the stop too tight. v2 idea: small spins, enter after ~day 28 |
| `taxloss/` | Buy December losers once the tax selling ends | US investors selling losers to reduce tax | **RETIRED** 2026-09-30: median net of fees negative |

## Lesson from the first retirement: the fee floor
At ~$60 a position, a round trip costs ~3.5%. **A strategy whose typical winning move is under ~5% cannot work at this size, however good the logic.** Only keep strategies that aim for moves measured in tens of percent over weeks or months (spin-offs, overhangs), or wait until the account can take positions large enough for fees to be under 1%.
| `overhang/` | Buy after a large registered share sale has been absorbed | Pre-IPO holders and insiders after lock-up / resale S-1 | IDEA (HMH) |
| `insider-cluster/` | Follow several insiders buying with their own money | Not a forced seller: an informed buyer | IDEA |

## Files
- `strategies/<name>/RULES.md`: the rules. Change them only with a dated note.
- `ideas/TICKER.md`: one per stock, the four-question thesis, written **before** entry.
- `journal/trades.csv`: the log. The `strategy` column must match a folder name here.
- IBKR: one watchlist per strategy, named `STRAT: <name>`.
