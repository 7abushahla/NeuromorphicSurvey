# S14. Basu et al., SNN Integrated Circuits

## Identity and retrieval

A. Basu, C. Frenkel, L. Deng, and X. Zhang, "Spiking Neural Network Integrated Circuits: A Review of Trends and Future Directions," in *2022 IEEE Custom Integrated Circuits Conference*, 2022, pp. 1-8. DOI: 10.1109/CICC53496.2022.9772783. The arXiv HTML full text and IEEE metadata page were inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs: <https://arxiv.org/html/2203.07006>; <https://ieeexplore.ieee.org/document/9772783>.

## Scope and assessment

This circuit review organizes designs as large multicore systems with spike-routing NoCs, digital single-core systems, and mixed-signal single-core systems. Its strongest explanatory contribution is normalized circuit-level comparison, including 40 nm and optional 0.9 V normalization and distinctions among task-independent, task-level, and pre-silicon reports. The review is not about SNN algorithms, software, or deployment pipelines. Its normalization practice is J-adjacent but does not establish a formal physical-versus-simulation-versus-proxy evidence taxonomy.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | none | Neuron behavior is background to circuit design, not a model taxonomy. Locator: Introduction and organization. |
| B | none | No encoding taxonomy was identified. Locator: full-text inspection. |
| C | none | No learning-method taxonomy was identified. Locator: full-text inspection. |
| D | none | No ANN-to-SNN conversion treatment was identified. Locator: full-text inspection. |
| E | none | No SNN software-framework taxonomy was identified. Locator: full-text inspection. |
| F | none | No compiler or mapper-toolchain taxonomy was identified. Locator: full-text inspection. |
| G | none | No interchange-format analysis was identified. Locator: full-text inspection. |
| H | full | Dedicated SNN ICs are compared across multicore, digital, and mixed-signal designs. Locator: Abstract; Secs. II-IV. |
| I | none | No deployment-boundary semantics taxonomy was identified. Locator: full-text inspection. |
| J | partial | It labels pre-silicon entries and applies process and voltage normalization, but does not classify all evidence into physical, simulated, and proxy classes. Locator: Sec. II, Table I and normalization discussion. |
| K | mentioned | The task-and-architecture table reports demonstrated applications and selected results. Locator: Table II. |
| L | none | The table summarizes reported implementations rather than tracing one trained network through a full deployment route. Locator: Tables I-II. |

## Verification limits

The evidence discipline applies to circuit comparison. It should not be cited as a general SNN deployment evidence framework.
