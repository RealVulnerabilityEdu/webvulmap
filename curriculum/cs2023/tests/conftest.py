"""Test fixtures for cs2023 parser tests."""

import json
import subprocess
import sys
import typing as t
from pathlib import Path

import pytest

# conftest.py lives at: webvulmap/curriculum/cs2023/tests/conftest.py
# parents[0] = .../tests
# parents[1] = .../cs2023  ← this is what we want
CS2023_DIR = Path(__file__).resolve().parents[1]
PARSER = CS2023_DIR / "parse_ka_text_to_json.py"
SCHEMA = CS2023_DIR / "ka.schema.json"
FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = FIXTURES / "SE.golden.json"


def read_json(p: Path) -> t.Any:
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def cs2023_dir() -> Path:
    return CS2023_DIR


@pytest.fixture(scope="session")
def parser_path() -> Path:
    assert PARSER.exists(), f"Parser not found: {PARSER}"
    return PARSER


@pytest.fixture(scope="session")
def schema_path() -> Path:
    assert SCHEMA.exists(), f"Schema not found: {SCHEMA}"
    return SCHEMA


@pytest.fixture(scope="session")
def golden_path() -> Path:
    assert GOLDEN.exists(), f"Golden not found: {GOLDEN}"
    return GOLDEN


@pytest.fixture()
def run_parser():
    """
    Returns a function:
    (inp: Path|None, out: Path|None) -> (returncode, stdout, stderr)
    """

    def _run(inp: Path | None = None, out: Path | None = None):
        cmd = [sys.executable, str(PARSER)]
        if inp is not None:
            cmd.append(str(inp))
        if out is not None:
            cmd.append(str(out))
        proc = None
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            return proc.returncode, (proc.stdout or ""), (proc.stderr or "")
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed: {e}")
            return e.returncode, (e.stdout or ""), (e.stderr or "")

    return _run


@pytest.fixture()
def write_text(tmp_path: Path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _write
