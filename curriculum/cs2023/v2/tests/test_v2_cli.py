"""
CLI Tests for Unified Parser v2

This test suite validates the command-line interface functionality of the
unified parser. It tests:
- CLI help functionality
- JSON output generation from text files
- Schema validation integration
- Error handling for invalid inputs
- Proper argument parsing and file I/O operations
"""

import json
import subprocess
import sys
from pathlib import Path


def run_cli(txt_path: Path, out_path: Path, schema_path: Path | None = None):
    """Run the unified parser CLI with correct arguments."""
    # Get the v2 directory (parent of tests)
    v2_dir = Path(__file__).resolve().parents[1]
    cli_path = v2_dir / "unified_parser_v2.py"

    cmd = [
        sys.executable,
        str(cli_path),
        "--txt",
        str(txt_path),
        "--out",
        str(out_path),
    ]
    if schema_path:
        cmd.extend(["--schema", str(schema_path)])

    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(v2_dir),
    )
    return r


def test_help_works():
    """Test that the help command works."""
    # Get the v2 directory (parent of tests)
    v2_dir = Path(__file__).resolve().parents[1]
    cli_path = v2_dir / "unified_parser_v2.py"

    r = subprocess.run(
        [sys.executable, str(cli_path), "--help"],
        capture_output=True,
        check=False,
        text=True,
        cwd=str(v2_dir),
    )
    assert r.returncode == 0
    assert "usage" in (r.stdout or "").lower()


def test_cli_produces_json(tmp_path: Path, sample_txt_paths, schema_path):
    """Test that CLI produces valid JSON output."""
    out = tmp_path / "out.json"
    r = run_cli(sample_txt_paths[0], out, schema_path)
    assert r.returncode == 0, f"CLI failed: {r.stderr}"

    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "schema" in data
    assert "knowledge_area" in data
    assert "sections" in data


def test_bad_input_fails(tmp_path: Path):
    """Test that CLI fails gracefully with bad input."""
    out = tmp_path / "x.json"
    bad_input = Path("does_not_exist.txt")
    r = run_cli(bad_input, out)
    assert r.returncode != 0
    msg = (r.stderr or r.stdout).lower()
    assert "not found" in msg or "no such file" in msg or "error" in msg
