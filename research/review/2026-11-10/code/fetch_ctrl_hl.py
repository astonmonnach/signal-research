"""Control universe: a seeded random sample of unflagged US stocks by market-value bucket, daily bars cached to ctrl.json."""
import csv, json, random, time, urllib.request, re
from pathlib import Path
HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[4]
caps = json.load(open(ROOT / "watch/marketcap.json", encoding="utf-8"))["caps"]
flag = {r["ticker"] for r in csv.DictReader(open(ROOT / "ledger/ledger.csv", encoding="utf-8"))}
flag |= {r["ticker"] for r in csv.DictReader(open(ROOT / "ledger/avoid_register.csv", encoding="utf-8"))}
flag |= set(json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"])
ok = {t: c for t, c in caps.items() if c and c > 0 and t not in flag and re.fullmatch(r"[A-Z]{1,5}", t)
      and not (len(t) == 5 and t[-1] in "WUR")}
B = [(0, 50e6, 450), (50e6, 300e6, 450), (300e6, 2e9, 380), (2e9, 10e9, 180), (10e9, 1e15, 90)]
rng = random.Random(20261110)
pick = []
for lo, hi, n in B:
    pool = sorted(t for t, c in ok.items() if lo <= c < hi)
    pick += rng.sample(pool, min(n, len(pool)))
    print(f"{lo/1e6:.0f}-{hi/1e6:.0f}M pool {len(pool)}", flush=True)
out_p = HERE / "ctrl_hl.json"
out = json.load(open(out_p)) if out_p.exists() else {}
todo = [t for t in pick if t not in out]
print(len(pick), "controls,", len(todo), "to fetch", flush=True)
for i, t in enumerate(todo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=6mo&interval=1d&events=split%7Cdiv"
    for attempt in range(2):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]; adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose")
            out[t] = {"ts": r.get("timestamp") or [], "o": q.get("open"), "h": q.get("high"), "l": q.get("low"), "c": q.get("close"), "v": q.get("volume"), "a": adj,
                      "cap": caps[t], "type": r["meta"].get("instrumentType")}
            break
        except Exception as e:
            if attempt == 1: out[t] = {"err": str(e)[:80]}
            time.sleep(1.0)
    time.sleep(0.15)
    if i % 100 == 99:
        json.dump(out, open(out_p, "w")); print(i + 1, flush=True)
json.dump(out, open(out_p, "w"))
print("done", len(out), "errors", sum(1 for v in out.values() if "err" in v))
