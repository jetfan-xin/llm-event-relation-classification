import json

# 加载JSON文件
DATA_PATH = "random_relations.json"

with open(DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)


def extract_errors(data):
    results = []

    # 遍历所有关系
    for relation, examples in data.items():
        for example in examples:
            # 确定预测关系为 HasSubevent，但实际不是 HasSubevent
            predicted_relation = example["final_relation"]["Relation"]
            if predicted_relation == "/r/HasSubevent" and relation != "HasSubevent":
                start_event = example["start"]["label"]
                end_event = example["end"]["label"]
                reason = example["final_relation"]["Reason"]
                original_relation = relation
                text = example["text"]

                # 添加到结果列表
                results.append({
                    "Event Pair": f"{start_event} -> {end_event}",
                    "Predicted Relation": predicted_relation,
                    "Reason": reason,
                    "Original Relation": original_relation,
                    "Text": text
                })
    return results


def display_errors(errors):
    print(f"Find {len(errors)} wrong relations：\n")
    for idx, error in enumerate(errors, 1):
        print(f"Error {idx}:")
        print(f"Event Pair: {error['Event Pair']}")
        print(f"Predicted Relation: {error['Predicted Relation']}")
        print(f"Reason: {error['Reason']}")
        print(f"Original Relation: {error['Original Relation']}")
        print(f"Text: {error['Text']}")
        print("-" * 50)


# 执行提取与展示
errors = extract_errors(data)
display_errors(errors)