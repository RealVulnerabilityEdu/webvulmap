import json
import re
from datetime import datetime


def extract_learning_outcomes(text):
    """
    Extracts learning outcomes from sentences containing 'Learning outcomes'
    or similar phrases. Returns a list of outcome objects with id, text,
    and cognitive_level.
    """
    outcomes = []
    # Find sentences with 'Learning outcomes' or similar
    matches = re.findall(r"(Learning outcomes[^.]*\.)", text, re.IGNORECASE)
    idx = 1
    for match in matches:
        outcome_text = re.sub(
            r"Learning outcomes (focus on|include|are)?",
            "",
            match,
            flags=re.IGNORECASE,
        ).strip()
        if outcome_text:
            outcomes.append(
                {
                    "id": f"lo-{idx}",
                    "text": outcome_text,
                    "cognitive_level": "Apply",
                }
            )
            idx += 1
    # Also look for sentences starting with 'Students will', 'Ability to', etc.
    for sentence in re.split(r"\. ", text):
        if re.match(
            r"^(Students will|Ability to|Learn to|Create|Document)",
            sentence.strip(),
        ):
            outcomes.append(
                {
                    "id": f"lo-{idx}",
                    "text": sentence.strip(),
                    "cognitive_level": "Understand",
                }
            )
            idx += 1
    return outcomes


def extract_topics(text):
    topics = []
    patterns = [
        r"(?:including|Key topics include|topics:)\s+(.+?)[.\n]",
        r"topics\s*-\s*(.+?)[.\n]",
    ]
    idx = 1
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            for t in m.group(1).split(","):
                topics.append({"id": f"topic-{idx}", "name": t.strip()})
                idx += 1
            break
    return topics


def v1_section_to_v2(section, idx):
    return {
        "id": f"se-sec-{idx+1}",
        "title": section.get("title", f"Section {idx+1}"),
        "order": idx + 1,
        "summary": (
            section["content_as_text"].split(".")[0]
            if "content_as_text" in section
            else ""
        ),
        "topics": extract_topics(section.get("content_as_text", "")),
        "learning_outcomes": extract_learning_outcomes(
            section.get("content_as_text", "")
        ),
        "bullets": [],
        "crossrefs": [],
        "qa_flags": {},
        "source_loc": {"file": "SE_SAMPLE_v1.json", "section": idx + 1},
        "subsections": [],
    }


def convert_v1_to_v2(v1_path, v2_path):
    with open(v1_path) as f:
        v1 = json.load(f)

    v2 = {
        "schema": {
            "name": "Knowledge Area/Skill Area Unified Schema v2",
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": v1_path,
        },
        "knowledge_area": v1["knowledge_area"],
        "description": v1["description"],
        "sections": [
            v1_section_to_v2(sec, idx)
            for idx, sec in enumerate(v1["sections"])
        ],
    }

    with open(v2_path, "w") as f:
        json.dump(v2, f, indent=2)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 parse_v1_to_v2.py input_v1.json output_v2.json")
    else:
        convert_v1_to_v2(sys.argv[1], sys.argv[2])
