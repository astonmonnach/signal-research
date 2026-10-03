"""Run the PREREG.md carry test exactly as frozen. Outputs RESULTS.md."""
import pandas as pd, numpy as np
RT_COST = 0.0031          # both legs, entry+exit
CAP_MULT = 1 + 1/3        # spot N + perp margin N/3
d = pd.read_csv("hl_btc_funding.csv")
d["t"] = pd.to_datetime(d.time_ms, unit="ms", utc=True)
d = d.set_index("t").sort_index()
r = d.funding_rate.astype(float)

def run(gated):
    if gated:
        sig = r.rolling(24).mean().shift(1) > 0          # known before the hour
        pos = sig.astype(float).fillna(0)
    else:
        pos = pd.Series(1.0, index=r.index)
    pnl = pos * r                                         # per-hour carry on N
    switches = (pos.diff().abs() > 0).sum() + (1 if pos.iloc[0] > 0 else 0)
    trips = switches / 2
    cost_series = pd.Series(0.0, index=r.index)
    chg = pos.diff().fillna(pos.iloc[0]).abs()
    cost_series[chg > 0] = RT_COST / 2                    # half a round trip at each entry/exit
    if not gated: cost_series.iloc[-1] += RT_COST / 2     # exit at the end
    net = pnl - cost_series
    return net, int(switches), pos

def stats(net, label):
    yrs = (net.index[-1] - net.index[0]).total_seconds() / (365.25 * 86400)
    tot = net.sum()
    ann_n = tot / yrs
    cum = net.cumsum()
    dd = (cum - cum.cummax()).min()
    monthly = net.resample("ME").sum()
    return {"period": label, "years": round(yrs, 2), "net_total_on_N_%": round(tot * 100, 2),
            "ann_on_N_%": round(ann_n * 100, 2), "ann_on_capital_%": round(ann_n / CAP_MULT * 100, 2),
            "pct_months_positive": round((monthly > 0).mean() * 100, 1), "worst_dd_on_N_%": round(dd * 100, 2)}

out = ["# Results: Hyperliquid BTC funding carry (spec frozen in PREREG.md)", ""]
for gated, name in ((False, "V1 always-on"), (True, "V2 gated (24h mean > 0)")):
    net, sw, pos = run(gated)
    rows = [stats(net, "ALL"), stats(net[:"2024-12-31"], "IS 2023-05→2024"), stats(net["2025-01-01":], "OOS 2025→2026-10")]
    by_year = net.groupby(net.index.year).sum() * 100
    oos = rows[2]; full_years = by_year.loc[[y for y in by_year.index if y in (2024, 2025)]]
    passed = oos["ann_on_capital_%"] > 0 and (full_years > 0).all()
    out += [f"## {name}", f"Switches: {sw}  |  time in carry: {pos.mean()*100:.1f}%", "",
            "| period | years | net on N | annualised on N | annualised on capital | months + | worst DD (on N) |",
            "|---|---|---|---|---|---|---|"]
    out += [f"| {x['period']} | {x['years']} | {x['net_total_on_N_%']}% | {x['ann_on_N_%']}% | **{x['ann_on_capital_%']}%** | {x['pct_months_positive']}% | {x['worst_dd_on_N_%']}% |" for x in rows]
    out += ["", "By calendar year (net on N, partial years marked): " + ", ".join(
        f"{y}{'*' if y in (2023, 2026) else ''}: {v:+.2f}%" for y, v in by_year.items()), "",
        f"**Verdict: {'PASS' if passed else 'FAIL'}** (OOS annualised on capital > 0 and full years 2024, 2025 > 0)", ""]
mean_ann = r.mean() * 24 * 365 * 100
out += ["## Context", f"Mean hourly funding annualised (gross, always short): {mean_ann:.2f}% on N. "
        f"Share of hours with negative funding: {(r < 0).mean()*100:.1f}%.",
        "Not modelled: spot–perp basis moves, liquidation of the short in a fast squeeze (3x margin), exchange risk."]
open("RESULTS.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
