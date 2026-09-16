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
converted the same way reached 8.52% error at roughly 400 timesteps, spanning 1,753
neuromorphic cores across 14 Loihi chips, at 102 mJ, 340 ms, and 34,926 µJ·s EDP
[rueckauer-2021-nxtf], [lenz-2023-quartz]. The same paper also ran SLAYER-trained
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

## References

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
