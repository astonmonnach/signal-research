"""Independent re-pull of Hyperliquid BTC funding history (audit)."""
import time, json, requests, pandas as pd
from datetime import datetime, timezone

URL = "https://api.hyperliquid.xyz/info"
start = int(datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
end = int(datetime(2026, 10, 4, tzinfo=timezone.utc).timestamp() * 1000)
rows, cur = [], start
while cur < end:
    for attempt in range(5):
        try:
            r = requests.post(URL, json={"type": "fundingHistory", "coin": "BTC", "startTime": cur, "endTime": end}, timeout=30)
            r.raise_for_status(); d = r.json(); break
        except Exception as e:
            print("retry", e); time.sleep(2 + attempt * 3)
    if not d:
        break
    rows.extend(d)
    last = d[-1]["time"]
    if last + 1 <= cur:
        break
    cur = last + 1
    print(len(rows), datetime.fromtimestamp(last / 1000, timezone.utc))
    time.sleep(0.3)
df = pd.DataFrame(rows)
df["fundingRate"] = df["fundingRate"].astype(float)
df["premium"] = df["premium"].astype(float)
df = df.drop_duplicates("time").sort_values("time")
df["ts"] = pd.to_datetime(df["time"], unit="ms", utc=True)
df.to_csv("audit_hl_btc_funding.csv", index=False)
print(len(df), df.ts.min(), df.ts.max())
