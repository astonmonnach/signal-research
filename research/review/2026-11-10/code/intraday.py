"""Reactions at actual times. For an event with an exact timestamp (an SEC acceptance time), measure the price from the
last trade before it to the first regular-session price we could act on, then 30 minutes, 1 hour and 2 hours later, the
close, the next close and the third close, plus the peak and the low on the way, with their times. 5-minute bars from
Yahoo, pre-market and after-hours included where the stock traded."""
import gzip, json, bisect, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).parent
NY, LON, UTC = ZoneInfo("America/New_York"), ZoneInfo("Europe/London"), dt.timezone.utc
OPEN, CLOSE = dt.time(9, 30), dt.time(16, 0)
_B = {}


def bars(t):
    """[(start_utc_epoch, start_ny, o, h, l, c, v, regular)] for one ticker, or None."""
    if t in _B:
        return _B[t]
    p = HERE / "i5" / f"{t}.json.gz"
    out = None
    if p.exists():
        d = json.load(gzip.open(p, "rt"))
        if "err" not in d and d.get("ts"):
            out = []
            for i, ts in enumerate(d["ts"]):
                o, h, l, c = d["o"][i], d["h"][i], d["l"][i], d["c"][i]
                if not o or not c:
                    continue
                ny = dt.datetime.fromtimestamp(ts, NY)
                out.append((ts, ny, o, h or max(o, c), l or min(o, c), c, d["v"][i] or 0, OPEN <= ny.time() < CLOSE))
            out = out or None
    _B[t] = out
    return out


def react(t, t0, bench="IWM"):
    """t0: aware datetime (UTC). Returns a dict or None."""
    b = bars(t)
    if not b:
        return None
    ts0 = t0.timestamp()
    starts = [x[0] for x in b]
    i = bisect.bisect_right(starts, ts0 - 300)            # bars that ended at or before t0
    if i == 0:
        return None
    prev = b[i - 1]
    if ts0 - prev[0] > 6 * 86400:
        return None
    # first regular bar starting at or after t0
    j = bisect.bisect_left(starts, ts0)
    while j < len(b) and not b[j][7]:
        j += 1
    if j >= len(b):
        return None
    E = b[j]
    if E[0] - ts0 > 5 * 86400:
        return None
    p0, pe = prev[5], E[2]
    out = {"t0": t0, "p0": p0, "entry_time": E[1], "entry": pe, "gap": (pe / p0 - 1) * 100, "wait_min": (E[0] - ts0) / 60,
           "in_hours": OPEN <= t0.astimezone(NY).time() < CLOSE and t0.astimezone(NY).weekday() < 5}
    ext = [x for x in b[i:j] if not x[7]]
    if ext:
        out["ext_first"] = (ext[0][2] / p0 - 1) * 100
        out["ext_last"] = (ext[-1][5] / p0 - 1) * 100
        out["ext_high"] = (max(x[3] for x in ext) / p0 - 1) * 100
        out["ext_vol"] = sum(x[6] for x in ext)
    day = E[1].date()
    # regular bars of the entry session and later sessions
    reg = [x for x in b[j:] if x[7]]
    sess = [x for x in reg if x[1].date() == day]
    days = sorted({x[1].date() for x in reg})

    def at(minutes):
        lim = E[0] + minutes * 60
        w = [x for x in sess if x[0] < lim]
        return (w[-1][5] / pe - 1) * 100, sess[-1][0] + 300 < lim     # value, truncated by the close?

    for m in (30, 60, 120):
        out[f"r{m}"], out[f"cut{m}"] = at(m)
    out["rclose"] = (sess[-1][5] / pe - 1) * 100
    for k, name in ((1, "rnext"), (2, "r3")):
        if len(days) > k:
            last = [x for x in reg if x[1].date() == days[k]][-1]
            out[name] = (last[5] / pe - 1) * 100

    def ext_window(w, tag):
        if not w:
            return
        hi = max(w, key=lambda x: x[3]); lo = min(w, key=lambda x: x[4])
        out[f"peak_{tag}"] = (hi[3] / pe - 1) * 100; out[f"peak_{tag}_min"] = (hi[0] - E[0]) / 60; out[f"peak_{tag}_time"] = hi[1]
        out[f"low_{tag}"] = (lo[4] / pe - 1) * 100; out[f"low_{tag}_min"] = (lo[0] - E[0]) / 60; out[f"low_{tag}_time"] = lo[1]
        # worst low before the peak
        pre = [x for x in w if x[0] <= hi[0]]
        out[f"pain_{tag}"] = (min(x[4] for x in pre) / pe - 1) * 100

    ext_window([x for x in sess if x[0] < E[0] + 7200], "2h")
    ext_window(sess, "day")
    ext_window([x for x in reg if x[1].date() in days[:3]], "3d")
    out["sess_minutes"] = (sess[-1][0] + 300 - E[0]) / 60
    out["dollar_vol_day"] = sum(x[5] * x[6] for x in sess)
    # benchmark over the same clock times
    bb = bars(bench)
    if bb and t != bench:
        bs = [x[0] for x in bb]

        def bpx(ts, use_open=False):
            k = bisect.bisect_right(bs, ts) - 1
            return None if k < 0 else (bb[k][2] if use_open and bb[k][0] == ts else bb[k][5])
        be = bpx(E[0], True)
        if be:
            for m in (30, 60, 120):
                x = bpx(min(E[0] + m * 60 - 300, sess[-1][0]))
                if x:
                    out[f"x{m}"] = out[f"r{m}"] - (x / be - 1) * 100
            x = bpx(sess[-1][0])
            if x:
                out["xclose"] = out["rclose"] - (x / be - 1) * 100
            bp0 = bpx(prev[0])
            if bp0:
                out["xgap"] = out["gap"] - (be / bp0 - 1) * 100
    return out
