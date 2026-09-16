# S34 SNN Foundation and Recent Progress

## Identity and retrieval

Nhan Trong Luu, Duong Trung Luu, Pham Ngoc Nam, and Truong Cong Thang. *A Survey on Spiking Neural Network Foundation and Recent Progress*. *IEEE Access*, vol. 14, 2026. DOI 10.1109/ACCESS.2026.3685666. The complete 61-page version of record was inspected on 2026-09-16. Retrieval status is `verified`.

Inspected sources include https://doi.org/10.1109/access.2026.3685666 and the local author-supplied PDF `/Users/hamza/Downloads/papers-review/A_Survey_on_Spiking_Neural_Network_Foundation_and_Recent_Progress.pdf`.

## Scope and assessment

This is a broad field-entry survey. Its strongest material covers neuron and synapse models, learning paradigms, ANN-to-SNN conversion, neural codes, application families, hardware-oriented design, platforms, and software frameworks. It is unusually expansive, but breadth does not produce an end-to-end deployment method. The hardware section explains mapping and hardware-aware approximations at a conceptual level. The framework tables list simulators and training paradigms. Neither component traces a trained model through a documented compiler and mapper to measured execution on a named chip.

The article cites NIR only as support for graph-structured SNN foundations. It does not discuss NIR as an interchange format. It also reproduces energy and per-spike figures from heterogeneous platform sources without classifying whether each value is measured, simulated, normalized, or estimated. The article is therefore strong background for the first half of the proposed pedagogical chain, but it does not close the deployment-evidence gap.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | full | Section IV develops a model taxonomy from Hodgkin-Huxley through IF, LIF, QIF, AdEx, Izhikevich, resonate-and-fire, dendritic, astrocyte-modulated, and synaptic models. See pp. 78499-78505 and Table 1. |
| B | full | Section VI compares direct, rate, temporal, TTFS, phase, bit-plane, burst, and event-sensor encodings, including their equations and limitations. See pp. 78509-78511. |
| C | full | Section V covers temporal backpropagation, surrogate gradients, BPTT memory costs, online alternatives, STDP variants, supervised local learning, reward modulation, intrinsic plasticity, and hybrid training. See pp. 78505-78509 and Table 2. |
| D | full | Section V-C explains ANN-to-SNN conversion, threshold and weight balancing, batch-normalization absorption, pooling and residual compatibility, conversion latency, low-timestep techniques, and transformer conversion. See pp. 78508-78509. |
| E | full | Section XIII and Tables 9-10 compare 20 open-source SNN frameworks by training paradigm, interface, purpose, maintenance, and documentation URL. See pp. 78545-78546. |
| F | partial | Section XI-A discusses depth-wise and spatial mapping, workload balancing, communication-aware placement, and hardware constraints. It does not compare concrete compiler or mapper toolchains. See pp. 78534-78535. |
| G | none | No interchange-format treatment was found. NIR appears only as reference [270] for graph-structured SNN foundations, not as an interoperability mechanism. See p. 78522 and reference [270]. |
| H | full | Section XI surveys digital, analog, mixed-signal, memristive, photonic, and quantum-inspired substrates. Table 7 compares BrainScaleS, Neurogrid, TrueNorth, SpiNNaker, Loihi, Darwin, and Dynap-SE. See pp. 78534-78539. |
| I | partial | Hardware-aware sections discuss discretization, power-of-two parameter approximations, quantization, mapping, synaptic payload, reset behavior, memory, and learning-state costs. These concerns are not organized as cross-boundary semantic contracts or failure modes. See Sections XI-A through XI-F, pp. 78534-78538. |
| J | none | No literature-wide evidence classification separates physical measurement, modeled hardware, operation-count proxies, and software simulation. Platform values are summarized without a common provenance taxonomy. See Section XI-G and Table 7, pp. 78538-78539. |
| K | full | Sections VII-XII cover computer vision, graphs, language, reinforcement learning, sensing, hybrid systems, hardware, and emerging neuron-astrocyte and dendritic models with reported task results. See pp. 78511-78547. |
| L | none | No worked route follows one trained network through export, compilation, mapping, physical execution, and measurement on a named chip. Framework and platform inventories remain separate. See Sections XI and XIII. |

## Verification limits

All A-L judgments are based on the complete article. The audit distinguishes conceptual hardware mapping from an exercised compiler path, and distinguishes a framework inventory from a traced deployment route. No supplementary file was required for these judgments.
