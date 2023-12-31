import os
from st_pages import Page, show_pages
from pages.cwe import main

show_pages(
    [
        Page(os.path.join(os.path.dirname(__file__), "pages", "cwe.py"), "CS Topics to CWE", ":books:"),
        Page(os.path.join(os.path.dirname(__file__), "pages", "cve.py"), "CVE to CWE", ":books:"),
        Page(os.path.join(os.path.dirname(__file__), "pages", "filter.py"), "Search", ":books:"),
    ]
)

main()
