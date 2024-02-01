import os

import pandas as pd
import streamlit as st
from loguru import logger

# from model.cwe import Cwe
# from model.subtopics import SubTopics
# from model.topics import Topics
from utils.cmdl_utils import get_run_settings


# # Function to display the CWEs upon clicking the subtopic
# def display_cwes(subtopic):
#     st.write(f"**{subtopic.toString()}**")
#     for cwe in subtopic.getCwes():
#         st.write(cwe.toString())


# def load_data(csv_path):
#     col_names = [
#         "TopicID",
#         "Topic Name",
#         "SubTopic Name",
#         "Weakness Name",
#         "CWE ID",
#         "Source URL",
#     ]
#     df = pd.read_csv(
#         csv_path, engine="python", names=col_names, header=None, delimiter=","
#     )
#     return df


# def process_data(df):
#     topic_dict = {}  # Dictionary to store topics and their subtopics
#     topic_visibility = {}  # Dictionary to track the visibility state of each topic

#     for _, row in df.iterrows():
#         topic_id = row["TopicID"]
#         topic_name = row["Topic Name"]
#         subtopic_name = row["SubTopic Name"]
#         vulnerability_name = row["Weakness Name"]
#         cwe_id = row["CWE ID"]
#         source_url = row["Source URL"]

#         # Add topic to dictionary if it doesn't already exist
#         if topic_id not in topic_dict:
#             topic_dict[topic_id] = Topics(topic_id, topic_name)
#             topic_visibility[topic_id] = False  # Initialize visibility state

#         # Add subtopic to topic if it doesn't already exist
#         if subtopic_name not in topic_dict[topic_id].subtopics:
#             subtopic = SubTopics(topic_id, subtopic_name, vulnerability_name)
#             topic_dict[topic_id].subtopics[
#                 subtopic_name
#             ] = subtopic  # Use dictionary-like syntax to add subtopic
#         cwe = Cwe(cwe_id, subtopic_name, source_url)
#         topic_dict[topic_id].subtopics[subtopic_name].addCwe(cwe)

#         # Add source URL to its respective CWE object (if it exists, row[4] is not empty)
#         if source_url:
#             topic_dict[topic_id].subtopics[subtopic_name].cwe[-1].addSourceUrl(
#                 source_url
#             )

#     return topic_dict



def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df


def display_mapped_cwes(topic_row, cwe_df):
    mapped_cwe_list = [cwe.strip().upper() for cwe in topic_row['CWE'].split(',')]
    logger.debug('mapped_cwe_list: {}'.format(mapped_cwe_list))
    cwe_df_list = []
    for cwe in mapped_cwe_list:
        disp_cwe_df = cwe_df[cwe_df['ID'] == cwe]
        cwe_df_list.append(disp_cwe_df)
    disp_cwe_df = pd.concat(cwe_df_list)
    disp_cwe_df.reset_index(drop=True, inplace=True)
    disp_cwe_df.index += 1
    logger.debug('disp_cwe_df: {}'.format(disp_cwe_df))
    disp_cwe_df = disp_cwe_df.to_html(escape=False)
    st.write(disp_cwe_df, unsafe_allow_html=True, hide_index=True)

def main():
    logger.debug("running script " + __file__ + " off working directory " + os.getcwd())

    app_settings = get_run_settings("Secure Software Knowledge Mapping")
    # st.set_page_config(page_title="CS Topics to CWE List")  # Set the page title
    st.title("Mapping CS Topics to CWE List")



    topic_df = load_data(app_settings.topic_to_cwe_file)
    cwe_df = load_data(app_settings.cwe_list_file)
    cwe_df['URL'] = cwe_df.apply(lambda x: '<a href="{}" target="_blank">{}</a>'.format(x['URL'], x['URL']), axis=1)
    # topic_dict = process_data(df)

    # Convert the dictionary values (topics) to a list
    # topics = list(topic_dict.values())

    # Display topics as clickable elements with toggles
    for index,row in topic_df.iterrows():
        if row['Topic'] == row['Subtopic']:
            button_label = "{}. Topic: ({}) {}/{}/{} ({})".format(
                index,
                row['KA'],
                row['Knowledge Area'],
                row['Knowledge Unit'],
                row['Topic'],
                row['Tier'])
        else:
            button_label = "{}. Topic: ({}) {}/{}/{}/{} ({})".format(
                index,
                row['KA'],
                row['Knowledge Area'],
                row['Knowledge Unit'],
                row['Topic'],
                row['Subtopic'],
                row['Tier'])
        button_key = "button_{}".format(index)
        toggle_subtopics = st.checkbox(button_label, key=button_key)
        if toggle_subtopics:
            display_mapped_cwes(row, cwe_df)
        # if toggle_subtopics:
        #     for subtopic in topic.subtopics.values():
        #         display_cwes(subtopic)


if __name__ == "__main__":
    main()
