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
| [MTUS](MTUS.md) | Metallus Inc. | $21.24 (29 Oct) | +12.7% since 25 Sep | +7.4 pts | [2026-10-28](../scans/2026-10-28.md) |

## Watchlist

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [ACB](ACB.md) | Aurora Cannabis Inc | $4.09 (29 Oct) | +3.0% since 20 Oct | +0.0 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ALEC](ALEC.md) | Alector, Inc. | $2.28 (29 Oct) | +23.6% since 16 Oct | +18.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ARTV](ARTV.md) | Artiva Biotherapeutics, Inc. | $4.25 (29 Oct) | -0.5% since 27 Oct | -3.8 pts | [2026-10-28](../scans/2026-10-28.md) |
| [BMBL](BMBL.md) | Bumble Inc. | $5.97 (29 Oct) | +0.3% since 13 Oct | -3.7 pts | 2026-10-29 |
| [BMEZ](BMEZ.md) | BlackRock Health Sciences Term Trust | $17.71 (29 Oct) | +8.7% since 16 Oct | +3.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [BMM](BMM.md) | private placement [6-K](https://www.sec.gov/Archives/edgar/data/1732379/000155485526002139/ex991_1.htm) | $4.33 (29 Oct) | +0.7% since 20 Oct | -2.8 pts | [2026-10-28](../scans/2026-10-28.md) |
| [BORR](BORR.md) | Borr Drilling Ltd | $4.29 (29 Oct) | -13.0% since 12 Oct | -16.2 pts | [2026-10-26](../scans/2026-10-26.md) |
| [BYRN](BYRN.md) | Roth Adam L. (director) bought 15,000 shares at $4.69 = $70,375 on 2026-10-15 | $4.67 (29 Oct) | -3.5% since 18 Oct | -12.0 pts | [2026-10-19](../scans/2026-10-19.md) |
| [CHDN](CHDN.md) | Churchill Downs Inc | $88.25 (29 Oct) | +16.6% since 28 Sep | +14.6 pts | [2026-10-27](../scans/2026-10-27.md) |
| [CPAC](CPAC.md) | Cementos Pacasmayo Saa | $12.81 (29 Oct) | +1.2% since 21 Oct | -2.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CRMT](CRMT.md) | Americas Carmart Inc | $0.913 (29 Oct) | -27.0% since 08 Oct | -29.8 pts | 2026-10-29 |
| [CSR](CSR.md) | Centerspace | $56.45 (29 Oct) | +3.7% since 07 Oct | +0.9 pts | [2026-10-21](../scans/2026-10-21.md) |
| [CTVA](CTVA.md) | Corteva, Inc. | $11.44 (29 Oct) | +628.2% since 29 Sep | +626.2 pts | [2026-10-23](../scans/2026-10-23.md) |
| [DIBS](DIBS.md) | 1stdibs.com, Inc., filed by Catsimatidis John A. Jr | $4.74 (29 Oct) | +10.2% since 20 Oct | +7.5 pts | [2026-10-22](../scans/2026-10-22.md) |
| [DOLE](DOLE.md) | Dole plc | $13.04 (29 Oct) | -3.0% since 23 Oct | -5.6 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ELMT](ELMT.md) | Elmet Group Co. | $24.12 (29 Oct) | +22.8% since 25 Sep | +23.9 pts | [2026-10-23](../scans/2026-10-23.md) |
| [ESRT](ESRT.md) | Empire State Realty Trust, Inc. | $5.01 (29 Oct) | +18.3% since 05 Oct | +16.4 pts | [2026-10-20](../scans/2026-10-20.md) |
| [FEAM](FEAM.md) | Weibel Paul Wesley III (Chief Executive Officer) bought 7,176 shares at $3.48 = $24,972 on 2026-10-08 | $2.44 (29 Oct) | -26.1% since 08 Oct | -27.3 pts | [2026-10-26](../scans/2026-10-26.md) |
| [GPRO](GPRO.md) | GoPro, Inc. | $1.02 (29 Oct) | -2.9% since 16 Oct | -14.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [HMH](HMH.md) | HMH Holding Inc | $18.99 (29 Oct) | -1.5% since 28 Sep | -0.9 pts | [2026-10-23](../scans/2026-10-23.md) |
| [IMMR](IMMR.md) | Singer Eric (director, President and CEO) bought 41,000 shares at $7.14 = $292,800 on 2026-10-07 | $7.24 (29 Oct) | -1.5% since 12 Oct | -3.6 pts | [2026-10-19](../scans/2026-10-19.md) |
| [IMSR](IMSR.md) | Terrestrial Energy Inc. /DE/ | $3.39 (29 Oct) | +5.3% since 15 Oct | +1.4 pts | [2026-10-27](../scans/2026-10-27.md) |
| [LCII](LCII.md) | Lci Industries | $98.50 (29 Oct) | +24.1% since 13 Oct | +21.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MDA](MDA.md) | MDA Space Ltd. | $29.56 (29 Oct) | +7.2% since 14 Oct | +4.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MG](MG.md) | Mistras Group, Inc. | $20.25 (29 Oct) | -2.0% since 15 Oct | -6.8 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MOD](MOD.md) | Modine Manufacturing Co | $140.70 (29 Oct) | -17.1% since 30 Sep | -19.9 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MSGS](MSGS.md) | Madison Square Garden Sports Corp. | $300.32 (28 Oct) | -0.9% since 10 Oct | -3.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NKLR](NKLR.md) | Terra Innovatum Global N.V. | $2.44 (29 Oct) |  |  | [2026-10-28](../scans/2026-10-28.md) |
| [NPB](NPB.md) | Northpointe Bancshares Inc | $16.47 (29 Oct) | +1.7% since 28 Oct | -1.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [PCRX](PCRX.md) | Pacira BioSciences, Inc. | $36.40 (29 Oct) | +0.0% since 08 Oct | -2.1 pts | [2026-10-19](../scans/2026-10-19.md) |
| [PED](PED.md) | Pedevco Corp | $15.87 (29 Oct) | +23.9% since 14 Oct | +16.9 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PTC](PTC.md) | Ptc Inc. | $194.42 (29 Oct) | +1.1% since 05 Oct | +0.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [PUSA](PUSA.md) | Aureus Greenway Holdings Inc | $1.80 (29 Oct) | -37.7% since 05 Oct | -40.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [RXO](RXO.md) | RXO, Inc. | $27.54 (29 Oct) | -3.9% since 05 Oct | -4.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [RYAM](RYAM.md) | Rayonier Advanced Materials Inc. | $6.72 (29 Oct) | -17.6% since 28 Sep | -19.1 pts | [2026-10-21](../scans/2026-10-21.md) |
| [SKYA](SKYA.md) | SkyAI, Inc. | $2.93 (29 Oct) | +12.7% since 12 Oct | +14.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SMTI](SMTI.md) | Sanara MedTech Inc. | $33.02 (29 Oct) | -0.4% since 16 Oct | -4.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SRTA](SRTA.md) | Strata Critical Medical, Inc. | $4.81 (29 Oct) | +10.8% since 15 Oct | +2.5 pts | [2026-10-23](../scans/2026-10-23.md) |
| [SSTI](SSTI.md) | Soundthinking, Inc. | $8.40 (29 Oct) | +2.3% since 29 Sep | +0.8 pts | [2026-10-22](../scans/2026-10-22.md) |
| [SYNA](SYNA.md) | SYNAPTICS Inc | $118.12 (29 Oct) | -0.8% since 08 Oct | -3.8 pts | [2026-10-26](../scans/2026-10-26.md) |
| [TALO](TALO.md) | Talos Energy Inc. | $18.24 (29 Oct) | +7.1% since 14 Oct | +1.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [TCPC](TCPC.md) | BlackRock TCP Capital Corp. | $4.16 (29 Oct) | +2.1% since 14 Oct | -2.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [TENX](TENX.md) | Tenax Therapeutics, Inc. | $1.95 (29 Oct) | +10.8% since 22 Oct | +7.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [THRM](THRM.md) | Gentherm Inc | $32.30 (29 Oct) | +1.3% since 29 Sep | -0.7 pts | [2026-10-27](../scans/2026-10-27.md) |
| [TWST](TWST.md) | Twist Bioscience Corp | $172.52 (29 Oct) | -10.7% since 30 Sep | -13.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ULBI](ULBI.md) | Ultralife Corp | $15.62 (29 Oct) | +0.1% since 28 Oct | -0.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [UUUU](UUUU.md) | Energy Fuels Inc | $8.23 (29 Oct) | -11.2% since 13 Oct | -12.5 pts | [2026-10-19](../scans/2026-10-19.md) |
| [VYLR](VYLR.md) | Vylor Inc. | $73.63 (29 Oct) | +7.9% since 01 Oct | +6.4 pts | [2026-10-26](../scans/2026-10-26.md) |
| [WHF](WHF.md) | WhiteHorse Finance, Inc. | $8.06 (29 Oct) | +15.6% since 28 Sep | +14.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [XPOF](XPOF.md) | Xponential Fitness, Inc. | $4.01 (29 Oct) | -16.8% since 13 Oct | -20.4 pts | [2026-10-22](../scans/2026-10-22.md) |

## Setups (watch only)

| ticker | company | latest | since first found | vs IWM | last mention |
|---|---|---|---|---|---|
| [AAON](AAON.md) | Aaon, Inc. | $74.36 (29 Oct) | -11.8% since 05 Oct | -12.9 pts | [2026-10-05](../scans/2026-10-05.md) |
| [ABEO](ABEO.md) | Abeona Therapeutics Inc. | $4.69 (29 Oct) | +6.6% since 23 Oct | +3.8 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ACOG](ACOG.md) | Opaleye Management Inc. (10% owner) bought 36,940 shares at $8.35 = $308,576 on 2026-10-16 | $9.29 (29 Oct) | +7.9% since 20 Oct | +5.3 pts | [2026-10-26](../scans/2026-10-26.md) |
| [ACVA](ACVA.md) | ACV Auctions Inc. | $10.50 (16 Oct) | +0.6% since 29 Sep | -1.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ADSK](ADSK.md) | Autodesk, Inc. | $239.34 (29 Oct) | +3.5% since 06 Oct | +1.2 pts | [2026-10-06](../scans/2026-10-06.md) |
| [AEHL](AEHL.md) | Antelope Enterprise Holdings Ltd | $7.59 (29 Oct) | -14.3% since 23 Oct | -17.4 pts | 2026-10-29 |
| [AGMB](AGMB.md) | Epstein David R (director) bought 10,000 shares at $8.88 = $88,800 on 2026-10-21 | $7.83 (29 Oct) | -13.5% since 23 Oct | -17.0 pts | [2026-10-23](../scans/2026-10-23.md) |
| [ALLO](ALLO.md) | Allogene Therapeutics, Inc. | $1.33 (29 Oct) | +2.3% since 28 Oct | -0.7 pts | [2026-10-28](../scans/2026-10-28.md) |
| [AMPY](AMPY.md) | Amplify Energy Corp. | $4.37 (29 Oct) | +0.7% since 14 Oct | -4.1 pts | [2026-10-14](../scans/2026-10-14.md) |
| [ASTS](ASTS.md) | AST SpaceMobile, Inc. | $44.33 (29 Oct) | -0.3% since 15 Oct | -0.7 pts | [2026-10-27](../scans/2026-10-27.md) |
| [ATKR](ATKR.md) | Atkore Inc. | $94.96 (16 Oct) | +0.1% since 07 Oct | -2.8 pts | [2026-10-28](../scans/2026-10-28.md) |
| [AZUL](AZUL.md) | Azul SA | $3.86 (29 Oct) | -4.7% since 26 Oct | -11.5 pts | [2026-10-27](../scans/2026-10-27.md) |
| [BRUN](BRUN.md) | Boost Run Inc. | $8.35 (29 Oct) | -1.5% since 20 Oct | -8.5 pts | [2026-10-21](../scans/2026-10-21.md) |
| [BSY](BSY.md) | Bentley Systems Inc | $39.02 (29 Oct) | +8.5% since 06 Oct | +6.2 pts | [2026-10-08](../scans/2026-10-08.md) |
| [CABA](CABA.md) | Cabaletta Bio, Inc. | $1.59 (29 Oct) | +4.3% since 28 Oct | +2.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CHRW](CHRW.md) | C. H. Robinson Worldwide, Inc. | $126.32 (29 Oct) | -10.2% since 05 Oct | -10.3 pts | [2026-10-06](../scans/2026-10-06.md) |
| [CLF](CLF.md) | Cleveland-cliffs Inc. | $14.16 (29 Oct) | +16.1% since 05 Oct | +9.9 pts | [2026-10-27](../scans/2026-10-27.md) |
| [CPSH](CPSH.md) | Cps Technologies Corp/de/ | $3.68 (29 Oct) | +5.3% since 26 Oct | +2.6 pts | [2026-10-27](../scans/2026-10-27.md) |
| [CTEV](CTEV.md) | ARES MANAGEMENT LLC (10% owner) + ASOF II Holdings I, L.P. (10% owner) + ASOF II A (DE) Holdings I, L.P. (10% owner) + 1 more bought 70,834 shares at $23.69 = $1,678,106 on 2026-10-26 | $24.56 (29 Oct) | +6.8% since 28 Oct | +4.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [CVX](CVX.md) | Chevron Corp | $230.85 (29 Oct) | +7.4% since 12 Oct | +4.0 pts | [2026-10-12](../scans/2026-10-12.md) |
| [CYAB](CYAB.md) | Cyabra, Inc. | $0.129 (29 Oct) | -35.6% since 04 Oct | -36.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [DFNS](DFNS.md) | T3 Defense Inc. | $3.83 (29 Oct) | -6.8% since 23 Oct | -10.9 pts | [2026-10-27](../scans/2026-10-27.md) |
| [DYAI](DYAI.md) | Dyadic International Inc | $0.402 (29 Oct) | -12.7% since 04 Oct | -13.6 pts | [2026-10-15](../scans/2026-10-15.md) |
| [FATE](FATE.md) | Fate Therapeutics Inc | $2.21 (29 Oct) | +1.8% since 28 Oct | +1.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [FLD](FLD.md) | Fold Holdings, Inc. | $0.510 (29 Oct) | -5.5% since 29 Sep | -6.2 pts | [2026-10-27](../scans/2026-10-27.md) |
| [FWDI](FWDI.md) | Forward Industries, Inc. | $6.96 (29 Oct) | -3.2% since 12 Oct | -3.8 pts | [2026-10-19](../scans/2026-10-19.md) |
| [GOVX](GOVX.md) | GeoVax Labs, Inc. | $0.190 (29 Oct) | -40.6% since 04 Oct | -43.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [GRND](GRND.md) | Grindr Inc. | $12.99 (29 Oct) | -16.0% since 13 Oct | -19.6 pts | [2026-10-13](../scans/2026-10-13.md) |
| [GRNT](GRNT.md) | Granite Ridge Resources, Inc. | $5.76 (29 Oct) | +16.6% since 14 Oct | +10.4 pts | [2026-10-14](../scans/2026-10-14.md) |
| [GTBP](GTBP.md) | GT Biopharma, Inc. | $5.53 (29 Oct) | -17.2% since 09 Oct | -20.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [GWH](GWH.md) | ESS Tech, Inc. | $0.060 (28 Oct) | -61.8% since 04 Oct | -54.8 pts | [2026-10-27](../scans/2026-10-27.md) |
| [GXAI](GXAI.md) | Gaxos.ai Inc. | $0.480 (29 Oct) | -7.0% since 04 Oct | -3.1 pts | [2026-10-04](../scans/2026-10-04.md) |
| [HCTI](HCTI.md) | Healthcare Triangle, Inc. | $6.42 (29 Oct) | -55.7% since 02 Oct | -47.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [HESM](HESM.md) | Hess Midstream LP, filed by Hess Investments North Dakota LLC | $32.10 (29 Oct) | -0.8% since 12 Oct | -2.9 pts | [2026-10-22](../scans/2026-10-22.md) |
| [HUBG](HUBG.md) | Hub Group, Inc. | $26.14 (29 Oct) | -7.2% since 06 Oct | -8.1 pts | [2026-10-06](../scans/2026-10-06.md) |
| [IBRX](IBRX.md) | ImmunityBio, Inc. | $8.84 (29 Oct) | +0.3% since 28 Oct | +0.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [INVE](INVE.md) | INVE Technologies, Inc. | $2.71 (29 Oct) | -2.5% since 21 Oct | -6.4 pts | [2026-10-26](../scans/2026-10-26.md) |
| [JBHT](JBHT.md) | Hunt J B Transport Services Inc | $221.40 (29 Oct) | -2.0% since 06 Oct | -3.2 pts | [2026-10-06](../scans/2026-10-06.md) |
| [KOS](KOS.md) | Kosmos Energy Ltd. | $2.73 (29 Oct) | +0.7% since 14 Oct | -5.2 pts | [2026-10-14](../scans/2026-10-14.md) |
| [KYTX](KYTX.md) | Kyverna Therapeutics, Inc., filed by HIRSCHMAN ORIN | $5.97 (29 Oct) | +1.4% since 28 Oct | +0.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [LEO](LEO.md) | Saba Capital Management, L.P. (10% owner) bought 65,000 shares at $5.68 = $369,200 on 2026-10-23 | $5.91 (29 Oct) | -0.1% since 27 Oct | -1.6 pts | [2026-10-28](../scans/2026-10-28.md) |
| [LEU](LEU.md) | Centrus Energy Corp | $112.38 (29 Oct) | -11.5% since 15 Oct | -12.4 pts | [2026-10-22](../scans/2026-10-22.md) |
| [LSTR](LSTR.md) | Landstar System Inc | $140.33 (29 Oct) | -17.0% since 06 Oct | -18.1 pts | [2026-10-27](../scans/2026-10-27.md) |
| [LYCA](LYCA.md) | Venrock Healthcare Capital Partners III, L.P. (10% owner) + VHCP Co-Investment Holdings III, LLC (10% owner) + VHCP Management III, LLC (10% owner) + 6 more bought 2,045,440 shares at $18.41 = $37,653,863 on 2026-10-27 | $25.47 (29 Oct) | -15.1% since 23 Oct | +4.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MDT](MDT.md) | Medtronic plc | $95.36 (29 Oct) | +8.7% since 08 Oct | +5.5 pts | [2026-10-15](../scans/2026-10-15.md) |
| [MDXG](MDXG.md) | Mimedx Group, Inc. | $3.62 (29 Oct) | -18.2% since 16 Oct | -23.0 pts | [2026-10-18](../scans/2026-10-18.md) |
| [MEDS](MEDS.md) | DataMeds AI, Inc. | $2.08 (29 Oct) | -24.6% since 20 Oct | -25.9 pts | [2026-10-27](../scans/2026-10-27.md) |
| [MFIC](MFIC.md) | MidCap Financial Investment Corp | $10.30 (29 Oct) | +0.4% since 27 Oct | -1.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [MP](MP.md) | MP Materials Corp. / DE | $41.87 (29 Oct) | -10.6% since 05 Oct | -11.7 pts | [2026-10-27](../scans/2026-10-27.md) |
| [MTCH](MTCH.md) | Match Group, Inc. | $42.76 (29 Oct) | +0.9% since 13 Oct | -3.3 pts | [2026-10-13](../scans/2026-10-13.md) |
| [NAUT](NAUT.md) | Nautilus Biotechnology, Inc. | $3.23 (29 Oct) | +11.9% since 27 Oct | +6.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NCT](NCT.md) | Intercont (Cayman) Ltd | $1.49 (29 Oct) | +0.3% since 26 Oct | -6.6 pts | [2026-10-26](../scans/2026-10-26.md) |
| [NE](NE.md) | Noble Corp plc | $47.68 (29 Oct) | +11.0% since 12 Oct | +7.0 pts | [2026-10-26](../scans/2026-10-26.md) |
| [NIVF](NIVF.md) | private placement, securities purchase agreement, merger agreement [6-K](https://www.sec.gov/Archives/edgar/data/1981662/000121390026112647/ea030961701ex99-1.htm) | $1.12 (29 Oct) | -51.4% since 29 Sep | -80.6 pts | 2026-10-29 |
| [NKTX](NKTX.md) | Nkarta, Inc. | $1.73 (29 Oct) | +0.5% since 28 Oct | -1.4 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NNBR](NNBR.md) | Nn Inc | $3.91 (29 Oct) | +16.5% since 26 Oct | +12.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [NNE](NNE.md) | Nano Nuclear Energy Inc.: SEC staff letter dated 2025-08-21 | $12.39 (29 Oct) | -20.7% since 02 Oct | -22.0 pts | [2026-10-15](../scans/2026-10-15.md) |
| [NWCL](NWCL.md) | newcleo plc | $4.59 (29 Oct) | -3.5% since 19 Oct | -9.3 pts | [2026-10-20](../scans/2026-10-20.md) |
| [OKLO](OKLO.md) | Oklo Inc. | $27.01 (29 Oct) | -10.0% since 15 Oct | -11.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [OSTX](OSTX.md) | OS Therapies Inc: sold $7,172,429 of $12,282,478 | $1.27 (29 Oct) | +5.0% since 26 Oct | +1.7 pts | [2026-10-26](../scans/2026-10-26.md) |
| [PATK](PATK.md) | Patrick Industries Inc | $73.30 (29 Oct) | +13.9% since 13 Oct | +12.1 pts | [2026-10-28](../scans/2026-10-28.md) |
| [PCOR](PCOR.md) | Procore Technologies, Inc. | $60.94 (29 Oct) | +12.0% since 06 Oct | +10.5 pts | [2026-10-15](../scans/2026-10-15.md) |
| [PL](PL.md) | Planet Labs PBC | $14.50 (29 Oct) | -0.3% since 15 Oct | -1.9 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PMI](PMI.md) | Picard Medical, Inc. | $7.88 (29 Oct) | +11.1% since 23 Oct | +7.3 pts | 2026-10-29 |
| [POLA](POLA.md) | Polar Power, Inc. | $0.650 (29 Oct) | -48.4% since 28 Sep | -50.8 pts | [2026-10-21](../scans/2026-10-21.md) |
| [PRTA](PRTA.md) | SCULLY WILLIAM P (10% owner) bought 150,000 shares at $8.15 = $1,222,045 on 2026-10-23 | $9.12 (29 Oct) | +3.6% since 27 Oct | +4.1 pts | [2026-10-27](../scans/2026-10-27.md) |
| [PZZA](PZZA.md) | PAPA JOHNS INTERNATIONAL INC, filed by Norbel Investments, S.L. | $18.47 (29 Oct) | +1.3% since 21 Oct | -3.3 pts | [2026-10-21](../scans/2026-10-21.md) |
| [RAPP](RAPP.md) | Sanchez Ramiro (director) bought 3,600 shares at $27.35 = $98,478 on 2026-10-23 | $24.58 (29 Oct) | -3.0% since 26 Oct | -4.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [RENT](RENT.md) | Nexus Capital Management LP (director, 10% owner) + Gateway Runway, LLC (director, 10% owner) + Gateway Runway Intermediate Holdings, Inc. (director, 10% owner) + 7 more bought 632,922 shares at $3.55 = $2,246,873 on 2026-10-21 | $2.55 (29 Oct) | -9.6% since 26 Oct | -14.1 pts | [2026-10-26](../scans/2026-10-26.md) |
| [RIG](RIG.md) | Transocean Ltd. | $6.76 (29 Oct) | +20.7% since 12 Oct | +17.5 pts | [2026-10-26](../scans/2026-10-26.md) |
| [RKLB](RKLB.md) | Rocket Lab Corp | $60.24 (29 Oct) | +9.0% since 15 Oct | +7.3 pts | [2026-10-23](../scans/2026-10-23.md) |
| [SAMG](SAMG.md) | Equinox Partners Investment Management LLC (10% owner) + EQUINOX PARTNERS LP (10% owner) bought 34,126 shares at $10.33 = $352,684 on 2026-10-22 | $10.48 (29 Oct) | +0.5% since 26 Oct | -1.4 pts | [2026-10-26](../scans/2026-10-26.md) |
| [SANA](SANA.md) | Sana Biotechnology, Inc. | $2.73 (29 Oct) | +3.7% since 28 Oct | +2.2 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SBGSY](SBGSY.md) | SBGSY | $55.21 (29 Oct) | -5.1% since 06 Oct | -4.9 pts | [2026-10-20](../scans/2026-10-20.md) |
| [SDRL](SDRL.md) | SEADRILL Ltd, filed by Elliott Investment Management L.P. | $52.65 (29 Oct) | +12.1% since 12 Oct | +6.2 pts | [2026-10-19](../scans/2026-10-19.md) |
| [SGRY](SGRY.md) | Surgery Partners, Inc. | $23.24 (29 Oct) | -0.1% since 26 Oct | -2.2 pts | 2026-10-29 |
| [SMR](SMR.md) | NUSCALE POWER Corp | $5.80 (29 Oct) | -5.8% since 15 Oct | -6.4 pts | [2026-10-15](../scans/2026-10-15.md) |
| [SNTI](SNTI.md) | Senti Biosciences Holdings, Inc. | $0.232 (29 Oct) | -27.9% since 04 Oct | -26.0 pts | [2026-10-28](../scans/2026-10-28.md) |
| [STC](STC.md) | EPPINGER FREDERICK H (director, Chief Executive Officer) bought 3,000 shares at $44.45 = $133,350 on 2026-10-26 | $45.32 (29 Oct) | +2.3% since 28 Oct | +0.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [SWBI](SWBI.md) | Smith & Wesson Brands, Inc. | $13.75 (29 Oct) | -8.9% since 21 Oct | -12.4 pts | [2026-10-26](../scans/2026-10-26.md) |
| [THO](THO.md) | Thor Industries Inc | $72.93 (29 Oct) | +11.4% since 14 Oct | +4.1 pts | [2026-10-14](../scans/2026-10-14.md) |
| [TKNO](TKNO.md) | Alpha Teknova, Inc. | $8.18 (29 Oct) | +39.8% since 21 Oct | +42.5 pts | [2026-10-27](../scans/2026-10-27.md) |
| [TMCR](TMCR.md) | Metals Royalty Co Inc. | $2.28 (29 Oct) | +7.5% since 23 Oct | +3.0 pts | [2026-10-26](../scans/2026-10-26.md) |
| [TNON](TNON.md) | Tenon Medical, Inc. | $2.25 (29 Oct) | -22.1% since 13 Oct | -24.3 pts | [2026-10-26](../scans/2026-10-26.md) |
| [TONX](TONX.md) | TON Strategy Co, filed by Stotz Manuel | $3.44 (29 Oct) | +2.7% since 28 Oct | +3.5 pts | [2026-10-28](../scans/2026-10-28.md) |
| [UAMY](UAMY.md) | United States Antimony Corp | $3.16 (29 Oct) | -19.9% since 05 Oct | -21.3 pts | [2026-10-28](../scans/2026-10-28.md) |
| [UMAC](UMAC.md) | Unusual Machines, Inc. | $17.43 (29 Oct) | -11.2% since 12 Oct | -12.1 pts | [2026-10-26](../scans/2026-10-26.md) |
| [VAL](VAL.md) | Valaris Ltd | $102.65 (29 Oct) | +20.9% since 12 Oct | +16.9 pts | [2026-10-26](../scans/2026-10-26.md) |
| [VHUB](VHUB.md) | VenHub Global, Inc. | $0.250 (29 Oct) | -48.0% since 04 Oct | -44.1 pts | [2026-10-04](../scans/2026-10-04.md) |
| [VRA](VRA.md) | Vera Bradley, Inc., filed by ROYCE & ASSOCIATES LP | $6.44 (29 Oct) | +5.2% since 22 Oct | +2.1 pts | [2026-10-22](../scans/2026-10-22.md) |
| [VREX](VREX.md) | Varex Imaging Corp | $18.45 (29 Oct) | +0.2% since 22 Oct | -3.3 pts | [2026-10-23](../scans/2026-10-23.md) |
| [VRT](VRT.md) | Vertiv Holdings Co | $249.83 (29 Oct) | -1.5% since 05 Oct | -1.4 pts | [2026-10-27](../scans/2026-10-27.md) |
| [WGO](WGO.md) | Winnebago Industries Inc | $29.28 (29 Oct) | +26.8% since 14 Oct | +19.8 pts | [2026-10-23](../scans/2026-10-23.md) |
| [WORX](WORX.md) | SCWorx Corp. | $1.71 (29 Oct) | -69.0% since 05 Oct | -70.0 pts | 2026-10-29 |
| [WTI](WTI.md) | W&t Offshore Inc | $4.13 (29 Oct) | +13.2% since 14 Oct | +8.7 pts | [2026-10-19](../scans/2026-10-19.md) |
| [XRPN](XRPN.md) | Evernorth Holdings Inc. | $15.06 (29 Oct) | -11.9% since 09 Oct | -11.9 pts | [2026-10-28](../scans/2026-10-28.md) |
| [ZURA](ZURA.md) | Zura Bio Ltd | $4.24 (29 Oct) | -2.6% since 28 Oct | -3.4 pts | [2026-10-28](../scans/2026-10-28.md) |
