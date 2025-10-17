# Unified Parser v2

A comprehensive parser for CS2023 curriculum knowledge areas that converts text
files into structured JSON format following the v2 unified schema.

## Overview

The Unified Parser v2 is designed to extract structured data from CS2023
curriculum text files, including:

- Knowledge area metadata
- Section organization
- Learning outcomes with cognitive levels
- Topics and cross-references
- Source location tracking

## Features

- **Smart Section Parsing**: Automatically identifies and parses sections from
  text
- **Learning Outcome Extraction**: Extracts learning outcomes with cognitive level
  classification
- **Schema Validation**: Validates output against the v2 unified schema
- **Robust Error Handling**: Gracefully handles edge cases and malformed input
- **CLI Interface**: Easy-to-use command-line interface
- **Comprehensive Testing**: Full test suite with edge cases and invariants

## File Structure

```text
v2/
├── README.md                          # This file
├── unified_parser_v2.py              # Main parser script
├── ka_schema_v2_unified.json         # JSON schema for validation
└── tests/                            # Test suite
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

````bash
# Basic usage
python unified_parser_v2.py --txt input_file.txt --out output.json


### Arguments

- `--txt`: Input text file path (required)
- `--out`: Output JSON file path (required)
- `--schema`: JSON schema file for validation (optional)

### Example

```bash
# Parse SE.txt and save to v2_output.json
python unified_parser_v2.py \
  --txt ../input/SE.txt \
  --out ../input/v2_output.json \
  --schema ka_schema_v2_unified.json
````
