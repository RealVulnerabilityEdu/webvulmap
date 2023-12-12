import os
import streamlit as st
import pandas as pd
from Topics import Topics
from SubTopics import SubTopics
from Cwe import Cwe

# Function to display the CWEs upon clicking the subtopic
def display_cwes(subtopic):
    st.write(f"**{subtopic.toString()}**")
    for cwe in subtopic.getCwes():
        st.write(cwe.toString())

# def load_data():
#     col_names = ['TopicID', 'Topic Name', 'SubTopic Name', 'Weakness Name', 'CWE ID', 'Source URL']
#     df = pd.read_csv('../data/my_data.csv', engine="python", names=col_names, header=None, delimiter=',')
#     return df

def load_data(csv_path):
    col_names = ['TopicID', 'Topic Name', 'SubTopic Name', 'Weakness Name', 'CWE ID', 'Source URL']
    df = pd.read_csv(csv_path, engine="python", names=col_names, header=None, delimiter=',')
    return df

def process_data(df):
    topic_dict = {}  # Dictionary to store topics and their subtopics
    topic_visibility = {}  # Dictionary to track the visibility state of each topic

    for index, row in df.iterrows():
        topic_id = row['TopicID']
        topic_name = row['Topic Name']
        subtopic_name = row['SubTopic Name']
        vulnerability_name = row['Weakness Name']
        cwe_id = row['CWE ID']
        source_url = row['Source URL']

        # Add topic to dictionary if it doesn't already exist
        if topic_id not in topic_dict:
            topic_dict[topic_id] = Topics(topic_id, topic_name)
            topic_visibility[topic_id] = False  # Initialize visibility state

        # Add subtopic to topic if it doesn't already exist
        if subtopic_name not in topic_dict[topic_id].subtopics:
            subtopic = SubTopics(topic_id, subtopic_name, vulnerability_name)
            topic_dict[topic_id].subtopics[subtopic_name] = subtopic  # Use dictionary-like syntax to add subtopic
        cwe = Cwe(cwe_id, subtopic_name, source_url)
        topic_dict[topic_id].subtopics[subtopic_name].addCwe(cwe)

        # Add source URL to its respective CWE object (if it exists, row[4] is not empty)
        if source_url:
            topic_dict[topic_id].subtopics[subtopic_name].cwe[-1].addSourceUrl(source_url)

    return topic_dict

def main():
    st.set_page_config(page_title="Page 1")  # Set the page title

    print('running from ' + os.getcwd())
    st.write("""# Prototype 1 CWE page
    """)

    # description text of what a CWE is
    st.write("## What is a CWE?")
    st.write("Common Weakness Enumeration (CWE) is a list of software weaknesses.") 
    st.write("It serves as a common language, a measuring stick for security tools, and as a baseline for weakness identification, mitigation, and prevention efforts.")

    df = load_data('../data/my_data.csv')
    topic_dict = process_data(df)

    # Convert the dictionary values (topics) to a list
    topics = list(topic_dict.values())

    # Display topics as clickable elements with toggles
    for topic in topics:
        button_label = f"Topic Number: ({topic.getID()}) Topic Name: {topic.getName()}"
        button_key = f"button_{topic.getID()}"
        toggle_subtopics = st.checkbox(button_label, key=button_key)
        if toggle_subtopics:
            for subtopic in topic.subtopics.values():
                display_cwes(subtopic)

if __name__ == "__main__":
    main()
