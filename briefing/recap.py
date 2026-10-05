"""After-the-close recap, sent to Discord. Plain text, no emojis.

  #daily-recap    the day in one post: market, inputs, calls, positions, best/worst, each size bucket, next session
  #micro-caps     one post per size bucket (watch/caps.json): a table of every stock in it plus a one-line
  #small-caps     verdict, thesis and next dated event. The benchmark depends on size: IWM for micro and
  #mid-caps       small caps, MDY for mid caps, SPY for large caps.
  #large-caps
  #positions      open positions and P&L after fees (watch/positions.md, from collectors/positions.py)
  #calls          the public calls, marked to today's close (calls/marks.csv)
  #setups         the watch-only setups since they were logged
  #weekly-recap   Fridays (or --weekly): the week for every stock, calls, positions, best/worst, next week

Usage: python briefing/recap.py [--dry-run] [--force] [--weekly]
Writes recaps/daily/YYYY-MM-DD.md (and recaps/weekly/YYYY-Www.md). Sends once per trading day
(recaps/.sent-DATE) and once per week (recaps/.sent-YYYY-Www). A run before the close writes the file but sends nothing.
"""
import csv, json, re, sys, time, urllib.request, datetime as dt
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "briefing")); sys.path.insert(0, str(ROOT / "reports"))
import notify  # noqa: E402
from sources import calendar_events  # noqa: E402

REPO = "https://github.com/astonmonnach/signal-research/blob/main"
BUCKETS = {  # key: (heading, range, channel, benchmark)
    "micro": ("MICRO CAPS", "under $300M", "microcaps", "IWM"),
    "small": ("SMALL CAPS", "$300M to $2B", "smallcaps", "IWM"),
    "mid": ("MID CAPS", "$2B to $10B", "midcaps", "MDY"),
    "large": ("LARGE CAPS", "over $10B", "largecaps", "SPY"),
}
MARKET = [("SPY", "S&P 500"), ("IWM", "Russell 2000"), ("QQQ", "Nasdaq 100"), ("MDY", "S&P MidCap 400")]
INPUTS = [("SLX", "Steel"), ("CPER", "Copper"), ("GLD", "Gold"), ("SLV", "Silver"), ("USO", "Oil")]
_cache, _meta = {}, {}


# ---------- data ----------
def bars(t):
    """[(date, close)] for ~3 months of Yahoo daily bars (today's bar is live until the close)."""
    if t in _cache: return _cache[t]
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=3mo&interval=1d"
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
        out = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), c) for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
        _meta[t] = r["meta"]
    except Exception:
        out = []
    _cache[t] = out; time.sleep(0.15)
    return out


def corporate_actions():
    p = ROOT / "ledger/corporate_actions.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


CAS = corporate_actions()


def holder_pct(t, base_date):
    """% from the close on/before base_date to the latest close, adding back cash and spun-off shares received."""
    b = bars(t)
    base = [x for x in b if x[0] <= base_date]
    if not b or not base: return None
    d0, d1, val = base[-1][0], b[-1][0], b[-1][1]
    for ca in CAS:
        ex = dt.date.fromisoformat(ca["ex_date"])
        if ca["ticker"] == t and d0 < ex <= d1:
            val += float(ca["ratio"]) if ca["receive_ticker"] == "CASH" else float(ca["ratio"]) * (bars(ca["receive_ticker"]) or [(0, 0)])[-1][1]
    return (val / base[-1][1] - 1) * 100


def back(t, n):
    """Date of the close n sessions before the latest one."""
    b = bars(t)
    return b[-1 - n][0] if len(b) > n else None


def day(t):
    return holder_pct(t, back(t, 1)) if back(t, 1) else None


def five(t):
    return holder_pct(t, back(t, 5)) if back(t, 5) else None


def minus(a, b):
    return None if a is None or b is None else a - b


def p(v):
    return "n/a" if v is None else f"{v:+.1f}%"


def pt(v):
    return "n/a" if v is None else f"{v:+.1f}"


def money(v):
    return "n/a" if not v else (f"${v / 1e9:.2f}B" if v >= 1e9 else f"${v / 1e6:.0f}M")


def clip(s, n):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s).replace("**", "").replace("*", "").strip()
    return s if len(s) <= n else s[: s.rfind(" ", 0, n)].rstrip(",;:") + "..."


def dossiers():
    """Verdict, score and one-line thesis per ticker from the hand-written index in stocks/README.md."""
    out = {}
    txt = (ROOT / "stocks/README.md").read_text(encoding="utf-8") if (ROOT / "stocks/README.md").exists() else ""
    txt = txt.split("<!-- AUTO")[0]                                # the hand-written part only
    for m in re.finditer(r"^\| \[(\w+)\]\(\w+\.md\) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|\s*$", txt, re.M):
        t, thesis, _, _, verdict, score = m.groups()
        if t in out: continue
        v = re.search(r"\*\*(.+?)\*\*", verdict)
        s = re.search(r"(\d+)/10", score)
        out[t] = {"thesis": thesis, "verdict": (v.group(1) if v else verdict.split("(")[0]).strip().rstrip(";"),
                  "score": f"{s.group(1)}/10" if s else ""}
    return out


def found():
    """First time each ticker was logged in the ledger: (date, category)."""
    out = {}
    for r in ledger_rows():
        d = dt.date.fromisoformat(r["found"])
        if r["ticker"] not in out or d < out[r["ticker"]][0]:
            out[r["ticker"]] = (d, r["category"])
    return out


def ledger_rows():
    p_ = ROOT / "ledger/ledger.csv"
    return list(csv.DictReader(open(p_, encoding="utf-8"))) if p_.exists() else []


def setup_found():
    """Watch-only setups: ticker -> the date it was logged as a setup (its earlier scan rows don't count)."""
    out = {}
    for r in ledger_rows():
        if r["category"].startswith("setup_"):
            d = dt.date.fromisoformat(r["found"])
            out[r["ticker"]] = min(d, out.get(r["ticker"], d))
    return out


def next_event(t, after, events):
    rx = re.compile(rf"\b{re.escape(t)}\b")
    ev = next((e for e in events if e["date"] >= after and rx.search(e["summary"])), None)
    return f"{ev['date']:%a %d %b}: {ev['summary']}" if ev else ""


def table(header, rows):
    w = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    line = lambda r: "  ".join(str(x).ljust(w[i]) if i == 0 else str(x).rjust(w[i]) for i, x in enumerate(r)).rstrip()
    return ["```", line(header)] + [line(r) for r in rows] + ["```"]


# ---------- sections ----------
def stock_rows(tickers, bench, fnd, base_week=None):
    rows = []
    for t in tickers:
        d, f5, bd = day(t), five(t), day(bench)
        since = holder_pct(t, fnd[t][0]) if t in fnd else None
        wk = holder_pct(t, base_week) if base_week else None
        rows.append(dict(t=t, close=(bars(t) or [(0, None)])[-1][1], day=d, vs=minus(d, bd), five=f5, since=since,
                         since_vs=minus(since, holder_pct(bench, fnd[t][0])) if t in fnd else None,
                         week=wk, week_vs=minus(wk, holder_pct(bench, base_week)) if base_week else None))
    return rows


def bucket_post(key, tickers, caps, info, fnd, events, label, session):
    head, rng, _, bench = BUCKETS[key]
    L = [f"**{head}** ({rng}) · {label}", f"Benchmark: {bench}. Day and 5-day moves include cash and spun-off shares received."]
    if not tickers:
        return "\n".join(L + ["No watchlist stocks in this size range right now."])
    rows = stock_rows(tickers, bench, fnd)
    rows.sort(key=lambda r: -(r["day"] if r["day"] is not None else -999))
    L += table(["Ticker", "Close", "Day", f"vs {bench}", "5d", "Since found"],
               [[r["t"], "n/a" if r["close"] is None else f"{r['close']:.2f}", p(r["day"]), pt(r["vs"]), p(r["five"]), p(r["since"])] for r in rows])
    for r in rows:
        i, c = info.get(r["t"], {}), caps.get(r["t"], {})
        verdict = i.get("verdict", "") + (f" ({i['score']})" if i.get("score") else "")
        cap = money(c.get("mcap")) + (" est." if "ESTIMATE" in c.get("shares_source", "") else "")
        nxt = next_event(r["t"], session + dt.timedelta(days=1), events)
        head_ = f"- **{r['t']}** · {verdict + ' · ' if verdict else ''}{cap}"
        L.append(head_ + (f"\n  {clip(i['thesis'], 170)}" if i.get("thesis") else "") + (f"\n  Next: {nxt}" if nxt else ""))
    L.append(f"Dossiers: <{REPO}/stocks/README.md>")
    return "\n".join(L)


def positions_post(label):
    p_ = ROOT / "watch/positions.md"
    if not p_.exists(): return ""
    body = p_.read_text(encoding="utf-8").splitlines()[1:]
    return "\n".join([f"**OPEN POSITIONS** · {label}"] + [l.replace("## ", "### ") for l in body if l.strip() or True]).strip()


def positions_line():
    p_ = ROOT / "watch/positions.md"
    if not p_.exists(): return "none"
    txt = p_.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^## (\w+).*?\n- Price \*\*\$([\d.]+)\*\* vs entry \$([\d.]+): \*\*([+-][\d.]+%)\*\*\n- P&L if sold now, after all fees: \*\*\$([+-][\d.]+)\*\*", txt, re.M):
        out.append(f"{m.group(1)} {m.group(4)} since entry (${m.group(5)} after fees)")
    return ", ".join(out) or ("none" if "No open positions" in txt else "see #positions")


def calls_lines():
    p_ = ROOT / "calls/marks.csv"
    out = []
    for r in (csv.DictReader(open(p_, encoding="utf-8")) if p_.exists() else []):
        side = ("LONG" if int(r["direction"]) > 0 else "SHORT") + (" (long-term)" if r.get("horizon") == "long" else "")
        if not r["ret_pct"]:
            out.append(f"#{r['id']} {side} {r['ticker']}: {r['status']}"); continue
        out.append(f"#{r['id']} {side} {r['ticker']} {float(r['ret_pct']):+.1f}% from ${float(r['entry']):.2f} ({r['entry_date']}), "
                   f"{pt(float(r['excess_bench']) if r['excess_bench'] else None)} vs {r['bench']}, {r['status']}")
    return out


def calls_post(label):
    lines = calls_lines()
    if not lines: return ""
    return "\n".join([f"**PUBLIC CALLS** · {label}", "Marked from the first open after each call was posted. Losers stay on the record."]
                     + [f"- {x}" for x in lines] + [f"Record: <{REPO}/calls/README.md>"])


def setups_post(label, fnd, info):
    sf = setup_found()
    if not sf: return ""
    rows = []
    for t in sorted(sf):
        b = bars(t)
        since = holder_pct(t, sf[t])
        flag = "SPIKE" if since is not None and since >= 50 else ("big move" if since is not None and abs(since) >= 20 else "")
        rows.append([t, f"{b[-1][1]:.3f}" if b else "n/a", p(day(t)) if b else "n/a", p(since), flag])
    L = [f"**SETUPS (WATCH ONLY, NOT BUYS)** · {label}",
         "Fresh share supply plus an exchange deficiency. Most of these collapse; the test is whether any spike first."]
    L += table(["Ticker", "Close", "Day", "Since logged", "Flag"], rows)
    flagged = [r[0] for r in rows if r[4]]
    L.append("Flagged: " + (", ".join(flagged) if flagged else "none"))
    L += [f"- **{t}** {clip(info[t]['thesis'], 120)}" for t in sorted(sf) if t in info]
    L.append(f"Notes: <{REPO}/stocks/README.md>")
    return "\n".join(L)


def daily_post(label, session, groups, caps, fnd, events):
    L = [f"**DAILY RECAP** · {label}", ""]
    L.append("**Market:** " + " · ".join(f"{name} {p(day(t))}" for t, name in MARKET))
    L.append("**Inputs:** " + " · ".join(f"{name} ({t}) {p(day(t))}" for t, name in INPUTS))
    cl = calls_lines()
    L.append("**Calls:** " + ("; ".join(cl) if cl else "none open"))
    L.append("**Positions:** " + positions_line())
    allrows = []
    for key, tickers in groups.items():
        for r in stock_rows(tickers, BUCKETS[key][3], fnd):
            allrows.append(dict(r, bucket=key))
    moved = [r for r in allrows if r["vs"] is not None]
    moved.sort(key=lambda r: -r["vs"])
    f = lambda r: f"{r['t']} {p(r['day'])} ({pt(r['vs'])} vs {BUCKETS[r['bucket']][3]})"
    if moved:
        L.append("**Best vs market:** " + ", ".join(f(r) for r in moved[:3]))
        L.append("**Worst vs market:** " + ", ".join(f(r) for r in moved[::-1][:3]))
    L += ["", "**By size** (average day move, and against the bucket's benchmark):"]
    for key, (head, rng, ch, bench) in BUCKETS.items():
        rs = [r for r in allrows if r["bucket"] == key and r["day"] is not None]
        if rs:
            L.append(f"- {head.title()} ({len(rs)}): {p(mean(r['day'] for r in rs))}, {pt(mean(r['vs'] for r in rs if r['vs'] is not None))} vs {bench}"
                     f" · {', '.join(r['t'] for r in rs)}")
    nxt_day = session + dt.timedelta(days=3 if session.weekday() == 4 else 1)
    evs = [e for e in events if session < e["date"] <= nxt_day]
    L += ["", f"**Next session ({nxt_day:%a %d %b}):** " + ("; ".join(e["summary"] for e in evs) if evs else "nothing dated")]
    L.append(f"Full recap: <{REPO}/recaps/daily/{session.isoformat()}.md>")
    return "\n".join(L)


def weekly_post(session, groups, fnd, events):
    monday = session - dt.timedelta(days=session.weekday())
    base = monday - dt.timedelta(days=1)       # holder_pct takes the close on/before this: last week's final close
    iy, iw, _ = session.isocalendar()
    L = [f"**WEEKLY RECAP** · week {iw} ({monday:%d %b} to {session:%d %b %Y})", ""]
    L.append("**Market (week):** " + " · ".join(f"{name} {p(holder_pct(t, base))}" for t, name in MARKET))
    L.append("**Inputs (week):** " + " · ".join(f"{name} {p(holder_pct(t, base))}" for t, name in INPUTS))
    cl = calls_lines()
    L.append("**Calls:** " + ("; ".join(cl) if cl else "none open"))
    L.append("**Positions:** " + positions_line())
    rows = []
    for key, tickers in groups.items():
        for r in stock_rows(tickers, BUCKETS[key][3], fnd, base_week=base):
            rows.append(dict(r, bucket=key))
    rows.sort(key=lambda r: -(r["week_vs"] if r["week_vs"] is not None else -999))
    L += [""] + table(["Ticker", "Size", "Week", "vs bench", "Since found"],
                      [[r["t"], r["bucket"], p(r["week"]), pt(r["week_vs"]), p(r["since"])] for r in rows])
    nxt0, nxt1 = monday + dt.timedelta(days=7), monday + dt.timedelta(days=11)
    evs = [e for e in events if nxt0 <= e["date"] <= nxt1]
    L += ["**Next week:**"] + ([f"- {e['date']:%a %d %b}: {e['summary']}" for e in evs] or ["- nothing dated"])
    L.append(f"Weekly report: <{REPO}/reports/weekly/{iy}-W{iw:02d}.md>")
    return "\n".join(L), f"{iy}-W{iw:02d}"


# ---------- main ----------
def main():
    spy = bars("SPY")
    if not spy: sys.exit("no SPY data")
    session = spy[-1][0]
    end = _meta.get("SPY", {}).get("currentTradingPeriod", {}).get("regular", {}).get("end")
    now = dt.datetime.now(dt.UTC)
    intraday = bool(end) and session == now.date() and now.timestamp() < end
    label = f"{session:%a %d %b} close" if not intraday else f"{session:%a %d %b}, intraday {now:%H:%M} UTC"

    caps = json.load(open(ROOT / "watch/caps.json", encoding="utf-8"))["stocks"] if (ROOT / "watch/caps.json").exists() else {}
    tickers = json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"]
    groups = {k: [t for t in tickers if caps.get(t, {}).get("bucket") == k] for k in BUCKETS}
    unsized = [t for t in tickers if not caps.get(t, {}).get("bucket")]
    groups["small"] += unsized                                    # no share count yet: shown with small caps
    info, fnd, events = dossiers(), found(), calendar_events()

    posts = {"dailyrecap": daily_post(label, session, groups, caps, fnd, events)}
    for k, (_, _, ch, _) in BUCKETS.items():
        posts[ch] = bucket_post(k, groups[k], caps, info, fnd, events, label, session)
    for ch, text in [("positions", positions_post(label)), ("calls", calls_post(label)), ("setups", setups_post(label, fnd, info))]:
        if text: posts[ch] = text
    weekly, wk = None, None
    if session.weekday() == 4 or "--weekly" in sys.argv:
        weekly, wk = weekly_post(session, groups, fnd, events)

    out = ROOT / f"recaps/daily/{session.isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n\n".join(posts.values()) + "\n", encoding="utf-8")
    if weekly:
        wo = ROOT / f"recaps/weekly/{wk}.md"; wo.parent.mkdir(parents=True, exist_ok=True)
        wo.write_text(weekly + "\n", encoding="utf-8")
    if "--dry-run" in sys.argv:
        print("\n\n=====\n\n".join(list(posts.values()) + ([weekly] if weekly else []))); return
    if intraday and "--force" not in sys.argv:
        print(f"market still open ({label}): recap written to {out.relative_to(ROOT)}, nothing sent"); return
    sent = []
    marker = ROOT / f"recaps/.sent-{session.isoformat()}"
    if not marker.exists() or "--force" in sys.argv:
        for ch, text in posts.items():
            if notify.has_own_channel(ch): sent += notify.send(text, ch)
        if sent: marker.write_text(", ".join(sent) + "\n", encoding="utf-8")
    if weekly:
        wm = ROOT / f"recaps/.sent-{wk}"
        if (not wm.exists() or "--force" in sys.argv) and notify.has_own_channel("weeklyrecap"):
            s = notify.send(weekly, "weeklyrecap"); sent += s
            if s: wm.write_text(", ".join(s) + "\n", encoding="utf-8")
    print(f"recap {session} written to {out.relative_to(ROOT)}; sent via: {', '.join(sent) or 'nothing (already sent, or no webhooks)'}")


if __name__ == "__main__":
    main()
