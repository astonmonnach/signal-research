# AV1 progress: our AVOIDs against matched unflagged stocks

Run 2026-10-27. Rules frozen in [PREREG_AV1.md](PREREG_AV1.md). **Description only**: the test reads once 30 primary rows are judged at 20 trading days, or on 31 Dec 2026.

Excess = the AVOID's return minus the median of up to 10 matched controls (same price bucket, half to twice the market value), over the same window. Negative = the AVOID fell more than similar stocks.

| group | rows with controls | judged (20 days or reversed) | mean excess, all | mean excess, judged | AVOID behind its controls |
|---|---|---|---|---|---|
| Primary: supply and distress | 50 | 0 | -1.1 pts | n/a | 32/50 |
| One-off offerings | 13 | 1 | +3.7 pts | +9.4 pts | 5/13 |
| Killed long theses | 2 | 0 | +5.0 pts | n/a | 0/2 |
| Other | 6 | 0 | -5.5 pts | n/a | 4/6 |

## Every AVOID

| date | ticker | type | status | entry | end | AVOID | controls (median, n) | excess |
|---|---|---|---|---|---|---|---|---|
| 2026-10-05 | CHDN | kill | reclassified | 2026-10-06 | 2026-10-27 (open) | +5.7% | +2.2% (10) | +3.5 |
| 2026-10-05 | CYAB | ongoing_supply | active | 2026-10-06 | 2026-10-27 (open) | -34.8% | -30.4% (10) | -4.4 |
| 2026-10-05 | DYAI | distress | active | 2026-10-06 | 2026-10-27 (open) | -13.2% | -21.9% (10) | +8.7 |
| 2026-10-05 | ELMT | other | active | 2026-10-06 | 2026-10-27 (open) | -0.0% | -1.1% (10) | +1.1 |
| 2026-10-05 | FLD | ongoing_supply | active | 2026-10-06 | 2026-10-27 (open) | -7.1% | -10.3% (10) | +3.2 |
| 2026-10-05 | GOVX | distress | active | 2026-10-06 | 2026-10-27 (open) | -35.3% | -20.5% (10) | -14.7 |
| 2026-10-05 | GWH | distress | active | | | | no controls | |
| 2026-10-05 | GXAI | warrant_supply | active | 2026-10-06 | 2026-10-27 (open) | -8.9% | -20.1% (10) | +11.1 |
| 2026-10-05 | HCTI | distress | active | 2026-10-06 | 2026-10-27 (open) | -42.5% | -5.1% (5) | -37.5 |
| 2026-10-05 | POLA | ongoing_supply | active | 2026-10-06 | 2026-10-27 (open) | -44.4% | -9.6% (10) | -34.8 |
| 2026-10-05 | SNTI | ongoing_supply | active | 2026-10-06 | 2026-10-27 (open) | -46.2% | -15.5% (10) | -30.7 |
| 2026-10-05 | TWST | other | active | 2026-10-06 | 2026-10-27 (open) | -23.6% | +1.6% (10) | -25.2 |
| 2026-10-05 | VHUB | ongoing_supply | active | 2026-10-06 | 2026-10-27 (open) | -29.3% | -14.3% (8) | -15.0 |
| 2026-10-10 | CRMT | distress | active | 2026-10-12 | 2026-10-27 (open) | -39.2% | -9.5% (10) | -29.7 |
| 2026-10-12 | PUSA | deal_dilution | active | 2026-10-13 | 2026-10-27 (open) | -16.3% | -6.6% (10) | -9.7 |
| 2026-10-14 | TALO | holder_selling | active | 2026-10-15 | 2026-10-27 (open) | +6.4% | -0.7% (10) | +7.1 |
| 2026-10-15 | IONQ | one_off_offering | active | 2026-10-16 | 2026-10-27 (open) | -0.1% | +0.0% (10) | -0.1 |
| 2026-10-15 | MOVE | ongoing_supply | active | 2026-10-16 | 2026-10-27 (open) | -8.1% | +2.4% (10) | -10.5 |
| 2026-10-15 | SKYX | deal_dilution | active | 2026-10-16 | 2026-10-27 (open) | -22.5% | -4.9% (10) | -17.5 |
| 2026-10-16 | GEMI | ongoing_supply | active | 2026-10-19 | 2026-10-27 (open) | -14.7% | +1.0% (10) | -15.8 |
| 2026-10-16 | RXRX | one_off_offering | active | 2026-10-19 | 2026-10-27 (open) | +17.1% | +1.0% (5) | +16.1 |
| 2026-10-18 | AIOK | ongoing_supply | active | 2026-10-19 | 2026-10-27 (open) | +218.4% | -4.1% (10) | +222.5 |
| 2026-10-18 | NKLR | distress | active | 2026-10-19 | 2026-10-27 (open) | -19.1% | +0.7% (10) | -19.8 |
| 2026-10-20 | AIAI | ongoing_supply | active | 2026-10-21 | 2026-10-27 (open) | -22.8% | -0.6% (10) | -22.2 |
| 2026-10-20 | CABO | holder_selling | active | 2026-10-21 | 2026-10-27 (open) | -13.0% | +0.4% (10) | -13.5 |
| 2026-10-20 | ENHA | other | active | 2026-10-21 | 2026-10-27 (open) | -3.4% | -2.1% (10) | -1.3 |
| 2026-10-20 | FBYD | holder_selling | active | 2026-10-21 | 2026-10-27 (open) | -3.7% | -0.7% (10) | -3.0 |
| 2026-10-20 | HOST | ongoing_supply | active | 2026-10-21 | 2026-10-27 (open) | +3.0% | -2.5% (10) | +5.5 |
| 2026-10-20 | NVGS | holder_selling | active | 2026-10-21 | 2026-10-27 (open) | +1.4% | +1.0% (10) | +0.5 |
| 2026-10-20 | NWCL | ongoing_supply | active | 2026-10-21 | 2026-10-27 (open) | +0.9% | +0.7% (8) | +0.2 |
| 2026-10-20 | RMCF | distress | active | 2026-10-21 | 2026-10-27 (open) | -1.3% | -0.7% (10) | -0.6 |
| 2026-10-20 | SDST | distress | active | | | | no controls | |
| 2026-10-20 | THRM | kill | reclassified | 2026-10-21 | 2026-10-27 (open) | +6.6% | +0.1% (10) | +6.5 |
| 2026-10-21 | BRUN | ongoing_supply | active | 2026-10-22 | 2026-10-27 (open) | +2.3% | +0.9% (10) | +1.3 |
| 2026-10-21 | CELU | distress | active | 2026-10-22 | 2026-10-27 (open) | -25.0% | -0.8% (10) | -24.2 |
| 2026-10-21 | GRDX | ongoing_supply | active | 2026-10-22 | 2026-10-27 (open) | +13.6% | +1.5% (10) | +12.1 |
| 2026-10-21 | MWYN | other | active | 2026-10-22 | 2026-10-27 (open) | +0.0% | -3.8% (10) | +3.8 |
| 2026-10-21 | TKNO | one_off_offering | reversed | 2026-10-22 | 2026-10-22 | +9.8% | +0.4% (10) | +9.4 |
| 2026-10-21 | XRPN | warrant_supply | active | | | | no controls | |
| 2026-10-21 | XTIA | distress | active | 2026-10-22 | 2026-10-27 (open) | +26.6% | -3.5% (10) | +30.1 |
| 2026-10-22 | ADIL | distress | active | 2026-10-23 | 2026-10-27 (open) | -6.5% | -5.6% (10) | -0.9 |
| 2026-10-22 | GTBP | ongoing_supply | active | 2026-10-23 | 2026-10-27 (open) | +0.0% | -10.4% (3) | +10.4 |
| 2026-10-22 | IMCC | ongoing_supply | active | 2026-10-23 | 2026-10-27 (open) | -8.1% | -7.4% (10) | -0.7 |
| 2026-10-22 | SWBI | deal_dilution | active | 2026-10-23 | 2026-10-27 (open) | -2.6% | +2.8% (10) | -5.4 |
| 2026-10-22 | VBIO | ongoing_supply | active | 2026-10-23 | 2026-10-27 (open) | -10.0% | -3.9% (10) | -6.1 |
| 2026-10-23 | AEHL | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | -14.1% | +1.8% (10) | -15.9 |
| 2026-10-23 | AIRE | one_off_offering | active | 2026-10-26 | 2026-10-27 (open) | -15.2% | -1.3% (10) | -13.9 |
| 2026-10-23 | AMCI | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | +0.5% | -0.1% (10) | +0.6 |
| 2026-10-23 | AMOD | one_off_offering | active | 2026-10-26 | 2026-10-27 (open) | +13.2% | -2.1% (10) | +15.4 |
| 2026-10-23 | AXG | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | -26.5% | -7.8% (2) | -18.7 |
| 2026-10-23 | EONR | distress | active | 2026-10-26 | 2026-10-27 (open) | -8.7% | -1.3% (10) | -7.5 |
| 2026-10-23 | JAGX | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | +10.7% | -0.6% (10) | +11.3 |
| 2026-10-23 | LAB | deal_dilution | active | 2026-10-26 | 2026-10-27 (open) | -0.2% | -7.0% (3) | +6.8 |
| 2026-10-23 | PMI | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | -5.6% | -1.2% (7) | -4.4 |
| 2026-10-23 | TNON | ongoing_supply | active | 2026-10-26 | 2026-10-27 (open) | +2.0% | -0.4% (10) | +2.4 |
| 2026-10-26 | AMSS | other | active | 2026-10-27 | 2026-10-27 (open) | -3.7% | +1.8% (10) | -5.5 |
| 2026-10-26 | BANL | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | +11.1% | +0.6% (10) | +10.5 |
| 2026-10-26 | BGMS | ongoing_supply | active | | | | no prices | |
| 2026-10-26 | BOF | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | +4.1% | -1.4% (10) | +5.6 |
| 2026-10-26 | BURU | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -14.6% | -1.6% (10) | -13.0 |
| 2026-10-26 | CNEY | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | +3.2% | +0.0% (10) | +3.1 |
| 2026-10-26 | CTW | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -2.9% | +0.3% (10) | -3.2 |
| 2026-10-26 | DFNS | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -3.7% | +0.2% (10) | -3.9 |
| 2026-10-26 | ENSC | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -0.9% | -1.8% (10) | +0.9 |
| 2026-10-26 | HLSQ | other | active | 2026-10-27 | 2026-10-27 (open) | -9.5% | -3.5% (10) | -6.0 |
| 2026-10-26 | HODO | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -3.5% | -0.2% (10) | -3.3 |
| 2026-10-26 | MACI | other | active | | | | no controls | |
| 2026-10-26 | MCRP | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | +21.1% | -3.5% (10) | +24.6 |
| 2026-10-26 | NCT | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | +6.5% | +0.0% (10) | +6.5 |
| 2026-10-26 | ONFO | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -4.0% | -0.5% (10) | -3.5 |
| 2026-10-26 | OSTX | warrant_supply | active | 2026-10-27 | 2026-10-27 (open) | +4.9% | -0.8% (10) | +5.7 |
| 2026-10-26 | TMCR | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | +0.0% | +2.7% (10) | -2.7 |
| 2026-10-26 | TRAW | ongoing_supply | active | 2026-10-27 | 2026-10-27 (open) | -1.3% | +0.0% (10) | -1.4 |
| 2026-10-26 | UFG | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | -11.8% | -2.5% (10) | -9.2 |
| 2026-10-26 | XXII | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | -9.4% | -1.0% (10) | -8.4 |
| 2026-10-26 | YMT | one_off_offering | active | 2026-10-27 | 2026-10-27 (open) | -7.5% | +3.3% (10) | -10.8 |
| 2026-10-27 | MEDS | deal_dilution | active | | | | no prices | |
