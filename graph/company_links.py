"""Customer, supplier and subsidiary leads from a company's latest annual report.

    python graph/company_links.py TICKER

Finds the company's latest 10-K (20-F or 40-F for a foreign company), downloads the main document and prints
  (a) every passage about customer or supplier concentration, with 250 characters of context either side;
  (b) the subsidiaries in Exhibit 21 (Exhibit 8 of a 20-F), when the filing has one;
  (c) ready-to-paste `python graph/links.py add ...` commands, only where a passage NAMES the other party.

It never writes to edges.csv: a link goes in when you have read the passage and run the command yourself.
"Customer A", "one distributor" and "a single supplier" are not names, so they get no command. A name is only
accepted when it carries a company ending (Inc., Corp., Ltd. ...) or matches a US-listed company's name exactly;
when it matches, the command uses that ticker and says which listed name it matched, so the match can be checked.
"""
import html
import json
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "PersonalResearch research@example.com"}
CONTEXT = 250          # characters shown either side of a match
MAX_PASSAGES = 60      # a 10-K repeats itself (risk factors, MD&A, notes); past this the rest is only counted
MAX_SUBSIDIARIES = 150
ANNUAL = ("10-K", "20-F", "40-F")

# What counts as talking about concentration. A passage is kept only if it also names a kind of counterparty
# (PARTY), so "gross margin was 40% of net sales" does not get through.
CONCENTRATION = [
    r"accounted\s+for\s+.{0,40}?%\s+of",
    r"%\s+of\s+(?:our\s+|the\s+company['’]s\s+|total\s+|consolidated\s+)*(?:net\s+)?(?:revenues?|sales|purchases|accounts\s+receivable)\b"
    r"(?!\s+(?:representatives|force|team|personnel|staff|employees|professionals|offices))",
    r"(?:sole|single)[- ]source",
    r"(?:sole|single)\s+(?:supplier|vendor|manufacturer|foundry|customer)",
    r"(?:largest|significant|major|principal)\s+(?:customer|supplier|vendor|distributor)s?\b(?!\s+orders?)",
    r"limited\s+number\s+of\s+(?:customers|suppliers|vendors|distributors|manufacturers)",
]
PARTY = r"customer|supplier|vendor|distributor|reseller|foundr|manufacturer|OEM"

# Company-name shapes. CAP is one capitalised word; a NAME is a run of them, with an optional company ending.
CAP = r"[A-Z][A-Za-z0-9&'’\-]*"
ENDING = r"(?:Inc\.?|Incorporated|Corp\.?|Corporation|Co\.?|Company|Ltd\.?|Limited|LLC|L\.L\.C\.|L\.P\.|LP|PLC|plc|AG|S\.A\.|N\.V\.|GmbH|Oyj|K\.K\.)"
NAME = rf"{CAP}(?:\s+(?:{CAP}|of|&))*(?:,?\s+{ENDING})*"
NAMES = rf"{NAME}(?:(?:\s*,\s*and\s+|\s+and\s+|\s*,\s*){NAME})*"
PERCENT = r"(?:approximately\s+|about\s+|more\s+than\s+|over\s+|at\s+least\s+)?\d[\d.]*\s*%"

# (kind, pattern). Keywords match in any case; the names themselves must be capitalised.
NAMED = [
    ("customer", rf"(?i:sales|revenues?|shipments)\s+(?i:to|from)\s+({NAMES})"),
    ("customer", rf"(?i:largest|significant|major|principal|key)\s+(?i:customers?),?\s*(?i:is|are|was|were|include[sd]?|including|such\s+as|:)?\s*({NAMES})"),
    ("customer", rf"(?i:customers?)\s+(?i:such\s+as|including|include[sd]?|like)\s+({NAMES})"),
    ("either", rf"({NAMES})(?:\s*\([^)]{{0,40}}\))?,?\s+(?i:each\s+|individually\s+)?(?i:accounted\s+for|represented|comprised|constituted)\s+(?i:{PERCENT})"),
    ("supplier", rf"(?i:purchase[sd]?|sourced?|procured?|obtain(?:s|ed)?)\s+(?:[a-z,\- ]{{0,60}}?\s)?(?i:from)\s+({NAMES})"),
    ("supplier", rf"(?i:manufactured|fabricated|produced|supplied|assembled|packaged|tested)\s+(?:[a-z ]{{0,30}}?\s)?(?i:by)\s+({NAMES})"),
    ("supplier", rf"(?i:sole|single)[- ](?i:source\s+)?(?i:supplier|vendor|manufacturer|foundry)(?:\s+(?i:is|of|for)|,)?\s+({NAMES})"),
    ("supplier", rf"(?i:rely|relies|relied|depend|depends|dependent|reliance)\s+(?i:solely\s+|primarily\s+|heavily\s+|substantially\s+|exclusively\s+)?(?i:on|upon)\s+({NAMES})"),
    ("supplier", rf"(?i:suppliers?|foundr(?:y|ies)|vendors?|manufacturers?),?\s+(?i:such\s+as|including|include[sd]?|like|is|are)\s+({NAMES})"),
]
# Capitalised words that only open a sentence: stripped from the front of a candidate ("In fiscal 2026 Nokia" -> "Nokia").
OPENERS = set("""The We Our It Its This These Those Such No None Each Any All Some Certain Both In During For As At On Of To By
    If When While Fiscal Sales Revenue Revenues Net Total Direct Indirect Based Purchases""".split())
# Capitalised words that name a region, period, market segment or role. A candidate made only of these is not a
# counterparty ("North America", "Automotive"), but one that merely starts with one can be ("Taiwan Semiconductor ...").
NOT_A_NAME = OPENERS | set("""One Two Three Four Five Six Ten OEM OEMs ODM ODMs
    Customer Customers Supplier Suppliers Distributor Distributors Vendor Vendors Company
    International Domestic Export Foreign U.S. US United States North South America American Americas Asia Asian Europe European
    China Chinese Japan Japanese Taiwan Korea Korean Germany German Canada Mexico India Israel EMEA APAC Pacific
    Fiscal In During For As At On Of To By If When While Note Notes Item Table Part Management Government Federal Other Others
    January February March April May June July August September October November December Q1 Q2 Q3 Q4
    Automotive Industrial Consumer Mobile Enterprise Communications Computing Defense Aerospace Medical Networking Commercial
    Military Energy Data Cloud Core Wireless Storage Memory Embedded IoT PC Product Products Segment Segments
    Accounts Receivable Inventory Purchases Cost Costs Gross Operating Financial Statements Annual Report Form Company's""".split())
PLACEHOLDER = r"\b(?:Customer|Supplier|Vendor|Distributor|Client|Partner)\s+(?:[A-Z]|\d{1,2}|#\d{1,2})\b"
LEGAL = {"INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "LLC", "LP", "SA", "NV", "AG", "GMBH", "OYJ", "KK"}


def get(url):
    """One SEC request: contact User-Agent, a pause first (well under 10 a second), a timeout."""
    time.sleep(0.15)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def plain(raw):
    """A filing document as plain text: tags and entities removed, whitespace collapsed."""
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|ix:header)\b.*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", t)))


def norm(name):
    """A company name reduced for matching: upper case, no punctuation, legal endings dropped ("Nokia Corp" -> NOKIA)."""
    words = re.sub(r"[^A-Z0-9& ]", " ", name.upper().replace("/DE/", " ")).split()
    if words[:1] == ["THE"]:
        words = words[1:]
    while words and words[-1] in LEGAL:
        words.pop()
    return " ".join(words)


def latest_annual(cik):
    """(company record, form, accession number, main document, date filed, period end) for the newest annual report."""
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    pages = [sub["filings"]["recent"]]
    older = [f["name"] for f in sub["filings"].get("files", [])]
    while pages:
        page = pages.pop(0)
        for i, form in enumerate(page["form"]):
            if form in ANNUAL:
                return sub, form, page["accessionNumber"][i], page["primaryDocument"][i], page["filingDate"][i], page["reportDate"][i]
        if older:   # a heavy filer's last 10-K can sit beyond the 1,000 most recent filings
            pages.append(json.loads(get("https://data.sec.gov/submissions/" + older.pop(0))))
    return sub, None, None, None, None, None


def passages(text):
    """Every stretch of the text around a concentration phrase, overlapping stretches merged, that mentions a counterparty."""
    spans = sorted((max(0, m.start() - CONTEXT), min(len(text), m.end() + CONTEXT))
                   for rx in CONCENTRATION for m in re.finditer(rx, text, re.I))
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out = []
    for a, b in merged:
        p = text[a:b]
        if re.search(PARTY, p, re.I):
            out.append(re.sub(r"^\S*\s+|\s+\S*$", "", p))   # drop the half words at either end
    return out


def exhibit(folder, acc, kinds):
    """(exhibit type, url) of the first document in the filing index whose type starts with one of `kinds`, or None."""
    page = get(f"{folder}{acc}-index.htm").decode("utf-8", "ignore")
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        link = re.search(r'href="([^"]+)"', row)
        if len(cells) >= 4 and link and re.sub(r"<[^>]+>", "", cells[3]).strip().upper().startswith(kinds):
            return re.sub(r"<[^>]+>", "", cells[3]).strip(), "https://www.sec.gov" + link.group(1).replace("/ix?doc=", "")
    return None


def subsidiaries(raw):
    """The rows of a subsidiaries exhibit as text lines ("Name | Jurisdiction | % owned"), headings dropped."""
    def clean(x):   # also drops zero-width spaces and byte-order marks, which filing agents leave in empty cells
        x = html.unescape(re.sub(r"(?s)<[^>]+>", " ", x)).replace(chr(0x200B), " ").replace(chr(0xFEFF), " ")
        return re.sub(r"\s+", " ", x).strip()

    def row(m):   # a table row becomes one line, whatever tags sit inside its cells
        cells = [clean(c) for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", m.group(1))]
        return "\n" + " | ".join(c for c in cells if c) + "\n"

    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|title)\b.*?</\1>", " ", t)
    t = re.sub(r"(?is)<tr[^>]*>(.*?)</tr>", row, t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>", "\n", t)
    out = []
    for line in t.split("\n"):
        line = clean(line)
        if (re.search(r"[A-Za-z]{2}", line) and not re.search(r"(?i)\.htm$|subsidiaries\s+of|subsidiaries$|^exhibit\b|^ex-2", line)
                and not re.match(r"(?i)^(list of|names?\b|jurisdiction|state or|country or|organized under|percent|entity\b|legal entity|"
                                 r"the following|the active subsidiaries|pursuant to|as of\b|page\b|directly or|by the company)", line)):
            out.append(line)
    return out


def named_parties(passage, aliases, listed, own):
    """([(kind, name as written, ticker or None, listed name or None, sentence)], {names seen but not trusted})
    for the counterparties the passage names."""
    found, unsure = [], set()
    for kind, rx in NAMED:
        for m in re.finditer(rx, passage):
            start = max(passage.rfind(". ", 0, m.start()) + 2, 0)
            end = passage.find(". ", m.end())
            sentence = passage[start:end + 1 if end >= 0 else len(passage)].strip()
            if kind == "either":
                kind_here = "supplier" if re.search(r"(?i)purchases|inventory|suppl|vendor|raw\s+material|cost\s+of", sentence) and \
                    not re.search(r"(?i)revenue|net\s+sales|customer", sentence) else "customer"
            else:
                kind_here = kind
            group = re.sub(rf",\s+(?={ENDING})", " ", m.group(1))   # keep "Avnet, Inc." in one piece before splitting the list
            for name in re.split(r"\s*,\s*and\s+|\s+and\s+|\s*,\s*", group):
                name = name.strip(" .,")
                words = name.split()
                while words and words[0] in OPENERS:   # "In fiscal 2026 Nokia ..." -> "Nokia"
                    words = words[1:]
                name = " ".join(words)
                if len(name) < 3 or all(w in NOT_A_NAME for w in words) or re.fullmatch(PLACEHOLDER, name):
                    continue
                full = aliases.get(name, name)
                key = norm(full)
                if not key or key in own or any(key.startswith(o + " ") or o.startswith(key + " ") for o in own):
                    continue   # the filer itself or one of its own defined names
                hit = listed.get(key)
                if hit or re.search(rf"\b{ENDING}$", full):
                    found.append((kind_here, full, hit[0] if hit else None, hit[1] if hit else None, sentence))
                else:
                    unsure.add(full)
    return found, unsure


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    ticker = sys.argv[1].upper()
    try:
        book = json.loads(get("https://www.sec.gov/files/company_tickers.json")).values()
    except Exception as e:
        raise SystemExit(f"Could not read the SEC ticker list: {e}")
    cik = next((v["cik_str"] for v in book if v["ticker"].upper() == ticker), None)
    if cik is None:
        raise SystemExit(f"{ticker} is not in the SEC ticker list.")
    listed = {}
    for v in book:   # the list runs largest company first, so the first holder of a name keeps it
        listed.setdefault(norm(v["title"]), (v["ticker"], v["title"]))
    try:
        sub, form, acc, doc, filed, period = latest_annual(cik)
    except Exception as e:
        raise SystemExit(f"Could not read {ticker}'s filing list: {e}")
    print(f"{ticker}  {sub.get('name')}  (CIK {cik}, SIC {sub.get('sic')} {sub.get('sicDescription')})")
    if not form:
        raise SystemExit("No 10-K, 20-F or 40-F found in its filings.")
    folder = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/"
    url = folder + doc
    print(f"Latest annual report: {form} filed {filed} for the year to {period}\n{url}\n")
    try:
        text = plain(get(url))
    except Exception as e:
        raise SystemExit(f"Could not download the report: {e}")

    found = passages(text)
    print(f"== (a) Customer and supplier concentration: {len(found)} passage{'' if len(found) == 1 else 's'} "
          f"({CONTEXT} characters either side of each match) ==")
    for i, p in enumerate(found[:MAX_PASSAGES], 1):
        print(f"[{i}] ...{p}...\n")
    if len(found) > MAX_PASSAGES:
        print(f"({len(found) - MAX_PASSAGES} more passages not shown; the report repeats itself.)\n")
    if not found:
        print("None found.\n")

    print("== (b) Subsidiaries ==")
    try:
        ex = exhibit(folder, acc, ("EX-21",) if form == "10-K" else ("EX-21", "EX-8"))
        if ex:
            rows = subsidiaries(get(ex[1]))
            print(f"{ex[0]}: {ex[1]}")
            for r in rows[:MAX_SUBSIDIARIES]:
                print(f"  - {r}")
            if len(rows) > MAX_SUBSIDIARIES:
                print(f"  ({len(rows) - MAX_SUBSIDIARIES} more rows not shown)")
            if not rows:
                print("  (the exhibit has no rows that read as text: open the link)")
        else:
            print("This filing has no subsidiaries exhibit in its index.")
    except Exception as e:
        print(f"Could not read the subsidiaries exhibit: {e}")

    print("\n== (c) Suggested links (only where a passage names the other party; read the passage, then run the line) ==")
    # Names the report defines for itself or for others: Taiwan Semiconductor Manufacturing Company Limited ("TSMC").
    aliases = {}
    for m in re.finditer(rf"({NAME})\s*\(\s*(?:or\s+|the\s+|together[^)“\"]{{0,60}})?[“\"]([A-Z][A-Za-z0-9&\- ]{{1,30}})[”\"]", text):
        aliases.setdefault(m.group(2).strip(), m.group(1).strip())
    own = {norm(sub.get("name") or "")} | {norm(x.get("name") or "") for x in sub.get("formerNames", [])}
    own |= {norm(a) for a, full in aliases.items() if norm(full) in own} | {"COMPANY", "REGISTRANT"}
    own.discard("")
    best, unsure, placeholders = {}, set(), sum(1 for p in found if re.search(PLACEHOLDER, p))
    for p in found:
        named, maybe = named_parties(p, aliases, listed, own)
        unsure |= maybe
        for kind, name, tk, title, sentence in named:
            node = tk or f"co:{name}"
            if tk == ticker:
                continue
            # one line per counterparty and kind; a sentence that gives a percentage beats one that does not
            if (node, kind) not in best or ("%" in sentence and "%" not in best[(node, kind)][3]):
                best[(node, kind)] = (name, tk, title, sentence)
    for (node, kind), (name, tk, title, sentence) in best.items():
        says = re.sub(r"\s+", " ", sentence).replace('"', "'")
        detail = f"{name} is a {kind} of {ticker} ({form} filed {filed}): {says}"
        detail = detail if len(detail) <= 220 else detail[:217].rsplit(" ", 1)[0] + "..."
        print(f'python graph/links.py add {ticker} "{node}" {kind} "{detail}" {url}'
              + (f'   # "{name}" matched by name to listed {tk} ({title}): check it is the same company' if tk else
                 "   # not matched to a listed company: it stays a co: node unless you know its ticker"))
    if not best:
        print("None: no passage names a customer or supplier in a way this script trusts.")
    unsure -= {name for name, *_ in best.values()}
    if unsure:
        print(f"(Also named in those passages, but with no company ending and no exact listed-name match, so no command: {', '.join(sorted(unsure))}.)")
    if placeholders:
        print(f"({placeholders} passage{'' if placeholders == 1 else 's'} use a placeholder such as \"Customer A\": that is not a name, so no link is suggested.)")


if __name__ == "__main__":
    main()
