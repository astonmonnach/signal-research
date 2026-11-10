"""Rule 2026-11-10: code-P rows that are not open-market buys of common stock don't count, and one joint purchase
reported by two owners is one buyer (OBIO, ANVS, FFAI, APOG, LKFN and SYNX in the 6-9 Nov scans)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "watch"))
import scan_market  # noqa: E402


def form4(owner, rows, notes=""):
    body = "".join(f"""<nonDerivativeTransaction><securityTitle><value>{title}</value></securityTitle>
      <transactionDate><value>2026-11-06</value></transactionDate>
      <transactionCoding><transactionCode>{code}</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>{n}</value></transactionShares>
      <transactionPricePerShare><value>{px}</value>{'<footnoteId id="F1"/>' if notes else ''}</transactionPricePerShare>
      <transactionAcquiredDisposedCode><value>{ad}</value></transactionAcquiredDisposedCode></transactionAmounts>
      </nonDerivativeTransaction>""" for title, code, n, px, ad in rows)
    xml = f"""<ownershipDocument><issuer><issuerCik>0000000123</issuerCik></issuer>
      <reportingOwner><reportingOwnerId><rptOwnerName>{owner}</rptOwnerName></reportingOwnerId>
      <reportingOwnerRelationship><isDirector>1</isDirector></reportingOwnerRelationship></reportingOwner>
      <nonDerivativeTable>{body}</nonDerivativeTable>
      <footnotes><footnote id="F1">{notes}</footnote></footnotes></ownershipDocument>"""
    return f"<SEC-DOCUMENT><XML>\n{xml}\n</XML></SEC-DOCUMENT>".encode()


def run(monkeypatch, docs, tmp_path):
    paths = {f"acc{i}": f"edgar/data/123/00000000000000000{i}/acc{i}.txt" for i in range(len(docs))}
    by_path = {"https://www.sec.gov/Archives/" + p: d for p, d in zip(paths.values(), docs)}
    monkeypatch.setattr(scan_market, "get", lambda url, limit=None: by_path[url])
    monkeypatch.setattr(scan_market, "OUT", tmp_path)            # no earlier reports: today's lines only
    return scan_market.insider_buys(paths, {123: ["ABC"]}, {123}, date(2026, 11, 9))


def test_offering_purchases_preferred_and_drip_are_not_buys(monkeypatch, tmp_path):
    lines = run(monkeypatch, [
        form4("A", [("Common Stock", "P", 10000, 5.00, "A")], "Purchased in an underwritten public offering at the public offering price."),
        form4("B", [("Series A Preferred Stock", "P", 1, 100, "A")]),
        form4("C", [("Common Stock", "P", 52, 30.0, "A")], "Shares acquired through the issuer's dividend reinvestment plan."),
    ], tmp_path)
    assert not any(line.startswith("- **") for line in lines)
    assert any("Not counted as buys: 3 code-P rows" in line for line in lines)


def test_open_market_buys_by_two_insiders_still_make_a_cluster(monkeypatch, tmp_path):
    lines = run(monkeypatch, [form4("SMITH JOHN", [("Common Stock", "P", 20000, 4.00, "A")]),
                              form4("JONES ANN", [("Common Stock", "P", 5000, 4.10, "A")])], tmp_path)
    assert sum(line.startswith("- **") for line in lines) == 2
    assert any(line.startswith("- Clusters: ABC (2 insiders") for line in lines)


def test_one_joint_purchase_filed_twice_is_one_buyer(monkeypatch, tmp_path):
    lines = run(monkeypatch, [form4("KLEIN RON", [("Common Stock", "P", 19940, 0.99, "A")]),
                              form4("KLEIN SARA", [("Common Stock", "P", 19940, 0.99, "A")])], tmp_path)
    assert any("joint holding, one buyer" in line for line in lines)
    assert "- Clusters: none" in lines


def test_gift_bought_back_the_same_day_is_not_a_buy(monkeypatch, tmp_path):
    lines = run(monkeypatch, [form4("LAKE DIRECTOR", [("Common Stock", "G", 1918, 0, "D"), ("Common Stock", "P", 1918, 61.0, "A")])], tmp_path)
    assert not any(line.startswith("- **") for line in lines)


def test_security_titles():
    assert scan_market.not_open_market("Units", "")                 # ANVS: a share plus a warrant from the company
    assert not scan_market.not_open_market("Common Units", "")      # an MLP's common units are its equity
    assert not scan_market.not_open_market("Class A Common Stock", "")
