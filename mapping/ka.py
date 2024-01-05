import json
import os

class KnowledgeArea:
    def __init__(self, ka):
        self._ka = ka
    
    @classmethod
    def from_json(self, json_file):
        with open(json_file, mode='rt') as f:
            ka_list = json.load(f)
            self.validate(ka_list)
            return KnowledgeArea(ka_list)

    @classmethod
    def validate(self, ka_list):
        assert isinstance(ka_list, list)
        for ka in ka_list:
            assert 'ka' in ka
            assert 'shortka' in ka
            if 'units' in ka:
                units = ka['units']
                assert isinstance(units, list)
                for unit in units:
                    assert 'ku' in unit
                    assert 'topics' in unit
                    assert 'outcomes' in unit
                    for topic in unit['topics']:
                        assert isinstance(topic, dict)

if __name__ == '__main__':
    ka = KnowledgeArea.from_json(os.path.join(os.path.dirname(__file__), 'ka.json'))
    print('tested')

