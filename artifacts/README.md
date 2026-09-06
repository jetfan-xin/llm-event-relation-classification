# Original workflow and experiment outputs

These are the saved seminar artifacts, not newly generated model results. Original filenames and folder structure are retained under `original/`. Existing final datasets and the confusion-matrix image are linked without duplicate copies.

## Follow the recorded workflow

| Stage | Inspect or download | What is actually saved |
| --- | --- | --- |
| Collection | [Original collection](original/semantic-networks_total/data/output.json) | 10,341 ConceptNet records across four relations. |
| Evaluation input | [Retained input](../data/event_pairs.json) | 10,336 records after the recorded exclusions; see [version differences](../docs/data.md). |
| Preliminary generation | [Early checkpoint](original/generated_relations_progress.json) | 820 `Causes` records, kept as a preliminary snapshot, not a separate evaluated experiment. |
| Complete generation checkpoint | [4,000-record checkpoint](original/semantic-networks_total/data/generated_relations_progress.json) | 1,000 records per reference relation, including the `dry -> dry` record absent from the final archive. |
| Final predictions | [3,999-record output](../data/predictions.json) | Three initial model responses per record, label counts, selected relations and explanations. |
| Numerical evaluation | [Evaluation Scores.xlsx](original/semantic-networks/result/Evaluation%20Scores.xlsx) | Both original worksheets, cell values and formatting. One absolute save-path metadata element has been removed for privacy. |
| Visual evaluation | [Original confusion matrix](../evidence/historical-confusion-matrix.png) | The saved figure, including its documented one-record normalization discrepancy. |
| Error filtering | [Filtered HasSubevent predictions](original/semantic-networks_total/data/filtered_has_subevent.json) | 1,340 records from the original exact-string filter. This is not the normalized total of 1,344. |
| Error enrichment | [Enriched filtered records](original/semantic-networks_total/data/enriched_filtered_data.json) | The same 1,340 records with the original assertion text added. |
| Qualitative error review | [Targeted error sample](original/semantic-networks_total/data/random_relations.json) | 30 records: 10 each from `Causes`, `HasFirstSubevent` and `HasLastSubevent` predicted as `HasSubevent`. This is not a representative random evaluation set. |

The workbook's "One-Time Generation" results use the historical second-response fallback for invalid first labels. Its FF-RNN comparison values have no supplied source, split or implementation; they remain visible as original material but are not a verified project baseline. See [the evaluation audit](../docs/results.md) before interpreting these numbers.

## Saved semantic-network visualizations

| Original HTML snapshot | Embedded nodes | Embedded edges | Browser screenshot |
| --- | ---: | ---: | --- |
| [Working-folder filtered graph](original/semantic-networks/visualizations/Filtered%20Semantic%20Network.html) | 69 | 82 | [PNG](../evidence/screenshots/filtered-network.png) |
| [Expanded-folder root filtered graph](original/semantic-networks_total/Filtered%20Semantic%20Network.html) | 69 | 82 | [PNG](../evidence/screenshots/filtered-network-root.png) |
| [Expanded-folder filtered graph](original/semantic-networks_total/visualizations/Filtered%20Semantic%20Network.html) | 194 | 246 | [PNG](../evidence/screenshots/filtered-network-expanded.png) |
| [K-core graph, k = 2](original/semantic-networks_total/visualizations/K-core%20Semantic%20Network%28k%3D2%29.html) | 278 | 353 | [PNG](../evidence/screenshots/k-core-network.png) |
| [Original connected-event graph](original/semantic-networks_total/visualizations/Original%20Semantic%20Network%20of%20Connected%20Events.html) | 1,978 | 2,064 | [PNG](../evidence/screenshots/connected-event-network.png) |

Counts are read directly from each HTML file's embedded node and edge arrays. These files are distinct saved views, not five independent experiments. Their exact run order and generation settings are not fully recorded. Historical label-based node identifiers can merge concepts that have the same text; the maintained exporter uses concept IDs and can therefore produce different graph sizes.

**How to view:** download or clone the repository, preserve its directory structure, and open an HTML file in a browser. GitHub displays the source rather than executing the visualization. The original pages load pinned vis-network and Bootstrap resources from public CDNs, so an internet connection is required and those CDNs receive ordinary browser requests. The required local Pyvis helper is included at each expected relative path with its [BSD license](../third_party/pyvis-LICENSE_BSD.txt).

The HTML files are byte-identical to the supplied originals. All five pages were rendered in an isolated Chrome session and their actual graph canvases captured, with node/edge counts and absence of runtime exceptions checked. This verifies rendering, not every interactive control. The browser used the original data and styles, stabilized physics for up to 1,000 iterations, stopped movement and fitted the network to its canvas. Layout positions can vary between captures; these PNGs are browser previews of saved HTML, not original seminar-era screenshot files or newly generated model results.

The [capture manifest](../evidence/screenshots/capture-manifest.json) records source and image hashes, dimensions and graph counts. The [capture script](../tools/capture_visualizations.mjs) uses an installed Chrome and Node.js 22 without npm packages or a browser download. Its temporary profile is removed after Chrome exits. These saved views remain separate from the maintained package's optional HTML export.

## Original analysis scripts

- [filter.py](../pipeline/filter.py): selects exact-string `HasSubevent` predictions.
- [merge.py](../pipeline/merge.py): adds original assertion text to selected records.
- [random_filter.py](../pipeline/random_filter.py): selects the targeted error sample.
- [analyzer.py](../pipeline/analyzer.py): prints targeted error cases with labels, model explanations and original assertion text.

All code is organized in the [complete pipeline source directory](../pipeline/README.md), separately from data and results. Original scripts retain their relative-path conventions; the source guide includes a direct command for running the original error analyzer, and the [usage guide](../docs/usage.md) covers the tested command-line interface.

## Integrity and privacy

Every original artifact is mapped to its source hash in the [source manifest](../source-manifest.json). All newly included files are byte-identical to their source except the workbook ZIP container: only `x15ac:absPath` in `xl/workbook.xml` was removed. Every other ZIP member's uncompressed bytes, including worksheets, shared strings, styles and document properties, are unchanged. The author's name and document timestamps remain. The [narrow metadata-redaction utility](../tools/sanitize_workbook_metadata.py) documents this operation.

No model requests were made to fill gaps or improve the recorded results. Original source files were not modified. Old Git history, the redundant ZIP, virtual environments and unnecessary dependency trees remain excluded. Privacy and credential scans are publication checks, not a guarantee that a dataset contains no potentially sensitive commonsense statements. See [rights and attribution](../RIGHTS_AND_ATTRIBUTION.md).
