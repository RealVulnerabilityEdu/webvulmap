import os

import pandas as pd
import streamlit as st
from loguru import logger
# from model.cwe import Cwe
# from model.subtopics import SubTopics
# from model.topics import Topics
from utils.cmdl_utils import get_run_settings


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df


def display_mapped_cwes(topic_row, cwe_df):
    mapped_cwe_list = [cwe.strip().upper() for cwe in topic_row["CWE"].split(",")]
    logger.debug("mapped_cwe_list: {}".format(mapped_cwe_list))
    cwe_df_list = []
    for cwe in mapped_cwe_list:
        disp_cwe_df = cwe_df[cwe_df["ID"] == cwe]
        cwe_df_list.append(disp_cwe_df)
    disp_cwe_df = pd.concat(cwe_df_list)
    disp_cwe_df.reset_index(drop=True, inplace=True)
    disp_cwe_df.index += 1
    logger.debug("disp_cwe_df: {}".format(disp_cwe_df))
    disp_cwe_df = disp_cwe_df.to_html(escape=False)
    st.write(disp_cwe_df, unsafe_allow_html=True, hide_index=True)


def main():
    logger.debug("running script " + __file__ + " off working directory " + os.getcwd())

    app_settings = get_run_settings("Secure Software Knowledge Mapping")
    st.title("Mapping CS Topics to CWE List")

    topic_df = load_data(app_settings.topic_to_cwe_file)
    cwe_df = load_data(app_settings.cwe_list_file)
    cwe_df["URL"] = cwe_df.apply(
        lambda x: '<a href="{}" target="_blank">{}</a>'.format(x["URL"], x["URL"]),
        axis=1,
    )

    # Display topics as clickable elements with toggles
    for index, row in topic_df.iterrows():
        if row["Topic"] == row["Subtopic"]:
            button_label = "{}. Topic: ({}) {}/{}/{} ({})".format(
                index,
                row["KA"],
                row["Knowledge Area"],
                row["Knowledge Unit"],
                row["Topic"],
                row["Tier"],
            )
        else:
            button_label = "{}. Topic: ({}) {}/{}/{}/{} ({})".format(
                index,
                row["KA"],
                row["Knowledge Area"],
                row["Knowledge Unit"],
                row["Topic"],
                row["Subtopic"],
                row["Tier"],
            )
        button_key = "button_{}".format(index)
        toggle_subtopics = st.checkbox(button_label, key=button_key)
        if toggle_subtopics:
            display_mapped_cwes(row, cwe_df)


if __name__ == "__main__":
    main()
