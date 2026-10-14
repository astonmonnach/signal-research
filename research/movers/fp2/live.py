"""FP2 forward paper log (rules: research/movers/PREREG_FP2.md). Paper only.

    python research/movers/fp2/live.py signal   # about 19:40 UTC on US trading days: logs today's S1/S2 signals
    python research/movers/fp2/live.py fill     # after the next US open: fills the signal-day close and the next open
    python research/movers/fp2/live.py status   # forward count, mean after 2% costs, interval

Signal: price $1 to $3, today's volume so far >= 5x the average of the previous 20 sessions, median dollar volume of the
previous 20 sessions >= $250k. S1 also needs a reverse split in the last 90 days. Data: the free Nasdaq stock screener
(price and volume so far for every listed stock) and Yahoo daily bars (history, splits, and the closes and opens used to fill).
"""
import csv, json, os, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "live_signals.csv")
COLS = ["signal_date", "run_utc", "late", "ticker", "name", "signal", "price_at_run", "volume_so_far", "avg20_volume",
        "vol_multiple", "median20_dollar_vol", "split_date", "split_ratio", "entry_close", "exit_open", "exit_date",
        "ret_gross", "ret_net2", "status"]
NASDAQ = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
          "Accept": "application/json, text/plain, */*", "Origin": "https://www.nasdaq.com", "Referer": "https://www.nasdaq.com/"}
YH = {"User-Agent": "Mozilla/5.0"}


def get_json(url, headers, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40).read())
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)


def yahoo(ticker, rng="6mo"):
    """Daily bars (date -> o, c, v) and splits [(date, ratio)] from Yahoo."""
    j = get_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval=1d&events=splits", YH)
    r = j["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    bars = {}
    for t, o, c, v in zip(r.get("timestamp", []), q["open"], q["close"], q["volume"]):
        if c is not None:
            bars[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")] = (o, c, v or 0)
    splits = [(datetime.fromtimestamp(s["date"], timezone.utc).strftime("%Y-%m-%d"), s["numerator"] / s["denominator"])
              for s in (r.get("events", {}) or {}).get("splits", {}).values()]
    return bars, splits


def read_log():
    return list(csv.DictReader(open(LOG, encoding="utf-8"))) if os.path.exists(LOG) else []


def write_log(rows):
    with open(LOG, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)


def signal():
    now = datetime.now(timezone.utc); today = now.strftime("%Y-%m-%d")
    late = now.hour > 20 or (now.hour == 20 and now.minute > 0)      # after the 20:00 UTC close (EDT); see PREREG
    rows = read_log()
    if any(r["signal_date"] == today for r in rows):
        print("already ran today"); return
    j = get_json("https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true", NASDAQ)
    cand = []
    for r in j["data"]["rows"]:
        try:
            px = float(r["lastsale"].replace("$", "").replace(",", "")); vol = float(r["volume"])
        except (ValueError, KeyError):
            continue
        sym = r["symbol"].strip()
        if 1 <= px < 3 and vol * px >= 250e3 and sym.isalpha():        # rough prefilter; the real tests follow
            cand.append((sym, r["name"][:60], px, vol))
    new = []
    for sym, name, px, vol in cand:
        try:
            bars, splits = yahoo(sym)
        except Exception:
            continue
        hist = [(d, b) for d, b in sorted(bars.items()) if d < today]
        if len(hist) < 20:
            continue
        last20 = hist[-20:]
        avg20 = float(np.mean([b[2] for _, b in last20]))
        med_dv = float(np.median([b[1] * b[2] for _, b in last20]))
        if avg20 <= 0 or vol < 5 * avg20 or med_dv < 250e3:
            continue
        cutoff = (now - timedelta(days=90)).strftime("%Y-%m-%d")
        rs = [(d, ratio) for d, ratio in splits if cutoff <= d <= today and ratio < 1]   # reverse split: fewer shares
        base = dict(signal_date=today, run_utc=now.strftime("%H:%M"), late=late, ticker=sym, name=name, price_at_run=px,
                    volume_so_far=int(vol), avg20_volume=int(avg20), vol_multiple=round(vol / avg20, 2), median20_dollar_vol=int(med_dv),
                    split_date=rs[-1][0] if rs else "", split_ratio=round(rs[-1][1], 6) if rs else "", status="open")
        new.append(dict(base, signal="S2"))
        if rs:
            new.append(dict(base, signal="S1"))
        time.sleep(0.2)
    write_log(rows + new)
    print(f"{today} {now:%H:%M} UTC: {len(cand)} candidates priced $1-3, {sum(1 for r in new if r['signal'] == 'S2')} S2 and "
          f"{sum(1 for r in new if r['signal'] == 'S1')} S1 signals" + (" (LATE run)" if late else ""))
    for r in new:
        print(f"  {r['signal']} {r['ticker']:6s} ${r['price_at_run']:.2f} volume {r['vol_multiple']}x" + (f" split {r['split_date']}" if r["split_date"] else ""))


def fill():
    rows = read_log(); changed = 0
    for r in rows:
        if r["status"] != "open":
            continue
        try:
            bars, _ = yahoo(r["ticker"], "1mo")
        except Exception:
            continue
        days = sorted(bars)
        if r["signal_date"] not in bars:
            continue
        after = [d for d in days if d > r["signal_date"]]
        if not after or bars[after[0]][0] is None:
            continue
        c0 = bars[r["signal_date"]][1]; o1 = bars[after[0]][0]
        r.update(entry_close=round(c0, 4), exit_open=round(o1, 4), exit_date=after[0], ret_gross=round(o1 / c0 - 1, 6),
                 ret_net2=round(o1 / c0 - 1 - 0.02, 6), status="filled")
        changed += 1
        time.sleep(0.2)
    write_log(rows); print(f"filled {changed}")


def status():
    rows = [r for r in read_log() if r["status"] == "filled"]
    for s, need in (("S2", 100), ("S1", 40)):
        x = [r for r in rows if r["signal"] == s]
        if not x:
            print(f"{s}: 0 forward trades (judged at {need})"); continue
        v = np.array([float(r["ret_net2"]) for r in x]); d = np.array([r["signal_date"] for r in x])
        days = np.unique(d); sm = np.array([v[d == q].sum() for q in days]); n = np.array([(d == q).sum() for q in days])
        rng = np.random.default_rng(20261014); dr = rng.integers(0, len(days), (2000, len(days)))
        m = sm[dr].sum(1) / n[dr].sum(1)
        print(f"{s}: {len(v)} of {need} forward trades | mean after 2% {v.mean():+.2%} [{np.percentile(m, 2.5):+.2%}, {np.percentile(m, 97.5):+.2%}] "
              f"| median {np.median(v):+.2%} | winners {(v > 0).mean():.0%}" + (" | READY TO JUDGE" if len(v) >= need else ""))


if __name__ == "__main__":
    {"signal": signal, "fill": fill, "status": status}[sys.argv[1] if len(sys.argv) > 1 else "status"]()
