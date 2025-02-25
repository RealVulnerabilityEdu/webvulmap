import argparse
import csv
import json
import os
from validate_ka import validate_csv_content

# parses command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert a CSV file into JSON format.")
    parser.add_argument("--input-file", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output-file",help="Path to the output JSON file. If not specified, the JSON file will be created with the same name as the CSV file.")
    return parser.parse_args()

# converts a csv file to json after validating.
def csv_to_json(file_path, output_file):

    if not validate_csv_content(file_path):
        print("CSV validation failed. Exiting.")
        return

    all_dict = {
        "curriculum": "cs2013",
        "knowledge-areas": []
    }
    # error handling
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    ka_data = {
                        "short-ka": row["short_ka"].strip(),
                        "long-ka": row["ka"].strip(),
                        "begin-page": int(row["page_begin"]),
                        "end-page": int(row["page_end"]),
                    }
                    all_dict["knowledge-areas"].append(ka_data)
                except (KeyError, ValueError) as e:
                    print(f"Skipping row due to error: {e}")

        with open(output_file, "w", encoding="utf-8") as jsonfile:
            json.dump(all_dict, jsonfile, indent=2)
        print(f"JSON file created: {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    args = parse_arguments()

    # If no output file is provided, generate one based on the input file name
    if not args.output_file:
        output_file = os.path.splitext(args.input_file)[0] + ".json"
    else:
        output_file = args.output_file

    csv_to_json(args.input_file, output_file)