"""Read the holding from a Schedule 13D/13G cover page, for every reporting person.

A 13D often has several cover pages (the fund, the manager, the person running it).
The first cover page is usually the smallest. Quote the LARGEST row-11 amount: that is
the group's holding. (LESSONS.md, 2026-10-08: ESRT's 13D was first read as 7.5M / 4.4%
from the fund's page; the manager's page shows 10.0M / 5.8%.)

Usage: python watch/thirteen_d.py <13D primary_doc URL>
"""
import html
import re
import sys
import urllib.request

UA = {"User-Agent": "PersonalResearch research@example.com"}


def covers(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    rows = []
    for m in re.finditer(r"Name of reporting person[s]?\s*(.{1,120}?)\s*2 Check", text, re.I):
        chunk = text[m.end():m.end() + 2500]
        amt = re.search(r"11 Aggregate amount beneficially owned by each reporting person\s*([\d,\.]+)", chunk, re.I)
        pct = re.search(r"13 Percent of class represented by amount in Row \(11\)\s*([\d\.]+)\s*%?", chunk, re.I)
        rows.append((m.group(1).strip(), amt.group(1) if amt else "?", pct.group(1) if pct else "?"))
    if not rows:  # fall back to the row-11 amounts alone
        for a in re.findall(r"11 Aggregate amount beneficially owned by each reporting person\s*([\d,\.]+)", text, re.I):
            rows.append(("(unnamed)", a, "?"))
    return rows


def main():
    rows = covers(sys.argv[1])
    for name, amt, pct in rows:
        print(f"{name[:60]:60s} {amt:>16s} {pct:>6s}%")
    nums = [float(a.replace(",", "")) for _, a, _ in rows if re.fullmatch(r"[\d,\.]+", a)]
    if nums:
        print(f"GROUP HOLDING (largest cover page): {max(nums):,.0f} shares")


if __name__ == "__main__":
    main()
