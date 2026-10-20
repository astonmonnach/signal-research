"""PUT1: would buying puts on fading top gainers have paid after the option's price?

Runs research/movers/PREREG_PUT1.md (committed in git 60e910c before any option price was looked at).

Commands (from anywhere):
    python run.py plan [N]   list the next N Massive API calls still missing from ./cache (JSON lines)
    python run.py            build trades_T1.csv, trades_T2.csv, results.json and RESULTS.md from the cache

Massive (Polygon) data come through the Massive market-data connector, which only Claude's tool calls
can reach. Each response is saved verbatim (the connector's JSON) under ./cache by the path that
`plan` prints, so a restart never repeats a call. The analysis step never touches the network.

Reads (never writes): research/movers/mv1/listB.csv, research/runners/work/raw/*.csv (Massive grouped
daily bars, unadjusted) and research/runners/work/ref/*splits.csv (Massive split records).
"""
import os, sys, json, glob, datetime
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.abspath(os.path.join(HERE, '..', '..'))
LISTB = os.path.join(RESEARCH, 'movers', 'mv1', 'listB.csv')
RAW = os.path.join(RESEARCH, 'runners', 'work', 'raw')
REF = os.path.join(RESEARCH, 'runners', 'work', 'ref')
CACHE = os.path.join(HERE, 'cache')
for _s in ('contracts', 'optaggs', 'check', 'grouped', 'splits'):
    os.makedirs(os.path.join(CACHE, _s), exist_ok=True)

# ---- pre-registered constants (PREREG_PUT1.md); do not change ----
N_T1, N_T2 = 300, 150
SAMPLE_SEED = 20261019
NBOOT, BOOT_SEED = 2000, 20261014
MIN_TDAYS = 20                 # expiry: first standard monthly at least 20 trading days after t+1
COSTS = (0.0, 0.10, 0.20)      # share of the premium added to the entry price; 10% is the tested one
COST_MAIN = 0.10
HALF2_FROM = '2025-10-01'      # halves: events before and from 1 Oct 2025
SMALL = '<$50M'

# ---- run choices the pre-registration left open (listed in RESULTS.md) ----
WIN_LO, WIN_HI = 0.5, 1.5      # the first few contracts calls asked for strikes in [0.5, 1.5] x the mover-day close;
                               # an empty window is followed by an unfiltered call before "no put listed"
LAST_KNOWN = None              # last session with stock closes on disk (set below)
LAST_SESSION_BEFORE_RUN = '2026-10-16'   # the run is on Mon 19 Oct 2026; later expiries have not happened
KNOWN_HOLIDAYS_AFTER_DATA = {'2026-11-26', '2026-12-25'}  # NYSE holidays after the raw bars end


NL = chr(10)


def log(*a):
    print(*a, flush=True)


# =====================================================================================
# 1. Events and samples
# =====================================================================================
B = pd.read_csv(LISTB, dtype={'cik': str})
# tickers such as NA must not be read as missing values
B['ticker'] = pd.read_csv(LISTB, usecols=['ticker'], dtype=str, keep_default_na=False)['ticker']
B['row_id'] = np.arange(len(B))          # position in listB.csv (file order: date, rank)
pool1 = B[(B['mech_any'] == True) & (B['mv_bucket'] != SMALL)].reset_index(drop=True)
pool2 = B[(B['mech_any'] == False) & (B['mv_bucket'] != SMALL)].reset_index(drop=True)


def draw(pool, n):
    rng = np.random.default_rng(SAMPLE_SEED)
    idx = np.sort(rng.choice(len(pool), size=n, replace=False))
    return pool.iloc[idx].reset_index(drop=True)


S1 = draw(pool1, N_T1)
S2 = draw(pool2, N_T2)
S1['test'] = 'T1'
S2['test'] = 'T2'
EV = pd.concat([S1, S2], ignore_index=True)
TICKERS = set(EV['ticker'])

# =====================================================================================
# 2. Stock bars (unadjusted) and market sessions
# =====================================================================================
raw_files = sorted(glob.glob(os.path.join(RAW, '*.csv')))
SESSIONS = [os.path.basename(f)[:-4] for f in raw_files]
bars = {}   # ticker -> {date: close}


def add_grouped(d, df):
    df = df[df['T'].isin(TICKERS)]
    for tk, c in zip(df['T'], df['c']):
        bars.setdefault(tk, {})[d] = float(c)


for f in raw_files:
    add_grouped(os.path.basename(f)[:-4], pd.read_csv(f, usecols=['T', 'c'], keep_default_na=False))


def read_api(path, expect=None):
    """A saved connector response -> its text, or None if not cached (or saved for different params)."""
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as fh:
        obj = json.load(fh)
    if expect is not None and obj.get('request', {}).get('params') != expect:
        return None
    return obj.get('result', '')


def is_not_found(text):
    return text.startswith('Error [HTTP]: HTTP 404')


def csv_rows(text):
    """Connector CSV text -> DataFrame; the connector's empty-result warning and 404s -> empty."""
    if text is None or text.startswith('Warning [EMPTY]') or text.startswith('Error'):
        return pd.DataFrame()
    body = text.split(NL + NL + 'Next page available')[0].strip()
    if not body or ',' not in body.split(NL)[0]:
        return pd.DataFrame()
    import io
    return pd.read_csv(io.StringIO(body), keep_default_na=False)


# grouped daily bars fetched for sessions after the runners raw files end (unadjusted). They give
# stock closes on those days only; the trading-day count after the raw files uses NYSE weekdays.
RAW_LAST = SESSIONS[-1]
SESSION_SET = set(SESSIONS)
GROUPED_EXTRA = {}
for f in sorted(glob.glob(os.path.join(CACHE, 'grouped', '*.json'))):
    d = os.path.basename(f)[:-5]
    df = csv_rows(read_api(f))
    if len(df) and d > RAW_LAST:
        df['c'] = df['c'].astype(float)
        add_grouped(d, df)
        GROUPED_EXTRA[d] = len(df)
LAST_KNOWN = max([RAW_LAST] + list(GROUPED_EXTRA))


def market_days_after(d, n):
    """n NYSE sessions after d: raw-file sessions, then weekdays past the raw files minus known holidays."""
    out = [s for s in SESSIONS if s > d][:n]
    x = pd.Timestamp(max(d, RAW_LAST))
    while len(out) < n:
        x += pd.Timedelta(days=1)
        s = x.strftime('%Y-%m-%d')
        if x.weekday() < 5 and s not in KNOWN_HOLIDAYS_AFTER_DATA:
            out.append(s)
    return out


def third_friday(y, m):
    first = datetime.date(y, m, 1)
    ff = 1 + (4 - first.weekday()) % 7
    return datetime.date(y, m, ff + 14)


def monthly_expiry(y, m):
    """Third Friday; the Thursday before if that Friday was a market holiday."""
    f = third_friday(y, m)
    s = f.isoformat()
    if s <= RAW_LAST:
        if s not in SESSION_SET:
            return (f - datetime.timedelta(days=1)).isoformat()
        return s
    if s in KNOWN_HOLIDAYS_AFTER_DATA:
        return (f - datetime.timedelta(days=1)).isoformat()
    return s


def first_expiry_on_or_after(d):
    x = pd.Timestamp(d)
    y, m = x.year, x.month
    for _ in range(4):
        e = monthly_expiry(y, m)
        if e >= d:
            return e
        m += 1
        if m == 13:
            y, m = y + 1, 1
    raise RuntimeError(d)


def schedule(tk, d):
    """t+1, t+2 (days the stock traded), the 20th trading day after t+1, and the expiry."""
    sd = sorted(x for x in bars.get(tk, {}) if d < x <= RAW_LAST)
    note = ''
    if not sd:
        return dict(t1=None, t2=None, d20=None, expiry=None, sched_note='no stock bar after the mover day')
    need = MIN_TDAYS + 1                     # t+1 and the 20 trading days after it
    if len(sd) < need:
        # the stock's bars on disk end (raw files end, or the stock stopped trading): go on with sessions
        sd = sd + market_days_after(sd[-1], need - len(sd))
        note = 'counted past the last stock bar on disk with market sessions'
    t1, t2 = sd[0], sd[1]
    d20 = sd[MIN_TDAYS]                       # 20th trading day after t+1
    return dict(t1=t1, t2=t2, d20=d20, expiry=first_expiry_on_or_after(d20), sched_note=note)


SCH = pd.DataFrame([schedule(tk, d) for tk, d in zip(EV['ticker'], EV['date'])])
EV = pd.concat([EV, SCH], axis=1)

# =====================================================================================
# 3. Splits (Massive split records: runners files to 2026-09-30, then cached Massive calls)
# =====================================================================================
spl = pd.concat([pd.read_csv(os.path.join(REF, 'reverse_splits.csv'), keep_default_na=False),
                 pd.read_csv(os.path.join(REF, 'other_splits.csv'), keep_default_na=False)], ignore_index=True)
SPLITS_LOCAL_THROUGH = spl['execution_date'].max()
extra_spl = []
for f in sorted(glob.glob(os.path.join(CACHE, 'splits', '*.json'))):
    df = csv_rows(read_api(f))
    if len(df):
        extra_spl.append(df)
SPLITS_EXTRA_FILES = len(glob.glob(os.path.join(CACHE, 'splits', '*.json')))
if extra_spl:
    spl = pd.concat([spl] + extra_spl, ignore_index=True)
spl = spl.drop_duplicates(subset=['ticker', 'execution_date', 'split_from', 'split_to'])
SPL_BY = {k: g for k, g in spl.groupby('ticker')}
SPLIT_FETCH = ('/v3/reference/splits', {'execution_date.gte': '2026-10-01', 'execution_date.lte': '2026-10-16',
                                        'limit': 1000}, os.path.join(CACHE, 'splits', '2026-10-01_2026-10-16.json'))

# =====================================================================================
# 4. Per-event state from the cache
# =====================================================================================


def otick(t):
    return t[2:] if t.startswith('O:') else t


def p_contracts(tk, asof, exp, kind):
    return os.path.join(CACHE, 'contracts', f'{tk}_{asof}_{exp}_{kind}.json')


def p_aggs(opt, a, b):
    return os.path.join(CACHE, 'optaggs', f'{otick(opt)}_{a}_{b}.json')


def p_check(opt, asof):
    return os.path.join(CACHE, 'check', f'{otick(opt)}_{asof}.json')


def contracts_req(tk, asof, exp, close, kind):
    params = {'underlying_ticker': tk, 'contract_type': 'put', 'as_of': asof, 'expiration_date': exp,
              'limit': 1000}
    if kind == 'w':
        params['strike_price.gte'] = round(close * WIN_LO, 4)
        params['strike_price.lte'] = round(close * WIN_HI, 4)
    elif kind == 'w25':
        params['strike_price.gte'] = round(close * 0.75, 4)
        params['strike_price.lte'] = round(close * 1.25, 4)
    return ('/v3/reference/options/contracts', params, p_contracts(tk, asof, exp, kind))


def standard(df, tk):
    """Standard contracts only: 100 shares, this underlying, no extra deliverables, root = ticker."""
    if not len(df):
        return df
    m = (df['contract_type'] == 'put') & (df['underlying_ticker'] == tk)
    m &= pd.to_numeric(df['shares_per_contract'], errors='coerce') == 100
    m &= df['ticker'].str.match(r'^O:' + tk.replace('.', r'\.') + r'\d{6}P\d{8}$')
    if 'additional_underlyings' in df.columns:
        m &= df['additional_underlyings'].astype(str).isin(['', 'nan', 'None', '[]'])
    return df[m]


def nyday(ms):
    return pd.Timestamp(int(ms), unit='ms', tz='UTC').tz_convert('America/New_York').strftime('%Y-%m-%d')


def splits_between(tk, a, b):
    """Split records for tk executing after a and on or before b."""
    g = SPL_BY.get(tk)
    if g is None:
        return []
    g = g[(g['execution_date'] > a) & (g['execution_date'] <= b)]
    return [f"{r.execution_date} {r.split_from}:{r.split_to} {r.adjustment_type}" for r in g.itertuples()]


def evaluate(ev):
    """Walk one event through the pre-registered steps. Returns (record, next needed call or None)."""
    tk, d, close = ev['ticker'], ev['date'], float(ev['close_raw'])
    rec = dict(test=ev['test'], date=d, ticker=tk, half=1 if d < HALF2_FROM else 2, mv_bucket=ev['mv_bucket'],
               fresh_supply=ev['fresh_supply'], repeat_spiker=ev['repeat_spiker'], whole_count=ev['whole_count'],
               turnover=ev['turnover'], close_raw=close, ret20_gross=ev['ret20_gross'], ret20_net=ev['ret20_net'],
               t1=ev['t1'], t2=ev['t2'], day20=ev['d20'], expiry=ev['expiry'], sched_note=ev['sched_note'],
               status='', note='', contract='', strike=np.nan, strikes_listed=np.nan, entry_date='',
               entry_price=np.nan, entry_volume=np.nan, stock_close_expiry=np.nan, payoff=np.nan,
               premium_pct_of_close=np.nan, ret_cost0=np.nan, ret_cost10=np.nan, ret_cost20=np.nan)
    if ev['t1'] is None or ev['t1'] != ev['t1']:
        rec.update(status='no stock close at expiry',
                   note='no stock bar under this ticker after the mover day (ticker change or delisting); not looked up')
        return rec, None
    asof, exp = ev['t1'], ev['expiry']
    # step 1: listed puts on the expiry, as of t+1. The full list for the expiry is used; a few early
    # calls asked only for strikes within 0.5x-1.5x of the close, which holds the closest strike whenever
    # it is not empty (an empty window is followed by the full list).
    rqw = contracts_req(tk, asof, exp, close, 'w')
    rqa = contracts_req(tk, asof, exp, close, 'all')
    txt = read_api(rqw[2], rqw[1])
    if txt is None and read_api(rqa[2], rqa[1]) is None and ev['mv_bucket'] == '>=$300M':
        # large names list long chains: ask for strikes within +-25% of the close first (symmetric, so it
        # holds the closest strike whenever it is not empty)
        rqw = contracts_req(tk, asof, exp, close, 'w25')
        txt = read_api(rqw[2], rqw[1])
        if txt is None:
            return rec, rqw
    df = standard(csv_rows(txt), tk) if txt is not None else pd.DataFrame()
    nonstd = (len(csv_rows(txt)) - len(df)) if txt is not None else 0
    if not len(df):
        txt = read_api(rqa[2], rqa[1])
        if txt is None:
            return rec, rqa
        allr = csv_rows(txt)
        df = standard(allr, tk)
        nonstd = len(allr) - len(df)
        if not len(df):
            rec.update(status='no put listed',
                       note=(f'{len(allr)} non-standard puts only' if len(allr) else ''))
            return rec, None
    df = df.copy()
    df['k'] = df['strike_price'].astype(float)
    df['dist'] = (df['k'] - close).abs()
    best = df.sort_values(['dist', 'k'], ascending=[True, False]).iloc[0]   # ties go to the higher strike
    opt, K = best['ticker'], float(best['k'])
    rec.update(contract=opt, strike=K, strikes_listed=len(df))
    if nonstd:
        rec['note'] = f'{nonstd} non-standard puts ignored'
    # step 2: entry at the option's VWAP on t+1, else t+2
    rq = ('/v2/aggs/ticker/' + opt + f'/range/1/day/{ev["t1"]}/{ev["t2"]}', None, p_aggs(opt, ev['t1'], ev['t2']))
    txt = read_api(rq[2])
    if txt is None:
        return rec, rq
    ab = csv_rows(txt)
    fill = None
    if len(ab) and 't' in ab.columns:          # a contract with no bars returns only 'ticker,adjusted'
        ab['day'] = [nyday(x) for x in ab['t']]
        for day in (ev['t1'], ev['t2']):
            hit = ab[ab['day'] == day]
            if len(hit):
                fill = (day, float(hit['vw'].iloc[0]), float(hit['v'].iloc[0]))
                break
    if fill is None:
        rec['status'] = 'no fill'
        return rec, None
    rec.update(entry_date=fill[0], entry_price=fill[1], entry_volume=fill[2],
               premium_pct_of_close=fill[1] / close)
    # step 3: adjustments before expiry: Massive split records (stock splits and stock dividends), then
    # the contract's own reference record as of expiry day (an adjusted contract is renamed, so its
    # original ticker is not found)
    sp = splits_between(tk, d, exp)
    if sp:
        rec.update(status='adjusted', note='split record ' + '; '.join(sp))
        return rec, None
    if exp > SPLITS_LOCAL_THROUGH and not os.path.exists(SPLIT_FETCH[2]):
        return rec, SPLIT_FETCH
    if exp > LAST_SESSION_BEFORE_RUN:
        rec.update(status='no stock close at expiry', note=f'expiry {exp} is after the run date')
        return rec, None
    rq = ('/v3/reference/options/contracts/' + opt, {'as_of': exp}, p_check(opt, exp))
    txt = read_api(rq[2], rq[1])
    if txt is None:
        return rec, rq
    cdf = csv_rows(txt)
    ok = (len(cdf) == 1 and str(cdf['ticker'].iloc[0]) == opt
          and float(cdf['strike_price'].iloc[0]) == K and str(cdf['expiration_date'].iloc[0]) == exp
          and pd.to_numeric(cdf['shares_per_contract'], errors='coerce').iloc[0] == 100
          and str(cdf['underlying_ticker'].iloc[0]) == tk
          and ('additional_underlyings' not in cdf.columns
               or str(cdf['additional_underlyings'].iloc[0]) in ('', 'nan', 'None', '[]')))
    if not ok:
        why = ('not found as of expiry' if is_not_found(txt)
               else 'terms differ as of expiry: ' + txt.strip().replace(NL, ' | ')[:200])
        rec.update(status='adjusted', note='contract ' + why)
        return rec, None
    # step 4: the stock's raw close on expiry day
    if exp > LAST_KNOWN:
        return rec, GROUPED_REQ(exp)
    sc = bars.get(tk, {}).get(exp)
    if sc is None:
        rec.update(status='no stock close at expiry', note='no stock bar on expiry day')
        return rec, None
    pay = max(K - sc, 0.0)
    rec.update(status='filled', stock_close_expiry=sc, payoff=pay)
    for c in COSTS:
        rec[f'ret_cost{int(round(c * 100))}'] = pay / (fill[1] * (1 + c)) - 1
    return rec, None


def GROUPED_REQ(day):
    return ('/v2/aggs/grouped/locale/us/market/stocks/' + day, {'adjusted': 'false'},
            os.path.join(CACHE, 'grouped', f'{day}.json'))


def run_all():
    recs, need = [], []
    for _, ev in EV.iterrows():
        r, q = evaluate(ev)
        recs.append(r)
        if q is not None:
            need.append((r['test'], r['date'], r['ticker'], q))
    return pd.DataFrame(recs), need


# =====================================================================================
# 5. plan: the calls still missing
# =====================================================================================
if len(sys.argv) > 1 and sys.argv[1] == 'plan':
    # Prints the next N calls, leaving out the ones printed last time that are not cached yet (they are
    # being made while this runs). Then waits so that batches are at least PACE seconds apart (the free
    # tier allows about 5 calls a minute).
    import time
    t0 = time.time()
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    pace = float(sys.argv[3]) if len(sys.argv) > 3 else 62
    infl_path = os.path.join(CACHE, 'inflight.json')
    infl = json.load(open(infl_path)) if os.path.exists(infl_path) else []
    infl = {x for x in infl if not os.path.exists(os.path.join(HERE, x))}
    R, need = run_all()
    seen, out = set(), []
    for test, d, tk, (path, params, save) in need:
        rel = os.path.relpath(save, HERE).replace(os.sep, '/')
        if rel in seen or rel in infl:
            continue
        seen.add(rel)
        out.append((rel, dict(path=path, params=params) if params else dict(path=path)))
    st = R['status'].replace('', 'pending').value_counts().to_dict()
    log(f'# missing {len(out)} (+{len(infl)} in flight); events waiting {len(need)}; ' + json.dumps(st))
    for rel, o in out[:n]:
        log(json.dumps(o, separators=(',', ':')))
    json.dump([rel for rel, _ in out[:n]], open(infl_path, 'w'))
    time.sleep(max(0.0, pace - (time.time() - t0)))
    sys.exit(0)

if len(sys.argv) > 1 and sys.argv[1] == 'interim':
    # INTERIM readout from the cache only: no API calls, no bootstrap, no pass or fail call.
    R, need = run_all()
    R.loc[R['status'] == '', 'status'] = 'pending'
    out = {}
    for test in ('T1', 'T2'):
        s_ = R[R['test'] == test]
        done = s_[s_['status'] != 'pending']
        f = done[done['status'] == 'filled']
        o = dict(sampled=int(len(s_)), evaluated=int(len(done)), pending=int((s_['status'] == 'pending').sum()),
                 counts={k: int((done['status'] == k).sum()) for k in
                         ('no put listed', 'no fill', 'adjusted', 'no stock close at expiry', 'filled')},
                 had_entry_price=int(done['entry_price'].notna().sum()),
                 evaluated_dates=[done['date'].min(), done['date'].max()] if len(done) else None)
        if len(f):
            for c in COSTS:
                k = f'ret_cost{int(round(c * 100))}'
                y = f[k].values.astype(float)
                o[k] = dict(n=int(len(y)), mean=float(y.mean()), median=float(np.median(y)),
                            share_over_100=float((y > 1.0).mean()))
            o['share_paid_anything'] = float((f['payoff'] > 0).mean())
            o['stock_ret20_net'] = summ_simple = dict(n=int(f['ret20_net'].notna().sum()),
                                                      mean=float(f['ret20_net'].mean()),
                                                      median=float(f['ret20_net'].median()))
            o['stock_ret20_gross'] = dict(n=int(f['ret20_gross'].notna().sum()), mean=float(f['ret20_gross'].mean()),
                                          median=float(f['ret20_gross'].median()))
            o['premium_pct_of_close'] = dict(mean=float(f['premium_pct_of_close'].mean()),
                                             median=float(f['premium_pct_of_close'].median()))
            o['by_half_filled'] = {int(h): int((f['half'] == h).sum()) for h in (1, 2)}
        out[test] = o
    log(json.dumps(out, indent=1))
    sys.exit(0)

if len(sys.argv) > 1 and sys.argv[1] == 'events':
    cols = ['test', 'date', 'ticker', 'close_raw', 'mv_bucket', 't1', 't2', 'd20', 'expiry', 'sched_note']
    EV[cols].to_csv(sys.stdout, index=False)
    sys.exit(0)

# =====================================================================================
# 6. Analysis (cache only)
# =====================================================================================
R, need = run_all()
if need:
    log(f'WARNING: {len(need)} events still wait for API calls; they are reported as pending')
    R.loc[R['status'] == '', 'status'] = 'pending'


def summ(y):
    y = np.asarray(y, float)
    y = y[np.isfinite(y)]
    if len(y) == 0:
        return dict(n=0, mean=None, median=None, pos=None)
    return dict(n=int(len(y)), mean=float(y.mean()), median=float(np.median(y)), pos=float((y > 0).mean()))


def boot_ci(days, y):
    """Day-clustered bootstrap (same code as MV1): resample whole event days, NBOOT draws, fixed seed."""
    days = np.asarray(days); y = np.asarray(y, float)
    m = np.isfinite(y)
    days, y = days[m], y[m]
    ud, did = np.unique(days, return_inverse=True)
    nd = len(ud)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.integers(0, nd, size=(NBOOT, nd))
    W = np.zeros((NBOOT, nd))
    for b in range(NBOOT):
        W[b] = np.bincount(draws[b], minlength=nd)
    S = np.bincount(did, weights=y, minlength=nd)
    C = np.bincount(did, minlength=nd).astype(float)
    stat = (W @ S) / (W @ C)
    return dict(lo=float(np.percentile(stat, 2.5)), hi=float(np.percentile(stat, 97.5)), days=int(nd))


def selfcheck(y):
    y = np.asarray(y, float); y = y[np.isfinite(y)]
    n = len(y)
    w, l = y[y > 0], y[y < 0]
    lhs = (len(w) / n) * (w.mean() if len(w) else 0) - (len(l) / n) * ((-l).mean() if len(l) else 0)
    return dict(n=n, wins=int(len(w)), losses=int(len(l)), avg_win=float(w.mean()) if len(w) else 0.0,
                avg_loss=float((-l).mean()) if len(l) else 0.0, lhs=float(lhs), mean=float(y.mean()),
                ok=bool(abs(lhs - y.mean()) < 1e-12))


def block(df, test):
    s = df[df['test'] == test]
    f = s[s['status'] == 'filled']
    out = dict(sampled=int(len(s)), status_counts=s['status'].value_counts().to_dict())
    out['put_listed'] = int((s['status'] != 'no put listed').sum() - (s['status'] == 'pending').sum())
    out['no_put_listed'] = int((s['status'] == 'no put listed').sum())
    out['filled'] = int(s['entry_price'].notna().sum())          # had an entry price
    out['no_fill'] = int((s['status'] == 'no fill').sum())
    out['adjusted'] = int((s['status'] == 'adjusted').sum())
    out['no_close_at_expiry'] = int((s['status'] == 'no stock close at expiry').sum())
    out['used'] = int(len(f))
    out['events_with_entry_on_t2'] = int(((s['entry_date'] != '') & (s['entry_date'] == s['t2'])
                                          & (s['entry_date'] != s['t1'])).sum())
    for c in COSTS:
        k = f'ret_cost{int(round(c * 100))}'
        y = f[k].values
        r = summ(y)
        if len(f):
            r['ci'] = boot_ci(f['date'].values, y)
            r['halves'] = {h: summ(f.loc[f['half'] == h, k].values) for h in (1, 2)}
            r['share_over_100'] = float((y > 1.0).mean())
            r['selfcheck'] = selfcheck(y)
        out[k] = r
    if len(f):
        out['share_paid_anything'] = float((f['payoff'] > 0).mean())
        out['premium_pct_of_close'] = summ(f['premium_pct_of_close'].values)
        out['stock_ret20_net'] = summ(f['ret20_net'].values)
        out['stock_ret20_gross'] = summ(f['ret20_gross'].values)
        out['stock_close_expiry_vs_mover_close'] = summ((f['stock_close_expiry'] / f['close_raw'] - 1).values)
        out['strike_vs_close'] = summ((f['strike'] / f['close_raw'] - 1).values)
        out['days'] = int(f['date'].nunique())
        out['entry_volume_median'] = float(f['entry_volume'].median())
        out['by_mv'] = {b: summ(f.loc[f['mv_bucket'] == b, 'ret_cost10'].values)
                        for b in ('$50M-$300M', '>=$300M', 'unknown')}
    return out


res = dict(prereg='research/movers/PREREG_PUT1.md (git 60e910c)', run_date=datetime.date.today().isoformat(),
           pools=dict(T1=int(len(pool1)), T2=int(len(pool2))), last_bars=LAST_KNOWN,
           grouped_extra_days=GROUPED_EXTRA, splits_local_through=SPLITS_LOCAL_THROUGH,
           pending=len(need))
res['T1'] = block(R, 'T1')
res['T2'] = block(R, 'T2')
t = res['T1']['ret_cost10']
if t['n']:
    res['T1']['pass'] = dict(mean_above_zero=bool(t['mean'] > 0), ci_above_zero=bool(t['ci']['lo'] > 0),
                             both_halves_positive=bool(all(t['halves'][h]['n'] and t['halves'][h]['mean'] > 0
                                                           for h in (1, 2))))
    res['T1']['pays'] = bool(all(res['T1']['pass'].values()))

cols = ['test', 'date', 'ticker', 'half', 'mv_bucket', 'fresh_supply', 'repeat_spiker', 'whole_count', 'turnover',
        'close_raw', 't1', 't2', 'day20', 'expiry', 'status', 'contract', 'strike', 'strikes_listed', 'entry_date',
        'entry_price', 'entry_volume', 'premium_pct_of_close', 'stock_close_expiry', 'payoff', 'ret_cost0',
        'ret_cost10', 'ret_cost20', 'ret20_gross', 'ret20_net', 'note', 'sched_note']
for test in ('T1', 'T2'):
    R.loc[R['test'] == test, cols].to_csv(os.path.join(HERE, f'trades_{test}.csv'), index=False)


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


with open(os.path.join(HERE, 'results.json'), 'w', encoding='utf-8') as fh:
    json.dump(clean(res), fh, indent=1)
log(json.dumps(clean({k: res[k] for k in ('pools', 'pending')}), indent=1))
log('T1 statuses', res['T1']['status_counts'])
log('T2 statuses', res['T2']['status_counts'])
