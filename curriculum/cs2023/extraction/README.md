# Extraction to JSON — Software Engineering (SE) knowledge area

This directory documents the extraction-to-JSON workflow for the
Software Engineering (SE) knowledge area

Goal

- Produce a complete v2 JSON representation for SE (schema: `curriculum/cs2023/ka.schema.v2.json`).
- The canonical output file is `curriculum/SE.golden.v2.json` (used for tests and
  regression checks).

Inputs

- Source knowledge area text files are read from: `curriculum/cs2023/input/*.txt`.
  - Each `.txt` file should contain the KA content for one knowledge area.
  - The parser extracts: title, summary (first paragraph), learning outcomes (bullet
    points), and other fields as the schema requires.

Primary script

- `curriculum/cs2023/direct_parse_v2.py` — a direct parser that reads `.txt` files
  and writes `SE.golden.v2.json`.

Dependencies

- Python 3.8+
- Recommended: create a virtual environment

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt   # if present
  python -m pip install jsonschema
  ```
