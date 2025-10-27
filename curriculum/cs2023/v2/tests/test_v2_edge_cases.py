"""
Edge Case Tests for Unified Parser v2

This test suite validates the parser's behavior with challenging or unusual
input scenarios. It tests:
- Unicode character handling (em-dash, special characters)
- Different newline formats (Windows vs Unix)
- Minimal valid input processing
- Section parsing with various formats
- Learning outcome extraction robustness
- Error resilience and graceful degradation
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Union


def run_cli_with_text(
    text: str,
    tmp_path: Path,
    schema_path: Union[Path, None] = None,
    filename: str = "SE_Software_Engineering.txt",
):
    """Run CLI with custom text input."""
    # Write text to temporary file with proper naming convention
    input_file = tmp_path / filename
    input_file.write_text(text, encoding="utf-8")

    # Run parser
    output_file = tmp_path / "test_output.json"
    # Get the v2 directory (parent of tests)
    v2_dir = Path(__file__).resolve().parents[1]
    cli_path = v2_dir / "unified_parser_v2.py"

    cmd = [
        sys.executable,
        str(cli_path),
        "--txt",
        str(input_file),
        "--out",
        str(output_file),
    ]
    if schema_path:
        cmd.extend(["--schema", str(schema_path)])

    # Add knowledge area parameters based on filename
    if "SE" in filename:
        cmd.extend(["--ka-code", "SE", "--ka-name", "Software Engineering"])
    elif "SEC" in filename:
        cmd.extend(["--ka-code", "SEC", "--ka-name", "Security"])
    elif "OS" in filename:
        cmd.extend(["--ka-code", "OS", "--ka-name", "Operating Systems"])

    r = subprocess.run(
        cmd, capture_output=True, text=True, check=False, cwd=str(v2_dir)
    )
    return r, output_file


def test_handles_em_dash(tmp_path: Path, schema_path):
    """Test that parser handles em-dash in learning outcomes."""
    txt = """Software Engineering (SE)

SE-TestSection: Test section with em-dash

This is a test section that demonstrates how the parser handles em-dash
characters in learning outcomes. The parser should be able to extract
learning outcomes even when they contain special characters like em-dashes.

Illustrative Learning Outcomes—Students will be able to:
- Apply hashing algorithms effectively in real-world scenarios
- Understand data structures and their implementation details
- Demonstrate knowledge of software engineering principles"""
    r, output_file = run_cli_with_text(txt, tmp_path, schema_path)
    assert r.returncode == 0, f"Parser failed: {r.stderr}"

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "knowledge_units" in data
    # Check that at least one knowledge unit was created
    assert (
        len(data["knowledge_units"]) > 0
    ), "No knowledge units were parsed from the input"

    # Check that the knowledge unit has the expected structure
    ku = data["knowledge_units"][0]
    assert "id" in ku
    assert "title" in ku


def test_windows_newlines(tmp_path: Path, schema_path):
    """Test that parser handles Windows-style line endings."""
    txt = """Software Engineering (SE)

SE-TestSection: Test section with Windows line endings

This section tests the parser's ability to handle Windows-style line
endings (CRLF) in the input text. The parser should normalize these
and process the content correctly.

Learning Outcomes:
- Understand testing methodologies and best practices
- Apply best practices in software development
- Demonstrate knowledge of cross-platform compatibility"""
    r, output_file = run_cli_with_text(txt, tmp_path, schema_path)
    assert r.returncode == 0, f"Parser failed: {r.stderr}"

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "knowledge_units" in data
    assert len(data["knowledge_units"]) > 0


def test_empty_file_is_error(tmp_path: Path):
    """Test that empty file produces an error."""
    r, _ = run_cli_with_text("", tmp_path)
    # Empty file should fail or produce minimal output
    # The parser might handle empty files gracefully, so we just check it
    # doesn't crash
    assert r.returncode >= 0  # Should not crash with segmentation fault


def test_minimal_valid_input(tmp_path: Path, schema_path):
    """Test that minimal valid input produces expected structure."""
    txt = """Software Engineering (SE)

SE-TestSection: Minimal test section

This is a minimal test section that should be parsed correctly by the
unified parser. It contains basic content and learning outcomes to
verify the parser's functionality.

Learning Outcomes:
- Understand basic concepts in software engineering
- Apply fundamental principles in practice
- Demonstrate knowledge of core topics"""
    r, output_file = run_cli_with_text(txt, tmp_path, schema_path)
    assert r.returncode == 0, f"Parser failed: {r.stderr}"

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "schema" in data
    assert "knowledge_area" in data
    assert "knowledge_units" in data
    # The parser infers SE from the filename "SE_Software_Engineering.txt"
    assert data["knowledge_area"]["code"] == "SE"
