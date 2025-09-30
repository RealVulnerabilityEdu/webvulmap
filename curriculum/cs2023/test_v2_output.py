import json

with open("curriculum/cs2023/SE_SAMPLE_v2.json") as f:
    data = json.load(f)

# Example: Check that "SE/Software Processes" has KA Core outcomes
processes = next(
    s for s in data["sections"] if s["title"] == "SE/Software Processes"
)
assert "KA Core" in processes["learning_outcomes"]
assert (
    "the ability to select and justify an appropriate software process "
    "for a given project."
    in processes["learning_outcomes"]["KA Core"]
)

# Example: Check that "SE/Software Design" has KA Core outcomes
design = next(
    s for s in data["sections"] if s["title"] == "SE/Software Design"
)
assert "KA Core" in design["learning_outcomes"]
assert (
    "creating and documenting a software design for a medium-sized "
    "software system."
    in design["learning_outcomes"]["KA Core"]
)
assert (
    "Students will learn about concepts like coupling, cohesion, and "
    "modularity"
    in design["learning_outcomes"]["KA Core"]
)

print("All tests passed!")
