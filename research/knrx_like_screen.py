"""Screen: KNRX-like setups = fresh registered supply + exchange listing deficiency + cheap stock."""
import json, re, time, urllib.request, datetime as dt
UA = {"User-Agent": "PersonalResearch research@example.com"}
def get(url, ua=UA, js=True):
    r = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30).read()
    return json.loads(r) if js else r.decode("latin-1")
tick = {}
for v in get("https://www.sec.gov/files/company_tickers.json").values(): tick.setdefault(v["cik_str"], []).append(v["ticker"])
FORMS = ("EFFECT", "S-1", "S-1/A", "F-1", "F-1/A", "424B4", "424B3", "S-3", "F-3")
days = [dt.date(2026, 9, d) for d in range(14, 31)] + [dt.date(2026, 10, 1), dt.date(2026, 10, 2)]
cands = {}
for day in days:
    if day.weekday() > 4: continue
    q = (day.month - 1) // 3 + 1
    try: idx = get(f"https://www.sec.gov/Archives/edgar/daily-index/{day.year}/QTR{q}/form.{day:%Y%m%d}.idx", js=False)
    except Exception: continue
    for line in idx.splitlines():
        f = next((x for x in sorted(FORMS, key=len, reverse=True) if line.startswith(x + " ")), None)
        if not f: continue
        parts = line.split()
        try: cik = int(parts[-3])
        except ValueError: continue
        if cik in tick: cands.setdefault(cik, set()).add(f"{f} {day:%d%b}")
    time.sleep(0.15)
print("registered-supply candidates:", len(cands))
def yahoo(t):
    try:
        r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=3mo&interval=1d", ua={"User-Agent": "Mozilla/5.0"})["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        return [(c, v or 0) for c, v in zip(q["close"], q["volume"]) if c]
    except Exception: return None
out = []
for cik, ev in cands.items():
    t = tick[cik][0]
    b = yahoo(t); time.sleep(0.2)
    if not b or len(b) < 25: continue
    px = b[-1][0]
    if px > 5: continue
    adv = sum(c * v for c, v in b[-20:]) / 20
    run10 = max(c for c, _ in b[-10:]) / min(c for c, _ in b[-20:-10]) - 1
    try:
        sub = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"); time.sleep(0.15)
    except Exception: continue
    r = sub["filings"]["recent"]
    deficiency, promo_8k = [], 0
    for i in range(len(r["form"])):
        if r["filingDate"][i] < "2026-06-01": break
        if r["form"][i] == "8-K" and "3.01" in (r["items"][i] or ""): deficiency.append(r["filingDate"][i])
    out.append(dict(t=t, name=sub["name"][:32], px=px, adv=adv, run10=run10 * 100, ev=sorted(ev), defi=deficiency,
                    foreign=sub.get("category", "").startswith("Non") or any(f in str(ev) for f in ("F-1", "F-3"))))
out.sort(key=lambda x: (not x["defi"], x["px"]))
for x in out[:40]:
    print(f"{x['t']:6} ${x['px']:<6.2f} {x['name']:32} adv ${x['adv']/1e3:>7,.0f}k  max-run10d {x['run10']:+6.0f}%  deficiency {','.join(x['defi']) or '-':24} | {', '.join(x['ev'])[:70]}")
