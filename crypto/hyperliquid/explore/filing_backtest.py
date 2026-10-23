"""Exploration, 23 Oct 2026 (the trader's question): when our SEC scan flags a company that also trades as a
Hyperliquid perp, does the perp then move the way the section suggests?

Only what was known on the filing day T is used:
- a market counts only if it was already trading on T (survivorship: delisted markets are included);
- the side comes from the form type alone (share sales -> short, activist / tender -> long);
- entry is the next US business day at 13:00 UTC (09:00 New York in summer, 08:00 in winter), before the cash open;
- when a stock has several Hyperliquid markets, the one with the most dollars traded in the 24 hours before entry.

Not a pre-registered test. Only the form-type sections of watch/scan_market.py are replayed; the sections that need
the filing's text (8-K phrases, Form 4 insider buys, red flags, new contracts) are not. 424B4/424B5 prospectuses are
split into share sales and debt sales by their cover page (a heuristic, see is_debt).

Run:  python crypto/hyperliquid/explore/filing_backtest.py   -> explore/2026-10-23-filings-on-hl.md and .csv
"""
import csv
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "watch"))
from scan_market import NOT_SUPPLY, same_asset  # noqa: E402

CACHE = ROOT / "crypto/hyperliquid/cache/backtest"
OUT = Path(__file__).parent
END = date(2026, 10, 15)          # last filing day with five business days of prices after it (run 23 Oct)
COST = 0.2                        # assumed round trip in %, taker fees both sides plus spread; funding not included
MIN_VOL = 5e5                     # dollars traded on the market in the 24 hours before entry, to count as takeable
SHORT = {"S-1": "Share registrations", "EFFECT": "Registrations effective", "424B4": "Offering priced",
         "424B5": "Share sales and shelves", "S-3": "Share sales and shelves", "S-3ASR": "Share sales and shelves",
         "F-3": "Share sales and shelves", "F-3ASR": "Share sales and shelves", "NT 10-K": "Late filings",
         "NT 10-Q": "Late filings"}
LONG = {"SC 13D": "Activists / new 5%+ holders", "SCHEDULE 13D": "Activists / new 5%+ holders",
        "SC TO-T": "Tender offers (third party)", "SC TO-I": "Tender offers (issuer buyback)",
        "SC 13E3": "Going-private deals", "SCHEDULE 13E-3": "Going-private deals"}
SUBJECT_FORMS = set(LONG)         # filed under both the holder's or bidder's CIK and the company's: keep the subject only
HOUR = 3600 * 1000


def cached(name, fn, max_age_h=None):
    p = CACHE / name
    if p.exists() and (max_age_h is None or time.time() - p.stat().st_mtime < max_age_h * 3600):
        return json.loads(p.read_text(encoding="utf-8"))
    v = fn()
    p.write_text(json.dumps(v), encoding="utf-8")
    return v


def info(body):
    for attempt in (1, 2, 3):
        try:
            req = urllib.request.Request("https://api.hyperliquid.xyz/info", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                time.sleep(0.25)
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3)


def markets():
    """Every builder-exchange perp, delisted ones included (the main exchange lists crypto only)."""
    out = []
    for d in info({"type": "perpDexs"}):
        if not d:
            continue
        for u in info({"type": "meta", "dex": d["name"]})["universe"]:
            out.append({"name": u["name"], "base": u["name"].split(":")[-1].upper(), "delisted": bool(u.get("isDelisted"))})
    return out


def candles(name, interval, start_ms):
    end = int(time.time() * 1000)
    return info({"type": "candleSnapshot", "req": {"coin": name, "interval": interval, "startTime": start_ms, "endTime": end}})


def yahoo(t):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(t)}?range=2y&interval=1d"
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
        r = r["chart"]["result"][0]
        time.sleep(0.2)
        return {datetime.fromtimestamp(ts, timezone.utc).date().isoformat(): c
                for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c}
    except Exception:
        return {}


def sec(url, limit=None):
    time.sleep(0.12)
    req = urllib.request.Request(url, headers={"User-Agent": "PersonalResearch research@example.com"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(limit)


def daily_index(day):
    p = CACHE / f"form.{day:%Y%m%d}.idx"
    if p.exists():
        return p.read_text(encoding="latin-1")
    qtr = (day.month - 1) // 3 + 1
    try:
        txt = sec(f"https://www.sec.gov/Archives/edgar/daily-index/{day.year}/QTR{qtr}/form.{day:%Y%m%d}.idx").decode("latin-1")
    except Exception:
        return ""                                   # weekend or holiday: no index
    p.write_text(txt, encoding="latin-1")
    return txt


def head(path, n=120000):
    """The first n bytes of a filing's full submission text, cached."""
    key = path.replace("/", "_")
    p = CACHE / f"head_{key}"
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    txt = sec(f"https://www.sec.gov/Archives/{path}", n).decode("utf-8", errors="replace")
    p.write_text(txt, encoding="utf-8")
    return txt


def subject_cik(path):
    m = re.search(r"SUBJECT COMPANY:.*?CENTRAL INDEX KEY:\s*(\d+)", head(path, 8000), re.S)
    return int(m.group(1)) if m else None


def effect_form(path):
    """The form an EFFECT notice makes effective (the scanner's rule 2026-10-05: POS AM, S-4 and the like are not supply)."""
    p = CACHE / f"effect_{path.replace('/', '_')}"
    if p.exists():
        return p.read_text(encoding="utf-8")
    try:
        xml = sec("https://www.sec.gov/Archives/" + path.replace("-", "").replace(".txt", "/primary_doc.xml")).decode("utf-8", "ignore")
        m = re.search(r"<form>([^<]+)</form>", xml)
        form = m.group(1).strip() if m else "?"
    except Exception:
        form = "?"
    p.write_text(form, encoding="utf-8")
    return form


def is_debt(path):
    """True if a prospectus cover sells notes rather than shares (heuristic: the cover's first 6,000 characters)."""
    raw = head(path)
    body = raw.split("<TEXT>", 1)[-1]
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    cover = re.sub(r"\s+", " ", text)[:6000]
    shares = re.search(r"shares of (?:our |its )?(?:class [a-z] )?(?:common|ordinary) stock|ordinary shares|"
                       r"american depositary shares|common shares", cover, re.I)
    notes = re.search(r"notes due|debentures|senior notes|subordinated notes|medium-term notes", cover, re.I)
    return bool(notes) and not shares


def bday_after(d, n=1):
    while n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def at(bars, ms):
    """Open of the first hourly bar at or up to 3 hours after ms."""
    for k in range(4):
        b = bars.get(ms + k * HOUR)
        if b:
            return float(b["o"])
    return None


def measure(bars, day):
    """(1-day return %, 5-day return %, dollars traded in the 24h before entry) for an entry after filing day `day`."""
    e = int(datetime.combine(bday_after(day), datetime.min.time(), timezone.utc).timestamp() * 1000) + 13 * HOUR
    p0 = at(bars, e)
    if p0 is None:
        return None
    vol = sum(float(bars[e - k * HOUR]["v"]) * float(bars[e - k * HOUR]["c"]) for k in range(1, 25) if e - k * HOUR in bars)
    out = []
    for n in (1, 5):
        d = bday_after(bday_after(day), n)
        p = at(bars, int(datetime.combine(d, datetime.min.time(), timezone.utc).timestamp() * 1000) + 13 * HOUR)
        out.append(None if p is None else (p / p0 - 1) * 100)
    return out[0], out[1], vol


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    tick = cached("company_tickers.json", lambda: json.loads(sec("https://www.sec.gov/files/company_tickers.json")), 24)
    cik_of = {v["ticker"].upper(): int(v["cik_str"]) for v in tick.values()}
    mk = [m for m in cached("markets.json", markets, 12) if m["base"] in cik_of]
    print(f"{len(mk)} builder-exchange markets share a symbol with an SEC-listed company")

    start = int(time.time() * 1000) - 5000 * HOUR             # Hyperliquid keeps the latest 5,000 candles per interval
    hourly, keep = {}, {}
    for m in mk:
        n = m["name"].replace(":", "_")
        h = cached(f"h_{n}.json", lambda: candles(m["name"], "1h", start), 12)
        dly = cached(f"d_{n}.json", lambda: candles(m["name"], "1d", start - 400 * 24 * HOUR), 12)
        stock = cached(f"y_{m['base']}.json", lambda: yahoo(m["base"]), 12)
        perp = {datetime.fromtimestamp(c["t"] / 1000, timezone.utc).date().isoformat(): float(c["c"]) for c in dly}
        ok = same_asset(perp, stock)
        if not h or not ok:
            print(f"  skip {m['name']}: {'no hourly candles' if not h else 'does not track the stock' if ok is False else 'no prices to compare'}")
            continue
        hourly[m["name"]] = {int(b["t"]): b for b in h}
        first = min(perp) if perp else None
        keep.setdefault(m["base"], []).append({"name": m["name"], "first": first})
    print(f"{sum(len(v) for v in keep.values())} markets on {len(keep)} stocks track their stock")

    wanted = {cik_of[t]: t for t in keep}
    first_day = min(datetime.fromtimestamp(min(b) / 1000, timezone.utc).date() for b in hourly.values())
    events, d = {}, first_day
    while d <= END:
        if d.weekday() < 5:
            for line in daily_index(d).splitlines():
                parts = line.split()
                if len(parts) < 5 or not parts[-2].isdigit() or int(parts[-3]) not in wanted:
                    continue
                form = re.match(r"\S+(?: \S+)*", line).group(0)
                side = -1 if form in SHORT else 1 if form in LONG else 0
                if not side:
                    continue
                cik, path = int(parts[-3]), parts[-1]
                if form in SUBJECT_FORMS and subject_cik(path) != cik:
                    continue                                  # the listed company is the holder or bidder, not the target
                section = SHORT.get(form) or LONG[form]
                if form in ("424B4", "424B5") and is_debt(path):
                    side, section = 0, "Debt sale (prospectus for notes)"
                if form == "EFFECT":
                    reg = effect_form(path)
                    if any(reg.upper().startswith(f) for f, _ in NOT_SUPPLY):
                        side, section = 0, f"Effective, not supply ({reg})"
                events.setdefault((d, wanted[cik], section), {"form": form, "side": side, "path": path})
        d += timedelta(days=1)
    print(f"{len(events)} ticker-day-section events from {first_day} to {END}")

    rows, control = [], {}
    for (day, t, section), e in sorted(events.items()):
        live = [m for m in keep[t] if m["first"] and m["first"] <= day.isoformat()]
        best = None
        for m in live:
            r = measure(hourly[m["name"]], day)
            if r and (best is None or r[2] > best[1][2]):
                best = (m["name"], r)
        if best is None:
            rows.append({"day": day, "ticker": t, "section": section, "form": e["form"], "side": e["side"],
                         "market": "", "note": "no Hyperliquid market on T" if not live else "no price at entry"})
            continue
        name, (r1, r5, vol) = best
        if name not in control:                               # the same market's average move on every day in the window
            xs = [measure(hourly[name], first_day + timedelta(days=i)) for i in range((END - first_day).days + 1)
                  if (first_day + timedelta(days=i)).weekday() < 5]
            xs = [x for x in xs if x and x[0] is not None]
            control[name] = (mean(x[0] for x in xs) if xs else 0,
                             mean(x[1] for x in xs if x[1] is not None) if xs else 0)
        rows.append({"day": day, "ticker": t, "section": section, "form": e["form"], "side": e["side"], "market": name,
                     "r1": r1, "r5": r5, "vol": vol, "c1": control[name][0], "c5": control[name][1], "note": ""})
    write(rows, first_day)


def once(rs):
    """One row per stock per filing day, so an IPO's EFFECT and 424B4 (or two prospectuses) are not counted twice."""
    seen, out = set(), []
    for r in rs:
        if (r["day"], r["ticker"]) not in seen:
            seen.add((r["day"], r["ticker"]))
            out.append(r)
    return out


def stats(rs, key, ctl):
    xs = [r["side"] * r[key] for r in rs if r.get(key) is not None]
    ex = [r["side"] * (r[key] - r[ctl]) for r in rs if r.get(key) is not None]
    if not xs:
        return "| 0 | | | | | |"
    return (f"| {len(xs)} | {mean(xs):+.2f}% | {median(xs):+.2f}% | {sum(x > 0 for x in xs)}/{len(xs)} | "
            f"{mean(ex):+.2f}% | {mean(xs) - COST:+.2f}% |")


def write(rows, first_day):
    stem = OUT / "2026-10-23-filings-on-hl"
    cols = ["day", "ticker", "section", "form", "side", "market", "r1", "r5", "vol", "c1", "c5", "note"]
    with open(stem.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.3f}" if isinstance(r.get(k), float) else r.get(k, "")) for k in cols})
    traded = [r for r in rows if r.get("market")]
    liquid = [r for r in traded if r["vol"] >= MIN_VOL]
    L = ["# Our SEC sections on Hyperliquid stock perps: a backdated check", "",
         f"Exploration, run 23 Oct 2026. Filing days {first_day} to {END}. Not a pre-registered test.", "",
         "Only what was known on the filing day T: a market counts only if it already traded on T; the side comes from "
         "the form type; entry is the next US business day at 13:00 UTC, before the cash open. Returns are in the "
         "direction of the side (a fall is a gain for a short). 'vs same market' subtracts that market's average move "
         "over every day in the window, so a short does not look good just because the stock fell all year. "
         f"'after cost' takes off an assumed {COST}% round trip; funding is not included. "
         f"'Takeable' = at least ${MIN_VOL/1e3:.0f}k traded on the market in the 24 hours before entry. "
         "The SHORT side and LONG side rows count a stock once per filing day; the section rows below them can share an "
         "event (an IPO's EFFECT and 424B4 land on the same day).", "",
         f"- Events found: {len(rows)} · with a Hyperliquid price at entry: {len(traded)} · takeable: {len(liquid)}", ""]
    for label, rs in (("All with a price", traded), ("Takeable only", liquid)):
        L += [f"## {label}", "", "| group | horizon | n | mean | median | went our way | vs same market | after cost |",
              "|---|---|---|---|---|---|---|---|"]
        groups = [("SHORT side", once([r for r in rs if r["side"] < 0])), ("LONG side", once([r for r in rs if r["side"] > 0]))]
        groups += [(s, [r for r in rs if r["section"] == s and r["side"]]) for s in sorted({r["section"] for r in rs if r["side"]})]
        for g, gr in groups:
            L.append(f"| {g} | 1 day " + stats(gr, "r1", "c1"))
            L.append(f"| {g} | 5 days " + stats(gr, "r5", "c5"))
        L.append("")
    L += ["## Every event", "", "| filed | ticker | section | form | side | market | price move 1 day | price move 5 days | $ traded 24h before |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        side = {1: "LONG", -1: "SHORT", 0: "none"}[r["side"]]
        if not r.get("market"):
            L.append(f"| {r['day']} | {r['ticker']} | {r['section']} | {r['form']} | {side} | {r['note']} | | | |")
            continue
        f = lambda v: "" if v is None else f"{v:+.1f}%"
        L.append(f"| {r['day']} | {r['ticker']} | {r['section']} | {r['form']} | {side} | {r['market']} | {f(r['r1'])} | "
                 f"{f(r['r5'])} | ${r['vol']/1e6:.1f}M |")
    stem.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
