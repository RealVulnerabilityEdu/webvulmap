import os
import json
from pathlib import Path
from pdfminer.high_level import extract_text
import sys

# === File and Directory Constants ===

# Input JSON file containing metadata about each knowledge area (KA)
INPUT_FILE = os.path.join("curriculum", "cs2023", "input", "knowledge_areas.json")

# PDF file to extract text from
PDF_FILE = os.path.join("curriculum", "cs2023", "CS2023_Curriculum_Guidelines.pdf")

# Directory where extracted text files will be saved
OUTPUT_DIR = os.path.join("curriculum", "cs2023", "test_dir")


def extract_knowledge_areas(input_file, pdf_file, output_dir):
    """
    Extracts text for each knowledge area (KA) defined in the input JSON file,
    and saves each one as a separate .txt file in the specified output directory.

    Args:
        input_file (str): Path to the JSON file describing knowledge areas.
        pdf_file (str): Path to the CS2023 Curriculum PDF.
        output_dir (str): Directory where extracted .txt files will be saved.

    Returns:
        bool: True if extraction completed successfully, False otherwise.
    """
    try:
        # Load JSON metadata containing short-ka, long-ka, begin-page, end-page
        with open(input_file, "r", encoding="utf-8") as f:
            knowledge_areas = json.load(f)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        print(f"Ensuring output directory exists: {os.path.abspath(output_dir)}")

        # Iterate over each knowledge area and extract the corresponding text
        for ka in knowledge_areas:
            short_code = ka["short-ka"]
            start_page = ka["begin-page"] - 1  # pdfminer is 0-indexed
            end_page = ka["end-page"]

            print(f"Extracting {short_code} from pages {start_page + 1} to {end_page}...")

            try:
                # Extract text from the specified page range
                text = extract_text(pdf_file, page_numbers=range(start_page, end_page))
            except Exception as e:
                # Log and skip if extraction fails for a specific KA
                print(f"Error extracting {short_code}: {e}")
                continue

            # Save the extracted text to a separate .txt file
            long_name = ka["long-ka"].replace(" ", "_")
            output_file = os.path.join(output_dir, f"{short_code}_{long_name}.txt")

            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(text)

            print(f"Saved to {os.path.abspath(output_file)}")

        return True

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        return False
    except json.JSONDecodeError as e:
        print("Error: Failed to decode the JSON input file.")
        print(f"Details: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")
        return False


def main():
    """
    Main function to initiate the knowledge area text extraction process.
    """
    if extract_knowledge_areas(INPUT_FILE, PDF_FILE, OUTPUT_DIR):
        sys.exit(0)  # Exit with success code
    else:
        sys.exit(1)  # # Exit with failure code 


if __name__ == "__main__":
    main()
