---
name: nth-order
description: (v3, 2026-10-05; long-term gates LT1–LT6) Turn a headline, event, filing, claim, or URL into a grounded four-rung nth-order analysis — what is it → what it actually means → who's affected (winners/losers) → what it could mean next — output as a postable, theme-aware HTML artifact with real charts. Use when the user hands over something to analyse "properly / deeper" or wants a share-ready take. Every rung must cite fetched evidence, not recall.
---

# nth-order analysis

Shallow takes stop at the first true thing. This runs a fixed ladder that goes
one order deeper at each rung, and — the whole point — **grounds every rung in
fetched evidence** so it comes out proper, not a horoscope with structure.

## The one rule that makes it real

A model reasoning through four lenses from its own head produces confident,
plausible, *made-up* filler — especially at rungs 3 and 4. So:

- **Rung 1 is retrieval from the PRIMARY SOURCE — never recall, never a summary.**
  A news article or search snippet is a *pointer* to the source, not the source.
  If a company is involved, open its actual filing (10-K / 10-Q / 8-K on SEC) and
  read the real figure out of it. Never build on a number you only saw in a
  summary. Stopping at the news is the lazy failure this skill exists to prevent.
- **Never chart a number you can't trace to a primary source.** If a figure isn't
  disclosed, it does **not** get a bar — it gets a "not disclosed in [source]"
  marker. Estimating an undisclosed number onto a chart is the cardinal sin: it's
  the mistake that gets a post torn apart with *"that's not even in their 10-K."*
- **Absence is a finding.** Verify the headline claim against the primary source,
  *including the negative*. If the exciting claim — a monopoly, a contract, a
  segment, a "sole supplier" line — isn't in the filing, that absence IS the
  finding. Report it plainly; often it's the most valuable thing you'll surface.
- **For a tradeable name, check it hasn't already run before writing it up.**
  An already-discovered, already-priced idea has no edge left. Clean structure is
  never a reason to skip this — say "already run" up front, or don't write it up.
- **Rungs 3 and 4 must name real entities and real precedents.** A "winner" is a
  named company/sector you can point at. A "near-future" claim is anchored to a
  cited precedent or a dated catalyst — never a vibe. If you can't ground it, drop it.

This skeptic layer *is* the product. A right answer beats a clean-looking wrong one.

### Before publishing — the not-lazy checklist
- Did I open the **actual filing**, or did I stop at a summary?
- Does **every number on every chart** trace to a primary source in the footer?
- If it's a ticker: did I check whether the thesis has **already run**?
- Did I report what the source does **not** say, not just what it does?

Fail any one of these and it is not finished. These are the exact checks that
caught this skill being lazy — an already-run name written up as fresh, and an
undisclosed number charted as if it were real. Run them every time.

## Go deeper on every branch (v2, added 2026-10-05 from the MTUS / ELMT / KNRX / RYAM work)

These rules exist because each one caught a mistake that a clean-looking analysis made:

1. **Press releases, not just filings.** Check the company's own release (wire or IR page)
   for the 5 days after any event. MTUS's $125M initial DLA delivery order was in a PRNewswire
   release, not an 8-K. Missing it nearly made "no orders, just a ceiling" the thesis.
   Use only trusted primary wires (GlobeNewswire, PR Newswire, Business Wire, company IR).
   News articles are pointers, not sources. Paid promo pieces ("4 Explosive Stories…") are
   a *signal of promotion*, never evidence.
2. **The spread, not the return.** Measure every price reaction against a control: the sector
   ETF, IWM, and one matched peer of the same size and sector. MTUS looked "dead" in absolute
   terms but was +5 points against the controls while steel sold off. Label moves exactly:
   close-to-close is not open-to-close. Verify pasted or second-hand numbers before using them.
3. **Same buyer, same day: find the siblings.** When an award, order or rule change hits one
   company, search for every other company hit by the same source. The same DLA stockpile
   office gave ELMT a $2B tungsten IDIQ (+33% day) while MTUS got $995M (+2%). First read was
   "story, not dollars". That was WRONG: ELMT's 14 Sep 8-K also closed a $200M Department of War
   preferred-equity purchase (up to $450M, warrants for 24.84% of the common), and the IDIQ has a
   $150M guaranteed minimum. Siblings tell you what is priced, but only after you've read
   *their* filings too, not just their headline.
4. **Contagion runs through peers and credit.** When a stock falls with no news, check its
   closest peers first. RYAM's −23% was Mercer (MERC) skipping a $25.8M interest payment
   (Fitch CCC−) in the same weak pulp market. Leverage turns a peer's default into your risk.
5. **Tie the theme to its input price.** Steel contract → HRC steel futures and SLX. Gold or
   silver → GC/SI. Chips → SOXX plus the metals they consume. Say so when no free price exists
   (tungsten, antimony, HF-1), and never invent a proxy price.
6. **Follow the money behind the contract.** A ceiling is not an order (IDIQ, no minimum).
   Find the funded order, and check whether the pot is oversubscribed: the NDS fund got $2B
   (Public Law 119-21 §20004(a)(40), available to Sep 2029), but September's stockpile ceilings
   alone totalled about $4.0B (ELMT $2B + $36M, MTUS $995M, Rio Tinto $995M aluminium), and that was
   still too small: USAspending shows 21 more stockpile IDIQs from Aug 2025 to Jul 2026 ($6.29B of
   ceilings; ≈$9.3B in all) and ≈$1.1B already ordered in FY2026. Read the whole DoD page, AND search
   USAspending for every award from the same office (here `SP8000`) across the whole funding period,
   not just this month's batch. Appropriations decide what gets ordered. Automated for capped funds by
   `collectors/funding_pot.py` (add the office to `watch/pots.json`); every miss and its rule go in `LESSONS.md`.
7. **Corporate actions fake moves.** Spin-offs, reverse-Morris-trusts and special dividends
   make broker "% change" numbers wrong (MOD showed "+14.9%" when the real move was +2%,
   CTVA showed −85%). Add back what holders received before judging any move.
8. **Before calling it an opportunity:** check the move *before* it was found, the move *on*
   the found day, and liquidity (average daily $ volume ≥ $250k, or flag it untradeable).
   KNRX's +305% happened on the found day itself, not before it.
9. **Supply + deficiency = promotion risk.** Fresh S-1/F-1 or EFFECT notices plus an exchange
   deficiency (8-K Item 3.01) plus a sub-$1 price is the KNRX pattern. It is a *don't-buy*
   flag (dilution or promo-spike-then-collapse), not a long setup.
10. **Keyword hits are not events.** A "strategic alternatives" phrase in a director's bio
    (Item 5.02) is not a strategic review (LWLG), nor is it in a refinancing's forward-looking
    boilerplate (CHDN, 28 Sep). A post-effective amendment (POS AM) "EFFECT" adds no new
    shares (HCTI). Check exchange status before logging a setup: GOVX and HCTI already had
    delisting determinations. Read the item codes and the actual text before trusting a scan.
    The scanner now tags `bio-mention`, `financing-mention` and EFFECTs that are `(not supply: ...)`
    (POS AM, F-6, N-2, S-4/F-4), and the ledger skips them (ledger/RULES.md, 2026-10-05).
11. **Score and log it.** Apply the METHOD gates G1–G5 and the 0–10 card
    (Desktop/nth-order-pipeline/METHOD.md). Log the call with a control ticker in
    `ledger/` so it gets marked against the market from the next session's open.
    Kills get logged too.

### Updated not-lazy checklist (all of these, every time)
- Primary filing **and** the company's own press release opened?
- Reaction measured against sector ETF + IWM + a matched peer, with move types labelled?
- Siblings (same buyer or event) and peers (contagion) checked?
- Input commodity named, with its price (or "no free price")?
- Funded order vs ceiling, and is the money pot oversubscribed?
- Corporate actions added back?
- Pre-move, found-day move and liquidity checked?
- Gates and score recorded, and logged in the ledger with a control?
- Long-term idea? LT1–LT6 checked and recorded, and the verdict is one of candidate / watch / already run / kill?

## Long-term mode: gates LT1–LT6 (v3, added 2026-10-05)

Use this mode when the horizon is 6–36 months (the `longterm/` section and the #long-term channel).
It keeps everything above, including gates G1–G5 and the 0–10 card, and adds six gates. A long hold
is exposed to things a two-week trade isn't: dilution, refinancing, a theme that never reaches the
income statement, or paying a price that already assumes success.

| Gate | Passes when | Source |
|---|---|---|
| **LT1 In the numbers** | The theme shows up in **reported** segment revenue, backlog/RPO or a funded order. An article, a CEO quote or a ceiling isn't enough. | Latest 10-K / 10-Q / 8-K, or the company's own release |
| **LT2 Survives two bad years** | Cash plus undrawn credit covers the next big maturity and two years of negative free cash flow (or FCF is positive). | Latest 10-Q balance sheet, debt note, cash-flow statement |
| **LT3 Dilution** | The diluted share count grew under ~3% a year over 3 years, with no live equity line or at-the-market programme doing the funding. | SEC companyfacts XBRL, S-3/424B filings |
| **LT4 Not already run** | The 1-year and 3-year moves against SPY plus the valuation (EV/sales or P/E) against its own 5-year range and two peers leave room. A real but fully priced theme gets **"already run"**, not a pass. | Yahoo closes, filings for EV |
| **LT5 Liquidity** | Average daily $ volume of $5M or more (large and mid caps preferred). Anything smaller is flagged. | Yahoo volume × price |
| **LT6 Benchmark** | It is measured against **SPY** and its sector ETF from the day it's added, and the thesis states what would make it beat both. | `longterm/build_longterm.py` |

**Verdicts in this mode:**
- **long-term candidate:** score ≥8 and every gate passes.
- **watch:** 5–7, or one of LT1/LT4 not yet met, each with a dated review trigger.
- **already run:** fails LT4.
- **kill:** any failed G-gate, or a failure of LT2 or LT3.

A candidate becomes a public call (`horizon = long`, benchmark SPY, review about 12 months out, a
stated thesis-break exit) only when the user says yes. Log candidates in `longterm/candidates.csv`.

## The ladder

1. **What is it** — the fact. Fetch it. State it in 2–3 sentences with the key
   verified numbers and who/what/when. Cite.
2. **What does it actually mean** — interpretation. What changed, what it signals,
   why now. Pull one or two comparables/definitions to ground it.
3. **Who's positively and negatively affected**: named winners and losers (including same-buyer siblings, peers hit by contagion, and input-commodity producers), each
   with a one-line *why*, each scored −5…+5 for the impact chart. Group where
   sensible (e.g. "private-credit managers"), but keep them concrete.
4. **What could this mean in the near future** — 2–3 scenarios (bull / base /
   bear or similar), each **anchored to a precedent or a dated catalyst**, plus a
   short "signals to watch" list. Honest forks, not a single confident prediction.

## Charts (use the `dataviz` skill before writing any chart code)

Default two, each doing a different job:

- **Winners/losers impact bar (flagship — rung 3).** Diverging horizontal bars,
  entities sorted most-positive to most-negative. **blue = positive, red =
  negative, gray zero-line.** Direct value labels (never color alone).
- **A grounded context chart (rung 1/2).** A magnitude bar that puts the headline
  number in scale against real, fetched comparators — the "sleeper stat" that
  teaches the reader something. Single magnitude job → one hue, or two categories
  (the new thing vs. the reference set) with a legend.

Skip a chart rather than invent data for it. A qualitative rung with no real
numbers stays prose.

### Palette tokens (validated reference set — use as-is, both themes)
```
              light      dark
text-primary  #0b0b0b    #ffffff
text-second   #52514e    #c3c2b7
muted         #898781    #898781
surface-1     #fcfcfb    #1a1a19
page          #f9f9f7    #0d0d0d
grid          #e1e0d9    #2c2c2a
baseline      #c3c2b7    #383835
positive/blue #2a78d6    #3987e5
negative/red  #e34948    #e66767
zero-gray     #f0efec    #383835
series-2/orng #eb6834    #d95926
border        rgba(11,11,11,.10)   rgba(255,255,255,.10)
```
Define these as CSS custom properties under `:root` (light), an
`@media (prefers-color-scheme: dark)` block, and a `:root[data-theme="dark"]`
block so the viewer's toggle wins both ways. Give `body` an explicit token bg.

## Output

A **self-contained, theme-aware HTML artifact**, ready to screenshot and post:
- Header: the event + date + a one-line thesis.
- The four rungs as sections, each titled with the plain question.
- The two charts inline (HTML/CSS bars are fine and responsive — no external libs).
- **Sources** list in the footer (every fetched URL).
- A short **post caption** draft at the end (lead with the sleeper insight, not
  the summary).

Publish with the Artifact tool and send it to the user. Also write the file into
the repo/working dir so it's kept.

## Run order

1. Fetch + verify rung 1 **from the primary source** — open the actual filing;
   don't trust a snippet; confirm the core number in the document itself.
2. Fetch comparators/precedents for rungs 2–4 as needed.
3. Assign the −5…+5 impact scores from the fetched winner/loser reasoning.
4. Load `dataviz`, build the two charts against the tokens above.
5. Assemble the artifact, list sources, draft the caption, publish, send, save.

## Changelog
- 2026-10-05, v3: long-term mode with gates LT1–LT6 (in the numbers, survives two bad years, dilution,
  not already run, liquidity, benchmark SPY) and its verdicts; checklist item added.
- 2026-10-05, v2: added "Go deeper on every branch" (press releases, controls/spread, siblings,
  contagion, input prices, funded orders, corporate actions, pre-move/liquidity, supply+deficiency
  pattern, keyword false positives, scoring and ledger logging) and the expanded checklist.
- 2026-10-01, v1: original four-rung ladder with primary-source rules (Human-Project repo).
