# S05. Advancing Neuromorphic Computing With Loihi

## Identity and retrieval

- **Citation:** M. Davies *et al.*, “Advancing Neuromorphic Computing With Loihi: A Survey of Results and Outlook,” *Proceedings of the IEEE*, vol. 109, no. 5, pp. 911-934, 2021, doi: 10.1109/JPROC.2021.3067593.
- **Source type:** Peer-reviewed survey.
- **Retrieval status:** `verified`. Substantive IEEE full text was inspected on 2026-09-16.
- **Inspected URLs:** <https://ieeexplore.ieee.org/document/9395703>; <https://doi.org/10.1109/JPROC.2021.3067593>.

## Assessment

**Scope.** Results and outlook for one chip family. **Organizing taxonomy.** Loihi systems/software, deep learning, attractor networks, nongradient algorithms, and applications. **Strongest explanatory contribution.** It links measured latency and energy results to physical Loihi execution across varied workloads. **Deployment depth.** High but single-platform. **Material omissions.** No cross-chip portability comparison or general deployment-fidelity taxonomy. **Verification limits.** Measurements cannot generalize to other chips or host configurations.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | partial | Loihi LIF compartments, plasticity, and adaptive mechanisms are explained. | Sec. II-A |
| B | partial | Spike messages and event encoding are explained at architectural level. | Sec. II-A and II-B |
| C | partial | Backpropagation, local learning, and plasticity are discussed. | Sec. III; Sec. II-A |
| D | partial | Converted rate-coded deep SNNs and their tradeoffs are analyzed. | Sec. III |
| E | mentioned | NxSDK and its interfaces are described for Loihi. | Sec. II-C |
| F | partial | NxSDK includes APIs, compilers, runtime, and debugging tools, but only for Loihi. | Sec. II-C |
| G | none | No interchange-format comparison is provided. | Sec. II-C |
| H | full | Chip, multichip systems, mesh, and I/O are described in depth. | Sec. II-A-B; Fig. 1 |
| I | mentioned | Host, FPGA, and asynchronous-mesh boundaries are described, but not systematically compared across chips. | Sec. II-A-C |
| J | partial | Physical Loihi results and measurement context are reported, without a general evidence taxonomy. | Secs. III-VI; tables |
| K | full | Applications include event processing, control, optimization, regression, and graph search with results. | Sec. VI; tables |
| L | partial | Repeated measured application routes reach Loihi silicon, but remain single-chip-family cases. | Secs. III-VI |
