# Market-wide filings scan, deep dive: 2026-10-02 filings

*Written 2026-10-04 (Sunday). Source scan: `watch/market/2026-10-02.md`. Method: `nth-order-pipeline/METHOD.md` v2.*
*Prices are Friday 2026-10-02 closes from the Yahoo chart API. Every claim below cites an EDGAR accession number. Quotes are copied verbatim from the filing.*

**Account lens:** UK retail trader at IBKR with £50–200 per trade, regular US hours only, long-only in practice. Shorting sub-$5 microcaps (borrow, margin, buy-ins) is not realistic at this size. So the supply-overhang items are treated as "avoid" flags, not as short trades.

---

## 0. Summary

| Rank | Item | What it is | Numbers | Verdict |
|---|---|---|---|---|
| 1 | **ZDGE** | Insider (Howard Jonas) put $6.5m in at $2.93 | Stock $3.00, 2.4% above his price. PIPE is 16.5% of market cap | **Watchlist 6/10.** The only long idea with a real buyer's cost basis nearby |
| 2 | **HZO** | $53.00 cash, Blackstone-backed, robust deal | Spread $0.65 (1.24%), about 5–7% annualised. Close not before 7 Dec | Clean deal but **kill for this account size**: minimum commissions eat most of a $1–2 gross gain |
| 3 | **LGMK** | $1.31 cash going-private; vote **Mon 5 Oct** | 15.9% spread vs −55% if it breaks. Market implies about 77% odds | A 5.6% holder has given notice to dissent, but the deal allows at most 1% dissent. **Kill (OTC, about $3k a day traded)**; watch the result |
| 4 | **Supply avoid-list** | TPST, HCWB, SBFM, NEOV, INM→MTRI | 56%, 81%, 236%+, 111%-of-market-cap and 73%-of-post-merger supply | Don't buy these for 30–60 days |
| 5 | **SSTI** | Transom tender at $8.00 cash plus a CVR worth up to $3 | Trades $8.33, so the cash spread is **−4.0%** | Kill. You pay $0.33 for a CVR that needs about 15–20% growth from a shrinking base |

**Main kills:** UTZ trades *above* the $14.25 deal price. VCTR is the acquirer, so there is no spread. GETY is distressed and trades on OTC Pink at $0.04. ATER's control buyers paid $0.05 a share against a $0.655 market. GOW is a crashed de-SPAC with a tiny float. ADRX's 13D is a passive post-IPO VC filing.

---

## How the gates were applied to event-driven nodes

METHOD.md's gates were built for supply-chain nodes. For merger, 13D and registration events I used the same five gates with this mapping, applied the same way to every row:

| Gate | Supply-chain meaning | Event-driven meaning used here |
|---|---|---|
| G1 Materiality | theme ≥15% of revenue | The event is material to the security: the deal is 100% of its value, the overhang is ≥5% of shares, or control changes |
| G2 Substitutability | customer can't switch in 12m | The counterparty **can't walk cheaply**: no financing out, no easily waived condition, and the reverse fee or damages are meaningful |
| G3 Already run | moved >50% with link-1 | The price already captures the event: the target already re-rated to near the deal price, or the price already fell to the PIPE price |
| G4 Verifiable | exposure in a filing | The link is in a filing (unchanged) |
| G5 Tradeable | listing, spread, volume | Listed on a national exchange, enough regular-hours volume, **and** the edge beats round-trip IBKR costs on £50–200 |

Score factors were mapped the same way: payoff size (0: <5%, 1: 5–15%, 2: >15%); deal or contract certainty; coverage; date visibility (0 none, 1 approximate, 2 hard date); and behavioural signal (someone put money in). Cut-offs are unchanged: ≥8 write up, 5–7 watchlist, ≤4 kill. Failing any gate means a kill whatever the score.

---

## 1. Merger votes

### 1a. Deal terms

| | **HZO** MarineMax | **UTZ** Utz Brands | **VCTR** Victory Capital |
|---|---|---|---|
| Filing | DEFM14A 0001193125-26-412241 | DEFM14A 0001193125-26-411198 | PREM14A 0001104659-26-112931 |
| Role | **Target** | **Target** | **Acquirer** (buying First Eagle) |
| Buyer | SHM Holdco, an affiliate of Safe Harbor Marinas, "a portfolio company of Blackstone Infrastructure Partners" (private) | Intersnack Group GmbH & Co. KG (private, Germany) | n/a. Seller is GC Ferry Parent (Genstar Capital, private) |
| Price / form | **$53.00 cash**: "you will be entitled to receive $53.00 in cash" | **$14.25 cash** per Class A share; Class V cancelled for nothing | $7.03bn base price: cash, plus 4.9% new VCTR common, plus Series B convertible preferred. Stock leg is $2bn "based on a per share price of $116.26" |
| Premium | "premium of 96% to … $27.03 on January 30, 2026" | "premium of approximately 91%" to the 20 Jul 2026 close | n/a |
| Vote | **11 Nov 2026**, 10:00 ET, virtual. Needs a majority of votes entitled to be cast (22,086,735 shares; D&O hold 3.2%) | **13 Nov 2026**, 9:00 ET. Needs a majority of outstanding **and** a majority of disinterested votes cast. **42.14% is locked** by voting agreement | Date blank (preliminary). The vote is only on the share issuance: "Stockholder approval of the share issuance is not a condition to the closing" |
| Expected close | "close by the end of the calendar year 2026. The Closing may not occur prior to December 7, 2026 without the prior written consent of Parent" | "Utz currently expects to complete the Merger in the fourth quarter of 2026" | "expected to be consummated by the end of the first quarter of 2027" |
| Regulatory | HSR refiled 30 Sep: "will expire at 11:59 p.m. Eastern Time on October 30, 2026" unless there is a second request. Plus unnamed foreign antitrust and FDI clearances | **All done.** HSR "expired at 11:59 p.m. Eastern Time on September 9, 2026"; Ukraine clearance "obtained on September 17, 2026" | HSR filed 22 Sep 2026; FINRA Rule 1017 application filed 23 Sep; client consents ≥75% of Base Revenue Run-Rate; other regulatory approvals |
| Financing | "not subject to any financing condition". Blackstone equity commitment "up to $2.309 billion" | Debt plus cash, about $2.027bn; "not subject to any financing condition" | $3.5bn incremental term loan, $200m revolver, $950m secured bridge |
| Outside date | 9 May 2027, plus two automatic 3-month extensions (maximum 15 months) | 20 Apr 2027 | 25 May 2027, plus two 45-day extensions |
| Fees | Target fee $31.65m. Buyer: specific performance plus "uncapped damages from Parent for willful breaches" | Target fee $50.0m | Not extracted (no arb payoff) |

### 1b. Spread, annualised return, break risk

| | HZO | UTZ | VCTR |
|---|---|---|---|
| Price 2 Oct | $52.35 | $14.27 | $113.23 |
| Spread | **+$0.65 (+1.24%)** | **−$0.02 (−0.14%)**. A possible extra $0.063 quarterly dividend only if closing falls after a record date (merger agreement caps dividends at $0.063 a quarter) | none (acquirer) |
| Days to close (from Mon 5 Oct) | 63 (7 Dec, earliest) to 87 (31 Dec) | about 40–85 | n/a |
| Annualised | **7.2% (7 Dec) / 5.2% (31 Dec)**, simple | negative | n/a |
| Break downside | to about $27 (unaffected close 30 Jan 2026) = −48%. Market implies **97.5%** completion | to about $7.45 (unaffected 20 Jul 2026) = −48% | n/a |
| Break risk | **Low.** Full sponsor equity backstop, no financing out, a regulatory covenant that includes divestitures, an auction with a runner-up at **$50.10** ("Party Z … $50.10 per share in cash"). Main risk is a DOJ second request by 30 Oct | **Very low.** Regulatory approvals done, 42% locked, debt committed. Remaining risk is the disinterested-holder vote | Acquirer-side risks: client-consent shortfall, which lowers the price below 92.5% of run-rate, and financing |
| £50–200 economics | 2–3 shares give $1.30–1.95 gross if it closes. IBKR minimum commission ×2 (about $0.70 tiered to $2.00 fixed) plus FX takes most or all of it | Negative before costs | No defined payoff |

### 1c. Branches: who else is affected

| Branch | Evidence | Already re-rated? | Verdict |
|---|---|---|---|
| HZO acquirer: Safe Harbor / Blackstone Infrastructure (private). Listed parent **BX** | DEFM14A cover letter | n/a | **G1 fail**: $2.3bn is immaterial to Blackstone |
| HZO supplier **BC** (Brunswick) | HZO 10-K 0001193125-25-284680: "Sales of new Brunswick boats accounted for approximately 18% of our revenue in fiscal 2025." That is HZO's dependence on BC, not BC's dependence on HZO | BC −20% since 7 Aug ($81.55 → $65.43). Did not react to the deal | **Kill**: no evidence the ownership change alters BC's economics. G1/G4 fail |
| HZO peer **ONEW** (OneWater Marine) | Named in Wells Fargo's selected-companies list in the HZO proxy. No filing links ONEW to any bidder | ONEW $12.29 (10 Aug) → $9.82. **No sympathy move** | **Kill**: G4 fail. Losing bidders (Party Z, the J&S Consortium) are anonymous |
| UTZ acquirer Intersnack | private KG | n/a | not tradeable (G5) |
| UTZ peers POST, FLO, MZTI, BRBR, BGS, JJSF, SMPL | UTZ proxy, Citi selected companies: 2027E EV/EBITDA "5.6x" to "9.2x", versus a deal at "13.2 times LTM Adjusted EBITDA" | none | **Kill**: a takeover read-across is narrative without a filing link (G4). All widely covered |
| VCTR seller Genstar / First Eagle | private. Genstar takes stock at $116.26 with a **3-year lock-up** | VCTR is flat against pre-deal ($115.34 on 25 Aug vs $113.23 now) | see the VCTR score |
| **Amundi** (Euronext Paris) | holds VCTR Series A preferred. The proxy cites "Amundi's distribution of First Eagle's products outside the U.S." | n/a | **Kill**: G1 fail for Amundi |
| Index deletion (HZO, UTZ) | **Index membership is not stated in either proxy.** I found no primary source this run | Deletion normally executes at the close at about the deal price, so index selling is absorbed by the arb | **Kill**: G4 fail and nothing to trade. Do not log it as an edge |
| Other public company party to a deal? | None of the three involves another US-listed company as a counterparty | | |

---

## 2. Activist / new 5%+ holders (13D)

None of the six is a classic activist campaign. Two are deal-support or control filings (SSTI, ATER), two are de-SPAC/IPO housekeeping (GOW, ADRX), one is an insider PIPE (ZDGE) and one is a small dissenter (LGMK).

| Rank | Ticker | Filer | Stake | Item 4 purpose (quoted) | Price paid | Track record | Price 2 Oct |
|---|---|---|---|---|---|---|---|
| **1** | **ZDGE** (0001213900-26-106074) | Howard S. Jonas via Chartwell Holding LLC. Vice Chairman of Zedge, Chairman of IDT; his son is Zedge's Executive Chairman | **15.6% of Class B** (2,344,805 sh), 7.6% of votes. Plus 1,996,587 warrants at $3.22, exercisable only after the later of stockholder approval and **25 Mar 2027** | "acquired the securities described in this Statement for investment purposes and to support the Company's expansion of its DataSeeds.AI ("DataSeeds") business" | **$2.93/sh** plus warrant, **$6.5m** (part of a $7.675m PIPE, 8-K/A 0001213900-26-104861) | Insider, not an outside activist. The 13D gives his occupation as "Chairman of the Board of Directors of IDT Corporation". His record at other companies was not checked against filings this run | **$3.00** |
| **2** | **LGMK** (0002157971-26-000001) | Kirtan S. Patel, private investor. First filing under this CIK, **no track record** | **5.6%** (50,000 of 899,759 sh) | "has sent to the Issuer written notices of intent to demand payment for the shares pursuant to Nevada Revised Statutes 92A.300 to 92A.500, and has voted against the Merger" | about **$175,706 for 50,000 sh** (about $3.51 avg). Sold 1,080 sh at $1.03–1.04 on 29 Sep | none found | **$1.13** (OTC) |
| **3** | **SSTI** (0001140361-26-038446) | Gary M. Lauder / Lauder Partners (VC). Previously a 13G filer, pre-2017-IPO holder | **17.0%** (2,255,406 sh). A 13D group with Transom-related parties and Veradace would hold 34.0% | "the Reporting Persons agreed to tender their aggregate 2,255,406 shares". They will reinvest for about 17.5% of Transom's Topco | Pre-IPO cost, not disclosed | Long-term VC holder; rolling into the buyout | **$8.33** |
| 4 | **ADRX** (0000947871-26-000917) | OrbiMed (Advisors, GP VII, Israel II, Genesis) | **14.0%** (Advisors) plus **8.7%** (Israel) = **22.7%** combined (24,205,789 of 106,801,325) | "acquired for the purpose of making an investment in the Issuer and not with the intention of acquiring control" | 2020–23 preferred rounds, plus 950,000 IPO shares at **$17.00** | Large healthcare VC; holds board seats (Gordon, Chimovits) | **$18.25** |
| 5 | **GOW** (0001213900-26-106583 / -106590) | (a) Hegro Well Pte (Xi Zhang, China); (b) Inflection Point Fund I (Michael Blitzer's SPAC team) | (a) **74.0%** (28,571,430 of 38,602,261); (b) **9.87%** incl. preferred and warrants | (a) none beyond the de-SPAC; may receive up to 20m earn-out shares. (b) "acquired the shares reported herein for investment purposes", and may discuss "potential business combination opportunities" | (a) no cash (merger consideration); (b) **$1.3m for 990,000 founder shares** (about $1.31/sh) plus **$20m** of Series A preferred and warrants (convert/exercise at $12, reset after 6 months to max(VWAP, **$5.00**)) | (b) EDGAR: Blitzer's prior SPAC Inflection Point Acquisition Corp II became USA Rare Earth (CIK 1970622); Corp III, V, VI and VIII are also on file | **$3.87** |
| 6 | **ATER** (0001437749-26-031908 / -031910) | Michelle Chiam Sin Ling and Chang Woei Jiann (Malaysia). New CIKs, **no track record** | **10.0% each** (26,121,180 sh each), part of a purchaser group buying **92.5%** of the company from David E. Lazar | "the Reporting Person may from time to time acquire additional Common Stock or engage in discussions with the Issuer concerning future acquisitions of its shares" | **$1,296,000 for 26.1m sh = $0.0496/sh.** The whole block was $12.0m (SPA, Exhibit 99.1) | none | **$0.655** |

**Context that matters:**
- **ZDGE.** Total PIPE was 2,616,447 shares plus 2,354,803 warrants for $7.675m (8-K/A). Market cap is about $46.6m, so the PIPE is about 16.5%. The stock trades at the insider's price. There is no hard catalyst; the next is the stockholder vote to approve the warrants, at the next annual or special meeting.
- **LGMK.** The merger (DEFR14A 0001213900-26-098236) pays "$1.31 per share", with the vote on **5 Oct 2026**. One of the buyer's closing conditions is that "holders of no more than 1% of the outstanding shares … have exercised, or remain entitled to exercise, statutory dissenters' rights". Patel alone is 5.6%, so Parent must waive this condition or the deal fails. Unaffected price was $0.512 (31 Jul): "premium of approximately 156%". The buyer is a management-led group (Nicholas Kovacevich / Positano Partners).
- **SSTI.** The 8-K (0001193125-26-406024) offer is "$8.00 per Share … plus … one non-transferable contingent value right". The CVR pays $0.50 if 2027 ShotSpotter plus SafePointe revenue is "$73,500,000" or more, rising to $3.00 at $87.0m. The 10-Q (0001193125-26-352203) shows H1 2026 revenue of "$48.1 million … a decrease of 11%", with ShotSpotter "approximately 65%" (about $31m, or about $62m annualised; SafePointe is not broken out) and NYC at 27% of revenue. Reaching the CVR needs roughly +15–20% growth from a shrinking base. The tender must start within 15 business days of 28 Sep (by about 20 Oct) and stay open 20 business days. Close is expected in Q4 2026.
- **ATER.** Aterian sold its brands to Trademark Global for "$18.0 million in cash" and closed 17 Jul (8-K 0001437749-26-023879). Old holders got a CVR cash payment of "approximately $0.9936 per CVR" around 2 Oct (8-K 0001437749-26-031486). What is left is a listed shell controlled by the new buyers at about $0.05 cost, with Nasdaq bid-price compliance due 1 Mar 2027 (8-K 0001437749-26-029837). The Series AAA shares were sold under Regulation S.
- **GOW.** The de-SPAC closed 24–25 Sep. Price went $10.375 (17 Sep) → $1.81 (29 Sep) → $3.87, with 21.3m shares traded on 30 Sep. At most about 9.0m shares (23%) sit outside the two 13D filers. The registration rights agreement requires a resale shelf "no later than 30 days after the Closing Date", which is about 25 Oct.

---

## 3. Registrations (supply)

"% out" means % of shares outstanding. Free float is smaller than outstanding, so the float % is higher still. "Immediate" means sellable on effectiveness without further exercise or approval. Warrants above the current price are not near-term supply.

| Ticker | Filing | Status | Who can sell | Shares | % out (total / immediate) | Their cost vs price | Read |
|---|---|---|---|---|---|---|---|
| **TPST** | S-3 333-299142, EFFECT 1 Oct; 424B3 0001213900-26-106362 | **Effective** | HCW-placed PIPE investors | **9,534,164**: 3,105,591 pre-funded warrants, 6,211,182 Series C/D warrants at **$0.805** (need stockholder approval), 217,391 placement-agent warrants | **56.4% / 18.4%** (of 16,889,767) | PIPE at **$0.804** vs $0.811 | Worst overhang. Price already sits at the PIPE price; below $1 |
| **HCWB** | S-1 0001493152-26-045532 | Filed, not effective | one existing institutional investor | **1,807,228**: 903,614 pre-funded warrants plus 903,614 warrants at $1.66 (need stockholder approval) | **80.8% / 40.4%** (of 2,236,324) | units at **$1.6599** vs $1.68 | Avoid. At-the-money supply equal to 40% of the company |
| **SBFM** | S-1 0001683168-26-007581 | Filed (primary, best-efforts, Aegis) | the company sells new units | up to **10,180,337** units (1 share plus 2 Series D warrants at about $0.6876) | **236%** of 4,310,301 in shares, plus **472%** in warrants | assumed $0.6876 vs $0.667 | Avoid. Offering "not later than November 30, 2026" |
| **NEOV** | S-3 333-299097, EFFECT 1 Oct (filed 0001683168-26-007334) | **Effective** | the company (universal shelf) | **$200,000,000** of securities | about **111% of market cap** (59,013,247 × $3.05 = $180m). Also: 4.5m IGC resale (7.6%) effective 25 Sep; new S-3 for 1,454,545 warrant shares at $3.30 (2.5%) filed 2 Oct | n/a | Stock +21% on 2 Oct ($2.52 → $3.05) with a fresh shelf. Classic setup for a takedown |
| **INM** | S-4 333-297234, EFFECT 1 Oct; 424B3 0001193125-26-410691 | **Effective**; meeting **4 Nov 2026** | Mentari holders and the **$490.0m** pre-closing PIPE (Vivo, Perceptive, ADAR1, Sirenia…), which has resale registration rights | PIPE = **73.36%** of the combined company; current INM holders = **0.97%** | n/a (merger) | Crude implied value: 0.97% × ($490m / 0.7336) ≈ $6.5m ≈ **$1.18 per INM share vs $1.33** | Becomes "MTRI" after a reverse split. INM looks rich against the deal-implied value; large post-close float. Avoid |
| **BSEM** | S-1 0001213900-26-106555 | Filed, not effective | HCW-placed PIPE investors | **2,224,270**: 735,296 shares, 1,470,592 warrants at $3.83, 18,382 placement-agent warrants at $6.12 | **11.9% / 3.9%** (of 18,672,125). Roughly 4.9% of a ~15m float | PIPE at **$4.08** vs $2.73 | Already fell 33% from the PIPE price (G3). Warrants are out of the money |
| **PLRZ** | F-1 333-299014, EFFECT 1 Oct (F-1/A 0001213900-26-104062) | **Effective** | one selling shareholder | **404,166**: 70,833 pre-funded warrants plus 333,333 warrants at **$12.00** | **16.6% / 2.9%** (of 2,428,604) | warrants at $12 vs $9.61 | Small immediate supply; illiquid (about $0.5m a day) |
| **VDTA** | S-1 0001493152-26-045574 | Filed, not effective | various selling stockholders | **1,373,152** | **9.0%** (of 15,206,716) | n/a | OTCQB, about $0.18m a day. G5 fail |

---

## 4. GETY delisting (25-NSE)

**Why it is delisting.** NYSE Form 25 (0000876661-26-000814): "no longer suitable for listing based on "abnormally low selling price" levels, pursuant to Section 802.01D". Trading was suspended 29 Sep and removal is effective **13 Oct 2026**. the company "does not intend to appeal the NYSE's determination", and the stock has traded on **OTC Pink as "GETY" since 30 Sep** (8-K 0001213900-26-105790). The price went $0.916 (6 Jul) → $0.042 (2 Oct), a fall of 95%.

**What caused it.**
1. **Shutterstock merger dead.** The UK CMA required a sale of Shutterstock's editorial business, and Getty refused: "On July 7, 2026, Getty Images delivered a written notice to Shutterstock terminating the Merger Agreement" (8-K/A 0001213900-26-076004). Its 10.5% senior secured notes are then redeemed.
2. **Liquidity stress.** Getty used 30-day grace periods on the 9.750% 2027 and 14.000% 2028 notes. It paid on 30 Sep, so there was "no "Event of Default"" (8-K 0001213900-26-104907). It also cites "substantial doubt about our ability to continue as a going concern". A warrant-lawsuit judgment totalling about $67.8m in principal (plus 9% pre-judgment interest from Aug 2022) was ordered on 27 Jul (8-K 0001213900-26-095091).
3. **The controlling holders are circling.** Getty family (Getty Investments etc.) and Koch (KED Icon, 115,259,246 sh) formed a 13(d) group on 25 Aug owning **306,633,252 of 421,018,476 shares (72.8%)** "with respect to any such alternatives and potentially providing capital solutions" (13D/A 0000950142-26-002432; 13D/A 0001193125-26-368887). The annual meeting was postponed. Guggenheim is advising.

**Consequences for other tickers.**

| Ticker | Link | Evidence | Already re-rated? | Verdict |
|---|---|---|---|---|
| **SSTK** (Shutterstock) | ex-merger partner | Termination 8-K 0001140361-26-028035. The 10-Q (0001549346-26-000029) records a "$173.7 million" goodwill impairment and **mentions no termination fee received**. CEO stepped down 12 Jul (interim CEO, Rik Powell). Three new independent directors from 8 Sep (8-K 0001140361-26-035918) | **Yes**: $9.19 (6 Jul) → $3.81, −58% | Kill (G3). A distressed Getty recapitalised by its 73% holders is not obviously good or bad for SSTK; there is no filing to anchor a thesis |
| GETY equity | | | −95% | Kill. On OTC Pink, about $17.7m market cap against a heavily indebted company. A "capital solution" from 72.8% holders is likely to dilute or wipe out the minority. Not a regular-hours exchange listing (G5) |
| Any new merger? | none filed | no 8-K, 425 or SC TO found | | No deal consequence beyond the dead SSTK merger |

---

## 5. Scores, all nodes (including kills)

| Node | G1 | G2 | G3 | G4 | G5 | Pay | Cert | Cov | Date | Behav | **Score** | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ZDGE** long (insider PIPE) | P | n/a | P | P | P | 1 | 0 | 2 | 1 | 2 | **6** | **Watchlist** |
| LGMK merger arb | P | **F** (waivable 1% dissent condition, small buyer) | **F** (+121% vs unaffected) | P | **F** (OTC, about $3k a day) | 2 | 0 | 2 | 2 | 1 | 7 | Kill (watch the 5 Oct result) |
| SSTI tender + CVR | P | P | **F** (+50% on 29 Sep; above cash) | P | P | 1 | 1 | 1 | 2 | 2 | 7 | Kill |
| UTZ merger arb | P | P | **F** (above deal) | P | **F** (negative edge) | 0 | 2 | 0 | 2 | 2 | 6 | Kill |
| HZO merger arb | P | P | **F** (98.8% of deal captured) | P | **F** (costs ≈ spread at £50–200) | 0 | 2 | 0 | 1 | 2 | 5 | Kill (fine for bigger tickets) |
| VCTR (acquirer) | P | n/a | P | P | P | 0 | 1 | 0 | 1 | 1 | 3 | Kill |
| GOW (de-SPAC) | P | n/a | **F** | P | **F** (≤9m-share float, foreign private issuer) | 0 | 0 | 2 | 1 | 0 | 3 | Kill |
| ADRX (passive 13D) | **F** | n/a | P | P | P | 0 | 0 | 0 | 1 | 1 | 2 | Kill |
| ATER (shell sale) | P | n/a | n/a | P | **F** (buyers' cost 92% below market) | 0 | 0 | 2 | 0 | 0 | 2 | Kill / avoid |
| TPST (overhang) | P | n/a | **F** (at PIPE price) | P | **F** (no short for this account) | 1 | 2 | 2 | 1 | 0 | 6 | Kill / avoid |
| HCWB (overhang) | P | n/a | P | P | **F** | 1 | 1 | 2 | 0 | 0 | 4 | Kill / avoid |
| SBFM (dilutive offering) | P | n/a | P | P | **F** | 1 | 1 | 2 | 1 | 0 | 5 | Kill / avoid |
| NEOV (shelf) | P | n/a | P | P | **F** | 1 | 0 | 1 | 0 | 0 | 2 | Kill / avoid |
| INM→MTRI | P | n/a | P | P | **F** (73% PIPE supply post-close) | 1 | 1 | 2 | 2 | 0 | 6 | Kill / avoid |
| BSEM | P | n/a | **F** (−33% since PIPE) | P | **F** | 0 | 1 | 2 | 0 | 0 | 3 | Kill |
| PLRZ | P | n/a | P | P | **F** (illiquid) | 0 | 1 | 2 | 0 | 0 | 3 | Kill |
| VDTA | P | n/a | P | P | **F** (OTCQB) | 0 | 1 | 2 | 0 | 0 | 3 | Kill |
| GETY | P | n/a | **F** | P | **F** (OTC Pink) | 0 | 0 | 1 | 1 | 0 | 2 | Kill |
| SSTK | n/a | n/a | **F** | P | P | 0 | 0 | 1 | 0 | 0 | 1 | Kill |
| ONEW (HZO read-across) | n/a | n/a | P | **F** | P | 0 | 0 | 1 | 0 | 0 | 1 | Kill |
| BC (HZO supplier) | **F** | n/a | P | **F** | P | 0 | 0 | 0 | 0 | 0 | 0 | Kill |
| BX (HZO sponsor) | **F** | n/a | n/a | P | P | 0 | 0 | 0 | 0 | 0 | 0 | Kill |
| UTZ peer read-across (7 names) | n/a | n/a | P | **F** | P | 0 | 0 | 0 | 0 | 0 | 0 | Kill |
| Amundi (VCTR) | **F** | n/a | n/a | P | P | 0 | 0 | 0 | 0 | 0 | 0 | Kill |
| Index-deletion trade (HZO, UTZ) | n/a | n/a | **F** | **F** | n/a | 0 | 0 | 0 | 1 | 0 | 1 | Kill |

*The overhang rows score the short-side thesis. They fail G5 only because shorting microcaps is not feasible at £50–200. The useful action is "don't buy". Several would be watchlist shorts for a larger, margin-enabled account (TPST 6, INM 6, SBFM 5).*

---

## 6. Dated events, next 60 days (to about 3 Dec 2026)

| Date | Event | Source |
|---|---|---|
| **Mon 5 Oct** | **LGMK special meeting**, $1.31 cash going-private. Watch whether Parent waives the ≤1% dissent condition (Patel is 5.6%) | DEFR14A 0001213900-26-098236; 13D 0002157971-26-000001 |
| 13 Oct | GETY NYSE delisting effective (already on OTC Pink) | Form 25 0000876661-26-000814 |
| by about 20 Oct | SSTI tender offer must commence (15 business days after 28 Sep). Then open 20 business days, so expiry about mid/late Nov | 8-K 0001193125-26-406024 |
| about 22 Oct | VCTR HSR waiting period, *derived* (filed 22 Sep plus the standard 30 days; not stated in the proxy) | PREM14A |
| about 25 Oct | GOW resale shelf due ("no later than 30 days after the Closing Date"). Supply | 13D 0001213900-26-106590 |
| **30 Oct** | **HZO HSR waiting period ends 11:59 p.m. ET** unless DOJ issues a second request (the key break-risk date) | DEFM14A 0001193125-26-412241 |
| 30 Oct | LGMK Series J one-time redemption right | DEFR14A |
| **4 Nov** | **INM shareholder meeting** (Mentari merger; reverse split 1:2 to 1:20; becomes MTRI) | 424B3 0001193125-26-410691 |
| **11 Nov** | **HZO special meeting** | DEFM14A |
| **13 Nov** | **UTZ special meeting** (regulatory approvals done; close can follow quickly) | DEFM14A 0001193125-26-411198 |
| by 30 Nov | SBFM best-efforts offering must close (pricing can come any day) | S-1 0001683168-26-007581 |
| 7 Dec | HZO earliest closing date without Parent consent | DEFM14A |
| TBD | VCTR share-issuance vote (definitive proxy will set it); TPST and HCWB stockholder votes to approve PIPE warrants | PREM14A; 424B3; S-1 |

Beyond 60 days: ATER Nasdaq bid-price deadline 1 Mar 2027. ZDGE warrants exercisable from 25 Mar 2027 at the earliest. ADRX 180-day IPO lock-up about late Mar 2027 (prospectus 24 Sep). VCTR close by end of Q1 2027. HZO outside date 9 May 2027.

---

## 7. Log entries (METHOD.md Stage 6)

Logged 2026-10-04. Price at log is the 2 Oct close. Control is picked mechanically: **IWM** for sub-$2bn names ($281.52) and **SPY** for larger ($769.64). Review dates: **+30 = 2026-11-03**, **+90 = 2027-01-02**. OUTCOME is left blank and filled at review; do not edit the rows above.

| Ticker | Chain | Gates | Score | Thesis (one line) | Evidence | What kills it | Price | Control |
|---|---|---|---|---|---|---|---|---|
| ZDGE | insider PIPE → DataSeeds pivot | all pass | 6 | Insider put $6.5m in at $2.93 and the stock sits at his cost | 13D 0001213900-26-106074 Item 3/4 | Closes below $2.93 for 2 weeks; another discounted raise; next 10-Q shows no DataSeeds revenue | 3.00 | IWM 281.52 |
| HZO | Blackstone/Safe Harbor → MarineMax $53 cash | G3, G5 F | 5 | Low-risk arb, spread too thin for £50–200 | DEFM14A 0001193125-26-412241 | DOJ second request by 30 Oct | 52.35 | IWM 281.52 |
| UTZ | Intersnack → Utz $14.25 cash | G3, G5 F | 6 | Trades above the deal price; nothing left | DEFM14A 0001193125-26-411198 | n/a (kill) | 14.27 | IWM 281.52 |
| VCTR | VCTR → First Eagle ($7.03bn) | pass, low score | 3 | Acquirer with no defined payoff | PREM14A 0001104659-26-112931 | n/a | 113.23 | SPY 769.64 |
| LGMK | Langham → LogicMark $1.31 | G2, G3, G5 F | 7 | 16% spread but a 5.6% dissenter vs a 1% cap | 13D 0002157971-26-000001; DEFR14A | Parent refuses to waive → break toward about $0.51 | 1.13 | IWM 281.52 |
| SSTI | Transom → SoundThinking $8 + CVR | G3 F | 7 | Paying $0.33 for a low-odds CVR | 13D 0001140361-26-038446; 8-K 0001193125-26-406024 | n/a (kill) | 8.33 | IWM 281.52 |
| ADRX | OrbiMed post-IPO 13D | G1 F | 2 | Passive VC holder; nothing to trade | 13D 0000947871-26-000917 | n/a | 18.25 | IWM 281.52 |
| GOW | IPEX de-SPAC → GOWell | G3, G5 F | 3 | Crashed low-float de-SPAC; shelf coming | 13Ds 0001213900-26-106583/-106590 | n/a | 3.87 | IWM 281.52 |
| ATER | Lazar → Malaysian buyers (shell) | G5 F | 2 | Buyers' cost $0.05 vs $0.655 market | 13Ds 0001437749-26-031908/-031910 | n/a | 0.655 | IWM 281.52 |
| TPST | PIPE resale 56% | G3, G5 F | 6 | Overhang at the PIPE price | 424B3 0001213900-26-106362 | n/a | 0.811 | IWM 281.52 |
| HCWB | PIPE resale 81% | G5 F | 4 | Overhang | S-1 0001493152-26-045532 | n/a | 1.68 | IWM 281.52 |
| SBFM | best-efforts units 236% | G5 F | 5 | Dilutive offering by 30 Nov | S-1 0001683168-26-007581 | n/a | 0.667 | IWM 281.52 |
| NEOV | $200m shelf effective | G5 F | 2 | Shelf ≈ 111% of market cap after a +21% day | EFFECT 333-299097 | n/a | 3.05 | IWM 281.52 |
| INM | Mentari reverse merger, $490m PIPE | G5 F | 6 | INM above deal-implied value; huge post-close float | 424B3 0001193125-26-410691 | n/a | 1.33 | IWM 281.52 |
| BSEM | PIPE resale 11.9% | G3, G5 F | 3 | Already −33% since PIPE | S-1 0001213900-26-106555 | n/a | 2.73 | IWM 281.52 |
| PLRZ | warrant resale 16.6% | G5 F | 3 | Small immediate supply; illiquid | F-1/A 0001213900-26-104062 | n/a | 9.61 | IWM 281.52 |
| VDTA | resale 9.0% | G5 F | 3 | OTCQB | S-1 0001493152-26-045574 | n/a | 5.25 | IWM 281.52 |
| GETY | NYSE delisting, distress | G3, G5 F | 2 | Equity is an option on a recap by 72.8% holders | Form 25; 13D/As | n/a | 0.042 | IWM 281.52 |
| SSTK | ex-Getty partner | G3 F | 1 | Already −58%; no fee received | 8-K 0001140361-26-028035; 10-Q | n/a | 3.81 | IWM 281.52 |
| ONEW, BC, BX, Amundi, UTZ peers, index deletion | branches | G1/G4 F | 0–1 | No filing link | as section 1c | n/a | ONEW 9.82, BC 65.43 | IWM / SPY |

---

## 8. Caveats

- **Index membership** (S&P 600 / Russell) for HZO and UTZ was **not confirmed** in a primary source this run. The deletion point is logged as unverified.
- **SSTI CVR maths** uses ShotSpotter's share of total revenue from the 10-Q. SafePointe revenue is not broken out, so the gap to $73.5m is approximate.
- **INM implied value** is a crude pro-rata of the PIPE's post-money. The exchange ratio floats with InMed's net cash at closing.
- **VCTR HSR expiry (about 22 Oct)** is derived from the 30-day statutory period, not stated in the proxy.
- **Costs:** IBKR minimums cited are standard published tiers (fixed $1.00 per order, tiered about $0.35 plus exchange fees). Check your own plan and whether you already hold USD (FX conversion has its own minimum).
