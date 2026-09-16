# S04. The NeuroBench Framework

## Identity and retrieval

- **Citation:** J. Yik *et al.*, “The NeuroBench framework for benchmarking neuromorphic computing algorithms and systems,” *Nature Communications*, vol. 16, art. 1545, 2025, doi: 10.1038/s41467-025-56739-4.
- **Source type:** Peer-reviewed benchmark-framework article. It is not a conventional literature survey.
- **Retrieval status:** `verified`. Substantive publisher PDF text was inspected on 2026-09-16.
- **Inspected URLs:** <https://www.nature.com/articles/s41467-025-56739-4.pdf>; <https://doi.org/10.1038/s41467-025-56739-4>; <https://doi.org/10.48550/arxiv.2304.04640>.

## Assessment

**Scope.** A community benchmark framework for algorithms and systems. **Organizing taxonomy.** Hardware-independent algorithm track versus hardware-dependent systems track. **Strongest explanatory contribution.** It makes proxy complexity and measured deployed performance non-interchangeable. **Deployment depth.** It supplies protocols and metrics, not a survey of deployment routes. **Material omissions.** No taxonomy of model semantic mismatches, conversion methods, or interchange formats. **Verification limits.** Benchmark protocol coverage should not be read as literature-wide evidence classification.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | none | Neuron models are outside the benchmark taxonomy. | Introduction; Fig. 1 |
| B | none | Encoding taxonomies are outside the benchmark taxonomy. | Introduction; Fig. 1 |
| C | none | Training methods are not reviewed. | Introduction; algorithm-track scope |
| D | none | ANN-to-SNN conversion is not a framework axis. | Introduction; Fig. 1 |
| E | partial | An open benchmark harness supports framework participation. | Introduction; Algorithm Track Benchmark Harness |
| F | none | No compiler or mapping-toolchain survey is presented. | System Track Benchmark Framework |
| G | none | No interchange format is specified. | Introduction; Fig. 1 |
| H | partial | The systems track targets deployed hardware and names candidate systems. | System Track Benchmark Framework |
| I | none | No semantic-boundary taxonomy is provided. | Introduction; System Track Benchmark Framework |
| J | full | The two tracks explicitly separate complexity proxies from real hardware measurement. | Fig. 1; Algorithm and System Track Benchmark Frameworks |
| K | full | Benchmark baselines and metrics report measured task outcomes. | Algorithm Track Baseline Results; System Track Metrics |
| L | mentioned | Systems-track protocols require deployed execution but do not trace one fixed route. | System Track Benchmark Framework |
