import io
import subprocess
import sys

import pytest

from col_snap.cli import main


def run(monkeypatch, capsys, argv, stdin=""):
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    code = main(argv)
    out, err = capsys.readouterr()
    return code, out, err


def test_aligns_stdin(monkeypatch, capsys):
    code, out, _ = run(monkeypatch, capsys, [], "name,qty\napple,3\nkiwi,10\n")
    assert code == 0
    assert out == "name   qty\napple    3\nkiwi    10\n"


def test_reads_files(tmp_path, monkeypatch, capsys):
    path = tmp_path / "t.tsv"
    path.write_text("a\tbb\nccc\td\n", encoding="utf-8")
    code, out, _ = run(monkeypatch, capsys, [str(path)])
    assert code == 0
    assert out == "a    bb\nccc  d\n"


def test_dash_reads_stdin(tmp_path, monkeypatch, capsys):
    path = tmp_path / "t.txt"
    path.write_text("x|y\n", encoding="utf-8")
    code, out, _ = run(monkeypatch, capsys, [str(path), "-"], "long|z\n")
    assert out == "x     y\nlong  z\n"


def test_delimiter_and_gap(monkeypatch, capsys):
    code, out, _ = run(monkeypatch, capsys, ["-d", ":", "-g", "1"], "a:b\ncc:d\n")
    assert out == "a  b\ncc d\n"


def test_missing_file(monkeypatch, capsys):
    code, out, err = run(monkeypatch, capsys, ["/nonexistent/file.txt"])
    assert code == 1
    assert "No such file" in err


def test_bad_delimiter_is_usage_error(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc:
        run(monkeypatch, capsys, ["-d", "::"])
    assert exc.value.code == 2


def test_negative_gap_is_usage_error(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc:
        run(monkeypatch, capsys, ["-g", "-1"])
    assert exc.value.code == 2


def test_module_entry_point():
    result = subprocess.run(
        [sys.executable, "-m", "col_snap.cli"],
        input="a b\nccc d\n",
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == "a    b\nccc  d\n"


def test_align_flag_overrides_guess(monkeypatch, capsys):
    code, out, _ = run(monkeypatch, capsys, ["-a", "r,l"], "name,qty\napple,3\nkiwi,10\n")
    assert out == " name  qty\napple  3\n kiwi  10\n"


def test_align_flag_empty_entry_keeps_guess(monkeypatch, capsys):
    code, out, _ = run(monkeypatch, capsys, ["-a", "c,"], "id,qty\nab,3\nabcd,10\n")
    assert out == " id   qty\n ab     3\nabcd   10\n"


def test_bad_align_is_usage_error(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc:
        run(monkeypatch, capsys, ["-a", "q"])
    assert exc.value.code == 2
