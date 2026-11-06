"""Every stock the research flagged, and how it has done since the day we found it.

Run:  python ledger/build_found.py
Out:  research/found/found.csv (every name), research/found/README.md, research/found/img/*.png (X images)

Sources (what we thought on the day):
- AVOID      ledger/avoid_register.csv: we expected the stock to fall (share supply or distress)
- WATCH/OWN  ledger/triggers.csv WATCH rows and the OWN dossier verdict: we expected it to rise if the trigger fired
- TRACKED    ledger/manual_calls.csv and TRACKED triggers: a real event, but no call, grouped by strategy
Measured like the ledger: from the OPEN of the next session after the find (the first price anyone could act on)
to the latest close, against IWM over the same window. The images show takeable names only ($1+ and a 20-day
median of $150k a day on the found day), the same rule as the headline numbers (ledger/RULES.md).
"""
import csv, json, sys, time, urllib.request, datetime as dt
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/found"
sys.path.insert(0, str(ROOT / "calls"))
from build_calls import bars  # Yahoo daily bars with recorded splits applied

SUPPLY = {"ongoing_supply": "Ongoing share sales (ATMs, equity lines)", "warrant_supply": "Warrants",
          "distress": "Distress (going concern, delisting, splits)", "holder_selling": "Holders free to sell",
          "deal_dilution": "Deal dilution", "one_off_offering": "One-off offerings", "other": "Other", "kill": "Killed long ideas"}
STRATEGY = {  # manual_calls category -> tracked group; None = not a find of ours (peers, acquirers)
    **dict.fromkeys(["merger_arb", "tender_issuer", "tender_issuer_buyback", "takeover_proposal", "merger_hostile",
                     "merger_cvr", "going_private", "issuer_tender_intent", "deal_dispute", "deal_reaction",
                     "exchange_offer_missed", "idea_merger", "mergerarb"], "Merger arb and tenders"),
    **dict.fromkeys(["activist_13d", "holder_buying", "activist_deep_dive", "holder_13d", "holder_13g",
                     "strategic_placement", "activist"], "Activists and big holders"),
    **dict.fromkeys(["insider_cluster", "insider_buy", "buyback"], "Insider buying"),
    "below_cash": "Below cash or book",
    **dict.fromkeys(["spin_off", "idea_spinoff", "spinoff"], "Spin-offs"),
    **dict.fromkeys(["longterm_research", "idea_catalyst", "idea_contract_press", "event_incident", "govfilings"],
                    "Contracts and catalysts"),
    "overhang": "Lock-up overhang",
}


def rows_in(path):
    p = ROOT / path
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def finds():
    out = []
    for r in rows_in("ledger/avoid_register.csv"):
        if r["status"] == "reclassified": continue
        out.append(dict(ticker=r["ticker"], found=r["date"], view="AVOID", group=SUPPLY.get(r["supply_type"], "Other"),
                        takeable=r["takeable_at_call"], why=r["reason"]))
    for r in rows_in("ledger/triggers.csv"):
        view = "WATCH" if r["verdict"] == "WATCH" else "TRACKED"
        out.append(dict(ticker=r["ticker"], found=r["set_date"], view=view, group=STRATEGY.get(r["strategy"], "Other"),
                        takeable="", why=r["trigger"]))
    for r in rows_in("ledger/verdicts.csv"):
        if r["verdict"].upper().startswith("OWN"):
            out.append(dict(ticker=r["ticker"], found=r["date"], view="OWN", group="Contracts and catalysts",
                            takeable="", why="dossier verdict OWN"))
    for r in rows_in("ledger/manual_calls.csv"):
        g = STRATEGY.get(r["category"])
        if g: out.append(dict(ticker=r["ticker"], found=r["found"], view="TRACKED", group=g, takeable="", why=r["note"]))
    # one row per ticker and view, kept at the first date we logged it in that view
    best = {}
    for f in sorted(out, key=lambda f: f["found"]):
        best.setdefault((f["ticker"], f["view"]), f)
    return list(best.values())


def names():
    req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json",
                                 headers={"User-Agent": "PersonalResearch research@example.com"})
    try:
        return {v["ticker"]: v["title"] for v in json.load(urllib.request.urlopen(req, timeout=30)).values()}
    except Exception:
        return {}


def measure(f, iwm):
    b = bars(f["ticker"])
    d0 = dt.date.fromisoformat(f["found"])
    before = [x for x in b if x[0] <= d0][-20:]
    after = [x for x in b if x[0] > d0]
    if not after: return None
    ed, eo, now_d, now = after[0][0], after[0][1], after[-1][0], after[-1][2]
    if f["takeable"] not in ("yes", "no"):
        # bars carry no volume, so judge on price alone here; the register's own flag wins where it exists
        f["takeable"] = "yes" if before and before[-1][2] >= 1 else "no"
    im = {d: (o, c) for d, o, c, _ in iwm}
    iw = (im[now_d][1] / im[ed][0] - 1) * 100 if ed in im and now_d in im else None
    pct = (now / eo - 1) * 100
    return dict(entry_date=ed.isoformat(), entry=round(eo, 4), now_date=now_d.isoformat(), now=round(now, 4),
                pct=round(pct, 1), iwm=None if iw is None else round(iw, 1),
                vs_iwm=None if iw is None else round(pct - iw, 1))


def right(r):
    """AVOID is right if the stock did worse than IWM; a long view (WATCH, OWN) if it did better."""
    if r["vs_iwm"] is None or r["view"] == "TRACKED": return None
    return r["vs_iwm"] < 0 if r["view"] == "AVOID" else r["vs_iwm"] > 0


def render(rows, title, sub, path, down_good):
    """down_good: True for AVOID images (a fall is green), False for long views, None for the all-in-one image,
    where each row is coloured by its own view and the view is printed in place of the name."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    per, cw = max(34, -(-len(rows) // 4)), 6.2
    cols = max(1, -(-len(rows) // per))
    W = max(cw * cols, 10.0)
    cw = W / cols
    h = 1.6 + 0.26 * min(len(rows), per) + 0.75
    fig = plt.figure(figsize=(W, h), dpi=150)
    X = lambda c, dx: (c * cw + dx * cw) / W  # column c, offset dx (share of one column) -> figure fraction
    fig.patch.set_facecolor("#0f1115")
    fig.text(0.012, 1 - 0.42 / h, title, color="white", fontsize=17, weight="bold", va="top")
    fig.text(0.012, 1 - 0.95 / h, sub, color="#a9b1bd", fontsize=10.5, va="top")
    good, bad, grey = "#3ecf8e", "#ff6b6b", "#c9d1d9"
    for c in range(cols):
        chunk = rows[c * per:(c + 1) * per]
        y = 1 - 1.45 / h
        heads = [("Ticker", 0.02), ("Name", 0.15), ("Found", 0.60), ("Since", 0.76), ("vs IWM", 0.89)]
        for t, dx in heads:
            fig.text(X(c, dx), y, t, color="#7d8590", fontsize=9.5, weight="bold", va="top")
        for i, r in enumerate(chunk):
            yy = y - (i + 1) * 0.26 / h
            dg = (r["view"] == "AVOID") if down_good is None else down_good
            neutral = r["view"] == "TRACKED"  # no call, so no colour
            col = grey if neutral else ((good if r["pct"] < 0 else bad) if dg else (good if r["pct"] > 0 else bad))
            vcol = grey if neutral or r["vs_iwm"] is None else ((good if r["vs_iwm"] < 0 else bad) if dg else (good if r["vs_iwm"] > 0 else bad))
            fig.text(X(c, 0.02), yy, r["ticker"], color="white", fontsize=10, weight="bold", va="top", family="monospace")
            label = (r["name"] or "")[:24] if down_good is not None else f"{r['view']:<8}{(r['name'] or '')[:15]}"
            fig.text(X(c, 0.15), yy, label, color=grey, fontsize=9.5, va="top")
            fig.text(X(c, 0.60), yy, dt.date.fromisoformat(r["found"]).strftime("%d %b"), color=grey, fontsize=9.5, va="top")
            fig.text(X(c, 0.76), yy, f"{r['pct']:+.1f}%", color=col, fontsize=10, va="top", family="monospace")
            fig.text(X(c, 0.89), yy, "" if r["vs_iwm"] is None else f"{r['vs_iwm']:+.1f}", color=vcol, fontsize=10, va="top", family="monospace")
    fig.text(0.012, 0.22 / h, "Measured from the next open after we flagged it, to the latest close. Takeable names only ($1+).\n"
             "Research, not trades or advice. Every name: github.com/astonmonnach/signal-research", color="#7d8590",
             fontsize=8.5, va="bottom", linespacing=1.5)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def summary(rs, view):
    ok = [right(r) for r in rs if right(r) is not None]
    med = median([r["pct"] for r in rs]) if rs else 0
    if view == "AVOID":
        return f"{len(rs)} names · median {med:+.1f}% since found · fell more than IWM: {sum(ok)}/{len(ok)}"
    if view == "TRACKED":
        return f"{len(rs)} names · median {med:+.1f}% since found · no call, so nothing to score"
    return f"{len(rs)} names · median {med:+.1f}% since found · beat IWM: {sum(ok)}/{len(ok)}"


def main():
    nm = names()
    iwm = bars("IWM")
    rows = []
    for f in finds():
        m = measure(f, iwm)
        if m:
            n = nm.get(f["ticker"], "")
            rows.append(dict(f, name=n.title() if n.isupper() else n, **m))
        time.sleep(0.05)
    rows.sort(key=lambda r: (r["view"], r["group"], r["found"], r["ticker"]))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "img").mkdir(exist_ok=True)
    cols = ["ticker", "name", "view", "group", "found", "takeable", "entry_date", "entry", "now_date", "now", "pct", "iwm", "vs_iwm", "why"]
    with open(OUT / "found.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    asof = max(r["now_date"] for r in rows)
    day = dt.date.fromisoformat(asof)
    tk = [r for r in rows if r["takeable"] == "yes"]
    # one image of everything (one row per ticker, its main view), then one per view and group
    main_view = {}
    for r in sorted(tk, key=lambda r: ("AVOID", "WATCH", "OWN", "TRACKED").index(r["view"])):
        main_view.setdefault(r["ticker"], r)
    every = sorted(main_view.values(), key=lambda r: r["pct"])
    images = [("all", every, "Every stock we flagged, since the day we found it",
               f"As of the {day.day} {day:%b} close · {len(every)} takeable names · AVOID = we expected it to fall, "
               "WATCH/OWN = rise, TRACKED = no call", None)]
    for view in ("AVOID", "WATCH", "OWN", "TRACKED"):
        vr = [r for r in tk if r["view"] == view]
        if not vr: continue
        if view in ("WATCH", "OWN"):
            images.append((view.lower(), sorted(vr, key=lambda r: r["pct"]), f"{view}", "We expected these to rise · " + summary(vr, view), False))
            continue
        for g in sorted({r["group"] for r in vr}):
            gr = sorted([r for r in vr if r["group"] == g], key=lambda r: r["pct"])
            if len(gr) < 2: continue
            lead = "We expected these to fall · " if view == "AVOID" else ""
            images.append((f"{view.lower()}-{g.split()[0].lower()}", gr, f"{view.title() if view == 'TRACKED' else view}: {g}",
                           lead + summary(gr, view), view == "AVOID"))
    for slug, rs, title, sub, down in images:
        render(rs, title, sub, OUT / f"img/{slug}.png", down)
    L = [f"# Every stock we flagged: how it has done since we found it", "",
         f"As of the {asof} close. Measured from the next open after the find, against IWM over the same window. "
         "AVOID is right when the stock does worse than IWM; WATCH and OWN when it does better; TRACKED had no call. "
         f"Takeable names only in the summary ($1+); every name is in [found.csv](found.csv). Images: [img/](img/).", "",
         "| view | group | names | median since found | right |", "|---|---|---|---|---|"]
    for view in ("AVOID", "WATCH", "OWN", "TRACKED"):
        for g in sorted({r["group"] for r in tk if r["view"] == view}):
            gr = [r for r in tk if r["view"] == view and r["group"] == g]
            ok = [right(r) for r in gr if right(r) is not None]
            L.append(f"| {view} | {g} | {len(gr)} | {median([r['pct'] for r in gr]):+.1f}% | "
                     + (f"{sum(ok)}/{len(ok)}" if ok else "n/a") + " |")
    L += ["", f"Not takeable (under $1 or illiquid on the day), left out above: {len(rows) - len(tk)} rows.", ""]
    (OUT / "README.md").write_text("\n".join(L), encoding="utf-8")
    print(f"found: {len(rows)} rows ({len(tk)} takeable) -> {OUT.relative_to(ROOT)}; images: {len(images)}")


if __name__ == "__main__":
    main()
