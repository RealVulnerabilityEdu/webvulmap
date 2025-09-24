import os

from pages.cwe import main
from st_pages import Page, show_pages

show_pages(
    [
        Page(
            os.path.join(os.path.dirname(__file__), "pages", "cwe.py"),
            "CS Topics to CWE",
            ":books:",
        ),
        Page(
            os.path.join(os.path.dirname(__file__), "pages", "cve.py"),
            "CVE to CWE and CS Topics",
            ":books:",
        ),
        Page(
            os.path.join(os.path.dirname(__file__), "pages", "filter.py"),
            "Search",
            ":books:",
        ),
        Page(
            os.path.join(os.path.dirname(__file__), "pages", "about.py"),
            "About",
            ":question:",
        ),
    ]
)

main()
