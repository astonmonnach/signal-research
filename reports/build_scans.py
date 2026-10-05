"""Daily scans: one file per date with everything the pipeline found that day.

Usage:
  python reports/build_scans.py                     # today and the 6 days before, plus any date with no file yet
  python reports/build_scans.py --date 2026-10-02   # one date
  python reports/build_scans.py --all               # every date that has any input (backfill)

Writes scans/YYYY-MM-DD.md and the index scans/README.md. Sections, always in this order:
S1 contract signals, watchlist filings, market-wide scan (by category, with the ledger's
5d-before / found-day / liquidity columns), press releases, new setups, triage notes.
Every item links to its source. It only reads files other jobs wrote (reports/sources.py),
so re-running with the same inputs gives the same output, and unchanged files aren't rewritten.
The default looks back a week because the evening job's triage and market scan land after the
morning run, and press releases keep arriving all day.
"""
import argparse, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sources import (Sources, BL, TODAY, label, pct, money, usd, price, day, long_day, link, plain, clip, write, sgn,  # noqa: E402
                     research_refs, triage_summary, is_watch_press, ROOT)

LOOKBACK_DAYS = 7


def ledger_cols(lr):
    """5d before | found day | $vol/day, from a ledger row (blank when there's none)."""
    if not lr or lr.get("pre_move_5d") is None and lr.get("adv_usd") is None:
        return ["", "", ""]
    adv = money(lr["adv_usd"]) + ("" if lr.get("liquid") == "yes" else " ⚠")
    return [pct(lr["pre_move_5d"]), pct(lr["found_day_move"]), adv]


def tick(S, t, frm):
    return link(t, f"stocks/{t}.md", frm) if t in S.dossiers else f"**{t}**"


def tickers_cell(S, s, frm):
    first, *rest = s.split("/")
    extra = ("/" + "/".join(rest)) if 0 < len(rest) <= 3 else (f" (+{len(rest)} more listings)" if rest else "")
    return tick(S, first, frm) + extra


def cat_note(cat):
    if cat in BL.CATEGORY_DIRECTION:
        d = BL.CATEGORY_DIRECTION[cat]
        return f"_Ledger category `{cat}`, direction {sgn(d)}{' (track only)' if d == 0 else ''}._"
    return f"_`{cat}`: listed for reading, not scored by the ledger._"


def headline(c):
    """One-line count of what a day holds ('–' = that input doesn't exist for the date)."""
    parts = [f"{c['signals']} S1 signal{'s' * (c['signals'] != 1)} ({c['awards']} DoD awards)" if c["dod"] or c["signals"] else "no DoD file",
             (f"{c['filings']} watchlist filing{'s' * (c['filings'] != 1)}" + (f" (+{c['filings_old']} older)" if c["filings_old"] else ""))
             if c["digest"] else "no watchlist digest",
             f"{c['market']} market-wide items" if c["market_scan"] else "no market-wide scan",
             f"{c['press_watch'] + c['press_kw']} press releases" if c["press_watch"] + c["press_kw"] else "no press releases",
             f"{c['setups']} new setup{'s' * (c['setups'] != 1)}" if c["setups"] else "no new setups",
             f"triage: {c['worth']} worth reading, {c['dismissed']} dismissed" if c["triage"] else "no triage"]
    return " · ".join(parts)


# ---------- sections ----------
def s1_section(S, d, frm):
    L = ["## S1 contract signals", ""]
    dod = S.dod.get(d)
    sig = [s for s in S.signals if s["date"] == d]
    if dod:
        src = [link("DoD file", dod["path"], frm)] + ([link("war.gov", dod["source"], frm)] if dod["source"] else [])
        L.append(f"DoD contracts announced {day(d)}: {dod['summary']} " + " · ".join(src))
    else:
        L.append("_No DoD contract file for this date (none is published at weekends)._")
    if sig:
        L += ["", "| ticker | awardee | type | value | market cap | materiality | decision | 5d before | found day | $vol/day | source |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in sig:
            mat = float(s["materiality"]) * 100 if s["materiality"] else None
            mat_s = "" if mat is None else f"{mat:.1f}%" if mat < 10 else f"{mat:.0f}%"
            ub = " (upper bound)" if "upper_bound" in s.get("notes", "") else ""
            lr = S.lx.get((s["ticker"], "s1_dod_contract", d))
            L.append(f"| {tick(S, s['ticker'], frm)} | {s['entity_raw']} | `{s['award_type']}` | {usd(float(s['value_usd'] or 0))} | "
                     f"{usd(float(s['mcap_usd'] or 0))} | {mat_s}{ub} | {s['decision']} | "
                     + " | ".join(ledger_cols(lr)) + f" | {link('war.gov', s['source_url'], frm)} |")
        if any("BACKFILL" in s.get("notes", "") for s in sig):
            L += ["", "_BACKFILL rows were detected after the fact and are excluded from forward stats (see `data/signals.csv` notes)._"]
    return L + [""]


def filings_section(S, d, frm):
    L = ["## Watchlist filings", ""]
    dg = S.digests.get(d)
    if not dg:
        return L + ["_No watchlist digest for this date._", ""]
    new = [f for f in dg["filings"] if not f["old"]]
    old = [f for f in dg["filings"] if f["old"]]
    refs = [link(f"deep read ({r['path'].rsplit('/', 1)[-1]})", r["path"], frm) for r in research_refs(dg["path"], S.research)]
    L.append(f"New SEC filings by watchlist companies (`watch/check_filings.py`): {len(new)}"
             + (f", plus {len(old)} older ones picked up for the first time" if old else "") + ". "
             + " · ".join([link("digest", dg["path"], frm)] + refs))
    L.append("")
    if new:
        L += ["| ticker | filed | form | what | filing |", "|---|---|---|---|---|"]
        for f in new:
            L.append(f"| {tick(S, f['ticker'], frm)} | {f['filed']} | `{f['form']}` | {f['what']} | {link('filing', f['link'], frm)} |")
        L.append("")
    by = {}
    for f in old:
        by.setdefault(f["ticker"], []).append(f)
    for t, fs in sorted(by.items()):
        span = f"{min(f['filed'] for f in fs):%d %b} – {max(f['filed'] for f in fs):%d %b %Y}"
        L.append(f"- {tick(S, t, frm)}: +{len(fs)} older filings (filed {span}) first picked up on this date, "
                 f"usually because the ticker was just added to the watchlist. Listed in the {link('digest', dg['path'], frm)}.")
    for n in dg["notes"]:
        L.append(f"- {n}")
    if not dg["filings"] and not dg["notes"]:
        L.append("No new filings of interest.")
    return L + [""]


def market_section(S, d, frm):
    L = ["## Market-wide scan", ""]
    mk = S.market.get(d)
    if not mk:
        return L + ["_No market-wide scan for this date._", ""]
    refs = [link(f"deep dive ({r['path'].rsplit('/', 1)[-1]})", r["path"], frm) for r in research_refs(mk["path"], S.research)]
    refs += [link(f"triage {td}", t["path"], frm) for td, t in sorted(S.triage.items()) if mk["path"] in t["text"]]
    L += [f"SEC filings on {day(d)}: {mk['filed']} filed, {mk['matched']} from listed companies match our event types "
          f"(`watch/scan_market.py`). " + " · ".join([link("source scan", mk["path"], frm)] + refs), "",
          "Price columns come from the ledger: the move over the 5 sessions before the found day, the found day's own move "
          "(scans run after the close), and average daily $ volume over the 20 sessions before (⚠ = under $250k, untradeable). "
          "Blank = no ledger row (no price data, or a category the ledger doesn't score).", ""]
    phrase_order = [c for _, c in BL.PHRASE_CATEGORY] + ["8k_other"]
    for sec in mk["sections"]:
        if sec["category"] == "8k":
            for cat in dict.fromkeys(phrase_order):
                items = [i for i in sec["items"] if i["category"] == cat]
                if not items:
                    continue
                has_items = any(i["items"] for i in items)   # older scans didn't record 8-K item numbers
                L += [f"### 8-K: {label(cat).replace('8-K ', '')} · {len(items)}", "", cat_note(cat), "",
                      "| ticker | phrases | " + ("items | " if has_items else "") + "5d before | found day | $vol/day | 8-K |",
                      "|---|---|" + ("---|" if has_items else "") + "---|---|---|---|"]
                for it in items:
                    lr = S.lx.get((it["ticker"], it["ledger_category"], d))
                    L.append(f"| {tickers_cell(S, it['tickers'], frm)} | {plain(it['what'])} | " + (f"{it['items'] or '?'} | " if has_items else "")
                             + " | ".join(ledger_cols(lr)) + " | " + " ".join(link("8-K" if i == 0 else str(i + 1), u, frm) for i, u in enumerate(it["links"])) + " |")
                L.append("")
        else:
            items = sec["items"]
            L += [f"### {sec['heading']} · {len(items)}", "", cat_note(sec["category"]), "",
                  "| ticker | company | form | 5d before | found day | $vol/day | filing |", "|---|---|---|---|---|---|---|"]
            for it in items:
                lr = S.lx.get((it["ticker"], it["ledger_category"], d))
                form = f"`{it['form']}`" + (f" ×{it['count']}" if it.get("count") else "")
                L.append(f"| {tickers_cell(S, it['tickers'], frm)} | {it['what']} | {form} | " + " | ".join(ledger_cols(lr)) + " | "
                         + " ".join(link("filing" if i == 0 else str(i + 1), u, frm) for i, u in enumerate(it["links"])) + " |")
            L.append("")
        for e in sec["errors"]:
            L += [f"- {e}", ""]
    return L


def press_section(S, d, frm):
    L = ["## Press releases", ""]
    rs = S.press.get(d)
    if not rs:
        return L + ["_No press releases first seen on this date._", ""]
    watch = [r for r in rs if is_watch_press(r)]
    kw = [r for r in rs if not is_watch_press(r)]
    digest = f"watch/press/{d}.md"
    L.append(f"Company releases first seen on this date by `collectors/press_wires.py` (trusted wires and company IR feeds): "
             f"{len(watch)} watchlist / position hits, {len(kw)} keyword hits. "
             + " · ".join(([link("press digest", digest, frm)] if (ROOT / digest).exists() else []) + [link("CSV", f"data/press/{d}.csv", frm)]))

    def line(r):
        ts = r["ticker"].split(";")
        pub = r["published_utc"][:16].replace("T", " ") + "Z" if r["published_utc"] else "undated"
        return (f"- {'/'.join(tick(S, t, frm) for t in ts)} ({r['exchange']}) · {r['wire']} · published {pub}: "
                f"{link(r['title'], r['link'], frm)} · matched `{r['matched_on'].replace(';', '; ')}`")
    for title, group in (("Watchlist / position hits", watch), ("Keyword hits (NYSE / Nasdaq / NYSE American only)", kw)):
        if group:
            L += ["", f"**{title}**", ""] + [line(r) for r in group]
    return L + [""]


def setups_section(S, d, frm):
    L = ["## New setups", ""]
    ms = [m for m in S.manual if m["found"] == d]
    if not ms:
        return L + ["_No ideas or setups logged on this date._", ""]
    L += [f"Ideas and watch-only setups logged on this date in {link('ledger/manual_calls.csv', 'ledger/manual_calls.csv', frm)} "
          f"({len(ms)}). Each ticker links to its dossier; the ledger tracks it from the next session's open.", "",
          "| ticker | category | dir | note | source | found @ | 5d before | found day | $vol/day |", "|---|---|---|---|---|---|---|---|---|"]
    for m in ms:
        lr = S.lx.get((m["ticker"], m["category"], d))
        L.append(f"| {tick(S, m['ticker'], frm)} | `{m['category']}` | {sgn(m['direction'])} | {m['note']} | {m['source']} | "
                 f"{price(lr['found_close']) if lr else ''} | " + " | ".join(ledger_cols(lr)) + " |")
    return L + [""]


def triage_section(S, d, frm):
    L = ["## Triage notes", ""]
    tr = S.triage.get(d)
    if not tr:
        return L + ["_No evening triage for this date._", ""]
    L.append(f"{tr['title']}: {len(tr['worth'])} worth reading, {len(tr['dismissed'])} dismissed. "
             + link("full triage", tr["path"], frm))
    if tr["worth"]:
        L += ["", "**Worth reading**", ""]
        for b in tr["worth"]:
            src = [link(lbl or "link", u, frm) for lbl, u in b["links"][:3]]
            L.append(f"- {triage_summary(b, 420)}" + (" " + " · ".join(src) if src else ""))
    if tr["dismissed"]:
        L += ["", "**Dismissed:** " + " · ".join(clip(plain(b["lead"]), 90) for b in tr["dismissed"]).rstrip(".…")
              + f". Reasons in the {link('full triage', tr['path'], frm)}."]
    return L + [""]


def other_files(S, d, frm):
    files = [(f"Morning briefing {d}", f"briefings/{d}.md"), (f"Market context {d}", f"watch/context/{d}.md")]
    out = [link(t, p, frm) for t, p in files if (ROOT / p).exists()]
    out += [link(r["title"], r["path"], frm) for r in S.research if r["date"] == d]
    return ["## Other files for this date", ""] + [f"- {x}" for x in out] + [""] if out else []


def render(S, d):
    frm = f"scans/{d}.md"
    dates = S.scan_dates()
    i = dates.index(d)
    nav = ([link(f"← {day(dates[i - 1])}", f"scans/{dates[i - 1]}.md", frm)] if i > 0 else []) + [link("all scans", "scans/README.md", frm)] \
        + ([link(f"{day(dates[i + 1])} →", f"scans/{dates[i + 1]}.md", frm)] if i + 1 < len(dates) else [])
    L = [f"# Scan: {long_day(d)}", "", " · ".join(nav), "",
         "Everything the pipeline found on this date, in one file. Built by `reports/build_scans.py` from the source files "
         "linked in each section: fix those, not this file.", "",
         f"**Found:** {headline(S.counts(d))}", ""]
    for sec in (s1_section, filings_section, market_section, press_section, setups_section, triage_section, other_files):
        L += sec(S, d, frm)
    while L and not L[-1]:
        L.pop()
    return "\n".join(L) + "\n"


def index(S):
    frm = "scans/README.md"
    L = ["# Daily scans", "",
         "One file per date with everything the pipeline found that day: S1 contract signals, watchlist filings, the "
         "market-wide SEC scan, press releases, new setups and the evening triage. Built by `reports/build_scans.py` in the "
         "weekday `morning-briefing` workflow. Newest first. A dash means that input doesn't exist for the date.", "",
         "| date | S1 signals (DoD awards) | watchlist filings | market-wide items | press (watch / keyword) | new setups | triage (worth / dismissed) |",
         "|---|---|---|---|---|---|---|"]
    for d in reversed(S.scan_dates()):
        c = S.counts(d)
        cells = [f"{c['signals']} ({c['awards']})" if c["dod"] or c["signals"] else "–",
                 (f"{c['filings']}" + (f" (+{c['filings_old']} older)" if c["filings_old"] else "")) if c["digest"] else "–",
                 str(c["market"]) if c["market_scan"] else "–",
                 f"{c['press_watch']} / {c['press_kw']}" if c["press_watch"] + c["press_kw"] else "–",
                 str(c["setups"]) if c["setups"] else "–",
                 f"{c['worth']} / {c['dismissed']}" if c["triage"] else "–"]
        L.append(f"| {link(long_day(d), f'scans/{d}.md', frm)} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", help="build one date, YYYY-MM-DD")
    ap.add_argument("--all", action="store_true", help="rebuild every date that has any input")
    a = ap.parse_args()
    S = Sources()
    dates = S.scan_dates()
    if a.date:
        want = [dt.date.fromisoformat(a.date)]
    elif a.all:
        want = dates
    else:
        want = [d for d in dates if d > TODAY - dt.timedelta(days=LOOKBACK_DAYS) or not (ROOT / f"scans/{d}.md").exists()]
    changed = []
    for d in want:
        if d not in dates:
            print(f"{d}: no input for this date, nothing written")
            continue
        if write(f"scans/{d}.md", render(S, d)):
            changed.append(str(d))
    idx = write("scans/README.md", index(S))
    print(f"scans: {len(want)} date(s) checked, {len(changed)} written{': ' + ', '.join(changed) if changed else ''}"
          f"; index {'updated' if idx else 'unchanged'}")


if __name__ == "__main__":
    main()
