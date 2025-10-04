"""Test schema."""

import json

from jsonschema import Draft202012Validator, validate


def test_output_matches_schema(tmp_path, run_parser, write_text, schema_path):
    """Parser output should satisfy the JSON Schema."""
    inp = write_text("se_sample.txt", "SE-Design: Header\nBody line 1\nBody line 2")
    out = tmp_path / "out.json"

    code, stdout, stderr = run_parser(inp, out)
    assert code == 0, f"Parser failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

    data = json.loads(out.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    validate(instance=data, schema=schema)


def test_output_matches_golden(tmp_path, run_parser, golden_path, cs2023_dir):
    """Real SE.txt should produce output identical to the golden."""
    se_txt = cs2023_dir / "input" / "SE.txt"
    assert se_txt.exists(), f"Missing input file: {se_txt}"

    out = tmp_path / "se.actual.json"
    code, stdout, stderr = run_parser(se_txt, out)
    assert code == 0, f"Parser failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

    def norm(o):
        if isinstance(o, dict):
            return {k: norm(v) for k, v in sorted(o.items())}
        if isinstance(o, list):
            return [norm(x) for x in o]
        return o

    actual = norm(json.loads(out.read_text(encoding="utf-8")))
    expected = norm(json.loads(golden_path.read_text(encoding="utf-8")))
    assert (
        actual == expected
    ), "Golden mismatch: update the golden only \
        if the schema/format intentionally changed."
