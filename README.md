# Signal Lab: catalyst research

A research log for event-driven trades in US small caps. Collectors read SEC filings, Department of War (DoD) contract announcements and company press releases. Anything that looks like a catalyst is logged and tracked against IWM from the next open, and a few small real positions are traded by written rules. The repo is public: nothing in it is advice.

## Where to look

| I want… | Open |
|---|---|
| **Today's scan**: everything found on a date | `scans/YYYY-MM-DD.md` (newest first in [scans/README.md](scans/README.md)) |
| **A stock's dossier**: deep dive, status, timeline, performance | `stocks/TICKER.md`, for example [stocks/MTUS.md](stocks/MTUS.md) (all of them: [stocks/README.md](stocks/README.md)) |
| **Weekly / monthly / quarterly update** | `reports/weekly/YYYY-Www.md`, `reports/monthly/YYYY-MM.md`, `reports/quarterly/YYYY-Qn.md` ([reports/README.md](reports/README.md)) |
| **Public calls**: the conviction track record, append-only, each marked from the next open vs IWM and a control | [calls/README.md](calls/README.md). Add a call as a new row in `calls/CALLS.csv` (never edit or delete one) |
| **Long-term research** (6–36 months): nth-order plus balance-sheet, dilution and "already run" checks, tracked against SPY | [longterm/README.md](longterm/README.md), method: [longterm/METHOD.md](longterm/METHOD.md). Candidates: `longterm/candidates.csv` |
| **Discord**: what each channel gets, and the setup | [briefing/discord_setup.py](briefing/discord_setup.py) (channel intros + welcome guide), [briefing/notify.py](briefing/notify.py) (the `DISCORD_WEBHOOKS` secret format) |
| **The ledger**: every scan item against IWM | [ledger/LEDGER.md](ledger/LEDGER.md). Rules: [ledger/RULES.md](ledger/RULES.md). Raw rows: `ledger/ledger.csv`. Ideas and watch-only setups: `ledger/manual_calls.csv` |
| **The morning briefing** | `briefings/YYYY-MM-DD.md`, also sent to Discord (one channel per section) and Telegram |
| **Open positions and trades** | [watch/positions.md](watch/positions.md), [journal/trades.csv](journal/trades.csv) |
| **Trade theses**, written before entry | `ideas/TICKER.md` ([MTUS](ideas/MTUS.md), [VYLR](ideas/VYLR.md)) |
| **Research** | `research/`: deep reports (e.g. [research/filings-2026-10-04/](research/filings-2026-10-04/)), studies, scans. `strategies/`: rules and backtests ([strategy book](strategies/README.md)). `posts/`: X threads |
| **Dated events** | [calendar/catalyst-dates.ics](calendar/catalyst-dates.ics) (subscribe to it in any calendar app) |
| **Raw collector output** | `watch/market/` (market-wide SEC scan), `watch/dod/` (DoD contracts), `watch/digests/` (watchlist filings and evening triage), `watch/press/` and `data/press/` (press releases), `watch/context/` (peers and commodities), `data/signals.csv` (S1 signals), `data/crypto/` |
| **The plan and the data sources** | [PLAN.md](PLAN.md), [SOURCES.md](SOURCES.md) |

What each generated file holds:
- **`scans/YYYY-MM-DD.md`**: one file per date. Sections: S1 contract signals, watchlist filings, the market-wide scan by category (with the ledger's move in the 5 days before, the found day's move and liquidity), press releases, new setups and triage notes. Every item links to its source.
- **`stocks/TICKER.md`**: one per ticker on the watchlist (`watch/watchlist.json`), in `ledger/manual_calls.csv` or in `journal/trades.csv`. The top part is a hand-written deep dive. Everything below the `<!-- AUTO … -->` marker is rebuilt: status (latest price, change since first found and against IWM, position P&L, peers and sympathy flag, next dated events), a timeline of every dated mention (one line per date, linked to that day's scan), and every ledger row for the stock. To add a stock, put it on the watchlist or log it in `manual_calls.csv`; the next run creates its dossier.
- **`reports/…`**: covers one period. Sections: counts of what the scans found, the biggest movers since found against IWM, ledger stats by category (tradeable only), positions and P&L, each watchlist stock's move with a one-line reason from its dossier, setups that spiked or collapsed, what's coming up, and links.

## How everything is generated

| When | What runs | Writes |
|---|---|---|
| **Evening job**, ~21:30 UK (a Claude scheduled task on the trader's machine, not GitHub) | `watch/check_filings.py`, `watch/scan_market.py`, `collectors/s1_dod.py`, `collectors/outcomes.py`, then Claude reads the hits and writes the triage | `watch/digests/`, `watch/market/`, `watch/dod/`, `data/signals.csv`, `data/outcomes.csv`, `watch/digests/YYYY-MM-DD-triage.md` |
| **GitHub Actions `morning-briefing`**, weekdays. Several slots from 04:07 to 06:07 UTC, because GitHub often starts late; the briefing and the weekly Discord post go out once a day | `collectors/positions.py`, `collectors/nq_regime.py`, `collectors/market_context.py`, `ledger/build_ledger.py`, `calls/build_calls.py --announce`, `longterm/build_longterm.py --post-weekly`, **`reports/build_scans.py`** (today and the 6 days before), **`reports/build_stocks.py`**, **`reports/build_periodic.py --current --post-weekly`**, then `briefing/morning.py`. Commits the outputs | `watch/positions.md`, `watch/nq_regime.md`, `watch/context/`, `ledger/`, `calls/`, `longterm/`, `scans/`, `stocks/`, `reports/`, `briefings/` |
| **GitHub Actions `announce`**, on every push that changes `calls/CALLS.csv` or `longterm/candidates.csv` | `calls/build_calls.py --announce`, `longterm/build_longterm.py --post-weekly` (each call and candidate is posted to Discord once) | `calls/announced.json`, `longterm/` |
| **GitHub Actions `discord-setup`**, by hand once | `briefing/discord_setup.py --intro`, then the same announcements | Discord only |
| **GitHub Actions `press-wires`**, every 20 minutes | `collectors/press_wires.py` | `data/press/YYYY-MM-DD.csv`, `watch/press/` |
| **GitHub Actions `crypto-trending`**, every 30 minutes | `collectors/crypto_trending.py` (C1); `collectors/c2_convergence.py` (C2, even hours) | `data/crypto/` |
| **By hand** | ideas, research, strategies, deep dives in `stocks/`, `calls/CALLS.csv`, `ledger/manual_calls.csv`, `journal/trades.csv`, the calendar | |

The three report generators only read files the jobs above wrote (`reports/sources.py` holds the shared readers). The exception is `build_periodic.py`, which fetches Yahoo daily closes to measure moves over a period. They are idempotent: re-running with the same inputs changes nothing. **Don't edit generated files** (`scans/`, the AUTO part of `stocks/`, `reports/weekly|monthly|quarterly/`, `ledger/LEDGER.md`, `briefings/`): fix the input and re-run.

Discord channels (`briefing/notify.py`; one webhook secret each): `#briefing` (`DISCORD_WEBHOOK_URL`), `#calendar`, `#ledger`, `#press`, `#filings`, `#watchlist`, `#setups`, `#crypto`, and `#reports` (`DISCORD_WEBHOOK_REPORTS`: last week's report summary, Mondays).

## Running it by hand

Everything is Python 3.12, standard library only.

```
python reports/build_scans.py                    # scans for today and the 6 days before (and any missing date)
python reports/build_scans.py --date 2026-10-02  # one date; --all rebuilds every date
python reports/build_stocks.py                   # every dossier (or: python reports/build_stocks.py MTUS VYLR)
python reports/build_periodic.py --period week --date 2026-10-02   # also month / quarter
python reports/build_periodic.py --current       # this week, month and quarter to date; --all rebuilds every period
python ledger/build_ledger.py                    # ledger/ledger.csv + LEDGER.md
python calls/build_calls.py                      # calls/README.md + marks.csv (--post N prints call N's facts for an X post)
python briefing/morning.py --dry-run             # print the briefing, send nothing
```
