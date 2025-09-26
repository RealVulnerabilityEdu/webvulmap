import json
import jsonschema

with open("curriculum/cs2023/SE_SAMPLE_v2.json") as f:
    instance = json.load(f)

with open("curriculum/cs2023/k.schema.v2.json") as f:
    schema = json.load(f)

try:
    jsonschema.validate(instance=instance, schema=schema)
    print("Schema validation passed!")
except jsonschema.ValidationError as e:
    print("Schema validation failed:")
    print(e)