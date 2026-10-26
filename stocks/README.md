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
| [MTUS](MTUS.md) | Metallus Inc. | $20.50 (26 Oct) | +8.8% since 25 Sep | +5.8 pts | [2026-10-23](../scans/2026-10-23.md) |

## Watchlist

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [ACB](ACB.md) | Aurora Cannabis Inc | $3.88 (26 Oct) | -2.1% since 20 Oct | -3.0 pts | [2026-10-22](../scans/2026-10-22.md) |
| [ALEC](ALEC.md) | Alector, Inc. | $1.90 (26 Oct) | +3.3% since 16 Oct | +0.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMBL](BMBL.md) | Bumble Inc. | $5.95 (26 Oct) | +0.1% since 13 Oct | -1.8 pts | [2026-10-21](../scans/2026-10-21.md) |
| [BMEZ](BMEZ.md) | BlackRock Health Sciences Term Trust | $16.86 (26 Oct) | +3.5% since 16 Oct | +0.9 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMM](BMM.md) | private placement [6-K](https://www.sec.gov/Archives/edgar/data/1732379/000155485526002139/ex991_1.htm) | $3.92 (26 Oct) | -8.8% since 20 Oct | -10.1 pts | [2026-10-22](../scans/2026-10-22.md) |
| [BORR](BORR.md) | Borr Drilling Ltd | $4.07 (26 Oct) | -17.6% since 12 Oct | -18.6 pts | [2026-10-26](../scans/2026-10-26.md) |
| [BYRN](BYRN.md) | Roth Adam L. (director) bought 15,000 shares at $4.69 = $70,375 on 2026-10-15 | $4.84 (26 Oct) | +0.0% since 18 Oct | -6.4 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CHDN](CHDN.md) | Churchill Downs Inc | $84.51 (26 Oct) | +11.6% since 28 Sep | +11.8 pts | [2026-09-28](../scans/2026-09-28.md) |
| [CPAC](CPAC.md) | Cementos Pacasmayo Saa | $12.79 (26 Oct) | +1.0% since 21 Oct | -0.2 pts | [2026-10-23](../scans/2026-10-23.md) |
| [CRMT](CRMT.md) | Americas Carmart Inc | $0.721 (26 Oct) | -42.3% since 08 Oct | -42.9 pts | [2026-10-23](../scans/2026-10-23.md) |
| [CSR](CSR.md) | Centerspace | $57.08 (26 Oct) | +4.9% since 07 Oct | +4.2 pts | [2026-10-21](../scans/2026-10-21.md) |
| [CTVA](CTVA.md) | Corteva, Inc. | $12.42 (26 Oct) | +621.7% since 29 Sep | +621.9 pts | [2026-10-23](../scans/2026-10-23.md) |
| [DIBS](DIBS.md) | 1stdibs.com, Inc., filed by Catsimatidis John A. Jr | $4.55 (26 Oct) | +5.9% since 20 Oct | +5.3 pts | [2026-10-22](../scans/2026-10-22.md) |
| [DOLE](DOLE.md) | Dole plc | $13.30 (26 Oct) | -1.0% since 23 Oct | -1.4 pts | [2026-10-23](../scans/2026-10-23.md) |
| [ELMT](ELMT.md) | Elmet Group Co. | $22.40 (26 Oct) | +14.1% since 25 Sep | +17.1 pts | [2026-10-23](../scans/2026-10-23.md) |
| [ESRT](ESRT.md) | Empire State Realty Trust, Inc. | $5.03 (26 Oct) | +19.0% since 05 Oct | +19.2 pts | [2026-10-20](../scans/2026-10-20.md) |
| [FEAM](FEAM.md) | Weibel Paul Wesley III (Chief Executive Officer) bought 7,176 shares at $3.48 = $24,972 on 2026-10-08 | $2.35 (26 Oct) | -29.0% since 08 Oct | -28.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GPRO](GPRO.md) | GoPro, Inc. | $1.01 (26 Oct) | -3.3% since 16 Oct | -12.2 pts | [2026-10-21](../scans/2026-10-21.md) |
| [HMH](HMH.md) | HMH Holding Inc | $18.64 (26 Oct) | -3.4% since 28 Sep | -0.6 pts | [2026-10-23](../scans/2026-10-23.md) |
| [IMMR](IMMR.md) | Singer Eric (director, President and CEO) bought 41,000 shares at $7.14 = $292,800 on 2026-10-07 | $7.20 (26 Oct) | -2.0% since 12 Oct | -2.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [IMSR](IMSR.md) | Terrestrial Energy Inc. /DE/ | $2.93 (26 Oct) | -9.1% since 15 Oct | -10.8 pts | [2026-10-22](../scans/2026-10-22.md) |
| [LCII](LCII.md) | Lci Industries | $86.11 (26 Oct) | +8.5% since 13 Oct | +7.6 pts | [2026-10-22](../scans/2026-10-22.md) |
| [MDA](MDA.md) | MDA Space Ltd. | $28.22 (26 Oct) | +2.4% since 14 Oct | +1.4 pts | [2026-10-19](../scans/2026-10-19.md) |
| [MG](MG.md) | Mistras Group, Inc. | $21.44 (26 Oct) | +3.7% since 15 Oct | +1.1 pts | [2026-10-21](../scans/2026-10-21.md) |
| [MOD](MOD.md) | Modine Manufacturing Co | $135.05 (26 Oct) | -20.9% since 30 Sep | -21.5 pts | [2026-10-21](../scans/2026-10-21.md) |
| [MSGS](MSGS.md) | Madison Square Garden Sports Corp. | $389.63 (26 Oct) | -3.1% since 10 Oct | -3.6 pts | [2026-10-21](../scans/2026-10-21.md) |
| [NKLR](NKLR.md) | Terra Innovatum Global N.V. | $2.08 (26 Oct) |  |  | [2026-10-19](../scans/2026-10-19.md) |
| [PCRX](PCRX.md) | Pacira BioSciences, Inc. | $36.41 (26 Oct) | +0.1% since 08 Oct | +0.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [PED](PED.md) | Pedevco Corp | $15.38 (26 Oct) | +20.1% since 14 Oct | +15.3 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PTC](PTC.md) | Ptc Inc. | $193.96 (26 Oct) | +0.9% since 05 Oct | +2.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [PUSA](PUSA.md) | Aureus Greenway Holdings Inc | $2.04 (26 Oct) | -29.7% since 05 Oct | -30.3 pts | [2026-10-23](../scans/2026-10-23.md) |
| [RXO](RXO.md) | RXO, Inc. | $28.80 (26 Oct) | +0.5% since 05 Oct | +2.3 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RYAM](RYAM.md) | Rayonier Advanced Materials Inc. | $6.74 (26 Oct) | -17.4% since 28 Sep | -16.7 pts | [2026-10-21](../scans/2026-10-21.md) |
| [SKYA](SKYA.md) | SkyAI, Inc. | $2.89 (26 Oct) | +11.2% since 12 Oct | +15.0 pts | [2026-10-21](../scans/2026-10-21.md) |
| [SMTI](SMTI.md) | Sanara MedTech Inc. | $32.78 (26 Oct) | -1.2% since 16 Oct | -2.8 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SRTA](SRTA.md) | Strata Critical Medical, Inc. | $4.77 (26 Oct) | +9.9% since 15 Oct | +3.8 pts | [2026-10-23](../scans/2026-10-23.md) |
| [SSTI](SSTI.md) | Soundthinking, Inc. | $8.36 (26 Oct) | +1.9% since 29 Sep | +2.5 pts | [2026-10-22](../scans/2026-10-22.md) |
| [SYNA](SYNA.md) | SYNAPTICS Inc | $117.64 (26 Oct) | -1.2% since 08 Oct | -2.0 pts | [2026-10-22](../scans/2026-10-22.md) |
| [TALO](TALO.md) | Talos Energy Inc. | $18.55 (26 Oct) | +8.9% since 14 Oct | +5.6 pts | [2026-10-22](../scans/2026-10-22.md) |
| [TCPC](TCPC.md) | BlackRock TCP Capital Corp. | $3.99 (26 Oct) | -2.2% since 14 Oct | -4.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [TENX](TENX.md) | Tenax Therapeutics, Inc. | $1.67 (26 Oct) | -5.1% since 22 Oct | -6.4 pts | [2026-10-23](../scans/2026-10-23.md) |
| [THRM](THRM.md) | Gentherm Inc | $29.26 (26 Oct) | -7.6% since 29 Sep | -7.5 pts | [2026-10-23](../scans/2026-10-23.md) |
| [TWST](TWST.md) | Twist Bioscience Corp | $146.54 (26 Oct) | -24.2% since 30 Sep | -24.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [UUUU](UUUU.md) | Energy Fuels Inc | $7.66 (26 Oct) | -17.4% since 13 Oct | -16.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VYLR](VYLR.md) | Vylor Inc. | $71.90 (26 Oct) | +5.3% since 01 Oct | +6.0 pts | [2026-10-22](../scans/2026-10-22.md) |
| [WHF](WHF.md) | WhiteHorse Finance, Inc. | $7.88 (26 Oct) | +13.0% since 28 Sep | +13.9 pts | [2026-10-20](../scans/2026-10-20.md) |
| [XPOF](XPOF.md) | Xponential Fitness, Inc. | $4.17 (26 Oct) | -13.5% since 13 Oct | -14.8 pts | [2026-10-22](../scans/2026-10-22.md) |

## Setups (watch only)

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [AAON](AAON.md) | Aaon, Inc. | $70.47 (26 Oct) | -16.5% since 05 Oct | -15.4 pts | [2026-10-05](../scans/2026-10-05.md) |
| [ACOG](ACOG.md) | Opaleye Management Inc. (10% owner) bought 36,940 shares at $8.35 = $308,576 on 2026-10-16 | $8.25 (26 Oct) | -4.2% since 20 Oct | -4.7 pts | [2026-10-20](../scans/2026-10-20.md) |
| [ACVA](ACVA.md) | ACV Auctions Inc. | $10.50 (16 Oct) | +0.6% since 29 Sep | +1.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [ADSK](ADSK.md) | Autodesk, Inc. | $248.87 (26 Oct) | +7.6% since 06 Oct | +7.5 pts | [2026-10-06](../scans/2026-10-06.md) |
| [AEHL](AEHL.md) | Antelope Enterprise Holdings Ltd | $8.08 (26 Oct) | -8.8% since 23 Oct | -9.7 pts | [2026-10-23](../scans/2026-10-23.md) |
| [AGMB](AGMB.md) | Epstein David R (director) bought 10,000 shares at $8.88 = $88,800 on 2026-10-21 | $9.33 (26 Oct) | +3.1% since 23 Oct | +1.7 pts | [2026-10-23](../scans/2026-10-23.md) |
| [AMPY](AMPY.md) | Amplify Energy Corp. | $4.50 (26 Oct) | +3.7% since 14 Oct | +1.1 pts | [2026-10-14](../scans/2026-10-14.md) |
| [ASTS](ASTS.md) | AST SpaceMobile, Inc. | $40.23 (26 Oct) | -9.5% since 15 Oct | -8.0 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ATKR](ATKR.md) | Atkore Inc. | $94.96 (16 Oct) | +0.1% since 07 Oct | -0.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BRUN](BRUN.md) | Boost Run Inc. | $7.70 (26 Oct) | -9.2% since 20 Oct | -13.7 pts | [2026-10-21](../scans/2026-10-21.md) |
| [BSY](BSY.md) | Bentley Systems Inc | $39.83 (26 Oct) | +10.7% since 06 Oct | +10.6 pts | [2026-10-08](../scans/2026-10-08.md) |
| [CHRW](CHRW.md) | C. H. Robinson Worldwide, Inc. | $141.01 (26 Oct) | +0.3% since 05 Oct | +2.2 pts | [2026-10-06](../scans/2026-10-06.md) |
| [CLF](CLF.md) | Cleveland-cliffs Inc. | $13.97 (26 Oct) | +14.5% since 05 Oct | +10.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CVX](CVX.md) | Chevron Corp | $232.63 (26 Oct) | +8.2% since 12 Oct | +7.0 pts | [2026-10-12](../scans/2026-10-12.md) |
| [CYAB](CYAB.md) | Cyabra, Inc. | $0.132 (26 Oct) | -34.0% since 04 Oct | -32.8 pts | [2026-10-20](../scans/2026-10-20.md) |
| [DYAI](DYAI.md) | Dyadic International Inc | $0.441 (26 Oct) | -4.1% since 04 Oct | -2.9 pts | [2026-10-15](../scans/2026-10-15.md) |
| [FLD](FLD.md) | Fold Holdings, Inc. | $0.512 (26 Oct) | -5.2% since 29 Sep | -3.7 pts | [2026-10-04](../scans/2026-10-04.md) |
| [FWDI](FWDI.md) | Forward Industries, Inc. | $6.78 (26 Oct) | -5.8% since 12 Oct | -4.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GOVX](GOVX.md) | GeoVax Labs, Inc. | $0.190 (26 Oct) | -40.6% since 04 Oct | -41.1 pts | [2026-10-04](../scans/2026-10-04.md) |
| [GRND](GRND.md) | Grindr Inc. | $13.51 (26 Oct) | -12.7% since 13 Oct | -14.1 pts | [2026-10-13](../scans/2026-10-13.md) |
| [GRNT](GRNT.md) | Granite Ridge Resources, Inc. | $5.85 (26 Oct) | +18.4% since 14 Oct | +14.4 pts | [2026-10-14](../scans/2026-10-14.md) |
| [GTBP](GTBP.md) | GT Biopharma, Inc. | $5.27 (26 Oct) | -21.1% since 09 Oct | -22.4 pts | [2026-10-22](../scans/2026-10-22.md) |
| [GWH](GWH.md) | ESS Tech, Inc. | $0.070 (23 Oct) | -55.4% since 04 Oct | -44.9 pts | [2026-10-04](../scans/2026-10-04.md) |
| [GXAI](GXAI.md) | Gaxos.ai Inc. | $0.440 (26 Oct) | -14.7% since 04 Oct | -9.2 pts | [2026-10-04](../scans/2026-10-04.md) |
| [HCTI](HCTI.md) | Healthcare Triangle, Inc. | $7.31 (26 Oct) | live since 02 Oct | +5.9 pts | [2026-10-22](../scans/2026-10-22.md) |
| [HESM](HESM.md) | Hess Midstream LP, filed by Hess Investments North Dakota LLC | $31.19 (26 Oct) | -3.6% since 12 Oct | -3.5 pts | [2026-10-22](../scans/2026-10-22.md) |
| [HUBG](HUBG.md) | Hub Group, Inc. | $25.84 (26 Oct) | -8.2% since 06 Oct | -7.0 pts | [2026-10-06](../scans/2026-10-06.md) |
| [INVE](INVE.md) | INVE Technologies, Inc. | $2.74 (26 Oct) | -1.4% since 21 Oct | -3.1 pts | [2026-10-22](../scans/2026-10-22.md) |
| [JBHT](JBHT.md) | Hunt J B Transport Services Inc | $227.07 (26 Oct) | +0.5% since 06 Oct | +1.5 pts | [2026-10-06](../scans/2026-10-06.md) |
| [KOS](KOS.md) | Kosmos Energy Ltd. | $2.88 (26 Oct) | +6.5% since 14 Oct | +2.7 pts | [2026-10-14](../scans/2026-10-14.md) |
| [LEU](LEU.md) | Centrus Energy Corp | $102.02 (26 Oct) | -19.7% since 15 Oct | -18.6 pts | [2026-10-22](../scans/2026-10-22.md) |
| [LSTR](LSTR.md) | Landstar System Inc | $167.12 (26 Oct) | -1.1% since 06 Oct | +0.1 pts | [2026-10-06](../scans/2026-10-06.md) |
| [MDT](MDT.md) | Medtronic plc | $94.64 (26 Oct) | +7.8% since 08 Oct | +6.8 pts | [2026-10-15](../scans/2026-10-15.md) |
| [MDXG](MDXG.md) | Mimedx Group, Inc. | $3.88 (26 Oct) | -12.5% since 16 Oct | -15.2 pts | [2026-10-18](../scans/2026-10-18.md) |
| [MP](MP.md) | MP Materials Corp. / DE | $38.13 (26 Oct) | -18.6% since 05 Oct | -17.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [MTCH](MTCH.md) | Match Group, Inc. | $45.45 (26 Oct) | +7.3% since 13 Oct | +5.3 pts | [2026-10-13](../scans/2026-10-13.md) |
| [NE](NE.md) | Noble Corp plc | $48.04 (26 Oct) | +11.9% since 12 Oct | +10.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [NNE](NNE.md) | Nano Nuclear Energy Inc.: SEC staff letter dated 2025-08-21 | $12.24 (26 Oct) | -21.6% since 02 Oct | -20.8 pts | [2026-10-15](../scans/2026-10-15.md) |
| [NWCL](NWCL.md) | newcleo plc | $4.54 (26 Oct) | -4.4% since 19 Oct | -8.0 pts | [2026-10-20](../scans/2026-10-20.md) |
| [OKLO](OKLO.md) | Oklo Inc. | $26.74 (26 Oct) | -10.9% since 15 Oct | -10.2 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PATK](PATK.md) | Patrick Industries Inc | $69.72 (26 Oct) | +8.4% since 13 Oct | +8.6 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PCOR](PCOR.md) | Procore Technologies, Inc. | $62.28 (26 Oct) | +14.5% since 06 Oct | +15.2 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PL](PL.md) | Planet Labs PBC | $13.85 (26 Oct) | -4.8% since 15 Oct | -4.3 pts | [2026-10-21](../scans/2026-10-21.md) |
| [POLA](POLA.md) | Polar Power, Inc. | $0.725 (26 Oct) | -42.5% since 28 Sep | -42.7 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PZZA](PZZA.md) | PAPA JOHNS INTERNATIONAL INC, filed by Norbel Investments, S.L. | $18.38 (26 Oct) | +0.7% since 21 Oct | -1.7 pts | [2026-10-21](../scans/2026-10-21.md) |
| [RIG](RIG.md) | Transocean Ltd. | $6.53 (26 Oct) | +16.6% since 12 Oct | +15.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RKLB](RKLB.md) | Rocket Lab Corp | $54.33 (26 Oct) | -1.7% since 15 Oct | -1.4 pts | [2026-10-23](../scans/2026-10-23.md) |
| [SBGSY](SBGSY.md) | SBGSY | $52.59 (26 Oct) | -9.6% since 06 Oct | -7.4 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SDRL](SDRL.md) | SEADRILL Ltd, filed by Elliott Investment Management L.P. | $52.03 (26 Oct) | +10.7% since 12 Oct | +7.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [SMR](SMR.md) | NUSCALE POWER Corp | $5.45 (26 Oct) | -11.4% since 15 Oct | -10.0 pts | [2026-10-15](../scans/2026-10-15.md) |
| [SNTI](SNTI.md) | Senti Biosciences Holdings, Inc. | $0.178 (26 Oct) | -44.8% since 04 Oct | -41.4 pts | [2026-10-16](../scans/2026-10-16.md) |
| [SWBI](SWBI.md) | Smith & Wesson Brands, Inc. | $13.86 (26 Oct) | -8.2% since 21 Oct | -9.5 pts | [2026-10-22](../scans/2026-10-22.md) |
| [THO](THO.md) | Thor Industries Inc | $70.53 (26 Oct) | +7.7% since 14 Oct | +2.8 pts | [2026-10-14](../scans/2026-10-14.md) |
| [TKNO](TKNO.md) | Alpha Teknova, Inc. | $6.69 (26 Oct) | +14.4% since 21 Oct | +18.1 pts | [2026-10-22](../scans/2026-10-22.md) |
| [TNON](TNON.md) | Tenon Medical, Inc. | $2.19 (26 Oct) | -24.2% since 13 Oct | -24.2 pts | [2026-10-23](../scans/2026-10-23.md) |
| [UAMY](UAMY.md) | United States Antimony Corp | $3.01 (26 Oct) | -23.9% since 05 Oct | -23.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [UMAC](UMAC.md) | Unusual Machines, Inc. | $17.18 (26 Oct) | -12.5% since 12 Oct | -11.2 pts | [2026-10-12](../scans/2026-10-12.md) |
| [VAL](VAL.md) | Valaris Ltd | $99.19 (26 Oct) | +16.8% since 12 Oct | +15.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VHUB](VHUB.md) | VenHub Global, Inc. | $0.327 (26 Oct) | -31.8% since 04 Oct | -24.4 pts | [2026-10-04](../scans/2026-10-04.md) |
| [VRA](VRA.md) | Vera Bradley, Inc., filed by ROYCE & ASSOCIATES LP | $5.93 (26 Oct) | -3.1% since 22 Oct | -4.1 pts | [2026-10-22](../scans/2026-10-22.md) |
| [VREX](VREX.md) | Varex Imaging Corp | $18.42 (26 Oct) | +0.0% since 22 Oct | -1.3 pts | [2026-10-23](../scans/2026-10-23.md) |
| [VRT](VRT.md) | Vertiv Holdings Co | $201.00 (26 Oct) | -20.8% since 05 Oct | -18.5 pts | [2026-10-23](../scans/2026-10-23.md) |
| [WGO](WGO.md) | Winnebago Industries Inc | $28.34 (26 Oct) | +22.7% since 14 Oct | +18.0 pts | [2026-10-23](../scans/2026-10-23.md) |
| [WTI](WTI.md) | W&t Offshore Inc | $4.24 (26 Oct) | +16.2% since 14 Oct | +13.9 pts | [2026-10-19](../scans/2026-10-19.md) |
| [XRPN](XRPN.md) | Evernorth Holdings Inc. | $14.89 (26 Oct) | -12.9% since 09 Oct | -10.7 pts | [2026-10-21](../scans/2026-10-21.md) |
