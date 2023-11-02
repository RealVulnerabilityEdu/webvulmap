import os
import streamlit as st
import pandas as pd
from Topics import Topics
from SubTopics import SubTopics
from Cwe import Cwe

st.set_page_config(page_title="Prototype 1")  # Set the page title

def display_cwes(subtopic):
    st.write(f"**{subtopic.toString()}**")
    for cwe in subtopic.getCwes():
        st.write(cwe.toString())

print('running from ' + os.getcwd())
st.write("""# Prototype 1 CWE page
""")

text_search = st.text_input('Search')

st.write('You searched for:', text_search)

# header for the table TopicID, Topic Name, SubTopic Name, CWE ID, Source URL

colNames = ['TopicID', 'Topic Name', 'SubTopic Name', 'CWE ID', 'Source URL']
df = pd.read_csv('../data/my_data.csv', engine="python" , names = colNames ,header=None, delimiter=',')
topic_dict = {}  # Dictionary to store topics and their subtopics

# Create a dictionary to track the visibility state of each topic's subtopics
topic_visibility = {}

for index, row in df.iterrows():
    topic_id = row['TopicID']
    topic_name = row['Topic Name']
    subtopic_name = row['SubTopic Name']
    cwe_id = row['CWE ID']
    source_url = row['Source URL']
    # Get the values from the CSV file

    #topic_id, topic_name, subtopic_name, cwe_id, source_url = row[0], row[1], row[2], row[3], row[4]

    # Add topic to dictionary if it doesn't already exist
    if topic_id not in topic_dict:
        topic_dict[topic_id] = Topics(topic_id, topic_name)
        topic_visibility[topic_id] = False  # Initialize visibility state

    # Add subtopic to topic if it doesn't already exist
    if subtopic_name not in topic_dict[topic_id].subtopics:
        subtopic = SubTopics(topic_id, subtopic_name)
        topic_dict[topic_id].subtopics[subtopic_name] = subtopic  # Use dictionary-like syntax to add subtopic
    cwe = Cwe(cwe_id, subtopic_name, source_url)
    topic_dict[topic_id].subtopics[subtopic_name].addCwe(cwe)

    # add source url to its respective CWE object (if it exists, row[4] is not empty)
    if source_url:
        # -1 is the last element in the array
        topic_dict[topic_id].subtopics[subtopic_name].cwe[-1].addSourceUrl(source_url)
    
    

# Convert the dictionary values (topics) to a list
topics = list(topic_dict.values())

# Display topics as clickable elements with toggles
for topic in topics:
    button_label = f"Topic ID: ({topic.getID()}) Topic Name: {topic.getName()}"
    button_key = f"button_{topic.getID()}"
    toggle_subtopics = st.checkbox(button_label, key=button_key)
    if toggle_subtopics:
        for subtopic in topic.subtopics.values():
            display_cwes(subtopic)

# Print data from the CSV file. This is just for testing purposes.
st.write(df)
