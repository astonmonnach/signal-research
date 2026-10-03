"""C1 TRENDING: forward-log Solana tokens the moment they first trend, then score them.

Usage:  python collectors/crypto_trending.py      (run every ~15 min)
Each run:
  1. pulls GeckoTerminal Solana trending pools (5m / 1h / 6h / 24h lists) + DexScreener paid boosts
  2. logs every pool seen for the FIRST time -> data/crypto/trending_signals.csv
  3. checks pending horizons (1h, 6h, 24h, 7d) -> data/crypto/trending_outcomes.csv
No money involved. The question: what does buying at "first trending" actually return,
net of fees and slippage on a ~$100 position?
"""
import csv
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "crypto"
SIGNALS, OUTCOMES = DIR / "trending_signals.csv", DIR / "trending_outcomes.csv"
GT = "https://api.geckoterminal.com/api/v2"
POSITION_USD = 100
HORIZONS = {"1h": timedelta(hours=1), "6h": timedelta(hours=6), "24h": timedelta(hours=24), "7d": timedelta(days=7)}
SIG_COLS = ["signal_id", "detected_at_utc", "pool", "token", "name", "dex", "first_list", "first_rank", "boosted",
            "boost_amount", "price_usd", "liquidity_usd", "mcap_usd", "fdv_usd", "pool_age_h", "chg_5m", "chg_1h",
            "chg_6h", "chg_24h", "vol_1h", "buys_1h", "sells_1h", "buyers_1h", "est_cost_pct"]
OUT_COLS = ["signal_id", "horizon", "checked_at_utc", "elapsed_h", "late", "price_usd", "liquidity_usd", "ret_pct", "ret_net_pct", "rugged"]


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(5 * (attempt + 1))         # GeckoTerminal free tier: ~30 calls/min
    return None


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def est_cost_pct(liq):
    """Round trip: ~0.3% swap fee each way + price impact of a $100 order on a constant-product pool."""
    if not liq:
        return None
    impact = 2 * POSITION_USD / liq                 # ≈ 2x order size / pool depth
    return round(2 * (0.3 + 100 * impact), 2)


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8"))) if path.exists() else []


def append(path, cols, rows):
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerows(rows)


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    signals = read(SIGNALS)
    seen = {s["pool"] for s in signals}

    boosts = {}
    for b in get("https://api.dexscreener.com/token-boosts/latest/v1") or []:
        if b.get("chainId") == "solana":
            boosts[b["tokenAddress"]] = b.get("totalAmount") or b.get("amount")

    new_rows = []
    for dur in ("5m", "1h", "6h", "24h"):
        data = get(f"{GT}/networks/solana/trending_pools?duration={dur}&include=base_token,dex")
        time.sleep(2.5)
        if not data:
            continue
        for rank, p in enumerate(data["data"], 1):
            a, pool = p["attributes"], p["attributes"]["address"]
            if pool in seen:
                continue
            seen.add(pool)
            token = p["relationships"]["base_token"]["data"]["id"].removeprefix("solana_")
            pc, tx, vol = a.get("price_change_percentage", {}), a.get("transactions", {}).get("h1", {}), a.get("volume_usd", {})
            created = a.get("pool_created_at")
            age = (now - datetime.fromisoformat(created.replace("Z", "+00:00"))).total_seconds() / 3600 if created else None
            liq = f(a.get("reserve_in_usd"))
            new_rows.append({
                "signal_id": f"C1-{now:%Y%m%d%H%M}-{pool[:8]}", "detected_at_utc": stamp, "pool": pool,
                "token": token, "name": a.get("name"), "dex": p["relationships"].get("dex", {}).get("data", {}).get("id"),
                "first_list": dur, "first_rank": rank, "boosted": token in boosts, "boost_amount": boosts.get(token),
                "price_usd": a.get("base_token_price_usd"), "liquidity_usd": liq, "mcap_usd": a.get("market_cap_usd"),
                "fdv_usd": a.get("fdv_usd"), "pool_age_h": None if age is None else round(age, 2),
                "chg_5m": pc.get("m5"), "chg_1h": pc.get("h1"), "chg_6h": pc.get("h6"), "chg_24h": pc.get("h24"),
                "vol_1h": vol.get("h1"), "buys_1h": tx.get("buys"), "sells_1h": tx.get("sells"),
                "buyers_1h": tx.get("buyers"), "est_cost_pct": est_cost_pct(liq)})
    append(SIGNALS, SIG_COLS, new_rows)
    signals += new_rows

    # ---- outcomes: horizons that have now passed and aren't recorded yet ----
    done = {(o["signal_id"], o["horizon"]) for o in read(OUTCOMES)}
    due = []
    for s in signals:
        t0 = datetime.fromisoformat(s["detected_at_utc"].replace("Z", "+00:00"))
        for h, dt in HORIZONS.items():
            # record at the first run after the horizon passes; GitHub's schedule can run late,
            # so the actual elapsed time is stored and late checks are flagged instead of skipped
            if (s["signal_id"], h) not in done and t0 + dt <= now:
                due.append((s, h, (now - t0).total_seconds() / 3600, now > t0 + dt * 1.5 + timedelta(minutes=30)))
    pools = list({s["pool"] for s, *_ in due})
    info, checked = {}, set()
    for i in range(0, len(pools), 30):                 # multi endpoint takes up to 30 pools
        data = get(f"{GT}/networks/solana/pools/multi/{','.join(pools[i:i + 30])}")
        time.sleep(2.5)
        if data is None:          # request failed (rate limit): retry these pools next run, don't score them
            continue
        checked.update(pools[i:i + 30])
        for p in data.get("data", []):
            info[p["attributes"]["address"]] = p["attributes"]
    out_rows = []
    for s, h, elapsed, late in due:
        if s["pool"] not in checked:
            continue
        a = info.get(s["pool"])
        p0, l0 = f(s["price_usd"]), f(s["liquidity_usd"])
        if a is None:                                  # pool gone from the API: treat as dead
            out_rows.append({"signal_id": s["signal_id"], "horizon": h, "checked_at_utc": stamp,
                             "elapsed_h": round(elapsed, 2), "late": late,
                             "ret_pct": -100, "ret_net_pct": -100, "rugged": "missing"})
            continue
        p1, l1 = f(a.get("base_token_price_usd")), f(a.get("reserve_in_usd"))
        ret = (p1 / p0 - 1) * 100 if p0 and p1 else None
        cost = f(s["est_cost_pct"]) or 0
        rug = bool(l0 and l1 is not None and l1 < 0.1 * l0)
        out_rows.append({"signal_id": s["signal_id"], "horizon": h, "checked_at_utc": stamp,
                         "elapsed_h": round(elapsed, 2), "late": late, "price_usd": p1,
                         "liquidity_usd": l1, "ret_pct": None if ret is None else round(ret, 2),
                         # liquidity pulled: the price may still show a gain, but there's nothing left to sell into
                         "ret_net_pct": -100 if rug else (None if ret is None else round(max(ret - cost, -100), 2)),
                         "rugged": rug})
    append(OUTCOMES, OUT_COLS, out_rows)
    print(f"{stamp}: {len(new_rows)} new trending pools logged ({len(signals)} total), {len(out_rows)} outcomes recorded")


if __name__ == "__main__":
    main()
