# Rumour trades: results (run 14 Oct 2026, partial)

Plan: [PLAN.md](PLAN.md), written 13 Oct 2026 and not changed. Code: `run.py` (recomputes everything below from `reports.csv`, `search_log.csv` and `data/prices/`). Per-case numbers: `cases.csv`. Summary numbers: `results.json` and `run_output.txt`.

**Read this first.** The news search ran out of credits part-way through. Only the first month and half of the second were searched (13 Apr to 12 Jun 2026). Nothing from 13 Jun to 13 Oct was searched in the sweep. Everything below is about that partial sample.

## The two results

**1. All reports (13 cases with prices, 13 Apr to 12 Jun only).** Buying at the first close after the report and holding 20 trading days lost money after 1% costs.

- Average: **-1.7%**. Middle: **-2.0%**. 5 of 13 were up after costs.
- Against IWM over the same days (before costs): average -3.4%, middle -4.0%.
- Three more reports passed the filters but have no price data (Catalyst Pharmaceuticals, Amex GBT, Nuvalent). They are left out of these numbers. All three became signed deals.

**2. The narrow slice (named buyer, "advanced" wording, a price per share, stock 10% or more below it at the close).** One case has prices: **Payoneer**, **+10.0%** over 20 days after costs. Two more meet the first three tests but have no price data, so whether they were 10% below the price is [UNVERIFIED]: Amex GBT and Nuvalent.

## Pass or fail

**Too thin to judge.** The pass mark needs 10 narrow-slice cases with a middle and average above zero after costs. There is 1 (3 at most, if both unpriced cases qualified). The one case was positive, but one case says nothing.

On the plan's own terms the pass mark is not met. I have not treated this as the plan's "fail, drop the idea", because only 15 of the 60 planned searches ran (10 of the 30 month-and-phrase pairs), and the last four months were never searched. Finishing the test needs the 45 searches marked "NOT RUN" in `search_log.csv`, run the same way once the credits are back, then `python run.py --write-status` again.

## Every narrow-slice case

Prices are Yahoo daily bars. "Close to next open", "close to close" as labelled. Returns are before costs; take 1 point off each for the 1% round trip.

| | Payoneer (PAYO) | Amex GBT (GBTG) | Nuvalent (NUVL) |
|---|---|---|---|
| Report time (ET), outlet | 9 Jun 2026 10:22, Reuters | 4 May 2026 07:23, Bloomberg | 8 Jun 2026 23:19, FT |
| Buyer, wording | Nuvei, "advanced talks" | Long Lake, "advanced talks" | GSK, "nears deal" (wire headline) |
| Price or value in the report | $2.7bn including cash | about $9.50 a share | $9bn to $10bn ($9bn used) |
| Shares, net debt (latest 10-Q) | 334,778,664; -$339.4m (net cash) | n/a | 78,997,915; -$1,287.5m (net cash) |
| Price per share: equity reading | $8.07 | $9.50 | $113.93 |
| Price per share: including-debt reading | $9.08 | $9.50 | $130.22 |
| Close before report | $5.14 (8 Jun) | [UNVERIFIED] | [UNVERIFIED] |
| Entry close (report day) | $6.39 (9 Jun) | [UNVERIFIED] | [UNVERIFIED] |
| Entry close against lower price reading | -20.8% (in the slice) | [UNVERIFIED] | [UNVERIFIED] |
| Close to next open | +0.9% (IWM -0.2%) | | |
| Close to close, 5 days | +9.9% (IWM +2.5%) | | |
| Close to close, 20 days | +11.0% (IWM +4.3%) | | |
| Close to close, day after signing (16 Jun) | +9.9% (IWM +2.5%) | | |
| Worst daily low within 20 days | -1.1% | | |
| Signed deal | 15 Jun, $7.40 cash (6 days later) | 4 May, $9.50 cash (same day) | 9 Jun, $124.00 cash tender (next day) |

Both had a signed deal announced on the entry day itself (the 8-K was filed that day; Nuvalent's before the close). A close bought after an announcement sits near the deal price, so neither is likely to have been 10% below it. That is an inference, not a fetched price.

## Monthly hit counts

A "hit" is a distinct story of takeover talks, a sale being explored, or takeover interest, found in the search results. Announced deals, lawsuits, IPOs and fundraisings are not hits. In the first month each phrase ran in both forms (bare and in a sentence); in the second month only the sentence form ran (see Deviations).

| Month (ET dates) | Searches planned | Searches run | Documents returned | Hits | Pass the manual filters | Kept, with prices | Kept, no prices |
|---|---|---|---|---|---|---|---|
| 13 Apr to 12 May | 10 | 10 | 491 | 85 | 8 | 6 | 2 |
| 13 May to 12 Jun | 10 | 5 | 376 | 62 | 8 | 7 | 1 |
| 13 Jun to 12 Jul | 10 | 0 | not searched | | | | |
| 13 Jul to 12 Aug | 10 | 0 | not searched | | | | |
| 13 Aug to 12 Sep | 10 | 0 | not searched | | | | |
| 13 Sep to 13 Oct | 10 | 0 | not searched | | | | |

Documents overlap between searches. Six more hits came only from test searches run before the sweep; they are listed in `reports.csv` (window "CAL") and are not in the sample. Bumble, the case that started this, is one of them: it falls in the last month, which was not searched.

Of the 147 hits in the two months, 131 were dropped: 36 not US-listed, 32 private targets, 26 business units or assets, 12 non-US company statements, and 25 for other reasons (outlet not WSJ/Bloomberg/Reuters/FT, not the first report, a public proposal came first, merger of equals, speculative articles). The reason for each is in `reports.csv`.

## Deviations

1. **The search stopped early (the main gap).** Bigdata credits ran out on 14 Oct 2026 after the last successful search (12:18 UTC). Completed: 13 Apr to 12 May, all 5 phrases in both forms (10 searches); 13 May to 12 Jun, all 5 phrases in the sentence form only (5 searches). Not run: the bare-phrase form for 13 May to 12 Jun (5 searches) and every search for 13 Jun to 13 Oct (40 searches). Per instruction, no other news source was used to fill the gap. Before that instruction arrived I tried two stand-ins: GDELT answered a few test queries and then rate-limited every request, and web search could not filter by date. No result from either is used.
2. **Phrase form.** The bare phrases returned mostly unrelated results. For example, "in talks to be taken private" for 13 Apr to 12 May returned 5 documents, none about deals, and an exact-match filter on it returned none. So each phrase was also run inside one fixed sentence, the same every month: "The company is in talks to be taken private, according to people familiar with the matter" (and likewise for the others). Both forms were run where credits allowed. The wording of each query is in `search_log.csv`.
3. **Month boundaries.** Months run from the 13th to the 12th in New York time (04:00 UTC boundaries), with the last month ending 13 Oct. Search settings: fast mode, news only, up to 100 text chunks per search, which gave 5 to 97 documents per search. A busy month can lose stories to that cap.
4. **Test searches.** Five test searches were run before the sweep to check the method. Their extra finds are in `reports.csv` as excluded, with the reason.
5. **Missing prices.** Yahoo returns nothing for Catalyst Pharmaceuticals (delisted 15 Jul), only bars from 29 Jul for Amex GBT, and one bar for Nuvalent. No other price source was used (one alternative showed a bot check, which I did not try to pass). These three are kept in `reports.csv` as "kept, no price data" and are left out of every return figure. All three were signed deals, so leaving them out may understate results.
6. **Report time.** The report time is the earliest item in the search results that names the outlet (for example "Bloomberg reported"). The outlet's own story may have been earlier. For Globalstar the earliest such item is 00:25 ET on 14 Apr, so the Bloomberg story was probably the evening before; the entry day (14 Apr) is the same either way.
7. **First report.** No company-name searches were run, as instructed. A report was ruled "not first" only when its own text showed earlier talks or an earlier public proposal (Papa John's, Caesars, MarineMax, Alkami). Some kept reports may still not be the first [UNVERIFIED].
8. **Wording.** The plan has three labels. I used: "advanced" for advanced, near, nearing, close to a deal, exclusive or final talks; "early" for early or preliminary talks, unqualified "in talks" or "in discussions", and preparing an offer; "exploring" for exploring, weighing, considering or studying a sale or targets. Dominion ("in discussions", deal "as soon as Monday") is "early". Nuvalent is "advanced" on the wire headline "Nears Deal".
9. **What counts as a takeover target.** Talks to combine two peers with no buyer or target named (Patrick/LCI, AvalonBay/Equity Residential) were left out. So were sales of business units. A controlling family's stake sale (Manchester United) and a US-listed ADS of a foreign company (Woodside, NYSE) were kept.
10. **Two price readings.** When only a value is given, both readings are worked out and the lower one is used for the 10% test, so the gap must hold under both. Net debt = borrowings (excluding leases) minus cash and short-term marketable securities, from the same 10-Q as the share count. For Nuvalent the low end of the $9bn to $10bn range was used.
11. **Exit and worst point.** "Day after signing" = the close on the first trading day after the day the signed deal was announced, if that is within 60 trading days of entry; otherwise the close 60 trading days after entry. The signing date used is the announcement date; the agreements are often dated a day or two earlier (noted in `reports.csv`). "Worst point" = the lowest daily low in the 20 trading days after entry, against the entry close.
12. **Filters and prices.** "$1 or more" uses the close before the report. "$250k a day" uses the average of close times volume over the 20 sessions before the entry day. Prices are unadjusted, so dividends are ignored. Data runs to the 13 Oct close.
13. **Listing and outcomes.** `company_tickers.json` lists only current tickers, so Catalyst, Amex GBT and Nuvalent are missing from it; their listing was confirmed from EDGAR filings instead (Nasdaq or NYSE delisting forms filed after the report). Outcomes come from each target's 8-K Item 1.01 or tender filings. For Woodside and Manchester United (foreign filers) only the filing index was checked, not the 6-K exhibits, so "no deal" for them is [UNVERIFIED].
14. **Saved search output.** Five searches came back too small to be saved to file. Their document counts are in `search_log.csv`, but their document lists are not in `search_results.csv`.

## Known weaknesses

- The sample is tiny: 13 cases with prices, 1 in the slice.
- News search favours stories that came true. 7 of the 16 reports that passed the filters had a signed deal within 30 days and 8 within 90.
- Buying at the close often means buying the announced deal, not the rumour. Globalstar, Amex GBT, Dominion and Nuvalent all filed a signed-deal 8-K on the entry day itself. Globalstar's and Nuvalent's were filed before the close; for Amex GBT and Dominion the time of the announcement against the close was not checked.
- Much of the move is gone by the entry close. From the close before the report to the entry close, the 13 priced cases rose 8.7% on average (middle 9.0%).
- Two months is one market mood. IWM rose over most of the 20-day windows.
- The first minutes after a report cannot be traded from the UK reliably, so the entry is the close.
- Every hit was classified by hand by one reader, with no second check.

## Appendix: every report that passed the filters

Returns are before costs. IWM column is the same 20 days.

| Hit | Ticker | Report (ET) | Outlet | Buyer named | Wording | Close before | Entry close | Close before to entry | Close to next open | 5 days | 20 days | IWM 20 days | Exit | Worst low, 20 days | Signed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W1-002 | GSAT | 14 Apr 00:25 | Bloomberg | Y (Amazon) | advanced | $72.89 | $79.91 | +9.6% | -0.0% | +0.6% | +3.5% | +5.2% | +0.9% (day after signing) | -0.6% | 14 Apr: $90.00 cash or stock election |
| W1-014 | TMUS | 21 Apr 14:07 | Bloomberg | Y (Deutsche Telekom) | exploring | $198.36 | $195.39 | -1.5% | -1.4% | -4.4% | -1.0% | -0.6% | -1.5% (day 60) | -6.8% | no |
| W1-021 | IHRT | 24 Apr 16:31 | Bloomberg | Y (Sirius XM) | early | $5.42 | $5.25 | -3.1% | -0.4% | +17.1% | -6.5% | +4.8% | -30.5% (day 60) | -16.2% | no |
| W1-024 | CPRX | 27 Apr 12:52 | Bloomberg | Y (Angelini Pharma) | early | [UNVERIFIED] | [UNVERIFIED] | | | | | | | | 7 May: $31.50 cash |
| W1-037 | EBAY | 1 May 17:26 | WSJ | Y (GameStop) | early | $104.07 | $109.33 | +5.1% | -1.7% | -1.1% | -0.4% | +5.0% | +3.8% (day 60) | -4.3% | no |
| W1-039 | GBTG | 4 May 07:23 | Bloomberg | Y (Long Lake) | advanced | [UNVERIFIED] | [UNVERIFIED] | | | | | | | | 4 May: $9.50 cash |
| W1-058 | MFIC | 10 May 20:47 | WSJ | N | early | $11.68 | $11.10 | -5.0% | +0.5% | -3.4% | -6.8% | -0.1% | -12.5% (day 60) | -7.9% | no |
| W1-061 | WEN | 12 May 00:40 | FT | Y (Trian) | early | $6.76 | $7.90 | +16.9% | +3.2% | +2.8% | -16.1% | -0.2% | -2.7% (day 60) | -17.3% | no |
| W2-008 | D | 17 May 12:08 | Bloomberg | Y (NextEra) | early | $61.73 | $67.56 | +9.4% | -0.5% | -0.4% | +1.4% | +5.8% | +0.8% (day after signing) | -4.5% | 18 May: 0.8138 NextEra shares plus a share of $360m cash |
| W2-015 | IMAX | 21 May 17:16 | WSJ | N | exploring | $33.88 | $39.12 | +15.5% | +0.4% | +3.5% | +15.0% | +3.6% | +37.3% (day 60) | -1.4% | no |
| W2-018 | LNTH | 22 May 15:58 | Bloomberg | Y (Curium) | exploring | $94.47 | $103.00 | +9.0% | -0.3% | -5.7% | +2.9% | +3.6% | -1.5% (day after signing) | -7.8% | 4 Aug: $102.50 cash plus CVR up to $12.00 |
| W2-026 | MANU | 4 Jun 09:41 | Bloomberg | N | exploring | $21.11 | $22.62 | +7.2% | -0.8% | +4.0% | -1.6% | +2.4% | -3.8% (day 60) | -7.2% | no [UNVERIFIED] |
| W2-030 | NUVL | 8 Jun 23:19 | FT | Y (GSK) | advanced | [UNVERIFIED] | [UNVERIFIED] | | | | | | | | 9 Jun: $124.00 cash tender |
| W2-032 | PAYO | 9 Jun 10:22 | Reuters | Y (Nuvei) | advanced | $5.14 | $6.39 | +24.3% | +0.9% | +9.9% | +11.0% | +4.3% | +9.9% (day after signing) | -1.1% | 15 Jun: $7.40 cash |
| W2-039 | WDS | 12 Jun 11:14 | Bloomberg | Y (Exxon Mobil) | exploring | $21.73 | $23.07 | +6.2% | -7.9% | -12.2% | -8.8% | +0.5% | +4.9% (day 60) | -18.5% | no [UNVERIFIED] |
| W2-042 | ROKU | 12 Jun 15:13 | Bloomberg | N | early | $119.64 | $143.66 | +20.1% | +0.2% | -5.9% | -1.3% | +0.5% | -4.0% (day after signing) | -6.5% | 15 Jun: 0.9693 Fox Class A shares plus $96.00 cash |

All times are 2026. Lantheus was also "exploring", so it is not in the slice; its entry close was 3.2% below the lower price reading ($106.41), short of the 10% test in any case.

## Sources

Reports (Bigdata.com documents): [GSAT](https://app.bigdata.com/documents/170BCF5803923C94FB63D24C7BF76927), [TMUS](https://app.bigdata.com/documents/5A8E32EE7FE9C5ABEE75E752F5055C8E), [IHRT](https://app.bigdata.com/documents/55BECD78DAD85E87119CF7B28D422F16), [CPRX](https://app.bigdata.com/documents/AB4319D20FE35AB5ECF555B58571BEA7), [EBAY](https://app.bigdata.com/documents/965220C6DEA1DAC83C54D7B30994299A), [GBTG](https://app.bigdata.com/documents/3B970CB43882A0B9C3B79158736A6AC6), [MFIC](https://app.bigdata.com/documents/BA129EA1202AC9719180139A05285D79), [WEN](https://app.bigdata.com/documents/9248A13C62AAB827310E9EB130F94CE1), [D](https://app.bigdata.com/documents/8F005A80682E2B4DE296E096DCBEC494), [IMAX](https://app.bigdata.com/documents/F314E20FCCC8642ACFBC14CE076B9149), [LNTH](https://app.bigdata.com/documents/4ADD95C9C0E07A3C3F8D7F6269E8663E), [MANU](https://app.bigdata.com/documents/716A5BB71488A61D97657B7660DF7E78), [NUVL](https://app.bigdata.com/documents/591AC014ACF9E4C320B1F75135AFC02C), [PAYO](https://app.bigdata.com/documents/CDCE277574799175CA8450A675C49F76), [WDS](https://app.bigdata.com/documents/8506740F4617028A68742167042D6143), [ROKU](https://app.bigdata.com/documents/93F4C5B0EF7BA10F594D682A3DB17806).

Signed deals (8-K Item 1.01): [Globalstar](https://www.sec.gov/Archives/edgar/data/1366868/000114036126014528/ef20070409_8k.htm), [Catalyst](https://www.sec.gov/Archives/edgar/data/1369568/000119312526210518/d90722d8k.htm), [Amex GBT](https://www.sec.gov/Archives/edgar/data/1820872/000114036126018699/ef20072315_form8k.htm), [Dominion](https://www.sec.gov/Archives/edgar/data/715957/000119312526227930/d158175d8k.htm), [Lantheus](https://www.sec.gov/Archives/edgar/data/1521036/000119312526331138/d167446d8k.htm), [Nuvalent](https://www.sec.gov/Archives/edgar/data/1861560/000119312526262950/d137459d8k.htm), [Payoneer](https://www.sec.gov/Archives/edgar/data/1845815/000095010326008945/dp248400_8k.htm), [Roku](https://www.sec.gov/Archives/edgar/data/1428439/000114036126025115/ef20076172_8k.htm).

Share counts and net debt: [Payoneer 10-Q](https://www.sec.gov/Archives/edgar/data/1845815/000110465926057109/payo-20260331x10q.htm), [Nuvalent 10-Q](https://www.sec.gov/Archives/edgar/data/1861560/000186156026000021/nuvl-20260331.htm), [Lantheus XBRL](https://data.sec.gov/api/xbrl/companyfacts/CIK0001521036.json) (10-Q 0001193125-26-210373). Filing lists for every kept target are saved in `data/sec/`. Prices: Yahoo chart API, saved in `data/prices/`.
