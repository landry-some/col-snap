"""Split lines of text into rows of cells."""

import csv
import io
import re
from collections import Counter

from .align import fill_rows
from .markdown import split_cells

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
        # Drops the outer pipes of "| a | b |" rows.
        return split_cells(line)
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


def join_rows(rows, delimiter):
    """Write rows as delimited text (CSV or TSV), quoting cells where needed.

    Short rows are padded with empty cells so every line has the same fields.
    """
    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter, lineterminator="")
    lines = []
    for row in fill_rows(rows):
        writer.writerow(row)
        lines.append(out.getvalue())
        out.seek(0)
        out.truncate()
    return lines


def parse_columns_spec(spec):
    """Turn "3,1" into the zero-based indexes [2, 0]."""
    indexes = []
    for part in spec.split(","):
        part = part.strip()
        if not part.isdigit() or int(part) < 1:
            raise ValueError(f"column numbers start at 1: {part!r}")
        indexes.append(int(part) - 1)
    return indexes


def select_columns(rows, indexes):
    """Keep only the given columns, in the given order; missing cells are empty."""
    return [[row[i] if i < len(row) else "" for i in indexes] for row in rows]
