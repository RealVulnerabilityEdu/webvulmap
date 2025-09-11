import json
import re
import sys
import os

def infer_ka_code_and_name(filename):
    base = os.path.basename(filename)
    name_part = os.path.splitext(base)[0]
    # Split at first underscore, if present
    if "_" in name_part:
        ka_code, ka_name = name_part.split("_", 1)
        ka_name = ka_name.replace("_", " ").replace("-", " ").title()
    else:
        ka_code = name_part
        ka_name = name_part.title()
    return ka_code, ka_name

def clean_text(text):
    # Remove page numbers (lines with only digits)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove form feed characters
    text = text.replace('\f', '')
    # Fix broken hyphens at line breaks
    text = re.sub(r'-\n(\w+)', r'\1', text)
    # Remove extra newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def parse_ka_text_to_json(input_txt, output_json):
    with open(input_txt, 'r', encoding='utf-8') as f:
        text = f.read()

    # --- edge-case: empty input -> fail fast (tests expect non-zero + 'empty' in message)
    if text.strip() == "":
        print("Error: empty input file", file=sys.stderr)
        sys.exit(1)

    text = clean_text(text)

    # --- edge-case: no header -> fail fast (tests expect non-zero + 'header' in message)
    section_pattern = re.compile(r'^[A-Z]+-[A-Za-z-]+: .+$', re.MULTILINE)
    if not section_pattern.search(text):
        print("Error: missing or invalid header (expected lines like 'SE-...: ...')", file=sys.stderr)
        sys.exit(1)

    # Infer KA name and code from filename
    ka_code, ka_name = infer_ka_code_and_name(input_txt)

    # Find headers
    section_headers = list(section_pattern.finditer(text))

    sections = []
    description = ""

    if section_headers:
        description = text[:section_headers[0].start()].strip()
        for i, match in enumerate(section_headers):
            title = match.group(0).strip()
            start = match.end()
            end = section_headers[i + 1].start() if i + 1 < len(section_headers) else len(text)
            content = text[start:end].strip()
            sections.append({
                "title": title,
                "content_as_text": content
            })
    else:
        description = text.strip()

    result = {
        "knowledge_area": {
            "name": ka_name,
            "code": ka_code
        },
        "description": description,
        "sections": sections
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Parsed {len(sections)} sections from '{input_txt}' and wrote JSON to '{output_json}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 parse_ka_text_to_json.py <input_txt> <output_json>")
        sys.exit(1)
    parse_ka_text_to_json(sys.argv[1], sys.argv[2])