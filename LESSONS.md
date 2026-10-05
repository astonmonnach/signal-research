# Lessons: every miss, the rule it created, and where the rule is enforced

When the research misses something, the miss goes here with the rule it produced. A rule only counts once it's
**enforced**: in code (it runs every day), in the [nth skill](.claude/skills/nth-order/SKILL.md) (every analysis),
or in a dated [ledger rule](ledger/RULES.md) (the scoring). Old ledger rows keep the rule they were recorded under.

| date | what we missed or got wrong | rule | enforced in | status |
|---|---|---|---|---|
| 2026-10-04 | MTUS's $125M funded order was in a **PR Newswire release, not an 8-K**, so "no orders, just a ceiling" nearly became the thesis | Read the company's own press releases for 5 days after any event, from trusted wires only | Code: `collectors/press_wires.py` (49 feeds, every 20 min, matched to the watchlist). Skill rule 1 | done |
| 2026-10-04 | ELMT read as "story, not dollars". Its 8-K also closed a **$200M DoW preferred-equity** purchase | Same buyer, same day: find the siblings and read *their* filings, not just their headline | Skill rule 3 | done (manual check) |
| 2026-10-04 | KNRX "+306% before we found it" was wrong: the pre-move window included the found day | Pre-move = the 5 sessions before the found day; the found-day move is reported separately | Code: `ledger/build_ledger.py` (`pre_move_5d`, `found_day_move`) | done |
| 2026-10-04 | LWLG "strategic review" was a new director's bio line | An Item 5.02 8-K without 8.01/1.01/2.01 is a `bio-mention`, not a review | Code: `watch/scan_market.py` + `ledger/build_ledger.py`. Ledger rule 2026-10-04 | done |
| 2026-10-04 | MOD showed "+14.9%" and CTVA "−85%": spin-off reference-price artefacts. THRM's −8% was mostly a $2.07 dividend | Add back cash and spun-off shares before judging any move | Code: `ledger/corporate_actions.csv`, used by the ledger, reports, recaps and long-term tracking | done |
| 2026-10-04 | RYAM's −23% read as "contagion from Mercer", which was inferred, not proven | Contagion runs through peers and credit, but label it an inference until a filing shows it | Skill rule 4 | done (manual check) |
| 2026-10-05 | GOVX and HCTI were logged as setups while they already had **delisting determinations**; GWH was suspended | Check exchange status before logging a setup | Skill rule 10. Recap shows each setup's latest 8-Ks as links | partly: no automatic exchange-status check yet |
| 2026-10-05 | HCTI's "EFFECT" was a **POS AM**: no new shares | An EFFECT notice names the form it makes effective; POS AM, F-6, N-2 and S-4/F-4 are not supply | Code: `watch/scan_market.py` tags `(not supply: ...)`, `ledger/build_ledger.py` skips it. Ledger rule 2026-10-05 | done |
| 2026-10-05 | CHDN's "strategic alternatives" 8-K was a **refinancing** (forward-looking boilerplate) | A strategic phrase in a debt-financing 8-K (Item 2.03 without 8.01/2.01) is a `financing-mention` | Code: `watch/scan_market.py` + `ledger/build_ledger.py`. Ledger rule 2026-10-05 | done |
| 2026-10-05 | The National Defense Stockpile pot was counted as **~$4.0bn of ceilings from one month of awards**. USAspending showed 21 more IDIQs: **~$9.3bn of ceilings against $2bn**, and **69% of the money already ordered** | For a capped fund, total EVERY award from the same office since the money started, not this month's batch | Code: `collectors/funding_pot.py` (daily, `watch/pots/`; shown next to MTUS and ELMT in Discord and in the briefing). Skill rule 6 | done |
| 2026-10-05 | A personal note (account funding) sat in the public calendar | The calendar is stock events only, no emojis | The evening task's calendar instructions; `calendar/catalyst-dates.ics` cleaned | done |
| 2026-10-05 | Long-term research ran before the long-term gates existed (AAON passed as "watch" but fails LT2) | Long-term ideas go through LT1–LT6; a failure of LT2 or LT3 is a kill | Skill v3, `longterm/METHOD.md` | done |
| 2026-10-05 | The ledger headline said "61/94 beat IWM, +5.0%", but 68 of the 94 were **short bets we can't take** (KNRX and WHLR "won" by collapsing). The takeable part was flat: 6/16 after costs, none held long enough to judge | The headline counts only what we could have taken: long, liquid, $1+, net of 1% costs, judged after 20 trading days. Shorts are a paper-only don't-buy list | Code: `ledger/build_ledger.py` (`takeable`, `net_excess_pct`, `tdays`), the briefing's #ledger post and the weekly reports. Ledger rule 2026-10-05 | done |

## Still to automate

- **Exchange status before logging a setup:** search the company's 8-Ks for Item 3.01 "delisting determination" or suspension, and its 25-NSE filings, before a setup is logged.
- **Siblings:** for each DoD award to a watchlist stock, list every other award on the same day's DoD page from the same contracting office.
