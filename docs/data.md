# Data and source provenance

## Reviewed material

The supplied folder contains a working `semantic-networks` repository, an expanded `semantic-networks_total` folder, a ZIP snapshot, preliminary scripts and a WordNet exploration notebook. The nested Git repository contains uncommitted edits and deletions; it was not reset, modified or pushed.

The collector, generator and prompt library are identical between the two main folders. The evaluator is the same code under a different filename. The final predictions and evaluation-input JSON files are byte-identical. Twelve ordinary files in the ZIP match the corresponding working files; only a Finder metadata file differs. The ZIP is therefore not a separate final implementation.

The [source manifest](../source-manifest.json) records hashes of 39 reviewed files without exposing absolute local paths. It excludes Git internals, virtual environments, bundled visualization libraries and operating-system metadata. The retained Git tip is `8bb4542`; the publication uses a clean history because the supplied history contains embedded credentials and unrelated generated artifacts.

## Dataset versions

| Source file role | Causes | HasSubevent | HasFirstSubevent | HasLastSubevent | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original collection | 1,832 | 3,507 | 2,128 | 2,874 | 10,841 |
| Input after example and self-loop exclusions | 1,830 | 3,506 | 2,127 | 2,873 | 10,836 |
| Complete progress checkpoint | 1,000 | 1,000 | 1,000 | 1,000 | 4,000 |
| Final prediction archive | 999 | 1,000 | 1,000 | 1,000 | 3,999 |

Comparing input versions identifies four removed example pairs: `lighting a match -> fire`, `attending school -> learn`, `wake up -> open your eyes`, and `take a shower -> dry off`. The fifth removed record is the `dry -> dry` self-loop.

The progress checkpoint also has one extra `Causes` record, `dry -> dry`, absent from the final archive. Its removal explains the count difference, but no deletion rationale is present in the code. Other self-loops remain; the final file should not be described as a completely self-loop-cleaned dataset. Each final relation list matches the corresponding retained input prefix in the same order; the progress file and final file are distinct snapshots, not interchangeable checkpoints.

## Published data

- [event_pairs.json](../data/event_pairs.json): the 10,836-record input snapshot, copied without changing its data.
- [predictions.json](../data/predictions.json): the 3,999-record final output with three initial responses, relation counts and selected explanations.
- [Historical confusion matrix](../evidence/historical-confusion-matrix.png): the original saved figure, including the normalization discrepancy explained in the results document.

The collection's stored nodes retain ConceptNet IDs, language and text labels, but the original collector discarded assertion-level license, source and dataset fields. The current collector preserves these fields for fresh runs. The old snapshot is not retroactively assigned missing metadata.

ConceptNet-derived data is distributed with attribution under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [rights and attribution](../RIGHTS_AND_ATTRIBUTION.md). Records may contain sensitive, prejudiced or offensive commonsense assertions. No private participant dataset is included.

## Publication decisions

The `archive` directory retains five representative scripts, with the embedded key replaced by `xxx`. The maintained package exposes tested entry points rather than requiring users to execute the original hard-coded scripts. Archive scripts are reference material, not the recommended runtime.

Not published: the virtual environment, ZIP archive, old Git history, duplicate datasets, provisional 820-record checkpoint, derived error-sampling copies, exploratory notebook, bundled JavaScript libraries, generated CDN-dependent HTML, Excel workbook metadata or unrelated toy graph code. The workbook's relevant numerical results are documented and verified by tests rather than republishing an unexplained external-baseline table.

All original source files remain unchanged. Sanitizing this publication does not revoke a key stored in the original files or old university repository history; any such key still in use should be rotated by its owner.
