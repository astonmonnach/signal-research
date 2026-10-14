"""IC1: does following insider cluster buying pay?

Runs the study pre-registered in ../PREREG_IC1.md (committed in git a90d629) and rebuilds
every number in RESULTS.md, signals.csv, controls.csv and singles.csv with one command:

    python run.py

Downloads (cached in data/, git-ignored): the six SEC Insider Transactions Data Sets zips
2024q4..2026q1, and IWM daily bars from Yahoo (context only, never used in a test).
The zips are read in place with zipfile; nothing is extracted.
"""
import os, re, csv, json, time, zipfile, urllib.request, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DATA = os.path.join(HERE, 'data')
WORK = os.path.join(ROOT, 'research', 'runners', 'work')
PANEL = os.path.join(WORK, 'panel.npz')
SHARES = os.path.join(WORK, 'sec', 'shares')
REF = os.path.join(WORK, 'ref')
SICMAP = os.path.join(ROOT, 'research', 'domino', 'sic_map.csv')
UA = 'PersonalResearch research@example.com'
QUARTERS = ['2024q4', '2025q1', '2025q2', '2025q3', '2025q4', '2026q1']
ZIP_URL = 'https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{q}_form345.zip'

# ---- pre-registered constants (PREREG_IC1.md; do not change) ----
FILING_START, FILING_END = '2024-10-01', '2026-03-31'
WINDOW_DAYS = 30            # 2+ different reporting owners within 30 calendar days
DEDUP_SESSIONS = 60         # one signal per issuer per 60 sessions
MIN_PRICE = 1.0             # takeable: prior close >= $1
MIN_DV = 250_000            # takeable: median $ volume over 20 sessions before entry >= $250k
DV_LOOKBACK = 20
HORIZONS = (20, 60)
CAP = 3.0                   # returns above +300% count as +300%
COST = 0.01                 # 1% per round trip
N_CTRL = 10
CTRL_LO, CTRL_HI = 0.5, 2.0
CTRL_NOBUY_DAYS = 90
MV_CUT = 300e6
SIZE_CUT = 250_000
SHARES_MAX_AGE_MONTHS = 15
BOOT_N, BOOT_SEED = 2000, 20261014
HALF1 = ('2024-10-01', '2025-06-30')
HALF2 = ('2025-07-01', '2026-03-31')

ROLE_RE = re.compile(r'Director|Officer|TenPercentOwner')
# a footnote that says the purchase was made under a 10b5-1 plan ("non-Rule 10b5-1" does not match)
FN_10B51 = re.compile(r'(?<!non-)(pursuant to|under)\s+(a\s+|an\s+)?(rule\s+)?10b5-?1', re.I)
NON_COMMON_RE = re.compile(r'prefer|\bnotes?\b|debenture|\bbonds?\b|warrant', re.I)
CEO_CFO_RE = re.compile(r'\bCEO\b|CHIEF EXECUTIVE|\bCFO\b|CHIEF FINANCIAL|PRINCIPAL EXECUTIVE|PRINCIPAL FINANCIAL', re.I)


# ------------------------------------------------------------------ downloads
def download(url, path, headers):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return True
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            with open(path, 'wb') as f:
                f.write(data)
            time.sleep(0.25)  # well under 10 requests a second
            return True
        except Exception as e:
            print('download retry', url, type(e).__name__)
            time.sleep(2 * (attempt + 1))
    return False


def fetch_all():
    os.makedirs(DATA, exist_ok=True)
    for q in QUARTERS:
        ok = download(ZIP_URL.format(q=q), os.path.join(DATA, f'{q}_form345.zip'), {'User-Agent': UA})
        assert ok, f'could not download {q}'
    p1 = int(dt.datetime(2024, 9, 1, tzinfo=dt.timezone.utc).timestamp())
    p2 = int(dt.datetime(2026, 10, 2, tzinfo=dt.timezone.utc).timestamp())
    iwm_url = f'https://query1.finance.yahoo.com/v8/finance/chart/IWM?period1={p1}&period2={p2}&interval=1d'
    download(iwm_url, os.path.join(DATA, 'iwm_daily.json'),
             {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'})


# ------------------------------------------------------------------ SEC tables
def read_table(q, name):
    with zipfile.ZipFile(os.path.join(DATA, f'{q}_form345.zip')) as z:
        with z.open(name + '.tsv') as f:
            return pd.read_csv(f, sep='\t', dtype=str, keep_default_na=False, quoting=csv.QUOTE_NONE)


def load_sec():
    sub = pd.concat([read_table(q, 'SUBMISSION') for q in QUARTERS], ignore_index=True)
    own = pd.concat([read_table(q, 'REPORTINGOWNER') for q in QUARTERS], ignore_index=True)
    ndt = pd.concat([read_table(q, 'NONDERIV_TRANS') for q in QUARTERS], ignore_index=True)
    fn = pd.concat([read_table(q, 'FOOTNOTES') for q in QUARTERS], ignore_index=True)
    for name, d in (('SUBMISSION', sub), ('REPORTINGOWNER', own), ('NONDERIV_TRANS', ndt), ('FOOTNOTES', fn)):
        bad = (~d['ACCESSION_NUMBER'].str.match(r'^\d{10}-\d{2}-\d{6}$')).sum()
        assert bad == 0, f'{name}: {bad} malformed rows'
    assert not sub['ACCESSION_NUMBER'].duplicated().any()
    sub['filing_date'] = pd.to_datetime(sub['FILING_DATE'], format='%d-%b-%Y')
    return sub, own, ndt, fn


def build_buys(sub, own, ndt, fn, F):
    """Insider buys as defined in the pre-registration. Returns (rows, owners) and fills funnel F."""
    p = ndt[(ndt['TRANS_CODE'] == 'P') & (ndt['TRANS_ACQUIRED_DISP_CD'] == 'A')].copy()
    F['p_acquired_rows_all_forms'] = len(p)
    p = p.merge(sub[['ACCESSION_NUMBER', 'DOCUMENT_TYPE', 'AFF10B5ONE', 'filing_date', 'ISSUERCIK',
                     'ISSUERNAME', 'ISSUERTRADINGSYMBOL']], on='ACCESSION_NUMBER', how='left')
    F['p_rows_form4_amend'] = int((p['DOCUMENT_TYPE'] == '4/A').sum())
    F['p_rows_form5'] = int(p['DOCUMENT_TYPE'].isin(['5', '5/A']).sum())
    p = p[p['DOCUMENT_TYPE'] == '4'].copy()
    F['p_rows_form4'] = len(p)
    p = p[(p['filing_date'] >= FILING_START) & (p['filing_date'] <= FILING_END)]
    # qualifying reporting owners: director, officer or 10% owner
    o = own[own['ACCESSION_NUMBER'].isin(set(p['ACCESSION_NUMBER']))].copy()
    o['qual'] = o['RPTOWNER_RELATIONSHIP'].str.contains(ROLE_RE)
    o = o[o['qual']].copy()
    o['is_dir'] = o['RPTOWNER_RELATIONSHIP'].str.contains('Director')
    o['is_off'] = o['RPTOWNER_RELATIONSHIP'].str.contains('Officer')
    o['is_ten'] = o['RPTOWNER_RELATIONSHIP'].str.contains('TenPercentOwner')
    o['is_ceo_cfo'] = o['is_off'] & o['RPTOWNER_TITLE'].fillna('').str.contains(CEO_CFO_RE)
    o['RPTOWNERCIK'] = o['RPTOWNERCIK'].str.zfill(10)
    o = o.drop_duplicates(['ACCESSION_NUMBER', 'RPTOWNERCIK'])
    n0 = len(p)
    p = p[p['ACCESSION_NUMBER'].isin(set(o['ACCESSION_NUMBER']))].copy()
    F['p_rows_no_qualifying_owner'] = n0 - len(p)
    # 10b5-1: the filing-level flag, plus a footnote on the row that says the purchase was under a plan
    p['flag_10b51'] = p['AFF10B5ONE'].str.strip().str.lower().isin(['1', 'true'])
    fnd = dict(zip(zip(fn['ACCESSION_NUMBER'], fn['FOOTNOTE_ID']), fn['FOOTNOTE_TXT']))
    fncols = [c for c in p.columns if c.endswith('_FN')]
    def fn_hit(r):
        ids = {i for c in fncols for i in str(r[c]).replace(' ', '').split(',') if i}
        return any(FN_10B51.search(fnd.get((r['ACCESSION_NUMBER'], i), '')) for i in ids)
    p['fn_10b51'] = p.apply(fn_hit, axis=1) if len(p) else False
    F['p_rows_10b51_flag'] = int(p['flag_10b51'].sum())
    F['p_rows_10b51_footnote_only'] = int((p['fn_10b51'] & ~p['flag_10b51']).sum())
    p = p[~(p['flag_10b51'] | p['fn_10b51'])].copy()
    p['tdate'] = pd.to_datetime(p['TRANS_DATE'], format='%d-%b-%Y', errors='coerce')
    F['p_rows_bad_trans_date'] = int(p['tdate'].isna().sum())
    p = p[p['tdate'].notna()].copy()
    # a transaction date after the filing date is impossible; cap it at the filing date
    F['p_rows_trans_after_filing'] = int((p['tdate'] > p['filing_date']).sum())
    p.loc[p['tdate'] > p['filing_date'], 'tdate'] = p['filing_date']
    p['shares'] = pd.to_numeric(p['TRANS_SHARES'], errors='coerce')
    p['price'] = pd.to_numeric(p['TRANS_PRICEPERSHARE'], errors='coerce')
    p['value'] = p['shares'] * p['price']
    F['p_rows_no_value'] = int(p['value'].isna().sum())
    p['value'] = p['value'].fillna(0.0)
    p['issuer_cik'] = p['ISSUERCIK'].str.zfill(10)
    p['row_id'] = p['ACCESSION_NUMBER'] + ':' + p['NONDERIV_TRANS_SK']
    o = o[o['ACCESSION_NUMBER'].isin(set(p['ACCESSION_NUMBER']))]
    F['insider_buy_rows'] = len(p)
    F['insider_buy_filings'] = p['ACCESSION_NUMBER'].nunique()
    F['insider_buy_issuers'] = p['issuer_cik'].nunique()
    F['joint_filings'] = int((o.groupby('ACCESSION_NUMBER').size() > 1).sum())
    return p, o


# ------------------------------------------------------------------ panel + mapping
class Panel:
    def __init__(self):
        z = np.load(PANEL)
        self.o, self.c, self.craw, self.vraw = z['o'], z['c'], z['craw'], z['vraw']
        self.tick = [str(t) for t in z['tick']]
        self.dates = [str(d) for d in z['dates']]
        self.T, self.N = self.c.shape
        self.jx = {t: i for i, t in enumerate(self.tick)}
        self.dts = np.array(self.dates, dtype='datetime64[D]')
        dv = np.nan_to_num(self.craw * self.vraw, nan=0.0)
        med = np.full((self.T, self.N), np.nan)
        for e in range(1, self.T):
            med[e] = np.median(dv[max(0, e - DV_LOOKBACK):e], axis=0)
        self.med_dv = med          # median $ volume over the 20 sessions before session e
        pc = np.full((self.T, self.N), np.nan)
        pc[1:] = self.craw[:-1]
        self.prior_close = pc      # raw close of the session before e
        self.takeable = (pc >= MIN_PRICE) & (med >= MIN_DV) & ~np.isnan(self.o)

    def entry_session(self, date):
        """first session strictly after the signal date"""
        return int(np.searchsorted(self.dts, np.datetime64(pd.Timestamp(date).date()), side='right'))

    def ret(self, j, e, k, entry='open'):
        p0 = self.o[e, j] if entry == 'open' else self.c[e, j]
        if np.isnan(p0):
            return np.nan, 'no_entry_price'
        te = e + k
        if te >= self.T:
            return np.nan, 'beyond_data'
        if not np.isnan(self.c[te, j]):
            return min(self.c[te, j] / p0 - 1, CAP), ''
        seg = self.c[e:te + 1, j]
        ok = ~np.isnan(seg)
        if not ok.any():
            return np.nan, 'no_close'
        flag = 'stopped' if np.isnan(self.c[te:, j]).all() else 'gap'
        return min(seg[ok][-1] / p0 - 1, CAP), flag


def norm_sym(s):
    s = (s or '').upper().strip()
    if ':' in s:
        s = s.split(':')[-1].strip()
    s = re.split(r'[,;\s]+', s)[0] if s else ''
    return s.replace('-', '.').replace('/', '.')


class Mapper:
    def __init__(self, P):
        self.P = P
        sm = pd.read_csv(SICMAP, dtype=str, keep_default_na=False)
        sm['cik'] = sm['cik'].str.zfill(10)
        self.cik_of = dict(zip(sm['ticker'], sm['cik']))
        self.tickers_of = {}
        for t, k in zip(sm['ticker'], sm['cik']):
            if t in P.jx:
                self.tickers_of.setdefault(k, []).append(t)

    def price_ok(self, j, prices):
        """median of (insider purchase price / panel raw close on the purchase date) within 0.5x..2x"""
        prices = prices() if callable(prices) else prices
        if prices is None or len(prices) == 0:
            return False
        rs = []
        for td, px in prices:
            e = int(np.searchsorted(self.P.dts, np.datetime64(td.date()), side='right')) - 1
            if e < 0:
                continue
            seg = self.P.craw[max(0, e - 4):e + 1, j]
            seg = seg[~np.isnan(seg)]
            if len(seg) and seg[-1] > 0:
                rs.append(px / seg[-1])
        return bool(rs) and 0.5 <= float(np.median(rs)) <= 2.0

    def map(self, symbol, cik, e, prices=None):
        """returns (panel column or -1, method, cik_conflict).
        A symbol match whose ticker sic_map.csv lists under a different CIK is kept only if the issuer's
        insider purchase prices agree with the panel price (0.5x..2x); otherwise CIK fallback."""
        s = norm_sym(symbol)
        conflict = False
        if s in self.P.jx:
            k2 = self.cik_of.get(s)
            conflict = bool(k2 and k2 != cik)
            if not conflict or self.price_ok(self.P.jx[s], prices):
                return self.P.jx[s], 'symbol', conflict
        cands = self.tickers_of.get(cik, [])
        if cands:
            cands = sorted(cands)
            if e is not None and e < self.P.T:
                live = [t for t in cands if not np.isnan(self.P.o[e, self.P.jx[t]])]
                if live:
                    cands = live
            return self.P.jx[cands[0]], 'cik', conflict
        return -1, ('symbol_rejected' if conflict else 'unmapped'), conflict


# ------------------------------------------------------------------ splits / market value
def load_splits():
    spl = pd.concat([pd.read_csv(os.path.join(REF, 'reverse_splits.csv'), keep_default_na=False),
                     pd.read_csv(os.path.join(REF, 'other_splits.csv'), keep_default_na=False)], ignore_index=True)
    return {k: g for k, g in spl.groupby('ticker')}


_shares_cache = {}
def shares_table(cik):
    if cik not in _shares_cache:
        path = os.path.join(SHARES, f'CIK{cik}.json')
        df = None
        if os.path.exists(path):
            try:
                j = json.load(open(path))
                vals = [v for arr in j.get('units', {}).values() for v in arr]
                if vals:
                    df = pd.DataFrame(vals)
            except Exception:
                df = None
        _shares_cache[cik] = df
    return _shares_cache[cik]


def market_value(cik, ticker, entry_date, prior_date, prior_close, splits):
    """shares outstanding (latest filed before entry, split-adjusted, within 15 months) x prior close"""
    sh = shares_table(cik)
    if sh is None or 'filed' not in sh:
        return np.nan, np.nan, '', 'no_share_data'
    s2 = sh[sh['filed'] < entry_date].sort_values(['filed', 'end'])
    if s2.empty:
        return np.nan, np.nan, '', 'none_filed_before_entry'
    r = s2.iloc[-1]
    oldest = (pd.Timestamp(entry_date) - pd.DateOffset(months=SHARES_MAX_AGE_MONTHS)).strftime('%Y-%m-%d')
    if r['end'] < oldest:
        return np.nan, float(r['val']), r['end'], 'stale_over_15_months'
    s = float(r['val'])
    g = splits.get(ticker)
    if g is not None:
        g = g[(g['execution_date'] > r['end']) & (g['execution_date'] <= prior_date)]
        for _, x in g.iterrows():
            s = s * float(x['split_to']) / float(x['split_from'])
    return s * prior_close, s, r['end'], 'ok'


# ------------------------------------------------------------------ clusters
def find_signals(p, o, P, F):
    """Candidate triggers: a Form 4 whose buy by owner X falls within 30 calendar days of a buy by a
    different owner Y that is already public (filed on or before this filing). Then one signal per
    issuer per 60 sessions (entry session), first one kept."""
    owners_by_acc = o.groupby('ACCESSION_NUMBER')['RPTOWNERCIK'].apply(lambda s: sorted(set(s))).to_dict()
    info = o.set_index(['ACCESSION_NUMBER', 'RPTOWNERCIK'])
    fil = (p.groupby('ACCESSION_NUMBER')
             .agg(filing_date=('filing_date', 'first'), issuer_cik=('issuer_cik', 'first'),
                  issuer_name=('ISSUERNAME', 'first'), symbol=('ISSUERTRADINGSYMBOL', 'first'),
                  tdates=('tdate', lambda s: sorted(set(s))))
             .reset_index().sort_values(['issuer_cik', 'filing_date', 'ACCESSION_NUMBER']))
    rows_by_acc = {a: g for a, g in p.groupby('ACCESSION_NUMBER')}
    win = pd.Timedelta(days=WINDOW_DAYS)
    signals, n_cand = [], 0
    for cik, g in fil.groupby('issuer_cik', sort=False):
        g = g.reset_index(drop=True)
        known = []       # (owner, tdate, acc, filing_date)
        last_e = -10 ** 9
        for _, f in g.iterrows():
            acc = f['ACCESSION_NUMBER']
            owners = owners_by_acc.get(acc, [])
            for ow in owners:
                for td in f['tdates']:
                    known.append((ow, td, acc, f['filing_date']))
            # pairing: a buy by X in this filing within 30 days of a public buy by a different owner
            hit_dates = [tx for tx in f['tdates']
                         if any(y != x and abs(tx - ty) <= win for x in owners for (y, ty, _, _) in known)]
            if not hit_dates:
                continue
            n_cand += 1
            S = f['filing_date']
            e = P.entry_session(S)
            if e - last_e < DEDUP_SESSIONS:
                continue
            last_e = e
            tx = max(hit_dates)
            # cluster: buys public by the end of the signal date within 30 days of the trigger buy
            later_same_day = g[(g['filing_date'] == S)]['ACCESSION_NUMBER'].tolist()
            accs = {a for (_, _, a, fd) in known} | set(later_same_day)
            cl_rows = pd.concat([rows_by_acc[a] for a in accs])
            cl_rows = cl_rows[(cl_rows['tdate'] >= tx - win) & (cl_rows['tdate'] <= tx + win)]
            cl_accs = sorted(set(cl_rows['ACCESSION_NUMBER']))
            buyers = sorted({ow for a in cl_accs for ow in owners_by_acc.get(a, [])})
            # independent buyer groups: owners that ever file together are one group
            parent = {b: b for b in buyers}
            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]; x = parent[x]
                return x
            for a in cl_accs:
                ows = owners_by_acc.get(a, [])
                for ow in ows[1:]:
                    parent[find(ow)] = find(ows[0])
            groups = len({find(b) for b in buyers})
            bi = info.loc[[(a, b) for a in cl_accs for b in owners_by_acc.get(a, [])]]
            names, roles = {}, {}
            for (a, b), r in bi.iterrows():
                names[b] = r['RPTOWNERNAME']
                rr = roles.setdefault(b, set())
                if r['is_dir']: rr.add('Dir')
                if r['is_off']: rr.add('Off:' + (r['RPTOWNER_TITLE'] or '').strip()[:40])
                if r['is_ten']: rr.add('10%')
            signals.append(dict(
                issuer_cik=cik, issuer_name=f['issuer_name'], symbol=f['symbol'], signal_date=S.strftime('%Y-%m-%d'),
                trigger_accession=acc, trigger_buy_date=tx.strftime('%Y-%m-%d'),
                first_buy_date=cl_rows['tdate'].min().strftime('%Y-%m-%d'),
                days_trigger_buy_to_filing=int((S - tx).days),
                n_buyers=len(buyers), n_buyer_groups=groups, n_filings=len(cl_accs), n_buy_rows=len(cl_rows),
                joint_filer_only=groups < 2,
                buyers='; '.join(f"{names[b]} ({'/'.join(sorted(roles[b]))})" for b in buyers),
                any_ceo_cfo=bool(bi['is_ceo_cfo'].any()), any_ten_pct=bool(bi['is_ten'].any()),
                any_director=bool(bi['is_dir'].any()), any_officer=bool(bi['is_off'].any()),
                cluster_value=float(cl_rows.drop_duplicates('row_id')['value'].sum()),
                cluster_shares=float(cl_rows.drop_duplicates('row_id')['shares'].sum()),
                security_titles=' | '.join(sorted(set(cl_rows['SECURITY_TITLE'].str.strip())))[:300],
                any_non_common=bool(cl_rows['SECURITY_TITLE'].str.contains(NON_COMMON_RE).any()),
                entry_session=e))
    F['candidate_trigger_filings'] = n_cand
    F['signals_after_dedup'] = len(signals)
    return pd.DataFrame(signals)


def find_singles(p, o, P):
    """Description only: Form 4 buys by one insider where no different insider bought within 30 days
    either side, ever in the data. One per issuer per 60 sessions."""
    owners_by_acc = o.groupby('ACCESSION_NUMBER')['RPTOWNERCIK'].apply(lambda s: sorted(set(s))).to_dict()
    fil = (p.groupby('ACCESSION_NUMBER')
             .agg(filing_date=('filing_date', 'first'), issuer_cik=('issuer_cik', 'first'),
                  issuer_name=('ISSUERNAME', 'first'), symbol=('ISSUERTRADINGSYMBOL', 'first'),
                  tdates=('tdate', lambda s: sorted(set(s))), value=('value', 'sum'))
             .reset_index().sort_values(['issuer_cik', 'filing_date', 'ACCESSION_NUMBER']))
    win = pd.Timedelta(days=WINDOW_DAYS)
    out = []
    for cik, g in fil.groupby('issuer_cik', sort=False):
        allb = [(ow, td) for _, f in g.iterrows() for ow in owners_by_acc.get(f['ACCESSION_NUMBER'], []) for td in f['tdates']]
        last_e = -10 ** 9
        for _, f in g.iterrows():
            ows = owners_by_acc.get(f['ACCESSION_NUMBER'], [])
            if len(ows) != 1:
                continue
            x = ows[0]
            if any(y != x and abs(tx - ty) <= win for tx in f['tdates'] for (y, ty) in allb):
                continue
            e = P.entry_session(f['filing_date'])
            if e - last_e < DEDUP_SESSIONS:
                continue
            last_e = e
            out.append(dict(issuer_cik=cik, issuer_name=f['issuer_name'], symbol=f['symbol'],
                            signal_date=f['filing_date'].strftime('%Y-%m-%d'), accession=f['ACCESSION_NUMBER'],
                            value=float(f['value']), entry_session=e))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ outcomes + controls
def issuer_prices(p, cik, end, days=90):
    """(transaction date, price) of the issuer's insider buys in the 90 days up to `end`, for the mapping check"""
    q = p[(p['issuer_cik'] == cik) & (p['price'] > 0) & (p['tdate'] <= end) & (p['tdate'] >= end - pd.Timedelta(days=days))]
    return list(zip(q['tdate'], q['price']))


def recent_buy_matrix(p, P, M):
    """recent[e, j] = a defined insider buy at panel column j with transaction date in the 90 days before entry date e"""
    rec = np.zeros((P.T, P.N), bool)
    fil = p.groupby('ACCESSION_NUMBER').agg(symbol=('ISSUERTRADINGSYMBOL', 'first'), cik=('issuer_cik', 'first'),
                                             fd=('filing_date', 'first'), tdates=('tdate', lambda s: sorted(set(s))))
    for _, f in fil.iterrows():
        j, _, _ = M.map(f['symbol'], f['cik'], P.entry_session(f['fd']), lambda: issuer_prices(p, f['cik'], f['fd']))
        if j < 0:
            continue
        for td in f['tdates']:
            lo = np.searchsorted(P.dts, np.datetime64(td.date()), side='right')                       # entry > tdate
            hi = np.searchsorted(P.dts, np.datetime64((td + pd.Timedelta(days=CTRL_NOBUY_DAYS)).date()), side='right')
            rec[lo:hi, j] = True
    return rec


def evaluate(sig, P, M, recent, splits, ctrl_rows, label, p):
    out = []
    for i, s in sig.iterrows():
        r = dict(s)
        e = int(s['entry_session'])
        r['entry_date'] = P.dates[e] if e < P.T else ''
        j, method, conflict = M.map(s['symbol'], s['issuer_cik'], e,
                                    lambda: issuer_prices(p, s['issuer_cik'], pd.Timestamp(s['signal_date'])))
        r['map_method'] = method
        r['cik_conflict'] = conflict
        r['ticker'] = P.tick[j] if j >= 0 else ''
        r['status'] = 'tested'
        if j < 0:
            r['status'] = 'unmapped'; out.append(r); continue
        if e >= P.T or np.isnan(P.o[e, j]):
            r['status'] = 'no_price_at_entry'; out.append(r); continue
        pc, med = P.prior_close[e, j], P.med_dv[e, j]
        r['prior_close'] = pc
        r['median_dv20'] = med
        r['entry_open'] = P.o[e, j]
        r['takeable'] = bool(P.takeable[e, j])
        if not r['takeable']:
            r['status'] = 'not_takeable'
        if 'cluster_value' in s:
            mv, sh, asof, mvs = market_value(s['issuer_cik'], P.tick[j], P.dates[e], P.dates[e - 1], pc, splits)
            r.update(market_value=mv, shares_adj=sh, shares_asof=asof, mv_status=mvs)
        for k in HORIZONS:
            g, fl = P.ret(j, e, k, 'open')
            r[f'ret{k}_gross'] = g
            r[f'ret{k}_net'] = g - COST if g == g else np.nan
            r[f'ret{k}_flag'] = fl
            g2, fl2 = P.ret(j, e, k, 'close')
            r[f'ret{k}_net_nextclose'] = g2 - COST if g2 == g2 else np.nan
            r[f'ret{k}_flag_nextclose'] = fl2
        if not r['takeable']:
            out.append(r); continue
        # controls: takeable, no insider buy in the 90 days before, prior 20-day median $ volume 0.5x..2x
        ok = P.takeable[e].copy()
        ok &= (P.med_dv[e] >= CTRL_LO * med) & (P.med_dv[e] <= CTRL_HI * med)
        ok &= ~recent[e]
        ok[j] = False
        for t in M.tickers_of.get(s['issuer_cik'], []):
            ok[P.jx[t]] = False
        pool = np.where(ok)[0]
        rng = np.random.default_rng(int(s['signal_date'].replace('-', '')))
        pick = np.sort(rng.choice(pool, size=min(N_CTRL, len(pool)), replace=False)) if len(pool) else np.array([], int)
        r['ctrl_pool'] = len(pool)
        r['n_ctrl'] = len(pick)
        r['ctrl_tickers'] = ' '.join(P.tick[c] for c in pick)
        cr = {f'{k}{m}': [] for k in HORIZONS for m in ('', 'c')}
        flags = 0
        for c in pick:
            row = dict(study=label, signal_ticker=r['ticker'], signal_date=s['signal_date'], control=P.tick[c],
                       control_median_dv20=P.med_dv[e, c])
            for k in HORIZONS:
                g, fl = P.ret(c, e, k, 'open'); cr[f'{k}'].append(g); row[f'ret{k}'] = g; row[f'ret{k}_flag'] = fl
                g2, _ = P.ret(c, e, k, 'close'); cr[f'{k}c'].append(g2); row[f'ret{k}_nextclose'] = g2
                flags += (k == 60 and fl == 'stopped')
            ctrl_rows.append(row)
        r['ctrl_stopped_flags'] = flags
        for k in HORIZONS:
            a = np.array(cr[f'{k}'], float); a2 = np.array(cr[f'{k}c'], float)
            r[f'ctrl{k}_avg'] = np.nanmean(a) if np.isfinite(a).any() else np.nan
            r[f'ctrl{k}_avg_nextclose'] = np.nanmean(a2) if np.isfinite(a2).any() else np.nan
            r[f'excess{k}'] = r[f'ret{k}_net'] - r[f'ctrl{k}_avg']
            r[f'excess{k}_nextclose'] = r[f'ret{k}_net_nextclose'] - r[f'ctrl{k}_avg_nextclose']
        if len(pick) == 0:
            r['status'] = 'no_controls'
        out.append(r)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ statistics
def boot_ci(df, col, seed=BOOT_SEED, n=BOOT_N):
    d = df[['signal_date', col]].dropna()
    g = d.groupby('signal_date')[col].agg(['sum', 'count'])
    sums, cnts = g['sum'].values, g['count'].values
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), size=(n, len(g)))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def boot_diff(df, col, grp, seed=BOOT_SEED, n=BOOT_N):
    """resample whole signal days; difference of group means (grp True minus grp False)"""
    d = df[['signal_date', col, grp]].dropna()
    days = sorted(d['signal_date'].unique())
    di = {x: i for i, x in enumerate(days)}
    D = len(days)
    sA = np.zeros(D); cA = np.zeros(D); sB = np.zeros(D); cB = np.zeros(D)
    for dd, v, gflag in zip(d['signal_date'], d[col], d[grp]):
        i = di[dd]
        if gflag: sA[i] += v; cA[i] += 1
        else: sB[i] += v; cB[i] += 1
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, D, size=(n, D))
    with np.errstate(invalid='ignore', divide='ignore'):
        diff = sA[idx].sum(1) / cA[idx].sum(1) - sB[idx].sum(1) / cB[idx].sum(1)
    diff = diff[np.isfinite(diff)]
    return float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)), len(diff)


SELF_CHECKS = []
def stats(x, df=None, col=None, ci=True):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n == 0:
        return dict(n=0, mean=np.nan, median=np.nan, pos=np.nan, lo=np.nan, hi=np.nan)
    wins, losses = x[x > 0], x[x < 0]
    aw = wins.mean() if len(wins) else 0.0
    al = -losses.mean() if len(losses) else 0.0
    recon = len(wins) / n * aw - len(losses) / n * al
    SELF_CHECKS.append(abs(recon - x.mean()) < 1e-9)
    lo, hi = boot_ci(df, col) if (ci and df is not None) else (np.nan, np.nan)
    return dict(n=n, mean=x.mean(), median=float(np.median(x)), pos=(x > 0).mean(), lo=lo, hi=hi,
                wins=len(wins), avg_win=aw, losses=len(losses), avg_loss=al)


def pct(v, d=2):
    return 'n/a' if v is None or not np.isfinite(v) else f'{v * 100:+.{d}f}%'


def row(name, st):
    ci = f"{pct(st['lo'])} to {pct(st['hi'])}" if np.isfinite(st.get('lo', np.nan)) else 'n/a'
    pp = f"{st['pos'] * 100:.1f}%" if st['n'] else 'n/a'
    return f"| {name} | {st['n']} | {pct(st['mean'])} | {pct(st['median'])} | {pp} | {ci} |"


HDR = '| Group | n | Mean | Median | % positive | 95% interval (mean) |\n|---|---|---|---|---|---|'


# ------------------------------------------------------------------ main
def main():
    fetch_all()
    F = {}
    sub, own, ndt, fn = load_sec()
    F['form345_submissions'] = len(sub)
    p, o = build_buys(sub, own, ndt, fn, F)
    P = Panel()
    M = Mapper(P)
    splits = load_splits()
    sig = find_signals(p, o, P, F)
    recent = recent_buy_matrix(p, P, M)
    ctrl_rows = []
    S = evaluate(sig, P, M, recent, splits, ctrl_rows, 'IC1', p)
    sing = find_singles(p, o, P)
    SG = evaluate(sing, P, M, recent, splits, ctrl_rows, 'singles', p)

    # ---- write data files
    cols_first = ['signal_date', 'entry_date', 'ticker', 'issuer_name', 'issuer_cik', 'symbol', 'status', 'map_method',
                  'cik_conflict', 'takeable', 'n_buyers', 'n_buyer_groups', 'joint_filer_only', 'buyers', 'cluster_value',
                  'market_value', 'prior_close', 'median_dv20', 'entry_open', 'ret20_net', 'ret60_net', 'ctrl20_avg',
                  'ctrl60_avg', 'excess20', 'excess60', 'ret20_flag', 'ret60_flag', 'n_ctrl']
    S = S[[c for c in cols_first if c in S.columns] + [c for c in S.columns if c not in cols_first]]
    S.to_csv(os.path.join(HERE, 'signals.csv'), index=False, float_format='%.6g')
    SG.to_csv(os.path.join(HERE, 'singles.csv'), index=False, float_format='%.6g')
    pd.DataFrame(ctrl_rows).to_csv(os.path.join(HERE, 'controls.csv'), index=False, float_format='%.6g')

    # ---- tests
    T = S[S['status'] == 'tested'].copy()
    T = T[T['excess60'].notna()].copy()
    st1 = stats(T['excess60'], T, 'excess60')
    h1 = T[(T['signal_date'] >= HALF1[0]) & (T['signal_date'] <= HALF1[1])]
    h2 = T[(T['signal_date'] >= HALF2[0]) & (T['signal_date'] <= HALF2[1])]
    sh1 = stats(h1['excess60'], h1, 'excess60'); sh2 = stats(h2['excess60'], h2, 'excess60')
    t1_pass = (st1['mean'] > 0 and st1['lo'] > 0 and st1['median'] > 0 and sh1['mean'] > 0 and sh2['mean'] > 0)
    t1_parts = dict(mean_pos=st1['mean'] > 0, ci_above=st1['lo'] > 0, median_pos=st1['median'] > 0,
                    halves_same_sign=bool(np.sign(sh1['mean']) == np.sign(sh2['mean']) == np.sign(st1['mean'])))
    # costs-on-controls sensitivity (literal reading charges costs to the signal only)
    st1_cc = st1['mean'] + COST

    T2 =T[T['market_value'].notna()].copy(); T2['small'] = T2['market_value'] < MV_CUT
    st_small = stats(T2.loc[T2['small'], 'excess60'], T2[T2['small']], 'excess60')
    st_large = stats(T2.loc[~T2['small'], 'excess60'], T2[~T2['small']], 'excess60')
    d2lo, d2hi, d2n = boot_diff(T2, 'excess60', 'small')
    d2 = st_small['mean'] - st_large['mean']
    t2_sep = d2lo > 0

    T['big'] = T['cluster_value'] >= SIZE_CUT
    st_big = stats(T.loc[T['big'], 'excess60'], T[T['big']], 'excess60')
    st_sml = stats(T.loc[~T['big'], 'excess60'], T[~T['big']], 'excess60')
    d3lo, d3hi, d3n = boot_diff(T, 'excess60', 'big')
    d3 = st_big['mean'] - st_sml['mean']
    t3_sep = d3lo > 0

    # ---- description only
    st20 = stats(T['excess20'], T, 'excess20')
    T20 = S[(S['status'] == 'tested') & S['excess20'].notna()]
    st20_all = stats(T20['excess20'], T20, 'excess20')
    raw60 = stats(T['ret60_net'], T, 'ret60_net'); ctl60 = stats(T['ctrl60_avg'], T, 'ctrl60_avg')
    raw20 = stats(T['ret20_net'], T, 'ret20_net'); ctl20 = stats(T['ctrl20_avg'], T, 'ctrl20_avg')
    SGT = SG[(SG['status'] == 'tested') & SG['excess60'].notna()]
    sg60 = stats(SGT['excess60'], SGT, 'excess60'); sg20 = stats(SGT['excess20'].dropna(), SGT[SGT['excess20'].notna()], 'excess20')
    ceo = stats(T.loc[T['any_ceo_cfo'], 'excess60'], T[T['any_ceo_cfo']], 'excess60')
    noceo = stats(T.loc[~T['any_ceo_cfo'], 'excess60'], T[~T['any_ceo_cfo']], 'excess60')
    ten = stats(T.loc[T['any_ten_pct'], 'excess60'], T[T['any_ten_pct']], 'excess60')
    noten = stats(T.loc[~T['any_ten_pct'], 'excess60'], T[~T['any_ten_pct']], 'excess60')
    TNC = T[T['excess60_nextclose'].notna()]
    nc60 = stats(TNC['excess60_nextclose'], TNC, 'excess60_nextclose')
    TNC20 = T[T['excess20_nextclose'].notna()]
    nc20 = stats(TNC20['excess20_nextclose'], TNC20, 'excess20_nextclose')
    jo = stats(T.loc[T['joint_filer_only'], 'excess60'], T[T['joint_filer_only']], 'excess60')
    ind = stats(T.loc[~T['joint_filer_only'], 'excess60'], T[~T['joint_filer_only']], 'excess60')
    smt = T2[T2['small']]
    smh1 = smt[(smt['signal_date'] >= HALF1[0]) & (smt['signal_date'] <= HALF1[1])]
    smh2 = smt[(smt['signal_date'] >= HALF2[0]) & (smt['signal_date'] <= HALF2[1])]
    sm_h1 = stats(smh1['excess60'], smh1, 'excess60'); sm_h2 = stats(smh2['excess60'], smh2, 'excess60')
    over_mv = T[T['market_value'].notna() & (T['cluster_value'] > T['market_value'])]

    # ---- counts a month
    S['month'] = S['signal_date'].str[:7]
    months = pd.period_range('2024-10', '2026-03', freq='M').strftime('%Y-%m')
    cm = pd.DataFrame(index=months)
    cm['all'] = S.groupby('month').size().reindex(months, fill_value=0)
    cm['mapped'] = S[S['status'] != 'unmapped'].groupby('month').size().reindex(months, fill_value=0)
    cm['takeable'] = S[S['takeable'] == True].groupby('month').size().reindex(months, fill_value=0)
    cm['tested'] = T.assign(month=T['signal_date'].str[:7]).groupby('month').size().reindex(months, fill_value=0)
    nmon = len(months)

    # ---- IWM context
    iwm_txt = 'IWM context: not available (download failed). [UNVERIFIED]'
    try:
        j = json.load(open(os.path.join(DATA, 'iwm_daily.json')))
        res = j['chart']['result'][0]
        off = res['meta'].get('gmtoffset', -14400)
        q = res['indicators']['quote'][0]
        iw = pd.DataFrame({'date': [dt.datetime.fromtimestamp(t + off, dt.timezone.utc).strftime('%Y-%m-%d') for t in res['timestamp']],
                           'open': q['open'], 'close': q['close']}).set_index('date')
        iw = iw.reindex(P.dates)
        vals = []
        for e in T['entry_session'].astype(int):
            if e + 60 < P.T:
                vals.append(iw['close'].iloc[e + 60] / iw['open'].iloc[e] - 1)
        vals = np.array(vals, float)
        miss = int(iw['close'].isna().sum())
        iwm_txt = (f'IWM context (Yahoo daily, price only, no dividends): over the same 60-session windows as the '
                   f'{len(vals)} tested signals, IWM returned {pct(np.nanmean(vals))} on average. '
                   f'Panel sessions with no IWM bar: {miss}. Context only; the test uses the matched controls.')
    except Exception as ex:
        iwm_txt += f' ({type(ex).__name__})'

    # ---- examples: five tested signals drawn with the study seed
    ex = T.sample(n=min(5, len(T)), random_state=BOOT_SEED).sort_values('signal_date')

    # ---- funnel
    st_counts = S['status'].value_counts().to_dict()
    n_unmapped = st_counts.get('unmapped', 0)
    n_noprice = st_counts.get('no_price_at_entry', 0)
    n_nottake = st_counts.get('not_takeable', 0)
    n_noctrl = st_counts.get('no_controls', 0)
    mv_counts = T['mv_status'].value_counts().to_dict()
    flag60 = T['ret60_flag'].value_counts().to_dict()
    capped = int((T['ret60_gross'] >= CAP).sum())
    n_conflict = int(S['cik_conflict'].fillna(False).astype(bool).sum())
    by_method = S['map_method'].value_counts().to_dict()
    stale = int((T['days_trigger_buy_to_filing'] > WINDOW_DAYS).sum())
    late = T['days_trigger_buy_to_filing'] > WINDOW_DAYS
    st_late = stats(T.loc[late, 'excess60'], T[late], 'excess60', ci=False)
    st_nonc = stats(T.loc[T['any_non_common'], 'excess60'], T[T['any_non_common']], 'excess60', ci=False)
    ctrl_short = int((T['n_ctrl'] < N_CTRL).sum())
    assert all(SELF_CHECKS), 'self-consistency check failed'

    # ---- RESULTS.md
    L = []
    w = L.append
    w('# IC1 results: insider cluster buying\n')
    w(f'Run of the study in `../PREREG_IC1.md` (git a90d629), built by `run.py` on {dt.date.today().isoformat()}. '
      'Every number below is printed by that script. Returns are after the 1% round-trip cost on the signal stock. '
      '"Excess" is the signal return after costs minus the average return of its matched controls.\n')
    w('## Verdicts\n')
    w(f"**T1, does the cluster filter pay? {'PAYS' if t1_pass else 'DOES NOT PAY'}.**\n")
    w(HDR)
    w(row('All tested signals, 60-session excess', st1))
    w(row(f'First half ({HALF1[0]} to {HALF1[1]})', sh1))
    w(row(f'Second half ({HALF2[0]} to {HALF2[1]})', sh2))
    w('')
    w(f"Pass marks: mean above zero ({'yes' if t1_parts['mean_pos'] else 'no'}); 95% interval above zero "
      f"({'yes' if t1_parts['ci_above'] else 'no'}); median above zero ({'yes' if t1_parts['median_pos'] else 'no'}); "
      f"same sign in both halves ({'yes' if t1_parts['halves_same_sign'] else 'no'}). All four are needed.\n")
    if not t1_pass:
        fails = [k for k, v in [('the interval includes zero', not t1_parts['ci_above']),
                                ('the median is not above zero', not t1_parts['median_pos']),
                                ('the mean is not above zero', not t1_parts['mean_pos']),
                                ('the halves disagree', not t1_parts['halves_same_sign'])] if v]
        w(f"In plain words: following every cluster did not beat similar stocks by a margin we can trust; "
          f"{' and '.join(fails)}. "
          + ("The typical signal trailed its controls, and fewer than half beat them. A minority of large winners lifts the mean.\n"
             if st1['median'] < 0 and st1['mean'] > 0 else '\n'))
    w(f"**T2, are small companies stronger? {'SEPARATES' if t2_sep else 'DOES NOT SEPARATE'}.**\n")
    w(HDR)
    w(row('Market value under $300M', st_small))
    w(row('Market value $300M or more', st_large))
    w('')
    w(f'Difference (small minus large): {pct(d2)}, 95% interval {pct(d2lo)} to {pct(d2hi)} '
      f'({d2n} usable bootstrap draws). Pass mark: interval above zero. '
      f'{len(T) - len(T2)} tested signals had no usable share count and are left out of T2.\n')
    if t2_sep:
        w(f"In plain words: clusters in companies under $300M did better against their controls than clusters in larger "
          f"companies, and the gap clears the pass mark. T2 only compares the two groups; it does not show that the small "
          f"group pays on its own (its median excess is {pct(st_small['median'])} and {st_small['pos'] * 100:.1f}% beat their controls).\n")
    w(f"**T3, do bigger clusters carry more signal? {'SEPARATES' if t3_sep else 'DOES NOT SEPARATE'}.**\n")
    w(HDR)
    w(row('Cluster worth $250k or more', st_big))
    w(row('Cluster worth under $250k', st_sml))
    w('')
    w(f'Difference (big minus small): {pct(d3)}, 95% interval {pct(d3lo)} to {pct(d3hi)} '
      f'({d3n} usable bootstrap draws). Pass mark: interval above zero.\n')
    if not t3_sep and d3hi < 0:
        w('In plain words: bigger clusters did not carry more signal. The gap went the other way: clusters under $250k '
          'did better than bigger ones, and that interval sits below zero.\n')
    p_any = 1 - 0.975 ** 3
    w(f'Three tests were run. If none of the three effects were real, each 95% interval would still sit wholly above zero '
      f'about 2.5% of the time, so the chance that at least one of the three does by luck alone is about '
      f'{p_any * 100:.0f}% (1 - 0.975^3, treating them as independent).\n')
    w(f'Self-consistency check: for every group in this file, (wins / n) x average win minus (losses / n) x average loss '
      f'equals the mean to within 1e-9. It ran on {len(SELF_CHECKS)} groups and passed on all of them. '
      f"For T1: {st1['wins']} wins averaging {pct(st1['avg_win'])}, {st1['losses']} losses averaging "
      f"{pct(-st1['avg_loss'])}, n = {st1['n']}, giving {pct(st1['wins'] / st1['n'] * st1['avg_win'] - st1['losses'] / st1['n'] * st1['avg_loss'], 4)} "
      f"against a mean of {pct(st1['mean'], 4)}.\n")

    w('## Description only (not tests, never promoted to results)\n')
    w('Each interval here comes from the same day-resampled bootstrap, but none of these rows is a test.\n')
    w(HDR)
    w(row('Signal return after costs, 60 sessions (not excess)', raw60))
    w(row('Controls average return, 60 sessions (no costs)', ctl60))
    w(row('Excess, 20 sessions', st20))
    w(row('Signal return after costs, 20 sessions', raw20))
    w(row('Controls average return, 20 sessions', ctl20))
    w(row('Single-insider buys that never became clusters, 60-session excess', sg60))
    w(row('Single-insider buys, 20-session excess', sg20))
    w(row('Clusters with a chief executive or finance chief buying, 60-session excess', ceo))
    w(row('Clusters without one, 60-session excess', noceo))
    w(row('Clusters with a 10% owner buying, 60-session excess', ten))
    w(row('Clusters without one, 60-session excess', noten))
    w(row('Next-close entry, 60-session excess', nc60))
    w(row('Next-close entry, 20-session excess', nc20))
    w(row('Clusters made only by joint filers (one buyer group), 60-session excess', jo))
    w(row('Clusters with two or more separate buyer groups, 60-session excess', ind))
    w(row(f'Market value under $300M, first half, 60-session excess', sm_h1))
    w(row(f'Market value under $300M, second half, 60-session excess', sm_h2))
    w('')
    w('## How many signals\n')
    w(f"Over {nmon} months of filings: {int(cm['all'].sum())} cluster signals after the one-per-60-sessions rule "
      f"({cm['all'].sum() / nmon:.1f} a month), {int(cm['mapped'].sum())} mapped to a stock in the price panel, "
      f"{int(cm['takeable'].sum())} takeable ({cm['takeable'].sum() / nmon:.1f} a month), "
      f"{int(cm['tested'].sum())} tested ({cm['tested'].sum() / nmon:.1f} a month).\n")
    w('| Month | All signals | Mapped | Takeable | Tested |\n|---|---|---|---|---|')
    for m_, r_ in cm.iterrows():
        w(f"| {m_} | {r_['all']} | {r_['mapped']} | {r_['takeable']} | {r_['tested']} |")
    w('')
    w('## Five example signals\n')
    w('Drawn at random from the tested signals with the study seed.\n')
    w('| Signal date | Ticker | Buyers | Cluster $ | 60-session return after costs | Controls average | Excess |\n|---|---|---|---|---|---|---|')
    for _, r_ in ex.iterrows():
        w(f"| {r_['signal_date']} | {r_['ticker']} | {r_['buyers']} | {r_['cluster_value']:,.0f} | {pct(r_['ret60_net'])} | "
          f"{pct(r_['ctrl60_avg'])} | {pct(r_['excess60'])} |")
    w('')
    w('## Funnel\n')
    w('| Step | Count |\n|---|---|')
    for k_, v_ in [('Form 3/4/5 filings in the six quarters', F['form345_submissions']),
                   ('Code P, acquired rows (all forms)', F['p_acquired_rows_all_forms']),
                   ('  of which on Form 4/A (left out)', F['p_rows_form4_amend']),
                   ('  of which on Form 5 or 5/A (left out)', F['p_rows_form5']),
                   ('Code P, acquired rows on original Form 4', F['p_rows_form4']),
                   ('  left out: no director, officer or 10% owner among the reporting owners', F['p_rows_no_qualifying_owner']),
                   ('  left out: 10b5-1 box ticked on the filing', F['p_rows_10b51_flag']),
                   ('  left out: 10b5-1 named in a footnote on the row, box not ticked', F['p_rows_10b51_footnote_only']),
                   ('  left out: unreadable transaction date', F['p_rows_bad_trans_date']),
                   ('  transaction date after filing date (set to filing date)', F['p_rows_trans_after_filing']),
                   ('  rows with no price (counted as $0 in cluster size)', F['p_rows_no_value']),
                   ('Insider-buy rows kept', F['insider_buy_rows']),
                   ('Insider-buy filings kept', F['insider_buy_filings']),
                   ('  of which joint filings (2+ qualifying reporting owners)', F['joint_filings']),
                   ('Issuers with an insider buy', F['insider_buy_issuers']),
                   ('Filings that complete a cluster (before the 60-session rule)', F['candidate_trigger_filings']),
                   ('Cluster signals after the 60-session rule', F['signals_after_dedup']),
                   ('  could not be mapped to a panel stock', n_unmapped),
                   ('  mapped, but no price at the entry open', n_noprice),
                   ('  mapped and priced, not takeable', n_nottake),
                   ('  takeable, no control found', n_noctrl),
                   ('Tested (T1 n)', st1['n'])]:
        w(f'| {k_} | {v_} |')
    w('')
    w(f"Mapping: {by_method.get('symbol', 0)} signals by the trading symbol on the filing, {by_method.get('cik', 0)} by CIK "
      f"through sic_map.csv, {by_method.get('unmapped', 0) + by_method.get('symbol_rejected', 0)} not mapped. "
      f"In {n_conflict} signals the symbol on the filing is a panel ticker that sic_map.csv lists under a different CIK; "
      f"{n_conflict - by_method.get('symbol_rejected', 0)} of them passed the price check and were kept, "
      f"{by_method.get('symbol_rejected', 0)} failed it and are counted as not mapped.\n")
    w(f"Market value for the {len(T)} tested signals: " + ', '.join(f'{k_} {v_}' for k_, v_ in sorted(mv_counts.items())) + '.\n')
    w(f"60-session exit flags for tested signals: " + ', '.join(f"{k_ or 'normal close'} {v_}" for k_, v_ in sorted(flag60.items())) +
      f". Signals capped at +300%: {capped}. Tested signals with fewer than 10 controls: {ctrl_short}. "
      f"Control 60-session exits marked at last close because the stock stopped trading: {int(T['ctrl_stopped_flags'].sum())} "
      f"of {int(T['n_ctrl'].sum())}.\n")
    w(iwm_txt + '\n')

    w('## Caveats\n')
    cc_pass = (st1['mean'] + COST > 0 and st1['lo'] + COST > 0 and st1['median'] + COST > 0
               and sh1['mean'] + COST > 0 and sh2['mean'] + COST > 0)
    w(f"- Costs are charged to the signal stock only, which is the literal reading of T1 (\"the return after costs minus the "
      f"controls' average\"). If the controls also paid 1%, every excess return would be 1.00 point higher: T1 mean "
      f"{pct(st1_cc)}, interval {pct(st1['lo'] + COST)} to {pct(st1['hi'] + COST)}, median {pct(st1['median'] + COST)}, "
      f"halves {pct(sh1['mean'] + COST)} and {pct(sh2['mean'] + COST)}. Under that reading T1 would "
      f"{'PASS' if cc_pass else 'still NOT PASS'}"
      + ('' if cc_pass else (', because the median would still be below zero' if st1['median'] + COST <= 0 else ''))
      + ". T2 and T3 compare groups, so this does not change them.")
    w(f"- A joint Form 4 lists several reporting owners against one set of purchases. Read literally, that is two or more "
      f"different reporting owners buying, so it counts. {int(T['joint_filer_only'].sum())} of the {len(T)} tested signals "
      f"are clusters made only by owners who file together (often one fund and its managers). The table above shows them separately.")
    w(f"- {stale} tested signals were triggered by a Form 4 filed more than 30 days after the purchase (late filings, some "
      f"reporting purchases years old). Read literally they still count. Their mean 60-session excess was {pct(st_late['mean'])}.")
    w(f"- Code P covers any non-derivative security. {int(T['any_non_common'].sum())} tested clusters include a purchase of "
      f"preferred stock, notes or warrants rather than common stock (mean 60-session excess {pct(st_nonc['mean'])}). Code P also "
      f"covers insiders buying in an IPO or a private placement, which the pre-registration includes.")
    w('- The data starts with filings on 1 Oct 2024. A buyer who bought in September 2024 cannot be seen, so early October '
      'clusters may be missed, and controls in late 2024 are only screened for insider buys from 1 Oct 2024.')
    w('- The price panel starts on 1 Oct 2024, so signals in the first 20 sessions use a shorter dollar-volume lookback.')
    w('- The panel holds US common stocks only. Funds, OTC stocks and units are not in it, which is most of the unmapped signals.')
    w('- When a company changes ticker, the panel series ends and the stock is marked at its last close, the same as a delisting.')
    w('- Share counts come from the dei cover-page tag. Companies with several share classes may report one class only, '
      'which understates market value.')
    w(f"- Purchase values are taken as filed. {len(over_mv)} tested clusters are worth more than the company's whole market "
      f"value ({', '.join(over_mv['ticker'] + ' ' + over_mv['signal_date'])}), which points to an error in a filed purchase price or in the share count. "
      f"They sit in the $250k-or-more group for T3.")
    w('- One period (Oct 2024 to Mar 2026) and one market. A pass here would still need a forward log.\n')

    w('## Deviations and choices\n')
    w('- The 10b5-1 indicator exists (`AFF10B5ONE` in SUBMISSION) but it is a box on the whole filing, not on each trade. '
      'A filing with the box ticked is left out in full. Rows whose own footnote says the purchase was made under a 10b5-1 '
      'plan are also left out. A footnote that says "non-Rule 10b5-1" is not treated as a plan.')
    w('- Only original Form 4 filings are used. Form 4/A amendments are left out so the same purchase is not counted twice, '
      'and Form 5 is left out because the signal is defined on a Form 4.')
    w('- The data has no link between a purchase row and one owner of a joint filing, so every qualifying owner on the '
      'filing is treated as a buyer of every purchase row on it. Cluster dollar value counts each purchase row once.')
    w('- "Within 30 calendar days" is measured between transaction dates. A filing triggers when one of its purchases '
      'is within 30 days of a purchase by a different owner that was public by then (filed on or before that filing date).')
    w('- Cluster size is the dollar value of all insider-buy rows public by the end of the signal date whose transaction '
      'date is within 30 days either side of the triggering purchase.')
    w('- The 60-session rule is applied to all signals by issuer before the takeable filter and before mapping.')
    w('- Exits are the closes 20 and 60 sessions after the entry session (entry session = session 0). Prices are '
      'split-adjusted only; dividends are not included.')
    w('- A takeable stock also needs an opening price on the entry session. Missing days in the 20-session dollar-volume '
      'window count as zero dollar volume.')
    w('- Controls are screened for insider buys (as defined) with a transaction date in the 90 calendar days before the '
      'entry date, for buys that could be mapped to a panel stock. Share classes of the same issuer are not used as its controls. '
      'The seed for each signal is its signal date as YYYYMMDD. Controls are charged no cost.')
    w('- Market value uses the latest share count filed before the entry date, rejected if its as-of date is more than '
      '15 months before entry, split-adjusted with the panel split files, times the raw prior close.')
    w('- Insider-buy rows with no price count as $0 in cluster size.')
    w('- Mapping check (the pre-registration does not say how to map): when the symbol on the filing is a panel '
      'ticker that sic_map.csv lists under a different CIK, the match is kept only if the median of the issuer\'s insider '
      'purchase prices (90 days up to the signal) divided by the panel close on each purchase date is between 0.5 and 2. '
      'Otherwise the CIK fallback is tried, and if that fails the signal counts as not mapped. This removed a closed-end '
      'fund mapped to a bank and an unlisted insurer mapped to a pipeline partnership.')
    w("- IWM is used for context only.")
    w('')
    with open(os.path.join(HERE, 'RESULTS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))

    # ---- console summary
    print(json.dumps(F, indent=1))
    print('status', st_counts)
    print('T1', {k: (round(v, 5) if isinstance(v, float) else v) for k, v in st1.items()}, 'pass', t1_pass, t1_parts)
    print('H1', round(sh1['mean'], 5), sh1['n'], 'H2', round(sh2['mean'], 5), sh2['n'])
    print('T2 small', st_small['n'], round(st_small['mean'], 5), 'large', st_large['n'], round(st_large['mean'], 5),
          'diff', round(d2, 5), (round(d2lo, 5), round(d2hi, 5)), 'sep', t2_sep)
    print('T3 big', st_big['n'], round(st_big['mean'], 5), 'small', st_sml['n'], round(st_sml['mean'], 5),
          'diff', round(d3, 5), (round(d3lo, 5), round(d3hi, 5)), 'sep', t3_sep)
    print('self checks', len(SELF_CHECKS), all(SELF_CHECKS))
    print(iwm_txt)


if __name__ == '__main__':
    main()
