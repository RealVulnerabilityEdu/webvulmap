"""Use zero-shot + LangChain + Ollama on 2023 CS Curriculum"""

import json
import os
import sys

from langchain_ollama import OllamaLLM
from ollama._types import ResponseError


def load_ka_name(json_path):
    """Load the Knowledge Area name from the JSON input."""
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("knowledge_area", {}).get("name", None)


def query_ollama(ka_name, model_name="mistral"):
    """Use Ollama with two fallback prompts to map KA to CWE(s)."""
    llm = OllamaLLM(model=model_name)

    primary_prompt = (
        f"What ONE cwe is most relevant to the computer science topic"
        f" {ka_name}?\n"
        f"\nFORMAT YOUR ANSWER STRICTLY AS:\n"
        f"CWE: (NO WORDS HERE ONLY NUMBER)\n"
        f"Name:\n"
        f"Reason:"
    )
    fallback_prompt = (
        f"Which potential cwes can be relevant to the computer science"
        f"knowledge area {ka_name}? Give me 3-5 cwes.\n"
        f"\nFORMAT YOUR ANSWER STRICTLY AS:\n"
        f"CWE: (NO WORDS HERE ONLY NUMBER)"
        f"Name:\n"
        f"Reason:"
    )

    print(f"\nAsking primary prompt:\n{primary_prompt}\n")
    try:
        primary_response = llm.invoke(primary_prompt).strip()
    except (ValueError, ConnectionError, ResponseError) as e:
        print(f"Error calling Ollama: {e}")
        return "Error: LLM invocation failed."

    if "CWE:" in primary_response:
        print("MAPPING NOW (from primary prompt).....")
        return primary_response

    print("\nNo direct CWE found in primary response. Trying fallback...\n")
    print(f"Asking fallback prompt:\n{fallback_prompt}\n")
    try:
        fallback_response = llm.invoke(fallback_prompt).strip()
    except (ValueError, ConnectionError, ResponseError) as e:
        print(f"Error calling Ollama (fallback): {e}")
        return "Error: Fallback LLM invocation failed."

    if "CWE:" in fallback_response:
        print("MAPPING NOW (from fallback prompt).....")
        return fallback_response

    return "No CWE mapping could be determined from either prompt."


def parse_cwe_result(cwe_result):
    """
    Parse the raw CWE mapping response into structured entries.

    Args:
        cwe_result (str): Raw text response from the LLM.

    Returns:
        list of dict: List of CWE entries with keys: cwe, name, reason.
    """
    cwe_entries = []
    current_entry = {}

    for line in cwe_result.strip().splitlines():
        if line.startswith("CWE: "):
            if current_entry:
                cwe_entries.append(current_entry)
                current_entry = {}
            current_entry["cwe"] = line.replace("CWE:", "").strip()
        elif line.startswith("Name:"):
            current_entry["name"] = line.replace("Name:", "").strip()
        elif line.startswith("Reason:"):
            current_entry["reason"] = line.replace("Reason:", "").strip()

    if current_entry:
        cwe_entries.append(current_entry)

    return cwe_entries


def update_output(output_file, ka_name, cwe_entries):
    """
    Update the output JSON file with new CWE mappings for the KA.

    Args:
        output_file (str): Path to output JSON file.
        ka_name (str): Knowledge Area name.
        cwe_entries (list): List of CWE mapping dictionaries.
    """
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    if ka_name in existing_data:
        existing_cwes = {entry["cwe"] for entry in existing_data[ka_name]}
        cwe_entries = [
            entry for entry in cwe_entries if entry["cwe"] not in existing_cwes
        ]

    if ka_name in existing_data:
        existing_data[ka_name].extend(cwe_entries)
    else:
        existing_data[ka_name] = cwe_entries

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        tuple: (json_path, output_file)
    """
    if len(sys.argv) < 3:
        print("Usage: python cs2023_zero_shot.py <SE_v2.json>" "<output.json> [--mock]")
        sys.exit(1)

    mock_mode = "--mock" in sys.argv

    return sys.argv[1], sys.argv[2], mock_mode


def main():
    """
    Main program entry point. Loads input,
    queries LLM, parses results, and writes output.
    OR handles mock mode for testing without Ollama.
    """
    json_path, output_file, mock_mode = parse_args()
    ka_name = load_ka_name(json_path)

    if not ka_name:
        print("Could not find a valid Knowledge Area in the provided JSON.")
        sys.exit(1)

    print(f"Mapping Knowledge Area: {ka_name}")

    if mock_mode:
        print("\n[MOCK MODE ENABLED] Skipping Ollama call...")
        mock_response = (
            f"CWE: 79\n"
            f"Name: Improper Neutralization of Input During"
            f"Web Page Generation ('Cross-site Scripting')\n"
            f"Reason: {ka_name} may involve topics that require"
            f"safe input/output handling to prevent injection flaws."
        )
        print(f"\nMock Result (not saved):\n{mock_response}\n")
        print("[MOCK MODE COMPLETE] No output file was modified.")
        return

    cwe_result = query_ollama(ka_name)

    print(f"\nFinal Result:\n{cwe_result}\n")

    if not cwe_result.startswith("Error:") and "No CWE mapping" not in cwe_result:
        cwe_entries = parse_cwe_result(cwe_result)
        update_output(output_file, ka_name, cwe_entries)
        print(f"Mappings saved to {output_file}")
    else:
        print("[ERROR] Mapping not saved due to Ollama error or no CWE found.")


if __name__ == "__main__":
    main()
