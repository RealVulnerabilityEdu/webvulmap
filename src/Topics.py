class Topics:

    #array of subtopics
    subtopics = []

    #string topic name, topic id
    topic_name = ""
    topic_id = 0

    # constructor
    def __init__(self, topic_id, topic_name):
        self.topic_id = topic_id
        self.topic_name = topic_name
    
    # to string method
    def toString(self):
        return "Topic ID: (" + str(self.topic_id) + ")Topic Name: " + str(self.topic_name)
    
    # add subtopic to array
    def addSubTopic(self, subtopic):
        self.subtopics.append(subtopic)
    