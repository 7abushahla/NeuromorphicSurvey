# S29 Practical Tutorial on Spiking Neural Networks

## Identity and retrieval

Bahgat Ayasi, Cristóbal J. Carmona, Mohammed Saleh, and Angel M. García-Vico. *A Practical Tutorial on Spiking Neural Networks: Comprehensive Review, Models, Experiments, Software Tools, and Implementation Guidelines*. *Eng*, 6(11), 304, 2025. DOI 10.3390/eng6110304. Publisher full text was substantively inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://doi.org/10.20944/preprints202509.2072.v1 and https://www.mdpi.com/2673-4117/6/11/304.

## Scope and assessment

The paper combines a broad tutorial with matched ANN and SNN experiments on MNIST and CIFAR-10. Its organizing sequence is components, encodings, neuron models, learning rules, software tools, and measured tutorial experiments. Its strongest contribution is the unusually explicit labeling of its energy result as a GPU operation-count proxy. Deployment discussion remains conceptual. The study does not deploy the evaluated models to a named chip or analyze boundary semantics such as reset behavior, operator support, payload precision, or time-model translation.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | full | Section 2.3 surveys IF, LIF, ALIF, AdEx, Izhikevich, CUBA, sigma-delta, and other models. |
| B | full | Section 2.2 and Table 1 compare direct, rate, temporal, TTFS, population, phase, burst, and sigma-delta encodings. |
| C | full | Section 2.4 covers surrogate-gradient BPTT, STDP, reinforcement, hybrid rules, and related training approaches. |
| D | partial | Introduction and Section 2 list ANN-to-SNN conversion, but it is not the organizing or experimental focus. |
| E | full | Section 3, “Implementation Frameworks and Tools,” discusses Lava, SLAYER, SpikingJelly, Norse, and PyTorch. |
| F | mentioned | Section 3 describes Lava NetX as a route to neuromorphic targets, without a comparative mapping-toolchain analysis. |
| G | none | No NIR or interchange-format taxonomy was found in the inspected full text. |
| H | mentioned | Sections 2.1.2 and 3 name Loihi, TrueNorth, and SpiNNaker as context, without platform analysis. |
| I | none | Deployment challenges are stated generally in Sections 1 and 2.1.3, but no boundary-semantics taxonomy is supplied. |
| J | mentioned | Abstract and Section 4 identify the reported energy as a GPU operation-count proxy, but no cross-literature evidence-classification scheme is offered. |
| K | full | Sections 2.1.5 and 4 discuss applications and report MNIST and CIFAR-10 results. |
| L | none | Section 4 reports GPU-proxy experiments only, with no end-to-end named-chip route. |

## Verification limits

The article is a tutorial-study, not a deployment survey. Its energy findings are limited to the stated proxy and cannot support physical-silicon conclusions.
