"""Representing CS Knowledge Area."""

import json
import os


class KnowledgeArea:
    """Representing CS Knowledge Area."""

    def __init__(self, ka):
        self._ka = ka

    @classmethod
    def from_json(cls, json_file):
        with open(json_file, mode="rt", encoding="utf-8") as f:
            ka_list = json.load(f)
            cls.validate(ka_list)
            return KnowledgeArea(ka_list)

    @classmethod
    def validate(cls, ka_list):
        assert isinstance(ka_list, list)
        for ka in ka_list:
            assert "ka" in ka
            assert "shortka" in ka
            if "units" in ka:
                units = ka["units"]
                assert isinstance(units, list)
                for unit in units:
                    assert "ku" in unit
                    assert "topics" in unit
                    assert "outcomes" in unit
                    for topic in unit["topics"]:
                        assert isinstance(topic, dict)


if __name__ == "__main__":
    knowledge_area = KnowledgeArea.from_json(
        os.path.join(os.path.dirname(__file__), "ka.json")
    )
    print("tested")
