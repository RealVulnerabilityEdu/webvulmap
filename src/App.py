import os
import streamlit as st
import pandas as pd

from Topics import Topics
#import sqlite3

# create a array of Topics objects of size n
topics = []

# read csv file and the first word of each line is the topic id ignoring the comma. 
# the second word of each line is the topic name.
# Using pd.read_csv() to read the csv file.
# Then make a new Topics object and add id and name to the object. Topics(id, name)
df = pd.read_csv('../data/my_data.csv', engine='python', header=None, delimiter=', ')
topic_ids = set()
for index, row in df.iterrows():
    if row[0] not in topic_ids:
        topic = Topics(row[0], row[1])
        topics.append(topic)
        topic_ids.add(row[0])


# print the topics to console for testing
for topic in topics:
    print(topic.toString())


 
print('running from ' + os.getcwd())
st.write("""# My first app
Hello *world!*
""")
         
text_search = st.text_input('Search')

#test to see if the input is read correctly
st.write('You searched for: ', text_search)

# print from csv file. 
df = pd.read_csv('../data/my_data.csv')
st.write(df)

# reads csv file and puts it into a array only 


