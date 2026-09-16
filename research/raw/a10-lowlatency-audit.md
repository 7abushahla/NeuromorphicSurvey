# A10 — Deployment Audit: Low-Latency / Low-T ANN-to-SNN Conversion Literature (QCFS Lineage)

Audit date: 2026-09-15. Scope: papers proposing or directly extending the QCFS ("quantization
clip-floor-shift") family of low-latency ANN-to-SNN conversion methods, plus adjacent low-T
conversion work (SNM, Fast-SNN, SEENN, burst-spike methods, etc.). For every paper the question
asked was: **did it run on physical neuromorphic hardware, and if so, what was measured?**
Classification never inferred from a motivational sentence in an abstract or introduction; only
from the Experiments/Results section (or, absent one, the paper's own explicit claims about what
was run).

## Classification key

- **E1** — physical silicon, latency/energy actually measured on the chip.
- **E2** — physical silicon, accuracy only measured on the chip (no latency/energy).
- **E3** — a documented hardware deployment path exists but was not executed/reported.
- **E4** — hardware *model* only (RTL synthesis + cycle-accurate simulator, or a named
  neuromorphic *architectural simulator*, not a physical chip).
- **E5** — pure software simulation (GPU/PyTorch), including any SynOps-based "energy" table
  computed with the Horowitz 45nm ADD/MAC numbers. A SynOps estimate table is **E5**, explicitly
  labeled "estimate," never E1.

## Main audit table

| # | Paper | Venue/Year | Neuron model / reset | Input encoding | T values reported | Datasets | Peak/typical accuracy | Hardware claim | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Bu et al., "Optimal ANN-SNN Conversion..." (**QCFS**) | ICLR 2022 (arXiv 2303.04347) | IF, soft/subtractive reset, QCFS-trained ANN activation `clip-floor-shift` | Direct/analog (real-valued input as constant current into first layer, standard since Rueckauer et al. 2017 — no Poisson coding used or discussed) | 1(discussed as future work only, not achieved), 4, 8, 16, 32, 64, 128, 256, 512+ | CIFAR-10, CIFAR-100, ImageNet | 93.96% CIFAR-10 @T=4; 59.35–74%+ ImageNet @T=16–64 | "Our results can benefit the implementations on neuromorphic hardware" (conclusion, aspirational only) — no experiments section hardware content | **E5** |
| 2 | Bu et al., "Optimized Potential Initialization for Low-latency SNNs" (**OPI**) | AAAI 2022 (arXiv 2202.01440) | IF, optimal non-zero initial membrane potential (θ/2), reset by subtraction | Direct/analog (same convention as QCFS/Rueckauer) | ≤32 explicitly targeted; results shown 8–512+ | CIFAR-10, CIFAR-100, ImageNet | 93.38% CIFAR-10 @T=16 | None. No hardware section, no chip named. | **E5** |
| 3 | Hao, Bu, Ding, Huang, Yu, "Reducing ANN-SNN Conversion Error through Residual Membrane Potential" (**SRP**) | AAAI 2023 (arXiv 2302.02091) | IF built on QCFS activation, residual-membrane-potential readout, two-stage inference (calibration + inference) | Direct/analog (inherits QCFS convention) | τ=4 headline result; T=4,8,16,32 tables | CIFAR-10, CIFAR-100, ImageNet | 64.32% ImageNet top-1 @10 steps; 95.25% CIFAR-10 (ResNet-18) @T=4 | "Promote the practical application of SNNs on neuromorphic chips" (conclusion, aspirational) — no experiments-section hardware | **E5** |
| 4 | Hao, Ding, Bu, Huang, Yu, "Bridging the Gap...by Calibrating Offset Spikes" (**COS**) | ICLR 2023 (arXiv 2302.10685) | IF, offset-spike detection + initial-membrane-potential shifting, iterative calibration | Direct/analog (inherits QCFS convention) | 6-step headline (4 calib + 2 inference); tables at T=2,4,6,8 | CIFAR-10, CIFAR-100, ImageNet | 67.12% ImageNet top-1 @T=6 | "Hampers the practical applications of SNNs to neuromorphic chips" (motivation only) — no hardware experiments | **E5** |
| 5 | Jiang, Anumasa, De Masi, Xiong, Gu, "A Unified Optimization Framework of ANN-SNN Conversion" (**SlipReLU**) | ICML 2023 | IF, SlipReLU (weighted ReLU + step function) activation, shift term δ | Direct/analog | **T=1** (first claimed 1-step conversion), T=2, T=4 | CIFAR-10, CIFAR-100 | 93.11% CIFAR-10 (ResNet-18) @T=1 | None mentioned in experiments; only ImageNet-scale/energy-efficiency framed generically in intro | **E5** |
| 6 | Li & Zeng, "Efficient and Accurate Conversion of SNN with Burst Spikes" | IJCAI 2022 (arXiv 2204.13271) | Burst-spike IF neuron (multiple spikes/step, bounded by Γ) + LIPooling | Not explicitly Poisson; standard rate/analog input for VGG/ResNet CIFAR/ImageNet setup | <100 steps (headline); ablations to T=32+ | CIFAR-10, CIFAR-100, ImageNet | 71.41% ImageNet (VGG-16) @T=32 | "the number of Γ is limited by the processing capacity of the neuromorphic hardware" — design constraint reasoning only, no chip run. Conclusion: "Hopefully, our work can be combined with neuromorphic hardware..." (aspirational) | **E5** |
| 7 | Wang, Zhang, Chen, Qu, "Signed Neuron with Memory" (**SNM** + NeuronNorm) | IJCAI 2022 | Signed neuron with memory (allows negative/positive spikes, asynchronous-compatible), neuron-wise normalization | Standard rate/analog input, no Poisson discussion | ≤128 (headline); tables to 1024 | CIFAR-10, CIFAR-100, ImageNet | 95.44% CIFAR-10, 78.3% CIFAR-100, 73.16% ImageNet | "Potential for ultra-low-power event-driven neuromorphic hardware implementation" (abstract motivation only) — no hardware section | **E5** |
| 8 | Hu, Zheng, Jiang, Pan, "Fast-SNN: Fast SNN by Converting Quantized ANN" | TPAMI 2023 (arXiv 2305.19868) | Signed IF neuron (reset by adding threshold on negative spike), layer-wise fine-tuning | Direct/analog (constant current injecting bias term) | Headline **T=3, 7, 15** (classification, detection, segmentation resp.) | ImageNet, PASCAL VOC 2007/2012 | 71.31% ImageNet @T=3 | Explicitly: "neuromorphic hardware such as Loihi already supports signed spikes" — cited as design justification for the signed-IF neuron choice, not as an executed deployment. No chip run. | **E5** |
| 9 | Li, Jones, Furber, "Unleashing the Potential of SNNs by Dynamic Confidence" | ICCV 2023 (arXiv 2303.10276) | Soft-reset IF (as in QCFS/QFFS), dynamic early-termination decision agent on top of QCFS/QFFS SNNs | Not discussed explicitly (inherits base method's encoding) | Baseline T=4/T=14 (QCFS/QFFS); avg. reduced to ~1.28–4.71 with Dynamic Confidence | CIFAR-10, ImageNet | 95.1–96.7% CIFAR-10 (upper bound); 82.47% ImageNet upper bound | None. Despite co-author Steve Furber (SpiNNaker's creator), no SpiNNaker or any chip experiment appears; purely simulated accuracy/latency-step curves. | **E5** |
| 10 | Li, Ma, Furber, "Quantization Framework for Fast SNNs" (**QFFS**) | Frontiers in Neuroscience 2022 | IF, quantization-aware ANN (LSQ-based) → SNN, "occasional noise" suppression | **Explicitly stated: "the network input is analog-coded (Rueckauer et al., 2017)"** — direct/analog encoding, not Poisson | 4 (CIFAR-10), 8/10 (ImageNet, with analog output layer) | CIFAR-10, ImageNet | 93.14% CIFAR-10 @T=4; 70.18% ImageNet @T=8 | None in experiments. Both ANN quantization and SNN "implementation are carried out with PyTorch." Despite Furber's SpiNNaker affiliation, no SpiNNaker run reported anywhere in the paper. | **E5** |
| 11 | Li, Geller, Kim, Panda, "SEENN: Towards Temporal Spiking Early-Exit Neural Networks" | NeurIPS 2023 (arXiv 2304.01230) | Inherits QCFS/TET base SNN; adds confidence-threshold or RL-based early exit | Inherits base method's convention (not separately discussed) | Avg. **1.08** timesteps (CIFAR-10, SEENN-II) up to full T=6 baselines | CIFAR-10, CIFAR-100, ImageNet, CIFAR10-DVS | 96.1% CIFAR-10 @ avg. T=1.08 | Section titled "4.3 Hardware Efficiency" explicitly states: "we directly use a GPU (NVIDIA Tesla V100) to evaluate the latency (or throughput)"; energy is a "rough measure" counting only operation counts — a SynOps-style estimate, not a chip measurement. | **E5** |
| 12 | Yang, Yang, Zhang, Dou, Shen, Zhao, "CS-QCFS: Bridging the performance gap in ultra-low latency SNNs" | Neural Networks 2024/2025 | IF, Channel-wise Softplus-QCFS activation (per-channel threshold, guaranteed positive) | Inherits QCFS direct/analog convention | **T=1** headline | CIFAR-10, CIFAR-100 | 95.86% CIFAR-10, 74.83% CIFAR-100 @T=1 | Reference list cites Davies et al. "Loihi: A Neuromorphic Manycore Processor" — a citation only, not an experiment. All reported results are CIFAR-10/100 accuracy tables. | **E5** |
| 13 | Wang, Fang, Cao, Ren, Xu, "Adaptive Calibration: A Unified Conversion Framework of SNNs" (AdaFire/SSC/IAT) | AAAI 2025 (Oral) (arXiv 2412.16219) | Adaptive-Firing (burst) neuron, training-free calibration | Standard (not separately specified; inherits Calibration/QCFS-family convention) | T=8 headline (vs. T=32 competitors at equal energy) | CIFAR-10, CIFAR-100, ImageNet, CIFAR10-DVS, N-Caltech101, PASCAL VOC, MS COCO | 75%+ ImageNet-class accuracy @T=8; up to 70.1% "energy reduction" reported | States burst-firing "is well-supported by neuromorphic hardware such as Intel's Loihi 2 and Synsense's Speck/Xylo" — cited twice as *motivation* for choosing a burst-firing neuron model, never as an executed run. Energy figures come from "the method of calculating the theoretical energy... shown in the Appendix" — explicitly a SynOps-style theoretical estimate. | **E5** (energy = estimate, explicitly labeled theoretical) |
| 14 | Ramesh & Srinivasan, "PASCAL: Precise and Efficient ANN-SNN Conversion using Spike Accumulation and Adaptive Layerwise Activation" | arXiv 2505.01730 (2025) | Multi-stage IF w/ spike accumulation + inhibitory spikes, mathematically exact QCFS-SNN equivalence | Inherits QCFS activation/encoding convention | T_eff ≈ 2.6–18 (layerwise-adaptive); baseline QCFS 64–1024 for comparison | CIFAR-10, CIFAR-100, ImageNet | ≈74% ImageNet (ResNet-34) w/ 56× fewer timesteps than baseline QCFS | Energy efficiency section states results come from "an analytical model" (E5). Acknowledgments separately credit a collaborator "for benchmarking our work on **neuromorphic architectural simulators**" — a simulator, not a physical chip. No latency/power numbers from silicon appear in the paper body. | **E5 (paper's own results) / E4 (acknowledged but unreported simulator benchmarking)** |
| 15 | Manjunath et al., "NeuroFlex: Column-Exact ANN-SNN Co-Execution Accelerator" | arXiv 2511.05215 (2025) — follow-on to PASCAL | Extends PASCAL's integer-exact QCFS-SNN equivalence to column-level hybrid ANN/SNN execution | Integer-exact spike generation from QCFS-activation, INT8 | Timesteps/levels tied to per-column QCFS `L` (not a single headline T) | VGG-16, ResNet-34, GoogLeNet, BERT (workload-level, not classification-accuracy-centric) | Reports EDP/throughput, not classification accuracy tables | Explicitly: "We implement key components of NeuroFlex and all baselines in **RTL** and synthesize with **Synopsys Design Compiler** at 560 MHz in **40 nm**... We develop a **Python cycle-level simulator**." This is textbook **hardware modeling**, not silicon. | **E4** |
| 16 | Liu, Zhao, Chen, Wang, Jiang, "SpikeConverter" (related, not QCFS-lineage but frequently co-cited) | AAAI 2022 | Inverse-leaky IF (iLIF), temporal separation scheme | Not Poisson; standard conversion convention | 16 steps headline (32×–512× fewer than SOTA baselines) | CIFAR-10, CIFAR-100, ImageNet | Comparable to source ANN at T=16 | "More power-efficient computation...in specialized neuromorphic hardware" — background motivation only | **E5** |

## Contrast case found during the search (NOT QCFS-lineage — included to calibrate what E1 actually looks like)

| Paper | Venue/Year | Method | Hardware | Measured | Class |
|---|---|---|---|---|---|
| Brehove, Tumpa, Kyubwa, Menon, Narayanan, "Sigma-Delta Neural Network Conversion on Loihi 2" | ICONS 2026 (arXiv 2505.06417) | Converts ANN to a **Sigma-Delta Neural Network (SDNN)** using Loihi 2's native **graded spikes** (16-bit signed integer payloads representing activation deltas) — explicitly **not** rate-coded IF/QCFS | Intel Loihi 2 (physical, "Oheo Gulch"/multi-chip boards), compared against NVIDIA Jetson Xavier | Latency and energy-delay product measured on the actual chip in the field | **E1** — but this is a fundamentally different conversion paradigm (graded-spike SDNN, not QCFS quantization-clip-floor-shift with rate-coded IF neurons). It demonstrates E1 is achievable on Loihi 2 for *some* ANN-to-SNN conversion method, just not for the QCFS lineage. |

Other adjacent citations found but not QCFS-lineage, noted for completeness:
- "Porting Deep Spiking Q-Networks to Neuromorphic Chip Loihi" (2021) — Loihi deployment, but for spiking DQN reinforcement learning, unrelated to image-classification ANN-SNN conversion. **E1**, out of scope.
- A Loihi-vs-Neural-Compute-Stick-2 comparison paper (arXiv 2210.05006) uses the "SNN Conversion Toolbox" + custom "NxTF" Loihi backend — a general conversion toolbox (Rueckauer-style), not QCFS. **E1**, out of scope for this lineage.
- Sinabs/DYNAP-CNN (Speck) toolchain from SynSense exists as a generic, production SNN-to-chip deployment path (handles AvgPool→SumPool conversion, 8-bit weight discretization, chip layer mapping) — but no paper was found pairing this toolchain with a QCFS-trained network specifically. **E3** at best (a documented path exists in principle via any IF-based SNN, never exercised for QCFS in the literature found).

## Answers to the sub-questions

**1. Do any of these papers name a target chip?**
Several *cite* chips (Loihi, Loihi 2, TrueNorth, Tianjic, Synsense Speck/Xylo) as motivation for
a design choice — e.g., Fast-SNN cites Loihi's support for signed spikes to justify its signed-IF
neuron; Adaptive Calibration cites Loihi 2/Speck's native support for burst firing to justify its
AdaFire neuron; the "Integer-Exact QCFS" literature summary (PASCAL/NeuroFlex family) states the
architecture "maps directly onto IF neuron hardware such as Loihi, TrueNorth, and Tianjic." None
of these citations is accompanied by an actual deployment on the named chip. No paper states "we
target chip X and here are results from chip X" for the QCFS lineage specifically.

**2. Do any report energy? Measured or SynOps-estimated?**
Several report energy, and in every case found it is an **estimate**, never a chip measurement:
- SEENN (NeurIPS 2023): "a rough measure to count only the energy of operations" — explicit SynOps-style op-counting estimate, GPU-timed latency.
- Adaptive Calibration/AdaFire (AAAI 2025): "the method of calculating theoretical energy is shown in the Appendix" — explicit theoretical/SynOps estimate.
- PASCAL (2025): "we demonstrated the energy efficiency of the proposed approach using an analytical model" — explicit analytical estimate.
- Li & Zeng Burst Spikes (IJCAI 2022): reports "0.693× energy consumption" relative to baseline — computed, not measured.
None of these energy figures derive from a physical chip's power rail or measured joules; all are
SynOps/operation-count-style estimates (the Horowitz 45nm ADD/MAC energy-per-op convention is the
standard underlying assumption in this literature, consistent with Rueckauer et al. 2017's
energy-table convention that essentially all these papers inherit).

**3. Is there ANY published work taking a QCFS-trained network and running it on Loihi, SpiNNaker, DYNAP-CNN, or any other physical neuromorphic chip?**
**NOT FOUND.** Across 16 QCFS-lineage/low-T conversion papers audited (QCFS itself, OPI, SRP, COS,
SlipReLU, Burst Spikes, SNM, Fast-SNN, Dynamic Confidence, QFFS, SEENN, CS-QCFS, Adaptive
Calibration, PASCAL, NeuroFlex, SpikeConverter), zero report an experiment executed on physical
neuromorphic silicon (Loihi, Loihi 2, SpiNNaker, SpiNNaker2, DYNAP-CNN/Speck, TrueNorth, Tianjic,
Akida, or any other chip). The closest approaches found are: (a) PASCAL's acknowledgment of
unreported benchmarking "on neuromorphic architectural simulators" (a simulator, E4, not silicon,
and results are not in the paper body); (b) NeuroFlex's RTL synthesis + cycle-accurate simulator
at 40nm (E4, a hardware *model*, never fabricated/run); (c) generic citations of Loihi/Speck/
TrueNorth as motivational or design-justification references (e.g., "Loihi already supports
signed spikes"). A structurally-similar but distinct conversion method — Sigma-Delta/graded-spike
ANN-to-SNN conversion (Brehove et al., ICONS 2026) — was deployed and measured on physical Loihi 2
hardware, proving E1 is achievable for *an* ANN-to-SNN conversion approach on real silicon, but
this method is not QCFS-lineage (it uses Loihi 2's native graded-spike payloads rather than
rate-coded IF neurons trained with the quantization-clip-floor-shift activation). No paper pairs a
QCFS-trained network with a physical chip run.

**4. Do any use first-layer "direct/analog encoding" (real-valued image as constant current) rather than Poisson spikes?**
Yes — this is the dominant convention across the entire lineage, not an exception. QCFS, OPI, SRP,
COS, SlipReLU, and QFFS all follow the Rueckauer et al. (2017) convention of injecting the
real-valued pixel intensities as a constant analog current into the first layer, rather than
Poisson-rate-coding the input. QFFS states this explicitly ("the network input is analog-coded
(Rueckauer et al., 2017)"). No paper in this audit discusses or uses a Poisson-coded input layer
for CIFAR/ImageNet classification; direct/analog encoding is treated as a solved default,
essentially never examined for its hardware feasibility implications (analog current injection is
not what most digital neuromorphic chips such as Loihi natively expose as an input interface —
they expect discrete spike events, so a direct-encoded first layer is itself a nontrivial
translation step that none of the audited papers address).

## Summary statistic

**N = 16** QCFS-lineage / low-T ANN-to-SNN conversion papers audited (main table).
**E1 or E2 (physical silicon, any measurement): 0 / 16.**
**E4 (hardware model/simulator, not silicon): 1 / 16 direct (NeuroFlex), plus 1 borderline
unreported acknowledgment (PASCAL).**
**E5 (pure software simulation, including SynOps/theoretical energy estimates): 15 / 16 (all others).**

Zero of the sixteen QCFS-lineage papers reached E1 or E2. The single documented E1 instance found
in the entire search (Loihi 2, Sigma-Delta Neural Network conversion) belongs to a different,
non-QCFS conversion paradigm, confirming that the "benefit implementations on neuromorphic
hardware" framing that opens the original QCFS paper (and is echoed by nearly every descendant)
remains, eight generations of follow-on papers later, an aspirational claim rather than a
demonstrated one.

## Source list

1. Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN Conversion for
   High-accuracy and Ultra-low-latency SNNs." ICLR 2022. https://arxiv.org/abs/2303.04347
   (OpenReview: https://openreview.net/forum?id=7B3IJMM1k_M)
2. Bu, T., Ding, J., Yu, Z., Huang, T. "Optimized Potential Initialization for Low-latency SNNs."
   AAAI 2022. https://arxiv.org/abs/2202.01440
3. Hao, Z., Bu, T., Ding, J., Huang, T., Yu, Z. "Reducing ANN-SNN Conversion Error through
   Residual Membrane Potential." AAAI 2023. https://arxiv.org/abs/2302.02091
4. Hao, Z., Ding, J., Bu, T., Huang, T., Yu, Z. "Bridging the Gap between ANNs and SNNs by
   Calibrating Offset Spikes." ICLR 2023. https://arxiv.org/abs/2302.10685
5. Jiang, H., Anumasa, S., De Masi, G., Xiong, H., Gu, B. "A Unified Optimization Framework of
   ANN-SNN Conversion." ICML 2023. https://proceedings.mlr.press/v202/jiang23a.html
6. Li, Y., Zeng, Y. "Efficient and Accurate Conversion of SNN with Burst Spikes." IJCAI 2022.
   https://arxiv.org/abs/2204.13271
7. Wang, Y., Zhang, M., Chen, Y., Qu, H. "Signed Neuron with Memory: Towards Simple, Accurate and
   High-Efficient ANN-SNN Conversion." IJCAI 2022. https://www.ijcai.org/proceedings/2022/0347.pdf
8. Hu, Y., Zheng, Q., Jiang, X., Pan, G. "Fast-SNN: Fast Spiking Neural Network by Converting
   Quantized ANN." IEEE TPAMI 2023. https://arxiv.org/abs/2305.19868
9. Li, C., Jones, E., Furber, S. "Unleashing the Potential of SNNs by Dynamic Confidence."
   ICCV 2023. https://arxiv.org/abs/2303.10276
10. Li, C., Ma, L., Furber, S. "Quantization Framework for Fast Spiking Neural Networks."
    Frontiers in Neuroscience 2022. https://www.frontiersin.org/articles/10.3389/fnins.2022.918793/full
11. Li, Y., Geller, T., Kim, Y., Panda, P. "SEENN: Towards Temporal Spiking Early-Exit Neural
    Networks." NeurIPS 2023. https://arxiv.org/abs/2304.01230
12. Yang, H., Yang, S., Zhang, L., Dou, H., Shen, F., Zhao, J. "CS-QCFS: Bridging the performance
    gap in ultra-low latency SNNs." Neural Networks 2024/2025.
    https://doi.org/10.1016/j.neunet.2024.107076
13. Wang, Z., Fang, Y., Cao, J., Ren, H., Xu, R. "Adaptive Calibration: A Unified Conversion
    Framework of Spiking Neural Networks." AAAI 2025 (Oral). https://arxiv.org/abs/2412.16219
    (repo: https://github.com/bic-L/burst-ann2snn)
14. Ramesh, P., Srinivasan, G. "PASCAL: Precise and Efficient ANN-SNN Conversion using Spike
    Accumulation and Adaptive Layerwise Activation." arXiv 2505.01730 (2025).
    (repo: https://github.com/BrainSeek-Lab/PASCAL)
15. Manjunath, V. et al. "NeuroFlex: Column-Exact ANN-SNN Co-Execution Accelerator with
    Cost-Guided Scheduling." arXiv 2511.05215 (2025).
16. Liu, F., Zhao, W., Chen, Y., Wang, Z., Jiang, L. "SpikeConverter: An Efficient Conversion
    Framework Zipping the Gap between ANNs and SNNs." AAAI 2022.
    https://ojs.aaai.org/index.php/AAAI/article/download/20061/19820
17. (Contrast case, not QCFS-lineage) Brehove, M., Tumpa, S.A., Kyubwa, E., Menon, N.,
    Narayanan, V. "Sigma-Delta Neural Network Conversion on Loihi 2." ICONS 2026.
    https://arxiv.org/abs/2505.06417
18. (Contrast case, not QCFS-lineage, RL not classification) "Porting Deep Spiking Q-Networks to
    Neuromorphic Chip Loihi." ACM 2021. https://doi.org/10.1145/3477145.3477159
19. (Contrast case, not QCFS-lineage, generic Rueckauer-toolbox conversion) Loihi vs. Intel Neural
    Compute Stick 2 comparison paper, SNN Conversion Toolbox + NxTF backend.
    https://export.arxiv.org/pdf/2210.05006v2.pdf
20. Sinabs/DYNAP-CNN (Speck) deployment documentation (SynSense toolchain, generic, not paired
    with any QCFS paper found). https://sinabs.readthedocs.io/
