"""Acceptance times (UTC) for every filing linked in the market scans -> accept.json {accession18: iso utc}, plus each company's recent filings."""
import re, glob, json, time, urllib.request
from pathlib import Path
HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[4]
UA = {"User-Agent": "PersonalResearch research@example.com"}
need = {}
for f in sorted(glob.glob(str(ROOT / "watch/market/2026-*.md"))):
    for line in open(f, encoding="utf-8"):
        for cik, acc in re.findall(r"/data/(\d+)/(\d{18})/", line):
            need.setdefault(cik, set()).add(acc)
tick = json.load(open(ROOT / "research/movers/mv1/cache/company_tickers.json"))
import csv
led = {r["ticker"] for r in csv.DictReader(open(ROOT / "ledger/ledger.csv", encoding="utf-8"))}
t2c = {v["ticker"]: str(v["cik_str"]) for v in tick.values()}
for t in led:
    if t in t2c: need.setdefault(t2c[t], set())
acc_p, fil_p = HERE / "accept.json", HERE / "filings.json"
acc = json.load(open(acc_p)) if acc_p.exists() else {}
fil = json.load(open(fil_p)) if fil_p.exists() else {}
todo = [c for c in need if c not in fil]
print(len(need), "ciks,", len(todo), "to fetch", flush=True)
for i, c in enumerate(todo):
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/submissions/CIK{int(c):010d}.json", headers=UA), timeout=30).read())
        r = d["filings"]["recent"]
        rows = [(r["accessionNumber"][k].replace("-", ""), r["form"][k], r["filingDate"][k], r["acceptanceDateTime"][k], r["items"][k]) for k in range(len(r["form"])) if r["filingDate"][k] >= "2026-08-15"]
        fil[c] = {"tickers": d.get("tickers", []), "rows": rows}
        for a, form, fd, adt, items in rows:
            acc[a] = adt
    except Exception as e:
        fil[c] = {"err": str(e)[:60], "rows": []}
    time.sleep(0.13)
    if i % 200 == 199:
        json.dump(acc, open(acc_p, "w")); json.dump(fil, open(fil_p, "w")); print(i + 1, flush=True)
json.dump(acc, open(acc_p, "w")); json.dump(fil, open(fil_p, "w"))
want = {a for s in need.values() for a in s}
print("done; filings wanted", len(want), "with times", sum(a in acc for a in want))
