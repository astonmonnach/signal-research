"""G. Every scanner flag at its actual filing time: what had already moved before we could act, and what happened in the
next 30 minutes, hour, two hours, to the close and over three sessions. Also the peak on the way and when it came."""
import sys, re, glob, json, pickle, datetime as dt
from statistics import median, mean
from intraday import *

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "ledger"))
from build_ledger import SECTION_CATEGORY, PHRASE_CATEGORY  # noqa: E402

ACC = json.load(open(HERE / "accept.json"))
# (found, ticker, category) -> accession, parsed the same way build_ledger reads the scans
KEY = {}
for f in sorted(glob.glob(str(ROOT / "watch/market/2026-*.md"))):
    day = Path(f).stem; cat = None
    for line in open(f, encoding="utf-8").read().splitlines():
        if line.startswith("## "):
            h = line[3:].lower(); cat = next((c for k, c in SECTION_CATEGORY if h.startswith(k)), "8k" if h.startswith("8-ks") else None)
            continue
        m = re.match(r"- \*\*([A-Z0-9.\-]+)[^*]*\*\*\s*(.*)", line)
        if not m or not cat:
            continue
        tk, rest = m.group(1), m.group(2).lower()
        c = cat
        if cat == "registration_effective" and "not supply" in rest:
            continue
        if cat == "8k":
            rest = re.sub(r"bio-mention \([^)]*\),?", "", rest); rest = re.sub(r"financing-mention \([^)]*\),?", "", rest)
            c = next((cc for p, cc in PHRASE_CATEGORY if p in rest), None)
            if not c:
                continue
        a = re.search(r"/data/\d+/(\d{18})/", line)
        if a:
            KEY.setdefault((day, tk, c), a.group(1))

rows = pickle.load(open(HERE / "rows.pkl", "rb"))
ev, nokey, notime, nobars = [], 0, 0, 0
seen = set()
for r in sorted(rows, key=lambda r: r["found"]):
    k = (r["found"], r["ticker"], r["cat"])
    a = KEY.get(k)
    if not a:
        nokey += 1; continue
    if a not in ACC:
        notime += 1; continue
    if (r["ticker"], a) in seen:
        continue
    seen.add((r["ticker"], a))
    t0 = dt.datetime.fromisoformat(ACC[a].replace("Z", "+00:00"))
    x = react(r["ticker"], t0)
    if not x:
        nobars += 1; continue
    x.update(ticker=r["ticker"], cat=r["cat"], found=r["found"], acc=a, take=r["take"], entry_raw=r["entry_raw"], mdv20=r["mdv20"], dirn=r["dirn"])
    ev.append(x)
print(len(rows), "ledger rows;", len(ev), "events with a filing time and 5-minute bars; no scan line", nokey, "| no time", notime, "| no bars", nobars)
pickle.dump(ev, open(HERE / "events.pkl", "wb"))

GROUPS = {
    "Buy-side flags (strategic review, 13D, issuer tender)": ["8k_strategic_review", "activist_13d", "tender_issuer_buyback"],
    "Signed deals and tenders": ["8k_merger_agreement", "8k_tender_offer", "tender_third_party", "merger_vote"],
    "Special dividends": ["8k_special_dividend"],
    "Spin-offs": ["8k_spin_off"],
    "Supply flags (reverse split, registration, EFFECT)": ["8k_reverse_split", "registration_effective", "share_registration"],
    "Lock-up 8-Ks, IPO priced, delisting": ["8k_lock_up", "ipo_priced", "delisting"],
}


def S_(v):
    v = [x for x in v if x is not None]
    if not v:
        return "   n/a"
    return f"{median(v):+5.1f}/{mean(v):+5.1f}/{100 * sum(x > 0 for x in v) / len(v):3.0f}%"


def first(es):
    s, out = set(), []
    for e in es:
        if e["ticker"] not in s:
            s.add(e["ticker"]); out.append(e)
    return out


print("\nmedian / mean / share positive. gap = last trade before the filing -> first regular price we could get. Then from that entry.")
print(f"{'group':52} {'n':>4} | {'when filed':16} | {'gap':>17} | {'+30m':>17} | {'+1h':>17} | {'+2h':>17} | {'close':>17} | {'next close':>17} | {'3rd close':>17}")
for g, cats in GROUPS.items():
    for lab, sub in (("all", lambda e: True), ("takeable", lambda e: e["take"])):
        es = first([e for e in ev if e["cat"] in cats and sub(e)])
        if len(es) < 5:
            continue
        inh = sum(e["in_hours"] for e in es)
        print(f"{g[:44] + ' ' + lab:52} {len(es):4} | {inh:3} in hours     | {S_([e['gap'] for e in es])} | {S_([e['r30'] for e in es])} | {S_([e['r60'] for e in es])} | {S_([e['r120'] for e in es])} | {S_([e['rclose'] for e in es])} | {S_([e.get('rnext') for e in es])} | {S_([e.get('r3') for e in es])}")

print("\nPeaks after the entry (takeable only): median peak within 2 hours / the entry session / 3 sessions, and the median time of the 3-session peak")
for g, cats in GROUPS.items():
    es = first([e for e in ev if e["cat"] in cats and e["take"]])
    if len(es) < 5:
        continue
    pm = [e["peak_3d_min"] for e in es if e.get("peak_3d_min") is not None]
    hit = lambda thr, tag: 100 * sum(1 for e in es if e.get(f"peak_{tag}", -99) >= thr) / len(es)
    print(f"{g[:50]:52} n={len(es):3} | peak 2h {median(e['peak_2h'] for e in es):+5.1f} | day {median(e['peak_day'] for e in es):+5.1f} | 3 sessions {median(e['peak_3d'] for e in es):+5.1f} | low 3 sessions {median(e['low_3d'] for e in es):+5.1f} | touched +5% in the session {hit(5, 'day'):3.0f}% | +10% in 3 sessions {hit(10, '3d'):3.0f}% | -10% in 3 sessions {100 * sum(1 for e in es if e.get('low_3d', 0) <= -10) / len(es):3.0f}%")

print("\nBy when the filing arrived (buy-side flags and deals, takeable)")
es = first([e for e in ev if e["cat"] in GROUPS["Buy-side flags (strategic review, 13D, issuer tender)"] + GROUPS["Signed deals and tenders"] + ["8k_special_dividend", "8k_spin_off"] and e["take"]])
for lab, f in (("during market hours", lambda e: e["in_hours"]), ("outside market hours", lambda e: not e["in_hours"])):
    s = [e for e in es if f(e)]
    print(f"  {lab:22} n={len(s):3} | gap {S_([e['gap'] for e in s])} | +30m {S_([e['r30'] for e in s])} | +1h {S_([e['r60'] for e in s])} | +2h {S_([e['r120'] for e in s])} | close {S_([e['rclose'] for e in s])} | next {S_([e.get('rnext') for e in s])}")
big = [e for e in es if abs(e["gap"]) >= 5]
print(f"  moved 5%+ before we could act: {len(big)} of {len(es)}; of those up-gaps: {sum(e['gap'] > 0 for e in big)}")
for lab, f in (("gapped UP 5%+", lambda e: e["gap"] >= 5), ("gapped DOWN 5%+", lambda e: e["gap"] <= -5), ("gap under 2%", lambda e: abs(e["gap"]) < 2)):
    s = [e for e in es if f(e)]
    if len(s) >= 4:
        print(f"  {lab:22} n={len(s):3} | +30m {S_([e['r30'] for e in s])} | +1h {S_([e['r60'] for e in s])} | +2h {S_([e['r120'] for e in s])} | close {S_([e['rclose'] for e in s])} | next {S_([e.get('rnext') for e in s])} | 3rd {S_([e.get('r3') for e in s])}")
