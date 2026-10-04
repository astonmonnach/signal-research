"""Performance ledger: every call the pipeline (or we) logged, then and now.

Run:  python ledger/build_ledger.py
Out:  ledger/ledger.csv, ledger/LEDGER.md

Rules (frozen in ledger/RULES.md, don't change after seeing results):
- found price  = close on the day the item was found (what you'd have seen)
- entry price  = OPEN of the next session (the first price you could act on)
- now price    = latest close
- control      = IWM over the same window (entry -> now)
- excess       = direction x (ticker return - IWM return); direction comes from the
                 category hypothesis in CATEGORY_DIRECTION, fixed before results.
"""
import csv, json, re, time, urllib.request, datetime as dt
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV, OUT_MD = ROOT / "ledger/ledger.csv", ROOT / "ledger/LEDGER.md"

# Pre-registered direction per category: +1 long bias, -1 short bias, 0 = track only.
CATEGORY_DIRECTION = {
    "merger_vote": 0, "tender_third_party": 0, "tender_issuer_buyback": 1,
    "activist_13d": 1, "share_registration": -1, "registration_effective": -1,
    "ipo_priced": 0, "delisting": 0,
    "8k_strategic_review": 1, "8k_spin_off": 0, "8k_reverse_split": -1,
    "8k_lock_up": 0, "8k_tender_offer": 0, "8k_special_dividend": 0,
    "s1_dod_contract": 1,
}
SECTION_CATEGORY = [
    ("merger votes", "merger_vote"), ("tender offers (third party)", "tender_third_party"),
    ("tender offers (issuer buyback)", "tender_issuer_buyback"), ("activists", "activist_13d"),
    ("share registrations", "share_registration"), ("registrations declared effective", "registration_effective"),
    ("ipo / offering priced", "ipo_priced"), ("delistings", "delisting"),
]
PHRASE_CATEGORY = [  # first match wins, strongest signal first
    ("strategic alternatives", "8k_strategic_review"), ("strategic review", "8k_strategic_review"),
    ("reverse stock split", "8k_reverse_split"), ("spin-off", "8k_spin_off"),
    ("special dividend", "8k_special_dividend"), ("tender offer", "8k_tender_offer"), ("lock-up", "8k_lock_up"),
]

MIN_ADV_USD = 250_000   # average daily $ volume over the 20 days before found; below this = untradeable
_cache = {}
def yahoo(t):
    if t in _cache: return _cache[t]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=6mo&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        bars = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), o, c, v or 0) for ts, o, c, v in zip(r["timestamp"], q["open"], q["close"], q["volume"]) if o and c]
    except Exception:
        bars = None
    _cache[t] = bars
    time.sleep(0.25)
    return bars

def prices(t, found):
    bars = yahoo(t)
    if not bars: return None
    f = [b for b in bars if b[0] <= found]
    nxt = [b for b in bars if b[0] > found]
    pre = pct(f[-1][2], f[-6][2]) if len(f) >= 6 else None
    adv = mean(b[2] * b[3] for b in f[-20:]) if f else None
    return {"pre_move_5d": pre, "adv_usd": adv,
            "found_close": f[-1][2] if f else None,
            "entry_date": nxt[0][0] if nxt else None, "entry_open": nxt[0][1] if nxt else None,
            "now_date": bars[-1][0], "now": bars[-1][2]}

def rows_market_scans():
    out = []
    for f in sorted((ROOT / "watch/market").glob("*.md")):
        day = dt.date.fromisoformat(f.stem); cat = None
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                h = line[3:].lower(); cat = next((c for k, c in SECTION_CATEGORY if h.startswith(k)), "8k" if h.startswith("8-ks") else None)
                continue
            m = re.match(r"- \*\*([A-Z0-9.\-]+)[^*]*\*\*\s*(.*)", line)
            if not m or not cat: continue
            tk, rest = m.group(1), m.group(2).lower()
            c = cat
            if cat == "8k":
                rest = re.sub(r"bio-mention \([^)]*\),?", "", rest)  # rule 2026-10-04: director-bio mentions aren't strategic reviews
                c = next((cc for p, cc in PHRASE_CATEGORY if p in rest), None)
                if not c: continue
            out.append({"found": day, "source": f"market scan {f.stem}", "ticker": tk, "category": c,
                        "direction": CATEGORY_DIRECTION[c], "note": rest[:80]})
    return out

def rows_s1():
    out = []
    for r in csv.DictReader(open(ROOT / "data/signals.csv", encoding="utf-8")):
        d = dt.date.fromisoformat(r["signal_id"].split("-")[1] + "-" + r["signal_id"].split("-")[2] + "-" + r["signal_id"].split("-")[3])
        out.append({"found": d, "source": "S1 DoD contracts", "ticker": r["ticker"], "category": "s1_dod_contract",
                    "direction": 1, "note": f"{r['decision']}; materiality {float(r['materiality'] or 0)*100:.0f}%"})
    return out

def rows_manual():
    p = ROOT / "ledger/manual_calls.csv"
    return [{"found": dt.date.fromisoformat(r["found"]), "source": r["source"], "ticker": r["ticker"],
             "category": r["category"], "direction": int(r["direction"]), "note": r["note"]}
            for r in csv.DictReader(open(p, encoding="utf-8"))] if p.exists() else []

def pct(a, b): return None if (a is None or b in (None, 0)) else (a / b - 1) * 100

def corporate_actions():
    p = ROOT / "ledger/corporate_actions.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []

def holder_value_now(ticker, entry_date, now_price):
    """Now price plus anything a holder received after entry (spin-off shares at today's price)."""
    extra, notes = 0.0, []
    for a in corporate_actions():
        ex = dt.date.fromisoformat(a["ex_date"])
        if a["ticker"] == ticker and entry_date <= ex and a["receive_ticker"] == "CASH":
            extra += float(a["ratio"]); notes.append(f"+${a['ratio']} cash ({a['kind']})")
        elif a["ticker"] == ticker and entry_date < ex:
            rb = yahoo(a["receive_ticker"])
            if rb:
                extra += float(a["ratio"]) * rb[-1][2]
                notes.append(f"+{a['ratio']} {a['receive_ticker']} (spin)")
    return now_price + extra, "; ".join(notes)

def main():
    items = rows_s1() + rows_manual() + rows_market_scans()
    seen, uniq = set(), []
    for it in items:  # one row per (ticker, category, found day)
        k = (it["ticker"], it["category"], it["found"])
        if k not in seen: seen.add(k); uniq.append(it)
    iwm = yahoo("IWM")
    out = []
    for it in uniq:
        p = prices(it["ticker"], it["found"])
        row = dict(it, found=it["found"].isoformat())
        if not p:
            row.update(status="no price data"); out.append(row); continue
        row.update(pre_move_5d=None if p["pre_move_5d"] is None else round(p["pre_move_5d"], 1),
                   adv_usd=None if p["adv_usd"] is None else round(p["adv_usd"]),
                   liquid="yes" if (p["adv_usd"] or 0) >= MIN_ADV_USD else "no",
                   found_close=p["found_close"], entry_date=p["entry_date"] and p["entry_date"].isoformat(),
                   entry_open=p["entry_open"], now_date=p["now_date"].isoformat(), now=p["now"])
        if not p["entry_open"]:
            row.update(status="pending (enters next session open)"); out.append(row); continue
        now_val, ca = holder_value_now(it["ticker"], p["entry_date"], p["now"])
        if ca: row["note"] = (row.get("note", "") + " | adj: " + ca).strip(" |")
        r = pct(now_val, p["entry_open"])
        io = next((b[1] for b in iwm if b[0] == p["entry_date"]), None); ic = iwm[-1][2]
        ir = pct(ic, io)
        row.update(ret_pct=round(r, 2), iwm_pct=round(ir, 2) if ir is not None else None,
                   since_found_pct=round(pct(now_val, p["found_close"]), 2) if p["found_close"] else None,
                   excess_pct=round(it["direction"] * (r - ir), 2) if (ir is not None and it["direction"]) else None,
                   days=(p["now_date"] - p["entry_date"]).days, status="live")
        out.append(row)

    cols = ["found", "source", "ticker", "category", "direction", "pre_move_5d", "adv_usd", "liquid", "found_close", "entry_date", "entry_open",
            "now_date", "now", "since_found_pct", "ret_pct", "iwm_pct", "excess_pct", "days", "status", "note"]
    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(out)

    live = [r for r in out if r.get("status") == "live"]
    lines = [f"# Ledger: {dt.date.today().isoformat()}", "",
             f"{len(out)} logged items · {len(live)} live · "
             f"{sum(1 for r in out if r.get('status','').startswith('pending'))} pending · "
             f"{sum(1 for r in out if r.get('status') == 'no price data')} no price data", "",
             "Entry = next session's open after the item was found. Control = IWM over the same window. "
             "Excess = direction × (return − IWM). **Days held are tiny: this is a log, not a result.**", "",
             "## By category (directional categories only)", "",
             "| category | dir | n live | mean excess | median excess | hit rate (excess > 0) |", "|---|---|---|---|---|---|"]
    cats = sorted({r["category"] for r in live})
    for c in cats:
        xs = [r["excess_pct"] for r in live if r["category"] == c and r.get("excess_pct") is not None]
        ds = [r["direction"] for r in live if r["category"] == c]; d = max(set(ds), key=ds.count) if ds else 0
        if xs:
            lines.append(f"| {c} | {d:+d} | {len(xs)} | {mean(xs):+.1f}% | {median(xs):+.1f}% | {sum(x > 0 for x in xs)}/{len(xs)} |")
        else:
            rs = [r["ret_pct"] for r in live if r["category"] == c]
            lines.append(f"| {c} | 0 (track) | {len(rs)} | raw {mean(rs):+.1f}% | raw {median(rs):+.1f}% | n/a |")
    tr = [r for r in live if r.get("liquid") == "yes" and r.get("excess_pct") is not None]
    lines += ["", f"## Tradeable only (avg daily volume ≥ ${MIN_ADV_USD:,.0f}), split by the move in the 5 days before found", "",
              "| category | dir | n | mean excess | right | of which fell >20% before found: n · mean excess |", "|---|---|---|---|---|---|"]
    for c in sorted({r["category"] for r in tr}):
        xs = [r for r in tr if r["category"] == c]; ex = [r["excess_pct"] for r in xs]
        cr = [r["excess_pct"] for r in xs if (r.get("pre_move_5d") or 0) <= -20]
        lines.append(f"| {c} | {xs[0]['direction']:+d} | {len(ex)} | {mean(ex):+.1f}% | {sum(x > 0 for x in ex)}/{len(ex)} | "
                     + (f"{len(cr)} · {mean(cr):+.1f}%" if cr else "0") + " |")
    lines += ["", "## Every live item", "",
              "| found | ticker | category | dir | 5d before | $vol/day | found @ | entry @ | now | since found | since entry | IWM | excess | days |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(live, key=lambda r: (r["found"], r["ticker"])):
        f = lambda v: "" if v is None else f"{v:+.1f}%"
        fc = "" if r.get("found_close") is None else f"{r['found_close']:.2f}"
        adv = "" if r.get("adv_usd") is None else (f"${r['adv_usd']/1e6:.1f}M" if r["adv_usd"] >= 1e6 else f"${r['adv_usd']/1e3:.0f}k")
        lines.append(f"| {r['found']} | {r['ticker']} | {r['category']} | {r['direction']:+d} | {f(r.get('pre_move_5d'))} | {adv}{'' if r.get('liquid') == 'yes' else ' ⚠'} | {fc} | {r['entry_open']:.2f} | "
                     f"{r['now']:.2f} | {f(r.get('since_found_pct'))} | {f(r['ret_pct'])} | {f(r.get('iwm_pct'))} | {f(r.get('excess_pct'))} | {r['days']} |")
    pend = [r for r in out if r.get("status", "").startswith("pending")]
    if pend:
        lines += ["", f"## Pending ({len(pend)}): enter at the next session open", "", ", ".join(sorted({r['ticker'] for r in pend}))]
    nod = [r for r in out if r.get("status") == "no price data"]
    if nod:
        lines += ["", f"## No price data ({len(nod)}): delisted, units/warrants or bad symbol", "", ", ".join(sorted({r['ticker'] for r in nod}))]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(out)} items, {len(live)} live -> {OUT_CSV.name}, {OUT_MD.name}")

if __name__ == "__main__":
    main()
