# The market-wide scanner: what each section means

`python watch/scan_market.py [YYYY-MM-DD]` reads every SEC filing made on one day and writes a shortlist to `watch/market/YYYY-MM-DD.md`. With no date it scans the last business day and catches up any business day it missed (up to 5). It judges nothing. Every line is a pointer to a filing to read, and nothing is listed that the SEC's own index or search did not return.

A line looks like this: **TICKER**, what it is, the form type in `code`, and a link. A line in *italics* is a note (a count of what was left out, or a search that failed), not a filing.

## Two kinds of section

**The older sections** (top of the file) list every listed company. Several feed the ledger, which scores them.

**The wider scan** (from "New contracts" down, added 10 Oct 2026) is noisier, so most of it lists only **relevant** companies and ends with one line saying how many other listed companies were left out. Nothing in the wider scan is scored by the ledger yet.

**Relevant** means any of:
- on the watchlist (`watch/watchlist.json`);
- a ticker in the link graph (`graph/edges.csv`);
- in an industry the domino funnel keeps: chips and computing hardware, power and electrical equipment, energy, mining and metals, defence and aerospace, compute hosting, freight. The codes are in `research/domino/PREREG_D3.md`; each stock's code comes from `research/domino/sic_map.csv`.

That is about 980 listed companies. `sic_map.csv` only covers stocks in the runners price panel, so a company that listed after the panel was built is not relevant until the file is rebuilt (`research/domino/build_sic.py`).

A section with no hits is left out of the file.

## The older sections

| Section | What the filing is | Default stance |
|---|---|---|
| Spin-offs (Form 10) | A company registering a business it will hand to its own shareholders as a new stock. | Read. See `strategies/spinoff/RULES.md`. |
| Tender offers (third party) | Someone offering to buy the shares directly from holders. | Track only. |
| Tender offers (issuer buyback) | The company offering to buy back or exchange its own shares. Marked READ TODAY: there is a hard expiry and often an odd-lot rule that favours small holders. | Read the day it is filed. Long bias in the ledger. |
| Merger votes | The proxy sent to shareholders before they vote on a deal. | Track only. It gives the vote date. |
| Activists / new 5%+ holders | A first Schedule 13D: someone owns over 5% and may push for change. | Read. Long bias in the ledger. |
| Going-private deals | Schedule 13E-3: insiders or a controlling holder taking the company private. | Read. |
| Share registrations (S-1) | A listed company registering shares for sale, often a resale by early holders. | Supply is coming. Short bias in the ledger; for a cash account, avoid. |
| Registrations declared effective | The SEC's notice that a registration is live. The line says which form it makes effective; "not supply" means no new shares can be sold. | Supply can now sell. Avoid until it clears. See `strategies/overhang/RULES.md`. |
| IPO / offering priced (424B4) | The final prospectus. Lock-up dates are inside. | Track only. Log the lock-up expiry. |
| Delistings (25-NSE) | The exchange removing a security. | Track only. It can be the last step of a merger or a company failing the listing rules: open it to see which. |
| 8-Ks with trigger phrases | 8-Ks whose text contains a phrase we trade on (merger agreement, strategic alternatives or review, go-shop, spin-off, reverse split, special dividend, lock-up, tender offer). "bio-mention" and "financing-mention" are known false alarms. | Depends on the phrase; the ledger scores each kind. |
| 6-Ks with trigger phrases | The same idea for foreign companies, which file 6-Ks. | Watch and avoid by default. |

## The wider scan

### New contracts (8-K Item 1.01)
- **What it is.** Item 1.01 of an 8-K means the company signed a material agreement. This section keeps the ones that are commercial: supply, offtake, master services, collaboration, licence, distribution, development, manufacturing, power purchase, framework or joint venture agreements, strategic partnerships, purchase orders, colocation agreements, data centre leases and memoranda of understanding.
- **Why it matters.** A new customer, supplier or partner is the kind of link the graph is built from, and a contract that is large next to the company's sales can move the stock.
- **How to read it.** Every listed company is shown, relevant ones first and marked `(relevant)`. The quotation is the filing's own words, starting where it says the agreement was entered into, signed, amended or announced. The last line counts the 8-Ks that only mention such an agreement in passing.
- **What is filtered out.** Loans (Item 2.03), completed takeovers (Item 2.01), share-sale and spin-off "distribution agreements", and any phrase that appears only in an attached legal document.
- **Default stance.** Read. If the other party is named, consider adding the link with `graph/links.py`.
- **Known gaps.** Contract news announced only by press release (Item 7.01 or 8.01, no Item 1.01) is not seen: Transocean's contract award on 9 Oct 2026 was one. A filing that lists several agreements after one "entered into" can be missed. Old agreements described as background can slip through.

### Share sales and shelves (dilution)
- **What it is.** Three things. A **424B5** is a prospectus supplement: shares (or sometimes bonds) are being sold now from a shelf. An **S-3, S-3ASR, F-3 or F-3ASR** is a shelf: permission to sell later. An **8-K** line means the company signed an at-the-market (ATM) programme, which lets it drip new shares into the market whenever it likes.
- **How to read it.** Relevant companies only. Nothing is classified: a 424B5 can be a bond sale, and a shelf can cover shares that existing holders are selling. On an 8-K line, "at-the-market, sales agreement" is an ATM programme; "at-the-market" alone is usually a one-off sale priced at the market.
- **Default stance.** An avoid list. New supply caps the price until it is absorbed.

### Insider open-market buys (Form 4, code P)
- **What it is.** A Form 4 is an insider reporting a trade in their own company's stock. Only code P is kept: a purchase with their own money. Grants, option exercises, tax withholding, gifts and sales are all ignored. Each line gives the insider, their role, the shares, the average price, the dollar value and the trade date.
- **Why it matters.** An insider can sell for many reasons; buying with their own money has fewer explanations. Several insiders buying together says more than one.
- **How to read it.** Relevant companies only, largest purchase first. The **Clusters** line names any ticker where two or more different insiders bought in the same day's filings. See `strategies/insider-cluster/`.
- **Watch for.** Code P also covers private purchases: buying in the company's own share sale, or from another holder. A line that says the form gives no price is almost always one of those. Read the footnotes before treating it as a market buy. Very small purchases are listed too; the dollar value is there so they can be skipped.
- **Limit.** At most 400 Form 4s are opened in a day. If that is hit, the section says so.
- **Default stance.** Read. A cluster, or one large buy by a chief executive or chairman, is worth a proper look.

### Activist updates (13D amendments)
- **What it is.** A 13D/A is an update from a holder who already filed a 13D: they bought more, sold, changed their plans or signed an agreement with the company.
- **How to read it.** Relevant companies only, with who filed. The scanner reads the filing's header to make sure the company shown is the one held, not the holder.
- **Default stance.** Read when it is a name you hold or watch. Many are routine: a parent company or a founder updating a count.

### New passive 5%+ holders (13G)
- **What it is.** A first Schedule 13G: someone now owns over 5% and says they are passive.
- **How to read it.** Relevant companies only, with who filed. A specialist fund or a person is more interesting than an index house such as Dimensional. Around the quarterly deadlines (mid February, May, August, November) dozens arrive at once: 74 on relevant companies on 14 Aug 2026. Above 20 the section groups them by holder instead of listing each filing.
- **Default stance.** Background. Low signal on its own.

### Late filings (cannot file on time)
- **What it is.** An NT 10-K or NT 10-Q: the company tells the SEC it cannot file its annual or quarterly accounts on time.
- **How to read it.** Every listed company is shown, relevant ones marked. Above 40 in a day, relevant companies only.
- **Default stance.** An avoid list. The reason is in the filing; "more time for the audit" is common and "restating prior periods" is serious.

### Red flags (avoid list)
Relevant companies only. Each line says which flag matched, and the last lines count the other listed companies left out, by flag.
- **Going concern.** The company or its auditor states "substantial doubt" that it can stay in business for a year. The scanner opens the document and quotes the sentence. Companies that use the words only to say there is no doubt, to describe a what-if, or to quote the accounting rule are not flagged; they are named in the "not flagged" line, along with companies saying an earlier doubt is now over.
- **Non-reliance on past accounts.** "Should no longer be relied upon": earlier accounts were wrong and will be restated (8-K Item 4.02, or a 10-K or 10-Q saying the same).
- **Bankruptcy petition.** "Voluntary petition". With Item 1.03 it is the company's own filing. Without it, the words are in a 10-K or 10-Q and can be history or someone else's bankruptcy; the line says so.
- **Auditor change.** 8-K Item 4.01. Read why: a resignation or a disagreement is a warning; a routine switch is not.
- **Default stance.** An avoid list.

### Private fundraisings (Form D)
- **What it is.** A notice that a company sold securities privately, without a public offering. The line gives the amount sold and the size of the offering as the form states them.
- **How to read it.** Relevant companies only. For a listed company it is typically a private placement of shares or convertible notes. Check the amount first: LightPath's on 9 Oct 2026 was $10,800.
- **Default stance.** Treat as dilution unless the amount is trivial.

### SEC comment letters
- **What it is.** `UPLOAD` is a letter from SEC staff questioning a company's filings. `CORRESP` is the company's reply. They are made public weeks or months after they are written, in batches, so the line gives the letter's own date.
- **How to read it.** Relevant companies only. Several rounds on one subject (revenue recognition, a restatement, a going-concern note) is worth reading. One letter and one reply about an S-1 is routine.
- **Default stance.** Background reading.

## A companion tool: who a company depends on

`python graph/company_links.py TICKER` is run by hand, not by the daily scan. It opens the company's latest 10-K (or 20-F) and prints the passages about customer and supplier concentration, the subsidiaries in Exhibit 21, and ready-to-paste `graph/links.py add` commands. A command is printed only when the passage names the other party. "Customer A" is not a name. The tool never writes to the graph itself.

## Limits to keep in mind

- Everything comes from the SEC's daily index and its full-text search. If the search service fails after three tries, the section carries one italic line saying which search failed.
- The older 8-K and 6-K phrase searches read the first 100 hits for each phrase. The wider scan reads up to 300 for contracts and share sales and 1,000 for red flags.
- Run time, old and new sections together: 44 to 57 seconds for 8 and 9 Oct 2026 (three runs each), and 108 seconds for 14 Aug 2026, the busiest day tested (11,140 filings).
- "Filing index" links in the wider scan use the long address (`.../data/CIK/ACCESSION/ACCESSION-index.htm`). The short address the older sections use (`.../data/CIK/ACCESSION-index.htm`) answered "Access Denied" when tested on 10 Oct 2026, in a browser as well as from a script.

## Not built

- **A 13G that turns into a 13D.** A passive holder going active is a real signal, but spotting it needs each holder's earlier filings on the same stock. The scanner lists new 13Gs and 13D amendments separately and does not join them up.
- **13F holdings.** Not built: it would take downloading the SEC's bulk 13F data set each quarter (every fund's full holdings table) and comparing it with the quarter before, which is a quarterly job, not part of a daily scan.
- **Contract press releases without Item 1.01.** Contract awards announced under Item 7.01 or 8.01 are not in "New contracts".
- **Acquisitions by purchase agreement.** The bare phrase "purchase agreement" was tested and dropped: it matched about ten Item 1.01 8-Ks a day and nearly all were share sales or takeovers. Asset and share purchase deals that do not use the words "agreement and plan of merger" are therefore in no section.
- **Share sales through a securities purchase agreement.** A registered direct or private placement shows up only through its 424B5 or Form D, not through its 8-K.
- **Sorting 424B5s into shares and bonds**, and sorting Form 4 code P into market buys and private purchases.
