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
[du-2025-temporal-flexibility]. This is genuine physical-silicon measurement, but Speck2e is fully event-driven
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
| 18 | 4.3 | Temporal Flexibility / MTT [du-2025-temporal-flexibility] | Stage-randomized T during training | direct/analog + event | 1-20, or event-driven | NMNIST | Speck2e (physical) | Spike-difference vs. software sim, on-chip accuracy | E1/E2 |
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

## Reference list

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
- [du-2025-temporal-flexibility] Du, K., Wu, Y., Deng, S., Gu, S. "Temporal Flexibility in Spiking Neural
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
