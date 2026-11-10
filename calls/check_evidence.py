"""Evidence for public calls: every claim is a verbatim quote from the filing, and this script proves it.

A call's claims live in calls/evidence/<id>.csv with columns:
  claim  - the sentence as it appears (or will appear) in the call or post
  quote  - text copied word for word from the source document (several rows per claim are fine;
           a number we worked out ourselves is marked "(arith)" in the claim and quotes its inputs)
  url    - the document the quote comes from (sec.gov or the company's own site)
  note   - optional; a note starting "CORRECTION" marks a claim already posted that the quotes show was wrong
           (the posted call stays as it was, append-only; the correction lives here and in LESSONS.md)

The check fetches every url (cached in calls/evidence/.cache/), turns the HTML into plain text and
confirms each quote is in it. Spacing, curly quotes and dashes are normalised; nothing else is. A call
numbered FIRST_ID or later must have an evidence file, and every row must pass.

Run:  python calls/check_evidence.py              -> check every evidence file; exit 1 on any problem
      python calls/check_evidence.py 9 10         -> check those calls only
      python calls/check_evidence.py --file research/evidence/2026-11-02-ABC.csv
                                                  -> check a deep dive's evidence file
      python calls/check_evidence.py --find URL "words"
                                                  -> print each sentence in URL containing the words,
                                                     so quotes are copied from the source, not typed
Rule 2026-11-01 (NIVF, call #9): see LESSONS.md.
"""
import csv, hashlib, html, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALLS = ROOT / "calls/CALLS.csv"
EVID = ROOT / "calls/evidence"
CACHE = EVID / ".cache"
FIRST_ID = 10
UA = {"User-Agent": "PersonalResearch research@example.com"}
SWAP = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "‑": "-", " ": " ", "​": ""}


def plain(raw):
    """HTML -> one line of plain text."""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    for a, b in SWAP.items():
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def found(quote, text):
    """True if the quote is in the text. Tags can split words ("Leak-<b>Out</b>"), so a second pass
    ignores all whitespace; letters, digits and punctuation must still match exactly."""
    q = plain(quote)
    if q in text:
        return True
    return re.sub(r"\s", "", q) in re.sub(r"\s", "", text)


def fetch(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".txt")
    if f.exists():
        return f.read_text(encoding="utf-8")
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    text = plain(raw.decode("utf-8", errors="ignore"))
    f.write_text(text, encoding="utf-8")
    time.sleep(0.15)                                   # SEC asks for at most 10 requests a second
    return text


def problems(call_id, rows, get=fetch):
    out = []
    if not rows:
        return [f"call {call_id}: evidence file has no rows"]
    for i, r in enumerate(rows, 2):                    # row 1 is the header
        where = f"call {call_id} row {i}"
        claim, quote, url = (r.get(k, "").strip() for k in ("claim", "quote", "url"))
        if not claim or not quote or not url:
            out.append(f"{where}: claim, quote and url are all required"); continue
        if not url.startswith("https://"):
            out.append(f"{where}: url must be https"); continue
        try:
            text = get(url)
        except Exception as e:
            out.append(f"{where}: could not fetch {url} ({e})"); continue
        if not found(quote, text):
            out.append(f"{where}: quote not found in {url}: {quote[:90]!r}")
        out += unfunded_claim(where, claim, quote, r.get("note", ""))
    return out


UNFUNDED = re.compile(r"no money|obligates? no|unfunded|not funded|no orders?\b|nothing (?:is )?(?:funded|ordered)", re.I)


def unfunded_claim(where, claim, quote, note):
    """Rule 2026-11-10 (ELMT): an SF 1449's "does not obligate funds" note is form boilerplate. A guaranteed IDIQ
    minimum is money the government must order, and ELMT's 10-Q later showed $161.9M funded at 2 Oct. A claim that an
    award is unfunded or has no orders may not rest on that sentence; quote the funds obligated at award (DoD contract
    page) or the next 10-Q's backlog instead. Rows whose note starts with CORRECTION are exempt."""
    if note.strip().upper().startswith("CORRECTION"):
        return []
    if "obligate funds" in quote.lower() and UNFUNDED.search(claim):
        return [f"{where}: 'does not obligate funds' is SF 1449 boilerplate, not proof of no money or no orders; "
                f"quote the funds obligated at award or the 10-Q backlog (rule 2026-11-10, ELMT)"]
    return []


def load(call_id):
    f = EVID / f"{call_id}.csv"
    if not f.exists():
        return None
    with open(f, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def call_ids():
    with open(CALLS, newline="", encoding="utf-8") as fh:
        return [int(r["id"]) for r in csv.DictReader(fh)]


def find(url, words):
    text = fetch(url)
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z(\"])", text):
        if words.lower() in s.lower():
            print("-", s.strip())


def main(argv):
    if argv[:1] == ["--find"]:
        return find(argv[1], argv[2]) or 0
    if argv[:1] == ["--file"]:                         # a deep dive's evidence, e.g. research/evidence/<date>-<TICKER>.csv
        with open(argv[1], newline="", encoding="utf-8") as fh:
            bad = problems(argv[1], list(csv.DictReader(fh)))
        for p in bad:
            print("PROBLEM", p)
        print(f"evidence: {argv[1]}, {len(bad)} problem(s)")
        return 1 if bad else 0
    ids = [int(a) for a in argv] or call_ids()
    bad, checked = [], 0
    for cid in ids:
        rows = load(cid)
        if rows is None:
            if cid >= FIRST_ID:
                bad.append(f"call {cid}: no calls/evidence/{cid}.csv (required from call #{FIRST_ID})")
            continue
        checked += 1
        bad += problems(cid, rows)
    for p in bad:
        print("PROBLEM", p)
    print(f"evidence: {checked} call(s) checked, {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
