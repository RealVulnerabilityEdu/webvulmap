"""download_cs2023_guidelines.py."""

import os
import sys
import requests

# Define the URL of the CS2023 curriculum guideline PDF.
PDF_URL = ("https://www."
           "sci."
           "brooklyn."
           "cuny."
           "edu/"
           "~chen/"
           "downloads/"
           "research/"
           "csed/"
           "CS2023."
           "pdf")

# Define the desired filename for the downloaded PDF.
OUTPUT_FILENAME = "CS2023_Curriculum_Guidelines.pdf"

# Define the target directory where the PDF should be saved.
TARGET_DIR = os.path.join("curriculum", "cs2023")


def download_pdf(url, target_directory, output_filename):
    """
    Downloads a PDF file from a given URL to a specified directory.

    Args:
        url (str): The URL of the PDF file to download.
        target_directory (str): The directory where the PDF should be saved.
        output_filename (str): The filename for the saved PDF.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    output_full_path = os.path.join(target_directory, output_filename)

    try:
        os.makedirs(target_directory, exist_ok=True)
        print("Ensuring target directory exists: " +
              os.path.abspath(target_directory))

        print(f"Attempting to download '{url}' to "
              f"'{output_full_path}'...")

        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/91.0.4472.124 Safari/537.36")
        }
        response = requests.get(url, stream=True, headers=headers, timeout=120)

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "application/pdf" not in content_type:
            print("Warning: Expected PDF, but received content "
                  f"type: {content_type}. Still attempting to save.")

        with open(output_full_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(f"Downloaded '{output_filename}' to "
              f"'{os.path.abspath(target_directory)}' successfully.")
        return True

    except requests.exceptions.HTTPError as e:
        print("Error: Failed to download file. HTTP "
              f"Status code: {e.response.status_code}")
        print(f"Details: {e}")
        return False


def main():
    """
    Main function to initiate the PDF download process.
    """
    if download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
