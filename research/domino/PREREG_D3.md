# D3: the funnel (filter the domino trades hard, then watch what actually happens)

Status: **sector list and filters written and committed on 2026-10-10, before any per-sector or per-filter return was looked at.** At the time of writing, the only D2 numbers seen were the totals, the drug/non-drug split and the China/HK split. The industry list below was built from trade **counts** only (`d3_sector_counts.csv`).

D2 bought every small linked stock: 30,659 takeable trades, and it lost after costs. Nobody can take that many trades and most of them were never worth taking. D3 filters them in stages and, instead of fixing a 5-day exit, **describes the whole path** so the exit can be chosen from what really happens.

This is **descriptive**. There is no pass mark, because choosing an exit from the same data and then calling it a result would be fitting. Whatever looks good here becomes a written rule that is then judged on new trades in the ledger.

## Starting point

Leader day: a stock with size of $20M a day or more closes up 20% or more (D2's primary). Followers: same 4-digit SIC, one tenth the leader's size or less, quiet on that day (own move below +10%, no runner flag for 3 days). Entry at the next open. No minimum size for followers.

## Stage 1: the continent test (industry)

The question asked of each industry, as if it were a continent on a map: **does the rest of the world rely on it and can't easily get it elsewhere, or is the rest of the world pouring money into it?** If neither, it is cut. A small stock in an industry nobody depends on has no reason to follow a big one.

**KEEP**

| Group | SIC codes | Why |
|---|---|---|
| Chips and computing hardware | 3674, 3672, 3670, 3679, 3559, 3571, 3572, 3576, 3577, 3661, 3663, 3669, 3825, 3827 | Every other industry runs on chips and compute, and the AI build-out is the biggest spending wave there is |
| Power and electrical equipment | 3620, 3621, 3690, 3443, 3585, 4911, 4931, 4924, 1623, 1731, 1600 | Electricity demand (data centres, electrification) is running into a grid that can't keep up; includes batteries, generators, reactors, cooling, grid construction |
| Energy | 1311, 1381, 1389, 3533 | The world runs on it |
| Mining and metals | 1000, 1040, 1090, 1220, 1400, 3312, 3330 | Critical minerals, uranium, copper, steel and monetary metals: governments are paying to secure supply |
| Defence and aerospace | 3721, 3760, 3812, 3480 | Re-armament and space budgets |
| Compute hosting and systems | 7374, 7373 | Data centres, AI compute, miners turning into hosts |
| Freight | 4412, 4400, 4213 | World trade moves on it |

**MAYBE** (reported separately, never added to the kept set): generic software (7370, 7371, 7372), general industrial machinery (3569, 3560, 3561, 3590), chemicals (2800, 2810, 2860, 2890), communication services (4899, 4812, 4813), engineering services (8711), special trade contractors (1700). The world uses these, but it is not clear the rest of the world is betting on their small stocks.

**CUT**: everything else. Drugs and biotech (each stock runs on its own trial), medical devices and labs (same reason), finance, shells and blank cheques, banks, insurers, property, retail, restaurants, consumer goods, vehicles, business services, health services, media, travel and education.

## Stage 2: takeable

Raw price of $1 or more and size of $250k a day or more (the ledger rule).

## Stage 3: does the company hold up

- Not headquartered in China or Hong Kong. (D2 found these lose, so on this data that part of the effect is already known; it is listed here so the funnel shows it.)
- No reverse split in the previous 90 days (a stock that just consolidated its shares is usually one that keeps issuing them).

## Stage 4: the follower is waking up

The follower's own volume on the leader's day is at least **5 times** its average of the previous 20 days, while its price is still quiet. (The runners study's strongest tell was a 5x volume day before the run.) A 2x version is shown next to it.

## What is described at every stage

- How many trades, how many different stocks, trades per year.
- From the entry at the open of the next day:
  - **day 1**: open to high (the best you could have done within hours), open to low, open to close;
  - the close after **2, 3, 5 and 10 days**;
  - the **best price reached** within 1, 3, 5 and 10 days, and the worst;
  - how often it reached **+20%, +50% and +100%** within 1, 3, 5 and 10 days;
  - **which day the best close fell on** (is this a one-day move or a slow one).
- The same numbers for size-matched controls from quiet industries, picked as in D2.
- Means and medians. A mean far above the median means lottery tickets.

## Limits

- Daily bars only: "within hours" is the day's high and low, not a minute-by-minute path, and the order of a high and a low on the same day is unknown.
- The industry judgement is one person's reading of 2024-2026. It was made blind to the returns, but it was made after two years in which chips, power and metals were obviously in favour. That hindsight is real and can't be removed.
- No untouched data. This describes; the ledger judges.
