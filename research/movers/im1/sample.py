"""IM1: draw the sample, and print the connector calls and the reduction SQL for each batch of 5 events.

    python sample.py draw          -> sample.csv (200 events, seed 20261029)
    python sample.py batch N       -> the 5 Massive calls and the SQL for events 5N..5N+4
    python sample.py save N FILE   -> append the SQL output (CSV text in FILE) to events_raw.csv

Rules: ../PREREG_IM1.md. The SQL is the template in extract.sql with the batch's tables and parameters filled in.
"""
import os, sys, csv, random, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', '..', 'runners', 'work')
SEED, N_SAMPLE, START, END = 20261029, 200, '2024-11-04', '2026-09-30'


def edt(day):
    """True when New York is on daylight time (US rules: second Sunday of March to first Sunday of November)."""
    d = dt.date.fromisoformat(day)
    mar = dt.date(d.year, 3, 8); mar += dt.timedelta((6 - mar.weekday()) % 7)
    nov = dt.date(d.year, 11, 1); nov += dt.timedelta((6 - nov.weekday()) % 7)
    return mar <= d < nov


def session_ms(day):
    off = 4 if edt(day) else 5
    o = dt.datetime.fromisoformat(day + 'T09:30:00') + dt.timedelta(hours=off)
    c = dt.datetime.fromisoformat(day + 'T16:00:00') + dt.timedelta(hours=off)
    ep = dt.datetime(1970, 1, 1)
    return int((o - ep).total_seconds() * 1000), int((c - ep).total_seconds() * 1000)


def draw():
    z = np.load(os.path.join(W, 'panel.npz'), allow_pickle=True)
    h, cp, crp, craw, vraw = z['h'], z['c_prev'], z['craw_prev'], z['craw'], z['vraw']
    dates, tick = list(z['dates']), list(z['tick'])
    med = pd.DataFrame(craw * vraw).rolling(20, min_periods=15).median().shift(1).values
    spl = pd.concat([pd.read_csv(os.path.join(W, 'ref', f), keep_default_na=False)
                     for f in ('reverse_splits.csv', 'other_splits.csv')], ignore_index=True)
    near_split = np.zeros(h.shape, bool)
    tix = {t: j for j, t in enumerate(tick)}
    arr = np.array(dates)
    for _, s in spl.iterrows():
        j = tix.get(s['ticker'])
        if j is None:
            continue
        p = int(np.searchsorted(arr, s['execution_date']))
        near_split[max(0, p - 2):min(len(dates), p + 3), j] = True
    with np.errstate(invalid='ignore', divide='ignore'):
        pool = (h / cp >= 1.2) & (crp >= 1) & (med >= 150000) & ~near_split
    i0, i1 = dates.index(START), dates.index(END)
    pool[:i0] = False; pool[i1 + 1:] = False
    ts, js = np.where(pool)
    rows = sorted(zip(ts.tolist(), js.tolist()))
    print('pool', len(rows))
    random.seed(SEED)
    pick = sorted(random.sample(rows, N_SAMPLE))
    with open(os.path.join(HERE, 'sample.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['k', 'ticker', 'date', 'prev_close_raw', 'P', 'open_ms', 'close_ms', 'high_vs_prev'])
        for k, (t, j) in enumerate(pick):
            d = dates[t]; om, cm = session_ms(d)
            w.writerow([k, tick[j], d, round(float(crp[t, j]), 4), round(1.2 * float(crp[t, j]), 4), om, cm,
                        round(float(h[t, j] / cp[t, j]), 3)])
    print('sample', len(pick), '->', os.path.join(HERE, 'sample.csv'))


def batch(n):
    rows = list(csv.DictReader(open(os.path.join(HERE, 'sample.csv'))))[5 * n:5 * n + 5]
    tpl = open(os.path.join(HERE, 'extract.sql')).read()
    for r in rows:
        print(f"CALL im_{r['k']}  /v2/aggs/ticker/{r['ticker']}/range/1/minute/{r['date']}/{r['date']}")
    bars = ' UNION ALL '.join(f"SELECT {r['k']} AS k, t, o, h, l, c FROM im_{r['k']}" for r in rows)
    params = ', '.join(f"({r['k']}, {r['P']}, {r['open_ms']}, {r['close_ms']})" for r in rows)
    print(tpl.replace('{BARS}', bars).replace('{PARAMS}', params).strip())


def save(n, path):
    txt = open(path).read().strip().splitlines()
    out = os.path.join(HERE, 'events_raw.csv')
    new = not os.path.exists(out)
    with open(out, 'a', newline='') as f:
        if new:
            f.write(txt[0] + '\n')
        for line in txt[1:]:
            f.write(line + '\n')
    print('saved batch', n, len(txt) - 1, 'rows')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'draw':
        draw()
    elif cmd == 'batch':
        batch(int(sys.argv[2]))
    elif cmd == 'save':
        save(int(sys.argv[2]), sys.argv[3])
