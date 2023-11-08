class Topics:
    subtopics = {}
    cve = [] # array of cves within a topic. mostly used by AppPage2.py for organizing Software Vulnerabilities

    #string topic name, topic id
    topic_name = ""
    topic_id = 0

    # modified constructor to mimic constructor overloading
    def __init__(self, *args):

        # if there is only one argument, then it is a topic name
        if len(args) == 1:
            self.topic_name = args[0]
            self.cve = [] # initialize a array of cves that are related to the topic
            self.subtopics = {}
        # if there are two arguments, then it is a topic id and topic name
        elif len(args) == 2:
            self.topic_id = args[0]
            self.topic_name = args[1]
            self.subtopics = {}
    
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
    
    # add cve to topic object (mostly for organizing Software Vulnerabilities)
    def addCve(self, cve):
        self.cve.append(cve)

    # get cves
    def getCves(self):
        return self.cve
    