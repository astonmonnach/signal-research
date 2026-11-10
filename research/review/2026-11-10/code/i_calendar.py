"""I. Dated events we put on the calendar (tender expiries, lock-ups, votes, spin dates, results): what the stock did on the day."""
import sys, re, datetime as dt, bisect
from core import *
sys.stdout.reconfigure(encoding="utf-8")
raw = open(ROOT / "calendar/catalyst-dates.ics", encoding="utf-8").read().replace("\r\n", "\n")
evs = []
for blk in raw.split("BEGIN:VEVENT")[1:]:
    d = re.search(r"DTSTART;VALUE=DATE:(\d{8})", blk); s = re.search(r"SUMMARY:(.*)", blk)
    if not d or not s: continue
    day = dt.datetime.strptime(d.group(1), "%Y%m%d").date(); summ = s.group(1).replace("\,", ",").replace("\;", ";").strip()
    m = re.match(r"([A-Z]{1,5})(?:/[A-Z]{1,5})*:\s*(.*)", summ)
    if not m or not (dt.date(2026, 9, 20) <= day <= dt.date(2026, 11, 9)): continue
    evs.append((day, m.group(1), m.group(2)))
print(len(evs), "dated events with a ticker, to 9 Nov")
print(f"{'date':10} {'tkr':5} {'gap':>6} {'high':>6} {'low':>6} {'close':>6} {'next':>6} {'3rd':>6} {'5th':>6} | event")
out = []
for day, t, what in sorted(evs):
    s = S(t)
    if not s: continue
    dates = [b[0] for b in s]
    i = bisect.bisect_left(dates, day)
    if i >= len(s) or i == 0: continue
    pc = s[i - 1][2]; b = s[i]
    g = lambda j: f"{(s[j][2] / pc - 1) * 100:+6.1f}" if j < len(s) else "   n/a"
    row = dict(day=day, t=t, what=what, gap=(b[1] / pc - 1) * 100, high=(b[6] / pc - 1) * 100, low=(b[7] / pc - 1) * 100, close=(b[2] / pc - 1) * 100,
               nxt=(s[i + 1][2] / pc - 1) * 100 if i + 1 < len(s) else None, d5=(s[i + 4][2] / pc - 1) * 100 if i + 4 < len(s) else None, on=dates[i])
    out.append(row)
    print(f"{dates[i].isoformat()} {t:5} {row['gap']:+6.1f} {row['high']:+6.1f} {row['low']:+6.1f} {row['close']:+6.1f} {g(i+1)} {g(i+2)} {g(i+4)} | {what[:95]}")
import pickle; pickle.dump(out, open(HERE / "cal_events.pkl", "wb"))
