"""Validate JSON schema for knowledge areas."""

import json
import sys

from jsonschema import ValidationError, validate

SCHEMA_PATH = "curriculum/cs2023/k.schema.v2.json"


def main(json_file):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(json_file, "r", encoding="utf-8") as f:
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
