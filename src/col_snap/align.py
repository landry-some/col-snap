"""Pad rows of cells into aligned lines, measuring cells by display width."""

import re
import unicodedata

LEFT, RIGHT, CENTER = "l", "r", "c"
ALIGNS = {"l": LEFT, "left": LEFT, "r": RIGHT, "right": RIGHT, "c": CENTER, "center": CENTER}

# An optional sign and currency sign, digits with optional "," thousands
# groups, then an optional exponent or percent sign: -3, $1,250.00, 12.5%.
_NUMBER = re.compile(
    r"([+-]?[$€£¥]?|[$€£¥][+-])"
    r"((\d{1,3}(,\d{3})+|\d+)(\.\d*)?|\.\d+)"
    r"([eE][+-]?\d+|%)?"
)


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


def is_numeric(text):
    return bool(_NUMBER.fullmatch(text))


def guess_aligns(rows):
    """RIGHT for columns whose non-empty cells are all numbers, else LEFT.

    The first row is ignored when it isn't numeric itself, since it is usually
    a header.
    """
    rows = fill_rows(rows)
    if rows and not any(is_numeric(cell) for cell in rows[0]):
        body = rows[1:]
    else:
        body = rows
    aligns = []
    for index in range(len(rows[0]) if rows else 0):
        cells = [row[index] for row in body if row[index]]
        aligns.append(RIGHT if cells and all(is_numeric(c) for c in cells) else LEFT)
    return aligns


def parse_align_spec(spec):
    """Turn "l,r,c" into [LEFT, RIGHT, CENTER]. An empty entry means auto (None)."""
    aligns = []
    for part in spec.split(","):
        part = part.strip().lower()
        if not part:
            aligns.append(None)
        elif part in ALIGNS:
            aligns.append(ALIGNS[part])
        else:
            raise ValueError(f"unknown alignment {part!r}, use l, r or c")
    return aligns


def merge_aligns(guessed, spec):
    """Use spec where it has an entry, the guess everywhere else."""
    merged = list(guessed)
    for index, align in enumerate(spec):
        if align is None:
            continue
        if index < len(merged):
            merged[index] = align
    return merged


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
