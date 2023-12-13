import os
import pandas as pd
from App import process_data, display_cwes, load_data
from unittest.mock import patch

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


# Mock Streamlit functions to test display_cwes function
@patch('App.st.write') #patch is used to mock the st.write function
def test_display_cwes(mock_write):
    # Import here to avoid issues with patching
    from SubTopics import SubTopics
    from Cwe import Cwe

    # Create a Subtopic object with CWEs for testing
    subtopic = SubTopics(1, 'Language 1.1', 'Weakness 1.1.1')
    cwe1 = Cwe('CWE-111', 'Language 1.1', 'http://example.com/cwe-111')

    # Add the CWE to the subtopic
    subtopic.addCwe(cwe1)

    # Call the display_cwes function with the Subtopic object
    display_cwes(subtopic)

    # Assertions to ensure the mock was called with the expected output
    expected_output_1 = f"**{subtopic.toString()}**"
    expected_output_2 = cwe1.toString()

    # Verify that the mock was called with the expected output
    mock_write.assert_any_call(expected_output_1)
    mock_write.assert_any_call(expected_output_2)

    

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
