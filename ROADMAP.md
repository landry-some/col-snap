# Roadmap

Planned work after v0.1. Estimates are rough, in hours.

## Features

- [ ] `--max-width N` to truncate or wrap long cells so the table fits the terminal (3 h)
- [ ] Box-drawing output style (`-f box`) with Unicode or ASCII borders (2 h)
- [x] CSV and TSV output, so colsnap can also convert between formats (1 h)
- [x] `--columns 1,3` to select and reorder columns (1.5 h)
- [ ] Keep comment lines (`#`) and blank lines in place while aligning the rows around them (1.5 h)
- [ ] Preserve leading indentation, so tables inside code comments stay indented (1 h)
- [ ] Align on a custom separator token, e.g. `=` in config files or `:` in YAML-ish lists (2 h)
- [ ] Neovim / VS Code snippets in the README for running colsnap on a selection (1 h)

## Bugs and edge cases

- [ ] Escaped pipes (`\|`) and inline code containing `|` inside markdown cells (1.5 h)
- [ ] Mixed line endings (CRLF input) and a missing final newline (0.5 h)
- [ ] Better delimiter detection when the first lines disagree (header vs data) (1.5 h)
- [x] Numbers with thousands separators, currency signs and percentages counted as numeric (1 h)
- [ ] Zero-width joiner emoji sequences and other width corner cases (1.5 h)
- [ ] Decimal-point alignment for numeric columns with different precision (1.5 h)

## Refactors

- [ ] Split parsing and rendering into reader/writer modules with a shared table type (1.5 h)
- [ ] Config file (`~/.config/col-snap/config.toml`) for default gap, format and delimiter (1.5 h)

## Tests

- [ ] Property-style tests: aligning twice gives the same output as aligning once (1 h)
- [ ] Golden-file tests over the files in `examples/` (1 h)
- [ ] CI workflow running the tests on Linux, macOS and Windows (1 h)

## Docs

- [ ] Man page and `--help` examples (1 h)
- [ ] Recipes section: `ps`, `df`, `git log --format` and CSV exports piped through colsnap (1 h)
- [ ] CHANGELOG and a first tagged release (0.5 h)

Total: about 29 hours.
