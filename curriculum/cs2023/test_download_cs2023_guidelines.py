"""Test test_download_cs2023_guidelines.py."""

import os
import shutil  # For cleaning up test directories
import sys
import unittest
from io import StringIO  # To capture print output
from unittest.mock import (
    mock_open,
    patch,
)

import requests
import requests_mock  # For mocking HTTP requests

# Import the function and constants to be tested from the main script.
from download_cs2023_guidelines import (
    OUTPUT_FILENAME,
    PDF_URL,
    TARGET_DIR,
    download_pdf,
)

# Explicitly add the 'cs2023_downloader' directory to Python's path.
module_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "cs2023_downloader"
)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


class TestDownloadPDF(unittest.TestCase):
    """
    Integration-style unit tests for the download_pdf function.
    Uses requests_mock for HTTP requests and real file system operations
    within a temporary directory for robustness.
    """

    @classmethod
    def setUpClass(cls):
        # Apply requests_mock to the entire test class once
        cls.mocker = requests_mock.Mocker()
        cls.mocker.start()

    @classmethod
    def tearDownClass(cls):
        # Stop requests_mock after all tests in the class are done
        cls.mocker.stop()

    def setUp(self):
        """
        Set up for each test:
        - Create a temporary working directory to simulate repository root.
        - Define paths relative to this temporary root.
        - Capture sys.stdout to check print statements.
        """
        self.original_cwd = os.getcwd()
        self.test_root_dir = "temp_repo_root"

        # Ensure temp_repo_root is clean before creating
        if os.path.exists(self.test_root_dir):
            shutil.rmtree(self.test_root_dir)

        os.makedirs(self.test_root_dir)
        os.chdir(self.test_root_dir)

        self.temp_target_abs_path = os.path.abspath(TARGET_DIR)
        self.temp_output_filepath_abs_path = os.path.join(
            self.temp_target_abs_path, OUTPUT_FILENAME
        )

        self.mocker.reset()

        # Capture print output
        self._stdout_capture = StringIO()
        sys.stdout = self._stdout_capture

    def tearDown(self):
        """
        Clean up after each test:
        - Restore original sys.stdout.
        - Change back to the original working directory.
        - Remove the temporary root directory and all its contents.
        """
        sys.stdout = sys.__stdout__
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_root_dir):
            shutil.rmtree(self.test_root_dir)

    def get_captured_output(self):
        """Helper to get captured print output."""
        return self._stdout_capture.getvalue()

    def test_successful_download(self):
        """
        Test case for a successful PDF download.
        Verifies directory creation, file content, and success messages.
        """
        mock_content = (
            b"%PDF-1.4\n% Sample PDF content for successful download.\n%%EOF"
        )
        self.mocker.get(
            PDF_URL,
            content=mock_content,
            headers={"Content-Type": "application/pdf"},
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertTrue(result)

        self.assertTrue(os.path.exists(self.temp_output_filepath_abs_path))
        with open(self.temp_output_filepath_abs_path, "rb") as f:
            self.assertEqual(f.read(), mock_content)

        output = self.get_captured_output()
        self.assertIn(
            f"Ensuring target directory exists: {self.temp_target_abs_path}",
            output,
        )
        self.assertIn(
            f"Attempting to download '{PDF_URL}' to "
            f"'{os.path.join(TARGET_DIR, OUTPUT_FILENAME)}'...",
            output,
        )
        self.assertIn(
            f"Downloaded '{OUTPUT_FILENAME}' to "
            f"'{self.temp_target_abs_path}' successfully.",
            output,
        )
        print("\nTest 'successful_download': Passed.")

    def test_404_not_found(self):
        """
        Test case for handling a 404 Not Found HTTP error.
        Verifies no file created and correct error message.
        """
        self.mocker.get(PDF_URL, status_code=404, reason="Not Found")

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.temp_output_filepath_abs_path))

        output = self.get_captured_output()
        self.assertIn(
            "Error: Failed to download file. HTTP Status code: 404", output
        )
        self.assertIn(
            f"Details: 404 Client Error: Not Found for url: {PDF_URL}\n",
            output,
        )
        print("\nTest '404_not_found': Passed.")

    def test_connection_error(self):
        """
        Test case for handling a network connection error.
        """
        self.mocker.get(
            PDF_URL,
            exc=requests.exceptions.ConnectionError("Mock Connection Error"),
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.temp_output_filepath_abs_path))

        output = self.get_captured_output()
        self.assertIn(
            "Error: Could not connect to the download URL. Please check your "
            "internet connection or the URL.",
            output,
        )
        self.assertIn(
            "Details: Mock Connection Error\n", output
        )
        print("\nTest 'connection_error': Passed.")

    def test_timeout_error(self):
        """
        Test case for handling a request timeout error.
        """
        self.mocker.get(
            PDF_URL, exc=requests.exceptions.Timeout("Mock Timeout Error")
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.temp_output_filepath_abs_path))

        output = self.get_captured_output()
        self.assertIn("Error: The request timed out.", output)
        self.assertIn("Details: Mock Timeout Error\n", output)
        print("\nTest 'timeout_error': Passed.")

    @patch("builtins.open", new_callable=mock_open)
    def test_file_write_permission_denied(self, mock_file_open):
        """
        Test case for handling file write permission errors (IOError).
        Mocks a successful HTTP response but simulates a permission
        denied error when trying to write to disk.
        """
        mock_content = b"PDF content."
        self.mocker.get(
            PDF_URL,
            content=mock_content,
            headers={"Content-Type": "application/pdf"},
        )

        mock_file_open.side_effect = IOError(
            13,
            "Permission denied: Mock Error"
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.temp_output_filepath_abs_path))

        output = self.get_captured_output()
        self.assertIn(
            f"Error: Could not write file to disk "
            f"'{os.path.join(TARGET_DIR, OUTPUT_FILENAME)}'. "
            f"Check permissions or disk space.",
            output,
        )
        self.assertIn(
            "Details: [Errno 13] Permission denied",
            output,
        )
        self.assertIn(
            "Mock Error\n",
            output,
        )
        mock_file_open.assert_called_once_with(
            os.path.join(TARGET_DIR, OUTPUT_FILENAME),
            "wb"
        )
        print("\nTest 'file_write_permission_denied': Passed.")

    def test_non_pdf_content_type_warning(self):
        """
        Test case where the URL returns content but with a non-PDF
        Content-Type.The program should download and warn, but still
        return True.
        """
        mock_content = (
            b"<html><body><h1>This is HTML, not PDF</h1></body></html>"
        )
        mock_content_type = "text/html"
        self.mocker.get(
            PDF_URL,
            content=mock_content,
            headers={"Content-Type": mock_content_type},
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_output_filepath_abs_path))
        with open(self.temp_output_filepath_abs_path, "rb") as f:
            self.assertEqual(f.read(), mock_content)

        output = self.get_captured_output()
        self.assertIn(
            f"Warning: Expected PDF, but received content type: "
            f"{mock_content_type}. Still attempting to save.\n",
            output,
        )
        print("\nTest 'non_pdf_content_type_warning': Passed.")

    @patch("os.makedirs", side_effect=IOError("Mock directory creation error"))
    def test_directory_creation_failure(self, mock_makedirs):
        """
        Test case for when directory creation fails
        (e.g., due to permissions in parent).
        The requests.get call will still occur, but the
        subsequent os.makedirs will fail.
        """
        mock_content = b"PDF content."
        self.mocker.get(
            PDF_URL,
            content=mock_content,
            headers={"Content-Type": "application/pdf"},
        )

        result = download_pdf(PDF_URL, TARGET_DIR, OUTPUT_FILENAME)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.temp_output_filepath_abs_path))

        output = self.get_captured_output()
        self.assertIn(
            f"Error: Could not write file to disk "
            f"'{os.path.join(TARGET_DIR, OUTPUT_FILENAME)}'. "
            f"Check permissions or disk space.",
            output,
        )
        self.assertIn(
            "Details: Mock directory creation error\n",
            output,
        )
        mock_makedirs.assert_called_once_with(
            TARGET_DIR,
            exist_ok=True
        )
        print("\nTest 'directory_creation_failure': Passed.")

# To run these tests:
# 1. Ensure the main program 'download_cs2023_guidelines.py' is
#    in 'cs2023_downloader/' and this test file
#   'test_download_cs2023_guidelines.py'
#    is also in 'webvulmap' root.
# 2. Ensure you have 'requests' and 'requests-mock' installed.
#    pip install requests requests-mock
# 3. Navigate to your 'webvulmap' root directory in the terminal.
# 4. Run the tests using the Python unittest module:
#    python3 -m unittest test_download_cs2023_guidelines.py


if __name__ == "__main__":
    unittest.main()
