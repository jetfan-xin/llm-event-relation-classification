# Results and evaluation audit

## Recomputed results

All numbers below come from the unchanged [prediction archive](../data/predictions.json). The executable command is:

```bash
python3 -B -m event_relations evaluate data/predictions.json
```

| Strategy | Correct / total | Accuracy | Macro F1 |
| --- | ---: | ---: | ---: |
| Strict first response | 2,381 / 3,999 | 59.54% | 0.603764 |
| Historical first response with fallback | 2,383 / 3,999 | 59.59% | 0.603910 |
| Multi-sampling selected response | 2,409 / 3,999 | 60.24% | 0.609947 |

The selected response improves accuracy by 0.70 percentage points over the strict first response, or 0.65 points over the historical fallback strategy. In the paired strict comparison, 120 incorrect first responses become correct, 92 correct responses become incorrect, 2,289 remain correct and 1,498 remain incorrect. The net difference is 28 records. No statistical-significance claim is made.

### Selected-response results by label

| Reference label | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Causes | 999 | 0.577922 | 0.712713 | 0.638279 |
| HasSubevent | 1,000 | 0.424851 | 0.571000 | 0.487201 |
| HasFirstSubevent | 1,000 | 0.771852 | 0.521000 | 0.622090 |
| HasLastSubevent | 1,000 | 0.808824 | 0.605000 | 0.692220 |

The clearest systematic issue is over-selection of `HasSubevent`: 773 of its 1,344 predicted instances disagree with the reference label. Broad subevent membership overlaps conceptually with initial and final subevents, so a forced single-label score alone does not settle which description is semantically defensible.

## Why the workbook and strict first-response metric differ

Four first responses use out-of-set labels. The archived evaluator substitutes the second sample in these cases, resulting in two additional correct predictions. Its sheet titled "One-Time Generation" therefore does not report a strictly first-response-only evaluation.

The maintained evaluator exposes this behavior as `historical-first`, while `first` counts all four as invalid predictions and false negatives. Both strategies retain all 3,999 records. The workbook's TP, FP and FN counts match the historical strategy exactly and are encoded as regression tests.

## Archived confusion-matrix image

![Archived selected-response confusion matrix](../evidence/historical-confusion-matrix.png)

This image is preserved, not silently edited. Its `HasSubevent -> HasFirstSubevent` cell displays **76**, whereas consistent label normalization gives **77**. One stored label uses `r/HasFirstSubevent`; the original plotting path only removed `/r/`, while the metric path applied an additional correction. The figure therefore accounts for 3,998 records, not 3,999. Use the maintained evaluator's JSON matrix for complete counts.

## Limits of interpretation

- The sample is almost balanced by relation and selected from file-order prefixes; it is not a representative random sample of ConceptNet.
- There are 135 repeated `(reference relation, start ID, end ID)` records. They remain in the archive to preserve the original denominator; these are not 3,999 independent unique examples.
- ConceptNet assertions can be ambiguous, offensive, incomplete or noisy. Its labels are the evaluation reference, not independently adjudicated ground truth.
- The prompt contains a reversed causal example. The corrected prompt has not been used to regenerate the archived experiment.
- There is no captured immutable model snapshot, seed, full API ledger, matched cost budget or repeated-run uncertainty estimate.
- Workbook values for an "FF-RNN Classifier" lack a supplied source, split and implementation. They are excluded from the headline comparison.
- The graph is a diagnostic view of the existing event pairs, not evidence that the model discovered a new causal network or validated real-world causality.
