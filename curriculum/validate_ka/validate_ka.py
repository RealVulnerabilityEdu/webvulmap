import argparse
import csv

# Simple version of validate csv, not as many error checks. Only checks column name and page continuity.
# python validate_ka.py --input-file cs2013_ka_meta.csv
parser = argparse.ArgumentParser()
parser.add_argument(
    "--input-file",
    required=True
)
args = parser.parse_args()  # Store the parsed arguments

file_path = args.input_file


# Argparse: User needs to input a file in order for the script to run because argparse.

# Validate CSV content
def validate_csv_content(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

        # Check for required columns if names are same
        required_columns = {'ka', 'short_ka', 'page_begin', 'page_end'}
        if not required_columns.issubset(rows[0].keys()):
            print("Error: Missing required columns.")
            return False

        # Check that each page_end is greater than the corresponding page_begin for every row
        # Also makes sure that the end page can't be the same as begin page.
        for i in range(len(rows)):
            current_begin = int(rows[i]['page_begin'])
            current_end = int(rows[i]['page_end'])

            if current_end <= current_begin:
                print("Page Error")
                return False

        # Check page continuity, ex: end page for ch1 is 65, begin page for ch2 should be 65+1=66
        for i in range(len(rows) - 1):
            current_end = int(rows[i]['page_end'])
            next_begin = int(rows[i + 1]['page_begin'])

            if current_end + 1 != next_begin:
                print("Page is not matching!")
                return False

    print("CSV file is valid.")
    return True


# Run the validation
validate_csv_content(file_path)
