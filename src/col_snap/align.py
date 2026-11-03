"""Pad rows of cells into aligned lines, measuring cells by display width."""

import unicodedata

LEFT, RIGHT, CENTER = "l", "r", "c"


def char_width(ch):
    """Columns a character takes in a terminal: 0, 1 or 2."""
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def display_width(text):
    return sum(char_width(ch) for ch in text)


def pad(text, width, align=LEFT):
    """Pad text with spaces up to width display columns."""
    space = max(width - display_width(text), 0)
    if align == RIGHT:
        return " " * space + text
    if align == CENTER:
        left = space // 2
        return " " * left + text + " " * (space - left)
    return text + " " * space


def fill_rows(rows):
    """Give every row the same number of cells by appending empty ones."""
    columns = max((len(row) for row in rows), default=0)
    return [row + [""] * (columns - len(row)) for row in rows]


def column_widths(rows):
    rows = fill_rows(rows)
    if not rows:
        return []
    return [max(display_width(cell) for cell in column) for column in zip(*rows)]


def align_rows(rows, aligns=None, gap=2):
    """Return one aligned line per row.

    aligns is a list of LEFT/RIGHT/CENTER per column; missing entries are LEFT.
    Trailing spaces are trimmed from each line.
    """
    rows = fill_rows(rows)
    widths = column_widths(rows)
    aligns = list(aligns or [])
    aligns += [LEFT] * (len(widths) - len(aligns))
    sep = " " * gap
    return [
        sep.join(pad(cell, width, align) for cell, width, align in zip(row, widths, aligns)).rstrip()
        for row in rows
    ]
