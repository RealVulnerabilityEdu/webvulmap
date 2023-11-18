#TODO future work: add a test to check if the data is being read correctly and displayed correctly

from Topics import Topics


class TestApp():
    def outputTopicName(x):
        return x.getName()
    
    def test_outputTopicName():
        topic = Topics("topic1")
        assert TestApp.outputTopicName(topic) == "topic1"
        