import json

CLAIM_IDS_TO_REMOVE = ["insuff_02"]

with open("evaluation/results.json", encoding="utf-8") as f:
    data = json.load(f)

before = len(data["detailed_results"])
data["detailed_results"] = [
    r for r in data["detailed_results"] if r["id"] not in CLAIM_IDS_TO_REMOVE
]
after = len(data["detailed_results"])

with open("evaluation/results.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Removed {before - after} entries. {after} results remain.")