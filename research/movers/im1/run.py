"""IM1: collect the per-event rows from the session transcript, then score the test exactly as pre-registered.

    python run.py ingest [transcript.jsonl ...]   -> events_raw.csv (rows from extract.sql runs on im_* tables)
    python run.py                                  -> results.json and a printed summary

Rules: ../PREREG_IM1.md. A row is taken only from a query_data call whose SQL reads im_* tables, so test
queries on other tables never enter. Later runs of the same event replace earlier ones.
"""
import os, sys, csv, json, glob, random, statistics as st, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.expanduser('~/.claude/projects/C--Users-thoma-catalyst-research')
COLS = ['k', 'n_all', 'n_rth', 'tt', 'entry', 'jumped', 'x30', 'x60', 'x120', 't120', 'xclose', 'hi', 'lo']
SEED, DRAWS, CAP = 20261029, 2000, 4.0
COSTS = (0.01, 0.02, 0.04)


def ingest(files):
    files = files or sorted(glob.glob(os.path.join(PROJ, '*.jsonl')), key=os.path.getmtime)[-3:]
    sql_by_id, rows = {}, {}
    for fn in files:
        with open(fn, encoding='utf-8') as fh:
            for line in fh:
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                content = (m.get('message') or {}).get('content')
                if not isinstance(content, list):
                    continue
                for b in content:
                    if b.get('type') == 'tool_use' and b.get('name', '').endswith('query_data'):
                        sql = (b.get('input') or {}).get('sql', '')
                        if 'FROM im_' in sql:
                            sql_by_id[b['id']] = sql
                    elif b.get('type') == 'tool_result' and b.get('tool_use_id') in sql_by_id:
                        c = b.get('content')
                        if isinstance(c, list):
                            c = ''.join(x.get('text', '') for x in c if isinstance(x, dict))
                        try:
                            res = json.loads(c)['result']
                        except (ValueError, TypeError, KeyError):
                            continue
                        lines = res.strip().splitlines()
                        if not lines or lines[0].split(',') != COLS:
                            continue
                        for ln in lines[1:]:
                            v = ln.split(',')
                            rows[int(v[0])] = v
    with open(os.path.join(HERE, 'events_raw.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for k in sorted(rows):
            w.writerow(rows[k])
    print('ingested', len(rows), 'events from', len(files), 'transcript(s)')


def num(x):
    return float(x) if x not in ('', None) else None


def et_hm(ms, day):
    d = dt.date.fromisoformat(day)
    mar = dt.date(d.year, 3, 8); mar += dt.timedelta((6 - mar.weekday()) % 7)
    nov = dt.date(d.year, 11, 1); nov += dt.timedelta((6 - nov.weekday()) % 7)
    off = 4 if mar <= d < nov else 5
    t = dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=ms) - dt.timedelta(hours=off)
    return t.hour * 60 + t.minute


def boot(trades, cost):
    days = sorted({t['date'] for t in trades})
    byday = {d: [t['gross'] - cost for t in trades if t['date'] == d] for d in days}
    rnd = random.Random(SEED)
    means = []
    for _ in range(DRAWS):
        xs = []
        for d in (rnd.choice(days) for _ in days):
            xs += byday[d]
        means.append(sum(xs) / len(xs))
    means.sort()
    return means[int(0.025 * DRAWS)], means[int(0.975 * DRAWS) - 1]


def describe(xs):
    if not xs:
        return {'n': 0}
    return {'n': len(xs), 'mean': round(100 * st.mean(xs), 2), 'median': round(100 * st.median(xs), 2),
            'win': round(100 * sum(1 for x in xs if x > 0) / len(xs), 1),
            'up10': round(100 * sum(1 for x in xs if x >= 0.10) / len(xs), 1),
            'down10': round(100 * sum(1 for x in xs if x <= -0.10) / len(xs), 1)}


def analyze():
    sample = {int(r['k']): r for r in csv.DictReader(open(os.path.join(HERE, 'sample.csv')))}
    raw = {int(r['k']): r for r in csv.DictReader(open(os.path.join(HERE, 'events_raw.csv')))}
    counts = {'sampled': len(sample), 'not_fetched': 0, 'no_minute_bars': 0, 'no_rth_trigger': 0, 'late_trigger': 0}
    trades = []
    for k, s in sorted(sample.items()):
        r = raw.get(k)
        if r is None:
            counts['not_fetched'] += 1; continue
        if int(r['n_rth'] or 0) == 0:
            counts['no_minute_bars'] += 1; continue
        if not r['tt']:
            counts['no_rth_trigger'] += 1; continue
        tt = int(float(r['tt']))
        if et_hm(tt, s['date']) >= 14 * 60:
            counts['late_trigger'] += 1; continue
        e = num(r['entry']); close = num(r['xclose'])
        ex = {h: (num(r[f'x{h}']) if num(r[f'x{h}']) is not None else close) for h in (30, 60, 120)}
        g = lambda x: min(x / e, CAP) - 1
        trades.append({'k': k, 'ticker': s['ticker'], 'date': s['date'], 'gross': g(ex[120]), 'g30': g(ex[30]),
                       'g60': g(ex[60]), 'gclose': g(close), 'jumped': r['jumped'] == '1',
                       'low_price': float(s['prev_close_raw']) < 3,
                       'hi': (num(r['hi']) / e - 1) if num(r['hi']) else None,
                       'lo': (num(r['lo']) / e - 1) if num(r['lo']) else None,
                       'entry_et': et_hm(tt, s['date'])})
    counts['tested'] = len(trades)
    res = {'counts': counts, 'by_cost': {}}
    for c in COSTS:
        xs = [t['gross'] - c for t in trades]
        lo, hi = boot(trades, c)
        h1 = [t['gross'] - c for t in trades if t['date'] < '2025-10-01']
        h2 = [t['gross'] - c for t in trades if t['date'] >= '2025-10-01']
        res['by_cost'][f'{int(c * 100)}%'] = {**describe(xs), 'ci95': [round(100 * lo, 2), round(100 * hi, 2)],
                                              'half1_mean': round(100 * st.mean(h1), 2), 'half1_n': len(h1),
                                              'half2_mean': round(100 * st.mean(h2), 2), 'half2_n': len(h2)}
    m = res['by_cost']['2%']
    res['verdict'] = 'PAYS' if (m['mean'] > 0 and m['ci95'][0] > 0 and m['half1_mean'] > 0 and m['half2_mean'] > 0) \
        else 'DOES NOT PAY'
    c = 0.02
    res['describe'] = {
        'exit_30min': describe([t['g30'] - c for t in trades]),
        'exit_60min': describe([t['g60'] - c for t in trades]),
        'exit_120min': describe([t['gross'] - c for t in trades]),
        'exit_close': describe([t['gclose'] - c for t in trades]),
        'gap_ups': describe([t['gross'] - c for t in trades if t['jumped']]),
        'crossed_in_session': describe([t['gross'] - c for t in trades if not t['jumped']]),
        'prev_close_1_to_3': describe([t['gross'] - c for t in trades if t['low_price']]),
        'prev_close_3_up': describe([t['gross'] - c for t in trades if not t['low_price']]),
        'median_best_high_vs_entry': round(100 * st.median([t['hi'] for t in trades if t['hi'] is not None]), 1),
        'median_worst_low_vs_entry': round(100 * st.median([t['lo'] for t in trades if t['lo'] is not None]), 1),
    }
    with open(os.path.join(HERE, 'trades.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
        w.writeheader(); w.writerows(trades)
    json.dump(res, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'ingest':
        ingest(sys.argv[2:])
    else:
        analyze()
