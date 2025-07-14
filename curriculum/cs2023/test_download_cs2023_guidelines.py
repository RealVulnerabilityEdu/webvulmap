import unittest
from unittest.mock import patch, MagicMock
import requests
from download_cs2023_guidelines import download_pdf

class TestDownloadPDF(unittest.TestCase):
    @patch("download_cs2023_guidelines.requests.get")
    def test_download_pdf_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"PDFDATA"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response  # <-- Fix here

        result = download_pdf("http://example.com/file.pdf", "test_dir", "test.pdf")
        self.assertTrue(result)

    @patch("download_cs2023_guidelines.requests.get")
    def test_download_pdf_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response  # <-- Fix here

        result = download_pdf("http://example.com/file.pdf", "test_dir", "test.pdf")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()