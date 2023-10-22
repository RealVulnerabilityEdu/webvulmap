from SubTopics import SubTopics
# this class is a subclass of subtopics

class Cwe(SubTopics):
    
    #array of cves within a cwe
    cve = []
    # constructor
    def __init__(self, cwe_id, cwe_name, source_url):
        self.cwe_id = cwe_id
        self.cwe_name = cwe_name
        self.source_url = source_url
        self.cve = [] # initialize a array of cves that are related to the cwe
    
    # to string method
    def toString(self):
        return f"CWE ID: <{self.cwe_id}> CWE Name: {self.cwe_name}"
    
    # get cwe
    def getCwes(self):
        return self.cwe