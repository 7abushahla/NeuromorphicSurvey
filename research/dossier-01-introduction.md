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

## References

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
