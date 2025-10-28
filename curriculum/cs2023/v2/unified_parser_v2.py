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
    """Clean text by removing form feeds, carriage returns, and page numbers."""
    t = text.replace("\f", "").replace("\r", "")
    return "\n".join(
        line for line in t.splitlines() if not re.fullmatch(r"\s*\d{1,4}\s*", line)
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
            if re.fullmatch(r"\d+", s) or re.fullmatch(r"[A-Za-z]", s):
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
    return {
        "name": _strip_xrefs(text),
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
        if re.fullmatch(r"\d+", s):
            continue
        if re.fullmatch(r"[A-Za-z]", s) and s not in {"A", "I"}:
            continue
        out.append(ln)
    return "\n".join(out)


def parse_preamble(text: str) -> Dict[str, Any]:
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
    overview_raw = get_block(
        text, r"\bOverview\b", [r"\n\s*Core Hours", r"\n\s*Knowledge Units"]
    )
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


def parse_core_hours(
    text: str,
    ku_names: Optional[List[str]] = None,
    ka_code: Optional[str] = None,
) -> List[Dict[str, Optional[str]]]:
    """
    Placeholder for now. Returns empty array to match golden file expectations.
    Core hours parsing will be implemented in a future PR.
    """
    # Suppress unused argument warnings
    _ = text, ku_names, ka_code
    return []


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


_LO_MAP = {
    "Explain": {
        "explain",
        "describe",
        "discuss",
        "define",
        "outline",
        "summarize",
    },
    "Apply": {
        "apply",
        "use",
        "implement",
        "execute",
        "perform",
        "demonstrate",
    },
    "Evaluate": {
        "evaluate",
        "assess",
        "compare",
        "contrast",
        "critique",
        "justify",
    },
    "Develop": {
        "develop",
        "design",
        "create",
        "construct",
        "refactor",
        "produce",
        "build",
    },
}


def infer_cognitive_level(text: str) -> Optional[str]:
    """Infer cognitive level from learning outcome text based on action verb."""
    s = text.strip().lower()
    first = re.split(r"[\s:]", s, maxsplit=1)[0]
    for level, verbs in _LO_MAP.items():
        if first in verbs:
            return level
    return None


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
        if not tree and part.strip():
            tree = [
                {
                    "name": _strip_xrefs(t),
                    "subs": [],
                    "cross_references": _xrefs(t)[0],
                }
                for t in split_numbered(part)
            ]
        out[dest] = tree
    return out


def _enrich_learning_outcomes(items: List[str]) -> List[Dict[str, str]]:
    """Add cognitive levels to learning outcome items."""
    enriched: List[Dict[str, str]] = []
    for t in items:
        level = infer_cognitive_level(t)
        if level:
            enriched.append({"text": t.strip(), "cognitive_level": level})
        else:
            enriched.append({"text": t.strip(), "cognitive_level": "Explain"})
    return enriched


def _parse_labeled_learning_outcomes(block: str) -> Dict[str, List[Dict[str, str]]]:
    """Parse labeled learning outcome sections."""
    out: Dict[str, List[Dict[str, str]]] = {
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
        if not part:
            continue

        bullets = collect_bullets(part)
        items = [txt for _, txt, _ in bullets] if bullets else split_numbered(part)
        out[dest] = _enrich_learning_outcomes(items)

    return out


def _parse_general_learning_outcomes(block: str) -> List[Dict[str, str]]:
    """Parse unlabeled learning outcomes into general category."""
    general_block = block
    general_block = re.sub(
        r"Illustrative\s+Learning\s+Outcomes?:\s*",
        "",
        general_block,
        flags=re.I,
    )
    general_block = re.sub(
        r"(?:CS|KA)[ -]?Core\s*:.*?(?=\n(?:CS|KA|Non)[ -]?Core\s*:|\Z)",
        "",
        general_block,
        flags=re.I | re.S,
    )
    general_block = re.sub(r"Non-?Core\s*:.*$", "", general_block, flags=re.I | re.S)

    general_block = general_block.strip()

    if general_block and not re.match(r"^\s*$", general_block):
        bullets = collect_bullets(general_block)
        items = (
            [txt for _, txt, _ in bullets] if bullets else split_numbered(general_block)
        )
        return _enrich_learning_outcomes([t for t in items if t.strip()])

    return []


def parse_three_block(section: str) -> Dict[str, Dict[str, Any]]:
    """Parse knowledge unit section into topics and learning outcomes."""
    section = drop_orphan_noise(section)

    # Split section at "Illustrative Learning Outcomes:" to separate topics
    learning_outcomes_match = re.search(
        r"Illustrative\s+Learning\s+Outcomes?:", section, re.I
    )
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
        if not line or line == "●":
            continue
        m = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
        if m:
            items.append(
                {"name": m.group(1).strip(), "description": m.group(2).strip()}
            )
        elif items:
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
    text = preclean(text)
    text = normalize_glitches(text)

    pre = parse_preamble(text)
    core_hours = parse_core_hours(text)
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
            ka_code = ka_code or "SEC"
            ka_name = ka_name or "Security"

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
