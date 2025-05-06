import json
import subprocess
import time

INPUT_JSON = "knowledge_areas_final.json"
OUTPUT_JSON = "cwe_mappings4.json"
MODEL = "mistral"
SLEEP_BETWEEN_CALLS = 1.5  # seconds

def query_model(prompt, model=MODEL):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result.stdout.strip()

def build_prompt(ka, ku):
    return f"""
You are a cybersecurity expert.

Knowledge Area: {ka}
Knowledge Unit: {ku}

Step by step, identify Common Weakness Enumerations (CWEs) that are most relevant to this unit.
For each CWE, provide the CWE-ID, CWE title, and a one-line justification.
Format:
CWE-ID: CWE Title — Reason
"""

def main():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        ka_data = json.load(f)

    output = {}

    for ka, kus in ka_data.items():
        print(f"\nProcessing Knowledge Area: {ka}")
        output[ka] = {}

        for ku in kus:
            print(f"  ↳ Querying KU: {ku}")
            prompt = build_prompt(ka, ku)
            response = query_model(prompt)
            output[ka][ku] = response.splitlines()
            time.sleep(SLEEP_BETWEEN_CALLS)  # throttle to avoid overload

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"\n✅ CWE mappings saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
