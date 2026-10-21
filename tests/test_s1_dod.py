import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "collectors"))
from s1_dod import Blocked, check_page, parse_awards  # noqa: E402

DENIED = """<HTML><HEAD>
<TITLE>Access Denied</TITLE>
</HEAD><BODY>
<H1>Access Denied</H1>
You don't have permission to access this server.
</BODY></HTML>"""


def test_access_denied_is_reported_as_a_block_not_a_layout_change():
    with pytest.raises(Blocked) as e:
        check_page(DENIED)
    assert "--html" in str(e.value)


def test_a_real_page_passes_the_check():
    page = '<div class="body"><p>ARMY</p><p>Acme Corp., Town, State, was awarded a $10,000,000 contract.</p></div>'
    assert check_page(page) == page


def test_a_saved_page_parses():
    page = ('<div class="body"><p>DEFENSE LOGISTICS AGENCY</p>'
            '<p>Acme Corp., Town, Texas (SPE604-27-D-8001, $38,136,143), has been awarded a contract.</p></div>')
    awards = parse_awards(page)
    assert len(awards) == 1 and awards[0]["agency"] == "Defense Logistics Agency"


TRIO = ("Constellation NewEnergy Inc., Baltimore, Maryland (SPE604-27-D-8000, $66,760,473); Direct Energy Business LLC, "
        "Houston, Texas (SPE604-27-D-8001,$38,136,143); and WGL Energy Services Inc., Vienna, Virginia (SPE604-27-D-8002, "
        "$19,256,344), have each been awarded a firm-fixed-price requirements contract.")


def test_multi_award_with_amounts_in_brackets_names_every_awardee():
    from s1_dod import parse_one
    a = parse_one(TRIO, "Defense Logistics Agency")
    assert a["names"] == ["Constellation NewEnergy Inc", "Direct Energy Business LLC", "WGL Energy Services Inc"]


def test_update_prefix_is_not_part_of_the_name():
    from s1_dod import parse_one
    a = parse_one("UPDATE: Maness Veteran Medical LLC,* Piney Flats, Tennessee (SPE2DH-27-D-0003, $41,000,000), "
                  "has been added as an awardee to the multiple award contract.", "Defense Logistics Agency")
    assert a["names"] == ["Maness Veteran Medical LLC"]
