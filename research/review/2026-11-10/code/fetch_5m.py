"""5-minute bars for the last 60 days, pre-market and after-hours included, for every ledger ticker -> i5/TICKER.json.gz"""
import csv, json, gzip, time, urllib.request, sys
from pathlib import Path
HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[4]
T = sorted({r["ticker"] for r in csv.DictReader(open(ROOT / "ledger/ledger.csv", encoding="utf-8"))} |
           {r["ticker"] for r in csv.DictReader(open(ROOT / "ledger/avoid_register.csv", encoding="utf-8"))} | {"IWM", "MSGK", "CCAP"})
out = HERE / "i5"; out.mkdir(exist_ok=True)
todo = [t for t in T if not (out / f"{t}.json.gz").exists()]
print(len(T), "tickers,", len(todo), "to fetch", flush=True)
for i, t in enumerate(todo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=5m&range=60d&includePrePost=true"
    d = {"err": "?"}
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            d = {"ts": r.get("timestamp") or [], "o": q.get("open"), "h": q.get("high"), "l": q.get("low"), "c": q.get("close"), "v": q.get("volume"),
                 "gmtoffset": r["meta"].get("gmtoffset")}
            break
        except Exception as e:
            d = {"err": str(e)[:80]}; time.sleep(2)
    with gzip.open(out / f"{t}.json.gz", "wt") as f:
        json.dump(d, f)
    time.sleep(0.15)
    if i % 100 == 99: print(i + 1, flush=True)
print("done")
