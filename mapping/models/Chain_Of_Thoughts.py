import pandas as pd
import json
import re
import subprocess

file_path = "CS2023_ka_meta.csv"
df = pd.read_csv(file_path, encoding="utf-8")

def query_model(prompt, model="mistral"):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result.stdout.strip()

def extract_cwe_data(response):
    pattern = r"(CWE-\d+)\s+\((.+?)\)\n(.+)"
    matches = re.findall(pattern, response)
    return [{"cwe": m[0], "name": m[1].strip(), "reason": m[2].strip()} for m in matches]

mappings = {}

for topic in df["ka"]:
    print(f"\nProcessing Topic: {topic}")

    # Chain of Thought Prompt (more guided and flexible)
    prompt = (
        f"You are a cybersecurity expert mapping CS topics to CWEs.\n"
        f"1. First, briefly explain the core idea of the topic '{topic}'.\n"
        f"2. Think step-by-step about how this topic might lead to common software security weaknesses.\n"
        f"3. Based on this reasoning, select the most relevant CWE (or the most general CWE if the mapping is unclear).\n\n"
        f"Always provide at least one CWE.\n"
        f"Format exactly as:\n"
        f"CWE-ID (CWE Name)\nReason\n\n"
        f"Example:\nCWE-79 (Improper Neutralization of Input During Web Page Generation)\nReason: This occurs when user inputs are not properly sanitized, leading to XSS attacks.\n\n"
        f"Begin now:\n"
    )
    response = query_model(prompt)
    cwe_data = extract_cwe_data(response)

    # Fallback in case no CWE is found
    if not cwe_data:
        print("No CWEs found, retrying with fallback...")
        fallback_prompt = (
            f"The topic is '{topic}'. Map it to at least 1 relevant CWE.\n"
            f"If uncertain, assign CWE-1000 (Default Weakness: Insufficient Security Assessment).\n"
            f"Chain of Thought: Explain your reasoning first, then present the CWE as:\n"
            f"CWE-ID (CWE Name)\nReason\n"
        )
        response = query_model(fallback_prompt)
        cwe_data = extract_cwe_data(response)

        # If still empty, hard fallback
        if not cwe_data:
            cwe_data = [{
                "cwe": "CWE-1000",
                "name": "Default Weakness: Insufficient Security Assessment",
                "reason": "No direct CWE found; assigned a general weakness for lacking thorough security evaluation."
            }]

    mappings[topic] = cwe_data

    for item in cwe_data:
        print(f"{item['cwe']} ({item['name']})\n{item['reason']}\n")

output_file = "Chain_Of_Thoughts_Mapping.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(mappings, f, indent=4, ensure_ascii=False)

print(f"Mappings saved to {output_file}")