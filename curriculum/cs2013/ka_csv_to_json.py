# Option + Command + L for reformat on mac

import argparse
import csv
import json
import os
from validate_ka import validate_csv_content
# File name, method name


parser = argparse.ArgumentParser()
parser.add_argument(
    "--input-file",  # Input CSV
    required=True,
)
parser.add_argument(
    "--output-file",  # Output json
    required=True,
)
args = parser.parse_args()  # Store the parsed arguments

file_path = args.input_file
output_file = args.output_file



# Function to convert the CSV file into a JSON file
def csv_to_json(file_path, output_file):

    # Validate CSV file
    if not validate_csv_content(file_path):
        print("CSV validation failed.") #returns if validation csv fails.
        return

    # Dictionary to store the final JSON structure
    all_dict = {
        "curriculum": "cs2013",
        "knowledge-areas": []
    }

    # Reading in the CSV
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            ka_data = {
                "short-ka": row['short_ka'],  # Short name of the knowledge area
                "long-ka": row['ka'],  # Long name of the knowledge area
                "begin-page": int(row['page_begin']),  # Start page number
                "end-page": int(row['page_end'])  # End page number
                # page read in as ints, by default they are strings as that will be invalid.
            }

            all_dict["knowledge-areas"].append(ka_data)
            # .append vs .extend

    # Output
    with open(output_file, 'w') as jsonfile:
        json.dump(all_dict, jsonfile, indent=2)
    print("JSON file created.")


csv_to_json(file_path, output_file)