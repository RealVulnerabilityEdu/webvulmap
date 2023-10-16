from Topics import Topics
# this class is a subclass of subtopics

class Cwe(Topics):
    
    #array of cves within a cwe
    cve = []
    # constructor
    def __init__(self, cwe_id, cwe_name):
        self.cwe_id = cwe_id
        self.cwe_name = cwe_name
        self.cve = [] # initialize a array of cves that are related to the cwe
    
    # to string method
    def toString(self):
        return "CWE ID: (" + str(self.cwe_id) + ") CWE Name: " + str(self.cwe_name)
