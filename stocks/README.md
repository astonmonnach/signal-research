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
| [MTUS](MTUS.md) | Metallus Inc. | $20.80 (19 Oct) | +10.4% since 25 Sep | +9.9 pts | [2026-10-19](../scans/2026-10-19.md) |

## Watchlist

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [ALEC](ALEC.md) | Alector, Inc. | $1.95 (19 Oct) | +6.0% since 16 Oct | +5.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMBL](BMBL.md) | Bumble Inc. | $5.96 (19 Oct) | +0.2% since 13 Oct | +0.9 pts | [2026-10-20](../scans/2026-10-20.md) |
| [BMEZ](BMEZ.md) | BlackRock Health Sciences Term Trust | $16.44 (19 Oct) | +0.9% since 16 Oct | +0.9 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BORR](BORR.md) | Borr Drilling Ltd | $4.44 (19 Oct) | -9.9% since 12 Oct | -8.4 pts | [2026-10-20](../scans/2026-10-20.md) |
| [BYRN](BYRN.md) | Roth Adam L. (director) bought 15,000 shares at $4.69 = $70,375 on 2026-10-15 | $5.17 (19 Oct) | +6.8% since 18 Oct | +2.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CHDN](CHDN.md) | Churchill Downs Inc | $81.97 (19 Oct) | +8.2% since 28 Sep | +11.1 pts | [2026-09-28](../scans/2026-09-28.md) |
| [CRMT](CRMT.md) | Americas Carmart Inc | $1.07 (19 Oct) | -14.4% since 08 Oct | -12.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CSR](CSR.md) | Centerspace | $54.87 (19 Oct) | +0.8% since 07 Oct | +2.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CTVA](CTVA.md) | Corteva, Inc. | $12.65 (19 Oct) | +627.9% since 29 Sep | +630.7 pts | [2026-10-20](../scans/2026-10-20.md) |
| [ELMT](ELMT.md) | Elmet Group Co. | $18.75 (19 Oct) | -4.5% since 25 Sep | +0.7 pts | [2026-10-20](../scans/2026-10-20.md) |
| [ESRT](ESRT.md) | Empire State Realty Trust, Inc. | $4.61 (19 Oct) | +9.0% since 05 Oct | +11.8 pts | [2026-10-20](../scans/2026-10-20.md) |
| [FEAM](FEAM.md) | Weibel Paul Wesley III (Chief Executive Officer) bought 7,176 shares at $3.48 = $24,972 on 2026-10-08 | $2.57 (19 Oct) | -22.4% since 08 Oct | -18.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GPRO](GPRO.md) | GoPro, Inc. | $1.04 (19 Oct) | -0.9% since 16 Oct | -7.4 pts | [2026-10-20](../scans/2026-10-20.md) |
| [HMH](HMH.md) | HMH Holding Inc | $17.38 (19 Oct) | -9.8% since 28 Sep | -4.7 pts | [2026-10-20](../scans/2026-10-20.md) |
| [IMMR](IMMR.md) | Singer Eric (director, President and CEO) bought 41,000 shares at $7.14 = $292,800 on 2026-10-07 | $7.08 (19 Oct) | -3.7% since 12 Oct | -1.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [IMSR](IMSR.md) | Terrestrial Energy Inc. /DE/ | $2.85 (19 Oct) | -11.5% since 15 Oct | -10.5 pts | [2026-10-20](../scans/2026-10-20.md) |
| [LCII](LCII.md) | Lci Industries | $81.92 (19 Oct) | +3.2% since 13 Oct | +4.9 pts | [2026-10-20](../scans/2026-10-20.md) |
| [MDA](MDA.md) | MDA Space Ltd. | $28.10 (19 Oct) | +1.9% since 14 Oct | +3.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [MG](MG.md) | Mistras Group, Inc. | $21.44 (19 Oct) | +3.7% since 15 Oct | +3.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [MOD](MOD.md) | Modine Manufacturing Co | $149.59 (19 Oct) | -13.3% since 30 Sep | -11.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [MSGS](MSGS.md) | Madison Square Garden Sports Corp. | $400.00 (19 Oct) | -0.6% since 10 Oct | +1.5 pts | [2026-10-20](../scans/2026-10-20.md) |
| [NKLR](NKLR.md) | Terra Innovatum Global N.V. | $2.39 (19 Oct) |  |  | [2026-10-19](../scans/2026-10-19.md) |
| [PCRX](PCRX.md) | Pacira BioSciences, Inc. | $36.34 (19 Oct) | -0.1% since 08 Oct | +2.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [PED](PED.md) | Pedevco Corp | $14.65 (19 Oct) | +14.4% since 14 Oct | +12.4 pts | [2026-10-20](../scans/2026-10-20.md) |
| [PTC](PTC.md) | Ptc Inc. | $193.06 (19 Oct) | +0.4% since 05 Oct | +4.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [PUSA](PUSA.md) | Aureus Greenway Holdings Inc | $1.94 (19 Oct) | -33.0% since 05 Oct | -30.9 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RXO](RXO.md) | RXO, Inc. | $28.50 (19 Oct) | -0.5% since 05 Oct | +3.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RYAM](RYAM.md) | Rayonier Advanced Materials Inc. | $6.87 (19 Oct) | -15.7% since 28 Sep | -12.5 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SKYA](SKYA.md) | SkyAI, Inc. | $2.79 (19 Oct) | +7.3% since 12 Oct | +13.6 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SMTI](SMTI.md) | Sanara MedTech Inc. | $33.14 (19 Oct) | -0.1% since 16 Oct | +1.0 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SRTA](SRTA.md) | Strata Critical Medical, Inc. | $4.54 (19 Oct) | +4.6% since 15 Oct | +1.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SYNA](SYNA.md) | SYNAPTICS Inc | $117.05 (19 Oct) | -1.7% since 08 Oct | +0.1 pts | [2026-10-20](../scans/2026-10-20.md) |
| [TALO](TALO.md) | Talos Energy Inc. | $18.05 (19 Oct) | +6.0% since 14 Oct | +5.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [TCPC](TCPC.md) | BlackRock TCP Capital Corp. | $4.11 (19 Oct) | +0.7% since 14 Oct | +0.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [THRM](THRM.md) | Gentherm Inc | $28.61 (19 Oct) | -9.6% since 29 Sep | -6.8 pts | [2026-10-20](../scans/2026-10-20.md) |
| [TWST](TWST.md) | Twist Bioscience Corp | $139.77 (19 Oct) | -27.7% since 30 Sep | -25.4 pts | [2026-10-19](../scans/2026-10-19.md) |
| [UUUU](UUUU.md) | Energy Fuels Inc | $8.16 (19 Oct) | -12.0% since 13 Oct | -8.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VYLR](VYLR.md) | Vylor Inc. | $72.39 (19 Oct) | +6.0% since 01 Oct | +9.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [WHF](WHF.md) | WhiteHorse Finance, Inc. | $7.43 (19 Oct) | +6.6% since 28 Sep | +10.1 pts | [2026-10-20](../scans/2026-10-20.md) |

## Setups (watch only)

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [AAON](AAON.md) | Aaon, Inc. | $75.34 (19 Oct) | -10.7% since 05 Oct | -7.1 pts | [2026-10-05](../scans/2026-10-05.md) |
| [ACB](ACB.md) | Aurora Cannabis Inc | $3.96 (19 Oct) | pending since 20 Oct |  | [2026-10-20](../scans/2026-10-20.md) |
| [ACOG](ACOG.md) | Opaleye Management Inc. (10% owner) bought 36,940 shares at $8.35 = $308,576 on 2026-10-16 | $8.50 (19 Oct) | pending since 20 Oct |  | [2026-10-20](../scans/2026-10-20.md) |
| [ACVA](ACVA.md) | ACV Auctions Inc. | $10.50 (16 Oct) | +0.6% since 29 Sep | +3.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [ADSK](ADSK.md) | Autodesk, Inc. | $240.70 (19 Oct) | +4.1% since 06 Oct | +6.5 pts | [2026-10-06](../scans/2026-10-06.md) |
| [AMPY](AMPY.md) | Amplify Energy Corp. | $4.53 (19 Oct) | +4.4% since 14 Oct | +4.4 pts | [2026-10-14](../scans/2026-10-14.md) |
| [ASTS](ASTS.md) | AST SpaceMobile, Inc. | $41.87 (19 Oct) | -5.8% since 15 Oct | -1.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [ATKR](ATKR.md) | Atkore Inc. | $94.96 (16 Oct) | +0.1% since 07 Oct | +1.9 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMM](BMM.md) | private placement [6-K](https://www.sec.gov/Archives/edgar/data/1732379/000155485526002139/ex991_1.htm) | $4.29 (19 Oct) | pending since 20 Oct |  | [2026-10-20](../scans/2026-10-20.md) |
| [BSY](BSY.md) | Bentley Systems Inc | $36.73 (19 Oct) | +2.1% since 06 Oct | +4.6 pts | [2026-10-08](../scans/2026-10-08.md) |
| [CHRW](CHRW.md) | C. H. Robinson Worldwide, Inc. | $138.85 (19 Oct) | -1.2% since 05 Oct | +3.2 pts | [2026-10-06](../scans/2026-10-06.md) |
| [CLF](CLF.md) | Cleveland-cliffs Inc. | $14.10 (19 Oct) | +15.6% since 05 Oct | +14.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CVX](CVX.md) | Chevron Corp | $224.37 (19 Oct) | +4.4% since 12 Oct | +5.8 pts | [2026-10-12](../scans/2026-10-12.md) |
| [CYAB](CYAB.md) | Cyabra, Inc. | $0.150 (19 Oct) | -25.0% since 04 Oct | -21.2 pts | [2026-10-20](../scans/2026-10-20.md) |
| [DIBS](DIBS.md) | 1stdibs.com, Inc., filed by Catsimatidis John A. Jr | $4.25 (19 Oct) | pending since 20 Oct |  | [2026-10-20](../scans/2026-10-20.md) |
| [DYAI](DYAI.md) | Dyadic International Inc | $0.380 (19 Oct) | -17.4% since 04 Oct | -13.6 pts | [2026-10-15](../scans/2026-10-15.md) |
| [FLD](FLD.md) | Fold Holdings, Inc. | $0.510 (19 Oct) | -5.6% since 29 Sep | -1.5 pts | [2026-10-04](../scans/2026-10-04.md) |
| [FWDI](FWDI.md) | Forward Industries, Inc. | $6.81 (19 Oct) | -5.3% since 12 Oct | -1.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GOVX](GOVX.md) | GeoVax Labs, Inc. | $0.228 (19 Oct) | -28.8% since 04 Oct | -27.1 pts | [2026-10-04](../scans/2026-10-04.md) |
| [GRND](GRND.md) | Grindr Inc. | $14.11 (19 Oct) | -8.8% since 13 Oct | -7.6 pts | [2026-10-13](../scans/2026-10-13.md) |
| [GRNT](GRNT.md) | Granite Ridge Resources, Inc. | $5.67 (19 Oct) | +14.8% since 14 Oct | +13.5 pts | [2026-10-14](../scans/2026-10-14.md) |
| [GWH](GWH.md) | ESS Tech, Inc. | $0.081 (19 Oct) | -48.4% since 04 Oct | -33.9 pts | [2026-10-04](../scans/2026-10-04.md) |
| [GXAI](GXAI.md) | Gaxos.ai Inc. | $0.417 (19 Oct) | -19.2% since 04 Oct | -11.3 pts | [2026-10-04](../scans/2026-10-04.md) |
| [HCTI](HCTI.md) | Healthcare Triangle, Inc. | $0.364 (19 Oct) | -49.8% since 02 Oct | -35.5 pts | [2026-10-04](../scans/2026-10-04.md) |
| [HESM](HESM.md) | Hess Midstream LP, filed by Hess Investments North Dakota LLC | $30.23 (19 Oct) | -6.6% since 12 Oct | -3.9 pts | [2026-10-12](../scans/2026-10-12.md) |
| [HUBG](HUBG.md) | Hub Group, Inc. | $25.66 (19 Oct) | -8.9% since 06 Oct | -5.1 pts | [2026-10-06](../scans/2026-10-06.md) |
| [JBHT](JBHT.md) | Hunt J B Transport Services Inc | $223.25 (19 Oct) | -1.2% since 06 Oct | +2.4 pts | [2026-10-06](../scans/2026-10-06.md) |
| [KOS](KOS.md) | Kosmos Energy Ltd. | $2.79 (19 Oct) | +3.0% since 14 Oct | +1.9 pts | [2026-10-14](../scans/2026-10-14.md) |
| [LEU](LEU.md) | Centrus Energy Corp | $110.12 (19 Oct) | -13.3% since 15 Oct | -9.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [LSTR](LSTR.md) | Landstar System Inc | $168.36 (19 Oct) | -0.4% since 06 Oct | +3.4 pts | [2026-10-06](../scans/2026-10-06.md) |
| [MDT](MDT.md) | Medtronic plc | $92.77 (19 Oct) | +5.7% since 08 Oct | +7.3 pts | [2026-10-15](../scans/2026-10-15.md) |
| [MDXG](MDXG.md) | Mimedx Group, Inc. | $4.38 (19 Oct) | -1.1% since 16 Oct | -1.2 pts | [2026-10-18](../scans/2026-10-18.md) |
| [MP](MP.md) | MP Materials Corp. / DE | $38.95 (19 Oct) | -16.8% since 05 Oct | -13.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [MTCH](MTCH.md) | Match Group, Inc. | $44.73 (19 Oct) | +5.6% since 13 Oct | +6.2 pts | [2026-10-13](../scans/2026-10-13.md) |
| [NE](NE.md) | Noble Corp plc | $44.04 (19 Oct) | +2.6% since 12 Oct | +3.4 pts | [2026-10-19](../scans/2026-10-19.md) |
| [NNE](NNE.md) | Nano Nuclear Energy Inc.: SEC staff letter dated 2025-08-21 | $13.01 (19 Oct) | -16.7% since 02 Oct | -13.3 pts | [2026-10-15](../scans/2026-10-15.md) |
| [NWCL](NWCL.md) | newcleo plc | $4.75 (19 Oct) | pending since 19 Oct |  | [2026-10-20](../scans/2026-10-20.md) |
| [OKLO](OKLO.md) | Oklo Inc. | $27.24 (19 Oct) | -9.2% since 15 Oct | -5.8 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PATK](PATK.md) | Patrick Industries Inc | $66.39 (19 Oct) | +3.2% since 13 Oct | +6.0 pts | [2026-10-20](../scans/2026-10-20.md) |
| [PCOR](PCOR.md) | Procore Technologies, Inc. | $58.01 (19 Oct) | +6.7% since 06 Oct | +9.8 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PL](PL.md) | Planet Labs PBC | $13.59 (19 Oct) | -6.5% since 15 Oct | -3.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [POLA](POLA.md) | Polar Power, Inc. | $0.890 (19 Oct) | -29.4% since 28 Sep | -27.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [RIG](RIG.md) | Transocean Ltd. | $5.89 (19 Oct) | +5.2% since 12 Oct | +6.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RKLB](RKLB.md) | Rocket Lab Corp | $51.36 (19 Oct) | -7.0% since 15 Oct | -4.2 pts | [2026-10-15](../scans/2026-10-15.md) |
| [SBGSY](SBGSY.md) | SBGSY | $53.90 (19 Oct) | -7.4% since 06 Oct | -2.5 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SDRL](SDRL.md) | SEADRILL Ltd, filed by Elliott Investment Management L.P. | $48.23 (19 Oct) | +2.6% since 12 Oct | +1.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [SMR](SMR.md) | NUSCALE POWER Corp | $5.69 (19 Oct) | -7.5% since 15 Oct | -3.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [SNTI](SNTI.md) | Senti Biosciences Holdings, Inc. | $0.227 (19 Oct) | -29.5% since 04 Oct | -23.0 pts | [2026-10-16](../scans/2026-10-16.md) |
| [THO](THO.md) | Thor Industries Inc | $65.86 (19 Oct) | +0.6% since 14 Oct | -1.6 pts | [2026-10-14](../scans/2026-10-14.md) |
| [UAMY](UAMY.md) | United States Antimony Corp | $3.10 (19 Oct) | -21.5% since 05 Oct | -18.3 pts | [2026-10-19](../scans/2026-10-19.md) |
| [UMAC](UMAC.md) | Unusual Machines, Inc. | $16.40 (19 Oct) | -16.5% since 12 Oct | -12.7 pts | [2026-10-12](../scans/2026-10-12.md) |
| [VAL](VAL.md) | Valaris Ltd | $89.39 (19 Oct) | +5.2% since 12 Oct | +6.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VHUB](VHUB.md) | VenHub Global, Inc. | $0.330 (19 Oct) | -31.2% since 04 Oct | -21.2 pts | [2026-10-04](../scans/2026-10-04.md) |
| [VRT](VRT.md) | Vertiv Holdings Co | $206.08 (19 Oct) | -18.7% since 05 Oct | -14.0 pts | [2026-10-05](../scans/2026-10-05.md) |
| [WGO](WGO.md) | Winnebago Industries Inc | $22.67 (19 Oct) | -1.8% since 14 Oct | -3.4 pts | [2026-10-14](../scans/2026-10-14.md) |
| [WTI](WTI.md) | W&t Offshore Inc | $3.85 (19 Oct) | +5.5% since 14 Oct | +5.8 pts | [2026-10-19](../scans/2026-10-19.md) |
