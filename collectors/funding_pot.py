"""How much of a capped funding pot is already promised? -> watch/pots/OFFICE.md and watch/pots/latest.json

The lesson behind it (5 Oct 2026): the National Defense Stockpile ceilings were first counted as ~$4.0bn
from one month of DoD announcements. USAspending showed 21 more IDIQs from the same office: ~$9.3bn of
ceilings against $2bn, and ~$1.1bn already ordered. So for every capped fund in watch/pots.json this
totals ALL of the office's awards since the fund started, never one month.

  ceilings  = every IDIQ (USAspending, award IDs starting with the office code) + recent awards it doesn't show yet
  ordered   = every funded delivery order on those IDIQs + recent orders it doesn't show yet
  committed = ordered as a share of the money

Usage: python collectors/funding_pot.py        (all pots; runs in the morning workflow)
"""
import json, time, urllib.request, datetime as dt
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.usaspending.gov/api/v2"
IDV = ["IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D", "IDV_E"]
ORDERS = ["A", "B", "C", "D"]


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=90))


def get(path):
    return json.load(urllib.request.urlopen(API + path, timeout=60))


def search(office, codes, since):
    out, page = [], 1
    while True:
        r = post("/search/spending_by_award/", {
            "filters": {"keywords": [office], "award_type_codes": codes,
                        "time_period": [{"start_date": since, "end_date": dt.date.today().isoformat()}]},
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Start Date", "generated_internal_id"],
            "limit": 100, "page": page, "sort": "Award Amount", "order": "desc"})
        # Only awards that START after the fund did: older IDIQs with activity in the window were paid from older money.
        out += [x for x in r["results"] if str(x.get("Award ID", "")).startswith(office) and str(x.get("Start Date") or "") >= since]
        if not r.get("page_metadata", {}).get("hasNext"): return out
        page += 1; time.sleep(0.3)


def money(v):
    return f"${v / 1e9:.2f}bn" if v >= 1e9 else f"${v / 1e6:.1f}M"


def run(office, cfg):
    idvs = search(office, IDV, cfg["since"])
    ceilings = []
    for x in idvs:
        try:
            a = get(f"/awards/{x['generated_internal_id']}/"); time.sleep(0.2)
            ceilings.append((x["Recipient Name"], x["Award ID"], x["Start Date"], a.get("base_and_all_options") or 0))
        except Exception:
            ceilings.append((x["Recipient Name"], x["Award ID"], x["Start Date"], 0))
    orders = search(office, ORDERS, cfg["since"])
    ordered = defaultdict(float)
    for x in orders:
        ordered[x["Recipient Name"]] += x.get("Award Amount") or 0
    extra = cfg.get("not_yet_in_usaspending", [])
    c_total = sum(c[3] for c in ceilings) + sum(e["ceiling_usd"] for e in extra)
    o_total = sum(ordered.values()) + sum(e["ordered_usd"] for e in extra)
    m = cfg["money_usd"]
    summary = {"office": office, "name": cfg["name"], "money_usd": m, "ceilings_usd": c_total, "ordered_usd": o_total,
               "committed_pct": round(o_total / m * 100, 1), "ceiling_multiple": round(c_total / m, 2),
               "idiqs": len(ceilings) + sum(1 for e in extra if e["ceiling_usd"]), "tickers": cfg.get("tickers", []),
               "updated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")}
    L = [f"# Funding pot: {cfg['name']} ({office})", "",
         f"Built by `collectors/funding_pot.py` on {summary['updated']} from USAspending (every award from office `{office}` since "
         f"{cfg['since']}), plus recent awards USAspending doesn't show yet (DoD data lags ~90 days).", "",
         f"- **Money:** {money(m)}. {cfg['money_source']}",
         f"- **Ceilings promised:** {money(c_total)} on {summary['idiqs']} IDIQs, **{summary['ceiling_multiple']}x the money**",
         f"- **Actually ordered:** {money(o_total)}, **{summary['committed_pct']}% of the money**",
         f"- **Watchlist stocks paid from it:** {', '.join(cfg.get('tickers', [])) or 'none'}", "",
         "A ceiling is a promise to buy up to an amount; only funded orders spend the money. When orders approach the money, "
         "further orders need a new appropriation.", "",
         "## Funded orders by recipient", "", "| recipient | ordered |", "|---|---|"]
    rows = sorted(list(ordered.items()) + [(e["recipient"] + " (not yet on USAspending)", e["ordered_usd"]) for e in extra if e["ordered_usd"]],
                  key=lambda r: -r[1])
    L += [f"| {n} | {money(v)} |" for n, v in rows]
    L += ["", "## Every IDIQ (ceiling)", "", "| recipient | award | start | ceiling |", "|---|---|---|---|"]
    L += [f"| {n} | [{aid}](https://www.usaspending.gov/award/CONT_IDV_{aid}_9700/) | {d} | {money(c)} |"
          for n, aid, d, c in sorted(ceilings, key=lambda c: -c[3])]
    L += [f"| {e['recipient']} | [not yet on USAspending]({e['source']}) | {e['date']} | {money(e['ceiling_usd'])} |" for e in extra if e["ceiling_usd"]]
    out = ROOT / "watch/pots"; out.mkdir(parents=True, exist_ok=True)
    (out / f"{office}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return summary


def main():
    cfg = json.load(open(ROOT / "watch/pots.json", encoding="utf-8"))["pots"]
    res = {}
    for office, c in cfg.items():
        try:
            res[office] = run(office, c)
            s = res[office]
            print(f"{office}: ceilings {money(s['ceilings_usd'])} ({s['ceiling_multiple']}x), ordered {money(s['ordered_usd'])} "
                  f"({s['committed_pct']}% of {money(s['money_usd'])})")
        except Exception as e:
            print(f"{office}: failed ({e})")
    if res:
        (ROOT / "watch/pots/latest.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
