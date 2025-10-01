"""
Temporary test file for v2 schema development
Will be updated/replaced once parser integration is complete
"""

import json

from jsonschema import validate


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_all_ids(sections):
    ids = set()

    def collect(section):
        ids.add(section["id"])
        for lo in section.get("learning_outcomes", []):
            ids.add(lo["id"])
        for b in section.get("bullets", []):
            ids.add(b["id"])
            for sb in b.get("subbullets", []):
                ids.add(sb["id"])
        for s in section.get("subsections", []):
            collect(s)

    for s in sections:
        collect(s)
    return ids


def get_orders(sections):
    orders = []

    def collect(section):
        orders.append(section["order"])
        for s in section.get("subsections", []):
            collect(s)

    for s in sections:
        collect(s)
    return orders


def test_sample_v2_schema_valid():
    schema = load_json("curriculum/cs2023/ka.schema.v2.json")
    sample = load_json("curriculum/cs2023/SE_SAMPLE_v2.json")
    validate(instance=sample, schema=schema)


def test_ids_unique():
    sample = load_json("curriculum/cs2023/SE_SAMPLE_v2.json")
    all_ids = list(get_all_ids(sample["sections"]))
    assert len(all_ids) == len(set(all_ids)), "Duplicate IDs found"


def test_order_strictly_increasing():
    sample = load_json("curriculum/cs2023/SE_SAMPLE_v2.json")
    orders = get_orders(sample["sections"])
    assert orders == sorted(
        orders), "Section orders are not strictly increasing"
