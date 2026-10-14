# IC1 pre-registration: does following insider cluster buying pay?

Written 14 Oct 2026, before any of this was computed. Committed before the run. It tests the trigger in `RULES.md` (stage IDEA since 30 Sep 2026), which has never been tested.

## Why
The trader wants a filter that finds stocks where insiders are buying with their own money, then follows them. Form 4 filings make insider trades public within two business days. Published research (Lakonishok and Lee 2001; Cohen, Malloy and Pomorski 2012) says open-market purchases predict returns, most of all in small companies, and that routine trades carry no signal.

## Data
- **Insider trades:** the SEC Insider Transactions Data Sets, quarters 2024Q4 to 2026Q1 (filings from 1 Oct 2024 to 31 Mar 2026), from https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets. 2026Q2 and later are not published yet.
- **Prices:** `research/runners/work/panel.npz` (US common stocks, split-adjusted, to 30 Sep 2026), so every signal has at least 60 sessions of prices after it.
- **Share counts:** `research/runners/work/sec/shares` (dei shares outstanding).

## Definitions
- **Insider buy:** a non-derivative transaction with code P (open-market or private purchase), acquired, by a reporting owner who is a director, an officer or a 10% owner. Trades marked as made under a pre-arranged 10b5-1 plan are left out.
- **Cluster signal:** two or more different reporting owners buy the same issuer within 30 calendar days. The signal date is the filing date of the Form 4 that brings in the second buyer, because that is when the public could know.
- **Entry:** the open of the first session after the signal date. One signal per issuer per 60 sessions; later clusters inside that window are ignored.
- **Takeable:** a prior close of $1 or more and a median dollar volume of $250k or more over the 20 sessions before entry. Only takeable signals are tested.
- **Exits:** the close 20 and 60 sessions after entry. A stock that stops trading is marked at its last close and flagged. Returns above +300% count as +300%.
- **Costs:** 1% per round trip.
- **Controls:** for each signal, up to 10 takeable common stocks with no insider buy in the 90 days before, with a prior 20-day median dollar volume between half and twice the signal stock's. They are picked with a seed fixed by the date and held over the same days.
- **Market value:** shares outstanding (latest filed before entry, split-adjusted, within 15 months) times the prior close.
- **Cluster size:** the total dollar value of the purchases in the cluster up to the signal date.

## Tests (three trials; nothing else is tested)
- **T1 (does the cluster filter pay?):** the 60-session return after costs minus the controls' average. It **pays** only if the mean is above zero with a day-clustered bootstrap 95% interval above zero, the median is above zero, and the sign is the same in both halves (signals from 1 Oct 2024 to 30 Jun 2025, and from 1 Jul 2025 to 31 Mar 2026).
- **T2 (are small companies stronger?):** within T1's signals, the excess return of market value under $300M minus $300M or more. It **separates** if the interval of the difference is above zero.
- **T3 (do bigger clusters carry more signal?):** within T1's signals, the excess return of clusters worth $250k or more minus smaller ones. It **separates** if the interval is above zero.
- **Bootstrap:** resample whole signal days, 2,000 draws, seed 20261014.

## Description only (never promoted to a result)
The 20-session horizon; single-insider buys that never became clusters; buys by chief executives and finance chiefs; buys by 10% owners; the next-close entry; how many signals there are a month.

## What would change things
Any change to a definition, threshold or test after a result is seen is a new, separately named study (IC2).
