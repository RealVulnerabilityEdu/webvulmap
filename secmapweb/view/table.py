import os

import pandas as pd
import streamlit as st


class Table:
    def __init__(self, short_ka, ka, ku, kt, kst, cwe_id, cwe_title, cwe_url, cve_id, cve_url):
        self.ka = short_ka
        self.knowledgeArea = ka
        self.knowledgeUnit = ku
        self.knowledgeTopic = kt
        self.knowledgeSubtopic = kst
        self.cwe_id, self.cwe_title, self.cwe_url = cwe_id, cwe_title, cwe_url
        self.cve_id, self.cve_url = cve_id, cve_url

    def to_string(self, data_list):
        if data_list and any(data_list):
            return ", ".join(map(str, data_list))
        else:
            return ""

    # # list argument: usually a list of CVE
    def generate_links(self, url_list):
        return "".join(
            [f'<a href="{url}" target="_blank">Link</a> ' for url in url_list]
        )

    # single argument: usually a single CWE url
    def generate_link(self, string):
        string = string.replace(
            "(",
            ") ",
        )
        return f'<a href="{string}" target="_blank">Link</a>'

    # to be called in the AppPage3.py file
    def makeTable(self):
        colNames = [
            "kA",
            "knowledgeArea",
            "knowledgeUnit",
            "knowledgeTopic",
            "knowledgeSubtopic",
            "cweId",
            "cweTitle",
            "cweUrl",
            "cveId",
            "cveUrl"
        ]
        # use the colNames array to create a dataframe where the values are created based on what was passed to the constructor
        df = pd.DataFrame(columns=colNames)
        # create a table with the dataframe
        table = st.table(df)
        # return the table
        return table

    def make_custom_table(self):
        # max_length = 3

        # # Pad the lists to the maximum length using a function
        # def pad_list(lst):
        #     return lst + [""] * (max_length - len(lst))

        # self.sourceURLcve = pad_list(self.sourceURLcve)

        cwe_link = self.generate_link(self.cwe_url)
        cve_link = self.generate_link(self.cve_url)

        # Construct the correct file paths based on the folder structure
        current_folder = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(
            current_folder, "..", "templates", "table_template.html"
        )
        style_path = os.path.join(current_folder, "..", "styles", "table_styles.css")

        # Read HTML template from file
        with open(template_path, "r") as template_file:
            table_html = template_file.read()

        # Apply the values to the HTML template
        table_html = table_html.format(
            kA=self.ka,
            knowledgeArea=self.knowledgeArea,
            knowledgeUnit=self.knowledgeUnit,
            knowledgeTopic=self.knowledgeTopic,
            knowledgeSubtopic=self.knowledgeSubtopic,
            cweId=self.cwe_id,
            cweTitle=self.cwe_title,
            cweUrl=cwe_link,
            cveId=self.cve_id,
            cveUrl=cve_link,
        )

        # Read CSS styles from file
        with open(style_path, "r") as style_file:
            custom_css = style_file.read()

        # Use st.write to display HTML and CSS
        st.write(table_html, unsafe_allow_html=True)
        st.write(f"<style>{custom_css}</style>", unsafe_allow_html=True)
