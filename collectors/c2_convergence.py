"""C2 CONVERGENCE: forward-test Thomas's smart-wallet convergence signal.

Usage:  python collectors/c2_convergence.py        (hourly; needs gmgn-cli + GMGN_API_KEY env)
Signal (from Desktop/Solana Wallet Finder, never forward-tested): a token that >= 3 distinct
wallets from the frozen 30-wallet panel (data/crypto/c2_panel.json) bought within the lookback.
His own out-of-sample test showed copying single wallets is noise (top-8: -48%, losers: +141%),
so convergence is the one idea left standing. This logs each new hot token at first detection,
then scores it at 1h / 6h / 24h / 7d net of fees, slippage and rug pulls (same method as C1).
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crypto_trending import GT, HORIZONS, append, est_cost_pct, f, get, read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "crypto"
PANEL = json.load(open(DIR / "c2_panel.json", encoding="utf-8"))
SIGNALS, OUTCOMES = DIR / "c2_signals.csv", DIR / "c2_outcomes.csv"
SIG_COLS = ["signal_id", "detected_at_utc", "version", "token", "symbol", "buyers", "wallets", "panel_usd",
            "first_buy_utc", "last_buy_utc", "pool", "price_usd", "liquidity_usd", "mcap_usd", "pool_age_h",
            "chg_1h", "chg_24h", "est_cost_pct"]
OUT_COLS = ["signal_id", "horizon", "checked_at_utc", "elapsed_h", "late", "price_usd", "liquidity_usd",
            "ret_pct", "ret_net_pct", "rugged"]
CLI = shutil.which("gmgn-cli") or "gmgn-cli"
_last = [0.0]


def gmgn(args):
    for attempt in range(4):
        gap = 0.45 - (time.time() - _last[0])
        if gap > 0:
            time.sleep(gap)
        _last[0] = time.time()
        try:
            r = subprocess.run([CLI, *args], capture_output=True, text=True, timeout=60,
                               encoding="utf-8", errors="replace")
            out = (r.stdout or "") + "\n" + (r.stderr or "")
        except Exception:
            out = ""
        i = out.find("{")
        if i >= 0:
            try:
                return json.JSONDecoder().raw_decode(out[i:])[0]
            except Exception:
                pass
        if "BANNED" in out:
            sys.exit("GMGN hard rate-limit ban: stopping so it isn't extended.")
        m = re.search(r"~(\d+)s remaining", out)
        time.sleep(min((int(m.group(1)) if m else 5 * (attempt + 1)) + 2, 60))
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.environ.get("GMGN_API_KEY"):
        print("GMGN_API_KEY not set: gmgn-cli may use its own stored key or fail.")
    DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = time.time() - PANEL["lookback_hours"] * 3600

    conv = {}
    for w in PANEL["panel"]:
        cursor = None
        for _ in range(2):                    # 2 pages = 40 most recent buys; enough for a 24h window
            args = ["portfolio", "activity", "--chain", "sol", "--wallet", w, "--limit", "20", "--type", "buy", "--raw"]
            if cursor:
                args += ["--cursor", cursor]
            d = gmgn(args)
            acts = (d or {}).get("activities") or []
            if not acts:
                break
            stop = False
            for a in acts:
                ts = a.get("timestamp") or 0
                if ts < cutoff:
                    stop = True
                    continue
                tok = a.get("token") or {}
                addr = tok.get("address")
                if not addr:
                    continue
                c = conv.setdefault(addr, {"sym": tok.get("symbol") or "?", "buyers": set(), "usd": 0.0,
                                           "first": ts, "last": ts})
                c["buyers"].add(w)
                c["usd"] += float(a.get("cost_usd") or 0)
                c["first"], c["last"] = min(c["first"], ts), max(c["last"], ts)
            cursor = d.get("next")
            if stop or not cursor:
                break

    signals = read(SIGNALS)
    seen = {s["token"] for s in signals}
    hot = [(a, c) for a, c in conv.items() if len(c["buyers"]) >= PANEL["min_buyers"] and a not in seen]
    new_rows = []
    for addr, c in hot:
        info = get(f"{GT}/networks/solana/tokens/{addr}/pools?page=1")
        time.sleep(2.5)
        pools = (info or {}).get("data") or []
        a = pools[0]["attributes"] if pools else {}
        liq = f(a.get("reserve_in_usd"))
        created = a.get("pool_created_at")
        age = (now - datetime.fromisoformat(created.replace("Z", "+00:00"))).total_seconds() / 3600 if created else None
        pc = a.get("price_change_percentage") or {}
        iso = lambda ts: datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new_rows.append({"signal_id": f"C2-{now:%Y%m%d%H%M}-{addr[:8]}", "detected_at_utc": stamp,
                         "version": PANEL["version"], "token": addr, "symbol": c["sym"], "buyers": len(c["buyers"]),
                         "wallets": " ".join(sorted(c["buyers"])), "panel_usd": round(c["usd"]),
                         "first_buy_utc": iso(c["first"]), "last_buy_utc": iso(c["last"]),
                         "pool": a.get("address"), "price_usd": a.get("base_token_price_usd"), "liquidity_usd": liq,
                         "mcap_usd": a.get("market_cap_usd") or a.get("fdv_usd"),
                         "pool_age_h": None if age is None else round(age, 2),
                         "chg_1h": pc.get("h1"), "chg_24h": pc.get("h24"), "est_cost_pct": est_cost_pct(liq)})
    append(SIGNALS, SIG_COLS, new_rows)
    signals += new_rows

    # ---- outcomes (same rules as C1: late checks kept and flagged, rugs = -100%) ----
    done = {(o["signal_id"], o["horizon"]) for o in read(OUTCOMES)}
    due = []
    for s in signals:
        if not s.get("pool"):
            continue
        t0 = datetime.fromisoformat(s["detected_at_utc"].replace("Z", "+00:00"))
        for h, dt in HORIZONS.items():
            if (s["signal_id"], h) not in done and t0 + dt <= now:
                due.append((s, h, (now - t0).total_seconds() / 3600, now > t0 + dt * 1.5 + timedelta(minutes=30)))
    pools = list({s["pool"] for s, *_ in due})
    info, checked = {}, set()
    for i in range(0, len(pools), 30):
        d = get(f"{GT}/networks/solana/pools/multi/{','.join(pools[i:i + 30])}")
        time.sleep(2.5)
        if d is None:             # request failed: retry next run instead of scoring as missing
            continue
        checked.update(pools[i:i + 30])
        for p in d.get("data", []):
            info[p["attributes"]["address"]] = p["attributes"]
    out_rows = []
    for s, h, elapsed, late in due:
        if s["pool"] not in checked:
            continue
        a = info.get(s["pool"])
        p0, l0 = f(s["price_usd"]), f(s["liquidity_usd"])
        base = {"signal_id": s["signal_id"], "horizon": h, "checked_at_utc": stamp,
                "elapsed_h": round(elapsed, 2), "late": late}
        if a is None:
            out_rows.append({**base, "ret_pct": -100, "ret_net_pct": -100, "rugged": "missing"})
            continue
        p1, l1 = f(a.get("base_token_price_usd")), f(a.get("reserve_in_usd"))
        ret = (p1 / p0 - 1) * 100 if p0 and p1 else None
        rug = bool(l0 and l1 is not None and l1 < 0.1 * l0)
        net = -100 if rug else (None if ret is None else round(max(ret - (f(s["est_cost_pct"]) or 0), -100), 2))
        out_rows.append({**base, "price_usd": p1, "liquidity_usd": l1,
                         "ret_pct": None if ret is None else round(ret, 2), "ret_net_pct": net, "rugged": rug})
    append(OUTCOMES, OUT_COLS, out_rows)
    print(f"{stamp}: {len(conv)} tokens bought by the panel in {PANEL['lookback_hours']}h, "
          f"{len(new_rows)} new convergence signals, {len(out_rows)} outcomes recorded")


if __name__ == "__main__":
    main()
