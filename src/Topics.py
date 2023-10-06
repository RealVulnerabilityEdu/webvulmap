class Topics:
    # constructor
    def __init__(self, topic_id, topic_name):
        self.topic_id = topic_id
        self.topic_name = topic_name
    
    # to string method
    def toString(self):
        return "Topic ID: (" + str(self.topic_id) + ")Topic Name: " + str(self.topic_name)
    