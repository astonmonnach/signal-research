"""Weekly, monthly and quarterly reports on everything the pipeline found and tracks.

Usage:
  python reports/build_periodic.py --period week --date 2026-10-02    # the ISO week holding that date (2026-W40)
  python reports/build_periodic.py --period month --date 2026-09-15   # 2026-09
  python reports/build_periodic.py --period quarter --date 2026-09-15 # 2026-Q3
  python reports/build_periodic.py --current      # this week, month and quarter to date, plus any period that
                                                  # ended in the last 3 days (so it's final after a weekend)
  python reports/build_periodic.py --all          # every period from the first scan date to today
  add --post-weekly to send last week's summary to Discord #reports on Mondays (briefing/notify.py), once:
  the marker reports/.sent-weekly-YYYY-Www stops the later workflow slots resending it (--force resends);
  add --dry-run to print that summary instead of sending it.

Writes reports/weekly/YYYY-Www.md, reports/monthly/YYYY-MM.md, reports/quarterly/YYYY-Qn.md and the
index reports/README.md. Each report covers its period:
  - what the scans found (counts by category, one row per scan day);
  - the biggest movers since found, best and worst against IWM (ledger/ledger.csv);
  - ledger stats by category for items found in the period, tradeable only (as LEDGER.md);
  - positions and their P&L after fees (journal/trades.csv);
  - each watchlist stock's move over the period vs IWM, with a one-line reason from its dossier timeline;
  - setups that spiked (>= +50% from the found price) or collapsed (<= -30%) during the period;
  - dated events coming up (calendar/catalyst-dates.ics), through the end of the next period;
  - links to the scans and dossiers.
Prices for moves over the period: Yahoo daily closes (the free source ledger/build_ledger.py uses),
fetched once per run. Today's bar is ignored until after the US close, so re-runs give the same report.
Everything else comes from local files (reports/sources.py). Standard library only.
"""
import argparse, csv, json, sys, time, urllib.request, datetime as dt
from collections import Counter
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "briefing"))
from sources import (Sources, BL, ROOT, REPO_URL, TODAY, label, pct, pts, money, price, day, long_day,  # noqa: E402
                     link, plain, clip, write, word_rx, sgn)

NOW = dt.datetime.now(dt.UTC)
SPIKE, COLLAPSE = 50.0, -30.0        # setup flags, % from the found price
SELL_COMMISSION = 0.58               # as collectors/positions.py
FOLDER = {"week": "weekly", "month": "monthly", "quarter": "quarterly"}
TITLE = {"week": "Weekly", "month": "Monthly", "quarter": "Quarterly"}
TOP = 5
# Which timeline mention best explains a move: triage and press first, a bare "logged" or filing list last.
REASON_RANK = {"triage": 0, "press": 1, "s1": 2, "research": 3, "trade": 4, "market": 5, "dismissed": 6,
               "setup": 7, "filings": 8, "calendar": 9, "post": 10}


# ---------- periods ----------
class Period:
    def __init__(self, kind, d):
        self.kind = kind
        if kind == "week":
            self.start = d - dt.timedelta(days=d.weekday())
            self.end = self.start + dt.timedelta(days=6)
            iy, iw, _ = d.isocalendar()
            self.key = f"{iy}-W{iw:02d}"
        elif kind == "month":
            self.start = d.replace(day=1)
            self.end = (self.start + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
            self.key = f"{d:%Y-%m}"
        else:
            q = (d.month - 1) // 3 + 1
            self.start = dt.date(d.year, 3 * q - 2, 1)
            self.end = (dt.date(d.year + (q == 4), 1 if q == 4 else 3 * q + 1, 1)) - dt.timedelta(days=1)
            self.key = f"{d.year}-Q{q}"
        self.path = f"reports/{FOLDER[kind]}/{self.key}.md"
        self.to_date = self.end >= TODAY
        self.as_of = min(self.end, TODAY)

    def prev(self): return Period(self.kind, self.start - dt.timedelta(days=1))
    def next(self): return Period(self.kind, self.end + dt.timedelta(days=1))

    def span(self):
        same_year = self.start.year == self.end.year
        a = f"{self.start:%a} {self.start.day} {self.start:%b}" + ("" if same_year else f" {self.start.year}")
        return f"{a} – {long_day(self.end)}"


# ---------- prices ----------
_bars = {}


def bars(t):
    """[(date, close)], one year of Yahoo daily closes; today's bar only once the US session is over."""
    if t in _bars:
        return _bars[t]
    last_ok = TODAY if (NOW.hour, NOW.minute) >= (21, 30) else TODAY - dt.timedelta(days=1)
    out = []
    for host in ("query1", "query2"):
        try:
            url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d"
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
            r = r["chart"]["result"][0]
            closes = r["indicators"]["quote"][0]["close"]
            out = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), c) for ts, c in zip(r["timestamp"], closes) if c]
            out = [(d, c) for d, c in out if d <= last_ok and d.weekday() < 5]
            break
        except Exception:
            out = []
    time.sleep(0.25)
    _bars[t] = out
    return out


def close_on(t, d):
    """Last close on or before d -> (date, close) or None."""
    return next(((bd, c) for bd, c in reversed(bars(t)) if bd <= d), None)


def corporate_actions():
    p = ROOT / "ledger/corporate_actions.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def holder_move(t, d0, d1):
    """% move d0 -> d1 for a holder: adds cash and spun-off shares received in between. -> (pct, note) or (None, '')."""
    a, b = close_on(t, d0), close_on(t, d1)
    if not a or not b or a[0] >= b[0]:
        return None, ""
    val, notes = b[1], []
    for ca in corporate_actions():
        ex = dt.date.fromisoformat(ca["ex_date"])
        if ca["ticker"] == t and a[0] < ex <= b[0]:
            if ca["receive_ticker"] == "CASH":
                val += float(ca["ratio"]); notes.append(f"+${ca['ratio']} cash ({ca['kind'].replace('_', ' ')})")
            else:
                rc = close_on(ca["receive_ticker"], b[0])
                if rc:
                    val += float(ca["ratio"]) * rc[1]; notes.append(f"+{ca['ratio']} {ca['receive_ticker']} ({ca['kind'].replace('_', ' ')})")
    return (val / a[1] - 1) * 100, "; ".join(notes)


# ---------- sections ----------
def found_section(S, P, frm):
    dates = [d for d in S.scan_dates() if P.start <= d <= P.end]
    C = [S.counts(d) for d in dates]
    L = ["## What the scans found", ""]
    if not dates:
        return L + ["_No scan in this period._", ""], {}
    tot = lambda k: sum(c[k] for c in C)
    mk = sum((c["market_by_cat"] for c in C), Counter())
    su = sum((c["setups_by_cat"] for c in C), Counter())
    sig = [s for s in S.signals if P.start <= s["date"] <= P.end]
    sig_names = ", ".join(tick(S, s["ticker"], frm) for s in sig)
    L += ["| source | category | count |", "|---|---|---|",
          f"| S1 DoD contracts | days with an announcement / awards / **signals** | {sum(c['dod'] for c in C)} / {tot('awards')} / **{len(sig)}**"
          + (f" ({sig_names})" if sig else "") + " |",
          f"| Watchlist filings | new SEC filings (older ones picked up late) | {tot('filings')}" + (f" (+{tot('filings_old')})" if tot("filings_old") else "") + " |"]
    order = list(BL.CATEGORY_DIRECTION) + ["spin_off_form10", "going_private", "8k_other"]
    for cat in sorted(mk, key=lambda c: order.index(c) if c in order else 99):
        L.append(f"| Market-wide scan | {label(cat)} (`{cat}`) | {mk[cat]} |")
    L += [f"| Press releases | watchlist / position hits | {tot('press_watch')} |",
          f"| Press releases | keyword hits (NYSE / Nasdaq / NYSE American) | {tot('press_kw')} |"]
    for cat in sorted(su):
        L.append(f"| New setups and ideas | {label(cat)} (`{cat}`) | {su[cat]} |")
    L += [f"| Evening triage | notes / worth reading / dismissed | {sum(c['triage'] for c in C)} / {tot('worth')} / {tot('dismissed')} |", "",
          f"**Scan days ({len(dates)})**", "",
          "| date | S1 signals (DoD awards) | watchlist filings | market-wide | press | new setups | triage (worth / dismissed) |",
          "|---|---|---|---|---|---|---|"]
    for d, c in zip(dates, C):
        cells = [f"{c['signals']} ({c['awards']})" if c["dod"] or c["signals"] else "–",
                 (f"{c['filings']}" + (f" (+{c['filings_old']})" if c["filings_old"] else "")) if c["digest"] else "–",
                 str(c["market"]) if c["market_scan"] else "–",
                 str(c["press_watch"] + c["press_kw"]) if c["press_watch"] + c["press_kw"] else "–",
                 str(c["setups"]) if c["setups"] else "–", f"{c['worth']} / {c['dismissed']}" if c["triage"] else "–"]
        L.append(f"| {link(day(d), f'scans/{d}.md', frm)} | " + " | ".join(cells) + " |")
    summary = {"days": len(dates), "signals": len(sig), "filings": tot("filings"), "market": sum(mk.values()),
               "press": tot("press_watch") + tot("press_kw"), "setups": sum(su.values()), "worth": tot("worth")}
    return L + [""], summary


def tick(S, t, frm):
    return link(t, f"stocks/{t}.md", frm) if t in S.dossiers else t


def movers_section(S, P, frm):
    rows = [r for r in S.ledger if P.start <= r["found"] <= P.end]
    live = [r for r in rows if r["status"] == "live" and r["ret_pct"] is not None and r["iwm_pct"] is not None]
    asof = max((r["now_date"] for r in live), default=None)
    L = ["## Biggest movers since found", ""]
    if not rows:
        return L + ["_Nothing found in this period is in the ledger._", ""], [], []
    L.append(f"{len(rows)} ledger items were found in this period: {len(live)} live, "
             f"{sum(r['status'].startswith('pending') for r in rows)} waiting for their first open, "
             f"{sum(r['status'] == 'no price data' for r in rows)} with no price data. "
             + (f"Prices as of the ledger's last close ({asof}). " if asof else "")
             + "vs IWM = return from the next open minus IWM over the same days; excess applies the category's direction "
               "(blank = track-only category).")
    if not live:
        return L + ["", "_No item found in this period has traded since its entry open yet._", ""], [], []
    first = {}   # one row per ticker (its first find); other categories it was found under are listed with it
    for r in sorted(live, key=lambda r: (r["found"], r["category"])):
        if r["ticker"] in first:
            if r["category"] not in first[r["ticker"]]["_cats"]:
                first[r["ticker"]]["_cats"].append(r["category"])
        else:
            first[r["ticker"]] = dict(r, _vs=r["ret_pct"] - r["iwm_pct"], _cats=[r["category"]])
    live = sorted(first.values(), key=lambda r: (-r["_vs"], r["ticker"]))
    best = [r for r in live if r["_vs"] > 0][:TOP]
    worst = [r for r in reversed(live) if r["_vs"] < 0][:TOP]
    scans = set(S.scan_dates())
    head = ["| ticker | found | category | dir | found @ | now | since found | since entry | IWM | **vs IWM** | excess | $vol/day |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for title, group in ((f"Best {len(best)} (up the most against IWM)", best), (f"Worst {len(worst)} (down the most against IWM)", worst)):
        if not group:
            continue
        L += ["", f"**{title}**", ""] + head
        for r in group:
            adv = "" if r["adv_usd"] is None else money(r["adv_usd"]) + ("" if r["liquid"] == "yes" else " ⚠")
            found = link(f"{r['found']:%d %b}", f"scans/{r['found']}.md", frm) if r["found"] in scans else f"{r['found']:%d %b}"
            L.append(f"| {tick(S, r['ticker'], frm)} | {found} | "
                     f"{', '.join(f'`{c}`' for c in r['_cats'])} | {sgn(r['direction'])} | {price(r['found_close'])} | {price(r['now'])} | {pct(r['since_found_pct'])} | "
                     f"{pct(r['ret_pct'])} | {pct(r['iwm_pct'])} | **{pts(r['_vs'])}** | {pct(r['excess_pct'])} | {adv} |")
    if any(len(r["_cats"]) > 1 for r in best + worst):
        L += ["", "_A ticker found under several categories is listed once, with the direction and excess of its first find._"]
    return L + [""], best, worst


def ledger_section(S, P, frm):
    tr = [r for r in S.ledger if P.start <= r["found"] <= P.end and r["status"] == "live"
          and r.get("takeable") == "yes" and r["excess_pct"] is not None]
    for r in tr:
        r["excess_pct"] = r["excess_pct"] - BL.ROUND_TRIP_COST          # same net-of-costs basis as LEDGER.md
    shorts = [r for r in S.ledger if P.start <= r["found"] <= P.end and r["status"] == "live" and r["direction"] < 0 and r["excess_pct"] is not None]
    L = ["## Ledger by category: items found this period, takeable only", "",
         f"Same rules as {link('LEDGER.md', 'ledger/LEDGER.md', frm)}'s honest scoreboard: long bets only (we can't short), average daily "
         f"$ volume ≥ ${BL.MIN_ADV_USD:,.0f}, entry ≥ ${BL.MIN_PRICE:.0f}, {BL.ROUND_TRIP_COST:.0f}% taken off for costs. Results under "
         f"{BL.JUDGE_TDAYS} trading days are an early read, not a result.", ""]
    if shorts:
        L += [f"Paper only: {len(shorts)} short bets found this period ({sum(r['excess_pct'] > 0 for r in shorts)} lagged IWM). They work as a "
              "don't-buy list and are never counted as wins.", ""]
    if not tr:
        return L + ["_No takeable item found in this period is live yet._", ""]
    L += ["| category | dir | n | mean excess | median excess | right | crashed >20% by found: n · excess | spiked >50% by found: n · excess |",
          "|---|---|---|---|---|---|---|---|"]
    for c in sorted({r["category"] for r in tr}):
        xs = [r for r in tr if r["category"] == c]
        ex = [r["excess_pct"] for r in xs]
        into = lambda r: (r["pre_move_5d"] or 0) + (r["found_day_move"] or 0)
        cr = [r["excess_pct"] for r in xs if into(r) <= -20]
        sp = [r["excess_pct"] for r in xs if into(r) >= 50]
        L.append(f"| `{c}` | {sgn(xs[0]['direction'])} | {len(ex)} | {mean(ex):+.1f}% | {median(ex):+.1f}% | {sum(x > 0 for x in ex)}/{len(ex)} | "
                 + (f"{len(cr)} · {mean(cr):+.1f}%" if cr else "0") + " | " + (f"{len(sp)} · {mean(sp):+.1f}%" if sp else "0") + " |")
    return L + [""]


def positions_section(S, P, frm):
    trades = [t for t in S.trades if t["entry_date"] <= P.end and (not t["exit_date"] or t["exit_date"] >= P.start)]
    L = ["## Positions", ""]
    if not trades:
        return L + [f"_No position was open in this period ({link('journal', 'journal/trades.csv', frm)})._", ""], []
    L += [f"Every trade open at some point in the period ({link('journal', 'journal/trades.csv', frm)}). Open trades are marked at the "
          f"close on or before {P.as_of}; P&L is after all fees, including an estimated ${SELL_COMMISSION:.2f} to sell.", "",
          "| # | ticker | strategy | side | qty | entry | mark | move | IWM since entry | P&L after fees | state |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    out = []
    for t in trades:
        closed = t["exit_date"] and t["exit_date"] <= P.as_of and t["exit"] is not None
        if closed:
            mark, md, fees = t["exit"], t["exit_date"], t["fees"]
        else:
            m = close_on(t["symbol"], P.as_of)
            if not m:
                lr = [r for r in S.ledger if r["ticker"] == t["symbol"] and r["now"] is not None]
                m = (lr[0]["now_date"], lr[0]["now"]) if lr else None
            mark, md = (m[1], m[0]) if m else (None, None)
            fees = t["fees"] + SELL_COMMISSION
        if mark is None:
            L.append(f"| {t['id']} | {tick(S, t['symbol'], frm)} | {t['strategy']} | {t.get('direction') or 'LONG'} | {t['quantity']:g} | "
                     f"${t['entry']:.3f} ({t['entry_date']:%d %b}) | n/a | | | | {'closed' if closed else 'open'} |")
            continue
        move = (mark / t["entry"] - 1) * 100 * t["sign"]
        pnl = (mark - t["entry"]) * t["quantity"] * t["sign"] - fees
        i0, i1 = next(((d, c) for d, c in bars("IWM") if d >= t["entry_date"]), None), close_on("IWM", md)
        iwm = (i1[1] / i0[1] - 1) * 100 if i0 and i1 and i1[0] >= i0[0] else None
        out.append((t, move, pnl, closed))
        L.append(f"| {t['id']} | {tick(S, t['symbol'], frm)} | {t['strategy']} | {t.get('direction') or 'LONG'} | {t['quantity']:g} | "
                 f"${t['entry']:.3f} ({t['entry_date']:%d %b}) | {price(mark)} ({md:%d %b}) | {pct(move)} | {pct(iwm)} | **${pnl:+.2f}** | "
                 f"{'closed' if closed else 'open'} |")
    return L + [""], out


def reason(S, t, P, frm):
    """One line from the stock's dossier timeline: the most telling mention in the period."""
    ms = [m for m in S.mentions().get(t, []) if P.start <= m["date"] <= P.as_of]
    if not ms:
        return "no new mentions this period"
    m = min(ms, key=lambda m: (REASON_RANK.get(m["kind"], 99), -m["date"].toordinal()))
    return f"{m['date']:%d %b}: {clip(plain(m['text']), 150)}"


def watchlist_section(S, P, frm):
    L = ["## Watchlist", "",
         f"Each stock on the {link('watchlist', 'watch/watchlist.json', frm)}: close before the period → last close in it (to {P.as_of}), "
         "including cash and spun-off shares received (ledger/corporate_actions.csv), against IWM over the same days. "
         "The reason is the most telling dated mention in the period from the stock's dossier timeline.", "",
         "| ticker | from | to | move | IWM | vs IWM | why |", "|---|---|---|---|---|---|---|"]
    out = []
    for t in S.watchlist:
        a = close_on(t, P.start - dt.timedelta(days=1))
        first_in = next(((d, c) for d, c in bars(t) if P.start <= d <= P.as_of), None)
        if not a and first_in:
            a = (first_in[0], first_in[1], "first close")
        b = close_on(t, P.as_of)
        if not a:
            cells = ["not trading yet", "", "", "", ""]
            mv = vs = None
        elif not b or b[0] <= a[0]:
            cells = [f"{price(a[1])} ({a[0]:%d %b})", "no close in the period yet", "", "", ""]
            mv = vs = None
        else:
            mv, adj = holder_move(t, a[0], b[0])
            iwm, _ = holder_move("IWM", a[0], b[0])
            vs = None if mv is None or iwm is None else mv - iwm
            cells = [f"{price(a[1])} ({a[0]:%d %b}{', first close' if len(a) > 2 else ''})", f"{price(b[1])} ({b[0]:%d %b})",
                     pct(mv) + (f" (incl. {adj})" if adj else ""), pct(iwm), f"**{pts(vs)}**" if vs is not None else ""]
        out.append((t, mv, vs))
        L.append(f"| {tick(S, t, frm)} | " + " | ".join(cells) + f" | {reason(S, t, P, frm)} |")
    return L + [""], out


def setups_section(S, P, frm):
    rows = [r for r in S.ledger if r["category"].startswith("setup_") and r["found"] <= P.as_of and r["found_close"]]
    L = ["## Setups: spikes and collapses", ""]
    if not rows:
        return L + ["_No watch-only setups were being tracked in this period._", ""], []
    flagged, table = [], []
    for r in sorted(rows, key=lambda r: (r["found"], r["ticker"])):
        win = [(d, c) for d, c in bars(r["ticker"]) if max(P.start, r["found"] + dt.timedelta(days=1)) <= d <= P.as_of]
        if not win:
            table.append(f"| {tick(S, r['ticker'], frm)} | {r['found']:%d %b} | {price(r['found_close'])} | | | | not traded since logged |")
            continue
        hi, lo = max(win, key=lambda x: x[1]), min(win, key=lambda x: x[1])
        up, dn = (hi[1] / r["found_close"] - 1) * 100, (lo[1] / r["found_close"] - 1) * 100
        flag = "**SPIKE**" if up >= SPIKE else "**COLLAPSE**" if dn <= COLLAPSE else ""
        if flag:
            flagged.append((r["ticker"], flag.strip("*"), up if up >= SPIKE else dn))
        table.append(f"| {tick(S, r['ticker'], frm)} | {r['found']:%d %b} | {price(r['found_close'])} | {price(hi[1])} ({hi[0]:%d %b}) {pct(up)} | "
                     f"{price(lo[1])} ({lo[0]:%d %b}) {pct(dn)} | {price(win[-1][1])} ({win[-1][0]:%d %b}) | {flag} |")
    L.append(f"Watch-only setups (`setup_*` rows in {link('the ledger', 'ledger/LEDGER.md', frm)}): highest and lowest close in the period "
             f"against the found price. SPIKE = a close ≥ {SPIKE:+.0f}%, COLLAPSE = a close ≤ {COLLAPSE:+.0f}%.")
    L += ["", ("**Flagged:** " + ", ".join(f"{t} {f.lower()} ({v:+.0f}%)" for t, f, v in flagged)) if flagged
          else f"**Flagged:** none of the {len(rows)} setups spiked or collapsed in this period.", "",
          "| ticker | logged | found @ | high in period | low in period | last | flag |", "|---|---|---|---|---|---|---|"] + table
    return L + [""], flagged


def events_section(S, P, frm):
    nxt = P.next()
    lo = TODAY if P.to_date else P.end + dt.timedelta(days=1)
    evs = [e for e in S.events if lo <= e["date"] <= nxt.end]
    L = ["## Coming up", "", f"Dated events from {day(lo)} to the end of the next {P.kind} ({nxt.key}, {long_day(nxt.end)}), "
                             f"from {link('the calendar', 'calendar/catalyst-dates.ics', frm)}.", ""]
    if not evs:
        return L + ["_Nothing dated in this window._", ""], []
    for e in evs:
        ts = [t for t in S.dossiers if word_rx(t).search(e["summary"] + " " + e["description"])]
        L.append(f"- **{day(e['date'])}**: {e['summary']}" + (" · " + ", ".join(link(t, f"stocks/{t}.md", frm) for t in ts) if ts else ""))
    return L + [""], evs


def links_section(S, P, frm):
    dates = [d for d in S.scan_dates() if P.start <= d <= P.end]
    named = sorted({t for t, ms in S.mentions().items() if any(P.start <= m["date"] <= P.as_of for m in ms)} | set(S.watchlist))
    L = ["## Links", ""]
    if dates:
        L.append("- **Scans:** " + " · ".join(link(day(d), f"scans/{d}.md", frm) for d in dates))
    L += ["- **Dossiers** (watchlist, plus every stock mentioned this period): " + " · ".join(link(t, f"stocks/{t}.md", frm) for t in named),
          f"- **Ledger:** {link('LEDGER.md', 'ledger/LEDGER.md', frm)} · **Index:** {link('all scans', 'scans/README.md', frm)} · "
          f"{link('all dossiers', 'stocks/README.md', frm)} · {link('all reports', 'reports/README.md', frm)}"]
    return L + [""]


def calls_section(S, P, frm):
    """Public calls (calls/marks.csv): every call open during the period, with its mark as of the latest close."""
    p = ROOT / "calls/marks.csv"
    rows = [r for r in csv.DictReader(open(p, encoding="utf-8"))] if p.exists() else []
    rows = [r for r in rows if r["posted_utc"][:10] <= P.end.isoformat() and (not r["end_date"] or r["status"] == "open"
            or r["end_date"] >= P.start.isoformat())]
    L = ["## Public calls", "", f"Every committed call ({link('the record', 'calls/README.md', frm)}), marked from the next open "
         "against IWM and a named control, closed only by its own pre-stated rule.", ""]
    if not rows:
        return L + ["_No public calls were open in this period._", ""], []
    L += ["| # | call | entry | latest / exit | return | vs market | vs control | status |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        side = "LONG" if int(r["direction"]) > 0 else "SHORT"
        if not r["ret_pct"]:
            L.append(f"| {r['id']} | {side} {r['ticker']} | | | | | | {r['status']} |"); continue
        f = lambda k: f"{float(r[k]):+.1f}%" if r[k] else ""
        L.append(f"| {r['id']} | {side} {link(r['ticker'], 'stocks/' + r['ticker'] + '.md', frm)} | ${float(r['entry']):.2f} ({r['entry_date']}) | "
                 f"${float(r['end_price']):.2f} ({r['end_date']}) | {f('ret_pct')} | {f('excess_bench')} ({r['bench']}) | {f('excess_control')} ({r['control']}) | {r['status']} |")
    return L + [""], rows


def render(S, P):
    frm = P.path
    prev, nxt = P.prev(), P.next()
    nav = ([link(f"← {prev.key}", prev.path, frm)] if (ROOT / prev.path).exists() else []) + [link("all reports", "reports/README.md", frm)] \
        + ([link(f"{nxt.key} →", nxt.path, frm)] if (ROOT / nxt.path).exists() else [])
    found, summ = found_section(S, P, frm)
    movers, best, worst = movers_section(S, P, frm)
    pos, pos_rows = positions_section(S, P, frm)
    wl, wl_rows = watchlist_section(S, P, frm)
    st, flagged = setups_section(S, P, frm)
    ev, evs = events_section(S, P, frm)
    cl, cl_rows = calls_section(S, P, frm)
    glance = []
    if summ:
        glance.append(f"Found: {summ['days']} scan days · {summ['signals']} S1 signals · {summ['filings']} watchlist filings · "
                      f"{summ['market']} market-wide items · {summ['press']} press releases · {summ['setups']} new setups · "
                      f"{summ['worth']} triage notes worth reading")
    if best or worst:
        f = lambda r: f"{r['ticker']} {pts(r['_vs'])}"
        glance.append("Since found, vs IWM: best " + (", ".join(f(r) for r in best[:3]) or "none") + "; worst " + (", ".join(f(r) for r in worst[:3]) or "none"))
    marked = [r for r in cl_rows if r["ret_pct"]]
    if cl_rows:
        glance.append(f"Public calls: {len(cl_rows)}" + (" · " + ", ".join(f"#{r['id']} {r['ticker']} {float(r['ret_pct']):+.1f}%"
                      + (f" ({float(r['excess_bench']):+.1f} vs {r['bench']})" if r['excess_bench'] else "") for r in marked) if marked else " (entering at the next open)"))
    if pos_rows:
        glance.append("Positions: " + ", ".join(f"{t['symbol']} {pct(m)} (${p:+.2f} after fees{', closed' if c else ''})" for t, m, p, c in pos_rows))
    moved = [r for r in wl_rows if r[2] is not None]
    if moved:
        moved.sort(key=lambda r: -r[2])
        glance.append(f"Watchlist vs IWM: best {moved[0][0]} {pts(moved[0][2])}, worst {moved[-1][0]} {pts(moved[-1][2])}")
    glance.append("Setups: " + (", ".join(f"{t} {f.lower()} {v:+.0f}%" for t, f, v in flagged) if flagged else "no spikes or collapses"))
    glance.append(f"Coming up: {len(evs)} dated events" + (f", next {day(evs[0]['date'])}: {evs[0]['summary']}" if evs else ""))
    state = f"to date, as of {long_day(P.as_of)}" if P.to_date else "complete"
    L = [f"# {TITLE[P.kind]} report: {P.key} ({P.span()})", "", " · ".join(nav), "",
         f"Period {state}. Built by `reports/build_periodic.py` from the daily scans, the ledger, the journal, the calendar and Yahoo "
         "daily closes. Rebuilt every weekday morning while the period is open.", "",
         "## At a glance", ""] + [f"- {g}" for g in glance] + [""]
    L += found + cl + movers + ledger_section(S, P, frm) + pos + wl + st + ev + links_section(S, P, frm)
    while L and not L[-1]:
        L.pop()
    return "\n".join(L) + "\n", glance


def index():
    frm = "reports/README.md"
    L = ["# Reports", "",
         "Weekly (ISO weeks, Monday to Sunday), monthly and quarterly reports: what the scans found, the biggest movers since "
         "found against IWM, ledger stats by category, positions and P&L, every watchlist stock's move with a reason, setups that "
         "spiked or collapsed, and what's coming up. Built by `reports/build_periodic.py`; the current week, month and quarter are "
         "rebuilt every weekday morning by the `morning-briefing` workflow, and on Mondays last week's summary goes to Discord #reports.", ""]
    for kind in ("week", "month", "quarter"):
        files = sorted((ROOT / "reports" / FOLDER[kind]).glob("*.md"), reverse=True)
        L += [f"## {TITLE[kind]}", ""] + ([f"- {link(f.stem, f'reports/{FOLDER[kind]}/{f.name}', frm)}" for f in files] or ["_None yet._"]) + [""]
    L += ["## Generators", "",
          "- `reports/build_scans.py`: daily scans, `scans/YYYY-MM-DD.md`",
          "- `reports/build_stocks.py`: stock dossiers, `stocks/TICKER.md` (only the part below the AUTO marker)",
          "- `reports/build_periodic.py`: these reports (`--period week|month|quarter --date YYYY-MM-DD`, `--current`, `--all`)",
          "- `reports/sources.py`: the shared readers all three use"]
    return "\n".join(L) + "\n"


def discord_text(P, glance):
    return "\n".join([f"**{TITLE[P.kind]} report {P.key}** ({P.span()})"] + [f"- {g}" for g in glance]
                     )


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--period", choices=["week", "month", "quarter"])
    ap.add_argument("--date", help="any date in the period, YYYY-MM-DD (default today)")
    ap.add_argument("--current", action="store_true", help="this week/month/quarter, plus periods that ended in the last 3 days")
    ap.add_argument("--all", action="store_true", help="every period from the first scan date to today")
    ap.add_argument("--post-weekly", action="store_true", help="on Mondays, send last week's summary to Discord #reports")
    ap.add_argument("--dry-run", action="store_true", help="print the Discord summary instead of sending it")
    ap.add_argument("--force", action="store_true", help="send the weekly summary even if it was already sent")
    a = ap.parse_args()
    if not (a.period or a.current or a.all or a.post_weekly):
        ap.error("give --period (with --date), --current or --all")
    S = Sources()
    want = {}
    if a.period:
        P = Period(a.period, dt.date.fromisoformat(a.date) if a.date else TODAY)
        want[P.path] = P
    if a.current:
        for kind in FOLDER:
            for d in (TODAY, TODAY - dt.timedelta(days=3)):
                P = Period(kind, d)
                want[P.path] = P
    if a.all:
        first = min(S.scan_dates(), default=TODAY)
        for kind in FOLDER:
            P = Period(kind, first)
            while P.start <= TODAY:
                want[P.path] = P
                P = P.next()
    glances, changed = {}, []
    # oldest first, so each report's "previous" link finds its file; then once more so "next" links appear too
    for rnd in (0, 1):
        for P in sorted(want.values(), key=lambda p: (p.kind, p.start)):
            text, glances[P.path] = render(S, P)
            if write(P.path, text) and P.path not in changed:
                changed.append(P.path)
    idx = write("reports/README.md", index())
    print(f"reports: {len(want)} period(s) checked, {len(changed)} written{': ' + ', '.join(changed) if changed else ''}"
          f"; index {'updated' if idx else 'unchanged'}")
    if a.post_weekly and (TODAY.weekday() == 0 or a.dry_run):
        P = Period("week", TODAY - dt.timedelta(days=7))
        if P.path not in glances:
            text, glances[P.path] = render(S, P)
            write(P.path, text)
        msg = discord_text(P, glances[P.path])
        marker = ROOT / "reports" / f".sent-weekly-{P.key}"   # the workflow has several morning slots: send once
        if a.dry_run:
            print("\n--- Discord #reports (dry run) ---\n" + msg)
        elif marker.exists() and not a.force:
            print(f"weekly summary {P.key} already sent ({marker.name}); nothing sent")
        else:
            import notify  # briefing/notify.py
            sent = notify.send(msg, "reports")
            if sent:
                marker.write_text(", ".join(sent) + "\n", encoding="utf-8")
            print(f"weekly summary {P.key}: sent via {', '.join(sent) or 'nothing (DISCORD_WEBHOOK_REPORTS not set)'}")


if __name__ == "__main__":
    main()
