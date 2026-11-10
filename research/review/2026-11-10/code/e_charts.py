"""Charts for the two-month review. Light surface, validated categorical palette (dataviz skill reference palette),
direct labels, one axis each. Text is ink, never the series colour."""
import sys, pickle, csv, bisect
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from bench import *

sys.stdout.reconfigure(encoding="utf-8")
OUT = HERE / "img"; OUT.mkdir(exist_ok=True)
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": SURF})


def title(fig, t, sub):
    fig.text(0.02, 0.965, t, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.915, sub, fontsize=10.5, color=INK2, va="top")


def foot(fig, s):
    fig.text(0.02, 0.012, s, fontsize=8.5, color=INK2, va="bottom")


# ---- 1. What ordinary unflagged stocks did, by price ----
entries = [d for d in IDATES if dt.date(2026, 9, 21) <= d <= dt.date(2026, 10, 12)]
vals = {pb: [] for pb in range(4)}
iw = []
for ed in entries:
    cp = ctrl_paths(ed)
    for (pb, cb), ps in cp.items():
        vals[pb] += [(p[19], w) for p, w in ps if len(p) > 19]
    i = bisect.bisect_left(IDATES, ed)
    iw.append((IWM[i + 19][2] / IWM[i][1] - 1) * 100)
med = [wmedian(vals[pb]) for pb in range(4)]
fig, ax = plt.subplots(figsize=(9, 5.2)); fig.subplots_adjust(top=0.80, bottom=0.14, left=0.09, right=0.97)
bars = ax.bar(range(4), med, width=0.5, color=C[0])
for i, v in enumerate(med):
    ax.text(i, v - 0.6 if v < 0 else v + 0.5, f"{v:+.1f}%", ha="center", va="top" if v < 0 else "bottom", fontsize=12, fontweight="bold", color=INK)
ax.axhline(0, color=INK2, lw=0.8)
ax.axhline(mean(iw), color=INK2, lw=1.2, ls=(0, (4, 3)))
NL = chr(10)
ax.text(3.42, mean(iw) - 0.5, f"IWM {mean(iw):+.1f}%" + NL + "(small-cap index)", ha="left", va="top", fontsize=10, color=INK2); ax.set_xlim(-0.6, 4.25)
ax.set_xticks(range(4)); ax.set_xticklabels([PB[pb] + NL + "(about " + str(len(vals[pb]) // len(entries)) + " stocks)" for pb in range(4)])
ax.set_ylabel("median return over the next 20 sessions"); ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_ylim(min(med) - 4, 3)
title(fig, "Cheap stocks fell hard on their own", "Stocks we never flagged, grouped by share price. Entries from 21 Sep to 12 Oct 2026.")
foot(fig, "1,519 randomly sampled US stocks not in our ledger, register or watchlist. Weighted median of every stock and start day. Source: Yahoo daily bars.")
fig.savefig(OUT / "1-market.png", dpi=170); plt.close(fig)
print("market", [round(m, 1) for m in med], "IWM", round(mean(iw), 1), [len(vals[pb]) // len(entries) for pb in range(4)])

# ---- 2. Day-by-day paths vs matched ----
P = pickle.load(open(HERE / "paths.pkl", "rb"))
series = [("AVOID register (read and judged)", "AVOID register"), ("Scanner supply flags, takeable", "Supply flags, takeable"),
          ("Buy-side names we wrote up", "Names we wrote up (long side)"), ("Scanner buy-side flags, takeable", "Raw buy-side flags, takeable")]
fig, ax = plt.subplots(figsize=(9.6, 5.6)); fig.subplots_adjust(top=0.80, bottom=0.13, left=0.08, right=0.70)
ends = []
for (lab, key), col in zip(series, C):
    ys = [v for v, n in P[key]]
    ax.plot(range(1, 21), ys[:20], color=col, lw=2.2, solid_capstyle="round")
    ax.plot([20], [ys[19]], "o", color=col, ms=6, mec=SURF, mew=1.5)
    ends.append([ys[19], lab, col, P[key][19][1], P[key][4][1]])
ends.sort(key=lambda e: e[0])
ypos = [e[0] for e in ends]
for i in range(1, len(ypos)):                      # keep end labels at least 2.6 points apart
    ypos[i] = max(ypos[i], ypos[i - 1] + 2.6)
for (v, lab, col, n20, n5), y in zip(ends, ypos):
    ax.plot([20.25, 20.9], [v, y], color=col, lw=1)
    ax.text(21.0, y, f"{lab}\n{v:+.1f} pts (n={n5} at day 5, {n20} at day 20)", va="center", fontsize=9.3, color=INK)
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xlim(1, 20.3); ax.set_xticks([1, 5, 10, 15, 20]); ax.set_xlabel("market sessions after the first open we could have acted on")
ax.set_ylabel("median gap to similar unflagged stocks (points)"); ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
title(fig, "The avoid side keeps falling; the buy side goes nowhere", "Each flagged stock against unflagged stocks of the same price and size, over the same dates.")
foot(fig, "Median across stocks. Fewer stocks reach the later days, so the right-hand end is noisier. 11 Sep to 9 Nov 2026.")
fig.savefig(OUT / "2-paths.png", dpi=170); plt.close(fig)

# ---- 3. Public AVOID calls vs matched ----
calls = [m for m in pickle.load(open(HERE / "calls.pkl", "rb")) if m["dirn"] == -1]
calls.sort(key=lambda m: m["last_c"])
fig, ax = plt.subplots(figsize=(9, 6)); fig.subplots_adjust(top=0.84, bottom=0.11, left=0.17, right=0.95)
y = range(len(calls))
ax.barh(list(y), [m["last_c"] for m in calls], height=0.62, color=C[0])
for i, m in enumerate(calls):
    ax.text(m["last_c"] - 0.8, i, f"{m['last_c']:+.1f}", ha="right", va="center", fontsize=10, color=INK)
ax.set_yticks(list(y)); ax.set_yticklabels([f"#{m['id']} {m['ticker']}  ({len(m['path'])}d)" for m in calls], color=INK)
ax.axvline(0, color=INK2, lw=0.8); ax.invert_yaxis(); ax.set_xlim(min(m["last_c"] for m in calls) - 9, 3)
ax.set_xlabel("gap to similar unflagged stocks since the call (points; negative = fell more)"); ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
title(fig, "All 14 public AVOID calls fell more than similar stocks", "Each call from its next open to the 9 Nov close, against unflagged stocks of the same price and size.")
foot(fig, "(3d) to (10d) = sessions since the call. NNBR was closed as wrong on 29 Oct at +10%, then fell to $2.67 by 5 Nov. Short windows, one two-week period.")
fig.savefig(OUT / "3-calls.png", dpi=170); plt.close(fig)

# ---- 4. Every OWN / WATCH pick, by what the reason was ----
picks = pickle.load(open(HERE / "picks.pkl", "rb"))
KIND = {"ESRT": 0, "SKYA": 0, "PED": 0, "SRTA": 0, "DIBS": 0, "ACB": 0, "XPOF": 0, "CPAC": 0, "DOLE": 0, "SEER": 0, "VVR": 0,
        "MTUS": 1, "RYAM": 1, "MOD": 1, "THRM": 1, "WHF": 1, "CTVA": 1, "VYLR": 1, "HMH": 1, "MSGS": 1, "BORR": 2, "IMSR": 2}
KN = ["An outside buyer or holder acting (tender, bid, 13D, big-holder buying)", "The company's own story or event (review, spin-off, contract)", "Insiders buying"]
for m in picks:
    m["kind"] = KIND[m["ticker"]]; m["last_c"] = m["cpath"][-1]
picks.sort(key=lambda m: -m["last_c"])
fig, ax = plt.subplots(figsize=(9.4, 7.6)); fig.subplots_adjust(top=0.80, bottom=0.09, left=0.21, right=0.95)
for i, m in enumerate(picks):
    ax.barh(i, m["last_c"], height=0.62, color=C[m["kind"]])
    ax.text(m["last_c"] + (0.8 if m["last_c"] >= 0 else -0.8), i, f"{m['last_c']:+.0f}", ha="left" if m["last_c"] >= 0 else "right", va="center", fontsize=9.5, color=INK)
ax.set_yticks(range(len(picks))); ax.set_yticklabels([f"{m['ticker']}  {m['date'][8:]}/{m['date'][5:7]}" for m in picks], color=INK)
ax.axvline(0, color=INK2, lw=0.8); ax.invert_yaxis(); ax.set_xlim(-58, 48)
ax.set_xlabel("gap to similar unflagged stocks, from the verdict to the 9 Nov close (points)"); ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
import matplotlib.patches as mp
fig.legend(handles=[mp.Patch(color=C[k], label=KN[k]) for k in range(3)], loc="upper left", bbox_to_anchor=(0.015, 0.895), frameon=False, fontsize=9.5, ncol=1, handlelength=1.2)
title(fig, "Our 22 OWN and WATCH picks, by the kind of reason", "From the next open after each verdict. Dates are the verdict dates.")
foot(fig, "The grouping was made after the results were known, from each note's stated reason. Treat it as a description, not a tested rule.")
fig.savefig(OUT / "4-picks.png", dpi=170); plt.close(fig)
for k in range(3):
    ms = [m for m in picks if m["kind"] == k]
    v10 = [m["c10"] for m in ms if m.get("c10") is not None]
    print(KN[k][:40], "n", len(ms), "to date median", round(median(m["last_c"] for m in ms), 1), "mean", round(mean(m["last_c"] for m in ms), 1), "beat", sum(m["last_c"] > 0 for m in ms), "| 10d median", round(median(v10), 1) if v10 else None, "n10", len(v10))
allv = [m["last_c"] for m in picks]
print("all picks to date: median", round(median(allv), 1), "mean", round(mean(allv), 1), "beat", sum(v > 0 for v in allv), "of", len(allv), "| raw return mean", round(mean(m["path"][-1][0] for m in picks), 1), "median", round(median(m["path"][-1][0] for m in picks), 1))
