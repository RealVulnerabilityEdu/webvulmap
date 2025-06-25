import json
import random
import pandas as pd

def load_and_merge_json(files):
    combined = {}

    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            for topic, cwe_list in data.items():
                if topic not in combined:
                    combined[topic] = {}
                for cwe_obj in cwe_list:
                    # Skip invalid entries
                    if "cwe" not in cwe_obj:
                        continue
                    cwe_id = cwe_obj["cwe"]
                    if cwe_id not in combined[topic]:
                        combined[topic][cwe_id] = cwe_obj

    # Convert sets back to lists
    return {topic: list(cwe_dict.values()) for topic, cwe_dict in combined.items()}

def write_combined_json(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def create_sample_csvs_strict(data, sample_size, output_prefix):
    all_topics = list(data.keys())
    max_possible = len(all_topics) // 2
    sample_size = min(sample_size, max_possible)

    print(f"Using sample size: {sample_size} (out of {len(all_topics)} available topics)")

    # Shuffle and split topics
    random.shuffle(all_topics)
    topics1 = all_topics[:sample_size]
    topics2 = all_topics[sample_size:sample_size*2]

    def build_sample(topics_subset):
        mappings = []
        for topic in topics_subset:
            if not data[topic]:
                continue  # skip if no CWE entries
            cwe_obj = random.choice(data[topic])
            mapping = f"{topic} -> {cwe_obj['cwe']}"
            mappings.append(mapping)
        return mappings

    def make_df(mappings):
        return pd.DataFrame({
            "mapping": mappings,
            "accepted": ["" for _ in mappings],
            "rejected": ["" for _ in mappings],
            "comments": ["" for _ in mappings],
            "human": ["" for _ in mappings]
        })

    df1 = make_df(build_sample(topics1))
    df2 = make_df(build_sample(topics2))

    df1.to_csv(f"{output_prefix}_sample1.csv", index=False)
    df2.to_csv(f"{output_prefix}_sample2.csv", index=False)

# === RUN CONFIGURATION ===
input_files = ["Zero_Shot_Mapping.json", "Chain_Of_Thoughts_Mapping.json", "Deepseek_Mappings.json"]
combined_json_path = "combined_output.json"
sample_size = 8

# Process pipeline
combined_data = load_and_merge_json(input_files)
write_combined_json(combined_data, combined_json_path)
create_sample_csvs_strict(combined_data, sample_size, "validation")