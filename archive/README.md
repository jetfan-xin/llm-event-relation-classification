# Archived reference scripts

These scripts are retained from the supplied seminar implementation for inspection:

- `data_collector.py`: original fixed-offset ConceptNet collection.
- `prompt_library.py`: original definitions, examples and an unused alternative prompt.
- `generator.py`: original three-sample selection and checkpoint logic.
- `evaluator.py`: original metric and heatmap routines.
- `visualizer.py`: original NetworkX/Pyvis graph exploration.

The hard-coded key in `generator.py` has been replaced with `xxx`. Original comments and experimental behavior are preserved; explanatory project documents are in English. The original endpoint is retained as provenance, not a recommendation to use it.

**Do not use these files as the normal entry points.** Some execute work at import time, depend on local relative paths, assume valid model output or contain inconsistent normalization. The generator's final entry point prints a prompt rather than running its batch method. The collector appends JSON documents, which can make repeated output invalid.

Use the tested `event_relations` package and [usage guide](../docs/usage.md). Its prompt correction, invalid-output handling, graph conventions and resume validation are documented separately from the archived experiment. Stored predictions are unchanged.
