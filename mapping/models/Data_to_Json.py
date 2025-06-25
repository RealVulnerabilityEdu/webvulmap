import json
import pandas as pd

input_csv_path = 'CS2023_ka_meta.csv'
output_json_path = 'knowledge_areas_final.json'

df = pd.read_csv(input_csv_path, encoding='utf-8-sig')

knowledge_structure = {}

for _, row in df.iterrows():
    ka = row['ka'].strip()
    ku_list_raw = row['knowledge_unit']
    if pd.isna(ku_list_raw):
        continue

    # Split by comma and clean whitespace
    ku_list = [ku.strip() for ku in ku_list_raw.split(',') if ku.strip()]

    if ka and ku_list:
        knowledge_structure[ka] = ku_list

# Write final output
with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(knowledge_structure, jsonfile, indent=4, ensure_ascii=False)

print(f"Output saved to {output_json_path}")

