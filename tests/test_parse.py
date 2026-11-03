import pytest

from col_snap.parse import detect_delimiter, resolve_delimiter, split_rows


def test_detects_tab():
    assert detect_delimiter(["a\tb\tc", "1\t2\t3"]) == "\t"


def test_detects_comma():
    assert detect_delimiter(["name,qty", "apple,3", "pear,10"]) == ","


def test_detects_semicolon_over_comma_in_values():
    lines = ["name;price", "apple;1,50", "pear;2,25"]
    assert detect_delimiter(lines) == ";"


def test_detects_pipe():
    assert detect_delimiter(["a | b", "1 | 2"]) == "|"


def test_falls_back_to_whitespace():
    assert detect_delimiter(["foo bar", "baz qux"]) == " "


def test_inconsistent_commas_fall_back_to_whitespace():
    lines = ["Hello, world  greeting", "x  y", "a  b"]
    assert detect_delimiter(lines) == " "


def test_empty_input():
    assert split_rows([]) == []


def test_csv_quoted_fields_keep_commas():
    rows = split_rows(['name,city', '"Doe, Jane",Springfield'])
    assert rows == [["name", "city"], ["Doe, Jane", "Springfield"]]


def test_cells_are_stripped():
    assert split_rows(["a , b", "c ,d"]) == [["a", "b"], ["c", "d"]]


def test_blank_lines_and_newlines_dropped():
    assert split_rows(["a\tb\n", "\n", "c\td\r\n"]) == [["a", "b"], ["c", "d"]]


def test_whitespace_prefers_wide_gaps():
    lines = ["Date     Event", "Jan 3    Launch day", "Feb 14   Review"]
    assert split_rows(lines) == [
        ["Date", "Event"],
        ["Jan 3", "Launch day"],
        ["Feb 14", "Review"],
    ]


def test_whitespace_single_spaces():
    assert split_rows(["a b c", "dd ee ff"]) == [["a", "b", "c"], ["dd", "ee", "ff"]]


def test_explicit_delimiter():
    assert split_rows(["a:b", "c:d"], delimiter=":") == [["a", "b"], ["c", "d"]]


@pytest.mark.parametrize("name,expected", [("tab", "\t"), ("\\t", "\t"), (",", ","), ("space", " ")])
def test_resolve_delimiter(name, expected):
    assert resolve_delimiter(name) == expected


def test_resolve_delimiter_rejects_long_names():
    with pytest.raises(ValueError):
        resolve_delimiter("::")
