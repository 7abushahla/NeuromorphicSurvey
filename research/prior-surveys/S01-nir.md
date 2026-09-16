# S01. Neuromorphic Intermediate Representation

## Identity and retrieval

- **Citation:** J. E. Pedersen *et al.*, “Neuromorphic intermediate representation: A unified instruction set for interoperable brain-inspired computing,” *Nature Communications*, vol. 15, art. 8122, 2024, doi: 10.1038/s41467-024-52259-9.
- **Source type:** Peer-reviewed research article. It is not a conventional literature survey.
- **Retrieval status:** `verified`. Substantive publisher PDF text was inspected on 2026-09-16.
- **Inspected URLs:** <https://www.nature.com/articles/s41467-024-52259-9.pdf>; <https://doi.org/10.1038/s41467-024-52259-9>; <https://doi.org/10.48550/arxiv.2311.14641>.

## Assessment

**Scope.** NIR specifies a platform-independent graph representation and demonstrates three graphs across seven simulators and four hardware back ends. **Organizing taxonomy.** Continuous versus discrete time, software versus hardware, NIR primitives, and backend interfaces. **Strongest explanatory contribution.** It directly exposes a portability boundary by separating a continuous-time reference model from discretized implementations and measures mismatches. **Deployment depth.** Three proof-of-concept graphs run across eleven platforms, including four chips. **Material omissions.** It is not an applications survey and does not analyze full CNN deployment routes, reset-policy taxonomies, residual operators, or quantized payload contracts. **Verification limits.** The demonstrations are deliberately small and cannot establish general deployment fidelity.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | partial | LIF and current-based LIF primitives are formalized, but neuron coverage is intentionally bounded. | Results, “NIR axioms and Computational primitives”; Discussion |
| B | none | The work evaluates existing graphs, not neural-code taxonomies. | Results and Methods scope |
| C | none | No direct-training-method review is provided. | Results and Methods scope |
| D | none | ANN-to-SNN conversion is not surveyed. | Introduction and Results scope |
| E | full | Seven simulator/framework back ends and their NIR interfaces are enumerated. | Results, Fig. 2e-f |
| F | partial | NIR is positioned as a source representation for compilers, rather than a comparative compiler review. | Introduction, paragraphs on ONNX, MLIR, and compilers |
| G | full | The paper defines, serializes, and evaluates an interchange representation. | Results, Fig. 1-2; Methods, “NIR graph” |
| H | full | Four physical platforms and seven simulators are named and evaluated. | Results, “Experiments”; Fig. 2 |
| I | full | Discretization and backend mismatches are explained and measured, including divergent recurrent behavior. | Results, “Discussion of mismatches”; Fig. 4-6 |
| J | partial | Cross-platform discrepancies and accuracies are measured, but evidence classes are not formalized. | Results, “Experiments”; Discussion |
| K | none | Datasets demonstrate graphs rather than surveying applications with measured results. | Results, Fig. 3 |
| L | partial | Three graphs are transferred to named physical chips, but they are limited benchmarks rather than full deployable routes. | Results, Figs. 3-6 |
