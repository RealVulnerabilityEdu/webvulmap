import json


class KnowledgeArea:
    def __init__(self, ka, short_ka) -> None:
        self.ka = ka
        self.short_ka = short_ka
        self.units = []
        self.references = []

    def add_ref_entry(self, ref_no, ref_entry):
        self.references.append(KnowledgeAreaReference(ref_no, ref_entry))

    def add_ku(self, ku):
        self.units.append(ku)

    def jsonize(self, indent=2):
        return json.dumps(self, default=lambda x: x.__dict__, indent=2)
        # return {
        #     'ka': self.ka,
        #     'short_ka': self.short_ka,
        #     'units': [ku.jsonize() for ku in self.units]
        # }


class KnowledgeUnit:
    def __init__(self, ku) -> None:
        self.ku = ku
        self.tiers = []
        self.topics = []
        self.hours = []
        self.outcomes = []

    def set_tiers(self, tier_list):
        self.tiers = tier_list

    def add_outcome(self, outcome):
        self.outcomes.append(outcome)

    def add_topic(self, topic):
        self.topics.append(topic)

    def get_last_topic(self):
        return self.topics[-1]


class KnowledgeTopic:
    def __init__(self, topic, tier=None) -> None:
        self.topic = topic
        self.tier = tier
        self.subtopics = []

    def add_subtopic(self, subtopic):
        self.subtopics.append(subtopic)


class LearningOutcome:
    def __init__(
        self, outcome_no, outcome, mastery, outcomes_tier, outcome_xref
    ) -> None:
        self.number = outcome_no
        self.outcome = outcome
        self.mastery = mastery
        self.tier = outcomes_tier
        self.xref = outcome_xref
    

    def to_json(self):
        return {
            "number": self.number,
            "outcome": self.outcome,
            "mastery": self.mastery,
            "tier": self.tier,
            "xref": self.xref
        }



class KnowledgeUnitTier:
    def __init__(self, tier, hours) -> None:
        self.tier = tier
        self.hours = hours


class KnowledgeAreaReference:
    def __init__(self, ref_no, ref_entry) -> None:
        self.ref_no = ref_no
        self.ref_entry = ref_entry
