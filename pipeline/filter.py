import json

total = 0
correctCount = 0
DATA_PATH = 'data/generated_relations_final.json'
relations = ["Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent"]
with open(DATA_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)

# Filter entries where final_relation is /r/HasSubevent
filtered_data = {
    relation: [
        example for example in examples
        if example.get("final_relation", {}).get("Relation") == "/r/HasSubevent"
    ]
    for relation, examples in data.items()
}

# Remove empty relation keys
filtered_data = {relation: examples for relation, examples in filtered_data.items() if examples}

# Save filtered data to a JSON file
output_file = "filtered_has_subevent.json"
with open(output_file, "w") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtered data saved to {output_file}")
