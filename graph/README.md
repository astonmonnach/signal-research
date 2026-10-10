# The link graph

Every row in `edges.csv` is one sourced link: **A is linked to B, how, and the document that proves it.** Links are two-way, so chains form on their own: MTUS is linked to the stockpile office, the stockpile office is linked to ELMT, so MTUS and ELMT are two links apart.

```
python graph/links.py neighbours MTUS --hops 3            # walk the chain outward
python graph/links.py neighbours MSGS --hops 3 --industry  # also list same-industry stocks (a weak link)
python graph/links.py add A B TYPE "detail" SOURCE [DATE]  # add one link; a source is required
python graph/links.py stats
```

- **Nodes** are tickers, or named things that aren't listed: `office:SP8000 (DLA stockpile)`, `fund:Erez Asset Management`, `co:MSG Networks`.
- **Link types:** merger, asset_deal, spin_off, holder_13d, awarded_by, peer_named, counterparty, customer, supplier, subsidiary, shared_director, same_theme.
- **Rule:** no source, no link. A guessed connection goes in a research note, labelled as a guess, not in this file.

The research run adds the day's links and lists each researched stock's neighbours. Whether linked names actually move after an event is measured in `research/domino/` (first test: [D1 results](../research/domino/RESULTS.md)).
