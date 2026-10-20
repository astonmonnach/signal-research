"""Copy Massive connector responses from Claude's session transcript into ./cache (verbatim).

The Massive connector is reachable only through Claude's tool calls, so `run.py plan` prints the calls
to make, Claude makes them, and this script finds each call and its response in the transcript and saves
the response under the cache path `run.py` expects, together with the request that produced it.
Rate-limit and other error responses are never cached. Existing cache files are never overwritten.

    python ingest.py [transcript.jsonl ...]     (default: this project's four newest transcripts)
"""
import os, sys, json, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
PROJ = os.path.expanduser('~/.claude/projects/C--Users-thoma-catalyst-research')


def save_path(path, params):
    p = params or {}
    if path == '/v3/reference/options/contracts':
        kind = 'all'
        if 'strike_price.gte' in p:
            ratio = float(p['strike_price.lte']) / float(p['strike_price.gte'])
            kind = 'w' if abs(ratio - 3.0) < 0.01 else 'w25' if abs(ratio - 1.25 / 0.75) < 0.01 else 'wx'
        return os.path.join(CACHE, 'contracts',
                            f"{p['underlying_ticker']}_{p['as_of']}_{p['expiration_date']}_{kind}.json")
    m = re.match(r'^/v2/aggs/ticker/O:([A-Z0-9.]+)/range/1/day/(\d{4}-\d\d-\d\d)/(\d{4}-\d\d-\d\d)$', path)
    if m:
        return os.path.join(CACHE, 'optaggs', f'{m.group(1)}_{m.group(2)}_{m.group(3)}.json')
    m = re.match(r'^/v3/reference/options/contracts/O:([A-Z0-9.]+)$', path)
    if m and 'as_of' in p:
        return os.path.join(CACHE, 'check', f"{m.group(1)}_{p['as_of']}.json")
    # the connector serves Massive split records at /stocks/v1/splits (/v3/reference/splits is not on its
    # allowlist); same records and columns, saved under the path run.py expects
    if path in ('/v3/reference/splits', '/stocks/v1/splits'):
        return os.path.join(CACHE, 'splits', f"{p['execution_date.gte']}_{p['execution_date.lte']}.json")
    m = re.match(r'^/v2/aggs/grouped/locale/us/market/stocks/(\d{4}-\d\d-\d\d)$', path)
    if m and str(p.get('adjusted')).lower() == 'false':
        return os.path.join(CACHE, 'grouped', f'{m.group(1)}.json')
    return None


def result_text(content):
    """Tool-result content -> the connector's JSON string (follows overflow files)."""
    if isinstance(content, list):
        content = ''.join(c.get('text', '') for c in content if isinstance(c, dict))
    if not isinstance(content, str):
        return None
    s = content.strip()
    if s.startswith('{"result"'):
        return s
    m = re.search(r'([A-Za-z]:[\\/][^\s"]+tool-results[\\/][^\s"]+\.(?:txt|json))', s)
    if m and os.path.exists(m.group(1)):
        with open(m.group(1), encoding='utf-8') as fh:
            t = fh.read().strip()
        return t if t.startswith('{"result"') else None
    return None


def main(files):
    calls, saved, skipped_err, exists = {}, 0, 0, 0
    for f in files:
        with open(f, encoding='utf-8') as fh:
            for line in fh:
                if 'Massive_Market_Data' not in line and 'tool_result' not in line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                msg = o.get('message') or {}
                content = msg.get('content')
                if not isinstance(content, list):
                    continue
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get('type') == 'tool_use' and c.get('name', '').endswith('Massive_Market_Data__call_api'):
                        calls[c['id']] = c.get('input', {})
                    elif c.get('type') == 'tool_result' and c.get('tool_use_id') in calls:
                        inp = calls[c['tool_use_id']]
                        sp = save_path(inp.get('path', ''), inp.get('params'))
                        if sp is None:
                            continue
                        txt = result_text(c.get('content'))
                        if txt is None:
                            continue
                        try:
                            res = json.loads(txt)['result']
                        except Exception:
                            continue
                        if not isinstance(res, str):
                            continue
                        # a 404 on a single-contract lookup is an answer (no such contract that day); every
                        # other error, such as the rate limit, is not cached and the call is made again
                        is_check = '/check/' in sp.replace(os.sep, '/')
                        if res.startswith('Error') and not (is_check and res.startswith('Error [HTTP]: HTTP 404')):
                            skipped_err += 1
                            continue
                        if os.path.exists(sp):
                            exists += 1
                            continue
                        os.makedirs(os.path.dirname(sp), exist_ok=True)
                        with open(sp, 'w', encoding='utf-8') as out:
                            json.dump(dict(request=dict(path=inp.get('path'), params=inp.get('params')),
                                           saved_from=os.path.basename(f), result=res), out)
                        saved += 1
    print(f'ingest: saved {saved}, already cached {exists}, error responses skipped {skipped_err}')


if __name__ == '__main__':
    fs = sys.argv[1:]
    if not fs:
        # newest transcripts of this project, sessions and subagents alike (whoever made the calls)
        fs = sorted(glob.glob(os.path.join(PROJ, '*', 'subagents', 'agent-*.jsonl')) +
                    glob.glob(os.path.join(PROJ, '*.jsonl')), key=os.path.getmtime)[-4:]
    main(fs)
