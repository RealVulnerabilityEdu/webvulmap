import os
import streamlit as st
import pandas as pd
from urllib.parse import quote

class Table:
    knowledgeArea = ""
    knowledgeTopic = ""
    CWE = ""
    CWEID = ""
    sourceURLcwe = ""
    cve = [""]
    cveID = [""]
    sourceURLcve = [""]

    def __init__(self, kA, kT, cwe, cweID, sourceURLcwe, cve, cveID, sourceURLcve):
        self.knowledgeArea = kA
        self.knowledgeTopic = kT
        self.CWE = cwe
        self.CWEID = cweID
        self.sourceURLcwe = sourceURLcwe
        self.cve = [cve] if cve else []  # Convert to a list if not empty, otherwise, keep it as an empty list
        self.cveID = [cveID] if cveID else []  # Convert to a list if not empty, otherwise, keep it as an empty list
        self.sourceURLcve = [sourceURLcve] if sourceURLcve else []  # Convert to a list if not empty, otherwise, keep it as an empty list  

    def to_string(self, data_list):
        if data_list and any(data_list):
            return ', '.join(map(str, data_list))
        else:
            return ''     
    # list argument: usually a list of CVE
    def generate_links(self, url_list):
        return ''.join([f'<a href="{url}" target="_blank">Link</a> ' for url in url_list])
    
    # single argument: usually a single CWE url
    def generate_link(self, string):
        string = string.replace("(" , ") ", )
        return f'<a href="{string}" target="_blank">Link</a>'

    # to be called in the AppPage3.py file
    def makeTable(self):
        colNames = ['knowledgeArea', 'knowledgeTopic', 'CWE Description', 'CWE num', 'sourceURLcwe'
                    , 'cve Description', 'cve num', 'sourceURLcve']
        # use the colNames array to create a dataframe where the values are created based on what was passed to the constructor
        df = pd.DataFrame(columns=colNames)
        # create a table with the dataframe
        table = st.table(df)
        # return the table
        return table  

    def make_custom_table(self):
        max_length = 3

        # Pad the lists to the maximum length using a function
        def pad_list(lst):
            return lst + [''] * (max_length - len(lst))

        self.sourceURLcve = pad_list(self.sourceURLcve)

        cwe_link = self.generate_link(self.sourceURLcwe)
        cve_links = self.generate_links(self.sourceURLcve[0])

        # Construct the correct file paths based on the folder structure
        current_folder = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_folder, "templates", "table_template.html")
        style_path = os.path.join(current_folder, "styles", "table_styles.css")

        # Read HTML template from file
        with open(template_path, "r") as template_file:
            table_html = template_file.read()

        # Apply the values to the HTML template
        table_html = table_html.format(
            knowledgeArea=self.knowledgeArea,
            knowledgeTopic=self.knowledgeTopic,
            CWE=self.CWE,
            CWEID=self.CWEID,
            cwe_link=cwe_link,
            cve=self.to_string(self.cve),
            cveID=self.to_string(self.cveID),
            cve_links=cve_links
        )

        # Read CSS styles from file
        with open(style_path, "r") as style_file:
            custom_css = style_file.read()

        # Use st.write to display HTML and CSS
        st.write(table_html, unsafe_allow_html=True)
        st.write(f'<style>{custom_css}</style>', unsafe_allow_html=True)
