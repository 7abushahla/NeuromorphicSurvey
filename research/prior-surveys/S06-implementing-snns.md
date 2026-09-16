# S06. Implementing Spiking Neural Networks on Neuromorphic Architectures

## Identity and retrieval

- **Citation:** P. K. Huynh, M. L. Varshika, A. Paul, M. Isik, A. Balaji, and A. Das, “Implementing Spiking Neural Networks on Neuromorphic Architectures: A Review,” arXiv:2202.08897, 2022.
- **Source type:** Preprint survey.
- **Retrieval status:** `verified`. Substantive arXiv PDF text was inspected on 2026-09-16.
- **Inspected URLs:** <https://arxiv.org/pdf/2202.08897>; <https://doi.org/10.48550/arxiv.2202.08897>.

## Assessment

**Scope.** System software for mapping SNNs to neuromorphic architectures. **Organizing taxonomy.** Platform-based design versus hardware-software co-design, then performance/energy versus thermal/reliability optimization. **Strongest explanatory contribution.** It explains how timing distortion and hardware resource limits affect mapping. **Deployment depth.** Detailed mapping-framework review, with framework-specific routes rather than unified end-to-end comparisons. **Material omissions.** No NIR-like interchange format or standardized evidence taxonomy. **Verification limits.** The work is a preprint and its framework inventory predates recent software stacks.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | mentioned | IF/LIF serve only as introductory background. | Sec. 1, Fig. 1 |
| B | mentioned | ISI coding is used to illustrate timing distortion, not surveyed as encoding taxonomy. | Sec. 2.1, Communication through spikes |
| C | mentioned | Learning methods are contextual rather than reviewed. | Sec. 2, platform-based design |
| D | none | ANN-to-SNN conversion is not a review category. | Secs. 2-3 |
| E | mentioned | General simulators are named as application-level inputs, not compared as frameworks. | Sec. 2.1, simulator discussion |
| F | full | Compilers, partitioners, mapping tools, and run-time managers structure the review. | Secs. 2-3; Tables 3-5 |
| G | none | No interchange format is proposed or compared. | Secs. 2-3 |
| H | partial | Hardware capacities and constraints are tabulated as mapping context. | Sec. 1, Table 1; Sec. 2.1 |
| I | partial | ISI distortion, fan-in/out, capacities, and mapping consequences are explained. | Sec. 2.1, Figs. 3-5 |
| J | mentioned | Performance, energy, and reliability guide optimization, but evidence classes are not formalized. | Sec. 2 introduction |
| K | mentioned | Application examples explain mapping but no application-results survey is organized. | Secs. 2-3, framework examples |
| L | partial | Frameworks transform high-level SNNs to physical implementations, but no comparable full route is traced. | Sec. 2.2, PACMAN discussion |
