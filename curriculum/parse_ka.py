import os
import re
from enum import Enum


PATTERN_IAS_HEADING = r'^\fInformation Assurance and Security \(IAS\)$'
PATTERN_KU_HEADING = r'^IAS/[A-Z].*$'
PATTERN_CORE_HOURS = r'\[\d.*hour[s]{0,1}(,\s*\d.*hour[s]{0,1})*\]|\[(Elective)\]'
PATTERN_KU_TOPICS_HEADING = r'^Topics:$'
PATTERN_TOPICS_HOURS = r'\[\d.*hour[s]{0,1}\]|\[Elective\]'
PATTERN_KU_TOPIC_LINE = r'^•\s*\w.*$!^Learning outcomes:$'
PATTERN_KU_LEARNING_OUTCOMES = r'^Learning outcomes:$'
PATTERN_KU_OUTCOMES_LINE = r'^\d+\.\w.*$'
PATTERN_PAGE_NUMBER = r'^\f-\s*\d+\s*-$'

pattern_ias_heading = re.compile(PATTERN_IAS_HEADING)
pattern_ku_heading = re.compile(PATTERN_KU_HEADING)
pattern_core_hours = re.compile(PATTERN_CORE_HOURS)
pattern_ku_topics_heading = re.compile(PATTERN_KU_TOPICS_HEADING)
pattern_topics_hours = re.compile(PATTERN_TOPICS_HOURS)
pattern_ku_topic_line = re.compile(PATTERN_KU_TOPIC_LINE)
pattern_ku_outcomes = re.compile(PATTERN_KU_LEARNING_OUTCOMES)
pattern_ku_outcomes_line = re.compile(PATTERN_KU_OUTCOMES_LINE)
pattern_page_number = re.compile(PATTERN_PAGE_NUMBER)

State = Enum('State',
             ['IN_KA',
              'KU_HEADING', 'KU_HOURS', 'KU_TOPICS_HEADING', 'TOPICS_HOURS', 'TOPICS_LIST',
              'LEARNING_OUTCOMES_HEADING'])

def is_ku_heading(state, line, f, line_stack):
    if state == State.IN_KA and not pattern_ku_heading.match(line):
        return False
    elif state == State.IN_KA and pattern_ku_heading.match(line):
        line = f.readline()
        if not line: return False
        line_stack.append(line)
        return True if pattern_core_hours.match(line) else False
    else:
        return False
        
def get_outcome_line(line, f, line_stack):
    while True:
        next_line = f.readline()
        if not next_line: break
        if pattern_page_number.match(next_line): continue
        if not pattern_ku_outcomes_line.match(next_line) and not pattern_ku_heading(next_line):
            line = line.strip() + ' ' + next_line.strip()
        else:
            line_stack.append(next_line)
            break 
    return line
    

def parse_ka(ka_fn):   
    state = None
    line_stack = []
    topics_list = []
    with open(ka_fn, mode='rt') as f:
        line_stack.append(f.readline())
        
        while line_stack:
            line = line_stack.pop()           
          
            if not state and pattern_ias_heading.match(line):
                state = State.IN_KA
            elif state == State.IN_KA and is_ku_heading(state, line, f, line_stack):
                state = State.KU_HEADING
            elif state == State.KU_HEADING and pattern_core_hours.match(line):
                state = State.KU_HOURS
                topics_hours = pattern_topics_hours.search(line)
            elif state == State.KU_HOURS and pattern_ku_topics_heading.match(line):
                state = State.KU_TOPICS_HEADING
            elif state == State.KU_TOPICS_HEADING and pattern_topics_hours.search(line):
                state = State.TOPICS_HOURS
                topics_hours = pattern_topics_hours.search(line)
            elif (state == State.KU_TOPICS_HEADING or state == State.TOPICS_HOURS) and pattern_ku_topic_line.match(line):
                state = State.TOPICS_LIST
                line_stack.append(line)
            elif state == State.TOPICS_LIST and pattern_ku_topic_line.match(line):
                topics_list.append(line)
            elif state == State.TOPICS_LIST and pattern_ku_outcomes.match(line):
                state = State.LEARNING_OUTCOMES_HEADING
            elif state == State.LEARNING_OUTCOMES_HEADING and pattern_ku_outcomes_line.match(line):
                outcome = get_outcome_line(line, f, line_stack)
            elif state == State.LEARNING_OUTCOMES_HEADING and pattern_ku_heading(line):
                state = State.KU_HEADING
                break
            elif pattern_page_number.match(line):
                pass
            else:
                state = None

            if not line_stack:
                line = f.readline()
                if line: line_stack.append(line) 

                

def main():
    ka_fn = os.path.join('webknwlmap', 'curriculum', 'data', 'cs2013_web_final_ias.txt')
    parse_ka(ka_fn)

if __name__ == '__main__':
    main()