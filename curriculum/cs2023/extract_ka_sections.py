"""Extract text by knowledge area from a CS2023 curriculum PDF."""

import argparse
import json
import os
import sys

import fitz  # PyMuPDF


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

        # Open the PDF file using PyMuPDF
        doc = fitz.open(pdf_file)

        # Iterate over each knowledge area and extract the corresponding text
        for ka in knowledge_areas:
            short_code = ka["short-ka"]
            long_name = ka["long-ka"]
            start_page = ka["begin-page"] - 1  # PyMuPDF is 0-indexed
            end_page = ka["end-page"]

            print(
                f"Extracting {short_code} from pages {start_page + 1} to {end_page}..."
            )

            if start_page < 0 or end_page > len(doc) or start_page >= end_page:
                print(f"Warning: Skipping {short_code} due to invalid page range.")
                continue

            try:
                # Extract text from the specified page range
                text = ""
                for page_num in range(start_page, end_page):
                    text += doc[page_num].get_text()
            except (fitz.fitz.FileDataError, OSError) as e:
                # Log and skip if extraction fails for a specific KA
                print(f"Error extracting {short_code}: {e}")
                continue

            # Save the extracted text to a separate .txt file
            safe_short_code = (
                short_code.replace(" ", "_")
                .replace("/", "-")
                .replace(":", "_")
                .replace("&", "and")
                .replace("(", "")
                .replace(")", "")
            )
            safe_long_name = (
                long_name.replace(" ", "_")
                .replace("/", "-")
                .replace(":", "_")
                .replace("&", "and")
                .replace("–", "-")
                .replace("(", "")
                .replace(")", "")
            )
            output_file = os.path.join(
                output_dir, f"{safe_short_code}_{safe_long_name}.txt"
            )

            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(text.strip())

            print(f"Saved to {os.path.abspath(output_file)}")

        doc.close()
        return True

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        return False
    except json.JSONDecodeError as e:
        print("Error: Failed to decode the JSON input file.")
        print(f"Details: {e}")
        return False
    except OSError as e:
        print(f"OS error occurred during extraction: {e}")
        return False
    except fitz.fitz.FileDataError as e:
        print(f"PyMuPDF file data error: {e}")
        return False


def main():
    """
    Main function to parse arguments and initiate the
    knowledge area text extraction process.
    """
    parser = argparse.ArgumentParser(
        description="Extract text by knowledge area from a CS2023 curriculum PDF."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the knowledge_areas.json file"
    )
    parser.add_argument(
        "--pdf", required=True, help="Path to the CS2023_Curriculum_Guidelines.pdf file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory where extracted .txt files will be saved",
    )

    args = parser.parse_args()

    if extract_knowledge_areas(args.input, args.pdf, args.output):
        sys.exit(0)  # Exit with success code
    else:
        sys.exit(1)  # Exit with failure code


if __name__ == "__main__":
    main()
