import os
import streamlit as st
import pandas as pd
from Topics import Topics

st.set_page_config(
    page_title="Prototype 1"
    
    )  # Set the page title

def display_subtopics(topic):
    st.write(f"**Topic ID: ({topic.getID()}) Topic Name: {topic.getName()}**")
    for subtopic in topic.getSubTopics():
        st.write(subtopic)

print('running from ' + os.getcwd())
st.write("""# Prototype 1
""")

text_search = st.text_input('Search')

st.write('You searched for:', text_search)

df = pd.read_csv('../data/my_data.csv', engine='python', header=None, delimiter=', ')
topic_dict = {}  # Dictionary to store topics and their subtopics

# Create a dictionary to track the visibility state of each topic's subtopics
topic_visibility = {}

for index, row in df.iterrows():
    topic_id, topic_name, subtopic_name = row[0], row[1], row[2]

    if topic_id not in topic_dict:
        topic_dict[topic_id] = Topics(topic_id, topic_name)
        topic_visibility[topic_id] = False  # Initialize visibility state
    topic_dict[topic_id].addSubTopic(subtopic_name)

# Convert the dictionary values (topics) to a list
topics = list(topic_dict.values())

# Display topics as clickable elements with toggles
for topic in topics:
    button_label = f"Topic ID: ({topic.getID()}) Topic Name: {topic.getName()}"
    button_key = f"button_{topic.getID()}"
    toggle_subtopics = st.checkbox(button_label, key=button_key)
    if toggle_subtopics:
        display_subtopics(topic)

# Print data from the CSV file.
df = pd.read_csv('../data/my_data.csv')
st.write(df)
