import argparse
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

PATTERN_KA_HEADING_FMT = r"^\f{{0,1}}({}) \(({})\)$"
# PATTERN_KU_HEADING_FMT = r"^{}/([A-Z].*)$"
PATTERN_KU_HEADING_FMT = r"^{}/([A-Z][^\.]+(?!\.$))$"

PATTERN_ALL_KA_HEADING = r"^\f{0,1}(.*) \(([A-Z]+)\)$"
# PATTERN_IAS_HEADING = r'^\fInformation Assurance and Security \(IAS\)$'
PATTERN_SDF_HEADING = r"^\f{0,1}(Software Development Fundamentals) \((SDF)\)$"
PATTERN_SDF_KU_HEADING = r"^SDF/([A-Z].*)$"
PATTERN_TIER_HOURS = r"\[((\d+)\s+([^\s,\,]+)\s+hour[s]{0,1})([,;]\s*(\d+)\s+([^\s,\,]+)\s+hour[s]{0,1})*\]|\[(Elective)\]"
PATTERN_TIER_HOURS_ALT = r"\[(\d+)\s+(Core-Tier\d+)\]"
PATTERN_KU_TOPICS_HEADING = r"^Topics:$"
PATTERN_TOPICS_TIER = r"\[(Core-Tier\d+)\]|\[(Elective[s]{0,1})\]"
PATTERN_KU_TOPIC_LINE = r"(?!^Learning [Oo]utomes:$)^•\s*(\w.*)$"
PATTERN_KU_SUBTOPIC_LINE = r"(?!^Learning [Oo]utomes:$)^o\s*(\w.*)$"
PATTERN_KU_LEARNING_OUTCOMES_HEADING = r"^Learning [Oo]utcomes:$"
PATTERN_KU_PARTIAL_OUTCOMES_LINE = r"^\d+\.\s*\w.*$"
PATTERN_KU_OUTCOMES_LINE = r"^(\d+)\.\s*(\w.*)\[(.*)\]$"
PATTERN_KU_OUTCOMES_LINE_XREF = r"^(\d+)\.\s*(\w.*)\[(.*)\]\s*(This outcome.*)$"
PATTERN_KA_REFS_HEADING = r"^References$"
PATTERN_KA_REFS_ENTRY_LINE = r"^\[(\d+)\]\s+(\w+.*)$"
PATTERN_PAGE_NUMBER = r"^\f-\s*\d+\s*-$"
# extracting x-refs
PATTERN_XREF = r"^.*\(cross-reference\s+([A-Z]+/[^/]*/[^/]*(?!and [A-Z]+).*)\)$"

pattern_all_ka_heading = re.compile(PATTERN_ALL_KA_HEADING)
pattern_ka_heading = re.compile(PATTERN_SDF_HEADING)
pattern_ku_heading = re.compile(PATTERN_SDF_KU_HEADING)
pattern_tier_hours = re.compile(PATTERN_TIER_HOURS)
pattern_tier_hours_alt = re.compile(PATTERN_TIER_HOURS_ALT)
pattern_ku_topics_heading = re.compile(PATTERN_KU_TOPICS_HEADING)
pattern_topics_tier = re.compile(PATTERN_TOPICS_TIER)
pattern_ku_topic_line = re.compile(PATTERN_KU_TOPIC_LINE)
pattern_ku_outcomes_heading = re.compile(PATTERN_KU_LEARNING_OUTCOMES_HEADING)
pattern_ku_partial_outcomes_line = re.compile(PATTERN_KU_PARTIAL_OUTCOMES_LINE)
pattern_ku_outcomes_line = re.compile(PATTERN_KU_OUTCOMES_LINE)
pattern_ku_outcomes_xref_line = re.compile(PATTERN_KU_OUTCOMES_LINE_XREF)
pattern_ka_refs_heading = re.compile(PATTERN_KA_REFS_HEADING)
pattern_ka_refs_entry_line = re.compile(PATTERN_KA_REFS_ENTRY_LINE)
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
        "NO_TOPICS_TIER",
        "TOPICS_LIST",
        "LEARNING_OUTCOMES_HEADING",
        "KA_REFS_HEADING",
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


def is_refs_heading(state, line, f, line_stack):
    if state != State.LEARNING_OUTCOMES_HEADING:
        return False
    if not pattern_ka_refs_heading.match(line):
        return False
    next_line = f.readline()
    line_stack.append(next_line)
    if pattern_ka_refs_entry_line.match(next_line):
        return True
    else:
        return False


def get_topic_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line:
            return line
        if pattern_page_number.match(next_line):
            continue
        if (
            not pattern_ku_topic_line.match(next_line)
            and not pattern_ku_subtopic_line.match(next_line)
            and not pattern_topics_tier.search(next_line)
            and not pattern_ku_outcomes_heading.match(next_line)
        ):
            if next_line.strip():
                line = line.strip() + " " + next_line.strip()
        else:
            line_stack.append(next_line)
            break
    return line


def get_subtopic_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line:
            return line
        if pattern_page_number.match(next_line):
            continue
        if (
            not pattern_ku_subtopic_line.match(next_line)
            and not pattern_ku_topic_line.match(next_line)
            and not pattern_topics_tier.search(next_line)
            and not pattern_ku_outcomes_heading.match(next_line)
        ):
            if next_line.strip():
                line = line.strip() + " " + next_line.strip()
        else:
            line_stack.append(next_line)
            break
    return line


def get_outcome_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line:
            return line
        if pattern_page_number.match(next_line):
            continue
        if (
            not pattern_ku_partial_outcomes_line.match(next_line)
            and not pattern_ku_heading.match(next_line)
            and not pattern_ka_refs_heading.match(next_line)
            and not pattern_topics_tier.search(next_line)
        ):
            if next_line.strip():
                line = line.strip() + " " + next_line.strip()
        else:
            line_stack.append(next_line)
            break
    return line


def get_references_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line:
            return line
        if pattern_page_number.match(next_line):
            continue
        if not pattern_ka_refs_entry_line.match(
            next_line
        ) and not pattern_all_ka_heading.match(next_line):
            if next_line.strip():
                line = line.strip() + " " + next_line.strip()
        else:
            line_stack.append(next_line)
            break
    return line


def parse_topics_tier(line):
    matches = pattern_topics_tier.search(line)
    if not matches:
        return None
    tier_list = [tier for tier in matches.groups() if tier]
    if len(tier_list) != 1:
        return None
    return tier_list[0].strip()


def parse_outcome_line(line):
    matches = pattern_ku_outcomes_line.match(line)
    if not matches:
        matches_xref = pattern_ku_outcomes_xref_line.match(line)
        if not matches_xref:
            return None
        if len(matches_xref.groups()) != 4:
            return None
        return (
            matches_xref.group(1).strip(),
            matches_xref.group(2).strip(),
            matches_xref.group(3).strip(),
            matches_xref.group(4).strip(),
        )
    else:
        if len(matches.groups()) != 3:
            return None
        return (
            matches.group(1).strip(),
            matches.group(2).strip(),
            matches.group(3).strip(),
            None,
        )


def parse_references_entry_line(line):
    matches = pattern_ka_refs_entry_line.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 2:
        return None
    return matches.group(1).strip(), matches.group(2).strip()


def parse_ka_title_line(line):
    matches = pattern_ka_heading.match(line)
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


def parse_ku_tier_alt_line(line):
    matches = pattern_tier_hours_alt.match(line)
    if not matches:
        return None
    if len(matches.groups()) != 2:
        return None
    return KnowledgeUnitTier(matches.group(2), matches.group(1))


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


def parse_ka(ka_fn, ka_text, short_ka_text):
    global pattern_ka_heading, pattern_ku_heading
    pattern_ka_heading = re.compile(
        PATTERN_KA_HEADING_FMT.format(ka_text, short_ka_text)
    )
    pattern_ku_heading = re.compile(PATTERN_KU_HEADING_FMT.format(short_ka_text))
    ka = None
    topics_tier = None
    state = None
    line_stack = []
    with open(ka_fn, mode="rt") as f:
        line_stack.append(f.readline())

        while line_stack:
            line = line_stack.pop()

            if not state and pattern_ka_heading.match(line):
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
            elif state == State.KU_HEADING and pattern_tier_hours_alt.match(line):
                state = State.KU_HOURS
                ku_tiers = parse_ku_tier_alt_line(line)
                ku.set_tiers(ku_tiers)
            elif state == State.KU_HOURS and pattern_ku_topics_heading.match(line):
                state = State.KU_TOPICS_HEADING
            elif state == State.KU_TOPICS_HEADING and pattern_topics_tier.search(line):
                state = State.TOPICS_TIER
                topics_tier = parse_topics_tier(line)
            elif state == State.KU_TOPICS_HEADING and not pattern_topics_tier.search(
                line
            ):
                state = State.NO_TOPICS_TIER
                topics_tier = None
                line_stack.append(line)
            elif (
                state == State.KU_TOPICS_HEADING
                or state == State.TOPICS_TIER
                or state == State.NO_TOPICS_TIER
            ) and pattern_ku_topic_line.match(line):
                state = State.TOPICS_LIST
                line_stack.append(line)
            elif state == State.TOPICS_LIST and pattern_ku_topic_line.match(line):
                topic_line = get_topic_line(line, f, line_stack)
                topic = parse_topic_line(topic_line)
                ku.add_topic(KnowledgeTopic(topic, topics_tier))
            elif state == State.TOPICS_LIST and pattern_ku_subtopic_line.match(line):
                subtopic_line = get_subtopic_line(line, f, line_stack)
                subtopic = parse_subtopic_line(subtopic_line)
                ku.get_last_topic().add_subtopic(subtopic)
            elif state == State.TOPICS_LIST and pattern_topics_tier.search(line):
                state = State.TOPICS_TIER
                topics_tier = parse_topics_tier(line)
            elif state == State.TOPICS_LIST and pattern_ku_outcomes_heading.match(line):
                state = State.LEARNING_OUTCOMES_HEADING
                outcomes_tier = None
            elif (
                state == State.LEARNING_OUTCOMES_HEADING
                and pattern_ku_partial_outcomes_line.match(line)
            ):
                outcome_line = get_outcome_line(line, f, line_stack)
                outcome_no, outcome, mastery, outcome_xref = parse_outcome_line(
                    outcome_line
                )
                ku.add_outcome(
                    LearningOutcome(
                        outcome_no, outcome, mastery, outcomes_tier, outcome_xref
                    )
                )
            elif (
                state == State.LEARNING_OUTCOMES_HEADING
                and pattern_topics_tier.search(line)
            ):
                outcomes_tier = parse_topics_tier(line)
            elif state == State.LEARNING_OUTCOMES_HEADING and is_refs_heading(
                state, line, f, line_stack
            ):
                state = State.KA_REFS_HEADING
            elif state == State.KA_REFS_HEADING and pattern_ka_refs_entry_line.match(
                line
            ):
                refs_entry_line = get_references_line(line, f, line_stack)
                ref_no, ref_entry = parse_references_entry_line(refs_entry_line)
                ka.add_ref_entry(ref_no, ref_entry)
            elif (
                state == State.LEARNING_OUTCOMES_HEADING
                or state == State.KA_REFS_HEADING
            ) and pattern_ku_heading.match(line):
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


def parse_cmd_line():
    parser = argparse.ArgumentParser(prog="PROG")
    parser.add_argument(
        "--data_dir", nargs=1, help="directory for input and output files"
    )
    parser.add_argument(
        "ka", nargs="+", help="knowledge area, e.g., 'Software Engineering'"
    )
    parser.add_argument(
        "short_ka", nargs="+", help="short name for knowledge area, e.g., 'SE'"
    )
    parser.add_argument(
        "in_file",
        nargs="+",
        help="input text file extracted from ACM/IEEE CS2013 Curriculum pdf file",
    )
    parser.add_argument("out_file", nargs="+", help="output json file")
    args = parser.parse_args()
    return args


def dump_ka(ka, out_fn):
    with open(out_fn, "wt") as f:
        f.write(ka.jsonize())


def main():
    data_dir = os.path.join("webknwlmap", "curriculum", "data")
    args = parse_cmd_line()
    if args.data_dir:
        data_dir = args.data_dir[0]
    ka_fn = os.path.join(data_dir, args.in_file[0])
    ka = parse_ka(ka_fn, args.ka[0], args.short_ka[0])
    # print(ka.jsonize())
    output_fn = os.path.join(data_dir, args.out_file[0])
    dump_ka(ka, output_fn)
    print("wrote to {}".format(output_fn))


if __name__ == "__main__":
    main()
