"""Charts for the peaks-and-times part: (5) the path at actual times around a filing, (6) each pick's low, peak and now."""
import sys, pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statistics import median
from core import *
sys.stdout.reconfigure(encoding="utf-8")
OUT = HERE / "img"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": SURF})
NL = chr(10)
ev = pickle.load(open(HERE / "events.pkl", "rb"))
def first(es):
    s, o = set(), []
    for e in es:
        if e["ticker"] not in s: s.add(e["ticker"]); o.append(e)
    return o
def path(es):
    pts = [0.0]
    cum = lambda e, k: ((1 + e["gap"] / 100) * (1 + e[k] / 100) - 1) * 100 if e.get(k) is not None else None
    pts.append(median(e["gap"] for e in es))
    for k in ("r30", "r60", "r120", "rclose", "rnext", "r3"):
        v = [cum(e, k) for e in es if cum(e, k) is not None]; pts.append(median(v))
    return pts
groups = [("Scanner buy-side flags (n=%d)", ["8k_strategic_review", "activist_13d", "tender_issuer_buyback"]),
          ("Scanner supply flags (n=%d)", ["8k_reverse_split", "registration_effective", "share_registration"]),
          ("Signed deals and tenders (n=%d)", ["8k_merger_agreement", "8k_tender_offer", "tender_third_party", "merger_vote"])]
labels = ["last trade" + NL + "before filing", "first open" + NL + "we could get", "+30 min", "+1 hour", "+2 hours", "that close", "next close", "3rd close"]
fig, ax = plt.subplots(figsize=(9.8, 5.6)); fig.subplots_adjust(top=0.80, bottom=0.16, left=0.08, right=0.73)
ends = []
for (lab, cats), col in zip(groups, C):
    es = first([e for e in ev if e["cat"] in cats and e["take"]]); p = path(es)
    ax.plot(range(8), p, color=col, lw=2.2, marker="o", ms=5, mec=SURF, mew=1.2)
    ends.append([p[-1], lab % len(es), col])
    print(lab % len(es), [round(x, 2) for x in p])
ends.sort(key=lambda e: e[0]); ypos = [e[0] for e in ends]
for i in range(1, len(ypos)): ypos[i] = max(ypos[i], ypos[i - 1] + 0.75)
for (v, lab, col), y in zip(ends, ypos):
    ax.plot([7.08, 7.3], [v, y], color=col, lw=1); ax.text(7.35, y, f"{lab}{NL}{v:+.1f}% by the 3rd close", va="center", fontsize=9.5, color=INK)
ax.axhline(0, color=INK2, lw=0.8); ax.set_xticks(range(8)); ax.set_xticklabels(labels, fontsize=9.5); ax.set_xlim(-0.2, 7.1)
ax.set_ylabel("median move from the last trade before the filing (%)"); ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
fig.text(0.02, 0.965, "At actual times: the buy side is flat from the open; supply slides from hour one", fontsize=14.5, fontweight="bold", va="top")
fig.text(0.02, 0.915, "Every scanner flag timed from its SEC acceptance stamp, on 5-minute bars. Takeable names, first flag per stock.", fontsize=10.5, color=INK2, va="top")
fig.text(0.02, 0.012, "95% of these filings arrived outside market hours, so the first price we could get was the next open. 18 Aug to 9 Nov 2026.", fontsize=8.5, color=INK2, va="bottom")
fig.savefig(OUT / "5-times.png", dpi=170); plt.close(fig)

# ---- 6. low / peak / now for every pick ----
PICKS = [("2026-10-05","MTUS",1),("2026-10-05","RYAM",1),("2026-10-05","MOD",1),("2026-10-05","THRM",1),("2026-10-05","WHF",1),("2026-10-05","CTVA",1),("2026-10-05","VYLR",1),("2026-10-05","HMH",1),("2026-10-06","ESRT",0),("2026-10-10","MSGS",1),("2026-10-12","BORR",2),("2026-10-12","SKYA",0),("2026-10-14","PED",0),("2026-10-15","IMSR",2),("2026-10-16","SRTA",0),("2026-10-20","DIBS",0),("2026-10-20","ACB",0),("2026-10-21","XPOF",0),("2026-10-22","CPAC",0),("2026-10-23","DOLE",0),("2026-11-01","SEER",0),("2026-11-05","VVR",0)]
KN = ["An outside buyer or holder acting", "The company's own story or event", "Insiders buying"]
rows = [(d, t, k, excursion(t, d)) for d, t, k in PICKS]
rows.sort(key=lambda r: -r[3]["peak"])
fig, ax = plt.subplots(figsize=(9.6, 7.8)); fig.subplots_adjust(top=0.80, bottom=0.09, left=0.17, right=0.95)
for i, (d, t, k, x) in enumerate(rows):
    ax.plot([x["trough"], x["peak"]], [i, i], color=C[k], lw=5, solid_capstyle="round", alpha=0.95)
    ax.plot([x["now"]], [i], "o", color=SURF, ms=9, mec=INK, mew=1.8, zorder=3)
    ax.text(x["peak"] + 1.5, i, f"{x['peak']:+.0f}% on {x['peak_date'].strftime('%d %b')}", va="center", fontsize=9, color=INK)
    ax.text(x["trough"] - 1.5, i, f"{x['trough']:+.0f}%", va="center", ha="right", fontsize=9, color=INK2)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{t}  {d[8:]}/{d[5:7]}" for d, t, k, x in rows], color=INK); ax.invert_yaxis()
ax.axvline(0, color=INK2, lw=0.8); ax.set_xlim(-66, 66); ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlabel("% from the first open after the verdict (bar: lowest low to highest high; ring: 9 Nov close)")
import matplotlib.patches as mp, matplotlib.lines as ml
h = [mp.Patch(color=C[k], label=KN[k]) for k in range(3)] + [ml.Line2D([], [], marker="o", ls="", color=SURF, mec=INK, mew=1.8, ms=9, label="where it closed on 9 Nov")]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.015, 0.905), frameon=False, fontsize=9.5, ncol=2, handlelength=1.2)
fig.text(0.02, 0.965, "What each pick peaked at, how low it went, and where it is now", fontsize=14.5, fontweight="bold", va="top")
fig.text(0.02, 0.925, "22 OWN and WATCH verdicts. Intraday highs and lows, adjusted for dividends and splits.", fontsize=10.5, color=INK2, va="top")
fig.savefig(OUT / "6-peaks.png", dpi=170); plt.close(fig)
print("ok")
