from Topics import Topics

class SubTopics(Topics):
    cwe = []
    vulnerability_name = ""

    def __init__(self, topic_id, subtopic_name, vulnerability_name):
        super().__init__(topic_id, subtopic_name)  # Call the superclass constructor
        self.cwe = []  # Initialize an array of CWEs related to the subtopic
        self.vulnerability_name = vulnerability_name

    def toString(self):
        return "SubTopic ID: (" + str(self.topic_id) + ") SubTopic Name: " + str(self.topic_name) + "\n Vulnerability Name: " + str(self.vulnerability_name)

    def addCwe(self, cwe):
        self.cwe.append(cwe)
    
    def getCwes(self):
        return self.cwe