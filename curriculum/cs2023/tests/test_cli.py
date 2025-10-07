"""test.cli.py."""

import json


def test_cli_usage_error(run_parser):
    """Running with no args should fail and print usage/help."""
    code, out, err = run_parser()
    msg = out + err
    assert code, "Running parser without args should return non-zero"
    assert "usage" in msg.lower() or "Usage" in msg, "Expected a usage/help message"


def test_cli_writes_json(tmp_path, run_parser, write_text):
    """Test CLI writes valid JSON output."""
    inp = write_text("in.txt", "SE-Design: Header\nSome content")
    out = tmp_path / "out.json"
    code, stdout, stderr = run_parser(inp, out)
    assert not code, f"Parser failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    # Ensure output is valid JSON
    json.loads(out.read_text(encoding="utf-8"))
