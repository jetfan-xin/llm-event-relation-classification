prompt_rel = """
Task: \"\"\"
You are tasked with identifying the most appropriate relationship between two event nodes (A and B) from the following predefined relationships. Provide a concise explanation for your choice, considering the definitions of each relation and the logical connection between the events.
\"\"\"

Available Relations Definitions: \"\"\"{definitions}
\"\"\"

Instructions: \"\"\"
You will be given two event nodes (A and B). Your task is to:
1. Analyze the relationship between the events.
2. Select one of the predefined relationships based on the analysis.
3. Provide a brief explanation that justifies your choice.
\"\"\"

Examples: \"\"\"
Note: These are examples of how someone might complete similar tasks, and they are not directly related to this task.
{examples}\"\"\"

Input: \"\"\"
- A: {event_A}
- B: {event_B}
\"\"\"

When responding, please use JSON format, and ensure that it adheres to Python's `json.loads` standard. Only fill in the placeholders {{}}.
Output format: \"\"\"
{{
    "Relation": "/r/{{Chosen Relation}}",
    "Reason": "{{Reason for choosing this relationship}}"
}}
\"\"\"
"""

example_list = ["""
Example {i}:
Input:
- A: fire
- B: lighting a match
Output:
- Relation: /r/Causes
- Reason: Lighting a match typically causes fire as a direct result.
"""
,
"""
Example {i}:
Input:
- A: attending school
- B: learn
Output:
- Relation: /r/HasSubevent
- Reason: Learning is an activity that occurs as a part of attending school.
"""
,
"""
Example {i}:
Input:
- A: wake up
- B: open your eyes
Output:
- Relation: /r/HasFirstSubevent
- Reason: Opening your eyes typically marks the beginning of waking up.
"""
,
"""
Example {i}:
Input:
- A: take a shower
- B: dry off
Output:
- Relation: /r/HasLastSubevent
- Reason: Drying off is usually the final step in the process of taking a shower.
"""]

definition_list = [
"""
-   /r/Causes: A and B are events, and it is typical for A to cause B.
    Example: exercise → sweat
    Explanation: Exercise typically leads to sweating as a consequence.
""",
"""
-   /r/HasSubevent: A and B are events, and B happens as a subevent of A.
    Example: eating → chewing
    Explanation: Chewing is a component of the broader activity of eating.
""",
"""
-   /r/HasFirstSubevent: A is an event that begins with subevent B.
    Example: sleep → close eyes
    Explanation: Closing one's eyes typically marks the beginning of sleep.
""",
"""
-   /r/HasLastSubevent: A is an event that concludes with subevent B.
    Example: cook → clean up kitchen
    Explanation: Cleaning up the kitchen is commonly the final step in the cooking process.
"""
]

improved_prompt_rel = """
Task: \"\"\"
You are tasked with evaluate whether a given relationship exists between two event nodes (A and B). Provide a concise explanation supporting or rejecting the existence of the relation based on the relation definition and the logical connection between the events.
\"\"\"

Available Relations Definition: \"\"\"{definitions}
\"\"\"

Instructions: \"\"\"
You will be given two event nodes (A and B) and a relation to evaluate. Your task is to:
1. Determine if the specified relationship exists between two events.
2. Respond to the existence with either "True" or "False".
3. Provide a brief explanation that justifies your answer.
\"\"\"

Examples: \"\"\"
Note: These are examples of how someone might complete similar tasks, and they are not directly related to this task.
{improved_examples}\"\"\"

Input: \"\"\"
- A: {event_A}
- B: {event_B}
\"\"\"

When responding, please use JSON format, and ensure that it adheres to Python's `json.loads` standard. Only fill in the placeholders {{}}.
Output format: \"\"\"
{{
    "Relation": "/r/{{Chosen Relation}}",
    "Reason": "{{Reason for choosing this relationship}}"
}}
\"\"\"
"""

improved_example_list = [
"""
Example 1:
Input:
- A: fire
- B: lighting a match
- Relation to Evaluate: /r/Causes
Output:
- Relation: /r/Causes
- Exists: "True"
- Reason: Lighting a match typically causes fire as a direct result.

Example 2:
Input:
- A: fire
- B: lighting a match
- Relation to Evaluate: /r/Causes
Output:
- Relation: /r/Causes
- Exists: "False"
- Reason: Lighting a match typically causes fire as a direct result.
"""
]