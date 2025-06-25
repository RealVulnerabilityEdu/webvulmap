# Task 2 for CISC 4900

"""
This program should read in all the json files and turn it into one json file.
This is the format.

[
{
"short-ka": "short name of KA",
"long-ka": "long name of KA",
"begin-page:  a number,
"end-page": a number
},
...
]
"""
# Option + Command + L for reformat on mac
import json


# Input list for the json files
ka_list = [
    "cs2013_web_final_sf.json",
    "cs2013_web_final_pl.json",
    # manually add the rest of the json files here
]

all_dict = {
    "curriculum": "cs2013",
    "knowledge-areas": []
}

for json_file in ka_list:
    with open(json_file, "r") as f:
        data = json.load(f)
    all_dict["knowledge-areas"].append(data)  # .append vs .extend

    # Dictionary and List, dumps everything into the new JSON file.
with open("combined_ka.json", "w") as f:
    json.dump(all_dict, f, indent=2)
