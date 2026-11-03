"""Split lines of text into rows of cells."""

import csv
import re
from collections import Counter

# Checked in this order, so on a tie the earlier one wins.
CANDIDATES = ["\t", "|", ",", ";"]

# Names accepted by -d besides a literal single character.
NAMED = {"tab": "\t", "\\t": "\t", "comma": ",", "semicolon": ";", "pipe": "|", "space": " "}

WHITESPACE = " "
_WIDE_GAP = re.compile(r"\s{2,}")
_ANY_GAP = re.compile(r"\s+")


def resolve_delimiter(name):
    """Turn a -d value into a delimiter character."""
    if name in NAMED:
        return NAMED[name]
    if len(name) != 1:
        raise ValueError(f"delimiter must be one character or one of {', '.join(NAMED)}: {name!r}")
    return name


def _split_line(line, delimiter):
    if delimiter == "|":
        return [cell.strip() for cell in line.split("|")]
    # csv understands quoted fields such as "Smith, Jane".
    row = next(csv.reader([line], delimiter=delimiter, skipinitialspace=True))
    return [cell.strip() for cell in row]


def _consistency(lines, delimiter):
    """Share of lines whose field count equals the most common count."""
    counts = Counter(len(_split_line(line, delimiter)) for line in lines)
    fields, hits = counts.most_common(1)[0]
    if fields < 2:
        return 0.0
    return hits / len(lines)


def detect_delimiter(lines):
    """Guess the delimiter, falling back to whitespace."""
    lines = [line for line in lines if line.strip()]
    if not lines:
        return WHITESPACE
    best, best_score = WHITESPACE, 0.5
    for candidate in CANDIDATES:
        if not any(candidate in line for line in lines):
            continue
        score = _consistency(lines, candidate)
        if score > best_score:
            best, best_score = candidate, score
    return best


def _split_whitespace(lines):
    # Command output like `df` or `ps` separates columns with runs of spaces,
    # while single spaces may sit inside a cell ("Jan 3"). Prefer the wide gaps
    # when the text has any.
    gap = _WIDE_GAP if any(_WIDE_GAP.search(line.strip()) for line in lines) else _ANY_GAP
    return [gap.split(line.strip()) for line in lines]


def split_rows(lines, delimiter=None):
    """Split non-blank lines into lists of stripped cells.

    With delimiter=None the delimiter is detected from the lines.
    """
    lines = [line.rstrip("\r\n") for line in lines]
    lines = [line for line in lines if line.strip()]
    if delimiter is None:
        delimiter = detect_delimiter(lines)
    if delimiter == WHITESPACE:
        return _split_whitespace(lines)
    return [_split_line(line, delimiter) for line in lines]
