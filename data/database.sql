--Topics table
CREATE TABLE topics(
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT NOT NULL,
)

--Subtopics table
CREATE TABLE subtopics (
    subtopic_id INTEGER PRIMARY KEY,
    subtopic_name TEXT NOT NULL,
    topic_id INTEGER,
    
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id)
);

--links that relates to subtopic
CREATE TABLE links (
    link_id INTEGER PRIMARY KEY,
    link_url TEXT NOT NULL,
    subtopic_id INTEGER,
    FOREIGN KEY (subtopic_id) REFERENCES subtopics (subtopic_id)
);

