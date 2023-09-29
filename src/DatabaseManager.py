import sqlite3
import os
import csv

# connect to the database
conn = sqlite3.connect('../data/Database.db')
c = conn.cursor()

# Open the csv file and insert the data into the database
with open('Database.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        topic_name, sub_topic, link_url = row

        # is the topic already in???
        c.execute("SELECT id FROM topics WHERE name=?", (topic_name,))
        topic_row = c.fetchone()
        if topic_row is None:
            # insert the topic
            c.execute("INSERT INTO topics (name) VALUES (?)", (topic_name,))
            topic_id = c.lastrowid
        else:
            topic_id = topic_row[0]

        c.execute("INSERT INTO subtopics (subtopic_name, topic_id) VALUES (?, ?)", (sub_topic, topic_id))
        subtopic_id = c.lastrowid
        c.execute("INSERT INTO links (link_url, subtopic_id) VALUES (?, ?)", (link_url, subtopic_id))

conn.commit()
conn.close()


