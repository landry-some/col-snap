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


def test_whitespace_uneven_gaps_fall_back_to_any_space():
    lines = [
        "Filesystem      Size  Used Avail Use% Mounted on",
        "/dev/sda1  20G  12G 7G  63% /",
        "tmpfs 2.0G 0 2.0G 0% /dev/shm",
    ]
    rows = split_rows(lines)
    assert rows[0] == ["Filesystem", "Size", "Used", "Avail", "Use%", "Mounted on"]
    assert rows[1] == ["/dev/sda1", "20G", "12G", "7G", "63%", "/"]
    assert rows[2] == ["tmpfs", "2.0G", "0", "2.0G", "0%", "/dev/shm"]


def test_whitespace_last_column_keeps_command_args():
    lines = [
        "PID TTY TIME CMD",
        "101 pts/0 00:00:01 bash",
        "202 pts/0 00:00:00 python3 -m http.server 8000",
    ]
    rows = split_rows(lines)
    assert rows[2] == ["202", "pts/0", "00:00:00", "python3 -m http.server 8000"]
