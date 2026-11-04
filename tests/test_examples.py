"""Golden-file tests: each file in examples/ must align to tests/golden/<name>.out.

After an intended output change, regenerate a golden file with
`colsnap examples/<name> > tests/golden/<name>.out` and review the diff.
"""

from pathlib import Path

import pytest

from col_snap.cli import main

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((ROOT / "examples").iterdir())
GOLDEN = ROOT / "tests" / "golden"


def test_every_example_has_a_golden_file():
    assert {path.name + ".out" for path in EXAMPLES} == {path.name for path in GOLDEN.iterdir()}


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.name)
def test_example_matches_golden(example, capsys):
    assert main([str(example)]) == 0
    expected = (GOLDEN / (example.name + ".out")).read_text(encoding="utf-8")
    assert capsys.readouterr().out == expected
