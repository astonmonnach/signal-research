# Reports

Weekly (ISO weeks, Monday to Sunday), monthly and quarterly reports: what the scans found, the biggest movers since found against IWM, ledger stats by category, positions and P&L, every watchlist stock's move with a reason, setups that spiked or collapsed, and what's coming up. Built by `reports/build_periodic.py`; the current week, month and quarter are rebuilt every weekday morning by the `morning-briefing` workflow, and on Mondays last week's summary goes to Discord #reports.

## Weekly

- [2026-W41](weekly/2026-W41.md)
- [2026-W40](weekly/2026-W40.md)
- [2026-W39](weekly/2026-W39.md)
- [2026-W38](weekly/2026-W38.md)
- [2026-W37](weekly/2026-W37.md)
- [2026-W36](weekly/2026-W36.md)

## Monthly

- [2026-10](monthly/2026-10.md)
- [2026-09](monthly/2026-09.md)

## Quarterly

- [2026-Q4](quarterly/2026-Q4.md)
- [2026-Q3](quarterly/2026-Q3.md)

## Generators

- `reports/build_scans.py`: daily scans, `scans/YYYY-MM-DD.md`
- `reports/build_stocks.py`: stock dossiers, `stocks/TICKER.md` (only the part below the AUTO marker)
- `reports/build_periodic.py`: these reports (`--period week|month|quarter --date YYYY-MM-DD`, `--current`, `--all`)
- `reports/sources.py`: the shared readers all three use
