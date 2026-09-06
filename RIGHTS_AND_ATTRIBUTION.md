# Rights and attribution

## Team implementation

The seminar project was developed by Jingfan Xin and Abdullah Abdelhafez. The supplied university Git history documents both contributors. This repository organizes the project for inspection and provides maintained entry points; it does not claim sole authorship of all team work.

No blanket software license is assigned to the team's historical code without agreement from its contributors. Public visibility is not a declaration that all code can be relicensed freely. Maintenance, tests and English documentation were prepared with AI assistance and checked against the supplied implementation and results.

## ConceptNet-derived data

This project includes data from ConceptNet 5, compiled by the Commonsense Computing Initiative and the ConceptNet community. ConceptNet incorporates contributions from commonsense knowledge projects and resources including Wikimedia, WordNet, Open Multilingual WordNet, DBpedia and other sources acknowledged by its maintainers.

The ConceptNet-derived datasets in `data/` and `artifacts/original/`, including embedded graph data, are distributed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/), consistent with the [ConceptNet data license](https://github.com/commonsense/conceptnet5/wiki/Copying-and-sharing-ConceptNet). Derived event labels and associated prediction annotations are presented with that dataset, not as an independently sourced proprietary knowledge base. Preserve attribution and share-alike obligations when redistributing adapted data. The original collector did not retain assertion-level source metadata; that limitation is documented rather than invented away.

Research reference: Robyn Speer, Joshua Chin and Catherine Havasi, *ConceptNet 5.5: An Open Multilingual Graph of General Knowledge*, AAAI 2017. See the [ConceptNet project](https://github.com/commonsense/conceptnet5).

Some assertions contain offensive or sensitive language and are included for evaluating a knowledge resource, not as endorsed claims. Generated explanations are model outputs, not human-verified facts.

## Dependencies and archived material

OpenAI's Python client, NetworkX, Pyvis, NumPy, Pandas, Matplotlib and Seaborn are external tools, not original project inventions. The original HTML pages and their local `lib/bindings/utils.js` helper were generated or supplied by Pyvis. The helper is copied at two relative locations to preserve the original HTML links, with the [Pyvis BSD license](third_party/pyvis-LICENSE_BSD.txt), sourced from the [upstream license](https://github.com/WestHealth/pyvis/blob/master/LICENSE_BSD.txt). Other dependency packages are not vendored. CDN-hosted resources retain their own licenses.

The historical figure, original workbook and saved graphs are preserved as team experiment artifacts, with known discrepancies disclosed in the [artifact catalog](artifacts/README.md). Only the workbook's absolute local save-path element was removed; its contents, formatting, author name and timestamps are retained. Duplicate archives, dependency trees and original Git history are not published. The workbook's external FF-RNN numbers are not represented as an implemented or verified project baseline.

Secrets were replaced with `xxx` before publication. Revocation of an old credential is a separate action for its owner; this repository does not assert that credentials found in the original sources have been revoked.
