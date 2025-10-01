"""Use Zero-Shot promping for mapping."""

import json
import re
import subprocess

import pandas as pd

file_path = "CS2023_ka_meta.csv"
df = pd.read_csv(file_path, encoding="utf-8")


def query_model(model_prompt, model="mistral"):
    result = subprocess.run(
        ["ollama", "run", model, model_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout.strip()


def extract_cwe_data(model_response):
    pattern = r"(CWE-\d+)\s+(.+)\n\s*(.+)"
    matches = re.findall(pattern, model_response)
    return [{
        "cwe": m[0],
        "name": m[1].strip(),
        "reason": m[2].strip()
    } for m in matches]


mappings = {}
for topic in df["ka"]:
    print(f"\nProcessing Topic: {topic}")

    # Balanced prompt: Focused but flexible
    prompt = (
        f"Identify 3 to 5 security CWEs relevant to the topic '{topic}'. "
        f"Prioritize CWEs that are commonly associated with this topic or "
        f"related areas.\n"
        f"If specific CWEs are not obvious, include common software security "
        f"risks that could still apply.\n\n"
        f"Format strictly as:\n"
        f"CWE-ID CWE Name\nReason\n\n"
        f"Example:\nCWE-79 Improper Neutralization of Input During Web Page "
        f"Generation\nReason: This occurs when user inputs are not properly "
        f"sanitized, leading to XSS attacks.\n\n"
        f"Begin now:\n")
    response = query_model(prompt)
    cwe_data = extract_cwe_data(response)

    # Retry fallback with similar balance but more urgency
    if not cwe_data:
        print("No CWEs found, retrying with slight fallback...")
        fallback_prompt = (
            f"Give 3 to 5 relevant or general CWEs for the topic '{topic}'. "
            f"If specific ones are hard to find, include widely applicable "
            f"CWEs.\n"
            f"Format exactly as:\nCWE-ID CWE Name\nReason\n\n"
            f"Do not leave this blank.\n"
            f"Begin:\n")
        response = query_model(fallback_prompt)
        cwe_data = extract_cwe_data(response)

    mappings[topic] = cwe_data

    if cwe_data:
        for item in cwe_data:
            print(f'{item["cwe"]} {item["name"]}\n{item["reason"]}\n')
    else:
        print("Still no CWE found after retry.\n")

output_file = "Zero_Shot_Mapping.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(mappings, f, indent=4, ensure_ascii=False)

print(f" Mappings saved to {output_file}")
