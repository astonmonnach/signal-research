# Share overhang: buy after a big registered sale is absorbed
Stage: IDEA · Created: 2026-09-30

- **Who is selling:** pre-IPO holders and insiders once a lock-up ends or a resale registration (S-1/S-3) goes effective.
- **Why they're forced:** they aren't strictly forced. Their reasons are liquidity and fund-life deadlines, and prices are held down while everyone knows the supply is coming.
- **Evidence:** Field & Hanka (2001), *Journal of Finance*: abnormal price falls around lock-up expiry. Whether the price recovers *after* the supply clears is what we need to test.
- **Trigger:** `scan_market.py` sections for S-1, EFFECT and 424B4. Lock-up dates are in the 424B4.
- **Open question before BACKTEST:** is the edge in avoiding these stocks before the supply hits, or in buying after it's absorbed? A cash account can only use the second.
- First case: HMH (resale S-1 for 31.9M shares filed 28 Sep 2026; −8% the next day).
