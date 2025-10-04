"""download_cs2023_guidelines.py."""

import os
import sys

import requests

# Define the URL of the CS2023 curriculum guideline PDF.
# This URL points to the Version-Gamma PDF, which is the pre-release
# version of the final report,
# hosted directly on the csed.acm.org website, which might be more
# permissive to downloads.
PDF_URL = "https://www.sci.brooklyn.cuny.edu/~chen/downloads/research/csed/CS2023.pdf"

# Define the desired filename for the downloaded PDF.
OUTPUT_FILENAME = "CS2023_Curriculum_Guidelines.pdf"

# Define the target directory where the PDF should be saved, relative to
# the script's execution location (repository root).
# As per the task, this is curriculum/cs2023
TARGET_DIR = os.path.join("curriculum", "cs2023")


def download_pdf(url, target_directory, output_filename):
    """
    Downloads a PDF file from a given URL to a specified directory.

    Args:
        url (str): The URL of the PDF file to download.
        target_directory (str): The directory where the PDF should be saved.
                                This directory will be created if it doesn't exist.
        output_filename (str): The filename for the saved PDF.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    # Construct the full path for the output file
    output_full_path = os.path.join(target_directory, output_filename)

    try:
        # Ensure the target directory exists. If not, create it.
        # exist_ok=True prevents an error if the directory already exists.
        os.makedirs(target_directory, exist_ok=True)
        print(f"Ensuring target directory exists: {os.path.abspath(target_directory)}")

        print(f"Attempting to download '{url}' to '{output_full_path}'...")

        # Send an HTTP GET request to the URL.
        # Use stream=True to allow downloading large files in chunks without
        # loading the entire file into memory at once.
        # Add a User-Agent header to mimic a web browser, as some servers block
        # requests that don't appear to come from a standard browser.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, stream=True, headers=headers, timeout=120)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Check if the response content type is indeed PDF
        content_type = response.headers.get("Content-Type", "")
        if "application/pdf" not in content_type:
            print(
                f"Warning: Expected PDF, but received content "
                f"type: {content_type}. Still attempting to save."
            )

        # Open the local file in binary write mode ('wb')
        with open(output_full_path, "wb") as pdf_file:
            # Iterate over the response content in chunks and write to the file
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(
            f"Downloaded '{output_filename}' to "
            f"'{os.path.abspath(target_directory)}' successfully."
        )
        return True

    except requests.exceptions.HTTPError as e:
        print(
            f"Error: Failed to download file. HTTP "
            f"Status code: {e.response.status_code}"
        )
        print(f"Details: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print("Error: The request timed out.")
        print(f"Details: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(
            "Error: Could not connect to the download URL. "
            "Please check your internet connection or the URL."
        )
        print(f"Details: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error: An unexpected request error occurred: {e}")
        return False
    except IOError as e:
        # Handle errors related to writing the file to disk
        # (e.g., permissions, disk space)
        print(
            f"Error: Could not write file to disk '{output_full_path}'. "
            f"Check permissions or disk space."
        )
        print(f"Details: {e}")
        return False


def main():
    """
    Main function to initiate the PDF download process.
    """
    if download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME):
        sys.exit(0)  # Exit with success code
    else:
        sys.exit(1)  # Exit with failure code


if __name__ == "__main__":
    main()
