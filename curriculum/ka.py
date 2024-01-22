class KnowledgeArea:
    def __init__(self, ka, short_ka) -> None:
        self.ka = ka
        self.short_ka = short_ka
        self.units = []

    def add_ku(self, ku):
        self.units.append(ku)

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

class KnowledgeTopic:
    def __init__(self, topic, tier=None) -> None:
        self.topic = topic
        self.tier = tier
        self.subtopics = []

    def add_subtopic(self, subtopic):
        self.subtopics.append(subtopic)

class LearningOutcome:
    def __init__(self, outcome, mastery) -> None:
        self.outcome = outcome
        self.mastery = mastery

class KnowledgeUnitTier:
    def __init__(self, tier, hours) -> None:
        self.tier = tier
        self.hours = hours
