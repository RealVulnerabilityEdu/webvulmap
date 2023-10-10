from Topics import Topics
# this class is a subclass of Topics
class SubTopics(Topics):

    # constructor
    def __init__(self, topic_id, subtopic_name):
        self.subtopic_id = topic_id
        self.subtopic_name = subtopic_name
    
    # to string method
    def toString(self):
        return "SubTopic ID: (" + str(self.subtopic_id) + ") SubTopic Name: " + str(self.subtopic_name)
        