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
        df = pd.DataFrame(columns = colNames)
        # create a table with the dataframe
        table = st.table(df)
        # return the table
        return table
    
    def make_custom_table(self):
        # Find the maximum length among all lists
        max_length = max(len(self.knowledgeArea), len(self.knowledgeTopic), len(self.CWE), len(self.CWEID),
                         len(self.sourceURLcwe), len(self.cve), len(self.cveID), len(self.sourceURLcve))

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

        # Create a DataFrame with the padded data
        data = {
            'knowledgeArea': self.knowledgeArea,
            'knowledgeTopic': self.knowledgeTopic,
            'CWE Description': self.CWE,
            'CWE num': self.CWEID,
            'sourceURLcwe': self.sourceURLcwe,
            'cve Description': self.cve,
            'cve num': self.cveID,
            'sourceURLcve': self.sourceURLcve
        }
        df = pd.DataFrame(data)

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

        # Apply the custom CSS
        st.markdown(custom_css, unsafe_allow_html=True)

        # Display the table using a div with a custom CSS class
        st.markdown('<div class="custom-table">{}</div>'.format(df.to_html(index=False, escape=False)), unsafe_allow_html=True)