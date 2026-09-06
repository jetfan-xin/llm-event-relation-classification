# Project context and contributions

## Research question

The Knowledge Processing seminar project investigates whether a language model can distinguish four closely related types of event knowledge in ConceptNet. The key difficulty is not extracting keywords: an event pair can plausibly have more than one interpretation, while the experiment requires one label.

The implementation connects a knowledge-graph API, a structured prompting workflow, classification evaluation and graph exploration. It offers a practical example of building and auditing an LLM experiment around an existing symbolic knowledge resource.

## Contributions supported by the retained Git history

| Area | Jingfan Xin's recorded implementation work |
| --- | --- |
| Data acquisition | ConceptNet collector and output updates, including commits `631c5e2` and `a1c7be1` |
| Prompting and generation | Prompt library, prompt generator and initial model outputs in `cb36cba`; expanded experiment in `b0c5193` |
| Evaluation | Precision/recall/F1 and confusion-matrix work in `b0c5193` and `d13a1bf`; strategy comparison in `f9a3683` |
| Visualization and presentation | Semantic-network visualization in `b0c5193`; result and heatmap updates in `ffe7b1f` and `8bb4542` |

Abdullah Abdelhafez contributed the initial repository, a comparison utility, filtering, data enrichment and random selection for error analysis. This is a team project; commit evidence supports contributions but is not a complete record of collaboration or a claim of exclusive authorship.

The retained implementation history runs from November through January. A small exploratory notebook also tries WordNet lookups; that notebook is not part of the final classifier. No final seminar paper or presentation was present in the supplied directory.

## Technologies

- Python and JSON for the experiment pipeline and result interchange.
- ConceptNet REST API for event-relation data.
- OpenAI-compatible Chat Completions client for prompted relation selection.
- Pandas, NumPy, Matplotlib and Seaborn in the archived evaluation scripts.
- NetworkX and Pyvis in the archived graph analysis and interactive visualization.
- Standard-library evaluation and graph utilities in the maintained entry points, allowing offline inspection without a large environment.

The project does not use a trained FF-RNN, a retrieval-augmented generation system or a vector database. An FF-RNN comparison appears in the workbook, but its source, split and implementation are not supplied; it is not represented as this project's implemented baseline.
