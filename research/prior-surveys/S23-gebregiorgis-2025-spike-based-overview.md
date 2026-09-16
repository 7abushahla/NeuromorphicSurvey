# S23. Gebregiorgis et al. (2026), spike-based neuromorphic computing

## Identity and retrieval

Anteneh Gebregiorgis et al., "Spike-based neuromorphic computing: An overview from bio-inspiration to hardware architectures and learning mechanisms," *Microprocessors and Microsystems*, vol. 124, art. 105240, 2026, doi: 10.1016/j.micpro.2025.105240. The version of record states that the article was available online on 20 December 2025. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16.

Local full text:

- `/Users/hamza/Downloads/papers-review/1-s2.0-S0141933125001073-main.pdf`

Inspected URLs:

- https://doi.org/10.1016/j.micpro.2025.105240
- https://www.sciencedirect.com/science/article/pii/S0141933125001744

## Scope and contribution

This tutorial follows a broad vertical path from biological neurons and synapses through computational models, learning algorithms, circuits, SNN hardware architectures, mapping, and applications. Its strongest deployment contribution is Section 8. That section explains graph partitioning, cluster placement, crossbar realization, limited-precision mapping, and recent mapping frameworks. It also identifies state storage, off-chip traffic, multicore synchronization, and numerical precision as coupled deployment constraints. This is substantially deeper than the former abstract-only assessment suggested.

The paper is strongest as a tutorial on hardware-aware SNN design and mapping. It is not a comparative software-framework survey, and it does not define an interchange format. Its application section is broad but mainly descriptive. The paper reports selected quantitative mapping and hardware examples, but it does not classify evidence as silicon, simulation, or analytical proxy. It also does not trace one trained network through a named software stack to a named physical chip.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Sections 2 and 3, pp. 2-6, explain biological neurons and synapses, SRM, IF, LIF, ALIF, synaptic dynamics, and the realism-efficiency trade-off. |
| B | partial | Section 4.9, pp. 8-9, explains binary spike representation. Section 9.1, p. 24, distinguishes rate, temporal, and population coding, but gives little decoding analysis. |
| C | full | Section 5, pp. 9-11, compares local plasticity, evolutionary search, backpropagation through time, spike-time gradients, surrogate gradients, and online learning. |
| D | mentioned | Section 5.2.2, p. 10, identifies rate-based ANN-to-SNN conversion and its efficiency limitation, but does not develop conversion methods or error mechanisms. |
| E | none | The full text does not survey SNN software frameworks or compare their model and operator support. |
| F | full | Section 8, pp. 20-23, treats partitioning, placement, crossbar mapping, limited-precision mapping, NeuProMa, SMART, AHM, Stream, and mapping objectives. |
| G | none | No neuromorphic interchange representation or concrete cross-platform interchange format is analyzed. |
| H | full | Sections 6 and 7, pp. 11-20, cover analog, digital, mixed-signal, memory-device, and many-core SNN implementations with explicit architectural trade-offs. |
| I | partial | Sections 8.4-8.6, p. 23, identify precision mismatch, persistent-state memory pressure, off-chip traffic, synchronization overhead, and mapping limitations. Section 10, pp. 24-25, adds noise, variability, and interoperability. These constraints are not organized as a complete cross-platform semantic taxonomy. |
| J | mentioned | Section 8.6, p. 23, identifies the absence of standardized mapping benchmarks and names NeuroBench. Section 9.2, p. 24, distinguishes algorithmic complexity from hardware efficiency. No evidence-classification scheme is applied to surveyed claims. |
| K | partial | Section 9.2, p. 24, organizes applications by workload. Section 8.5, p. 23, reports 12x external-memory, 5x energy, and 20x hidden-state reductions on event-vision benchmarks, but most application coverage lacks measured comparisons. |
| L | mentioned | Sections 8 and 9 discuss mapping and deployment stages, but no case study traces a trained network through a named framework and compiler to measured execution on a named physical chip. |

## Verification limits

All 30 PDF pages were inspected. Pages 26-30 are references and author biographies. Selected pages containing the mapping and precision discussion were also rendered to confirm the table, figure, and section layout. The local PDF resolves the former access limitation. Numerical claims remain attributed to the reviewed paper rather than independently reproduced.
