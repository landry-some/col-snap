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

Usage and install instructions are written as each feature lands; see
ROADMAP.md for the plan after v0.1.

## License

MIT, see [LICENSE](LICENSE).
