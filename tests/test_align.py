from col_snap.align import (
    CENTER,
    RIGHT,
    align_rows,
    column_widths,
    display_width,
    fill_rows,
    pad,
)


def test_ascii_width():
    assert display_width("hello") == 5


def test_cjk_is_double_width():
    assert display_width("東京") == 4


def test_emoji_is_double_width():
    assert display_width("🍎") == 2


def test_combining_marks_take_no_space():
    assert display_width("é") == 1


def test_pad_left_right_center():
    assert pad("ab", 5) == "ab   "
    assert pad("ab", 5, RIGHT) == "   ab"
    assert pad("ab", 5, CENTER) == " ab  "


def test_pad_wide_text():
    assert pad("東京", 6) == "東京  "


def test_fill_rows_ragged():
    assert fill_rows([["a"], ["b", "c", "d"]]) == [["a", "", ""], ["b", "c", "d"]]


def test_column_widths():
    assert column_widths([["a", "bbb"], ["cc", "d"]]) == [2, 3]


def test_align_rows_basic():
    rows = [["name", "qty"], ["apple", "3"], ["kiwi", "10"]]
    assert align_rows(rows) == [
        "name   qty",
        "apple  3",
        "kiwi   10",
    ]


def test_align_rows_wide_characters_line_up():
    rows = [["city", "code"], ["東京", "TYO"], ["Lima", "LIM"]]
    lines = align_rows(rows)
    assert [display_width(line[:-3]) for line in lines[1:]] == [6, 6]
    assert lines[1] == "東京  TYO"


def test_align_rows_custom_gap_and_align():
    rows = [["a", "1"], ["bb", "22"]]
    assert align_rows(rows, aligns=["l", "r"], gap=1) == ["a   1", "bb 22"]


def test_align_rows_trims_trailing_spaces():
    assert align_rows([["a", ""], ["b", "c"]]) == ["a", "b  c"]


def test_align_rows_empty():
    assert align_rows([]) == []


import pytest

from col_snap.align import LEFT, guess_aligns, is_numeric, merge_aligns, parse_align_spec


@pytest.mark.parametrize("text", ["0", "42", "-3", "+7", "3.14", ".5", "10.", "1e9", "-2.5E-3"])
def test_is_numeric(text):
    assert is_numeric(text)


@pytest.mark.parametrize("text", ["", "abc", "1.2.3", "12px", "1,000", "--1", "e5"])
def test_is_not_numeric(text):
    assert not is_numeric(text)


def test_guess_aligns_skips_header():
    rows = [["name", "qty", "price"], ["apple", "3", "1.50"], ["kiwi", "10", ""]]
    assert guess_aligns(rows) == [LEFT, RIGHT, RIGHT]


def test_guess_aligns_mixed_column_stays_left():
    rows = [["id", "size"], ["1", "12"], ["2", "big"]]
    assert guess_aligns(rows) == [RIGHT, LEFT]


def test_guess_aligns_numeric_first_row_is_data():
    rows = [["1", "a"], ["22", "b"]]
    assert guess_aligns(rows) == [RIGHT, LEFT]


def test_guess_aligns_empty_column_is_left():
    assert guess_aligns([["a", ""], ["b", ""]]) == [LEFT, LEFT]


def test_guess_aligns_no_rows():
    assert guess_aligns([]) == []


def test_parse_align_spec():
    assert parse_align_spec("l,R, center,,right") == [LEFT, RIGHT, CENTER, None, RIGHT]


def test_parse_align_spec_rejects_unknown():
    with pytest.raises(ValueError):
        parse_align_spec("l,x")


def test_merge_aligns_overrides_and_ignores_extra():
    assert merge_aligns([LEFT, RIGHT, LEFT], [None, LEFT, CENTER, RIGHT]) == [LEFT, LEFT, CENTER]


def test_numbers_right_aligned_end_to_end():
    rows = [["name", "qty"], ["apple", "3"], ["kiwi", "10"]]
    assert align_rows(rows, aligns=guess_aligns(rows)) == [
        "name   qty",
        "apple    3",
        "kiwi    10",
    ]
