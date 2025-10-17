"""
Test Fixtures and Configuration for Unified Parser v2

This module provides shared fixtures and configuration for all v2 parser tests.
It defines:
- Path configuration for test files and schema
- Sample text file fixtures for testing
- Schema validation fixtures
- Common test data and utilities
- Test environment setup and teardown
"""

import json
from pathlib import Path

import pytest

# Get the cs2023 directory (parent of v2)
CS2023_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = CS2023_DIR / "input"
SCHEMA_PATH = CS2023_DIR / "v2" / "ka_schema_v2_unified.json"


@pytest.fixture(scope="session")
def cs2023_dir() -> Path:
    """Return the cs2023 directory path."""
    return CS2023_DIR


@pytest.fixture(scope="session")
def input_dir() -> Path:
    """Return the input directory path."""
    return INPUT_DIR


@pytest.fixture(scope="session")
def sample_txt_paths():
    """Return paths to sample text files for testing."""
    return [
        INPUT_DIR / "SE.txt",
        INPUT_DIR / "OS_Operating_Systems.txt",
        INPUT_DIR / "SEC_Security.txt",
    ]


@pytest.fixture(scope="session")
def schema():
    """Load and return the JSON schema for validation."""
    pytest.importorskip("jsonschema", reason="jsonschema not installed")
    assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def schema_path() -> Path:
    """Return the path to the schema file."""
    return SCHEMA_PATH
