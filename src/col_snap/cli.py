"""Command-line entry point for colsnap."""

import argparse
import sys

from . import __version__
from .align import align_rows, guess_aligns, merge_aligns, parse_align_spec
from .markdown import is_markdown_table, parse_table, render_table
from .parse import resolve_delimiter, split_rows


def build_parser():
    parser = argparse.ArgumentParser(
        prog="colsnap",
        description="Line up the columns of text tables read from files or stdin.",
    )
    parser.add_argument("files", nargs="*", help="files to read (default: stdin, '-' also means stdin)")
    parser.add_argument(
        "-d",
        "--delimiter",
        help="column delimiter: one character, or tab/comma/semicolon/pipe/space "
        "(default: detect it)",
    )
    parser.add_argument(
        "-a",
        "--align",
        help="alignment per column, comma-separated l/r/c, e.g. 'l,r,,c'; an empty entry "
        "keeps the default (numbers right, text left)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["plain", "markdown"],
        help="output format (default: markdown when the input is a markdown table, else plain)",
    )
    parser.add_argument("-g", "--gap", type=int, default=2, help="spaces between columns (default: 2)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def read_lines(files):
    if not files:
        return sys.stdin.readlines()
    lines = []
    for name in files:
        if name == "-":
            lines += sys.stdin.readlines()
        else:
            with open(name, encoding="utf-8") as fh:
                lines += fh.readlines()
    return lines


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gap < 0:
        parser.error("--gap must be 0 or more")
    delimiter = None
    if args.delimiter is not None:
        try:
            delimiter = resolve_delimiter(args.delimiter)
        except ValueError as exc:
            parser.error(str(exc))
    spec = []
    if args.align is not None:
        try:
            spec = parse_align_spec(args.align)
        except ValueError as exc:
            parser.error(str(exc))

    try:
        lines = read_lines(args.files)
    except OSError as exc:
        print(f"colsnap: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as exc:
        print(f"colsnap: input is not valid UTF-8: {exc}", file=sys.stderr)
        return 1

    if delimiter is None and is_markdown_table(lines):
        rows, markers = parse_table(lines)
        out_format = args.format or "markdown"
    else:
        rows, markers = split_rows(lines, delimiter), []
        out_format = args.format or "plain"

    # Priority: --align, then markdown :--: markers, then the numeric guess.
    aligns = merge_aligns(merge_aligns(guess_aligns(rows), markers), spec)
    if out_format == "markdown":
        out = render_table(rows, aligns)
    else:
        out = align_rows(rows, aligns=aligns, gap=args.gap)
    for line in out:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
