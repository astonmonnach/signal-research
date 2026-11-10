# AV1 progress: our AVOIDs against matched unflagged stocks

Run 2026-11-10. Rules frozen in [PREREG_AV1.md](PREREG_AV1.md). **Description only**: the test reads once 30 primary rows are judged at 20 trading days, or on 31 Dec 2026.

Excess = the AVOID's return minus the median of up to 10 matched controls (same price bucket, half to twice the market value), over the same window. Negative = the AVOID fell more than similar stocks.

| group | rows with controls | judged (20 days or reversed) | mean excess, all | mean excess, judged | AVOID behind its controls |
|---|---|---|---|---|---|
| Primary: supply and distress | 179 | 11 | -0.1 pts | -17.3 pts | 112/179 |
| One-off offerings | 21 | 1 | -9.3 pts | +9.9 pts | 12/21 |
| Killed long theses | 2 | 1 | +13.1 pts | +22.8 pts | 0/2 |
| Other | 5 | 2 | -26.8 pts | -21.3 pts | 4/5 |

## Every AVOID

| date | ticker | type | status | entry | end | AVOID | controls (median, n) | excess |
|---|---|---|---|---|---|---|---|---|
| 2026-10-05 | CHDN | kill | reclassified | 2026-10-06 | 2026-11-02 | +27.1% | +4.3% (10) | +22.8 |
| 2026-10-05 | CYAB | ongoing_supply | active | 2026-10-06 | 2026-11-02 | -47.6% | -15.8% (10) | -31.8 |
| 2026-10-05 | DYAI | distress | active | 2026-10-06 | 2026-11-02 | -19.1% | -32.4% (10) | +13.3 |
| 2026-10-05 | ELMT | other | reversed | 2026-10-06 | 2026-11-02 | +2.3% | +1.5% (10) | +0.8 |
| 2026-10-05 | FLD | ongoing_supply | active | 2026-10-06 | 2026-11-02 | -3.3% | -15.1% (10) | +11.8 |
| 2026-10-05 | GOVX | distress | active | 2026-10-06 | 2026-11-02 | -48.7% | -13.8% (10) | -34.9 |
| 2026-10-05 | GWH | distress | active | | | | no controls | |
| 2026-10-05 | GXAI | warrant_supply | active | 2026-10-06 | 2026-11-02 | -16.3% | -8.0% (10) | -8.3 |
| 2026-10-05 | HCTI | distress | active | 2026-10-06 | 2026-11-02 | -58.2% | -9.1% (4) | -49.0 |
| 2026-10-05 | POLA | ongoing_supply | active | 2026-10-06 | 2026-11-02 | -53.4% | -6.1% (10) | -47.3 |
| 2026-10-05 | SNTI | ongoing_supply | active | 2026-10-06 | 2026-11-02 | -42.2% | -6.7% (10) | -35.4 |
| 2026-10-05 | TWST | other | active | 2026-10-06 | 2026-11-02 | -38.4% | +4.9% (10) | -43.3 |
| 2026-10-05 | VHUB | ongoing_supply | active | 2026-10-06 | 2026-11-02 | -45.2% | -18.5% (8) | -26.8 |
| 2026-10-10 | CRMT | distress | active | 2026-10-12 | 2026-11-06 | +5.9% | -28.5% (10) | +34.3 |
| 2026-10-12 | PUSA | deal_dilution | active | 2026-10-13 | 2026-11-09 | -32.6% | -16.2% (10) | -16.4 |
| 2026-10-14 | TALO | holder_selling | active | 2026-10-15 | 2026-11-10 (open) | -13.7% | -0.4% (10) | -13.2 |
| 2026-10-15 | IONQ | one_off_offering | active | 2026-10-16 | 2026-11-10 (open) | +5.4% | +8.6% (10) | -3.2 |
| 2026-10-15 | MOVE | ongoing_supply | active | 2026-10-16 | 2026-11-10 (open) | -44.5% | -2.5% (10) | -42.0 |
| 2026-10-15 | SKYX | deal_dilution | active | 2026-10-16 | 2026-11-10 (open) | -31.0% | -6.6% (10) | -24.4 |
| 2026-10-16 | GEMI | ongoing_supply | active | 2026-10-19 | 2026-11-10 (open) | -26.2% | +3.6% (10) | -29.8 |
| 2026-10-16 | RXRX | one_off_offering | active | 2026-10-19 | 2026-11-10 (open) | +0.1% | +1.3% (2) | -1.1 |
| 2026-10-18 | AIOK | ongoing_supply | active | 2026-10-19 | 2026-11-10 (open) | +151.6% | -7.8% (10) | +159.4 |
| 2026-10-18 | NKLR | distress | active | 2026-10-19 | 2026-11-10 (open) | -4.6% | -8.7% (10) | +4.1 |
| 2026-10-20 | AIAI | ongoing_supply | active | 2026-10-21 | 2026-11-10 (open) | -58.5% | -11.2% (10) | -47.3 |
| 2026-10-20 | CABO | holder_selling | active | 2026-10-21 | 2026-11-10 (open) | -34.2% | -1.0% (10) | -33.2 |
| 2026-10-20 | ENHA | deal_dilution | active | 2026-10-21 | 2026-11-10 (open) | -32.2% | +1.0% (8) | -33.2 |
| 2026-10-20 | FBYD | holder_selling | active | 2026-10-21 | 2026-11-10 (open) | -22.6% | -9.4% (10) | -13.2 |
| 2026-10-20 | HOST | ongoing_supply | active | 2026-10-21 | 2026-11-10 (open) | -33.3% | -10.6% (10) | -22.7 |
| 2026-10-20 | NVGS | holder_selling | active | 2026-10-21 | 2026-11-10 (open) | -3.2% | -1.3% (10) | -1.9 |
| 2026-10-20 | NWCL | ongoing_supply | active | 2026-10-21 | 2026-11-10 (open) | +1.6% | +9.5% (3) | -7.9 |
| 2026-10-20 | RMCF | distress | active | 2026-10-21 | 2026-11-10 (open) | -9.0% | -7.5% (10) | -1.5 |
| 2026-10-20 | SDST | distress | active | | | | no controls | |
| 2026-10-20 | THRM | kill | reclassified | 2026-10-21 | 2026-11-10 (open) | +0.6% | -2.8% (10) | +3.4 |
| 2026-10-21 | BRUN | ongoing_supply | active | 2026-10-22 | 2026-11-10 (open) | -21.9% | -0.6% (10) | -21.3 |
| 2026-10-21 | CELU | distress | active | 2026-10-22 | 2026-11-10 (open) | -33.1% | -24.2% (10) | -8.9 |
| 2026-10-21 | GRDX | ongoing_supply | active | 2026-10-22 | 2026-11-10 (open) | +10.0% | -6.0% (10) | +16.0 |
| 2026-10-21 | MWYN | other | active | 2026-10-22 | 2026-11-10 (open) | -38.2% | -10.8% (10) | -27.4 |
| 2026-10-21 | TKNO | one_off_offering | reversed | 2026-10-22 | 2026-10-22 | +9.8% | -0.1% (10) | +9.9 |
| 2026-10-21 | XRPN | warrant_supply | active | | | | no controls | |
| 2026-10-21 | XTIA | distress | active | 2026-10-22 | 2026-11-10 (open) | +30.1% | -16.1% (10) | +46.2 |
| 2026-10-22 | ADIL | distress | active | | | | no controls | |
| 2026-10-22 | GTBP | ongoing_supply | active | 2026-10-23 | 2026-11-10 (open) | -30.0% | -9.8% (5) | -20.2 |
| 2026-10-22 | IMCC | ongoing_supply | active | 2026-10-23 | 2026-11-10 (open) | -33.4% | -20.5% (10) | -12.9 |
| 2026-10-22 | SWBI | deal_dilution | active | 2026-10-23 | 2026-11-10 (open) | +6.4% | -6.1% (10) | +12.5 |
| 2026-10-22 | VBIO | ongoing_supply | active | 2026-10-23 | 2026-11-10 (open) | -45.0% | -10.2% (10) | -34.8 |
| 2026-10-23 | AEHL | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | +30.5% | +2.5% (10) | +28.0 |
| 2026-10-23 | AIRE | one_off_offering | active | 2026-10-26 | 2026-11-10 (open) | -60.5% | -12.2% (10) | -48.2 |
| 2026-10-23 | AMCI | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | -51.0% | -8.2% (10) | -42.8 |
| 2026-10-23 | AMOD | one_off_offering | active | 2026-10-26 | 2026-11-10 (open) | +5.0% | -6.9% (10) | +11.9 |
| 2026-10-23 | AXG | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | -90.7% | -28.9% (1) | -61.9 |
| 2026-10-23 | EONR | distress | active | 2026-10-26 | 2026-11-10 (open) | -44.7% | -14.1% (10) | -30.5 |
| 2026-10-23 | JAGX | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | -78.6% | -3.2% (10) | -75.3 |
| 2026-10-23 | LAB | deal_dilution | active | 2026-10-26 | 2026-11-10 (open) | +9.3% | +15.5% (2) | -6.2 |
| 2026-10-23 | PMI | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | +14.6% | -2.2% (8) | +16.9 |
| 2026-10-23 | TNON | ongoing_supply | active | 2026-10-26 | 2026-11-10 (open) | -18.6% | -5.4% (10) | -13.3 |
| 2026-10-26 | AMSS | other | active | 2026-10-27 | 2026-11-10 (open) | -19.3% | -14.0% (10) | -5.3 |
| 2026-10-26 | BANL | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -16.6% | -8.9% (10) | -7.7 |
| 2026-10-26 | BGMS | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -14.0% | -19.6% (10) | +5.7 |
| 2026-10-26 | BOF | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | +0.6% | -14.8% (10) | +15.4 |
| 2026-10-26 | BURU | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -1.6% | -20.1% (10) | +18.5 |
| 2026-10-26 | CNEY | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -4.1% | -25.2% (10) | +21.1 |
| 2026-10-26 | CTW | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -5.8% | -1.9% (10) | -4.0 |
| 2026-10-26 | DFNS | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -47.6% | -6.6% (10) | -40.9 |
| 2026-10-26 | ENSC | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -24.9% | -10.6% (10) | -14.3 |
| 2026-10-26 | HLSQ | other | active | 2026-10-27 | 2026-11-10 (open) | -65.4% | -6.4% (10) | -59.0 |
| 2026-10-26 | HODO | ongoing_supply | active | | | | no controls | |
| 2026-10-26 | MACI | other | active | | | | no controls | |
| 2026-10-26 | MCRP | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -12.6% | -5.3% (10) | -7.3 |
| 2026-10-26 | NCT | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -74.7% | -14.4% (10) | -60.3 |
| 2026-10-26 | ONFO | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -32.7% | -14.3% (10) | -18.3 |
| 2026-10-26 | OSTX | warrant_supply | active | 2026-10-27 | 2026-11-10 (open) | -27.9% | +1.3% (10) | -29.2 |
| 2026-10-26 | TMCR | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -10.5% | +4.5% (10) | -14.9 |
| 2026-10-26 | TRAW | ongoing_supply | active | 2026-10-27 | 2026-11-10 (open) | -29.4% | -4.7% (10) | -24.7 |
| 2026-10-26 | UFG | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -11.0% | -2.7% (10) | -8.3 |
| 2026-10-26 | XXII | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -76.9% | -12.3% (2) | -64.5 |
| 2026-10-26 | YMT | one_off_offering | active | 2026-10-27 | 2026-11-10 (open) | -46.6% | -14.0% (10) | -32.6 |
| 2026-10-27 | AQB | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -15.3% | -11.5% (10) | -3.8 |
| 2026-10-27 | BBLG | distress | active | 2026-10-28 | 2026-11-10 (open) | -12.0% | -13.8% (10) | +1.7 |
| 2026-10-27 | DCM | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -21.1% | -7.5% (10) | -13.6 |
| 2026-10-27 | DVLT | distress | active | 2026-10-28 | 2026-11-10 (open) | -16.2% | +2.2% (5) | -18.4 |
| 2026-10-27 | MEDS | deal_dilution | active | 2026-10-28 | 2026-11-10 (open) | -54.0% | -19.3% (10) | -34.8 |
| 2026-10-27 | NAUT | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -24.2% | +4.9% (10) | -29.0 |
| 2026-10-27 | NNBR | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -17.6% | -7.3% (10) | -10.3 |
| 2026-10-27 | OBAI | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -18.2% | -8.6% (10) | -9.6 |
| 2026-10-27 | PBK | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -17.8% | -11.7% (10) | -6.1 |
| 2026-10-27 | PCSA | deal_dilution | active | 2026-10-28 | 2026-11-10 (open) | +6.3% | -2.8% (10) | +9.1 |
| 2026-10-27 | SHFS | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -79.3% | -21.9% (10) | -57.5 |
| 2026-10-27 | WHLR | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -78.4% | -2.2% (10) | -76.2 |
| 2026-10-27 | XPON | ongoing_supply | active | 2026-10-28 | 2026-11-10 (open) | -28.4% | -6.5% (10) | -21.9 |
| 2026-10-28 | ACTU | one_off_offering | active | 2026-10-29 | 2026-11-10 (open) | -15.2% | -16.2% (10) | +1.0 |
| 2026-10-28 | CABR | ongoing_supply | active | 2026-10-29 | 2026-11-10 (open) | -19.8% | -9.4% (10) | -10.4 |
| 2026-10-28 | CDT | distress | active | 2026-10-29 | 2026-11-10 (open) | -60.0% | -3.5% (10) | -56.4 |
| 2026-10-28 | CHSN | distress | active | 2026-10-29 | 2026-11-10 (open) | +92.4% | -5.0% (10) | +97.4 |
| 2026-10-28 | EDVA | ongoing_supply | active | 2026-10-29 | 2026-11-10 (open) | +5.2% | -11.8% (10) | +16.9 |
| 2026-10-28 | HYFM | distress | active | 2026-10-29 | 2026-11-10 (open) | -7.5% | -13.8% (10) | +6.3 |
| 2026-10-28 | IBO | deal_dilution | active | 2026-10-29 | 2026-11-10 (open) | +1.2% | -7.4% (10) | +8.5 |
| 2026-10-28 | IMNN | warrant_supply | active | 2026-10-29 | 2026-11-10 (open) | -9.8% | -9.7% (10) | -0.1 |
| 2026-10-28 | NCI | one_off_offering | active | 2026-10-29 | 2026-11-10 (open) | +2.8% | -16.4% (6) | +19.2 |
| 2026-10-28 | NIVF | distress | active | 2026-10-29 | 2026-11-10 (open) | -71.6% | -14.4% (10) | -57.2 |
| 2026-10-28 | SCKT | distress | active | 2026-10-29 | 2026-11-10 (open) | -28.3% | -7.1% (10) | -21.2 |
| 2026-10-28 | TELO | ongoing_supply | active | 2026-10-29 | 2026-11-10 (open) | -42.6% | -10.5% (6) | -32.0 |
| 2026-10-28 | WFF | warrant_supply | active | 2026-10-29 | 2026-11-10 (open) | +0.0% | -3.2% (10) | +3.2 |
| 2026-10-28 | WORX | warrant_supply | active | 2026-10-29 | 2026-11-10 (open) | -26.2% | -2.4% (10) | -23.8 |
| 2026-10-28 | XHLD | ongoing_supply | active | 2026-10-29 | 2026-11-10 (open) | -10.5% | -17.5% (10) | +7.0 |
| 2026-11-01 | AMZE | ongoing_supply | active | | | | no controls | |
| 2026-11-01 | APVO | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -21.8% | -8.9% (10) | -12.9 |
| 2026-11-01 | ARAI | warrant_supply | active | 2026-11-02 | 2026-11-10 (open) | -43.7% | -15.7% (10) | -28.0 |
| 2026-11-01 | BCAB | ongoing_supply | active | | | | no controls | |
| 2026-11-01 | BCTX | distress | active | 2026-11-02 | 2026-11-10 (open) | +20.8% | -5.3% (10) | +26.2 |
| 2026-11-01 | CAPS | distress | active | 2026-11-02 | 2026-11-10 (open) | -8.2% | -13.7% (10) | +5.5 |
| 2026-11-01 | CDZI | one_off_offering | active | 2026-11-02 | 2026-11-10 (open) | -25.5% | -5.8% (10) | -19.7 |
| 2026-11-01 | ENVX | warrant_supply | active | 2026-11-02 | 2026-11-10 (open) | -18.7% | +8.8% (8) | -27.4 |
| 2026-11-01 | ESYN | warrant_supply | active | 2026-11-02 | 2026-11-10 (open) | -19.8% | -4.7% (10) | -15.1 |
| 2026-11-01 | FCHL | distress | active | 2026-11-02 | 2026-11-10 (open) | -17.0% | -4.9% (10) | -12.1 |
| 2026-11-01 | GPRK | deal_dilution | active | 2026-11-02 | 2026-11-10 (open) | -13.2% | -1.1% (10) | -12.1 |
| 2026-11-01 | GRRR | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -3.9% | -0.2% (10) | -3.8 |
| 2026-11-01 | HCAI | warrant_supply | active | 2026-11-02 | 2026-11-10 (open) | +30.5% | -24.0% (10) | +54.5 |
| 2026-11-01 | HUDI | distress | active | 2026-11-02 | 2026-11-10 (open) | -3.9% | -3.1% (10) | -0.8 |
| 2026-11-01 | IPW | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -16.9% | -13.3% (10) | -3.6 |
| 2026-11-01 | LOTT | distress | active | | | | no controls | |
| 2026-11-01 | LVWR | distress | active | 2026-11-02 | 2026-11-10 (open) | -27.8% | -14.9% (5) | -12.8 |
| 2026-11-01 | MASK | distress | active | 2026-11-02 | 2026-11-10 (open) | +6.5% | +1.5% (10) | +5.0 |
| 2026-11-01 | MGN | one_off_offering | active | 2026-11-02 | 2026-11-10 (open) | -14.9% | -6.0% (10) | -8.9 |
| 2026-11-01 | MIST | distress | active | 2026-11-02 | 2026-11-10 (open) | -9.5% | -12.2% (4) | +2.7 |
| 2026-11-01 | MOBX | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -22.5% | +0.3% (10) | -22.7 |
| 2026-11-01 | MVIS | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -17.0% | -2.3% (10) | -14.7 |
| 2026-11-01 | NNOX | distress | active | 2026-11-02 | 2026-11-10 (open) | +0.4% | -2.3% (10) | +2.7 |
| 2026-11-01 | NNUP | holder_selling | active | | | | no controls | |
| 2026-11-01 | OPNW | warrant_supply | active | 2026-11-02 | 2026-11-10 (open) | -48.8% | -6.5% (10) | -42.2 |
| 2026-11-01 | OPTT | distress | active | 2026-11-02 | 2026-11-10 (open) | +4.7% | -5.7% (10) | +10.3 |
| 2026-11-01 | OSRH | distress | active | | | | no controls | |
| 2026-11-01 | PARA | distress | active | 2026-11-02 | 2026-11-10 (open) | -97.3% | -8.1% (10) | -89.2 |
| 2026-11-01 | PPCB | distress | active | 2026-11-02 | 2026-11-10 (open) | -15.2% | -16.2% (10) | +1.0 |
| 2026-11-01 | PTHS | deal_dilution | active | 2026-11-02 | 2026-11-10 (open) | -3.1% | +0.1% (9) | -3.2 |
| 2026-11-01 | RCON | distress | active | 2026-11-02 | 2026-11-10 (open) | -10.1% | -4.3% (10) | -5.8 |
| 2026-11-01 | RCT | distress | active | 2026-11-02 | 2026-11-10 (open) | -21.3% | -3.4% (10) | -17.9 |
| 2026-11-01 | SRTM | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | -12.4% | -14.6% (4) | +2.2 |
| 2026-11-01 | TOPS | ongoing_supply | active | 2026-11-02 | 2026-11-10 (open) | +908.1% | -14.6% (4) | +922.6 |
| 2026-11-01 | VTEX | holder_selling | active | 2026-11-02 | 2026-11-10 (open) | -1.0% | -7.9% (9) | +6.8 |
| 2026-11-01 | XRX | distress | active | 2026-11-02 | 2026-11-10 (open) | -29.2% | +1.1% (10) | -30.3 |
| 2026-11-01 | ZTG | distress | active | 2026-11-02 | 2026-11-10 (open) | -21.8% | -11.4% (10) | -10.3 |
| 2026-11-04 | ABTS | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -6.7% | -8.5% (10) | +1.8 |
| 2026-11-04 | ABVC | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | +0.1% | -5.0% (10) | +5.1 |
| 2026-11-04 | AMIX | distress | active | 2026-11-05 | 2026-11-10 (open) | +4.5% | -0.2% (10) | +4.7 |
| 2026-11-04 | BIAF | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -17.8% | -2.7% (10) | -15.1 |
| 2026-11-04 | CJMB | distress | active | 2026-11-05 | 2026-11-10 (open) | -8.8% | -13.9% (10) | +5.0 |
| 2026-11-04 | DRMA | warrant_supply | active | 2026-11-05 | 2026-11-10 (open) | -11.8% | -11.8% (10) | +0.0 |
| 2026-11-04 | GMEX | distress | active | | | | no controls | |
| 2026-11-04 | GMM | one_off_offering | active | 2026-11-05 | 2026-11-10 (open) | -1.4% | -11.8% (10) | +10.4 |
| 2026-11-04 | GPRO | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -9.5% | -9.0% (2) | -0.5 |
| 2026-11-04 | INTZ | distress | active | 2026-11-05 | 2026-11-10 (open) | +12.8% | -7.1% (10) | +19.9 |
| 2026-11-04 | INV | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -28.1% | -4.8% (10) | -23.3 |
| 2026-11-04 | KALA | distress | active | 2026-11-05 | 2026-11-10 (open) | -5.7% | -9.0% (10) | +3.3 |
| 2026-11-04 | KPTI | distress | active | 2026-11-05 | 2026-11-10 (open) | -63.7% | -9.1% (10) | -54.6 |
| 2026-11-04 | LNAI | distress | active | | | | no prices | |
| 2026-11-04 | MERC | distress | active | 2026-11-05 | 2026-11-10 (open) | -0.0% | -6.7% (10) | +6.6 |
| 2026-11-04 | NTCL | one_off_offering | active | 2026-11-05 | 2026-11-10 (open) | -45.2% | -11.1% (10) | -34.1 |
| 2026-11-04 | OTAI | deal_dilution | active | | | | no controls | |
| 2026-11-04 | PRSO | holder_selling | active | 2026-11-05 | 2026-11-10 (open) | -11.2% | -8.3% (10) | -2.9 |
| 2026-11-04 | SEGG | distress | active | 2026-11-05 | 2026-11-10 (open) | -35.2% | -2.0% (10) | -33.1 |
| 2026-11-04 | SPRC | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -20.4% | -9.7% (10) | -10.6 |
| 2026-11-04 | UZX | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -2.9% | -7.1% (10) | +4.2 |
| 2026-11-04 | WBX | holder_selling | active | 2026-11-05 | 2026-11-10 (open) | -6.7% | -1.2% (10) | -5.5 |
| 2026-11-04 | WCT | distress | active | 2026-11-05 | 2026-11-10 (open) | +30.0% | -3.5% (10) | +33.6 |
| 2026-11-04 | YOUL | ongoing_supply | active | 2026-11-05 | 2026-11-10 (open) | -21.7% | -2.2% (10) | -19.5 |
| 2026-11-05 | ANVS | distress | active | 2026-11-06 | 2026-11-10 (open) | +20.6% | -2.5% (10) | +23.1 |
| 2026-11-05 | ARAY | distress | active | 2026-11-06 | 2026-11-10 (open) | -37.1% | +1.4% (10) | -38.5 |
| 2026-11-05 | BIVI | one_off_offering | active | 2026-11-06 | 2026-11-10 (open) | +0.8% | -0.7% (10) | +1.5 |
| 2026-11-05 | CLNN | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | +12.8% | +3.4% (10) | +9.4 |
| 2026-11-05 | CODX | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | -0.8% | -3.1% (10) | +2.3 |
| 2026-11-05 | DAIO | deal_dilution | active | 2026-11-06 | 2026-11-10 (open) | +7.7% | +3.7% (10) | +4.0 |
| 2026-11-05 | DSGN | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | +8.8% | +2.6% (10) | +6.2 |
| 2026-11-05 | ECOR | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | -16.2% | +0.6% (10) | -16.8 |
| 2026-11-05 | EHTH | distress | active | 2026-11-06 | 2026-11-10 (open) | -15.6% | +7.5% (10) | -23.1 |
| 2026-11-05 | EVAX | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | +8.3% | +0.6% (10) | +7.7 |
| 2026-11-05 | FISN | distress | active | 2026-11-06 | 2026-11-10 (open) | +44.3% | -0.3% (10) | +44.7 |
| 2026-11-05 | FTCI | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | +9.2% | +10.4% (10) | -1.2 |
| 2026-11-05 | GMHS | deal_dilution | active | 2026-11-06 | 2026-11-10 (open) | +11.1% | -2.8% (10) | +13.9 |
| 2026-11-05 | GRML | holder_selling | active | 2026-11-06 | 2026-11-10 (open) | +11.4% | +3.0% (10) | +8.3 |
| 2026-11-05 | GRO | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | +16.1% | +2.4% (10) | +13.7 |
| 2026-11-05 | HMH | holder_selling | active | 2026-11-06 | 2026-11-10 (open) | -9.0% | +4.0% (10) | -13.0 |
| 2026-11-05 | JSPR | distress | active | 2026-11-06 | 2026-11-10 (open) | +14.0% | +2.4% (7) | +11.6 |
| 2026-11-05 | MCRB | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | -24.2% | -2.8% (10) | -21.4 |
| 2026-11-05 | OCGN | distress | active | 2026-11-06 | 2026-11-10 (open) | +14.0% | -11.6% (2) | +25.6 |
| 2026-11-05 | PRPL | distress | active | 2026-11-06 | 2026-11-10 (open) | -14.2% | +2.4% (10) | -16.6 |
| 2026-11-05 | QNRX | ongoing_supply | active | 2026-11-06 | 2026-11-10 (open) | -1.7% | +1.5% (10) | -3.2 |
| 2026-11-05 | SMX | distress | active | 2026-11-06 | 2026-11-10 (open) | +382.6% | +2.4% (10) | +380.2 |
| 2026-11-05 | STIM | distress | active | 2026-11-06 | 2026-11-10 (open) | -16.6% | +1.6% (10) | -18.2 |
| 2026-11-06 | ADGM | distress | active | 2026-11-09 | 2026-11-10 (open) | -14.4% | -3.4% (10) | -11.1 |
| 2026-11-06 | AGEN | distress | active | 2026-11-09 | 2026-11-10 (open) | -5.7% | -0.2% (10) | -5.6 |
| 2026-11-06 | AMTX | distress | active | 2026-11-09 | 2026-11-10 (open) | +0.6% | +0.5% (10) | +0.1 |
| 2026-11-06 | BYND | distress | active | 2026-11-09 | 2026-11-10 (open) | -5.4% | +0.4% (10) | -5.9 |
| 2026-11-06 | CCOI | distress | active | 2026-11-09 | 2026-11-10 (open) | +8.4% | +1.0% (10) | +7.3 |
| 2026-11-06 | CGTX | distress | active | 2026-11-09 | 2026-11-10 (open) | -1.9% | +14.2% (9) | -16.1 |
| 2026-11-06 | COCH | distress | active | 2026-11-09 | 2026-11-10 (open) | -3.6% | +0.3% (10) | -3.9 |
| 2026-11-06 | CRBU | distress | active | 2026-11-09 | 2026-11-10 (open) | -9.6% | +2.2% (10) | -11.8 |
| 2026-11-06 | CVI | holder_selling | active | 2026-11-09 | 2026-11-10 (open) | +0.1% | +1.2% (10) | -1.1 |
| 2026-11-06 | DDD | ongoing_supply | active | 2026-11-09 | 2026-11-10 (open) | +1.7% | -1.7% (10) | +3.4 |
| 2026-11-06 | ELTX | distress | active | 2026-11-09 | 2026-11-10 (open) | +11.7% | -3.3% (10) | +15.1 |
| 2026-11-06 | INAB | distress | active | 2026-11-09 | 2026-11-10 (open) | -3.1% | +2.1% (10) | -5.2 |
| 2026-11-06 | INM | deal_dilution | active | | | | no controls | |
| 2026-11-06 | INMB | distress | active | 2026-11-09 | 2026-11-10 (open) | -1.8% | +2.6% (10) | -4.4 |
| 2026-11-06 | INO | one_off_offering | active | 2026-11-09 | 2026-11-10 (open) | +11.5% | +1.8% (10) | +9.8 |
| 2026-11-06 | INTS | distress | active | 2026-11-09 | 2026-11-10 (open) | +8.9% | +1.1% (10) | +7.8 |
| 2026-11-06 | ISPC | deal_dilution | active | 2026-11-09 | 2026-11-10 (open) | -9.5% | +0.6% (10) | -10.1 |
| 2026-11-06 | LXEH | holder_selling | active | 2026-11-09 | 2026-11-10 (open) | -3.7% | -0.9% (10) | -2.8 |
| 2026-11-06 | NAAS | distress | active | 2026-11-09 | 2026-11-10 (open) | -21.6% | +2.3% (10) | -24.0 |
| 2026-11-06 | NEXR | ongoing_supply | active | 2026-11-09 | 2026-11-10 (open) | +2.4% | +4.2% (10) | -1.8 |
| 2026-11-06 | NTHI | distress | active | 2026-11-09 | 2026-11-10 (open) | +12.9% | +1.4% (10) | +11.4 |
| 2026-11-06 | PESI | distress | active | 2026-11-09 | 2026-11-10 (open) | +6.0% | -1.0% (10) | +7.0 |
| 2026-11-06 | PHIO | distress | active | 2026-11-09 | 2026-11-10 (open) | +7.1% | -5.6% (10) | +12.7 |
| 2026-11-06 | PODC | distress | active | 2026-11-09 | 2026-11-10 (open) | +5.6% | -1.1% (10) | +6.7 |
| 2026-11-06 | REFR | distress | active | 2026-11-09 | 2026-11-10 (open) | +3.5% | +1.8% (10) | +1.6 |
| 2026-11-06 | REVB | distress | active | 2026-11-09 | 2026-11-10 (open) | -0.3% | -0.1% (10) | -0.1 |
| 2026-11-06 | RGNX | distress | active | 2026-11-09 | 2026-11-10 (open) | -3.2% | +2.0% (10) | -5.2 |
| 2026-11-06 | SANA | distress | active | 2026-11-09 | 2026-11-10 (open) | -2.7% | -2.2% (8) | -0.5 |
| 2026-11-06 | SGRX | distress | active | 2026-11-09 | 2026-11-10 (open) | -12.1% | -4.7% (10) | -7.4 |
| 2026-11-06 | SINT | distress | active | 2026-11-09 | 2026-11-10 (open) | -0.1% | -0.9% (10) | +0.8 |
| 2026-11-06 | SPWR | distress | active | 2026-11-09 | 2026-11-10 (open) | -14.6% | -4.0% (8) | -10.7 |
| 2026-11-06 | SRFM | distress | active | 2026-11-09 | 2026-11-10 (open) | +0.5% | -2.5% (6) | +3.0 |
| 2026-11-06 | SUNS | holder_selling | active | 2026-11-09 | 2026-11-10 (open) | +2.2% | +0.5% (10) | +1.7 |
| 2026-11-06 | VEEE | distress | active | 2026-11-09 | 2026-11-10 (open) | -7.4% | -2.7% (3) | -4.7 |
| 2026-11-10 | AGIG | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | AIRS | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | ALGS | distress | active | | | | no prices | |
| 2026-11-10 | AMRO | distress | active | | | | no prices | |
| 2026-11-10 | ATYR | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | CRVO | distress | active | | | | no prices | |
| 2026-11-10 | CVR | distress | active | | | | no prices | |
| 2026-11-10 | DRK | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | DRVN | distress | active | | | | no prices | |
| 2026-11-10 | DWTX | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | EXOZ | one_off_offering | active | | | | no prices | |
| 2026-11-10 | GPUS | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | HAIN | distress | active | | | | no prices | |
| 2026-11-10 | HIHO | deal_dilution | active | | | | no prices | |
| 2026-11-10 | HRTX | distress | active | | | | no prices | |
| 2026-11-10 | HYPR | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | KDK | distress | active | | | | no prices | |
| 2026-11-10 | LFMD | distress | active | | | | no prices | |
| 2026-11-10 | MDCX | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | MVST | distress | active | | | | no prices | |
| 2026-11-10 | NRXS | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | OPTU | distress | active | | | | no prices | |
| 2026-11-10 | PIII | warrant_supply | active | | | | no prices | |
| 2026-11-10 | SLE | warrant_supply | active | | | | no prices | |
| 2026-11-10 | SNGX | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | THRY | distress | active | | | | no prices | |
| 2026-11-10 | TNXP | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | TTRX | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | USBC | ongoing_supply | active | | | | no prices | |
| 2026-11-10 | XLAB | ongoing_supply | active | | | | no prices | |
