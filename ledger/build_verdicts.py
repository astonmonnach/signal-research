"""Verdict scoreboard: are our own verdicts (OWN / WATCH / AVOID) right? -> ledger/verdicts.csv and ledger/VERDICTS.md

The ledger tests signal categories and the calls record tests committed calls. This tests every dossier verdict.
Each time a stock's verdict in stocks/README.md is new or changes, it is snapshotted with that day's close (append-only).
Each verdict is then measured from that close against the stock's size benchmark (IWM micro/small, MDY mid, SPY large),
with cash and spun-off shares added back. If the verdicts mean anything, OWN should beat WATCH, and WATCH should beat AVOID.

Usage: python ledger/build_verdicts.py   (runs in the morning workflow)
"""
import csv, json, sys, datetime as dt
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "briefing"))
import recap  # noqa: E402

CSV = ROOT / "ledger/verdicts.csv"
MD = ROOT / "ledger/VERDICTS.md"
COLS = ["date", "ticker", "verdict", "score", "close"]
FIRST_BASE = "2026-10-05"   # the first verdicts were written during 5 Oct; measured from that day's close (after they were made)


def group(v):
    w = v.split()[0].upper().strip(";(:") if v else ""
    return w if w in ("OWN", "WATCH", "AVOID") else ("AVOID" if w == "KILL" else w or "?")


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8"))) if CSV.exists() else []
    latest = {}
    for r in rows: latest[r["ticker"]] = r
    caps = json.load(open(ROOT / "watch/caps.json", encoding="utf-8"))["stocks"] if (ROOT / "watch/caps.json").exists() else {}
    today = dt.date.today().isoformat()
    first_run = not rows                                    # the first snapshot uses the day the verdicts were written
    for t, i in recap.dossiers().items():
        if t in latest and latest[t]["verdict"] == i["verdict"]: continue
        d = FIRST_BASE if first_run else today
        b = [x for x in recap.bars(t) if x[0].isoformat() <= d]
        if not b: continue
        rows.append(dict(date=d, ticker=t, verdict=i["verdict"], score=i.get("score", ""), close=round(b[-1][1], 4)))
        latest[t] = rows[-1]
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    res = []
    for t, r in latest.items():
        base = dt.date.fromisoformat(r["date"])
        m, bench = recap.holder_pct(t, base), recap.holder_pct(recap.bench_of(t, caps), base)
        if m is None or bench is None: continue
        res.append(dict(r, g=group(r["verdict"]), move=m, vs=m - bench, bench=recap.bench_of(t, caps)))
    L = ["# Verdict scoreboard: are our own verdicts right?", "",
         "Every dossier verdict, measured from the close on the day it was given against the stock's size benchmark (IWM for micro and "
         "small caps, MDY for mid caps, SPY for large caps). Cash and spun-off shares are added back. If the verdicts mean anything, "
         "**OWN > WATCH > AVOID**. A verdict only counts as tested after 20 trading days. Built by `ledger/build_verdicts.py`.", "",
         "| verdict | n | average vs benchmark | median | beat benchmark |", "|---|---|---|---|---|"]
    for g in ("OWN", "WATCH", "AVOID"):
        xs = [r["vs"] for r in res if r["g"] == g]
        if xs:
            L.append(f"| {g} | {len(xs)} | {mean(xs):+.1f} pts | {median(xs):+.1f} pts | {sum(x > 0 for x in xs)}/{len(xs)} |")
    L += ["", "| ticker | verdict | since | move | vs benchmark |", "|---|---|---|---|---|"]
    for r in sorted(res, key=lambda r: (r["g"], -r["vs"])):
        L.append(f"| {r['ticker']} | {r['verdict']} {r['score']} | {r['date']} | {r['move']:+.1f}% | {r['vs']:+.1f} pts vs {r['bench']} |")
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"verdicts: {len(res)} tracked -> {MD.relative_to(ROOT)}")
    for g in ("OWN", "WATCH", "AVOID"):
        xs = [r["vs"] for r in res if r["g"] == g]
        if xs: print(f"  {g}: n {len(xs)}, avg {mean(xs):+.1f} pts vs benchmark, beat {sum(x > 0 for x in xs)}/{len(xs)}")


if __name__ == "__main__":
    main()
