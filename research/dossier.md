# From Neural Networks to Neuromorphic Execution

**A survey of the ANN-to-SNN deployment stack, from application to silicon.**

Research dossier, consolidated 16 September 2026. This document is the evidence base
from which the survey site and its main figure are generated. Every factual claim
carries a bracketed source identifier resolved in the per-section reference lists, and
every source is labeled by type so that a reader can weigh it.

## Evidence classes

Applied to every edge in the stack and to every published result.

| Class | Meaning |
|-------|---------|
| E1 | Physical silicon, measured. Ran on the chip, with latency and/or energy measured on hardware. |
| E2 | Physical silicon, accuracy only. Ran on the chip, with no hardware latency or energy measurement reported. |
| E3 | Documented path, unexercised. An official toolchain edge exists and is documented, but no published run of this model class traverses it. |
| E4 | Hardware model. RTL synthesis, cycle-accurate simulation, or an analytical energy model. No silicon. |
| E5 | Software simulation. Accuracy versus T on GPU, possibly with operation counts. |

E3 is a distinct class and not a weaker E2. A documented backend and a published run are
different facts. E4 is not a failure grade. Synthesized RTL is real evidence for a design
even when no accessible platform executes it. A single paper may hold two classes for two
different claims, and is recorded that way rather than flattened to one.

## Source types

Peer-reviewed, preprint, official documentation, repository state, vendor material, and
community commentary. Non-academic sources are admissible throughout, because much of the
deployment reality is recorded nowhere else. Where a consequential claim rested on a weak
source, it was corroborated at the primary artifact.

## Contents

- **1 Introduction** — existing surveys and the gap, contributions, organization
- **2 Preliminaries** — neuron models, reset semantics, neural codes, formalization, execution contracts
- **3 Primary Training Paths** — direct training, classical conversion
- **4 Advanced Conversion Techniques** — low-latency, quantization-aware, mixed-timestep, hardware-aware, calibration
- **5 Alternative Codes** — TTFS, phase, sigma-delta, rank order coding
- **6 Hardware and Software Deployment Stack** — platforms, frameworks, compilers, runtimes, documented routes
- **7 Applications and Deployment Evidence** — per-platform deployments, the cross-case evidence table, measurement comparability
- **8 Challenges and Future Directions** — the nine seams of the stack
- **9 Conclusion**

---

# 1 Introduction

Neuromorphic hardware promises inference at a fraction of the energy cost of conventional
accelerators, by replacing dense synchronous arithmetic with sparse, event-driven spikes
[davies-2021-loihi], [kudithipudi-2025]. Spiking neural networks (SNNs) are the computational
model built to exploit that substrate. Two paths lead to a trained SNN. Direct training
back-propagates through the spiking nonlinearity with a surrogate gradient, which is expensive
and unstable at the depths and timestep counts current vision benchmarks require
[eshraghian-2023]. ANN-to-SNN conversion instead trains a conventional ReLU network with
ordinary backpropagation and then re-expresses each ReLU as an integrate-and-fire (IF) neuron,
substituting a spike count accumulated over `T` timesteps for a single real-valued activation.
Conversion exists because it sidesteps direct training's optimization difficulty, and a line of
work from 2021 onward, anchored by QCFS, has driven the timestep count `T` needed to match ANN
accuracy down from the hundreds into the single digits [bu-2022-qcfs].

That correspondence between a ReLU activation and a count of `T` spikes is proved on paper and
verified in software simulation. Whether it is proved on hardware is a separate question, and it
is the question this survey answers. A trained network that reaches a chip must survive a
sequence of handoffs, each governed by a different toolchain, a different reset rule, a different
spike payload, and a different time model, and each handoff can silently break the correspondence
the algorithm paper established. This survey traces those handoffs. It asks, for the low-`T`
conversion literature specifically, whether the correspondence its authors prove reaches physical
silicon, and if so, by what documented path, or whether the accuracy gains accumulate only in
simulation while a separate, older deployment literature continues to run a different, frozen
toolchain on a different, rate-coded model.

## 1.1 Existing Surveys

Thirty-seven prior surveys of spiking neural networks and neuromorphic computing, spanning 2017
through 2026, were scored against twelve axes: neuron models (A), neural codes (B), direct
training (C), ANN-to-SNN conversion (D), software frameworks (E), compilers and hardware-mapping
toolchains (F), interchange formats (G), hardware platforms (H), edge semantics, meaning what a
handoff between layers or platforms preserves or breaks (I), evidence classification, meaning
whether a claim is separated as physical silicon, simulation, or an operation-count estimate (J),
applications with measured results (K), and end-to-end traceable routes from a trained network to
a named chip (L). Each cell is scored full, partial, mentioned, or absent, argued from the
survey's own stated contributions and section structure, and from direct keyword verification of
the full text wherever the source was available rather than assumed from the abstract or title.

| # | Survey | Year | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Pedersen et al., NIR [pedersen-2024-nir] | 2024 | P | – | – | – | F | P | F | F | F | P | – | P |
| 2 | Kudithipudi et al. [kudithipudi-2025] | 2025 | M | M | M | – | P | P | M | F | P | P | P | – |
| 3 | Deng et al., EdgeSNN [deng-2025-edgesnn] | 2025 | F | P | F | F | M | M | – | F | P | F | F | P |
| 4 | Yik et al., NeuroBench [yik-2025-neurobench] | 2025 | – | – | – | – | P | – | – | P | – | F | F | M |
| 5 | Davies et al., Loihi survey [davies-2021-loihi] | 2021 | P | P | P | P | M | P | – | F | M | P (single chip) | F | P (single chip) |
| 6 | Huynh, Balaji, Das [huynh-2022] | 2022 | – | – | – | – | – | F | – | P | P | M | – | P |
| 7 | Roy, Jaiswal, Panda [roy-2019] | 2019 | P | P | F | P | – | – | – | F | – | – | P | – |
| 8 | Schuman et al., 35-year survey [schuman-2017] | 2017 | F | P | F | M | P | – | – | F | – | – | F | – |
| 9 | Schuman et al., Opportunities [schuman-2022] | 2022 | P | P | P | M | – | – | – | P | – | – | P | – |
| 10 | Eshraghian et al. [eshraghian-2023] | 2023 | P | F | F | P | M | – | – | M | – | – | M | – |
| 11 | Rathi et al., Algorithms to Hardware [rathi-2023] | 2023 | F | F | F | F | M | P | – | F | – | – | P | – |
| 12 | Yamazaki et al. [yamazaki-2022] | 2022 | F | P | F | P | F | – | – | M | – | – | F | – |
| 13 | Ivanov et al. [ivanov-2022] | 2022 | M | – | – | – | – | – | – | F | – | – | M | – |
| 14 | Basu et al., SNN ICs [basu-2022] | 2022 | – | – | – | – | – | – | – | F | – | P | M | – |
| 15 | Nunes et al. [nunes-2022] | 2022 | F | F | F | M | M | – | – | M | – | – | P | – |
| 16 | Khan et al. [khan-2025] | 2025 | P | – | F | F | M | – | – | F | – | – | F | – |
| 17 | Zheng et al. [zheng-2022] | 2022 | F | M | F | M | – | – | – | – | – | – | – | – |
| 18 | "Towards Neuromorphic Computing on Edge" [anon-edge-survey] | n.d. | F | M | P | F | – | – | – | – | M | – | P | – |
| 19 | Xie, Yang, Gao [xie-2024] | 2024 | M | – | P | – | – | – | – | M | – | – | – | – |
| 20 | Ferreira et al. [ferreira-2025] | 2025 | F | M | M | – | – | – | – | F | – | P | F | – |
| 21 | Manna et al. [manna-2023] | 2023 | – | – | – | – | F | P | – | – | – | – | – | M |
| 22 | Gallego et al., Event-based Vision [gallego-2022] | 2019/22 | – | – | M | – | M | – | – | P (sensor) | – | – | F | – |
| 23 | Gebregiorgis et al. [gebregiorgis-2025] | 2025 | F | M | F | M | – | F† | M† | F | M† | – | F | P† |
| 24 | Bouvier et al. [bouvier-2019] | 2019 | M | – | – | – | – | – | – | F | – | – | M | – |
| 25 | Shrestha et al. [shrestha-2022] | 2022 | F | – | M | – | – | – | – | F | – | – | M | – |
| 26 | "A New Era in Computing," Chips (MDPI) [chips-2026] | 2026 | P | – | – | – | – | – | – | F | – | P | M | – |
| 27 | "Brain-inspired computing systems," EPJB [epjb-2024] | 2024 | – | – | – | – | – | – | – | F | – | P | M | – |
| 28 | "Toward Large-scale SNNs" [spiking-transformers-2024] | 2024 | P | – | F | F | – | – | – | – | – | – | M | – |
| 29 | "A Practical Tutorial on SNNs" (MDPI) [mdpi-tutorial-2025] | 2025 | F | F | F | P | F | – | – | M | – | P (self only) | F | – |
| 30 | Al Abdul Wahid et al. [alabdulwahid-2024] | 2024 | F | – | P | – | – | – | – | F | – | – | M | – |
| 31 | Tayarani-Najaran, Schmuker [tayarani-2021] | 2021 | – | F | – | – | – | – | – | F (sensor) | – | – | F | – |
| 32 | Cimarelli et al. [cimarelli-2025] | 2025 | – | – | – | – | – | – | – | F (sensor) | – | – | F | – |
| 33 | "Four-Stage Structural Evolution SNN" [npl-2026] | 2026 | M | – | P | P | – | – | – | – | – | – | – | – |
| 34 | Luu et al. [luu-2026] | 2026 | M† | M† | M† | M† | M† | – | – | M† | – | – | M† | – |
| 35 | Caviglia et al., NeuroTrain [caviglia-2026] | 2026 | M | – | F | P | P | – | – | – | – | P | – | – |
| 36 | "Benchmarking SNNs across sensing modalities" [edge-bench-2026] | 2026 | – | – | – | – | – | – | – | P | – | P | F | M |
| 37 | Farsa et al. [farsa-2026] | 2026 | – | – | – | – | M | P | – | F | M | – | – | M |

`†` marks a score argued from abstract, reference list, or a vault note rather than confirmed
full text.

Read as a whole, the table does not show an empty field. It shows a field that has been worked
piecemeal. Neuron models, codes, and direct-versus-conversion training are covered repeatedly and
well; hardware platforms are covered by nearly every survey that touches applications; software
frameworks appear often enough that a reader can assemble a partial picture from Manna et al.
[manna-2023] and Yamazaki et al. [yamazaki-2022]. What does not recur is the combination: a
survey that treats a handoff between two adjacent layers of the stack as a fact with its own
mechanism, its own preserved and broken properties, and its own evidence grade, and that does
this consistently enough to trace a full route from a trained network to a named chip. Where a
survey approaches that combination, as the six discussed below do, it approaches one or two axes
at a time, over a narrow scope, or as a benchmark-design decision rather than a retrospective
audit of the literature's own claims. The gap the present survey addresses is real at that level
of specificity. It is not a claim that nothing prior touches deployment, hardware, or evidence
quality.

That specificity matters because the alternative, weaker claim is checkable and false. Schuman et
al.'s widely cited 2022 survey in *Nature Computational Science* [schuman-2022] is representative
of the field's general-purpose surveys: a full-text keyword search of the paper returns zero
occurrences of "software," zero of "compiler," and zero of "toolchain." The word "silicon" occurs
twice, both times in the single sentence noting that current large-scale neuromorphic computers
are silicon-based, not in any discussion of a software or compilation path to that silicon. This
survey, together with its companion 2017 survey by an overlapping author list [schuman-2017], sets
the domain's vocabulary of neuron models and applications without ever naming the toolchain a
reader would need to move a trained model onto the hardware it describes. Most of the field's
general surveys share this shape.

Six prior works depart from that shape closely enough that the present survey's contribution must
be argued against them by name.

**NIR** (Pedersen et al., 2024, *Nature Communications*) [pedersen-2024-nir] is the strongest
prior instance of edge semantics as a first-class concern. It defines a fixed set of hybrid
continuous-time primitives shared across seven simulators and four physical chips (Loihi 2,
Speck, SpiNNaker2, Xylo), and it does what almost nothing else in the table does: it states, by
name, which neuron mechanisms its own representation excludes (adaptive threshold, gating,
resonate-and-fire, multicompartmental dynamics), and it reports measured divergence between the
idealized continuous-time model and eleven discretized platform implementations for a recurrent
network. That is a genuine instance of edge semantics, evidence classification, and an end-to-end
traceable route, all three, in one paper. Its scope is the limit. NIR deploys three benchmark
graphs, at most one convolutional network among them, not a family of deployable CNN-scale
classifiers, and its own primitive specification has no notion of reset by subtraction, the reset
rule the ANN-to-SNN conversion literature depends on. The present survey's distinction from NIR is
one of scope and of the specific mechanism under study, full convolutional networks under the
reset-by-subtraction IF neuron, not a claim that NIR left the edge-semantics question untouched.

**Kudithipudi et al. 2025** (*Nature*) [kudithipudi-2025] names the gap this survey addresses
without building the apparatus to close it. Its Figure 4 is captioned as case studies showing gaps
in the neuromorphic software ecosystem relative to conventional AI/ML frameworks, and its text
states plainly that a hardware abstraction layer and a general compilation scheme for porting an
arbitrary SNN to an arbitrary architecture do not yet exist, and that metrics for comparing
hardware performance across platforms lack consensus. That is a landmark venue stating, in its own
words, that the problem is real and unsolved. It is diagnosis, not a taxonomy. The paper does not
catalog what specifically breaks at each boundary (reset semantics, operator coverage, spike
payload, time model), does not classify evidence by physical, simulated, or estimated origin
beyond naming the absence of consensus metrics, and offers no worked end-to-end case study. The
present survey treats Kudithipudi et al. as the field's own acknowledgment that its contribution
is needed, not as a competing instance of it.

**NeuroBench** (Yik et al. 2025, *Nature Communications*) [yik-2025-neurobench] and the **EdgeSNN
survey** (Deng et al. 2025) [deng-2025-edgesnn] both build an explicit two-track evidence
structure, an "algorithm track" that reports hardware-independent proxies such as synaptic
operation counts, against a "systems track" that reports measurement on deployed hardware. This is
real precedent for separating simulated estimates from physical measurement, and it is the closest
prior instance of the spirit of a graded evidence classification. It is two-way, algorithm proxy
versus system measurement, where the present survey's five-class scheme (E1 through E5) separates
physical silicon with full measurement, physical silicon with accuracy only, a documented but
unexercised toolchain path, a hardware model without silicon, and pure software simulation, into
distinct grades with different evidentiary weight. More consequentially, NeuroBench's split is a
benchmark-design decision, a protocol for future submissions to follow, not a classification
applied retrospectively to grade the claims already published in the literature. Deng et al.
describes itself, in its own words, as the first dedicated and comprehensive survey of SNNs at the
edge, and it is the closest prior survey in territory to this one: it surveys lightweight models,
resource-aware training, and hardware heterogeneity as open deployment concerns, and its Section V
dual-track benchmarking strategy explicitly extends NeuroBench's split. It inventories deployment
techniques and hardware categories. It does not build a taxonomy of what breaks at each handoff,
and it has no single worked route tracing one trained network through one full pipeline to one
named chip with reported numbers.

**Davies et al. 2021** (*Proceedings of the IEEE*) [davies-2021-loihi] is the strongest prior
precedent for a traceable end-to-end route, repeatedly. It reports latency and energy for specific
trained and converted networks on physical Loihi silicon across event-based data processing,
adaptive control, constrained optimization, sparse regression, and graph search. That density of
genuine E1-grade evidence is unusual among general surveys. It is confined by construction to one
chip family, and it does not attempt to generalize what a given network configuration would look
like if retargeted to a different platform, the cross-chip comparison the present survey's route
tracing requires.

**Huynh, Balaji, and Das 2022** [huynh-2022] is the only prior survey organized entirely around
compiler and mapping toolchains for neuromorphic hardware, covering SentryOS and SentryC,
TrueNorth's Corelet paradigm, PACMAN for SpiNNaker, SpiNeMap, PyCARL, and related run-time
managers. It is real coverage of axis F, the compiler and mapping-toolchain axis, but of a
different toolchain family than the one this survey's own worked examples require: NxTF, Lava's
NetX, the DynapCNN mapper, and sPyNNaker do not appear together, or in most cases at all, in its
reference set. No survey located in the course of this research treats those four toolchains
comparatively in one place. That absence, not a claim that compiler surveys do not exist, is the
finding that motivates the present survey's cross-toolchain scope.

## 1.2 Contributions

This survey makes three contributions, each stated so that it can be checked against the evidence
above and against the field's own published record.

**A cross-toolchain taxonomy of the deployment edges.** No prior survey treats the handoff between
a trained model and a target chip as a set of typed facts, mechanism, what is preserved, what
breaks, a primary source, and an evidence grade, across the toolchain families a converted SNN
would actually need to cross: NxTF, Lava's NetX, the DynapCNN mapper, and sPyNNaker. Huynh, Balaji,
and Das [huynh-2022] cover a different toolchain family under the same axis; no located survey
covers these four together. This survey's taxonomy fills that specific absence, not a general
absence of compiler or software-ecosystem discussion.

**A five-way evidence classification (E1 through E5) applied to a literature, not to a benchmark
protocol.** NeuroBench [yik-2025-neurobench] and the EdgeSNN survey [deng-2025-edgesnn] establish a
two-way physical-versus-proxy split as a forward-looking submission standard. This survey applies a
finer, five-way split, physical silicon with full measurement (E1), physical silicon with accuracy
only (E2), a documented but unexercised toolchain path (E3), a hardware model without silicon (E4),
and pure software simulation (E5), retrospectively, to grade claims already in print. The same
paper can occupy two classes at once for two different claims, which a coarser or forward-only
protocol cannot represent.

**A structural claim about a two-population field, with a tested refinement.** Algorithm papers in
the low-`T` conversion lineage advance accuracy and never deploy their own method to silicon; 0 of
13 QCFS-lineage papers checked directly report their own conversion running on a named chip.
Deployment papers reach silicon and do not use the recent algorithms; every hardware-deployment
paper checked routes through the classical SNN Toolbox pipeline or direct training, and SNN
Toolbox's own development record ends within months of the point where the low-`T` literature
began accelerating (last release March 2021, last substantive commit August 2022). The refinement,
tested rather than assumed, is that every confirmed instance of a new conversion method reaching
physical silicon abandons rate coding for a platform-native code: Quartz [lenz-2023-quartz] uses
single-spike time-to-first-spike coding on Loihi 1, and Brehove et al. [brehove-2026] uses Loihi
2's native graded sigma-delta spikes. **The falsifier is explicit and was searched for
deliberately**: a paper that both proposes a new low-`T`, rate-coded conversion method and deploys
it to physical silicon with measurement would weaken this claim. None was found.

Two qualifications belong alongside the claim rather than beneath it, because they were found by
the same search that confirmed the claim and they sharpen rather than soften it. First, QCFS itself
[bu-2022-qcfs] cites two physical-hardware papers, Massa et al. 2020 and Singh et al. 2021, in its
related work, correctly, as acknowledged prior art rather than as throat-clearing motivation. Of
the thirteen QCFS-lineage descendants audited against their full text, twelve revert to citing
chip-architecture papers only in the introduction, as generic motivation, never as prior deployment
work and never in a methods or experiments section. QCFS is the single exception, not the rule.
Second, a rate-coded QCFS and SRP baseline has, in one instance, been measured on physical
neuromorphic silicon, a Lynxi HP201 accelerator, but only as a comparison row inside a later,
unrelated paper, Adaptive Fission (Jiang et al., NeurIPS 2025), whose own algorithmic contribution
is population coding, itself a departure from plain rate coding. The defensible form of the claim
is therefore that no QCFS-lineage paper deploys its own method to silicon, and the one occasion a
rate-coded QCFS or SRP configuration reached silicon required a different paper's rate-coding
departure to motivate the run.

## 1.3 Organization

Section 2 establishes the preliminaries: the biological motivation, the IF and LIF neuron models
and the two competing reset rules, the family of neural codes from rate through sigma-delta, the
activation-to-spike-count correspondence that gives conversion its formal grounding, and the
execution contracts, time model, spike payload, and precision, that Section 6 later measures
platforms against. Section 3 covers the two primary training paths, direct training and classical
ANN-to-SNN conversion. Section 4 covers the advanced conversion techniques that reduced `T` from
the classical literature's hundreds of steps to single digits: low-latency conversion,
quantization- and distribution-aware conversion, mixed-timestep and per-layer allocation, and
hardware-aware co-design. Section 5 covers the alternative, non-rate codes, temporal and
time-to-first-spike, phase and weighted-slot, and differential and sigma-delta payloads, the
representations the refined structural claim in Section 1.2 identifies as the ones that reach
silicon. Section 6 is the hardware and software deployment stack itself: platforms, training and
simulation frameworks, export and compilation, runtime and host I/O, and the documented routes that
connect them, the taxonomy this survey's first contribution builds. Section 7 collects applications
and deployment evidence by platform family, Loihi, DYNAP-CNN and Speck, SpiNNaker and BrainScaleS,
and FPGA and custom ASIC implementations, closing with a cross-case evidence table graded by the
five-way classification from Section 1.2's second contribution. Section 8 states the open
challenges the stack argument exposes, operator coverage, reset-semantics mismatch, encoding and
readout cost, time-model mismatch, the absence of an execution model for per-layer timestep
horizons, incomparable efficiency claims across measurement boundaries, device availability, and
the general portability gap. Section 9 concludes.

## References for Section 1

- [pedersen-2024-nir] Pedersen, J. E. et al. "Neuromorphic intermediate representation: a unified
  instruction set for interoperable brain-inspired computing." *Nature Communications* 15, 8122
  (2024). https://doi.org/10.1038/s41467-024-52259-9. Peer-reviewed.
- [kudithipudi-2025] Kudithipudi, D. et al. "Neuromorphic computing at scale." *Nature* 637,
  801-812 (2025). https://doi.org/10.1038/s41586-024-08253-8. Peer-reviewed.
- [deng-2025-edgesnn] Deng, S. et al. "Edge Intelligence with Spiking Neural Networks."
  arXiv:2507.14069 (2025). Preprint.
- [yik-2025-neurobench] Yik, J. et al. "The NeuroBench framework for benchmarking neuromorphic
  computing algorithms and systems." *Nature Communications* 16, 1545 (2025).
  https://doi.org/10.1038/s41467-025-56739-4. Peer-reviewed.
- [davies-2021-loihi] Davies, M. et al. "Advancing Neuromorphic Computing With Loihi: A Survey of
  Results and Outlook." *Proceedings of the IEEE* 109(5), 911-934 (2021).
  https://doi.org/10.1109/JPROC.2021.3067593. Peer-reviewed.
- [huynh-2022] Huynh, P. K., Varshika, M. L., Paul, A., Isik, M., Balaji, A., Das, A. "Implementing
  Spiking Neural Networks on Neuromorphic Architectures: A Review." arXiv:2202.08897 (2022).
  Preprint.
- [schuman-2022] Schuman, C. D. et al. "Opportunities for neuromorphic computing algorithms and
  applications." *Nature Computational Science* 2, 10-19 (2022).
  https://doi.org/10.1038/s43588-021-00184-y. Peer-reviewed.
- [schuman-2017] Schuman, C. D. et al. "A Survey of Neuromorphic Computing and Neural Networks in
  Hardware." arXiv:1705.06963 (2017). Preprint.
- [roy-2019] Roy, K., Jaiswal, A., Panda, P. "Towards spike-based machine intelligence with
  neuromorphic computing." *Nature* 575, 607-617 (2019). https://doi.org/10.1038/s41586-019-1677-2.
  Peer-reviewed.
- [eshraghian-2023] Eshraghian, J. K. et al. "Training Spiking Neural Networks Using Lessons From
  Deep Learning." *Proceedings of the IEEE* 111(9) (2023).
  https://doi.org/10.1109/JPROC.2023.3308088. Peer-reviewed.
- [rathi-2023] Rathi, N. et al. "Exploring Neuromorphic Computing Based on Spiking Neural Networks:
  Algorithms to Hardware." *ACM Computing Surveys* 55(12), Art. 243 (2023).
  https://doi.org/10.1145/3571155. Peer-reviewed.
- [yamazaki-2022] Yamazaki, K., Vo-Ho, V.-K., Bulsara, D., Le, N. "Spiking Neural Networks and Their
  Applications: A Review." *Brain Sciences* 12(7), 863 (2022).
  https://doi.org/10.3390/brainsci12070863. Peer-reviewed.
- [ivanov-2022] Ivanov, D., Chezhegov, A., Kiselev, M., Grunin, A., Larionov, D. "Neuromorphic
  artificial intelligence systems." *Frontiers in Neuroscience* 16, 959626 (2022).
  https://doi.org/10.3389/fnins.2022.959626. Peer-reviewed.
- [basu-2022] Basu, A., Frenkel, C., Deng, L., Zhang, X. "Spiking Neural Network Integrated
  Circuits: A Review of Trends and Future Directions." *IEEE CICC 2022*.
  https://doi.org/10.1109/CICC53496.2022.9772783. Peer-reviewed.
- [nunes-2022] Nunes, J. D., Carvalho, M., Carneiro, D., Cardoso, J. S. "Spiking Neural Networks: A
  Survey." *IEEE Access* 10, 60738-60764 (2022). https://doi.org/10.1109/ACCESS.2022.3179968.
  Peer-reviewed.
- [khan-2025] Khan, A. H. et al. "Spiking Neural Networks: A Comprehensive Survey of Training
  Methodologies, Hardware Implementations and Applications." *Artificial Intelligence Science and
  Engineering* (2025). https://doi.org/10.23919/aise.2025.000013. Peer-reviewed.
- [zheng-2022] Zheng, S. et al. "An Introductory Review of Spiking Neural Network and Artificial
  Neural Network." *CS & IT-CSCP 2022*, 129-145. https://doi.org/10.5121/csit.2022.121010.
  Peer-reviewed.
- [anon-edge-survey] "Towards Neuromorphic Computing on Edge: A Survey on Efficient Techniques for
  Spiking Neural Networks." Venue and author list unconfirmed; vault PDF filename
  `1_Towards_Neuromorphic_Computi.pdf`. Preprint (unconfirmed venue).
- [xie-2024] Xie, H., Yang, G., Gao, W. "Toward Efficient Deep Spiking Neuron Networks: A Survey on
  Compression." Springer, ISBN 978-981-97-6125-8 (2024). Peer-reviewed (book chapter).
- [ferreira-2025] Ferreira, P. M., Wang, S., Gao, Y., Benlarbi-Delai, A. "A comparative review of
  deep and spiking neural networks for edge AI neuromorphic circuits." *Frontiers in Neuroscience*
  19, 1676570 (2025). https://doi.org/10.3389/fnins.2025.1676570. Peer-reviewed.
- [manna-2023] Manna, D. L., Vicente, A., Kirkland, P., Bihl, T., Di Caterina, G. "Frameworks for
  SNNs: a Review of Data Science-oriented Software and an Expansion of SpykeTorch."
  arXiv:2302.07624 (2023). Preprint.
- [gallego-2022] Gallego, G. et al. "Event-based Vision: A Survey." *IEEE TPAMI* 44(1), 154-180
  (2022; arXiv 2019). https://doi.org/10.1109/TPAMI.2020.3008413. Peer-reviewed.
- [gebregiorgis-2025] Gebregiorgis, A. et al. "Spike-based neuromorphic computing: An overview from
  bio-inspiration to hardware architectures and learning mechanisms." *Microprocessors and
  Microsystems* (2025). https://doi.org/10.1016/j.micpro.2025.105240. Peer-reviewed. Scores marked
  `†` are assessed from abstract and reference list only, not independently confirmed against full
  text.
- [bouvier-2019] Bouvier, M. et al. "Spiking neural networks hardware implementations and
  challenges: A survey." *ACM JETC* 15(2), 1-35 (2019). Peer-reviewed. Score pulled from citation
  context in later work, not independently fetched in full.
- [shrestha-2022] Shrestha, A. et al. "A Survey on Neuromorphic Computing: Models and Hardware."
  *IEEE Circuits and Systems Magazine* 22(2), 6-35 (2022). https://doi.org/10.1109/MCAS.2022.3166331.
  Peer-reviewed. Score pulled from citation context in later work, not independently fetched in
  full.
- [chips-2026] "A New Era in Computing: A Review of Neuromorphic Computing Chip Architecture and
  Applications." *Chips* (MDPI) 5(1), 3 (2026). https://doi.org/10.3390/chips5010003.
  Peer-reviewed.
- [epjb-2024] "Brain-inspired computing systems: a systematic literature review." *European
  Physical Journal B* (2024). https://doi.org/10.1140/epjb/s10051-024-00703-6. Peer-reviewed.
- [spiking-transformers-2024] "Toward Large-scale Spiking Neural Networks." arXiv:2409.02111
  (2024). Preprint.
- [mdpi-tutorial-2025] "A Practical Tutorial on Spiking Neural Networks: Comprehensive Review,
  Models, Experiments, Software Tools, and Implementation Guidelines." *MDPI* (2025).
  https://www.mdpi.com/2673-4117/6/11/304. Peer-reviewed.
- [alabdulwahid-2024] Al Abdul Wahid, S., Asad, A., Mohammadi, F. "A Survey on Neuromorphic
  Architectures for Running Artificial Intelligence Algorithms." *Electronics* 13(15), 2963 (2024).
  https://doi.org/10.3390/electronics13152963. Peer-reviewed.
- [tayarani-2021] Tayarani-Najaran, M.-H., Schmuker, M. "Event-Based Sensing and Signal Processing
  in the Visual, Auditory, and Olfactory Domain: A Review." *Frontiers in Neural Circuits* 15,
  610446 (2021). https://doi.org/10.3389/fncir.2021.610446. Peer-reviewed.
- [cimarelli-2025] Cimarelli, C. et al. "Hardware, Algorithms, and Applications of the Neuromorphic
  Vision Sensor: a Review." arXiv:2504.08588 (2025). Preprint.
- [npl-2026] "A Four-Stage Structural Evolution Framework for SNNs: A Review and Perspective from
  Binary ANN to Event-Driven Models." *Neural Processing Letters* 58:14 (2026).
  https://link.springer.com/article/10.1007/s11063-025-11832-z. Peer-reviewed. Recorded from a
  vault note; underlying PDF not independently retrieved.
- [luu-2026] Luu, N. T., Luu, D. T., Nam, P. N., Thang, T. C. "A Survey on Spiking Neural Network
  Foundation and Recent Progress." IEEE (2026), document 11488853. Peer-reviewed. Recorded from a
  vault note; underlying PDF not independently retrieved, all scores marked `†`.
- [caviglia-2026] Caviglia, A. et al. "NeuroTrain: Surveying Local Learning Rules for SNNs with an
  Open Benchmarking Framework." arXiv:2605.15058 (2026). Preprint. Recorded from a vault note;
  underlying PDF not independently retrieved.
- [edge-bench-2026] "Benchmarking spiking neural networks across sensing modalities on edge
  devices." arXiv:2609.00026 (2026). Preprint. Recorded from a vault note; underlying PDF not
  independently retrieved.
- [farsa-2026] Farsa, E. Z. et al. "GPU and RISC-V acceleration for neuromorphic computing based on
  SNNs: taxonomy, comparison, and open challenges." *Neuromorphic Computing and Engineering*,
  accepted manuscript (2026). https://iopscience.iop.org/article/10.1088/2634-4386/aea4eb.
  Peer-reviewed. Recorded from a vault note; underlying PDF not independently retrieved.
- [bu-2022-qcfs] Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN Conversion
  for High-accuracy and Ultra-low-latency Spiking Neural Networks." ICLR 2022, arXiv:2303.04347.
  Peer-reviewed (conference).
- [lenz-2023-quartz] Lenz, G., Orchard, G., Sheik, S. "Ultra-low-power Image Classification on
  Neuromorphic Hardware." arXiv:2309.16795 (2023-2024). Preprint.
- [brehove-2026] Brehove, T., Tumpa, S. N., Kyubwa, E., Menon, A., Narayanan, V. "Sigma-Delta
  Neural Network Conversion on Loihi 2." ICONS 2026, arXiv:2505.06417. Peer-reviewed (conference).
- [jiang-2025-adaptive-fission] Jiang, Y. et al. "Adaptive Fission." NeurIPS 2025 proceedings.
  Peer-reviewed (conference). Code repository
  https://github.com/JiangYizhou16/Adaptive-Fission is repository state, not independently
  re-verified.


---

# 2 Preliminaries

This section establishes every concept the stack argument in later sections depends on. It is deliberately not a glossary. Each subsection carries a claim forward: neuron models determine what a hardware substrate can natively execute (2.2), codes determine what a spike train represents and what it costs to decode (2.3), the activation-to-spike-count correspondence explains why the conversion literature is bound to a uniform quantization grid it never chose (2.4), and execution contracts define the axes Section 6 later uses to compare platforms (2.5).

## 2.1 From Biological Neurons to Spiking Models

A biological neuron integrates synaptic input arriving at its dendrites within its soma. When the membrane potential crosses a threshold, the neuron emits an action potential that propagates along its axon to postsynaptic targets. Communication is event-driven and effectively binary. A spike either occurs or it does not [cao2015]. Artificial neural network (ANN) neurons abstract this into a single real-valued weighted sum followed by a static nonlinearity, discarding both the discrete event structure and the temporal dynamics of the biological original. Spiking neural network (SNN) neurons restore both. A spiking neuron maintains an internal state, the membrane potential, that evolves over a simulation horizon of $T$ discrete steps (or continuous time, on analog substrates), and it communicates with other neurons only through discrete spike events rather than continuous activations [maass1997].

This restoration is not merely biological fidelity for its own sake. It is what makes a network executable on hardware that computes by accumulation rather than multiplication, and it is what makes the neuron and coding choices in the rest of this section load-bearing for deployment rather than a stylistic variation on the ANN.

Model families span a wide range of biological detail. The Hodgkin-Huxley model describes the ionic conductances underlying the action potential with four coupled differential equations and is treated in this literature as a ceiling on biological realism, not a deployment target [hodgkin1952]. The Izhikevich model reproduces a wide range of observed firing patterns with two coupled equations and four parameters, trading realism for tractability [izhikevich2003]. Neither is used in the ANN-to-SNN conversion literature this survey is built around. The neuron models actually deployed sit at the simple end of this spectrum, described next.

[FIGURE: biological neuron schematic, dendrites/soma/axon/synapse, paired with the abstracted artificial-neuron weighted-sum-and-nonlinearity diagram, to set up why the spiking models in 2.2 restore what the ANN abstraction discarded. Redraw of Figures/biological_neuron.pdf.]

## 2.2 Spiking Neuron Models

Every neuron model below is characterized by two things: its state variables and how those states evolve between spikes. The choice of model determines what a piece of hardware can execute without a workaround, which is the axis Section 6's platform comparison turns on.

### Integrate-and-fire (IF)

The IF neuron holds one state variable, the membrane potential $V(t)$, and integrates weighted input with no decay:
$$V(t) = V(t-1) + \sum_i w_i s_i(t) + b.$$
A spike is emitted when $V(t)$ crosses a threshold $V_{th}$. IF is the canonical neuron of the ANN-to-SNN conversion literature specifically because, under reset-by-subtraction and constant or rate-coded input, its time-averaged firing rate is an unbiased estimator of the ReLU activation it was converted from [cao2015] [rueckauer2017]. Nearly every rate-coding conversion method reviewed for this survey targets an IF neuron, not a leaky variant.

### Leaky integrate-and-fire (LIF)

LIF adds an exponential decay term, so the membrane relaxes toward a resting potential between inputs:
$$V(t) = \lambda V(t-1) + \sum_i w_i s_i(t) + b, \qquad 0 < \lambda < 1.$$
The decay constant $\lambda$ (equivalently a membrane time constant $\tau_m$ in continuous time) is an additional degree of freedom absent from IF. LIF is the default built-in neuron on SpiNNaker (`IF_curr_exp`) and is available as a selectable leak-disabled or leak-enabled mode on DYNAP-CNN and Speck, where leak requires a bias term on the preceding convolution and an externally configured slow-clock frequency [sinabs-docs].

### Current-based LIF (CUBA LIF)

CUBA LIF separates a first-order synaptic current state $u(t)$, itself leaky-integrated, from the membrane voltage state $V(t)$:
$$u(t) = \alpha_u u(t-1) + (\text{weighted spike input}), \qquad V(t) = \alpha_v V(t-1) + u(t) + b.$$
This gives the neuron two decaying state variables instead of one. CUBA LIF is Loihi's native, default neuron model, and it is exposed directly as `slayer.block.cuba.*` in Lava-DL [shrestha2023] [lava-dl]. Loihi's native single-compartment reset for this neuron is hard reset to zero, a fact with direct consequences for the reset discussion below.

### Adaptive / threshold-adaptive neurons (ALIF)

ALIF adds spike-frequency adaptation: the effective firing threshold rises after each spike and relaxes back toward baseline between spikes, or equivalently a decaying after-hyperpolarizing (AHP) current is subtracted from the input. In discrete time, following Bellec et al., the membrane and an adaptive threshold component evolve jointly:
$$V(t{+}1) = \alpha V(t) + (1-\alpha)\sum w \cdot s(t), \qquad B(t{+}1) = b_0 + \beta\, b(t), \qquad b(t{+}1) = \rho\, b(t) + (1-\rho)\, s(t),$$
with a spike emitted when $V \geq B$ [bellec2018]. Adaptation is what gives recurrent SNNs an LSTM-like long-memory capacity without a genuine multiplicative gate. On Loihi, ALIF is realized through the multi-compartment mechanism described below, at a cost of two compartments per neuron rather than one [nxtf2021]. On BrainScaleS-2, adaptation is native: the analog AdEx circuit directly implements a spike-triggered adaptation current with its own decay constant, with no compartment-doubling cost [brainscales-pehle2022].

### Multi-compartment neurons

A multi-compartment neuron is built from several coupled sub-units, each with its own state, rather than a single lumped state variable. In the ANN-to-SNN conversion and deployment literature reviewed here, multi-compartment structure is used less for dendritic realism and more as an engineering workaround. A second compartment can hold the auxiliary state a single-compartment hardware primitive cannot express natively. Loihi's multi-compartment feature is used for three distinct purposes in the literature this survey covers, a soft-reset workaround, AHP-based adaptation, and a four-state adaptive sigma-delta neuron mapping that needs two compartments on Loihi 1 [nxtf2021] [boeshertz2024]. BrainScaleS-2's multi-compartment support is comparatively the most developed among the platforms surveyed, used for genuine dendritic computation (branch-dependent plateau potentials), not only as a single-primitive workaround [brainscales-pehle2022].

### Signed-spike neurons

Standard IF and LIF neurons emit only non-negative (unipolar) spikes, which cannot directly represent a negative activation. This matters because batch normalization and residual connections routinely produce substantial negative mass in pre-activation distributions; one source reports 51% of a YOLO detector's neuron outputs are negative [ijcai2025negspike]. Signed-neuron methods address this either by tracking a running net spike count and gating negative spikes so the effective rate never goes below zero (Signed Neuron with Memory) [wang2022signed], or by maintaining a shadow membrane potential and firing a compensating negative spike whenever it diverges from the true potential past a negative threshold [zou2023negspike]. Hardware support for a genuinely bipolar spike event, as opposed to a workaround, is confirmed only for Loihi 2, whose graded-spike payload carries a signed integer magnitude directly in the spike message [shrestha2023] [brehove2025]. Every other platform reviewed either lacks documented support or achieves the same effect through a paired excitatory and inhibitory channel, which doubles wiring or neuron cost, structurally analogous to the multi-compartment reset workaround above [pmc-loihi-backprop].

[FIGURE: neuron-model comparison across IF, LIF, CUBA LIF, ALIF, multi-compartment, and signed-spike variants, showing state variables and update equations side by side. Redraw of Figures/neuron_models.pdf, extended beyond the thesis chapter's IF/LIF/Hodgkin-Huxley/Izhikevich comparison to include the CUBA, ALIF, multi-compartment, and signed cases this survey needs.]

### Soft Reset Versus Hard Reset

Every neuron model above still requires a reset rule once it spikes, and this choice is treated in this survey as its own subject because the conversion literature's central correctness argument depends on it.

In a hard reset (reset-to-zero), the membrane potential is clamped to a fixed reset value, typically zero, immediately after a spike:
$$V(t) \leftarrow V_{\text{reset}}.$$
In a soft reset (reset-by-subtraction), only the threshold is subtracted, and any residual charge above threshold is carried forward into the next integration window:
$$V(t) \leftarrow V(t) - s(t)\, V_{th}.$$

Rueckauer et al. show analytically why this distinction is not cosmetic. Under hard reset, the residual charge above threshold at each spike event, $\epsilon = n \cdot z - V_{th}$, is discarded outright. This is not zero-mean noise that averages out over a longer simulation window; it is a systematic, input-dependent bias that compounds across layers in a deep network and does not vanish as $T \to \infty$ [rueckauer2017]. Under soft reset, that same excess charge is preserved and integrated in the following step, and the authors prove the resulting firing-rate estimator converges to the exact target ANN activation as $T \to \infty$, with only a bounded discretization error remaining, not a persistent bias [rueckauer2017]. This is the reason essentially the entire modern low-latency conversion literature assumes soft reset as a baseline, citing Rueckauer's derivation directly [rueckauer2017].

The empirical size of the effect is the number that matters for a deployment argument. Holding Poisson input and weight normalization fixed and changing only the reset rule, Rueckauer et al.'s CIFAR-10 ablation shows soft reset over hard reset is worth roughly twenty percentage points of accuracy [rueckauer2017]. This single ablation is the quantitative anchor for why reset semantics belongs in the execution-contract axis in 2.5 rather than as an implementation footnote. A platform whose native hardware reset is hard, and that cannot cheaply emulate soft reset, is not a neutral choice of deployment target for a rate-coded, IF-based converted network.

Native hardware support for soft reset is uneven. TrueNorth's digital neuron implements reset-by-subtraction as a first-class, natively configurable "linear mode" [truenorth-neuron]. DYNAP-CNN and Speck expose it through a `return_to_zero` configuration flag, with `False` selecting subtractive reset [speck-datasheet]. FPGA accelerator generators such as Spiker+ synthesize both hard and subtractive reset as selectable datapaths per neuron type [spiker-fpga]. Loihi's native single-compartment reset, by contrast, is hard reset to zero; the NxTF compiler recovers soft reset only by allocating a second compartment that absorbs the residual charge and inhibits the primary compartment back to the correct level, at the explicit cost of doubling compartment count, a cost the same paper flags as something future hardware with a built-in soft reset would eliminate [nxtf2021]. SpiNNaker's neuron model is software-programmable rather than hard-wired to either reset rule, so soft reset is achievable, but only by writing a custom neuron kernel in C rather than using one of sPyNNaker's built-in cell types [spinnaker-neuron-lab]. No source located in this research pass documents a soft-reset mode, native or via workaround, on BrainScaleS-2, whose analog AdEx circuit clamps the membrane to a reset potential for a fixed refractory period by construction [brainscales-pehle2022].

[FIGURE: membrane potential trace over several timesteps, drawn twice side by side, once under hard reset (potential clamped to a fixed value after each spike, residual charge visibly lost) and once under soft reset (threshold subtracted, residual charge visibly carried into the next step). Redraw and extension of Figures/LIFillustration.pdf to show both reset rules on the same input trace rather than only soft reset.]

## 2.3 Neural Codes

A neural code is the map between a represented quantity and a pattern of spikes. What follows treats each code by what it represents, how many spikes or timesteps it needs for a given precision, and what decoder is required to recover the represented value on the receiving end.

### Rate coding

The number of spikes a neuron emits over a window of $T$ timesteps represents a scalar value. Two variants matter in the conversion literature. Poisson rate coding draws spike times from a Poisson process whose rate is set by the represented value; deterministic count coding instead integrates a constant input current and emits a spike count that is a floor or round of the analog value [rueckauer2017]. Quantization error under deterministic count coding scales as $1/T$; under Poisson coding, variance instead scales as $1/\sqrt{T}$, so Poisson coding needs quadratically more timesteps for the same precision, which is why essentially all modern low-latency conversion work has abandoned Poisson input [auge2021]. The decoder is simply the output spike count divided by $T$, or, in several conversion frameworks, the accumulated pre-threshold membrane potential of the final layer read out directly without further spiking [jiang2023].

### Time-to-first-spike (TTFS) coding

Each neuron fires at most once; the timing of that spike, relative to a reference onset, encodes the value, typically with larger values producing earlier spikes. In principle a single spike's continuous-valued timing carries arbitrary precision, which is TTFS's appeal. On real hardware, firing times must be quantized to discrete timesteps, which reintroduces a quantization floor and, per one source, "inevitably downgrades performance" relative to the idealized continuous-time formulation [latency-framework2026]. The decoder is a winner-take-all over first-spike time, or a learned temporal-weighting decoder that favors early spikes [ettfs2024]. TTFS trains poorly relative to rate coding because the single-spike constraint concentrates all of a layer's information into precise spike timing rather than spike count, giving sparse gradients that must accumulate correctly across depth [yoso2020].

### Phase coding

Spikes are assigned a weight depending on their position (phase) within a repeating cycle of $K$ timesteps, typically powers of two: $2^{K-1}, 2^{K-2}, \ldots, 2^0$, analogous to binary place-value encoding [kim2018phase]. Because the phase weights are powers of two, the representable output values are sums over a subset of these weights, which makes phase coding a genuinely non-uniform, exponentially weighted quantization grid, in direct contrast to rate coding's uniform $1/T$-spaced grid. A single early-phase spike can therefore carry as much information as many unweighted spikes, at the cost of a latency that scales with the global cycle length; one follow-up reports phase coding alone needing on the order of three thousand simulation steps for a 32-layer network on CIFAR-100 [swsc2024].

### Burst coding

A neuron may emit multiple spikes within or between a single simulation timestep when residual membrane potential after a threshold crossing is large, instead of the usual one-spike-per-step ceiling. This packs several unweighted rate units of information into a single step, sitting as a middle ground between plain rate coding (at most one spike per step) and TTFS (at most one spike total) [li2022burst]. Burst coding requires a neuron capable of multi-spike emission within a timestep; Speck documents a distinct multi-spike neuron mode ("M-IF") for exactly this, though the cited deployment using this chip in fact used plain IF rather than the multi-spike variant [speck-natcomm].

### Population coding

A value is represented jointly by the activity pattern across a population of neurons rather than by any single neuron's rate or timing, for example through per-neuron tuning curves and an ensemble readout. Population coding is best understood as an orthogonal, spatial-multiplexing axis rather than a fourth encoding primitive alongside rate and temporal codes, since a population can itself be rate-coded or temporally coded internally [auge2021]. It is supported wherever a network can be instantiated with multiple neurons per logical unit, which is every platform reviewed in this survey, subject only to neuron-count budget.

### Sigma-delta coding

A sigma-delta neuron wraps a conventional activation with a delta encoder on output and a running-sum (sigma) decoder on input. A spike is transmitted only when the change in activation since the last transmission exceeds a threshold, and it carries that change as its payload rather than as a count of unit events [shrestha2023]. This exploits temporal redundancy (a static or slowly changing input produces few or no spikes) in addition to ordinary spatial sparsity. Loihi 2 supports graded spikes carrying up to 24 bits of signed integer magnitude directly in the spike message, which is the hardware feature that makes sigma-delta conversion practical on that chip. A single graded spike carries a quantized activation delta directly, rather than the delta being spread across many binary rate spikes [shrestha2023] [brehove2025]. A concrete ANN-to-sigma-delta-network conversion pipeline on Loihi 2 reports 112 FPS, 5.0 ms latency, and 20 mJ per frame in a fielded object-detection demo [brehove2025]. Loihi 1 lacks native graded spikes and approximates the mechanism through a two-compartment adaptive sigma-delta neuron mapping at double the compartment cost [boeshertz2024].

### Rank order coding

Rank order coding (ROC) was introduced to explain how the primate visual system performs complex recognition within roughly 150 ms, a budget too short for conventional rate coding, which needs at least two spikes per neuron to estimate an interspike interval [thorpe1996]. Each neuron in a population fires at most once, modeled as an analog-to-delay converter where more strongly activated neurons cross threshold sooner; the represented quantity is not a rate and not an absolute latency but purely the relative order in which the population's neurons fire during one feedforward wave triggered by a single stimulus. ROC is contrast-invariant by construction. Rescaling input intensity changes the absolute latencies but not their relative order, so the code is intrinsically robust to a class of nuisance transformations that would corrupt a literal TTFS code [cerco-spikenet]. The canonical decoder is a feedforward shunting-inhibition mechanism, where each arriving spike progressively desensitizes the postsynaptic neuron so that an afferent's contribution decays with its arrival rank; if synaptic weights are ranked to match an expected firing order, the postsynaptic neuron reaches maximal activation exactly when that order occurs [thorpe1996]. With $N$ neurons, ROC's channel capacity is $\log_2(N!)$ bits per population, obtained with roughly $N$ spikes total rather than the $O(N \log T)$ spikes a rate code needs over a $T$-step window, and requiring only a single feedforward wave rather than a full multi-timestep integration [thorpe1996]. The price is that ROC discards absolute amplitude information entirely; a survey of encoding schemes states plainly that ROC "is not possible to reconstruct the absolute signal amplitude" from [auge2021], and its ordinal code is fragile to timing jitter when spikes cluster closely, a failure mode a pure count-based code does not share [auge2021].

The measured hardware comparison that makes ROC's cost advantage concrete is MorphIC, a 65 nm quad-core digital neuromorphic processor. On the identical MNIST classification task, on the identical fabricated silicon, the authors directly measured 205 µJ per classification for rate coding (97.8% accuracy) against 21.8 µJ per classification for rank order coding, in which the inferred class is whichever output neuron spikes first (95.9% accuracy, a 1.9 percentage point drop) [frenkel2019]. This is a measured 9.4-fold energy reduction for a 1.9-point accuracy cost, on the same chip, which is as close to a controlled comparison between rate coding and rank order coding as exists in the hardware literature reviewed for this survey.

### Direct (constant-current) input encoding

Real-valued input, such as normalized pixel intensities, is applied as a constant analog current to the first hidden layer's neurons at every timestep instead of first being converted into a spike train; only the output of that first layer is spiking. Rueckauer et al. introduce this alongside soft reset and weight normalization as one of three mechanisms that close the ANN-SNN accuracy gap, reporting that switching the first layer from Poisson spike-train input to constant analog current alone improved CIFAR-10 accuracy from roughly 59.8% to 83.6% under otherwise fixed settings [rueckauer2017]. Because the first-layer computation becomes a genuine multiply-accumulate on real-valued input rather than an accumulate over binary spikes, this layer forfeits the accumulate-only efficiency the rest of the network enjoys; multiple sources note the overhead is negligible for the network as a whole because it applies to a single layer, but it means the very first layer of a "converted SNN" is, in an important architectural sense, not spiking at all [ace-snn2022].

[FIGURE: encoding comparison across rate/count, TTFS/latency, phase, burst, population, sigma-delta, rank order, and direct/analog coding, showing for each what the spike pattern represents and roughly how many spikes or timesteps a given precision costs. Redraw and substantial extension of Figures/coding.pdf, which in the thesis chapter shows only rate versus TTFS.]

## 2.4 Formalization

The correspondence at the center of the classical conversion literature is the following. A non-negative ReLU activation value in the source ANN is set equal to a firing rate, a spike count over $T$ timesteps (or an equivalent time-averaged membrane quantity), in the converted SNN [cao2015] [rueckauer2017]. Under reset-by-subtraction and constant or rate-matched input, the time-averaged firing rate of an IF neuron converges to the target ANN activation as $T \to \infty$, with the only remaining error a bounded discretization term rather than a persistent bias, which is exactly the soft-reset result established in 2.2 [rueckauer2017].

This correspondence has a consequence for quantization that the conversion literature inherits rather than chooses. With a fixed threshold $V_{th}$ and a fixed maximum firing rate $r_{max} = 1/\Delta t$, the achievable spike counts over a $T$-step window are $\{0, 1, \ldots, T\}$, which means the achievable firing-rate levels are equally spaced at $1/T$ intervals. A spike count over $T$ timesteps is, by construction, a uniform $T$-level quantizer of the activation it represents; there is no design choice that makes it otherwise, because the counting operation itself is what fixes the grid spacing. This is the direct mathematical link between rate/count coding and the thesis's independent claim that QCFS realizes standard uniform quantization-aware training: rate coding under reset-by-subtraction realizes exactly the same uniform staircase a $T$-level uniform quantizer would.

The consequence is that every conversion method built on the rate-matching correspondence is a uniform-grid method whether or not its authors describe it that way. The grid is a structural fact about counting spikes, not a hyperparameter selected during method design. This reframes what "low-latency conversion" methods that modify activation functions, neuron dynamics, or thresholds are actually doing. They operate within a uniform $T$-level grid whose existence follows from the counting mechanism itself, and their interventions are about placing that grid well (clipping, threshold calibration) or compensating for its coarseness at small $T$ (signed spikes, burst spikes), not about escaping it.

Rank order coding sits outside this formalization entirely, and the reason is structural rather than incidental. Every conversion proof built on the firing-rate correspondence, including Ding et al.'s Theorem 1, is stated and proved in terms of matching a per-layer firing rate, a magnitude, between the ANN and the SNN [ding2021]. This machinery is cardinal by construction, matching a count or magnitude on one side to a count or magnitude on the other. Rank order coding's entire content is ordinal, a single permutation of $N$ neurons rather than $N$ independently conveyed magnitudes, so there is no natural target for a rate-matching argument to converge toward. A ReLU layer's output is a vector of $N$ independent real numbers; a rank-order code over the same $N$ neurons discards everything except their relative order, one combinatorial object among $N!$ possibilities. No bijection or convergence argument analogous to "spike count converges to activation value" carries over to this setting, because there is no single scalar quantization level per neuron to be gridded, uniformly or otherwise. Consistent with this structural gap, no conversion method targeting rank order coding was located anywhere in the literature surveyed for this dossier [thorpe1996] [deneve2022] [ding2021]. The closest adjacent work, BrainChip's Akida toolchain, does convert trained ANNs onto ROC-decoding hardware, but it collapses the conversion to a single simulation timestep rather than implementing any genuine multi-layer rank-preserving proof, and no accuracy-preservation theorem for that pipeline was located [akida-roc].

## 2.5 Execution Contracts for Deployment

The axes below are what Section 6 later compares platforms against, and they are, the design of this survey holds, the material that determines whether an algorithm-level conversion result transfers to physical silicon at all. No prior survey isolates this subsection as its own axis of comparison.

### Time model

Three distinct time models appear across the platforms this survey covers, and they are not variations on a theme; they change what "the timestep $T$" means.

**Synchronous global tick.** The whole chip advances in lockstep on a shared timestep boundary, and every neuron's update for step $t$ is guaranteed complete before step $t{+}1$ begins. Loihi enforces this through an asynchronous blocking barrier handshake between cores, described in its own architecture paper as producing "fixed-size, synchronized time steps" that relate to algorithmic time and need not correspond to any fixed wall-clock duration; actual wall-clock time per step depends on spike traffic and network congestion [loihi-barrier]. SpiNNaker's default convention is a 1 ms timestep matched to biological real time, a software/API convention rather than a hardware limit, since sub-millisecond timesteps have been used at the cost of a proportionally slower real-time factor [spinnaker-1ms]. TrueNorth likewise introduces a fixed latency of one timestep $\Delta t$, given in one source as 1 ms, on event generation at every layer [richter2023speck]. Xylo, SynSense's audio and IMU inference line, is explicitly documented as a "synchronous time-stepped architecture with a global time-step `dt`," with a master clock running up to 50 MHz; the chip genuinely executes one network update per global tick, and up to 31 output spikes per neuron can be processed within a single tick [rockpool-xylo].

**Asynchronous event-driven.** There is no shared clock at all. Computation is triggered directly by the arrival of an event at a block's input, and each block calculates its output as soon as its input is available, independent of any other block's state. DYNAP-CNN and Speck, SynSense's vision line, state this directly, noting "the neuromorphic chip no longer needs the global or local clock signal," and asynchronous logic communicates via a request/acknowledge protocol "without requiring a global clock" [speck-natcomm]. Measured consequence: a single event traverses all nine convolutional layers of Speck in 3.36 µs, a hardware propagation delay that is not a multiple of any chosen simulation $\Delta t$, in explicit contrast to Loihi and TrueNorth, which the same source notes architecturally introduce a full timestep of latency per layer on event generation [richter2023speck].

**Analog continuous.** State evolves as continuous analog circuit dynamics rather than as discrete update steps at all, though the surrounding chip is still digitally orchestrated. BrainScaleS-2 runs its neuron circuits with time constants physically scaled by an acceleration factor, roughly 1,000x for BrainScaleS-2 and 10,000x for the wafer-scale BrainScaleS-1 system, relative to the biological time constants they represent; this is not a digital speedup but a physical circuit property, since capacitances and bias currents are chosen so the analog circuit literally evolves faster [brainscales-accel]. Even so, experiments are scheduled into fixed wall-clock "experiment frames" by a surrounding digital control layer (the PPU/FPGA), with an explicit input interval $\Delta t_{\text{input}}$ on the order of 100 to 500 ns in the non-spiking ANN mode. Continuous analog dynamics are sampled and triggered by digital control, not run in unstructured free time [brainscales-accel].

The sharpest illustration of why this distinction matters for a single vendor's own product line is the direct contrast between two SynSense chips. Speck has no global clock; a spike's propagation latency is a fixed hardware quantity, not a function of a chosen $T$. Xylo, from the same vendor, documents a global time step `dt` and genuinely advances state once per tick [speck-natcomm] [rockpool-xylo]. A software `num_timesteps` parameter set for a rate-coding simulation means something concrete and hardware-real on Xylo; the identical parameter passed to a Speck deployment pipeline exists only at the boundary where a discrete-time raster is converted into individually timestamped events, and has no meaning once those events reach the asynchronous compute fabric [speck-t-question].

[FIGURE: diagram of the three time models side by side, synchronous global tick (all cores advance on a shared boundary), asynchronous event-driven (blocks fire independently on event arrival, no shared clock), and analog continuous (physically accelerated continuous dynamics sampled by a digital control frame), using Loihi/SpiNNaker/Xylo, Speck/DYNAP-CNN, and BrainScaleS-2 respectively as the concrete instance of each. No direct predecessor among the existing thesis figures; this is a new diagram for the survey.]

### Spike payload

Spike payload is what a single spike event carries beyond its bare occurrence. Three regimes appear in the platforms surveyed. A binary payload carries only the fact that an event occurred, with no magnitude; this is the payload assumed by rate/count coding and by the classical IF correspondence, and it is what nearly every platform reviewed supports as its baseline. A signed binary payload adds a polarity bit, distinguishing an excitatory from an inhibitory event but still carrying no magnitude; TrueNorth's negative-threshold "bounce" behavior and Loihi 1's paired excitatory/inhibitory channel workaround both realize signed information this way, through two unsigned events rather than one bipolar event [truenorth-neuron] [pmc-loihi-backprop]. A graded integer payload carries a quantized magnitude directly in the spike message; Loihi 2 is the confirmed case, with graded spikes carrying up to 24 bits of signed integer magnitude and dedicated microcode support, which is the mechanism that makes sigma-delta conversion practical on that chip without spreading a delta across many binary rate spikes [shrestha2023].

### State and weight precision

Precision is set independently for neuron state and for synaptic weight, and the two do not move together. On Xylo, weights are 8-bit and neuron/synapse states are 16-bit [rockpool-xylo]. On Speck, weights and thresholds are quantized through the Sinabs toolchain to match the chip's fixed-point logic. On Loihi 2, the graded-spike payload width (up to 24 bits) sets an upper bound on activation precision distinct from the weight precision used elsewhere in the network. This state/weight precision split is a second, independent axis from the spike-payload question above: a platform can carry only binary spikes while still storing multi-bit synaptic weights, which is in fact the default arrangement on nearly every rate-coding platform reviewed.

### Delays

Two distinct notions of delay appear across the platforms and are easy to conflate. Synaptic or axonal delay is a configured per-connection property, present on some platforms (SpiNNaker's programmable per-synapse delay) and absent or fixed on others. Architectural per-layer latency is a consequence of the time model itself, not a configured parameter. On a synchronous platform, an event generated at layer $\ell$ cannot be consumed at layer $\ell{+}1$ until the next global tick, which architecturally introduces a full $\Delta t$ of latency at every layer boundary regardless of how the network is configured [richter2023speck]. On an asynchronous platform this architectural floor does not exist; latency is instead set by hardware propagation delay through the combinational logic of each block, measured on Speck at roughly 0.37 µs per layer [richter2023speck]. This is the same synchronous/asynchronous distinction driving the time-model discussion above, restated as a latency consequence rather than a definitional one, because it is the form in which the distinction shows up directly in a deployment latency budget.

---

## References for Section 2

| ID | Citation | Type |
|---|---|---|
| cao2015 | Cao, Y., Chen, Y., Khosla, D. "Spiking Deep Convolutional Neural Networks for Energy-Efficient Object Recognition." International Journal of Computer Vision 113(1), 2015. | Peer-reviewed |
| perez2013 | Pérez-Carrasco, J.A. et al. "Mapping from Frame-Driven to Frame-Free Event-Driven Vision Systems by Low-Rate Rate Coding and Coincidence Processing." IEEE TPAMI 35(11), 2013. | Peer-reviewed |
| maass1997 | Maass, W. "Networks of Spiking Neurons: The Third Generation of Neural Network Models." Neural Networks 10(9), 1997. | Peer-reviewed |
| hodgkin1952 | Hodgkin, A.L., Huxley, A.F. "A Quantitative Description of Membrane Current and Its Application to Conduction and Excitation in Nerve." Journal of Physiology 117(4), 1952. | Peer-reviewed |
| izhikevich2003 | Izhikevich, E.M. "Simple Model of Spiking Neurons." IEEE Transactions on Neural Networks 14(6), 2003. | Peer-reviewed |
| gerstner2002 | Gerstner, W., Kistler, W.M. Spiking Neuron Models: Single Neurons, Populations, Plasticity. Cambridge University Press, 2002. | Peer-reviewed (book) |
| bellec2018 | Bellec, G., Salaj, D., Subramoney, A., Legenstein, R., Maass, W. "Long Short-Term Memory and Learning-to-Learn in Networks of Spiking Neurons." NeurIPS 31, 2018. | Peer-reviewed |
| rueckauer2017 | Rueckauer, B., Lungu, I.-A., Hu, Y., Pfeiffer, M., Liu, S.-C. "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image Classification." Frontiers in Neuroscience, 2017. https://doi.org/10.3389/fnins.2017.00682 | Peer-reviewed |
| ding2021 | Ding, J., Yu, Z., Tian, Y., Huang, T. "Optimal ANN-SNN Conversion for Fast and Accurate Inference in Deep Spiking Neural Networks." IJCAI 2021. https://doi.org/10.24963/ijcai.2021/321 | Peer-reviewed |
| deneve2022 | Denève, S. et al. "Analyzing Time-to-First-Spike Coding Schemes: A Theoretical Approach." Frontiers in Neuroscience, 2022. https://doi.org/10.3389/fnins.2022.971937 | Peer-reviewed |
| thorpe1996 | Thorpe, S.J., Gautrais, J. "Rapid Visual Processing Using Spike Asynchrony." NeurIPS 1996. https://papers.neurips.cc/paper_files/paper/1996/file/fd5c905bcd8c3348ad1b35d7231ee2b1-Paper.pdf | Peer-reviewed |
| cerco-spikenet | CERCO/CNRS. "What Is Order Coding" (SpikeNet documentation). https://cerco.cnrs.fr/pagesp/arno/spikenet/order.html | Official documentation |
| furber2004 | Furber, S., Bainbridge, W.J., Cumpstey, J.M., Temple, S. "Sparse Distributed Memory Using N-of-M Codes." Neural Networks 17(10), 2004. | Peer-reviewed |
| frenkel2019 | Frenkel, C., Legat, J.-D., Bol, D. "MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning." IEEE TBioCAS 13(5), 2019. https://doi.org/10.1109/tbcas.2019.2928793 | Peer-reviewed |
| kim2018phase | Kim, J., Kim, H., Huh, S., Lee, J., Choi, K. "Deep Neural Networks with Weighted Spikes." Neurocomputing 311, 2018. https://doi.org/10.1016/j.neucom.2018.05.087 | Peer-reviewed |
| auge2021 | Auge, D. et al. "A Survey of Encoding Techniques for Signal Processing in Spiking Neural Networks." Neural Processing Letters, Springer. https://doi.org/10.1007/s11063-021-10562-2 | Peer-reviewed |
| guo2021 | Guo, W., Fouda, M.E., Eltawil, A.M., Salama, K. "Neural Coding in Spiking Neural Networks: A Comparative Study for Robust Neuromorphic Systems." Frontiers in Neuroscience, 2021. https://doi.org/10.3389/fnins.2021.638474 | Peer-reviewed |
| li2022burst | Li, Y., Zeng, Y. "Efficient and Accurate Conversion of Spiking Neural Network with Burst Spikes." IJCAI 2022. https://doi.org/10.24963/ijcai.2022/345 | Peer-reviewed |
| wang2022signed | Wang, Y., Zhang, M., Chen, Y., Qu, H. "Signed Neuron with Memory: Towards Simple, Accurate and High-Efficient ANN-SNN Conversion." IJCAI 2022. https://www.ijcai.org/proceedings/2022/0347.pdf | Peer-reviewed |
| zou2023negspike | Zou, C. et al. "Toward a Lossless Conversion for Spiking Neural Networks with Negative-Spike Dynamics." Advanced Intelligent Systems, 2023. https://doi.org/10.1002/aisy.202300383 | Peer-reviewed |
| ijcai2025negspike | Wang, X., Zhu, D., Li, J. "A Fast and Accurate ANN-SNN Conversion Algorithm with Negative Spikes." IJCAI 2025. https://www.ijcai.org/proceedings/2025/0719.pdf | Peer-reviewed |
| shrestha2023 | Shrestha, S.B., Timcheck, J., Frady, P., Campos-Macías, L., Davies, M. "Efficient Video and Audio Processing with Loihi 2." arXiv:2310.03251. | Preprint |
| brehove2025 | Brehove, M. et al. "Sigma-Delta Neural Network Conversion on Loihi 2." ICONS 2026 / arXiv:2505.06417. https://doi.org/10.1145/3822454.3822490 | Peer-reviewed / preprint |
| boeshertz2024 | Boeshertz, G., Indiveri, G., Nair, M.V., Renner, A. "Accurate Mapping of RNNs on Neuromorphic Hardware with Adaptive Spiking Neurons." arXiv:2407.13534. | Preprint |
| nxtf2021 | Kastellakis, G. et al. "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi." arXiv:2101.04261. | Preprint (toolchain documentation) |
| pmc-loihi-backprop | "The Backpropagation Algorithm Implemented on Spiking Neuromorphic Hardware." PMC11549378. | Peer-reviewed |
| truenorth-neuron | "Cognitive Computing Building Block: A Versatile and Efficient Digital Neuron Model for Neurosynaptic Cores." viplab.fudan.edu.cn. | Technical report / documentation |
| spiker-fpga | "Spiker+: A Framework for the Generation of Efficient Spiking Neural Networks FPGA Accelerators for Inference at the Edge." arXiv:2401.01141. | Preprint |
| spinnaker-neuron-lab | SpiNNaker "Creating New Neuron Models" lab manual. spinnakermanchester.github.io. | Official documentation |
| spinnaker-1ms | SpiNNaker documentation / Furber et al. 2012 IEEE Transactions on Computers; SpiNNaker datasheet v2.02. | Official documentation / peer-reviewed |
| loihi-barrier | Loihi architecture paper (barrier synchronization, algorithmic time step), as characterized in this survey's platform research pass. | Peer-reviewed (characterized via research pass) |
| lava-dl | Lava-DL SLAYER documentation. https://lava-nc.org/lava-lib-dl/slayer/slayer.html | Official documentation |
| brainscales-pehle2022 | Pehle, C. et al. "The BrainScaleS-2 Accelerated Neuromorphic System with Hybrid Plasticity." Frontiers in Neuroscience, 2022. https://doi.org/10.3389/fnins.2022.795876 | Peer-reviewed |
| brainscales-accel | Schemmel, J. et al. "Accelerated Analog Neuromorphic Computing." arXiv:2003.11996. | Preprint |
| speck-natcomm | Yao, M., Richter, O. et al. "Spike-Based Dynamic Computing with Asynchronous Sensing-Computing Neuromorphic Chip." Nature Communications 15:4464, 2024. https://doi.org/10.1038/s41467-024-47811-6 | Peer-reviewed |
| speck-2019 | SynSense. "DYNAP-CNN — The World's First 1M Neuron, Event-Driven Neuromorphic AI Processor." 2019. https://www.synsense.ai/dynap-cnn-the-worlds-first-1m-neuron-event-driven-neuromorphic-ai-processor-for-vision-processing/ | Vendor material |
| speck-datasheet | SynSense. Speck Dev Kit Manual / Datasheet, 2023-2025 revisions. | Vendor material |
| richter2023speck | Richter, O. et al. "Speck: A Smart Event-Based Vision Sensor with a Low Latency 327K Neuron Convolutional Neural Network Processing Pipeline." arXiv:2304.06793. | Preprint |
| rockpool-xylo | Rockpool documentation, "Overview of the Xylo Family." https://rockpool.ai/devices/xylo-overview.html; XyloAudio datasheets. | Official documentation / vendor material |
| sinabs-docs | Sinabs API and documentation. https://sinabs.readthedocs.io/ | Official documentation |
| speck-t-question | Synthesis of Sinabs `num_timesteps` documentation against Speck/Richter et al. hardware characterization, as compiled in this survey's platform research pass. | Official documentation + preprint, cross-read |
| ettfs2024 | "Efficiently Training Time-to-First-Spike Spiking Neural Networks from Scratch." arXiv:2410.23619. | Preprint |
| yoso2020 | "You Only Spike Once: Improving Energy-Efficient Deep SNN with Temporal Coding." arXiv:2006.09982. | Preprint |
| latency-framework2026 | "A Latency Coding Framework for Deep Spiking Neural Networks with Ultra-Low Latency." arXiv:2603.23206. | Preprint |
| swsc2024 | "Stepwise Weighted Spike Coding for Deep Spiking Neural Networks." arXiv:2408.17245. | Preprint |
| jiang2023 | Jiang, H., Anumasa, S., De Masi, G., Xiong, H., Gu, B. "A Unified Optimization Framework of ANN-SNN Conversion." ICML 2023. https://proceedings.mlr.press/v202/jiang23a/jiang23a.pdf | Peer-reviewed |
| ace-snn2022 | "ACE-SNN: Algorithm-Hardware Co-Design of Energy-Efficient and Low-Latency Deep Spiking Neural Networks for 3D Image Recognition." Frontiers in Neuroscience, 2022. https://doi.org/10.3389/fnins.2022.815258 | Peer-reviewed |
| akida-roc | Lunghi, P., Silvestrini, S., Dold, D., Meoni, G., Hadjiivanov, A., Izzo, D. "Energy Efficiency Analysis of Spiking Neural Networks for Space Applications." arXiv:2505.11418; BrainChip "What Is the Akida" technical brief; Open Neuromorphic, "A Look at Akida." | Preprint + vendor material + community commentary |

All entries above are drawn from `NeuromorphicSurvey/research/raw/a13-encodings-neurons.md` and `NeuromorphicSurvey/research/raw/a03-synsense.md` (both compiled research passes with full source lists), cross-checked for foundational neuron-model citations against the author's own thesis bibliography (`00-Vault/04-Writing/Thesis/references.bib`). Rows without a direct DOI/arXiv identifier here are traceable in full in those two files.


---

# 3 Primary Training Paths

Two routes produce a trained SNN. Direct training back-propagates through the spiking
nonlinearity, usually with a surrogate gradient standing in for the non-differentiable spike
function. ANN-to-SNN conversion trains a conventional ReLU network with ordinary backpropagation
and re-expresses each ReLU as an integrate-and-fire (IF) neuron whose spike count over `T`
timesteps approximates the original activation. The two paths are audited separately below because
they reach hardware through different toolchains, and the audit finds that the toolchain, not the
training method itself, is what actually predicts whether a paper's numbers ever leave a GPU.

## 3.1 Direct Training

The headline surrogate-gradient lineage that runs through the SpikingJelly framework, SEW-ResNet,
tdBN, TET, the Spikformer family, Spikingformer, and the Spike-driven Transformer, has zero
confirmed physical-chip runs across every paper checked for this audit [fang-2021-sew],
[zheng-2021-tdbn], [fang-2021-plif], [deng-2022-tet], [zhou-2023-spikformer],
[zhou-2024-spikformerv2], [zhou-2023-spikingformer], [yao-spikedriven]. Every energy figure these
papers report is a theoretical synaptic-operation count multiplied by a 45 nm MAC or accumulate
energy constant, never a measurement taken from a chip's power rail. Spikingformer's own
related-work section states the point against its immediate predecessors directly. It argues that
SEW-ResNet's and Spikformer's residual connections retain non-spike, integer-float arithmetic at
the shortcut, which the paper calls unsuitable for deployment on mainstream neuromorphic hardware,
and redesigns the residual path specifically to remove that arithmetic [zhou-2023-spikingformer].
The admission is notable because it comes from inside the lineage itself, not from an external
critic. tdBN's own paper makes a symmetric move in the other direction. It frames batch-norm
folding as something that would enable efficient neuromorphic-hardware inference, but the paper
stops at that framing and reports no chip run of its own [zheng-2021-tdbn]. Xpikeformer, a hybrid
analog-digital accelerator built for spiking transformers, gets no closer than a NeuroSim circuit
simulation combined with an FPGA prototype of a single attention tile, which is a hardware model of
a sub-block, not a fabricated full-network chip [song-2024-xpikeformer].

Direct training does reach silicon, but only where two conditions hold together, an event-native
workload and a training-to-deployment pipeline built by the chip vendor itself. Intel's SLAYER,
Lava-DL, and NxTF chain is the clearest instance. SLAYER was published as an offline training
system explicitly meant to precede a chip deployment, not as a deployment result on its own
[shrestha-2018-slayer], and Intel's own tutorial scripts close that loop, training a
convolutional SNN with SLAYER and deploying it to a physical Loihi 1 board with built-in latency
and energy probes for DVS Gesture [intel-nxtf-slayer-gestures]. Mészáros, Knight, Timcheck, and
Nowotny extend the same pipeline through mlGeNN and NetX to Loihi 2, reporting feedforward latency
of 1.46 ms with learned synaptic delays and 0.46 mJ dynamic energy per inference on keyword-spotting
benchmarks, eighteen times faster and 250 times lower energy than a Jetson Orin Nano baseline at
batch size one [meszaros-2025-loihi2-delays]. A co-designed continual-learning rule trained and
adapted directly on Loihi 2 measures 0.33 ms latency and 0.05 mJ dynamic energy per inference, more
than a hundred times faster and thousands of times lower energy than the same Jetson baseline
[clpsnn-2025]. EXODUS, an exact-gradient descendant of SLAYER, is the exception inside this
lineage that proves the rule. It is a training-speed contribution benchmarked only against
un-optimized backpropagation on a GPU, and no experiment in the paper itself runs on a chip; its
deployment story exists only through downstream Sinabs users [bauer-2023-exodus].

SynSense's Speck and Xylo product lines show the same pattern on a second vendor stack. The Speck1
paper runs the only same-chip, head-to-head comparison found between direct backpropagation
training and ANN-to-SNN conversion, both measured on physical silicon. Direct BPTT training reaches
98.50% on-chip N-MNIST accuracy at 180 microjoules per inference, against a converted baseline on
the same chip at 141 microjoules, and both are compared directly to Loihi 1 numbers taken from
SLAYER (620 microjoules) and from the SNN Toolbox pipeline (290 microjoules) [richter-2023-speck1].
A later Nature Communications paper on the same Speck architecture measures real-time power as low
as 0.70 mW and per-input latency of 3.36 microseconds on gesture and gait recognition tasks
[yao-2024-speck-naturecomm]. Xylo, SynSense's audio chip, is trained directly through the Rockpool
toolchain and measured at 291 microwatts of dynamic power and 6.6 microjoules of dynamic energy per
inference on a keyword-spotting benchmark, beating Loihi and SpiNNaker2 on the identical benchmark
table [bos-2024-xylo].

SpikingJelly's own reach into hardware is narrow relative to how widely the framework is cited.
Its Science Advances paper demonstrates a `lava_exchange` path that trains a convolutional SNN on
DVS Gesture and deploys it to a physical Loihi chip, but this is presented as a capability
demonstration with no separate latency or energy table for the chip run, distinct from the GPU
baseline [fang-2023-spikingjelly-sciadv]. Two independent third-party papers close that gap. A
2026 preprint trains object-detection SNNs with SpikingJelly, exports them through a Lava-DL
compatible path, and reports inference rate, dynamic energy, total power, and energy-delay product
measured on physical Loihi 2, benchmarked against a Jetson Orin Nano, a Jetson Nano B01, and an
Apple M2 [objdet-2026-loihi2-preprint]. A separate group trains DVS128 Gesture networks with
SpikingJelly and runs them on the CRI FPGA-based neuromorphic platform built at UC San Diego,
recording accuracy alongside hardware performance counters such as clock cycles and HBM accesses
[hiaer-cri-docs]. A live GitHub issue against the SpikingJelly repository documents users hitting
Loihi's axon-count ceiling when attempting this export in practice, which confirms the path is used
but is non-trivial and architecture-constrained [spikingjelly-issue543]. Weighed against the
number of published works that build on SpikingJelly, these are a small handful of exceptions, not
a routine outcome.

A distinct, larger, and equally rigorously measured body of Loihi application work reaches hardware
without gradient-based training at all. Olfactory circuit recognition [imam-2020-olfaction],
head-direction SLAM [tang-2019-slam], iCub head-pose estimation [kreiser-2020-icub], sparse coding
by the Locally Competitive Algorithm [davies-2018-loihi], [tang-2017-lca-theory],
[parpart-2023-lca-loihi2], [convlca-2025-2026], and Boolean satisfiability solving
[satcsp-2020] are all hand-designed spiking circuits with local, biologically derived plasticity
rules, not surrogate-gradient trained networks, and every one reaches E1. Two robotics-control
papers, a mapless-navigation policy [sddpg-2020] and an industrial force-control policy
[forcecontrol-2024], are gradient-trained end to end and also reach Loihi with full energy and
latency measurement, which keeps the gradient-trained category from being empty, but the largest
E1 cluster in the Loihi ecosystem belongs to hand-designed circuits, not to the surrogate-gradient
paradigm that SpikingJelly's headline architectures represent. Conflating "directly trained" with
"not converted from an ANN" overstates how much of the Loihi hardware evidence base traces back to
BPTT-style training specifically.

## 3.2 Classical ANN-to-SNN Conversion

Classical conversion rests on three mechanisms formalized across this lineage, weight and
threshold balancing so a fixed-point IF neuron's maximum firing rate matches the source ReLU's
dynamic range [diehl-2015], reset by subtraction in place of reset to zero, which carries residual
membrane charge forward instead of discarding it at every spike, closing a systematic bias that
reset-to-zero introduces and that does not vanish with more simulation time
[rueckauer-2017], and direct analog current injected into the first layer in place of
Poisson-coded input, which alone cut CIFAR-10 error from 40.18% to 16.40% in one controlled
ablation when substituted for Poisson coding under otherwise fixed conditions [rueckauer-2017].

Nine papers propose a classical conversion algorithm by this audit's count, spanning Cao, Chen, and
Khosla's original spiking CNN mapping [cao-2015], Diehl et al.'s weight and threshold balancing
[diehl-2015], the SNN Toolbox paper that formalizes reset by subtraction [rueckauer-2017],
SPIKE-NORM [sengupta-2019-spikenorm], RMP-SNN [han-2020-rmpsnn], temporal-switch coding
[han-2020-tsc], optimal threshold-shift conversion [deng-2021-optconv], SNN calibration
[li-2021-calibration], and trainable clipping layers [ho-2021-tcl]. Zero of the nine report
physical hardware execution. All nine are E5. This is not a matter of the papers being silent about
hardware. Several report an analytical, synaptic-operation-count energy or complexity estimate in
language that reads as a hardware result on a first pass. Cao et al. call their estimate a
"hardware mapping analysis" of a hypothetical DARPA SyNAPSE-style chip, with no chip or simulator
named [cao-2015]. Sengupta et al.'s abstract closes by claiming to demonstrate "reduced hardware
overhead," a claim resting entirely on spike-sparsity operation counts, not a measurement
[sengupta-2019-spikenorm]. Li et al.'s calibration paper computes energy from a published
per-operation constant, 0.9 picojoules per addition and 4.6 picojoules per multiplication, and the
paper's own text flags this as an estimate rather than a chip measurement [li-2021-calibration].
Ho and Chang report results in units the paper calls "cycles," which a reader could mistake for
hardware clock cycles, but the paper's own implementation is PyTorch simulation throughout, and no
clock frequency or chip is named anywhere in the text [ho-2021-tcl]. None of these five estimates
crosses into E4, because none synthesizes RTL or runs a cycle-accurate simulator against a named
technology node. They remain E5, an analytical estimate, with the estimate's status made explicit
here because downstream literature has, in places, cited them as though they were measurements.

Physical hardware validation of classical conversion exists, but it lives in a separate population
of systems and compiler papers that adopt someone else's conversion pipeline as an input, never in
the papers that introduce the conversion technique itself. Massa, Marchisio, Martina, and Shafique
take the SNN Toolbox pipeline and deploy it through NxSDK to a physical Loihi chip, measuring
89.64% accuracy and 11.43 milliseconds per-frame latency on DVS Gesture [massa-2020-loihi-dvs].
Rueckauer, Bybee, Goettsche, Singh, Mishra, and Wild build NxTF, a compiler that takes the same
SNN Toolbox front end onto up to sixteen physical Loihi chips, and measure error rate, energy per
sample, and delay per sample directly against CPU and GPU baselines, reaching 8.52% error on
CIFAR-10, the lowest reported on neuromorphic hardware for that dataset at the time
[rueckauer-2021-nxtf]. Kelber et al. benchmark the same class of pre-trained-to-spiking conversion
across BrainScaleS, Spikey, and SpiNNaker with a real power meter on the digital platforms,
though the BrainScaleS energy figure in that same paper is itself an estimate drawn from prior
published per-event data rather than a measurement taken in that study, which the paper's own text
flags [kelber-2020-benchmark]. Stromatias et al. realize a conventionally trained Deep Belief
Network as a spiking network on SpiNNaker, measuring 95% MNIST accuracy and sub-0.3-watt power
draw on a single chip, and predates the CNN-specific IF pipeline that Diehl and Rueckauer later
formalize [stromatias-2015-spinnaker]. Esser et al.'s TrueNorth paper is frequently cited alongside
this group as a conversion success story, but on inspection its method is direct, hardware-
constrained backpropagation with binary neurons and trinary synapses trained from the outset to
map onto TrueNorth, not weight-transplant conversion from a pre-trained ReLU network, and its E1
status should not be read as evidence that classical conversion specifically reached hardware
[esser-2016-eedn].

No classical conversion of a full VGG-16 or ResNet-34 trained the way Sengupta, Han, or Deng and
Gu train it has been demonstrated on physical neuromorphic silicon in any paper found in this
audit. The CIFAR-10 result on Loihi uses MobileNet, not VGG-16 or ResNet, and no ImageNet-scale
conversion has been shown on physical hardware in any paper surveyed here [rueckauer-2021-nxtf].
Combining both populations, five of fourteen papers audited reach E1, but restricted to the nine
papers that actually propose a classical conversion algorithm, the figure is a clean zero. Hardware
validation of classical ANN-to-SNN conversion as a technique happens exclusively in later,
systems-oriented papers that adopt someone else's pipeline, never in the paper that introduces the
technique.

## Table 1. Primary training paths, evidence summary

| # | Subsection | Method | Neuron / reset | Encoding | T | Datasets | Target hardware | What was measured | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.1 | SEW-ResNet [fang-2021-sew] | IF/PLIF, hard reset | direct frame input | 4-16 | ImageNet, DVS Gesture, CIFAR10-DVS | none | GPU accuracy only; theoretical energy | E5 |
| 2 | 3.1 | tdBN / STBP-tdBN [zheng-2021-tdbn] | LIF | direct frame input | 2-6 | CIFAR-10/100, ImageNet, DVS-CIFAR10 | none (design argument only) | GPU accuracy only | E5 |
| 3 | 3.1 | Spikformer / V2 [zhou-2023-spikformer], [zhou-2024-spikformerv2] | LIF, spike Q/K/V | direct frame input | 4-16 | ImageNet, CIFAR, DVS128 Gesture | none | GPU accuracy; theoretical 45 nm SOP energy | E5 |
| 4 | 3.1 | Spikingformer [zhou-2023-spikingformer] | LIF, MS-residual | direct frame input | 4 | 13 datasets incl. ImageNet | none | GPU accuracy; theoretical energy; explicit non-deployability claim about predecessor residuals | E5 |
| 5 | 3.1 | Xpikeformer [song-2024-xpikeformer] | LIF | direct frame input | n/a | ImageNet-1K | NeuroSim model + FPGA attention tile | Circuit simulation, FPGA sub-block prototype | E4 |
| 6 | 3.1 | SLAYER-NxTF gesture demo [shrestha-2018-slayer], [intel-nxtf-slayer-gestures] | CUBA-LIF | DVS event stream | 24-1024 bins | DVS Gesture | Loihi 1 (physical) | Latency, energy (on-chip probes) | E1 |
| 7 | 3.1 | mlGeNN synaptic delays [meszaros-2025-loihi2-delays] | LIF, exp. synapse + delay | event stream | up to 62 delay steps | SHD, SSC | Loihi 2 (physical) | Latency, dynamic energy, EDP vs. Jetson Orin Nano | E1 |
| 8 | 3.1 | CLP-SNN continual learning [clpsnn-2025] | spiking state machine | event stream | n/a | OpenLORIS | Loihi 2 (physical, INT8) | Latency, energy, EDP vs. Jetson Orin Nano | E1 |
| 9 | 3.1 | EXODUS [bauer-2023-exodus] | IAF/LIF/ExpLeak | event stream | task-dependent | DVS Gesture, SHD, SSC | none (training-speed contribution) | GPU training-time benchmark only | E5 |
| 10 | 3.1 | Speck1 BPTT vs. conversion [richter-2023-speck1] | IF | direct/event | 300 ms window | N-MNIST | Speck1 (physical) | On-chip accuracy, energy/inference, same-chip BPTT-vs-conversion comparison | E1 |
| 11 | 3.1 | Speck dynamic SNN [yao-2024-speck-naturecomm] | IF | event stream | task-dependent | DVS128 Gesture/Gait, HAR-DVS | Speck (physical) | Real-time power, idle power, per-input latency | E1 |
| 12 | 3.1 | Xylo audio KWS [bos-2024-xylo] | LIF, quantized | audio | n/a | Aloha KWS | Xylo Audio 2 (physical) | Accuracy, dynamic power, energy/inference vs. Loihi/SpiNNaker2/GPU | E1 |
| 13 | 3.1 | SpikingJelly object detector [objdet-2026-loihi2-preprint] | SpikingJelly-trained | direct/event | not stated | frame + event detection | Loihi 2 (physical) | Inference rate, dynamic energy, power, EDP vs. edge devices | E1 |
| 14 | 3.1 | SpikingJelly-CRI gesture [hiaer-cri-docs] | SpikingJelly-trained SCNN | event stream | 10 frames + 6 drain | DVS128 Gesture | CRI FPGA hardware | Accuracy, clock cycles, HBM accesses | E1/E2 |
| 15 | 3.1 | Hand-designed Loihi olfaction [imam-2020-olfaction] | biologically derived, local plasticity | event stream | 200 | chemosensor wind-tunnel data | Loihi (physical) | Latency, total/dynamic energy per sniff | E1 |
| 16 | 3.2 | Cao, Chen, Khosla [cao-2015] | IF, rank-order/spike-count | pixel-proportional spikes | not fixed | Neovision2, CIFAR-10 | none | "hardware mapping analysis" (analytical only) | E5 |
| 17 | 3.2 | Diehl et al. [diehl-2015] | IF, reset-to-zero | Poisson | ~20 ms window | MNIST | none | MATLAB IF simulator only | E5 |
| 18 | 3.2 | Rueckauer et al., SNN Toolbox [rueckauer-2017] | IF, reset-by-subtraction (introduced here) | Poisson and direct/analog compared | varies | MNIST, CIFAR-10, ImageNet | none (own paper) | Software simulator only | E5 |
| 19 | 3.2 | SPIKE-NORM [sengupta-2019-spikenorm] | IF, hard reset | Poisson (normalization only) | 2500 | CIFAR-10, ImageNet | none | GPU accuracy; SynOps-style overhead claim | E5 |
| 20 | 3.2 | RMP-SNN [han-2020-rmpsnn] | IF, soft reset | rate/analog | 64-2048 | CIFAR-10/100, ImageNet | none | GPU accuracy only | E5 |
| 21 | 3.2 | TSC [han-2020-tsc] | soft-reset, dual-spike | temporal-switch coding | latency ratio, not fixed T | CIFAR-10/100, ImageNet | none | GPU accuracy; analytical op-count claim | E5 |
| 22 | 3.2 | Opt-conv threshold shift [deng-2021-optconv] | IF, soft reset | direct/analog | 16-256 | CIFAR-10/100, ImageNet | none | GPU simulation only | E5 |
| 23 | 3.2 | SNN Calibration [li-2021-calibration] | IF | direct/analog (explicitly non-spiking input by design) | up to 256 | CIFAR-10/100, ImageNet | none | GPU only; explicit SynOps energy estimate (0.9/4.6 pJ) | E5 |
| 24 | 3.2 | TCL [ho-2021-tcl] | IF | direct/analog | 20-350 "cycles" (simulated, not hardware) | CIFAR-10, ImageNet | none | PyTorch simulation only | E5 |
| 25 | 3.2 | Eedn / TrueNorth [esser-2016-eedn] | binary neuron, trinary synapse (not classical IF conversion) | hardware-constrained training | n/a | 8 vision/speech datasets | TrueNorth NS1e/NS1t (physical) | Accuracy, throughput, power | E1 (direct-trained, not conversion) |
| 26 | 3.2 | DBN on SpiNNaker [stromatias-2015-spinnaker] | spiking DBN realization | rate | n/a | MNIST | SpiNNaker (physical) | Accuracy, latency, power | E1 |
| 27 | 3.2 | SNN Toolbox on Loihi, DVS Gesture [massa-2020-loihi-dvs] | IF (SNN Toolbox pipeline) | rate | n/a | DVS Gesture, MNIST, CIFAR-10 | Loihi (physical) | Accuracy, per-frame latency | E1 |
| 28 | 3.2 | NxTF [rueckauer-2021-nxtf] | IF (SNN Toolbox pipeline) | rate | n/a | N-MNIST, MNIST, CIFAR-10, DVS Gestures | Loihi, up to 16 chips (physical) | Error, energy/sample, delay/sample | E1 |
| 29 | 3.2 | Benchmarking on BrainScaleS/Spikey/SpiNNaker [kelber-2020-benchmark] | pre-trained-to-spiking | rate | n/a | five networks | BrainScaleS, Spikey, SpiNNaker (physical) | Accuracy, power-meter energy (digital); BrainScaleS energy estimated, not measured | E1 (digital) / E5 (BrainScaleS energy) |

---

# 4 Advanced Conversion Techniques

## 4.1 Low-Latency Conversion

The low-`T` literature splits into three levels of intervention. Activation-level methods change
the clipping and rounding function applied to the ANN's activation before conversion, exemplified
by the clip-floor-shift function QCFS introduces and by its channel-wise successor
[bu-2022-qcfs], [yang-2024-csqcfs]. Neuron-model-level methods keep the ANN training convention
close to standard and instead change what the IF neuron itself does at inference time, illustrated
by optimized non-zero initial membrane potential [bu-2022-opi], residual membrane-potential readout
[hao-2023-srp], burst-firing neurons that emit more than one spike per step to pack more
information into fewer timesteps [li-2022-burstspikes], signed neurons that permit a compensating
negative spike [wang-2022-snm], and signed IF neurons built specifically around a quantized ANN
[hu-2023-fastsnn]. Encoding and inference-level methods leave both the activation function and the
neuron largely alone and instead change how much of the simulation window actually needs to run,
either by proving a one-step conversion is sufficient [jiang-2023-sliprelu] or by deciding, per
input sample, when to stop simulating early.

Two early-exit methods belong to this third group and deserve an explicit distinction from the
per-layer mixed-timestep methods discussed in Section 4.3. SEENN uses a confidence threshold or a
reinforcement-learned policy to decide when a whole network has integrated enough evidence for a
given input, reaching an average of 1.08 timesteps on CIFAR-10 while keeping every layer
synchronized to the same running timestep count [li-2023-seenn]. Dynamic Confidence does the same
with a Pareto-calibrated confidence threshold, reaching 2.52 average timesteps on CIFAR-10 with a
negative-spike backbone [li-2023-dynconf]. Both decide a single global `T` per input sample, not a
different `T` per layer within one inference, so neither inherits the pipeline-stalling problem
that a genuinely heterogeneous per-layer timestep assignment creates on barrier-synchronized
hardware. A pipelined multi-core accelerator can in principle run an early-exit network by cutting
the same uniform per-layer `T` short in time once confidence is reached, without any layer waiting
on another layer for a different number of ticks. Keeping this distinction explicit matters because
the two families are frequently discussed together in surveys and are architecturally unrelated.

Across sixteen QCFS-lineage and adjacent low-`T` papers audited, zero report physical hardware
execution [bu-2022-qcfs], [bu-2022-opi], [hao-2023-srp], [hao-2023-cos], [jiang-2023-sliprelu],
[li-2022-burstspikes], [wang-2022-snm], [hu-2023-fastsnn], [li-2023-dynconf], [li-2022-qffs],
[li-2023-seenn], [yang-2024-csqcfs], [wang-2025-adafire], [ramesh-2025-pascal],
[manjunath-2025-neuroflex], [liu-2022-spikeconverter]. Fifteen of the sixteen are E5, software
simulation including SynOps-style theoretical energy tables, and one, NeuroFlex, is E4, RTL
synthesized and cycle-simulated but never fabricated [manjunath-2025-neuroflex]. Every paper in
this group that names a target chip does so as design justification inside an introduction or a
conclusion, never as an executed run. Fast-SNN cites Loihi's support for signed spikes to justify
its own signed-IF neuron [hu-2023-fastsnn]; the burst-firing literature cites Loihi 2 and
SynSense's Speck and Xylo to justify a burst-firing neuron choice [wang-2025-adafire]; none of
these citations is accompanied by a deployment on the named chip. Direct or analog first-layer
encoding, real-valued pixel intensity injected as constant current rather than Poisson-coded, is
the near-universal convention across this entire lineage, not an exception, inherited directly from
the SNN Toolbox paper [rueckauer-2017].

## 4.2 Quantization- and Distribution-Aware Conversion

QCFS's clip-floor-shift activation is the pivot of this lineage and the direct object of the
thesis's own contribution. A spike count accumulated over `T` timesteps under reset-by-subtraction
is, by construction, a uniform `T`-level quantization grid, because a fixed threshold produces
equally spaced achievable firing-rate levels at `1/T` intervals [rueckauer-2017]. QCFS trains the
ANN side of the conversion with an explicit clip-floor-shift nonlinearity that anticipates exactly
this grid, reaching 93.96% CIFAR-10 accuracy at `T=4` [bu-2022-qcfs]. CS-QCFS extends the same
activation to a per-channel softplus form, reaching a `T=1` headline of 95.86% on CIFAR-10 and
74.83% on CIFAR-100 [yang-2024-csqcfs]. QFFS makes the quantization framing explicit rather than
implicit, training the ANN with an LSQ-style quantization-aware quantizer before conversion and
stating directly that its input is analog-coded following the Rueckauer convention, reaching 93.14%
on CIFAR-10 at `T=4` [li-2022-qffs]. SlipReLU generalizes the activation to a weighted-ReLU-plus-
step-function form and reports the first claimed one-step, `T=1`, conversion at 93.11% on
CIFAR-10, framing the whole family explicitly as a single optimization problem over the
quantization parameters shared by the ANN and SNN sides of the conversion [jiang-2023-sliprelu].

This quantization framing is also the seam into per-layer mixed-timestep work. QAC's Theorem 1
proves, for soft-reset IF neurons, that the SNN timestep count `T` and the quantization level `2^n`
of a matched-precision quantized ANN activation are mathematically equivalent, which is the same
correspondence a13's uniform-grid argument establishes from the neuron-dynamics side rather than
the quantization-theory side [rueckauer-2017]. Section 4.3 takes up what happens when that
equivalence is applied per layer rather than globally.

## 4.3 Mixed-Timestep and Per-Layer Allocation

Three papers assign a different quantization level, and therefore a different unrolled timestep
count, to each layer of a network, then report a single scalar `T_eff` as the headline efficiency
number. In every case that number is a mean over layers, not a measured latency, and in every case
the paper's own hardware evidence, where any exists, covers a narrower claim than the mixed-
timestep headline itself.

PASCAL reports `T_eff` of 3.14 for ResNet-18 on CIFAR-10 at 95.34% accuracy, and other
configurations from 2.13 to 12.94 depending on architecture and dataset, computed as a per-layer
weighted arithmetic mean, explicitly normalized by the inverse of the total layer count
[ramesh-2025-pascal]. The paper's Appendix A.10 does report physical hardware validation. It
synthesizes RTL for a modified LoAS accelerator and a modified SparTen accelerator with the
Synopsys Design Compiler on 40 nm CMOS, determines an operating frequency of 560 MHz, and builds a
cycle-accurate simulator of both accelerators [ramesh-2025-pascal]. That validation, however,
covers only a single design point, a uniform `T=4` PASC-IF neuron running VGG-16 on CIFAR-10, and
checks only that the PASC-IF neuron itself adds negligible energy and latency overhead relative to
a standard IF neuron under one shared timestep count for every layer. The paper never synthesizes,
simulates, or measures the Adaptive Layerwise mode that actually produces the `T_eff=3.14` headline
result; that number rests entirely on the software and PyTorch simulation used to produce the
paper's own accuracy tables. This split matters enough that the same paper occupies two evidence
classes at once, E4 for the uniform-`T` PASC-IF neuron-overhead claim, E5 for the mixed-timestep
`T_eff` claim.

QAC proves the timestep-quantization equivalence noted in Section 4.2, trains a mixed-precision
ANN with a per-layer bit-width, and converts it into an SNN with per-layer timesteps, adding a
temporal-alignment step to reconcile the differing temporal dimensions between adjacent layers
[guo-2025-qac]. Its headline is 95.29% top-1 accuracy on ResNet-18/CIFAR-10 at an average of 2.76
timesteps, again a per-layer mean, not a sum, latency, or cycle count [guo-2025-qac]. No RTL
synthesis, cycle-accurate simulator, or technology node accompanies any part of this paper. Its own
Appendix 7.7, headed "Hardware Efficiency Analysis," states plainly that under the pipelined
multi-core execution model standard to platforms like TrueNorth and Loihi, a mixed-timestep SNN
requires a downstream layer to wait until an upstream layer completes its own, different, number of
timesteps before it can begin, and that pipeline stalling may occur as a result, introducing
computational delays [guo-2025-qac]. This is a direct, qualitative acknowledgment from the authors
of the exact failure mode a per-layer heterogeneous timestep schedule creates on real pipelined
hardware. No quantitative estimate of the resulting stall penalty accompanies the statement.

MT-SNN, the direct successor to QAC from an overlapping author list, claims 73.63% top-1 accuracy
on ResNet-34/ImageNet-1K at 4.88 average timesteps, again a per-layer mean [guo-2026-mtsnn-withdrawn].
The paper was submitted to ICLR 2026 and withdrawn near or after the review period, and the same
author group subsequently republished essentially the same result, rebranding the temporal-
alignment mechanism as "Scaled Synaptic Current Accumulation," in Frontiers in Neuroscience
[guo-2026-mtsnn-frontiers]. Neither the withdrawn version nor the republished version reports any
accelerator implementation, RTL synthesis, cycle-accurate simulator, or physical chip; both remain
E5 on the evidence available.

Whether any simulator or chip can execute a genuinely per-layer heterogeneous timestep horizon
within a single forward pass is answered directly, not merely assumed, by NeuroScale. Li, Imam,
and Manohar confirm that TrueNorth, Loihi, Loihi 2, and Tianjic all advance time through a single
global synchronization signal shared by every core, an externally controlled clock or barrier that
prevents any core from proceeding to the next tick until every other core has finished the current
one [li-2025-neuroscale]. There is architecturally no notion, on any of these four platforms, of
one layer sitting at tick eight while another sits at tick two. This is exactly the mechanism that
produces the pipeline stalling QAC's own appendix describes, and it holds independently of whether
any particular mixed-timestep paper's software simulation happens to produce a coherent-looking
`T_eff` number. On the software side, no simulator audited here executes per-layer heterogeneous
`T` natively either. PASCAL and QAC both compute each layer's contribution as a separate, layer-
local unrolling inside a standard simulation loop, then explicitly re-align the resulting spike
trains between layers before the next layer can consume them, which confirms that even in software
a layer at `T_l` cannot hand its output directly to a layer at `T_{l+1}` timesteps without an
explicit workaround [ramesh-2025-pascal], [guo-2025-qac].

One paper reaches physical silicon while training with heterogeneous timesteps, and it sidesteps
rather than solves this problem. Du, Wu, Deng, and Gu's Mixed Time-step Training randomly assigns
different timesteps to different stages during training to produce a single model that generalizes
across many evaluation timestep counts, then deploys the resulting weights to a physical Speck2e
device, measuring a 3.92% spike-difference metric against a software simulator on N-MNIST
[du-2025-tempflex]. This is genuine physical-silicon measurement, but Speck2e is fully event-driven
and asynchronous, with no discrete timestep concept at all, so there is no `T` to be heterogeneous
about on that chip. The paper's contribution is making a network's weights transferable across the
boundary between discrete-time and event-driven execution, not executing a mixed-integer-`T`
schedule on synchronous, barrier-clocked hardware, which remains the unsolved case QAC's own
appendix describes.

## 4.4 Hardware-Aware and Co-Designed Conversion

A small number of conversion papers reach physical silicon precisely because they abandon the
rate-coded, uniform-grid correspondence in favor of a code native to the target chip. Quartz
proposes a time-to-first-spike conversion scheme using two additional synapses per neuron to avoid
the dynamic-threshold machinery that made earlier temporal-coding methods hard to implement, and
its own abstract states explicitly that prior temporal-coding conversion methods "have yet to show
that they can be implemented on neuromorphic hardware" [lenz-2023-quartz]. Quartz closes that gap
on physical Loihi 1, reporting on-chip static power, dynamic power, latency, energy per inference,
and energy-delay product for MNIST and CIFAR-10, measured with NxSDK on a Nahuku 32 board
[lenz-2023-quartz]. MNIST reaches 0.77% error against a 0.73% ANN baseline in 65 timesteps and 5.4
thousand spikes; CIFAR-10 reaches 25.14% error in 1211 timesteps, considerably worse than the
rate-coded NxTF result of 8.52% on the same dataset, which the paper frames as a direct energy-
accuracy trade rather than a strict improvement [lenz-2023-quartz]. Because Quartz's neurons fire
at most once, the paper states plainly that no soft reset of membrane potential is needed at all,
which underlines that reset-by-subtraction is specifically a rate-coding concern, not a universal
requirement of ANN-to-SNN conversion [lenz-2023-quartz].

Brehove, Tumpa, Kyubwa, Menon, and Narayanan convert an ANN into a Sigma-Delta Neural Network built
around Loihi 2's native graded-spike payloads rather than rate-coded IF neurons, and measure
latency and energy-delay product on a physical, multi-chip Loihi 2 VPX board against an NVIDIA
Jetson Xavier baseline, reporting 112 frames per second, 5.0 ms latency, and 20 millijoules per
frame on a YOLO-style detector in a fielded demo [brehove-2026]. Both papers converge on the same
finding from opposite directions inside the same low-`T` conversion literature. Every confirmed
instance found of a paper that both proposes a new or adapted conversion method and reports
physical-silicon measurement abandons rate coding for a code native to the target platform, temporal
single-spike coding for Quartz, graded sigma-delta spikes for Brehove et al. No paper was found
that keeps rate coding, proposes a new low-`T` conversion algorithm, and reaches physical silicon
with measurement.

## 4.5 Hybrid and Calibration-Based Fine-Tuning

Three papers correct a trained or partially converted network's activation statistics after the
fact rather than changing the conversion theorem itself. Li, Deng, Dong, Gong, and Gu's calibration
method adjusts bias, weight, and initial membrane-potential statistics post-training, explicitly
choosing to keep the first layer's input continuous rather than binary because generating binary
spikes "requires time and degrades accuracy," and reaches an ImageNet accuracy improvement on
MobileNet at `T=256` [li-2021-calibration]. Calibrating Offset Spikes iteratively detects and
corrects the offset between an SNN's actual spike output and the value its source ANN activation
would produce, reaching 67.12% top-1 ImageNet accuracy at `T=6` [hao-2023-cos]. Adaptive
Calibration introduces a training-free burst-firing calibration step reaching 75%-plus ImageNet-
class accuracy at `T=8`, and states its energy figures come from "the method of calculating the
theoretical energy... shown in the Appendix," an explicit theoretical estimate rather than a
measurement [wang-2025-adafire]. None of the three reports hardware execution; all three remain E5,
with energy figures where present flagged by the papers' own text as estimates.

## Table 2. Advanced conversion techniques, evidence summary

| # | Subsection | Method | Neuron / reset | Encoding | T | Datasets | Target hardware | What was measured | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4.1/4.2 | QCFS [bu-2022-qcfs] | IF, soft reset, clip-floor-shift activation | direct/analog | 4-512+ | CIFAR-10/100, ImageNet | none (aspirational only) | GPU accuracy vs. T | E5 |
| 2 | 4.1 | OPI [bu-2022-opi] | IF, optimal nonzero init. potential | direct/analog | 8-512+ | CIFAR-10/100, ImageNet | none | GPU accuracy vs. T | E5 |
| 3 | 4.1 | SRP [hao-2023-srp] | IF, residual membrane readout | direct/analog | 4-32 | CIFAR-10/100, ImageNet | none | GPU accuracy vs. T | E5 |
| 4 | 4.5 | COS [hao-2023-cos] | IF, offset-spike calibration | direct/analog | 2-8 | CIFAR-10/100, ImageNet | none | GPU accuracy vs. T | E5 |
| 5 | 4.2 | SlipReLU [jiang-2023-sliprelu] | IF, weighted-ReLU + step | direct/analog | 1-4 | CIFAR-10/100 | none | GPU accuracy vs. T | E5 |
| 6 | 4.1 | Burst spikes [li-2022-burstspikes] | Burst-IF, bounded Γ | direct/analog | <100 | CIFAR-10/100, ImageNet | none (design constraint reasoning only) | GPU accuracy vs. T | E5 |
| 7 | 4.1 | SNM [wang-2022-snm] | Signed-with-memory neuron | direct/analog | ≤128-1024 | CIFAR-10/100, ImageNet | none | GPU accuracy vs. T | E5 |
| 8 | 4.1 | Fast-SNN [hu-2023-fastsnn] | Signed IF | direct/analog | 3, 7, 15 | ImageNet, PASCAL VOC | none (Loihi cited as design justification) | GPU accuracy vs. T | E5 |
| 9 | 4.1 | Dynamic Confidence [li-2023-dynconf] | Soft-reset IF, early-exit policy | inherits base method | avg. 1.28-49.5 | CIFAR-10, ImageNet | none (explicit self-reported gap) | GPU spike-count proxy only | E5 |
| 10 | 4.2 | QFFS [li-2022-qffs] | IF, LSQ-based quant-aware ANN | explicit direct/analog | 4, 8/10 | CIFAR-10, ImageNet | none | GPU accuracy vs. T | E5 |
| 11 | 4.1 | SEENN [li-2023-seenn] | Inherits QCFS/TET, RL early-exit | inherits base method | avg. 1.08-6 | CIFAR-10/100, ImageNet, CIFAR10-DVS | none (V100 GPU latency proxy) | GPU latency, SynOps energy estimate | E5 |
| 12 | 4.2 | CS-QCFS [yang-2024-csqcfs] | IF, per-channel softplus-QCFS | direct/analog | 1 | CIFAR-10/100 | none (citation only) | GPU accuracy | E5 |
| 13 | 4.5 | AdaFire [wang-2025-adafire] | Adaptive burst-firing, training-free calib. | inherits base convention | 8 | CIFAR-10/100, ImageNet, CIFAR10-DVS, COCO | none (Loihi 2/Speck cited as motivation) | GPU accuracy; theoretical energy | E5 |
| 14 | 4.3 | PASCAL, uniform-T check [ramesh-2025-pascal] | PASC-IF (spike accumulation + inhibitory spikes) | direct/analog | T=4 (overhead check) | CIFAR-10 (VGG-16) | modified LoAS + SparTen, Synopsys 40 nm/560 MHz | Energy, latency vs. standard IF | E4 |
| 15 | 4.3 | PASCAL, mixed-T headline [ramesh-2025-pascal] | PASC-IF, Adaptive Layerwise | direct/analog | T_eff = 2.13-12.94 (layer mean) | CIFAR-10/100, ImageNet | none (software only) | GPU accuracy vs. T_eff | E5 |
| 16 | 4.3 | QAC [guo-2025-qac] | Soft-reset IF, mixed-precision quant. | direct/analog | T_eff = 2.33-3.74 (layer mean) | CIFAR-10, ImageNet | none (qualitative pipeline-stall discussion only) | GPU accuracy vs. T_eff | E3 (execution discussion) / E5 (accuracy) |
| 17 | 4.3 | MT-SNN (withdrawn/Frontiers) [guo-2026-mtsnn-withdrawn], [guo-2026-mtsnn-frontiers] | Soft-reset IF, per-layer T + SSCA alignment | direct/analog | T_eff = 4.88 (layer mean) | CIFAR-10, ImageNet-1K, CIFAR10-DVS, DVS-Gesture | none | GPU accuracy vs. T_eff | E5 |
| 18 | 4.3 | Temporal Flexibility / MTT [du-2025-tempflex] | Stage-randomized T during training | direct/analog + event | 1-20, or event-driven | NMNIST | Speck2e (physical) | Spike-difference vs. software sim, on-chip accuracy | E1/E2 |
| 19 | 4.4 | Quartz [lenz-2023-quartz] | Non-leaky IF, single spike, no reset needed | TTFS | 65 (MNIST), 1211 (CIFAR-10) | MNIST, CIFAR-10 | Loihi 1 (physical) | Power, latency, energy/inference, EDP | E1 |
| 20 | 4.4 | Sigma-Delta on Loihi 2 [brehove-2026] | Graded-spike SDNN | delta/sigma (graded) | 16 (fall-through mode) | video/RGB frames | Loihi 2, multi-chip VPX (physical) | Latency, energy-delay product vs. Jetson Xavier | E1 |
| 21 | 4.5 | SNN Calibration [li-2021-calibration] | IF, calibrated stats | explicit continuous first layer | ≤256 | CIFAR-10/100, ImageNet | none | GPU accuracy; explicit SynOps estimate | E5 |
| 22 | 4.1 | SpikeConverter [liu-2022-spikeconverter] | Inverse-leaky IF | direct/analog | 16 | CIFAR-10/100, ImageNet | none (background motivation only) | GPU accuracy vs. T | E5 |
| 23 | 4.3 | NeuroFlex accelerator [manjunath-2025-neuroflex] | Column-exact PASCAL activation, INT8 | direct/analog | tied to per-column L | VGG-16, ResNet-34, GoogLeNet, BERT | RTL, Synopsys 40 nm/560 MHz, cycle simulator | EDP, throughput | E4 |

---

# 5 Alternative Codes and Non-Rate Representations

## 5.1 Temporal and TTFS

Time-to-first-spike coding lets each neuron fire at most once, with the timing of that single
spike carrying the value, typically an inverse relationship in which a larger value fires earlier
[rueckauer-2017]. In principle a single spike's continuous-valued timing carries arbitrary
precision, which is why T2FSNN reports spike counts under 1% and 22% of the latency of burst
coding on CIFAR-100 [park-2020-t2fsnn]. Once a TTFS-coded network is deployed on real hardware,
firing times must be quantized to the chip's discrete timestep grid, which reintroduces the same
quantization floor the coding scheme was meant to avoid, and a 2026 paper on latency coding states
this directly, that floating-point firing times are "not natively supported by existing
neuromorphic hardware, which is designed to communicate discrete binary spikes"
[latencycoding-2026]. The single-spike constraint that gives TTFS its efficiency also makes it hard
to train, because most of the network's expressive content must be squeezed into precise spike
timing rather than spike count, and quantization error accumulates across layers in deep networks
[yoso-2020]. Guo et al.'s comparative study finds TTFS has the fastest inference convergence of the
coding schemes it tests but the slowest effective training convergence, because gradient-based
training needs long time windows to produce useful spike-time gradients [guo-2021-neuralcoding].
ETTFS addresses this with parameter initialization, a learned temporal-weighting decoder, and by
relaxing the strict single-spike constraint in hidden layers to preserve gradient flow
[ettfs-2024].

TTFS reaches hardware more directly than the rate-coded low-`T` lineage does. Quartz is a TTFS
conversion method measured on physical Loihi 1 with a full power, latency, and energy-delay-product
table, and because its neurons fire at most once it needs no soft-reset mechanism at all
[lenz-2023-quartz], as discussed in Section 4.4. SpiNNaker2's event-based backpropagation
implementation names a dedicated "Time-to-First-Spike Loss Program" that transmits and consumes
first-spike timing values as part of its backward pass [deneve-2022-ttfs]. No source located for
this audit confirms a dedicated TTFS-decoding hardware primitive on DYNAP-CNN/Speck, BrainScaleS-2,
or TrueNorth specifically, which does not mean TTFS is unsupported there, only that no documented,
dedicated mechanism was found.

## 5.2 Phase and Weighted-Slot

Phase coding assigns each spike a weight determined by its position within a repeating cycle of `K`
timesteps, typically powers of two, `2^{K-1}` down to `2^0`, analogous to binary place value
[kim-2018-weightedspikes]. Because the weights are powers of two, the representable output values
are sums over a subset of that geometric sequence, which makes phase coding's effective
quantization grid genuinely non-uniform, exponentially weighted rather than evenly spaced. This is
the direct contrast case to rate and count coding's uniform `1/T`-spaced grid established in
Section 4.2, and it is exactly the spike-domain analogue of non-uniform, logarithmic-style
quantization rather than the uniform integer quantization QCFS and reset-by-subtraction implement.
The efficiency this buys is real but bounded. A single early-phase spike can carry as much
information as many unweighted spikes, cutting classification latency relative to plain rate
coding, but a follow-up paper on stepwise weighted spike coding reports that the transmission
capacity of phase coding is bounded by a single global phase shared across the whole network,
which produces inefficiency in hidden layers and latency of up to three thousand steps for a
32-layer network [swsc-2024]. A bistable-SNN paper combining phase coding with a bistability
mechanism reports the same order-of-magnitude limitation, roughly three thousand simulation steps
for phase coding alone on CIFAR-100 [bsnn-2022]. No dedicated hardware primitive for phase coding
was found on any of the platforms reviewed for this survey. It is implemented purely as a software
or training-time convention layered on top of an ordinary binary-spike substrate, which any of the
reviewed platforms can in principle host, but none advertise a native phase-decoding mechanism.

## 5.3 Differential, Sigma-Delta, and Graded Payloads

A sigma-delta neural network wraps a conventional activation with a delta encoder on its output and
a sigma, running-sum, decoder on the receiving end. The delta encoder transmits a spike carrying
only the change in activation since the last transmitted value, and only when that change exceeds
a threshold, which exploits temporal redundancy in slowly changing input in addition to the usual
spatial sparsity a rate code exploits [shrestha-2023-loihi2video]. Loihi 2 is the platform that
makes this practical at the hardware level, supporting graded spikes that carry up to 24 bits of
signed integer magnitude in the spike message itself, in contrast to Loihi 1's binary-only spikes
[shrestha-2023-loihi2video], [brehove-2026]. Brehove et al.'s conversion pipeline built on this
feature is discussed in Section 4.4; Lava-DL's SLAYER library exposes sigma-delta blocks as a
first-class layer type alongside CUBA and adaptive-LIF blocks, explicitly described as amenable to
backpropagation [lavadl-slayer-docs]. Loihi 1 lacks native graded spikes and approximates a
sigma-delta neuron only through a two-compartment adaptive-LIF workaround, at twice the compartment
cost of the single-compartment case, which Boeshertz et al. use to set a new state of the art for
on-chip speech classification with three-bit quantization-aware trained weights
[boeshertz-2024-alif]. SpiNNaker2's software-defined packet system carries 128-bit payloads and has
been shown to transmit signed floating-point values for gradient error signals during a backward
pass, which demonstrates the packet architecture can carry a graded or signed payload, but this has
been demonstrated for gradients specifically, not yet for a forward-pass sigma-delta activation
encoding in any source reviewed here [deneve-2022-ttfs]. No native graded-spike or sigma-delta
support was found documented for SpiNNaker 1, DYNAP-CNN/Speck, BrainScaleS-2, or TrueNorth.

## 5.4 Rank Order Coding

Rank order coding was introduced by Thorpe and Gautrais to explain how the primate visual system
performs complex recognition in under 150 milliseconds, a budget too short for conventional rate
coding, which needs at least two spikes to estimate an interspike interval [thorpe-1996]. Each
neuron in a population fires at most once, modeled as an integrate-and-fire analog-to-delay
converter in which more strongly activated neurons cross threshold sooner, and the encoded
information is carried entirely by the relative order in which the population fires, not by which
timesteps carry spikes and not by how many spikes occur [thorpe-spikebased]. The code is ordinal,
not cardinal. Rank order coding is explicitly contrast-invariant, because rescaling input intensity
changes the absolute latency of every analog-to-delay converter but leaves the relative order
unchanged, at the cost of discarding the absolute amplitude information a rate or TTFS code
preserves [cerco-spikenet-docs]. The canonical decoder is a shunting-inhibition mechanism, in which
every afferent spike progressively desensitizes the postsynaptic neuron, so the earliest-arriving
input contributes most and later inputs contribute progressively less, letting a neuron's synaptic
weights encode a target rank ordering without any explicit timestamp storage [thorpe-spikebased].
Deneve et al.'s unifying framework places rank order coding precisely relative to two neighboring
schemes. TTFS reads the continuous timing value of each spike; rank order coding reads only the
relative order and discards timing entirely; N-of-M coding keeps only a hard cutoff on the first
`N` of `M` afferents to fire, discarding order as well as timing, in exchange for needing only
binary synapses; a fourth hybrid, Ranked-N-of-M, restores order-sensitivity to the N-of-M cutoff
[deneve-2022-ttfs].

No ANN-to-SNN conversion theorem reviewed for this survey targets rank order coding, and there is a
structural reason to expect none currently does. Every conversion proof surveyed, including the
SNN Toolbox derivation and Ding et al.'s optimal-conversion theorem, is built on matching a
per-layer firing rate between the ANN and the SNN, a cardinal quantity, a count or magnitude
[rueckauer-2017], [ding-2021-optimalconv]. A rank-order code over the same layer's neurons encodes
only their relative order, a single combinatorial object drawn from `N!` possible permutations,
which has no obvious analogue to a per-neuron magnitude that a convergence proof could match layer
by layer. Mapping an ANN activation vector onto a target permutation for one layer is
straightforward, the sort order of the activations themselves, but no source reviewed here attempts
the harder half, a proof that a downstream layer's rank-order output, computed by the shunting-
inhibition decoder from an upstream layer's rank-order input, converges to the ordering the source
ANN's own next layer would have produced. This gap is sharpened, not resolved, by the fact that a
commercially shipping processor, BrainChip's Akida, is built on rank-order-coding lineage. No
source examined for this survey, including a dedicated research pass on Akida specifically, shows
Akida's converted-CNN deployment path, the path essentially all published Akida benchmarks use,
implementing the order-sensitive shunting-inhibition mechanism inside a network's hidden layers.
Direct inspection of the CNN2SNN toolkit's source shows the Akida 1.0 activation output computed
as a single, static per-neuron threshold comparison, a magnitude test that is order-agnostic within
a layer, it registers only whether a weighted sum crosses a threshold, not which input arrived
first [cnn2snn-source-inspection]. No published conversion theorem targets rank order coding, and
that absence holds even inside the one toolchain built by the company most associated with the
code commercially, which is discussed fully below.

The clearest measured hardware comparison of rank order coding against rate coding is MorphIC, a
65-nanometer, four-core digital neuromorphic chip. On the identical MNIST classification task, on
the same fabricated chip, rate coding reaches 97.8% accuracy at 205 microjoules per classification,
while rank order coding, in which the inferred class is whichever output neuron spikes first,
reaches 95.9% accuracy, a 1.9-percentage-point drop, at 21.8 microjoules per classification, a
measured, on-chip energy reduction the paper's own text states as tenfold [frenkel-2019-morphic].
BrainChip's Akida processor is the clearest commercial instance of rank order coding presented as a
native hardware encoding, and its lineage is genuine rather than a label attached after the fact.
BrainChip acquired Spikenet Technology, the company that grew out of Simon Thorpe's own
rank-order-coding research program, in September 2016, and Thorpe has since sat on BrainChip's
Scientific Advisory Board [akida-story-2016]. An independent trade-press technical analysis
corroborates the resulting design pivot directly, reporting that BrainChip started with rate
coding, found it commercially unworkable, and moved to rank coding instead [moyer-2020-semieng].
BrainChip's own technical documentation states that Akida's native encoding expresses information
as the time and place an event occurs, paired with a non-leaky integrate-and-fire neuron
[brainchip-akida-techbrief], and an independent community technical summary corroborates this
specifically at the input-encoding stage, describing Akida as converting pixels to events using
rank order coding rather than implementing leaky integrate-and-fire dynamics
[openneuromorphic-akida]. The lineage and the input-encoding stage are real.

What is not established by any source located, for this survey or for the dedicated Akida research
pass behind it, is that order-sensitivity operates past that input stage. The converted-CNN
deployment path, the one essentially all published Akida benchmarks use, collapses to a single
feedforward pass over quantized, integer-only activations. Two independent groups that trained and
deployed on physical AKD1000 hardware confirm this from opposite research communities, both
describing the mechanism as a step-wise quantized ReLU evaluated once rather than a rate code
unrolled over a simulation horizon, with one reporting energy of 0.63 to 1.38 millijoules per frame
on a EuroSAT classification task measured on the chip itself [ziegler-2024-fastobjects],
[lunghi-2025-space-snn]. Direct inspection of the CNN2SNN toolkit's own source code confirms the
mechanism rather than merely the behavior. The Akida 1.0 activation output is a magnitude
comparison against a static, per-neuron threshold that has absorbed a batch-norm fold and a
rounding offset, computed once at conversion time, not an iterative accumulate-compare-reset loop,
and that comparator is order-agnostic. It registers whether a weighted sum crosses a threshold, not
which input arrived first [cnn2snn-source-inspection]. Both halves of this picture carry equal
weight. Akida's rank-order-coding heritage is genuine, and its input-encoding stage is described by
multiple independent, non-BrainChip sources as rank-order-coded; equally, no source shows that
heritage's defining order-sensitive mechanism operating inside the hidden layers of a converted
CNN on the silicon nearly every published Akida result actually uses. Section 6.1 gives Akida a
full platform entry and states this divergence in the detail a platform-level treatment requires;
it is treated here only as it bears on rank order coding as a code, not repeated as a platform
assessment. A dedicated 65-nanometer research ASIC implementing
rank order coding with unsupervised spike-timing-dependent plasticity reports 90.2% MNIST accuracy
at 6.79 microjoules per classification, motivated explicitly by rank order coding needing roughly
thirty simulation steps against hundreds for a two-layer rate-coded network of comparable depth
[kim-2020-roc-scnn]. No source reviewed here documents rank-order-coding support, or its absence,
on Loihi 1, Loihi 2, SpiNNaker, DYNAP-CNN/Speck, BrainScaleS-2, or TrueNorth; given that any
substrate able to determine which of a population's neurons spiked first could in principle run a
rank-order code, this is most plausibly a gap in documentation rather than a gap in capability.

## Table 3. Alternative codes and non-rate representations, evidence summary

| # | Subsection | Method / platform | Neuron / reset | Encoding | T | Datasets | Target hardware | What was measured | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.1 | T2FSNN [park-2020-t2fsnn] | TTFS neuron | TTFS | single spike | CIFAR-100 | none | GPU spike count, latency vs. burst coding | E5 |
| 2 | 5.1 | ETTFS [ettfs-2024] | Relaxed single-spike | TTFS | single spike (relaxed hidden layers) | not detailed | none | GPU accuracy, training convergence | E5 |
| 3 | 5.1 | Quartz [lenz-2023-quartz] | Non-leaky IF, no soft reset needed | TTFS | 65 (MNIST), 1211 (CIFAR-10) | MNIST, CIFAR-10 | Loihi 1 (physical) | Power, latency, energy/inference, EDP | E1 |
| 4 | 5.1 | SpiNNaker2 EventProp TTFS [deneve-2022-ttfs] | software-defined | TTFS loss/backward pass | n/a | not detailed | SpiNNaker2 (physical, programmable) | Timing-value transmission in backward pass | E1 (mechanism demo) |
| 5 | 5.2 | Weighted spikes [kim-2018-weightedspikes] | standard IF/LIF, phase-weighted decode | phase (powers of two, non-uniform grid) | K-cycle repeating window | not detailed | none documented | GPU accuracy, latency vs. rate coding | E5 |
| 6 | 5.2 | Stepwise weighted spike coding [swsc-2024] | phase-weighted | phase | up to ~3000 (32-layer net) | not detailed | none | GPU latency limitation analysis | E5 |
| 7 | 5.2 | BSNN [bsnn-2022] | bistable + phase | phase | ~3000 (CIFAR-100) | CIFAR-100 | none | GPU accuracy, step count | E5 |
| 8 | 5.3 | Sigma-Delta on Loihi 2 [brehove-2026] | Graded-spike SDNN | delta/sigma (graded, native 24-bit) | 16 (fall-through) | video/RGB frames | Loihi 2 (physical) | Latency, EDP vs. Jetson Xavier | E1 |
| 9 | 5.3 | Boeshertz et al. aLIF/ΣΔ [boeshertz-2024-alif] | 2-compartment workaround on Loihi 1 | delta/sigma (workaround) | task-dependent | speech/audio | Loihi 1 (physical) | On-chip speech classification accuracy, SOTA claim | E1/E2 |
| 10 | 5.3 | Lava-DL sigma-delta blocks [lavadl-slayer-docs] | sigma-delta layer type | delta/sigma | n/a | n/a (library documentation) | Loihi 2 (documented path) | Documented, not independently benchmarked here | E3 |
| 11 | 5.4 | MorphIC rate vs. ROC [frenkel-2019-morphic] | LIF, 2k neurons, 4 cores | rate vs. rank order (both measured, same chip) | n/a | MNIST | 65 nm MorphIC chip (physical) | Accuracy, measured energy/classification, both codes | E1 |
| 12 | 5.4 | BrainChip Akida, input encoding only [brainchip-akida-techbrief], [ziegler-2024-fastobjects], [lunghi-2025-space-snn], [cnn2snn-source-inspection] | non-leaky IF at circuit level; converted-CNN path is a static, order-agnostic threshold comparator | rank order (genuine lineage, native/default at input stage; order-sensitivity not shown inside hidden layers) | effectively 1 (converted-CNN path) | EuroSAT (third-party benchmark) | AKD1000 (physical; full platform entry in Section 6.1) | Energy/frame (third-party silicon benchmark); toolkit source inspection | E1 (third-party, converted-CNN path) |
| 13 | 5.4 | 65 nm ROC-SCNN ASIC [kim-2020-roc-scnn] | custom STDP-trained | rank order | ~30 | MNIST | custom 65 nm ASIC (physical) | Accuracy, energy/classification, throughput | E1 |
| 14 | 5.4 | Rate/count coding baseline (cross-reference) [rueckauer-2017] | IF, reset-by-subtraction | rate/count (uniform T-level grid) | varies | MNIST, CIFAR-10, ImageNet | none (own paper) | GPU accuracy only | E5 |

---

## References for Sections 3 to 5

- [fang-2021-sew] Fang, W. et al. "Deep Residual Learning in Spiking Neural Networks." NeurIPS
  2021, arXiv:2102.04159. Peer-reviewed (conference).
- [zheng-2021-tdbn] Zheng, H., Wu, Y., Deng, L., Hu, Y., Li, G. "Going Deeper With Directly-Trained
  Larger Spiking Neural Networks." AAAI 2021, arXiv:2011.05280. Peer-reviewed (conference).
- [fang-2021-plif] Fang, W. et al. "Incorporating Learnable Membrane Time Constant to Enhance
  Learning of Spiking Neural Networks." ICCV 2021, arXiv:2007.05785. Peer-reviewed (conference).
- [deng-2022-tet] Deng, S. et al. "Temporal Efficient Training of Spiking Neural Network via
  Gradient Re-weighting." ICLR 2022, arXiv:2202.11946. Peer-reviewed (conference).
- [zhou-2023-spikformer] Zhou, Z. et al. "Spikformer: When Spiking Neural Network Meets
  Transformer." arXiv:2209.15425 (2022/2023). Preprint.
- [zhou-2024-spikformerv2] Zhou, Z. et al. "Spikformer V2: Join the High Accuracy Club on ImageNet
  with an SNN Ticket." arXiv:2401.02020 (2024). Preprint.
- [zhou-2023-spikingformer] Zhou, C. et al. "Spikingformer: A Key Foundation Model for Spiking
  Neural Networks." AAAI 2026 / arXiv:2304.11954. Peer-reviewed (conference).
- [yao-spikedriven] Yao, M. et al. "Spike-driven Transformer / Meta-SpikeFormer V2." Citation
  details incomplete in the underlying research audit (a12); recorded here from the audit's own
  table entry, not independently re-verified. Preprint (unconfirmed identifier).
- [song-2024-xpikeformer] Song, S., Katti, A., Simeone, O., Rajendran, B. "Xpikeformer: Hybrid
  Analog-Digital Hardware Acceleration for Spiking Transformers." arXiv:2408.08794 (2024).
  Preprint.
- [shrestha-2018-slayer] Shrestha, S. B., Orchard, G. "SLAYER: Spike Layer Error Reassignment in
  Time." NeurIPS 2018, arXiv:1810.08646. Peer-reviewed (conference).
- [intel-nxtf-slayer-gestures] Intel `intel-nrc-ecosystem/models` repository,
  `nxsdk_modules_ncl/dnn/tutorials/d_slayer_nxtf_gestures.py`.
  https://github.com/intel-nrc-ecosystem/models. Repository state / vendor material.
- [meszaros-2025-loihi2-delays] Mészáros, A., Knight, J., Timcheck, J., Nowotny, T. "A Complete
  Pipeline for deploying SNNs with Synaptic Delays on Loihi 2." arXiv:2510.13757 (2025). Preprint.
- [clpsnn-2025] "Online Continual Learning on Intel Loihi 2 via a Co-designed Spiking Neural
  Network" (CLP-SNN). arXiv:2511.01553 (2025). Preprint.
- [bauer-2023-exodus] Bauer, F. C., Lenz, G., Haghighatshoar, S., Sheik, S. "EXODUS: Stable and
  Efficient Training of Spiking Neural Networks." Frontiers in Neuroscience 2023 /
  arXiv:2205.10242. Peer-reviewed.
- [richter-2023-speck1] Richter, O. et al. "Speck: A Smart event-based Vision Sensor with a low
  latency 327K Neuron Convolutional Neuromorphic Processor." arXiv:2304.06793 (2023). Preprint.
- [yao-2024-speck-naturecomm] Yao, M. et al. "Spike-based dynamic computing with asynchronous
  sensing-computing neuromorphic chip." Nature Communications 15 (2024).
  https://doi.org/10.1038/s41467-024-47811-6. Peer-reviewed.
- [liu-2019-facedemo] Liu, Q., Richter, O., Nielsen, C., Sheik, S., Indiveri, G., Qiao, N. "Live
  Demonstration: Face Recognition on an Ultra-Low Power Event-Driven Convolutional Neural Network
  ASIC." CVPRW 2019. Peer-reviewed (conference).
- [sinabs-docs] SynSense / Sinabs documentation, N-MNIST quick-start (direct BPTT training via
  `sinabs-exodus`, deployment to Speck2f dev kit). https://sinabs.readthedocs.io/. Official
  documentation.
- [riverpub-mcu-dynapcnn] "Deploying a Convolutional Neural Network on Edge MCU and Neuromorphic
  Hardware Platforms." River Publishers book chapter.
  https://www.riverpublishers.com/pdf/ebook/chapter/RP_9788770227902C10.pdf. Peer-reviewed (book
  chapter).
- [hiaer-cri-docs] UCSD Institute for Neural Computation, "DVS128 Gesture Inference on HiAER-Spike
  Hardware." https://isn.ucsd.edu/hiaer-spike/auto_examples/plot_dvs_gesture_inference.html.
  Official documentation.
- [imam-2020-olfaction] Imam, N., Cleland, T. A. "Rapid online learning and robust recall in a
  neuromorphic olfactory circuit." Nature Machine Intelligence 2 (2020).
  https://doi.org/10.1038/s42256-020-0159-4. Peer-reviewed.
- [tang-2019-slam] Tang, G., Shah, A., Michmizos, K. P. "Spiking Neural Network on Neuromorphic
  Hardware for Energy-Efficient Unidimensional SLAM." arXiv:1903.02504 (2019). Preprint.
- [sddpg-2020] "Reinforcement co-Learning of Deep and Spiking Neural Networks for Energy-Efficient
  Mapless Navigation with Neuromorphic Hardware." arXiv:2003.01157 (2020). Preprint.
- [kreiser-2020-icub] Kreiser, R. et al. "An On-chip Spiking Neural Network for Estimation of the
  Head Pose of the iCub Robot." Frontiers in Neurorobotics 2020.
  https://doi.org/10.3389/fnbot.2020.00035. Peer-reviewed.
- [forcecontrol-2024] "Neuromorphic force-control in an industrial task: validating energy and
  latency benefits." arXiv:2403.08928 (2024). Preprint.
- [davies-2018-loihi] Davies, M. et al. "Loihi: A Neuromorphic Manycore Processor with On-Chip
  Learning." IEEE Micro 38(1) (2018). https://doi.org/10.1109/MM.2018.112130359. Peer-reviewed.
- [tang-2017-lca-theory] Tang, P. T. P., Lin, T.-H., Davies, M. "Sparse Coding by Spiking Neural
  Networks: Convergence Theory and Computational Results." arXiv:1705.05475 (2017). Preprint.
- [parpart-2023-lca-loihi2] Parpart, G., Risbud, S., Kenyon, G., Watkins, Y. "Implementing and
  Benchmarking the Locally Competitive Algorithm on the Loihi 2 Neuromorphic Processor." 2023.
  Preprint.
- [convlca-2025-2026] "Convolutional Sparse Coding via the Locally Competitive Algorithm on
  Loihi 2." arXiv preprint (2025/2026). Preprint.
- [satcsp-2020] "Solving Constraint Satisfaction Problems Using the Loihi Processor." DATE 2020
  workshop paper. Peer-reviewed (workshop).
- [bos-2024-xylo] Bos, H., Muir, D. "Micro-power spoken keyword spotting on Xylo Audio 2."
  arXiv:2406.15112 (2024). Preprint.
- [fang-2023-spikingjelly-sciadv] Fang, W. et al. "SpikingJelly: An open-source machine learning
  infrastructure platform for spike-based intelligence." Science Advances 9(40) (2023).
  https://doi.org/10.1126/sciadv.adi1480. Peer-reviewed.
- [objdet-2026-loihi2-preprint] "Real-Time Frame- and Event-based Object Detection with Spiking
  Neural Networks on Edge Neuromorphic Hardware: Design, Deployment and Benchmark." 2026 preprint;
  code repository `gwgknudayanga/Realtime-frame--and-event-based-detection-with-SNN-on-
  Neuromorphic-hardware`. Preprint.
- [spikingjelly-issue543] `fangwei123456/spikingjelly` GitHub Issue #543, "Limitations when
  deploying SNNs to loihi" (May 2024). Repository state / community commentary.
- [cao-2015] Cao, Y., Chen, Y., Khosla, D. "Spiking Deep Convolutional Neural Networks for
  Energy-Efficient Object Recognition." International Journal of Computer Vision 113(1) (2015).
  https://doi.org/10.1007/s11263-014-0788-3. Peer-reviewed.
- [diehl-2015] Diehl, P. U., Neil, D., Binas, J., Cook, M., Liu, S.-C., Pfeiffer, M.
  "Fast-classifying, high-accuracy spiking deep networks through weight and threshold balancing."
  IJCNN 2015. https://doi.org/10.1109/IJCNN.2015.7280696. Peer-reviewed (conference).
- [rueckauer-2017] Rueckauer, B., Lungu, I.-A., Hu, Y., Pfeiffer, M., Liu, S.-C. "Conversion of
  Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image Classification."
  Frontiers in Neuroscience 11:682 (2017). https://doi.org/10.3389/fnins.2017.00682.
  Peer-reviewed.
- [sengupta-2019-spikenorm] Sengupta, A., Ye, Y., Wang, R., Liu, C., Roy, K. "Going Deeper in
  Spiking Neural Networks: VGG and Residual Architectures." Frontiers in Neuroscience 13:95
  (2019). https://doi.org/10.3389/fnins.2019.00095. Peer-reviewed.
- [han-2020-rmpsnn] Han, B., Srinivasan, G., Roy, K. "RMP-SNN: Residual Membrane Potential Neuron
  for Enabling Deeper High-Accuracy and Low-Latency Spiking Neural Network." CVPR 2020.
  https://doi.org/10.1109/CVPR42600.2020.01357. Peer-reviewed (conference).
- [han-2020-tsc] Han, B., Roy, K. "Deep Spiking Neural Network: Energy Efficiency Through Time
  Based Coding." ECCV 2020. https://doi.org/10.1007/978-3-030-58607-2_23. Peer-reviewed
  (conference).
- [deng-2021-optconv] Deng, S., Gu, S. "Optimal Conversion of Conventional Artificial Neural
  Networks to Spiking Neural Networks." ICLR 2021, arXiv:2103.00476. Peer-reviewed (conference).
- [li-2021-calibration] Li, Y., Deng, S., Dong, X., Gong, R., Gu, S. "A Free Lunch From ANN:
  Towards Efficient, Accurate Spiking Neural Networks Calibration." ICML 2021,
  arXiv:2106.06984. Peer-reviewed (conference).
- [ho-2021-tcl] Ho, N.-D., Chang, I.-J. "TCL: an ANN-to-SNN Conversion with Trainable Clipping
  Layers." DAC 2021, arXiv:2008.04509. Peer-reviewed (conference).
- [esser-2016-eedn] Esser, S. K. et al. "Convolutional networks for fast, energy-efficient
  neuromorphic computing." PNAS 113(41) (2016). https://doi.org/10.1073/pnas.1604850113.
  Peer-reviewed.
- [stromatias-2015-spinnaker] Stromatias, E., Neil, D., Galluppi, F., Pfeiffer, M., Liu, S.-C.,
  Furber, S. "Scalable Energy-Efficient, Low-Latency Implementations of Spiking Deep Belief
  Networks on SpiNNaker." IJCNN 2015. https://doi.org/10.1109/IJCNN.2015.7280625. Peer-reviewed
  (conference).
- [massa-2020-loihi-dvs] Massa, R., Marchisio, A., Martina, M., Shafique, M. "An Efficient
  Spiking Neural Network for Recognizing Gestures with a DVS Camera on the Loihi Neuromorphic
  Processor." IJCNN 2020. https://doi.org/10.1109/IJCNN48605.2020.9207109. Peer-reviewed
  (conference).
- [rueckauer-2021-nxtf] Rueckauer, B., Bybee, C., Goettsche, R., Singh, Y., Mishra, J., Wild, A.
  "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi." ACM JETC /
  arXiv:2101.04261. Peer-reviewed.
- [kelber-2020-benchmark] Kelber, F. et al. "Benchmarking Deep Spiking Neural Networks on
  Neuromorphic Hardware." arXiv:2004.01656 (2020). Preprint.
- [bu-2022-qcfs] Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN Conversion
  for High-accuracy and Ultra-low-latency Spiking Neural Networks." ICLR 2022, arXiv:2303.04347.
  Peer-reviewed (conference).
- [bu-2022-opi] Bu, T., Ding, J., Yu, Z., Huang, T. "Optimized Potential Initialization for
  Low-latency Spiking Neural Networks." AAAI 2022, arXiv:2202.01440. Peer-reviewed (conference).
- [hao-2023-srp] Hao, Z., Bu, T., Ding, J., Huang, T., Yu, Z. "Reducing ANN-SNN Conversion Error
  through Residual Membrane Potential." AAAI 2023, arXiv:2302.02091. Peer-reviewed (conference).
- [hao-2023-cos] Hao, Z., Ding, J., Bu, T., Huang, T., Yu, Z. "Bridging the Gap between ANNs and
  SNNs by Calibrating Offset Spikes." ICLR 2023, arXiv:2302.10685. Peer-reviewed (conference).
- [jiang-2023-sliprelu] Jiang, H., Anumasa, S., De Masi, G., Xiong, H., Gu, B. "A Unified
  Optimization Framework of ANN-SNN Conversion." ICML 2023.
  https://proceedings.mlr.press/v202/jiang23a.html. Peer-reviewed (conference).
- [li-2022-burstspikes] Li, Y., Zeng, Y. "Efficient and Accurate Conversion of Spiking Neural
  Network with Burst Spikes." IJCAI 2022, arXiv:2204.13271. Peer-reviewed (conference).
- [wang-2022-snm] Wang, Y., Zhang, M., Chen, Y., Qu, H. "Signed Neuron with Memory: Towards Simple,
  Accurate and High-Efficient ANN-SNN Conversion." IJCAI 2022. Peer-reviewed (conference).
- [hu-2023-fastsnn] Hu, Y., Zheng, Q., Jiang, X., Pan, G. "Fast-SNN: Fast Spiking Neural Network by
  Converting Quantized ANN." IEEE TPAMI 2023, arXiv:2305.19868. Peer-reviewed.
- [li-2023-dynconf] Li, C., Jones, E., Furber, S. "Unleashing the Potential of Spiking Neural
  Networks with Dynamic Confidence." ICCV 2023, arXiv:2303.10276. Peer-reviewed (conference).
- [li-2022-qffs] Li, C., Ma, L., Furber, S. "Quantization Framework for Fast Spiking Neural
  Networks." Frontiers in Neuroscience 2022. https://doi.org/10.3389/fnins.2022.918793.
  Peer-reviewed.
- [li-2023-seenn] Li, Y., Geller, T., Kim, Y., Panda, P. "SEENN: Towards Temporal Spiking Early-Exit
  Neural Networks." NeurIPS 2023, arXiv:2304.01230. Peer-reviewed (conference).
- [yang-2024-csqcfs] Yang, H., Yang, S., Zhang, L., Dou, H., Shen, F., Zhao, J. "CS-QCFS: Bridging
  the performance gap in ultra-low latency SNNs." Neural Networks (2024/2025).
  https://doi.org/10.1016/j.neunet.2024.107076. Peer-reviewed.
- [wang-2025-adafire] Wang, Z., Fang, Y., Cao, J., Ren, H., Xu, R. "Adaptive Calibration: A Unified
  Conversion Framework of Spiking Neural Networks." AAAI 2025 (Oral), arXiv:2412.16219.
  Peer-reviewed (conference).
- [ramesh-2025-pascal] Ramesh, P., Srinivasan, G. "PASCAL: Precise and Efficient ANN-SNN Conversion
  using Spike Accumulation and Adaptive Layerwise Activation." TMLR (2025), arXiv:2505.01730.
  Peer-reviewed.
- [manjunath-2025-neuroflex] Manjunath, V. et al. "NeuroFlex: Column-Exact ANN-SNN Co-Execution
  Accelerator with Cost-Guided Scheduling." arXiv:2511.05215 (2025). Preprint.
- [liu-2022-spikeconverter] Liu, F., Zhao, W., Chen, Y., Wang, Z., Jiang, L. "SpikeConverter: An
  Efficient Conversion Framework Zipping the Gap between ANNs and SNNs." AAAI 2022. Peer-reviewed
  (conference).
- [guo-2025-qac] Guo, M., Li, Q., Li, Y., Cheng, J., Chen, L. "QAC: Quantization-Aware Conversion
  for Mixed-Timestep Spiking Neural Networks." ICLR 2025 submission #8774 (final venue
  unconfirmed). https://openreview.net/forum?id=D4sQzdMvcG. Preprint (unconfirmed venue).
- [guo-2026-mtsnn-withdrawn] Guo, M., Li, Q., Yao, X., Cheng, J., Chen, L. "Mixed-Timestep Spiking
  Neural Networks with Temporal Alignment for Ultra-Low Latency Conversion." ICLR 2026 withdrawn
  submission. https://openreview.net/forum?id=4dwAZRr9L5. Preprint (withdrawn).
- [guo-2026-mtsnn-frontiers] Guo, M., Yao, X., Li, Q., Li, Y., Cheng, J., Chen, L. "Mixed-Timestep
  Spiking Neural Networks: A Temporal Alignment Framework for High-Efficiency Neuromorphic
  Computing." Frontiers in Neuroscience (2026-08-12). Peer-reviewed.
- [li-2025-neuroscale] Li, C., Imam, N., Manohar, R. "A deterministic neuromorphic architecture
  with scalable time synchronization." Nature Communications 16, 10329 (2025).
  https://doi.org/10.1038/s41467-025-65268-z. Peer-reviewed.
- [du-2025-tempflex] Du, Y., Wu, Y., Deng, L., Gu, S. "Temporal Flexibility in Spiking Neural
  Networks: Towards Generalization Across Time Steps and Deployment Friendliness." ICLR 2025
  (Poster), arXiv:2503.17394. Peer-reviewed (conference).
- [lenz-2023-quartz] Lenz, G., Orchard, G., Sheik, S. "Ultra-low-power Image Classification on
  Neuromorphic Hardware." arXiv:2309.16795 (2023-2024). Preprint.
- [brehove-2026] Brehove, T., Tumpa, S. N., Kyubwa, E., Menon, A., Narayanan, V. "Sigma-Delta
  Neural Network Conversion on Loihi 2." ICONS 2026, arXiv:2505.06417. Peer-reviewed (conference).
- [park-2020-t2fsnn] Park, S., Kim, S., Na, B., Yoon, S. "T2FSNN: Deep Spiking Neural Networks
  with Time-to-first-spike Coding." arXiv:2003.11741 (2020). Preprint.
- [ettfs-2024] "Efficiently Training Time-to-First-Spike Spiking Neural Networks from Scratch"
  (ETTFS). arXiv:2410.23619 (2024). Preprint.
- [latencycoding-2026] "A Latency Coding Framework for Deep Spiking Neural Networks with
  Ultra-Low Latency." arXiv:2603.23206 (2026). Preprint.
- [deneve-2022-ttfs] Denève, S. et al. "Analyzing time-to-first-spike coding schemes: A
  theoretical approach." Frontiers in Neuroscience (2022). https://doi.org/10.3389/fnins.2022.971937.
  Peer-reviewed. (Also cited in this dossier for the SpiNNaker2 event-based-backpropagation TTFS
  and signed-payload claims, sourced from arXiv:2412.15021, "Event-based backpropagation on the
  neuromorphic platform SpiNNaker2," preprint.)
- [yoso-2020] "You Only Spike Once: Improving Energy-Efficient Deep SNN with Temporal Coding."
  arXiv:2006.09982 (2020). Preprint.
- [guo-2021-neuralcoding] Guo, W., Fouda, M. E., Eltawil, A. M., Salama, K. "Neural Coding in
  Spiking Neural Networks: A Comparative Study for Robust Neuromorphic Systems." Frontiers in
  Neuroscience (2021). https://doi.org/10.3389/fnins.2021.638474. Peer-reviewed.
- [kim-2018-weightedspikes] Kim, J., Kim, H., Huh, S., Lee, J., Choi, K. "Deep neural networks with
  weighted spikes." Neurocomputing 311:373-386 (2018).
  https://doi.org/10.1016/j.neucom.2018.05.087. Peer-reviewed.
- [swsc-2024] "Stepwise Weighted Spike Coding for Deep Spiking Neural Networks."
  arXiv:2408.17245 (2024). Preprint.
- [bsnn-2022] "BSNN: Towards faster and better conversion of artificial neural networks to spiking
  neural networks with bistable neurons." Frontiers in Neuroscience (2022).
  https://doi.org/10.3389/fnins.2022.991851. Peer-reviewed.
- [shrestha-2023-loihi2video] Shrestha, S. B., Timcheck, J., Frady, P., Campos-Macías, L., Davies,
  M. "Efficient Video and Audio Processing with Loihi 2." arXiv:2310.03251 (2023). Preprint.
- [lavadl-slayer-docs] Lava-DL SLAYER documentation.
  https://lava-nc.org/lava-lib-dl/slayer/slayer.html. Official documentation.
- [boeshertz-2024-alif] Boeshertz, G., Indiveri, G., Nair, M. V., Renner, A. "Accurate Mapping of
  RNNs on Neuromorphic Hardware with Adaptive Spiking Neurons." arXiv:2407.13534 (2024). Preprint.
- [thorpe-1996] Thorpe, S. J., Gautrais, J. "Rapid Visual Processing using Spike Asynchrony."
  NeurIPS 1996. Peer-reviewed (conference).
- [thorpe-spikebased] Thorpe, S., Delorme, A., Van Rullen, R. "Spike-based strategies for rapid
  processing." Neural Networks 14(6-7), 715-725 (2001). Author's preprint copy:
  https://sccn.ucsd.edu/~arno/mypapers/ThorpeSpiking_Neurons.pdf. Peer-reviewed.
- [cerco-spikenet-docs] CNRS CERCO, "What is order coding" (SpikeNet documentation).
  https://cerco.cnrs.fr/pagesp/arno/spikenet/order.html. Official documentation (research group).
- [furber-2004-nofm] Furber, S., Bainbridge, W. J., Cumpstey, J. M., Temple, S. "Sparse distributed
  memory using N-of-M codes." Neural Networks 17(10) (2004). Peer-reviewed.
- [akida-story-2016] BrainChip. "The Brainchip Story, 2016 to December 2020."
  https://akida.io/story. Vendor material (company history page); documents the September 2016
  acquisition of Spikenet Technology and Simon Thorpe's subsequent role on BrainChip's Scientific
  Advisory Board.
- [moyer-2020-semieng] Moyer, B. "Spiking Neural Networks: Research Projects or Commercial
  Products?" Semiconductor Engineering, May 18, 2020.
  https://semiengineering.com/spiking-neural-networks-research-projects-or-commercial-products/.
  Community commentary / trade press.
- [ziegler-2024-fastobjects] Ziegler, C., Vetter, J., Gossard, T., Tebbe, J., Otte, S., Zell, A.
  "Detection of Fast-Moving Objects with Neuromorphic Hardware." arXiv:2403.10677 (2024). Preprint;
  trained and deployed on physical AKD1000 hardware.
- [cnn2snn-source-inspection] Direct inspection of the `cnn2snn` 2.19.1 toolkit source,
  `cnn2snn/quantizeml/outputs.py`, function `set_output_v1_variables`, and `activations.py`,
  function `parse_relu_v1`. Repository state (primary source, hands-on inspection of the author's
  own local copy of the toolkit, reported in the a16 research audit; not an independently
  published artifact with its own URL).
- [frenkel-2019-morphic] Frenkel, C., Legat, J.-D., Bol, D. "MorphIC: A 65-nm 738k-Synapse/mm²
  Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online
  Learning." IEEE Transactions on Biomedical Circuits and Systems 13(5) (2019).
  https://doi.org/10.1109/TBCAS.2019.2928793. Peer-reviewed.
- [brainchip-akida-techbrief] BrainChip. "What is the Akida" technical brief.
  https://brainchip.com/wp-content/uploads/2020/03/BrainChip_tech-brief_What-is-Akida_v3-1.pdf.
  Vendor material.
- [openneuromorphic-akida] Open Neuromorphic. "A Look at Akida."
  https://open-neuromorphic.org/neuromorphic-computing/hardware/akida-brainchip/. Community
  commentary.
- [lunghi-2025-space-snn] Lunghi, P., Silvestrini, S., Dold, D., Meoni, G., Hadjiivanov, A.,
  Izzo, D. "Energy efficiency analysis of Spiking Neural Networks for space applications."
  arXiv:2505.11418 (2025). Preprint.
- [kim-2020-roc-scnn] Kim, D. et al. "Rank order coding based spiking convolutional neural network
  architecture with energy-efficient membrane voltage updates." Neurocomputing (2020).
  https://doi.org/10.1016/j.neucom.2020.06.107. Peer-reviewed.
- [ding-2021-optimalconv] Ding, J., Yu, Z., Tian, Y., Huang, T. "Optimal ANN-SNN Conversion for
  Fast and Accurate Inference in Deep Spiking Neural Networks." IJCAI 2021.
  https://doi.org/10.24963/ijcai.2021/321. Peer-reviewed (conference).


---

# 6 Hardware and Software Deployment Stack

This section is the survey's core. It compares platforms on the properties that gate
deployment, not on marketing specifications, then traces the software that connects a
trained network to each platform, and finally walks every documented route from a
trained network to silicon, stating what each route preserves, what it drops, and
whether a physical-silicon result has been published through it.

## 6.1 Neuromorphic Hardware Platforms

Table 6.1 compares thirteen platforms on the axes that determine whether a given
network, and specifically a rate-coded, integrate-and-fire, reset-by-subtraction
network, can be deployed on them at all. "Unknown" marks a property the underlying
research could not establish from any source; it is not a placeholder for "no."

| Platform | Time model | Neuron models (native) | Reset semantics | Spike payload | Weight precision | State precision | On-chip learning | Conv. operator coverage | Host interface | Official toolchain | Availability | Price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Loihi 1 | Synchronous algorithmic tick, barrier-synchronized over async NoC; wall-clock duration of a tick varies with traffic [Davies18] | Fixed hardware CUBA-LIF (two-stage current + leaky membrane) [Davies18] | Hard reset-to-zero native; soft reset only via a two-compartment compiler trick (doubles neuron/memory cost) [Rueckauer21-NxTF] | Binary by default; optional graded payload in a 32-bit message, rarely used [Davies21] | 1-9 bit signed, mixable per fan-out [Davies18] | Fixed 24 bytes/neuron [IntelBrief-L2] | Microcode learning engine: STDP, triplet STDP, RL via tags [Davies18] | NxTF: input, flatten, average, concat, dense, pool, conv (CUBA-LIF only) [Rueckauer21-NxTF] | Research Cloud VMs (SSH), 3 embedded x86 Lakemont cores on-die [Davies18] | NxSDK/NxTF, Keras-derived, superseded [Rueckauer21-NxTF] | Not commercially sold; INRC membership required, cloud or loan access [IntelINRC-Access] | Not publicly listed |
| Loihi 2 | Same barrier-synchronized algorithmic tick; pipelined or fall-through execution modes [Orchard21-Loihi2Sig] | Fully programmable microcode neural engine: CUBA-LIF, Resonate-and-Fire, Izhikevich, sigma-delta [IntelBrief-L2] | Hard reset-to-zero is the documented reference behavior (`PyLifModel`, "Loihi-1 compatible"); no soft-reset primitive documented in Lava or NetX [LavaDocs-Overview] | Graded, 32-bit architectural maximum, individual projects configure 8/16/24-bit [IntelBrief-L2] | 8-bit default, extendable via chained synapses [IntelBrief-L2] | Variable, 0-4096 bytes/neuron, model-dependent [IntelBrief-L2] | Three-factor learning validated in CPU simulation; on-chip execution not confirmed on physical silicon in any source found [Davies18] | `lava_exchange`/NetX HDF5 schema: input, flatten, average, concat, dense, pool, conv (CUBA-LIF) [LavaDL-NetX-Docs] | Research Cloud (Oheo Gulch single-chip, Kapoho Point 8-chip stackable) [Davies21] | Lava/Lava-DL/NetX, **archived by Intel 13 May 2026** [LavaGH-Archive] | INRC-gated; on-site purchase possible for members, evaluated by an Intel Labs checklist [IntelINRC-Access] | Not publicly listed |
| SpiNNaker 1 | Discrete timer interrupt, 1 ms/timestep default (software convention, not a hardware floor); GALS [Furber12-SpiNNOverview] | Software-defined in C (commonly LIF, CuBa-LIF, Izhikevich) [Furber12-SpiNNOverview] | Whatever the C model implements; not fixed by the chip | Binary AER, 40/72-bit packets, no delivery guarantee [Furber12-SpiNNOverview] | Fixed-point only (no FPU), e.g. Q6.16 [Furber12-SpiNNOverview] | Software-defined fixed-point | STDP and structural plasticity plugins [Furber12-SpiNNOverview] | SNN Toolbox `spiNNaker_target_sim.py` via PyNN: Conv2D, DepthwiseConv2D, Conv1D, dense, pooling; ~256 neurons/core memory limit [SNNToolbox-Docs] | EBRAINS Neuromorphic Computing Platform, queued jobs [EBRAINS-Access] | sPyNNaker/SpiNNTools (PyNN) [Rhodes18-sPyNNaker] | Free EBRAINS research/evaluation access; not a commercial product [EBRAINS-Access] | Free (evaluation/basic research) |
| SpiNNaker 2 | Same 1 ms convention; per-PE DVFS; dense MAC array runs ANN layers dense/synchronously alongside event-driven SNN layers [Scholze26-SpiNN2Chip] | Software-defined LIF/CuBa-LIF (32-bit float dynamics) plus hybrid dense-layer execution on the MAC array [Arfa25-SpiNN2NIR] | Both reset-by-subtraction and reset-to-zero supported in the hardware/software stack, per the NIR paper's own SpiNNaker2 methods; the formal NIR primitive spec itself does not expose this [Pedersen24-NIR] | Binary AER (same fabric lineage as SpiNNaker 1) | 8-bit signed synapse weights (deployed config) [Arfa25-SpiNN2NIR] | 32-bit float neuron state [Arfa25-SpiNN2NIR] | Unknown beyond inherited plasticity support | py-spinnaker2 NIR importer: Conv1d, Conv2d, Flatten, Affine, Linear, CuBaLIF, IF, LIF, SumPool2d (import only, no NIR export) [Pedersen24-NIR] | SpiNNcloud commercial racks and standalone boards | py-spinnaker2 (PyNN-inspired) plus NIR import [Pedersen24-NIR] | Commercially available (SpiNNcloud Systems), on-prem and cloud [SpiNNcloud24-PR] | Not publicly listed (enterprise sales) |
| Speck / DYNAP-CNN | Fully asynchronous, no global clock; optional slow clock on Speck2e+ for leak/DVS-filter/readout only, not the conv pipeline [Richter23-SpeckASIC] | Nonleaky IF by default; leak optional via bias + slow clock [Sinabs-FromTorch] | Reset-by-subtraction (`MembraneSubtract`) is the documented default [Sinabs-FromTorch] | Binary AER events, addressed by layer/x/y/feature/timestamp [SynSense-SpeckOverview] | 8-bit [SynSense-SpeckDatasheet] | 16-bit membrane [SynSense-SpeckDatasheet] | None documented | Conv2d (kernel up to 16x16) to IF to SumPool per core only; no native BatchNorm; `Linear` auto-converted to Conv2d; `AvgPool2d` rewritten to `SumPool2d`; 9 cores, fan-out 2 [Sinabs-Basics] | samna (Python/C++), USB 3.1 [SynSense-SpeckDatasheet] | Sinabs `from_model` to `DynapcnnNetwork` to samna [Sinabs-Basics] | Commercially purchasable, no gatekeeping [Sinabs-Basics] | Not publicly posted; Demo Kit presold near $199 [A18-Research] |
| Xylo | Synchronous, global timestep `dt`, master clock 50-100 MHz [Rockpool-XyloOverview] | CUBA-LIF, current-based, per-neuron/synapse time constants [Rockpool-XyloOverview] | Subtractive, a fixed hardware property (not software-switchable) [Rockpool-XyloOverview] | Binary events, but up to 31 output spikes/neuron/timestep [Rockpool-XyloOverview] | 8-bit [Rockpool-XyloOverview] | 16-bit [Rockpool-XyloOverview] | Unknown (not documented as a first-class feature) | Audio/IMU CuBa-LIF network, up to ~1000 hidden neurons (Audio 2) [Rockpool-XyloOverview] | samna, SPI [Rockpool-XyloA3Tutorial] | Rockpool: `mapper()`, `quantize_methods`, `config_from_specification()`, `XyloSamna`/`XyloSim`/`XyloMonitor` [Rockpool-XyloDeploy] | Commercially purchasable dev kits | Pricing on application; not public |
| BrainScaleS-2 | Physical analog time, 1000x accelerated vs. biological; PPU-orchestrated batched frames, explicit ~100-500 ns stimulus/readout windows [Pehle22-BSS2] | Analog LIF/AdEx circuit, individually calibrated [Pehle22-BSS2] | Reset-by-conductance to a reset potential with finite refractory period (analog, not the digital hard/soft binary) [Pehle22-BSS2] | Binary spike events (digital read-out); separate non-spiking "hagen" MAC mode exists on the same silicon [Weis20-ANNMode] | 6-bit signed synaptic weight [Weis20-hxtorch] | 8-bit ADC digitization of the analog membrane [Weis20-hxtorch] | Hybrid plasticity: STDP, R-STDP, homeostatic, structural, via PPU + CADC [Pehle22-BSS2] | hxtorch: `matmul`, `conv{1,2,3}d`, `Linear`, `ConvertingReLU` (ANN/hagen mode); hxtorch.snn: LIF/LI (AdEx not yet supported as of the cited paper) [Weis20-hxtorch][Pehle22-hxtorchsnn] | EBRAINS Jupyter/PyNN, hxtorch Python API [EBRAINS-BSS] | hxtorch / hxtorch.snn / `pynn_brainscales` [Pehle22-BSS2] | Free remote EBRAINS access; not purchasable [EBRAINS-BSS] | Free (evaluation/basic research) |
| TrueNorth | Global 1 kHz synchronization "tick," full network evaluated once per tick [Akopyan15-TrueNorth] | 23-parameter configurable augmented IF, reproduces all 20 Izhikevich classes via 1-3 instances [Cassidy13-TNNeuron] | Three configurable modes: hard reset to Rj, linear/residual-preserving reset, non-reset stochastic [Cassidy13-TNNeuron] | 1-bit binary only [Akopyan15-TrueNorth] | Trinary {-1,0,+1} via a 4-entry axon-type LUT construction for Eedn; general LUT supports signed [-255,255] [Esser16-Eedn] | Not documented beyond the configurable-parameter neuron | None (inference only) [Esser16-Eedn] | Eedn: trinary-weight backprop-trained CNN, block-wise crossbar-constrained convolution [Esser16-Eedn] | NS1e/NS16e development boards [Sawada16-TNEcosystem] | Eedn training + Corelet/CPE/Compass simulator [Esser16-Eedn] | Discontinued; distributed only to >30 research organizations during the DARPA SyNAPSE era [Sawada16-TNEcosystem] | N/A, discontinued |
| Tianjic / Lynxi | Timestep-driven, the timestep loop sits outside the network (unlike GPU-style frameworks); hybrid ANN (cycle-refresh) / SNN (event-driven) FCores on the same silicon [BIDL-GitHub] | LIF / LIF+ (BIDL default), user-defined neuron classes possible [BIDL-GitHub] | Unknown | Unknown | Mixed precision, e.g. INT8/FP16 on KA200 [Lynxi-KA200] | Unknown | Unknown, not documented | BIDL: ConvLIF/ConvLIAF spatiotemporal layers interleaved with Conv/BN/pooling ANN layers, VGG-/ResNet-/Transformer-/YOLOv5-like topologies; batch size 1 only on-chip [BIDL-PMC] | Lyngor compiler / LynSDK [Lynxi-HP300] | BIDL, PyTorch-based [BIDL-GitHub] | Not available outside mainland China in any source found [BIDL-GitHub] | Unknown |
| Akida (AKD1000/1500) | No exposed multi-timestep horizon for the standard converted-CNN path; a single feedforward pass. Some layer types (`BufferTempConv`) carry an internal buffer for genuinely sequential data, a distinct notion of time [Ziegler24-FastObjects][CNN2SNN-Source] | Integrate-and-single-fire, no leak/decay on the standard path [Ziegler24-FastObjects] | Not reset-by-subtraction; a static per-neuron comparator threshold, computed once at conversion, absorbs the BN scale/shift and a rounding offset [CNN2SNN-Source] | Not necessarily binary; events "can have a value" except the mandatory 1-bit Edge-Learning layer [BrainChip-AkidaUserGuide] | 1/2/4/8-bit, layer- and version-dependent [BrainChip-AkidaUserGuide] | N/A on the standard path; no persistent multi-step membrane state [CNN2SNN-Source] | "Edge Learning," last `FullyConnected` layer only, 1-bit weights/input, Hebbian-style `AkidaUnsupervised` rule, Akida 1.0 only [BrainChip-AkidaUserGuide] | Akida 1.0: InputConv/Conv/SeparableConv/Dense, feed-forward only, strict ordering/padding/stride rules; Akida 2.0 adds Attention/ViT blocks, Add/Concatenate, BufferTempConv [BrainChip-AkidaUserGuide] | PCIe, USB 3.0, SPI, I3C, I2S, UART, JTAG (AKD1000/1500) [BrainChip-AKD1000Brief] | MetaTF: QuantizeML to CNN2SNN to Akida runtime [BrainChip-CNN2SNNDocs] | Commercially purchasable dev boards, no gatekeeping [A18-Research] | AKD1000 PCIe $289, RPi4 kit $995, RPi5 kit $1,495; AKD1500 5-pack $199.99 [BrainChip-AKD1000Brief][BrainChip-AKD1500Brief] |
| Innatera (T1/Pulsar) | Unknown in detail; mixed analog SNN engine + digital SNN engine on the same die [Innatera-Pulsar-PR] | Proprietary analog/digital SNN engine; IF-based encoder in the Talamo SDK [Innatera-Talamo] | Unknown | Unknown | Unknown (16K-parameter analog engine, 49K-parameter digital engine capacity reported, not bit-widths) [Innatera-Pulsar-PR] | Unknown | Unknown | Talamo SDK compiles PyTorch-defined SNNs directly onto device [Innatera-Talamo] | QSPI, I2C, UART, JTAG, GPIO, AER; on-die CV32E40P RISC-V host [Innatera-EETimes] | Talamo SDK [Innatera-Talamo] | Commercially available, Pulsar in production since 2Q25 [Innatera-Pulsar-PR] | Not publicly posted |
| Academic ASICs (ODIN, ReckOn, MorphIC, μBrain) | Mostly event-driven/clockless (ODIN, μBrain); design center is online learning, not deep-CNN throughput [Frenkel19-ODIN][muBrain21] | LIF or Izhikevich-configurable (ODIN); LIF (ReckOn, MorphIC); ReLU-to-accumulator-wraparound (μBrain) [Frenkel19-ODIN][FrenkelIndiveri22-ReckOn][Frenkel19-MorphIC][muBrain21] | Not standardized across the class; none of ODIN, ReckOn, or MorphIC documents classical reset-by-subtraction explicitly [Frenkel19-ODIN][FrenkelIndiveri22-ReckOn][Frenkel19-MorphIC] | Binary | 4-bit synapse (ODIN); 8-bit (ReckOn); 1-bit (MorphIC) [Frenkel19-ODIN][FrenkelIndiveri22-ReckOn][Frenkel19-MorphIC] | Not consistently documented | SDSP (ODIN), e-prop-derived (ReckOn), stochastic S-SDSP (MorphIC): on-chip learning is the design center for this whole class [Frenkel19-ODIN][FrenkelIndiveri22-ReckOn][Frenkel19-MorphIC] | Small fully-connected/recurrent research-scale networks, not a deep-CNN operator set | Research prototype boards, not standardized | Per-project open-source HDL (github.com/ChFrenkel/*), no unified toolchain | Not commercially available; a handful of fabricated research dies | N/A, not sold |
| FPGA (SyncNN, Spiker+, FireFly v2, Cerebron) | Synchronous, clock-driven at the accelerator's own clock (100-600 MHz depending on design); SyncNN reformulates the T-loop to run only at the input-encoding layer [Panchapakesan22-SyncNN] | IF (SyncNN, Cerebron via SNN Toolbox); IF/1st-/2nd-order LIF (Spiker+); generic LIF (FireFly) [Panchapakesan22-SyncNN][Carpegna24-SpikerPlus][Li24-FireFlyv2] | Not standardized; SyncNN implements explicit reset-by-subtraction; Spiker+ is the only design offering user-selectable hard or reset-by-subtraction [Panchapakesan22-SyncNN][Carpegna24-SpikerPlus] | Binary | Project-configurable, typically 4/8/16-bit | Project-configurable | Mostly inference-only; one exception (Spiker-LL) adds on-device local learning | Project-dependent; Cerebron is explicitly built around SNN Toolbox conversion (Conv/pool via Rueckauer-style mapping) [ChenGaoFu22-Cerebron] | Xilinx SoC boards (ZCU102/104, Artix-7, UltraScale+), standard FPGA host tooling | None unified; each design is its own open-source RTL/HLS project (Vitis HLS/SDSoC, Vivado) | Purchasable general-purpose FPGA dev boards; no packaged commercial SNN product | Standard FPGA board pricing, not SNN-specific |

### Per-platform notes

**Loihi 1.** The chip's fixed CUBA-LIF datapath hard-resets to zero; QCFS-style soft
reset is not a hardware primitive but a compiler construction, the two-compartment
trick, that consumes one extra compartment per neuron and was explicitly flagged by
the NxTF authors as a feature they would prefer the hardware to provide directly
[Rueckauer21-NxTF]. Loihi 1 is the platform with the clearest published physical-silicon
result for a rate-coded, reset-by-subtraction conversion: NxTF-compiled CNNs reached
0.79% error on MNIST and 8.52% error on CIFAR-10, both measured for accuracy, energy,
and latency on physical chips [Rueckauer21-NxTF]. It is not commercially available;
access requires INRC membership and is mediated through a cloud of shared VMs
[IntelINRC-Access].

**Loihi 2.** The architectural headline is a microcode-programmable neural engine that
replaces Loihi 1's fixed datapath, enabling Resonate-and-Fire, Izhikevich, and
sigma-delta neuron models alongside CUBA-LIF, and generalizing binary spikes into a
32-bit graded payload [IntelBrief-L2]. No source located documents a soft-reset
primitive for Loihi 2; the reference `PyLifModel` process explicitly hard-resets to
zero and is annotated "Loihi-1 compatible" [LavaDocs-Overview]. The chip's own
architects state directly that classic rate-coded conversion is a poor fit for Loihi 2,
citing long latencies at scale, and that this is the stated rationale behind Loihi 2's
shift toward graded and sigma-delta coding for deep-learning workloads [Davies21]. Intel
archived the entire Lava software stack on 13 May 2026, stating a next-generation SDK is
in development [LavaGH-Archive]; the only published conversion result on physical Loihi
2 abandons rate coding for sigma-delta coding specifically because rate coding
"required many simulation time steps per inference, which degraded efficiency"
[Brehove26-SigmaDelta].

**SpiNNaker 1.** A general-purpose, software-defined many-core system rather than a
fixed-function neuromorphic ASIC: every neuron/synapse model is compiled C code, so
reset semantics and precision are whatever the user's model implements, not a hardware
constant [Furber12-SpiNNOverview]. A converted, rate-coded LeNet reached 98.20% accuracy
on physical SpiNNaker-103 hardware, the clearest CNN-conversion result found on this
platform, though no CIFAR-10-scale or larger converted CNN has been measured on
physical SpiNNaker 1 or 2 silicon in any source located [PatinoSaucedo20-SpiNNConv].
Access is free through EBRAINS for research and evaluation [EBRAINS-Access].

**SpiNNaker 2.** Adds a dense 8/16-bit MAC array alongside the SpiNNaker-lineage
event-driven core, explicitly targeting hybrid ANN/SNN/rule-based execution on the same
processing element [Scholze26-SpiNN2Chip]. Its NIR importer is the only backend in this
survey documented to support both reset-by-subtraction and reset-to-zero as software
options, a hardware/software capability that sits outside NIR's own formal primitive
specification [Pedersen24-NIR]. The one VGG-16/ResNet-50-scale SpiNNaker2 deployment
result found in the literature is a pre-silicon timing simulation, explicitly stated
by its own authors ("the SpiNNaker2 chip is not yet available"), not a measurement on
fabricated hardware [Kelber20-SpiNN2Map]. SpiNNcloud Systems now sells SpiNNaker2 as a
commercial on-prem or cloud-accessed supercomputer platform [SpiNNcloud24-PR].

**Speck / DYNAP-CNN.** Fully asynchronous, clockless convolutional compute: nine
fixed-order Conv-to-IF-to-SumPool cores route events with a measured end-to-end latency
of 3.36 microseconds across all nine layers, contrasted explicitly by the chip's authors
against clocked chips (Loihi, TrueNorth), which "architecturally introduce a latency of
one timestep on event generation in each layer" [Richter23-SpeckASIC]. Reset-by-subtraction
is the software and hardware default, not an option a user must opt into
[Sinabs-FromTorch]. The chip has no native BatchNorm support and no native
`AvgPool2d`; both are handled by architectural rewriting at conversion time, not by a
transparent mapping [Sinabs-Basics]. Hardware is commercially purchasable with no
research-membership gate, distinguishing it sharply from the INRC- and
EBRAINS-gated platforms above [Sinabs-Basics].

**Xylo.** A genuinely synchronous, globally clocked digital SNN core for audio/IMU
workloads, the opposite time model from Speck: "Synchronous time-stepped architecture
with a global time-step dt" is a hardware property, not a software convention
[Rockpool-XyloOverview]. Reset-by-subtraction is likewise a fixed hardware property.
Deployment is via Rockpool, a separate SynSense toolchain from the Sinabs path that
targets Speck [Rockpool-XyloDeploy]. Xylo neurons can emit up to 31 spikes per neuron
per timestep, a materially different regime from the single-spike-per-step assumption
most conversion theory makes [Rockpool-XyloOverview].

**BrainScaleS-2.** A physical analog emulation, not a digital simulator: circuit time
constants are genuinely 1000x faster than the biological values they represent, and
experiments run as PPU-orchestrated batched frames with explicit, digitally controlled
stimulus and readout windows [Pehle22-BSS2]. A converted, rate-coded ANN-to-SNN pipeline
has been demonstrated on the wafer-scale predecessor system, recovering from a
72%-to-95% accuracy collapse only after hardware-in-the-loop retraining, for a small
digit-classification network, not a deep CNN [Schmitt17-HITL]. The CNN-scale results on
BrainScaleS-2 itself use a distinct, non-spiking "hagen" MAC mode rather than
multi-timestep rate-coded IF accumulation [Weis20-ANNMode]. Analog fixed-pattern
mismatch and trial-to-trial variability are irreducible even after calibration; every
source in this literature reports hardware-in-the-loop training, not an assumption of
exact IF correspondence, as the practical countermeasure [Pehle22-BSS2]. Access is free
through EBRAINS, not a commercial purchase [EBRAINS-BSS].

**TrueNorth.** Discontinued since the mid-2010s DARPA SyNAPSE program and never
commercially sold [Sawada16-TNEcosystem]. Its Eedn training methodology is not
multi-timestep temporal rate coding: activation magnitude is represented spatially, by
the aggregate spike count across a population of redundant trinary-weighted neuron
copies evaluated once per 1 kHz tick, not by accumulation over repeated ticks
[Esser16-Eedn]. TrueNorth should not be cited as a hardware validation of the temporal
rate-coded, reset-by-subtraction IF conversion this thesis builds on. IBM's successor
chip, NorthPole, is a purely digital, non-spiking, low-precision inference accelerator
with no membrane dynamics; it is architecturally descended from TrueNorth's
memory-locality principles but is out of scope as a spiking substrate.

**Tianjic / Lynxi.** Designed explicitly to fuse ANN and SNN execution on shared
silicon within a single network, with some cores relaying full-precision membrane
potentials between compartments rather than binary spikes [Pei19-Tianjic]. Lynxi, the
commercial spinout, ships the BIDL PyTorch-based framework and states plainly in its own
documentation that "most brain-inspired chips operate in a timestep driven manner,
where a timestep iteration is located outside the neural network," confirming a global,
not per-layer, time model [BIDL-GitHub]. No evidence was found of Lynxi hardware being
sold, distributed, or benchmarked outside mainland China [BIDL-GitHub].

**Akida.** Treated in full critical detail below.

**Innatera.** A commercially shipping mixed analog/digital SNN microcontroller family
(T1, Pulsar) aimed at always-on sensor edge tasks, sub-millisecond wake triggers at
microwatt power [Innatera-Pulsar-PR]. No independent, peer-reviewed benchmark of either
chip was located; every quantitative claim retrieved (100x latency, 500x energy
reduction) is vendor-sourced [Innatera-Pulsar-PR]. Reset semantics, spike payload, and
weight precision are not documented in any source found.

**Academic ASICs.** ODIN, ReckOn, and MorphIC are research-fabricated single-digit-count
prototype dies whose design center is on-chip online learning (SDSP, e-prop, stochastic
SDSP), not deep-CNN throughput or reset-semantics fidelity to the conversion literature
[Frenkel19-ODIN][FrenkelIndiveri22-ReckOn][Frenkel19-MorphIC]. MorphIC provides the
clearest same-silicon, same-task energy comparison in this survey: rate coding measured
205 microjoules per MNIST classification versus 21.8 microjoules for rank-order coding
on the identical chip, a roughly tenfold difference attributable to the coding scheme
alone [Frenkel19-MorphIC]. SENECA, a RISC-V-based digital neuromorphic processor from
imec, has not been fabricated as of any source found; all reported efficiency figures
are synthesis and simulation results [Tang23-SENECA][Shidqi22-SENECAThesis].

**FPGA.** No unified toolchain exists; each accelerator surveyed is an independent
open-source RTL or HLS project. SyncNN is the design closest to this thesis's
assumptions, explicitly implementing the IF model with reset-by-subtraction and Poisson
rate encoding, measured across three physical Xilinx boards [Panchapakesan22-SyncNN].
Spiker+ is the only accelerator surveyed offering reset-by-subtraction as a named,
user-selectable configuration option alongside hard reset [Carpegna24-SpikerPlus].
Cerebron is the clearest FPGA accelerator explicitly built around the SNN Toolbox
conversion pipeline [ChenGaoFu22-Cerebron]. All measured results in this row are
physical-board measurements (E1), not synthesis estimates alone.

### Akida, examined critically

Akida gets a full platform entry above and a separate critical treatment here because
its marketing framing ("neuromorphic," "spiking neural processor") and its actual
converted-CNN execution mechanism diverge sharply, and because that divergence is
directly relevant to a thesis built on the ReLU-to-IF, rate-coded conversion
correspondence.

The standard deployment path, QuantizeML to CNN2SNN, is quantization-aware training
followed by a batch-norm fold, not a rate-coding conversion. QuantizeML performs
uniform, symmetric, zero-centered integer quantization of weights and activations; it
contains no weight-normalization pass calibrated to a target firing rate over a chosen
horizon `T`, and no iterative "spike count over T approximates the ReLU" simulation
[BrainChip-QuantizeMLDocs]. CNN2SNN's own documentation states that BatchNorm scale and
shift, along with the quantized-activation math, "are never performed during inference"
as separate floating-point operations; they are folded once, at conversion time, into
the neuron's firing threshold and other static parameters
[BrainChip-CNN2SNNDocs]. Direct inspection of the CNN2SNN 2.19.1 source confirms the
mechanism at the code level: the Akida 1.0 activation output is computed as
`y = x / act_step`, where `act_step` derives from the QuantizeML output quantizer's
scale, and the threshold itself is offset by a rounded half-step before division, a
rounding-to-nearest-bin correction folded into a static comparator, not an accumulator
integrating over a simulation horizon [CNN2SNN-Source]. There is no membrane potential
carried across timesteps on this path, and no user-exposed `T`.

Two independent papers, trained and deployed on real AKD1000 hardware, describe the
same collapse in near-identical language. A robotics group building a fast-moving-object
detector states that Akida "squashes the rate-code approximation of the ReLU into one
time step, where it is then represented by a step-wise quantized ReLU," and that this
representation "allows for processing in a single time step" [Ziegler24-FastObjects]. A
space-applications benchmarking paper independently concludes that "the AKD1000 does
not support leaky neurons... the implementation suggest[s] that the converted spiking
model reduces the computation to a single time step" [Lunghi25-SpaceSNN]. Both papers
were checked and corroborated against the CNN2SNN source directly; the empirical claim
and the mechanism agree.

This is not simply marketing dressed up as neuromorphic computing. Akida's lineage is
genuine: BrainChip acquired Spikenet Technology in 2016, and Simon Thorpe, the
originator of rank order coding, has since sat on BrainChip's Scientific Advisory Board
[Thorpe98-RankOrder]. Rank order coding is a real, peer-reviewed temporal code in which
a neuron population is maximally activated when its inputs arrive in the order of their
synaptic weights, via a shunting-inhibition mechanism, with at most one spike per
neuron carrying the information [ThorpeGautrais96-SpikeAsync]. A trade-press technical
analysis independently corroborates the pivot: "BrainChip started with rate coding, but
decided that wasn't commercially viable. Instead, it uses rank coding" [Moyer20-SemiEng].
Akida's input-encoding stage is described by multiple independent, non-BrainChip
sources as rank-order-coded. However, no source examined in this research, including
direct inspection of the CNN2SNN output and activation code, shows evidence of an
order-sensitive, shunting-inhibition mechanism operating inside the hidden layers of a
converted CNN on Akida hardware. The threshold mechanism visible in the source is a
magnitude comparator, order-agnostic within a layer: it does not matter which input
arrived first, only whether the weighted sum crosses a threshold [CNN2SNN-Source]. The
honest summary is that Akida's lineage and its input-encoding stage draw on genuine
rank-order-coding research, but the converted-CNN inference path that essentially all
published Akida benchmarks use is not shown, by any source located, to implement rank
order coding's defining order-sensitivity inside hidden layers.

## 6.2 Training and Simulation Frameworks

Table 6.2 compares thirteen frameworks on role, native neuron models and their
*default* reset behavior (the axis the conversion literature is most sensitive to),
the time model each assumes, documented hardware export paths, and current maintenance
status.

| Framework | Role | Neuron models / default reset | Time model | Documented export paths | Maintenance (2026) |
|---|---|---|---|---|---|
| SpikingJelly | Full-stack PyTorch SNN toolkit: preprocessing, training, `ann2snn` conversion, hardware export [SJ23-SciAdv] | `IFNode`/`LIFNode`; constructor **defaults to hard reset** (`v_reset=0.0`, with `v_threshold=1.0`); soft reset requires explicit `v_reset=None`, which is what `ann2snn`'s conversion recipes set [SJ-NeuronDocs][SJ-ANN2SNNDocs] | Single network-wide `T`; `step_mode` (`'s'`/`'m'`) toggles single- vs. multi-step processing of one shared scalar, not per-layer T [SJ23-SciAdv] | `lava_exchange` (to Lava/Loihi, IF/LIF only, hard reset only), `nir_exchange`, a Lynxi tutorial [SJ-LavaExchangeDocs] | Actively maintained; last push within one day of this research; `ann2snn` module substantially rewritten in 2026 [SJ-GitHub] |
| snnTorch | PyTorch-native SNN training library [Eshraghian23-snnTorch] | `snn.Leaky`; `reset_mechanism='subtract'` is the literal default [snnTorch-Docs] | Single shared `num_steps`, user-written outer loop [snnTorch-Docs] | No official first-party hardware export documented in this pass; NIR export exists per the snnTorch codebase itself (`export_nir`) [snnTorch-PR388] | Actively documented, versioned docs live |
| Norse | PyTorch functional/module SNN library | `LIFParameters`; `v_reset=tensor(0.)`, i.e. **hard reset is the only reset mechanism exposed** in the documented `LIF`/`LIFCell` classes [Norse-Docs] | Single shared sequence length / `dt`, handled internally by `LIFCell`/`LIF` wrappers [Norse-Docs] | Exports to NIR (`norse.to_nir`); no first-party direct-to-chip path found | Actively documented (v1.0.0 API reference live) |
| Lava-DL | Intel's deep-learning library within Lava: `slayer` (native training), `bootstrap` (rate-coded training), `netx` (HDF5 inference deployment) [LavaDL-NetX-Docs] | SLAYER 2.0: CUBA, Resonator, Adaptive Integrator families; the reference `PyLifModel` process **hard-resets to zero**, no soft-reset variant documented [LavaDocs-Overview] | `net.run(condition=RunSteps(total_run_time), ...)`, one shared run duration for the whole compiled Process network [LavaDL-NetX-Docs] | HDF5 to `netx.hdf5.Network` to Lava Process graph, runnable on CPU simulation or, for INRC members, physical Loihi 2 [LavaDL-NetX-Docs] | **Archived by Intel, 13 May 2026**; frozen, legacy [LavaGH-Archive] |
| Sinabs | SynSense's PyTorch SNN library with a first-party path to Speck [Sinabs-FromTorch] | `sinabs.layers.IAF`; `reset_fn` configurable, **`MembraneSubtract()` (soft/subtractive) is the constructor default** [Sinabs-FromTorch] | Standard PyTorch forward over a batched, single shared time axis [Sinabs-Basics] | `from_model()` to `DynapcnnNetwork` to samna to Speck, fully worked and measured on physical silicon [Sinabs-Basics] | Active, versioned docs |
| Rockpool | SynSense's second SNN library, targeting Xylo | Digital LIF with bit-shift-approximated synapses; **subtractive reset is a fixed hardware property**, documented as the default [Rockpool-XyloOverview] | Synchronous, global `dt`, a hardware-level guarantee, not a software convention [Rockpool-XyloOverview] | `mapper()` to `quantize_methods` to `config_from_specification()` to `XyloSamna`/`XyloMonitor`, measured on physical Xylo HDKs [Rockpool-XyloDeploy] | Active, multiple point releases live |
| Brian2 | Neuroscience-first differential-equation simulator, Python front end, C++ code generation | Whatever equations the user defines; no default imposed by the framework itself | User-defined, continuous or discretized per model | Reachable as an SNN Toolbox output backend for converted deep networks; GPU acceleration only via the separate Brian2GeNN bridge [SNNToolbox-Docs] | Active as a general simulator; no native deep-CNN or hardware path |
| NEST | Large-scale, densely-connected point-neuron simulator, in continuous development since the 1990s | User-defined per model; no CNN-scale demonstration found in any source reviewed | User-defined | Reachable as a PyNN backend for SNN Toolbox-converted networks, not natively | Active as a general simulator; no native CNN or hardware path |
| GeNN (via mlGeNN) | GPU code-generation framework for spiking dynamics; mlGeNN adds explicit Keras-to-SNN CNN conversion [Turner22-mlGeNN] | Conversion-recipe-dependent; the companion mlGeNN paper demonstrates VGG-16 and ResNet-34/20 converted at CIFAR-10/ImageNet scale (70.2% vs. 70.3% ANN baseline on ImageNet) [Turner22-mlGeNN] | GPU/CPU simulation only, one shared `T` | None to physical neuromorphic silicon; explicitly out of scope by the authors' own framing [Turner22-mlGeNN] | Active |
| BindsNET | PyTorch-tensor-based SNN library for STDP/RL research, reuses `torch.nn.functional` ops [BindsNET18] | Documents an ANN-to-SNN conversion path (Diehl et al. 2015 style) from PyTorch/ONNX; primary design center is not deep-CNN-scale inference [BindsNET18] | Single shared `T`; comparative benchmarking found its performance scales as the ANN's cost multiplied by T, not sparsity-exploiting [Turner22-mlGeNN] | None to physical neuromorphic silicon found | Active |
| PyNN | Simulator-independent API: write once, run on NEURON, NEST, Brian, or certain neuromorphic hardware [PyNN-Docs] | Inherited entirely from the executing backend; PyNN itself does not define reset semantics [PyNN-Docs] | Inherited from backend | **Two physical hardware backends documented**: `pyNN.spiNNaker` (SpiNNaker) and `pynn_brainscales.brainscales2` (BrainScaleS), both run as live, queued jobs on physical hardware via EBRAINS [HBP-Guidebook][PynnBSS2-Docs] | Active, foundational layer for both platforms |
| NengoDL | Trains SNN-compatible models with a differentiable approximation of spiking neurons during training, actual spiking neurons at inference [NengoDL-Rasmussen19] | Depends on the substituted spiking neuron (commonly LIF) | Single shared simulation length | Provides a `Converter` for ReLU-to-spiking conversion; NengoLoihi backend compiles to physical Loihi (E1 results: CIFAR-10 tutorial-scale, 38x energy advantage on a keyword-spotting network, a 7-DOF robot-arm controller) [NengoLoihi-Docs][ABR-PressRelease][DeWolf23-NengoArm] | Active |
| spyx | Compact JAX/Flax NNX SNN library | LIF, ALIF, CuBaLIF, LI, IF, and recurrent variants [Spyx-Docs] | Single shared time index (JAX-vectorized) | Exports via NIR; no chip-specific worked deployment example found in this pass | Actively developed (recent Flax NNX rewrite) |

**Confirmed finding: no framework in this survey can express a per-layer timestep
horizon within a single forward pass.** In every case, execution is driven by exactly
one network-wide time index. SpikingJelly's `step_mode` is set per module, but the
value of `T` being iterated remains one shared scalar for the whole network
[SJ23-SciAdv]. snnTorch's neuron classes process one timestep per call inside a single
outer Python loop shared by every layer [snnTorch-Docs]. Norse's `LIF`/`LIFRecurrent`
wrap a cell "in time" over one sequence length shared by composition across the
network [Norse-Docs]. Lava runs the whole compiled Process network for a single
`total_run_time` under the Loihi synchronization protocol [LavaDL-NetX-Docs]. On Xylo
this is not merely a software convention but a physical hardware guarantee: the chip is
architecturally "a synchronous time-stepped architecture with a global time-step dt,"
which makes per-layer `T` physically impossible on that silicon as documented
[Rockpool-XyloOverview]. SpikingJelly's own paper states the underlying reason
directly: because a stateful spiking layer's output at time `t` depends on hidden state
carried from `t-1`, "the for-loop concerning time steps is inevitable," and every
framework surveyed builds exactly one such loop per network, never one per layer
[SJ23-SciAdv].

## 6.3 Export, Interchange, and Compilation

Table 6.3 records what each converter or compiler consumes, emits, and drops.

| Tool | Consumes | Emits | Drops |
|---|---|---|---|
| SNN Toolbox | Keras/TensorFlow, PyTorch, Lasagne, Caffe models [Rueckauer17-SNNTB] | INIsim (Keras software sim, recommended path), pyNN (NEST/Brian/NEURON), Brian2, MegaSim, SpiNNaker (via SpyNNaker), Loihi (via NxTF) [SNNToolbox-Docs] | Nothing on the reset axis: **reset-by-subtraction is the default and the paper's own recommended mechanism** [Rueckauer17-SNNTB]. Dormant since March 2021 (last release) / August 2022 (last patch commit); its Loihi and SpiNNaker backends depend on external SDKs that have themselves moved on [SNNToolbox-GitHub] |
| NIR | Nine simulators, five hardware platforms on the write side (hxtorch/jaxsnn, Nengo, Norse, Rockpool, Sinabs, snnTorch, Spyx) [Pedersen24-NIR] | A graph of 17 typed primitives, including Integrate-and-Fire and LIF [NIR-Primitives] | **Reset by subtraction.** The formal primitive spec defines only reset to a fixed target value `v_reset` for I&F and LIF; no subtract-reset primitive exists in the published spec [NIR-Primitives]. The paper's own discussion states plainly the format "excludes... adaptive threshold mechanisms, gating, resonate-and-fire, and multicompartmental neuron models," and hardware backends are permitted to simply ignore unsupported nodes rather than approximate them [Pedersen24-NIR][NIR-Porting] |
| NxTF | Keras-derived model, specifically via an SNN-Toolbox bridge [Rueckauer21-NxTF] | Compiled register-level NxCore configuration for physical Loihi 1 [Rueckauer21-NxTF] | No bridge from a PyTorch SNN framework exists (SNN Toolbox's own PyTorch input path reaches NxTF through ONNX, and the NxTF repository's SLAYER tutorials load PyTorch-trained weights by hand); host repository (`intel-nrc-ecosystem/models`) carries a discontinuation notice [A18-Research] |
| NetX / the Lava compiler | Platform-independent HDF5 network description from SLAYER/bootstrap training [LavaDL-NetX-Docs] | A runnable Lava Process graph, CPU-simulated or physical Loihi 2 for INRC members [LavaDL-NetX-Docs] | Soft reset: the reference process model hard-resets to zero, and no documented subtract-reset process exists for NetX [LavaDocs-Overview]. The whole stack is archived as of 13 May 2026 [LavaGH-Archive] |
| DynapCNN mapper (`DynapcnnNetwork`) | A Sinabs spiking model, IF-based, from `from_model()` [Sinabs-Basics] | 8-bit weight / 16-bit membrane quantized `DynapcnnLayer` objects, placed onto physical Speck cores [Sinabs-Basics] | Nothing on the reset axis (subtract-reset preserved by default); drops per-neuron threshold individuality (collapsed to one value per layer) and rewrites `Linear`/`AvgPool2d` architecturally [Sinabs-Basics] |
| sPyNNaker | PyNN-described network (populations, projections, neuron/synapse models) [Rhodes18-sPyNNaker] | A machine graph mapped to SpiNNaker cores, routed and loaded via SpiNNTools [Rowley19-SpiNNTools] | Reset semantics are inherited from whatever C model the user compiles; nothing is imposed or dropped by the framework itself |
| NengoLoihi | A Nengo model (NEF-built or NengoDL-converted) [NengoLoihi-Docs] | Compiled Loihi processes, physical hardware backend or an emulator [NengoLoihi-Docs] | Uses `LoihiLIF`/`LoihiSpikingRectifiedLinear` classes to model Loihi's own quantization during training; not built around the reset-by-subtraction rate-coding correspondence this thesis assumes |
| CNN2SNN | A QuantizeML-quantized Keras/ONNX model [BrainChip-CNN2SNNDocs] | An Akida-runtime `.fbz` model, BN and activation-quantization folded into static per-neuron thresholds [BrainChip-CNN2SNNDocs] | Drops the multi-timestep rate-coding correspondence entirely; the output is a single-pass quantized network, not a temporal accumulator [CNN2SNN-Source] |
| SpikingJelly `lava_exchange` | SpikingJelly IF/LIF modules only [SJ-LavaExchangeDocs] | Lava DL HDF5, loadable by Lava, runnable on Loihi or CPU-simulated Loihi [SJ-LavaExchangeDocs] | **Hard-codes rejection of any other reset value**: `if sj_ms_neuron.v_reset != 0.: raise ValueError('lava only supports for v_reset == 0!')`, at four call sites, plus an assertion in `CubaLIFNode.__init__` with a different message; also rejects `decay_input=True` and any bias on exported Conv2d/Linear layers [SJ-LavaExchangeSource] |
| SpikingJelly `nir_exchange` | SpikingJelly `BaseNode` modules | A NIR graph | `to_nir.py`'s `_hard_reset()` helper raises `NotImplementedError("NIR does not distinguish soft reset.")` whenever `module.v_reset is None`, i.e. whenever the neuron uses soft reset [SJ-NIRExchangeSource] |

**The central finding of this section: reset by subtraction is the single most
consistently dropped feature across every surveyed interoperability path to real
hardware.** NIR's own formal primitive specification encodes only reset to a fixed
value for its Integrate-and-Fire and LIF primitives, not reset-by-subtraction
[NIR-Primitives]. SpikingJelly is a self-contained illustration of the same problem
inside a single codebase. Its `ann2snn` conversion module defaults to soft reset,
`v_reset=None`, precisely because "ReLU activations in ANNs are strongly related to
the firing rates of IF neurons with subtractive reset" [SJ-ANN2SNNDocs]. Yet neither of
SpikingJelly's own two hardware/interop export paths can accept that output as-is.
`lava_exchange.py` raises `ValueError("lava only supports for v_reset == 0!")` at five
separate call sites [SJ-LavaExchangeSource], and `nir_exchange`'s `to_nir.py` raises
`NotImplementedError("NIR does not distinguish soft reset.")` whenever it encounters a
soft-reset neuron [SJ-NIRExchangeSource]. A network produced by SpikingJelly's own
`ann2snn.convert()` cannot be handed to SpikingJelly's own Lava or NIR export code
without either silently re-parameterizing to hard reset, which reintroduces
approximately the twenty-percentage-point accuracy gap Rueckauer et al. measured when
comparing the two reset modes on CIFAR-10 [Rueckauer17-SNNTB], or writing new code that
does not currently exist. This self-inconsistency, one framework producing an output
its own export paths refuse, is the clearest, most concrete evidence for the survey's
broader argument that reset-by-subtraction is the feature interoperability tooling
drops first.

## 6.4 Runtime and Host I/O

**NxSDK.** Intel's Loihi 1-era runtime, structured around three high-level APIs
(the third-party Nengo API, Intel's own low-level NxNet, and the Keras-derived NxTF),
all compiling down through a common register-level NxCore API [Rueckauer21-NxTF]. It is
superseded; INRC's own 2022 migration guidance tells members to move to Lava
[IntelINRC-Access].

**Lava ProcessModels.** Lava structures computation as CSP-style communicating
Processes, each with one or more ProcessModel implementations (e.g. a `PyLifModel`
running on CPU, or a Loihi-targeted model compiled through the proprietary Magma
layer). The Process/ProcessModel separation is explicitly extensible: a user can write
a custom `PyLoihiProcessModel` with arbitrary `run_spk()` dynamics, which in principle
makes a subtract-reset neuron implementable, though no source found documents one
having been written [LavaDocs-Overview]. Core Lava (the Process API, BSD-3/LGPL-2.1) is
open; the Magma components that compile Processes specifically to Loihi hardware remain
proprietary to Intel, distributed only as the "Lava extension for Loihi," gated to INRC
members [LavaDocs-Overview].

**samna.** SynSense's own developer interface and runtime for all SynSense devices
(Speck, DYNAP-CNN, Xylo, DYNAP-SE), described by the vendor as running its core in C++
with a Python API layered on top, featuring an event-based stream-filter system for
real-time, multi-branch processing of event streams entering or leaving the device
[SynSense-SpeckOverview]. Chip "Models" expose a hardware-agnostic interface:
`apply_configuration()` validates and applies a device configuration; `get_source_node()`
and `get_sink_node()` stream events to and from the chip [Sinabs-Basics]. samna is the
runtime layer common to both the Sinabs-to-Speck and Rockpool-to-Xylo deployment paths.

**SpiNNaker runtime.** SpiNNTools generates the full compile pipeline, partitioning an
application graph into a machine graph, placing vertices onto specific cores, routing
multicast tables, and loading per-core parameter blocks and compiled C executables into
each core's tightly-coupled memory [Rowley19-SpiNNTools]. At execution time, the
event-driven SpiN1API operating system on each core runs for the configured duration;
results are extracted off-machine via the PyNN API [Rhodes18-sPyNNaker].

**Host-side encoding and readout.** Every platform surveyed requires an explicit
host-side step to turn a static image or a continuous-valued vector into whatever the
device consumes, and to turn device output back into a classification. For rate-coded
static-image conversion, this is Bernoulli/Poisson rate encoding, generated on the host
and streamed as timestamped AER events (`raster_to_events`), a step Sinabs itself
documents as separate from the chip's native event stream [Sinabs-Basics]. Readout is
either raw spike accumulation read back over a fixed window and interpreted as a
firing-rate vote, or, on Speck, an on-chip readout layer performing majority-vote
classification directly on-chip [Sinabs-Basics].

## 6.5 Documented Routes

Every traversal from a trained network to silicon located in this research, with its
chain, evidence class, and stated limits.

**1. SNN Toolbox to NxTF to Loihi 1.** Rate-coded, weight-normalized, reset-by-subtraction
IF conversion, compiled by NxTF, measured on physical Loihi 1: MNIST 0.79% error, 0.66
mJ, 6.65 ms; CIFAR-10 (MobileNet-derived) 8.52% error, 102 mJ, 340 ms on 861 cores
across 7 chips [Rueckauer21-NxTF]. (The 1,753-core, 14-chip figure sometimes attached to
this result belongs to the Quartz paper's own, separate CIFAR-10 network, not the NxTF
MobileNet: Lenz, Orchard, and Sheik, "Ultra-low-power Image Classification on
Neuromorphic Hardware," arXiv:2309.16795, Sec. 4.2.) Reset by subtraction survives the whole chain, via the
two-compartment compiler trick [Rueckauer21-NxTF]. **Evidence class: E1.** Neither
component is maintained: SNN Toolbox's last substantive release was March 2021, last
bugfix patch August 2022 [SNNToolbox-GitHub]; NxSDK/NxTF is Loihi-1-era and Intel's own
2022 guidance redirects users to Lava for Loihi 2 [IntelINRC-Access].

**2. SNN Toolbox to pyNN to SpiNNaker.** A LeNet CNN, trained conventionally, converted
via SNN Toolbox's Rueckauer-2017 method, deployed on a physical SpiNNaker-103 machine:
98.20% accuracy on MNIST, 15 ms of recorded activity per sample [PatinoSaucedo20-SpiNNConv].
Reset by subtraction survives, as SNN Toolbox's default [Rueckauer17-SNNTB]. **Evidence
class: E1**, but only at MNIST scale; no CIFAR-10-or-larger converted CNN has been
measured on physical SpiNNaker silicon in any source found. SpyNNaker/sPyNNaker remains
actively developed (SpiNNaker2 successor work is ongoing), but SNN Toolbox's own
SpiNNaker backend is dormant along with the rest of the toolbox [SNNToolbox-GitHub].

**3. Sinabs to `DynapcnnNetwork` to samna to Speck.** `from_model()` replaces ReLUs
with soft-reset IF layers by default; `DynapcnnNetwork` quantizes to 8-bit weights and
16-bit membrane state and places layers onto physical Speck cores; samna applies the
configuration and streams events [Sinabs-Basics]. Reset by subtraction survives the
entire chain as the documented default on both software and hardware sides
[Sinabs-FromTorch]. Worked, measured examples exist at N-MNIST and small-CNN scale
(90.00% accuracy on physical silicon in one documented tutorial) [A18-Research].
**Evidence class: E1.** Every component (Sinabs, samna, the Speck hardware line) is
actively maintained, and the hardware is commercially purchasable with no
research-membership gate.

**4. Rockpool to Xylo.** `mapper()` to `quantize_methods` to `config_from_specification()`
to `XyloSamna`/`XyloMonitor`, deployed to a physical Xylo HDK, with on-chip power
recording [Rockpool-XyloDeploy]. Reset by subtraction survives, as a fixed hardware
property [Rockpool-XyloOverview]. A published, physical-silicon result exists for
keyword spotting (the SynNet architecture on XyloAudio 2, "Aloha" benchmark)
[Bos24-XyloKWS]. **Evidence class: E1**, for audio/sensory-scale workloads; Xylo is not
a CIFAR-scale vision accelerator.

**5. SpikingJelly to `lava_exchange` to Lava to Loihi 2.** Documented, but **does not
preserve reset by subtraction**: `lava_exchange.py` raises `ValueError` for any
`v_reset != 0.`, at four call sites, plus an assertion in `CubaLIFNode.__init__` with a
different message [SJ-LavaExchangeSource]. The operator dispatch
supports only `nn.Linear`, `nn.Conv2d`, `nn.AvgPool2d`, and `nn.Flatten`; a VGG's
`nn.MaxPool2d` or a ResNet's residual add would each raise `NotImplementedError`
[SJ-LavaExchangeSource]. The one worked example in SpikingJelly's own documentation
(`lava_mnist`) reports accuracy from a CPU-simulated Lava run, not a physical-Loihi
measurement [SJ-LavaExchangeDocs]. **Evidence class: E3 at best**, and the underlying
software stack is archived as of 13 May 2026 [LavaGH-Archive]. A route that breaks soft
reset anywhere is not viable for this thesis's literature, and this route breaks it at
the first hop.

**6. QuantizeML to CNN2SNN to Akida.** MetaTF training and quantization to a static,
BN-and-activation-folded threshold, deployed to physical AKD1000/AKD1500 hardware
[BrainChip-CNN2SNNDocs]. Physical-silicon measurements exist and are independently
corroborated, e.g. an IIoT comparison against a Jetson Orin NX on MNIST, with real
plug-power measurement [A18-Research reference to BrainChip literature via a16 §8.1].
**Evidence class: E1** for the platform generally. However this route does **not**
implement rate-coded, reset-by-subtraction IF conversion at all; it collapses the
rate-code approximation of ReLU into a single quantized pass with no membrane state
carried across timesteps [Ziegler24-FastObjects][Lunghi25-SpaceSNN][CNN2SNN-Source].
It is a live, maintained, commercially purchasable route to silicon, but not a route
for the specific conversion family this thesis studies.

**7. SpikingJelly to NIR to a backend.** Documented, and **does not preserve reset by
subtraction** either: `to_nir.py`'s `_hard_reset()` helper raises
`NotImplementedError("NIR does not distinguish soft reset.")` whenever
`module.v_reset is None` [SJ-NIRExchangeSource], consistent with the NIR primitive
specification itself, which defines only reset to a fixed value
[NIR-Primitives]. **Evidence class: E3** (a documented path exists, an FX-graph
`nir_exchange` module is shipped and maintained) but no published run of a
soft-reset SpikingJelly model through this path to physical silicon was found.

### Verdicts

**SpikingJelly into NxTF into Loihi 1 is blocked.** NxTF is Keras-native; no bridge from
a PyTorch SNN framework such as SpikingJelly exists. The only automated bridge into NxTF,
`nxsdk_modules_ncl/snntoolbox/nx_backend.py`, was purpose-built for SNN Toolbox, not for
SpikingJelly, and its host repository, `intel-nrc-ecosystem/models`, carries a blanket
discontinuation notice from Intel [A18-Research]. A PyTorch-to-Keras workaround does
exist and is documented, just not for SpikingJelly: SNN Toolbox's own
`pytorch_input_lib.py` ingests PyTorch ANNs by exporting them to ONNX and reloading them
through the Keras-model parser, and the NxTF repository's SLAYER tutorials load
PyTorch-trained weight arrays by hand from `.npy` files. Neither path accepts a
SpikingJelly-converted network; it would be original engineering to connect one.

**SpikingJelly into Lava into Loihi 2 is blocked.** It is blocked at reset semantics,
by SpikingJelly's own hard-coded `v_reset == 0` assertion, and separately by an
operator set covering only `Linear`, `Conv2d`, `AvgPool2d`, and `Flatten`, which excludes
max-pooling and residual addition, the two most common structural elements in the
CNN families this thesis targets [SJ-LavaExchangeSource]. Intel archived Lava on 13 May
2026, freezing this stack regardless of the reset-semantics and operator-coverage
problems [LavaGH-Archive].

**The one live, reset-consistent, commercially purchasable route is Sinabs
`from_model()` into `DynapcnnNetwork` into `samna` onto Speck.** Reset by subtraction
is the documented default at every stage, the software toolchain is actively
maintained, and the hardware ships without a research-membership gate
[Sinabs-FromTorch][Sinabs-Basics].

---

## References for Section 6

Source-type labels: peer-reviewed, preprint, official documentation, repository state,
vendor material, community commentary.

- [Davies18] M. Davies et al., "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning," *IEEE Micro* 38(1), 2018. https://doi.org/10.1109/mm.2018.112130359 — peer-reviewed.
- [Davies21] M. Davies, A. Wild, G. Orchard, Y. Sandamirskaya, et al., "Advancing Neuromorphic Computing With Loihi: A Survey of Results and Outlook," *Proceedings of the IEEE* 109(5), 2021. https://doi.org/10.1109/jproc.2021.3067593 — peer-reviewed.
- [Rueckauer21-NxTF] B. Rueckauer, C. Bybee, R. Goettsche, Y. Singh, J. Mishra, A. Wild, "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi," *ACM JETC* 18(2), 2022 (arXiv:2101.04261). https://doi.org/10.1145/3501770 — peer-reviewed.
- [IntelBrief-L2] Intel Corporation, "Taking Neuromorphic Computing to the Next Level with Loihi 2," technical brief. https://www.intel.com/content/dam/www/central-libraries/us/en/documents/neuromorphic-computing-loihi-2-brief.pdf — vendor material.
- [IntelINRC-Access] Intel INRC Confluence, "Access Intel Loihi Hardware." https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001 — vendor material.
- [LavaGH-Archive] Lava-nc GitHub repositories (archived), banner text. https://github.com/lava-nc/lava/ ; https://github.com/lava-nc/lava-dl — repository state.
- [LavaDocs-Overview] Lava Software Framework overview / documentation, incl. reference `PyLifModel`. https://lava-nc.org/ — official documentation (archived project).
- [LavaDL-NetX-Docs] Lava-DL NetX documentation and README. https://lava-nc.org/lava-lib-dl/netx/netx.html ; https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/netx/README.md — official documentation (archived project).
- [Orchard21-Loihi2Sig] G. Orchard, E. P. Frady, D. Ben Dayan Rubin, et al., "Efficient Neuromorphic Signal Processing with Loihi 2," *2021 IEEE SiPS*. https://doi.org/10.1109/sips52927.2021.00053 — peer-reviewed.
- [Shrestha23-VideoAudio] S. B. Shrestha, J. Timcheck, P. Frady, L. Campos-Macías, M. Davies, "Efficient Video and Audio Processing with Loihi 2," arXiv:2310.03251, 2023 — preprint.
- [Brehove26-SigmaDelta] M. Brehove, S. A. Tumpa, E. Kyubwa, N. Menon, V. Narayanan, "Sigma-Delta Neural Network Conversion on Loihi 2," ICONS 2026 preprint. https://arxiv.org/html/2505.06417v2 — preprint.
- [Furber12-SpiNNOverview] S. Furber, D. Lester, L. A. Plana, et al., "Overview of the SpiNNaker System Architecture," *IEEE Trans. Computers* 62(12), 2012. https://doi.org/10.1109/tc.2012.142 — peer-reviewed.
- [Painkras13-SpiNN1chip] E. Painkras et al., "SpiNNaker: A 1-W 18-Core System-on-Chip for Massively-Parallel Neural Network Simulation," *IEEE JSSC* 48(8), 2013. https://doi.org/10.1109/jssc.2013.2259038 — peer-reviewed.
- [Rhodes18-sPyNNaker] A. D. Rhodes et al., "sPyNNaker: A Software Package for Running PyNN Simulations on SpiNNaker," *Frontiers in Neuroscience* 12:816, 2018. https://doi.org/10.3389/fnins.2018.00816 — peer-reviewed.
- [Rowley19-SpiNNTools] A. G. D. Rowley et al., "SpiNNTools: The Execution Engine for the SpiNNaker Platform," *Frontiers in Neuroscience* 13:231, 2019. https://doi.org/10.3389/fnins.2019.00231 — peer-reviewed.
- [PatinoSaucedo20-SpiNNConv] A. Patiño-Saucedo, H. Rostro-González, T. Serrano-Gotarredona, B. Linares-Barranco, "Event-driven implementation of deep spiking convolutional neural networks for supervised classification using the SpiNNaker neuromorphic platform," *Neural Networks* 121, 2020. https://doi.org/10.1016/j.neunet.2019.09.008 — peer-reviewed.
- [Stromatias15-DBN] E. Stromatias, D. Neil, F. Galluppi, M. Pfeiffer, S.-C. Liu, S. Furber, "Scalable Energy-Efficient, Low-Latency Implementations of Spiking Deep Belief Networks on SpiNNaker," IJCNN 2015. https://pure.manchester.ac.uk/ws/files/32800773/FULL_TEXT.PDF — peer-reviewed.
- [Kelber20-SpiNN2Map] F. Kelber, B. Wu, B. Vogginger, et al., "Mapping Deep Neural Networks on SpiNNaker2," NICE '20, ACM, 2020. https://dl.acm.org/doi/10.1145/3381755.3381778 — peer-reviewed.
- [Arfa25-SpiNN2NIR] S. Arfa, B. Vogginger, C. Liu, J. Partzsch, M. Schöne, C. Mayr, "Efficient Deployment of Spiking Neural Networks on SpiNNaker2 for DVS Gesture Recognition Using Neuromorphic Intermediate Representation," NICE 2025. https://doi.org/10.1109/nice65350.2025.11065119 — peer-reviewed.
- [Scholze26-SpiNN2Chip] S. Scholze, J. Partzsch, S. Höppner, et al., "The SpiNNaker2 chip: a many-core platform for flexible and scalable brain-inspired computing," arXiv:2607.24396, 2026 — preprint.
- [SpiNNcloud24-PR] SpiNNcloud Systems, "SpiNNcloud Systems Announces First Commercially Available Neuromorphic Supercomputer," Newswire, 2024-05-08. https://www.newswire.com/news/spinncloud-systems-announces-first-commercially-available-neuromorphic-22325275 — vendor material.
- [EBRAINS-Access] EBRAINS, "Getting access to the NMC systems BrainScaleS and SpiNNaker," HBP Wiki. https://wiki.ebrains.eu/bin/view/Collabs/neuromorphic/Getting%20access/ — official documentation.
- [EBRAINS-BSS] EBRAINS, "BrainScaleS" platform page. https://ebrains.eu/data-tools-services/tools/brainscales — official documentation.
- [SynSense-SpeckOverview] SynSense/Sinabs, "Overview" (Speck). https://sinabs.readthedocs.io/main/speck/overview.html — official documentation.
- [Richter23-SpeckASIC] Richter, Xing, De Marchi, et al., "Speck: A Smart event-based Vision Sensor with a low latency 327K Neuron Convolutional Neural Network Processing Pipeline," arXiv:2304.06793 — preprint.
- [Yao24-SpeckNatComm] Yao, Richter, Zhao, et al., "Spike-based dynamic computing with asynchronous sensing-computing neuromorphic chip," *Nature Communications* 15:4464, 2024. https://doi.org/10.1038/s41467-024-47811-6 — peer-reviewed.
- [SynSense-SpeckDatasheet] SynSense, Speck Dev Kit Datasheet. https://www.synsense.ai/wp-content/uploads/2023/06/Speck-devkit-datasheet.pdf — vendor material.
- [Sinabs-FromTorch] Sinabs API reference, `sinabs.from_torch.from_model`. https://sinabs.readthedocs.io/main/api/from_torch.html — official documentation.
- [Sinabs-Basics] Sinabs, "The Basics" (Speck deployment guide). https://sinabs.readthedocs.io/v3.1.1/speck/the_basics.html — official documentation.
- [Rockpool-XyloOverview] Rockpool docs, "Overview of the Xylo family." https://rockpool.ai/devices/xylo-overview.html — official documentation.
- [Rockpool-XyloDeploy] Rockpool docs, "Quick-start with Xylo SNN core." https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html — official documentation.
- [Rockpool-XyloA3Tutorial] Rockpool docs, "Using XyloSamna and XyloMonitor to deploy a model on XyloAudio 3 HDK." https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html — official documentation.
- [Bos24-XyloKWS] Bos, Muir, et al., "Micro-power spoken keyword spotting on Xylo Audio 2," arXiv:2406.15112 — preprint.
- [Pehle22-BSS2] C. Pehle, S. Billaudelle, B. Cramer, et al., "The BrainScaleS-2 Accelerated Neuromorphic System With Hybrid Plasticity," *Frontiers in Neuroscience* 16:795876, 2022. https://doi.org/10.3389/fnins.2022.795876 — peer-reviewed.
- [Weis20-hxtorch] Spilger, Weis, et al., "hxtorch: PyTorch for BrainScaleS-2 — Perceptrons on Analog Neuromorphic Hardware," arXiv:2006.13138 — preprint.
- [Weis20-ANNMode] Weis, Spilger, et al., "Inference with Artificial Neural Networks on Analog Neuromorphic Hardware," arXiv:2006.13177 — preprint.
- [Pehle22-hxtorchsnn] C. Pehle et al., "hxtorch.snn: Machine-learning-inspired Spiking Neural Network Modeling on BrainScaleS-2 Hardware," arXiv:2212.12210 — preprint.
- [Cramer22-SurrogateGrad] B. Cramer et al., "Surrogate gradients for analog neuromorphic computing," *PNAS*, 2022 (arXiv:2006.07239) — peer-reviewed.
- [Schmitt17-HITL] Schmitt, Klähn, Bellec, et al., "Neuromorphic Hardware In The Loop: Training a Deep Spiking Network on the BrainScaleS Wafer-Scale System," 2017. https://ar5iv.labs.arxiv.org/html/1703.01909 — peer-reviewed.
- [Stradmann21-Mobile] Stradmann, Billaudelle, et al., "Demonstrating Analog Inference on the Mobile System," arXiv:2103.15960 — preprint.
- [Akopyan15-TrueNorth] F. Akopyan et al., "TrueNorth: Design and Tool Flow of a 65 mW 1 Million Neuron Programmable Neurosynaptic Chip," *IEEE TCAD*, 2015 — peer-reviewed.
- [Cassidy13-TNNeuron] A. Cassidy et al., "Cognitive Computing Building Block: A Versatile and Efficient Digital Neuron Model for Neurosynaptic Cores." https://viplab.fudan.edu.cn/vip/attachments/download/3248/neuron-model_of_truenorth.pdf — peer-reviewed.
- [Esser16-Eedn] S. K. Esser et al., "Convolutional Networks for Fast, Energy-Efficient Neuromorphic Computing," *PNAS* 113(41), 2016. https://www.pnas.org/doi/10.1073/pnas.1604850113 — peer-reviewed.
- [Sawada16-TNEcosystem] J. Sawada et al., "TrueNorth Ecosystem for Brain-Inspired Computing," SC 2016. https://dl.dropboxusercontent.com/s/brj18cmy9vy5oq5/TrueNorthEcosystem.pdf — peer-reviewed.
- [Shukla19-TNCarCount] S. Shukla et al., "REMODEL: Rethinking Deep CNN Models to Detect and Count on a NeuroSynaptic System," *Frontiers in Neuroscience*, 2019. https://doi.org/10.3389/fnins.2019.00004 — peer-reviewed.
- [Pei19-Tianjic] J. Pei, L. Deng, S. Song, et al., "Towards artificial general intelligence with hybrid Tianjic chip architecture," *Nature* 572, 2019. https://www.nature.com/articles/s41586-019-1424-8.epdf — peer-reviewed.
- [Lynxi-KA200] Lynxi, KA200 product page. https://lynxi.com/lq2001/18.html — vendor material.
- [Lynxi-HP300] Lynxi, HP300 product page / PDF datasheet. https://www.lynxi.com/ka2003/21.html — vendor material.
- [BIDL-GitHub] LynxiTech/BIDL GitHub repository and user manual. https://github.com/LynxiTech/BIDL ; https://bidl-user-manual.readthedocs.io/en/latest/ — repository state / official documentation.
- [BIDL-PMC] BIDL team, "BIDL: a brain-inspired deep learning framework for spatiotemporal processing," 2023. https://pmc.ncbi.nlm.nih.gov/articles/PMC10410154/ — peer-reviewed.
- [BrainChip-AKD1000Brief] BrainChip, AKD1000 SoC Product Brief V2.3. https://brainchip.com/wp-content/uploads/2025/08/Akida-AKD1000-SoC-Product-Brief-V2.3-Aug.25.pdf — vendor material.
- [BrainChip-AKD1500Brief] BrainChip, AKD1500 Product Brief V2.4 and commercial-availability press release. https://brainchip.com/wp-content/uploads/2025/11/AKD1500-Product-Brief-V2.4-Oct.25.pdf — vendor material.
- [BrainChip-CNN2SNNDocs] BrainChip, CNN2SNN user guide / advanced tutorial. https://doc.brainchipinc.com/user_guide/cnn2snn.html ; https://brainchip-inc.github.io/akida_examples_2.9.0-doc-1/user_guide/cnn2snn.html — official documentation.
- [BrainChip-QuantizeMLDocs] BrainChip, QuantizeML user guide. https://doc.brainchipinc.com/user_guide/quantizeml.html — official documentation.
- [BrainChip-AkidaUserGuide] BrainChip, Akida user guide (layers, edge learning, hardware constraints). https://doc.brainchipinc.com/user_guide/akida.html — official documentation.
- [CNN2SNN-Source] Author's local copy of BrainChip's `cnn2snn` 2.19.1 source, `cnn2snn/quantizeml/outputs.py` (`set_output_v1_variables`) and `activations.py` (`parse_relu_v1`) — repository state (primary, hands-on).
- [Ziegler24-FastObjects] Ziegler, Vetter, Gossard, Tebbe, Otte, Zell, "Detection of Fast-Moving Objects with Neuromorphic Hardware," arXiv:2403.10677 — preprint.
- [Lunghi25-SpaceSNN] Lunghi, Silvestrini, Dold, Meoni, Hadjiivanov, Izzo, "Energy efficiency analysis of Spiking Neural Networks for space applications," arXiv:2505.11418 — preprint.
- [Thorpe98-RankOrder] S. Thorpe, J. Gautrais, "Rank Order Coding," in *Computational Neuroscience: Trends in Research 1998*, Plenum Press — peer-reviewed (book chapter).
- [ThorpeGautrais96-SpikeAsync] S. Thorpe, J. Gautrais, "Rapid Visual Processing using Spike Asynchrony," NeurIPS 1996. https://proceedings.neurips.cc/paper_files/paper/1996/file/fd5c905bcd8c3348ad1b35d7231ee2b1-Paper.pdf — peer-reviewed.
- [Moyer20-SemiEng] B. Moyer, "Spiking Neural Networks: Research Projects or Commercial Products?", Semiconductor Engineering, 2020. https://semiengineering.com/spiking-neural-networks-research-projects-or-commercial-products/ — community commentary (trade press).
- [Innatera-EETimes] "Innatera Productizes SNN Accelerator As 'Neuromorphic Microcontroller'," EE Times, 2024. https://www.eetimes.com/innatera-productizes-snn-accelerator-as-neuromorphic-microcontroller/ — community commentary (trade press).
- [Innatera-Pulsar-PR] Innatera, "Innatera Unveils Pulsar, the World's First Mass-Market Neuromorphic Microcontroller for the Sensor Edge." https://www.innatera.com/newsroom/innatera-unveils-pulsar-the-worlds-first-mass-market-neuromorphic-microcontroller-for-the-sensor-edge/ — vendor material.
- [Innatera-Talamo] Innatera, Talamo SDK page. https://www.innatera.com/software-and-tools/ — vendor material.
- [Frenkel19-ODIN] C. Frenkel, M. Lefebvre, J.-D. Legat, D. Bol, "ODIN: A 0.086-mm² 12.7-pJ/SOP 64k-Synapse 256-Neuron Online-Learning Digital Spiking Neuromorphic Processor in 28-nm CMOS," *IEEE TBioCAS*, 2019 (arXiv:1804.07858) — peer-reviewed.
- [FrenkelIndiveri22-ReckOn] C. Frenkel, G. Indiveri, "ReckOn: A 28-nm Sub-mm² Task-Agnostic Spiking Recurrent Neural Network Processor," ISSCC 2022 (arXiv:2208.09759) — peer-reviewed.
- [Frenkel19-MorphIC] C. Frenkel, J.-D. Legat, D. Bol, "MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning," ISCAS 2019 (arXiv:1904.08513) — peer-reviewed.
- [Tang23-SENECA] Tang, Vadivel, Xu, Bilgic, et al., "SENECA: building a fully digital neuromorphic processor, design trade-offs and challenges," *Frontiers in Neuroscience*, 2023. https://doi.org/10.3389/fnins.2023.1187252 — peer-reviewed.
- [Shidqi22-SENECAThesis] N. Shidqi, "Benchmarking and Algorithm Optimization for SENeCA: A RISC-V-based Neuromorphic Processor," TU Delft MSc thesis, 2022. http://resolver.tudelft.nl/uuid:3b6a47f2-bde5-4652-8e6a-8fb6155a4740 — repository state (thesis).
- [muBrain21] "μBrain: An Event-Driven and Fully Synthesizable Architecture for Spiking Neural Networks," *Frontiers in Neuroscience*, 2021. https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2021.664208/full — peer-reviewed.
- [Panchapakesan22-SyncNN] A. Panchapakesan, Z. Fang, J. Li, "SyncNN: Evaluating and Accelerating Spiking Neural Networks on FPGAs," ACM TRETS 2022. https://doi.org/10.1145/3514253 — peer-reviewed.
- [Carpegna24-SpikerPlus] A. Carpegna, A. Savino, S. Di Carlo, "Spiker+: A Framework for the Generation of Efficient Spiking Neural Networks FPGA Accelerators for Inference at the Edge," *IEEE TETC*, 2024. https://doi.org/10.1109/tetc.2024.3511676 — peer-reviewed.
- [Li23-FireFly] G. Li, L. Shen, Y. Zhao, Y. Zhang, Y. Zeng, "FireFly: A High-Throughput Hardware Accelerator for Spiking Neural Networks," *IEEE TVLSI*, 2023. https://doi.org/10.1109/tvlsi.2023.3279349 — peer-reviewed.
- [Li24-FireFlyv2] G. Li, L. Shen, Y. Zhao, Y. Zhang, Y. Zeng, "FireFly v2: Advancing Hardware Support for High-Performance Spiking Neural Network With a Spatiotemporal FPGA Accelerator," *IEEE TCAD*, 2024. https://doi.org/10.1109/tcad.2024.3380550 — peer-reviewed.
- [ChenGaoFu22-Cerebron] G. K. Chen, B. Gao, Y. Fu, "Cerebron: A Reconfigurable Architecture for Spatiotemporal Sparse Spiking Neural Networks," *IEEE TVLSI*, 2022. https://doi.org/10.1109/tvlsi.2022.3196839 — peer-reviewed.
- [SNNToolbox-Docs] SNN Toolbox documentation, introduction and simulation-backend guide. https://snntoolbox.readthedocs.io/en/latest/guide/intro.html — official documentation.
- [Rueckauer17-SNNTB] B. Rueckauer, I.-A. Lungu, Y. Hu, M. Pfeiffer, S.-C. Liu, "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image Classification," *Frontiers in Neuroscience* 11:682, 2017. https://doi.org/10.3389/fnins.2017.00682 — peer-reviewed.
- [SNNToolbox-GitHub] SNN Toolbox GitHub repository, PyPI release history, commit history, deps.dev activity score. https://github.com/NeuromorphicProcessorProject/snn_toolbox — repository state.
- [Pedersen24-NIR] J. E. Pedersen, S. Abreu, M. Jobst, et al., "Neuromorphic intermediate representation: A unified instruction set for interoperable brain-inspired computing," *Nature Communications* 15:8122, 2024. https://doi.org/10.1038/s41467-024-52259-9 — peer-reviewed.
- [NIR-Primitives] NIR project, primitives documentation. https://neuroir.org/docs/primitives/ — official documentation.
- [NIR-Support] NIR project, supported frameworks/hardware matrix. https://neuroir.org/docs/support/ — official documentation.
- [NIR-Porting] NIR project, porting-to-hardware guide. https://neuroir.org/docs/porting-nir/ — official documentation.
- [snnTorch-PR388] snnTorch GitHub, "nir: add missing v_reset parameter on export." https://github.com/jeshraghian/snntorch/pull/388 — repository state.
- [snnTorch-PR426] snnTorch GitHub, reset-mechanism refactor PR. https://github.com/jeshraghian/snntorch/pull/426 — repository state.
- [NengoLoihi-Docs] NengoLoihi documentation, overview and hardware/installation guides. https://www.nengo.ai/nengo-loihi/overview.html — official documentation.
- [ABR-PressRelease] Applied Brain Research, press release on Nengo/Loihi energy comparison. https://www.prnewswire.com/news-releases/applied-brain-research-inc-shows-nengo-spiking-real-time-ai-deep-learning-networks-on-intel-loihi-use-38x-less-energy-than-on-nvidia-quadro-k4000-gpu-300761243.html — vendor material.
- [DeWolf23-NengoArm] T. DeWolf et al., "Neuromorphic control of a simulated 7-DOF arm using Loihi," *Neuromorphic Computing and Engineering* 3:014007, 2023. https://doi.org/10.1088/2634-4386/acb286 — peer-reviewed.
- [SJ23-SciAdv] W. Fang et al., "SpikingJelly: An open-source machine learning infrastructure platform for spike-based intelligence," *Science Advances* 9(40), 2023. https://www.science.org/doi/pdf/10.1126/sciadv.adi1480 — peer-reviewed.
- [SJ-NeuronDocs] SpikingJelly docs, "Neuron" tutorial. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/neuron.html — official documentation.
- [SJ-ANN2SNNDocs] SpikingJelly docs, "ANN2SNN" tutorial. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/ann2snn.html — official documentation.
- [SJ-LavaExchangeDocs] SpikingJelly docs, "Convert to Lava for Loihi Deployment." https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html — official documentation.
- [SJ-LavaExchangeSource] SpikingJelly `lava_exchange.py` module source. https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html — repository state.
- [SJ-NIRExchangeSource] SpikingJelly `nir_exchange/to_nir.py` module source (`_hard_reset` helper) — repository state.
- [SJ-GitHub] SpikingJelly GitHub repository metadata, maintainers, CHANGELOG. https://github.com/fangwei123456/spikingjelly — repository state.
- [snnTorch-Docs] snnTorch docs, `snn.Leaky` API reference and Tutorial 2. https://snntorch.readthedocs.io/en/latest/snn.neurons_leaky.html — official documentation.
- [Eshraghian23-snnTorch] J. K. Eshraghian et al., "Training Spiking Neural Networks Using Lessons From Deep Learning," *Proceedings of the IEEE* 111(9), 2023 — peer-reviewed.
- [Norse-Docs] Norse docs, `norse.torch.functional.lif` and `norse.torch.module.lif`. https://norse.github.io/norse/auto_api/norse.torch.functional.lif.html — official documentation.
- [Sinabs-NIRToSpeck] Sinabs NIR-to-Speck deployment tutorial. https://sinabs.readthedocs.io/main/tutorials/nir_to_speck.html — official documentation.
- [BindsNET18] H. Hazan, D. J. Saunders, et al., "BindsNET: A Machine Learning-Oriented Spiking Neural Networks Library in Python," *Frontiers in Neuroinformatics*, 2018. https://doi.org/10.3389/fninf.2018.00089 — peer-reviewed.
- [Turner22-mlGeNN] J. P. Turner, J. C. Knight, A. Subramanian, T. Nowotny, "mlGeNN: accelerating SNN inference using GPU-enabled neural networks," *Neuromorphic Computing and Engineering*, 2022. https://doi.org/10.1088/2634-4386/ac5ac5 — peer-reviewed.
- [PyNN-Docs] PyNN documentation, "Introduction." https://pynn.readthedocs.io/en/latest/introduction.html — official documentation.
- [HBP-Guidebook] HBP Neuromorphic Computing Platform Guidebook. https://electronicvisions.github.io/hbp-sp9-guidebook/using_the_platform.html — official documentation.
- [PynnBSS2-Docs] PyNN for BrainScaleS-2 documentation. https://electronicvisions.github.io/documentation-brainscales2/latest/pynn-brainscales/index.html — official documentation.
- [Spyx-Docs] Spyx documentation / GitHub README. https://spyx.readthedocs.io/en/latest/ ; https://github.com/kmheckel/spyx/ — official documentation / repository state.
- [NengoDL-Rasmussen19] E. Rasmussen, "NengoDL: Combining deep learning and neuromorphic modelling methods," arXiv:1805.11144 — preprint.
- [A18-Research] Internal comparative research note, "SNN Toolbox vs. SpikingJelly `ann2snn`: source-level equivalence test," compiled for this survey from direct inspection of both codebases and their documentation (2026-09-15) — repository state / synthesis of primary sources cited therein.


---

# 7 Applications and Deployment Evidence

This section inventories every published result located during this survey's research
passes in which a trained network ran on, or was synthesized for, physical or
near-physical neuromorphic hardware. Each result is separated by evidence class, E1
through E5, and by whether the network was converted from a pretrained ANN, directly
trained with a surrogate gradient, or hand-designed with local plasticity. The pattern
that emerges is not a single deployment literature but several disconnected ones, each
tied to a specific chip vendor's own toolchain, with the low-`T` conversion literature
this thesis builds on almost entirely absent from the physical-silicon record.

## 7.1 Loihi-family deployments

**The NxTF-era conversion results, on physical Loihi 1.** Rueckauer et al.'s NxTF
compiler took a 4-layer CNN, trained conventionally in Keras, through SNN Toolbox's
rate-coded conversion pipeline, and ran it on physical Loihi 1 hardware. On MNIST, the
converted network reached 0.79% error at 100 timesteps, using 14 neurocores, measuring
0.66 mJ energy, 6.65 ms delay, and 4.38 µJ·s energy-delay product (EDP)
[rueckauer-2021-nxtf], [lenz-2023-quartz]. On CIFAR-10, an off-the-shelf MobileNet
converted the same way reached 8.52% error at roughly 400 timesteps, on 861
neuromorphic cores across 7 Loihi chips, at 102 mJ, 340 ms, and 34,926 µJ·s EDP
[rueckauer-2021-nxtf]. (The 1,753-core, 14-chip figure that the Quartz paper's
comparison table cites alongside this result describes Quartz's own, separate CIFAR-10
network, not the NxTF MobileNet [lenz-2023-quartz].) The same paper also ran SLAYER-trained
(directly trained, not converted) convolutional SNNs on N-MNIST and DVS Gestures on the
same physical chip [rueckauer-2021-nxtf]. These are the only classic rate-coded,
IF-neuron ANN-to-SNN conversions of a CNN found running on physical Loihi silicon
anywhere in this survey, and both are Loihi 1, not Loihi 2.

Massa et al. deployed a gesture-recognition network to physical Loihi 1 the same way,
through SNN Toolbox, but the pipeline first accumulates DVS events into frames and trains
a conventional DNN on those frames before conversion, so the deployed SNN is a
frame-trained network wearing an event-camera dataset, not a native event processor
[massa-2020]. Measured: 11.43 ms per-frame classification plus 150 ms of preprocessing,
6.24 FPS effective throughput, 89.64% accuracy, 37 cores. QCFS itself cites this paper,
along with Singh et al.'s Gesture-SNN, in its related work as prior physical-hardware
evidence, making QCFS the single exception among its own lineage to citing deployment
work as acknowledged prior art rather than motivational throat-clearing
[singh-2021-gesture-snn], [bu-2022-qcfs].

**The genuine falsifiers.** Two papers propose a new conversion method and measure it on
physical silicon. Quartz, a time-to-first-spike (TTFS) conversion scheme, deploys to
physical Loihi 1 and reports a like-for-like, on-chip EDP comparison against a rate-coded
baseline also run on Loihi: 0.9 µJ·s versus 4.38 µJ·s on MNIST, 10.3 mJ·s versus roughly
34.9 mJ·s on CIFAR-10 [lenz-2023-quartz]. Brehove et al. convert a post-training-quantized
ANN into a Sigma-Delta Neural Network and deploy it on a physical 16-chip Loihi 2 VPX
board, benchmarking a YOLOv3-style detector against a Jetson Xavier [brehove-2026]. Both
papers abandon rate coding for a platform-native code, temporal single-spike coding for
Quartz and graded sigma-delta spikes for Brehove, and no paper was found that keeps rate
coding, proposes a new conversion algorithm, and reaches physical silicon.

**Directly trained networks reaching Loihi through a vendor toolchain.** Shrestha et
al.'s PilotNet steering-angle regression network and accompanying audio-denoising
networks, trained natively with Lava-DL (SLAYER and bootstrap), not converted from a
separately pretrained ANN, ran on physical Loihi 2 with energy, latency, and EDP measured
against a Jetson Orin Nano and an Intel i9 [shrestha-2023-video-audio]. Boeshertz et al.
mapped a converted sigma-delta-neuron RNN to physical Loihi 1 with 3-bit weights for
speech classification [boeshertz-2024-rnn]. Mészáros, Knight, Timcheck, and Nowotny
trained an SNN with synaptic delays using EventProp (an exact-gradient method that maps
onto event-driven hardware by construction), then deployed it to a physical single-chip
Loihi 2, measuring latency around 1.46 to 1.54 ms and total energy of 0.28 to 0.46 mJ per
inference on keyword-spotting benchmarks, an 18-fold speedup and 250-fold energy reduction
over a Jetson Orin Nano at batch size 1 [meszaros-2025-delays]. A continual-learning
system (CLP-SNN) that adapts on-chip via a local three-factor rule reached 0.33 ms latency
and 0.05 mJ total energy per inference on physical Loihi 2, 113 times lower latency and
6,600 times lower energy than a Jetson Orin Nano baseline [clp-snn-2025]. A 2026 preprint
trained an object detector with SpikingJelly, exported it through a Lava-DL-compatible
format, and benchmarked it on physical Loihi 2 against Jetson Orin Nano, Jetson Nano B01,
and Apple M2 [spikingjelly-loihi2-2026]. A separate SpikingJelly-trained DVS128 Gesture
network reached physical, FPGA-based CRI neuromorphic hardware through the `hs_api`
conversion path, an independent, non-Loihi hardware target [cri-2025-hiaerspike].

**The hand-designed, local-plasticity body, the largest E1 concentration on Loihi.** None
of this work is gradient-trained, converted, or QCFS-lineage. Imam and Cleland's olfactory
circuit, trained by one-shot local plasticity rather than backpropagation, ran on physical
Loihi with 2.75 ms per sniff and 0.43 mJ total energy per classification, reported at 92%
accuracy [imam-2020-olfaction]. A 2023 replication study found the underlying dataset
suffers from sensor drift and a non-randomized measurement protocol, and that a simple
hash-table baseline matches the network's accuracy under a proper train/test split, a
caution against treating the hardware measurement as evidence for the algorithmic claim
even though the latency and energy figures themselves are not in question
[dennler-2023-olfaction-critique]. Tang, Shah, and Michmizos's biologically constrained
head-direction circuit for unidimensional SLAM ran on physical Loihi with dynamic power
100 times lower than GMapping on a CPU [tang-2019-slam]. The Locally Competitive
Algorithm, a provably convergent spiking solver for LASSO, appeared in Loihi's own
introductory paper with an EDP improvement of more than three orders of magnitude over an
Atom CPU running LARS/FISTA [davies-2018-loihi], and was subsequently extended to Loihi 2
for sparse coding [parpart-2023-lca] and convolutional sparse coding [convlca-2025-lca].
A Boolean satisfiability solver encoded as an SNN ran on physical Loihi, the first
reported CSP/SAT implementation on embedded neuromorphic hardware [satcsp-2020].

**Directly trained (gradient-based) robotics, audio, EEG, and radar work.** A spiking
actor network co-trained end-to-end with a deep critic via a surrogate-gradient extension
of STBP drove mapless robot navigation on a physical Kapoho Bay Loihi board, reaching 75
times lower energy per inference than DDPG on a Jetson TX2 [patel-2020-sddpg]. An
industrial peg-in-hole force-control policy, trained via spiking reinforcement learning in
simulation, ran on both physical Loihi 1 and Loihi 2, at 1.8 ms and 1.5 ms latency
respectively and 53 µJ dynamic energy per inference on Loihi 2, against roughly 3,800 µJ
on a CPU [forcecontrol-2024]. Kreiser et al.'s hand-designed path-integration circuit for
iCub head-pose estimation ran on Kapoho Bay with a closed loop under 10 ms, though only
accuracy, not energy, was reported [kreiser-2020-icub]. Recurrent SNNs for EMG gesture
classification reached 983 times lower energy and 19 times lower latency than a GPU at
batch size 50 on a Nahuku 32 board [bezugam-2023-emg], and a separate implementation on a
Kapoho Bay board reached 74% accuracy at 5.7 ms and 41 mW [donati-2022-emg]. A tri-modal
EMG-plus-DVS sign-language classifier spanning Loihi and the ODIN/MorphIC chips matched
GPU accuracy with a 30 to 600 times better energy-delay product [ceolini-emg-dvs]. A
graded-SNN seizure predictor reached 99.14% accuracy and 25.1 mJ per input on Loihi 2
[eeg-seizure-2025]; a separate motor-imagery decoder reported a self-described 95%
energy advantage over DNNs, not independently re-verified in this pass
[eeg-motor-imagery-repo]. A vehicle-mounted automotive radar pipeline ran real-time,
on-chip FFT, non-coherent integration, and CFAR detection on Loihi 2, the first such
deployment on real (not simulated) radar data [radar-automotive-2026], and a separate
spiking-resonator radar pipeline on simulated data measured full-activation power at
2.62 W with activity-gated sparsity cutting energy roughly 60% [radar-resonator-2025].
Keyword spotting on Loihi beat CPU, GPU, Jetson TX1, and Movidius NCS baselines at
equivalent accuracy, with the advantage growing with network size [blouw-2019-kws].

**Toolchain status.** NxSDK/NxTF targeted Loihi 1 only and is superseded. Lava, Lava-DL,
and NetX targeted Loihi 2 and were the documented forward path from 2021 onward, but all
`lava-nc` repositories were archived by Intel around May 2026, with Intel stating it is
developing a next-generation Loihi architecture and SDK rather than continuing Lava
[lava-archived-2026]. No published, peer-reviewed paper was found running a classic
rate-coded, IF-neuron, ANN-to-SNN-converted CNN, the style this thesis's own QCFS track
uses, on physical Loihi 2 silicon. The closest analogues are Brehove et al.'s sigma-delta
conversion, a different, non-rate-coded scheme purpose-built to avoid rate coding's
inefficiency on Loihi 2, and the NxTF rate-coded conversions, which ran on Loihi 1, not
Loihi 2 [rueckauer-2021-nxtf]. Intel's own technical brief states typical use of Loihi 2's
32-bit graded-spike payload at 8-bit precision, "a negligible extra energy cost compared
to binary spike processing" [intel-2021-loihi2-brief], and Davies et al.'s survey states
directly why: rate-coded feedforward conversion needs more timesteps as layer count grows,
and large networks spanning multiple chips congest inter-chip mesh links that carry
roughly 30 times less bandwidth than on-chip links, making converted rate-coded models
"less attractive for neuromorphic architectures optimized for sparsity" on Loihi 2
specifically [davies-2021-loihi].

## 7.2 DYNAP-CNN and Speck event-vision deployments

DYNAP-CNN is the processor core, and Speck is a system-on-chip integrating DYNAP-CNN with
an on-chip dynamic vision sensor on one die [sinabs-docs-overview]. Both expose nine
configurable computing cores, each a fixed `Conv2d → Integrate-and-Fire → optional
SumPool2d` pipeline stage, with no global clock driving the convolutional path
[sinabs-docs-overview]. Richter et al.'s characterization of the fabricated Speck1 ASIC
measured an end-to-end latency of **3.36 µs for a single event traversing all nine sCNN
layers**, and 1.58 µs through one layer, explicitly contrasted against clocked chips:
"Speck1 is specifically built to consume real-time data, its latency is significantly
lower than Loihi1/2 and TrueNorth which architecturally introduce a latency of one
timestep Δt on event generation in each layer" [richter-2023-speck]. A software-side
`num_timesteps` in the Sinabs toolchain only exists at the boundary where a rate-coded
raster is converted into individually timestamped events; once on-chip, the network has no
notion of a timestep and reacts continuously to each event's arrival [richter-2023-speck],
[sinabs-docs-overview].

Yao et al.'s Nature Communications characterization of the fabricated Speck chip measured
real-time power as low as 0.70 mW and resting power of 0.42 mW across DVS128 Gesture,
Gait-day, Gait-night, and HAR-DVS, with input masking trading accuracy for power (for
example, plus 9.0 percentage points on Gesture at 50% masking, at 3.8 mW versus 9.5 mW
unmasked) [yao-2024-speck]. Liu et al.'s live face-recognition demonstration on the
DynapCNN predecessor chip reported sub-mW power and a 98% recognition rate on a recorded
DVS dataset, though the accuracy figure was validated against a software simulation rather
than measured live on-chip [liu-2019-facerecognition]. A book-chapter comparison of a
small CNN on a DynapCNN devkit against a Kendryte K210 and an STM32L4R9 used the toolchain's
`raster_to_events` path to feed a genuinely rate-coded, static-image MNIST classifier to
physical silicon, reaching 98.79% balanced accuracy with energy estimated from synaptic
operation counts rather than directly measured on a power sensor
[riverpub-mcu-chapter]. No object-detection network was found measured on physical
DYNAP-CNN or Speck silicon anywhere in this search.

The weight resolution on DYNAP-CNN and Speck is 8 bits, and membrane-potential state is
16 bits [sinabs-docs-overview]. The default neuron is nonleaky integrate-and-fire with
reset-by-subtraction, the same reset convention the classical rate-coding conversion
literature uses [sinabs-docs-overview]. There is no native BatchNorm layer type; Speck-
targeted networks are built without BatchNorm from the start rather than relying on a
fold-in utility [sinabs-docs-overview]. SynSense's separate Xylo product line, for audio
and IMU rather than vision, is genuinely clocked and synchronous, unlike DYNAP-CNN and
Speck, and its own published keyword-spotting deployment reached 95% accuracy at 6.6 µJ
dynamic energy per inference on physical XyloAudio 2 silicon, beating Loihi and SpiNNaker2
on the same benchmark table [bos-2024-xylo].

## 7.3 SpiNNaker and BrainScaleS deployments

**SpiNNaker.** sPyNNaker's software stack exposes a documented SNN Toolbox backend, and
the clearest physical result is Patiño-Saucedo et al.'s conventional LeNet, trained in
Keras, converted with SNN Toolbox's rate-coded threshold-balancing pipeline, and deployed
on a physical **SpiNNaker-103 machine (48 chips, 864 ARM cores)**. The full 10,000-sample
MNIST test set was propagated through the physical hardware, reaching **98.20%** accuracy,
with **15 ms of recorded spiking activity per sample** and a measured wall-clock inference
time of **roughly 0.4 s per sample**, against about 10 s per sample for a NEST software
simulation of the identical PyNN model [patino-saucedo-2020-spinnaker]. A companion STBP
spiking CNN for event-based N-MNIST, directly trained rather than converted, reached
97.92% on the same physical machine [patino-saucedo-2020-spinnaker]. An earlier
DBN-to-SNN conversion (rate-coded, Poisson pixel encoding) ran on a single physical
SpiNNaker chip, reaching 95.01% accuracy, 0.3 W power, and roughly 20 ms latency
[stromatias-2015-dbn]. A design-space-exploration study reported 98.85% accuracy on a
physical SpiNNaker target with a faster hyperparameter search, though the latency and
energy figures were not confirmed in the retrieved text [galanis-2020-spinnaker]. A
motor-imagery EEG decoder mapped directly to a spiking CNN and deployed on physical
SpiNNaker reached 73.72% against 75.63% for the original CNN, a 1.91-point accuracy drop
from conversion and deployment [pals-2021-eeg-spinnaker]. No CIFAR-10-scale or larger,
VGG- or ResNet-class rate-coded CNN conversion was found running on physical SpiNNaker 1
or SpiNNaker 2 silicon anywhere in this search. The one VGG-16/ResNet-50-scale SpiNNaker2
result, Kelber et al.'s mapping study, reports 43.5 ms and 19.5 ms inference times, but the
paper states plainly that "as the SpiNNaker2 chip is not yet available, we developed a
Python simulator that replicates the timings," making the reported figures a pre-silicon
timing simulation, not a hardware measurement [kelber-2020-spinnaker2sim]. Arfa et al.
deployed natively trained, 8-bit quantized SNNs on a physical single-chip SpiNNaker2 test
board for DVS Gesture recognition, reaching 94.13% on-chip against roughly 94.6% in
floating-point software, an SNN-native deployment rather than a converted static-image CNN
[arfa-2025-spinnaker2].

**BrainScaleS.** Schmitt et al. converted a deep ReLU network to a spiking network on the
BrainScaleS-1 wafer-scale analog system using explicit rate coding, disabling the AdEx
model's adaptation and exponential features so the analog neuron approximates a ReLU
[schmitt-2017-brainscales]. **Direct transfer without retraining collapsed accuracy from
97% (software) to 72%** on a handwritten-digit classification task, because analog device
mismatch and trial-to-trial variation distort the rate-coded correspondence. **Hardware-
in-the-loop training, computing gradients in software using the ReLU derivative as an
approximation of the untractable hardware activation function, recovered accuracy to
95%**, close to the software model [schmitt-2017-brainscales]. The paper is explicit that
the algorithm had no exact knowledge of the neuron and synapse parameters on the analog
substrate, and that using the ReLU derivative as a stand-in circumvented rather than
solved the problem of an intractable analog activation function
[schmitt-2017-brainscales].

**BrainScaleS-2's CNN-scale demonstrations use a non-spiking, analog matrix-multiply mode,
not spike-rate conversion.** The same physical substrate can be reconfigured, by disabling
neuron leak and choosing the reset point so the ADC saturates at the reset voltage, into a
stateless analog vector-matrix multiplier rather than a genuine multi-timestep spiking
integrator [weis-2020-brainscales2]. A three-layer CNN classifying MNIST in this "hagen"
mode, with weights and activations quantized to 6 and 5 bits, went from 98.29% in float32
software to 98.10% after quantization, collapsed to 92.13% on direct, uncorrected transfer
to the chip, and recovered to **98.01% after hardware-in-the-loop training**
[weis-2020-brainscales2]. A deployed BrainScaleS-2 mobile system running this same
non-spiking mode for ECG atrial-fibrillation detection measured 276 µs classification time
and 192 µJ ASIC energy per sample at 5.6 W system power, with a 93.7% detection rate
[stradmann-2021-mobile]. A separate line of work trains genuinely spiking, surrogate-
gradient networks directly on BrainScaleS-2, not by conversion, reaching 97.6% MNIST
accuracy at 8 µs latency and 2.4 µJ per classified image on physical silicon
[cramer-2022-surrogate]. No source was found reporting a rate-coded, spike-count IF
conversion of a CNN at CIFAR-10 or ImageNet scale running on any BrainScaleS system; every
BrainScaleS deployment above that reaches usable accuracy does so through hardware-in-the-
loop retraining, not a one-shot convert-and-deploy pipeline.

## 7.4 FPGA and custom ASIC implementations

**Board-measured (E1).** SyncNN explicitly targets rate-encoding IF-model SNNs with
reset-by-subtraction, stating directly, "we focus on the IF model: the membrane potential
is just added or subtracted by the weight of the connection... and is reset immediately
once it reaches the threshold value," and proves a synchronous reformulation that runs
downstream layers once rather than for the full timestep window [syncnn-2022]. Measured
across three physical Xilinx ARM-FPGA boards (ZCU102, ZCU104, ZED), it reaches 99.6%
accuracy and 13,086 FPS on MNIST, its headline throughput claim, with SVHN and CIFAR-10
also evaluated at 16-, 8-, and 4-bit weight quantization [syncnn-2022]. Spiker+ generalizes
an earlier LIF-only FPGA accelerator into a configurable multi-layer architecture offering
six neuron models, IF, first-order LIF, and second-order LIF, each with a choice of hard
or subtractive reset, the first FPGA accelerator surveyed to offer reset-by-subtraction as
a named, user-selectable option matching the QCFS-style IF neuron this thesis uses
[spikerplus-2024]. Measured on physical Xilinx FPGA synthesis and deployment, it reaches
93.85% on MNIST at 780 µs and 180 mW using a 100-timestep encoding window, and 95% on
AudioMNIST at 290 mW [spikerplus-2024]. Cerebron is the clearest FPGA accelerator
explicitly built around the ANN-to-SNN conversion literature, stating directly that it
uses "an open-source SNNtoolbox" for conversion [cerebron-2022]. Measured on a physical
Xilinx XC7Z100 FPGA at 200 MHz, it reaches 99.40% on an MNIST ConvNet at 0.026 ms and
0.04 mJ per image, 91.90% on a thinned MobileNet for CIFAR-10 at 10.63 ms and 14.88 mJ,
and 97.30% on a lane-segmentation SegNet at 0.80 ms and 1.12 mJ [cerebron-2022].

**Synthesized but unfabricated (E4).** PASCAL proves an exact, integer-level equivalence
between a QCFS-activated ANN and an IF-neuron SNN using a spike-accumulation neuron with
soft reset, and reports a hardware-efficiency result derived from an analytical
operation-count model, not a synthesized circuit [pascal-2025]. Its acknowledgments
separately credit a collaborator for benchmarking the work on an unnamed "neuromorphic
architectural simulator," but no simulator result is reported in the paper body, so
PASCAL's own hardware-adjacent claim remains E5 with an unreported E4 gesture
[pascal-2025]. APEX takes PASCAL's spike-accumulation neuron and implements its full
spike-generation datapath as a fully combinational circuit inside the LoAS accelerator
framework, synthesized with Synopsys Design Compiler at 400 MHz on 40 nm CMOS, evaluated
by cycle-level simulation rather than fabricated silicon, and reports a 61.9% energy
reduction at matched accuracy against a standard, non-PASC IF neuron baseline
[apex-2026]. NeuroFlex independently extends PASCAL's neuron to column-level hybrid
ANN/SNN scheduling within a layer, synthesized with Synopsys Design Compiler at 560 MHz on
the same 40 nm node, again evaluated by RTL synthesis and a Python cycle-level simulator
rather than a fabricated chip, reporting PE-array utilization gains from fine-grained
scheduling [neuroflex-2025]. **APEX and NeuroFlex both build directly on PASCAL's
spike-accumulation neuron and reuse near-identical LoAS and SparTen baselines and Synopsys
synthesis methodology; APEX shares a co-author, Gopalakrishnan Srinivasan, with PASCAL
itself** [apex-2026], [neuroflex-2025], [pascal-2025]. None of the three has been
fabricated. The board-measured accelerators above, SyncNN, Spiker+, and Cerebron, are E1
because a physical device ran the network and reported the number; PASCAL, APEX, and
NeuroFlex are E4 at best because Synopsys Design Compiler synthesis and a cycle-level
simulator, however precise, are not a fabricated chip.

## 7.5 Event-based sensing and what actually computes on the events

Most published event-vision pipelines do not process events natively. A 2025 survey
states this directly: "most event-based deep learning pipelines convert asynchronous
events into dense representations (particularly voxel grids) before neural network
processing" [v2v-2025]. Of the six representation families a comprehensive event-vision
survey catalogs, image-based, surface-based, learning-based, voxel-based, graph-based, and
spike-based, only the last is native to spiking hardware, and the other five collapse the
asynchronous stream into a dense tensor handed to a conventional CNN or transformer
[eventvision-survey-2023]. Concretely, Prophesee's own production object-detection
pipeline accumulates events into a frame buffer before calling a conventional TorchScript
network on CPU or GPU [prophesee-docs-detection]; the pedestrian-detection literature
frames its central research question as frame CNNs versus asynchronous sparse CNNs, with
frame reconstruction remaining one of exactly two mainstream options
[prophesee-2025-pedestrian]; and even a "Loihi paper," Massa et al.'s gesture recognition,
states plainly that events must first be collected into frames and used to train a DNN
before that DNN is converted for deployment [massa-2020].

Where the survey looked across roughly twenty application papers spanning optical flow,
detection, automotive, SLAM, high-speed robotics, and gesture recognition, the compute
platform behind the majority is a GPU or workstation for algorithm development, an
embedded CPU, Raspberry Pi, or Jetson for the majority of real-time onboard robotics
demos, and an FPGA running a conventional, non-spiking CNN accelerator (the AMD/Xilinx
DPU, in most cases) for a distinct and fairly common third category, especially for drones
and SLAM [a14-application-survey]. A vendor's own production reference designs make the
pattern explicit. Prophesee's GenX320 sensor documentation states its CPI/AER output path
"is mainly destined for integration with neuromorphic systems," implying the sensor's
default, primary output path is not, and the vendor's own reference kits target a
Raspberry Pi 5 and an STM32 microcontroller, not a spiking chip [prophesee-genx320-docs].

**Some processors marketed as neuromorphic are confirmed non-spiking by their own
makers.** GrAI Matter Labs is the explicit case. An EE Times interview with the company
states directly, "while GrAI Matter describes its technology as 'brain-inspired,' its
NeuronFlow technology is based on a digital SoC architecture optimized for deep learning
acceleration (no spiking networks here)" [eetimes-graimatter]. NeuronFlow's core primitive
performs change-based, delta-quantized activations of a conventional ANN, exploiting
temporal sparsity inside an otherwise ordinary MAC-based dataflow accelerator, and its own
architecture paper describes its events as "valued events... not simple spikes as usual in
neuromorphic systems" [neuronflow-2020]. A conventional Xilinx DPU fed by an event sensor,
as in the Kria-Prophesee object-detection pipeline and the FPGA-drone obstacle-avoidance
work, is architecturally an ordinary systolic-array CNN accelerator with zero spiking
neurons; from the DPU's perspective, an event camera is just a low-latency frame source
[kria-prophesee-vitisai], [bonazzi-2025-fpgadrone].

**Genuine sensor-to-spiking-chip pipelines exist but are a minority, concentrated in
gesture recognition and simple closed-loop control.** IBM's TrueNorth-plus-DVS128 gesture
recognizer is the clearest landmark instance, a live DVS event stream feeding a TrueNorth
spiking CNN with no host-side frame accumulation in the deployed path, measuring 105 ms
onset latency, under 200 mW, and 96.5% accuracy [amir-2017-truenorth-gesture]. SynSense's
Speck reports vendor-measured sub-5 mW power and sub-50 ms response for gesture
recognition with no frame reconstruction [synsense-speck-gesture-datasheet], and the
GelNeuro tactile system feeds DVS-like marker-motion events directly into a physical
Speck2f spiking CNN, reaching 96.3% accuracy at 80 ms and 19.6 mW
[gelneuro-2026]. DYNAP-SE closes a spiking control loop directly against an iCub robot's
joint encoder [dynapse-icub-2020], and a separate DYNAP-SE deployment localizes touch on
an e-skin at 185 µW median inference power [ortone-2026-tactile]. A SpiNNaker-driven
goalkeeper robot closes an event-camera-to-servo loop fully on-chip, disconnected from any
PC, at 6.5 ms response latency and 85% interception accuracy
[cheng-2020-goalkeeper]. Outside this cluster of gesture recognition and simple
closed-loop control, event-vision applications, SLAM, optical flow, automotive detection,
and high-speed catching or robotics, essentially all route through a conventional
compute platform after frame reconstruction.

## 7.6 Cross-case evidence table

This is the survey's central exhibit: every paper located in this research that touches
physical or synthesized hardware, tagged by which population it belongs to.

| Paper | Method family | Population | Toolchain | Target | Measured | Class |
|---|---|---|---|---|---|---|
| NxTF MNIST [rueckauer-2021-nxtf] | Rate-coded ANN-SNN conversion | deployment | SNN Toolbox → NxTF | Loihi 1 (physical) | error, energy, delay, EDP | E1 |
| NxTF CIFAR-10 MobileNet [rueckauer-2021-nxtf] | Rate-coded ANN-SNN conversion | deployment | SNN Toolbox → NxTF | Loihi 1 (physical) | error, energy, delay, EDP | E1 |
| NxTF N-MNIST / DVS Gestures [rueckauer-2021-nxtf] | Directly trained (SLAYER) | deployment | SLAYER → NxTF | Loihi 1 (physical) | error, energy, delay, EDP | E1 |
| Massa et al. gesture [massa-2020] | Frame-trained CNN, then conversion | deployment | SNN Toolbox → NxSDK | Loihi 1 (physical) | latency, throughput, accuracy | E1 |
| Singh et al. Gesture-SNN [singh-2021-gesture-snn] | Hardware-aware co-optimization | deployment | own pipeline | neuromorphic accelerator (physical) | accuracy, latency, energy | E1 |
| Quartz [lenz-2023-quartz] | TTFS conversion (novel) | both | own pipeline | Loihi 1 (physical) | error, EDP, energy vs. rate-coded baseline | E1 |
| Brehove et al. sigma-delta [brehove-2026] | Sigma-delta conversion (novel) | both | own pipeline | Loihi 2, 16-chip VPX (physical) | EDP vs. Jetson Xavier | E1 |
| Shrestha et al. PilotNet/audio [shrestha-2023-video-audio] | Directly trained (SLAYER/bootstrap) | deployment | Lava-DL → NetX | Loihi 2 (physical) | energy, latency, EDP | E1 |
| Boeshertz et al. lpRNN [boeshertz-2024-rnn] | Converted RNN, sigma-delta | deployment | own pipeline | Loihi 1 (physical) | accuracy | E1/E2 |
| Mészáros et al. delays [meszaros-2025-delays] | Directly trained (EventProp) | deployment | mlGeNN → NetX | Loihi 2 (physical) | latency, energy, EDP vs. Jetson | E1 |
| CLP-SNN [clp-snn-2025] | On-chip local learning | deployment | Lava | Loihi 2 (physical) | latency, energy, EDP vs. Jetson | E1 |
| SpikingJelly object detector [spikingjelly-loihi2-2026] | Directly trained (SpikingJelly) | deployment | SpikingJelly → Lava-DL | Loihi 2 (physical) | inference rate, energy, power, EDP | E1 |
| DVS128 Gesture on CRI [cri-2025-hiaerspike] | Directly trained (SpikingJelly) | deployment | `hs_api` | CRI FPGA (physical) | accuracy, clock cycles, HBM accesses | E1/E2 |
| Imam and Cleland olfaction [imam-2020-olfaction] | Hand-designed, local plasticity | deployment | own pipeline | Loihi (physical) | latency, energy, accuracy | E1 |
| Tang, Shah, Michmizos SLAM [tang-2019-slam] | Hand-designed | deployment | own pipeline | Loihi (physical) | power vs. GMapping, accuracy | E1 |
| Spiking LCA [davies-2018-loihi] | Hand-designed | deployment | own pipeline | Loihi predecessor (physical) | EDP vs. CPU | E1 |
| LCA on Loihi 2 [parpart-2023-lca] | Hand-designed | deployment | own pipeline | Loihi 2 (physical) | efficiency vs. CPU/GPU | E1 |
| Convolutional LCA [convlca-2025-lca] | Hand-designed | deployment | own pipeline | Loihi 2 (physical) | latency, power, PSNR vs. GPU | E1 |
| SAT/CSP solver [satcsp-2020] | Hand-designed | deployment | own pipeline | Loihi (physical) | power | E1 |
| SDDPG navigation [patel-2020-sddpg] | Directly trained (gradient) | deployment | own pipeline | Loihi, Kapoho Bay (physical) | power, µJ/inference vs. Jetson TX2 | E1 |
| Force-control peg-in-hole [forcecontrol-2024] | Directly trained (spiking RL) | deployment | NxSDK / Lava | Loihi 1 and 2 (physical) | latency, energy vs. CPU/GPU | E1 |
| Kreiser et al. iCub [kreiser-2020-icub] | Hand-designed | deployment | own pipeline | Loihi, Kapoho Bay (physical) | accuracy (RMSE), latency | E2 |
| EMG classification [bezugam-2023-emg] | Directly trained | deployment | own pipeline | Loihi, Nahuku 32 (physical) | energy, latency vs. GPU | E1 |
| EMG classification [donati-2022-emg] | Directly trained | deployment | own pipeline | Loihi, Kapoho Bay (physical) | accuracy, latency, power | E1 |
| EMG+DVS fusion [ceolini-emg-dvs] | Directly trained | deployment | own pipeline | Loihi + ODIN/MorphIC (physical) | accuracy, EDP vs. GPU | E1 |
| EEG seizure prediction [eeg-seizure-2025] | Graded SNN, directly trained | deployment | own pipeline | Loihi 2 (physical) | accuracy, throughput, energy | E1 |
| EEG motor imagery [eeg-motor-imagery-repo] | Directly trained | deployment | NxSDK/Kapoho Bay | Loihi (physical) | self-reported energy claim | E1 (self-reported) |
| Automotive radar [radar-automotive-2026] | Directly trained/hand-designed | deployment | own pipeline | Loihi 2, vehicle-mounted (physical) | latency, throughput, power | E1 |
| Radar resonators [radar-resonator-2025] | Hand-designed | deployment | own pipeline | Loihi 2 (physical) | power vs. sparsity | E1 |
| Keyword spotting [blouw-2019-kws] | Directly trained | deployment | own pipeline | Loihi (research) | energy vs. CPU/GPU/Jetson | E1 |
| Kelber et al. VGG/ResNet [kelber-2020-spinnaker2sim] | Deployment mapping study | deployment | own pipeline | SpiNNaker2 (**timing simulator**, chip "not yet available") | inference time (simulated) | E4/E5 |
| Patiño-Saucedo et al. LeNet [patino-saucedo-2020-spinnaker] | Rate-coded ANN-SNN conversion | deployment | SNN Toolbox → sPyNNaker | SpiNNaker-103 (physical, 48 chips) | accuracy, latency | E1 |
| Patiño-Saucedo et al. STBP N-MNIST [patino-saucedo-2020-spinnaker] | Directly trained (STBP) | deployment | own pipeline | SpiNNaker-103 (physical) | accuracy | E1/E2 |
| Stromatias/O'Connor DBN [stromatias-2015-dbn] | DBN-to-SNN conversion, rate-coded | deployment | own pipeline | SpiNNaker (physical, 1 chip) | accuracy, power, latency | E1 |
| Galanis et al. [galanis-2020-spinnaker] | Conversion, design-space search | deployment | own pipeline | SpiNNaker (physical) | accuracy | E1/E2 |
| Pals et al. EEG [pals-2021-eeg-spinnaker] | Converted CNN | deployment | own pipeline | SpiNNaker (physical) | accuracy | E1 |
| Serrano-Gotarredona et al. ConvNets [serrano-2015-convnets] | Event-native SNN | deployment | own pipeline | SpiNNaker (physical) | architecture proof-of-concept | E1 |
| Arfa et al. DVS Gesture [arfa-2025-spinnaker2] | Directly trained, quantized | deployment | py-spinnaker2 + NIR | SpiNNaker2 (physical, 1 chip) | accuracy | E1 |
| Schmitt et al. BrainScaleS-1 [schmitt-2017-brainscales] | Rate-coded ANN-SNN conversion | deployment | own pipeline | BrainScaleS-1 (physical, wafer-scale) | accuracy, before/after HITL | E1 |
| Weis et al. BrainScaleS-2 CNN [weis-2020-brainscales2] | Non-spiking analog MAC mode | deployment | hxtorch | BrainScaleS-2 (physical) | accuracy, before/after HITL | E1 |
| Stradmann et al. mobile ECG [stradmann-2021-mobile] | Non-spiking analog MAC mode | deployment | hxtorch | BrainScaleS-2 mobile (physical) | latency, energy, power, accuracy | E1 |
| Cramer et al. surrogate gradient [cramer-2022-surrogate] | Directly trained (surrogate gradient) | deployment | hxtorch.snn | BrainScaleS-2 (physical) | accuracy, latency, energy, throughput | E1 |
| SyncNN [syncnn-2022] | Rate-coded IF conversion, own reformulation | both | Vitis HLS/SDSoC | Xilinx FPGA boards (physical, 3 boards) | accuracy, throughput | E1 |
| Spiker [spiker-2022] | STDP, LIF, hard reset | deployment | own pipeline | Xilinx Artix-7 (physical) | latency, energy | E1 |
| Spiker+ [spikerplus-2024] | IF/LIF, selectable reset (novel framework) | both | own pipeline, snnTorch | Xilinx FPGA (physical) | accuracy, latency, power | E1 |
| Cerebron [cerebron-2022] | SNNtoolbox-based conversion | deployment | SNN Toolbox | Xilinx XC7Z100 (physical) | accuracy, latency, energy | E1 |
| PASCAL [pascal-2025] | Exact QCFS-SNN equivalence (novel) | algorithm | own pipeline | analytical model only | energy ratio (analytical) | E5 (E4 unreported) |
| APEX [apex-2026] | PASC-IF neuron, RTL realization | both | Synopsys Design Compiler | 40 nm synthesis + cycle sim (unfabricated) | power, area, energy vs. LoAS baseline | E4 |
| NeuroFlex [neuroflex-2025] | PASC-IF neuron, column-hybrid | both | Synopsys Design Compiler | 40 nm synthesis + cycle sim (unfabricated) | PE utilization | E4 |
| TrueNorth+DVS128 gesture [amir-2017-truenorth-gesture] | Genuinely spiking, sensor-to-chip | deployment | Eedn/Corelet | TrueNorth (physical) | latency, power, accuracy | E1 |
| SynSense Speck gesture [synsense-speck-gesture-datasheet] | Genuinely spiking, sensor-to-chip | deployment | Sinabs | Speck (physical) | power, latency | E1 (vendor datasheet) |
| GelNeuro tactile [gelneuro-2026] | Genuinely spiking, sensor-to-chip | deployment | Sinabs | Speck2f (physical) | accuracy, latency, power | E1 |
| DYNAP-SE iCub [dynapse-icub-2020] | Hand-designed, closed-loop control | deployment | own pipeline | DYNAP-SE (physical) | step response | E1 |
| DYNAP-SE tactile [ortone-2026-tactile] | Genuinely spiking, sensor-to-chip | deployment | own pipeline | DYNAP-SE (physical) | localization error, power | E1 |
| SpiNNaker goalkeeper [cheng-2020-goalkeeper] | Genuinely spiking, sensor-to-chip | deployment | sPyNNaker | SpiNNaker (physical) | latency, accuracy, power | E1 |
| Xylo keyword spotting [bos-2024-xylo] | Directly trained | deployment | Rockpool | XyloAudio 2 (physical) | accuracy, power, energy | E1 |
| Adaptive Fission [jiang-2025-adaptive-fission] | Population coding (novel), QCFS/SRP as baseline | both | own pipeline | Lynxi HP201 (physical) | latency, energy, accuracy (incl. QCFS/SRP baseline rows) | E1 |

**Aggregate counts.** Among the QCFS-lineage low-latency conversion papers audited
directly against full text, 13 of 13 report pure software simulation as their own result,
and 0 of 13 report an experiment executed on named physical or synthesized hardware
[a17-two-populations]. Among the classical ANN-to-SNN conversion algorithm papers audited
separately, 0 of 9 reach silicon [a17-two-populations]. Among the broader 16-paper
QCFS-lineage sample audited in a companion pass, the same 0-of-16 finding holds
[a17-two-populations]. On the reverse edge, 0 of 4 hardware-deployment papers audited
(Stromatias 2015, Patiño-Saucedo 2020, Massa 2020, NxTF 2021) cite or use any post-2020
low-latency conversion method, and every one uses either the classical SNN Toolbox
pipeline or direct SLAYER/STBP training, rate-coded throughout
[a17-two-populations]. **Two qualifications the research established, and which the
survey states rather than smooths over.** First, QCFS itself is the single exception in
its own lineage: it cites two physical-hardware papers, Massa et al. 2020 and Singh et
al.'s Gesture-SNN, in its related work as acknowledged prior art, not motivational
framing, while 12 of its 13 audited descendants cite hardware only in the introduction as
generic motivation and never as executed prior art [a17-two-populations]. Second,
Adaptive Fission, a NeurIPS 2025 paper whose own algorithmic contribution is population
coding, a non-rate-coded scheme, reports rate-coded QCFS and SRP baseline configurations
measured on physical Lynxi HP201 silicon inside its own Table 1, alongside its own
fission-modified results [jiang-2025-adaptive-fission]. This means a rate-coded
QCFS-lineage output has, in fact, touched physical neuromorphic silicon once, not in
QCFS's or SRP's own papers, which remain E5, but as a baseline row inside a different
paper whose own innovation abandons rate coding. The defensible claim is therefore not
that rate-coded QCFS output has never touched silicon under any circumstances, but that no
QCFS-lineage paper deploys its own method to silicon, and the one time it happened, it
took a different research group's non-rate-coding innovation to motivate doing so
[jiang-2025-adaptive-fission], [a17-two-populations].

## 7.7 Measurement and comparability

Reported efficiency numbers across this literature are not comparable to one another, for
reasons that recur across every platform surveyed above.

**SynOps estimates establish an operation-count ratio, not joules.** The "0.9 pJ MAC,
0.1 pJ AC" figures cited across most SNN papers trace to a single ISSCC 2014 plenary
talk's Table 1.1.9, reporting rough energy costs for a 45 nm process at 0.9 V
[horowitz-2014]. The talk itself stresses that computation is a minority of total system
energy once memory access is included, and that a programmable processor's per-instruction
overhead, roughly 70 pJ per instruction from fetch and register clocking, dwarfs the
per-operation figure entirely [horowitz-2014]. Multiple independent, hardware-realistic
studies confirm the gap this produces is large and systematic. Bhattacharjee et al.
benchmark published SNN algorithms on two hardware-realistic accelerator models and find
"the actual energy-efficiency improvements of recent SNN algorithmic works differ
significantly from their estimated values due to various hardware bottlenecks"
[bhattacharjee-2023-hardware]. Shen et al. propose replacing the timestep-versus-bit-width
asymmetry with a unified "Bit Budget" metric precisely because SNN papers are routinely
compared against unquantized, rather than similarly optimized, ANN baselines
[shen-2024-bitbudget]. A SynOps-based energy number establishes, at best, a relative
operation-count ratio under an implicit, usually unstated hardware model, one process
node, one precision, no memory-access cost, no neuron-state-update cost, and no routing
cost.

**Static and leakage power dominate measured energy on synchronous chips, so reducing `T`
does not reduce energy proportionally.** A sigma-delta conversion study on Loihi 2
varies effective sparsity and reports throughput improving substantially, from 176 to 362
FPS, while "total power usage... remained relatively consistent for all experiments as it
is dominated by static draw" [brehove-2026]. A separate LCA study on Loihi 2 measures
static power essentially constant near 0.54 W across all sparsity settings, nearly double
the dynamic power even at the sparsest, most favorable operating point
[parpart-2023-lca]. On a synchronous, clocked digital chip with SRAM-resident weights and
state, static power is drawn continuously for the full duration a network is mapped and
powered, independent of how much useful spiking work a given timestep performs, so cutting
`T` reduces only the dynamic term and can even increase energy per inference if the
reduction also reduces the throughput benefit of parallelism across a fixed static floor.

**Measurement-boundary choices alone produce large swings for the identical chip and
network.** Shrestha et al.'s PilotNet benchmark on Loihi 2 reports **0.09 mJ total energy
and 1.21 ms latency with weights pre-staged and no host I/O counted, against 1.26 mJ and
65.41 ms with streaming host I/O included, a 14-fold difference in energy and a 54-fold
difference in latency for the same chip and the same network**, purely as a function of
where the measurement window is drawn [shrestha-2023-video-audio]. Static power dominates
the IO-limited configuration so completely that over 94% of the reported 1.26 mJ is static
or leakage, not spiking computation [shrestha-2023-video-audio]. Intel's own recommended
reporting convention, followed by later independent papers citing the same source, reports
static, dynamic, and total power separately and computes EDP from the total, precisely
because a headline "dynamic energy" figure by construction excludes the leakage
contribution that this boundary problem shows can dominate the true total
[shrestha-2023-video-audio].

**When neuromorphic hardware wins and when it does not, in the architects' own words.**
Davies et al.'s survey of Loihi results states the finding directly in its abstract:
"conventional feedforward deep neural networks show modest if any benefit on Loihi,"
while "more brain-inspired networks using recurrence, precise spike-timing relationships,
synaptic plasticity, stochasticity, and sparsity perform certain computation with orders
of magnitude lower latency and energy" [davies-2021-loihi]. The same paper states that it
"would be naïve to expect SNNs to outperform ANN accelerators on the very task that they
have been optimized for," and that per-synaptic-operation energy on Loihi is in practice
greater than a MAC on a dedicated ANN accelerator, because of the overhead of supporting
sparse, event-driven, time-and-space-sparse computation that a dense accelerator does not
have to pay for [davies-2021-loihi].

**Quantizing the ANN baseline alone closes much of the reported gap.** Shrestha et al.
report both floating-point and int8-quantized ANN baselines for PilotNet on a Jetson Orin
Nano alongside the Loihi 2 int8 result. Quantizing the ANN from fp32 to int8 at batch size
1 on the identical GPU **cuts its energy from 21.94 mJ to 13.72 mJ, roughly 37%, and cuts
its energy-delay product from 126.69 µJ·s to 47.08 µJ·s, a 63% reduction**, before Loihi's
own numbers change at all [shrestha-2023-video-audio]. Loihi 2 still shows an
order-of-magnitude-plus advantage over the int8, batch-1 ANN baseline for this specific
workload, but a substantial fraction of the advantage claimed against an unquantized
baseline evaporates once the ANN side is quantized to the same precision the SNN uses,
and the workload itself, a small regression CNN with sparse sigma-delta activations, sits
close to the sparse, low-dynamic-range regime Davies et al. identify as Loihi's favorable
case, not a generic large-scale classifier [shrestha-2023-video-audio],
[davies-2021-loihi].

---

## References for Section 7

- [rueckauer-2021-nxtf] Rueckauer, B., Bybee, C., Goettsche, R., Singh, Y., Mishra, J.,
  Wild, A. "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi."
  arXiv:2101.04261 (2021); *ACM JETC* (2022), https://doi.org/10.1145/3501770.
  Peer-reviewed.
- [massa-2020] Massa, R., Marchisio, A., Martina, M., Shafique, M. "An Efficient Spiking
  Neural Network for Recognizing Gestures with a DVS Camera on the Loihi Neuromorphic
  Processor." IJCNN 2020. https://doi.org/10.1109/ijcnn48605.2020.9207109.
  Peer-reviewed.
- [singh-2021-gesture-snn] Singh, S., Sarma, A., Lu, N., Sengupta, A., Narayanan, V., Das,
  C. R. "Gesture-SNN: Co-optimizing accuracy, latency and energy of SNNs for neuromorphic
  vision sensors." ISLPED 2021. https://doi.org/10.1109/islped52811.2021.9502506.
  Peer-reviewed.
- [bu-2022-qcfs] Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN
  Conversion for High-accuracy and Ultra-low-latency Spiking Neural Networks." ICLR 2022,
  arXiv:2303.04347. Peer-reviewed (conference).
- [lenz-2023-quartz] Lenz, G., Orchard, G., Sheik, S. "Ultra-low-power Image Classification
  on Neuromorphic Hardware." arXiv:2309.16795 (2023-2024). Preprint.
- [brehove-2026] Brehove, T., Tumpa, S. N., Kyubwa, E., Menon, A., Narayanan, V.
  "Sigma-Delta Neural Network Conversion on Loihi 2." ICONS 2026, arXiv:2505.06417.
  Peer-reviewed (conference).
- [shrestha-2023-video-audio] Shrestha, S. B., Timcheck, J., Frady, P., Campos-Macías, L.,
  Davies, M. "Efficient Video and Audio Processing with Loihi 2." arXiv:2310.03251;
  ICASSP 2024, https://doi.org/10.1109/icassp48485.2024.10448003. Peer-reviewed
  (conference).
- [boeshertz-2024-rnn] Boeshertz, G., Indiveri, G., Nair, M. V., Renner, A. "Accurate
  Mapping of RNNs on Neuromorphic Hardware with Adaptive Spiking Neurons."
  arXiv:2407.13534 (2024). Preprint.
- [meszaros-2025-delays] Mészáros, B., Knight, J. C., Timcheck, J., Nowotny, T. "A
  Complete Pipeline for deploying SNNs with Synaptic Delays on Loihi 2." arXiv:2510.13757
  (2025). Preprint.
- [clp-snn-2025] "Online Continual Learning on Intel Loihi 2 via a Co-designed Spiking
  Neural Network." arXiv:2511.01553 (2025). Preprint.
- [spikingjelly-loihi2-2026] "Real-Time Frame- and Event-based Object Detection with
  Spiking Neural Networks on Edge Neuromorphic Hardware: Design, Deployment and
  Benchmark." 2026 preprint; code at
  github.com/gwgknudayanga/Realtime-frame--and-event-based-detection-with-SNN-on-Neuromorphic-hardware.
  Preprint; code repository is repository state.
- [cri-2025-hiaerspike] UCSD Institute for Neural Sensors, "DVS128 Gesture Inference on
  HiAER-Spike Hardware." isn.ucsd.edu/hiaer-spike/auto_examples/plot_dvs_gesture_inference.html.
  Official documentation.
- [imam-2020-olfaction] Imam, N., Cleland, T. A. "Rapid online learning and robust recall
  in a neuromorphic olfactory circuit." *Nature Machine Intelligence* 2 (2020),
  arXiv:1906.07067. Peer-reviewed.
- [dennler-2023-olfaction-critique] Dennler, N., van Schaik, A., Schmuker, M.
  "Limitations in odour recognition and generalisation in a neuromorphic olfactory
  circuit." arXiv:2309.11555 (2023). Preprint.
- [tang-2019-slam] Tang, G., Shah, A., Michmizos, K. P. "Spiking Neural Network on
  Neuromorphic Hardware for Energy-Efficient Unidimensional SLAM." arXiv:1903.02504
  (2019). Preprint.
- [davies-2018-loihi] Davies, M., Srinivasa, N., Lin, T.-H., Chinya, G. N., et al. "Loihi:
  A Neuromorphic Manycore Processor with On-Chip Learning." *IEEE Micro* 38(1), 82-99
  (2018), https://doi.org/10.1109/mm.2018.112130359. Peer-reviewed.
- [parpart-2023-lca] Parpart, G., Risbud, S., Kenyon, G., Watkins, Y. "Implementing and
  Benchmarking the Locally Competitive Algorithm on the Loihi 2 Neuromorphic Processor."
  arXiv:2307.13762 (2023). Preprint.
- [convlca-2025-lca] "Convolutional Sparse Coding via the Locally Competitive Algorithm on
  Loihi 2." arXiv preprint (2025/2026). Preprint.
- [satcsp-2020] "Solving Constraint Satisfaction Problems Using the Loihi Processor."
  DATE 2020 workshop paper. Peer-reviewed (workshop).
- [patel-2020-sddpg] "Reinforcement co-Learning of Deep and Spiking Neural Networks for
  Energy-Efficient Mapless Navigation with Neuromorphic Hardware." arXiv:2003.01157
  (2020). Preprint.
- [forcecontrol-2024] "Neuromorphic force-control in an industrial task: validating energy
  and latency benefits." arXiv:2403.08928 (2024). Preprint.
- [kreiser-2020-icub] Kreiser, R., Renner, A., et al., Sandamirskaya, Y. "An On-chip
  Spiking Neural Network for Estimation of the Head Pose of the iCub Robot." *Frontiers in
  Neurorobotics* (2020). Peer-reviewed.
- [bezugam-2023-emg] Bezugam, S. S., et al. "Neuromorphic Recurrent SNNs for EMG Gesture
  Classification on Loihi." ISCAS 2023, https://doi.org/10.1109/iscas46773.2023.10181510;
  earlier version arXiv:2206.02061 (2022). Peer-reviewed.
- [donati-2022-emg] Vitale, A., Donati, E., Germann, R., Magno, M. "Neuromorphic Edge
  Computing for Biomedical Applications: EMG Gesture Classification." *IEEE Sensors
  Journal* (2022), https://doi.org/10.1109/jsen.2022.3194678. Peer-reviewed.
- [ceolini-emg-dvs] Ceolini, E., et al. "Hand-Gesture Recognition Based on EMG and
  Event-Based Camera Sensor Fusion." https://pmc.ncbi.nlm.nih.gov/articles/PMC7438887/.
  Peer-reviewed.
- [eeg-seizure-2025] "Predicting EEG seizures using graded spiking neural networks on
  Loihi 2." *Journal of Neural Engineering* (2025),
  https://beta.iopscience.iop.org/article/10.1088/1741-2552/adb455. Peer-reviewed.
- [eeg-motor-imagery-repo] combra-lab/snn-eeg. github.com/combra-lab/snn-eeg. Repository
  state, self-reported claim not independently re-verified.
- [radar-automotive-2026] "Towards real-time neuromorphic radar processing on Loihi 2."
  *Neuromorphic Computing and Engineering* (2026),
  https://google.iopscience.iop.org/article/10.1088/2634-4386/ae8694. Peer-reviewed.
- [radar-resonator-2025] "Energy-efficient radar detection with spiking neural resonators
  on Loihi 2." *Neuromorphic Computing and Engineering*,
  https://iopscience.iop.org/article/10.1088/2634-4386/ae629d. Peer-reviewed.
- [blouw-2019-kws] Blouw, P., et al. "Benchmarking Keyword Spotting Efficiency on
  Neuromorphic Hardware." ACM NICE 2019, https://doi.org/10.1145/3320288.3320304.
  Peer-reviewed.
- [lava-archived-2026] Lava-nc GitHub organization, archive banner on `lava`, `lava-dl`,
  `lava-dnf` repositories, 2026. github.com/lava-nc/lava. Repository state.
- [intel-2021-loihi2-brief] Intel Corporation. "Taking Neuromorphic Computing to the Next
  Level with Loihi 2." Technical brief.
  intel.com/content/dam/www/central-libraries/us/en/documents/neuromorphic-computing-loihi-2-brief.pdf.
  Vendor material.
- [davies-2021-loihi] Davies, M., Wild, A., Orchard, G., Sandamirskaya, Y., Fonseca
  Guerra, G. A., Joshi, P., Plank, P., Risbud, S. R. "Advancing Neuromorphic Computing
  With Loihi: A Survey of Results and Outlook." *Proceedings of the IEEE* 109(5), 911-934
  (2021), https://doi.org/10.1109/jproc.2021.3067593. Peer-reviewed.
- [sinabs-docs-overview] SynSense/Sinabs documentation, "Overview" (Speck) and related
  API/discretization pages. sinabs.readthedocs.io. Official documentation.
- [richter-2023-speck] Richter, O., Xing, Y., De Marchi, M., Nielsen, C., Katsimpris, M.,
  Cattaneo, R., Ren, Y., Hu, Y., Liu, S.-C., Sheik, S., Demirci, T., Qiao, N. "Speck: A
  Smart event-based Vision Sensor with a low latency 327K Neuron Convolutional Neural
  Network Processing Pipeline." arXiv:2304.06793 (2023). Preprint.
- [yao-2024-speck] Yao, M., Richter, O., Zhao, G., Qiao, N., Xing, Y., Wang, D., Hu, T.,
  Fang, W., Demirci, T., De Marchi, M., Deng, L., Yan, T., Nielsen, C., Sheik, S., Wu, C.,
  Tian, Y., Xu, B., Li, G. "Spike-based dynamic computing with asynchronous
  sensing-computing neuromorphic chip." *Nature Communications* 15:4464 (2024),
  https://doi.org/10.1038/s41467-024-47811-6. Peer-reviewed.
- [liu-2019-facerecognition] Liu, Q., Richter, O., Nielsen, C., Sheik, S., Indiveri, G.,
  Qiao, N. "Live Demonstration: Face Recognition on an Ultra-Low Power Event-Driven
  Convolutional Neural Network ASIC." CVPRW 2019. Peer-reviewed (workshop).
- [riverpub-mcu-chapter] "Deploying a Convolutional Neural Network on Edge MCU and
  Neuromorphic Hardware Platforms." River Publishers book chapter.
  riverpublishers.com/pdf/ebook/chapter/RP_9788770227902C10.pdf. Peer-reviewed.
- [bos-2024-xylo] Bos, H., Muir, D. "Micro-power spoken keyword spotting on Xylo Audio 2."
  arXiv:2406.15112 (2024). Preprint.
- [patino-saucedo-2020-spinnaker] Patiño-Saucedo, A., Rostro-González, H.,
  Serrano-Gotarredona, T., Linares-Barranco, B. "Event-driven implementation of deep
  spiking convolutional neural networks for supervised classification using the SpiNNaker
  neuromorphic platform." *Neural Networks* 121, 319-328 (2020),
  https://doi.org/10.1016/j.neunet.2019.09.008. Peer-reviewed.
- [stromatias-2015-dbn] Stromatias, E., Neil, D., Galluppi, F., Pfeiffer, M., Liu, S.-C.,
  Furber, S. "Scalable Energy-Efficient, Low-Latency Implementations of Spiking Deep
  Belief Networks on SpiNNaker." IJCNN 2015. Peer-reviewed (conference).
- [galanis-2020-spinnaker] Galanis, I., Anagnostopoulos, I., Nguyen, C. K., Bares, G.
  "Efficient Deployment of Spiking Neural Networks on SpiNNaker Neuromorphic Platform."
  *IEEE Trans. Circuits and Systems II* (2020), https://doi.org/10.1109/tcsii.2020.3047425.
  Peer-reviewed.
- [pals-2021-eeg-spinnaker] Pals, M., Perez Belizon, R. J., Berberich, N., Ehrlich, S. K.,
  Nassour, J., Cheng, G. "Demonstrating the Viability of Mapping Deep Learning Based EEG
  Decoders to Spiking Networks on Low-powered Neuromorphic Chips." IEEE EMBC 2021,
  https://doi.org/10.1109/embc46164.2021.9629621. Peer-reviewed.
- [serrano-2015-convnets] Serrano-Gotarredona, T., Linares-Barranco, B., Galluppi, F.,
  Plana, L. A., Furber, S. "ConvNets experiments on SpiNNaker." ISCAS 2015,
  https://doi.org/10.1109/iscas.2015.7169169. Peer-reviewed.
- [kelber-2020-spinnaker2sim] Kelber, F., Wu, B., Vogginger, B., Partzsch, J., Liu, C.,
  Stolba, M., Mayr, C. "Mapping Deep Neural Networks on SpiNNaker2." NICE '20 Workshop,
  ACM (2020), https://doi.org/10.1145/3381755.3381778. Peer-reviewed (workshop).
- [arfa-2025-spinnaker2] Arfa, S., Vogginger, B., Liu, C., Partzsch, J., Schöne, M., Mayr,
  C. "Efficient Deployment of Spiking Neural Networks on SpiNNaker2 for DVS Gesture
  Recognition Using Neuromorphic Intermediate Representation." NICE 2025,
  https://doi.org/10.1109/nice65350.2025.11065119; arXiv:2504.06748. Peer-reviewed.
- [schmitt-2017-brainscales] Schmitt, S., Klähn, J., Bellec, G., Grübl, A., et al. (incl.
  Schemmel, Meier, Petrovici, Maass, Legenstein). "Neuromorphic Hardware In The Loop:
  Training a Deep Spiking Network on the BrainScaleS Wafer-Scale System." 2017,
  arXiv:1703.01909. Preprint.
- [weis-2020-brainscales2] Weis, J., Spilger, P., et al. "Inference with Artificial Neural
  Networks on Analog Neuromorphic Hardware." arXiv:2006.13177 (2020). Preprint.
- [stradmann-2021-mobile] Stradmann, Y., Billaudelle, S., et al. "Demonstrating Analog
  Inference on the Mobile System." arXiv:2103.15960 (2021). Preprint.
- [cramer-2022-surrogate] Cramer, B., Billaudelle, S., Kanya, S., Leibfried, A., Grübl,
  A., Karasenko, V., Pehle, C., Schreiber, K., Stradmann, Y., Weis, J., Schemmel, J.,
  Zenke, F. "Surrogate gradients for analog neuromorphic computing." *PNAS* (2022),
  arXiv:2006.07239. Peer-reviewed.
- [syncnn-2022] Panchapakesan, S., Fang, Z., Li, J. "SyncNN: Evaluating and Accelerating
  Spiking Neural Networks on FPGAs." FPL 2021; *ACM TRETS* (2022),
  https://doi.org/10.1145/3514253. Peer-reviewed.
- [spiker-2022] Carpegna, A., Savino, A., Di Carlo, S. "Spiker: an FPGA-optimized Hardware
  accelerator for Spiking Neural Networks." ISVLSI 2022, arXiv:2201.06993. Peer-reviewed
  (conference).
- [spikerplus-2024] Carpegna, A., Savino, A., Di Carlo, S. "Spiker+: A Framework for the
  Generation of Efficient Spiking Neural Networks FPGA Accelerators for Inference at the
  Edge." *IEEE TETC* (2024), https://doi.org/10.1109/tetc.2024.3511676; arXiv:2401.01141.
  Peer-reviewed.
- [cerebron-2022] Chen, S., Gao, M., Fu, J. "Cerebron: A Reconfigurable Architecture for
  Spatiotemporal Sparse Spiking Neural Networks." *IEEE TVLSI* (2022),
  https://doi.org/10.1109/tvlsi.2022.3196839. Peer-reviewed.
- [pascal-2025] Ramesh, P., Srinivasan, G. "PASCAL: Precise and Efficient ANN-SNN
  Conversion using Spike Accumulation and Adaptive Layerwise Activation." *Transactions on
  Machine Learning Research* (2025), arXiv:2505.01730. Peer-reviewed.
- [apex-2026] Manjunath, V., et al. (incl. Srinivasan, G.). "APEX: A Dual-Sparsity
  Accelerator for Precise and Efficient SNN Inference." arXiv:2608.19046 (2026). Preprint.
- [neuroflex-2025] Manjunath, V., et al. "NeuroFlex: a flexible ANN-SNN accelerator for
  sparse edge inference." arXiv:2511.05215 (2025). Preprint.
- [v2v-2025] "V2V: Scaling Event-Based Vision through Efficient Video-to-Voxel
  Simulation." NeurIPS 2025. Peer-reviewed (conference).
- [eventvision-survey-2023] "Deep Learning for Event-based Vision: A Comprehensive Survey
  and Benchmarks." *IEEE TPAMI*, arXiv:2302.08890. Peer-reviewed.
- [prophesee-docs-detection] Prophesee, "Detection and Tracking Tutorial," Metavision SDK
  documentation. docs.prophesee.ai. Official documentation.
- [prophesee-2025-pedestrian] Prophesee, "Pedestrian Detection with High-Resolution Event
  Cameras" (2025). prophesee.ai/2025/02/07/pedestrian-detection-high-resolution-event-camera/.
  Vendor material.
- [a14-application-survey] A14 research pass, "Real Neuromorphic Applications and
  Event-Based Sensing," internal synthesis of ~20 application papers surveyed against
  compute-platform category. Internal research synthesis, sources as cited within.
- [prophesee-genx320-docs] Prophesee, GenX320 product catalogue and RidgeRun GenX320
  developer guide. prophesee.ai; ridgerun.com. Vendor material.
- [eetimes-graimatter] EE Times, "GrAI Matter Raises $14M for Sparsity-Driven AI SoC."
  eetimes.com/grai-matter-raises-14m-for-sparsity-driven-ai-soc/. Community commentary
  (trade press, direct company interview quote).
- [neuronflow-2020] Moreira, O., et al. "NeuronFlow: A Hybrid Neuromorphic-Dataflow
  Processor Architecture." AICAS 2020, https://doi.org/10.1109/aicas48895.2020.9073999.
  Peer-reviewed.
- [kria-prophesee-vitisai] LogicTronixInc/Kria-Prophesee-Event-VitisAI. GitHub repository.
  github.com/LogicTronixInc/Kria-Prophesee-Event-VitisAI. Repository state.
- [bonazzi-2025-fpgadrone] Bonazzi, P., et al. "Towards Low-Latency Event-based Obstacle
  Avoidance on a FPGA-Drone." CVPR-W 2025. Peer-reviewed (workshop).
- [amir-2017-truenorth-gesture] Amir, A., Taba, B., Berg, D., et al. "A Low Power, Fully
  Event-Based Gesture Recognition System." CVPR 2017,
  https://doi.org/10.1109/cvpr.2017.781. Peer-reviewed.
- [synsense-speck-gesture-datasheet] SynSense, "Speck Gesture Recognition" product
  datasheet. synsense.ai/wp-content/uploads/.../Speck-Gesture-recognition.pdf. Vendor
  material.
- [gelneuro-2026] "GelNeuro" (2026). pubdb.com/paper/2607.05241. Peer-reviewed.
- [dynapse-icub-2020] "Closed-loop spiking control on a neuromorphic processor implemented
  on the iCub." arXiv:2009.09081 (2020). Preprint.
- [ortone-2026-tactile] Ortone, A., et al. "Bioinspired spiking architecture enables
  energy constrained touch encoding." *Nature Communications* (2026),
  https://doi.org/10.1038/s41467-026-68858-7. Peer-reviewed.
- [cheng-2020-goalkeeper] Cheng, Y., Nikolić, D. "System integration of neuromorphic
  DVS+SpiNNaker+servomotor robot." TechRxiv (2020),
  https://doi.org/10.36227/techrxiv.11854254. Preprint.
- [jiang-2025-adaptive-fission] Jiang, Y., et al. "Adaptive Fission." NeurIPS 2025
  proceedings. Peer-reviewed (conference). Code repository
  github.com/JiangYizhou16/Adaptive-Fission is repository state, not independently
  re-verified.
- [a17-two-populations] A17 research pass, "Two Populations: Testing the Division-of-Labor
  Claim," internal audit of citation direction, toolchain freeze, and shared artifacts
  across the QCFS-lineage algorithm literature and the hardware-deployment literature.
  Internal research synthesis, sources as cited within.
- [horowitz-2014] Horowitz, M. "1.1 Computing's Energy Problem (and what we can do about
  it)." ISSCC 2014, https://doi.org/10.1109/ISSCC.2014.6757323. Peer-reviewed
  (conference).
- [bhattacharjee-2023-hardware] Bhattacharjee, A., Yin, R., Moitra, A., Panda, P. "Are
  SNNs Truly Energy-efficient? A Hardware Perspective." arXiv:2309.03388 (2023). Preprint.
- [shen-2024-bitbudget] Shen, G., Zhao, D., Li, T., Li, J., Zeng, Y. "Are Conventional
  SNNs Really Efficient? A Perspective from Network Quantization." CVPR 2024.
  Peer-reviewed (conference).


---

# 8 Challenges and Future Directions

Each subsection below is a seam: a point where a trained network passes from one layer of the
stack to the next and something is lost. Each becomes a numbered pin in the survey's main figure,
linking the layer bands to the specific mechanism that breaks at that handoff.

## 8.1 Operator coverage in SNN toolchains

Every documented software path from a trained network to physical silicon accepts a narrower set
of operators than a standard vision CNN uses, and closing the gap is architectural rewriting, not
configuration.

SpikingJelly's `lava_exchange` module, the only first-party bridge from SpikingJelly to Loihi,
dispatches on layer type and handles exactly four cases: `nn.Linear`, `nn.Conv2d`, `nn.AvgPool2d`
(rewritten internally as a Lava `SumPool2d`), and `nn.Flatten`. Anything else raises
`ValueError(type(net[i]))` or `NotImplementedError(type(net[i]))` [fang-2023-spikingjelly-lava]
[jelly-lava-source]. A VGG-family network hits this immediately, since VGG's canonical pooling is
`nn.MaxPool2d`, which the dispatch does not handle. A ResNet hits it at every residual addition,
since no elementwise-add or skip-connection handling appears in the operator dispatch, and again
at any `BatchNorm2d` layer not already fused away before export [jelly-lava-source]. The module
also asserts no bias term on exported `Conv2d`/`Linear` layers and rejects any LIF neuron with
`decay_input=True` [jelly-lava-source].

Sinabs, SynSense's PyTorch library for the Speck/DYNAP-CNN line, does fold BatchNorm
automatically, just not inside the `discretize` module. Speck itself has no BatchNorm
operator, so `DynapcnnNetwork`'s graph extractor calls `handle_batchnorm_nodes`, which
merges `BatchNorm2d`/`BatchNorm1d` layers into the preceding `Conv2d`/`Linear` layer via
`merge_bn` (`sinabs.backend.dynapcnn.utils`), automatically and before the model reaches
the chip [sinabs-discretize-api]. The `discretize` module's own public functions
(`discretize_conv`, `discretize_conv_spike`, `discretize_spk`) operate only on
`(Conv2d, IAF)` pairs and carry no `discretize_bn` or `fold_bn` counterpart, because
BatchNorm folding already happened earlier, in the graph extractor, not in discretization
[sinabs-discretize-api]. Sinabs's own hardware-targeted tutorials still avoid the
question by construction, building bias-free convolutional layers followed directly by
IF layers with no BatchNorm in the architecture at all [sinabs-nmnist-tutorial]. A
`Conv2d` bias, where present, is repurposed on-chip as the per-timestep leak current
rather than an ordinary additive bias, a further departure from what a standard trained
CNN expects [sinabs-nmnist-tutorial].

BrainChip's Akida, evaluated here only as a constraint-list illustration and not as a deployment
target this survey otherwise covers, documents perhaps the most exhaustive operator contract of
any platform reviewed. Input width must fall between 5 and 256 pixels; exceeding 256 forces the
convolutional layers back onto software execution, a silent performance cliff rather than a hard
failure. Input channels are restricted to 1 or 3. Activations must be a bounded ReLU
(`ReLU(max_value=6.0)`) expressed as a separate layer; an unbounded `QuantizedReLU` raises
`ValueError: unbounded QuantizedReLU is not supported in AkidaVersion.v1`. All convolutional
layers after the first must use `'same'` padding only, a `'valid'`-padded intermediate layer
raises `RuntimeError`, and no dilated or grouped convolutions are supported at all. Dense layers
must receive a spatially flattened input, with total input features capped at 57,334
[akida-hw-constraints]. This is the contract of a quantized, integer-only CNN accelerator with a
strict graph-compiler front end, comparable in spirit to a TFLite Micro or TensorRT deployment
target, not a general-purpose spiking-network simulator willing to accept an arbitrary topology
[akida-hw-constraints].

The older SNN Toolbox pipeline, by contrast, supports max-pooling natively, offering a choice of
three spiking approximations (`fir_max`, `exp_max`, `avg_max`), and extracts BatchNorm parameters
directly from the source Keras layer for fusion into the preceding convolution
[rueckauer-2017-frontiers] [snntoolbox-docs]. Its operator coverage is broader on exactly the two
axes (max-pooling, BatchNorm) that the newer, purpose-built export paths above either drop or push
back onto the user. No toolchain surveyed accepts a standard VGG or ResNet as trained; every one
requires either an architectural rewrite before conversion (avg-pool in place of max-pool, no
BatchNorm, bounded activations, same-padding-only convolutions) or a bespoke translation step
after it.

## 8.2 Reset-semantics mismatch

This is the sharpest finding in the survey. ANN-to-SNN conversion under IF neurons requires reset
by subtraction, not reset to a fixed value. Rueckauer et al. derive analytically that reset to zero
discards a systematic, input-dependent residual charge at every spike, a bias that compounds
across layers rather than averaging out with longer simulation; reset by subtraction instead
carries that residual into the next integration window, and the firing-rate estimator converges
exactly to the target ReLU activation as `T → ∞` [rueckauer-2017-frontiers]. Their own CIFAR-10
ablation, switching only the reset mechanism while holding Poisson input and weight normalization
fixed, improves accuracy by roughly twenty percentage points [rueckauer-2017-frontiers]. This
result is now treated as settled practice throughout the conversion literature
[wang-2023-ijcai-snm] [hao-2023-aaai-srp].

Despite this, the interoperability layer built after the fact does not carry the mechanism. NIR's
own primitive specification defines the reset rule for its Integrate-and-Fire and LIF primitives
as reset to a fixed target value (`v ← v_reset` if spiking, `v` otherwise); the published primitive
table contains no subtract-reset primitive [pedersen-2024-nir]. The gap is not theoretical.
snnTorch's neuron classes internally implement subtract-reset but historically exported
`v_reset = 0` to NIR, silently discarding the distinction, a bug tracked in two separate pull
requests against the reference exporter [snntorch-pr-388] [snntorch-pr-426]. SpikingJelly's own
exporters go further and refuse the case outright: `lava_exchange.py` raises `ValueError('lava
only supports for v_reset == 0!')` at four separate call sites, and asserts the same (with a
different message) for its `CubaLIFNode` path; its `nir_exchange/to_nir.py` raises
`NotImplementedError("NIR does not distinguish soft reset.")` whenever `v_reset is None`
[jelly-lava-source] [jelly-nir-source]. A network converted by SpikingJelly's own `ann2snn`
module, which itself defaults to soft reset, cannot be handed to either of SpikingJelly's own
export modules without either re-parameterizing to hard reset, and reintroducing the
twenty-point cost above, or writing new code [jelly-lava-source].

On hardware, the picture splits three ways. Loihi 1 and Loihi 2 hard-reset the membrane voltage to
zero natively, in a single compartment [pehle-2022-bmtk]. NxTF's compiler works around this with a
two-compartment neuron: one compartment plays the soma, the second is recurrently connected and
activates only once the soma crosses threshold, then inhibits the soma by an amount equal to the
threshold, reproducing subtraction at the cost of doubling the compartment count per neuron
[rueckauer-2022-nxtf]. The paper's own authors recommend that future hardware add a built-in soft
reset specifically to eliminate this duplication [rueckauer-2022-nxtf]. SpiNNaker is not
hard-wired to either mode; its ARM cores are fully software-programmable, and a
`neuron_model_has_spiked()` callback lets a user implement subtraction in a custom C neuron model,
but this is not one of sPyNNaker's built-in cell types (`IF_curr_exp` and its relatives use
conventional PyNN hard-reset semantics), so soft reset on SpiNNaker means writing and compiling a
bespoke neuron kernel [spinnaker-neuron-lab-manual]. BrainScaleS-2's native analog AdEx circuit
clamps the membrane to a fixed reset potential for a refractory period on every spike, a hard reset
by construction; no source describes a native or workaround soft-reset mode on BrainScaleS-2,
despite the chip's otherwise extensive multi-compartment capability, which is used there for
genuine dendritic computation rather than as a reset workaround [pehle-2022-brainscales-multicomp].

Native support exists in three places. TrueNorth's digital neuron model implements a "linear mode"
reset as a first-class, natively configurable hardware option, in which the residual potential
above threshold is not discarded but carried forward exactly as reset-by-subtraction requires
[truenorth-neuron-model]. Speck/DYNAP-CNN exposes the choice as a single hardware register,
`return_to_zero`; `False` selects subtractive reset and is the devkit's documented default, with
SynSense's own guidance explicitly directing ANN-to-SNN conversion users to that setting
[speck-devkit-manual]. FPGA-targeted SNN accelerator generators (Spiker+, SIA) support subtractive
reset as a synthesizable, and in SIA's case preferred, option because it measurably improves
classification accuracy [spiker-plus-fpga] [sia-fpga]. Sinabs, the software library targeting
Speck, defaults its `IAF` layer to `MembraneSubtract()`, matching the hardware default
[sinabs-discretize-api]. Taken together, the mechanism proven worth roughly twenty accuracy points
is the single most consistently dropped feature across every interoperability path to accessible
hardware surveyed in this report.

## 8.3 Input encoding and output readout

Direct (analog, constant-current) input encoding applies the raw, real-valued input at every
timestep as a constant current to the first hidden layer, rather than first converting it into a
spike train. Rueckauer et al. introduce this explicitly as one of three mechanisms, alongside
reset-by-subtraction and robust weight normalization, that close the ANN-SNN accuracy gap:
replacing Poisson spike-train input with constant analog current for the first layer alone raised
CIFAR-10 accuracy from roughly 59.8 percent to 83.6 percent, holding weight normalization and
reset-to-zero fixed [rueckauer-2017-frontiers]. Deterministic count coding under a fixed threshold
achieves quantization error that scales as `1/T`, while Poisson coding's variance scales only as
`1/√T`, so Poisson input needs quadratically more timesteps for equivalent precision
[auge-2021-encoding-survey]. This is the direct reason essentially all modern low-latency
conversion work, including the QCFS lineage, uses direct encoding at the input layer rather than
Poisson.

The consequence for hardware is that the first layer is, in effect, an ANN layer. Because its
computation is a real-valued multiply-accumulate rather than an accumulate over binary spikes, it
forfeits the accumulate-only efficiency the rest of the network enjoys; one Eyeriss-scale energy
study measured rate coding costing roughly fifty percent less energy than direct coding
specifically because the direct-encoded first layer carries sixteen-bit precision
[kim-2022-rate-vs-direct]. Toolchains that document this explicitly route the first layer off the
spiking core entirely: Nengo-Loihi's own tooling notes that the input-encoding layer "should run
off-chip" [nengoloihi-cifar10-example], and FPGA accelerator designs place a conventional MAC array
ahead of the spiking core rather than attempt to spike it [spiker-plus-fpga]. No source located
confirms or denies whether Speck, Xylo, BrainScaleS-2, or SpiNNaker support a direct-encoded first
layer as a hardware-native path; there is no architectural reason it should be infeasible, since a
constant input current is a basic capability, but no worked deployment example was found, so the
gap is recorded as unconfirmed rather than assumed closed [kim-2022-rate-vs-direct].

Readout cost is not free either. SNN Toolbox's default output decoding is `temporal_mean_rate`,
spike count divided by `T`, with `temporal_pattern` and three TTFS-family variants offered as
alternatives [snntoolbox-docs]. TTFS decoding instead reads a winner-take-all over first-spike
time, or a learned temporal-weighting decoder over decayed contributions
[park-2020-t2fsnn]. The decision window is not a modeling abstraction; it is real latency paid on
the chip. NxTF's CIFAR-10 run on physical Loihi 1 required a 340 ms per-sample decision delay at
102 mJ per sample [rueckauer-2022-nxtf]. Quartz's TTFS conversion trades this differently: measured
on the same chip family, it reaches 0.9 µJ·s energy-delay product on MNIST against 4.38 µJ·s for a
rate-coded Loihi baseline, but its CIFAR-10 accuracy (25.14 percent error) is markedly worse than
the rate-coded NxTF result (8.52 percent error), even though the TTFS run uses far fewer total
spikes [lenz-2023-quartz]. Reducing the readout window is a real design axis with a real accuracy
cost, not a free efficiency lever.

## 8.4 Time-model mismatch

`T` names three physically different things depending on the platform. Under a synchronous tick,
exemplified by SynSense's own Xylo line, the hardware genuinely advances all state once per a
global `dt`; up to fifteen input events per channel and up to thirty-one output spikes per neuron
can be processed within a single tick, and `T` corresponds to a real, chip-wide clock edge
[rockpool-xylo-overview]. Under an asynchronous event stream, exemplified by SynSense's own Speck
line, there is no clock in the compute path at all: computation is triggered directly by changes
arriving at each block, communicated via a request/acknowledge protocol, and a measured per-layer
propagation latency of roughly 0.37 µs (3.36 µs across nine layers) is a hardware propagation
delay, not a multiple of any chosen simulation `Δt` [richter-2023-speck]. The paper's own
comparison table draws this out explicitly against clocked chips: "Loihi1/2 and TrueNorth... which
architecturally introduce a latency of one timestep `Δt` on event generation in each layer," a
delay stated as 1 ms for TrueNorth's clocked design [richter-2023-speck]. Under analog continuous
time, exemplified by BrainScaleS-2, the substrate runs accelerated, physical-model dynamics at
roughly ten-thousand times real time, with no discretized tick at all [dewolf-2020-nengo-loihi].

The Speck-versus-Xylo contrast is instructive precisely because it sits inside one vendor's product
line. On Xylo, a software `num_timesteps`/`dt` parameter is a hardware-level guarantee: the chip is
architecturally a synchronous time-stepped machine, and per-layer heterogeneous `T` is physically
impossible as currently built [rockpool-xylo-overview]. On Speck, the equivalent software parameter
(Sinabs's `num_timesteps`) exists only at the boundary where a discrete-time raster is converted
into individually timestamped address-event-representation spikes; past that conversion point the
chip has no notion of a timestep whatsoever, and it reacts continuously to each event's arrival
regardless of how many software timesteps were used to construct the input stream
[richter-2023-speck]. The only clocked element anywhere in the Speck2e-and-later compute path is an
auxiliary slow clock governing leak, DVS-filter, and readout-averaging behavior, not the
convolutional datapath itself [richter-2023-speck]. A `T` value reported in a software simulation
paper is therefore not a portable physical quantity across platforms, and on a fully event-driven
chip there may be no hardware `T` to map it onto at all.

## 8.5 Per-layer timestep horizons have no execution model

No framework surveyed expresses a per-layer timestep horizon, layer A running `T=2` while layer B
runs `T=4`, in a single forward pass. SpikingJelly drives every layer from one shared scalar `T`,
either through a user-written `for t in range(T)` loop in single-step mode or a shared `[T, N, *]`
tensor in multi-step mode [fang-2023-spikingjelly]. snnTorch, Norse, and Lava follow the identical
pattern: one external loop, one sequence length, one `RunSteps(total_run_time)` condition applied
to the whole compiled process graph [fang-2023-spikingjelly-lava] [lava-dl-docs]. Rockpool/Xylo
enforces this at the hardware level, not merely in software, since the chip is architecturally a
single global-clock machine (8.4). PyNN inherits whatever global-clock convention its chosen
backend uses. The underlying reason is architectural, stated most plainly in SpikingJelly's own
paper: because a stateful spiking layer's output at time `t` depends on hidden state carried from
`t-1, t-2, ..., 0`, "the for-loop concerning time steps is inevitable," and every framework builds
exactly one such loop per network, not one per layer [fang-2023-spikingjelly].

This is not merely a software-abstraction limit. NeuroScale (Li, Imam, and Manohar, *Nature
Communications* 16, 10329, 2025) confirms it architecturally for the four most-cited large-scale
digital neuromorphic platforms: "The TrueNorth system uses an externally controlled signal that is
distributed to all the hardware components of the architecture... typically operating with a
frequency of 1 kHz... Intel's Loihi and Loihi 2 architectures also implement barrier
synchronization to advance time. Tianjic uses a global clock for all its coordination processes,
including advancing time" [li-2025-neuroscale]. No core on any of these four chips can proceed past
tick `t` until every core has finished tick `t`; there is no hardware primitive corresponding to
"layer 3 is at tick 8 while layer 4 is still at tick 2" [li-2025-neuroscale].

Two papers that assign a different quantization step, and hence a different unrolled timestep
count, to each layer make the resulting cost explicit without resolving it. QAC's own
hardware-efficiency appendix states that under sequential dataflow-accelerator execution (one layer
computed at a time, iterating across the network), cost scales as `O(N·T)`, layers times timesteps,
a sum over layers, which is precisely QAC's own motivation for moving to mixed timesteps in the
first place [guo-2025-qac]. Under the alternative, pipelined multi-core execution that is the
standard model for chips like TrueNorth and Loihi, the same appendix states plainly: "Layer 2 must
wait until Layer 1 completes `T_l1` timesteps before it can start computation... pipeline stalling
may occur, introducing computational delays and preventing the hardware from achieving optimal
performance" [guo-2025-qac]. Under pipelining, the pipeline's overlap benefit is lost exactly at
the boundary between two layers of unequal horizon, so the effective latency again accumulates as a
sum, this time via stall rather than via sequential iteration. QAC's own headline number, 2.76
average timesteps for ResNet-18 on CIFAR-10, is computed as an unweighted mean across layers, not
either of these two costs, and the gap between the accuracy-optimized mean and the
hardware-realizable sum is flagged by the paper's own text but never closed [guo-2025-qac].
PASCAL's analogous `T_eff` of 3.14 for the same architecture and dataset is likewise a weighted
arithmetic mean over layers (Eq. 16), and PASCAL's own hardware section, RTL synthesis via Synopsys
Design Compiler at 40 nm and 560 MHz with a cycle-accurate simulator, validates only that its
modified IF neuron adds negligible overhead relative to a standard IF neuron at a single, uniform
`T=4`; it never synthesizes, simulates, or measures the mixed-timestep execution model that
produces the 3.14 headline [ramesh-2025-pascal]. No paper surveyed, PASCAL, QAC, or QAC's
ICLR-2026-withdrawn successor, performs RTL synthesis, cycle-accurate simulation, or a physical
chip run of the actual heterogeneous-`T` execution path itself.

The one physical deployment of heterogeneous timing found in this survey, Mixed Time-step Training
(Du, Wu, Deng, and Gu, ICLR 2025 poster), works only by targeting a timestep-free chip. MTT trains
a network whose stages are randomly assigned different `T` during training, so the resulting
weights transfer across many single global `T` values and onto a fully event-driven chip that has
no discrete tick to be heterogeneous about in the first place. Deployed on a Speck2e devkit, the
measured spike-difference between the training-time software simulator and the physical chip's
output is 3.92 percent, close to the 2.81 percent difference measured between two identical on-chip
runs, and far below the 28.77 percent difference between a conventional time-stepped simulator and
the chip's actual behavior [du-2025-temporal-flexibility]. This confirms physical deployment of a
temporally flexible model, not execution of a genuine `T_1 ≠ T_2 ≠ ... ≠ T_L` schedule on
synchronous silicon; the two problems, mixed-timestep training for cross-platform generalization
and per-layer heterogeneous-horizon execution, are only superficially related, and MTT's Speck2e
result is evidence for the former, not the latter.

## 8.6 Measurement boundaries and incomparable efficiency claims

SynOps is not joules. The per-operation energy figures nearly every SNN paper cites, roughly 0.9 pJ
for a multiply-accumulate against 0.1 pJ for an accumulate, trace to Mark Horowitz's ISSCC 2014
plenary talk, a table specific to a 45 nm process at 0.9 V [horowitz-2014-isscc]. The talk itself
states that a 32 KB SRAM access already costs 5 pJ, an off-chip DRAM access costs 640 pJ, and a
programmable processor's instruction fetch and register overhead adds roughly 70 pJ per
instruction, none of which a SynOps-times-constant estimate captures [horowitz-2014-isscc]. Three
independent hardware-realistic studies converge on the same conclusion from three different
angles. Bhattacharjee, Yin, Moitra, and Panda benchmark published SNN algorithms on two
hardware-realistic accelerator models (a sparsity-aware systolic array, an RRAM crossbar simulator)
and report that "the actual energy-efficiency improvements of recent SNN algorithmic works differ
significantly from their estimated values" [bhattacharjee-2023-hardware]. Shen, Zhao, Li, Li, and
Zeng propose replacing SynOps with a unified "Bit Budget" metric specifically because comparisons
against unquantized ANN baselines are not fair comparisons [shen-2024-cvpr]. Narduzzi, Zenke, Liu,
and Dunbar find that SynOps and spike-count metrics "fail to account for" membrane-update and
gating-dynamics overhead and propose an alternative, EFLOP, that does [narduzzi-2025-eflop]. None
of these are marginal corrections; all three report the gap between the SynOps estimate and
measured hardware energy as large and systematic.

Static power dominates, so cutting `T` does not cut energy proportionally. On Loihi 2, a sigma-delta
conversion study reports total power "remained relatively consistent for all experiments as it is
dominated by static draw," even as throughput rose from 176 to 362 frames per second with
increasing sparsity [brehove-2026]. A separate Loihi 2 study of the Locally Competitive Algorithm
shows static power nearly constant (approximately 0.54 W) across sparsity settings while dynamic
power varies only modestly (0.17 to 0.39 W), so at the sparsest, most favorable operating point,
static power still exceeds dynamic power [lca-loihi2-2023]. No source in this survey sweeps `T`
alone on identical silicon holding everything else fixed, but the underlying mechanism, an
SRAM-per-core design that draws static power continuously regardless of whether a given tick
performs useful spiking work, is confirmed independently by both studies; reducing `T` shrinks only
the dynamic term, and can even raise energy per inference if the reduction also lowers achievable
throughput.

Boundary choice alone produces order-of-magnitude swings. Shrestha, Timcheck, Frady, Campos-Macías,
and Davies report, for the identical Loihi 2 chip and identical PilotNet network, 0.09 mJ total
energy and 1.21 ms latency per frame when host I/O is excluded from the measurement window (weights
pre-staged), against 1.26 mJ and 65.41 ms when streaming from the host is included, a fourteen-fold
energy difference and a fifty-four-fold latency difference from the boundary choice alone
[shrestha-2023-loihi2]. In the host-inclusive configuration, over ninety-four percent of the
reported energy is static leakage, not spiking computation [shrestha-2023-loihi2]. Other boundary
choices swing the number further: ANN baseline energy on the same Jetson Orin Nano differs by
roughly 3.5 times between batch sizes one and sixteen; input-encoding circuitry (the Poisson
spike-generator itself) is frequently excluded from rate-coded SNN energy totals, though one
sixteen-bit Eyeriss-scale study costs it explicitly and finds it material
[kim-2022-rate-vs-direct]; and quantizing the ANN comparison baseline from fp32 to int8 on the same
Jetson cuts its energy by roughly thirty-seven percent and its energy-delay product by roughly
sixty-three percent, narrowing without eliminating the reported SNN advantage
[shrestha-2023-loihi2]. The field itself names the underlying cause structurally rather than
accidentally: NeuroBench identifies "lack of a formal definition," "implementation diversity" (no
ONNX-equivalent exchange format for SNNs), and "rapid research evolution" as the three reasons a
single enforced measurement protocol is currently infeasible, and settles for transparency and
reporting guidelines instead of a strict standard [yik-2025-neurobench].

## 8.7 Device availability and toolchain decay

SNN Toolbox's last PyPI release, v0.6.0, shipped 2021-03-17; its last substantive code commits date
to August 2022 (a kernel-conversion slicing fix, a deprecated GUI import fix); one further,
documentation-only commit in January 2023 adds a citation, and no commit has been found after
[snntoolbox-github]. The issue tracker was still answered personally by the maintainer into 2024,
but with an explicit admission of reduced capacity ("I won't be able to help much with debugging at
this point"), and no issue in the tracker ever requests a feature from the post-2020, QCFS-family
literature [snntoolbox-issues].

Intel archived all Lava repositories on 13 May 2026: "Intel is developing the next-generation Loihi
architecture and SDK to power the coming era physical AI... All Lava repositories are archived.
Stay tuned for announcements about our new SDK and next generation Loihi processor"
[lava-dl-readme]. No patches are accepted and no maintenance is offered; a successor SDK is named
only as forthcoming, with no release as of this survey. NxTF's own host repository,
`intel-nrc-ecosystem/models`, which carries the only bridge between SNN Toolbox and NxTF, carries a
blanket "DISCONTINUATION OF PROJECT" notice, and Intel's own INRC guidance has redirected users to
Lava for Loihi 2 development since 2022, treating NxSDK and NxTF as Loihi-1-era and superseded even
before Lava's own archival [inrc-loihi-access] [nxsdk-models-repo]. Loihi 1 itself is superseded
hardware, not the current INRC access target.

Access to this hardware is gated, while the hardware that supports reset-by-subtraction natively is
not. Loihi 1 and 2 access runs through INRC membership, behind a research proposal and
participation agreement, not a guaranteed or open channel [inrc-loihi-access]; BrainScaleS and
SpiNNaker access runs through EBRAINS's queued-job Neuromorphic Computing Platform
[hbp-guidebook]. Speck, by contrast, was presold as a 199 US dollar demo kit, and its dev kit is
sold through an ordinary sales channel with no described approval process; Xylo development kits
are likewise commercially purchasable [speck-devkit-manual]. The two toolchains with the deepest
published CNN-scale conversion results in this survey, SNN Toolbox through NxTF to Loihi 1, and
Lava-DL's NetX to Loihi 2, sit behind the least accessible, least currently maintained
software-hardware combination surveyed. Reproducing NxTF's own published CIFAR-10 result on Loihi 1
today would require pinning software Intel no longer distributes support for, against a chip
Intel's own current community guidance no longer directs new users toward.

## 8.8 Interoperability and the portability gap

NIR's reach is genuine and, among the interchange formats surveyed, unmatched. Nine simulators
write and or read NIR (hxtorch and jaxsnn for BrainScaleS-2, Lava-DL read-only, Nengo, Norse,
Rockpool, Sinabs, snnTorch, SpiNNaker2 read-only, and Spyx), reaching five physical hardware
platforms: BrainScaleS-2, Loihi 2, Speck, SpiNNaker2, and Xylo, up from the seven simulators and
four hardware platforms reported at initial publication [pedersen-2024-nir]. This reduces what
would otherwise be an `m × n` interoperability problem, every framework needing a bespoke exporter
to every chip, to `m + n`: every framework needs only one NIR exporter, and every chip needs only
one NIR importer [pedersen-2024-nir].

The paper's own hardware validation shows where this degrades. Cross-platform agreement is reported
as faithful for feedforward dynamics, a single LIF neuron and a spiking convolutional network with
IF neurons, but diverges for a recurrent current-based LIF network, where the authors state
explicitly that reaching the highest accuracy required "platform-dependent optimization, such as
quantization-aware training" [pedersen-2024-nir]. NIR by itself does not guarantee bit-accurate
transfer even for the model classes it covers well. And it stops well short of the full primitive
space a conversion paper needs: its own stated limitations exclude adaptive-threshold mechanisms,
gating, resonate-and-fire, and multicompartmental neuron models from the current primitive set, and
its own porting guide permits a hardware backend to simply ignore an unsupported node rather than
approximate it, with approximation strategies for such cases listed as future work, not implemented
[pedersen-2024-nir] [nir-porting-guide]. Section 8.2 documents the same gap for reset by
subtraction specifically.

No universal exporter exists because every hardware deployment surveyed required nontrivial,
platform-specific rewriting on top of whatever the interchange format carried. Per-neuron
thresholds are collapsed to a single value per layer for Speck, whose hardware does not support
individual per-neuron parameters [sinabs-nmnist-tutorial]. `Linear` layers are rewritten as `1×1`
`Conv2d` layers and `AvgPool2d` as `SumPool2d` to fit a fixed per-core template
[jelly-lava-source]. Multi-core targets require explicit per-core neuron-count partitioning. A
working IR handoff is therefore a starting point for hand adaptation, not a drop-in compile step,
and framework-native export paths compound the problem: SpikingJelly's own `lava_exchange` and
`nir_exchange` modules both reject the soft-reset neurons its own `ann2snn` converter produces by
default, so a model converted by one first-party SpikingJelly module cannot be handed to another
first-party SpikingJelly export module without either reintroducing the reset-related accuracy cost
documented in 8.2 or writing new code [jelly-lava-source] [jelly-nir-source].

No QCFS-to-silicon route is asserted by any source reviewed. The nearest analogues are, first,
NxTF and SNN Toolbox to Loihi 1, which realizes the same conversion family, rate-coded IF neurons
under reset by subtraction, on physical hardware, but not QCFS's specific clip-floor-shift
activation or learnable per-layer threshold [rueckauer-2022-nxtf]; and second, APEX and its
predecessor PASCAL, which are QCFS-specific in their neuron design but target a synthesized,
simulated accelerator, not fabricated, accessible silicon [ramesh-2025-pascal].

## 8.9 The two-population division of labor

Thirteen QCFS-lineage papers audited directly against full text report E5, pure software
simulation, for thirteen of thirteen of their own experiments; zero report a run on a named chip.
Twelve of the thirteen cite neuromorphic hardware only as generic architecture-paper motivational
material, Davies 2018 for Loihi, Akopyan 2015 for TrueNorth, in their introductions, never in
methods or experiments. QCFS itself is the sole partial exception, citing two genuine
physical-silicon deployment papers, Massa et al. 2020 and Singh et al. 2021, as acknowledged prior
art in its related work section rather than as introductory motivation [bu-2022-qcfs].

The deployment side mirrors this. Four hardware-deployment papers audited (Stromatias 2015,
Patiño-Saucedo 2020, Massa 2020, and NxTF 2021/2022) use zero post-2020 low-latency conversion
methods between them; every one runs SNN Toolbox's classical threshold-balancing pipeline or direct
STBP or SLAYER training, rate-coded throughout [rueckauer-2022-nxtf]. NxTF's own related-work
section, written by the same laboratory that authors SNN Toolbox, shows no forward awareness of the
low-latency program about to accelerate [rueckauer-2022-nxtf]. The toolchain freeze overlaps almost
exactly with that acceleration: SNN Toolbox's last substantive commit, August 2022, falls within
months of QCFS's own publication window, and the entire subsequent low-latency literature audited
here, spanning 2022 through 2025, unfolds after the toolbox's code was already frozen
[snntoolbox-github].

The falsifier was searched for deliberately, and every confirmed instance found abandons rate
coding. Quartz (Lenz, Orchard, and Sheik) proposes a time-to-first-spike conversion scheme, states
in its own abstract that "most conversion methods rely on rate coding in the SNN to represent ANN
activation, which uses enormous amounts of spikes," and reports measured results on physical Loihi
1: 0.9 µJ·s energy-delay product on MNIST against 4.38 µJ·s for a rate-coded Loihi baseline, and
10.3 mJ·s against roughly 34.9 mJ·s on CIFAR-10, a same-chip, method-versus-method comparison, not
an isolated demonstration [lenz-2023-quartz]. Brehove et al. propose a sigma-delta, graded-payload
conversion targeting Loihi 2's native graded-spike hardware and report measured, field-deployed
results on a Loihi 2 VPX board [brehove-2026]. No paper was found that keeps rate coding, proposes
a new conversion algorithm, and reaches physical silicon with measurements; the nearest near-miss,
a Speck chip-introduction paper, uses a conventional conversion baseline rather than a novel
low-latency algorithm and is a hardware paper first [richter-2023-speck].

One qualification is owed here, stated honestly rather than smoothed over. A rate-coded QCFS and
SRP baseline configuration has, once, been measured on physical silicon, as a comparison row inside
Adaptive Fission (Jiang et al., NeurIPS 2025), whose own algorithmic contribution is a
population-coding scheme layered on top of existing conversion methods, deployed on a Lynxi HP201
accelerator [jiang-2025-adaptive-fission]. QCFS and SRP's own authors never ran this measurement; a
different group's non-rate-coding innovation motivated the one instance that exists. The defensible
claim is therefore not that rate-coded QCFS-lineage output has never touched silicon under any
circumstances, but that no QCFS-lineage algorithm paper deploys its own method to silicon, and the
one time it happened, it required a different paper's rate-coding-abandoning innovation to make it
happen [jiang-2025-adaptive-fission]. A second, weaker qualification: one non-peer-reviewed,
self-reported GitHub project claims a QCFS implementation with dedicated SpiNNaker and BrainScaleS-2
backends and reports "physical silicon confirmed" runs, but its own documentation describes a
two-neuron validation network, not a benchmark-scale classifier, and does not rise to the bar of a
published counterexample; it suggests the gap may be sociological rather than technically forced,
without closing it in the published record.

# 9 Conclusion

This survey set out to answer whether the ReLU-to-integrate-and-fire correspondence that anchors
the low-`T` ANN-to-SNN conversion literature is realized on physical silicon or only in simulation,
and where the disconnect between that literature and the accessible neuromorphic landscape actually
lies. The seam-by-seam audit in Section 8 answers both questions concretely rather than by
assertion. A trained network passing from a conversion paper toward physical silicon loses at least
one of its pooling or skip-connection topology (8.1), its BatchNorm folding (8.1), its reset rule
(8.2), its encoding scheme's energy accounting (8.3), or its timestep semantics (8.4, 8.5) at
nearly every handoff surveyed, and no single documented toolchain preserves all of them
simultaneously. The two-population finding (8.9) is not an artifact of an incomplete search: it
rests on full-text citation audits of thirteen algorithm papers and four deployment papers, a dated
toolchain-freeze overlap, and a deliberately adversarial search for a falsifier that returned
exactly two positive instances, Quartz and Brehove et al., both of which abandon rate coding to
reach silicon. Whether a Lava-to-Loihi-2 deployment direction is viable for further work on this
thesis (design question 6) has a direct answer: the software stack was archived on 13 May 2026,
accepting no further patches, with an unnamed successor SDK, and the reset-semantics blocker (8.2)
together with the operator-coverage blocker (8.1) both apply before the gated, proposal-based
hardware access (8.7) is even reached.

Four concrete problems remain open, and each follows directly from a seam documented above rather
than from a general appeal to future work.

A conversion theorem for an ordinal, non-rate code is missing. The correspondence proved for IF
neurons under reset by subtraction, that a spike count over `T` steps realizes exactly a uniform
`T`-level quantizer, has no published analogue for the codes that actually reach silicon alongside
a new algorithm: time-to-first-spike (Quartz) and graded sigma-delta (Brehove et al.). Until such a
theorem exists, "abandon rate coding to reach hardware" and "prove the QCFS-as-QAT correspondence"
remain two separate, currently incompatible research programs rather than one.

An execution model for heterogeneous per-layer timestep horizons is missing. NeuroScale confirms
that every major digital neuromorphic chip audited here, TrueNorth, Loihi, Loihi 2, and Tianjic,
advances through a single global synchronization barrier. No simulator or chip surveyed executes a
genuine `T_1 ≠ T_2 ≠ ... ≠ T_L` schedule within one forward pass, and the two papers that compute an
average-timestep headline, QAC and PASCAL, do not resolve, and in QAC's case do not even quantify,
the sequential-sum or pipeline-stall cost their own appendices identify as the consequence of
mapping that schedule onto real hardware.

A maintained, soft-reset-preserving export path is missing. Every framework-native bridge surveyed,
SpikingJelly's `lava_exchange` and `nir_exchange`, and the NIR primitive specification itself,
rejects or fails to express reset by subtraction, the one mechanism independently shown worth
roughly twenty accuracy points. The platforms that support it natively, TrueNorth, Speck via
`return_to_zero=False`, and the FPGA frameworks, are either legacy hardware or require bespoke,
per-project glue rather than offering a general, maintained tool.

A measured comparison of a modern low-`T` method against a quantized ANN baseline on the same
silicon is missing. The single closest data point found, Loihi 2 against an int8-quantized Jetson
Orin Nano on PilotNet, shows that quantizing the ANN baseline closes a substantial fraction, though
not all, of the reported SNN advantage. No equivalent same-chip comparison exists for a post-2021
low-`T` conversion method measured against an INT8 or lower ANN baseline of matching bit budget.

Chapter 2's inability to connect conversion methods to hardware execution, noted at the outset of
this survey as motivation rather than as a flaw in the author's own literature review, is not a gap
in that review. It is a gap in the field's published record, confirmed here across nine research
passes and eighteen source files rather than assumed. This survey's edge structure, tracing what
each handoff preserves and what it breaks, is offered as a first attempt to make that gap itself an
object of study, rather than an implicit background condition every subsequent conversion paper
continues to work around without naming.

---

## References for Section 8

- [rueckauer-2017-frontiers] Rueckauer, B., Lungu, I.-A., Hu, Y., Pfeiffer, M., Liu, S.-C.
  "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image
  Classification." *Frontiers in Neuroscience* 11:682 (2017). https://doi.org/10.3389/fnins.2017.00682.
  Peer-reviewed.
- [rueckauer-2022-nxtf] Rueckauer, B., Bybee, C., Goettsche, R., Singh, Y., Mishra, J., Wild, A.
  "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi." *ACM Journal on
  Emerging Technologies in Computing Systems* 18(2) (2022). https://doi.org/10.1145/3501770
  (arXiv:2101.04261). Peer-reviewed.
- [pedersen-2024-nir] Pedersen, J. E. et al. "Neuromorphic intermediate representation: A unified
  instruction set for interoperable brain-inspired computing." *Nature Communications* 15:8122
  (2024). https://doi.org/10.1038/s41467-024-52259-9. Peer-reviewed.
- [nir-porting-guide] NIR project, "Porting to a New Platform." Official documentation.
  https://neuroir.org/docs/porting-nir/.
- [snntorch-pr-388] snnTorch GitHub pull request #388, "nir: add missing v_reset parameter on
  export." Repository state. https://github.com/jeshraghian/snntorch/pull/388.
- [snntorch-pr-426] snnTorch GitHub pull request #426, reset-mechanism refactor (subtract vs. zero
  confusion). Repository state. https://github.com/jeshraghian/snntorch/pull/426.
- [fang-2023-spikingjelly] Fang, W. et al. "SpikingJelly: An open-source machine learning
  infrastructure platform for spike-based intelligence." *Science Advances* 9(40), eadi1480 (2023).
  https://www.science.org/doi/pdf/10.1126/sciadv.adi1480. Peer-reviewed.
- [fang-2023-spikingjelly-lava] SpikingJelly documentation, "Convert to Lava for Loihi Deployment."
  Official documentation. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html.
- [jelly-lava-source] SpikingJelly `lava_exchange` module source (`v_reset == 0` hard constraint,
  operator dispatch). Repository state.
  https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html.
- [jelly-nir-source] SpikingJelly `nir_exchange/to_nir.py` source (`NotImplementedError` on soft
  reset). Repository state, retrieved via `raw.githubusercontent.com/fangwei123456/spikingjelly`.
- [sinabs-discretize-api] Sinabs documentation, discretize/DynapcnnLayer API (no BatchNorm-fold
  utility; default `MembraneSubtract()` reset). Official documentation.
  https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html.
- [sinabs-nmnist-tutorial] Sinabs NMNIST quick-start tutorial (bias-as-leak, BN-free architecture
  convention). Official documentation. https://sinabs.readthedocs.io/v3.1.3/tutorials/nmnist.html.
- [akida-hw-constraints] BrainChip Akida hardware constraints documentation. Official
  documentation. https://doc.brainchipinc.com/user_guide/hardware/1.0.html and
  https://brainchip-inc.github.io/akida_examples_2.4.0-doc-1/user_guide/1.0_hw_constraints.html.
- [snntoolbox-docs] SNN Toolbox documentation, introduction and simulation API (operator coverage,
  output coding schemes). Official documentation. https://snntoolbox.readthedocs.io/en/latest/.
- [snntoolbox-github] SNN Toolbox GitHub repository, release history and commit log. Repository
  state. https://github.com/NeuromorphicProcessorProject/snn_toolbox.
- [snntoolbox-issues] SNN Toolbox GitHub issue tracker, issues #142 and #143 (2024). Repository
  state / community commentary. https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues.
- [pehle-2022-bmtk] BMTK-Loihi mapping paper (native hard reset on Loihi). *Frontiers in
  Neuroinformatics* (2022). https://doi.org/10.3389/fninf.2022.883360. Peer-reviewed.
- [pehle-2022-brainscales-multicomp] Pehle, C. et al. "The BrainScaleS-2 Accelerated Neuromorphic
  System With Hybrid Plasticity." *Frontiers in Neuroscience* (2022).
  https://doi.org/10.3389/fnins.2022.795876. Peer-reviewed.
- [spinnaker-neuron-lab-manual] SpiNNaker Manchester, "Creating New Neuron Models" lab manual, and
  sPyNNaker "Models and Limitations" documentation. Official documentation.
  https://spinnakermanchester.github.io/.
- [truenorth-neuron-model] "Cognitive Computing Building Block: neuron model of TrueNorth."
  Technical report. https://viplab.fudan.edu.cn/vip/attachments/download/3248/neuron-model_of_truenorth.pdf.
- [speck-devkit-manual] SynSense, Speck Dev Kit Manual / Datasheet. Vendor material.
  https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf.
- [spiker-plus-fpga] Spiker+ FPGA SNN accelerator generator (native subtractive reset). Preprint,
  arXiv:2401.01141.
- [sia-fpga] SIA hardware-software co-optimized FPGA SNN accelerator (subtractive reset as
  default). Preprint, arXiv:2410.16298.
- [auge-2021-encoding-survey] Auge, D., Hille, J., Mueller, E., Knoll, A. "A Survey of Encoding
  Techniques for Signal Processing in Spiking Neural Networks." *Neural Processing Letters* (2021).
  https://doi.org/10.1007/s11063-021-10562-2. Peer-reviewed.
- [kim-2022-rate-vs-direct] Kim, Y., Park, H., Moitra, A., Bhattacharjee, A., Venkatesha, Y.,
  Panda, P. "Rate Coding or Direct Coding: Which One is Better for Accurate, Robust, and
  Energy-efficient Spiking Neural Networks?" arXiv:2202.03133 (2022). Preprint.
- [nengoloihi-cifar10-example] NengoLoihi CIFAR-10 convnet example (off-chip input layer). Official
  documentation. https://www.nengo.ai/nengo-loihi/v1.0.0/examples/cifar10-convnet.html.
- [park-2020-t2fsnn] Park, S. et al. "T2FSNN: Deep Spiking Neural Networks with Time-to-First-Spike
  Coding." arXiv:2003.11741 (2020). Preprint.
- [lenz-2023-quartz] Lenz, G., Orchard, G., Sheik, S. "Ultra-low-power Image Classification on
  Neuromorphic Hardware" (Quartz). arXiv:2309.16795 (2023-2024). Preprint.
- [richter-2023-speck] Richter, O. et al. (SynSense), "Speck: A Smart event-based Vision Sensor
  with a low latency 327K Neuron Convolutional Neuronal Network Processing Pipeline."
  arXiv:2304.06793 (2023). Preprint.
- [rockpool-xylo-overview] Rockpool documentation, "Overview of the Xylo family." Official
  documentation. https://rockpool.ai/devices/xylo-overview.html.
- [dewolf-2020-nengo-loihi] DeWolf, T., Jaworski, P., Eliasmith, C. "Nengo and Low-Power AI
  Hardware for Robust, Embedded Neurorobotics." *Frontiers in Neurorobotics* (2020).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/. Peer-reviewed.
- [li-2025-neuroscale] Li, C., Imam, N., Manohar, R. "A deterministic neuromorphic architecture
  with scalable time synchronization" (NeuroScale). *Nature Communications* 16, 10329 (2025).
  https://doi.org/10.1038/s41467-025-65268-z. Peer-reviewed.
- [guo-2025-qac] Guo, M., Li, Q., Li, Y., Cheng, J., Chen, L. "QAC: Quantization-Aware Conversion
  for Mixed-Timestep Spiking Neural Networks." ICLR 2025 submission #8774.
  https://openreview.net/forum?id=D4sQzdMvcG. Preprint (venue/acceptance status unconfirmed).
- [ramesh-2025-pascal] Ramesh, P., Srinivasan, G. "PASCAL: Precise and Efficient ANN-SNN Conversion
  using Spike Accumulation and Adaptive Layerwise Activation." *Transactions on Machine Learning
  Research* (2025). arXiv:2505.01730. Peer-reviewed.
- [du-2025-temporal-flexibility] Du, Y., Wu, D., Deng, L., Gu, S. "Temporal Flexibility in Spiking
  Neural Networks: Towards Generalization Across Time Steps and Deployment Friendliness." ICLR 2025
  Poster. https://arxiv.org/html/2503.17394v1. Peer-reviewed.
- [horowitz-2014-isscc] Horowitz, M. "1.1 Computing's Energy Problem (and what we can do about
  it)." ISSCC 2014. https://doi.org/10.1109/ISSCC.2014.6757323. Peer-reviewed (conference).
- [bhattacharjee-2023-hardware] Bhattacharjee, A., Yin, R., Moitra, A., Panda, P. "Are SNNs Truly
  Energy-efficient? — A Hardware Perspective." arXiv:2309.03388 (2023). Preprint.
- [shen-2024-cvpr] Shen, G., Zhao, D., Li, T., Li, J., Zeng, Y. "Are Conventional SNNs Really
  Efficient? A Perspective from Network Quantization." CVPR 2024.
  https://openaccess.thecvf.com/content/CVPR2024/papers/Shen_Are_Conventional_SNNs_Really_Efficient_A_Perspective_from_Network_Quantization_CVPR_2024_paper.pdf.
  Peer-reviewed.
- [narduzzi-2025-eflop] Narduzzi, S., Zenke, F., Liu, S.-C., Dunbar, L. A. "EFLOP: a sparsity-aware
  metric for evaluating computational cost in spiking and non-spiking neural networks."
  *Neuromorphic Computing and Engineering* 5, 034011 (2025). https://doi.org/10.1088/2634-4386/addee8.
  Peer-reviewed.
- [brehove-2026] Brehove, T., Tumpa, S. N., Kyubwa, E., Menon, A., Narayanan, V. "Sigma-Delta
  Neural Network Conversion on Loihi 2." ICONS 2026, arXiv:2505.06417. Peer-reviewed (conference).
- [lca-loihi2-2023] "Implementing and Benchmarking the Locally Competitive Algorithm on the Loihi 2
  Neuromorphic Processor." arXiv:2307.13762 (2023). Preprint.
- [shrestha-2023-loihi2] Shrestha, S. B., Timcheck, J., Frady, P., Campos-Macías, L., Davies, M.
  "Efficient Video and Audio Processing with Loihi 2." arXiv:2310.03251; ICASSP 2024.
  https://doi.org/10.1109/icassp48485.2024.10448003. Peer-reviewed.
- [yik-2025-neurobench] Yik, J. et al. "The NeuroBench framework for benchmarking neuromorphic
  computing algorithms and systems." *Nature Communications* 16, 1545 (2025).
  https://doi.org/10.1038/s41467-025-56739-4. Peer-reviewed.
- [lava-dl-readme] `lava-nc/lava-dl` GitHub README, archival notice (13 May 2026). Repository
  state. https://github.com/lava-nc/lava-dl/blob/main/README.md.
- [lava-dl-docs] Lava documentation, "Deep Learning" (SLAYER/Bootstrap/NetX overview, `RunSteps`
  execution model). Official documentation. https://lava-nc.org/dl.html.
- [inrc-loihi-access] Intel Neuromorphic Research Community, "Access Intel Loihi Hardware."
  Vendor material (Confluence). https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001.
- [nxsdk-models-repo] `intel-nrc-ecosystem/models` GitHub repository, discontinuation notice.
  Repository state. https://www.github.com/intel-nrc-ecosystem/models.
- [hbp-guidebook] HBP Neuromorphic Computing Platform Guidebook (BrainScaleS and SpiNNaker access
  via EBRAINS). Vendor/official documentation.
  https://flagship.kip.uni-heidelberg.de/jss/FileExchange/HBPNeuromorphicComputingPlatformGuidebook.pdf.
- [bu-2022-qcfs] Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN Conversion
  for High-accuracy and Ultra-low-latency Spiking Neural Networks." ICLR 2022, arXiv:2303.04347.
  Peer-reviewed (conference).
- [wang-2023-ijcai-snm] Wang, Y., Zhang, M., Chen, Y., Qu, H. "Signed Neuron with Memory" (SNM).
  IJCAI 2022. https://www.ijcai.org/proceedings/2022/0347.pdf. Peer-reviewed (conference).
- [hao-2023-aaai-srp] Hao, Z., Bu, T., Ding, J., Huang, T., Yu, Z. "Reducing ANN-SNN Conversion
  Error through Residual Membrane Potential" (SRP). AAAI 2023, arXiv:2302.02091. Peer-reviewed
  (conference).
- [jiang-2025-adaptive-fission] Jiang, Y. et al. "Adaptive Fission." NeurIPS 2025 proceedings.
  Peer-reviewed (conference). Code repository (not independently re-verified): repository state,
  https://github.com/JiangYizhou16/Adaptive-Fission.


---

