from Topics import Topics

class SubTopics(Topics):
    cwe = []
    weakness_name = ""

    def __init__(self, topic_id, subtopic_name, weakness_name):
        super().__init__(topic_id, subtopic_name)  # Call the superclass constructor
        self.cwe = []  # Initialize an array of CWEs related to the subtopic
        self.weakness_name_name = weakness_name

    def toString(self):
        return "SubTopic ID: (" + str(self.topic_id) + ") SubTopic Name: " + str(self.topic_name) + "\n Weakness Name: " + str(self.weakness_name)

    def addCwe(self, cwe):
        self.cwe.append(cwe)
    
    def getCwes(self):
        return self.cwe