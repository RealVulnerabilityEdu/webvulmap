import pytest
from ka import LearningOutcome
import json
import os

def test_learning_outcome_to_json():
    lo = LearningOutcome("1", "Understand basic concepts", "Familiarity", "Core-Tier1", "This outcome...")
    expected = {
        "number": "1",
        "outcome": "Understand basic concepts",
        "mastery": "Familiarity",
        "tier": "Core-Tier1",
        "xref": "This outcome..."
    }
    assert lo.to_json() == expected
    
    # the following is to check the saved json 

    # tmp_path = '/home/cning/webvulmap/curriculum'

    # file_path = os.path.join(tmp_path, "learning_outcome.json")
    
    # with open(file_path, "w") as f:
    #     json.dump(lo.to_json(), f, indent=2)


