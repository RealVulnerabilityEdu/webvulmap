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
        # TODO temp solution is to use int literal . Need to find a way to get max length of every unique table object
        max_length = 3

        # Pad the lists to the maximum length using a function
        def pad_list(lst):
            return lst + [''] * (max_length - len(lst))

        # Pad all lists
        # self.knowledgeArea = ([self.knowledgeArea])
        # self.knowledgeTopic = ([self.knowledgeTopic])
        # self.CWE = ([self.CWE])
        # self.CWEID = ([self.CWEID])
        self.sourceURLcwe = ([self.sourceURLcwe])
        self.cve = pad_list(self.cve)
        self.cveID = pad_list(self.cveID)
        self.sourceURLcve = pad_list(self.sourceURLcve)

        for i in range(max_length):
            cve_links = ''.join([f'<a href="{url}" target="_blank">Link</a> ' for url in self.sourceURLcve[i]])

        # Create an HTML table with the padded data and "Link" alias for URLs
            table_html = f"""
                <table class="custom-table">
                    <tr>
                        <th>knowledgeArea</th>
                        <th>Ex: Language</th>
                        <th>CWE Description</th>
                        <th>CWE num</th>
                        <th>URL cwe</th>
                        <th>cve Description</th>
                        <th>cve num</th>
                        <th>URL cve</th>
                    </tr>
                    <tr>
                        <td>{self.knowledgeArea}</td>
                        <td>{self.knowledgeTopic}</td>
                        <td>{self.CWE}</td>
                        <td>{self.CWEID}</td>
                        <td><a href="{quote(self.sourceURLcwe[0])}" target="_blank">Link</a></td>
                        <td style="min-width: 150px;">{self.cve[i]}</td>
                        <td style="min-width: 150px;">{self.cveID[i]}</td>
                        <td>{cve_links}</td>
                    </tr>
                </table>
            """

            # Custom CSS for styling the table
            custom_css = """
                <style>
                    .custom-table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                    }
                    .custom-table th, .custom-table td {
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 8px;
                    }
                    .custom-table th {
                        background-color: #f2f2f2;
                    }
                </style>
            """

            # Apply the custom CSS and display the HTML table
            st.markdown(custom_css + table_html, unsafe_allow_html=True)
