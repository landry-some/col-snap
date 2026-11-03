from col_snap.align import CENTER, LEFT, RIGHT
from col_snap.markdown import is_markdown_table, parse_table, render_table, split_cells


def test_split_cells_outer_pipes():
    assert split_cells("| a | b |") == ["a", "b"]
    assert split_cells("a | b") == ["a", "b"]


def test_split_cells_keeps_escaped_pipes():
    assert split_cells(r"| a \| b | c |") == [r"a \| b", "c"]


def test_is_markdown_table():
    assert is_markdown_table(["| a | b |", "|---|:-:|", "| 1 | 2 |"])
    assert is_markdown_table(["a|b", "-|-"])


def test_not_markdown_without_separator():
    assert not is_markdown_table(["a | b", "1 | 2"])
    assert not is_markdown_table(["| a |"])


def test_parse_table():
    rows, aligns = parse_table(["|name|qty|note|kind|", "|:--|--:|:-:|---|", "|apple|3|ok|x|"])
    assert rows == [["name", "qty", "note", "kind"], ["apple", "3", "ok", "x"]]
    assert aligns == [LEFT, RIGHT, CENTER, None]


def test_parse_table_unescapes_pipes():
    rows, _ = parse_table(["| cmd |", "| --- |", r"| a \| b |"])
    assert rows == [["cmd"], ["a | b"]]


def test_render_table():
    rows = [["name", "qty"], ["apple", "3"], ["kiwi", "10"]]
    assert render_table(rows, [None, RIGHT]) == [
        "| name  | qty |",
        "| ----- | --: |",
        "| apple |   3 |",
        "| kiwi  |  10 |",
    ]


def test_render_table_center_and_min_width():
    assert render_table([["a"], ["b"]], [CENTER]) == [
        "|  a  |",
        "| :-: |",
        "|  b  |",
    ]


def test_render_table_escapes_pipes_and_fills_ragged_rows():
    assert render_table([["cmd", "x"], ["a | b"]]) == [
        "| cmd    | x   |",
        "| ------ | --- |",
        r"| a \| b |     |",
    ]


def test_render_wide_characters():
    assert render_table([["city"], ["東京"]]) == [
        "| city |",
        "| ---- |",
        "| 東京 |",
    ]


def test_round_trip_is_stable():
    lines = ["|name|qty|", "|---|--:|", "|apple|3|", "|kiwi|10|"]
    rows, aligns = parse_table(lines)
    once = render_table(rows, aligns)
    rows2, aligns2 = parse_table(once)
    assert render_table(rows2, aligns2) == once


def test_render_empty():
    assert render_table([]) == []
