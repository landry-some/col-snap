"""Read and write markdown (GitHub-style pipe) tables."""

import re

from .align import CENTER, LEFT, RIGHT, display_width, fill_rows, pad

_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_SEPARATOR_CELL = re.compile(r":?-+:?")


def split_cells(line):
    """Split one table line on unescaped pipes, dropping the outer pipes."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.strip() for cell in _CELL_SPLIT.split(line)]


def _is_separator(line):
    cells = split_cells(line)
    return bool(cells) and all(_SEPARATOR_CELL.fullmatch(cell) for cell in cells)


def is_markdown_table(lines):
    """True when lines are a header row, a ---|--- row, then body rows."""
    lines = [line for line in lines if line.strip()]
    return len(lines) >= 2 and all("|" in line for line in lines) and _is_separator(lines[1])


def _marker_align(cell):
    if cell.startswith(":") and cell.endswith(":"):
        return CENTER
    if cell.endswith(":"):
        return RIGHT
    if cell.startswith(":"):
        return LEFT
    return None


def parse_table(lines):
    """Return (rows, aligns) for a markdown table.

    rows includes the header but not the separator row. aligns has one entry
    per separator cell: LEFT/RIGHT/CENTER from the colons, or None when the
    cell is plain dashes.
    """
    lines = [line for line in lines if line.strip()]
    header, separator, body = lines[0], lines[1], lines[2:]
    aligns = [_marker_align(cell) for cell in split_cells(separator)]
    rows = [split_cells(header)] + [split_cells(line) for line in body]
    # Escaped pipes stay escaped while parsing and are restored here.
    rows = [[cell.replace("\\|", "|") for cell in row] for row in rows]
    return rows, aligns


def _separator_cell(width, align):
    if align == CENTER:
        return ":" + "-" * (width - 2) + ":"
    if align == RIGHT:
        return "-" * (width - 1) + ":"
    return "-" * width


def render_table(rows, aligns=None):
    """Render rows as a padded markdown table; the first row is the header.

    LEFT and unset alignments are written as plain dashes, which markdown
    renders left-aligned.
    """
    rows = fill_rows([[cell.replace("|", "\\|") for cell in row] for row in rows])
    if not rows:
        return []
    columns = len(rows[0])
    aligns = list(aligns or [])[:columns]
    aligns += [None] * (columns - len(aligns))
    # Three is the narrowest separator that can hold ":-:".
    widths = [max(3, *(display_width(row[i]) for row in rows)) for i in range(columns)]

    def line(cells):
        return "| " + " | ".join(cells) + " |"

    out = [line(pad(cell, w, a or LEFT) for cell, w, a in zip(rows[0], widths, aligns))]
    out.append(line(_separator_cell(w, a) for w, a in zip(widths, aligns)))
    for row in rows[1:]:
        out.append(line(pad(cell, w, a or LEFT) for cell, w, a in zip(row, widths, aligns)))
    return out
