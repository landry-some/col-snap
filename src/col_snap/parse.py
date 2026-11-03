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
    lines = [line.strip() for line in lines]
    if not lines:
        return []
    counts = Counter(len(_ANY_GAP.split(line)) for line in lines)
    columns = counts.most_common(1)[0][0]
    # Single spaces may sit inside a cell ("Jan 3"). Runs of 2+ spaces win when
    # they split every line into the same number of cells, and into no fewer
    # cells than a plain whitespace split usually gives (right-aligned columns
    # in `ps` output would otherwise merge).
    wide = [_WIDE_GAP.split(line) for line in lines]
    wide_counts = {len(row) for row in wide}
    if len(wide_counts) == 1 and 2 <= min(wide_counts) and min(wide_counts) >= columns:
        return wide
    # Otherwise split on any whitespace. Command output like `df` or `ps` has a
    # last column that may contain spaces ("Mounted on", command arguments), so
    # extra words are kept together in the last cell.
    return [_ANY_GAP.split(line, maxsplit=columns - 1) for line in lines]


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
