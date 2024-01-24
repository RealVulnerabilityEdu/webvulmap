import os

import pandas as pd
import streamlit as st
from loguru import logger

from utils.cmdl_utils import get_run_settings
from view.table import Table


# Assuming Table is defined in a separate file
# Function to read CSV files
# def read_csv_files(topic_cwe_file, cve_cwe_file):
#     col_names = [
#         "TopicID",
#         "Topic Name",
#         "SubTopic Name",
#         "Weakness Name",
#         "CWE ID",
#         "Source URL",
#     ]
#     df1 = pd.read_csv(
#         topic_cwe_file, engine="python", names=col_names, header=None, delimiter=","
#     )

#     col_names2 = [
#         "Software vulnerability name (CVE name)",
#         "CVE ID",
#         "Source URL",
#         "CWE ID",
#     ]
#     df2 = pd.read_csv(
#         cve_cwe_file, engine="python", names=col_names2, header=None, delimiter=","
#     )

#     return df1, df2

def load_data(cve_cwe_file, cwe_list_file, topic_to_cwe_file):
    cve_cwe_df = pd.read_csv(cve_cwe_file)
    cwe_list_df = pd.read_csv(cwe_list_file)
    topic_cwe_df = pd.read_csv(topic_to_cwe_file)
    return cve_cwe_df, cwe_list_df, topic_cwe_df


# Function to create tables
def create_tables(cve_cwe_df, cwe_list_df, topic_to_cwe_df):
    tables = []

    for _, row in topic_to_cwe_df.iterrows():
        ka = row["KA"]
        knowledge_area = row["Knowledge Area"]
        knowledge_unit = row["Knowledge Unit"]
        knowledge_topic = row["Topic"]
        knowledge_subtopic = row["Subtopic"]

        for cwe_id in [cwe.strip().upper() for cwe in row["CWE"].split(",")]:
            cwe_df = cwe_list_df[cwe_list_df['ID'] == cwe_id]
            cve_df = cve_cwe_df[cve_cwe_df['CWE ID'] == cwe_id]
            for _, cve_row in cve_df.iterrows():
                tables.append(
                    Table(
                        ka,
                        knowledge_area,
                        knowledge_unit,
                        knowledge_topic,
                        knowledge_subtopic,
                        cwe_df['ID'],
                        cwe_df['Title'],
                        cwe_df['URL'],
                        cve_row['CVE ID'],
                        cve_row['NVD URL']
                    )
                )

    return tables

def main():
    logger.debug("running script " + __file__ + " off working directory " + os.getcwd())

    app_settings = get_run_settings("Secure Software Dev Web App")
    st.set_page_config(page_title="Pathway Page")
    st.write("""# Search the Mapping""")

    cve_cwe_df, cwe_list_df, topic_cwe_df = load_data(app_settings.cve_cwe_file, app_settings.cwe_list_file, app_settings.topic_to_cwe_file)

    tables = create_tables(cve_cwe_df, cwe_list_df, topic_cwe_df)
    filtered_tables = tables

    filter_ka = st.multiselect(
        "Filter by Knowledge Area",
        [knowledge_area for knowledge_area in topic_cwe_df["Knowledge Area"].unique()],
        default=[],
        key=1,
    )

    mapped_cwe_list = []
    for topic_cwe in topic_cwe_df['CWE']:
        mapped_cwe_list.extend([cwe.strip().upper() for cwe in topic_cwe.split(',')])
    mapped_cwe_set = set(mapped_cwe_list)
    filter_cwe_id = st.multiselect(
        "Filter by CWE-ID",
        [ cwe_id for cwe_id in mapped_cwe_set],
        default=[],
        key=2,
    )



    mapped_cve_list = cve_cwe_df['CVE ID'].tolist()
    filter_cve_id = st.multiselect(
        "Filter by CVE-ID",
        [ cve_id for cve_id in mapped_cve_list],
        default=[],
        key=3,
    )


    filter_topic_kw = st.text_input("Filter by Keywords in Topic or Subtopic", "", key=4).lower()

    if filter_ka:
        filtered_tables = [
            table for table in filtered_tables if table.knowledgeArea in filter_ka
        ]

    if filter_cwe_id:
        filtered_tables = [
            table for table in filtered_tables if table.cwe_id.isin(filter_cwe_id).all()
        ]

    if filter_cve_id:
        filtered_tables = [
            table for table in filtered_tables if table.cve_id in filter_cve_id
        ]

    if filter_topic_kw:
        filtered_tables = [
            table
            for table in filtered_tables
            if filter_topic_kw in table.knowledgeTopic.lower() or filter_topic_kw in table.knowledgeSubtopic.lower()
        ]


    for table in filtered_tables:
        table.make_custom_table()


if __name__ == "__main__":
    main()
