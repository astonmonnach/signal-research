"""Hyperliquid scanner: which markets move big and clean, and can actually be traded?

Covers every perp on Hyperliquid: the main crypto list plus the builder-deployed exchanges (xyz, flx, vntl, km,
para, io ...), which carry stocks, leveraged funds like KORU, indexes, commodities and pre-IPO names.

For each market that passes the barriers (max leverage, 24h volume, open interest) it pulls hourly candles and
measures:
  hour_range_pct   typical (median) hourly high-low range, % of the open
  day_range_pct    typical (median) daily high-low range, % of the open (UTC days)
  days_10pct       share of days whose range was 10% or more
  clean            how cleanly price travels: net move / total distance moved, averaged over 24-hour windows
                   (1.0 = a straight line, near 0 = chop)
  score            day_range_pct x clean: big days that go somewhere
  quiet            outside the top 30 markets by 24h volume (the ones everyone is already watching)

Free public data, no key, no account, no orders. Every run is saved to crypto/hyperliquid/scans/ and the candles
to crypto/hyperliquid/cache/ (gitignored) so rules can be tested on them later.

Run: python crypto/hyperliquid/scan.py [--min-lev 10] [--min-vol 1e6] [--min-oi 5e5] [--days 30] [--top 25]
"""
import argparse
import csv
import json
import statistics as st
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = "https://api.hyperliquid.xyz/info"
H_MS = 3_600_000
QUIET_RANK = 30


def info(body, tries=5):
    data = json.dumps(body).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            raise


def cleanness(closes, n=24):
    """Average over non-overlapping n-bar windows of |net move| / total distance moved."""
    out = []
    for s in range(0, len(closes) - n, n):
        w = closes[s:s + n + 1]
        path = sum(abs(b - a) for a, b in zip(w, w[1:]))
        if path > 0:
            out.append(abs(w[-1] - w[0]) / path)
    return st.mean(out) if out else 0.0


def daily_bars(hours):
    """Group hourly bars into UTC days; keep days with at least 20 hours."""
    days = {}
    for b in hours:
        d = datetime.fromtimestamp(b["t"] / 1000, UTC).date()
        days.setdefault(d, []).append(b)
    out = []
    for d in sorted(days):
        bs = sorted(days[d], key=lambda b: b["t"])
        if len(bs) >= 20:
            out.append({"d": d, "o": bs[0]["o"], "h": max(b["h"] for b in bs), "l": min(b["l"] for b in bs),
                        "c": bs[-1]["c"], "v": sum(b["v"] for b in bs)})
    return out


def profile(hours):
    hr = [(b["h"] - b["l"]) / b["o"] * 100 for b in hours if b["o"] > 0]
    days = daily_bars(hours)
    dr = [(d["h"] - d["l"]) / d["o"] * 100 for d in days if d["o"] > 0]
    return {
        "hour_range_pct": st.median(hr) if hr else 0.0,
        "day_range_pct": st.median(dr) if dr else 0.0,
        "days_10pct": (sum(x >= 10 - 1e-9 for x in dr) / len(dr)) if dr else 0.0,
        "clean": cleanness([b["c"] for b in hours], 24),
        "days": len(dr),
    }


def passes(m, *, min_lev, min_vol, min_oi):
    return (not m["delisted"]) and m["max_lev"] >= min_lev and m["vol_24h"] >= min_vol and m["oi_usd"] >= min_oi


def markets():
    """Every perp on every Hyperliquid perp exchange, with leverage, volume and open interest."""
    out = []
    for d in info({"type": "perpDexs"}):
        dex = d["name"] if d else ""
        body = {"type": "metaAndAssetCtxs"} | ({"dex": dex} if dex else {})
        meta, ctxs = info(body)
        for u, c in zip(meta["universe"], ctxs):
            mark = float(c.get("markPx") or 0)
            prev = float(c.get("prevDayPx") or 0)
            out.append({
                "coin": u["name"], "dex": dex or "main", "max_lev": int(u.get("maxLeverage") or 0),
                "delisted": bool(u.get("isDelisted")), "mark": mark,
                "chg_24h_pct": (mark / prev - 1) * 100 if prev else 0.0,
                "vol_24h": float(c.get("dayNtlVlm") or 0), "oi_usd": float(c.get("openInterest") or 0) * mark,
                "funding_hr_pct": float(c.get("funding") or 0) * 100,
            })
    ranked = sorted(out, key=lambda m: -m["vol_24h"])
    for i, m in enumerate(ranked, 1):
        m["vol_rank"] = i
    return out


def candles(coin, days):
    end = int(time.time() * 1000)
    raw = info({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": end - days * 24 * H_MS,
                                                     "endTime": end}})
    return [{"t": int(b["t"]), "o": float(b["o"]), "h": float(b["h"]), "l": float(b["l"]), "c": float(b["c"]),
             "v": float(b["v"])} for b in raw]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-lev", type=int, default=10)
    ap.add_argument("--min-vol", type=float, default=1e6)
    ap.add_argument("--min-oi", type=float, default=5e5)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    allm = markets()
    keep = [m for m in allm if passes(m, min_lev=a.min_lev, min_vol=a.min_vol, min_oi=a.min_oi)]
    print(f"{len(allm)} markets on {len({m['dex'] for m in allm})} exchanges; {len(keep)} pass the barriers "
          f"(leverage {a.min_lev}x+, 24h volume ${a.min_vol:,.0f}+, open interest ${a.min_oi:,.0f}+)")

    stamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
    cache = HERE / "cache" / stamp
    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for m in keep:
        try:
            hours = candles(m["coin"], a.days)
        except Exception as e:
            print(f"  {m['coin']}: candles failed ({type(e).__name__})")
            continue
        time.sleep(0.25)
        if len(hours) < 24 * 5:
            continue
        (cache / f"{m['coin'].replace(':', '_')}.json").write_text(json.dumps(hours), encoding="utf-8")
        p = profile(hours)
        rows.append(m | p | {"score": p["day_range_pct"] * p["clean"], "quiet": m["vol_rank"] > QUIET_RANK,
                             "link": f"https://app.hyperliquid.xyz/trade/{m['coin']}"})
    rows.sort(key=lambda r: -r["score"])

    out = HERE / "scans"
    out.mkdir(exist_ok=True)
    cols = ["coin", "dex", "score", "day_range_pct", "clean", "days_10pct", "hour_range_pct", "max_lev", "vol_24h",
            "vol_rank", "oi_usd", "chg_24h_pct", "funding_hr_pct", "quiet", "mark", "days", "link"]
    with open(out / f"{stamp}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    lines = [f"# Hyperliquid scan {stamp} UTC", "",
             f"{len(allm)} markets; {len(rows)} pass the barriers and have {a.days} days of hourly candles. "
             "Ranked by score = typical daily range x cleanness. 'quiet' = outside the top 30 by 24h volume.", "",
             "| # | market | score | daily range | clean | days 10%+ | hourly range | max lev | 24h vol | vol rank | quiet |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:a.top], 1):
        lines.append(f"| {i} | [{r['coin']}]({r['link']}) | {r['score']:.2f} | {r['day_range_pct']:.1f}% | "
                     f"{r['clean']:.2f} | {r['days_10pct'] * 100:.0f}% | {r['hour_range_pct']:.2f}% | {r['max_lev']}x | "
                     f"${r['vol_24h'] / 1e6:.1f}M | {r['vol_rank']} | {'yes' if r['quiet'] else ''} |")
    (out / f"{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[4:]))
    print(f"\nSaved: crypto/hyperliquid/scans/{stamp}.md and .csv; candles in crypto/hyperliquid/cache/{stamp}/")


if __name__ == "__main__":
    main()
