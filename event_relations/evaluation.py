"""Offline metrics that account for every row, including invalid predictions."""

from collections import Counter

RELATIONS = ("Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent")
INVALID = "Invalid"


def normalize(value):
    if not isinstance(value, str):
        return INVALID
    value = value.strip()
    for prefix in ("/r/", "r/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value if value in RELATIONS else INVALID


def records(data):
    if not isinstance(data, dict) or not data or not set(data) <= set(RELATIONS):
        raise ValueError("Input must map supported relation names to event lists")
    for gold, rows in data.items():
        if not isinstance(rows, list):
            raise ValueError("Each relation must contain a list")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Each event record must be an object")
            for side in ("start", "end"):
                if not isinstance(row.get(side), dict) or not isinstance(row[side].get("label"), str):
                    raise ValueError("Each endpoint requires a string label")
                if not isinstance(row[side].get("@id"), str) or not row[side]["@id"]:
                    raise ValueError("Each endpoint requires a nonempty @id")
            yield gold, row


def prediction(row, strategy):
    samples = row.get("generated_relations", [])
    if not isinstance(samples, list):
        raise ValueError("generated_relations must be a list")
    def label(obj):
        return normalize(obj.get("Relation")) if isinstance(obj, dict) else INVALID
    if strategy == "selected":
        return label(row.get("final_relation"))
    if strategy not in ("first", "historical-first"):
        raise ValueError("Unknown evaluation strategy")
    first = label(samples[0]) if samples else INVALID
    if strategy == "historical-first" and first == INVALID and len(samples) > 1:
        return label(samples[1])
    return first


def evaluate(data, strategy="selected"):
    matrix = {gold: {pred: 0 for pred in (*RELATIONS, INVALID)} for gold in RELATIONS}
    seen = Counter()
    for gold, row in records(data):
        matrix[gold][prediction(row, strategy)] += 1
        seen[(gold, row["start"]["@id"], row["end"]["@id"])] += 1
    total = sum(sum(row.values()) for row in matrix.values())
    if not total:
        raise ValueError("No records to evaluate")
    metrics = {}
    for rel in RELATIONS:
        tp = matrix[rel][rel]
        support = sum(matrix[rel].values())
        fp = sum(matrix[g][rel] for g in RELATIONS if g != rel)
        fn = support - tp
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / support if support else 0
        metrics[rel] = dict(support=support, tp=tp, fp=fp, fn=fn,
                            precision=precision, recall=recall,
                            f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0)
    correct = sum(matrix[r][r] for r in RELATIONS)
    return dict(strategy=strategy, total=total, correct=correct, accuracy=correct / total,
                macro_f1=sum(m["f1"] for m in metrics.values()) / len(RELATIONS),
                invalid_predictions=sum(matrix[r][INVALID] for r in RELATIONS),
                duplicate_relation_pairs=sum(c - 1 for c in seen.values()),
                per_relation=metrics, confusion_matrix=matrix)


def compare(data):
    results = {s: evaluate(data, s) for s in ("first", "historical-first", "selected")}
    results["paired_changes"] = dict(improved=0, regressed=0, both_correct=0, both_wrong=0)
    for gold, row in records(data):
        a, b = prediction(row, "first") == gold, prediction(row, "selected") == gold
        key = "both_correct" if a and b else "regressed" if a else "improved" if b else "both_wrong"
        results["paired_changes"][key] += 1
    return results
