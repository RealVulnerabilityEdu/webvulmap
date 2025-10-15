"""USe zero-shot + LangChain + Ollama on 2023 CS Curriculum"""

import sys
import json
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM

# Read in KA name from JSON file
def load_ka_name(json_path):
    """Load the Knowledge Area name from the JSON input."""
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get("knowledge_area", {}).get("name", None)

def query_ollama(ka_name, model_name="mistral"):    # 'mistral' can be replaced with other models
    """Use Ollama with two fallback prompts to map KA to CWE(s)."""
    llm = OllamaLLM(model=model_name)

    primary_prompt = (
        f"What ONE cwe is most relevant to the computer science topic {ka_name}?\n"
        f"Format strictly as:\n"
        f"CWE-ID CWE Name\nReason\n"
    )
    fallback_prompt = (
        f"Which potential cwes can be relevant to the topic {ka_name}? Give me 3-5 cwes.\n"
        f"Format strictly as:\n"
        f"CWE-ID CWE Name\nReason\n"
    )

    print(f"\nAsking primary prompt:\n{primary_prompt}\n")
    primary_response = llm.invoke(primary_prompt).strip()   # Get model response

    # Look for 'CWE' in response
    if "CWE-" in primary_response:
        print("CWE mapping (from primary prompt):")
        return primary_response

    print("\nNo direct CWE found in primary response. Trying fallback...\n")    
    print(f"Asking fallback prompt:\n{fallback_prompt}\n")      # Fallback prompt if no response to primary
    fallback_response = llm.invoke(fallback_prompt).strip()

    # Look far 'CWE' in fallback prompt response
    if "CWE-" in fallback_response:
        print("CWE mapping (from fallback prompt):")
        return fallback_response

    return "No CWE mapping could be determined from either prompt."     # If no valid reponse from either prompt

def main():
    if len(sys.argv) != 2:
        print("Usage: python cs2023_zero_shot.py <your_input_file.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    ka_name = load_ka_name(json_path)

    if not ka_name:
        print("Could not find a valid Knowledge Area in the provided JSON.")    # If KA not found
        sys.exit(1)

    print(f"Mapping Knowledge Area: {ka_name}")
    cwe_result = query_ollama(ka_name)
    print(f"\nFinal Result:\n{cwe_result}\n")

if __name__ == "__main__":
    main()
