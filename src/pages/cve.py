import os

import pandas as pd
import streamlit as st
from loguru import logger

from model.topics import Topics
from utils.cmdl_utils import get_run_settings


def load_data(cve_cwe_file):
    col_names = [
        "Software vulnerability name (CVE name)",
        "CVE ID",
        "Source URL",
        "CWE ID",
    ]
    df = pd.read_csv(
        cve_cwe_file, engine="python", names=col_names, header=None, delimiter=","
    )
    return df


def process_data(df):
    softwareV_dict = (
        {}
    )  # Dictionary to store Software Vulnerabilities and their CVE ID and Source URL, and CWE ID
    topic_visibility = (
        {}
    )  # Dictionary to track the visibility state of each topic's subtopics

    for _, row in df.iterrows():
        vulnerability_name = row["Software vulnerability name (CVE name)"]
        cve_id = row["CVE ID"]
        source_url = row["Source URL"]
        cwe_id = row["CWE ID"]

        # Get the values from the CSV file
        if vulnerability_name not in softwareV_dict:
            softwareV_dict[vulnerability_name] = Topics(vulnerability_name)
            topic_visibility[vulnerability_name] = False

        # add cve id to its respective topic object (if it exists, row[1] is not empty, and if it is not already in the array)
        if cve_id and cve_id not in softwareV_dict[vulnerability_name].getCves():
            softwareV_dict[vulnerability_name].addCve(cve_id)

        # add source url to its respective topic object (if it exists, row[2] is not empty, and if it is not already in the array)
        if (
            source_url
            and source_url not in softwareV_dict[vulnerability_name].getCves()
        ):
            softwareV_dict[vulnerability_name].add_CveSource(source_url)

        # add cwe id to its respective topic object (if it exists, row[3] is not empty, and if it is not already in the array)
        if cwe_id and cwe_id not in softwareV_dict[vulnerability_name].getCves():
            softwareV_dict[vulnerability_name].addCwe(cwe_id)

    return softwareV_dict, topic_visibility


def main():
    logger.debug("running script " + __file__ + " off working directory " + os.getcwd())

    app_settings = get_run_settings("Secure Software Dev Web App")
    st.set_page_config(page_title="CVE and CWE")  # Set the page title

    # large title text
    st.write("""# CVE topics""")

    df = load_data(app_settings.cve_cwe_file)
    softwareV_dict, topic_visibility = process_data(df)

    # display the list of software vulnerabilities as clickable elements with toggles
    for topic in softwareV_dict.values():
        topic_name = topic.getName()
        topic_visibility[topic_name] = st.checkbox(topic_name, value=False)
        if topic_visibility[topic_name]:
            st.write("CVE ID: ", topic.getCves())
            st.write("Source URL: ", topic.getCveSource())
            st.write("CWE ID: ", topic.getCwes())
            st.write("")


if __name__ == "__main__":
    main()
