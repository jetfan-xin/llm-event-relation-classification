import json
import re
from openai import OpenAI
from prompt_library import *
DATA_PATH = r'data/output_wo_example.json'
SAVE_PATH = r'data/generated_relations_progress.json'
FINAL_PATH = r'data/generated_relations_final.json'
SAVE_INTERVAL = 10  # Save the progress every 10 iterations
MAX_COUNT = 1000 # Maximum number of event pairs to process per relation type

client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    api_key="xxx",
)

class GenerateRelation:
    def __init__(self):
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

        # Try to load the progress file to resume from the last checkpoint
        try:
            with open(SAVE_PATH, 'r', encoding='utf-8') as progress_file:
                self.output = json.load(progress_file)
                for rel in self.data.keys():
                    if rel not in self.output.keys():
                        self.output[rel] = []
                print("Progress loaded successfully.")
        except FileNotFoundError:
            print("No progress file found. Starting fresh.")
            self.output = {rel: [] for rel in self.data.keys()}

    def compose_prompt(self, start, end, rels):
        """
        Create a prompt based on the input events and the selected relations.

        Args:
            start (str): The starting event.
            end (str): The ending event.
            rels (list): List of relations to include in the prompt.

        Returns:
            str: The generated prompt.
        """
        examples = ""
        definitions = ""
        for id, r in enumerate(rels):
            examples += example_list[r].format(i=id+1)
            definitions += definition_list[r]
        prompt = prompt_rel.format(event_A=start, event_B=end, examples=examples,definitions=definitions)
        return prompt

    def generate_relation(self, prompt):
        """
        Generate a response using the GPT model based on the given prompt.

        Args:
           prompt (str): The input prompt.

        Returns:
           str: The GPT model's response.
        """
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def extract_relation_and_reason(self, response):
        """
        Extract the relation and reason from a GPT-generated response.

        Args:
            response (str): The GPT model's response.

        Returns:
            dict: A dictionary containing the relation and reason, or an empty dictionary if extraction fails.
        """
        # Regular expression to match the JSON object between '{' and '}'
        json_pattern = re.search(r"\{.*?\}", response, re.DOTALL)
        if json_pattern:
            json_text = json_pattern.group(0)
            try:
                # Parse the JSON string into a Python dictionary
                return json.loads(json_text)
            except json.JSONDecodeError:
                print("Failed to parse JSON.")
                return {}
        else:
            print("No JSON object found.")
            return {}

    def main(self):
        for rel, events in self.data.items():
            existing_count = len(self.output[rel])
            # Skip if all events for this relation type are already processed
            if existing_count >= min(len(events), MAX_COUNT):
                print(f"Skipping completed relation type: {rel}")
                continue
            # Process unprocessed events, respecting MAX_COUNT
            for count, ev in enumerate(events[existing_count:MAX_COUNT], start=existing_count + 1):
                event_output = {"start": ev["start"], "end": ev["end"]}
                start = ev['start']['label']
                end = ev['end']['label']

                # Generate the prompt and collect responses
                prompt = self.compose_prompt(start, end, rels=range(4))

                responses = []
                rel_rea_dicts = []
                for i in range(3):  # Repeat the generation 3 times
                    try:
                        responses.append(self.generate_relation(prompt))
                    except Exception as e:
                        print(f"Error during generation: {e}")
                        responses.append("{\"Relation\": \"\", \"Reason\": \"\"}")
                    rel_rea_dicts.append(self.extract_relation_and_reason(responses[-1]))
                event_output["generated_relations"] = rel_rea_dicts

                # Count the frequency of each relation type
                rel_type_counts = {"Causes":0, "HasSubevent":0, "HasFirstSubevent":0, "HasLastSubevent":0}
                for rel_rea_dict in rel_rea_dicts:      # identify relation types
                    for rel_type in rel_type_counts.keys():
                        if rel_type in rel_rea_dict['Relation']:
                            rel_type_counts[rel_type] += 1
                event_output["relation_counts"] = rel_type_counts

                # Handle ties: if the counts are like (1, 1, 1), regenerate
                if max(rel_type_counts.values()) == 1:
                    non_zero_indices = [index for index, value in enumerate(rel_type_counts.values()) if value != 0]
                    prompt = self.compose_prompt(start, end, rels=non_zero_indices)
                    try:
                        response = self.generate_relation(prompt)
                    except Exception as e:
                        print(f"Error during regeneration: {e}")
                        response = "{\"Relation\": \"\", \"Reason\": \"\"}"
                    event_output["final_relation"] = self.extract_relation_and_reason(response)

                # Pick the most frequent relation type
                else:
                    max_key = max(rel_type_counts, key=rel_type_counts.get)
                    for response in rel_rea_dicts:
                        if max_key in response['Relation']:
                            event_output["final_relation"] = response
                            break

                # Append the result to the output
                self.output[rel].append(event_output)
                # Save progress every 10 iterations
                if count % SAVE_INTERVAL == 0:
                    with open(SAVE_PATH, 'w', encoding='utf-8') as gr_f:
                        json.dump(self.output, gr_f, indent=4, ensure_ascii=False)
                    print(f"Progress saved after {count} iterations for {rel}.")

                # Print the processed output
                print(json.dumps(event_output, indent=4, ensure_ascii=False))
                '''
                Real relation counts:
                # Causes: ~1833
                # HasSubevent: ~3505
                # HasFirstSubevent: ~2127
                # HasLastSubevent: ~2873
                '''
        # Save the final output
        with open(FINAL_PATH, 'w', encoding='utf-8') as gr_f:
            json.dump(self.output, gr_f, indent=4, ensure_ascii=False)
        print("Final output saved.")

generator = GenerateRelation()


prompt = generator.compose_prompt("tickling", 'laughter', rels=range(4))
print(prompt)
