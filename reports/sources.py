"""Shared readers for the report generators (build_scans.py, build_stocks.py, build_periodic.py).

Reads only files other jobs wrote and never fetches anything:
  watch/dod/YYYY-MM-DD.md, data/signals.csv     S1 DoD contracts (evening job)
  watch/digests/YYYY-MM-DD.md                   watchlist filings (watch/check_filings.py)
  watch/digests/YYYY-MM-DD-triage.md            evening triage
  watch/market/YYYY-MM-DD.md                    market-wide SEC scan (watch/scan_market.py)
  data/press/YYYY-MM-DD.csv                     press releases, by the UTC day first seen
  ledger/ledger.csv, ledger/manual_calls.csv    every call vs IWM; ideas and setups
  journal/trades.csv, watch/watchlist.json      positions, watchlist
  watch/context/latest.json                     peers and sympathy flags
  calendar/catalyst-dates.ics                   dated events
  research/**/*.md|.html, posts/*.md            notes, dated by the YYYY-MM-DD in their path
Category rules come from ledger/build_ledger.py, so a scan item and its ledger row always agree.
Standard library only.
"""
import csv, html, json, os, re, sys, datetime as dt
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/astonmonnach/signal-research/blob/main"
sys.path.insert(0, str(ROOT / "ledger"))
import build_ledger as BL  # noqa: E402  (only its rule tables are used; importing fetches nothing)

TODAY = dt.datetime.now(dt.UTC).date()
OLD_FILING_DAYS = 7   # digest filings older than this were backfilled (e.g. a ticker just added), not new

# Market-scan sections the ledger doesn't score, and 8-Ks whose only phrase isn't a ledger category.
SCAN_ONLY = [("spin-offs", "spin_off_form10"), ("going-private", "going_private")]
CATEGORY_LABEL = {
    "s1_dod_contract": "S1 DoD contract", "merger_vote": "merger vote", "tender_third_party": "tender offer (third party)",
    "tender_issuer_buyback": "issuer tender / buyback", "activist_13d": "activist / new 5% holder (13D)",
    "share_registration": "share registration (S-1)", "registration_effective": "registration declared effective",
    "ipo_priced": "IPO / offering priced", "delisting": "delisting", "spin_off_form10": "spin-off (Form 10)",
    "going_private": "going private (13E-3)", "8k_strategic_review": "8-K strategic review / alternatives",
    "8k_spin_off": "8-K spin-off", "8k_reverse_split": "8-K reverse split", "8k_lock_up": "8-K lock-up",
    "8k_tender_offer": "8-K tender offer", "8k_special_dividend": "8-K special dividend",
    "8k_other": "8-K other phrase (go-shop, bio-mention)",
    "idea_catalyst": "idea: catalyst", "idea_spinoff": "idea: spin-off", "idea_merger": "idea: merger",
    "idea_overhang": "idea: overhang", "setup_supply_deficiency": "setup: supply + listing deficiency",
}
# Order of the mentions within one date of a dossier timeline.
KIND_RANK = {"triage": 0, "press": 1, "s1": 2, "trade": 3, "setup": 4, "market": 5, "filings": 6,
             "calendar": 7, "research": 8, "post": 9, "dismissed": 10}
SECTION_ANCHOR = {"s1": "s1-contract-signals", "filings": "watchlist-filings", "market": "market-wide-scan",
                  "press": "press-releases", "setup": "new-setups", "triage": "triage-notes", "dismissed": "triage-notes"}


# ---------- small helpers ----------
def label(cat):
    return CATEGORY_LABEL.get(cat or "", (cat or "uncategorised").replace("_", " "))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def pct(v, nd=1):
    return "" if v is None else f"{v:+.{nd}f}%"


def pts(v):
    return "" if v is None else f"{v:+.1f} pts"


def money(v):
    """Average daily $ volume, compact."""
    if v is None: return ""
    return f"${v / 1e6:.1f}M" if v >= 1e6 else f"${v / 1e3:.0f}k" if v >= 500 else f"${v:.0f}"


def usd(v):
    if v is None: return ""
    return f"${v / 1e9:,.2f}bn" if v >= 1e9 else f"${v / 1e6:,.1f}M"


def price(v):
    if v is None: return ""
    return f"${v:,.2f}" if v >= 1 else f"${v:.3f}"


def day(d):
    return f"{d:%a} {d.day} {d:%b}"


def long_day(d):
    return f"{d:%a} {d.day} {d:%b %Y}"


def rows(path):
    p = ROOT / path
    return list(csv.DictReader(open(p, encoding="utf-8", newline=""))) if p.exists() else []


def word_rx(ticker):
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(ticker)}(?![A-Za-z0-9])")


def href(target, frm):
    """Link target from repo file `frm` to `target` (a repo path, optionally with #anchor, or a URL)."""
    if re.match(r"https?://", target):
        return target
    path, _, anchor = target.partition("#")
    r = os.path.relpath(ROOT / path, (ROOT / frm).parent).replace(os.sep, "/")
    return r + (f"#{anchor}" if anchor else "")


def link(text, target, frm):
    text = str(text).replace("[", "(").replace("]", ")")
    return f"[{text}]({href(target, frm)})"


def write(path, text):
    """Write repo file `path` only if its content changed. -> True when written."""
    p = ROOT / path
    text = text.replace("\r\n", "\n")
    if p.exists() and p.read_text(encoding="utf-8") == text:
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


LINK_RX = re.compile(r"\[([^\]]*)\]\((\S+?)\)")


def links_in(s):
    out = []
    for m in LINK_RX.finditer(s):
        if (m.group(1), m.group(2)) not in out:
            out.append((m.group(1), m.group(2)))
    return out


def plain(s):
    """Markdown -> one tidy line: links dropped (list them separately), table pipes and backticks removed."""
    s = LINK_RX.sub("", s)
    s = s.replace("`", "").replace("|", " ")
    s = re.sub(r"\s*·\s*(?=[.,;:)]|$)", "", s)
    s = re.sub(r"\(\s*\)", "", s)
    s = re.sub(r"\s+([.,;:])", r"\1", s)
    s = re.sub(r"\.(\s*\.)+", ".", s)
    return " ".join(s.split()).strip(" ·")


def sgn(d):
    return f"{d:+d}" if d else "0"


def clip(s, n, sentence=False):
    """Shorten to n chars; with sentence=True, prefer ending on a full sentence."""
    if sentence and len(s) > n:
        cut = s[:n].rfind(". ")
        if cut > n // 2:
            s = s[:cut + 1]
    if len(s) > n:
        s = s[:n].rsplit(" ", 1)[0].rstrip(" ,;:·(") + "…"
    if s.count("**") % 2:
        s += "**"
    return s


def first_sentence(s):
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    return m.group(1) if m else s


def dated_files(folder, suffix=".md"):
    """{date: Path} for folder/YYYY-MM-DD<suffix> (so *-triage.md is skipped)."""
    out = {}
    for f in sorted((ROOT / folder).glob(f"*{suffix}")):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})" + re.escape(suffix), f.name)
        if m:
            out[dt.date.fromisoformat(m.group(1))] = f
    return out


def relp(f):
    return Path(f).relative_to(ROOT).as_posix()


# ---------- readers ----------
def ledger():
    out = []
    for r in rows("ledger/ledger.csv"):
        r = dict(r)
        for c in ("pre_move_5d", "found_day_move", "adv_usd", "found_close", "entry_open", "now", "since_found_pct",
                  "ret_pct", "iwm_pct", "excess_pct", "days"):
            r[c] = num(r.get(c))
        r["direction"] = int(r["direction"] or 0)
        r["found"] = dt.date.fromisoformat(r["found"])
        r["now_date"] = dt.date.fromisoformat(r["now_date"]) if r.get("now_date") else None
        out.append(r)
    return out


def signals():
    out = []
    for r in rows("data/signals.csv"):
        m = re.match(r"S1-(\d{4}-\d{2}-\d{2})-", r["signal_id"])
        if m:
            out.append(dict(r, date=dt.date.fromisoformat(m.group(1))))
    return out


def dod_days():
    out = {}
    for d, f in dated_files("watch/dod").items():
        md = f.read_text(encoding="utf-8")
        src = re.search(r"^Source: (\S+)", md, re.M)
        summ = re.search(r"^(\d+ awards.*)$", md, re.M)
        awards = re.search(r"^(\d+) awards", md, re.M)
        out[d] = {"path": relp(f), "source": src.group(1) if src else None,
                  "summary": summ.group(1).strip() if summ else "", "awards": int(awards.group(1)) if awards else 0}
    return out


def market_scans():
    """{date: {path, header, sections: [{heading, category, items}]}}; items merged per ticker within a section."""
    out = {}
    for d, f in dated_files("watch/market").items():
        md = f.read_text(encoding="utf-8")
        hm = re.search(r"^([\d,]+) filings filed\. (\d+) from listed", md, re.M)
        sections, cur = [], None
        for line in md.splitlines():
            if line.startswith("## "):
                h = line[3:].strip(); hl = h.lower()
                cat = next((c for k, c in BL.SECTION_CATEGORY if hl.startswith(k)), None)
                cat = cat or next((c for k, c in SCAN_ONLY if hl.startswith(k)), None) or ("8k" if hl.startswith("8-ks") else None)
                cur = {"heading": h, "category": cat, "items": [], "errors": []}
                sections.append(cur)
                continue
            if cur is None or not line.startswith("- "):
                continue
            m = re.match(r"- \*\*([^*]+)\*\*\s*(.*)", line)
            if not m:
                cur["errors"].append(line[2:].strip())
                continue
            tickers, rest = m.group(1), m.group(2)
            first = re.match(r"[A-Z0-9.\-]+", tickers)
            lk = LINK_RX.search(rest)
            it = {"tickers": tickers, "ticker": first.group(0) if first else tickers, "links": [lk.group(2)] if lk else []}
            if cur["category"] == "8k":   # same rule as build_ledger.rows_market_scans, so the keys match
                low = re.sub(r"bio-mention \([^)]*\),?", "", rest.lower())
                it["category"] = next((c for p, c in BL.PHRASE_CATEGORY if p in low), None) or "8k_other"
                it["ledger_category"] = None if it["category"] == "8k_other" else it["category"]
                it["form"] = "8-K"
                it["what"] = rest[:lk.start()].strip() if lk else rest
                im = re.search(r"items (\S+)", rest)
                it["items"] = im.group(1) if im else ""
            else:
                fm = re.search(r"`([^`]+)`", rest)
                it["category"] = it["ledger_category"] = cur["category"]
                if cur["category"] in dict(SCAN_ONLY).values():
                    it["ledger_category"] = None
                it["form"] = fm.group(1) if fm else ""
                it["what"] = rest[:fm.start()].strip() if fm else rest
            prev = next((x for x in cur["items"] if x["tickers"] == it["tickers"] and x["category"] == it["category"]), None)
            if prev:   # the same company filing twice in one section (e.g. two 13Ds) -> one row, two links
                prev["links"] += [u for u in it["links"] if u not in prev["links"]]
                prev["count"] = prev.get("count", 1) + 1
            else:
                cur["items"].append(it)
        out[d] = {"path": relp(f), "filed": hm.group(1) if hm else "?", "matched": hm.group(2) if hm else "?",
                  "sections": sections}
    return out


def digests():
    out = {}
    for d, f in dated_files("watch/digests").items():
        filings, notes = [], []
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"- \*\*([A-Z0-9.\-]+)\*\* (\d{4}-\d{2}-\d{2}) `([^`]+)`: (.*?)\s*\[filing\]\((\S+)\)", line)
            if m:
                filed = dt.date.fromisoformat(m.group(2))
                filings.append({"ticker": m.group(1), "filed": filed, "form": m.group(3), "what": m.group(4).rstrip(". "),
                                "link": m.group(5), "old": filed < d - dt.timedelta(days=OLD_FILING_DAYS)})
            elif line.startswith("- "):
                notes.append(line[2:].strip())
        out[d] = {"path": relp(f), "filings": filings, "notes": notes}
    return out


def _bullets(body):
    out, cur = [], None
    for line in body.splitlines():
        if line.startswith("- "):
            cur = [line[2:].strip()]
            out.append(cur)
        elif cur is not None and line[:1] in (" ", "\t") and line.strip():
            cur.append(line.strip())
        elif line.strip():
            cur = None
    return out


def _lead(first):
    """Text before the first ':' outside brackets: '**MTUS** (position)', 'Other 13Ds (BSAA, NSAI, ELAB)'."""
    depth, i = 0, 0
    if first.startswith("**"):
        i = first.find("**", 2) + 2 if first.find("**", 2) > 0 else 0
    for j in range(i, len(first)):
        ch = first[j]
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        elif ch == ":" and depth <= 0:
            return first[:j].strip()
    return first[:200].strip()


def triages():
    out = {}
    for f in sorted((ROOT / "watch/digests").glob("*-triage.md")):
        d = dt.date.fromisoformat(f.name[:10])
        md = f.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), f.stem)
        worth, dismissed = [], []
        for sec in re.split(r"^## ", md, flags=re.M)[1:]:
            head, _, body = sec.partition("\n")
            kind = "worth" if "worth" in head.lower() else "dismissed" if "dismiss" in head.lower() else None
            if not kind:
                continue
            for b in _bullets(body):
                full = " ".join(b)
                item = {"first": b[0], "rest": " ".join(b[1:]), "full": full, "lead": _lead(b[0]), "links": links_in(full)}
                (worth if kind == "worth" else dismissed).append(item)
        out[d] = {"path": relp(f), "title": title, "worth": worth, "dismissed": dismissed, "text": md}
    return out


def triage_summary(b, n):
    s = plain(b["first"])
    if len(s) < 110 and b["rest"]:
        s += " " + first_sentence(plain(b["rest"]))
    return clip(s, n, sentence=True)


def press():
    out = {}
    for d, f in dated_files("data/press", ".csv").items():
        seen, keep = set(), []
        for r in rows(relp(f)):
            if r["link"] not in seen:
                seen.add(r["link"]); keep.append(r)
        keep.sort(key=lambda r: (r["published_utc"], r["link"]), reverse=True)   # newest first...
        keep.sort(key=lambda r: not is_watch_press(r))                           # ...watchlist/position hits on top
        if keep:   # a header-only CSV (no hits yet today) isn't an input
            out[d] = keep
    return out


def is_watch_press(r):
    return not r["matched_on"].startswith("keyword:")


def manual_calls():
    return [dict(r, found=dt.date.fromisoformat(r["found"]), direction=int(r["direction"] or 0))
            for r in rows("ledger/manual_calls.csv")]


def trades():
    out = []
    for r in rows("journal/trades.csv"):
        if not r.get("symbol") or not r.get("entry"):
            continue
        out.append(dict(r, entry_date=dt.date.fromisoformat(r["entry_date"]), entry=float(r["entry"]),
                        quantity=float(r["quantity"] or 0), fees=float(r["fees_total"] or 0),
                        exit_date=dt.date.fromisoformat(r["exit_date"]) if r.get("exit_date") else None,
                        exit=num(r.get("exit")), sign=-1 if r.get("direction", "").upper() == "SHORT" else 1))
    return out


def watchlist():
    p = ROOT / "watch/watchlist.json"
    return json.loads(p.read_text(encoding="utf-8")).get("tickers", []) if p.exists() else []


def context():
    p = ROOT / "watch/context/latest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def calendar_events():
    p = ROOT / "calendar/catalyst-dates.ics"
    ics = p.read_text(encoding="utf-8") if p.exists() else ""
    ics = re.sub(r"\r?\n[ \t]", "", ics)   # unfold continuation lines
    out = []
    for ev in ics.split("BEGIN:VEVENT")[1:]:
        s = re.search(r"^SUMMARY:(.*)$", ev, re.M); d = re.search(r"^DTSTART[^:]*:(\d{8})", ev, re.M)
        desc = re.search(r"^DESCRIPTION:(.*)$", ev, re.M)
        if s and d:
            unesc = lambda x: x.replace("\\,", ",").replace("\\;", ";").replace("\\n", " ").strip()
            summary = re.sub(r"^[^\w$£(]+", "", unesc(s.group(1)))   # drop the leading emoji
            out.append({"date": dt.datetime.strptime(d.group(1), "%Y%m%d").date(), "summary": summary,
                        "description": unesc(desc.group(1)) if desc else ""})
    return sorted(out, key=lambda e: (e["date"], e["summary"]))


def research_files():
    """Dated research notes and posts: [{date, path, title, kind, heads, lines}]."""
    out = []
    files = sorted(list((ROOT / "research").rglob("*.md")) + list((ROOT / "research").rglob("*.html"))
                   + list((ROOT / "posts").glob("*.md")))
    for f in files:
        rp = relp(f)
        m = re.search(r"(\d{4}-\d{2}-\d{2})", rp)
        if not m or "/work/" in rp:
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        if f.suffix == ".html":
            t = re.search(r"<title>(.*?)</title>", raw, re.S | re.I)
            body = re.sub(r"<(style|script)\b.*?</\1>", " ", raw, flags=re.S | re.I)
            heads = [" ".join(html.unescape(re.sub(r"<[^>]+>", "", h)).split())
                     for h in re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", body, re.S | re.I)]
            # block tags end a line; inline tags (<b>, <a>, <span>) don't, so sentences stay whole
            body = re.sub(r"</?(p|div|li|ul|ol|h\d|tr|td|th|table|section|article|header|footer|br|figure|figcaption)\b[^>]*>",
                          "\n", body, flags=re.I)
            lines = [" ".join(l.split()) for l in html.unescape(re.sub(r"<[^>]+>", "", body)).splitlines() if l.strip()]
            title = html.unescape(t.group(1)).strip() if t else f.stem
        else:
            lines = raw.splitlines()
            title = next((l[2:].strip() for l in lines if l.startswith("# ")), f.stem)
            heads = [l.lstrip("#").strip() for l in lines if re.match(r"#{2,4} ", l)]
        out.append({"date": dt.date.fromisoformat(m.group(1)), "path": rp, "title": title,
                    "kind": "post" if rp.startswith("posts/") else "research", "heads": heads, "lines": lines})
    return out


def research_refs(path, research):
    """Research notes that cite a source file (e.g. 'watch/market/2026-10-02.md') -> deep-dive links."""
    return [r for r in research if any(path in l for l in r["lines"])]


# ---------- everything at once ----------
class Sources:
    def __init__(self):
        self.ledger = ledger()
        self.lx = {(r["ticker"], r["category"], r["found"]): r for r in self.ledger}
        self.signals = signals()
        self.dod = dod_days()
        self.market = market_scans()
        self.digests = digests()
        self.triage = triages()
        self.press = press()
        self.manual = manual_calls()
        self.trades = trades()
        self.watchlist = watchlist()
        self.context = context()
        self.events = calendar_events()
        self.research = research_files()
        self.dossiers = sorted(set(self.watchlist) | {r["ticker"] for r in self.manual} | {t["symbol"] for t in self.trades})
        self._mentions = None

    def scan_dates(self):
        return sorted(set(self.dod) | set(self.market) | set(self.digests) | set(self.triage) | set(self.press)
                      | {s["date"] for s in self.signals} | {m["found"] for m in self.manual})

    def market_items(self, d):
        """[(section, item)] for a date."""
        mk = self.market.get(d)
        return [(s, it) for s in mk["sections"] for it in s["items"]] if mk else []

    def counts(self, d):
        """What a day's scan holds, for headlines, the scans index and the periodic reports."""
        dg = self.digests.get(d, {"filings": []})
        pr = self.press.get(d, [])
        tr = self.triage.get(d)
        mk = Counter(it["category"] for _, it in self.market_items(d))
        ms = [m for m in self.manual if m["found"] == d]
        return {"dod": d in self.dod, "awards": self.dod.get(d, {}).get("awards", 0),
                "signals": sum(s["date"] == d for s in self.signals),
                "digest": d in self.digests, "filings": sum(not f["old"] for f in dg["filings"]),
                "filings_old": sum(f["old"] for f in dg["filings"]),
                "market_scan": d in self.market, "market": sum(mk.values()), "market_by_cat": mk,
                "press_watch": sum(is_watch_press(r) for r in pr), "press_kw": sum(not is_watch_press(r) for r in pr),
                "setups": len(ms), "setups_by_cat": Counter(m["category"] for m in ms),
                "triage": tr is not None, "worth": len(tr["worth"]) if tr else 0, "dismissed": len(tr["dismissed"]) if tr else 0}

    # ----- every dated mention of a dossier ticker -----
    def mentions(self):
        """{ticker: [mention]}; mention = {date, kind, text (markdown, no links), links [(label, target)], scan}.
        `scan` is the section anchor in scans/<date>.md that holds the item, if any."""
        if self._mentions is not None:
            return self._mentions
        T = set(self.dossiers)
        out = {t: [] for t in T}

        def add(t, d, kind, text, links=(), scan=None):
            if t in T:
                out[t].append({"date": d, "kind": kind, "text": text, "links": list(links), "scan": scan})

        for s in self.signals:
            mat = num(s["materiality"])
            ub = " (upper bound)" if "upper_bound" in s.get("notes", "") else ""
            add(s["ticker"], s["date"], "s1",
                f"S1 signal: DoD `{s['award_type']}` {usd(num(s['value_usd']))}"
                + (f", {mat * 100:.0f}% of market cap{ub}" if mat is not None else "") + f", decision {s['decision']}",
                [("war.gov", s["source_url"])] if s.get("source_url") else [], "s1")
        for d, mk in self.market.items():
            for sec, it in ((s, i) for s in mk["sections"] for i in s["items"]):
                for t in set(it["tickers"].split("/")):
                    lr = self.lx.get((it["ticker"], it["ledger_category"], d)) if t == it["ticker"] else None
                    move = f" (5d before {pct(lr['pre_move_5d'])}, found day {pct(lr['found_day_move'])})" if lr and lr["pre_move_5d"] is not None else ""
                    what = (f"8-K trigger phrase \"{plain(it['what'])}\" ({label(it['category']).replace('8-K ', '')})"
                            if it["form"] == "8-K" else f"{label(it['category'])} (`{it['form']}`)")
                    add(t, d, "market", f"Market scan: {what}{move}",
                        [("filing", u) for u in it["links"][:1]], "market")
        for d, dg in self.digests.items():
            by = {}
            for f in dg["filings"]:
                by.setdefault(f["ticker"], []).append(f)
            for t, fs in by.items():
                new = [f for f in fs if not f["old"]]
                old = [f for f in fs if f["old"]]
                same = Counter((f["form"], f["filed"]) for f in new)
                parts = [f"`{form}`{f' ×{n}' if n > 1 else ''} {filed.day} {filed:%b}" for (form, filed), n in same.items()]
                text = "Filings: " + (", ".join(parts) if parts else "")
                if old:
                    span = f"{min(f['filed'] for f in old):%b} – {max(f['filed'] for f in old):%b %Y}"
                    text += ("; " if parts else "") + f"+{len(old)} older ({span}) first picked up"
                add(t, d, "filings", text, [], "filings")
        for d, tr in self.triage.items():
            for kind, items in (("triage", tr["worth"]), ("dismissed", tr["dismissed"])):
                for b in items:
                    for t in T:
                        if word_rx(t).search(b["lead"]):
                            add(t, d, kind, ("Triage: " if kind == "triage" else "Triage, dismissed: ") + triage_summary(b, 150),
                                [("triage", tr["path"])], kind)
        for d, rs in self.press.items():
            for r in rs:
                for t in set(r["ticker"].split(";")):
                    pub = r["published_utc"][:10]
                    when = f", published {day(dt.date.fromisoformat(pub))}" if pub and pub != d.isoformat() else ""
                    add(t, d, "press", f"Press: {clip(r['title'], 110)} ({r['wire']}{when})", [("release", r["link"])], "press")
        for m in self.manual:
            add(m["ticker"], m["found"], "setup",
                f"Logged as `{m['category']}` (direction {sgn(m['direction'])}): {m['note']}; source: {m['source']}",
                [("manual_calls.csv", "ledger/manual_calls.csv")], "setup")
        for tr in self.trades:
            add(tr["symbol"], tr["entry_date"], "trade",
                f"Trade #{tr['id']} opened: {tr.get('direction', 'LONG')} {tr['quantity']:g} @ ${tr['entry']:.3f} ({tr['strategy']})",
                [("journal", "journal/trades.csv")])
            if tr["exit_date"]:
                add(tr["symbol"], tr["exit_date"], "trade", f"Trade #{tr['id']} closed @ ${tr['exit']:.3f} ({tr.get('exit_reason') or 'no reason logged'})",
                    [("journal", "journal/trades.csv")])
        for e in self.events:
            if e["date"] < TODAY:   # today's and later events are "next dated events", not history
                for t in T:
                    if word_rx(t).search(e["summary"] + " " + e["description"]):
                        add(t, e["date"], "calendar", f"Calendar: {e['summary']}", [("calendar", "calendar/catalyst-dates.ics")])
        for r in self.research:
            text = "\n".join(r["lines"])
            for t in T:
                rx = word_rx(t)
                if not rx.search(text):
                    continue
                head = next((h for h in r["heads"] if rx.search(h)), None)
                line = next((l for l in r["lines"] if rx.search(l) and not l.startswith("# ")), "")
                where = head or ("" if rx.search(r["title"]) else line)   # a title naming the ticker says enough
                where = clip(plain(where.lstrip("#").strip()), 110)
                add(t, r["date"], r["kind"], ("Post: " if r["kind"] == "post" else "Research: ") + f"{r['title']}" + (f" ({where})" if where else ""),
                    [("note", r["path"])])
        for t in out:
            out[t].sort(key=lambda m: (m["date"], KIND_RANK.get(m["kind"], 99), m["text"]))
        self._mentions = out
        return out


def ledger_rows_for(S, ticker):
    return sorted((r for r in S.ledger if r["ticker"] == ticker), key=lambda r: (r["found"], r["category"]))
