"""Rule 2026-11-10: code-P rows that are not open-market buys of common stock don't count, and one joint purchase
reported by two owners is one buyer (OBIO, ANVS, FFAI, APOG, LKFN and SYNX in the 6-9 Nov scans)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "watch"))
import scan_market  # noqa: E402


def form4(owner, rows, notes=""):
    rows = [r if len(r) == 6 else (*r, "2026-11-06") for r in rows]   # optional 6th item: the transaction date
    body = "".join(f"""<nonDerivativeTransaction><securityTitle><value>{title}</value></securityTitle>
      <transactionDate><value>{day}</value></transactionDate>
      <transactionCoding><transactionCode>{code}</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>{n}</value></transactionShares>
      <transactionPricePerShare><value>{px}</value>{'<footnoteId id="F1"/>' if notes else ''}</transactionPricePerShare>
      <transactionAcquiredDisposedCode><value>{ad}</value></transactionAcquiredDisposedCode></transactionAmounts>
      </nonDerivativeTransaction>""" for title, code, n, px, ad, day in rows)
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


def test_sale_on_another_day_in_the_same_form_is_netted(monkeypatch, tmp_path):
    """Rule 2026-11-11 (MX): sold 378,252 on 6 Nov, bought 268,009 on 6 Nov and 300,000 on 9 Nov = net +189,757."""
    lines = run(monkeypatch, [form4("AMORUSO", [("Common Stock", "S", 378252, 2.2225, "D", "2026-11-06"),
                                                ("Common Stock", "P", 268009, 2.3586, "A", "2026-11-06"),
                                                ("Common Stock", "P", 300000, 2.4634, "A", "2026-11-09")])], tmp_path)
    buy = [line for line in lines if line.startswith("- **")]
    assert len(buy) == 1 and "also sold 110,243 more shares: net +189,757" in buy[0]
    assert "bought 300,000 shares at $2.46 = $739,020" in buy[0]   # the gross line keeps the real price


def test_net_seller_is_not_a_buy(monkeypatch, tmp_path):
    lines = run(monkeypatch, [form4("SELLER", [("Common Stock", "S", 50000, 10.0, "D", "2026-11-05"),
                                               ("Common Stock", "P", 1000, 10.0, "A", "2026-11-06")])], tmp_path)
    assert not any(line.startswith("- **") for line in lines)
    assert any("1 Form 4 that sold at least as many shares as they bought" in line for line in lines)


def test_security_titles():
    assert scan_market.not_open_market("Units", "")                 # ANVS: a share plus a warrant from the company
    assert not scan_market.not_open_market("Common Units", "")      # an MLP's common units are its equity
    assert not scan_market.not_open_market("Class A Common Stock", "")
