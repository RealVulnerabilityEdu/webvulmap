import json
import random
import csv
import re
from pathlib import Path

# Load JSON data
json_path = Path("cwe_mappings4.json")
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Randomly select a Knowledge Area and Unit
knowledge_area = random.choice(list(data.keys()))
knowledge_units = list(data[knowledge_area].keys())
knowledge_unit = random.choice(knowledge_units)

# Extract and clean CWE entries to include only CWE ID and Name
raw_entries = data[knowledge_area][knowledge_unit]
cwe_entries = []
for entry in raw_entries:
    match = re.match(r"\s*\d+\.\s*(CWE-\d+):\s*([^—:]+)", entry)
    if match:
        cwe_id, cwe_name = match.groups()
        cwe_entries.append(f"{cwe_id}: {cwe_name.strip()}")

# Prepare CSV data
csv_rows = [["Knowledge Area Name", knowledge_area],
            ["Knowledge Unit", knowledge_unit],
            ["CWE ID and Name", "Accept", "Reject", "Why"]]

for cwe in cwe_entries:
    csv_rows.append([cwe, "", "", ""])

# Write to CSV file
output_csv_path = "random_knowledge_cwe.csv"
with open(output_csv_path, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)

print(f"CSV saved to {output_csv_path}")