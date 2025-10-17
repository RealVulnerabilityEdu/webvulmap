#!/usr/bin/env python3
"""
CS2023 Text to JSON Parser v2

Parses CS2023 curriculum text files into v2 JSON schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# --- Configuration ---
TOOL_NAME = "parse_txt_to_json_v2.py"
SCHEMA_VERSION = "2.0"

# ------------------ Helpers ------------------


def slug(s: str) -> str:
    """Create a URL/ID-safe slug."""
    s = re.sub(r"[^a-z0-9]+", "-", s.strip().lower())
    return s.strip("-")


def infer_ka_from_filename(p: Path) -> Tuple[str, str]:
    """Infer KA code and name from filename.

    Example: OS_Operating_Systems.txt -> OS, Operating Systems
    """
    m = re.match(r"^([A-Z]{2,5})[ _-]+(.+)$", p.stem)
    if m:
        code, raw = m.group(1), m.group(2)
        name = re.sub(r"[_-]+", " ", raw).strip().title()
        return code, name
    return p.stem.upper(), p.stem.replace("_", " ").title()


def _norm_topic_id(unused_topic_string: str, index: int = 1) -> str:
    """Generate topic ID following schema pattern: topic-N."""
    return f"topic-{index}"


def guess_topics_for(title: str, body: str = "") -> List[Dict[str, str]]:
    """Heuristically guess cross-cutting topics (e.g., 'security')."""
    t = (title + " " + body[:400]).lower()
    out: List[Dict[str, str]] = []

    def add(i: str, n: str, idx: int) -> None:
        topic_id = _norm_topic_id(i, idx)
        if not any(d["id"] == topic_id for d in out):
            out.append({"id": topic_id, "name": n})

    idx = 1
    if "security" in t or "protection" in t:
        add("sec", "security", idx)
        idx += 1
    if "concurrency" in t or "process" in t or "thread" in t:
        add("concurrency", "concurrency", idx)
        idx += 1
    if "i/o" in t or "device" in t:
        add("io-devices", "device & I/O", idx)
        idx += 1
    return out


def extract_preamble(text: str) -> str:
    """Extract the document's preamble/description."""
    m = re.search(
        r"\bPreamble\b\s*(.+?)\n\s*(?:Changes since|Changes from|\f)",
        text,
        flags=re.S | re.I,
    )
    if m:
        return re.sub(r"\s+\n", "\n", m.group(1)).strip()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "\n\n".join(paragraphs[:2])


def _summarize(body: str) -> str:
    """Extract the first paragraph as a summary."""
    first = re.split(r"\n\s*\n", body.strip(), maxsplit=1)[0]
    return re.sub(r"\s+", " ", first).strip()


def _preclean(text: str) -> str:
    """Clean input text (remove form feeds, page numbers)."""
    t = text.replace("\f", "").replace("\r", "")
    t = "\n".join(
        line for line in t.splitlines() if not re.fullmatch(r"\s*\d{1,4}\s*", line)
    )
    return t


# ------------------ Block Extraction ------------------

# Bullet pattern: (indent) (bullet) (text)
_BULLET_WITH_INDENT = re.compile(
    r"""^(?P<indent>[ \t]*)
    (?: [-*•·]\s+ | [0-9]+\.\s+ | [a-z][\.\)]\s+ | [ivxlcdm]+\.\s+ )
    (?P<text>.+?)\s*$""",
    re.I | re.M | re.X,
)

# Subheadings to detect blocks
_SUBHEAD_PATTERNS = {
    "ilos": re.compile(
        (
            r"^\s*(?:Illustrative\s+)?(?:Learning\s+Outcomes?|LOs|Outcomes?)"
            r"\s*:?\s*$"
        ),
        re.I | re.M,
    ),
}


def _find_block_ranges(
    body: str, anchors: List[Tuple[str, re.Pattern[str]]]
) -> Dict[str, Tuple[int, int]]:
    """Find start/end indices for major content blocks."""
    hits = sorted(
        [(m.start(), m.end(), key) for key, pat in anchors for m in pat.finditer(body)],
        key=lambda x: x[0],
    )
    ranges: Dict[str, Tuple[int, int]] = {}
    for i, (unused_match_start, match_end, key) in enumerate(hits):
        start = match_end
        end = hits[i + 1][0] if (i + 1) < len(hits) else len(body)
        if key not in ranges:
            ranges[key] = (start, end)
    return ranges


def _collect_bullet_lines(block_text: str) -> List[Tuple[int, str]]:
    """
    Collect bullet points from a text block, joining wrapped lines.

    Returns: list of (indent_level, text).
    """
    lines = block_text.splitlines()
    items: List[Tuple[int, str]] = []
    cur_lvl: Optional[int] = None
    cur_text: Optional[str] = None

    def flush() -> None:
        nonlocal cur_lvl, cur_text
        if cur_text is not None:
            items.append((cur_lvl or 0, cur_text.strip()))
        cur_lvl, cur_text = None, None

    for raw in lines:
        line = raw.rstrip()
        m = _BULLET_WITH_INDENT.match(line)
        if m:
            flush()
            cur_lvl = len(m.group("indent").replace("\t", "  ")) // 2
            cur_text = m.group("text").strip()
        elif cur_text is not None:
            if line.strip():
                cur_text += " " + line.strip()

    flush()
    return items


# ------------------ Learning Outcomes (LO) Fix ------------------

_BLOOMS: Dict[str, List[str]] = {
    "Remember": [
        "list",
        "define",
        "identify",
        "recall",
        "state",
        "name",
        "label",
        "recognize",
    ],
    "Understand": [
        "explain",
        "describe",
        "summarize",
        "discuss",
        "interpret",
        "understand",
        "convert",
    ],
    "Apply": ["apply", "use", "implement", "execute", "demonstrate", "solve"],
    "Analyze": ["analyze", "analyse", "differentiate", "compare", "contrast"],
    "Evaluate": [
        "evaluate",
        "justify",
        "critique",
        "assess",
        "argue",
        "recommend",
    ],
    "Create": [
        "create",
        "design",
        "compose",
        "formulate",
        "construct",
        "develop",
    ],
}
_BLOOMS_RE = re.compile(r"^\s*(?:\([^\)]+\)\s*)*\s*(?P<verb>[A-Za-z\-]+)\b", re.I)


def _infer_cognitive_level(lo_text: str) -> str:
    """Infer Bloom's Taxonomy level from the LO's starting verb."""
    m = _BLOOMS_RE.match(lo_text)
    if m:
        v = m.group("verb").lower()
        v_stem = re.sub(r"(ing|ed|es|s)$", "", v)
        for level, verbs in _BLOOMS.items():
            if v in verbs or v_stem in verbs:
                return level
    return "Understand"


def _extract_learning_outcomes(block_text: str) -> List[Dict[str, Any]]:
    """
    Extract LOs using a direct iteration over collected lines.

    The schema expects a flat list.
    """
    pairs = _collect_bullet_lines(block_text)
    los: List[Dict[str, Any]] = []
    for i, (unused_level, text) in enumerate(pairs, start=1):
        lo_id = f"lo-{i}"
        los.append(
            {
                "id": lo_id,
                "text": text,
                "cognitive_level": _infer_cognitive_level(text),
            }
        )
    return los


# ------------------ Cross-References ------------------

_SEE_ALSO_LINE = re.compile(r"(?i)\bSee\s+also:\s*(.+)$", re.M)
_CWE_PAT = re.compile(r"\bCWE-\d+\b", re.I)
_CVE_PAT = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.I)


def _normalize_ref_token(tok: str) -> str:
    """Clean up cross-reference tokens."""
    t = tok.strip().strip("'\"")
    t = re.sub(r"^[(\[].*?(\s*)\s*|\s*.*?[\)\]\.;,:]+$", r"\1", t).strip()
    return re.sub(r"\s+", " ", t).strip()


def _classify_crossref(tok: str) -> str:
    """Classify a cross-reference target per schema enum."""
    if _CVE_PAT.fullmatch(tok):
        return "knowledge_area"
    if _CWE_PAT.fullmatch(tok):
        return "knowledge_area"
    if re.fullmatch(r"[A-Z]{2,5}(?:-[A-Za-z0-9]+)?", tok):
        return "knowledge_area"
    return "section"


def _extract_crossrefs(body: str) -> List[Dict[str, str]]:
    """Extract all 'See also:' references."""
    seen: set[str] = set()
    out: List[Dict[str, str]] = []
    for m in _SEE_ALSO_LINE.finditer(body):
        for part in re.split(r"[;,]", m.group(1)):
            tok = _normalize_ref_token(part)
            if not tok or tok.lower() in seen:
                continue
            seen.add(tok.lower())
            out.append({"type": _classify_crossref(tok), "reference": tok})
    return out


# ------------------ Parser Dispatcher ------------------


def _parse_internal_blocks(
    section_body: str, unused_bullet_id_prefix: str
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, str]]]:
    """Parse section body for LOs, Crossrefs, and generate Markdown."""
    anchors = [("ilos", _SUBHEAD_PATTERNS["ilos"])]
    ranges = _find_block_ranges(section_body, anchors)

    los: List[Dict[str, Any]] = []
    if "ilos" in ranges:
        s, e = ranges["ilos"]
        los = _extract_learning_outcomes(section_body[s:e])

    xrefs = _extract_crossrefs(section_body)
    md_content = _to_markdown_from_plain(section_body)

    return md_content, los, xrefs


# ------------------ Document Builders ------------------


def _to_markdown_from_plain(text: str) -> str:
    """Minimal conversion from plain text to Markdown."""
    if not text.strip():
        return "# (empty)\n"
    lines = [ln.strip() for ln in text.splitlines()]
    md = "\n".join(lines).strip()
    md = re.sub(r"\n\s*\n", "\n\n", md)
    md = re.sub(r"([^\n])\n([0-9]+\.|\-|\*|[a-z]\.)", r"\1\n\n\2", md)
    return md if md else "# (empty)\n"


def _hash_sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def _extract_section_heading_and_body(
    match: re.Match[str], matches: List[re.Match[str]], i: int, text: str
) -> Tuple[str, str]:
    """Extract heading and body text from a match."""
    heading = match.group(1).strip()
    start = match.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    body = text[start:end].strip()
    return heading, body


def _build_section_metadata(heading: str, ka_code: str, i: int) -> Tuple[str, str]:
    """Build section ID and display title from heading."""
    left, right = heading.split(": ", 1) if ": " in heading else (heading, "")
    sec_id = slug(left)
    # Ensure ID follows schema pattern: ka-sec-number
    if not re.match(r"^[a-z]+-[a-z]+-\d+$", sec_id):
        sec_id = f"{ka_code.lower()}-sec-{i + 1}"

    # Build display title - keep the original format but clean up duplicates
    if right:
        # If we have a subtitle after colon, use it as the main title
        # Keep the KA prefix but avoid duplication
        if left.endswith(right):
            # If "SE-Teamwork: Teamwork", just use "SE-Teamwork"
            display_title = left
        else:
            # If different subtitle, use full format
            display_title = f"{left}: {right}"
    else:
        # If no subtitle, just clean up the main part
        display_title = left.replace("-", " ")

    return sec_id, display_title


def _create_section_object(
    section_data: Dict[str, Any], *, ka_code: str, i: int
) -> Dict[str, Any]:
    """Create a section object with all required fields."""
    return {
        "id": section_data["sec_id"],
        "title": section_data["display_title"],
        "order": i + 1,
        "summary": section_data["summary"],
        "topics": section_data["topics"],
        "learning_outcomes": section_data["los"],
        "bullets": [],
        "crossrefs": section_data["xrefs"],
        "qa_flags": {},
        "source_loc": {
            "file": f"{ka_code}_SAMPLE_v1.json",
            "section": i + 1,
        },
        "subsections": [],
    }


def _add_provenance_if_needed(
    section_obj: Dict[str, Any],
    include_provenance: bool,
    md: str,
    tool_name: str,
    commit_sha: Optional[str],
) -> None:
    """Add provenance info to section object if needed."""
    if include_provenance:
        prov: Dict[str, Any] = {
            "content_hash": _hash_sha256(md),
            "tool": tool_name,
        }
        if commit_sha:
            prov["commit_sha"] = commit_sha
        section_obj["provenance"] = prov


def _deduplicate_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate sections by ID."""
    seen: set[str] = set()
    uniq_sections: List[Dict[str, Any]] = []
    for s in sections:
        if s["id"] not in seen:
            seen.add(s["id"])
            uniq_sections.append(s)
    return uniq_sections


def _process_single_section(
    section_context: Dict[str, Any], *, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Process a single section match into a section object."""
    match = section_context["match"]
    matches = section_context["matches"]
    i = section_context["i"]
    text = section_context["text"]
    ka_code = section_context["ka_code"]

    heading, body = _extract_section_heading_and_body(match, matches, i, text)
    sec_id, display_title = _build_section_metadata(heading, ka_code, i)
    md, los, xrefs = _parse_internal_blocks(body, sec_id)
    topics = guess_topics_for(display_title, body)

    if not topics and not los:
        topics = [{"id": _norm_topic_id(display_title, 1), "name": display_title}]

    return _create_and_provenance_section(
        {
            "sec_id": sec_id,
            "display_title": display_title,
            "body": body,
            "topics": topics,
            "los": los,
            "xrefs": xrefs,
            "md": md,
            "config": config,
            "ka_code": ka_code,
            "i": i,
        }
    )


def _create_and_provenance_section(section_info: Dict[str, Any]) -> Dict[str, Any]:
    """Create section object and add provenance."""
    section_data = {
        "sec_id": section_info["sec_id"],
        "display_title": section_info["display_title"],
        "summary": _summarize(section_info["body"]),
        "topics": section_info["topics"],
        "los": section_info["los"],
        "xrefs": section_info["xrefs"],
    }
    section_obj = _create_section_object(
        section_data, ka_code=section_info["ka_code"], i=section_info["i"]
    )
    _add_provenance_if_needed(
        section_obj=section_obj,
        include_provenance=section_info["config"]["include_provenance"],
        md=section_info["md"],
        tool_name=section_info["config"]["tool_name"],
        commit_sha=section_info["config"]["commit_sha"],
    )
    return section_obj


def build_section_objects(
    text: str,
    ka_code: str,
    *,
    include_provenance: bool,
    tool_name: str,
    commit_sha: Optional[str],
) -> List[Dict[str, Any]]:
    """Parse the text for all sections and build section objects."""
    pat = re.compile(
        rf"^({ka_code}[/-][A-Za-z0-9\-]+(?:[/-][A-Za-z0-9\-]+)*" rf"(?::\s*[^\n]+)?)",
        flags=re.M,
    )

    matches = list(pat.finditer(text))
    sections: List[Dict[str, Any]] = []

    config = {
        "include_provenance": include_provenance,
        "tool_name": tool_name,
        "commit_sha": commit_sha,
    }

    for i, m in enumerate(matches):
        section_context = {
            "match": m,
            "matches": matches,
            "i": i,
            "text": text,
            "ka_code": ka_code,
        }
        section_obj = _process_single_section(section_context, config=config)
        sections.append(section_obj)

    return _deduplicate_sections(sections)


def build_document(
    text: str,
    ka_code: str,
    ka_name: str,
    *,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble the final JSON document."""
    if config is None:
        config = {
            "schema_version": SCHEMA_VERSION,
            "include_provenance": True,
            "tool_name": TOOL_NAME,
            "commit_sha": None,
        }

    sections = build_section_objects(
        text,
        ka_code=ka_code,
        include_provenance=config["include_provenance"],
        tool_name=config["tool_name"],
        commit_sha=config["commit_sha"],
    )
    return {
        "schema": {
            "name": "Knowledge Area/Skill Area Unified Schema v2",
            "version": config["schema_version"],
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "source": (f"curriculum/cs2023/{ka_code}_SAMPLE_v2.json"),
        },
        "knowledge_area": {"name": ka_name, "code": ka_code},
        "description": extract_preamble(text),
        "sections": sections,
    }


# ------------------ CLI ------------------


def main() -> None:
    """Main CLI entry point for the CS2023 parser."""
    ap = argparse.ArgumentParser(description="Parse CS2023 KA plain-text into v2 JSON.")
    ap.add_argument("--txt", required=True, help="Path to input KA text")
    ap.add_argument("--out", required=True, help="Path to output JSON")
    ap.add_argument("--ka_code", help="Override KA code (e.g., SE)")
    ap.add_argument("--ka_name", help="Override KA name (e.g., SE name)")
    ap.add_argument(
        "--schema",
        help="Path to ka.schema.v2.json for optional validation",
    )
    ap.add_argument(
        "--no-provenance",
        action="store_true",
        help="Do not include provenance in sections",
    )
    ap.add_argument(
        "--commit-sha",
        help="Optional git commit SHA for provenance",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit(1) if validation fails",
    )
    args = ap.parse_args()

    txt_path = Path(args.txt)
    out_path = Path(args.out)

    if not txt_path.exists():
        print(f"ERROR: Input text not found: {txt_path}", file=sys.stderr)
        sys.exit(2)

    ka_code, ka_name = args.ka_code, args.ka_name
    if not ka_code or not ka_name:
        ka_code, ka_name = infer_ka_from_filename(txt_path)

    raw = txt_path.read_text(encoding="utf-8", errors="ignore")
    text = _preclean(raw)

    cfg = {
        "schema_version": SCHEMA_VERSION,
        "include_provenance": not args.no_provenance,
        "tool_name": TOOL_NAME,
        "commit_sha": args.commit_sha,
    }
    doc = build_document(text, ka_code=ka_code, ka_name=ka_name, config=cfg)

    if args.schema:
        if not HAS_JSONSCHEMA:
            print(
                "WARNING: jsonschema not installed; skipping validation.",
                file=sys.stderr,
            )
        else:
            try:
                schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
                jsonschema.validate(instance=doc, schema=schema)
                print("Schema validation passed.")
            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                print(f"Schema validation failed: {e}", file=sys.stderr)
                if args.strict:
                    sys.exit(1)

    out_path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} (KA: {ka_code} — {ka_name})")


if __name__ == "__main__":
    main()
