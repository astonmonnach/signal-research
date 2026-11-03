# Stock dossiers
<!-- DEEP DIVE (hand-written; generators never touch this part) -->
*Hand-written index of the deep dives, 5 Oct 2026 (~16:00 UK). Each file's top section is the dossier; the AUTO part under it (status, timeline, ledger rows) is generated.*

**How to read the scores:**
- Scores use the METHOD card (`nth-order-pipeline/METHOD.md` stage 5): **≥8 write up, 5–7 watchlist, ≤4 kill**. **Any failed gate (G1–G5) means kill, whatever the score.**
- Supply-chain nodes (MTUS, ELMT, TWST) use the stock gates.
- Event-driven names use the mapping from `research/filings-2026-10-04/market-scan-deep.md`: payoff / certainty / coverage / date visibility / behavioural signal.
- Prices "found @" come from `ledger/ledger.csv`. "5 Oct" is intraday at ~11:00 ET.

## Open position
| ticker | one-line thesis | found @ | 5 Oct | verdict | score |
|---|---|---|---|---|---|
| [MTUS](MTUS.md) | Sole-source DLA HF-1 shell-steel IDIQ ($995M ceiling) with a **funded $125M first order** (~77% of 2025 A&D sales); +12 pts vs IWM since the award, still below the August high | 25 Sep @ $18.84 | ~$21.09 | **OWN** (trade #1; exit on a close < $17; thesis check at Q3 on 6 Nov) | **7/10** |

## Watchlist and ideas
| ticker | one-line thesis | found @ | 5 Oct | verdict | score |
|---|---|---|---|---|---|
| [ELMT](ELMT.md) | DoW bought **$200M of equity** and DLA guaranteed a **$150M minimum** on a $2B tungsten IDIQ. Priced in one day (+33%); IPO lock-up (68% of shares) ends ~19–22 Oct | 25 Sep @ $19.64 | ~$21.19 | **AVOID now; watch the lock-up supply** | 8/10, **G3 fail = kill** |
| [RYAM](RYAM.md) | Sale review to conclude in Q4 2026. AIP's rejected $11–12 bid; AIP holds 5% at $7.48 and is inside the process. Premium fully unwound | 28 Sep @ $8.15 | ~$7.10 | **WATCH** | **6/10** |
| [MOD](MOD.md) | Post-RMT data-centre cooling: customer prepaid **$165M** on a $4B+ capacity deal; Investor Day 18 Nov; possible S&P / GICS forced buyers | 30 Sep @ $187.20 | ~$185.05 | **WATCH** | 5/10 |
| [THRM](THRM.md) | 23.7M unwanted shares sent to MOD holders, against a **$400M buyback** (~22% of market cap) at ~6× EBITDA; ex-dividend date unclear | 29 Sep @ $33.92 | ~$32.90 | **AVOID (kill: closed $28.61 on 19 Oct, below the $28.92 line)** | 5/10 |
| [WHF](WHF.md) | BDC at **0.60× NAV** with a special committee exploring a sale; $85M of notes due in December force action | 28 Sep @ $6.97 | ~$7.04 | **WATCH** | 5/10 |
| [CTVA](CTVA.md) | The real forced seller of the Corteva split (S&P 500 → MidCap 400 at the 5 Oct close); ~5.7× EBITDA with an unquantified PFAS tail | 29 Sep @ $77.87 (pre-spin) | ~$12.12 | **tracked, no call** (20 Oct trigger rule: no dated trigger; the 5-session test ended about 13 Oct ungraded) | 4/10 (kill band) |
| [TWST](TWST.md) | The lock-up overhang was tested and absorbed (new high on 5 Oct); +530% YTD, ~31× sales | 30 Sep @ $193.24 | ~$199.98 | **AVOID** | 3/10 (G2, G3 fail) |
| [VYLR](VYLR.md) | Seed spin went straight into the S&P 500, so there is no forced seller; ~20× EBITDA | 1 Oct @ $68.26 | ~$69.39 | **tracked, no call** (20 Oct trigger rule: no dated trigger) | 2/10 (G3 fail) |
| [HMH](HMH.md) | Resale S-1 for 31.9M shares (2.6× the Class A float), **not yet effective**; test case for "buy after absorption" | 28 Sep @ $19.28 | ~$19.12 | **tracked, no call** (20 Oct trigger rule: no dated trigger; the overhang test continues as observation) | 2/10 |
| [CHDN](CHDN.md) | The logged "strategic alternatives" 8-K was a **refinancing** (false positive); the real casino-sale review dates from 29 Jul | 28 Sep @ $75.72 | ~$77.75 | **AVOID (kill)** | 1/10 (G4 fail as logged) |

## Setups (watch-only forward test, KNRX-like screen, logged 4 Oct)
| ticker | one-line status | found @ | 5 Oct | verdict | score |
|---|---|---|---|---|---|
| [GOVX](GOVX.md) | Already a Nasdaq **delisting determination** (no compliance period after a 1:25 split in Jan); hearing 13 Oct; the 27 Oct vote unlocks warrants equal to 113% of shares | $0.320 | ~$0.336 | AVOID | 6/10, G5 fail |
| [SNTI](SNTI.md) | Celadon control deal plus a 1:20–1:50 split, voted **8 Oct**; resale of note shares equal to 82% of outstanding | $0.322 | ~$0.323 | AVOID | 6/10, kill (certainty 0) |
| [DYAI](DYAI.md) | Small (9%) warrant resale; deficiency deadline 24 Mar 2027; a 2:1–10:1 split is already authorised | $0.460 | ~$0.467 | AVOID | 5/10, G5 fail |
| [GXAI](GXAI.md) | Warrant resale of 56% at $0.95; **trades below cash** (~$5.7M market cap vs ~$14M); no going-concern doubt | $0.516 | ~$0.497 | AVOID | 5/10, G5 fail |
| [VHUB](VHUB.md) | $100M equity line plus 5.3M shares paid to marketing and service firms; deadline 1 Mar 2027 | $0.480 | ~$0.458 | AVOID | 5/10, G5 fail |
| [FLD](FLD.md) | $25M Roth equity line equal to 94% of shares; 1:2–1:50 split vote 22 Oct | $0.541 | ~$0.569 | AVOID | 6/10, G5 fail |
| [GWH](GWH.md) | **NYSE suspended it 2 Oct; now OTC as GWHT** (~−41%); two delisting determinations; drop from the test | $0.157 (1 Oct) | ~$0.09 (GWHT) | AVOID | 6/10, G5 fail (OTC) |
| [HCTI](HCTI.md) | **Delisting determination, no compliance period** (cumulative splits of 1-for-14,940); hearing request due 8 Oct; the "EFFECT" was a no-new-shares POS AM; the spike already came on 23 Sep | $0.725 | ~$0.581 | AVOID | 6/10, G5 fail |
| [POLA](POLA.md) | Variable-price "death-spiral" converts equal to 201% of shares; equity deadline 28 Oct; split vote 14 Oct | $1.16 | ~$1.14 | AVOID | 6/10, G5 fail |
| [CYAB](CYAB.md) | Resale overhang of 123%, $794K cash; deficiency deadline 7 Dec | $0.200 | ~$0.208 | AVOID | 5/10, kill |

## Cross-cutting findings from this pass
- **The DLA stockpile pot is bigger on paper and tighter in cash.** Ceilings total ≈$4.0bn: Rio Tinto's $995M high-purity aluminium award, announced 25 Sep, was missing from the earlier ≈$3.0bn. That compares with $2bn appropriated under P.L. 119-21 §20004(a)(40). Committed money is MTUS's $125M order and ELMT's $150M minimum.
- **"Check the timestamp" catches:**
  - THRM's "−27% pre-priced" was measured from a one-day +26.5% spike.
  - TWST's "+349% this year" was measured from 28 Jan; YTD is +495% to 2 Oct.
  - GWH's "2 Oct close" is really the 1 Oct close.
  - CHDN and WHF catalysts were 2 months and 13 days old when found.
- **Scanner fixes:** ignore "strategic alternatives" when it appears only in a forward-looking paragraph (CHDN); don't count a POS AM as EFFECT supply (HCTI); check exchange status before logging (GWH).

<!-- AUTO (generated by reports/build_stocks.py; everything below is rewritten on each run) -->
# Stock dossiers

One file per stock: every ticker on the watchlist (`watch/watchlist.json`), in `ledger/manual_calls.csv` or in `journal/trades.csv`. The top of each file is a hand-written deep dive; everything below the AUTO marker (status, timeline of every dated mention, performance since found) is rebuilt by `reports/build_stocks.py` every weekday morning.

## Open positions

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [MTUS](MTUS.md) | Metallus Inc. | $20.58 (03 Nov) | +9.2% since 25 Sep | +5.3 pts | [2026-11-03](../scans/2026-11-03.md) |

## Watchlist

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [ACB](ACB.md) | Aurora Cannabis Inc | $5.11 (03 Nov) | +28.7% since 20 Oct | +26.9 pts | [2026-11-01](../scans/2026-11-01.md) |
| [ALEC](ALEC.md) | Alector, Inc. | $2.17 (03 Nov) | +17.9% since 16 Oct | +14.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ARTV](ARTV.md) | Artiva Biotherapeutics, Inc. | $4.19 (03 Nov) | -1.9% since 27 Oct | -3.9 pts | [2026-11-01](../scans/2026-11-01.md) |
| [BMBL](BMBL.md) | Bumble Inc. | $5.97 (03 Nov) | +0.4% since 13 Oct | -2.3 pts | [2026-10-29](../scans/2026-10-29.md) |
| [BMEZ](BMEZ.md) | BlackRock Health Sciences Term Trust | $17.52 (03 Nov) | +7.6% since 16 Oct | +4.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMM](BMM.md) | private placement [6-K](https://www.sec.gov/Archives/edgar/data/1732379/000155485526002139/ex991_1.htm) | $3.78 (03 Nov) | -12.1% since 20 Oct | -14.2 pts | [2026-11-03](../scans/2026-11-03.md) |
| [BORR](BORR.md) | Borr Drilling Ltd | $3.62 (03 Nov) | -26.7% since 12 Oct | -28.5 pts | [2026-11-02](../scans/2026-11-02.md) |
| [BYRN](BYRN.md) | Roth Adam L. (director) bought 15,000 shares at $4.69 = $70,375 on 2026-10-15 | $4.12 (03 Nov) | -14.9% since 18 Oct | -21.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CHDN](CHDN.md) | Churchill Downs Inc | $97.95 (03 Nov) | +29.4% since 28 Sep | +28.6 pts | [2026-11-02](../scans/2026-11-02.md) |
| [CPAC](CPAC.md) | Cementos Pacasmayo Saa | $12.75 (03 Nov) | +0.7% since 21 Oct | -1.4 pts | [2026-11-01](../scans/2026-11-01.md) |
| [CRMT](CRMT.md) | Americas Carmart Inc | $1.07 (03 Nov) | -14.4% since 08 Oct | -16.0 pts | [2026-11-02](../scans/2026-11-02.md) |
| [CSR](CSR.md) | Centerspace | $58.02 (03 Nov) | +6.6% since 07 Oct | +5.1 pts | [2026-11-03](../scans/2026-11-03.md) |
| [CTVA](CTVA.md) | Corteva, Inc. | $11.76 (03 Nov) | +622.2% since 29 Sep | +621.5 pts | [2026-10-23](../scans/2026-10-23.md) |
| [DIBS](DIBS.md) | 1stdibs.com, Inc., filed by Catsimatidis John A. Jr | $5.16 (03 Nov) | +20.0% since 20 Oct | +18.5 pts | [2026-10-22](../scans/2026-10-22.md) |
| [DOLE](DOLE.md) | Dole plc | $13.02 (03 Nov) | -3.1% since 23 Oct | -4.4 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ELMT](ELMT.md) | Elmet Group Co. | $23.21 (03 Nov) | +18.2% since 25 Sep | +20.5 pts | [2026-11-02](../scans/2026-11-02.md) |
| [ESRT](ESRT.md) | Empire State Realty Trust, Inc. | $5.06 (03 Nov) | +19.6% since 05 Oct | +18.9 pts | [2026-11-01](../scans/2026-11-01.md) |
| [FEAM](FEAM.md) | Weibel Paul Wesley III (Chief Executive Officer) bought 7,176 shares at $3.48 = $24,972 on 2026-10-08 | $2.20 (03 Nov) | -33.5% since 08 Oct | -33.5 pts | [2026-10-26](../scans/2026-10-26.md) |
| [GPRO](GPRO.md) | GoPro, Inc. | $0.959 (03 Nov) | -8.7% since 16 Oct | -18.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [HMH](HMH.md) | HMH Holding Inc | $17.33 (03 Nov) | -10.1% since 28 Sep | -8.4 pts | [2026-10-23](../scans/2026-10-23.md) |
| [IMMR](IMMR.md) | Singer Eric (director, President and CEO) bought 41,000 shares at $7.14 = $292,800 on 2026-10-07 | $7.04 (03 Nov) | -4.2% since 12 Oct | -5.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [IMSR](IMSR.md) | Terrestrial Energy Inc. /DE/ | $2.92 (03 Nov) | -9.2% since 15 Oct | -11.7 pts | [2026-11-01](../scans/2026-11-01.md) |
| [LCII](LCII.md) | Lci Industries | $101.39 (03 Nov) | +27.8% since 13 Oct | +26.2 pts | [2026-11-02](../scans/2026-11-02.md) |
| [MDA](MDA.md) | MDA Space Ltd. | $27.04 (03 Nov) | -1.9% since 14 Oct | -3.8 pts | [2026-10-30](../scans/2026-10-30.md) |
| [MG](MG.md) | Mistras Group, Inc. | $20.17 (03 Nov) | -2.4% since 15 Oct | -5.9 pts | [2026-11-02](../scans/2026-11-02.md) |
| [MOD](MOD.md) | Modine Manufacturing Co | $126.72 (03 Nov) | -24.9% since 30 Sep | -26.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MSGS](MSGS.md) | Madison Square Garden Sports Corp. | $310.15 (02 Nov) | +2.4% since 10 Oct | +1.0 pts | [2026-11-01](../scans/2026-11-01.md) |
| [NKLR](NKLR.md) | Terra Innovatum Global N.V. | $2.32 (03 Nov) |  |  | [2026-11-01](../scans/2026-11-01.md) |
| [NPB](NPB.md) | Northpointe Bancshares Inc | $15.88 (03 Nov) | -1.9% since 28 Oct | -3.3 pts | [2026-11-01](../scans/2026-11-01.md) |
| [PCRX](PCRX.md) | Pacira BioSciences, Inc. | $36.40 (03 Nov) | +0.0% since 08 Oct | -0.8 pts | [2026-11-01](../scans/2026-11-01.md) |
| [PED](PED.md) | Pedevco Corp | $15.85 (03 Nov) | +23.7% since 14 Oct | +18.1 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PTC](PTC.md) | Ptc Inc. | $194.32 (03 Nov) | +1.1% since 05 Oct | +1.9 pts | [2026-10-28](../scans/2026-10-28.md) |
| [PUSA](PUSA.md) | Aureus Greenway Holdings Inc | $1.69 (03 Nov) | -41.6% since 05 Oct | -42.6 pts | [2026-11-01](../scans/2026-11-01.md) |
| [RXO](RXO.md) | RXO, Inc. | $27.86 (03 Nov) | -2.8% since 05 Oct | -1.8 pts | [2026-11-01](../scans/2026-11-01.md) |
| [RYAM](RYAM.md) | Rayonier Advanced Materials Inc. | $6.70 (03 Nov) | -17.8% since 28 Sep | -18.0 pts | [2026-10-21](../scans/2026-10-21.md) |
| [SEER](SEER.md) | Seer, Inc. | $1.76 (03 Nov) | -9.3% since 29 Oct | -6.5 pts | [2026-11-02](../scans/2026-11-02.md) |
| [SKYA](SKYA.md) | SkyAI, Inc. | $2.94 (03 Nov) | +13.1% since 12 Oct | +16.1 pts | [2026-11-02](../scans/2026-11-02.md) |
| [SMTI](SMTI.md) | Sanara MedTech Inc. | $32.42 (03 Nov) | -2.2% since 16 Oct | -4.8 pts | [2026-11-01](../scans/2026-11-01.md) |
| [SRTA](SRTA.md) | Strata Critical Medical, Inc. | $4.57 (03 Nov) | +5.2% since 15 Oct | -1.6 pts | [2026-11-01](../scans/2026-11-01.md) |
| [SSTI](SSTI.md) | Soundthinking, Inc. | $8.35 (03 Nov) | +1.7% since 29 Sep | +1.4 pts | [2026-10-22](../scans/2026-10-22.md) |
| [SYNA](SYNA.md) | SYNAPTICS Inc | $117.90 (03 Nov) | -1.0% since 08 Oct | -2.7 pts | [2026-11-01](../scans/2026-11-01.md) |
| [TALO](TALO.md) | Talos Energy Inc. | $16.46 (03 Nov) | -3.4% since 14 Oct | -7.5 pts | [2026-11-02](../scans/2026-11-02.md) |
| [TCPC](TCPC.md) | BlackRock TCP Capital Corp. | $4.24 (03 Nov) | +3.9% since 14 Oct | +0.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [TENX](TENX.md) | Tenax Therapeutics, Inc. | $1.90 (03 Nov) | +8.0% since 22 Oct | +5.8 pts | [2026-10-30](../scans/2026-10-30.md) |
| [THRM](THRM.md) | Gentherm Inc | $30.93 (03 Nov) | -2.7% since 29 Sep | -3.4 pts | [2026-10-27](../scans/2026-10-27.md) |
| [TWST](TWST.md) | Twist Bioscience Corp | $136.17 (03 Nov) | -29.5% since 30 Sep | -30.8 pts | [2026-10-29](../scans/2026-10-29.md) |
| [ULBI](ULBI.md) | Ultralife Corp | $15.62 (03 Nov) | +0.1% since 28 Oct | +0.6 pts | [2026-11-02](../scans/2026-11-02.md) |
| [UUUU](UUUU.md) | Energy Fuels Inc | $7.38 (03 Nov) | -20.4% since 13 Oct | -20.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VYLR](VYLR.md) | Vylor Inc. | $72.62 (03 Nov) | +6.4% since 01 Oct | +6.2 pts | [2026-10-26](../scans/2026-10-26.md) |
| [WHF](WHF.md) | WhiteHorse Finance, Inc. | $8.14 (03 Nov) | +16.8% since 28 Sep | +16.9 pts | [2026-10-28](../scans/2026-10-28.md) |
| [XPOF](XPOF.md) | Xponential Fitness, Inc. | $4.74 (03 Nov) | -1.8% since 13 Oct | -3.9 pts | [2026-11-02](../scans/2026-11-02.md) |

## Setups (watch only)

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [AAON](AAON.md) | Aaon, Inc. | $70.73 (03 Nov) | -16.1% since 05 Oct | -15.9 pts | [2026-10-05](../scans/2026-10-05.md) |
| [ABEO](ABEO.md) | Abeona Therapeutics Inc. | $4.37 (03 Nov) | -0.7% since 23 Oct | -2.2 pts | [2026-11-02](../scans/2026-11-02.md) |
| [ACOG](ACOG.md) | Opaleye Management Inc. (10% owner) bought 36,940 shares at $8.35 = $308,576 on 2026-10-16 | $8.50 (03 Nov) | -1.3% since 20 Oct | -2.6 pts | [2026-11-03](../scans/2026-11-03.md) |
| [ACVA](ACVA.md) | ACV Auctions Inc. | $10.50 (16 Oct) | +0.6% since 29 Sep | +0.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ADSK](ADSK.md) | Autodesk, Inc. | $252.45 (03 Nov) | +9.2% since 06 Oct | +8.1 pts | [2026-10-06](../scans/2026-10-06.md) |
| [AEHL](AEHL.md) | Antelope Enterprise Holdings Ltd | $6.60 (03 Nov) | -25.5% since 23 Oct | -27.2 pts | [2026-10-29](../scans/2026-10-29.md) |
| [AGMB](AGMB.md) | Epstein David R (director) bought 10,000 shares at $8.88 = $88,800 on 2026-10-21 | $6.99 (03 Nov) | -22.7% since 23 Oct | -24.8 pts | [2026-10-23](../scans/2026-10-23.md) |
| [ALLO](ALLO.md) | Allogene Therapeutics, Inc. | $1.11 (03 Nov) | -14.6% since 28 Oct | -16.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [AMPY](AMPY.md) | Amplify Energy Corp. | $3.95 (03 Nov) | -8.9% since 14 Oct | -12.4 pts | [2026-10-14](../scans/2026-10-14.md) |
| [ASTS](ASTS.md) | AST SpaceMobile, Inc. | $38.20 (03 Nov) | -14.1% since 15 Oct | -13.6 pts | [2026-10-27](../scans/2026-10-27.md) |
| [ATKR](ATKR.md) | Atkore Inc. | $94.96 (16 Oct) | +0.1% since 07 Oct | -1.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [AZUL](AZUL.md) | Azul SA | $4.17 (03 Nov) | +3.0% since 26 Oct | -2.9 pts | [2026-10-27](../scans/2026-10-27.md) |
| [BCTX](BCTX.md) | going concern: "...in legislation and regulations may affect our ability to generate revenue and profitability ● There is substantial doubt about our ability to continue as a going concern ● We are dependent on our key personnel; ● We have an unproven market for our pr" | $3.17 (03 Nov) | +4.3% since 01 Nov | +3.5 pts | [2026-11-01](../scans/2026-11-01.md) |
| [BRUN](BRUN.md) | Boost Run Inc. | $7.44 (03 Nov) | -12.2% since 20 Oct | -17.4 pts | [2026-10-21](../scans/2026-10-21.md) |
| [BSY](BSY.md) | Bentley Systems Inc | $41.85 (03 Nov) | +16.4% since 06 Oct | +15.4 pts | [2026-11-03](../scans/2026-11-03.md) |
| [CABA](CABA.md) | Cabaletta Bio, Inc. | $1.49 (03 Nov) | -2.3% since 28 Oct | -3.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CABO](CABO.md) | Cable One, Inc., filed by GRAHAM DONALD | $4.99 (03 Nov) | -8.5% since 01 Nov | -6.4 pts | [2026-11-02](../scans/2026-11-02.md) |
| [CHRW](CHRW.md) | C. H. Robinson Worldwide, Inc. | $128.96 (03 Nov) | -8.3% since 05 Oct | -7.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CLF](CLF.md) | Cleveland-cliffs Inc. | $14.22 (03 Nov) | +16.6% since 05 Oct | +11.6 pts | [2026-10-27](../scans/2026-10-27.md) |
| [CPSH](CPSH.md) | Cps Technologies Corp/de/ | $3.60 (03 Nov) | +2.9% since 26 Oct | +1.5 pts | [2026-10-27](../scans/2026-10-27.md) |
| [CTEV](CTEV.md) | ARES MANAGEMENT LLC (10% owner) + ASOF II Holdings I, L.P. (10% owner) + ASOF II A (DE) Holdings I, L.P. (10% owner) + 1 more bought 70,834 shares at $23.69 = $1,678,106 on 2026-10-26 | $21.44 (03 Nov) | -6.8% since 28 Oct | -7.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CVX](CVX.md) | Chevron Corp | $226.66 (03 Nov) | +5.4% since 12 Oct | +3.4 pts | [2026-11-02](../scans/2026-11-02.md) |
| [CYAB](CYAB.md) | Cyabra, Inc. | $0.111 (03 Nov) | -44.8% since 04 Oct | -44.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [DFNS](DFNS.md) | T3 Defense Inc. | $3.56 (03 Nov) | -13.5% since 23 Oct | -16.2 pts | [2026-10-27](../scans/2026-10-27.md) |
| [DYAI](DYAI.md) | Dyadic International Inc | $0.370 (03 Nov) | -19.6% since 04 Oct | -19.2 pts | [2026-10-30](../scans/2026-10-30.md) |
| [FATE](FATE.md) | Fate Therapeutics Inc | $2.07 (03 Nov) | -4.6% since 28 Oct | -4.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [FLD](FLD.md) | Fold Holdings, Inc. | $0.570 (03 Nov) | +5.6% since 29 Sep | +6.3 pts | [2026-10-27](../scans/2026-10-27.md) |
| [FWDI](FWDI.md) | Forward Industries, Inc. | $6.18 (03 Nov) | -14.1% since 12 Oct | -13.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GOLD](GOLD.md) | Tether Global Investments Fund, S.I.C.A.F., S.A. (10% owner) + TPM, S.A. de C.V. (10% owner) + Devasini Giancarlo (10% owner) bought 100,000 shares at $39.27 = $3,927,258 on 2026-10-28 | $39.49 (03 Nov) | +3.8% since 01 Nov | +1.8 pts | [2026-11-02](../scans/2026-11-02.md) |
| [GOVX](GOVX.md) | GeoVax Labs, Inc. | $0.170 (03 Nov) | -46.9% since 04 Oct | -48.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [GRND](GRND.md) | Grindr Inc. | $12.87 (03 Nov) | -16.8% since 13 Oct | -19.1 pts | [2026-11-03](../scans/2026-11-03.md) |
| [GRNT](GRNT.md) | Granite Ridge Resources, Inc. | $5.18 (03 Nov) | +4.9% since 14 Oct | +0.1 pts | [2026-10-14](../scans/2026-10-14.md) |
| [GRRR](GRRR.md) | securities purchase agreement, going private, tender offer [6-K](https://www.sec.gov/Archives/edgar/data/1903145/000121390026114094/ea0310294-6k_gorilla.htm) | $7.82 (03 Nov) | +3.7% since 01 Nov | +3.2 pts | [2026-11-02](../scans/2026-11-02.md) |
| [GTBP](GTBP.md) | GT Biopharma, Inc. | $5.24 (03 Nov) | -21.6% since 09 Oct | -23.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [GWH](GWH.md) | ESS Tech, Inc. | $0.065 (02 Nov) | -58.6% since 04 Oct | -49.6 pts | [2026-10-27](../scans/2026-10-27.md) |
| [GXAI](GXAI.md) | Gaxos.ai Inc. | $0.436 (03 Nov) | -15.5% since 04 Oct | -10.8 pts | [2026-10-04](../scans/2026-10-04.md) |
| [HCTI](HCTI.md) | Healthcare Triangle, Inc. | $5.92 (03 Nov) | -59.2% since 02 Oct | -50.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [HESM](HESM.md) | Hess Midstream LP, filed by Hess Investments North Dakota LLC | $33.11 (03 Nov) | +2.3% since 12 Oct | +1.6 pts | [2026-10-30](../scans/2026-10-30.md) |
| [HUBG](HUBG.md) | Hub Group, Inc. | $27.28 (03 Nov) | -3.1% since 06 Oct | -2.7 pts | [2026-10-06](../scans/2026-10-06.md) |
| [IBRX](IBRX.md) | ImmunityBio, Inc. | $8.35 (03 Nov) | -5.2% since 28 Oct | -4.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [INVE](INVE.md) | INVE Technologies, Inc. | $2.68 (03 Nov) | -3.6% since 21 Oct | -6.2 pts | [2026-11-02](../scans/2026-11-02.md) |
| [IPW](IPW.md) | iPower Inc. | $1.56 (03 Nov) | -67.6% since 16 Oct | -73.1 pts | [2026-11-01](../scans/2026-11-01.md) |
| [JBHT](JBHT.md) | Hunt J B Transport Services Inc | $223.98 (03 Nov) | -0.9% since 06 Oct | -0.7 pts | [2026-10-06](../scans/2026-10-06.md) |
| [KOS](KOS.md) | Kosmos Energy Ltd. | $2.52 (03 Nov) | -7.2% since 14 Oct | -11.7 pts | [2026-11-02](../scans/2026-11-02.md) |
| [KYTX](KYTX.md) | Kyverna Therapeutics, Inc., filed by HIRSCHMAN ORIN | $5.34 (03 Nov) | -9.3% since 28 Oct | -9.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [LEE](LEE.md) | LEE ENTERPRISES, Inc | $6.01 (02 Nov) | -1.8% since 30 Oct | -1.5 pts | [2026-11-02](../scans/2026-11-02.md) |
| [LEO](LEO.md) | Saba Capital Management, L.P. (10% owner) bought 65,000 shares at $5.68 = $369,200 on 2026-10-23 | $5.93 (03 Nov) | +0.1% since 27 Oct | -0.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [LEU](LEU.md) | Centrus Energy Corp | $96.89 (03 Nov) | -23.7% since 15 Oct | -23.6 pts | [2026-10-22](../scans/2026-10-22.md) |
| [LSTR](LSTR.md) | Landstar System Inc | $147.05 (03 Nov) | -13.0% since 06 Oct | -12.8 pts | [2026-10-27](../scans/2026-10-27.md) |
| [LYCA](LYCA.md) | Venrock Healthcare Capital Partners III, L.P. (10% owner) + VHCP Co-Investment Holdings III, LLC (10% owner) + VHCP Management III, LLC (10% owner) + 6 more bought 2,045,440 shares at $18.41 = $37,653,863 on 2026-10-27 | $27.29 (03 Nov) | -9.0% since 23 Oct | +13.3 pts | [2026-10-30](../scans/2026-10-30.md) |
| [MDT](MDT.md) | Medtronic plc | $99.10 (03 Nov) | +12.9% since 08 Oct | +11.0 pts | [2026-10-15](../scans/2026-10-15.md) |
| [MDXG](MDXG.md) | Mimedx Group, Inc. | $3.21 (03 Nov) | -27.4% since 16 Oct | -30.9 pts | [2026-10-18](../scans/2026-10-18.md) |
| [MEDS](MEDS.md) | DataMeds AI, Inc. | $1.69 (03 Nov) | -38.5% since 20 Oct | -38.9 pts | [2026-10-27](../scans/2026-10-27.md) |
| [MFIC](MFIC.md) | MidCap Financial Investment Corp | $10.30 (03 Nov) | +0.3% since 27 Oct | +0.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MP](MP.md) | MP Materials Corp. / DE | $38.29 (03 Nov) | -18.2% since 05 Oct | -18.0 pts | [2026-10-27](../scans/2026-10-27.md) |
| [MTCH](MTCH.md) | Match Group, Inc. | $39.72 (03 Nov) | -6.2% since 13 Oct | -9.1 pts | [2026-11-03](../scans/2026-11-03.md) |
| [MVIS](MVIS.md) | going concern: "...when analyzed in the aggregate in accordance with Accounting Standards Codification (“ASC”) 205-40, raises substantial doubt about the Company’s ability to continue as a going concern through at least twelve months from the date the condensed consolidate" | $1.27 (03 Nov) | -5.9% since 01 Nov | -7.7 pts | [2026-11-02](../scans/2026-11-02.md) |
| [NAUT](NAUT.md) | Nautilus Biotechnology, Inc. | $2.35 (03 Nov) | -18.8% since 27 Oct | -22.0 pts | [2026-10-30](../scans/2026-10-30.md) |
| [NCT](NCT.md) | Intercont (Cayman) Ltd | $1.41 (02 Nov) | -4.7% since 26 Oct | -10.1 pts | [2026-11-02](../scans/2026-11-02.md) |
| [NE](NE.md) | Noble Corp plc | $45.26 (03 Nov) | +5.4% since 12 Oct | +2.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [NIVF](NIVF.md) | private placement, securities purchase agreement, merger agreement [6-K](https://www.sec.gov/Archives/edgar/data/1981662/000121390026112647/ea030961701ex99-1.htm) | $0.850 (03 Nov) | -63.1% since 29 Sep | -84.4 pts | [2026-11-02](../scans/2026-11-02.md) |
| [NKTX](NKTX.md) | Nkarta, Inc. | $1.57 (03 Nov) | -9.0% since 28 Oct | -9.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NNBR](NNBR.md) | Nn Inc | $3.72 (03 Nov) | +10.9% since 26 Oct | +8.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NNE](NNE.md) | Nano Nuclear Energy Inc.: SEC staff letter dated 2025-08-21 | $11.48 (03 Nov) | -26.5% since 02 Oct | -26.5 pts | [2026-10-15](../scans/2026-10-15.md) |
| [NWCL](NWCL.md) | newcleo plc | $4.42 (03 Nov) | -7.0% since 19 Oct | -11.4 pts | [2026-11-02](../scans/2026-11-02.md) |
| [OKLO](OKLO.md) | Oklo Inc. | $23.69 (03 Nov) | -21.1% since 15 Oct | -21.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [OSTX](OSTX.md) | OS Therapies Inc: sold $7,172,429 of $12,282,478 | $1.21 (03 Nov) | -0.4% since 26 Oct | -2.3 pts | [2026-10-26](../scans/2026-10-26.md) |
| [PATK](PATK.md) | Patrick Industries Inc | $81.04 (03 Nov) | +26.0% since 13 Oct | +25.7 pts | [2026-11-03](../scans/2026-11-03.md) |
| [PCOR](PCOR.md) | Procore Technologies, Inc. | $62.25 (03 Nov) | +14.4% since 06 Oct | +14.2 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PL](PL.md) | Planet Labs PBC | $13.53 (03 Nov) | -6.9% since 15 Oct | -7.3 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PMI](PMI.md) | Picard Medical, Inc. | $8.19 (03 Nov) | +15.6% since 23 Oct | +13.1 pts | [2026-10-29](../scans/2026-10-29.md) |
| [POLA](POLA.md) | Polar Power, Inc. | $0.519 (03 Nov) | -58.8% since 28 Sep | -59.7 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PRTA](PRTA.md) | SCULLY WILLIAM P (10% owner) bought 150,000 shares at $8.15 = $1,222,045 on 2026-10-23 | $8.39 (03 Nov) | -4.8% since 27 Oct | -3.1 pts | [2026-10-30](../scans/2026-10-30.md) |
| [PZZA](PZZA.md) | PAPA JOHNS INTERNATIONAL INC, filed by Norbel Investments, S.L. | $18.72 (03 Nov) | +2.6% since 21 Oct | -0.6 pts | [2026-10-21](../scans/2026-10-21.md) |
| [RAPP](RAPP.md) | Sanchez Ramiro (director) bought 3,600 shares at $27.35 = $98,478 on 2026-10-23 | $25.57 (03 Nov) | +0.9% since 26 Oct | +0.8 pts | [2026-10-30](../scans/2026-10-30.md) |
| [RENT](RENT.md) | Nexus Capital Management LP (director, 10% owner) + Gateway Runway, LLC (director, 10% owner) + Gateway Runway Intermediate Holdings, Inc. (director, 10% owner) + 7 more bought 632,922 shares at $3.55 = $2,246,873 on 2026-10-21 | $2.38 (03 Nov) | -15.6% since 26 Oct | -18.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [RIG](RIG.md) | Transocean Ltd. | $6.05 (03 Nov) | +8.1% since 12 Oct | +6.3 pts | [2026-10-26](../scans/2026-10-26.md) |
| [RKLB](RKLB.md) | Rocket Lab Corp | $54.46 (03 Nov) | -1.4% since 15 Oct | -2.0 pts | [2026-11-02](../scans/2026-11-02.md) |
| [SAMG](SAMG.md) | Equinox Partners Investment Management LLC (10% owner) + EQUINOX PARTNERS LP (10% owner) bought 34,126 shares at $10.33 = $352,684 on 2026-10-22 | $10.87 (03 Nov) | +4.2% since 26 Oct | +3.7 pts | [2026-10-29](../scans/2026-10-29.md) |
| [SANA](SANA.md) | Sana Biotechnology, Inc. | $2.46 (03 Nov) | -6.3% since 28 Oct | -6.6 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SBGSY](SBGSY.md) | SBGSY | $53.82 (03 Nov) | -7.5% since 06 Oct | -6.1 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SDRL](SDRL.md) | SEADRILL Ltd, filed by Elliott Investment Management L.P. | $47.52 (03 Nov) | +1.1% since 12 Oct | -3.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [SGRY](SGRY.md) | Surgery Partners, Inc. | $23.21 (03 Nov) | -0.2% since 26 Oct | -1.0 pts | [2026-10-29](../scans/2026-10-29.md) |
| [SMR](SMR.md) | NUSCALE POWER Corp | $5.39 (03 Nov) | -12.4% since 15 Oct | -11.9 pts | [2026-10-15](../scans/2026-10-15.md) |
| [SNTI](SNTI.md) | Senti Biosciences Holdings, Inc. | $0.180 (03 Nov) | -44.2% since 04 Oct | -41.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [STC](STC.md) | EPPINGER FREDERICK H (director, Chief Executive Officer) bought 3,000 shares at $44.45 = $133,350 on 2026-10-26 | $45.01 (03 Nov) | +1.6% since 28 Oct | +0.9 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SWBI](SWBI.md) | Smith & Wesson Brands, Inc. | $13.30 (03 Nov) | -11.9% since 21 Oct | -14.1 pts | [2026-10-29](../scans/2026-10-29.md) |
| [THO](THO.md) | Thor Industries Inc | $77.99 (03 Nov) | +19.1% since 14 Oct | +13.0 pts | [2026-10-14](../scans/2026-10-14.md) |
| [TKNO](TKNO.md) | Alpha Teknova, Inc. | $7.29 (03 Nov) | +24.6% since 21 Oct | +28.0 pts | [2026-10-27](../scans/2026-10-27.md) |
| [TMCR](TMCR.md) | Metals Royalty Co Inc. | $2.29 (03 Nov) | +8.0% since 23 Oct | +4.8 pts | [2026-10-26](../scans/2026-10-26.md) |
| [TNON](TNON.md) | Tenon Medical, Inc. | $2.01 (03 Nov) | -30.4% since 13 Oct | -31.5 pts | [2026-10-26](../scans/2026-10-26.md) |
| [TONX](TONX.md) | TON Strategy Co, filed by Stotz Manuel | $2.96 (03 Nov) | -11.6% since 28 Oct | -9.8 pts | [2026-10-28](../scans/2026-10-28.md) |
| [TTMI](TTMI.md) | Ali Wajid (director) bought 10,000 shares at $90.25 = $902,460 on 2026-10-28 | $83.56 (03 Nov) | +0.8% since 01 Nov | -0.6 pts | [2026-11-01](../scans/2026-11-01.md) |
| [UAMY](UAMY.md) | United States Antimony Corp | $2.86 (03 Nov) | -27.6% since 05 Oct | -27.6 pts | [2026-10-28](../scans/2026-10-28.md) |
| [UMAC](UMAC.md) | Unusual Machines, Inc. | $14.98 (03 Nov) | -23.8% since 12 Oct | -23.5 pts | [2026-10-26](../scans/2026-10-26.md) |
| [VAL](VAL.md) | Valaris Ltd | $91.94 (03 Nov) | +8.2% since 12 Oct | +5.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [VHUB](VHUB.md) | VenHub Global, Inc. | $0.233 (03 Nov) | -51.4% since 04 Oct | -46.6 pts | [2026-10-04](../scans/2026-10-04.md) |
| [VRA](VRA.md) | Vera Bradley, Inc., filed by ROYCE & ASSOCIATES LP | $6.80 (03 Nov) | +11.1% since 22 Oct | +9.3 pts | [2026-10-22](../scans/2026-10-22.md) |
| [VREX](VREX.md) | Varex Imaging Corp | $18.55 (03 Nov) | +0.7% since 22 Oct | -1.5 pts | [2026-10-30](../scans/2026-10-30.md) |
| [VRT](VRT.md) | Vertiv Holdings Co | $238.87 (03 Nov) | -5.8% since 05 Oct | -4.4 pts | [2026-10-27](../scans/2026-10-27.md) |
| [WGO](WGO.md) | Winnebago Industries Inc | $31.68 (03 Nov) | +37.2% since 14 Oct | +31.4 pts | [2026-10-23](../scans/2026-10-23.md) |
| [WORX](WORX.md) | SCWorx Corp. | $1.40 (03 Nov) | -74.6% since 05 Oct | -74.2 pts | [2026-10-29](../scans/2026-10-29.md) |
| [WTI](WTI.md) | W&t Offshore Inc | $3.65 (03 Nov) | +0.1% since 14 Oct | -3.1 pts | [2026-10-29](../scans/2026-10-29.md) |
| [XRPN](XRPN.md) | Evernorth Holdings Inc. | $12.05 (03 Nov) | -29.5% since 09 Oct | -28.6 pts | [2026-11-02](../scans/2026-11-02.md) |
| [ZURA](ZURA.md) | Zura Bio Ltd | $4.03 (03 Nov) | -7.4% since 28 Oct | -6.8 pts | [2026-10-28](../scans/2026-10-28.md) |
