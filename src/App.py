import os
import streamlit as st
import pandas as pd
from Topics import Topics
from SubTopics import SubTopics  # Import the SubTopics class

print('running from ' + os.getcwd())
st.write("""# My first app
Hello *world!*
""")

# Create an array of Topics objects
topics = []

# Read the CSV file and group subtopics into topics
df = pd.read_csv('../data/my_data.csv', engine='python', header=None, delimiter=', ')
topic_dict = {}  # Dictionary to store topics and their subtopics

for index, row in df.iterrows():
    topic_id, topic_name, subtopic_name = row[0], row[1], row[2]

    if topic_id not in topic_dict:
        topic_dict[topic_id] = Topics(topic_id, topic_name)
    
    subtopic = SubTopics(topic_id, subtopic_name)
    topic_dict[topic_id].addSubTopic(subtopic)

# Convert the dictionary values (topics) to a list
topics = list(topic_dict.values())

# Print the topics and their subtopics to the web page using streamlit
for topic in topics:
    st.write(topic.toString())
    for subtopic in topic.getSubTopics():
        st.write(subtopic.toString())

text_search = st.text_input('Search')

# Test to see if the input is read correctly
st.write('You searched for: ', text_search)

# Print data from the CSV file.
df = pd.read_csv('../data/my_data.csv')
st.write(df)
