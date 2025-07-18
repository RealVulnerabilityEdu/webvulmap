# CS 2023 JSONizer

This is a Python application that jsonizes ACM/IEEE/AAAI 2023 curriculum guideline.

# CS2023 Knowledge Area Extractor

This module provides scripts to extract individual Knowledge Area (KA) text sections from the official **CS2023 Curriculum Guidelines PDF**.

Each KA is defined by its page range and name in a JSON input file. The script will extract the text from the corresponding PDF pages and save it as separate `.txt` files.

---

## Project Structure
curriculum/cs2023/
├── input/
│ └── knowledge_areas.json # Metadata describing each KA
├── test_dir/ # Output directory for extracted text files
├── CS2023_Curriculum_Guidelines.pdf # The source PDF
├── extract_ka_sections.py # Main extraction script (PyMuPDF-based)
├── download_cs2023_guidelines.py # Script to download the official PDF
└── cs2023_guidelines.feature # Feature file with expected behavior


---

## How to Run

Install PyMuPDF if not already installed:

```bash
pip install pymupdf
```
Then run the script:

python curriculum/cs2023/extract_ka_sections.py \
  --input curriculum/cs2023/input/knowledge_areas.json \
  --pdf curriculum/cs2023/CS2023_Curriculum_Guidelines.pdf \
  --output curriculum/cs2023/test_dir/

--- 

Notes

--The PDF must be text-based, not scanned or image-based.

--Filenames are sanitized to remove problematic characters like :, &, –, and ().

--Page numbers in knowledge_areas.json are 1-indexed but internally adjusted for zero-based indexing.

--Output .txt files are saved to the path provided by --output.