"""Rumour-trade check: recompute every number in RESULTS.md.

Inputs (all in this folder):
  reports.csv          one row per hit, hand-classified (manual filters, outcome, value fields)
  search_log.csv       which searches ran and how many documents each returned
  data/prices/*.json   raw Yahoo daily bars (fetched by fetch.py), IWM included

Run:  python run.py                 prints the tables and writes cases.csv + results.json
      python run.py --write-status  also writes final_status / final_reason back into reports.csv

Rules (from PLAN.md, with the interpretations listed in RESULTS.md):
  entry       = first regular-session close (16:00 ET) after the report time
  close_before= the close of the trading day before the entry day
  next_open   = open of the trading day after the entry day ("close to next open")
  5d / 20d    = close 5 / 20 trading days after the entry close ("close to close")
  exit        = close of the first trading day after the day a signed deal was announced,
                if that is within 60 trading days of entry; otherwise the close 60 trading days after entry
  worst       = lowest daily low from day 1 to day 20 after entry, against the entry close
  costs       = 1 percentage point taken off every trade return (round trip)
  filters     = close_before >= $1 and average daily dollar volume (close x volume, 20 sessions
                ending at close_before) >= $250,000
  slice       = buyer named, wording 'advanced', a price per share that can be worked out, and the
                entry close at least 10% below it. When only a value is given, both readings are
                worked out (equity: value / shares; including debt: (value - net debt) / shares)
                and the LOWER one is used, so the gap must hold under both readings.
  pass mark   = slice has >= 10 cases with a 20-day net return, median > 0 and mean > 0
"""
import csv, json, os, sys, statistics as st
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ET = ZoneInfo('America/New_York')
AS_OF = date(2026, 10, 13)      # last complete session when the study was run (14 Oct 2026, before the close)
COST = 0.01
MIN_PRICE, MIN_DOLLAR_VOL = 1.0, 250_000


def load_bars(ticker):
    p = os.path.join(HERE, 'data', 'prices', f'{ticker}.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    res = (d.get('chart') or {}).get('result')
    if not res or not res[0].get('timestamp'):
        return None
    r = res[0]; q = r['indicators']['quote'][0]
    bars = []
    for i, t in enumerate(r['timestamp']):
        day = datetime.fromtimestamp(t, timezone.utc).astimezone(ET).date()
        if day > AS_OF:
            continue
        o, h, l, c, v = (q[k][i] for k in ('open', 'high', 'low', 'close', 'volume'))
        if None in (o, h, l, c):
            continue
        bars.append({'d': day, 'o': o, 'h': h, 'l': l, 'c': c, 'v': v or 0})
    return bars


def idx_on_or_after(bars, d):
    for i, b in enumerate(bars):
        if b['d'] >= d:
            return i
    return None


def pct(a, b):
    return None if a is None or b is None else b / a - 1


def f2(x, n=1):
    return '' if x is None else f'{x * 100:.{n}f}%'


def case_metrics(row, iwm):
    out = {'hit_id': row['hit_id'], 'ticker': row['ticker'], 'target': row['target']}
    # implied price per share (two readings when only a value is given)
    ppx = row['price_per_share_reported']
    if ppx:
        out['px_eq'] = out['px_incl_debt'] = float(ppx)
    elif row['value_usd_m'] and row['shares_out']:
        v, sh, nd = float(row['value_usd_m']) * 1e6, float(row['shares_out']), float(row['net_debt_usd_m'] or 0) * 1e6
        out['px_eq'], out['px_incl_debt'] = v / sh, (v - nd) / sh
    if 'px_eq' in out:
        out['px_slice'] = min(out['px_eq'], out['px_incl_debt'])
    bars = load_bars(row['ticker'])
    rt = datetime.fromisoformat(row['report_time_utc']).replace(tzinfo=timezone.utc).astimezone(ET)
    out['report_time_et'] = rt.strftime('%Y-%m-%d %H:%M')
    # entry day from the IWM calendar (complete for the period)
    cal = [b['d'] for b in iwm]
    entry_day = next(d for d in cal if d > rt.date() or (d == rt.date() and rt.hour < 16))
    out['entry_day'] = str(entry_day)
    if not bars or entry_day not in [b['d'] for b in bars]:
        out['price_data'] = 'missing'
        return out
    out['price_data'] = 'ok'
    by = {b['d']: i for i, b in enumerate(bars)}
    e = by[entry_day]
    if e < 21:
        out['price_data'] = 'too short before entry'
        return out
    out['close_before'] = bars[e - 1]['c']; out['close_before_day'] = str(bars[e - 1]['d'])
    out['entry_close'] = bars[e]['c']
    out['avg_dollar_vol_20'] = sum(b['c'] * b['v'] for b in bars[e - 20:e]) / 20
    out['pass_price'] = out['close_before'] >= MIN_PRICE
    out['pass_liquidity'] = out['avg_dollar_vol_20'] >= MIN_DOLLAR_VOL
    ie = idx_on_or_after(iwm, entry_day)

    def leg(k_from, k_to, kind):
        """return (stock, iwm) gross returns between bar index offsets, or (None, None) if not yet available."""
        a, b = e + k_from, e + k_to
        if b >= len(bars) or ie + k_to >= len(iwm):
            return None, None
        if kind == 'open':
            return pct(bars[a]['c'], bars[b]['o']), pct(iwm[ie + k_from]['c'], iwm[ie + k_to]['o'])
        return pct(bars[a]['c'], bars[b]['c']), pct(iwm[ie + k_from]['c'], iwm[ie + k_to]['c'])

    out['next_open'] = bars[e + 1]['o'] if e + 1 < len(bars) else None
    out['day_before_to_entry'] = pct(out['close_before'], out['entry_close'])
    out['r_next_open'], out['iwm_next_open'] = leg(0, 1, 'open')
    out['r_5d'], out['iwm_5d'] = leg(0, 5, 'close')
    out['r_20d'], out['iwm_20d'] = leg(0, 20, 'close')
    # exit: day after signing (within 60 trading days) else day 60
    k_exit, why = 60, 'day 60, no signing by then'
    if row['signed_announce_date']:
        sd = date.fromisoformat(row['signed_announce_date'])
        j = next((i for i, b in enumerate(bars) if b['d'] > sd), None)
        if j is not None and j - e <= 60:
            k_exit, why = max(j - e, 1), 'day after signing'
        elif j is None:
            k_exit, why = None, 'day after signing not yet traded'
    out['exit_rule'] = why
    if k_exit is not None:
        out['exit_k'] = k_exit
        out['r_exit'], out['iwm_exit'] = leg(0, k_exit, 'close')
        if out['r_exit'] is not None:
            out['exit_day'] = str(bars[e + k_exit]['d'])
    window = bars[e + 1:e + 21]
    out['worst_20d'] = (min(b['l'] for b in window) / out['entry_close'] - 1) if len(window) == 20 else None
    if 'px_slice' in out:
        out['gap_to_px'] = out['entry_close'] / out['px_slice'] - 1
    return out


def summarise(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {'n': 0, 'mean': None, 'median': None, 'up': 0}
    return {'n': len(vals), 'mean': st.mean(vals), 'median': st.median(vals), 'up': sum(v > 0 for v in vals)}


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'reports.csv'), encoding='utf-8')))
    iwm = load_bars('IWM')
    cases = []
    for r in rows:
        if r['manual_status'] != 'pass':
            r['final_status'], r['final_reason'] = 'excluded', r['exclusion_reason']
            continue
        m = case_metrics(r, iwm)
        if m['price_data'] != 'ok':
            r['final_status'] = 'kept, no price data'
            r['final_reason'] = 'passes the manual filters; Yahoo does not serve this ticker for the report dates, so the $1 and $250k filters and all returns are [UNVERIFIED]'
        elif not m['pass_price']:
            r['final_status'], r['final_reason'] = 'excluded', f"close before report ${m['close_before']:.2f} < $1"
        elif not m['pass_liquidity']:
            r['final_status'], r['final_reason'] = 'excluded', f"average dollar volume ${m['avg_dollar_vol_20']:,.0f} < $250,000"
        else:
            r['final_status'], r['final_reason'] = 'kept', ''
        rd = datetime.fromisoformat(r['report_time_utc']).replace(tzinfo=timezone.utc).astimezone(ET).date()
        if r['signed_announce_date']:
            lag = (date.fromisoformat(r['signed_announce_date']) - rd).days
            m['signed_lag_days'] = lag
            m['signed_30'] = 'yes' if lag <= 30 else 'no'
            m['signed_90'] = 'yes' if lag <= 90 else 'no'
        else:
            known = (AS_OF - rd).days
            m['signed_30'] = 'no' if known >= 30 else 'not yet known'
            m['signed_90'] = 'no' if known >= 90 else 'not yet known'
        m['final_status'] = r['final_status']
        m['buyer_named'], m['wording'], m['window'] = r['buyer_named'], r['wording'], r['window']
        m['signed_terms'] = r['signed_terms']
        slice_ok = r['buyer_named'] == 'Y' and r['wording'] == 'advanced' and ('px_slice' in m or r['price_per_share_reported'] or r['value_usd_m'])
        if not slice_ok:
            m['in_slice'] = 'no'
        elif 'gap_to_px' not in m:
            m['in_slice'] = '[UNVERIFIED] no entry close'
        else:
            m['in_slice'] = 'yes' if m['gap_to_px'] <= -0.10 else 'no (gap under 10%)'
        cases.append(m)

    kept = [c for c in cases if c['final_status'] == 'kept']
    net = lambda c, k: None if c.get(k) is None else c[k] - COST
    exc = lambda c, k: None if c.get(k) is None else c[k] - c['iwm' + k[1:]]
    res = {'as_of': str(AS_OF), 'hits_total': len(rows),
           'hits_by_window': {}, 'pass_manual': sum(r['manual_status'] == 'pass' for r in rows),
           'kept_with_prices': len(kept), 'kept_no_prices': sum(c['final_status'] == 'kept, no price data' for c in cases)}
    for r in rows:
        w = res['hits_by_window'].setdefault(r['window'], {'hits': 0, 'pass_manual': 0, 'kept': 0, 'kept_no_prices': 0})
        w['hits'] += 1
        w['pass_manual'] += r['manual_status'] == 'pass'
        w['kept'] += r['final_status'] == 'kept'
        w['kept_no_prices'] += r['final_status'] == 'kept, no price data'
    for name, grp in (('all', kept), ('slice', [c for c in kept if c['in_slice'] == 'yes'])):
        res[name] = {}
        for k in ('r_next_open', 'r_5d', 'r_20d', 'r_exit'):
            res[name][k + '_net'] = summarise([net(c, k) for c in grp])
            res[name][k + '_vs_iwm'] = summarise([exc(c, k) for c in grp])
        res[name]['worst_20d'] = summarise([c.get('worst_20d') for c in grp])
        res[name]['close_before_to_entry_close'] = summarise([c.get('day_before_to_entry') for c in grp])
        res[name]['signed_30'] = sum(c['signed_30'] == 'yes' for c in grp)
        res[name]['signed_90'] = sum(c['signed_90'] == 'yes' for c in grp)
        res[name]['tickers'] = [c['ticker'] for c in grp]
    allp = [c for c in cases if c['final_status'] in ('kept', 'kept, no price data')]
    res['signed_all_passing'] = {'n': len(allp), 'signed_30': sum(c['signed_30'] == 'yes' for c in allp),
                                 'signed_90': sum(c['signed_90'] == 'yes' for c in allp)}
    s = res['slice']['r_20d_net']
    res['pass_mark'] = {'needs_cases': 10, 'cases': s['n'],
                        'median_above_zero': s['median'] is not None and s['median'] > 0,
                        'mean_above_zero': s['mean'] is not None and s['mean'] > 0}
    res['pass_mark']['passes'] = s['n'] >= 10 and res['pass_mark']['median_above_zero'] and res['pass_mark']['mean_above_zero']
    # search coverage
    log = list(csv.DictReader(open(os.path.join(HERE, 'search_log.csv'), encoding='utf-8')))
    cov = {}
    for l in log:
        c = cov.setdefault(l['window'], {'searches_planned': 0, 'searches_done': 0, 'docs_returned': 0})
        c['searches_planned'] += 1
        if l['status'].startswith('done'):
            c['searches_done'] += 1; c['docs_returned'] += int(l['docs_returned'])
    res['search_coverage'] = cov

    # ---- write outputs ----
    cols = ['hit_id', 'window', 'ticker', 'target', 'final_status', 'report_time_et', 'entry_day', 'close_before_day', 'close_before', 'entry_close', 'next_open',
            'avg_dollar_vol_20', 'day_before_to_entry', 'r_next_open', 'iwm_next_open', 'r_5d', 'iwm_5d', 'r_20d', 'iwm_20d', 'exit_rule', 'exit_day',
            'r_exit', 'iwm_exit', 'worst_20d', 'buyer_named', 'wording', 'px_eq', 'px_incl_debt', 'px_slice', 'gap_to_px', 'in_slice',
            'signed_lag_days', 'signed_30', 'signed_90', 'signed_terms', 'price_data']
    with open(os.path.join(HERE, 'cases.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader()
        for c in cases:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()})
    json.dump(res, open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=str)
    if '--write-status' in sys.argv:
        with open(os.path.join(HERE, 'reports.csv'), 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # ---- print ----
    print(f"Hits: {len(rows)} | pass manual filters: {res['pass_manual']} | kept with prices: {len(kept)} | kept, no price data: {res['kept_no_prices']}")
    print('Search coverage:', json.dumps(cov))
    print('Hits by window:', json.dumps(res['hits_by_window']))
    for name in ('all', 'slice'):
        print(f"\n== {name} ({len(res[name]['tickers'])}): {', '.join(res[name]['tickers'])}")
        for k in ('r_next_open', 'r_5d', 'r_20d', 'r_exit'):
            a, b = res[name][k + '_net'], res[name][k + '_vs_iwm']
            print(f"  {k:12s} net of 1%: n={a['n']} mean={f2(a['mean'])} median={f2(a['median'])} up={a['up']} | gross minus IWM: mean={f2(b['mean'])} median={f2(b['median'])}")
        ww = res[name]['worst_20d']
        print(f"  worst low within 20d: mean={f2(ww['mean'])} median={f2(ww['median'])}")
        jb = res[name]['close_before_to_entry_close']
        print(f"  close before report -> entry close (already gone before entry): mean={f2(jb['mean'])} median={f2(jb['median'])}")
        print(f"  signed within 30 days: {res[name]['signed_30']} | within 90 days: {res[name]['signed_90']}")
    print('All passing manual filters (incl. no price data):', res['signed_all_passing'])
    print('\nPass mark:', res['pass_mark'])
    print('\nPer case:')
    for c in cases:
        print(f"  {c['hit_id']} {c['ticker']:5s} {c['final_status']:22s} entry {c.get('entry_day')} close {c.get('entry_close') and round(c['entry_close'], 2)}"
              f" | 20d {f2(c.get('r_20d'))} IWM {f2(c.get('iwm_20d'))} | exit({c.get('exit_rule', '')}) {f2(c.get('r_exit'))} | worst {f2(c.get('worst_20d'))}"
              f" | slice {c['in_slice']} px {c.get('px_slice') and round(c['px_slice'], 2)} gap {f2(c.get('gap_to_px'))} | signed30 {c['signed_30']} signed90 {c['signed_90']}")


if __name__ == '__main__':
    main()
