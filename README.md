# col-snap

`colsnap` is a small command-line filter that lines up the columns of ad-hoc
text tables. Pipe in command output, a CSV snippet or a messy markdown table,
and it prints the same rows with every column padded to the same width.

## Who it's for

People who paste tables into notes, READMEs, commit messages and chat, and
are tired of fixing the spacing by hand or fighting `column -t` over quoted
CSV fields, wide (CJK, emoji) characters and markdown pipes.

## Built with

- Python 3.11+, standard library only (`csv`, `unicodedata`, `argparse`)
- pytest for tests

## Install

Needs Python 3.11 or newer.

```bash
git clone https://github.com/landry-some/col-snap.git
cd col-snap
python3 -m venv .venv
.venv/bin/pip install -e .
```

This puts the `colsnap` command in `.venv/bin/`. Activate the venv
(`source .venv/bin/activate`) or call `.venv/bin/colsnap` directly.

## Usage

```
colsnap [FILE ...] [-d DELIM] [-a SPEC] [-f {plain,markdown,csv,tsv}]
        [-c COLS] [-g GAP]
```

With no files, or with `-`, it reads stdin. Output goes to stdout, so it works
as an editor filter (for example `:'<,'>!colsnap` in Vim).

### Delimiters

The delimiter is detected from the input: tab, `|`, `,` or `;`, whichever
splits the lines most consistently. If none fits, columns are split on
whitespace. Quoted CSV fields such as `"Doe, Jane"` stay in one cell.

```console
$ colsnap examples/groceries.csv
item           store             qty  price
Apples, green  Corner Market       6   2.40
Oat milk       Corner Market       2   3.15
Coffee beans   Example Roasters    1  11.90
Rice           Big Box Foods       1   4.05
```

For whitespace input, runs of two or more spaces separate columns when they do
so consistently. Otherwise any whitespace does, and extra words stay in the
last column, which suits `df` and `ps` output:

```console
$ colsnap examples/disk-usage.txt
Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/fake1  50G   21G   27G     44%  /
/dev/fake2  200G  150G  40G     79%  /home
tmpfs       3.9G  0     3.9G     0%  /dev/shm
```

Set the delimiter yourself with `-d`: a single character, or one of `tab`,
`comma`, `semicolon`, `pipe`, `space`.

### Wide characters

Cells are measured in terminal columns, not characters, so CJK text and emoji
(two columns each) and combining accents (zero columns) line up:

```console
$ colsnap examples/cities.tsv
city       country      population_m
東京       Japan                14.0
São Paulo  Brazil               11.5
Lagos      Nigeria              15.4
Zürich     Switzerland           0.4
```

### Alignment

Columns where every cell (apart from a text header) is a number are
right-aligned, everything else is left-aligned. Numbers may have a sign, `,`
thousands separators, a leading currency sign (`$`, `€`, `£`, `¥`) or a
trailing `%`, so `-$1,250.00` and `12.5%` both count. Override it per column with
`-a`, a comma-separated list of `l`, `r` and `c`. An empty entry keeps the
default for that column:

```bash
colsnap -a c,,l examples/groceries.csv   # center column 1, auto column 2, left column 3
```

`-g` sets the number of spaces between columns (default 2).

### Selecting columns

`-c` keeps only the listed columns, numbered from 1, in the order given. A
column can be repeated, and rows that are too short get an empty cell:

```console
$ colsnap -c 4,1 examples/groceries.csv
price  item
 2.40  Apples, green
 3.15  Oat milk
11.90  Coffee beans
 4.05  Rice
```

### Markdown tables

Input that is already a markdown table (header row, then a `---|---` row) is
re-aligned as markdown. The `:--`, `--:` and `:-:` markers are kept as
alignment, and `|` inside a cell is written as `\|`:

```console
$ colsnap examples/messy-table.md
| task                    | owner | hours |   status    |
| ----------------------- | ----- | ----: | :---------: |
| write parser            | me    |     3 |    done     |
| width handling for 東京 | me    |   1.5 |    done     |
| markdown output         | me    |     2 | in progress |
| docs                    | me    |     1 |    todo     |
```

Left-aligned columns are written with plain dashes (`---`), which markdown also
renders left-aligned. Use `-f markdown` to turn any other input into a markdown
table (the first row becomes the header), or `-f plain` to turn a markdown table
back into plain columns.

### Converting to CSV or TSV

`-f csv` and `-f tsv` write the parsed rows as delimited text instead of
aligning them. Cells that contain the delimiter or quotes are quoted, and short
rows get empty cells so every line has the same number of fields:

```console
$ colsnap -f csv examples/messy-table.md
task,owner,hours,status
write parser,me,3,done
width handling for 東京,me,1.5,done
markdown output,me,2,in progress
docs,me,1,todo
```

### Limits in v0.1

- Blank lines are dropped.
- Leading indentation is not kept.
- Long cells are never truncated or wrapped.

These are on the [roadmap](ROADMAP.md).

### Exit codes

| Code | Meaning |
| ---: | ------- |
| 0 | Success |
| 1 | A file could not be read, or the input is not UTF-8 |
| 2 | Bad command-line arguments |

## Tests

```bash
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
```

## License

MIT, see [LICENSE](LICENSE).
