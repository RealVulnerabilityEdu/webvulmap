from .subtopics import SubTopics

# this class is a subclass of subtopics


class Cwe(SubTopics):
    # array of cves within a cwe
    cve = []

    # constructor
    def __init__(self, cwe_name, cwe_id, source_url):
        self.cwe_name = cwe_name
        self.cwe_id = cwe_id
        self.source_url = source_url
        self.cve = []  # initialize a array of cves that are related to the cwe

    # to string method to print out the cwe id and cwe name and source url
    def toString(self):
        return f"CWE ID: <{self.cwe_id}> CWE Name: {self.cwe_name} Source URL: {self.source_url}"

    # get cwe id
    def getCweID(self):
        return self.cwe_id

    # add source url
    def addSourceUrl(self, source_url):
        self.source_url = source_url
