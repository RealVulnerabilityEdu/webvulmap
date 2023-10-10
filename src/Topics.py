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
        self.subtopics = [] # initialize a array of subtopics
    
    # get topic id
    def getID(self):
        return self.topic_id
    # get topic name
    def getName(self):
        return self.topic_name
    
    # to string method
    def toString(self):
        return f"Topic ID: ({self.topic_id}) Topic Name: {self.topic_name}"
    
    # add subtopic to array
    def addSubTopic(self, subtopic):
        self.subtopics.append(subtopic)
    
    # get topics and its subtopics
    def getSubTopics(self):
        return self.subtopics
    