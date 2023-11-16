import os
import streamlit as st
import pandas as pd
from Table import Table

#page title
st.set_page_config(
    page_title="Pathway Page"
    )

# large title text
st.write("""# Prototype 1 Roadmap Page""")

# Array of Tables
tables = []

# read 2 csv files
colNames = ['TopicID', 'Topic Name', 'SubTopic Name', 'Weakness Name' ,'CWE ID', 'Source URL']
df = pd.read_csv('../data/my_data.csv', engine="python" , names = colNames ,header=None, delimiter=',')
colNames2 = ['Software vulnerability name (CVE name)', 'CVE ID', 'Source URL', 'CWE ID']
df2 = pd.read_csv('../data/my_data2.csv', engine="python" , names = colNames2 ,header=None, delimiter=',')

# Table object has these parameters: knowledgeArea, knowledgeTopic, CWE des, CWEID, sourceURLcwe, cve des, cveID, sourceURLcve
# traverse through the first csv file and add the values that matches the knowledgeArea, knowledgeTopic, CWE des, CWEID, sourceURLcwe
# for index, row in df.iterrows():
#     knowledgeArea = row['Topic Name']
#     knowledgeTopic = row['SubTopic Name']
#     CWE = row['Weakness Name']
#     CWEID = row['CWE ID']
#     sourceURLcwe = row['Source URL']
#     cve = ""
#     cveID = ""
#     sourceURLcve = ""

# traverse through the first csv file and add the values that match
for index, row in df.iterrows():
    knowledgeArea = row['Topic Name']
    knowledgeTopic = row['SubTopic Name']
    CWE = row['Weakness Name']
    CWEID = row['CWE ID']
    sourceURLcwe = row['Source URL']
    
    cve = []  # Initialize as a list
    cveID = []  # Initialize as a list
    sourceURLcve = []  # Initialize as a list

    # traverse through the second csv file and add the values that match
    for index2, row2 in df2.iterrows():
        # if the CWEID mathces the CVE's CWEID located in last row 'CWE ID', add the values to the cve array
        # ignore case sensitivity and strip the whitespace
        if str(row2['CWE ID']).strip().lower() == str(CWEID).strip().lower():
            cve.append(row2['Software vulnerability name (CVE name)'])
            cveID.append(row2['CVE ID'])
            sourceURLcve.append(row2['Source URL'])

        

    # add the table to the array of tables
    tables.append(Table(knowledgeArea, knowledgeTopic, CWE, CWEID, sourceURLcwe, cve, cveID, sourceURLcve))

# Display tables
for table in tables:
    table.make_custom_table()