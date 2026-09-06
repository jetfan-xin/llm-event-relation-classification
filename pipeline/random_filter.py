import json
import random

# Load the JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Save JSON file
def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Filter and randomly select relations
def select_random_relations(data, relation_types, num_relations=10):
    selected_relations = {relation_type: [] for relation_type in relation_types}

    for relation_type in relation_types:
        for relation in data.get(relation_type, []):
            selected_relations[relation_type].append(relation)

    # Randomly pick 10 relations for each type
    for relation_type in relation_types:
        selected_relations[relation_type] = random.sample(
            selected_relations[relation_type], min(num_relations, len(selected_relations[relation_type]))
        )

    return selected_relations

# Main execution
if __name__ == "__main__":
    input_file = r"data/enriched_filtered_data.json"
    output_file = r"data/random_relations.json"

    # Relation types to include
    relation_types = ["Causes", "HasFirstSubevent", "HasLastSubevent"]

    # Load data
    data = load_json(input_file)

    # Select random relations
    random_relations = select_random_relations(data, relation_types)

    # Save the result
    save_json(random_relations, output_file)

    print(f"Randomly selected relations saved to {output_file}")
