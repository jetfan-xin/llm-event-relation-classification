# LLM Event-Relation Classification

Classifying how events relate to one another with language models, then examining the predictions as a semantic network.

**Knowledge Processing seminar, University of Hamburg | 2024–2025 team project**

Does one event cause another, contain it as a subevent, or begin or end with it? This project uses ConceptNet event pairs to study that distinction through definition-based prompting, three-sample classification, tie-breaking and graph-based error analysis.

I implemented data collection, prompt construction and relation generation, evaluation comparisons, and semantic-network visualization. The project was developed with Abdullah Abdelhafez; the retained Git history also records his work on comparison and error-analysis utilities. See [project context and contributions](docs/project.md).

## What the project contains

- **Event-relation pipeline:** ConceptNet collection, structured prompts, three model responses per pair, exact-label voting and a candidate-restricted tie-break.
- **Evaluation:** precision, recall, macro F1, confusion matrices and paired comparisons, with invalid predictions retained in the denominator.
- **Semantic-network analysis:** concept-ID-based graphs, parallel relation edges, k-core filtering and bounded neighborhood exploration.
- **Reproducibility:** 3,999 archived prediction records, original prompts, source hashes, offline tests and resumable opt-in generation.

The archived experiment requested `gpt-4o` through an OpenAI-compatible third-party endpoint. The saved records do not identify an immutable model snapshot. It was a prompting experiment, not model training or fine-tuning.

## Results in context

| Evaluation strategy | Accuracy | Macro F1 | Invalid predictions |
| --- | ---: | ---: | ---: |
| Strict first response | 59.54% | 0.6038 | 4 |
| Historical first-response evaluation, with fallback | 59.59% | 0.6039 | 0 |
| Multi-sampling selection | 60.24% | 0.6099 | 0 |

Multi-sampling produces a modest improvement. The more useful finding is the error structure: the model often assigns the broad `HasSubevent` label where ConceptNet distinguishes causal, initial or final subevents. These scores measure agreement with the archived ConceptNet labels, not universally correct semantic judgments. [Detailed results and limitations](docs/results.md)

## Try it without an API key

Python 3.10 or newer. Evaluation and graph JSON export require no installed packages, credentials or network access. Run these commands from the repository root:

```bash
python3 -B -m event_relations evaluate data/predictions.json
python3 -B -m event_relations graph data/predictions.json --labels selected --k 2 --hops 2
python3 -B -m unittest discover -s tests -v
python3 -B tools/verify_repository.py
```

For optional model generation and interactive Pyvis visualization, see [usage](docs/usage.md). Generation requires explicit opt-in, reads credentials from the environment and checkpoints completed pairs. No paid model calls are part of the tests.

## Explore

- [Project context](docs/project.md): research question, contributions and technology choices.
- [Method and implementation](docs/method.md): relation definitions, sampling, graph conventions and implementation fixes.
- [Results](docs/results.md): all evaluation strategies and the difference between stored figures and recomputed metrics.
- [Data and provenance](docs/data.md): dataset sizes, duplicates, source versions and publication decisions.
- [Usage](docs/usage.md): commands, checkpoint behavior and optional dependencies.
- [Archived scripts](archive/README.md): reference code with credentials replaced by `xxx`.

This work includes ConceptNet-derived data under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Attribution, team-code ownership and data limitations are described in [rights and attribution](RIGHTS_AND_ATTRIBUTION.md). Some commonsense assertions contain offensive or sensitive language; their inclusion is not an endorsement.
