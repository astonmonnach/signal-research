"""Scan ALL of the day's SEC filings for catalyst-type events.

Usage:  python watch/scan_market.py [YYYY-MM-DD]   (default: yesterday)
About 5,000 filings land each business day. This keeps only the ones from
listed companies (those with a ticker) that match the event types we trade,
plus any 8-K using our trigger phrases, and writes
watch/market/YYYY-MM-DD.md. Nothing is judged here; the digest is a
shortlist to read.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
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


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today() - timedelta(days=1)
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
        hits[FORMS[form]].append(
            f"- **{'/'.join(tickers[cik])}** {name} `{form}`{note} "
            f"[filing index](https://www.sec.gov/Archives/{path.replace('.txt', '-index.htm')})")

    by_filing = {}
    for p in PHRASES:
        time.sleep(0.3)
        q = urllib.parse.urlencode({"q": f'"{p}"', "dateRange": "custom", "category": "custom",
                                    "startdt": f"{day}", "enddt": f"{day}", "forms": "8-K"})
        try:
            res = json.loads(fetch(f"https://efts.sec.gov/LATEST/search-index?{q}"))["hits"]["hits"]
        except Exception as e:
            by_filing[f"err-{p}"] = [f"_search for \"{p}\" failed: {e}_"]
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
            entry = by_filing.setdefault(acc, [tk, url, [], items])
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

    n = sum(len(v) for v in hits.values()) + len(phrase_hits)
    lines = [f"# Market-wide filings scan {day}", "",
             f"{total:,} filings filed. {n} from listed companies match our event types.", ""]
    for section in dict.fromkeys(FORMS.values()):
        if hits.get(section):
            lines += [f"## {section}", *hits[section], ""]
    if phrase_hits:
        lines += ["## 8-Ks with trigger phrases", *phrase_hits, ""]
    OUT.mkdir(exist_ok=True)
    (OUT / f"{day}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
