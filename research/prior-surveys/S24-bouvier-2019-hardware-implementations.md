# S24. Bouvier et al. (2019), SNN hardware implementations

## Identity and retrieval

Maxence Bouvier et al., "Spiking Neural Networks Hardware Implementations and Challenges: A Survey," *ACM Journal on Emerging Technologies in Computing Systems*, vol. 15, no. 2, art. 22, pp. 1-35, 2019, doi: 10.1145/3304103. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16. The article PDF identifies `10.1145/3304103` as the article DOI. The previously recorded `10.1145/3287626` does not match the DOI printed on the primary text.

Local full text:

- `/Users/hamza/Downloads/papers-review/3304103.pdf`

Inspected URLs:

- https://dl.acm.org/doi/10.1145/3304103
- https://doi.org/10.1145/3304103

## Scope and contribution

The survey asks whether the event-driven and sparse properties of SNNs produce genuine hardware benefits. It connects neuron and code choices to neurocore organization, mapping, approximation, training, and accelerator comparison. Its strongest explanation is the joint treatment of algorithm and hardware constraints. The paper shows how coding, topology, precision, mapping, on-chip learning, and benchmark choice alter the apparent efficiency of an implementation.

The low-power accelerator comparison in Table 2 is unusually careful for its date. It labels simulated 28 nm, FPGA, simulated 65 nm, 10 nm FinFET, and 28 nm results separately. It also records training location, coding, input conversion, topology, accuracy, energy, and chip area. The accompanying prose flags that one nominal SNN result evaluates a BNN on spiking hardware. This is meaningful evidence discipline, although the paper does not formalize a reusable evidence taxonomy.

The survey does not cover modern SNN software frameworks, compilers, or interchange formats. Its mapping discussion is conceptual rather than a toolchain comparison. Its application evidence is concentrated on MNIST image classification and does not establish a general end-to-end deployment methodology.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Sections 2 and 3, pp. 2-10, explain IF, LIF, refractory and leakage behavior, bio-plausible neuron and synapse models, and their implementation costs. |
| B | full | Section 2.2, pp. 4-5, distinguishes rate, TTFS, and inter-spike-interval coding. Sections 4.3 and 7.1, pp. 14-15 and 25, connect coding to conversion, timing error, accuracy, and hardware activity. |
| C | full | Section 5, pp. 18-21, compares STDP, reward modulation, supervised learning, spike-domain backpropagation, and on-chip versus off-chip training. |
| D | partial | Section 5.1, p. 18, reviews ANN-to-SNN conversion frameworks, topology modification, rate-coding cost, and temporal conversion. Section 7.1, p. 25, reports an example conversion accuracy loss. The treatment predates later low-latency conversion taxonomies. |
| E | none | No software-framework ecosystem or simulator comparison is provided. |
| F | partial | Section 2.3.2, pp. 5-7, compares depth-wise and spatial mapping, load balance, communication distance, and graph-based optimization. It does not compare named compiler toolchains. |
| G | none | No interchange representation or portable graph format is analyzed. |
| H | full | Sections 3, 4, and 6, pp. 8-24, cover analog and digital neurocores, crossbars, large-scale systems, and embedded accelerators, including BrainScaleS, Neurogrid, TrueNorth, SpiNNaker, and Loihi. |
| I | partial | Sections 2.3.2 and 4, pp. 5-18, explain mapping imbalance, timing error, input-conversion bias, topology dependence, precision loss, and device non-idealities. These are not organized as a cross-platform semantic contract. |
| J | partial | Section 6.2 and Table 2, pp. 22-24, explicitly distinguish simulated, FPGA, and fabricated technologies and flag incomparable model types and missing values. Section 6, p. 21, states that accelerator comparison remains unresolved. No general evidence classes are defined. |
| K | partial | Section 6.2 and Table 2, pp. 22-24, provide accuracy, energy, area, and coding data for low-power image-classification accelerators. Coverage is narrow and centered on MNIST. |
| L | partial | Table 2, p. 24, records compact routes from training type and input conversion through network topology to a specific implementation and energy result. It does not document a reproducible framework-to-compiler-to-chip workflow. |

## Verification limits

All 35 PDF pages were inspected. Pages 28-35 are references. Pages 5-7, 18-24, and 25-27 received detailed review, and Table 2 was rendered to verify its evidence labels and footnotes. The local file resolves the former access limitation. The PDF's article DOI supersedes the earlier mismatched identifier.
