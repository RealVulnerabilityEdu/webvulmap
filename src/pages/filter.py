import streamlit as st
import pandas as pd
from table import Table
from utils.cmdl_utils import get_run_settings


# Assuming Table is defined in a separate file
# Function to read CSV files
def read_csv_files(topic_cwe_file, cve_cwe_file):
    col_names = [
        "TopicID",
        "Topic Name",
        "SubTopic Name",
        "Weakness Name",
        "CWE ID",
        "Source URL",
    ]
    df1 = pd.read_csv(
        topic_cwe_file, engine="python", names=col_names, header=None, delimiter=","
    )

    col_names2 = [
        "Software vulnerability name (CVE name)",
        "CVE ID",
        "Source URL",
        "CWE ID",
    ]
    df2 = pd.read_csv(
        cve_cwe_file, engine="python", names=col_names2, header=None, delimiter=","
    )

    return df1, df2


# Function to create tables
def create_tables(df1, df2):
    tables = []

    for _, row in df1.iterrows():
        knowledge_area = row["Topic Name"]
        knowledge_topic = row["SubTopic Name"]
        cwe = row["Weakness Name"]
        cwe_id = row["CWE ID"]
        source_url_cwe = row["Source URL"]

        cve = df2[df2["CWE ID"].str.strip().str.lower() == cwe_id.strip().lower()]

        tables.append(
            Table(
                knowledge_area,
                knowledge_topic,
                cwe,
                cwe_id,
                source_url_cwe,
                cve["Software vulnerability name (CVE name)"].tolist(),
                cve["CVE ID"].tolist(),
                cve["Source URL"].tolist(),
            )
        )

    return tables


def main():
    app_settings = get_run_settings("Secure Software Dev Web App")
    st.set_page_config(page_title="Pathway Page")
    st.write("""# Page: Table of contents""")

    df1, df2 = read_csv_files(app_settings.topic_to_cwe_file, app_settings.cve_cwe_file)
    tables = create_tables(df1, df2)

    filtered_tables = tables

    filter_keywords = st.multiselect(
        "Filter by keywords",
        [knowledge_area for knowledge_area in df1["Topic Name"].unique()],
        default=[],
    )
    filter_topic = st.text_input("Filter by Language", "").lower()

    if filter_topic:
        filtered_tables = [
            table
            for table in filtered_tables
            if filter_topic in table.knowledgeTopic.lower()
        ]

    if filter_keywords:
        filtered_tables = [
            table for table in filtered_tables if table.knowledgeArea in filter_keywords
        ]

    for table in filtered_tables:
        table.make_custom_table()


if __name__ == "__main__":
    main()
