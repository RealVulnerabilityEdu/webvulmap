import os
import streamlit as st
import pandas as pd

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
        # Find the maximum length among all lists
        # max_length = max(len(self.knowledgeArea), len(self.knowledgeTopic), len(self.CWE), len(self.CWEID),
        #                  len(self.sourceURLcwe), len(self.cve), len(self.cveID), len(self.sourceURLcve))
        # TODO temp solution is to use int literal 8. Need to find a way to get max length of every unique table object
        max_length = 3

        # Pad the lists to the maximum length using a function
        def pad_list(lst):
            return lst + [''] * (max_length - len(lst))

        # Pad all lists
        self.knowledgeArea = pad_list([self.knowledgeArea])
        self.knowledgeTopic = pad_list([self.knowledgeTopic])
        self.CWE = pad_list([self.CWE])
        self.CWEID = pad_list([self.CWEID])
        self.sourceURLcwe = pad_list([self.sourceURLcwe])
        self.cve = pad_list(self.cve)
        self.cveID = pad_list(self.cveID)
        self.sourceURLcve = pad_list(self.sourceURLcve)

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
                    <td>{self.knowledgeArea[0]}</td>
                    <td>{self.knowledgeTopic[0]}</td>
                    <td>{self.CWE[0]}</td>
                    <td>{self.CWEID[0]}</td>
                    <td><a href="{self.sourceURLcwe[0]}" target="_blank">Link</a></td>
                    <td style="min-width: 150px;">{self.cve[0]}</td>
                    <td style="min-width: 150px;">{self.cveID[0]}</td>
                    <td><a href="{self.sourceURLcve[0]}" target="_blank">Link</a></td>
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
