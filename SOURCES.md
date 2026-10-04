## Market data

Used by `collectors/market_context.py`, which writes `watch/context/latest.json` and `watch/context/YYYY-MM-DD.md`. All of it is free and needs no key. It uses the Python standard library only.

**Prices: Yahoo Finance chart API (unofficial)**
- Endpoint: `https://query1.finance.yahoo.com/v8/finance/chart/SYMBOL?range=3mo&interval=1d`. It falls back to `query2` on errors other than 404.
- Requests send a browser User-Agent and wait about 0.25s between calls. A 404 means the symbol is dropped and listed under `failed_symbols`.
- The last close is taken from `meta.regularMarketPrice` when that is newer than the last bar. The 3mo response can lag on thinly traded futures; on 4 Oct 2026 HRC=F showed 1275 in the bars against 1306 in the meta.
- Weekend placeholder bars are dropped.
- Futures (`=F`) are front-month continuous series, so a contract roll can show up as a false 1-day jump.
- Spin-offs are not adjusted. Any one-day move over 40% is flagged as a possible corporate action and kept out of peer medians.
- Commodity and sector symbols, all returning data on 4 Oct 2026:
  - steel: HRC=F, SLX
  - metals: GC=F, SI=F, HG=F, PL=F, PA=F, ALI=F, XME
  - energy: CL=F, NG=F, XLE, OIH
  - uranium: URA
  - lithium: LIT
  - rare earths: REMX
  - defence: ITA, XAR
  - semis: SOXX
  - agriculture: ZC=F, ZS=F, ZW=F
  - small caps: IWM
  - market: SPY
  - dollar: DX-Y.NYB
  - 10y yield: ^TNX
- **No free price exists for tungsten, antimony, molybdenum or HF-1 artillery steel.** Themes that need one point to labelled proxies: XME and REMX (mining ETFs) for the metals, and HRC=F and SLX (general steel) for HF-1. These are not prices for the thing itself. Paid sources would be Fastmarkets or Argus for APT and antimony.

**Industry / peers: SEC EDGAR**
- All SEC requests use the User-Agent `PersonalResearch research@example.com`.
- Ticker to CIK: `https://www.sec.gov/files/company_tickers.json`. The file is roughly in market-cap order, which is used to rank peers largest first.
- CIK to SIC: `https://data.sec.gov/submissions/CIK##########.json`, using the `sic` and `sicDescription` fields. Funds and BDCs often have no SIC.
- Companies with the same SIC: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=####&owner=include&count=100&start=N&output=atom`, which returns 100 CIKs per page.
- Cached in `data/context/sic_cache.json`. Each SIC and its list of companies is refreshed after 30 days.
- Peers with the same SIC are a best-effort read on the industry. The curated peer groups in the collector (for example MTUS: steel plus the defence-metals group ELMT/ATI/CRS) are what the peer median uses.

## Press-release wires (primary, company-issued)

Used by `collectors/press_wires.py`, which writes `data/press/YYYY-MM-DD.csv`, `watch/press/latest.json`, `watch/press/YYYY-MM-DD.md` and keeps its state in `data/press/seen.json`. It uses the Python standard library only. Only primary sources are used: the wires that companies pay to put out their own releases, and companies' own IR feeds. All 49 feeds below were fetched and parsed on Sunday 4 Oct 2026, and all 49 returned valid XML.

**How they are fetched**
- Requests send the full browser header set: User-Agent, Accept, Accept-Language and Sec-Fetch-*. GlobeNewswire sits behind Akamai, which never answers a Chrome User-Agent sent without the matching headers; the connection just hangs until the timeout. With the full set it answers in under a second.
- At most one request per second per host, a 20s timeout, and one retry on timeouts and 5xx/429 errors. A failing feed is logged and skipped. The run fails only if every feed fails.
- **Every feed returns only its newest items**: 20 on GlobeNewswire and PR Newswire, about 10 on Business Wire. On Sunday 4 Oct the 20 items in PR Newswire's all-news feed covered 17.6h. On a weekday the two firehoses (PRN all news, GNW public companies) will cover well under an hour. The topic feeds reach back much further, as the "20 items span" column shows. Hourly runs catch everything in the topic feeds. Catching every watchlist release that only reaches the firehoses needs runs every 15 to 30 minutes in US hours.

**GlobeNewswire** (19 RSS feeds; the full index is at https://www.globenewswire.com/rss/list). Each item carries its tickers as structured data, for example `<category domain=".../rss/stock">NYSE:MTUS</category>`, and the issuer in `dc:contributor`. Paths are relative to `https://www.globenewswire.com/RssFeed/`.

| Feed | Path | 20 items span (4 Oct) |
|---|---|---|
| Public companies (all listed issuers) | `orgclass/1/feedTitle/GlobeNewswire - News about Public Companies` | 40h |
| United States | `country/United States/feedTitle/...` | 25h |
| Business Contracts | `subjectcode/7-Business Contracts/...` | 33h |
| Mergers and Acquisitions | `subjectcode/27-Mergers And Acquisitions/...` | 11h |
| Dividend Reports | `subjectcode/12-Dividend Reports And Estimates/...` | 34h |
| Government News | `subjectcode/19-Government News/...` | 5 days |
| Corporate Action | `subjectcode/61-Corporate Action/...` | 4 days |
| Restructuring / Recapitalization | `subjectcode/37-Restructuring 2f Recapitalization/...` | 41 days |
| Financing Agreements | `subjectcode/17-Financing Agreements/...` | 50h |
| Clinical Study | `subjectcode/90-Clinical Study/...` | 27h |
| Industry: Defense | `industry/2717-Defense/...` | 17 days |
| Industry: Aerospace | `industry/2713-Aerospace/...` | 9 days |
| Industry: Iron & Steel | `industry/1757-Iron 26 Steel/...` | 62 days |
| Industry: Nonferrous Metals | `industry/1755-Nonferrous Metals/...` | 51 days |
| Industry: General Mining | `industry/1775-General Mining/...` | 14 days |
| Industry: Basic Materials | `industry/1000-Basic Materials/...` | 39h |
| Industry: Industrials | `industry/2000-Industrials/...` | 47h |
| Industry: Biotechnology | `industry/4573-Biotechnology/...` | 32h |
| Industry: Pharmaceuticals | `industry/4577-Pharmaceuticals/...` | 53h |

The `AtomFeed/...` variants also respond, but every entry's timestamp is the build time, so the collector uses RSS.

**PR Newswire** (16 RSS feeds; the index is at https://www.prnewswire.com/rss/). The issuer is in `dc:contributor`, and the ticker is in the opening sentence of the summary, for example "(NYSE: MTUS)". The summary is cut at about 300 characters, so a ticker placed late is occasionally missed. **An unknown path does not return 404**: it silently serves the all-news feed with an empty `<title>`, so check the channel title when adding a feed. Paths are relative to `https://www.prnewswire.com/rss/`.

| Feed | Path | 20 items span (4 Oct) |
|---|---|---|
| All news releases | `news-releases-list.rss` | 18h |
| Financial Services & Investing | `financial-services-latest-news/financial-services-latest-news-list.rss` | 46h |
| General Business | `general-business-latest-news/general-business-latest-news-list.rss` | 28h |
| Heavy Industry & Manufacturing | `heavy-industry-manufacturing-latest-news/heavy-industry-manufacturing-latest-news-list.rss` | 28h |
| Aerospace & Defense | `heavy-industry-manufacturing-latest-news/aerospace-defense-list.rss` | 41h |
| Contracts | `financial-services-latest-news/contracts-list.rss` | 27h |
| Acquisitions, Mergers and Takeovers | `financial-services-latest-news/acquisitions-mergers-and-takeovers-list.rss` | 46h |
| Dividends | `financial-services-latest-news/dividends-list.rss` | 43h |
| Stock Offering | `financial-services-latest-news/stock-offering-list.rss` | 72h |
| Earnings | `financial-services-latest-news/earnings-list.rss` | 52h |
| Mining & Metals | `energy-latest-news/mining-metals-list.rss` | 33h |
| Energy | `energy-latest-news/energy-latest-news-list.rss` | 47h |
| Health | `health-latest-news/health-latest-news-list.rss` | 29h |
| FDA Approval | `health-latest-news/fda-approval-list.rss` | 58h |
| Business Technology | `business-technology-latest-news/business-technology-latest-news-list.rss` | 42h |
| Policy & Public Interest | `policy-public-interest-latest-news/policy-public-interest-latest-news-list.rss` | 45h |

The other index feeds (consumer technology, entertainment, environment, multicultural, sports, telecoms, travel) also respond but are not used.

**Business Wire** (13 RSS feeds at `https://feed.businesswire.com/rss/home/?rss=<code>`)
- The codes are opaque. businesswire.com itself, including its feed directory, returns 403 to scripts, so the codes came from a third-party list of 147. **That list is badly mislabelled**: the code it calls "Defense: Contracts" is really "Energy: Alternative Energy". Every code used was therefore checked against the feed's own `<channel><title>`.
- Codes in use:
  - Merger/Acquisition `G1QFDERJXkJeEFtRWA==`
  - Manufacturing `G1QFDERJXkJeEFpTXA==`
  - Manufacturing: Aerospace `G1QFDERJXkJeGFNZXQ==`
  - Manufacturing: Steel `G1QFDERJXkJeGFNZWw==`
  - Manufacturing: Machine Tools, Metalworking & Metallurgy `G1QFDERJXkJaF1tQWA==`
  - Natural Resources: Mining/Minerals `G1QFDERJXkJeGFNYXQ==`
  - Energy: Oil/Gas `G1QFDERJXkJeGFNSVQ==`
  - Health: Pharmaceutical `G1QFDERJXkJeGFNWWg==`
  - Health: Oncology `G1QFDERJXkJeGFNWWQ==`
  - Professional Services: Banking `G1QFDERJXkJeGFNTXA==`
  - Professional Services: Business `G1QFDERJXkJaF1tQVQ==`
  - Communications: PR/IR `G1QFDERJXkJeGVpUWg==`
  - Public Policy/Government: Public Policy `G1QFDERJXkJeGVpTXA==`
- **None of the 147 codes is a Defense feed.** Business Wire defense releases are reached only through Aerospace, Manufacturing and M&A. This is the main gap.
- On Sunday 4 Oct most Business Wire feeds held 0 items, and the busiest held 10 (Pharmaceutical, spanning 12h). The feeds therefore look like a short rolling window. **Re-check the item counts on a weekday.**

**Official company IR feeds** (in `OFFICIAL_FEEDS`; the ticker is assigned in the config because the items carry no ticker text)
- Metallus (MTUS, NYSE): `https://investors.metallus.com/rss/PressRelease.aspx?LanguageId=1`. It holds the last 10 releases, back to Feb 2026, including the 29 Sep "$995 million contract ... initial $125 million delivery order".
- IR sites hosted by Q4 Inc. serve this same `/rss/PressRelease.aspx?LanguageId=1` path, so watchlist names on Q4 can be added the same way.
- Elmet's sites (www.elmetgroup.com, investors.elmetgroup.com) timed out from here, so no Elmet feed has been added yet.

**Deliberately not used**
- **ACCESS Newswire (formerly Accesswire)**: `https://www.accessnewswire.com/feed/rss2` and `/feed/atom` respond, but they are the company's own blog ("ACCESS Newswire Blog"), not client releases. The newsroom is HTML only, and no release feed was found.
- **TMX Newsfile**: the newsroom (`www.newsfilecorp.com/newsroom`) sits behind an AWS WAF JavaScript challenge (HTTP 202 plus a challenge page). That is bot protection, so it is not worked around. `feeds.newsfilecorp.com` answers "No data could be found." on every path tried. Its issuers are mostly Canadian (TSX, TSXV, CSE) in any case.
- **EQS News**: no public RSS was found; `/feed/` redirects to the homepage and the `/rss/` paths return HTML. Its issuers are mostly German and European.
- **Aggregators** (Yahoo Finance, Benzinga, Seeking Alpha, MarketWatch, Finviz, StockTitan, Barchart, Quantisnow and similar): they republish wire copy later, sometimes edited or summarised, so they are not primary.
- **Social media** (X/Twitter, StockTwits, Reddit): not primary, and full of rumour and paid promotion.
- **Paywalled newswires and terminals** (Bloomberg, LSEG/Reuters, Dow Jones Newswires, Benzinga Pro, The Fly): they need paid credentials that the Actions runner doesn't have, and their terms forbid redistributing the content.
- **Bigdata.com**: available only inside Claude sessions (as an MCP connector), not in GitHub Actions. Use it for manual cross-checks, not in the collector.
- **Third-party items on the wires themselves**: law-firm "investor alerts", class-action deadline notices and paid stock-promotion "news commentary" are dropped by the collector because they are not company-issued. On 4 Oct this was 16 items.
