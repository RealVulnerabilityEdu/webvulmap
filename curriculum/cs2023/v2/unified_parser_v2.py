#!/usr/bin/env python3
"""
CS2023 Curriculum Text Parser

Parses curriculum text files into structured JSON format according to CS2023
schema.
Extracts knowledge areas, learning outcomes, topics, and metadata from text
documents.
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
except ImportError:
    jsonschema = None

BASE_DIR = Path(__file__).resolve().parent


def _load_verb_dictionary(path: Path) -> Dict[str, List[str]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            # normalize keys -> lists of lowercase verbs
            return {k: [v.lower() for v in vals] for k, vals in data.items()}
    except (json.JSONDecodeError, KeyError, TypeError, OSError):
        return {}


VERB_DICTIONARIES = [
    ("cs2023", BASE_DIR / "dictionaries" / "cs2023_verbs.json"),
    ("blooms", BASE_DIR / "dictionaries" / "blooms_verbs.json"),
    ("custom", BASE_DIR / "dictionaries" / "custom_verbs.json"),
]

# Load all dictionaries at startup
LO_DICTIONARIES = [
    (name, _load_verb_dictionary(path)) for name, path in VERB_DICTIONARIES
]


TOOL_NAME = "unified_parser_v2.py"
SCHEMA_VERSION = "2.0"


def slug(s: str) -> str:
    """Convert string to URL-friendly slug."""
    return re.sub(r"[^a-z0-9]+", "-", s.strip().lower()).strip("-")


def sha256(s: str) -> str:
    """Compute SHA256 hash of string."""
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()


def file_sha256(path: Path) -> Optional[str]:
    """Compute SHA256 hash of file."""
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None


def preclean(text: str) -> str:
    """Clean text by removing form feeds, carriage returns, and page numbers.

    Page numbers are identified as lines containing only digits (3+ digits are
    definitely page numbers; 1-2 digits are removed as they're likely artifacts).
    Consolidates page number removal to avoid duplication with normalize_glitches().
    """
    t = text.replace("\f", "").replace("\r", "")
    # Remove lines that are only digits (page numbers)
    # 3+ digits are definitely page numbers; 1-2 digits are also removed
    # as they're typically artifacts since core hours parsing happens before preclean()
    return "\n".join(
        line for line in t.splitlines() if not re.fullmatch(r"\s*\d+\s*", line)
    )


def normalize_glitches(text: str) -> str:
    """Normalize common PDF-to-text conversion artifacts and fix typos."""
    repl = [
        (r"\bCore\s+Hourse\b", "Core Hours"),
        (r"\bCore\s+Hourse\s*\.", "Core Hours"),
        (r"\bKnowledges?\s*Units\b", "Knowledge Units"),
        (r"\bKA-?\s*Core\b", "KA Core"),
        (r"\bCS-?\s*Core\b", "CS Core"),
        (r"\bKA-Core:\b", "KA Core:"),
        (r"\bCS-Core:\b", "CS Core:"),
        (r"Non[- ]?core", "Non-Core"),
        (
            r"Illustrative\s+Learning\s+Outcome[s]?\s*:",
            "Illustrative Learning Outcomes:",
        ),
        (
            r"Illustrative\s+Learning\s+Outcome[s]?",
            "Illustrative Learning Outcomes",
        ),
        (r"\bSEC\s*\(\s*Security\s*\)", "Security (SEC)"),
        (r"[ \t]+$", ""),
    ]
    for pat, rep in repl:
        text = re.sub(pat, rep, text, flags=re.I | re.M)

    lines = text.splitlines()
    new_lines: List[str] = []
    buf: List[str] = []

    def flush_buf():
        nonlocal buf
        if not buf:
            return
        if len(buf) <= 2:
            new_lines.extend(buf)
        buf = []

    for ln in lines:
        s = ln.strip()
        if len(s) <= 2 and s not in {"●"} and not re.match(r"^\d+\.$", s):
            buf.append(ln)
        else:
            flush_buf()
            # Only remove single-character letters (likely artifacts)
            # Page numbers (numeric lines) are already removed by preclean()
            if re.fullmatch(r"[A-Za-z]", s):
                continue
            new_lines.append(ln)
    flush_buf()

    t = "\n".join(new_lines)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


BULLET = re.compile(
    r"""^(?P<indent>[ \t]*)
        (?:
            (?:[-*•·]\s+) |
            (?:\d+\.\s+)  |
            (?:[a-z][\.\)]\s+) |
            (?:[ivxlcdm]+\.\s+)
        )
        (?P<text>.+?)\s*$
    """,
    re.I | re.X | re.M,
)


def get_bullet_type(line: str) -> str:
    """Identify bullet type: numbered, lettered, bullet, or roman."""
    if re.match(r"^\d+\.\s+", line):
        return "numbered"
    if re.match(r"^[a-z][\.\)]\s+", line):
        return "lettered"
    if re.match(r"^[-*•·]\s+", line):
        return "bullet"
    if re.match(r"^[ivxlcdm]+\.\s+", line, re.I):
        return "roman"
    return "unknown"


def collect_bullets(block: str) -> List[Tuple[int, str, str]]:
    """Extract bulleted items from text block with indentation and type info."""
    lines = block.splitlines()
    out: List[Tuple[int, str, str]] = []
    cur: Optional[Tuple[int, str, str]] = None

    def indent_units(s: str) -> int:
        spaces = s.replace("\t", "  ")
        return max(0, len(spaces) // 2)

    for raw in lines:
        m = BULLET.match(raw.rstrip())
        if m:
            if cur:
                out.append(cur)
            lvl = indent_units(m.group("indent"))
            bullet_type = get_bullet_type(raw.rstrip())
            cur = (lvl, m.group("text").strip(), bullet_type)
        elif (
            cur is not None and raw.strip() and isinstance(cur, tuple) and len(cur) == 3
        ):
            # cur is guaranteed to be a tuple of length 3 at this point
            lvl, text, bullet_type = cur  # pylint: disable=unpacking-non-sequence
            cur = (lvl, f"{text} {raw.strip()}", bullet_type)
    if cur:
        out.append(cur)
    return out


def _fix_lettered_levels(
    pairs: List[Tuple[int, str, str]],
) -> List[Tuple[int, str, str]]:
    """Fix indentation levels for lettered bullets."""
    fixed_pairs: List[Tuple[int, str, str]] = []
    for i, (lvl, txt, bullet_type) in enumerate(pairs):
        if bullet_type == "lettered":
            for j in range(i - 1, -1, -1):
                if pairs[j][2] == "numbered":
                    lvl = 1
                    break
        fixed_pairs.append((lvl, txt, bullet_type))
    return fixed_pairs


def _make_topic_node(text: str) -> Dict[str, Any]:
    """Create a topic node with cross-references."""
    xrefs, _ = _xrefs(text)
    name = _strip_xrefs(text)
    return {
        "name": name,
        "subs": [],
        "cross_references": xrefs,
    }


def _convert_subs_to_strings(items: List[Any]) -> List[Any]:
    """Convert subs to strings for schema compliance."""
    out: List[Any] = []
    for it in items:
        if isinstance(it, dict):
            it["subs"] = [
                sub["name"] if isinstance(sub, dict) else sub
                for sub in it.get("subs", [])
            ]
            out.append(it)
        else:
            out.append(it)
    return out


def _ensure_defaults(items: List[Any]):
    """Ensure all items have required default fields."""
    for it in items:
        if isinstance(it, dict):
            it.setdefault("cross_references", [])
            _ensure_defaults(it.get("subs", []))


def _has_orphaned_number_pattern(text: str) -> bool:
    """Check if text contains orphaned number pattern (e.g., "6. 7. 8.")."""
    return bool(re.search(r"\b\d+\.\s+\d+\.\s+\d+\.", text))


def _check_subs_for_orphaned_numbers(topic: Dict[str, Any]) -> bool:
    """Check if topic subs contain orphaned numbers pattern."""
    for sub in topic.get("subs", []):
        if isinstance(sub, str) and _has_orphaned_number_pattern(sub):
            return True
    return False


def _check_topic_anomalies(
    topic: Dict[str, Any], original_text: Optional[str] = None
) -> bool:
    """Check if topic has parsing anomalies (text patterns or orphaned numbers)."""
    name = topic.get("name", "")
    if _detect_parsing_anomaly(name):
        return True
    if original_text and _detect_parsing_anomaly(original_text):
        return True
    return _check_subs_for_orphaned_numbers(topic)


def bullets_to_tree(pairs: List[Tuple[int, str, str]]) -> List[Dict[str, Any]]:
    """Convert bulleted items into nested topic tree structure."""
    if not pairs:
        return []

    fixed_pairs = _fix_lettered_levels(pairs)
    root: List[Any] = []
    stack: List[Tuple[int, List[Any]]] = [(-1, root)]

    for lvl, text, _ in fixed_pairs:
        while stack and lvl <= stack[-1][0]:
            stack.pop()
        parent_list = stack[-1][1]

        node = _make_topic_node(text)
        parent_list.append(node)
        stack.append((lvl, node["subs"]))

    result = _convert_subs_to_strings(root)
    _ensure_defaults(result)
    return result


def split_numbered(block: str) -> List[str]:
    """Parse numbered list items with continuation lines."""
    if not block.strip():
        return []
    items, cur = [], None
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\d+\.\s*(.*)$", line)
        if m:
            if cur:
                items.append(cur.strip())
            cur = m.group(1).strip()
        else:
            cur = (cur + " " + line) if cur else line
    if cur:
        items.append(cur.strip())
    if items:
        return items
    txt = re.sub(r"\s+", " ", block.strip())
    parts = re.split(r"\.\s+(?=[A-Z])", txt)
    return [
        p + ("." if i < len(parts) - 1 else "")
        for i, p in enumerate(parts)
        if p.strip()
    ]


def section_id_and_title(heading: str, ka_code: str, idx: int) -> Tuple[str, str]:
    """Generate section ID and display title from heading text."""
    left, right = heading.split(": ", 1) if ": " in heading else (heading, "")
    sec_id = slug(left)
    if not re.match(r"^[a-z]+-[a-z0-9\-]+$", sec_id):
        sec_id = f"{ka_code.lower()}-sec-{idx + 1}"
    display = (
        left
        if (right and left.endswith(right))
        else (f"{left}: {right}" if right else left.replace("-", " "))
    )
    return sec_id, display


def get_block(text: str, start_pat: str, end_choices: List[str]) -> str:
    """Extract text block between start pattern and first matching end pattern."""
    m = re.search(start_pat, text, re.I | re.S)
    if not m:
        return ""
    start = m.end()
    candidates = []
    for e in end_choices:
        m2 = re.search(e, text[start:], re.I)
        if m2:
            candidates.append(m2.start())
    end = min(candidates) if candidates else len(text[start:])
    end_pos = start + end
    return text[start:end_pos].strip()


def drop_orphan_noise(block: str) -> str:
    """Remove orphaned single counters and letters from text block."""
    lines = block.splitlines()
    out = []
    for ln in lines:
        s = ln.strip()
        # Remove lines that are just numbers (e.g., "243")
        if re.fullmatch(r"\d+", s):
            continue
        # Remove lines that are just numbers with periods (e.g., "6.", "7.", "8.", "9.")
        if re.fullmatch(r"\d+\.\s*$", s):
            continue
        # Remove single letters (except A and I which are valid words)
        if re.fullmatch(r"[A-Za-z]", s) and s not in {"A", "I"}:
            continue
        out.append(ln)
    return "\n".join(out)


def parse_preamble(text: str) -> Dict[str, Any]:  # noqa: C901
    """Extract preamble sections including description, changes, and overview."""
    desc = get_block(
        text,
        r"\bPreamble\b",
        [
            r"\n\s*Changes since CS",
            r"\n\s*Overview",
            r"\n\s*Core Hours",
            r"\n\s*Knowledge Units",
        ],
    )
    if not desc:
        desc = get_block(
            text,
            r"Preamble",
            [
                r"\n\s*Changes since CS",
                r"\n\s*Overview",
                r"\n\s*Core Hours",
                r"\n\s*Knowledge Units",
            ],
        )
    changes = get_block(
        text,
        r"Changes since CS",
        [r"\n\s*Overview", r"\n\s*Core Hours", r"\n\s*Knowledge Units"],
    )
    # Only extract Overview if it's a standalone section heading
    # Look for "Overview" as a line by itself (not "Overview of...")
    # It should appear after Preamble/Changes and before Core Hours/Knowledge Units
    overview_raw = ""
    # Find "Overview" as standalone section heading (own line, optional colon)
    # Pattern: newline, optional whitespace, "Overview", optional colon, end of line
    # This ensures we only match "Overview" as a section heading, not "Overview of..."
    overview_match = re.search(r"\n\s*Overview\s*:?\s*$", text, re.MULTILINE)
    if overview_match:
        # Verify it appears before "Core Hours" or "Knowledge Units"
        overview_pos = overview_match.start()
        core_hours_pos = text.find("\nCore Hours", overview_pos)
        knowledge_units_pos = text.find("\nKnowledge Units", overview_pos)

        # Find the closest end marker
        end_pos = len(text)
        if core_hours_pos != -1:
            end_pos = min(end_pos, core_hours_pos)
        if knowledge_units_pos != -1:
            end_pos = min(end_pos, knowledge_units_pos)

        # Only extract if Overview appears before Core Hours/Knowledge Units
        if end_pos < len(text) and end_pos > overview_pos:
            overview_raw = text[overview_match.end() : end_pos].strip()  # noqa: E203
    overview: List[Dict[str, Any]] = []
    for line in overview_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\.\s+(.+?)\:\s*(.*)$", line)
        if m:
            order, title, desc_i = (
                int(m.group(1)),
                m.group(2).strip(),
                m.group(3).strip(),
            )
            overview.append({"order": order, "title": title, "description": desc_i})
        else:
            if overview:
                overview[-1]["description"] += " " + line
    out: Dict[str, Any] = {}
    if desc:
        out["description"] = desc.strip()
    if changes:
        out["changes_since_cs2013"] = changes.strip()
    if overview:
        out["overview"] = overview
    return out


def parse_core_hours(  # noqa: C901
    text: str,
) -> List[Dict[str, Optional[str]]]:
    """
    Parse the Core Hours table from the TXT file.
    Note: CS Core values can span multiple
    lines (e.g., "1 + 7 (DM, FPL, PDC, SDF,\nSE, OS)")
    """
    # Find Core Hours section
    core_hours_idx = text.find("Core Hours")
    if core_hours_idx == -1:
        return []

    # Extract section and find where it ends (look for "Knowledge Units" or similar)
    section = text[core_hours_idx:]
    end_markers = ["Knowledge Units", "\n\nNote:", "\n\n9."]
    end_idx = len(section)
    for marker in end_markers:
        idx = section.find(marker)
        if idx != -1 and idx < end_idx:
            end_idx = idx

    section = section[:end_idx]

    # Split into lines
    lines = [ln.strip() for ln in section.splitlines()]

    # Find header row (flexible matching for variations like "CS Core hours")
    header_idx = None
    for i, line in enumerate(lines):
        if line == "Knowledge Unit":
            # Check for CS Core header (with or without "hours")
            if i + 2 < len(lines):
                cs_core_line = lines[i + 1].strip()
                ka_core_line = lines[i + 2].strip()
                # Match "CS Core" or "CS Core hours" (case-insensitive)
                if re.match(
                    r"CS\s+Core\s*(hours)?\s*$", cs_core_line, re.I
                ) and re.match(r"KA\s+Core\s*(hours)?\s*$", ka_core_line, re.I):
                    header_idx = i + 3
                    break

    if header_idx is None:
        return []

    result: List[Dict[str, Optional[str]]] = []
    i = header_idx

    # Helper function to check if a line looks like a KU name (not a number or value)
    def is_ku_name(line: str) -> bool:
        if not line:
            return False
        # Skip single/double digit numbers (these are KA Core values)
        if line.isdigit() and len(line) <= 2:
            return False
        # Skip 3+ digit numbers (page numbers)
        if line.isdigit() and len(line) >= 3:
            return False
        # Skip lines that start with numbers and operators (CS Core values)
        if re.match(r"^\d+\s*[+\-]|\d+\s*\(\w", line):
            return False
        # Skip lines that are just "0" or "Total hours" continuation
        if line in ["0", "Total hours"]:
            return False
        return True

    # Helper function to check if a line is a CS Core value (including text values)
    def is_cs_core_value(line: str) -> bool:
        if not line:
            return False
        # Numbers with operators (e.g., "2", "1 + 4 (SEP)")
        if re.match(r"^\d+\s*([+\-]|\()", line):
            return True
        # Single/double digit numbers (simple numeric values)
        if line.isdigit() and len(line) <= 2:
            return True
        # Text values (e.g., "Included in SEP hours")
        if re.match(r"^[A-Z]", line):
            return True
        return False

    # Helper function to check if a line is a CS Core value continuation
    def is_cs_core_continuation(line: str) -> bool:
        if not line:
            return False
        # Lines starting with letters and ending with comma or closing paren
        if re.match(r"^[A-Z]", line) and (line.endswith(",") or line.endswith(")")):
            return True
        # Lines that complete a parenthetical expression
        if line.endswith(")") and not line.startswith("("):
            return True
        return False

    # Helper function to check if a line is a KA Core value
    def is_ka_core_value(line: str) -> bool:
        if not line:
            return False
        # Single or double digit numbers
        if line.isdigit() and len(line) <= 2:
            return True
        # "0" is a valid KA Core value
        if line == "0":
            return True
        return False

    # Parse rows (KU, CS Core [possibly multi-line], KA Core)
    while i < len(lines):
        # Stop at "Total" or "Total hours" row
        if lines[i] == "Total" or lines[i] == "Total hours":
            # Find CS Core and KA Core for Total row
            cs_core_val = lines[i + 1].strip() if i + 1 < len(lines) else None
            ka_core_val = lines[i + 2].strip() if i + 2 < len(lines) else None

            # Handle "Total hours" case where "hours" might be on next line
            if (
                lines[i] == "Total"
                and i + 1 < len(lines)
                and lines[i + 1].strip() == "hours"
            ):
                cs_core_val = lines[i + 2].strip() if i + 2 < len(lines) else None
                ka_core_val = lines[i + 3].strip() if i + 3 < len(lines) else None
                result.append(
                    {
                        "ku": "Total",
                        "cs_core": cs_core_val,
                        "ka_core": ka_core_val,
                    }
                )
                break

            result.append(
                {
                    "ku": "Total",
                    "cs_core": cs_core_val,
                    "ka_core": ka_core_val,
                }
            )
            break

        # Skip empty lines
        if not lines[i]:
            i += 1
            continue

        # Check if this looks like a KU name
        if not is_ku_name(lines[i]):
            i += 1
            continue

        # Get KU name
        ku = lines[i].strip()
        i += 1

        # Collect CS Core value (may span multiple lines, can be text or numbers)
        cs_core_parts = []

        # Check if next line is a CS Core value
        if i < len(lines) and lines[i]:
            # Skip page numbers (3+ digit numbers) first
            while i < len(lines) and lines[i].isdigit() and len(lines[i]) >= 3:
                i += 1

            # Check if current line (after skipping page numbers) is CS Core value
            if i < len(lines) and lines[i]:
                if is_cs_core_value(lines[i]):
                    cs_core_parts.append(lines[i])
                    i += 1
                else:
                    # If it doesn't look like a CS Core value, skip it
                    i += 1

            # Check if CS Core continues on next line(s)
            while i < len(lines):
                # Skip page numbers
                if lines[i].isdigit() and len(lines[i]) >= 3:
                    i += 1
                    continue
                # If next line is a CS Core continuation, merge it
                if is_cs_core_continuation(lines[i]):
                    cs_core_parts.append(lines[i])
                    i += 1
                # If next line is a KA Core value, stop
                elif is_ka_core_value(lines[i]):
                    break
                # If next line is empty, skip but don't break yet
                elif not lines[i]:
                    i += 1
                # Otherwise, stop (probably next KU)
                else:
                    break

        cs_core = " ".join(cs_core_parts).strip() if cs_core_parts else None

        # Get KA Core value (should be next non-empty line)
        ka_core = None
        while i < len(lines):
            if is_ka_core_value(lines[i]):
                ka_core = lines[i].strip()
                i += 1
                break
            elif not lines[i]:
                i += 1
            else:
                # If we hit something that's not a KA Core value and not empty,
                # we might be at the next KU, so don't advance i
                break

        # Only add if we have a valid KU name
        if ku:
            result.append(
                {
                    "ku": ku,
                    "cs_core": cs_core,
                    "ka_core": ka_core,
                }
            )

    return result


def _xrefs(text: str) -> Tuple[List[str], List[str]]:
    """Extract cross-references from text."""
    refs = []
    for m in re.findall(r"\(See also:\s*([^)]+)\)", text):
        refs += [r.strip() for r in m.split(",")]
    return refs, []


def _strip_xrefs(text: str) -> str:
    """Remove cross-reference annotations from text."""
    t = re.sub(r"\(See also:[^)]+\)", "", text)
    t = re.sub(r"\s+", " ", t).strip().rstrip(",;:")
    return t


def infer_cognitive_level_with_source(text: str) -> Tuple[Optional[str], Optional[str]]:
    s = text.strip().lower()
    first = re.split(r"[\s:]", s, maxsplit=1)[0]

    for dict_name, mapping in LO_DICTIONARIES:
        for level, verbs in mapping.items():
            if first in verbs:
                return level, dict_name

    return None, None


def infer_cognitive_level(text: str) -> Optional[str]:
    """Infer cognitive level from learning outcome text based on action verb."""
    level, _ = infer_cognitive_level_with_source(text)
    return level


def _extract_labeled_section(section: str, label: str, until: List[str]) -> str:
    """Extract a labeled section from text."""
    label_pat = label.replace(" ", r"[ -]?")
    return get_block(section, rf"{label_pat}\s*:", until)


def _parse_labeled_topics(section: str) -> Dict[str, List[Any]]:
    """Parse labeled topic sections (CS Core, KA Core, Non-Core)."""
    out: Dict[str, List[Any]] = {
        "cs_core": [],
        "ka_core": [],
        "non_core": [],
    }
    for key, dest in [
        ("CS Core", "cs_core"),
        ("KA Core", "ka_core"),
        ("Non-Core", "non_core"),
    ]:
        part = _extract_labeled_section(
            section,
            key,
            [
                r"\n\s*KA[ -]?Core\s*:",
                r"\n\s*Non-?Core\s*:",
                r"\n\s*Illustrative\s+Learning\s+Outcomes?:",
                r"\n\s*$",
            ],
        )
        if not part:
            continue
        pairs = collect_bullets(part)
        tree = bullets_to_tree(pairs) if pairs else []
        numbered_texts = []
        if not tree and part.strip():
            tree = []
            for t in split_numbered(part):
                name = _strip_xrefs(t)
                topic: Dict[str, Any] = {
                    "name": name,
                    "subs": [],
                    "cross_references": _xrefs(t)[0],
                }
                tree.append(topic)
                numbered_texts.append(t)  # Store original text for anomaly checking
        # Check all topics for anomalies once after creation
        for idx, topic in enumerate(tree):
            if isinstance(topic, dict):
                # For numbered topics, check original text; bulleted, only name/subs
                original_text = (
                    numbered_texts[idx] if idx < len(numbered_texts) else None
                )
                if _check_topic_anomalies(topic, original_text):
                    topic["parsing_anomaly"] = True
        out[dest] = tree
    return out


def _detect_parsing_anomaly(text: str) -> bool:
    """Detect if text might contain merged items or orphaned numbers."""
    t = text.strip()
    if _has_orphaned_number_pattern(t):
        return True
    sentence_markers = len(re.findall(r"[.;]\s+[A-Z0-9]", t))
    return len(t) > 500 and sentence_markers >= 2


def _enrich_learning_outcomes(items: List[str]) -> List[Dict[str, Any]]:
    """Add cognitive levels to learning outcome items."""
    enriched: List[Dict[str, Any]] = []
    for t in items:
        level, source = infer_cognitive_level_with_source(t)
        level = level or "Explain"
        source = source or "fallback-default"

        anomaly = _detect_parsing_anomaly(t)

        item: Dict[str, Any] = {
            "text": t.strip(),
            "cognitive_level": level,
            "cognitive_level_source": source,
        }
        if anomaly:
            item["parsing_anomaly"] = True

        enriched.append(item)
    return enriched


def _extract_and_enrich_learning_outcomes(block: str) -> List[Dict[str, Any]]:
    """Unified extractor: extract LO items (bullets or numbered) and enrich them."""
    bullets = collect_bullets(block)
    items = [txt for _, txt, _ in bullets] if bullets else split_numbered(block)
    return _enrich_learning_outcomes([t for t in items if t.strip()])


def _parse_labeled_learning_outcomes(block: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse labeled learning outcome sections."""
    out: Dict[str, List[Dict[str, Any]]] = {
        "cs_core": [],
        "ka_core": [],
        "non_core": [],
        "general": [],
    }
    if not block.strip():
        return out
    for key, dest in [
        ("CS Core", "cs_core"),
        ("KA Core", "ka_core"),
        ("Non-Core", "non_core"),
    ]:
        label_pat = key.replace(" ", r"[ -]?")
        part = get_block(
            block,
            rf"{label_pat}\s*:",
            [r"\n\s*KA[ -]?Core\s*:", r"\n\s*Non-?Core\s*:", r"\n\s*$"],
        )
        if part:
            out[dest] = _extract_and_enrich_learning_outcomes(part)
    return out


def _parse_general_learning_outcomes(block: str) -> List[Dict[str, Any]]:
    """Parse unlabeled learning outcomes into general category."""
    lo_pattern = r"Illustrative\s+Learning\s+Outcomes?:\s*"
    general_block = re.sub(lo_pattern, "", block, flags=re.I)
    core_pattern = r"(?:CS|KA)[ -]?Core\s*:.*?(?=\n(?:CS|KA|Non)[ -]?Core\s*:|\Z)"
    general_block = re.sub(core_pattern, "", general_block, flags=re.I | re.S)
    noncore_pattern = r"Non-?Core\s*:.*$"
    general_block = re.sub(
        noncore_pattern, "", general_block, flags=re.I | re.S
    ).strip()
    if general_block and not re.match(r"^\s*$", general_block):
        return _extract_and_enrich_learning_outcomes(general_block)
    return []


def _has_orphaned_numbers(text: str) -> bool:
    """
    Check if text contains orphaned number patterns before cleaning.
    Orphaned numbers are lines like "6.", "7.", "8.", "9." on separate lines.
    """
    lines = text.splitlines()
    orphaned_count = 0
    for ln in lines:
        s = ln.strip()
        # Check for lines that are just numbers with periods (e.g., "6.", "7.")
        if re.fullmatch(r"\d+\.\s*$", s):
            orphaned_count += 1
    # If we have 2+ consecutive orphaned numbers, it's likely a parsing issue
    return orphaned_count >= 2


def _find_topics_with_orphaned_numbers(
    topics: Dict[str, List[Any]], topics_raw_original: str
) -> set:
    """
    Find which specific topics contain orphaned numbers in the raw text.
    Returns a set of (category, index) tuples for topics that contain orphaned numbers.

    Strategy: Check which category has orphaned numbers, then flag topics
    in that category that show signs of being affected (long subs, merged).
    """
    affected_topics: set = set()

    # Check which categories have orphaned numbers
    categories_with_orphaned: set = set()
    for key, dest in [
        ("CS Core", "cs_core"),
        ("KA Core", "ka_core"),
        ("Non-Core", "non_core"),
    ]:
        part = _extract_labeled_section(
            topics_raw_original,
            key,
            [
                r"\n\s*KA[ -]?Core\s*:",
                r"\n\s*Non-?Core\s*:",
                r"\n\s*Illustrative\s+Learning\s+Outcomes?:",
                r"\n\s*$",
            ],
        )
        if part and _has_orphaned_numbers(part):
            categories_with_orphaned.add(dest)

    # For categories with orphaned numbers, flag topics showing signs of being affected
    # Signs: very long subs (>300 chars), orphaned number patterns, or merged content
    for cat in categories_with_orphaned:
        topic_list = topics.get(cat, [])
        for idx, topic in enumerate(topic_list):
            # Check subs for signs of orphaned numbers affecting parsing
            subs = topic.get("subs", [])
            has_long_merged_subs = False
            for sub in subs:
                if isinstance(sub, str):
                    if len(sub) > 300 or _has_orphaned_number_pattern(sub):
                        has_long_merged_subs = True
                        break

            # Flag topic if it has signs of being affected by orphaned numbers
            if has_long_merged_subs:
                affected_topics.add((cat, idx))

    return affected_topics


def parse_three_block(section: str) -> Dict[str, Dict[str, Any]]:
    """Parse knowledge unit section into topics and learning outcomes."""
    # Split section at "Illustrative Learning Outcomes:" to separate topics
    # Do this BEFORE cleaning to check for orphaned numbers in original text
    learning_outcomes_match = re.search(
        r"Illustrative\s+Learning\s+Outcomes?:", section, re.I
    )
    if learning_outcomes_match:
        start_pos = learning_outcomes_match.start()
        topics_raw_original = section[:start_pos].strip()
    else:
        topics_raw_original = section

    # Now clean the sections
    section = drop_orphan_noise(section)
    if learning_outcomes_match:
        start_pos = learning_outcomes_match.start()
        topics_raw = section[:start_pos].strip()
        los_raw = section[start_pos:].strip()
        los_raw = re.sub(
            r"Illustrative\s+Learning\s+Outcomes?:\s*", "", los_raw, flags=re.I
        )
    else:
        topics_raw = section
        los_raw = ""

    topics = _parse_labeled_topics(topics_raw)
    learning_outcomes = _parse_labeled_learning_outcomes(los_raw)
    learning_outcomes["general"] = _parse_general_learning_outcomes(los_raw)

    # Find which specific topics contain orphaned numbers (only flag those)
    affected_topics = _find_topics_with_orphaned_numbers(topics, topics_raw_original)

    # Assign order numbers (order first in dict)
    # Flag topics that are specifically affected by orphaned numbers in raw text
    # (anomalies from text patterns and subs checked in _parse_labeled_topics)
    order = 1
    for cat in ["cs_core", "ka_core", "non_core"]:
        for i, topic in enumerate(topics.get(cat, [])):
            if (cat, i) in affected_topics:
                topic["parsing_anomaly"] = True
            topics[cat][i] = {"order": order, **topic}
            order += 1
    order = 1
    for cat in ["cs_core", "ka_core", "non_core", "general"]:
        for i, lo in enumerate(learning_outcomes.get(cat, [])):
            learning_outcomes[cat][i] = {"order": order, **lo}
            order += 1

    return {
        "topics": topics,
        "learning_outcomes": learning_outcomes,
    }


def extract_ku_sections(full_text: str, ka_code: str) -> List[Tuple[str, str]]:
    """Extract knowledge unit sections from text."""
    ku_scope = get_block(
        full_text,
        r"\bKnowledge Units\b",
        [
            r"\n\s*Professional Dispositions",
            r"\n\s*Mathematics Requirements",
            r"\n\s*Committee",
            r"\Z",
        ],
    )
    if not ku_scope:
        ku_scope = full_text

    head_pat = re.compile(rf"^[\s\f]*({ka_code}[/-][^\n:]+)\s*:\s*(.*)$", re.M)
    out: List[Tuple[str, str]] = []

    for m in head_pat.finditer(ku_scope):
        start = m.end()
        next_m = head_pat.search(ku_scope, start)
        end = next_m.start() if next_m else len(ku_scope)

        left = m.group(1).strip()
        right_inline = m.group(2).strip()
        subtitle = right_inline

        body_region = ku_scope[start:end].lstrip()
        if not subtitle:
            first_line = (
                body_region.splitlines()[0].strip() if body_region.splitlines() else ""
            )
            if (
                first_line
                and len(first_line) <= 80
                and not re.match(r"^(CS|KA)[ -]?Core\s*:$", first_line, re.I)
            ):
                subtitle = first_line
                off = body_region.find(first_line) + len(first_line)
                body = body_region[off:].strip()
            else:
                body = body_region.strip()
        else:
            body = body_region.strip()

        heading = f"{left}: {subtitle}" if subtitle else left
        out.append((heading, body))

    return out


def parse_dispositions(text: str) -> List[Dict[str, str]]:
    """Parse professional dispositions section."""
    block = get_block(
        text,
        r"Professional Dispositions",
        [
            r"\n\s*Mathematics Requirements",
            r"\n\s*Course Packaging Suggestions",
            r"\n\s*Committee",
            r"\Z",
        ],
    )
    if not block:
        return []
    items: List[Dict[str, str]] = []
    for line in block.splitlines():
        line = line.strip()
        # Skip empty lines, standalone bullets, and page numbers
        if not line or line == "●" or (line.isdigit() and len(line) >= 3):
            continue
        # Remove bullet character if present
        if line.startswith("●"):
            line = line[1:].strip()
        # Match pattern: Name: Description
        m = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
        if m:
            items.append(
                {"name": m.group(1).strip(), "description": m.group(2).strip()}
            )
        elif items:
            # Continuation line - append to last item's description
            items[-1]["description"] += " " + line
    return items


def parse_math_requirements(text: str) -> Dict[str, List[Dict[str, str]]]:
    """Parse mathematics requirements section."""
    block = get_block(
        text,
        r"Mathematics Requirements",
        [r"\n\s*Course Packaging Suggestions", r"\n\s*Committee", r"\Z"],
    )
    if not block:
        return {"required": [], "desirable": []}
    desirable: List[Dict[str, str]] = []
    required: List[Dict[str, str]] = []
    for line in block.splitlines():
        line = line.strip()
        if not line or not line.startswith("●"):
            continue
        topic = line.replace("●", "", 1).strip()
        notes = ""
        m = re.search(r"\(([^)]+)\)$", topic)
        if m:
            notes = m.group(1).strip()
            topic = topic[: m.start()].strip()
        desirable.append({"topic": topic, "notes": notes})
    return {"required": required, "desirable": desirable}


def parse_course_packaging(text: str) -> Dict[str, Any]:
    """Parse course packaging suggestions section."""
    block = get_block(text, r"Course Packaging Suggestions", [r"\n\s*Committee", r"\Z"])
    if not block:
        return {
            "advanced_course_hours": [],
            "prerequisites": [],
            "objectives": "",
        }
    adv, pre, obj = [], [], ""
    section: Optional[str] = None
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("advanced course"):
            section = "adv"
            continue
        if line.lower().startswith("prerequisites"):
            section = "pre"
            continue
        if line.lower().startswith("course objectives"):
            section = "obj"
            obj = line.split(":", 1)[1].strip()
            continue
        if section == "adv" and line.startswith("●"):
            txt = line[1:].strip()
            m = re.match(r"^(.*)\((\d+)\s*hours?\)\s*$", txt)
            if m:
                adv.append(
                    {
                        "knowledge_unit": m.group(1).strip(),
                        "hours": int(m.group(2)),
                    }
                )
        elif section == "pre" and line.startswith("●"):
            pre.append(line[1:].strip())
        elif section == "obj":
            obj += " " + line
    return {
        "advanced_course_hours": adv,
        "prerequisites": pre,
        "objectives": obj.strip(),
    }


def parse_committee(text: str) -> Dict[str, Any]:
    """Parse committee section."""
    block = get_block(text, r"Committee", [r"\Z"])
    if not block:
        return {"chair": {}, "members": [], "contributors": []}
    chair: Dict[str, str] = {}
    members: List[Dict[str, str]] = []
    contributors: List[Dict[str, str]] = []
    section: Optional[str] = None
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Chair:"):
            section = "chair"
            parts = [p.strip() for p in line.replace("Chair:", "", 1).split(",")]
            if len(parts) >= 3:
                chair = {
                    "name": parts[0],
                    "affiliation": parts[1],
                    "location": parts[2],
                }
        elif line.startswith("Members:"):
            section = "members"
        elif line.startswith("Contributors:"):
            section = "contributors"
        elif line.startswith("●"):
            parts = [p.strip() for p in line[1:].split(",")]
            if len(parts) >= 3:
                entry = {
                    "name": parts[0],
                    "affiliation": parts[1],
                    "location": parts[2],
                }
                (members if section == "members" else contributors).append(entry)
    return {"chair": chair, "members": members, "contributors": contributors}


def build_document(
    text: str,
    ka_code: str,
    ka_name: str,
    input_file: str,
    include_provenance: bool = True,
    commit_sha: Optional[str] = None,
    tool_version: Optional[str] = None,
    pdf_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Build complete JSON document from curriculum text."""
    # Parse core_hours BEFORE preclean() because preclean() removes single-digit
    # lines that are valid CS Core/KA Core values in the table
    core_hours = parse_core_hours(text)

    text = preclean(text)
    text = normalize_glitches(text)

    pre = parse_preamble(text)
    ku_sections = extract_ku_sections(text, ka_code)

    sections = []
    for idx, (heading, body) in enumerate(ku_sections):
        sec_id, title = section_id_and_title(heading, ka_code, idx)
        triple = parse_three_block(body)
        sec: Dict[str, Any] = {
            "id": sec_id,
            "title": title,
            "order": idx + 1,
            "topics": triple["topics"],
            "learning_outcomes": triple["learning_outcomes"],
            "source_loc": {"file": input_file, "section": idx + 1},
            "subsections": [],
        }
        if include_provenance:
            prov = {"content_hash": sha256(body), "tool": TOOL_NAME}
            if tool_version:
                prov["tool_version"] = tool_version
            if commit_sha:
                prov["commit_sha"] = commit_sha
            sec["provenance"] = prov
        sections.append(sec)

    schema_obj: Dict[str, Any] = {
        "name": "ka.schema.v2",
        "version": SCHEMA_VERSION,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "source": input_file,
        "schema_ref": "schema/ka.schema.v2.json",
    }
    if tool_version:
        schema_obj["parser_version"] = tool_version
    if pdf_path:
        pdf_hash = file_sha256(Path(pdf_path))
        if pdf_hash:
            schema_obj["pdf_hash"] = pdf_hash

    doc: Dict[str, Any] = {
        "schema": schema_obj,
        "knowledge_area": {"name": ka_name, "code": ka_code},
        "preamble": pre,
        "core_hours": core_hours,
        "knowledge_units": sections,
        "professional_dispositions": parse_dispositions(text),
        "mathematics_requirements": parse_math_requirements(text),
        "course_packaging_suggestions": parse_course_packaging(text),
        "committee": parse_committee(text),
    }
    return doc


def main():
    """Command-line interface for the parser."""
    ap = argparse.ArgumentParser(
        description="Parse CS2023 curriculum text to structured JSON."
    )
    ap.add_argument("--txt", required=True, help="Input text file path")
    ap.add_argument("--out", required=True, help="Output JSON file path")
    ap.add_argument("--ka-code", help="Knowledge area code (e.g., SE, SEC)")
    ap.add_argument(
        "--ka-name", help="Knowledge area name (e.g., Software Engineering)"
    )
    ap.add_argument(
        "--no-provenance",
        action="store_true",
        help="Exclude provenance metadata",
    )
    ap.add_argument("--commit-sha", help="Git commit SHA for provenance")
    ap.add_argument("--schema", help="JSON schema file for validation")
    ap.add_argument("--strict", action="store_true", help="Exit on validation failure")
    ap.add_argument("--tool-version", help="Tool version string for provenance")
    ap.add_argument("--pdf", help="PDF file path for hash computation")
    args = ap.parse_args()

    txt_path = Path(args.txt)
    if not txt_path.exists():
        print(f"ERROR: file not found: {txt_path}", file=sys.stderr)
        sys.exit(2)

    raw = txt_path.read_text(encoding="utf-8", errors="ignore")

    ka_code, ka_name = args.ka_code, args.ka_name
    if not ka_code or not ka_name:
        m = re.match(r"^([A-Z]{2,5})[ _-]+(.+)$", txt_path.stem)
        if m:
            ka_code = m.group(1)
            ka_name = re.sub(r"[_-]+", " ", m.group(2)).strip().title()
        else:
            ka_code = ka_code or "KA"
            ka_name = ka_name or "Knowledge Area"

    doc = build_document(
        text=raw,
        ka_code=ka_code,
        ka_name=ka_name,
        input_file=str(txt_path),
        include_provenance=(not args.no_provenance),
        commit_sha=args.commit_sha,
        tool_version=args.tool_version,
        pdf_path=args.pdf,
    )

    if args.schema:
        if jsonschema is None:
            print(
                "jsonschema not available, skipping validation",
                file=sys.stderr,
            )
        else:
            try:
                schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
                jsonschema.validate(instance=doc, schema=schema)
                print("Schema validation: OK", file=sys.stderr)
            except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
                print(f"Schema validation failed: {e}", file=sys.stderr)
                if args.strict:
                    sys.exit(1)

    Path(args.out).write_text(
        json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {args.out} (KA: {ka_code} — {ka_name})")


if __name__ == "__main__":
    main()
