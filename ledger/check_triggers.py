"""Every WATCH carries a dated, checkable trigger (rule 2026-10-20). Checks ledger/triggers.csv.

A WATCH's trigger, when it fires, makes a TRADE plan. A TRACKED name's trigger means re-read it for WATCH.
A trigger that passes its deadline without firing is marked expired, not left open.

Usage: python ledger/check_triggers.py   (prints problems; exit 1 if any)
Run it after verdicts are written in every research run, and fix every problem before committing.
"""
import csv
import json
import re
import sys
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "ledger" / "triggers.csv"
COLS = ["id", "set_date", "ticker", "verdict", "strategy", "trigger", "kind", "value", "deadline",
        "source", "status", "status_date", "note"]
VERDICTS = {"WATCH", "TRACKED"}
KINDS = {"date", "price_above", "price_below", "filing", "manual"}
STATUSES = {"open", "fired", "expired", "cancelled"}
FILING = re.compile(r"^[A-Z0-9/\-]+(\|[A-Z0-9/\-]+)*@[A-Z0-9.\-]+$")


def _date(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def problems(rows, verdicts, strategies, today, watchlist=None):
    """rows: triggers.csv rows; verdicts: {ticker: current dossier verdict}; strategies: channel names;
    watchlist: tickers the daily filing check follows (None skips that check)."""
    out, seen = [], set()
    for r in rows:
        rid = r.get("id") or "?"
        where = f"{rid} {r.get('ticker', '?')}"
        if rid in seen:
            out.append(f"{where}: duplicate id")
        seen.add(rid)
        for col in ("set_date", "ticker", "verdict", "strategy", "trigger", "kind", "deadline", "source", "status"):
            if not (r.get(col) or "").strip():
                out.append(f"{where}: {col} is empty")
        if r.get("verdict") and r["verdict"] not in VERDICTS:
            out.append(f"{where}: verdict must be one of {sorted(VERDICTS)}")
        if r.get("strategy") and r["strategy"] not in strategies:
            out.append(f"{where}: strategy {r['strategy']!r} is not a channel in watch/strategies.json")
        if r.get("kind") and r["kind"] not in KINDS:
            out.append(f"{where}: kind must be one of {sorted(KINDS)}")
        if r.get("status") and r["status"] not in STATUSES:
            out.append(f"{where}: status must be one of {sorted(STATUSES)}")
        value = (r.get("value") or "").strip()
        if r.get("kind") in ("price_above", "price_below"):
            try:
                float(value)
            except ValueError:
                out.append(f"{where}: value must be a price for {r['kind']}")
        if r.get("kind") == "filing" and not FILING.match(value):
            out.append(f"{where}: value must be FORM|FORM@TICKER for a filing trigger")
        set_d, dead = _date(r.get("set_date")), _date(r.get("deadline"))
        if r.get("deadline") and dead is None:
            out.append(f"{where}: deadline is not an ISO date")
        if set_d and dead and dead < set_d:
            out.append(f"{where}: deadline is before set_date")
        if r.get("status") == "open" and dead and dead < today:
            out.append(f"{where}: overdue since {dead}; mark it fired, expired or cancelled")
        if watchlist is not None and r.get("status") == "open" and r.get("ticker") not in watchlist:
            out.append(f"{where}: not on watch/watchlist.json, so the daily filing check would miss its filings (LESSONS 2026-10-21)")
    open_tickers = {r.get("ticker") for r in rows if r.get("status") == "open"}
    for t, v in sorted(verdicts.items()):
        if (v or "").split()[0].upper().strip(";(:.") == "WATCH" and t not in open_tickers:
            out.append(f"{t}: verdict is WATCH but there is no open trigger row (no row, no WATCH)")
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "briefing"))
    import recap
    rows = list(csv.DictReader(open(CSV, encoding="utf-8"))) if CSV.exists() else []
    verdicts = {t: i["verdict"] for t, i in recap.dossiers().items()}
    strategies = {s["channel"] for s in json.load(open(ROOT / "watch" / "strategies.json", encoding="utf-8"))["strategies"]}
    watchlist = set(json.load(open(ROOT / "watch" / "watchlist.json", encoding="utf-8"))["tickers"])
    found = problems(rows, verdicts, strategies, dt.date.today(), watchlist)
    print("\n".join(found) if found else f"triggers: {len(rows)} rows, no problems")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
