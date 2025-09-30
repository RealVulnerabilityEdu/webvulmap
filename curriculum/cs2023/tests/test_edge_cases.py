"""Test edge cases."""

import json


def test_cleaning_and_header_detection(tmp_path, run_parser, write_text):
    """
    Should handle form feeds, hyphen-joins, and detect section header.
    """
    sample = (
        "123\n"
        "Form\fFeed\n"
        "Hyphen-\n"
        "join\n"
        "\n"
        "SE-Design: Header\n"
        "Body.\n"
    )
    inp = write_text("edge.txt", sample)
    out = tmp_path / "out.json"

    code, stdout, stderr = run_parser(inp, out)
    assert code == 0, f"Parser failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, dict)


def test_handles_empty_file_gracefully(tmp_path, run_parser, write_text):
    """
    Should fail with clear message on empty input.
    """
    inp = write_text("empty.txt", "")
    out = tmp_path / "out.json"

    code, stdout, stderr = run_parser(inp, out)
    assert code != 0, "Empty input should not succeed"
    assert "empty" in (stdout + stderr).lower()


def test_invalid_header_format(tmp_path, run_parser, write_text):
    """
    Should fail with message if no valid section header is present.
    """
    inp = write_text("bad_header.txt", "Random text without expected header")
    out = tmp_path / "out.json"

    code, stdout, stderr = run_parser(inp, out)
    assert code != 0
    assert "header" in (stdout + stderr).lower()
