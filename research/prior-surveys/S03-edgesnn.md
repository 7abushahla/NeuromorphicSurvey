# S03. Edge Intelligence with Spiking Neural Networks

## Identity and retrieval

- **Citation:** S. Deng *et al.*, “Edge Intelligence with Spiking Neural Networks,” arXiv:2507.14069, 2025.
- **Source type:** Preprint survey.
- **Retrieval status:** `verified`. Substantive arXiv HTML full text was inspected on 2026-09-16.
- **Inspected URLs:** <https://arxiv.org/html/2507.14069>; <https://arxiv.org/abs/2507.14069>.

## Assessment

**Scope.** EdgeSNN foundations, practical deployment considerations, benchmarking, and open challenges. **Organizing taxonomy.** Foundations, three practical considerations, evaluation, and challenges. **Strongest explanatory contribution.** It distinguishes conventional-hardware proxy evaluation from hardware-aware evaluation through a dual-track strategy. **Deployment depth.** Broad deployment review, not a trace of one fixed model through one named chip. **Material omissions.** No operator-by-operator semantic-boundary taxonomy and no full worked deployment route. **Verification limits.** Preprint status and rapidly changing edge hardware landscape limit stability.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | full | Neuron models are a named foundation of the taxonomy. | Sec. III, EdgeSNN foundations |
| B | partial | Encoding appears within SNN foundations but is not the primary organizing dimension. | Sec. III |
| C | full | Learning algorithms and resource-aware updating are surveyed. | Sec. III; Sec. IV-B |
| D | full | Lightweight SNN construction includes conversion-oriented efficiency methods. | Sec. IV-A, on-device inference |
| E | mentioned | Supporting software is acknowledged within the stack, without a framework comparison. | Sec. III, hardware support |
| F | mentioned | Hardware heterogeneity is discussed, without a compiler/mapping taxonomy. | Sec. III; Sec. VI |
| G | none | No interchange format is identified as a survey axis. | Secs. III-VI |
| H | full | Supporting hardware platforms form a stated foundation. | Sec. III |
| I | partial | Heterogeneity and deployment constraints are discussed, but no layer-boundary semantics taxonomy is built. | Sec. IV; Sec. VI |
| J | full | Dual-track benchmarking distinguishes proxy and hardware-aware evaluation. | Sec. V |
| K | full | Edge applications and practical results are surveyed. | Sec. IV-A; Sec. V |
| L | partial | The paper covers deployment ingredients but gives no single complete named route. | Secs. IV-V |
