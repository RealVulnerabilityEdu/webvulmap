### Feature: CS2023 Curriculum Guideline PDF Downloader

**User Story:**
As a researcher or student,
I want a Python script to download the official "ACM/IEEE/AAAI Computer Science Curricula 2023" guideline PDF,
so that I can access the document offline for reference and research purposes without requiring a GUI.

---

**Scenario: Successful PDF Download to `curriculum/cs2023`**
* **Given:** The script is executed from the repository root.
* **And:** A valid URL for the "CS2023 Curriculum Guidelines" PDF is accessible and allows direct download.
* **And:** The `curriculum/cs2023` directory exists or can be created.
* **And:** The target directory `curriculum/cs2023` has write permissions.
* **When:** The program `download_cs2023_guidelines.py` is run.
* **Then:** The PDF file "CS2023_Curriculum_Guidelines.pdf" should be saved inside `curriculum/cs2023`.
* **And:** The script should output a success message, e.g., "Downloaded 'CS2023_Curriculum_Guidelines.pdf' to 'curriculum/cs2023' successfully."
* **And:** The program should exit with a status code of 0.

**Scenario: Handling Invalid URL (e.g., 404 Not Found)**
* **Given:** The script is executed from the repository root.
* **And:** The configured PDF URL leads to a 404 Not Found error (or similar HTTP client/server error).
* **When:** The program `download_cs2023_guidelines.py` is run.
* **Then:** The script should output an error message indicating the download failure and the HTTP status code, e.g., "Error: Failed to download file. HTTP Status code: 404".
* **And:** No PDF file should be created or an empty/corrupted file should not be reported as successful.
* **And:** The program should exit with a non-zero status code (e.g., 1).

**Scenario: Handling Network Connectivity Issues**
* **Given:** The script is executed from the repository root.
* **And:** There is no internet connection or the host is unreachable.
* **When:** The program `download_cs2023_guidelines.py` is run.
* **Then:** The script should output an error message related to network connectivity, e.g., "Error: Could not connect to the download URL. Please check your internet connection or the URL."
* **And:** No PDF file should be created.
* **And:** The program should exit with a non-zero status code (e.g., 1).

**Scenario: Handling File Write Permission Issues**
* **Given:** The script is executed from the repository root.
* **And:** A valid PDF URL is accessible.
* **And:** The target directory `curriculum/cs2023` exists but does *not* have write permissions.
* **When:** The program `download_cs2023_guidelines.py` is run.
* **Then:** The script should output an error message indicating a file writing problem, e.g., "Error: Could not write file to disk 'curriculum/cs2023/CS2023_Curriculum_Guidelines.pdf'. Check permissions or disk space."
* **And:** No PDF file should be created or saved.
* **And:** The program should exit with a non-zero status code (e.g., 1).

**Scenario: Handling Missing Target Directory (Program Creates It)**
* **Given:** The script is executed from the repository root.
* **And:** The `curriculum/cs2023` directory does not exist.
* **And:** The user has permissions to create directories.
* **When:** The program `download_cs2023_guidelines.py` is run.
* **Then:** The `curriculum/cs2023` directory should be created.
* **And:** The PDF file "CS2023_Curriculum_Guidelines.pdf" should be saved inside `curriculum/cs2023`.
* **And:** The script should output a success message.
* **And:** The program should exit with a status code of 0.