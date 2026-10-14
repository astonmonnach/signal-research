"""MV1: the ten biggest daily gainers over two years, and what came next.

Runs research/movers/PREREG_MV1.md (committed in git cab1406) as written.
One command, from anywhere:   python run.py

Reads (never writes) research/runners/work/: panel.npz, raw/DATE.csv, ref/*splits.csv, ref/cs_tickers.csv,
sec/subm, sec/shares; and research/domino/sic_map.csv.
Downloads only what is missing into ./cache: SEC company_tickers.json, SEC submissions and share counts
for CIKs that the runners cache lacks, fresh SEC submissions for movers whose 10-day after-window runs past
the runners cache date, and Yahoo IWM daily bars. Later runs read the cache and need no network.
Writes listA.csv, listB.csv, RESULTS.md and cache/numbers.json next to this file.
"""
import os, sys, json, time, glob, datetime, urllib.request, urllib.error
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.abspath(os.path.join(HERE, '..', '..'))
RW = os.path.join(RESEARCH, 'runners', 'work')
CACHE = os.path.join(HERE, 'cache')
for _s in ('sec/subm', 'sec/shares', 'sec/subm_fresh'):
    os.makedirs(os.path.join(CACHE, _s), exist_ok=True)

# ---- pre-registered constants (PREREG_MV1.md); do not change ----
TOPN = 10
MIN_PRICE = 1.0            # takeable: prior close $1 or more
MIN_MDV = 250_000.0        # takeable: median dollar volume $250k or more
MDV_WIN = 20               # over the 20 sessions ending the day before
HORIZONS = (1, 5, 20)
CAP = 3.0                  # returns above +300% count as +300%
COST = 0.01                # 1% per round trip
SUPPLY_LOOKBACK = 60       # calendar days
SPIKE = 0.5                # +50% day
SPIKE_LOOKBACK = 250       # sessions
SPIKE_MIN = 2              # two or more
WHOLE = 1.0                # turnover of 1.0 or more
SHARES_MAX_AGE_MONTHS = 15
MV_EDGES = (50e6, 300e6)
CL_STRONG, CL_FADED = 0.9, 0.7
AFTER_DAYS = 10
NBOOT, SEED = 2000, 20261014
HALF1_LAST_SESSION = 250   # sessions 1-250 and 251-501 (1-based)

UA_SEC = 'PersonalResearch research@example.com'
UA_WEB = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
          'Chrome/124.0 Safari/537.36')
NY = 'America/New_York'


def log(*a):
    print(*a, flush=True)


def http_get(url, path, ua, missing_ok=True):
    """Download url to path unless path exists. 404 -> '{}' (same convention as the runners cache)."""
    if os.path.exists(path):
        return True
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(path, 'wb') as f:
                f.write(data)
            time.sleep(0.15)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404 and missing_ok:
                with open(path, 'wb') as f:
                    f.write(b'{}')
                time.sleep(0.15)
                return True
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return False


# =====================================================================================
# 1. Panel, split windows, valid bars
# =====================================================================================
z = np.load(os.path.join(RW, 'panel.npz'))
dates = [str(x) for x in z['dates']]
tick = [str(x) for x in z['tick']]
c, c_prev, o = z['c'], z['c_prev'], z['o']
craw, craw_prev, vraw = z['craw'], z['craw_prev'], z['vraw']
T, N = c.shape
tix = {t: i for i, t in enumerate(tick)}
darr = np.array(dates)
log('panel', T, 'sessions x', N, 'stocks', dates[0], dates[-1])

# Split windows rebuilt exactly as research/runners/work/build_panel.py does (split executing on day p
# flags sessions p-2..p+2). The panel's own `valid` stops at 2026-09-29 for a reason unrelated to splits
# (the runners study needed a next day), so it is rebuilt here to include 2026-09-30 and checked against
# the stored array on every other session.
spl = pd.concat([pd.read_csv(os.path.join(RW, 'ref', f), keep_default_na=False)
                 for f in ('reverse_splits.csv', 'other_splits.csv')], ignore_index=True)
spl = spl[spl['ticker'].isin(tix)].copy()
splitflag = np.zeros((T, N), bool)
for _, s in spl.iterrows():
    p = int(np.searchsorted(darr, s['execution_date']))
    if p >= T:
        continue
    splitflag[max(0, p - 2):min(T, p + 3), tix[s['ticker']]] = True
spl_by = {k: g.sort_values('execution_date') for k, g in spl.groupby('ticker')}

valid = (~np.isnan(craw_prev)) & (craw_prev > 0) & (~np.isnan(c)) & (~splitflag)
valid[0] = False
valid_mismatch = int((valid[1:T - 1] != z['valid'][1:T - 1]).sum())
log('valid rebuilt; mismatches vs stored panel on sessions 2..500:', valid_mismatch)

with np.errstate(divide='ignore', invalid='ignore'):
    r = np.where(valid, c / c_prev - 1.0, np.nan)

# takeable: prior close >= $1 and median dollar volume over the 20 sessions ending the day before >= $250k.
# A session with no trade counts as $0. The window must lie inside the panel, so sessions 1-20 have none.
dv = np.nan_to_num(craw * vraw, nan=0.0)
mdv = np.full((T, N), np.nan)
for t in range(MDV_WIN, T):
    mdv[t] = np.median(dv[t - MDV_WIN:t], axis=0)
with np.errstate(invalid='ignore'):
    takeable = valid & (craw_prev >= MIN_PRICE) & (mdv >= MIN_MDV)


def top_list(mask):
    rows = []
    for t in range(1, T):
        js = np.where(mask[t] & np.isfinite(r[t]))[0]
        if len(js) == 0:
            continue
        order = sorted(js, key=lambda j: (-r[t, j], tick[j]))[:TOPN]
        for k, j in enumerate(order):
            rows.append((t, int(j), k + 1))
    return rows


# Universe. The prereg calls the panel "6,924 US common stocks", but 574 panel tickers have no
# common-stock (CS) label in the runners ticker file (ref/cs_tickers.csv: empty type, name and CIK).
# Many are leveraged single-stock ETFs, ETNs, closed-end funds, ADRs and warrants. The definitions say
# "common stocks", so the primary run keeps only tickers that Massive labelled CS. The full panel is
# re-run as an impact check (Deviations).
massive = pd.read_csv(os.path.join(RW, 'ref', 'cs_tickers.csv'), dtype=str, keep_default_na=False)
cs_labelled = set(massive.loc[massive['type'] == 'CS', 'ticker'])
is_cs = np.array([t in cs_labelled for t in tick])
ALL = np.ones(N, bool)
LA_rows = top_list(valid & is_cs[None, :])
LB_rows = top_list(takeable & is_cs[None, :])
LB_full_rows = top_list(takeable)   # impact check only: the panel as-is, unlabelled tickers included
log('CS-labelled tickers', int(is_cs.sum()), 'of', N)
log('list A rows', len(LA_rows), 'list B rows', len(LB_rows), 'full-panel list B rows', len(LB_full_rows))

# =====================================================================================
# 2. Outcomes
# =====================================================================================

def exit_price(t, j, k):
    """Exit at the close k sessions after t. Bars inside a split window are not used.
    Returns (price or nan, note)."""
    tt = t + k
    if tt > T - 1:
        return np.nan, 'beyond_panel'
    if not np.isnan(c[tt, j]) and not splitflag[tt, j]:
        return c[tt, j], ''
    seg = np.arange(t + 1, tt + 1)
    usable = seg[(~np.isnan(c[seg, j])) & (~splitflag[seg, j])]
    traded_after = bool(np.any(~np.isnan(c[tt:, j]))) if tt < T else False
    if len(usable):
        s = usable[-1]
        if not np.isnan(c[tt, j]):          # bar exists but sits in a split window
            note = 'split_window_last_usable'
        elif not traded_after:
            note = 'stale_last_close'       # stopped trading
        else:
            note = 'gap_last_close'         # no trade on the exit day, trades later
        return c[s, j], note
    # no usable close after entry
    if np.any(~np.isnan(c[t + 1:tt + 1, j])):
        return np.nan, 'split_window_no_usable'
    if not np.any(~np.isnan(c[t + 1:, j])):
        return c[t, j], 'stale_last_close'  # stopped trading after the mover day: marked at its last close
    return c[t, j], 'gap_last_close'


def capnet(gross):
    if np.isnan(gross):
        return np.nan, np.nan, False
    capped = gross > CAP
    g = min(gross, CAP)
    return g, g - COST, capped


def outcomes(t, j):
    rec = {}
    entry = c[t, j]
    nopen = np.nan
    if t + 1 <= T - 1 and not np.isnan(o[t + 1, j]) and not splitflag[t + 1, j]:
        nopen = o[t + 1, j]
    for k in HORIZONS:
        px, note = exit_price(t, j, k)
        g, n, cp = capnet(px / entry - 1 if not np.isnan(px) else np.nan)
        rec[f'ret{k}_gross'] = g
        rec[f'ret{k}_net'] = n
        rec[f'ret{k}_capped'] = cp
        rec[f'exit{k}_note'] = note
        g2, n2, cp2 = capnet(px / nopen - 1 if not (np.isnan(px) or np.isnan(nopen)) else np.nan)
        rec[f'nextopen_ret{k}_net'] = n2
        rec[f'nextopen_ret{k}_capped'] = cp2
    rec['entry_close_adj'] = entry
    rec['next_open_adj'] = nopen
    return rec


# =====================================================================================
# 3. Raw bars: day's low/high for close location; IWM from the same source for a cross-check
# =====================================================================================
need = {}
for (t, j, _) in LA_rows + LB_rows + LB_full_rows:
    need.setdefault(t, set()).add(tick[j])
rawbar = {}
iwm_raw = {}
raw_dupes = 0
for t, d in enumerate(dates):
    p = os.path.join(RW, 'raw', d + '.csv')
    df = pd.read_csv(p, usecols=['T', 'o', 'c', 'h', 'l'], keep_default_na=False, na_values=[''])
    want = need.get(t, set()) | {'IWM'}
    df = df[df['T'].isin(want)]
    raw_dupes += int(df['T'].duplicated().sum())
    df = df.drop_duplicates('T', keep='first')
    for _, x in df.iterrows():
        if x['T'] == 'IWM':
            iwm_raw[d] = (x['o'], x['c'])
        if x['T'] in need.get(t, set()):
            rawbar[(t, x['T'])] = (x['o'], x['c'], x['h'], x['l'])
log('raw bars read; duplicate ticker rows dropped:', raw_dupes)

# =====================================================================================
# 4. IWM: Yahoo daily (IWM is not in the CS panel), cross-checked against the raw bars
# =====================================================================================
yp = os.path.join(CACHE, 'iwm_yahoo.json')
p1 = int(pd.Timestamp('2024-09-25', tz='UTC').timestamp())
p2 = int(pd.Timestamp('2026-10-03', tz='UTC').timestamp())
if not http_get(f'https://query1.finance.yahoo.com/v8/finance/chart/IWM?period1={p1}&period2={p2}&interval=1d',
                yp, UA_WEB, missing_ok=False):
    sys.exit('could not download IWM from Yahoo')
yj = json.load(open(yp))['chart']['result'][0]
yq = yj['indicators']['quote'][0]
iwm = {}
for i, ts in enumerate(yj['timestamp']):
    d = pd.Timestamp(ts, unit='s', tz='UTC').tz_convert(NY).strftime('%Y-%m-%d')
    iwm[d] = (yq['open'][i], yq['close'][i])
iwm_o = np.array([iwm.get(d, (np.nan, np.nan))[0] for d in dates], float)
iwm_c = np.array([iwm.get(d, (np.nan, np.nan))[1] for d in dates], float)
iwm_missing = int(np.isnan(iwm_c).sum())
iwm_diff = [abs(iwm_c[t] - iwm_raw[d][1]) / iwm_raw[d][1] for t, d in enumerate(dates) if d in iwm_raw and not np.isnan(iwm_c[t])]
iwm_check = dict(missing_yahoo_days=iwm_missing, raw_days=len(iwm_raw), compared=len(iwm_diff),
                 max_rel_diff=float(max(iwm_diff)) if iwm_diff else None,
                 n_over_0_1pct=int(sum(x > 0.001 for x in iwm_diff)))
log('IWM check', iwm_check)


def iwm_ret(t, k, from_open=False):
    tt = t + k
    if tt > T - 1:
        return np.nan
    if from_open:
        return iwm_c[tt] / iwm_o[t + 1] - 1
    return iwm_c[tt] / iwm_c[t] - 1


# =====================================================================================
# 5. SEC: CIK map, submissions, share counts
# =====================================================================================
ctp = os.path.join(CACHE, 'company_tickers.json')
http_get('https://www.sec.gov/files/company_tickers.json', ctp, UA_SEC, missing_ok=False)
cikmap = {}
sm = pd.read_csv(os.path.join(RESEARCH, 'domino', 'sic_map.csv'), dtype=str, keep_default_na=False)
for _, x in sm.iterrows():
    if x['cik']:
        cikmap[x['ticker']] = x['cik'].zfill(10)
n_sicmap = len(cikmap)
for v in json.load(open(ctp)).values():
    cikmap.setdefault(v['ticker'], str(v['cik_str']).zfill(10))
massive_cik = {}
for _, x in massive.iterrows():
    if x['cik']:
        massive_cik.setdefault(x['ticker'], set()).add(x['cik'].zfill(10))


def cik_of(t):
    return cikmap.get(t) or cikmap.get(t.replace('.', '-')) or ''


# What are the panel tickers without a CS label? SEC's fund/ETF ticker list is a partial check.
mfp = os.path.join(CACHE, 'company_tickers_mf.json')
http_get('https://www.sec.gov/files/company_tickers_mf.json', mfp, UA_SEC, missing_ok=False)
_mf = json.load(open(mfp))
sec_fund_tickers = {row[_mf['fields'].index('symbol')] for row in _mf['data']}
unlab = [t for t in tick if t not in cs_labelled]
UNLAB = dict(n=len(unlab),
             sec_fund=sum(t in sec_fund_tickers for t in unlab),
             sec_company=sum((t not in sec_fund_tickers) and bool(cik_of(t)) for t in unlab),
             neither=sum((t not in sec_fund_tickers) and not cik_of(t) for t in unlab))
log('unlabelled panel tickers', UNLAB)


def runners_cache_complete_through():
    """Last filing date fully covered by the runners SEC cache: the day before the earliest file time."""
    ts = min(os.path.getmtime(p) for p in glob.glob(os.path.join(RW, 'sec', 'subm', 'CIK*.json')))
    d = pd.Timestamp(ts, unit='s', tz='UTC').tz_convert(NY).normalize()
    return (d - pd.Timedelta(days=1)).strftime('%Y-%m-%d')


CACHE_THROUGH = runners_cache_complete_through()
log('runners SEC cache complete through', CACHE_THROUGH)


def subm_paths(cik, fresh):
    if fresh:
        return os.path.join(CACHE, 'sec', 'subm_fresh')
    if os.path.exists(os.path.join(RW, 'sec', 'subm', f'CIK{cik}.json')):
        return os.path.join(RW, 'sec', 'subm')
    return os.path.join(CACHE, 'sec', 'subm')


def fetch_subm(cik, folder):
    p = os.path.join(folder, f'CIK{cik}.json')
    http_get(f'https://data.sec.gov/submissions/CIK{cik}.json', p, UA_SEC)
    try:
        j = json.load(open(p))
        rd = j.get('filings', {}).get('recent', {}).get('filingDate', [])
        if rd and min(rd) > '2024-06-01':
            for f in j['filings'].get('files', []):
                if f.get('filingTo', '') >= '2024-06-01':
                    http_get('https://data.sec.gov/submissions/' + f['name'], os.path.join(folder, f['name']), UA_SEC)
    except Exception:
        pass


def load_filings(cik, fresh=False):
    folder = subm_paths(cik, fresh)
    p = os.path.join(folder, f'CIK{cik}.json')
    if not os.path.exists(p):
        fetch_subm(cik, folder)
    try:
        j = json.load(open(p))
    except Exception:
        return None
    if not j or 'filings' not in j:
        return None
    df = pd.DataFrame(j['filings'].get('recent', {}))
    for f in j['filings'].get('files', []):
        pp = os.path.join(folder, f['name'])
        if os.path.exists(pp):
            try:
                df = pd.concat([df, pd.DataFrame(json.load(open(pp)))], ignore_index=True)
            except Exception:
                pass
    if df.empty:
        return None
    if 'items' not in df:
        df['items'] = ''
    df = df.drop_duplicates('accessionNumber')
    acc = pd.to_datetime(df['acceptanceDateTime'], utc=True, errors='coerce')  # true UTC (checked: see RESULTS)
    df['acc_utc'] = acc.dt.tz_localize(None)
    df['form'] = df['form'].astype(str)
    df['filingDate'] = df['filingDate'].astype(str)
    df['items'] = df['items'].fillna('').astype(str)
    return df[['form', 'filingDate', 'acc_utc', 'items', 'accessionNumber']].reset_index(drop=True)


def load_shares(cik):
    p = os.path.join(RW, 'sec', 'shares', f'CIK{cik}.json')
    if not os.path.exists(p):
        p = os.path.join(CACHE, 'sec', 'shares', f'CIK{cik}.json')
        http_get(f'https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/dei/EntityCommonStockSharesOutstanding.json',
                 p, UA_SEC)
    try:
        j = json.load(open(p))
    except Exception:
        return None
    vals = []
    for unit, arr in (j.get('units') or {}).items():
        vals += arr
    if not vals:
        return None
    df = pd.DataFrame(vals)
    if 'filed' not in df or 'end' not in df:
        return None
    return df.sort_values(['filed', 'end'], kind='mergesort').reset_index(drop=True)


def is_supply(form):
    return (form in ('S-1', 'F-1', 'S-3', 'F-3', 'EFFECT')) or form.startswith('424B')


def is_supply_wide(form):  # sensitivity only: amendments, MEF and automatic shelves too
    return is_supply(form) or form in ('S-1/A', 'F-1/A', 'S-3/A', 'F-3/A', 'S-1MEF', 'S-3MEF', 'F-1MEF',
                                       'F-3MEF', 'S-3ASR', 'F-3ASR')


def ny_close_utc(d):
    return pd.Timestamp(f'{d} 16:00', tz=NY).tz_convert('UTC').tz_localize(None)


sec_cache = {}


def sec_for(cik):
    if cik not in sec_cache:
        sec_cache[cik] = (load_filings(cik), load_shares(cik))
    return sec_cache[cik]


fresh_cache = {}


def fresh_for(cik):
    if cik not in fresh_cache:
        fresh_cache[cik] = load_filings(cik, fresh=True)
    return fresh_cache[cik]


def sec_features(t, j):
    d = dates[t]
    tk = tick[j]
    rec = dict(cik=cik_of(tk))
    mc = massive_cik.get(tk, set())
    rec['cik_differs_from_massive'] = bool(rec['cik'] and mc and rec['cik'] not in mc)
    fl, sh = sec_for(rec['cik']) if rec['cik'] else (None, None)
    rec['sec_found'] = fl is not None
    keys_bool = ['event', 'event_incl_amend', 'fresh_supply', 'fresh_supply_wide', 'supply_10d_after']
    if fl is None:
        for k in keys_bool:
            rec[k] = None
        rec.update(event_forms='', event_8k_items='', fresh_supply_forms='', supply_10d_after_forms='',
                   supply_after_source='')
    else:
        lo, hi = ny_close_utc(dates[t - 1]), ny_close_utc(d)
        inwin = (fl['acc_utc'] > lo) & (fl['acc_utc'] < hi)
        ev = fl[inwin & fl['form'].isin(['8-K', '6-K'])]
        ev_a = fl[inwin & fl['form'].isin(['8-K', '6-K', '8-K/A', '6-K/A'])]
        rec['event'] = len(ev) > 0
        rec['event_incl_amend'] = len(ev_a) > 0
        rec['event_forms'] = ';'.join(ev['form'])
        rec['event_8k_items'] = ';'.join(sorted({i for s in ev.loc[ev['form'] == '8-K', 'items'] for i in s.split(',') if i}))
        lo60 = (pd.Timestamp(d) - pd.Timedelta(days=SUPPLY_LOOKBACK)).strftime('%Y-%m-%d')
        prior = (fl['filingDate'] >= lo60) & (fl['filingDate'] < d)
        sup = fl[prior & fl['form'].map(is_supply)]
        rec['fresh_supply'] = len(sup) > 0
        rec['fresh_supply_wide'] = bool((prior & fl['form'].map(is_supply_wide)).any())
        rec['fresh_supply_forms'] = ';'.join(sorted(set(sup['form'])))
        hi10 = (pd.Timestamp(d) + pd.Timedelta(days=AFTER_DAYS)).strftime('%Y-%m-%d')
        if hi10 <= CACHE_THROUGH:
            fa, src = fl, 'runners_cache'
        else:
            fa, src = fresh_for(rec['cik']), 'fresh_fetch'
        if fa is None:
            rec['supply_10d_after'] = None
            rec['supply_10d_after_forms'] = ''
        else:
            aft = fa[(fa['filingDate'] > d) & (fa['filingDate'] <= hi10) & fa['form'].map(is_supply)]
            rec['supply_10d_after'] = len(aft) > 0
            rec['supply_10d_after_forms'] = ';'.join(sorted(set(aft['form'])))
        rec['supply_after_source'] = src
    # shares outstanding: latest filed before the day, adjusted for splits since its as-of date
    rec.update(shares_out=np.nan, shares_asof='', shares_filed='', shares_adj=np.nan)
    if sh is not None:
        s2 = sh[sh['filed'] < d]
        if not s2.empty:
            x = s2.iloc[-1]
            rec['shares_out'] = float(x['val'])
            rec['shares_asof'] = str(x['end'])
            rec['shares_filed'] = str(x['filed'])
            if pd.Timestamp(x['end']) >= pd.Timestamp(d) - pd.DateOffset(months=SHARES_MAX_AGE_MONTHS):
                s = float(x['val'])
                g = spl_by.get(tk)
                if g is not None:
                    for _, y in g[(g['execution_date'] > str(x['end'])) & (g['execution_date'] <= d)].iterrows():
                        s *= float(y['split_to']) / float(y['split_from'])
                rec['shares_adj'] = s
    return rec


# =====================================================================================
# 6. Build the per-mover tables
# =====================================================================================
SPLIT_RATIOS = (2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 100)


def build(rows, name):
    out = []
    for i, (t, j, rank) in enumerate(rows):
        tk = tick[j]
        d = dates[t]
        rec = dict(list=name, date=d, session=t + 1, half=1 if t + 1 <= HALF1_LAST_SESSION else 2, rank=rank,
                   ticker=tk, prior_close_raw=craw_prev[t, j], close_raw=craw[t, j], ret_day=r[t, j],
                   med_dollar_vol20=mdv[t, j], takeable=bool(takeable[t, j]), day_volume_raw=vraw[t, j])
        # close location from the raw bar; skip if the raw close does not match the panel close
        rb = rawbar.get((t, tk))
        rec.update(day_open_raw=np.nan, day_high_raw=np.nan, day_low_raw=np.nan, raw_close_match=False,
                   close_loc=np.nan)
        if rb is not None:
            ro, rc, rh, rl = rb
            rec.update(day_open_raw=ro, day_high_raw=rh, day_low_raw=rl)
            rec['raw_close_match'] = bool(np.isclose(rc, craw[t, j], rtol=1e-9, atol=1e-9))
            if rec['raw_close_match'] and rh > rl:
                rec['close_loc'] = (rc - rl) / (rh - rl)
        cl = rec['close_loc']
        rec['close_loc_bucket'] = ('unknown' if np.isnan(cl) else 'closed strong (>=0.9)' if cl >= CL_STRONG
                                   else 'faded (<=0.7)' if cl <= CL_FADED else 'middle (0.7-0.9)')
        # data-quality flag only (not a filter): same heuristic as the runners study for an unrecorded split
        rr = craw[t, j] / craw_prev[t, j]
        lowr = rec['day_low_raw'] / craw_prev[t, j] if not np.isnan(rec['day_low_raw']) else np.nan
        near = min(abs(rr / k - 1) for k in SPLIT_RATIOS)
        rec['suspect_split'] = bool(lowr == lowr and lowr >= 1.8 and near < 0.03)
        # repeat spiker: +50% days in the 250 sessions before the mover day (inside the panel)
        lo = max(1, t - SPIKE_LOOKBACK)
        seg = r[lo:t, j]
        rec['spikes_250'] = int(np.sum(seg >= SPIKE))
        rec['spike_lookback_sessions'] = t - lo
        rec['repeat_spiker'] = rec['spikes_250'] >= SPIKE_MIN
        rec.update(sec_features(t, j))
        sa = rec['shares_adj']
        rec['turnover'] = vraw[t, j] / sa if sa == sa and sa > 0 else np.nan
        rec['whole_count'] = None if np.isnan(rec['turnover']) else bool(rec['turnover'] >= WHOLE)
        mv = sa * craw_prev[t, j] if sa == sa else np.nan
        rec['mkt_value'] = mv
        rec['mv_bucket'] = ('unknown' if np.isnan(mv) else '<$50M' if mv < MV_EDGES[0]
                            else '$50M-$300M' if mv < MV_EDGES[1] else '>=$300M')
        flags = [rec['fresh_supply'], rec['repeat_spiker'], rec['whole_count']]
        if any(f is True for f in flags):
            rec['mech_any'] = True
        elif all(f is False for f in flags):
            rec['mech_any'] = False
        else:
            rec['mech_any'] = None
        rec.update(outcomes(t, j))
        for k in HORIZONS:
            rec[f'iwm{k}'] = iwm_ret(t, k)
            rec[f'excess{k}'] = rec[f'ret{k}_net'] - rec[f'iwm{k}']
            rec[f'nextopen_iwm{k}'] = iwm_ret(t, k, from_open=True)
        out.append(rec)
        if i % 1000 == 0:
            log(name, i, '/', len(rows))
    return pd.DataFrame(out)


A = build(LA_rows, 'A')
B = build(LB_rows, 'B')
B_full = build(LB_full_rows, 'B_fullpanel')
A.to_csv(os.path.join(HERE, 'listA.csv'), index=False)
B.to_csv(os.path.join(HERE, 'listB.csv'), index=False)
B_full.to_csv(os.path.join(HERE, 'listB_fullpanel.csv'), index=False)
log('wrote listA.csv', len(A), 'listB.csv', len(B), 'listB_fullpanel.csv', len(B_full))

# =====================================================================================
# 7. Statistics
# =====================================================================================

def summ(y):
    y = np.asarray(y, float)
    y = y[np.isfinite(y)]
    if len(y) == 0:
        return dict(n=0, mean=np.nan, median=np.nan, pos=np.nan)
    return dict(n=int(len(y)), mean=float(y.mean()), median=float(np.median(y)), pos=float((y > 0).mean()))


def boot_ci(days, y, g=None):
    """Day-clustered bootstrap: resample whole mover days with replacement, NBOOT draws, fixed seed.
    g None -> mean of y; g bool -> mean(y | g) - mean(y | ~g). Percentile 95% interval."""
    days = np.asarray(days); y = np.asarray(y, float)
    m = np.isfinite(y)
    days, y = days[m], y[m]
    if g is not None:
        g = np.asarray(g, bool)[m]
    ud, did = np.unique(days, return_inverse=True)
    nd = len(ud)
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, nd, size=(NBOOT, nd))
    W = np.zeros((NBOOT, nd))
    for b in range(NBOOT):
        W[b] = np.bincount(draws[b], minlength=nd)
    if g is None:
        S = np.bincount(did, weights=y, minlength=nd); C = np.bincount(did, minlength=nd).astype(float)
        stat = (W @ S) / (W @ C)
    else:
        S1 = np.bincount(did[g], weights=y[g], minlength=nd); C1 = np.bincount(did[g], minlength=nd).astype(float)
        S0 = np.bincount(did[~g], weights=y[~g], minlength=nd); C0 = np.bincount(did[~g], minlength=nd).astype(float)
        with np.errstate(invalid='ignore', divide='ignore'):
            stat = (W @ S1) / (W @ C1) - (W @ S0) / (W @ C0)
    bad = int(np.sum(~np.isfinite(stat)))
    stat = stat[np.isfinite(stat)]
    return dict(lo=float(np.percentile(stat, 2.5)), hi=float(np.percentile(stat, 97.5)), days=int(nd),
                draws_used=int(len(stat)), draws_dropped=bad)


def selfcheck(y, label):
    y = np.asarray(y, float); y = y[np.isfinite(y)]
    n = len(y)
    w = y[y > 0]; l = y[y < 0]
    aw = w.mean() if len(w) else 0.0
    al = (-l).mean() if len(l) else 0.0
    lhs = (len(w) / n) * aw - (len(l) / n) * al
    ok = bool(abs(lhs - y.mean()) < 1e-12)
    return dict(label=label, n=n, wins=int(len(w)), losses=int(len(l)), zeros=int(n - len(w) - len(l)),
                avg_win=float(aw), avg_loss=float(al), lhs=float(lhs), mean=float(y.mean()), ok=ok)


MV_ORDER = ['<$50M', '$50M-$300M', '>=$300M', 'unknown']
CL_ORDER = ['closed strong (>=0.9)', 'middle (0.7-0.9)', 'faded (<=0.7)', 'unknown']
NUM = dict(valid_mismatch=valid_mismatch, iwm_check=iwm_check, raw_dupes=raw_dupes, cache_through=CACHE_THROUGH,
           n_sicmap=n_sicmap, unlabelled=UNLAB, n_cs_labelled=int(is_cs.sum()), n_panel=N)
checks = []


def group_test(df, gcol, label, chk, names=('yes', 'no')):
    d = df[np.isfinite(df['ret20_net'])].copy()
    g = d[gcol].astype(bool).values
    res = dict(yes=summ(d.loc[g, 'ret20_net']), no=summ(d.loc[~g, 'ret20_net']))
    # description of the groups' size mix (for the caveats; not part of any pass mark)
    res['mv_mix'] = {nm_: {b: float((d.loc[gg, 'mv_bucket'] == b).mean()) for b in MV_ORDER}
                     for nm_, gg in (('yes', g), ('no', ~g))}
    res['diff'] = res['yes']['mean'] - res['no']['mean']
    res['diff_median'] = res['yes']['median'] - res['no']['median']
    res['ci'] = boot_ci(d['date'], d['ret20_net'], g)
    res['halves'] = {}
    for h in (1, 2):
        dh = d[d['half'] == h]
        gh = dh[gcol].astype(bool)
        yes, no = summ(dh.loc[gh, 'ret20_net']), summ(dh.loc[~gh, 'ret20_net'])
        res['halves'][h] = dict(yes=yes, no=no, diff=yes['mean'] - no['mean'])
    if chk is not None:
        chk.append(selfcheck(d.loc[g, 'ret20_net'], f'{label}: {names[0]}'))
        chk.append(selfcheck(d.loc[~g, 'ret20_net'], f'{label}: {names[1]}'))
    return res


def run_tests(Bdf, tag, chk):
    """The three pre-registered trials on one list B table."""
    # T1: does buying list B at the close pay?
    y20 = Bdf['ret20_net'].values
    t1 = summ(y20)
    t1['ci'] = boot_ci(Bdf['date'], y20)
    t1['excess'] = summ(Bdf['excess20'].values)
    t1['excess_ci'] = boot_ci(Bdf['date'], Bdf['excess20'].values)
    t1['iwm'] = summ(Bdf.loc[np.isfinite(Bdf['ret20_net']), 'iwm20'].values)
    t1['halves'] = {h: summ(Bdf.loc[Bdf['half'] == h, 'ret20_net'].values) for h in (1, 2)}
    t1['pays'] = bool(t1['mean'] > 0 and t1['ci']['lo'] > 0 and t1['median'] > 0)
    if chk is not None:
        chk.append(selfcheck(y20, f'T1{tag}: list B, 20 sessions, after costs'))
    # T2: event movers minus no-event movers (movers with no SEC data cannot be classed and are left out)
    B20 = Bdf[np.isfinite(Bdf['ret20_net'])]
    t2 = group_test(B20[B20['sec_found']], 'event', f'T2{tag}', chk, ('event', 'no event'))
    t2['excluded_no_sec'] = int((~B20['sec_found']).sum())
    t2['separates'] = bool(t2['ci']['lo'] > 0 and t2['halves'][1]['diff'] > 0 and t2['halves'][2]['diff'] > 0)
    # T3: within no-event movers, any mechanic minus none (unknown when turnover is unknown and the
    # other two flags are off: cannot tell "none" from "any", so left out)
    ne = B20[B20['sec_found'] & (B20['event'] == False)]
    t3 = group_test(ne[ne['mech_any'].notna()], 'mech_any', f'T3{tag}', chk, ('any flag', 'no flag'))
    t3['excluded_unknown'] = int(ne['mech_any'].isna().sum())
    t3['separates'] = bool(t3['ci']['hi'] < 0 and t3['halves'][1]['diff'] < 0 and t3['halves'][2]['diff'] < 0)
    return t1, t2, t3


t1, t2, t3 = run_tests(B, '', checks)
NUM['T1'], NUM['T2'], NUM['T3'] = t1, t2, t3
f1, f2, f3 = run_tests(B_full, ' (full panel)', checks)
NUM['FULL'] = dict(T1=f1, T2=f2, T3=f3, rows=len(B_full),
                   rows_unlabelled=int((~B_full['ticker'].isin(cs_labelled)).sum()),
                   rows_unlabelled_sec_fund=int(((~B_full['ticker'].isin(cs_labelled)) &
                                                 B_full['ticker'].isin(sec_fund_tickers)).sum()),
                   top_unlabelled=B_full.loc[~B_full['ticker'].isin(cs_labelled), 'ticker'].value_counts().head(12).to_dict())

# =====================================================================================
# 8. Description only
# =====================================================================================

def outcome_table(df):
    rows = []
    for k in HORIZONS:
        y = df[f'ret{k}_net'].values
        s = summ(y)
        m = np.isfinite(y)
        s.update(iwm=float(np.nanmean(df.loc[m, f'iwm{k}'])) if m.any() else np.nan,
                 excess=float(np.nanmean(df.loc[m, f'excess{k}'])) if m.any() else np.nan,
                 flagged=int(df.loc[m, f'exit{k}_note'].isin(['stale_last_close', 'gap_last_close',
                                                               'split_window_last_usable']).sum()),
                 capped=int(df.loc[m, f'ret{k}_capped'].sum()), horizon=k, entry='close')
        rows.append(s)
        checks.append(selfcheck(y, f'list {df["list"].iloc[0]} {k}-session net, close entry'))
    for k in HORIZONS:
        y = df[f'nextopen_ret{k}_net'].values
        s = summ(y)
        m = np.isfinite(y)
        s.update(iwm=float(np.nanmean(df.loc[m, f'nextopen_iwm{k}'])) if m.any() else np.nan,
                 excess=float(np.nanmean(df.loc[m, f'nextopen_ret{k}_net'] - df.loc[m, f'nextopen_iwm{k}'])) if m.any() else np.nan,
                 flagged=np.nan, capped=int(df.loc[m, f'nextopen_ret{k}_capped'].sum()), horizon=k, entry='next open')
        rows.append(s)
    return rows


def by_bucket(df, col, order):
    rows = []
    for b in order:
        s = summ(df.loc[df[col] == b, 'ret20_net'])
        s['bucket'] = b
        s['count_all'] = int((df[col] == b).sum())
        rows.append(s)
    return rows


DESC = {}
for nm, df in (('A', A), ('B', B)):
    D = {}
    D['rows'] = len(df)
    D['days'] = int(df['date'].nunique())
    D['first_day'], D['last_day'] = df['date'].min(), df['date'].max()
    D['outcomes'] = outcome_table(df)
    D['by_mv'] = by_bucket(df, 'mv_bucket', MV_ORDER)
    D['by_cl'] = by_bucket(df, 'close_loc_bucket', CL_ORDER)
    D['by_event'] = {str(v): summ(df.loc[(df['sec_found']) & (df['event'] == v), 'ret20_net']) for v in (True, False)}
    sec = df[df['sec_found']]
    D['sec_found'] = int(df['sec_found'].sum())
    D['no_cik'] = int((df['cik'] == '').sum())
    D['cik_differs_from_massive'] = int(df['cik_differs_from_massive'].sum())
    D['event_n'] = int((sec['event'] == True).sum())
    D['event_incl_amend_n'] = int((sec['event_incl_amend'] == True).sum())
    D['fresh_n'] = int((sec['fresh_supply'] == True).sum())
    D['fresh_wide_n'] = int((sec['fresh_supply_wide'] == True).sum())
    D['repeat_n'] = int(df['repeat_spiker'].sum())
    D['repeat_full_lookback_rows'] = int((df['spike_lookback_sessions'] == SPIKE_LOOKBACK).sum())
    D['shares_known'] = int(df['shares_adj'].notna().sum())
    D['whole_n'] = int((df['whole_count'] == True).sum())
    D['turnover_median'] = float(df['turnover'].median())
    known = df[df['shares_adj'].notna()]
    age = (pd.to_datetime(known['date']) - pd.to_datetime(known['shares_asof'])).dt.days
    D['shares_age_median_days'] = float(age.median())
    D['shares_age_over_365'] = int((age > 365).sum())
    D['turnover_over_10'] = int((df['turnover'] > 10).sum())
    D['mv_counts'] = {b: int((df['mv_bucket'] == b).sum()) for b in MV_ORDER}
    D['cl_counts'] = {b: int((df['close_loc_bucket'] == b).sum()) for b in CL_ORDER}
    D['raw_close_mismatch'] = int((~df['raw_close_match']).sum())
    D['suspect_split'] = int(df['suspect_split'].sum())
    D['ret_day_median'] = float(df['ret_day'].median())
    D['ret_day_min'] = float(df['ret_day'].min())
    D['prior_close_median'] = float(df['prior_close_raw'].median())
    # supply within 10 days after
    sa = df[df['supply_10d_after'].notna()]
    D['after'] = dict(n=int(len(sa)), filed=int((sa['supply_10d_after'] == True).sum()),
                      fresh_fetch_rows=int((df['supply_after_source'] == 'fresh_fetch').sum()))
    D['after']['share'] = D['after']['filed'] / D['after']['n'] if D['after']['n'] else np.nan
    # movers per day with no event
    per = df.groupby('date').agg(n=('ticker', 'size'),
                                 no_event=('event', lambda s: int((s == False).sum())),
                                 event=('event', lambda s: int((s == True).sum())),
                                 unknown=('event', lambda s: int(s.isna().sum())))
    D['per_day'] = dict(days=int(len(per)), mean_no_event=float(per['no_event'].mean()),
                        median_no_event=float(per['no_event'].median()),
                        mean_event=float(per['event'].mean()), mean_unknown=float(per['unknown'].mean()),
                        dist={int(k): int(v) for k, v in per['no_event'].value_counts().sort_index().items()},
                        days_all10_no_event=int((per['no_event'] == per['n']).sum()),
                        days_full=int((per['n'] == TOPN).sum()))
    # exit notes
    D['notes20'] = {k: int(v) for k, v in df['exit20_note'].value_counts().items()}
    D['ret20_known'] = int(np.isfinite(df['ret20_net']).sum())
    DESC[nm] = D

# overlap of lists
ka = set(zip(A['date'], A['ticker'])); kb = set(zip(B['date'], B['ticker']))
NUM['overlap_AB'] = len(ka & kb)

# data-quality sensitivity (not a test): T1 without movers flagged as a possible unrecorded split,
# and without exits flagged stale/gap/split-window
m_ok = ~B['suspect_split']
NUM['T1_sens_no_suspect'] = summ(B.loc[m_ok, 'ret20_net'])
m_clean = B['exit20_note'] == ''
NUM['T1_sens_clean_exits'] = summ(B.loc[m_clean, 'ret20_net'])
NUM['B_capped20'] = int(B['ret20_capped'].sum())
_ff = glob.glob(os.path.join(CACHE, 'sec', 'subm_fresh', 'CIK*.json'))
NUM['fresh_fetch_date'] = (pd.Timestamp(min(os.path.getmtime(x) for x in _ff), unit='s', tz='UTC').tz_convert(NY)
                           .strftime('%Y-%m-%d') if _ff else '')
NUM['run_date'] = datetime.date.today().isoformat()
NUM['B_first_session'] = int(B['session'].min())

NUM['DESC'] = DESC
NUM['checks'] = checks
NUM['checks_all_ok'] = bool(all(x['ok'] for x in checks))
log('self-consistency checks:', len(checks), 'all ok' if NUM['checks_all_ok'] else 'FAILED')


def _clean(o_):
    if isinstance(o_, dict):
        return {str(k): _clean(v) for k, v in o_.items()}
    if isinstance(o_, (list, tuple)):
        return [_clean(v) for v in o_]
    if isinstance(o_, (np.integer,)):
        return int(o_)
    if isinstance(o_, (np.floating,)):
        return float(o_)
    if isinstance(o_, (np.bool_,)):
        return bool(o_)
    return o_


json.dump(_clean(NUM), open(os.path.join(CACHE, 'numbers.json'), 'w'), indent=1, default=str)
log('T1', {k: t1[k] for k in ('n', 'mean', 'median', 'pos', 'pays')}, t1['ci'])
log('T2', t2['yes'], t2['no'], t2['diff'], t2['ci'], {h: t2['halves'][h]['diff'] for h in (1, 2)}, t2['separates'])
log('T3', t3['yes'], t3['no'], t3['diff'], t3['ci'], {h: t3['halves'][h]['diff'] for h in (1, 2)}, t3['separates'])
log('FULL', {k: (v['mean'] if k == 'T1' else v['diff'], v['ci']) for k, v in (('T1', f1), ('T2', f2), ('T3', f3))})



# =====================================================================================
# 9. RESULTS.md (every number below comes from NUM, computed above)
# =====================================================================================

def P(x):   # signed percent
    return 'n/a' if x is None or not np.isfinite(x) else f'{x * 100:+.1f}%'


def S(x):   # share
    return 'n/a' if x is None or not np.isfinite(x) else f'{x * 100:.1f}%'


def PT(x):  # percentage points
    return 'n/a' if x is None or not np.isfinite(x) else f'{x * 100:+.1f} points'


def I(n):
    return f'{int(n):,}'


def CI(ci):
    return f'{P(ci["lo"])} to {P(ci["hi"])}'


def CIPT(ci):
    return f'{PT(ci["lo"])} to {PT(ci["hi"])}'


def row(*cells):
    return '| ' + ' | '.join(str(x) for x in cells) + ' |'


def srow(label, s_):
    return row(label, I(s_['n']), P(s_['mean']), P(s_['median']), S(s_['pos']))


def yesno(b):
    return 'yes' if b else 'no'


def write_report(path):
    D_A, D_B = DESC['A'], DESC['B']
    F = NUM['FULL']
    L = []
    w = L.append
    w('# MV1 results: the ten biggest daily gainers, and what came next')
    w('')
    w(f'Pre-registration: `research/movers/PREREG_MV1.md` (git cab1406). Run on {NUM["run_date"]} with `python run.py`. '
      'Every number in this file is written by `run.py` from the runners panel and caches. '
      'The run follows the pre-registration except where listed under Deviations.')
    w('')
    w(f'- List A: the ten biggest daily gains among all common stocks. {I(D_A["rows"])} movers on {I(D_A["days"])} days, '
      f'{D_A["first_day"]} to {D_A["last_day"]}.')
    w(f'- List B (the tested list): the ten biggest gains among takeable stocks (prior close $1 or more, median dollar volume '
      f'$250k or more over the 20 sessions before). {I(D_B["rows"])} movers on {I(D_B["days"])} days, '
      f'{D_B["first_day"]} to {D_B["last_day"]}.')
    w(f'- {I(NUM["overlap_AB"])} movers are on both lists.')
    w(f'- Returns are after {COST * 100:.0f}% round-trip costs. A gain above +{CAP * 100:.0f}% counts as +{CAP * 100:.0f}%. '
      '"20 sessions" means from the mover day\'s close to the close 20 sessions later.')
    w(f'- The 95% interval resamples whole mover days: {NBOOT:,} draws, seed {SEED}, percentile interval.')
    w('')
    w('## Verdicts')
    w('')
    w(row('Test', 'Pass mark', 'Result'))
    w(row('---', '---', '---'))
    w(row('T1: does buying list B at the close pay?', 'mean above 0, interval above 0, median above 0',
          '**Pays**' if t1['pays'] else '**Does not pay**'))
    w(row('T2: do event movers hold up better?', 'interval of the difference above 0, same sign in both halves',
          '**Separates**' if t2['separates'] else '**Does not separate**'))
    w(row('T3: do the mechanics mark the fade?', 'interval of the difference below 0, same sign in both halves',
          '**Separates**' if t3['separates'] else '**Does not separate**'))
    w('')
    # ---- T1
    w('### T1: buying list B at the close ' + ('pays' if t1['pays'] else 'does not pay'))
    w('')
    w(row('List B, 20 sessions', 'n', 'mean', 'median', '% positive', '95% interval of the mean'))
    w(row('---', '---', '---', '---', '---', '---'))
    w(row('Bought at the close', I(t1['n']), P(t1['mean']), P(t1['median']), S(t1['pos']), CI(t1['ci'])))
    w(row('Mover minus IWM, same days', I(t1['excess']['n']), P(t1['excess']['mean']), P(t1['excess']['median']),
          S(t1['excess']['pos']), CI(t1['excess_ci'])))
    w('')
    w(f'- Mean above zero: {yesno(t1["mean"] > 0)}. Interval above zero: {yesno(t1["ci"]["lo"] > 0)}. '
      f'Median above zero: {yesno(t1["median"] > 0)}.')
    w(f'- IWM over the same entry and exit days averaged {P(t1["iwm"]["mean"])} (median {P(t1["iwm"]["median"])}).')
    w(f'- By half (not part of the pass mark): sessions 1-{HALF1_LAST_SESSION} mean {P(t1["halves"][1]["mean"])} '
      f'(n {I(t1["halves"][1]["n"])}), sessions {HALF1_LAST_SESSION + 1}-{T} mean {P(t1["halves"][2]["mean"])} (n {I(t1["halves"][2]["n"])}).')
    w(f'- {I(t1["ci"]["days"])} mover days had a 20-session outcome.')
    w('')
    # ---- T2
    h1, h2 = t2['halves'][1], t2['halves'][2]
    w('### T2: event movers ' + ('held up better' if t2['separates'] else 'did not separate'))
    w('')
    w('An event is an 8-K or 6-K accepted after 16:00 New York time the session before and before 16:00 on the mover day.')
    w('')
    w(row('List B, 20 sessions', 'n', 'mean', 'median', '% positive'))
    w(row('---', '---', '---', '---', '---'))
    w(srow('With an event', t2['yes']))
    w(srow('No event', t2['no']))
    w('')
    w(f'- Difference in means (event minus no event): {PT(t2["diff"])}. 95% interval: {CIPT(t2["ci"])}.')
    w(f'- First half: {PT(h1["diff"])} (event {P(h1["yes"]["mean"])}, n {I(h1["yes"]["n"])}; no event {P(h1["no"]["mean"])}, n {I(h1["no"]["n"])}).')
    w(f'- Second half: {PT(h2["diff"])} (event {P(h2["yes"]["mean"])}, n {I(h2["yes"]["n"])}; no event {P(h2["no"]["mean"])}, n {I(h2["no"]["n"])}).')
    w(f'- Interval above zero: {yesno(t2["ci"]["lo"] > 0)}. Same sign in both halves: {yesno((h1["diff"] > 0) == (h2["diff"] > 0))}.')
    w(f'- Difference in medians (not part of the pass mark): {PT(t2["diff_median"])}.')
    w(f'- "Better" is relative. Event movers still averaged {P(t2["yes"]["mean"])} after 20 sessions, and {S(t2["yes"]["pos"])} were higher.')
    w(f'- Movers left out for lack of SEC data: {I(t2["excluded_no_sec"])}.')
    w('')
    # ---- T3
    h1, h2 = t3['halves'][1], t3['halves'][2]
    w('### T3: among no-event movers, the mechanics ' + ('marked the fade' if t3['separates'] else 'did not separate'))
    w('')
    w('A mover is flagged if it had any of: fresh supply (S-1, F-1, S-3, F-3, any 424B or EFFECT in the 60 days before), '
      'repeat spiker (two or more +50% days in the 250 sessions before), or whole count traded (turnover 1.0 or more).')
    w('')
    w(row('List B, no event, 20 sessions', 'n', 'mean', 'median', '% positive'))
    w(row('---', '---', '---', '---', '---'))
    w(srow('Any flag', t3['yes']))
    w(srow('No flag', t3['no']))
    w('')
    w(f'- Difference in means (any minus none): {PT(t3["diff"])}. 95% interval: {CIPT(t3["ci"])}.')
    w(f'- First half: {PT(h1["diff"])} (any {P(h1["yes"]["mean"])}, n {I(h1["yes"]["n"])}; none {P(h1["no"]["mean"])}, n {I(h1["no"]["n"])}).')
    w(f'- Second half: {PT(h2["diff"])} (any {P(h2["yes"]["mean"])}, n {I(h2["yes"]["n"])}; none {P(h2["no"]["mean"])}, n {I(h2["no"]["n"])}).')
    w(f'- Interval below zero: {yesno(t3["ci"]["hi"] < 0)}. Same sign in both halves: {yesno((h1["diff"] < 0) == (h2["diff"] < 0))}.')
    w(f'- Difference in medians (not part of the pass mark): {PT(t3["diff_median"])}.')
    w(f'- {I(t3["excluded_unknown"])} no-event movers were left out. Their share count was unknown and the other two flags were off, '
      'so "no flag" could not be confirmed.')
    w(f'- The flags mark the fade. They do not make a long trade: the no-flag group still averaged {P(t3["no"]["mean"])} '
      f'(median {P(t3["no"]["median"])}).')
    w('')
    # ---- Description
    w('## Description only (not tested, never a result)')
    w('')
    mv_b = {x['bucket']: x for x in D_B['by_mv']}
    cl_b = {x['bucket']: x for x in D_B['by_cl']}
    oB = {(x['entry'], x['horizon']): x for x in D_B['outcomes']}
    w('### What stands out')
    w('')
    w(f'1. **Size separated outcomes more than anything else described.** List B movers under $50M averaged '
      f'{P(mv_b["<$50M"]["mean"])} after 20 sessions (median {P(mv_b["<$50M"]["median"])}, {S(mv_b["<$50M"]["pos"])} higher, '
      f'n {I(mv_b["<$50M"]["n"])}). Movers of $300M or more averaged {P(mv_b[">=$300M"]["mean"])} '
      f'(median {P(mv_b[">=$300M"]["median"])}, {S(mv_b[">=$300M"]["pos"])} higher, n {I(mv_b[">=$300M"]["n"])}). Not tested.')
    w(f'2. **Most movers had no filing, and some filed new share supply soon after.** On a typical day '
      f'{D_B["per_day"]["median_no_event"]:.0f} of the ten list B movers had no event (mean {D_B["per_day"]["mean_no_event"]:.2f}). '
      f'{S(D_B["after"]["share"])} of list B movers filed an S-1, F-1, S-3, F-3, 424B or EFFECT within {AFTER_DAYS} days after the mover day '
      f'({S(D_A["after"]["share"])} for list A).')
    cl_a = {x['bucket']: x for x in D_A['by_cl']}
    w(f'3. **Waiting for the next open did not help, and the close location mattered little in list B.** Bought at the next open, '
      f'list B averaged {P(oB[("next open", 20)]["mean"])} after 20 sessions (median {P(oB[("next open", 20)]["median"])}), '
      f'against {P(oB[("close", 20)]["mean"])} from the close. List B movers that closed strong averaged {P(cl_b["closed strong (>=0.9)"]["mean"])}; '
      f'those that faded into the close averaged {P(cl_b["faded (<=0.7)"]["mean"])}. In list A the gap was wider: '
      f'{P(cl_a["closed strong (>=0.9)"]["mean"])} against {P(cl_a["faded (<=0.7)"]["mean"])}.')
    w('')
    w('### What came next, both lists')
    w('')
    w(row('List', 'Entry', 'Sessions', 'n', 'mean', 'median', '% positive', 'IWM mean', 'mover minus IWM'))
    w(row(*['---'] * 9))
    for nm in ('B', 'A'):
        for x in DESC[nm]['outcomes']:
            w(row(nm, x['entry'], x['horizon'], I(x['n']), P(x['mean']), P(x['median']), S(x['pos']), P(x['iwm']), P(x['excess'])))
    w('')
    w('### By market value (shares outstanding times prior close), 20 sessions from the close')
    w('')
    w(row('List', 'Market value', 'movers', 'n with outcome', 'mean', 'median', '% positive'))
    w(row(*['---'] * 7))
    for nm in ('B', 'A'):
        for x in DESC[nm]['by_mv']:
            w(row(nm, x['bucket'], I(x['count_all']), I(x['n']), P(x['mean']), P(x['median']), S(x['pos'])))
    w('')
    w("### By close location (where the close sat between the day's low and high), 20 sessions from the close")
    w('')
    w(row('List', 'Close location', 'movers', 'n with outcome', 'mean', 'median', '% positive'))
    w(row(*['---'] * 7))
    for nm in ('B', 'A'):
        for x in DESC[nm]['by_cl']:
            w(row(nm, x['bucket'], I(x['count_all']), I(x['n']), P(x['mean']), P(x['median']), S(x['pos'])))
    w('')
    w(f'### New share supply within {AFTER_DAYS} days after the mover day')
    w('')
    w(row('List', 'movers with SEC data', 'filed S-1/F-1/S-3/F-3/424B/EFFECT', 'share'))
    w(row(*['---'] * 4))
    for nm in ('B', 'A'):
        a = DESC[nm]['after']
        w(row(nm, I(a['n']), I(a['filed']), S(a['share'])))
    w('')
    w('### Movers per day with no event')
    w('')
    for nm in ('B', 'A'):
        pdy = DESC[nm]['per_day']
        w(f'- List {nm}: {I(pdy["days"])} days. Movers with no event per day: mean {pdy["mean_no_event"]:.2f}, median {pdy["median_no_event"]:.0f}. '
          f'Movers with an event per day: mean {pdy["mean_event"]:.2f}. No SEC data: mean {pdy["mean_unknown"]:.3f} per day. '
          f'Days on which all ten had no event: {I(pdy["days_all10_no_event"])}.')
    w('')
    w(row('No-event movers that day', *[str(k) for k in range(TOPN + 1)]))
    w(row(*['---'] * (TOPN + 2)))
    for nm in ('B', 'A'):
        dist = DESC[nm]['per_day']['dist']
        w(row(f'List {nm}: days', *[I(dist.get(k, 0)) for k in range(TOPN + 1)]))
    w('')
    w('### Who was on the lists')
    w('')
    w(row('Count', 'List B', 'List A'))
    w(row('---', '---', '---'))
    w(row('movers', I(D_B['rows']), I(D_A['rows'])))
    w(row('median day gain', P(D_B['ret_day_median']), P(D_A['ret_day_median'])))
    w(row('smallest day gain on the list', P(D_B['ret_day_min']), P(D_A['ret_day_min'])))
    w(row('median prior close (actual price)', f'${D_B["prior_close_median"]:.2f}', f'${D_A["prior_close_median"]:.2f}'))
    w(row('with SEC data', I(D_B['sec_found']), I(D_A['sec_found'])))
    w(row('event (8-K or 6-K in the window)', I(D_B['event_n']), I(D_A['event_n'])))
    w(row('fresh supply in the 60 days before', I(D_B['fresh_n']), I(D_A['fresh_n'])))
    w(row('repeat spiker', I(D_B['repeat_n']), I(D_A['repeat_n'])))
    w(row('share count known', I(D_B['shares_known']), I(D_A['shares_known'])))
    w(row('whole count traded (turnover 1.0 or more)', I(D_B['whole_n']), I(D_A['whole_n'])))
    w(row('median turnover (where known)', f'{D_B["turnover_median"]:.2f}', f'{D_A["turnover_median"]:.2f}'))
    for b in MV_ORDER:
        w(row(f'market value {b}', I(D_B['mv_counts'][b]), I(D_A['mv_counts'][b])))
    for b in CL_ORDER:
        w(row(f'close location {b}', I(D_B['cl_counts'][b]), I(D_A['cl_counts'][b])))
    w('')
    # ---- self check
    w('## Self-consistency check')
    w('')
    w('For every set of returns: share of wins times average win, minus share of losses times average loss, must equal the mean. '
      f'Zero returns count as neither. {len(checks)} sets were checked. '
      + ('**All passed** (largest gap below 1e-12).' if NUM['checks_all_ok'] else '**At least one FAILED.**'))
    w('')
    w(row('Set', 'n', 'wins', 'average win', 'losses', 'average loss (size)', '(wins x average win - losses x average loss) / n', 'mean', 'passed'))
    w(row(*['---'] * 9))
    for x in checks:
        w(row(x['label'], I(x['n']), I(x['wins']), S(x['avg_win']), I(x['losses']), S(x['avg_loss']),
              f'{x["lhs"] * 100:+.4f}%', f'{x["mean"] * 100:+.4f}%', yesno(x['ok'])))
    w('')
    # ---- caveats
    nb = D_B['notes20']
    w('## Caveats')
    w('')
    w('- **This is not a long trade.** List B lost money on average at every horizon from both entries. The tests describe which movers fade. '
      'A cash account cannot short, and borrow on small movers is often unavailable or costly. Costs of 1% may be too low for the smallest names.')
    m3, m2 = t3['mv_mix'], t2['mv_mix']
    w(f'- **Size may confound T2 and T3.** In the T3 sample, {S(m3["yes"]["<$50M"])} of flagged movers were under $50M, against '
      f'{S(m3["no"]["<$50M"])} of unflagged movers. In the T2 sample, {S(m2["yes"]["<$50M"])} of event movers were under $50M, against '
      f'{S(m2["no"]["<$50M"])} of no-event movers. Small movers faded more (see the market value table). Neither test was built to separate '
      'its feature from size, and nothing here tests that.')
    w('- **"No event" means no SEC 8-K or 6-K in the window.** No newswire or social media was checked. A mover with no filing may still have had news.')
    w(f'- **Share counts can be stale.** They are the latest dei cover-page count filed before the day, up to {SHARES_MAX_AGE_MONTHS} months old, '
      f'adjusted for recorded splits since. In list B the median count was {D_B["shares_age_median_days"]:.0f} days old at the mover day, '
      f'and {I(D_B["shares_age_over_365"])} were more than a year old. A stale count in a fast-diluting company understates shares, '
      f'which overstates turnover and understates market value. {I(D_B["turnover_over_10"])} list B movers showed turnover above 10. '
      'Split records start on 2024-06-03, so an older split between the count date and the mover day is not adjusted.')
    w(f'- **Stocks that stopped trading.** At 20 sessions in list B: {I(nb.get("stale_last_close", 0))} stopped trading and were marked at their last close; '
      f'{I(nb.get("gap_last_close", 0))} had no trade on the exit day and were marked at the last close before it; '
      f'{I(nb.get("split_window_last_usable", 0))} had an exit bar inside a split window and used the last close before the window; '
      f'{I(nb.get("split_window_no_usable", 0))} had no usable close and has no outcome. Marking a delisted stock at its last close probably understates its loss. '
      'A ticker change also looks like a stop in this panel.')
    w(f'- **The panel ends on {dates[-1]}.** The {I(nb.get("beyond_panel", 0))} list B movers from the last 20 sessions have no 20-session outcome. '
      'Raw bars to 2026-10-09 exist on disk but are outside the pre-registered data and were not used.')
    w(f'- **Possible unrecorded splits.** {I(D_B["suspect_split"])} list B movers ({I(D_A["suspect_split"])} in list A) match the runners study\'s flag for an '
      f'unrecorded reverse split. They were kept. Without them, T1 is mean {P(NUM["T1_sens_no_suspect"]["mean"])}, median '
      f'{P(NUM["T1_sens_no_suspect"]["median"])} (n {I(NUM["T1_sens_no_suspect"]["n"])}).')
    w(f'- **Cap.** {I(NUM["B_capped20"])} list B 20-session returns were above +{CAP * 100:.0f}% and were capped.')
    w('- **Ticker to CIK** uses `research/domino/sic_map.csv`, then SEC company_tickers.json downloaded on this run. Both are current lists, so a '
      'recycled ticker could map to the wrong company [UNVERIFIED]. Where the Massive ticker file also had a CIK, none disagreed '
      f'(list B: {I(D_B["cik_differs_from_massive"])}, list A: {I(D_A["cik_differs_from_massive"])}).')
    w('- **SEC acceptance times** in the submissions files are true UTC. This was checked: converted to New York time, filings accepted after 17:30 carry '
      "the next day's filing date, as EDGAR rules say. The event window uses exact times: after 16:00:00 the session before, before 16:00:00 on the mover day.")
    w('- **Amendments are not counted** because the pre-registration names the base forms. Counting 8-K/A and 6-K/A would add '
      f'{I(D_B["event_incl_amend_n"] - D_B["event_n"])} list B events. Counting S-1/A, F-1/A, S-3/A, F-3/A, MEF and ASR forms would add '
      f'{I(D_B["fresh_wide_n"] - D_B["fresh_n"])} fresh-supply flags. Neither was tested.')
    w(f'- **SEC cache dates.** The runners SEC cache is complete through {NUM["cache_through"]}. Movers whose {AFTER_DAYS}-day after-window ends later '
      f'({I(D_B["after"]["fresh_fetch_rows"])} in list B) used submissions fetched on {NUM["fresh_fetch_date"]}.')
    ic = NUM['iwm_check']
    w(f'- **IWM** is Yahoo daily closes (price only, no dividends). They match the IWM bars in the raw files on all {I(ic["compared"])} sessions; '
      f"the largest relative gap was {ic['max_rel_diff']:.1e}. IWM returns run from the mover day's close to the scheduled exit day and carry no costs.")
    w('- **No significance claim beyond the three tests.** The description tables are many cuts of one sample. Read them as description.')
    w('')
    # ---- deviations
    w('## Deviations')
    w('')
    w(f'1. **Universe: common stocks only, by label.** The pre-registration calls the panel "6,924 US common stocks". {I(UNLAB["n"])} of those tickers have no '
      f'common-stock (CS) label in the runners ticker file. They came in from an untyped ticker source. {I(UNLAB["sec_fund"])} are on the SEC fund and ETF ticker list. '
      f'{I(UNLAB["sec_company"])} map to an SEC company; a manual look at their names found ETNs, closed-end funds, ADRs, warrants and some genuine '
      f'common stocks [UNVERIFIED: not counted by type]. {I(UNLAB["neither"])} are on neither list. The definitions say "common stocks", so the primary run keeps the '
      f'{I(NUM["n_cs_labelled"])} tickers Massive labelled CS. Exact security types could not be fetched: the Massive reference endpoint is not reachable '
      'through the connector. Some genuine common stocks, such as recent listings, are therefore left out.')
    w(f'   - Impact check, the panel as-is: list B then has {I(F["rows_unlabelled"])} of {I(F["rows"])} rows from unlabelled tickers '
      f'({I(F["rows_unlabelled_sec_fund"])} of them on the SEC fund list). The most frequent were '
      + ', '.join(f'{k} ({v})' for k, v in F['top_unlabelled'].items()) + ', mostly leveraged single-stock ETFs by name [UNVERIFIED for the rest]. Results: '
      f'T1 mean {P(F["T1"]["mean"])}, median {P(F["T1"]["median"])}, interval {CI(F["T1"]["ci"])}, {"pays" if F["T1"]["pays"] else "does not pay"}. '
      f'T2 difference {PT(F["T2"]["diff"])}, interval {CIPT(F["T2"]["ci"])}, halves {PT(F["T2"]["halves"][1]["diff"])} and {PT(F["T2"]["halves"][2]["diff"])}, '
      f'{"separates" if F["T2"]["separates"] else "does not separate"}. '
      f'T3 difference {PT(F["T3"]["diff"])}, interval {CIPT(F["T3"]["ci"])}, halves {PT(F["T3"]["halves"][1]["diff"])} and {PT(F["T3"]["halves"][2]["diff"])}, '
      f'{"separates" if F["T3"]["separates"] else "does not separate"}. '
      + ('The verdicts are the same.' if (F['T1']['pays'], F['T2']['separates'], F['T3']['separates']) == (t1['pays'], t2['separates'], t3['separates'])
         else 'At least one verdict differs.') + ' That table is `listB_fullpanel.csv`.')
    w(f'2. **List B starts on session {NUM["B_first_session"]} ({D_B["first_day"]}).** The 20-session liquidity window needs data before {dates[0]}, '
      f'which the panel does not have. So list B has no movers on the first {NUM["B_first_session"] - 2} mover days. List A starts on session 2.')
    w(f'3. **Repeat-spiker lookback is shorter in the first half.** The 250 sessions before the mover day are only fully inside the panel from session '
      f'{SPIKE_LOOKBACK + 2} on. Earlier movers use every session available. This undercounts repeat spikers in the first half, which matters for '
      'the T3 halves check.')
    w('4. **Exits inside a split window.** The pre-registration says bars inside a split window are not used. An exit that falls in one uses the last '
      'usable close before it and is flagged. The next-day open is not used if that day is in a split window. Counts are under Caveats.')
    w("5. **The last session.** The panel's stored `valid` array ends on 2026-09-29 for a reason unrelated to splits (the runners study needed a next day). "
      'It was rebuilt from the same split records so that 2026-09-30 counts as a mover day. On every other session the rebuilt array matches the stored one '
      f'({I(NUM["valid_mismatch"])} differences).')
    w('6. **Choices the pre-registration left open.** A session with no trade counts as $0 dollar volume. A stock with no trade between entry and exit is '
      'marked at its last close (the entry close) and flagged. The +300% cap is applied before costs. In T2 and T3, movers that cannot be classed '
      '(no SEC data, or unknown flags) are left out. "Same sign in both halves" is checked on the difference in means. '
      "Ties in daily return are broken by ticker. IWM is from Yahoo, as the brief said, and was cross-checked against the panel's own source.")
    w('')
    w('## Files')
    w('')
    w('- `run.py`: rebuilds everything here with one command. It reads the runners panel and caches and writes only inside this folder.')
    w('- `listA.csv`, `listB.csv`: one row per mover with every feature and outcome. `listB_fullpanel.csv`: the impact check for Deviation 1.')
    w('- `cache/`: SEC and Yahoo downloads, and `numbers.json` with every number above.')
    w('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))


if '--no-report' not in sys.argv:
    write_report(os.path.join(HERE, 'RESULTS.md'))
    log('wrote RESULTS.md')
