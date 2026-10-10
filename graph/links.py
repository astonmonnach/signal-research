"""The link graph: every row in edges.csv says "A is linked to B, here is how, here is the document that proves it".

    python graph/links.py neighbours TICKER [--hops 3] [--industry]   walk the chain outward from a ticker
    python graph/links.py add A B TYPE "detail" SOURCE [YYYY-MM-DD]   add one sourced link (duplicates are skipped)
    python graph/links.py stats                                        how many nodes and links, by type

Nodes are tickers (MTUS) or named things that aren't listed: office:SP8000, fund:Erez Asset Management, co:Century.
Links are two-way. A link without a source is not allowed: an unproven link is a guess and belongs in a note, not here.
--industry also lists stocks with the same 4-digit SIC code (a weak link, from research/domino/sic_map.csv).
"""
import csv
import sys
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDGES = HERE / "edges.csv"
FIELDS = ["date", "a", "b", "type", "detail", "source"]
TYPES = {"merger", "asset_deal", "spin_off", "holder_13d", "awarded_by", "peer_named", "counterparty", "customer", "supplier",
         "subsidiary", "shared_director", "same_theme"}


def load():
    if not EDGES.exists():
        return []
    with open(EDGES, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def node(x):
    return x.strip() if ":" in x else x.strip().upper()


def add(a, b, typ, detail, source, when=None):
    a, b = node(a), node(b)
    if typ not in TYPES:
        raise SystemExit(f"unknown type '{typ}'. Use one of: {', '.join(sorted(TYPES))}")
    if not source.strip():
        raise SystemExit("a link needs a source (filing URL or note path)")
    rows = load()
    if any({r["a"], r["b"]} == {a, b} and r["type"] == typ for r in rows):
        print(f"already linked: {a} -- {b} ({typ})"); return False
    new = not EDGES.exists()
    with open(EDGES, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerow(dict(date=when or date.today().isoformat(), a=a, b=b, type=typ, detail=detail, source=source))
    print(f"linked: {a} -- {b} ({typ})"); return True


def graph():
    g = defaultdict(list)
    for r in load():
        g[r["a"]].append((r["b"], r)); g[r["b"]].append((r["a"], r))
    return g


def neighbours(start, hops=3, industry=False):
    start = node(start); g = graph()
    if start not in g:
        print(f"{start}: no sourced links yet.")
    seen, q, found = {start}, deque([(start, 0, [start])]), []
    while q:
        cur, d, path = q.popleft()
        if d == hops: continue
        for nxt, r in g.get(cur, []):
            if nxt in seen: continue
            seen.add(nxt); found.append((d + 1, path + [nxt], r)); q.append((nxt, d + 1, path + [nxt]))
    for hop in range(1, hops + 1):
        level = [x for x in found if x[0] == hop]
        if not level: continue
        print(f"\n{hop} link{'s' if hop > 1 else ''} away ({len(level)}):")
        for _, path, r in level:
            print(f"  {' -> '.join(path)}   [{r['type']}] {r['detail']}  ({r['date']}; {r['source']})")
    tickers = sorted({p[-1] for _, p, _ in found if ":" not in p[-1]})
    print(f"\nListed names within {hops} links of {start}: {', '.join(tickers) or 'none'}")
    if industry:
        sic_file = HERE.parent / "research" / "domino" / "sic_map.csv"
        if sic_file.exists():
            m = {r["ticker"]: r for r in csv.DictReader(open(sic_file, encoding="utf-8"))}
            if start in m:
                code = m[start]["sic"]; same = sorted(t for t, r in m.items() if r["sic"] == code and t != start)
                print(f"\nSame industry code {code} ({m[start]['sic_desc']}), a weak link, {len(same)} stocks: {', '.join(same[:60])}{' ...' if len(same) > 60 else ''}")
            else:
                print(f"\n{start} has no industry code in sic_map.csv.")
    return tickers


def stats():
    rows = load(); nodes = {r["a"] for r in rows} | {r["b"] for r in rows}; by = defaultdict(int)
    for r in rows: by[r["type"]] += 1
    print(f"{len(nodes)} nodes, {len(rows)} links: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "add":
        add(*a[1:6], *(a[6:7]))
    elif a[0] == "neighbours":
        hops = int(a[a.index("--hops") + 1]) if "--hops" in a else 3
        neighbours(a[1], hops, "--industry" in a)
    elif a[0] == "stats":
        stats()
    else:
        print(__doc__)
