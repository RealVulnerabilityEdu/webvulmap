from Topics import Topics
# this class is a subclass of Topics
class SubTopics(Topics):

    cwe = []


    # constructor
    def __init__(self, topic_id, subtopic_name):
        self.subtopic_id = topic_id
        self.subtopic_name = subtopic_name
        self.cwe = [] # initialize a array of cwes that are related to the subtopic
    
    # to string method
    def toString(self):
        return "SubTopic ID: (" + str(self.subtopic_id) + ") SubTopic Name: " + str(self.subtopic_name)
        