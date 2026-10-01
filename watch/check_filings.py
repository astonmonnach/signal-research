"""Check SEC EDGAR for new filings on the watchlist.

Usage:  python watch/check_filings.py
Compares each company's recent filings with watch/state.json, prints what's
new, and writes watch/digests/YYYY-MM-DD.md. The first run just records the
current state, so it reports nothing new.
"""
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
STATE = HERE / "state.json"
DIGESTS = HERE / "digests"
UA = {"User-Agent": "PersonalResearch research@example.com"}

# Forms worth a look, with what they usually mean for a catalyst trade.
IMPORTANT = {
    "8-K": "material event",
    "8-K/A": "material event (amended)",
    "S-1": "registration (possible share sale)",
    "S-1/A": "registration amendment",
    "S-3": "shelf registration (possible share sale)",
    "EFFECT": "SEC declared a registration effective",
    "424B3": "prospectus (resale / offering)",
    "424B4": "final offering prospectus",
    "424B5": "offering prospectus supplement",
    "4": "insider buy/sell",
    "144": "insider intends to sell",
    "SC 13D": "activist / 5%+ holder",
    "SC 13D/A": "activist / 5%+ holder update",
    "SCHEDULE 13D": "activist / 5%+ holder",
    "SCHEDULE 13D/A": "activist / 5%+ holder update",
    "SC 13G": "passive 5%+ holder",
    "SCHEDULE 13G": "passive 5%+ holder",
    "SCHEDULE 13G/A": "passive 5%+ holder update",
    "10-Q": "quarterly results",
    "10-K": "annual results",
    "DEF 14A": "proxy / shareholder meeting",
    "DEFM14A": "merger proxy",
    "SC TO-T": "tender offer",
    "SC TO-I": "issuer tender offer",
    "10-12B/A": "spin-off registration",
}

# 8-K item codes, so the digest says what happened.
ITEMS = {
    "1.01": "material agreement", "1.02": "agreement terminated",
    "2.01": "acquisition/disposal completed", "2.02": "results",
    "2.03": "new debt", "2.05": "restructuring costs", "2.06": "impairment",
    "3.01": "listing notice", "3.02": "unregistered share sale",
    "3.03": "shareholder rights changed", "5.02": "exec/director change",
    "5.03": "charter/bylaw change", "5.07": "shareholder vote results",
    "7.01": "Reg FD disclosure", "8.01": "other event", "9.01": "exhibits",
}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    tickers = json.loads((HERE / "watchlist.json").read_text())["tickers"]
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    first_run = not state

    lookup = {v["ticker"]: v["cik_str"] for v in get_json(
        "https://www.sec.gov/files/company_tickers.json").values()}

    new_lines = []
    for t in tickers:
        cik = lookup.get(t)
        if cik is None:
            new_lines.append(f"- **{t}**: not found in SEC ticker list (new listing? check again later)")
            continue
        time.sleep(0.2)
        recent = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")["filings"]["recent"]
        seen = set(state.get(t, []))
        fresh = []
        for i, acc in enumerate(recent["accessionNumber"][:40]):
            if acc in seen:
                continue
            form = recent["form"][i]
            if form not in IMPORTANT:
                continue
            items = ", ".join(ITEMS.get(x, x) for x in recent["items"][i].split(",") if x and x != "9.01")
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                   f"{acc.replace('-', '')}/{recent['primaryDocument'][i]}")
            what = IMPORTANT[form] + (f" ({items})" if items else "")
            fresh.append(f"- **{t}** {recent['filingDate'][i]} `{form}`: {what}. [filing]({url})")
        state[t] = recent["accessionNumber"][:40]
        if not first_run:
            new_lines.extend(fresh)

    STATE.write_text(json.dumps(state, indent=1))
    if first_run:
        print("First run: recorded current filings. Future runs will report anything new.")
        return
    DIGESTS.mkdir(exist_ok=True)
    body = "\n".join(new_lines) if new_lines else "No new filings of interest."
    (DIGESTS / f"{date.today()}.md").write_text(f"# Filings digest {date.today()}\n\n{body}\n", encoding="utf-8")
    print(body)


if __name__ == "__main__":
    sys.exit(main())
