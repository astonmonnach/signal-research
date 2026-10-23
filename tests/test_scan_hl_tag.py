import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "watch"))
from scan_market import same_asset, tag_hl  # noqa: E402

HL = {"TWST": [{"name": "xyz:TWST", "lev": 10, "px": 20.0}],
      "SNDK": [{"name": "io:SNDK", "lev": 10, "px": 100.0}, {"name": "xyz:SNDK", "lev": 10, "px": 101.0}],
      "GOLD": [{"name": "xyz:GOLD", "lev": 20, "px": 4100.0}],     # the gold commodity, not the GOLD stock
      "SOL": [{"name": "SOL", "lev": 20, "px": 180.0}]}            # main exchange = crypto token, never a stock
CHECK = lambda t, mk: t != "GOLD"


def test_line_for_a_listed_company_gets_the_tag():
    out = tag_hl(["- **TWST** Twist Bioscience `424B5` [filing index](x)"], HL, CHECK)
    assert out == ["- **TWST** Twist Bioscience `424B5` [filing index](x) **[Hyperliquid: xyz:TWST 10x]**"]


def test_multi_ticker_bold_group_matches_any_ticker():
    out = tag_hl(["- **SNDK/SNDKW** Sandisk `8-K`"], HL, CHECK)
    assert out[0].endswith("**[Hyperliquid: io:SNDK 10x, xyz:SNDK 10x]**")


def test_other_lines_untouched():
    lines = ["# Scan", "- **ABCD** Something `8-K`", "- _note line_", "plain text"]
    assert tag_hl(lines, HL, CHECK) == lines


def test_relevant_marker_inside_bold_is_ignored():
    out = tag_hl(["- **TWST** (relevant) did a thing `8-K`"], HL, CHECK)
    assert "Hyperliquid: xyz:TWST" in out[0]


def test_same_symbol_but_a_different_asset_is_not_tagged():
    line = "- **GOLD** Gold.com `4` insider buy"
    assert tag_hl([line], HL, CHECK) == [line]


def test_main_exchange_crypto_token_is_never_a_stock():
    line = "- **SOL** Emeren `8-K`"
    assert tag_hl([line], HL, lambda t, mk: None) == [line]


def test_unchecked_market_is_tagged_but_says_so():
    out = tag_hl(["- **TWST** Twist Bioscience `424B5`"], HL, lambda t, mk: None)
    assert out[0].endswith("**[Hyperliquid: xyz:TWST 10x, not checked]**")


def _days(n):
    return [f"2026-10-{d:02d}" for d in range(1, n + 1)]


def test_same_asset_when_prices_move_together():
    stock = dict(zip(_days(12), [10, 10.5, 10.2, 10.8, 11, 10.6, 10.9, 11.4, 11.1, 11.6, 11.3, 11.8]))
    perp = {d: p * 1.01 for d, p in stock.items()}
    assert same_asset(perp, stock) is True


def test_different_asset_with_a_similar_price_is_rejected():
    stock = dict(zip(_days(12), [97, 97.5, 97.2, 97.8, 98, 97.6, 97.9, 98.4, 98.1, 98.6, 98.3, 98.8]))
    perp = dict(zip(_days(12), [101, 99, 102, 98, 100, 103, 99, 97, 101, 98, 102, 99]))
    assert same_asset(perp, stock) is False


def test_far_apart_prices_are_rejected_and_short_history_falls_back_to_price():
    assert same_asset({"2026-10-01": 4100.0}, {"2026-10-01": 38.0}) is False
    assert same_asset({"2026-10-01": 20.2}, {"2026-10-01": 20.0}) is True
    assert same_asset({}, {"2026-10-01": 20.0}) is None
