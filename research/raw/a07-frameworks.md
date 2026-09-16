# A07 — SNN Training and Simulation Frameworks: Hardware Reach

Research pass for the neuromorphic-deployment survey. Primary tool: Exa web search / fetch against
official documentation (ReadTheDocs, GitHub READMEs, official framework sites) and the peer-reviewed
framework papers. Quotations are copied verbatim from documentation where reset semantics are at
stake, per instructions. "NOT FOUND" is used where a fact could not be verified from a primary source
in this pass.

---

## 1. SpikingJelly (Fang et al., *Science Advances* 2023)

**(a) What it is for.** A PyTorch-based, full-stack toolkit: "we present the SpikingJelly framework
... we contribute a full-stack toolkit for preprocessing neuromorphic datasets, building deep SNNs,
optimizing their parameters, and deploying SNNs on neuromorphic chips" [S1]. Training acceleration
claimed at 11x over prior methods [S1].

**(b) Neuron models and reset semantics.**
IFNode / LIFNode constructor parameter `v_reset`: "reset voltage of this neurons layer. If not `None`,
the neuron's voltage will be set to `v_reset` after firing a spike. If `None`, the neuron's voltage
will subtract `v_threshold` after firing a spike" [S2].

Two reset equations are named explicitly:
- Hard reset: `V[t] = H[t]·(1−S[t]) + V_reset·S[t]`
- Soft reset: `V[t] = H[t] − V_threshold·S[t]` [S2]

Default: "The default value of `v_reset` in the `__init__` function of
`spikingjelly.activation_based.neuron` is `1.0` and the neuron will use hard reset by default. If we
set `v_reset = None`, then the neuron will use the soft reset." [S2]

So the neuron class **defaults to hard reset** (v_reset=1.0), but soft reset (`v_reset=None`) is what
the ANN2SNN conversion path requires and sets explicitly: "ReLU activations in ANNs are strongly
related to the firing rates of IF neurons with subtractive reset, where the membrane voltage is reset
by subtracting V_threshold. This neuron update method is the Soft reset method... `RateCodingRecipe`
uses this relationship for conversion." [S3] Converted models instantiate `IFNode(v_threshold=1.0,
v_reset=None, ...)` [S3].

**(c) Time model.** Every module carries a `step_mode` attribute (`'s'` single-step or `'m'`
multi-step): "A module in the single-step mode receives X[t] and outputs Y[t]... In contrast, a module
in the multistep mode receives X = {X[0], X[1], ..., X[T−1]} and outputs Y = {Y[0], ..., Y[T−1]}...
Correspondingly, the SNN with all modules in a single-step or multistep mode follows the step-by-step
or layer-by-layer propagation pattern, respectively" [S1]. T is a single scalar shared by the whole
network in multi-step mode; in single-step mode the user writes one Python `for t in range(T)` loop
that drives *every* layer through the same t. There is no per-layer T parameter anywhere in the neuron
or module API surfaced in the documentation reviewed — `step_mode` toggles single vs. multi step
processing of one shared T, it does not allow heterogeneous T across layers.

**(d) Export / hardware deployment paths (officially documented).**
- **Lava / Loihi.** `spikingjelly.activation_based.lava_exchange`: "To deploy SNNs on Loihi, we need
  to use Lava. SpikingJelly provides conversion modules to convert the SNN trained by SpikingJelly to
  the Lava SNN format... `SpikingJelly -> Lava DL -> Lava -> Loihi`" [S4]. Workflow: build with
  `BlockContainer` (currently only supports `CubaLIFNode`, with automatic conversion of `IFNode`/
  `LIFNode` into `CubaLIFNode`), export to hdf5 via `export_hdf5`, then "Lava can rebuild the SNN and
  run the SNN on Loihi, or the CPU-simulated Loihi" [S4]. A worked example (`lava_mnist`) is given with
  logged output: `test acc[sj] = 0.9855`, `test acc[lava dl] = 0.9863` — this is a software/CPU-simulated
  Loihi run in the documented example, not a report of silicon measurement [S4].
- **NIR** (Neuromorphic Intermediate Representation) exchange module, `nirtorch`/`nir` interop listed
  as an installable extra [S5].
- **Lynxi** chip: a dedicated tutorial "在灵汐芯片上推理" ("Inference on Lynxi chip") is listed in the
  current docs table of contents [S6], and the README's deployment table lists "NIR, Lava, and
  Lynxi-oriented exchange interfaces for neuromorphic workflows" [S5].
- No CUDA-only path is "hardware deployment" in the neuromorphic sense; CuPy/Triton backends (below)
  are GPU acceleration for training/simulation, not neuromorphic silicon.

**`ann2snn` module — what conversion it implements.** Current (V2) docs: two conversion executors,
`FXConverter` (traces a `torch.fx.GraphModule`) and `ModuleConverter` (direct `nn.Module` tree
replacement, used for e.g. SpikeZIP/Qwen2 paths) [S7]. For the classical CNN/rate-coding path,
`RateCodingRecipe` "directly matches exact `nn.ReLU` modules, calibrates them with `VoltageHook`, and
replaces each activation with `VoltageScaler(1/s) -> IFNode -> VoltageScaler(s)`" [S7]. Calibration
(normalization) modes: `mode="max"` (MaxNorm, uses the maximum activation) [S8], `mode="99.9%"`
(RobustNorm, 99.9th percentile of activations, following the cited literature) [S8], or a float in
`(0,1]` for manual scaling [S8]. `LocalThresholdBalancingRecipe` implements local-threshold-balancing
as an alternative recipe [S8]. Conv-BN fusion (`fuse_flag=True` by default) happens before calibration
[S7][S8]. This is the classical Diehl/Cao-style weight/threshold-normalization ANN2SNN conversion
family, not a training-based conversion.

**`lava_exchange` module.** Converts SpikingJelly modules/networks into Lava DL format for Loihi
deployment; provides `to_lava_neuron` (currently IF/LIF only), synapse converters
(`linear_to_lava_synapse_dense`, `conv2d_to_lava_synapse_conv`, `avgpool2d_to_lava_synapse_pool`), and
`BlockContainer` to mimic Lava DL's `Blocks` with matching quantized synapse/neuron outputs
[S4]. Data-layout note: "The default data format in Lava DL is `shape = [N, *, T]`... SpikingJelly in
multi-step mode... uses the data format `shape = [T, N, *]`", requiring `TNX_to_NXT`/`NXT_to_TNX`
conversion helpers [S4].

**Multi-step vs. single-step, CuPy backend.** "Some neurons support for `cupy` backend when using
multi-step mode. In addition, `triton` backend is also available for `IFNode`, `LIFNode`,
`ParametricLIFNode`, etc. `cupy` and `triton` backend can accelerate forward and backward" [S2]. The
Science Advances paper: CuPy is used for "semiautomatic CUDA code generation" — raw CUDA kernels are
written as Python strings and JIT-compiled/cached by CuPy, fusing per-timestep neuronal-dynamics
kernels (FPTT/BPTT) into single CUDA kernels rather than looping many small kernel launches, which is
the source of the claimed training speedup [S1]. Benchmarked: CuPy-backend LIF training/inference is
much faster than the naive PyTorch for-loop implementation, and execution time scales roughly linearly
(not quadratically, for training) with T under the fused-kernel approach [S1].

**(e) Maintenance status (2026).** Actively maintained. GitHub: "Last push: 2026-06-26" as of the
crawl, 70 contributors, 2K+ stars [S9]. Current maintainers listed "since July 2024": Yifan Huang
(AllenYolk), Peng Xue (PengXue0812), succeeding the original core maintainer group [S9]. A major V2
refactor is in progress: CHANGELOG entries `2.0.0.dev0` (2026-07-09) and `2.0.0.dev1` (2026-08-14) are
present [S10]; a commit from 2026-05-31 shows active feature work (distributed training API,
op-counter/energy-estimation refactor) [S11]. Release policy: post-V2 uses SemVer
(`MAJOR.MINOR.PATCH`); pre-V2 used an odd/even `0.0.0.0.X` scheme (odd = dev, even = stable PyPI)
[S9][S10].

---

## 2. snnTorch (Eshraghian et al., *Proceedings of the IEEE* 2023)

**(a) What it is for.** PyTorch-native SNN training library; companion paper "Training Spiking Neural
Networks Using Lessons From Deep Learning," *Proc. IEEE*, 111(9), Sept. 2023 [T1].

**(b) Neuron models / reset semantics.** `snn.Leaky` (first-order LIF) constructor:
`reset_mechanism='subtract'` is the literal default value in the signature [T2]. Documented options:
"reset_mechanism (str, optional) – Defines the reset mechanism applied to `mem` each time the
threshold is met. Reset-by-subtraction: 'subtract', reset-to-zero: 'zero', none: 'none'. Defaults to
'subtract'" [T2][T3]. Equations given:
- subtract: `U[t+1] = βU[t] + I_in[t+1] − R·U_thr`
- zero: `U[t+1] = βU[t] + I_syn[t+1] − R·(βU[t] + I_in[t+1])` [T2]

Tutorial commentary: "Applying `"subtract"` (the default value in `reset_mechanism`) is less lossy,
because it does not ignore how much the membrane exceeds the threshold by... applying a hard reset with
`"zero"` promotes sparsity and potentially less power consumption when running on dedicated
neuromorphic hardware." [T3] This is snnTorch's own documented rationale connecting reset choice to
target hardware.

**(c) Time model.** snnTorch neurons are stateful `nn.Module`s that process one timestep per call
(`spk, mem = lif(x)`); the user writes the outer `for step in range(num_steps):` loop explicitly and
calls the same network object once per step [T3]. There is a single, network-wide `num_steps`/
`time_step` variable; no per-layer step count is exposed in the neuron or `Leaky`/`Lapicque` API
reviewed.

**(d) Export / hardware paths.** NOT FOUND as an official snnTorch deployment path to physical silicon
in the pages fetched; the documentation frames `reset_mechanism="zero"` as advantageous specifically
for eventual dedicated-hardware deployment [T3], but no documented export pipeline to a named chip was
located in this pass (snnTorch integrates with the cross-framework NIR standard per third-party
sources, but this was not verified against snnTorch's own docs in this pass).

**(e) Maintenance status.** Actively documented; latest stable docs (v1.0.0) and a `0.9.4`/`latest`
dev-docs track were both live at crawl time [T2].

---

## 3. Norse

**(b) Neuron models / reset semantics.** `norse.torch.functional.lif.LIFParameters` default:
`v_reset=tensor(0.)` [N1][N2]. The LIF step equation used throughout the functional and module APIs
(`LIFCell`, `LIFRecurrentCell`) is: `v = (1−z)·v + z·v_reset` [N2][N3] — i.e., membrane potential is
replaced by `v_reset` whenever a spike `z` occurs. This is definitionally the **hard-reset** equation,
and it is the only reset mechanism exposed in the `LIF`/`LIFCell` classes documented; `v_reset` is a
settable float/tensor rather than an optional `None` switch as in SpikingJelly. A separate
`norse.torch.functional` submodule, "`norse.torch.functional.reset` — Functions for reset mechanisms,"
is listed in the API index [N1], indicating other reset functions exist in the codebase, but their
semantics were not verified in this pass. Because `v_reset` defaults to 0, **Norse's documented default
neuron behavior is reset-to-zero (hard reset)**, in contrast to SpikingJelly's and snnTorch's
soft-reset defaults for ANN2SNN-style use (note SpikingJelly's neuron *constructor* default is also
hard reset, but the value defaults to `v_reset=1.0` there, not `0.0`).

**(c) Time model.** `LIF` / `LIFRecurrent` "wraps a `LIFCell` in time such that the layer keeps track
of temporal sequences of spikes. After application, the layer returns a tuple containing (spikes from
all timesteps, state from the last timestep)" [N3][N4] — i.e., time is handled by iterating the `Cell`
internally over one shared sequence length; `dt` (default `0.001`) is the discretization step, again a
single scalar for the whole layer/network, not per-layer-configurable timestep counts.

**(d) Export / hardware paths.** Norse exports to **NIR** (`norse.to_nir`), confirmed via third-party
NIR-consumer documentation showing a working Norse → NIR example (`graph = norse.to_nir(model,
torch.randn(1,128))`) [N5]. That same third-party source flags a caveat: "Norse's own export-import
cycle produces different spike patterns on identical input (verified with Norse 1.1.0)" for the
NIR round-trip [N5] — evidence the export path is functional but not fully numerically stable as of
that check. No official Norse documentation page describing a direct path to a specific neuromorphic
chip was located in this pass; NOT FOUND for a first-party Norse hardware-deployment doc.

**(e) Maintenance status.** NOT FOUND (not directly checked for last-commit recency in this pass); docs
site (`norse.github.io/norse`) is live with a v1.0.0 generated-API reference.

---

## 4. Lava and Lava-DL (Intel)

**(a) What it is for.** "Lava is an open-source software framework for developing neuro-inspired
applications and mapping them to neuromorphic hardware... Lava is platform-agnostic so that
applications can be prototyped on conventional CPUs/GPUs and deployed to heterogeneous system
architectures spanning both conventional processors as well as a range of neuromorphic chips such as
Intel's Loihi" [L1]. Lava-DL (`lava.lib.dl`) is "a library of deep learning tools within Lava that
support offline training, online training and inference methods for various Deep Event-Based
Networks," containing `slayer` (SLAYER 2.0, native training), `bootstrap` (fast rate-coded-SNN
training via an ANN surrogate), and `netx` (hdf5 → Lava-process inference deployment) [L2][L3].

**(b) Neuron models and reset semantics.** SLAYER 2.0 supports several neuron dynamics families:
Leaky Integrator (CUBA), Resonator, Adaptive Integrator with Refractory Dynamics, Adaptive Resonator
with Refractory Dynamics, combined into named models `slayer.neuron.{cuba, alif, rf, rf_iz, adrf,
adrf_iz, sigma_delta}` [L4]. The **core Lava process** reference `PyLifModel` (a CPU-backed Loihi
process model) shows the neuron's actual reset in code: `s_out = self.v > self.vth; self.v[s_out] = 0
# Reset voltage to 0. This is Loihi-1 compatible.` [L1] — i.e., the documented reference LIF process
model in Lava core performs **hard reset-to-zero**, explicitly annotated as matching Loihi-1 hardware
behavior. No soft-reset variant was found documented for this canonical process model in the pages
fetched.

**(c) Time model.** Lava's execution model is asynchronous message-passing between stateful
"Processes" over discretized time steps under a Loihi synchronization protocol
(`LoihiProtocol`) [L1]; `net.run(condition=RunSteps(total_run_time), run_cfg=...)` runs the whole
compiled network for a single shared `total_run_time` [L2][L3]. No per-layer timestep-count mechanism
is documented; the run duration is a property of the run condition applied to the whole compiled
Process network.

**(d) Export / hardware deployment paths.** This is the most hardware-committed framework in this
survey: "Lava is platform-agnostic so that applications can be prototyped on conventional CPUs/GPUs and
deployed to heterogeneous system architectures spanning both conventional processors as well as a range
of neuromorphic chips such as Intel's Loihi... the specific components of Magma needed to compile
processes specifically to Intel Loihi chips remain proprietary to Intel" [L1]. Lava-DL's documented
pipeline: train with `slayer`/`bootstrap` → export hdf5 → `netx` loads it "as Lava Processes, which can
be directly run on a desired backend," with an explicit `Loihi1SimCfg()` run-config shown in the docs
[L2][L3] (a *simulated*-Loihi config; the docs also describe physical-Loihi run configs elsewhere in
the Magma/Loihi-protocol stack, but the exact physical-hardware `RunCfg` was not captured verbatim in
this pass).

**(e) Maintenance status (2026) — important finding.** **Lava and Lava-DL are formally
discontinued/archived.** GitHub README (`lava-nc/lava-dl`): "Intel is developing the next-generation
Loihi architecture and SDK to power the coming era physical AI. The new SDK is built on open-standard
AI frameworks to lower the adoption barrier while enabling maximum performance and efficiency on
Loihi. **All Lava repositories are archived. Stay tuned for announcements about our new SDK and next
generation Loihi processor.**" [L3] This means the Lava/Lava-DL stack documented above (SLAYER 2.0,
Bootstrap, NetX, the hdf5 exchange format) is a **legacy, frozen path** as of the 2026 crawl; Intel is
replacing it with an unnamed, not-yet-released successor SDK.

---

## 5. Sinabs (SynSense)

**(a) What it is for.** PyTorch-based SNN library from SynSense with a first-party deployment path to
SynSense's own DYNAP-CNN-family edge chips (Speck).

**(b) Neuron models / reset semantics.** Core spiking layer is `sinabs.layers.IAF` (Integrate-and-Fire).
Reset is configurable via `reset_fn`: `MembraneSubtract()` (soft/subtractive) or `MembraneReset()`
(hard, to a fixed value) [SI1]. For the Speck hardware target specifically, documentation states: "Our
devkit provides two types of reset mechanism for the spiking neuron's membrane potential. 1. Reset to 0
after firing 1 spike. 2. Subtract by spiking-threshold after firing 1 spike. **By default, our devkit
use the second strategy for membrane potential reset.**" [SI2] — i.e., **subtractive/soft reset is the
documented hardware default**, with explicit guidance: "If you use an ANN-to-SNN conversion, then you
should choose the second one strategy... If you train an SNN with a 'reset to 0' strategy, then you
should choose the first one" [SI2]. The hardware-config switch is `samna` `return_to_zero`: `True` =
hard reset, `False` (documented default behavior) = soft/subtract [SI2].

**(c) Time model.** Standard PyTorch `nn.Module`-style forward over a batched, single shared time axis
(`torch.Tensor` with a T dimension); layers are placed onto physical chip cores (`chip_layers_ordering`)
each running the same global event stream — no per-layer independent T was documented [SI3].

**(d) Export / hardware deployment paths.** First-party, fully worked path to **physical silicon**:
`sinabs.backend.dynapcnn.DynapcnnNetwork` converts a trained `sinabs` SNN into a sequence of
`DynapcnnLayer`s, quantizes parameters to the chip's native precision ("8 bits for weights and 16 bits
for membrane potentials" by default under `discretize=True`) [SI3], is placed onto chip cores
(`chip_layers_ordering="auto"` or manual), and deployed with `model.to("speck2fdevkit:0", ...)` [SI3].
A worked example streams real DVS-style events to a connected Speck device and reports on-chip test
accuracy: `print(f"Test accuracy on speck: {accuracy:.2%}")` [SI4] — this is a **measured, on-silicon
accuracy run** (classification **E1/E2**-type evidence; the docs example computes accuracy on-chip but
this pass did not confirm whether latency/power were also measured in the same run).

**(e) Maintenance status.** Active, versioned docs through at least `v3.1.4.dev13` observed at crawl
time [SI3].

---

## 6. Rockpool (SynSense)

**(a) What it is for.** SynSense's second SNN library, targeting deployment to the **Xylo** family of
ultra-low-power always-on audio/sensor SNN chips (distinct product line from Speck/DYNAP-CNN, which
Sinabs targets).

**(b) Neuron models / reset semantics.** Hidden/output neurons on Xylo are digital LIF with exponential
(bit-shift-approximated) synapses. Hardware spec, quoted: "Synchronous time-stepped architecture with a
global time-step `dt`... Up to N_hid = 1000 digital LIF hidden neurons... **Subtractive reset, with up
to 31 events generated per time-step per neuron**... Reset during event generation is performed by
subtraction" [R1]. So **Xylo hardware, and therefore Rockpool's documented default, uses subtractive
(soft) reset**, and — notably — Xylo neurons can emit more than one spike per timestep (up to 31),
which is not the binary single-spike-per-step model assumed by most conversion theory.

**(c) Time model.** "Synchronous time-stepped architecture with a global time-step `dt`" [R1] — the
whole chip runs one shared clock; deployment tooling (`mapper()`, `config_from_specification()`) maps
network layers onto Xylo's fixed hardware resources under this one global `dt`, and simulation objects
(`XyloSim`) mirror the same single-`dt` execution [R2][R3]. No per-layer distinct time-step count is
exposed; `time_constants_per_layer` in `SynNet` controls how many distinct **synaptic time constants**
(not distinct simulated *step counts*) are allocated per layer [R4] — a different axis of
heterogeneity than "layer A runs T=2 while layer B runs T=4."

**(d) Export / hardware deployment paths.** First-party, fully worked path to **physical silicon**:
train with `LIFTorch`/`SynNet` → `mapper()` → quantize
(`rockpool.transform.quantize_methods`) → `config_from_specification()` → deploy via
`XyloSamna`/`XyloMonitor` to a connected Xylo HDK, with a bit-precise `XyloSim` software model
available for pre-deployment verification [R2][R3]. A worked audio-classification example
(`XyloAudio 3`) deploys a trained multiclass model, drives it with live microphone input in real time,
and records on-chip power in `io`/`analog`/`digital` channels via `record_power=True` [R3] — this is
**measured, on-silicon accuracy *and* power evidence (E1)**.

**(e) Maintenance status.** Actively versioned docs (`rockpool.ai`), multiple point releases (3.0.x,
3.1.x) observed live at crawl time [R2][R3].

---

## 7. Brian2, NEST, GeNN, BindsNET — neuroscience-oriented simulators

**Do they support deep converted CNNs?**

- **BindsNET.** Built directly on PyTorch tensors specifically to leverage GPU batching and existing
  `torch.nn.functional` ops (e.g., `Conv2dConnection` reuses `torch.nn.conv2d`) [B1]. Documented
  capability: "Automatic conversion of deep neural network models implemented in PyTorch or specified
  in the ONNX format to near-equivalent spiking neural networks (as in Diehl et al., 2015)" [B1] — so
  BindsNET does document an ANN2SNN conversion path, and is PyTorch-native (GPU-capable), but its
  primary design center is STDP/reinforcement-learning-style research rather than deep CNN-scale
  inference; comparative benchmarking in mlGeNN found BindsNET "uses the same dense tensor operations
  as the ANN... performance is very similar to that of the ANN multiplied by T" [G1], i.e., it does not
  exploit spike sparsity for speed.
- **GeNN (via mlGeNN).** GeNN itself is a GPU code-generation framework for spiking dynamics; the
  companion **mlGeNN** library adds explicit deep-CNN support: "mlGeNN — a Python library for the
  conversion of artificial neural networks (ANNs) specified in Keras to spiking neural networks (SNNs)"
  with "extensions to efficiently support convolutional connectivity and batching" [G1]. This is
  demonstrated at real deep-CNN scale: VGG-16 and ResNet-34/ResNet-20 converted and evaluated on
  **CIFAR-10 and ImageNet** [G1] — e.g., VGG-16 few-spike-converted SNN reaches 70.2% ImageNet
  accuracy vs. 70.3% ANN baseline [G1]. This is **software/GPU simulation only (E5)** — GeNN targets
  NVIDIA GPUs (or CPU), not a neuromorphic ASIC; the paper explicitly separates this GPU-simulator
  approach from "neuromorphic hardware... which is not considered here" in the related GeNN/NEST
  large-scale-simulation study [G2].
- **NEST.** Purpose-built for "the parallelized simulation of large and densely connected recurrent
  networks of point neurons," under continuous development since the 1990s (originally SYNOD), and used
  in this survey's sources for large biologically-realistic cortical-microcircuit-scale models (up to
  ~4.13×10^6 neurons in cited multi-area cortical benchmarks), not deep converted CNNs [G2]. No CNN- or
  ANN2SNN-scale demonstration for NEST was found in the sources reviewed in this pass; NEST is exposed
  as one of several possible **PyNN backends** for ANN2SNN pipelines built on top of it (see §8 and the
  SNN-toolbox note below), but that CNN capability is provided by the conversion tool (e.g., SNN
  Toolbox), not by NEST's own native API.
- **Brian2.** Also neuroscience-first (differential-equation-defined neuron/synapse dynamics, Python
  front end, C++ code generation) [B2]; GPU acceleration is available only through the separate
  **Brian2GeNN** bridge package, which "provides an interface to use GeNN as a backend device in
  Brian2... allows users to run their Brian 2 scripts on NVIDIA GPU accelerators" [B3][B4], with the
  caveat that "not all features of Brian work with Brian2GeNN" [B4]. Brian2 is one of the SNN Toolbox's
  documented ANN2SNN output/simulation backends (see below), so it can run converted deep networks via
  that external tool, but this is not a native Brian2 capability.

**Third-party note found in this pass — SNN Toolbox.** A separate conversion tool, `snntoolbox`,
explicitly targets Brian2/NEST/NEURON (via PyNN), and neuromorphic hardware, as *output* simulators for
converted deep networks: "the resulting spiking network can be exported for simulation in a spiking
simulator or deployment on dedicated spiking neuron chips... pyNN models... allows running the
converted net in a spiking simulator like Brian, Nest, Neuron... Brian2... a built-in simulator based
on Keras, called INIsim" [ST1]. This confirms Brian2/NEST *can* run deep converted CNNs, but only via
this external ANN2SNN toolbox layered on top, not through their own native deep-learning-oriented APIs.

**Benchmarking context.** A published simulator comparison found "BindsNET simulator has the best
speed and scalability for most of the SNN workloads... on a single core CPU. However, when comparing
the simulators leveraging the GPU capabilities, Brian2GeNN outperforms the others... NEST performs the
best for small sparse networks and is also the most flexible simulator" [G3] — i.e., these tools'
comparative strengths lie in classical neuroscience-style workloads, not deep CNN-scale inference,
GeNN/mlGeNN being the documented exception for CNN-scale conversion.

**Hardware.** None of Brian2, NEST, GeNN, or BindsNET has a documented native path to a physical
neuromorphic chip in the sources reviewed (GeNN and NEST both explicitly target CPU/GPU, not ASICs; see
§8 for PyNN, which is the layer that actually reaches SpiNNaker/BrainScaleS silicon and can use NEST as
a co-backend for the software side of an experiment).

---

## 8. PyNN — cross-simulator API

**(a) What it is for.** "PyNN (pronounced 'pine') is a simulator-independent language for building
neuronal network models... you can write the code for a model once, using the PyNN API... and then run
it without modification on any simulator that PyNN supports (currently NEURON, NEST and Brian) **as
well as on certain neuromorphic hardware systems**" [P1].

**(d) Hardware backends.** Two physical neuromorphic systems are documented as PyNN backends:
- **SpiNNaker** ("many-core," Manchester): PyNN backend module `pyNN.spiNNaker` (via the sPyNNaker
  software stack) [P2][P3].
- **BrainScaleS** ("physical model," Heidelberg, analog wafer-scale and single-chip BrainScaleS-2):
  PyNN backend `pynn_brainscales.brainscales2`, with hardware-specific `setup()` extra parameters
  (e.g. `neuronPermutation`, `enable_neuron_bypass`, `initial_config` for a calibration result) [P4][P5].
  BrainScaleS offers "highly accelerated operation (10^4 x real time)" as an analog physical-model
  system, versus SpiNNaker's real-time digital many-core operation [P3].
Both are accessed through the EBRAINS/HBP Neuromorphic Computing Platform, which runs user PyNN scripts
as queued jobs against the chosen hardware backend [P3]. This is a documented **E1/E2-class** path: real
experiments are run on physical BrainScaleS wafers/chips and physical SpiNNaker boards via this API,
not merely simulated.

**(b)/(c)** PyNN itself does not define its own neuron reset semantics or time model beyond exposing
"a library of standard neuron, synapse and synaptic plasticity models, which have been verified to work
the same on the different supported simulators" [P1] — reset/timestep behavior is inherited from
whichever backend (NEST/NEURON/Brian/SpiNNaker/BrainScaleS) executes the model; NOT independently
specified by PyNN.

---

## 9. spyx, SLAYER, NengoDL — brief

- **spyx.** "A compact spiking neural network (SNN) library built on JAX and Flax NNX... Trained models
  can be exported to neuromorphic hardware via the Neuromorphic Intermediate Representation (NIR)."
  [SP1] Neuron zoo: LIF, ALIF, CuBaLIF, LI, IF, "and their recurrent variants" [SP1][SP2]. No
  first-party direct-to-chip deployment tool is documented beyond the NIR export hook; hardware reach is
  therefore **E3 (documented path via NIR, no published on-chip run located in this pass)**. Actively
  developed (JAX/Flax NNX rewrite of an earlier Haiku-based version) [SP2].
- **SLAYER** (as `lava.lib.dl.slayer`, i.e., SLAYER 2.0 inside Lava-DL). Covered in §4; this is the
  neuron/training library whose hdf5 export feeds Lava's `netx` for Loihi deployment, and is therefore
  now under the same "all Lava repositories are archived" status as the rest of Lava-DL [L3]. The
  original standalone SLAYER (`bamsumit/slayerPytorch`) is a separate, earlier project that
  `lava.lib.dl.slayer` describes itself as "an enhanced version of" [L4].
- **NengoDL / NengoLoihi.** NengoDL trains SNN-compatible models by using "a differentiable
  approximation of the spiking neurons during the training process, and the actual spiking neurons
  during inference" (the Hunsberger & Eliasmith 2016 method), automatically substituted by the
  framework [ND1]. Separately, **NengoLoihi** is "a backend for running Nengo models on Intel's Loihi
  architecture... contains a Loihi emulator backend for rapid model development and easier debugging,
  and a Loihi hardware backend for running models on a Loihi board," using Intel's proprietary NxSDK
  API on a "superhost" connected to physical Loihi boards [ND2][ND3]. This is a genuine, detailed,
  first-party **E3-or-better** documented hardware path (installation/configuration docs down to board
  and host wiring are provided [ND3][ND4]), though this pass did not locate a specific *published
  accuracy or power number* from a NengoLoihi silicon run, so it is classified **E3** absent that
  confirmation.

---

## Answers to the specific survey questions

### Q1 — Can any framework express a per-layer timestep horizon (layer A runs T=2, layer B runs T=4) in one forward pass?

**No framework in this survey documents this.** In every case checked, the forward loop is driven by a
single, network-wide time index:

- SpikingJelly: `step_mode` (`'s'`/`'m'`) is set per-module, but the *value* of T being iterated is one
  shared scalar for the whole network — single-step mode requires the user to write one Python
  `for t in range(T)` loop that calls every layer at the same `t`; multi-step mode processes a shared
  tensor of shape `[T, N, *]` end to end [S1][S2].
- snnTorch: identical pattern — one `for step in range(num_steps)` loop external to the network, the
  same `num_steps` driving every `Leaky`/LIF layer call [T3].
- Norse: `LIF`/`LIFRecurrent` wrap a `Cell` "in time" internally, again over one sequence length /
  `dt` shared by the layer and, by composition, the network [N3][N4].
- Lava: `net.run(condition=RunSteps(total_run_time), ...)` runs the whole compiled Process network for
  one `total_run_time` under the Loihi synchronization protocol [L1][L2].
- Rockpool/Xylo: the hardware itself is architecturally "a synchronous time-stepped architecture with a
  **global** time-step `dt`" [R1] — this is a hardware-level guarantee, not just a software-API
  convention, so per-layer T is physically impossible on Xylo as currently documented.
- Sinabs/Speck: chip cores are placed and run on shared event streams under one clocking scheme; no
  per-core independent step count is exposed in the deployment API reviewed [SI3].
- PyNN: inherits whatever global-clock behavior its backend (NEST/NEURON/Brian/SpiNNaker/BrainScaleS)
  uses; none of those backends were found to expose independent per-population/per-layer step counts.

The underlying reason, stated most explicitly in the SpikingJelly paper itself, is architectural: "For
stateful layers such as spiking neurons, Y[t] depends on not only X[t] but also the hidden states
H[t−1], which successively depend on X[t−1], X[t−2], ..., X[0]. Thus, the for-loop concerning time
steps is inevitable" [S1] — every framework's execution model is built around exactly one such
for-loop (in Python, in a compiled kernel, or on synchronous hardware) per network, not one per layer.
Rockpool's `SynNet` exposes `time_constants_per_layer`, and Lava-DL's `alif`/resonator neuron families
expose per-neuron-learnable time *constants*, but in both cases this varies the neuron's **decay rate**
per layer, not the **number of simulated steps** per layer within one forward pass — a materially
different axis of heterogeneity than the question asks about. **Two unrelated, non-mainstream,
independently-published research repositories** turned up during this search (an FPGA-targeting
"SC-NeuroCore" project and a "spikeDE" library) that do implement genuine multi-clock, per-layer-step
scheduling (`MultiClockSNN`, `clock_intervals` per layer) [MC1]; these are not part of the nine
frameworks surveyed here, are not established/widely-adopted tools, and their claims were not verified
beyond their own documentation — flagged for awareness only, not as a qualification of the "none of the
mainstream frameworks" finding above.

### Q2 — Which frameworks default to reset-by-subtraction (soft) vs. reset-to-zero (hard)?

| Framework | Documented default | Source |
|---|---|---|
| SpikingJelly (`IFNode`/`LIFNode` constructor) | **Hard** (`v_reset=1.0` by default); soft reset requires explicit `v_reset=None`, which is what the `ann2snn` conversion recipe sets | [S2][S3] |
| snnTorch (`Leaky`, `Lapicque`, etc.) | **Soft** (`reset_mechanism='subtract'` is the literal default) | [T2][T3] |
| Norse (`LIFParameters`) | **Hard** (`v_reset=tensor(0.)`; the documented step equation always performs `v=(1−z)v+z·v_reset`, i.e. hard reset, with reset value 0) | [N1][N2] |
| Lava core `PyLifModel` (Loihi-1-compatible reference process) | **Hard** (`self.v[s_out] = 0 # Reset voltage to 0. This is Loihi-1 compatible.`) | [L1] |
| Sinabs / Speck (SynSense) | **Soft** ("By default, our devkit use the second strategy" = subtract-by-threshold) | [SI2] |
| Rockpool / Xylo (SynSense) | **Soft** ("Reset during event generation is performed by subtraction," a hardware-architecture property) | [R1] |
| Lava-DL SLAYER (`cuba` etc.) | NOT FOUND (reset polarity not stated explicitly in the module pages fetched) | — |
| PyNN | Inherited from backend; not independently specified | [P1] |

This directly supports the conversion-literature requirement noted in the task: SpikingJelly's and
Norse's neuron *classes* default to hard reset, and a user (or, in SpikingJelly's case, the `ann2snn`
recipe itself) must deliberately override that default to soft reset to satisfy ANN2SNN theory: "ReLU
activations in ANNs are strongly related to the firing rates of IF neurons with subtractive reset"
[S3]. The two vendor hardware stacks with an explicit ANN2SNN use case documented in their own guidance
(Sinabs/Speck) ship **soft reset as the hardware default**, with the docs explicitly telling users to
switch to hard reset only if they trained natively with reset-to-zero [SI2]. Xylo/Rockpool's soft reset
is a fixed hardware property, not a software default that could be flipped [R1].

### Q3 — Which frameworks have an actual documented path to physical neuromorphic hardware, and to which chip?

| Framework | Chip(s) | Classification | Evidence |
|---|---|---|---|
| Sinabs (SynSense) | Speck / DYNAP-CNN family | **E1/E2** — worked example runs real events through a connected Speck device and reports on-chip test accuracy | [SI3][SI4] |
| Rockpool (SynSense) | Xylo (Audio 2, Audio 3, other Xylo variants) | **E1** — worked example deploys to a connected Xylo HDK, runs live microphone audio in real time, and records on-chip power per channel (`io`/`analog`/`digital`) | [R2][R3] |
| PyNN | SpiNNaker (Manchester); BrainScaleS-1/2 (Heidelberg) | **E1/E2** — documented as a live queued-job platform (EBRAINS/HBP Neuromorphic Computing Platform) running user PyNN scripts on physical boards/wafers | [P1][P3][P4] |
| Lava / Lava-DL (Intel) | Loihi (1 and 2, per Lava's own docs, plus explicit "Loihi-1 compatible" process code) | **E3** as currently documented (`netx`/hdf5 → Lava Processes → run on "a desired backend"; the worked MNIST example in the docs uses a CPU-simulated run, not a reported physical-Loihi accuracy number) — and now a **frozen/legacy** path since "all Lava repositories are archived" [L1][L2][L3] | [L1][L2][L3] |
| SpikingJelly | Loihi (via `lava_exchange` → Lava DL → Lava); Lynxi chip (dedicated tutorial) | **E3** — documented conversion/export pipeline exists and a runnable example is given, but the example's reported accuracy (`test acc[lava dl] = 0.9863`) is from the Lava-DL software step prior to/without a stated physical-Loihi run; Lynxi path was located only as a tutorial title, not independently verified for a published on-chip number in this pass | [S4][S6] |
| NengoLoihi (Nengo/NengoDL ecosystem) | Loihi | **E3** — detailed first-party hardware/emulator backend, board-and-host setup docs, but no specific published accuracy/power figure from a silicon run was located in this pass | [ND2][ND3][ND4] |
| spyx | Unspecified, via NIR | **E3** — export hook documented, no chip-specific worked deployment example found | [SP1] |
| snnTorch, Norse, Brian2, NEST, GeNN, BindsNET | — | **E5** (software/GPU simulation only) — no first-party documented path to a physical neuromorphic chip found in this pass (third-party NIR export exists for Norse/snnTorch per external sources, not a first-party hardware deployment doc) | [T1–T3][N1–N5][B1–B4][G1–G3] |

---

## SpikingJelly usage share among recent (2022–2026) SNN papers

No source located in this pass reports a **quantified percentage** of recent SNN papers using
SpikingJelly specifically (e.g., "SpikingJelly is used in X% of papers surveyed"). The closest
first-party evidence is qualitative: the Science Advances paper itself states "Since being open-sourced
in December 2019, SpikingJelly has been widely used in many spiking deep learning studies," and lists
roughly 20 application categories with citation clusters (adversarial attack, ANN2SNN, attention
mechanisms, hardware design, spiking-neuron improvements, training-method improvements, pruning, NAS,
NLP, object detection/tracking, reinforcement learning, etc.), concluding "its widespread adoption by
the community marks SpikingJelly as one of the most commonly used spiking deep learning frameworks"
[S1]. A secondary source (alphaXiv listing) states "SpikingJelly has been adopted in over 94 academic
publications" [S12] — this figure's provenance/date cutoff was not independently verified and should be
treated cautiously (it may already be a stale/undercount figure relative to 2026, given the pace of
citation growth implied by [S1]'s own citation list).

One independent benchmarking study (2025, *Journal of Applied Sciences*) directly compared SpikingJelly
against other frameworks on image-classification tasks and reported: "the neuromorphic training
framework SpikingJelly outperforms others in terms of both training time and classification accuracy in
direct SNN training, while the Lava framework achieves the highest classification accuracy in
ANN-to-SNN conversion training" [BM1] — evidence of comparative standing among practitioners, not a
literature-share statistic.

**Whether SpikingJelly-based papers deploy to hardware:** the survey/tutorial sources reviewed (e.g.,
the "Toward Large-Scale SNNs" survey [LS1] and the "Edge Intelligence with SNNs" survey [ES1], both of
which catalog large numbers of deep-SNN papers by architecture/accuracy) report accuracy and time-step
counts as the standard comparison axes for deep SNN papers (ImageNet/CIFAR accuracy vs. latency in
time-steps), essentially never reporting a measured on-chip accuracy/power number for the catalogued
works — consistent with the general E5-heavy pattern implied above (most SpikingJelly-adjacent deep-SNN
literature reports software-simulated accuracy only, not physical-hardware measurement), but this
pass did not locate a source that explicitly cross-tabulates "framework used" against "deployed to
hardware (yes/no)" for a literature sample. **NOT FOUND** for a direct statistic answering this
sub-question quantitatively.

---

## Source list

- [S1] Fang, W. et al., "SpikingJelly: An open-source machine learning infrastructure platform for
  spike-based intelligence," *Science Advances* 9(40), eadi1480, 2023.
  https://www.science.org/doi/pdf/10.1126/sciadv.adi1480?download=true
- [S2] SpikingJelly docs, "Neuron" tutorial. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/neuron.html
- [S3] SpikingJelly docs, "ANN2SNN" tutorial. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/ann2snn.html
  (Chinese parallel page: https://spikingjelly.readthedocs.io/zh-cn/latest/activation_based/5_ann2snn.html)
- [S4] SpikingJelly docs, "Convert to Lava for Loihi Deployment." https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html
  (source .rst: https://spikingjelly.readthedocs.io/zh-cn/latest/_sources/tutorials/en/lava_exchange.rst.txt ;
  GitHub discussion confirming tutorial addition: https://github.com/fangwei123456/spikingjelly/discussions/339)
- [S5] SpikingJelly GitHub README (master). https://github.com/fangwei123456/spikingjelly/blob/master/README.md
- [S6] SpikingJelly ReadTheDocs project root / table of contents (Lynxi tutorial listed).
  https://spikingjelly.readthedocs.io/
- [S7] SpikingJelly API docs, `ann2snn` package. https://spikingjelly.readthedocs.io/zh-cn/latest/APIs/spikingjelly.activation_based.ann2snn.html
- [S8] SpikingJelly legacy `ann2snn` module docs (Converter class, VoltageHook/VoltageScaler).
  https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.14/spikingjelly.activation_based.ann2snn.html
- [S9] SpikingJelly GitHub repository (fangwei123456/spikingjelly): stats, maintainers, last push.
  https://github.com/fangwei123456/spikingjelly and https://github.com/fangwei123456/SpikingJelly
- [S10] SpikingJelly CHANGELOG.md. https://github.com/fangwei123456/spikingjelly/blob/master/CHANGELOG.md
- [S11] SpikingJelly commit 3d27124 (2026-05-31), distributed-training refactor.
  https://github.com/fangwei123456/spikingjelly/commit/3d27124c5180a961afa79d155b85f61139466f86
- [S12] alphaXiv listing for SpikingJelly paper (adoption-count claim). https://www.alphaxiv.org/abs/2310.16620

- [T1] Eshraghian, J.K. et al., "Training Spiking Neural Networks Using Lessons From Deep Learning,"
  *Proceedings of the IEEE*, 111(9), Sept. 2023 (cited via snnTorch tutorial pages).
- [T2] snnTorch docs, `snn.Leaky` API reference. https://snntorch.readthedocs.io/en/latest/snn.neurons_leaky.html
  (source module: https://snntorch.readthedocs.io/en/latest/_modules/snntorch/_neurons/leaky.html ;
  package overview: https://snntorch.readthedocs.io/en/latest/snntorch.html)
- [T3] snnTorch docs, Tutorial 2 — "The Leaky Integrate-and-Fire Neuron."
  https://snntorch.readthedocs.io/en/latest/tutorials/tutorial_2.html

- [N1] Norse docs, `norse.torch.functional` module index. https://norse.github.io/norse/generated/norse.torch.functional.html
- [N2] Norse docs, `norse.torch.functional.lif` module. https://norse.github.io/norse/auto_api/norse.torch.functional.lif.html
- [N3] Norse docs, `norse.torch.module.lif` module. https://norse.github.io/norse/auto_api/norse.torch.module.lif.html
- [N4] Norse docs, `norse.torch.LIF` class (v1.0.0). https://norse.github.io/norse/generated/norse.torch.LIF.html
- [N5] SC-NeuroCore third-party docs, "NIR Integration" page (Norse export example and caveat).
  https://anulum.github.io/sc-neurocore/guides/nir_integration/

- [L1] Lava Software Framework overview / homepage (incl. reference `PyLifModel`). https://lava-nc.org/
- [L2] Lava documentation, "Deep Learning" (Lava-DL overview: SLAYER/Bootstrap/NetX). https://lava-nc.org/dl.html
- [L3] lava-nc/lava-dl GitHub README (archival notice, current maintainers section absent — repo archived).
  https://github.com/lava-nc/lava-dl/blob/main/README.md ; PyPI mirror: https://pypi.org/project/lava-dl/
- [L4] Lava-DL SLAYER docs. https://lava-nc.org/lava-lib-dl/slayer/slayer.html and
  https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/slayer/README.md

- [SI1] Sinabs docs, "How-Tos: Activations" (IAF `spike_fn`/`reset_fn` options). https://sinabs.readthedocs.io/v3.0.2/how_tos/activations.html
- [SI2] Sinabs docs, "Troubleshooting and Tips" — reset mechanism for Speck. https://sinabs.readthedocs.io/v3.1.4.dev13/speck/faqs/tips_for_training.html
  (also https://sinabs.readthedocs.io/v3.1.2/speck/faqs/tips_for_training.html)
- [SI3] Sinabs docs, "The Basics" (Speck deployment, DynapcnnNetwork, quantization, chip placement).
  https://sinabs.readthedocs.io/main/speck/the_basics.html
- [SI4] Sinabs docs, "NIR to Speck" tutorial (worked on-chip accuracy example). https://sinabs.readthedocs.io/v3.1.3/tutorials/nir_to_speck.html

- [R1] Rockpool docs, "Overview of the Xylo family." https://rockpool.ai/devices/xylo-overview.html
- [R2] Rockpool docs, "Quick-start with Xylo SNN core." https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html
- [R3] Rockpool docs, "Using XyloSamna and XyloMonitor to deploy a model on XyloAudio 3 HDK" (power recording).
  https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html
- [R4] Rockpool docs, `nn.networks.SynNet` API reference (`time_constants_per_layer`).
  https://rockpool.ai/reference/_autosummary/nn.networks.SynNet.html

- [B1] Hazan, H., Saunders, D.J., et al., "BindsNET: A Machine Learning-Oriented Spiking Neural Networks
  Library in Python," *Frontiers in Neuroinformatics*, 2018.
  https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2018.00089/full
  (GitHub: https://github.com/BindsNET/bindsnet)
- [B2] Stimberg, M., Brette, R., Goodman, D.F.M., "Brian 2, an intuitive and efficient neural
  simulator," *eLife* 8, 2019 (cited via [G2]/[G3] bibliographies).
- [B3] brian-team/brian2genn GitHub README. https://github.com/brian-team/brian2genn/
- [B4] Brian2GeNN docs, "Introduction." https://brian2genn.readthedocs.io/en/stable/introduction/

- [G1] Turner, J.P., Knight, J.C., Subramanian, A., Nowotny, T., "mlGeNN: accelerating SNN inference
  using GPU-enabled neural networks," *Neuromorphic Computing and Engineering*, 2022.
  https://doi.org/10.1088/2634-4386/ac5ac5 (IOP mirror: https://iopscience.iop.org/article/10.1088/2634-4386/ac5ac5 ;
  code: https://github.com/genn-team/ml_genn)
- [G2] Schmitt, F.J., Rostami, V., Nawrot, M.P., "Efficient parameter calibration and real-time
  simulation of large-scale spiking neural networks with GeNN and NEST," 2023.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9950635/
- [G3] Kulkarni, S. et al., "Benchmarking the Performance of Neuromorphic and Spiking Neural Network
  Simulators," OSTI technical report, 2021. https://www.osti.gov/biblio/1779135

- [ST1] SNN Toolbox docs, "Introduction" (Brian2/NEST/Neuron via pyNN, INIsim, hardware-deployment framing).
  https://snntoolbox.readthedocs.io/en/latest/guide/intro.html

- [P1] PyNN docs, "Introduction." https://pynn.readthedocs.io/en/latest/introduction.html
- [P2] Hazan et al. 2018 simulator-comparison table (SpiNNaker row: "PyNN & sPyNNaker support").
  https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2018.00089/full
- [P3] HBP Neuromorphic Computing Platform Guidebook (BrainScaleS + SpiNNaker via PyNN backends, job
  submission). https://electronicvisions.github.io/hbp-sp9-guidebook/using_the_platform.html and
  https://flagship.kip.uni-heidelberg.de/jss/FileExchange/HBPNeuromorphicComputingPlatformGuidebook.pdf
- [P4] PyNN for BrainScaleS-2 docs. https://electronicvisions.github.io/documentation-brainscales2/latest/pynn-brainscales/index.html
- [P5] `pynn_brainscales.brainscales2` API reference (setup() hardware-specific parameters).
  https://electronicvisions.github.io/documentation-brainscales2/ebrains-2.0/api_pynn-brainscales2.html

- [SP1] Spyx docs (ReadTheDocs), module table incl. `spyx.nir`, JAX/Flax NNX description.
  https://spyx.readthedocs.io/en/latest/
- [SP2] kmheckel/spyx GitHub README (neuron zoo, JIT/XLA claims). https://github.com/kmheckel/spyx/

- [ND1] NengoDL docs, "Optimizing a spiking neural network" example (Hunsberger & Eliasmith 2016 method).
  https://www.nengo.ai/nengo-dl/examples/spiking-mnist.html
- [ND2] NengoLoihi docs, home page. https://www.nengo.ai/nengo-loihi/
- [ND3] NengoLoihi docs, "Overview" (hardware backend, NxSDK, emulator vs. hardware target).
  https://www.nengo.ai/nengo-loihi/overview.html
- [ND4] NengoLoihi docs, "Installation" and "Hardware setup" pages.
  https://www.nengo.ai/nengo-loihi/installation.html and https://www.nengo.ai/nengo-loihi/setup/index.html

- [MC1] SC-NeuroCore third-party docs, "Multi-Timescale" / `MultiClockSNN` page (non-mainstream,
  flagged for awareness only — not one of the nine surveyed frameworks).
  https://anulum.github.io/sc-neurocore/api/temporal_hierarchy/

- [BM1] "Benchmarking of Spiking Neural Networks and Performance Evaluation of Neuromorphic Training
  Frameworks," *Journal of Applied Sciences*, 2025. https://www.jas.shu.edu.cn/EN/10.3969/j.issn.0255-8297.2025.01.012
- [LS1] Hu, Y., Qian, Z., Li, G., Tang, H., Pan, G., "Toward Large-scale Spiking Neural Networks: A
  Comprehensive Survey and Future Directions," arXiv:2409.02111, 2024. https://doi.org/10.48550/arxiv.2409.02111
- [ES1] "Edge Intelligence with Spiking Neural Networks" survey, arXiv:2507.14069, 2025.
  https://arxiv.org/html/2507.14069v1

---

## Notes on gaps / follow-ups for the survey author

1. Lava/Lava-DL's **archival status** ("All Lava repositories are archived... stay tuned for
   announcements about our new SDK") [L3] is a significant, citable fact for a "hardware reach as of
   2026" framing — Intel's own primary Loihi software path is currently frozen/EOL pending a successor,
   which should be foregrounded if the survey ranks frameworks by *current* viability rather than
   historical documentation completeness.
2. No first-party quantitative "% of papers use framework X" statistic was found for SpikingJelly or
   any other framework; if this number is load-bearing for the thesis, it likely needs to be computed
   directly (e.g., a keyword/citation sweep of a paper corpus such as the one in [LS1]/[ES1]), not
   quoted from an existing source.
3. SLAYER (standalone, pre-Lava-DL, `bamsumit/slayerPytorch`) was identified only as the ancestor
   project cited by Lava-DL's SLAYER 2.0 docs [L4]; its own reset semantics/time model were not
   independently verified in this pass and would need a separate check if the standalone version
   (rather than the Lava-DL-integrated SLAYER 2.0) is the one relevant to the thesis's comparison.
4. Sinabs vs. Rockpool are easy to conflate (both SynSense, both PyTorch-based) but target different
   chip families (Speck/DYNAP-CNN vs. Xylo) with different neuron/reset defaults documented — keep them
   as separate rows in any comparison table.
