# S30 Neuromorphic Architectures for AI Algorithms

## Identity and retrieval

Seham Al Abdul Wahid, Arghavan Asad, and Farah Mohammadi. *A Survey on Neuromorphic Architectures for Running Artificial Intelligence Algorithms*. *Electronics*, 13(15), 2963, 2024. DOI 10.3390/electronics13152963. Publisher full text was substantively inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://www.researchgate.net/publication/382613210_A_Survey_on_Neuromorphic_Architectures_for_Running_Artificial_Intelligence_Algorithms and https://www.mdpi.com/2079-9292/13/15/2963.

## Scope and assessment

This hardware-oriented review organizes neuromorphic systems by neuron models, implementation style, memory technology, learning mechanisms, and representative projects. Table 1 provides the strongest contribution, a compact comparison of chips and architecture properties. It does not examine software-to-chip routes, interchange formats, boundary semantics, or evidence classes. Applications are used as motivation rather than analyzed through measured deployment cases.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | full | Introduction, Section 2.1, and Figure 1 cover HH, Izhikevich, IF, and spike-response models. |
| B | none | No encoding or neural-code taxonomy was found in the inspected text. |
| C | partial | Introduction and Section 2 distinguish supervised, unsupervised, and reinforcement learning, including STDP and VDSP. |
| D | none | ANN-to-SNN conversion is not a reviewed category. |
| E | none | No SNN-framework comparison is provided. |
| F | none | No compiler or graph-mapping taxonomy is provided. |
| G | none | No interchange format is reviewed. |
| H | full | Section 3 and Table 1 compare representative neuromorphic projects, including TrueNorth, Loihi, SpiNNaker, BrainScaleS, Tianjic, GrAIOne, Akida, and memristor systems. |
| I | none | The hardware descriptions do not analyze semantic failures at deployment boundaries. |
| J | none | The review does not classify reported results by physical, simulation, or proxy evidence. |
| K | mentioned | Introduction and Section 4 identify application sectors, without a measured-results synthesis. |
| L | none | No trained-network-to-chip route is documented. |

## Verification limits

The platform table is descriptive. It should not be treated as an interoperable deployment comparison or as normalized performance evidence.
