# Unified Parser v2

A comprehensive parser for CS2023 curriculum knowledge areas that converts text
files into structured JSON format following the v2 unified schema.

## Overview

The Unified Parser v2 is designed to extract structured data from CS2023
curriculum text files, including:

- Knowledge area metadata (name, code)
- Preamble information (description, changes since CS2013, overview)
- Knowledge units with topics and learning outcomes
- Learning outcomes with cognitive levels (Explain, Apply, Evaluate, Develop)
- Professional dispositions
- Mathematics requirements
- Course packaging suggestions
- Committee information
- Cross-references and source tracking

## Features

- **Knowledge Unit Parsing**: Extracts knowledge units with topics organized by category
  (CS Core, KA Core, Non-Core)
- **Learning Outcome Extraction**: Extracts learning outcomes with cognitive level
  classification and categorization
- **Preamble Processing**: Parses description, changes since CS2013, and structured
  overview sections
- **Additional Sections**: Extracts professional dispositions, mathematics requirements,
  course packaging, and committee info
- **Schema Validation**: Validates output against the v2 unified schema
- **Robust Error Handling**: Gracefully handles edge cases and malformed input
- **CLI Interface**: Easy-to-use command-line interface with knowledge area detection
- **Comprehensive Testing**: Full test suite with edge cases and invariants (16 tests)

## File Structure

```text
v2/
├── README.md                          # This file
├── unified_parser_v2.py              # Main parser script (858 lines)
├── ka_schema_v2_unified.json         # JSON schema for validation (320 lines)
└── tests/                            # Test suite (16 tests)
    ├── conftest.py                   # Test fixtures and configuration
    ├── test_invariants.py            # Invariant property tests
    ├── test_schema_only.py           # Schema validation tests
    ├── test_v2_cli.py               # CLI functionality tests
    └── test_v2_edge_cases.py        # Edge case and robustness tests
```

## Installation

Ensure you have Python 3.11+ and required dependencies:

```bash
# Install dependencies
pip install -r ../requirements.txt

# Or install specific packages
pip install jsonschema pytest
```

## Usage

### Command Line Interface

```bash
# Basic usage
python unified_parser_v2.py --txt input_file.txt --out output.json

# With knowledge area specification
python unified_parser_v2.py --txt input_file.txt --out output.json \
  --ka-code "SE" --ka-name "Software Engineering"

# With schema validation
python unified_parser_v2.py --txt input_file.txt --out output.json \
  --schema ka_schema_v2_unified.json
```

### Arguments

- `--txt`: Input text file path (required)
- `--out`: Output JSON file path (required)
- `--ka-code`: Knowledge area code (e.g., SE, SEC) (optional, auto-detected from
  filename)
- `--ka-name`: Knowledge area name (e.g., "Software Engineering") (optional,
  auto-detected from filename)
- `--schema`: JSON schema file for validation (optional)
- `--no-provenance`: Exclude provenance metadata (optional)

### Examples

```bash
# Parse Software Engineering curriculum
python unified_parser_v2.py \
  --txt ../input/SE.txt \
  --out ../input/SE.final.json \
  --ka-code "SE" \
  --ka-name "Software Engineering" \
  --schema ka_schema_v2_unified.json

# Parse Security curriculum
python unified_parser_v2.py \
  --txt ../input/SEC_Security.txt \
  --out ../input/SEC_Security.final.json \
  --ka-code "SEC" \
  --ka-name "Security" \
  --schema ka_schema_v2_unified.json
```

## Output Structure

The parser generates JSON files with the following structure:

```json
{
  "schema": {
    "name": "ka.schema.v2",
    "version": "2.0",
    "generated_at": "2025-10-26T01:17:00.000000Z",
    "source": "input/SE.txt",
    "schema_ref": "schema/ka.schema.v2.json"
  },
  "knowledge_area": {
    "name": "Software Engineering",
    "code": "SE"
  },
  "preamble": {
    "description": "...",
    "changes_since_cs2013": "...",
    "overview": [...]
  },
  "core_hours": [],
  "knowledge_units": [...],
  "professional_dispositions": [...],
  "mathematics_requirements": {...},
  "course_packaging_suggestions": {...},
  "committee": {...}
}
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_invariants.py
```

## Code Quality

The parser follows strict code quality standards:

- **Black**: Code formatting (88 character line limit)
- **isort**: Import sorting
- **flake8**: Style guide enforcement
- **mypy**: Type checking
- **pylint**: Code quality analysis

All linting checks pass and the code maintains a high quality rating.
