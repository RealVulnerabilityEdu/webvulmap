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
V2_CONVERTER = CS2023_DIR / "parse_v1_to_v2.py"
SCHEMA = CS2023_DIR / "ka.schema.json"
SCHEMA_V2 = CS2023_DIR / "ka.schema.v2.json"
FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = FIXTURES / "SE.golden.json"
GOLDEN_V2 = FIXTURES / "SE.golden.v2.json"


def read_json(p: Path) -> t.Any:
    """Read and parse JSON file."""
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def cs2023_dir() -> Path:
    """Return the cs2023 directory path."""
    return CS2023_DIR


@pytest.fixture(scope="session")
def parser_path() -> Path:
    """Return the v1 parser script path."""
    assert PARSER.exists(), f"Parser not found: {PARSER}"
    return PARSER


@pytest.fixture(scope="session")
def schema_path() -> Path:
    """Return the v1 JSON schema path."""
    assert SCHEMA.exists(), f"Schema not found: {SCHEMA}"
    return SCHEMA


@pytest.fixture(scope="session")
def golden_path() -> Path:
    """Return the v1 golden file path."""
    assert GOLDEN.exists(), f"Golden not found: {GOLDEN}"
    return GOLDEN


@pytest.fixture(scope="session")
def schema_v2_path() -> Path:
    """Return the v2 JSON schema path."""
    assert SCHEMA_V2.exists(), f"Schema v2 not found: {SCHEMA_V2}"
    return SCHEMA_V2


@pytest.fixture(scope="session")
def golden_v2_path() -> Path:
    """Return the v2 golden file path."""
    assert GOLDEN_V2.exists(), f"Golden v2 not found: {GOLDEN_V2}"
    return GOLDEN_V2


@pytest.fixture(scope="session")
def v2_converter_path() -> Path:
    """Return the v1-to-v2 converter script path."""
    assert V2_CONVERTER.exists(), f"V2 converter not found: {V2_CONVERTER}"
    return V2_CONVERTER


@pytest.fixture()
def run_parser():
    """
    Returns a function:
    (inp: Path|None, out: Path|None) -> (returncode, stdout, stderr)
    """

    def _run(inp: t.Optional[Path] = None, out: t.Optional[Path] = None):
        cmd = [sys.executable, str(PARSER)]
        if inp is not None:
            cmd.append(str(inp))
        if out is not None:
            cmd.append(str(out))
        proc = None
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            return (
                proc.returncode,
                (proc.stdout or ""),
                (proc.stderr or ""),
            )
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed: {e}")
            return (
                e.returncode,
                (e.stdout or ""),
                (e.stderr or ""),
            )

    return _run


@pytest.fixture()
def run_parser_v2():
    """
    Returns a function that runs v1 parser followed by v2 conversion:
    (inp: Path|None, out: Path|None) -> (returncode, stdout, stderr)
    """

    def _run_v2(inp: t.Optional[Path] = None, out: t.Optional[Path] = None):
        if inp is None or out is None:
            return 1, "", "Both input and output paths required for v2 parser"

        # Step 1: Run v1 parser to temporary file
        temp_v1 = out.parent / f"{out.stem}_temp_v1.json"

        cmd_v1 = [sys.executable, str(PARSER), str(inp), str(temp_v1)]
        try:
            proc_v1 = subprocess.run(
                cmd_v1,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            return (
                e.returncode,
                (e.stdout or ""),
                f"""V1 parser failed: {e.stderr or ""}""",
            )

        # Step 2: Convert v1 to v2
        cmd_v2 = [sys.executable, str(V2_CONVERTER), str(temp_v1), str(out)]
        try:
            proc_v2 = subprocess.run(
                cmd_v2,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            # Clean up temp file
            temp_v1.unlink(missing_ok=True)
            err_msg = f"""V2 conversion failed: {e.stderr or ""}"""
            return (
                e.returncode,
                (e.stdout or ""),
                err_msg,
            )

        # Clean up temp file
        temp_v1.unlink(missing_ok=True)

        # Combine outputs
        combined_stdout = f"""V1: {proc_v1.stdout or ""}\nV2: {proc_v2.stdout or ""}"""
        combined_stderr = f"""V1: {proc_v1.stderr or ""}\nV2: {proc_v2.stderr or ""}"""

        return 0, combined_stdout, combined_stderr

    return _run_v2


@pytest.fixture()
def write_text(tmp_path: Path):
    """Fixture to write text files in temp directory."""

    def _write(name: str, content: str) -> Path:
        """Write content to a file and return the path."""
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _write
