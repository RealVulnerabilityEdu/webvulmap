"""
Invariant Tests for Unified Parser v2.

This suite validates properties that should always hold regardless of input variations.
It tests:
- Required fields are present and non-empty
- Learning outcomes have valid cognitive levels and text
- ID/slug uniqueness within sections
- Reasonable learning outcome extraction counts
- Topic titles are non-empty when present
- Deterministic output behavior (same input → same output)
- Data consistency and structural integrity
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Union

import pytest

COG_LEVELS = {"Explain", "Apply", "Evaluate", "Develop"}


def parse_via_cli(
    txt_path: Path,
    tmp_path: Path,
    schema_path: Union[Path, None] = None,
) -> dict:
    """Parse a text file via CLI and return the JSON result."""
    out = tmp_path / (txt_path.stem + ".json")
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
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(v2_dir),
    )
    assert r.returncode == 0, f"CLI failed: {r.stderr}"
    return json.loads(out.read_text(encoding="utf-8"))


def _collect_learning_outcomes(obj: dict) -> list[dict]:
    """Return the list of learning outcomes from the unified structure."""
    knowledge_units = obj.get("knowledge_units", []) or []
    all_los: list[dict] = []

    for ku in knowledge_units:
        # Check for learning outcomes in each category
        for category in ["cs_core", "ka_core", "non_core", "general"]:
            los = ku.get("learning_outcomes", {}).get(category, [])
            if isinstance(los, list):
                all_los.extend(los)

    return all_los


def _slug_ok(s: str) -> bool:
    """kebab-case: lowercase letters/digits with single hyphens; no edge hyphens."""
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s or ""))


@pytest.mark.parametrize("which", ["first"])
def test_required_fields_nonempty(  # pylint: disable=unused-argument
    sample_txt_paths,
    tmp_path,
    schema_path,
    which,
) -> None:
    """Essential fields are present and non-empty."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")
    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    # Top-level
    assert obj.get("schema"), "missing schema metadata"
    assert obj.get("knowledge_area"), "missing knowledge_area"
    assert obj.get("knowledge_units"), "missing knowledge_units"

    # Schema metadata
    scm = obj["schema"]
    assert scm.get("name") and scm.get("version"), "schema name/version required"

    # KA
    ka = obj["knowledge_area"]
    assert ka.get("name") and ka.get("code"), "KA name/code required"
    if "slug" in ka:
        slug_value = ka["slug"]
        assert _slug_ok(slug_value), f"Invalid KA slug: {slug_value}"


def test_learning_outcomes_have_text_and_level(
    sample_txt_paths,
    tmp_path,
    schema_path,
) -> None:
    """Each LO has text and a valid cognitive_level."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")
    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    los = _collect_learning_outcomes(obj)
    assert isinstance(los, list) and len(los) > 0, "No learning outcomes parsed"

    for i, lo in enumerate(los):
        assert (lo.get("text") or "").strip(), f"LO[{i}] missing text"
        lvl = lo.get("cognitive_level")
        assert lvl in COG_LEVELS, f"LO[{i}] invalid cognitive_level: {lvl}"
        if "id" in lo:
            lo_id = lo["id"]
            assert _slug_ok(lo_id), f"LO[{i}] invalid id slug: {lo_id}"
        if "slug" in lo:
            lo_slug = lo["slug"]
            assert _slug_ok(lo_slug), f"LO[{i}] invalid slug: {lo_slug}"


def test_ids_unique_within_section(
    sample_txt_paths,
    tmp_path,
    schema_path,
) -> None:
    """Any present IDs/slugs for LOs are unique within each knowledge unit."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")
    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    knowledge_units = obj.get("knowledge_units", []) or []
    for ku in knowledge_units:
        all_los = []
        # Collect all learning outcomes from all categories
        for category in ["cs_core", "ka_core", "non_core", "general"]:
            los = ku.get("learning_outcomes", {}).get(category, [])
            if isinstance(los, list):
                all_los.extend(los)

        ids = [lo.get("id") for lo in all_los if lo.get("id")]
        slugs = [lo.get("slug") for lo in all_los if lo.get("slug")]

        ku_id = ku.get("id", "unknown")
        assert len(ids) == len(set(ids)), f"Duplicate LO ids in knowledge unit {ku_id}"
        assert len(slugs) == len(
            set(slugs)
        ), f"Duplicate LO slugs in knowledge unit {ku_id}"


def test_learning_outcomes_extracted(
    sample_txt_paths,
    tmp_path,
    schema_path,
) -> None:
    """Parser extracts a reasonable number of learning outcomes from the input."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")

    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)
    los = _collect_learning_outcomes(obj)
    n_los = len(los)

    assert n_los > 0, "Parser produced zero LOs"
    assert n_los >= 10, f"Too few learning outcomes extracted: {n_los}"
    assert n_los <= 200, f"Too many learning outcomes extracted: {n_los}"


def test_topic_titles_nonempty(
    sample_txt_paths,
    tmp_path,
    schema_path,
) -> None:
    """If knowledge units exist, every topic has a non-empty name."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")
    obj = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    knowledge_units = obj.get("knowledge_units", []) or []
    for ku in knowledge_units:
        # Check topics in each category
        for category in ["cs_core", "ka_core", "non_core"]:
            topics = ku.get("topics", {}).get(category, [])
            for i, topic in enumerate(topics):
                if isinstance(topic, dict):
                    assert (
                        topic.get("name") or ""
                    ).strip(), f"Topic[{i}] in {category} missing name"
                else:
                    assert (
                        str(topic) or ""
                    ).strip(), f"Topic[{i}] in {category} missing name"


def test_deterministic_output(
    sample_txt_paths,
    tmp_path,
    schema_path,
) -> None:
    """Same input → identical normalized JSON (ignoring cosmetic whitespace)."""
    if not sample_txt_paths or not sample_txt_paths[0].exists():
        pytest.skip("No valid input files available")

    obj1 = parse_via_cli(sample_txt_paths[0], tmp_path, schema_path)

    txt2 = sample_txt_paths[0].read_text(encoding="utf-8") + "\n"
    tmp_in = tmp_path / sample_txt_paths[0].name
    tmp_in.write_text(txt2, encoding="utf-8")
    obj2 = parse_via_cli(tmp_in, tmp_path, schema_path)

    def normalize_for_comparison(d: dict) -> str:
        d_copy = json.loads(json.dumps(d))
        if "schema" in d_copy:
            d_copy["schema"]["generated_at"] = "NORMALIZED"
            d_copy["schema"]["source"] = "NORMALIZED"

        # Normalize any file paths in the data
        def normalize_paths(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and ("/" in value or "\\" in value):
                        # Replace file paths with normalized version
                        obj[key] = re.sub(r'/[^"]*\.txt', "/NORMALIZED.txt", value)
                    else:
                        normalize_paths(value)
            elif isinstance(obj, list):
                for item in obj:
                    normalize_paths(item)

        normalize_paths(d_copy)
        return json.dumps(
            d_copy,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    norm1 = normalize_for_comparison(obj1)
    norm2 = normalize_for_comparison(obj2)
    assert norm1 == norm2, "Output changed with harmless whitespace"
