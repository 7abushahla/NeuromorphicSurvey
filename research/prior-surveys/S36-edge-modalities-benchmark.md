# S36 Edge Modalities Benchmark

## Identity and retrieval

Xin Du et al. *Benchmarking Spiking Neural Networks Across Sensing Modalities on Edge Devices*. arXiv:2609.00026, 2026. DOI 10.48550/arXiv.2609.00026. The supplied manuscript carries the title *A Modality-Aware Benchmark Reveals When Spiking Neural Networks Benefit Edge Sensing*. The complete 24-page main article was inspected on 2026-09-16. Retrieval status is `verified` for the main article.

Inspected sources include https://arxiv.org/abs/2609.00026, https://arxiv.org/pdf/2609.00026, and the local author-supplied PDF `/Users/hamza/Downloads/papers-review/2609.00026v1.pdf`.

## Scope and assessment

This work is an experimental benchmark rather than a conventional literature survey. It is included because it directly tests the deployment-centered question. The benchmark crosses five sensing modalities, multiple codes, neuron models, network families, seven physical conventional edge devices, and four modeled neuromorphic platforms. Its central finding is conditional. SNN benefit depends on the interaction among modality, representation, dynamics, architecture, and hardware. Energy improvement does not imply lower latency or memory.

The paper also introduces Soul-NeuSim. Soul standardizes data, encoding, training, and profiling. NeuSim compiles trained SNN graphs through synapse extraction, capacity-constrained partitioning, logical-core placement, and cycle-level simulation. This provides meaningful compiler and edge-semantics evidence. It is not physical neuromorphic deployment. The Loihi, Darwin3, TrueNorth, and SpiNNaker2 results are explicitly simulated. Physical measurements use NCNN on CPUs, GPUs, and NPUs in named edge devices.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | full | The benchmark implements and compares 13 neuron models while holding topology and training settings fixed. It explicitly varies integration, leakage, threshold, reset, and adaptation behavior. See Results, pp. 4-5, and Methods, “Neuron models and surrogate-gradient training,” p. 11. |
| B | full | Encoding is a primary controlled dimension. The paper compares direct, rate, TTFS, phase, burst, and temporal-switch encodings and identifies direct input as non-spike-compatible. See Results, p. 4, and Methods, pp. 10-11. |
| C | partial | The benchmark uses surrogate-gradient backpropagation and supports 13 surrogate formulations. It does not survey STDP, conversion, or the broader direct-training design space. See Methods, “Neuron models and surrogate-gradient training,” p. 11. |
| D | none | No ANN-to-SNN conversion method or conversion-error analysis is presented. The word “conversion” concerns input encoding or device-format conversion. See Results and Methods, pp. 3-14. |
| E | partial | Soul-NeuSim is specified in detail and compared with selected SNN software and simulators. The work does not provide a systematic review of the broader framework landscape. See Results, pp. 7-8, and Fig. 5, p. 23. |
| F | full | NeuSim provides an automated pipeline for synapse extraction, operator fusion, capacity-constrained partitioning, logical-core clustering, mesh placement, and simulator execution. See Methods, “Neuromorphic compilation and mapping,” pp. 13-14, and Fig. 5, p. 23. |
| G | none | No hardware-neutral SNN interchange format or NIR-like semantic contract is described. NCNN is used as a deployment backend for conventional devices. See Methods, p. 12. |
| H | full | The paper evaluates Raspberry Pi 4B, Jetson Nano, Jetson NX, Jetson AGX, Redmi K80, Pixel 6, and Huawei Mate 40 physically, and models Loihi, Darwin3, TrueNorth, and SpiNNaker2. See Results, pp. 6-7, Methods, pp. 12-14, and Fig. 4, p. 22. |
| I | full | The benchmark exposes representation and execution boundaries directly. Direct inputs are labeled non-spike-compatible, backend support is conditional, temporal state affects memory, recurrent timesteps affect latency, and hardware choice changes system outcomes. See Results, pp. 3-8, and Methods, pp. 10-14. |
| J | partial | Physical device profiling is separated from cycle-level neuromorphic simulation, and latency, energy, memory, FLOPs, and synaptic operations are defined separately. The paper does not create a literature-wide evidence taxonomy. See Results, pp. 6-7, Methods, pp. 11-14, and Fig. 4, p. 22. |
| K | full | The controlled benchmark reports measured results across vision, acoustic, motion, wireless, and neuromorphic event sensing, with three repeated runs and matched protocols. See Results, pp. 3-8, Table 1, p. 20, and Methods, p. 10. |
| L | partial | A trained model is converted through NCNN and measured on seven named physical edge devices. The paper also describes a complete mapping route into NeuSim. The named neuromorphic chips remain simulated, and device-specific details are deferred to an unavailable supplement. See Methods, pp. 12-14. |

## Verification limits

The supplied PDF contains the complete main article and a list of supplementary contents, but not the supplementary text or Figs. S1-S10. The main article supports every score above. Exact per-device settings, detailed energy procedures, and additional per-dataset results cited only in the supplement remain unverified. The work is a September 2026 preprint and must be described as such.
