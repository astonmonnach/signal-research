"""Scan ALL of the day's SEC filings for catalyst-type events.

Usage:  python watch/scan_market.py [YYYY-MM-DD]
With no date it scans the previous business day AND any business day missed since the last scan
(up to 5), so a skipped research run never leaves a hole (rule 2026-10-10, LESSONS.md).
About 5,000 filings land each business day. This keeps only the ones from
listed companies (those with a ticker) that match the event types we trade,
plus any 8-K using our trigger phrases, and writes
watch/market/YYYY-MM-DD.md. Nothing is judged here; the digest is a
shortlist to read.

After those sections comes the wider scan (added 2026-10-10): new contracts, share sales, insider buys, 13D
amendments, new 13G holders, late filings, red flags, Form D and SEC comment letters. Most of it is limited to
"relevant" companies (watchlist + link graph + kept industries). watch/SCANNER.md explains every section.
"""
import csv
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.resolve().parent
OUT = HERE / "market"
UA = {"User-Agent": "PersonalResearch research@example.com"}

# Form type -> section heading in the digest.
FORMS = {
    "10-12B": "Spin-offs (new Form 10)", "10-12B/A": "Spin-offs (Form 10 amended)",
    "SC TO-T": "Tender offers (third party)", "SC TO-I": "Tender offers (issuer buyback)",
    "SC TO-T/A": "Tender offers (third party)", "SC TO-I/A": "Tender offers (issuer buyback)",
    "DEFM14A": "Merger votes (definitive proxy)", "PREM14A": "Merger votes (preliminary proxy)",
    "SC 13D": "Activists / new 5%+ holders", "SCHEDULE 13D": "Activists / new 5%+ holders",
    "SC 13E3": "Going-private deals", "SCHEDULE 13E-3": "Going-private deals",
    "S-1": "Share registrations by listed companies (possible supply)",
    "EFFECT": "Registrations declared effective (supply can now sell)",
    "424B4": "IPO / offering priced (lock-up clock starts)",
    "25-NSE": "Delistings",
}

# Registration forms whose EFFECT notice does NOT put new shares on the market (rule 2026-10-05; HCTI's POS AM,
# then F-6 ADR facilities, N-2 funds and S-4 merger shares seen in the 23 Sep scan).
NOT_SUPPLY = [("POS", "no new shares"), ("S-8 POS", "no new shares"), ("F-6", "ADR facility"), ("N-2", "closed-end fund"),
              ("N-14", "fund merger"), ("S-4", "merger shares"), ("F-4", "merger shares")]

# 8-K phrases searched market-wide for the day.
# "agreement and plan of merger" added 2026-10-06: CHRW's deal for RXO was only caught by the word "spin-off" (LESSONS.md).
PHRASES = ["agreement and plan of merger", "strategic alternatives", "strategic review", "go-shop", "spin-off",
           "reverse stock split", "special dividend", "lock-up", "tender offer"]

# Foreign companies listed in the US (most small Chinese and Hong Kong names) file 6-Ks, not 8-Ks, and no Form 4s.
# Added 2026-10-10: in the runners study a 6-K on the run day or the evening before was 4.4x more common in runners.
# These are a watch-and-avoid list by default: the D2 test found China/HK followers lost about 3.5% in 5 days.
PHRASES_6K = ["private placement", "registered direct offering", "securities purchase agreement", "share consolidation",
              "strategic cooperation", "merger agreement", "going private", "tender offer"]

# ---- Wider scan (added 2026-10-10). Every section below is explained in watch/SCANNER.md. ----
# "Relevant" companies = the watchlist + every ticker in the link graph (graph/edges.csv) + every stock in an industry
# the domino funnel keeps (research/domino/PREREG_D3.md stage 1, looked up in research/domino/sic_map.csv).
# Noisy sections list only relevant companies and end with a count of the other listed companies left out.
KEEP_SIC = set("3674 3672 3670 3679 3559 3571 3572 3576 3577 3661 3663 3669 3825 3827 "   # chips and computing hardware
               "3620 3621 3690 3443 3585 4911 4931 4924 1623 1731 1600 "                  # power and electrical equipment
               "1311 1381 1389 3533 "                                                     # energy
               "1000 1040 1090 1220 1400 3312 3330 "                                      # mining and metals
               "3721 3760 3812 3480 "                                                     # defence and aerospace
               "7374 7373 "                                                               # compute hosting and systems
               "4412 4400 4213".split())                                                  # freight

CONTRACTS = "New contracts (8-K Item 1.01)"
DILUTION = "Share sales and shelves (dilution)"
INSIDERS = "Insider open-market buys (Form 4, code P)"
ACTIVIST_UPDATES = "Activist updates (13D amendments)"
PASSIVE = "New passive 5%+ holders (13G)"
LATE = "Late filings (cannot file on time)"
RED_FLAGS = "Red flags (avoid list)"
FORM_D = "Private fundraisings (Form D)"
LETTERS = "SEC comment letters"

# Daily-index form type -> wider-scan section. Matched on the exact form type, never a prefix: "D" must not pick up
# "DEF 14A", "DFAN14A" or "DRS", and "S-3" must not pick up "S-3/A".
MORE_FORMS = {
    "424B5": DILUTION, "S-3": DILUTION, "S-3ASR": DILUTION, "F-3": DILUTION, "F-3ASR": DILUTION,
    "SC 13D/A": ACTIVIST_UPDATES, "SCHEDULE 13D/A": ACTIVIST_UPDATES,
    "SC 13G": PASSIVE, "SCHEDULE 13G": PASSIVE,
    "NT 10-K": LATE, "NT 10-Q": LATE,
    "D": FORM_D, "D/A": FORM_D,
    "UPLOAD": LETTERS, "CORRESP": LETTERS,
}

# 8-K Item 1.01 phrases for commercial deals. The bare phrase "purchase agreement" is left out on purpose: over
# 21 Sep to 9 Oct 2026 it hit about 10 Item 1.01 8-Ks a day and they were share sales and acquisitions (securities /
# share / asset purchase agreements). The commercial kinds are covered by "power purchase agreement" and "purchase order".
CONTRACT_PHRASES = ["supply agreement", "offtake agreement", "master services agreement", "collaboration agreement",
                    "license agreement", "strategic partnership", "development agreement", "distribution agreement",
                    "manufacturing agreement", "power purchase agreement", "purchase order", "framework agreement",
                    "joint venture agreement", "colocation agreement", "data center lease", "memorandum of understanding"]
# A phrase only counts when the filing says the agreement was entered into, signed, amended or announced: one of these
# words within 90 characters before the phrase, in the same sentence. A merger 8-K that mentions the target's
# "license agreement" in passing fails this (XMAX, VEEE and HEPA's supply agreement, 8 and 9 Oct 2026).
# Not counted: the Item 1.01 title itself ("Entry into a Material ...") and the name "Amended and Restated ...".
SIGNED = (r"\b(?:entered\s+into|enter(?:ing|s)?\s+into|entry\s+into(?!\s+a\s+material)|executed|(?:counter)?signed|accepted|awarded|received|"
          r"announc\w+|amend(?:ed|ment|ments|ing|s)?(?!\s+and\s+restated)|extend\w*|renew\w*)\b")
# "Distribution agreement" is also what share-sale programmes and spin-offs are called. Those are not contracts.
NOT_A_CONTRACT = r"equity\s+distribution|separation\s+and\s+distribution|spin|offer\s+and\s+sell|issuance\s+and\s+sale|at[- ]the[- ]market"
CHECK_CAP = 60       # most 8-Ks opened in a day to check contract phrases

# 8-K phrases for a share-sale programme. "sales agreement" alone is too loose (gas and power sales agreements), so a
# filing must match one of the first two; "sales agreement" then tells an ATM programme from a one-off priced sale.
ATM_PHRASES = ["at-the-market", "equity distribution agreement", "sales agreement"]

FORM4_CAP = 400      # most Form 4s opened in a day
LATE_LIMIT = 40      # above this many late filings, list relevant companies only
HOLDER_LIMIT = 20    # above this many 13D/A or 13G filings on relevant companies, group them by holder instead of listing
GOING_CONCERN_CAP = 60   # most 10-K / 10-Q / 8-K documents opened in a day to read the going-concern sentence

# Red flags: (label, search query, forms searched, 8-K item the filing must carry or None).
# With no item the phrase must be in the main document: exhibits (acquired companies' accounts, loan agreements,
# share designations) repeat these words as boilerplate (PINE, BWIN, CRGY, NXXT, VREOF on 8 and 9 Oct 2026).
FLAGS = [
    ("going concern", '"substantial doubt"', "8-K,10-K,10-Q", None),   # not "... about": NVVE wrote "substantial doubt exists"
    ("non-reliance on past accounts", '"should no longer be relied upon"', "8-K,10-K,10-Q", None),
    ("bankruptcy petition", '"voluntary petition"', "8-K,10-K,10-Q", None),
    ("auditor change", '"independent registered public accounting firm"', "8-K", "4.01"),
    ("auditor change", '"certifying accountant"', "8-K", "4.01"),   # the title of Item 4.01; catches 8-Ks that say "auditor"
]
# "Substantial doubt" is also how a healthy company says there is none, and how the accounting rule is quoted
# (BYRN's 10-Q, 8 Oct 2026). A mention with one of these just before it, in the same sentence, is not a flag.
NO_DOUBT = (r"\b(?:no|not|if|when|whether|unless)\s+substantial\s+doubt|\bnot\s+(?:raise|give\s+rise|believe|indicate|result|identif\w+)|"
            r"\bno\s+(?:conditions|events)\b|\b(?:if|whether|when|unless)\s+(?:there\s+(?:is|are|was|were)|conditions|events)|"
            r"\balleviat\w+|\bmitigat\w+|\bno\s+longer\b|\b(?:could|may|might|would)\s+(?:also\s+)?(?:raise|result|cast|create|lead|give)")
# A sentence like these says an earlier doubt is over (CREX, NUAI and DFLI, 14 Aug 2026). That is not a flag either.
DOUBT_LIFTED = (r"\b(?:has|have|had)\s+(?:been\s+)?alleviated|\b(?:is|was|were)\s+alleviated|\bno\s+longer\s+exists?\b|"
                r"\balleviates\s+(?:the\s+)?substantial\s+doubt")


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def get(url, limit=None):
    """fetch() for the wider scan: always waits first (stays under 10 requests a second) and can stop after `limit` bytes."""
    time.sleep(0.12)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(limit)


def search(query, day, forms, pages=1):
    """EDGAR full-text search for one day: the hits for `query` in `forms`, 100 a page. The search service throws the
    odd HTTP 500, so each page is tried up to three times; if it still fails the error goes to the caller."""
    out = []
    for page in range(pages):
        q = {"q": query, "dateRange": "custom", "category": "custom", "startdt": f"{day}", "enddt": f"{day}", "forms": forms}
        if page:
            q["from"] = page * 100
        for attempt in (1, 2, 3):
            time.sleep(0.3)
            try:
                res = json.loads(fetch(f"https://efts.sec.gov/LATEST/search-index?{urllib.parse.urlencode(q)}"))["hits"]["hits"]
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2)
        out += res
        if len(res) < 100:
            break
    return out


def plain(url):
    """A filing document as plain text: tags and entities removed, whitespace collapsed."""
    t = get(url).decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|ix:header)\b.*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", t)))


def quote(s, n=200):
    """A short quotation that is safe inside a digest line (no markdown or table characters)."""
    s = re.sub(r"[|`*_\[\]<>]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().replace('"', "'")
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."


def main():
    # Quoted filing text can hold characters a Windows console can't print; never let that stop a catch-up run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if len(sys.argv) > 1:
        return scan(date.fromisoformat(sys.argv[1]))
    target = date.today() - timedelta(days=1)
    while target.weekday() >= 5:                         # the research run is early morning: Monday scans Friday
        target -= timedelta(days=1)
    # Catch up: every business day after the last scan file, up to the target (rule 2026-10-10).
    done = sorted(date.fromisoformat(f.stem) for f in OUT.glob("20??-??-??.md")) if OUT.exists() else []
    days, d = [], (done[-1] if done else target - timedelta(days=1)) + timedelta(days=1)
    while d <= target:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    for day in (days or [target])[-5:]:
        scan(day)


def scan(day):
    qtr = (day.month - 1) // 3 + 1
    try:
        idx = fetch(f"https://www.sec.gov/Archives/edgar/daily-index/{day.year}/QTR{qtr}/"
                    f"form.{day:%Y%m%d}.idx").decode("latin-1")
    except Exception as e:
        print(f"No daily index for {day} (weekend, holiday, or not posted yet): {e}")
        return

    tickers = defaultdict(list)
    for v in json.loads(fetch("https://www.sec.gov/files/company_tickers.json")).values():
        tickers[v["cik_str"]].append(v["ticker"])

    relevant, unread = load_relevant(tickers)
    more = defaultdict(dict)   # wider scan: section -> {accession number: [(cik, name, form, path, date filed), ...]}
    form4 = {}                 # accession number -> index path, for Form 4s listed under a relevant company

    total, hits = 0, defaultdict(list)
    for line in idx.splitlines():
        if not line[:1].strip() or line.startswith(("Form Type", "---", "Description", "Last Data",
                                                     "Comments", "Anonymous")):
            continue
        parts = line.split()
        if len(parts) < 5 or not parts[-2].isdigit():
            continue
        total += 1
        path, cik = parts[-1], int(parts[-3])
        # Wider scan. The exact form type is the leading text up to the first run of two or more spaces (the index
        # is fixed-width), so "D" is only ever Form D. A filing is listed once under each party's CIK (a Form 4
        # under the insider and the issuer, a 13D under the holder and the company): group the rows by accession number.
        exact = re.match(r"\S+(?: \S+)*", line).group(0)
        acc = path.rsplit("/", 1)[-1].replace(".txt", "")
        if exact == "4" and cik in relevant:
            form4.setdefault(acc, path)
        elif exact in MORE_FORMS:
            more[MORE_FORMS[exact]].setdefault(acc, []).append(
                (cik, " ".join(parts[len(exact.split()):-3]), exact, path, parts[-2]))
        # Form types can contain spaces ("SC 13D"), so match on the leading text.
        form = next((f for f in sorted(FORMS, key=len, reverse=True) if line.startswith(f + " ")), None)
        if form is None or cik not in tickers:
            continue
        name = " ".join(parts[len(form.split()):-3])
        note = ""
        if form == "EFFECT":
            # Rule 2026-10-05 (HCTI): an EFFECT for a post-effective amendment registers no new shares, so it isn't supply.
            # The notice names the form it makes effective.
            try:
                time.sleep(0.12)
                xml = fetch("https://www.sec.gov/Archives/" + path.replace("-", "").replace(".txt", "/primary_doc.xml")).decode("utf-8", "ignore")
                reg = re.search(r"<form>([^<]+)</form>", xml)
                if reg:
                    reg = reg.group(1).strip()
                    why = next((w for f, w in NOT_SUPPLY if reg.upper().startswith(f)), "")
                    note = f" registers {reg}" + (f" (not supply: {why})" if why else "")
            except Exception:
                note = " registers ?"
        elif form == "SC TO-I":
            # Rule 2026-10-10 (MDT/MiniMed): a new issuer tender or exchange offer has a hard expiry and often an
            # odd-lot rule that favours small holders. Read it the day it is filed.
            note = " **READ TODAY: new issuer tender / exchange offer. Log the expiry, the price or ratio, and any odd-lot terms**"
        hits[FORMS[form]].append(
            f"- **{'/'.join(tickers[cik])}** {name} `{form}`{note} "
            f"[filing index]({index_url(path)})")

    by_filing, by_6k = {}, {}
    for form_type, p in [("8-K", x) for x in PHRASES] + [("6-K", x) for x in PHRASES_6K]:
        store = by_filing if form_type == "8-K" else by_6k
        try:
            res = search(f'"{p}"', day, form_type)   # same query as before, now retried when the service hiccups
        except Exception as e:
            store[f"err-{p}"] = [f"_search for \"{p}\" failed: {e}_"]
            continue
        for h in res:
            s = h["_source"]
            ciks = [int(c) for c in s.get("ciks", [])]
            # Indentures and contracts (EX-4, EX-10) repeat these phrases as boilerplate.
            if not any(c in tickers for c in ciks) or s.get("file_type", "").startswith(("EX-4", "EX-10")):
                continue
            acc, fname = h["_id"].split(":")
            url = f"https://www.sec.gov/Archives/edgar/data/{ciks[0]}/{acc.replace('-', '')}/{fname}"
            tk = "/".join(t for c in ciks for t in tickers.get(c, []))
            items = s.get("items", []) or []
            entry = store.setdefault(acc, [tk, url, [], items])
            # A director/officer 8-K (Item 5.02) without a business item (8.01/1.01/2.01) that
            # mentions "strategic alternatives" is almost always a bio line (e.g. LWLG 29 Sep 2026).
            label = p
            if p.startswith("strategic") and "5.02" in items and not {"8.01", "1.01", "2.01"} & set(items):
                label = f"bio-mention ({p})"
            # Rule 2026-10-05 (CHDN, 28 Sep): in a debt financing 8-K (Item 2.03, no 8.01/2.01) the phrase is
            # forward-looking boilerplate, not a sale review.
            elif p.startswith("strategic") and "2.03" in items and not {"8.01", "2.01"} & set(items):
                label = f"financing-mention ({p})"
            if label not in entry[2]:
                entry[2].append(label)
    phrase_hits = [f"- {v[0]}" if k.startswith("err-") else
                   f"- **{v[0]}** {', '.join(v[2])} [8-K]({v[1]}) items {','.join(v[3]) or '?'}"
                   for k, v in by_filing.items()]

    hits_6k = [f"- {v[0]}" if k.startswith("err-") else f"- **{v[0]}** {', '.join(v[2])} [6-K]({v[1]})"
               for k, v in by_6k.items()]

    # Wider scan: each builder returns the section's lines, or nothing when it has no hits (the section is then left out).
    # A builder that breaks costs its own section one line, never the scan.
    wider = {}
    for heading, build in [
            (CONTRACTS, lambda: contracts(day, tickers, relevant)),
            (DILUTION, lambda: dilution(day, more[DILUTION], tickers, relevant)),
            (INSIDERS, lambda: insider_buys(form4, tickers, relevant)),
            (ACTIVIST_UPDATES, lambda: holders(more[ACTIVIST_UPDATES], tickers, relevant)),
            (PASSIVE, lambda: holders(more[PASSIVE], tickers, relevant)),
            (LATE, lambda: late_filings(more[LATE], tickers, relevant)),
            (RED_FLAGS, lambda: red_flags(day, tickers, relevant)),
            (FORM_D, lambda: form_d(more[FORM_D], tickers, relevant)),
            (LETTERS, lambda: letters(more[LETTERS], tickers, relevant))]:
        try:
            wider[heading] = build()
        except Exception as e:
            wider[heading] = [f"- _this section failed: {e}_"]

    n = sum(len(v) for v in hits.values()) + len(phrase_hits) + len(hits_6k)
    lines = [f"# Market-wide filings scan {day}", "",
             f"{total:,} filings filed. {n} from listed companies match our event types.", ""]
    if any(wider.values()):
        first = next(h for h, body in wider.items() if body)
        lines += [f"Wider scan: {sum(len(v) for v in wider.values())} more lines in the sections from \"{first}\" down. "
                  f"\"Relevant\" there means one of {len(relevant):,} listed companies on the watchlist, in the link graph or "
                  f"in a kept industry" + (f" (could not read {', '.join(unread)})" if unread else "")
                  + ". Guide to every section: watch/SCANNER.md.", ""]
    for section in dict.fromkeys(FORMS.values()):
        if hits.get(section):
            lines += [f"## {section}", *hits[section], ""]
    if phrase_hits:
        lines += ["## 8-Ks with trigger phrases", *phrase_hits, ""]
    if hits_6k:
        lines += ["## 6-Ks with trigger phrases (foreign companies: watch and avoid by default)", *hits_6k, ""]
    for heading, body in wider.items():
        if body:
            lines += [f"## {heading}", *body, ""]
    OUT.mkdir(exist_ok=True)
    (OUT / f"{day}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


# ---------------------------------------------------------------------------------------------------------------------
# Wider scan: one function per section. Each returns digest lines in the usual shape
#   - **TICKER** what it is `FORM` [link](url)
# so reports/sources.py reads them like the older sections. An empty list means the section is left out.
# ---------------------------------------------------------------------------------------------------------------------

def load_relevant(tickers):
    """CIKs of the listed companies the noisy sections are limited to (watchlist + link graph + kept industries),
    and the names of any input file that could not be read."""
    by_ticker = {t.upper(): c for c, ts in tickers.items() for t in ts}
    names, ciks, unread = set(), set(), []
    try:
        names |= {t.strip().upper() for t in json.loads((HERE / "watchlist.json").read_text(encoding="utf-8"))["tickers"]}
    except Exception:
        unread.append("watch/watchlist.json")
    try:
        with open(ROOT / "graph" / "edges.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                names |= {x.strip().upper() for x in (r.get("a") or "", r.get("b") or "") if x.strip() and ":" not in x}
    except Exception:
        unread.append("graph/edges.csv")
    try:
        with open(ROOT / "research" / "domino" / "sic_map.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("sic") or "").strip() in KEEP_SIC:
                    # By CIK, because tickers get reused (BRKH is now a different shell). By ticker only when that CIK
                    # has left the SEC's ticker file, which is what a company moving to a new CIK looks like (VNOM, XPRO).
                    if int(r["cik"]) in tickers:
                        ciks.add(int(r["cik"]))
                    else:
                        names.add(r["ticker"].strip().upper())
    except Exception:
        unread.append("research/domino/sic_map.csv")
    ciks |= {by_ticker[t] for t in names if t in by_ticker}
    return {c for c in ciks if c in tickers}, unread


def symbols(ciks, tickers):
    return "/".join(t for c in ciks for t in tickers.get(c, []))


def index_url(path):
    """The filing's index page, in the long form .../data/CIK/ACCESSIONNODASHES/ACCESSION-index.htm.
    The short form (.../data/CIK/ACCESSION-index.htm) answered "Access Denied" (HTTP 403) on 10 Oct 2026."""
    folder, name = path.rsplit("/", 1)
    acc = name.replace(".txt", "")
    return f"https://www.sec.gov/Archives/{folder}/{acc.replace('-', '')}/{acc}-index.htm"


def doc_url(ciks, acc, fname):
    return f"https://www.sec.gov/Archives/edgar/data/{ciks[0]}/{acc.replace('-', '')}/{fname}"


def left_out(ciks):
    n = len(ciks)
    return [f"- _{n} other listed compan{'y' if n == 1 else 'ies'} left out (not on the watchlist, in the graph or in a kept industry)._"] if n else []


def pick(filings, tickers, relevant, everyone=False):
    """Sort one index-driven section into the filings to list and the companies left out.
    filings = {accession number: [(cik, name, form, path, date filed), ...]}, one row per party to the filing.
    Returns ([(is relevant, row)] with relevant companies first, {CIKs of other listed companies})."""
    shown, left = [], set()
    for rows in filings.values():
        listed = [r for r in rows if r[0] in tickers]
        rel = [r for r in listed if r[0] in relevant]
        if rel or (everyone and listed):
            shown.append((bool(rel), (rel or listed)[0]))
        elif listed:
            left.add(listed[0][0])
    return sorted(shown, key=lambda x: not x[0]), left - {row[0] for _, row in shown}


def parse_hit(h, tickers):
    """(accession number, file name, ciks, 8-K items, document type, form) for one full-text-search hit,
    or None when no listed company is behind the filing."""
    s = h["_source"]
    ciks = [int(c) for c in s.get("ciks", [])]
    if not any(c in tickers for c in ciks):
        return None
    acc, fname = h["_id"].split(":")
    return acc, fname, ciks, s.get("items") or [], s.get("file_type") or "", s.get("form") or ""


def announced(text, phrases):
    """(phrase, the words around it) if the text says one of these agreements was entered into, signed, amended or
    announced; None if they are only mentioned in passing. Reads from Item 1.01 on when the text has one."""
    start = re.search(r"Item\s*1\.01", text, re.I)
    body = text[start.start():] if start else text
    for p in phrases:
        for m in re.finditer(r"\s+".join(map(re.escape, p.split())), body, re.I):
            before = body[max(0, m.start() - 90):m.start()]
            verbs = list(re.finditer(SIGNED, before, re.I))
            if not verbs or re.search(r"\.\s+[A-Z]|\.\s*$", before[verbs[-1].end():]):
                continue   # no signing word, or it belongs to an earlier sentence (or the phrase is only a heading)
            if p == "distribution agreement" and re.search(NOT_A_CONTRACT, body[max(0, m.start() - 40):m.end() + 200], re.I):
                continue
            return p, body[m.start() - len(before) + verbs[-1].start():m.end() + 110]
    return None


def contracts(day, tickers, relevant):
    """8-Ks with Item 1.01 (a new material agreement) that say a commercial agreement was signed. All listed companies."""
    found, notes = {}, []
    for p in CONTRACT_PHRASES:
        try:
            res = search(f'"{p}"', day, "8-K", pages=3)
        except Exception as e:
            notes.append(f"- _search for \"{p}\" failed: {e}_")
            continue
        for h in res:
            hit = parse_hit(h, tickers)
            # With Item 2.03 the agreement is a loan. With Item 2.01 a takeover has closed and the 8-K describes the
            # target's old contracts as if new (HEPA, 9 Oct 2026: a licence "entered into" in 2023). Only the 8-K itself
            # and its press release (EX-99) count: merger agreements, underwriting agreements and loan documents
            # (EX-2, EX-1, EX-4, EX-10) list these phrases as boilerplate.
            if (not hit or "1.01" not in hit[3] or {"2.01", "2.03"} & set(hit[3])
                    or not hit[4].startswith(("8-K", "EX-99"))):
                continue
            acc, fname, ciks, items, kind, _ = hit
            e = found.setdefault(acc, {"ciks": ciks, "items": items, "docs": {}})
            e["docs"].setdefault(fname, (kind, []))[1].append(p)
    shown, passing = [], 0
    for n, (acc, e) in enumerate(found.items()):
        docs = sorted(e["docs"].items(), key=lambda d: not d[1][0].startswith("8-K"))   # the 8-K itself first, then the press release
        said, at, opened = None, docs[0][0], n < CHECK_CAP
        if opened:
            try:
                for fname, (_, phrases) in docs:
                    said = announced(plain(doc_url(e["ciks"], acc, fname)), phrases)
                    if said:
                        at = fname
                        break
            except Exception:
                opened = False
        if opened and not said:
            passing += 1
            continue
        what = (f'{said[0]}: "{quote(said[1])}"' if said else
                ", ".join(dict.fromkeys(p for _, (_, ps) in docs for p in ps)) + " (filing not opened to check)")
        rel = any(c in relevant for c in e["ciks"])
        shown.append((not rel, f"- **{symbols(e['ciks'], tickers)}** {'(relevant) ' if rel else ''}{what} `8-K` "
                               f"items {','.join(e['items'])} [8-K]({doc_url(e['ciks'], acc, at)})"))
    lines = [line for _, line in sorted(shown, key=lambda x: x[0])]
    if lines and passing:
        lines.append(f"- _{passing} other Item 1.01 8-K{'' if passing == 1 else 's'} only mention these agreement types in passing (not listed)._")
    return lines + notes


def dilution(day, filings, tickers, relevant):
    """Prospectus supplements and shelf registrations from the index, plus 8-Ks that start a share-sale programme.
    Relevant companies only. A 424B5 can also be a debt offering: nothing here is classified, only listed."""
    shown, left = pick(filings, tickers, relevant)
    lines = [f"- **{symbols([r[0]], tickers)}** {r[1]} `{r[2]}` [filing index]({index_url(r[3])})" for _, r in shown]
    found, notes = {}, []
    for p in ATM_PHRASES:
        try:
            res = search(f'"{p}"', day, "8-K", pages=3)
        except Exception as e:
            notes.append(f"- _search for \"{p}\" failed: {e}_")
            continue
        for h in res:
            hit = parse_hit(h, tickers)
            # Item 1.01 = a new agreement. Only the 8-K itself or its press release counts: underwriting agreements,
            # legal opinions and loan documents repeat these words about older programmes (PCVX, UUU on 9 Oct 2026).
            if not hit or "1.01" not in hit[3] or not hit[4].startswith(("8-K", "EX-99")):
                continue
            acc, fname, ciks, items, kind, _ = hit
            e = found.setdefault(acc, {"ciks": ciks, "items": items, "phrases": [], "doc": fname})
            if p not in e["phrases"]:
                e["phrases"].append(p)
            if kind.startswith("8-K"):
                e["doc"] = fname
    for acc, e in found.items():
        if not {"at-the-market", "equity distribution agreement"} & set(e["phrases"]):
            continue
        if any(c in relevant for c in e["ciks"]):
            lines.append(f"- **{symbols(e['ciks'], tickers)}** {', '.join(e['phrases'])} `8-K` items {','.join(e['items'])} "
                         f"[8-K]({doc_url(e['ciks'], acc, e['doc'])})")
        else:
            left.add(next(c for c in e["ciks"] if c in tickers))
    left -= {r[0] for _, r in shown}
    return (lines + left_out(left) if lines else []) + notes


def insider_buys(form4, tickers, relevant):
    """Form 4s filed for relevant companies: open-market or private purchases (code P) of ordinary shares only.
    Grants, option exercises, tax withholding, gifts and sales are ignored."""
    def yes(x):
        return (x or "").strip().lower() in ("1", "true")

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    buys, people, failed = [], defaultdict(set), 0
    for acc, path in list(form4.items())[:FORM4_CAP]:
        try:   # the ownership XML sits inside the filing's text file, between <XML> tags
            text = get("https://www.sec.gov/Archives/" + path).decode("utf-8", "ignore")
            doc = ET.fromstring(re.search(r"<XML>\s*(.*?)\s*</XML>", text, re.S).group(1))
        except Exception:
            failed += 1
            continue
        issuer = int(doc.findtext("issuer/issuerCik") or 0)
        if issuer not in relevant:
            continue   # the index row was a relevant company acting as the insider of some other issuer
        shares = priced = value = 0.0
        last = ""
        for t in doc.findall("nonDerivativeTable/nonDerivativeTransaction"):
            n = num(t.findtext("transactionAmounts/transactionShares/value"))
            if (t.findtext("transactionCoding/transactionCode") or "").strip() != "P" or not n:
                continue
            price = num(t.findtext("transactionAmounts/transactionPricePerShare/value"))
            shares += n
            if price:
                priced += n
                value += n * price
            last = max(last, (t.findtext("transactionDate/value") or "").strip()[:10])
        if not shares:
            continue
        who = []
        for o in doc.findall("reportingOwner"):
            r = o.find("reportingOwnerRelationship")
            roles = []
            if r is not None:
                if yes(r.findtext("isDirector")):
                    roles.append("director")
                if yes(r.findtext("isOfficer")):
                    roles.append((r.findtext("officerTitle") or "").strip() or "officer")
                if yes(r.findtext("isTenPercentOwner")):
                    roles.append("10% owner")
                if yes(r.findtext("isOther")):
                    roles.append((r.findtext("otherText") or "").strip() or "other")
            who.append(quote(o.findtext("reportingOwnerId/rptOwnerName") or "?", 60) + (f" ({quote(', '.join(roles), 80)})" if roles else ""))
        first = doc.find("reportingOwner")
        people[issuer].add((first.findtext("reportingOwnerId/rptOwnerCik") or who[0]).strip() if first is not None else acc)
        avg = value / priced if priced else None
        cost = "with no price in the form (usually a private deal, not a market buy: read the footnotes)"   # NFE, 15 Sep 2026
        if avg:
            cost = (f"at ${avg:,.2f}" if avg >= 1 else f"at ${avg:,.4f}") + f" = ${value:,.0f}" + (" (part of it unpriced)" if priced < shares else "")
        buys.append((-value, f"- **{symbols([issuer], tickers)}** {' + '.join(who[:3])}{f' + {len(who) - 3} more' if len(who) > 3 else ''} "
                             f"bought {shares:,.0f} shares {cost}{f' on {last}' if last else ''} `4` [Form 4]({index_url(path)})"))
    lines = [line for _, line in sorted(buys)]
    if lines:
        clusters = [f"{symbols([c], tickers)} ({len(p)} insiders)" for c, p in people.items() if len(p) > 1]
        lines.append("- Clusters: " + (", ".join(clusters) if clusters else "none"))
    if len(form4) > FORM4_CAP:
        lines.append(f"- _Form 4 cap hit: opened {FORM4_CAP} of the {len(form4)} filed for relevant companies; the rest were not read._")
    if failed:
        lines.append(f"- _{failed} Form 4{'' if failed == 1 else 's'} could not be opened._")
    return lines


def holders(filings, tickers, relevant):
    """13D amendments and new 13Gs where the company held is relevant, with who filed.
    The index lists each of these under the company AND under the holder; the filing's header says which is which."""
    lines, left, todo = [], set(), []
    for rows in filings.values():
        listed = [r for r in rows if r[0] in tickers]
        if any(r[0] in relevant for r in listed):
            todo.append((rows, listed))
        else:
            left |= {r[0] for r in listed[:1]}
    if len(todo) > HOLDER_LIMIT:
        # A quarterly 13G deadline (mid February, May, August, November) brings dozens: 75 on 14 Aug 2026. Group them by
        # who filed, from the index alone: the relevant company is taken as the one held, the other name as the holder.
        by = defaultdict(list)
        for rows, listed in todo:
            held = next(r[0] for r in listed if r[0] in relevant)
            for name in dict.fromkeys(r[1] for r in rows if r[0] != held) or ["holder not in the index"]:
                if symbols([held], tickers) not in by[name]:
                    by[name].append(symbols([held], tickers))
        lines = [f"- _{len(todo)} filings on relevant companies, too many to list one by one (quarterly deadlines do this). "
                 "Grouped by who filed, from the index alone:_"]
        lines += [f"- _{quote(name, 80)}: {', '.join(held)}_" for name, held in sorted(by.items(), key=lambda kv: -len(kv[1])) if len(held) > 1]
        singles = [f"{held[0]} ({quote(name, 60)})" for name, held in by.items() if len(held) == 1]
        if singles:
            lines.append(f"- _One each: {'; '.join(singles)}_")
        return lines + left_out(left)
    for rows, listed in todo:
        subject, filers, note = None, [], ""
        try:
            head = get("https://www.sec.gov/Archives/" + rows[0][3], 40000).decode("latin-1").split("</SEC-HEADER>")[0]
            subject = int(re.search(r"SUBJECT COMPANY:.*?CENTRAL INDEX KEY:\s*(\d+)", head, re.S).group(1))
            filers = [x.strip() for x in re.findall(r"FILED BY:.*?COMPANY CONFORMED NAME:\s*([^\r\n]+)", head, re.S)]
        except Exception:
            subject = None
        if subject is None:   # header not read: take the relevant company as the one held, as the older sections do
            subject = next(r[0] for r in listed if r[0] in relevant)
            filers, note = [r[1] for r in rows if r[0] != subject], " (header not read: roles assumed)"
        row = next((r for r in rows if r[0] == subject), None)
        if row is None or subject not in relevant:
            if subject in tickers:
                left.add(subject)
            continue
        by = f", filed by {quote('; '.join(dict.fromkeys(filers)), 120)}" if filers else ""
        lines.append(f"- **{symbols([subject], tickers)}** {row[1]}{by}{note} `{row[2]}` [filing index]({index_url(row[3])})")
    return lines + left_out(left) if lines else []


def late_filings(filings, tickers, relevant):
    """NT 10-K / NT 10-Q: the company says it cannot file its accounts on time. All listed companies, unless there are too many."""
    shown, left = pick(filings, tickers, relevant, everyone=True)
    if len(shown) > LATE_LIMIT:
        shown, left = pick(filings, tickers, relevant)
    lines = [f"- **{symbols([r[0]], tickers)}** {'(relevant) ' if rel else ''}{r[1]} `{r[2]}` [filing index]({index_url(r[3])})"
             for rel, r in shown]
    return lines + left_out(left) if lines else []


def form_d(filings, tickers, relevant):
    """Form D: a listed company sold securities privately. Relevant companies only, with the amounts the form gives."""
    def money(x):
        return f"${int(x):,}" if x.isdigit() else x

    shown, left = pick(filings, tickers, relevant)
    lines = []
    for _, (cik, name, form, path, _) in shown:
        note = ""
        try:
            xml = get("https://www.sec.gov/Archives/" + path.replace("-", "").replace(".txt", "/primary_doc.xml")).decode("utf-8", "ignore")
            size, sold = (re.search(rf"<{tag}>\s*([^<]+?)\s*</{tag}>", xml) for tag in ("totalOfferingAmount", "totalAmountSold"))
            if size and sold:
                note = f": sold {money(sold.group(1))} of {money(size.group(1))}"
        except Exception:
            pass
        lines.append(f"- **{symbols([cik], tickers)}** {name}{note} `{form}` [filing index]({index_url(path)})")
    return lines + left_out(left) if lines else []


def letters(filings, tickers, relevant):
    """UPLOAD = a letter from SEC staff, CORRESP = the company's reply. They are made public weeks after they are
    written, so the line gives the letter's own date. Relevant companies only."""
    kinds = {"UPLOAD": "SEC staff letter", "CORRESP": "company reply"}
    shown, left = pick(filings, tickers, relevant)
    lines = [f"- **{symbols([r[0]], tickers)}** {r[1]}: {kinds.get(r[2], r[2])} dated {r[4][:4]}-{r[4][4:6]}-{r[4][6:]} "
             f"`{r[2]}` [filing index]({index_url(r[3])})" for _, r in sorted(shown, key=lambda x: (x[1][1], x[1][4]))]
    return lines + left_out(left) if lines else []


def going_concern(text):
    """How a document uses the words "substantial doubt":
    ("stated", the sentence) when it says the doubt exists; ("lifted", "") when it says an earlier doubt is over;
    ("none", "") when every mention is a denial, a what-if or the accounting rule being quoted."""
    stated = None
    for m in re.finditer(r"substantial\s+doubt", text, re.I):
        before = re.split(r"\.\s+(?=[A-Z])", text[max(0, m.start() - 220):m.start()])[-1]
        after = re.split(r"\.\s+(?=[A-Z])", text[m.end():m.end() + 200])[0]
        if re.search(DOUBT_LIFTED, before + m.group(0) + after, re.I):
            return "lifted", ""
        if stated is None and not re.search(NO_DOUBT, before + "substantial doubt", re.I):
            lead = before if len(before) <= 110 else "..." + before[-110:].split(" ", 1)[-1]
            stated = lead + m.group(0) + after[:130]
    return ("stated", stated) if stated else ("none", "")


def red_flags(day, tickers, relevant):
    """Going-concern doubt, withdrawn accounts, bankruptcy petitions and auditor changes. Relevant companies only."""
    found, notes = {}, []
    for label, query, forms, item in FLAGS:
        try:
            res = search(query, day, forms, pages=10)
        except Exception as e:
            notes.append(f"- _search for {query} ({label}) failed: {e}_")
            continue
        for h in res:
            hit = parse_hit(h, tickers)
            if not hit or ((item not in hit[3]) if item else hit[4].startswith("EX-")):
                continue
            acc, fname, ciks, items, kind, form = hit
            e = found.setdefault(acc, {"ciks": ciks, "items": items, "form": form or kind, "flags": {}, "doc": None})
            e["flags"].setdefault(label, fname)
            if not kind.startswith("EX-"):
                e["doc"] = fname
    lines, others, lifted, denied, read = [], defaultdict(set), [], [], 0
    for acc, e in found.items():
        if not any(c in relevant for c in e["ciks"]):
            for label in e["flags"]:
                others[label].add(next(c for c in e["ciks"] if c in tickers))
            continue
        said = []
        for label, fname in e["flags"].items():
            if label == "going concern":
                # Open the document and read the sentences: most mentions in a healthy company's 10-Q are denials.
                verdict, doubt = "unread", ""
                if read < GOING_CONCERN_CAP:
                    read += 1
                    try:
                        verdict, doubt = going_concern(plain(doc_url(e["ciks"], acc, fname)))
                    except Exception:
                        pass
                if verdict in ("lifted", "none"):
                    (lifted if verdict == "lifted" else denied).append(symbols(e["ciks"], tickers))
                    continue
                said.append(f'going concern: "{quote(doubt, 270)}"' if doubt else "going concern (words found, sentences not read)")
            elif label == "bankruptcy petition":
                said.append("bankruptcy petition (Item 1.03)" if "1.03" in e["items"] else
                            "mentions a bankruptcy petition (can be history or another party)")
            elif label == "auditor change":
                said.append("auditor change (Item 4.01)")
            else:
                said.append(label + (" (Item 4.02)" if "4.02" in e["items"] else ""))
        if not said:
            continue
        url = doc_url(e["ciks"], acc, e["doc"]) if e["doc"] else doc_url(e["ciks"], acc, f"{acc}-index.htm")
        lines.append(f"- **{symbols(e['ciks'], tickers)}** {'; '.join(said)} `{e['form']}`"
                     + (f" items {','.join(e['items'])}" if e["items"] else "") + f" [{e['form']}]({url})")
    if lines and others:
        lines.append("- _Other listed companies left out (not relevant, sentences not read): "
                     + ", ".join(f"{label} {len(c)}" for label, c in others.items()) + "._")
    if lines and (lifted or denied):
        why = [", ".join(dict.fromkeys(names)) + f" ({reason})" for names, reason in
               ((lifted, "an earlier doubt is said to be over"), (denied, "denial, what-if or the accounting rule quoted")) if names]
        lines.append(f"- _Going concern not flagged: {'; '.join(why)}._")
    return lines + notes


if __name__ == "__main__":
    main()
