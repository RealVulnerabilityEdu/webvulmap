import os
import streamlit as st
import pandas as pd
from Topics import Topics

st.set_page_config(
    page_title="Pathway Page"
    #../data/my_data.csv
    )  # Set the page title

# large title text
st.write("""# Prototype 1 CVE topics""")

# header for CSV file: Software Vulnerability name (CVE name), CVE ID, Source URL, CWE ID.
colNames = ['Software vulnerability name (CVE name)', 'CVE ID', 'Source URL', 'CWE ID']
df = pd.read_csv('../data/my_data2.csv', engine="python" , names = colNames ,header=None, delimiter=',')

topic_dict = {}  # Dictionary to store Software Vulnerabilites and their CVE ID and Source URL, and CWE ID

# Create a dictionary to track the visibility state of each topic's subtopics
topic_visibility = {}

for index, row in df.iterrows():
    vulnerability_name = row['Software vulnerability name (CVE name)']
    cve_id = row['CVE ID']
    source_url = row['Source URL']
    cwe_id = row['CWE ID']

    # Get the values from the CSV file
    if vulnerability_name not in topic_dict:
        topic_dict[vulnerability_name] = Topics(vulnerability_name)
        topic_visibility[vulnerability_name] = False
    
    # add cve id to its respective topic object (if it exists, row[1] is not empty, and if it is not already in the array)
    if cve_id and cve_id not in topic_dict[vulnerability_name].getCves():
        topic_dict[vulnerability_name].addCve(cve_id)





