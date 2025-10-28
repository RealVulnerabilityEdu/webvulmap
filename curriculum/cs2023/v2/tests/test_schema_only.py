"""
Schema Validation Tests for Unified Parser v2

This test suite focuses specifically on JSON schema validation functionality.
It tests:
- Output validation against the v2 unified schema
- Required field presence and correct types
- Schema compliance for knowledge areas, sections, and learning outcomes
- Proper metadata structure (schema name, version, timestamps)
- Schema evolution compatibility and validation rules
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Union

import pytest
from jsonschema import validate


def parse_via_cli(
    txt_path: Path, tmp_path: Path, schema_path: Union[Path, None] = None
) -> dict:
    """Parse a text file via CLI and return the JSON result."""
    out = tmp_path / (txt_path.stem + ".json")
    # Get the v2 directory (parent of tests)
    v2_dir = Path(__file__).resolve().parents[1]
    cli_path = v2_dir / "unified_parser_v2.py"

    cmd = [
        sys.executable,
        str(cli_path),
        "--txt",
        str(txt_path),
        "--out",
        str(out),
    ]
    if schema_path:
        cmd.extend(["--schema", str(schema_path)])

    # Add knowledge area parameters based on filename
    if "SE.txt" in str(txt_path):
        cmd.extend(["--ka-code", "SE", "--ka-name", "Software Engineering"])
    elif "SEC_Security.txt" in str(txt_path):
        cmd.extend(["--ka-code", "SEC", "--ka-name", "Security"])
    elif "OS_Operating_Systems.txt" in str(txt_path):
        cmd.extend(["--ka-code", "OS", "--ka-name", "Operating Systems"])

    r = subprocess.run(
        cmd, capture_output=True, text=True, check=False, cwd=str(v2_dir)
    )
    assert r.returncode == 0, f"CLI failed: {r.stderr}"
    return json.loads(out.read_text(encoding="utf-8"))


def test_schema_valid(sample_txt_paths, schema, tmp_path, schema_path):
    """Test that parsed output validates against the schema."""
    for txt_path in sample_txt_paths:
        # Skip if file doesn't exist
        if not txt_path.exists():
            pytest.skip(f"Input file not found: {txt_path}")

        obj = parse_via_cli(txt_path, tmp_path, schema_path)

        # Validate against schema
        try:
            validate(instance=obj, schema=schema)
        except (ValueError, TypeError, KeyError) as e:
            pytest.fail(f"Schema validation failed for {txt_path.name}: {e}")


def test_schema_structure(schema):
    """Test that the schema itself has the expected structure."""
    assert "$schema" in schema
    assert "type" in schema
    assert "properties" in schema
    assert "required" in schema

    # Check required fields
    required_fields = schema["required"]
    expected_required = ["schema", "knowledge_area", "preamble", "knowledge_units"]
    for field in expected_required:
        assert field in required_fields, f"Required field '{field}' missing from schema"


def test_output_has_required_fields(sample_txt_paths, tmp_path, schema_path):
    """Test that parser output contains all required fields."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")

    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    # Check required top-level fields
    assert "schema" in obj
    assert "knowledge_area" in obj
    assert "preamble" in obj
    assert "knowledge_units" in obj

    # Check schema metadata
    schema_obj = obj["schema"]
    assert "name" in schema_obj
    assert "version" in schema_obj
    assert "generated_at" in schema_obj

    # Check knowledge area structure
    ka_obj = obj["knowledge_area"]
    assert "name" in ka_obj
    assert "code" in ka_obj
