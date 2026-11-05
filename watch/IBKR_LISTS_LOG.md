# IBKR watchlist change log

Every change to the IBKR watchlists, newest first. The AVOID list (id 114) mirrors the active rows of
`ledger/avoid_register.csv` (rule 2026-10-27). Changes are made only with the trader's go-ahead and checked by reading the
list back afterwards.

## 2026-11-04: AVOID +24, CALLED +2, merger arb +1 (runs of 3 and 4 Nov)

The trader's go-ahead: "yeah make those changes" (4 Nov), for the lists in watch/digests/2026-11-03-triage.md and 2026-11-04-triage.md. Every list was read back from IBKR afterwards.

- **AVOID (114):** 138 to 162, equal to the register's 162 active rows. Added: BIAF (#14), INV, INTZ, ABTS, GMEX, CJMB, UZX, GMM, ABVC, WBX, NTCL, WCT, DRMA, LNAI, SEGG, KPTI, PRSO, OTAI (Starlink AI Acquisition, 895512157), KALA, AMIX, GPRO, SPRC, YOUL, MERC. XRPN (#15) was already on it.
- **CALLED (107):** 13 to 15: BIAF, XRPN.
- **STRAT merger arb (113):** 13 to 14: ACB (T021).

## 2026-11-02: AVOID +37, CALLED +4, Gov Filings +1 (the 1 Nov catch-up run)

The trader's go-ahead: on 2 Nov he reconnected IBKR ("Its connected") after being told the sync would follow; the list is in watch/digests/2026-11-02-triage.md. Every list was read back from IBKR afterwards.

- **AVOID (114):** 101 to 138, equal to the register's 138 active rows. Added: IPW (#10), GRRR (#11), MVIS (#12), BCTX, MGN, ENVX, GPRK, HCAI, NNOX, AMZE, OPTT, OSRH, LOTT, MIST, CDZI, LVWR, ESYN, TOPS, PPCB, SRTM, ARAI, FCHL, MASK, HUDI, RCON, ZTG, XRX, PTHS, VTEX, PARA (Parabolic Technologies, contract 938443339), CAPS (Capstone Holding, 935551478), MOBX, BCAB, OPNW, APVO, RCT (RedCloud, 758557374), NNUP. CABO (#13) was already on it.
- **CALLED (107):** 9 to 13: IPW, GRRR, MVIS, CABO.
- **Gov Filings pipeline findings (100):** 33 to 34: SEER (T019).
- Not changed: BMM stays off the AVOID list (dropped, no call); the ALL list was not touched.

## 2026-10-28: AVOID +15, CALLED +2, Gov Filings +2, merger arb +1 (from the 27 Oct filings)

The trader's go-ahead: "yeah make those changes" (28 Oct), for the list in watch/digests/2026-10-28-triage.md. Every list was read back from IBKR afterwards.

- **AVOID (114):** 86 to 101, equal to the register's 101 active rows.
  - Public calls: WORX (#8) and NIVF (#9).
  - Not takeable: CABR, IMNN, EDVA, WFF, ACTU, TELO, CHSN, XHLD, CDT, NCI (Neo-Concept on Nasdaq, not the Canadian NCI), IBO (Impact BioMedical on AMEX, not the Canadian IBO), SCKT and HYFM.
- **CALLED (107):** 7 to 9, adding WORX (#8) and NIVF (#9).
- **Gov Filings pipeline findings (100):** 31 to 33, adding NPB (T017) and ARTV (T018).
- **STRAT merger arb (tracked) (113):** 12 to 13, adding ULBI (T016). MFIC was optional and not added.

## 2026-10-27: CALLED (107) +6 public AVOID calls

The trader's go-ahead: "add them to CALLED as well" (27 Oct). Went from 1 (MTUS) to 7, read back from IBKR. Added the public AVOID calls DFNS (#2), NCT (#3), TMCR (#4), OSTX (#5), NNBR (#6) and NAUT (#7).

## 2026-10-27 (second change): AVOID (114) +12 from the 26 Oct filings

Went from 74 to 86, read back from IBKR and equal to the register's 86 active rows. Added:
- **Public AVOID calls:** NNBR (#6) and NAUT (#7).
- **Not takeable:** AQB, OBAI, PCSA, PBK, DCM (DeFi Capital Markets on AMEX, not the Canadian DCM), XPON, WHLR, SHFS, BBLG and DVLT.
- **MEDS** was already added in the first change.

## 2026-10-27: AVOID (114) rebuilt from the AVOID register

The trader's go-ahead: "Yeah clean it up but keep a log" (27 Oct). Before the change the list had 26 entries; after it, 74,
read back from IBKR and equal to the register's 74 active rows.

**Removed (4)**
- **TKNO:** the 22 Oct note reversed the AVOID ("the supply was absorbed above the deal price, so it is no longer an AVOID").
- **THRM:** an "AVOID (kill)" from 20 Oct. Reclassified as a killed long thesis, which is "dropped, no call" (rule 2026-10-27). The CEO and a director then bought $662.6k in the open market on 23 Oct.
- **CHDN:** an "AVOID (kill)" from 5 Oct (the logged strategic-alternatives 8-K was a false positive). Reclassified the same way.
- **Contract 853046979:** blank name, so it couldn't be identified. Most likely HCTI's contract from before its reverse split (inference). HCTI was re-added below under its current contract.

**Added (52)**
- **The public AVOID calls of 26 Oct:** DFNS (#2), NCT (#3), TMCR (#4), OSTX (#5).
- **HCTI:** AVOID since 5 Oct, now contract 937943818.
- **AVOIDs given in notes or triage but never put on the list:**
  - 18 Oct: AIOK.
  - 20 Oct: NWCL, AIAI, HOST, SDST (OTC only now), CABO, NVGS, FBYD, RMCF, ENHA.
  - 21 Oct: GRDX, MWYN, XTIA, CELU.
  - 22 Oct: GTBP, IMCC, VBIO, ADIL, SWBI.
  - 23 Oct: AEHL, TNON, AXG, AIRE, AMCI, PMI, JAGX, EONR, AMOD, LAB.
  - 26 Oct (not takeable): AMSS, MACI, ONFO, BURU, XXII, BOF, UFG, CTW, BGMS, ENSC, HODO, TRAW, HLSQ, BANL, YMT, MCRP, CNEY.
- **New today:** MEDS (dilution letter of intent, 26 Oct 8-K).

**Kept (22):** ELMT, TWST, CRMT, GOVX, SNTI, DYAI, GXAI, VHUB, FLD, GWHT (the old GWH, now OTC), POLA, CYAB, PUSA, TALO, SKYX, MOVE, IONQ, RXRX, GEMI, NKLR, BRUN and XRPN.
- On 27 Oct I wrongly said eight of these (IONQ, RXRX, GEMI, SKYX, MOVE, NKLR, PUSA, TALO) were not AVOIDs.
- In fact they are AVOIDs from the 12-18 Oct triage that were never added to the scoring file. The register now holds them.

## 2026-11-05

- **AVOID (114):** 162 -> 185. Added the 23 register rows dated 5 Nov: STIM, GRO, DSGN, ECOR, FTCI, CLNN, HMH, QNRX, CODX, GMHS, MCRB, PRPL, OCGN, EVAX, FISN, GRML, BIVI, SMX, DAIO, ARAY, JSPR, EHTH, ANVS. Read back: 185.
- **STRAT activist (112):** +VVR (T022). Read back: ESRT, SRTA, TCPC, XPOF, VVR.
- Approved by the trader in chat ("yeah make the IBKR changes").
