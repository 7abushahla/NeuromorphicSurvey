# 6. Hardware and Software Deployment Stack

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

## References

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
