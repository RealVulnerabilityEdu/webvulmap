import os

import pandas as pd
import streamlit as st
from loguru import logger

# from model.topics import Topics
from utils.cmdl_utils import get_run_settings


def load_data(cve_cwe_file, cwe_list_file, topic_to_cwe_file):
    cve_cwe_df = pd.read_csv(cve_cwe_file)
    cwe_list_df = pd.read_csv(cwe_list_file)
    topic_cwe_df = pd.read_csv(topic_to_cwe_file)
    return cve_cwe_df, cwe_list_df, topic_cwe_df


def retrieve_topics_by_cwe(cwe_id, topic_cwe_df):
    topic_cwe_df = topic_cwe_df[topic_cwe_df["CWE"].str.contains(cwe_id)]
    return topic_cwe_df


def display_mapped_cves(cve_record, cwe_list_df, topic_cwe_df):
    cwes = [cwe.strip().upper() for cwe in cve_record["CWE ID"].split(",")]
    topic_df_list = []
    for cwe in cwes:
        topic_df = retrieve_topics_by_cwe(cwe, topic_cwe_df)
        topic_df_list.append(topic_df)
    logger.debug("topic_df_list: {}".format(topic_df_list))
    cve_topic_df = pd.concat(topic_df_list).reset_index(
        drop=True, inplace=False
    )
    if not cve_topic_df.empty:
        st.table(cve_topic_df)
    else:
        st.write(
            pd.DataFrame(
                ["CS Topic mapping: work in progress"], columns=["Status"]
            )
        )
    ref_cwe_df = cwe_list_df[cwe_list_df["ID"].isin(cwes)].reset_index(
        drop=True, inplace=False
    )
    if not ref_cwe_df.empty:
        st.table(ref_cwe_df)
    else:
        st.write(
            pd.DataFrame(
                ["CWE mapping: work in progress"], columns=["Status"]
            )
        )


def main():
    logger.debug(
        "running script " + __file__ + " off working directory " + os.getcwd()
    )

    app_settings = get_run_settings("Secure Software Dev Web App")
    st.set_page_config(page_title="CVE and CWE")  # Set the page title

    # large title text
    st.write("""# Map CVE to CS Topics and CWEs""")

    cve_cwe_df, cwe_list_df, topic_cwe_df = load_data(
        app_settings.cve_cwe_file,
        app_settings.cwe_list_file,
        app_settings.topic_to_cwe_file,
    )

    # display the list of software vulnerabilities as clickable elements with
    # toggles
    for index, row in cve_cwe_df.iterrows():
        cve_id = row["CVE ID"]
        button_label = "CVE ID: {}".format(cve_id)
        button_key = "button_{}".format(index)
        cve_checkbox = st.checkbox(button_label, key=button_key)
        if cve_checkbox:
            display_mapped_cves(row, cwe_list_df, topic_cwe_df)


if __name__ == "__main__":
    main()