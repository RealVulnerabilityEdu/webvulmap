import argparse
import csv

# Parse arguments
parser = argparse.ArgumentParser(description="Validate CSV file for required columns and page order.")
parser.add_argument("--input-file", required=True, help="Path to the input CSV file.")
args = parser.parse_args()
file_path = args.input_file

def validate(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            # Check if file is empty
            if not rows:
                print("Error: CSV file is empty.")
                return False

            # Ensure required columns are present
            required_columns = {'ka', 'short_ka', '#knowledge_units', 'cs_core_hours',
                                'ka_core_hours', 'page_begin', 'page_end'}
            csv_columns = set(rows[0].keys())

            if not required_columns.issubset(csv_columns):
                missing_cols = required_columns - csv_columns
                print(f"Error: Missing required columns: {missing_cols}")
                return False

            # Validate page numbers
            for i, row in enumerate(rows):
                try:
                    current_begin = int(row['page_begin'])
                    current_end = int(row['page_end'])

                    if current_end <= current_begin:
                        print(f"Error on row {i+2}: 'end_page' ({current_end}) is not greater than 'begin_page' ({current_begin}).")
                        return False
                except ValueError:
                    print(f"Error: Non-numeric page value on row {i+2}.")
                    return False

            # Check consecutive page continuity
            for i in range(len(rows) - 1):
                try:
                    current_end = int(rows[i]['page_end'])
                    next_begin = int(rows[i + 1]['page_begin'])

                    if current_end + 1 != next_begin:
                        print(f"Error: Page {current_end} is not immediately followed by {next_begin} (Row {i+2} → Row {i+3}).")
                        return False
                except ValueError:
                    print(f"Error: Invalid page number at Row {i+2}.")
                    return False

        print("CSV file is valid.")
        return True

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# Run the validation function
validate(file_path)
