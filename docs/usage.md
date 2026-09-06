# Running the project

## Offline evaluation

Run from the repository root with Python 3.10 or later:

```bash
python3 -B -m event_relations evaluate data/predictions.json
python3 -B -m unittest discover -s tests -v
python3 -B tools/verify_repository.py
```

The evaluator prints strict-first, historical-first-with-fallback and selected-response metrics. It accepts the archived relation-keyed format and the maintained generator's checkpoint envelope. It never calls a model or modifies input files.

## Graph analysis

```bash
python3 -B -m event_relations graph data/predictions.json --labels reference --k 2 --hops 2
python3 -B -m event_relations graph data/predictions.json --labels selected --k 2 --hops 2 --seed /c/en/eat
```

Output contains nodes, directed labelled edges, the selected seed, core size and excluded-row counts. A seed outside the selected core is an error. An empty core is returned explicitly, not treated as a plotting failure. The method document defines the projection and neighborhood conventions.

For optional interactive HTML, install the optional dependencies and call the small Python API:

```python
from pathlib import Path
from event_relations.graph import build_graph, render_html
from event_relations.io import read_json

graph = build_graph(read_json("data/predictions.json"), labels="selected", k=2, hops=2)
output = Path("outputs/network.html")
output.parent.mkdir(exist_ok=True)
with output.open("x", encoding="utf-8") as stream:
    stream.write(render_html(graph))
```

The export uses Pyvis with inline resources and does not auto-open a browser. Node identity remains a ConceptNet URI. This optional view is separate from the preserved historical heatmap.

## Optional dependencies

Core evaluation, graph JSON and collection use the Python standard library. Install only if model calls or Pyvis HTML are needed:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-cache-dir -r requirements-optional.txt
```

The OpenAI SDK is constrained to compatible major versions rather than claiming an exact historical environment lock. Pyvis is pinned to 0.3.2. Optional-dependency tests run separately in CI; a local skip is not evidence that the optional integrations were exercised.

## Model generation: explicit opt-in

The archived model name is `gpt-4o`. Access and endpoint compatibility depend on the account/provider; this repository does not promise historical model availability or identical responses. Set `OPENAI_API_KEY` in your environment without adding it to Git. `.env.example` contains only `xxx` and is illustrative; the program does not automatically load `.env` files.

```bash
python -B -m event_relations generate data/event_pairs.json \
  --output outputs/predictions.json \
  --model gpt-4o --limit 1 --prompt-version corrected \
  --allow-api-calls
```

Without `--allow-api-calls`, the command exits before creating an API client. The default limit is one pair per relation: up to four pairs, normally three requests each plus at most one tie-break per pair. Increasing the limit increases potential charges. The default endpoint is `https://api.openai.com/v1`; a compatible third-party endpoint must be specified explicitly with `--endpoint`. Credentials and event labels are sent to that endpoint when generation is enabled, so use only a provider you trust.

The client follows the [official Python SDK interface](https://developers.openai.com/api/reference/python) and [Chat Completions schema](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create). It uses a 30-second timeout, disables automatic SDK retries and caps each completion at 500 tokens. Models that do not support this Chat Completions configuration require an explicitly reviewed adapter change.

## Checkpoints and errors

Each completed pair is saved atomically with input and prompt hashes, model name, endpoint, prompt version and per-relation limit. Re-running the same command resumes only when configuration and input order match. Changing the prompt, model, input or limit requires a separate output path. Existing unrelated files and the input itself are not overwritten.

An API error stops the run with a redacted error category; earlier completed pairs remain saved. If a request succeeded remotely but the process failed before saving the pair, resuming can repeat requests and incur additional charges. Checkpointing is not an exactly-once billing guarantee. Do not run concurrent writers against the same checkpoint path.

Invalid model JSON is recorded as an invalid sample. Three initial attempts are bounded; no indefinite repair loop runs. A vote needs at least two matching valid labels. If two or more valid labels tie, one restricted tie-break is allowed; an invalid or out-of-candidate tie-break leaves an explicit abstention.

## Fresh ConceptNet collection

```bash
python3 -B -m event_relations collect --max-pages 1 --output outputs/conceptnet.json
```

This command makes network requests, unlike evaluation. It uses HTTPS, a timeout, a per-relation page bound and host validation for pagination. It does not overwrite an existing output. Both endpoint nodes must be English; fresh output retains assertion identifiers and available license/source metadata. API availability and provider rate limits are external dependencies. The command has been tested with fixtures, not used to download fresh data during repository preparation.

Fresh collections do not automatically reproduce the archived example exclusions or file-order sample. Preserve the collection version, explicitly remove prompt examples for a new controlled experiment and document its sampling policy before comparing results.
