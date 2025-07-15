import os
import json
from pdfminer.high_level import extract_text
from pathlib import Path

# Define paths
INPUT_FILE = "curriculum/cs2023/input/knowledge_areas.json"
PDF_FILE = "curriculum/cs2023/CS2023_Curriculum_Guidelines.pdf"
OUTPUT_DIR = "curriculum/cs2023/test_dir"

def extract_knowledge_areas():
    # Load knowledge area metadata
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        knowledge_areas = json.load(f)

    # Make sure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for ka in knowledge_areas:
        short_code = ka["short_code"]
        start_page = ka["start_page"] - 1  # pdfminer is 0-indexed
        end_page = ka["end_page"]

        print(f"Extracting {short_code} from pages {start_page+1} to {end_page}...")

        try:
            text = extract_text(PDF_FILE, page_numbers=range(start_page, end_page))
        except Exception as e:
            print(f"Error extracting {short_code}: {e}")
            continue

        output_file = os.path.join(OUTPUT_DIR, f"{short_code}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved to {output_file}")

if __name__ == "__main__":
    extract_knowledge_areas()
