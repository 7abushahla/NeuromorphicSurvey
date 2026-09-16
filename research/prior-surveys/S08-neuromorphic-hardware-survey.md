# S08. A Survey of Neuromorphic Computing and Neural Networks in Hardware

## Identity and retrieval

- **Citation:** C. D. Schuman *et al.*, “A Survey of Neuromorphic Computing and Neural Networks in Hardware,” arXiv:1705.06963, 2017.
- **Source type:** Preprint survey.
- **Retrieval status:** `verified`. Substantive arXiv PDF text was inspected on 2026-09-16.
- **Inspected URLs:** <https://arxiv.org/pdf/1705.06963>; <https://doi.org/10.48550/arxiv.1705.06963>.

## Assessment

**Scope.** A 35-year historical survey of neuromorphic motivations, models, algorithms, hardware, supporting systems, and applications. **Organizing taxonomy.** History followed by models, learning, hardware, supporting systems, and applications. **Strongest explanatory contribution.** It supplies broad historical integration across over 3,000 papers. **Deployment depth.** Broad platform coverage but no individual deployment trace. **Material omissions.** No modern interchange-format or evidence-classification methodology. **Verification limits.** The 2017 cutoff predates NIR, contemporary toolchains, and recent edge benchmarks.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | full | Neuro-inspired models and neuron/synapse models are a principal section. | Sec. III |
| B | partial | Information representation appears in model and algorithm discussions, without a dedicated code taxonomy. | Secs. III-IV |
| C | full | Algorithms and learning approaches constitute a principal section. | Sec. IV |
| D | none | ANN/deep-learning and SNN relationships are contextual, without ANN-to-SNN conversion treatment. | Sec. IV, Algorithms; no conversion subsection identified |
| E | partial | Supporting software systems are included under supporting components. | Sec. VI-B |
| F | none | No compiler/mapping-toolchain taxonomy is presented. | Sec. VI-B scope |
| G | none | No interchange format is discussed as a survey category. | Secs. I-VII |
| H | full | Hardware implementations and devices are a principal section. | Sec. V |
| I | none | No deployment-boundary semantic taxonomy is provided. | Secs. V-VI |
| J | none | No classification of physical, simulation, and estimate evidence is provided. | Secs. I-VII |
| K | full | Applications are a principal section. | Sec. VII |
| L | none | No end-to-end trained-network-to-chip case-route taxonomy is provided. | Secs. V-VII |
