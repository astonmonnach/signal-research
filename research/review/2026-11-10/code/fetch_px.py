"""Daily bars (open, close, adjclose, volume, splits) for every ledger ticker plus benchmarks, cached to px.json."""
import csv, json, time, urllib.request, sys
from pathlib import Path
HERE = Path(__file__).parent
L = list(csv.DictReader(open(Path(__file__).resolve().parents[4] / "ledger/ledger.csv", encoding="utf-8")))
A = list(csv.DictReader(open(Path(__file__).resolve().parents[4] / "ledger/avoid_register.csv", encoding="utf-8")))
F = list(csv.DictReader(open(Path(__file__).resolve().parents[4] / "research/found/found.csv", encoding="utf-8")))
T = sorted({r["ticker"] for r in L} | {r["ticker"] for r in A} | {r["ticker"] for r in F} | {"IWM", "SPY", "XBI", "IWC"})
out_p = HERE / "px.json"
out = json.load(open(out_p)) if out_p.exists() else {}
todo = [t for t in T if t not in out]
print(len(T), "tickers,", len(todo), "to fetch", flush=True)
for i, t in enumerate(todo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d&events=split%7Cdiv"
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]; adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose")
            ts = r.get("timestamp") or []
            out[t] = {"ts": ts, "o": q.get("open"), "h": q.get("high"), "l": q.get("low"), "c": q.get("close"), "v": q.get("volume"), "a": adj,
                      "splits": [(v["date"], v["numerator"], v["denominator"]) for v in (r.get("events", {}).get("splits", {}) or {}).values()],
                      "name": r["meta"].get("longName") or r["meta"].get("shortName"), "exch": r["meta"].get("exchangeName"), "type": r["meta"].get("instrumentType")}
            break
        except Exception as e:
            if attempt == 2: out[t] = {"err": str(e)[:80]}
            time.sleep(1.5)
    time.sleep(0.2)
    if i % 100 == 99:
        json.dump(out, open(out_p, "w")); print(i + 1, flush=True)
json.dump(out, open(out_p, "w"))
print("done", len(out), "errors", sum(1 for v in out.values() if "err" in v))
