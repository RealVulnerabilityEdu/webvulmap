import os

import pandas as pd
import streamlit as st
from loguru import logger

# from model.topics import Topics
from utils.cmdl_utils import get_run_settings


# def load_data(cve_cwe_file):
#     col_names = [
#         "Software vulnerability name (CVE name)",
#         "CVE ID",
#         "Source URL",
#         "CWE ID",
#     ]
#     df = pd.read_csv(
#         cve_cwe_file, engine="python", names=col_names, header=None, delimiter=","
#     )
#     return df


# def process_data(df):
#     softwareV_dict = (
#         {}
#     )  # Dictionary to store Software Vulnerabilities and their CVE ID and Source URL, and CWE ID
#     topic_visibility = (
#         {}
#     )  # Dictionary to track the visibility state of each topic's subtopics

#     for _, row in df.iterrows():
#         vulnerability_name = row["Software vulnerability name (CVE name)"]
#         cve_id = row["CVE ID"]
#         source_url = row["Source URL"]
#         cwe_id = row["CWE ID"]

#         # Get the values from the CSV file
#         if vulnerability_name not in softwareV_dict:
#             softwareV_dict[vulnerability_name] = Topics(vulnerability_name)
#             topic_visibility[vulnerability_name] = False

#         # add cve id to its respective topic object (if it exists, row[1] is not empty, and if it is not already in the array)
#         if cve_id and cve_id not in softwareV_dict[vulnerability_name].getCves():
#             softwareV_dict[vulnerability_name].addCve(cve_id)

#         # add source url to its respective topic object (if it exists, row[2] is not empty, and if it is not already in the array)
#         if (
#             source_url
#             and source_url not in softwareV_dict[vulnerability_name].getCves()
#         ):
#             softwareV_dict[vulnerability_name].add_CveSource(source_url)

#         # add cwe id to its respective topic object (if it exists, row[3] is not empty, and if it is not already in the array)
#         if cwe_id and cwe_id not in softwareV_dict[vulnerability_name].getCves():
#             softwareV_dict[vulnerability_name].addCwe(cwe_id)

#     return softwareV_dict, topic_visibility


def load_data(cve_cwe_file, cwe_list_file, topic_to_cwe_file):
    cve_cwe_df = pd.read_csv(cve_cwe_file)
    cwe_list_df = pd.read_csv(cwe_list_file)
    topic_cwe_df = pd.read_csv(topic_to_cwe_file)
    return cve_cwe_df, cwe_list_df, topic_cwe_df


def retrieve_topics_by_cwe(cwe_id, topic_cwe_df):
    topic_cwe_df = topic_cwe_df[topic_cwe_df["CWE"].str.contains(cwe_id)]
    return topic_cwe_df

def display_mapped_cves(cve_record, cwe_list_df, topic_cwe_df):
    cwes = [cwe.strip().upper() for cwe in cve_record["CWE ID"].split(',')]
    topic_df_list = []
    for cwe in cwes:
        topic_df = retrieve_topics_by_cwe(cwe, topic_cwe_df)
        topic_df_list.append(topic_df)
    logger.debug("topic_df_list: {}".format(topic_df_list))
    cve_topic_df = pd.concat(topic_df_list).reset_index(drop=True, inplace=False)
    if not cve_topic_df.empty:
        st.table(cve_topic_df)
    else:
        st.write(pd.DataFrame(["CS Topic mapping: work in progress"], columns=["Status"]))
    ref_cwe_df = cwe_list_df[cwe_list_df["ID"].isin(cwes)].reset_index(drop=True, inplace=False)
    if not ref_cwe_df.empty:
        st.table(ref_cwe_df)
    else:
        st.write(pd.DataFrame(["CWE mapping: work in progress"], columns=["Status"]))


def main():
    logger.debug("running script " + __file__ + " off working directory " + os.getcwd())

    app_settings = get_run_settings("Secure Software Dev Web App")
    st.set_page_config(page_title="CVE and CWE")  # Set the page title

    # large title text
    st.write("""# Map CVE to CS Topics and CWEs""")

    cve_cwe_df, cwe_list_df, topic_cwe_df = load_data(app_settings.cve_cwe_file, app_settings.cwe_list_file, app_settings.topic_to_cwe_file)
    # softwareV_dict, topic_visibility = process_data(df)

    # display the list of software vulnerabilities as clickable elements with toggles
    for index,row in cve_cwe_df.iterrows():
        cve_id = row['CVE ID']
        button_label = "CVE ID: {}".format(cve_id)
        button_key = "button_{}".format(index)
        cve_checkbox = st.checkbox(button_label, key=button_key)
        if cve_checkbox:
            display_mapped_cves(row, cwe_list_df, topic_cwe_df)

    # for topic in softwareV_dict.values():
    #     topic_name = topic.getName()
    #     topic_visibility[topic_name] = st.checkbox(topic_name, value=False)
    #     if topic_visibility[topic_name]:
    #         st.write("CVE ID: ", topic.getCves())
    #         st.write("Source URL: ", topic.getCveSource())
    #         st.write("CWE ID: ", topic.getCwes())
    #         st.write("")


if __name__ == "__main__":
    main()
