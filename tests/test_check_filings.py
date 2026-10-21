import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "watch"))
from check_filings import digest_text  # noqa: E402


def test_first_run_of_the_day_writes_header_and_lines():
    out = digest_text(None, ["- **ELMT** 8-K"], "2026-10-21")
    assert out == "# Filings digest 2026-10-21\n\n- **ELMT** 8-K\n"


def test_nothing_new_on_first_run_says_so():
    assert "No new filings of interest." in digest_text(None, [], "2026-10-21")


def test_rerun_with_nothing_new_keeps_the_earlier_list():
    first = digest_text(None, ["- **ELMT** 8-K"], "2026-10-21")
    assert digest_text(first, [], "2026-10-21") == first


def test_rerun_with_new_lines_appends():
    first = digest_text(None, ["- **ELMT** 8-K"], "2026-10-21")
    out = digest_text(first, ["- **SKYA** SC TO-I/A"], "2026-10-21")
    assert "- **ELMT** 8-K" in out and out.rstrip().endswith("- **SKYA** SC TO-I/A")


def test_rerun_replaces_an_earlier_nothing_new():
    first = digest_text(None, [], "2026-10-21")
    out = digest_text(first, ["- **ELMT** 8-K"], "2026-10-21")
    assert "No new filings of interest." not in out and "- **ELMT** 8-K" in out
