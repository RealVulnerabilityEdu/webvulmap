import os
import pandas as pd
from App import process_data, display_cwes, load_data
from Cwe import Cwe
from SubTopics import SubTopics

def test_process_data():
    # Load test data
    test_data = [
        [1, 'Topic 1', 'Language 1.1', 'Weakness 1.1.1', 'CWE-111', 'http://example.com/cwe-111'],
        
    ]
    test_df = pd.DataFrame(test_data, columns=['TopicID', 'Topic Name', 'SubTopic Name', 'Weakness Name', 'CWE ID', 'Source URL'])

    # Process the test data
    test_topic_dict = process_data(test_df)

    # assertions
    assert len(test_topic_dict) == 1
    assert 'Language 1.1' in test_topic_dict[1].subtopics
    assert 'Language 1.1' in test_topic_dict[1].subtopics['Language 1.1'].toString()


# def test_display_cwe(capsys):
#     # Create a Subtopic object with CWEs for testing
#     subtopic = SubTopics(1, 'Language 1.1', 'Weakness 1.1.1')
#     cwe1 = Cwe('CWE-111', 'Language 1.1', 'http://example.com/cwe-111')
    
#     subtopic.addCwe(cwe1)

#     # Call the display_cwes function with the Subtopic object
#     display_cwes(subtopic)



#     # Capture the printed output
#     captured = capsys.readouterr()

#     # Print captured output for debugging
#     print(captured.out)

#     # assertions 
#     assert 'CWE-111' in captured.out
    

def test_load_data():
    
    test_csv_path = 'test_data.csv'
    test_csv_content = "TopicID,Topic Name,SubTopic Name,Weakness Name,CWE ID,Source URL\n1,Topic 1,Subtopic 1.1,Weakness 1.1.1,CWE-111,http://example.com/cwe-111\n"
    with open(test_csv_path, 'w') as test_csv:
        test_csv.write(test_csv_content)

    # Call the load_data function with the test CSV file
    test_df = load_data(test_csv_path)

    # Add assertions based on the expected DataFrame structure
    assert 'TopicID' in test_df.columns
    assert 'Topic Name' in test_df.columns
    assert 'CWE ID' in test_df.columns

    # Clean up the test CSV file
    os.remove(test_csv_path)
