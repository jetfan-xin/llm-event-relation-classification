"""Bounded multi-sampling with exact label voting and explicit abstentions."""

from collections import Counter
import hashlib
import json

from archive.prompt_library import prompt_rel, example_list, definition_list
from .evaluation import INVALID, RELATIONS, normalize


def compose_prompt(start, end, allowed=RELATIONS, version="corrected"):
    if version not in ("historical", "corrected") or not allowed or not set(allowed) <= set(RELATIONS):
        raise ValueError("Unsupported prompt version or candidate labels")
    examples, definitions = [], []
    for i, label in enumerate(allowed):
        index = RELATIONS.index(label)
        example = example_list[index]
        if version == "corrected" and label == "Causes":
            example = example.replace("- A: fire\n- B: lighting a match", "- A: lighting a match\n- B: fire")
        examples.append(example.format(i=i + 1))
        definitions.append(definition_list[index])
    return prompt_rel.format(event_A=start, event_B=end,
                             examples="".join(examples), definitions="".join(definitions))


def parse_response(text):
    if not isinstance(text, str):
        return {"Relation": INVALID, "Reason": "Missing text response"}
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        obj = json.loads(text)
    except (ValueError, TypeError):
        return {"Relation": INVALID, "Reason": "Invalid JSON response"}
    if not isinstance(obj, dict) or not isinstance(obj.get("Reason"), str):
        return {"Relation": INVALID, "Reason": "Invalid response schema"}
    rel = normalize(obj.get("Relation"))
    return {"Relation": "/r/" + rel if rel != INVALID else INVALID, "Reason": obj["Reason"]}


def classify(start, end, complete, version="corrected"):
    prompt = compose_prompt(start, end, version=version)
    samples = [parse_response(complete(prompt)) for _ in range(3)]
    counts = Counter(normalize(s["Relation"]) for s in samples if normalize(s["Relation"]) != INVALID)
    maximum = max(counts.values(), default=0)
    final = {"Relation": INVALID, "Reason": "No valid majority"}
    tie_break = None
    if maximum >= 2:
        winner = next(label for label in RELATIONS if counts[label] == maximum)
        final = next(s for s in samples if normalize(s["Relation"]) == winner)
    elif len(counts) >= 2:
        allowed = tuple(label for label in RELATIONS if counts[label])
        tie_break = parse_response(complete(compose_prompt(start, end, allowed, version)))
        if normalize(tie_break["Relation"]) in allowed:
            final = tie_break
    return dict(generated_relations=samples, relation_counts={r: counts[r] for r in RELATIONS},
                final_relation=final, tie_break=tie_break,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
