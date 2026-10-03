"""Pull Hyperliquid BTC perp funding history (hourly) from the public info API."""
import json, time, urllib.request, csv, sys
URL = "https://api.hyperliquid.xyz/info"
def post(body):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
start = int(time.mktime((2023, 1, 1, 0, 0, 0, 0, 0, 0))) * 1000
end = int(time.time() * 1000)
rows, t = [], start
while t < end:
    batch = post({"type": "fundingHistory", "coin": "BTC", "startTime": t, "endTime": end})
    if not batch: break
    rows += batch
    last = batch[-1]["time"]
    if last <= t: break
    t = last + 1
    time.sleep(0.25)
seen = {}
for r in rows: seen[r["time"]] = r
rows = [seen[k] for k in sorted(seen)]
with open("hl_btc_funding.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["time_ms", "funding_rate", "premium"])
    for r in rows: w.writerow([r["time"], r["fundingRate"], r.get("premium", "")])
import datetime as dt
print(len(rows), "hourly funding prints from", dt.datetime.utcfromtimestamp(rows[0]["time"]/1000), "to", dt.datetime.utcfromtimestamp(rows[-1]["time"]/1000))
