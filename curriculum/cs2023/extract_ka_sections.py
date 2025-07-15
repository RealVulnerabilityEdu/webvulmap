import os
import json
from pdfminer.high_level import extract_text
from pathlib import Path

# === File and Directory Constants ===
INPUT_FILE = "curriculum/cs2023/input/knowledge_areas.json"  # Metadata input file
PDF_FILE = "curriculum/cs2023/CS2023_Curriculum_Guidelines.pdf"  # Source PDF to extract from
OUTPUT_DIR = "curriculum/cs2023/test_dir"  # Directory where extracted text files will be saved

def extract_knowledge_areas():
    """
    Extracts text for each knowledge area defined in the input JSON,
    and saves each one as a separate .txt file in the output directory.
    """
    
    # Load JSON metadata containing short_code, start_page, and end_page for each KA
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        knowledge_areas = json.load(f)

    # Ensure output directory exists (create if missing)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Iterate over all knowledge areas
    for ka in knowledge_areas:
        short_code = ka["short_code"]
        start_page = ka["start_page"] - 1  # pdfminer uses 0-based indexing
        end_page = ka["end_page"]

        print(f"Extracting {short_code} from pages {start_page + 1} to {end_page}...")

        try:
            # Extract text from the specified page range
            text = extract_text(PDF_FILE, page_numbers=range(start_page, end_page))
        except Exception as e:
            # Log and skip if extraction fails
            print(f"Error extracting {short_code}: {e}")
            continue

        # Save extracted text to output file
        output_file = os.path.join(OUTPUT_DIR, f"{short_code}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved to {output_file}")

if __name__ == "__main__":
    extract_knowledge_areas()
