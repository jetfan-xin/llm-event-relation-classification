import json

# Load filtered data with /r/HasSubevent relations
with open("data/filtered_has_subevent.json", "r") as filtered_file:
    filtered_data = json.load(filtered_file)

# Load output data containing text fields
with open("data/output.json", "r") as output_file:
    output_data = json.load(output_file)

# Relation types to process
relation_types = ["Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent"]

# Create a dictionary for quick lookup of text by start and end IDs in output data
text_lookup = {}
for relation_type in relation_types:
    for relation in output_data.get(relation_type, []):
        start_id = relation["start"]["@id"]
        end_id = relation["end"]["@id"]
        text_lookup[(start_id, end_id)] = relation.get("text", "")

# Enrich filtered data with text from output data
for relation_type in relation_types:
    for relation in filtered_data.get(relation_type, []):
        start_id = relation["start"]["@id"]
        end_id = relation["end"]["@id"]
        # Add text if it exists in the output data
        relation["text"] = text_lookup.get((start_id, end_id), "")

# Save the enriched data to a new JSON file
with open("data/enriched_filtered_data.json", "w") as enriched_file:
    json.dump(filtered_data, enriched_file, indent=4)

print("Filtered data has been enriched and saved to 'enriched_filtered_data.json'.")
