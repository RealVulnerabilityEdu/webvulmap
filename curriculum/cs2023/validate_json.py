import json
from jsonschema import validate, ValidationError
import sys

SCHEMA_PATH = "k.schema.v2.json"

def main(json_file):
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)
    with open(json_file, "r") as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=schema)
        print(f"{json_file} is valid ✅")
    except ValidationError as e:
        print(f"{json_file} is INVALID ❌")
        print(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_json.py <json_file>")
    else:
        main(sys.argv[1])