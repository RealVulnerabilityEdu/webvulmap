import pandas as pd
import json
import re
import subprocess
import time

file_path = "CS2023_ka_meta.csv"
df = pd.read_csv(file_path, encoding="utf-8")

def query_model(prompt, model="deepseek-llm"):
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

    base_prompt = (
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

    fallback_prompt = (
        f"The topic is '{topic}'.\n"
        f"Explain briefly how this topic could relate to insecure software design or development, and provide at least one relevant CWE.\n"
        f"Format as:\n"
        f"CWE-ID (CWE Name)\nReason\n"
    )

    retries = 0
    max_retries = 3
    cwe_data = []

    # First attempt with base_prompt
    while retries < max_retries and not cwe_data:
        response = query_model(base_prompt)
        cwe_data = extract_cwe_data(response)
        if not cwe_data:
            print(f"No CWEs found with base prompt, retrying ({retries+1}/{max_retries})...")
            retries += 1
            time.sleep(2)

    # If base_prompt fails, fallback to fallback_prompt
    if not cwe_data:
        print("Switching to fallback prompt...")
        retries = 0
        while retries < max_retries and not cwe_data:
            response = query_model(fallback_prompt)
            cwe_data = extract_cwe_data(response)
            if not cwe_data:
                print(f"No CWEs found with fallback prompt, retrying ({retries+1}/{max_retries})...")
                retries += 1
                time.sleep(2)

    if not cwe_data:
        print("Skipping topic after all attempts failed.")
        continue

    mappings[topic] = cwe_data

    for item in cwe_data:
        print(f"{item['cwe']} ({item['name']})\n{item['reason']}\n")

output_file = "Deepseek_Mapping.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(mappings, f, indent=4, ensure_ascii=False)

print(f"Mappings saved to {output_file}")

