import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
import pandas as pd

total = 0
correctCount = 0
DATA_PATH = 'data/generated_relations_final.json'
relations = ["Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent"]
with open(DATA_PATH, 'r', encoding='utf-8') as file:
        generated_data = json.load(file)


# Function to evaluate precision, recall, and F1-score
def evaluate_metrics(data):
    relation_types = list(data.keys())
    metrics = {rel: {"TP": 0, "FP": 0, "FN": 0} for rel in relation_types}

    # Calculate TP, FP, FN for each relation type
    for true_relation, examples in data.items():
        for example in examples:
            predicted_relation = example.get("final_relation", {}).get("Relation", "").replace("/r/", "")
            if 'r' in predicted_relation[:2]:
                predicted_relation = predicted_relation[2:]
            if predicted_relation == true_relation:
                metrics[true_relation]["TP"] += 1
            else:
                metrics[true_relation]["FN"] += 1
                metrics[predicted_relation]["FP"] += 1

    # Calculate Precision, Recall, and F1-Score for each relation type
    results = []
    for rel, counts in metrics.items():
        TP = counts["TP"]
        FP = counts["FP"]
        FN = counts["FN"]
        precision = TP / (TP + FP) if TP + FP > 0 else 0.0
        recall = TP / (TP + FN) if TP + FN > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0.0
        results.append({
            "Relation": rel,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1_score,
            "TP": TP,
            "FP": FP,
            "FN": FN
        })

    return pd.DataFrame(results)

def plot_heatmap(data):
    # Prepare data for the confusion matrix
    relation_types = list(data.keys())
    confusion_matrix = defaultdict(lambda: defaultdict(int))

    for true_relation, examples in data.items():
        for example in examples:
            predicted_relation = example["final_relation"]["Relation"].replace("/r/", "")
            confusion_matrix[true_relation][predicted_relation] += 1

    # Convert confusion matrix to a 2D array
    matrix = np.zeros((len(relation_types), len(relation_types)))

    for i, true_relation in enumerate(relation_types):
        for j, predicted_relation in enumerate(relation_types):
            matrix[i, j] = confusion_matrix[true_relation].get(predicted_relation, 0)

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt="g",
        cmap="Blues",
        xticklabels=relation_types,
        yticklabels=relation_types,
        cbar_kws={'label': 'Count'},
        annot_kws = {"size": 20}  # 增大注释文字大小
    )

    # plt.title("Confusion Matrix Heatmap for Multi-Sampling Selection")

    # plt.title("Confusion Matrix Heatmap for Multi-Sampling Selection", fontsize=15)
    plt.xlabel("Selected Relation", fontsize=18)
    plt.ylabel("True Relation", fontsize=18)

    # 使横纵坐标倾斜并设置字体大小
    plt.xticks(rotation=30, fontsize=12)
    plt.yticks(rotation=30, fontsize=12)

    # 调整色条标签字体
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=18)

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # 确保标题不会重叠
    plt.savefig(r"result/heatmap.png", dpi=300)  # 高分辨率保存

def evaluate_metrics_once(data):
    relation_types = list(data.keys())
    metrics = {rel: {"TP": 0, "FP": 0, "FN": 0} for rel in relation_types}

    # Calculate TP, FP, FN for each relation type
    for true_relation, examples in data.items():
        for example in examples:
            predicted_relation = example["generated_relations"][0]["Relation"].replace("/r/", "")
            if 'r' in predicted_relation[:2]:
                predicted_relation = predicted_relation[2:]
            if predicted_relation not in metrics.keys():
                predicted_relation = example["generated_relations"][1]["Relation"].replace("/r/", "")
                if 'r' in predicted_relation[:2]:
                    predicted_relation = predicted_relation[2:]
            if predicted_relation == true_relation:
                metrics[true_relation]["TP"] += 1
            else:
                metrics[true_relation]["FN"] += 1
                metrics[predicted_relation]["FP"] += 1

    # Calculate Precision, Recall, and F1-Score for each relation type
    results = []
    for rel, counts in metrics.items():
        TP = counts["TP"]
        FP = counts["FP"]
        FN = counts["FN"]
        precision = TP / (TP + FP) if TP + FP > 0 else 0.0
        recall = TP / (TP + FN) if TP + FN > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0.0
        results.append({
            "Relation": rel,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1_score,
            "TP": TP,
            "FP": FP,
            "FN": FN
        })

    return pd.DataFrame(results)

def plot_heatmap_once(data):
    # Prepare data for the confusion matrix
    relation_types = list(data.keys())
    confusion_matrix = defaultdict(lambda: defaultdict(int))

    for true_relation, examples in data.items():
        for example in examples:
            predicted_relation = example["generated_relations"][0]["Relation"].replace("/r/", "")
            confusion_matrix[true_relation][predicted_relation] += 1

    # Convert confusion matrix to a 2D array
    matrix = np.zeros((len(relation_types), len(relation_types)))

    for i, true_relation in enumerate(relation_types):
        for j, predicted_relation in enumerate(relation_types):
            matrix[i, j] = confusion_matrix[true_relation].get(predicted_relation, 0)

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt="g",
        cmap="Blues",
        xticklabels=relation_types,
        yticklabels=relation_types,
        cbar_kws={'label': 'Count'}
    )

    plt.title("Confusion Matrix Heatmap for One-Time Generation")
    plt.xlabel("Predicted Relation")
    plt.ylabel("True Relation")
    plt.show()

# Evaluate metrics
metrics = evaluate_metrics(generated_data)
print(metrics)
plot_heatmap(generated_data)

# Evaluate metrics
metrics_once = evaluate_metrics_once(generated_data)
print(metrics_once)
plot_heatmap_once(generated_data)
