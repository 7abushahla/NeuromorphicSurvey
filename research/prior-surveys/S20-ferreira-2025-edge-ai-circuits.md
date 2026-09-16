# S20. Ferreira et al. (2025), edge-AI neuromorphic circuits

## Identity and retrieval

Pietro M. Ferreira, Siqi Wang, Yueyuan Gao, and Aziz Benlarbi-Delai, "A comparative review of deep and spiking neural networks for edge AI neuromorphic circuits," *Frontiers in Neuroscience*, vol. 19, art. 1676570, 2025, doi: 10.3389/fnins.2025.1676570. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16.

Inspected URLs:

- https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1676570/full
- https://doi.org/10.3389/fnins.2025.1676570

## Scope and contribution

The mini-review compares digital DNN and digital or analog SNN circuit implementations for edge AI. Its organizing taxonomy is DNN versus SNN, then digital versus analog SNN circuit realization. Table 1 organizes reported circuits by device architecture, implementation model, energy per operation, area per operation, and technology. Its strongest explanatory contribution is the explicit normalization of energy and area figures, coupled with a discussion of analog and digital implementation trade-offs. Deployment depth is comparative circuit-level reporting. It does not trace one trained network through a software stack to a named chip.

Material omissions include compiler and mapper behavior, interchange formats, reset and operator semantics across deployment boundaries, an evidence-class taxonomy, and an end-to-end route. The full text supports only the bounded judgments below. It does not justify cross-platform performance equivalence.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Section 3, "Spiking neural network," describes HH, ML, Izhikevich, R&F, LIF, and I&F models. |
| B | partial | Section 3 distinguishes rate and time or phase spike encoding, without a dedicated coding taxonomy. |
| C | partial | Section 3 contrasts STDP, ANN-to-SNN conversion, BPTT, and surrogate-gradient training. |
| D | partial | Section 3 describes ANN2SNN conversion and its absence of temporal dependency. |
| E | mentioned | Sections 1 and 3 name TensorFlow and related training tools but do not compare SNN frameworks. |
| F | none | No compiler or hardware-mapping taxonomy was located in Sections 1-4. |
| G | none | No interchange-format treatment was located in Sections 1-4. |
| H | full | Section 3 and Table 1 compare digital and analog neuromorphic circuits, including SpiNNaker, TrueNorth, Loihi 2, and fabricated implementations. |
| I | none | Section 4 identifies limited standardization but does not analyze edge semantics. |
| J | partial | Table 1 and Section 4 normalize energy and area figures, but do not classify silicon, simulation, and estimate evidence. |
| K | partial | Table 1 aggregates implementations and their circuit metrics, rather than a systematic application-results taxonomy. |
| L | none | No trained-network-to-specific-chip route is documented. |
