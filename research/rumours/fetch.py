"""Fetch helpers for the rumour study. Caches raw responses under data/ so run.py can recompute offline.
Usage: python fetch.py prices TICKER [TICKER...]   (daily bars 2026-02-01 .. today, Yahoo)
       python fetch.py subs CIK                     (EDGAR submissions JSON)
       python fetch.py facts CIK                    (EDGAR XBRL companyfacts, trimmed)
"""
import json, os, sys, time, urllib.request, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
UA_BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
UA_SEC = 'PersonalResearch research@example.com'
P1 = int(dt.datetime(2026, 2, 1, tzinfo=dt.timezone.utc).timestamp())

def get(url, ua):
    req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': 'application/json'})
    for i in range(4):
        try:
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            err = e
            if '404' in str(e): break
            time.sleep(2 + 3 * i)
    raise err

def prices(t):
    p2 = int(time.time())
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1={P1}&period2={p2}&interval=1d&events=div%2Csplits'
    try:
        raw = get(url, UA_BROWSER)
    except Exception as e:
        if '404' in str(e):
            raise RuntimeError('404 at Yahoo (symbol not served)')
        raise
    d = json.loads(raw)
    out = os.path.join(HERE, 'data', 'prices', f'{t}.json')
    json.dump(d, open(out, 'w'))
    r = d['chart']['result'][0] if d['chart'].get('result') else None
    n = len(r['timestamp']) if r and r.get('timestamp') else 0
    print(t, 'bars', n, 'exch', r['meta'].get('exchangeName') if r else None)

def subs(cik):
    cik = str(int(cik)).zfill(10)
    raw = get(f'https://data.sec.gov/submissions/CIK{cik}.json', UA_SEC)
    open(os.path.join(HERE, 'data', 'sec', f'subs_{cik}.json'), 'wb').write(raw)
    d = json.loads(raw)
    print(d['name'], d.get('tickers'), d.get('exchanges'))

def facts(cik):
    cik = str(int(cik)).zfill(10)
    raw = get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', UA_SEC)
    d = json.loads(raw)
    keep = {}
    wanted = ['EntityCommonStockSharesOutstanding', 'CashAndCashEquivalentsAtCarryingValue', 'LongTermDebt', 'LongTermDebtNoncurrent',
              'LongTermDebtCurrent', 'DebtCurrent', 'ShortTermBorrowings', 'LongTermDebtAndCapitalLeaseObligations', 'ConvertibleNotesPayable',
              'ConvertibleNotesPayableCurrent', 'ConvertibleDebtNoncurrent', 'SeniorNotes', 'LineOfCredit', 'NotesPayable',
              'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'ShortTermInvestments', 'MarketableSecuritiesCurrent',
              'LongTermDebtAndCapitalLeaseObligationsCurrent', 'OperatingLeaseLiabilityNoncurrent', 'WeightedAverageNumberOfDilutedSharesOutstanding']
    for ns, fs in d.get('facts', {}).items():
        for k, v in fs.items():
            if k in wanted:
                units = {u: [x for x in vals if x.get('end', '') >= '2025-06-30'] for u, vals in v['units'].items()}
                keep[f'{ns}:{k}'] = units
    out = {'cik': cik, 'entityName': d.get('entityName'), 'facts': keep}
    json.dump(out, open(os.path.join(HERE, 'data', 'sec', f'facts_{cik}.json'), 'w'))
    print(d.get('entityName'), len(keep), 'concepts kept')

if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    for a in args:
        try:
            {'prices': prices, 'subs': subs, 'facts': facts}[cmd](a)
        except Exception as e:
            print(a, 'FAILED', e)
        time.sleep(0.4)
