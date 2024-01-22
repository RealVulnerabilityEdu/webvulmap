import os
import re
from enum import Enum
from ka import (
    KnowledgeArea,
    KnowledgeUnit,
    KnowledgeTopic,
    LearningOutcome,
    KnowledgeUnitTier,
)


# PATTERN_IAS_HEADING = r'^\fInformation Assurance and Security \(IAS\)$'
PATTERN_IAS_HEADING = r"^\f{0,1}(Software Development Fundamentals) \((SDF)\)$"
PATTERN_KU_HEADING = r"^SDF/([A-Z].*)$"
PATTERN_TIER_HOURS = r"\[((\d+)\s+([^\s,\,]+)\s+hour[s]{0,1})(,\s*(\d+)\s+([^\s,\,]+)\s+hour[s]{0,1})*\]|\[(Elective)\]"
PATTERN_KU_TOPICS_HEADING = r"^Topics:$"
PATTERN_TOPICS_TIER = r"\[Core-Tier\d+\]|\[Elective\]"
PATTERN_KU_TOPIC_LINE = r"(?!^Learning outomes:$)^•\s*(\w.*)$"
PATTERN_KU_SUBTOPIC_LINE = r"(?!^Learning outomes:$)^o\s*(\w.*)$"
PATTERN_KU_LEARNING_OUTCOMES_HEADING = r"^Learning Outcomes:$"
PATTERN_KU_PARTIAL_OUTCOMES_LINE = r"^\d+\.\s*\w.*$"
PATTERN_KU_OUTCOMES_LINE = r"^\d+\.\s*(\w.*)\[(.*)\]$"
PATTERN_PAGE_NUMBER = r"^\f-\s*\d+\s*-$"

pattern_ias_heading = re.compile(PATTERN_IAS_HEADING)
pattern_ku_heading = re.compile(PATTERN_KU_HEADING)
pattern_tier_hours = re.compile(PATTERN_TIER_HOURS)
pattern_ku_topics_heading = re.compile(PATTERN_KU_TOPICS_HEADING)
pattern_topics_tier = re.compile(PATTERN_TOPICS_TIER)
pattern_ku_topic_line = re.compile(PATTERN_KU_TOPIC_LINE)
pattern_ku_outcomes_heading = re.compile(PATTERN_KU_LEARNING_OUTCOMES_HEADING)
pattern_ku_partial_outcomes_line = re.compile(PATTERN_KU_PARTIAL_OUTCOMES_LINE)
pattern_ku_outcomes_line = re.compile(PATTERN_KU_OUTCOMES_LINE)
pattern_page_number = re.compile(PATTERN_PAGE_NUMBER)
pattern_ku_subtopic_line = re.compile(PATTERN_KU_SUBTOPIC_LINE)

State = Enum(
    "State",
    [
        "IN_KA",
        "KU_HEADING",
        "KU_HOURS",
        "KU_TOPICS_HEADING",
        "TOPICS_TIER",
        "TOPICS_LIST",
        "LEARNING_OUTCOMES_HEADING",
    ],
)


def is_ku_heading(state, line, f, line_stack):
    if state == State.IN_KA and not pattern_ku_heading.match(line):
        return False
    elif state == State.IN_KA and pattern_ku_heading.match(line):
        line = f.readline()
        if not line:
            return False
        line_stack.append(line)
        return True if pattern_tier_hours.match(line) else False
    else:
        return False


def get_outcome_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line:
            return line
        if pattern_page_number.match(next_line):
            continue
        if not pattern_ku_partial_outcomes_line.match(
            next_line
        ) and not pattern_ku_heading.match(next_line):
            if next_line.strip():
                line = line.strip() + " " + next_line.strip()
        else:
            line_stack.append(next_line)
            break
    return line


def parse_outcome_line(line):
    matches = pattern_ku_outcomes_line.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 2:
        return None
    return matches.group(1).strip(), matches.group(2).strip()


def parse_ka_title_line(line):
    matches = pattern_ias_heading.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 2:
        return None
    return matches.group(1), matches.group(2)


def parse_ku_title_line(line):
    matches = pattern_ku_heading.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 1:
        return None
    return matches.group(1).strip()


def parse_ku_tier_line(line):
    matches = pattern_tier_hours.match(line)
    if not matches:
        return None
    m_list = [m for m in matches.groups() if m]
    if len(m_list) % 3 == 0:
        tier_list = []
        for i in range(0, len(m_list), 3):
            tier_list.append(KnowledgeUnitTier(m_list[i + 2], m_list[i + 1]))
        return tier_list
    elif len(m_list) == 1:
        return KnowledgeUnitTier(m_list[0], None)
    else:
        return None


def parse_topic_line(line):
    matches = pattern_ku_topic_line.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 1:
        return None
    return matches.group(1).strip()


def parse_subtopic_line(line):
    matches = pattern_ku_subtopic_line.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 1:
        return None
    return matches.group(1).strip()


def parse_ka(ka_fn):
    ka = None
    topics_tier = None
    state = None
    line_stack = []
    topics_list = []
    with open(ka_fn, mode="rt") as f:
        line_stack.append(f.readline())

        while line_stack:
            line = line_stack.pop()

            if not state and pattern_ias_heading.match(line):
                state = State.IN_KA
                ka_title, ka_short_title = parse_ka_title_line(line)
                ka = KnowledgeArea(ka_title, ka_short_title)
            elif state == State.IN_KA and is_ku_heading(state, line, f, line_stack):
                state = State.KU_HEADING
                ku_title = parse_ku_title_line(line)
                ku = KnowledgeUnit(ku_title)
                ka.add_ku(ku)
            elif state == State.KU_HEADING and pattern_tier_hours.match(line):
                state = State.KU_HOURS
                ku_tiers = parse_ku_tier_line(line)
                ku.set_tiers(ku_tiers)
            elif state == State.KU_HOURS and pattern_ku_topics_heading.match(line):
                state = State.KU_TOPICS_HEADING
            elif state == State.KU_TOPICS_HEADING and pattern_topics_tier.match(line):
                state = State.TOPICS_TIER
                topics_tier = line.strip()
            elif state == State.KU_TOPICS_HEADING and not pattern_topics_tier.match(
                line
            ):
                state = State.TOPICS_TIER
                topics_tier = None
                line_stack.append(line)
            elif (
                state == State.KU_TOPICS_HEADING or state == State.TOPICS_TIER
            ) and pattern_ku_topic_line.match(line):
                state = State.TOPICS_LIST
                line_stack.append(line)
            elif state == State.TOPICS_LIST and pattern_ku_topic_line.match(line):
                topic = parse_topic_line(line)
                ku.add_topic(KnowledgeTopic(topic, topics_tier))
            elif state == State.TOPICS_LIST and pattern_ku_subtopic_line.match(line):
                subtopic = parse_subtopic_line(line)
                ku.get_last_topic().add_subtopic(subtopic)
            elif state == State.TOPICS_LIST and pattern_ku_outcomes_heading.match(line):
                state = State.LEARNING_OUTCOMES_HEADING
            elif (
                state == State.LEARNING_OUTCOMES_HEADING
                and pattern_ku_partial_outcomes_line.match(line)
            ):
                outcome_line = get_outcome_line(line, f, line_stack)
                outcome, mastery = parse_outcome_line(outcome_line)
                ku.add_outcome(LearningOutcome(outcome, mastery))
            elif state == State.LEARNING_OUTCOMES_HEADING and pattern_ku_heading.match(
                line
            ):
                state = State.KU_HEADING
                ku_title = parse_ku_title_line(line)
                ku = KnowledgeUnit(ku_title)
                ka.add_ku(ku)
            elif pattern_page_number.match(line):
                pass
            else:
                pass

            if not line_stack:
                line = f.readline()
                if line:
                    line_stack.append(line)

    return ka


def main():
    ka_fn = os.path.join("webknwlmap", "curriculum", "data", "cs2013_web_final_sdf.txt")
    ka = parse_ka(ka_fn)
    print(ka.jsonize())


if __name__ == "__main__":
    main()
