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
