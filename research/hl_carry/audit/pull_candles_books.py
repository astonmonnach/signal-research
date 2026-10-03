"""Pull HL perp BTC and spot UBTC/USDC (@142) candles + L2 books for the audit."""
import requests, time, json, pandas as pd
from datetime import datetime, timezone

U = "https://api.hyperliquid.xyz/info"


def candles(coin, interval, start_ms, end_ms):
    out, cur = [], start_ms
    while cur < end_ms:
        d = requests.post(U, json={"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": cur, "endTime": end_ms}}, timeout=30).json()
        if not d:
            break
        out.extend(d)
        last = d[-1]["t"]
        if last + 1 <= cur:
            break
        cur = last + 1
        if len(d) < 10:
            break
        time.sleep(0.3)
    df = pd.DataFrame(out).drop_duplicates("t")
    for c in "ohlcv":
        df[c] = df[c].astype(float)
    df["ts"] = pd.to_datetime(df.t, unit="ms", utc=True)
    return df[["ts", "o", "h", "l", "c", "v", "n"]]


now = int(time.time() * 1000)
start = int(datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
for coin, tag in [("BTC", "perp"), ("@142", "spot")]:
    for iv in ["1h", "1d", "15m"]:
        df = candles(coin, iv, start, now)
        df.to_csv(f"hl_{tag}_{iv}.csv", index=False)
        print(tag, iv, len(df), df.ts.min(), df.ts.max())

books = []
for i in range(6):
    snap = {"t": datetime.now(timezone.utc).isoformat()}
    for coin in ["BTC", "@142"]:
        snap[coin] = requests.post(U, json={"type": "l2Book", "coin": coin}, timeout=30).json()
        snap[coin + "_agg4"] = requests.post(U, json={"type": "l2Book", "coin": coin, "nSigFigs": 4}, timeout=30).json()
        snap[coin + "_agg3"] = requests.post(U, json={"type": "l2Book", "coin": coin, "nSigFigs": 3}, timeout=30).json()
    books.append(snap)
    time.sleep(20)
json.dump(books, open("l2_snapshots.json", "w"))
print("books", len(books))
