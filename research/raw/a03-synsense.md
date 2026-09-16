# The SynSense Stack: DYNAP-CNN, Speck, Xylo, Sinabs/Rockpool/samna

Research notes for neuromorphic deployment survey. Evidence classes: **E1** physical
silicon, latency+energy measured. **E2** physical silicon, accuracy/power only (no
rigorous latency/energy benchmark). **E3** documented deployment path, no published
run of this model class. **E4** hardware model / architectural characterization
(datasheet, chip paper without an application benchmark). **E5** software simulation
only.

---

## 1. DYNAP-CNN / Speck hardware

### 1.1 Chip family and relationship

- DYNAP-CNN is the processor core; Speck is a SoC that integrates the DYNAP-CNN
  processor with an on-chip Dynamic Vision Sensor (DVS). "Speck™ is the world first
  neuromorphic device which integrates the DYNAP-CNN neuromorphic processor and a
  dynamic vision sensor (DVS) into a single SoC." [E4] — Sinabs docs,
  https://sinabs.readthedocs.io/main/speck/overview.html
- The original standalone DYNAP-CNN (2019 announcement) was a 12 mm² chip in 22 nm
  technology with **over 1 million spiking Integrate-and-Fire neurons and 4 million
  programmable parameters**, scalable across daisy-chained devices. [E4] — SynSense,
  "DYNAP-CNN — the World's First 1M Neuron, Event-Driven Neuromorphic AI Processor",
  2019, https://www.synsense.ai/dynap-cnn-the-worlds-first-1m-neuron-event-driven-neuromorphic-ai-processor-for-vision-processing/
- Speck (integrated DVS+DYNAP-CNN SoC) is configurable with **up to 0.32M (328K)
  spiking neurons**, die size 6.1 mm × 4.9 mm, integration level ~11,000
  neurons/mm². [E4] — Yao, Richter et al., "Spike-based dynamic computing with
  asynchronous sensing-computing neuromorphic chip," *Nature Communications* 15,
  4464 (2024), https://doi.org/10.1038/s41467-024-47811-6

### 1.2 Layer/core structure

- Both chips expose **9 configurable computing cores ("layers")**. Each core
  implements one pipeline stage: `Conv2d → Integrate-and-Fire neuron → (optional)
  SumPool2d`, in that fixed order. Each core can route its output events to up to
  **2 destination cores** ("fan-out of 2" at the routing level), which is also how
  residual/shortcut connections are implemented (one core's output copied to two
  downstream cores). [E4] — Sinabs docs (Speck overview and FAQ),
  https://sinabs.readthedocs.io/main/speck/overview.html and
  https://sinabs.readthedocs.io/develop/speck/faqs/available_network_arch.html
- Full component list (Speck): 1× built-in 128×128 DVS, 1× DVS/event
  pre-processing layer (crop, rescale, decimate, noise/hot-pixel/low-pass
  filtering, mirror), 9× DYNAP-CNN convolutional layers, 1× readout layer, SPI/serial
  I/O, interrupt pins encoding up to 15+1 classes. [E4] — SynSense, Speck Dev Kit
  Datasheet (2023/2024/2025 revisions), e.g.
  https://www.synsense.ai/wp-content/uploads/2023/06/Speck-devkit-datasheet.pdf and
  https://www.synsense.ai/wp-content/uploads/2024/12/Speck-Dev-Kit-Manual.pdf

### 1.3 Time model — asynchronous, no global clock

- "Computation in DYNAP-CNN is triggered directly by changes in the visual scene,
  **without using a high-speed clock**. Moving objects give rise to sequences of
  events, which are processed immediately by the processor. Since there is no notion
  of frames, DYNAP-CNN's continuous computation enables ultra-low-latency of below
  5 ms." [E4] — SynSense product announcement, 2019 (URL above).
- "The fully asynchronous architecture of Speck ... In this paradigm, the
  neuromorphic chip **no longer needs the global or local clock signal**, which
  efficiently prevents the redundant power consumed by clock empty flips ... the
  asynchronous design can be understood as the most extreme form of fine granular
  clock gating for every component in the processing pipeline while being instantly
  available, requiring no wake-up procedures." "Asynchronous logic is built using a
  cascade of asynchronous circuit blocks that communicate via a request/acknowledge
  protocol when transferring data, **without requiring a global clock**. As soon as
  the data is accessible at its input port, each block independently calculates its
  output value." [E1/E4] — Yao, Richter et al., *Nature Communications* 2024 (URL
  above).
- Richter et al. (Speck ASIC characterization paper) measured **end-to-end latency
  of 3.36 µs for a single event traversing all 9 sCNN layers** (3×3 kernel, stride
  1, pad 1), and 1.58 µs for a single layer. This is compared explicitly against
  clocked chips: "Speck1 is specifically built to consume real-time data, its
  latency is significantly lower than Loihi1/2 and TrueNorth **which
  architecturally introduce a latency of one timestep Δt on event generation in
  each layer**." [E1/E4] — Richter et al., "Speck: A Smart event-based Vision
  Sensor with a low latency 327K Neuron Convolutional Neural Network Processing
  Pipeline," arXiv:2304.06793, https://arxiv.org/html/2304.06793
- Exception: on **Speck2e and later**, there is an optional low-frequency "slow
  clock" used only for peripheral, non-convolutional features — the leak operation
  (if enabled), the DVS pre-processing noise/flicker filter's internal state
  update, and the readout layer's moving-average window. This slow clock does not
  drive the convolution/IF compute pipeline itself. [E4] — Sinabs docs, Speck
  overview page (URL above); "How To Leak The Neurons On The Devkit" tutorial,
  https://sinabs.readthedocs.io/main/speck/notebooks/leak_neuron.html

### 1.4 Neuron model and reset semantics

- Default neuron on DYNAP-CNN/Speck is a **nonleaky Integrate-and-Fire (IF)**
  neuron (the `sinabs.layers.IAFSqueeze` class, the default `spike_layer_class` used
  by `from_model`/`from_torch`). Leak is an *optional* feature: it requires a bias
  term on the preceding conv layer and an externally configured slow-clock
  frequency; without it the neuron only integrates and fires (no decay). [E3/E4] —
  Sinabs API, https://sinabs.readthedocs.io/main/api/from_torch.html ; "How To Leak
  The Neurons On The Devkit" (URL above): "To leak the neuron ... Make sure you
  have a bias term ... Setting the external slow-clock frequency. Then the bias
  term will be added to the neuron's membrane potential at every clock cycle."
- Reset semantics: the default `reset_fn` in `sinabs.from_torch.from_model` is
  `MembraneSubtract()` — i.e., **reset-by-subtraction** (the firing threshold is
  subtracted from the membrane potential on spike, not reset-to-zero). This is the
  same reset convention used in the classical ANN-to-SNN rate-coding conversion
  literature (Diehl et al., Rueckauer et al.). [E3] — Sinabs source,
  https://sinabs.readthedocs.io/main/api/from_torch.html and
  https://sinabs.readthedocs.io/develop/_modules/sinabs/from_torch.html
- Membrane lower bound: `min_v_mem = -1.0` by default (clamps negative membrane
  excursions). [E3] — same source.

### 1.5 Spike payload / addressing

- Spikes are binary events carrying an address: on the `Spike` event class used by
  samna/Sinabs, each event has `layer`, `x`, `y`, `feature`, and `timestamp`
  (microsecond resolution) fields — a standard Address-Event-Representation (AER)
  scheme. [E3] — Sinabs `chip_factory.py` source (`raster_to_events`,
  `events_to_raster`),
  https://sinabs.readthedocs.io/v2.0.1/_modules/sinabs/backend/dynapcnn/chip_factory.html;
  Samna events reference, https://synsense-sys-int.gitlab.io/samna/0.48.0/reference/events/index.html

### 1.6 Weight / state precision

- **Weight resolution: 8 bits. Neuron state (membrane potential) resolution: 16
  bits.** Confirmed independently in the Speck datasheet and in Sinabs deployment
  docs: "The hardware supports fixed point weights (8 bits for weights and 16 bits
  for membrane potentials)." [E4] — Speck Dev Kit Datasheet,
  https://www.synsense.ai/wp-content/uploads/2023/06/Speck-devkit-datasheet.pdf ;
  Sinabs "The Basics" (Speck deployment guide),
  https://sinabs.readthedocs.io/v3.1.1/speck/the_basics.html

### 1.7 Supported operators

From the Speck Dev Kit Datasheet, "2.1.3 DYNAP-CNN computing layers" [E4] (URL
above):

- Max input dimension: 128×128. Max feature output size: 64×64. Max feature
  number: 1024.
- Max kernel size: **16×16**.
- Stride: **{1, 2, 4, 8}**, independently configurable in X/Y.
- Padding: **[0..7]**, independently configurable in X/Y.
- Pooling: **sum-pooling only**, ratios {1:1, 1:2, 1:4}. `AvgPool2d` is *not*
  natively supported — Sinabs's `DynapcnnNetwork` conversion step automatically
  rewrites `nn.AvgPool2d` into `sinabs.layers.SumPool2d` because "spikes cannot
  really be averaged." [E3] — Sinabs "The Basics",
  https://sinabs.readthedocs.io/v3.1.1/speck/the_basics.html
- Fan-out: **2** destination cores per core (routing fan-out, not per-neuron
  synaptic fan-out).
- Per-core features: leak operation, spike decimator, spike congestion balancer;
  layers 0 and 1 can run in parallel for higher input throughput.
- `nn.Linear` layers are automatically converted to an equivalent `nn.Conv2d` with
  a kernel equal to the full spatial input (`convert_linear_to_conv`) so that they
  fit the `DynapcnnLayer` conv→spike→pool template. [E3] — Sinabs source,
  https://sinabs.readthedocs.io/develop/_modules/sinabs/backend/dynapcnn/dynapcnn_layer.html
- **No native BatchNorm.** No BatchNorm layer type appears anywhere in the
  supported-operator list, the `DynapcnnLayer` template (`conv → spike → pool`
  only), or the discretization API (`discretize_conv`, `discretize_conv_spike`,
  which operate on `Conv2d`+`IAF` pairs only). Sinabs tutorials for
  hardware-targeted networks build BN-free architectures directly (e.g., the NMNIST
  Speck-deployment tutorial's conv layers are all `bias=False`, and the reference
  network built for the Speck2f manual has no BN layer). NOT FOUND: an explicit
  built-in Sinabs "BatchNorm-fold" utility function analogous to the discretize_*
  functions — the burden of removing/folding BN appears to fall on the user before
  calling `from_model`. [E3] — Sinabs discretize API,
  https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html ; NMNIST
  tutorial, https://sinabs.readthedocs.io/v3.1.3/tutorials/nmnist.html
- **Bias is effectively disabled for normal (non-leak) use.** The `nmnist_quick_start`
  tutorial states explicitly: "Why Disable All 'Bias' Of The Convolutional Layers?
  ... The bias term in fact is related to the neuron's leak mechanism on the
  hardware." I.e., on-chip, a conv bias is repurposed as the per-timestep leak
  current, not a standard additive bias. [E3] — Sinabs NMNIST quick start,
  https://sinabs.readthedocs.io/develop/speck/notebooks/nmnist_quick_start.html

### 1.8 Memory per core

- Kernel memory (in WORDs) and neuron memory differ per core — the datasheet gives
  a per-core kernel-memory table; cores are "divided ... the memory capacities of
  the cores are different, and restrict the implementation of larger layers to
  specific cores." Exact per-core numeric table is in the PDF datasheet (table not
  fully extractable via text search) — layer-to-core placement is handled
  automatically by `DynapcnnNetwork(..., chip_layers_ordering="auto")`, which
  raises an error if no valid placement fits the available per-core memory. [E4] —
  Speck Dev Kit Datasheet (URL above); Sinabs "The Basics" (URL above).
- `DynapcnnLayer.memory_summary()` in Sinabs computes the kernel/neuron/bias memory
  footprint analytically as
  K_MT = c·2^(⌈log2(kx·ky)⌉+⌈log2(f)⌉), N_MT = f·2^(⌈log2(fy)⌉+⌈log2(fx)⌉). [E3] —
  Sinabs source, https://sinabs.readthedocs.io/develop/_modules/sinabs/backend/dynapcnn/dynapcnn_layer.html

### 1.9 Speck's integrated DVS

- 128×128-pixel event-based Dynamic Vision Sensor, integrated on the same die as
  the DYNAP-CNN processor. Per-pixel kill/disable is configurable. Preprocessing
  pipeline before the first CNN core includes: on/off/both/merge polarity
  switching, spatial pooling, ROI selection, mirror operation, DVS noise filter,
  low-pass (flicker) filter, hot-pixel filter, and fan-out. [E4] — Sinabs Speck
  overview (URL above); Speck Dev Kit Manual,
  https://www.synsense.ai/wp-content/uploads/2024/12/Speck-Dev-Kit-Manual.pdf
- DVS asynchronously and sparsely emits binary polarity events ("spikes with
  addresses") on per-pixel brightness change; "the processor in Speck only operates
  when receiving incoming events." [E1/E4] — Yao, Richter et al., *Nature
  Communications* 2024 (URL above).

---

## 2. Xylo (separate product line)

- Xylo is SynSense's **separate digital SNN inference ASIC family for audio / IMU /
  low-dimensional sensory signals** (not vision). Variants: XyloAudio 2, XyloAudio
  3, XyloIMU. [E4] — Rockpool docs, "Overview of the Xylo family,"
  https://rockpool.ai/devices/xylo-overview.html
- Neuron model: **Leaky Integrate-and-Fire (LIF)**, specifically current-based LIF
  (CUBA-LIF) with per-neuron/per-synapse configurable time constants, biases, and
  thresholds; up to two synaptic states per hidden neuron ("Isyn1"/"Isyn2"), one for
  output neurons. Reset is **subtractive**: "Reset during event generation is
  performed by subtraction." Multiple spikes per timestep are supported (up to 31
  for hidden neurons, 1 for output neurons). [E4] — Rockpool Xylo overview (URL
  above).
- **Time model: clocked / synchronous.** "Synchronous time-stepped architecture
  with a global time-step `dt`." Master clock runs up to 50 MHz (XyloAudio 3) or
  100 MHz (XyloAudio 2) internally. This is the opposite regime from DYNAP-CNN/Speck:
  Xylo genuinely executes one network update per global timestep `dt`. [E4] —
  Rockpool Xylo overview (URL above); XyloAudio datasheet,
  https://www.synsense.ai/wp-content/uploads/2023/06/Xylo-Audio-datasheet.pdf
- Scale: up to 1000 (XyloAudio 2) / 992 (XyloAudio 3) / 496 (XyloIMU) hidden
  neurons; 8 (Audio 2) to 32 (Audio 3) output/classification channels; 16 input
  event channels; 8-bit weights, 16-bit neuron/synapse states; on-chip memory
  ~124–150 KB. [E4] — XyloAudio 3 Devkit datasheet,
  https://www.synsense.ai/wp-content/uploads/2026/03/XyloAudio-3-Devkit-datasheet_2026.03.pdf
- Xylo has two operating modes: **Real-Time mode** (autonomous, driven by the
  chip's internal timestep counter, live microphone/sensor input, output read via
  `XyloMonitor`) and **Accelerated-Time mode** (host-driven, pre-generated spike
  trains processed as fast as possible, monitoring of internal state enabled, via
  `XyloSamna`). [E3/E4] — Samna docs, "Xylo-Audio v3,"
  https://synsense-sys-int.gitlab.io/samna/0.39.4/models/xyloSeries/xylo_audio_v3.html ;
  Rockpool tutorial, https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html
- Deployment path is via **Rockpool**, not Sinabs: `mapper()` extracts a hardware
  specification from a trained Rockpool computational graph, `quantize_methods`
  (`global_quantize`/`channel_quantize`) quantizes weights/thresholds to the
  integer chip logic, `config_from_specification()` builds the hardware config
  object, and `XyloSamna`/`XyloSim` deploy to real hardware or a bit-precise
  simulator respectively. [E3] — Rockpool "Quick-start with Xylo SNN core,"
  https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html
- Published E1 result: "Micro-power spoken keyword spotting on Xylo Audio 2" —
  SynNet architecture (feed-forward LIF, multiple per-layer synaptic time
  constants), deployed to physical XyloAudio 2 HDK, "Aloha" keyword-spotting
  benchmark, on-board current monitors sampled at 1280 Hz, power measured
  streaming continuous audio for the full test set, master clock 6.25 MHz. [E1] —
  arXiv:2406.15112, https://arxiv.org/html/2406.15112v1
- DYNAP-SE2 (a related but distinct SynSense chip — mixed-signal, recurrent,
  analog IF neurons, not part of the DYNAP-CNN/Speck/Xylo lines named in the
  prompt) is documented separately; noted here only because Rockpool's DynapSim
  training/deployment paper is sometimes conflated with Xylo. [E4] — Richter, Wu et
  al., "DYNAP-SE2: a scalable multi-core dynamic neuromorphic asynchronous spiking
  neural network processor," *Neuromorphic Computing and Engineering*,
  https://doi.org/10.1088/2634-4386/ad1cd7 ; Rockpool DynapSim training paper,
  https://doi.org/10.1088/2634-4386/ad2ec3

---

## 3. Sinabs (software: ReLU→IF conversion)

### 3.1 `from_model` / `from_torch` mechanism

- `sinabs.from_torch.from_model(model, input_shape=None, spike_threshold=1.0,
  spike_fn=MultiSpike, reset_fn=MembraneSubtract(), surrogate_grad_fn=
  SingleExponential(), min_v_mem=-1.0, bias_rescaling=1.0, batch_size=None,
  num_timesteps=None, synops=False, add_spiking_output=False,
  spike_layer_class=sl.IAFSqueeze, ...)`. "Converts a Torch model and returns a
  Sinabs network object. The modules in the model are analyzed, and a copy is
  returned, **with all ReLUs and NeuromorphicReLUs turned into SpikingLayers**."
  Implementation: `replace_module(model, source_class=nn.ReLU, mapper_fn=...)`
  then again for `sl.NeuromorphicReLU`. [E3] — Sinabs API reference,
  https://sinabs.readthedocs.io/main/api/from_torch.html ; source,
  https://sinabs.readthedocs.io/main/_modules/sinabs/from_torch.html
- Only `nn.ReLU` (and Sinabs's own `NeuromorphicReLU`) are replaced — no other
  activation type is touched by this pass.
- Default target neuron class is `sinabs.layers.IAFSqueeze` (nonleaky IF), default
  spike function `MultiSpike` (multiple spikes per timestep possible if membrane
  exceeds threshold by more than one unit), default reset `MembraneSubtract()`.
  [E3] — same source.
- `add_spiking_output=True` appends a spiking layer at the network's end if it does
  not already terminate in one, so both input and output are natively spike-typed.
  [E3] — same source; tutorial:
  https://sinabs.readthedocs.io/main/tutorials/weight_transfer_mnist.html

### 3.2 What `num_timesteps` means in Sinabs

- `num_timesteps`: "**Number of timesteps per sample.** If None, `batch_size` must
  be provided to separate batch and time dimensions." It is purely a **software
  simulation bookkeeping parameter**: because Sinabs SNN layers process a flattened
  `(batch × time)` leading dimension, `num_timesteps` tells the `Network` wrapper
  how to unflatten that dimension back into `(batch, time, ...)` for output
  interpretation. It does not correspond to any hardware clock tick (see §5). [E3]
  — Sinabs API reference (URL above).
- In the weight-transfer MNIST tutorial, `num_timesteps` (there called
  `time_window`) is explicitly the length of the **rate-coding window**: "The
  longer `time_window` is, the more spikes we produce as input and the better the
  performance of the network is going to be." Input generation is literal Bernoulli
  rate coding: `img = (torch.rand(time_window, *img.shape) < img).float()`. [E3] —
  https://sinabs.readthedocs.io/main/tutorials/weight_transfer_mnist.html and
  https://sinabs.readthedocs.io/v1.1.2/tutorials/weight_transfer_mnist.html

### 3.3 Default reset behavior

- Confirmed default is subtractive: `reset_fn: Callable = MembraneSubtract()`. This
  matches the reset convention of the Diehl/Rueckauer-style classical rate-coding
  ANN→SNN conversion literature (see §8 summary point). [E3] — Sinabs API reference
  (URL above).

### 3.4 BatchNorm handling

- NOT FOUND: a dedicated, documented Sinabs API function that automatically folds
  BatchNorm into a preceding Conv/Linear layer as part of `from_model` or
  `DynapcnnNetwork`. The `discretize` module's public functions
  (`discretize_conv`, `discretize_conv_spike`, `discretize_spk`, ...) operate only
  on `(Conv2d, IAF)` pairs; there is no `discretize_bn` or `fold_bn` counterpart in
  the module's function list. [E3] — Sinabs discretize API,
  https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html ; discretize
  source, https://sinabs.readthedocs.io/v3.0.4/speck/api/dynapcnn/discretize.html
- Tutorials targeting Speck deployment build networks that never include BatchNorm
  in the first place (bias-free convs immediately followed by IF layers), implying
  the standard practice in the SynSense ecosystem is to **avoid BN in the trainable
  architecture** rather than rely on an automated post-hoc fold. [E3] — NMNIST
  Speck deployment tutorials (URLs above).

### 3.5 Discretization to hardware precision — `DynapcnnNetwork`

- `DynapcnnNetwork(sinabs_model.spiking_model, discretize=True, input_shape=...,
  dvs_input=...)`: "automates this model conversion from a sequential sinabs
  spiking neural network into a sequence of `DynapcnnLayer`s. In addition, it also
  discretizes/quantizes the parameters to 8 bits (according to the chip
  specifications)." "The hardware supports fixed point weights (8 bits for weights
  and 16 bits for membrane potentials for instance) ... Setting `discretize=True`
  converts the model parameters from floating point to fixed point representation
  while preserving the highest possible precision." [E3] — Sinabs "The Basics,"
  https://sinabs.readthedocs.io/v3.1.1/speck/the_basics.html
- Each `DynapcnnLayer` = `(conv, spk, pool)`, always applied in that order
  (`x = self.conv_layer(x); x = self.spk_layer(x)`; pooling optional per
  destination). `nn.Linear` is converted to `nn.Conv2d`; `nn.AvgPool2d` is
  converted to `SumPool2d`. [E3] — Sinabs source (dynapcnn_layer.html, URL
  above).
- Layer→core placement: `chip_layers_ordering="auto"` runs a placement algorithm
  respecting per-core memory constraints; throws an error if no valid placement
  exists; can also be set manually as an explicit list of core indices. [E3] —
  Sinabs "The Basics" and FAQ (URLs above).
- Speck additionally imposes **uniform per-layer thresholds**: "Speck does not
  support individual parameters per neuron. Set threshold to a single value per
  spiking layer" — demonstrated explicitly when converting a NIR-imported model for
  Speck deployment. [E3] — Sinabs NIR-to-Speck tutorial,
  https://sinabs.readthedocs.io/v3.0.0/tutorials/nir_to_speck.html

---

## 4. Deployment path: Sinabs → DynapcnnNetwork → chip mapping → samna → device

1. **Train/convert in Sinabs**: `from_model(ann, ...)` replaces ReLUs with IF
   layers (§3.1).
2. **`DynapcnnNetwork(..., discretize=True, input_shape=..., dvs_input=...)`**:
   restructures the sequential model into `DynapcnnLayer` objects, quantizes
   weights to 8-bit / thresholds+membrane to 16-bit (§3.5).
3. **`hw_model.to(device="speck2fdevkit:0", chip_layers_ordering="auto",
   monitor_layers=[...])`** or, at a lower level, **`make_config(device=...,
   chip_layers_ordering=...)`**: produces a `samna` configuration object
   (`samna_cfg`) containing per-core `cnn_layers[i]` fields — `weights`, `biases`,
   `destinations`, `dimensions`, `threshold_high`/`threshold_low`,
   `leak_enable`, `neurons_initial_value`, `return_to_zero`, plus `dvs_layer`
   and `readout` configuration blocks. [E3] — Speck Dev Kit Manual (URL above),
   §4.2.2 "Samna Configuration."
4. **samna applies the configuration to physical silicon.** SynSense describes
   samna as "**the developer interface to the SynSense toolchain and run-time
   environment for interacting with all SynSense devices**. ... a Python API is
   available with the core running in C++ ... Samna also features an event-based
   stream filter system that allows real-time, multi-branch processing of the
   event-based stream coming in or out from the device ... with an integration of a
   just-in-time compiler ... supports adding user-defined filter functions at
   run-time." [E4] — SynSense, "SAMNA | Developer Interface to SynSense Toolchain,"
   https://www.synsense.ai/products/samna/
   - Chip "Models" in samna provide a hardware-agnostic interface: `apply_configuration(cfg)`
     validates and applies a device configuration; `get_source_node()` streams
     events produced by the chip; `get_sink_node()` accepts events to transmit to
     the chip. [E3] — Samna docs, "Chip Models,"
     https://synsense-sys-int.gitlab.io/samna/0.48.0/models/models.html
   - `samna.graph.EventFilterGraph` chains source nodes, built-in or JIT filters
     (e.g. `DvsEventCrop`, `DvsEventRescale`, `DvsEventDecimate`,
     `Speck2fOutputEventTypeFilter`), and sink nodes to route/process the event
     stream in real time. [E3] — Samna Quick Start,
     https://synsense-sys-int.gitlab.io/samna/0.48.0/quickStart.html
5. **Feeding input events.** Two documented conversion utilities in
   `sinabs.backend.dynapcnn.chip_factory.ChipFactory`:
   - `raster_to_events(raster, layer, dt=1e-3, truncate=False, delay_factor=0)`:
     "Convert spike raster to events for DynapcnnNetworks." Input is a 4-D
     `[Time, Channel, Height, Width]` binary/count tensor (e.g. output of a
     rate-coding scheme); each nonzero raster entry is converted to one or more
     `Spike` events with `timestamp = t_index·dt·1e6 + delay_factor·1e6`
     microseconds. [E3] — Sinabs source,
     https://sinabs.readthedocs.io/v2.0.1/_modules/sinabs/backend/dynapcnn/chip_factory.html
   - `xytp_to_events(xytp, layer, delay_factor=0)`: converts a structured
     `(x, y, timestamp, polarity)` event array (e.g. directly from a Tonic/NMNIST
     event-camera dataset) into `Spike` events — used for genuinely event-native
     data. [E3] — same source; usage example,
     https://sinabs.readthedocs.io/v3.1.3/tutorials/nir_to_speck.html and
     https://synsense-sys-int.gitlab.io/samna/0.38.5/devkits/dynapCnnSeries/examples/gesture_recognition.html
   - `events_to_raster(events, dt, shape)` performs the inverse conversion for
     reading output back into a dense tensor for analysis. [E3] — same source.
6. **Reading output.** Either (a) raw monitored-layer `Spike` events accumulate in
   a `samna_output_buffer`/sink node and are read with `.get_events()`, or (b) the
   dedicated **on-chip readout layer** performs classification directly on-chip
   (inactive / threshold / max-spiking-class / selected-class modes), reducing
   host-side post-processing. [E3] — Speck Dev Kit Datasheet (URL above); gesture
   recognition example (URL above) uses a majority-vote readout over a
   `t_interval` window on host-collected spikes.

---

## 5. The T question — software timesteps vs. asynchronous hardware execution

**Direct documentation statements, DYNAP-CNN/Speck:**

- "Computation in DYNAP-CNN is triggered directly by changes in the visual scene,
  **without using a high-speed clock**." [E4] — SynSense 2019 announcement (URL
  above, §1.3).
- "the neuromorphic chip **no longer needs the global or local clock signal**...
  As soon as the data is accessible at its input port, each block independently
  calculates its output value. Thus, **no running power from logic gates is
  employed when the asynchronous pipeline is idle**." [E1/E4] — Yao, Richter et
  al., *Nature Communications* 2024 (URL above).
- Explicit contrast with clocked neuromorphic chips: "Speck1 is specifically built
  to consume real-time data, its latency is significantly lower than Loihi1/2 and
  TrueNorth **which architecturally introduce a latency of one timestep Δt on event
  generation in each layer**." A footnote in the same comparison table states: "When
  connected to a sensor and the simulation time is synchronised to real-time,
  latency per layer is minimum the simulation time resolution Δt, **1 ms for
  TrueNorth**, as event generation takes one Δt." Speck's measured per-layer
  latency is instead ~0.37 µs/layer (3.36 µs ÷ 9 layers), a hardware propagation
  delay, **not a multiple of any chosen simulation Δt**. [E1] — Richter et al.,
  arXiv:2304.06793 (URL above).
- Conclusion drawn from these primary sources: on DYNAP-CNN/Speck, a
  software-side `num_timesteps` (Sinabs) is **not** "one hardware update tick."
  `num_timesteps`/`dt` only exists at the boundary where a discrete-time raster is
  converted into a stream of individually timestamped AER events
  (`raster_to_events`, §4.5) — after that point, the chip has no notion of a
  timestep at all; it reacts continuously and asynchronously to each event's
  arrival with a fixed, sub-4-µs propagation latency through up to 9 layers,
  regardless of how many "software timesteps" were used to construct the input
  spike train. The *only* clocked element on Speck2e+ is the auxiliary slow clock
  governing leak/DVS-filter/readout-averaging, not the convolutional compute path
  (§1.3).

**Direct contrast, Xylo:** "Synchronous time-stepped architecture with a global
time-step `dt`." Here the hardware genuinely advances state once per `dt`, and up
to 15 input events/channel and up to 31 output spikes/neuron are processed within
each such tick — i.e., on Xylo (audio/IMU line), unlike DYNAP-CNN/Speck (vision
line), T *does* correspond to a real, globally synchronous hardware clock. [E4] —
Rockpool Xylo overview (URL above, §2).

---

## 6. Published deployments on physical DYNAP-CNN / Speck hardware

| Work | Chip | Network / task | Dataset | Measured | Class |
|---|---|---|---|---|---|
| Yao, Richter, Zhao, Qiao, Xing, Wang, Hu, Fang, Demirci, De Marchi, Deng, Yan, Nielsen, Sheik, Wu, Tian, Xu, Li, *Nat. Commun.* 15:4464 (2024), https://doi.org/10.1038/s41467-024-47811-6 | Speck (physical, fabricated) | Dynamic (attention-gated) SNNs vs. vanilla SNNs, event-based action recognition | DVS128 Gesture, Gait-day, and 2 more event-based action-recognition benchmarks | Resting power 0.42 mW; real-time power as low as **0.70 mW**; Gesture: vanilla 81.0% acc / 9.5 mW, dynamic (50% input masking) 90.0% acc (**+9.0%**) / 3.8 mW (**−60% power**, spikes dropped 60.0%); end-to-end single-spike latency 3.36 µs; sub-0.1 ms latency reported for single-sample classification on public datasets | **E1** |
| Richter, Xing, De Marchi, Nielsen, Katsimpris, Cattaneo, Ren, Hu, Liu, Sheik, Demirci, Qiao, arXiv:2304.06793 (also underlying the Speck1 ASIC in the Nat. Commun. paper) | Speck1 (physical, fabricated silicon) | Hardware characterization only (no specific trained-network accuracy reported in this paper) | — | 327.6K neurons, 272 KB synaptic memory, 3.36 µs / 9-layer or 1.58 µs / 1-layer event latency, compared against Loihi1/2, TrueNorth, SCAMP5, Sony ISSCC21 | **E4** (chip characterization; latency measured on silicon but no application-level accuracy/energy pair) |
| Liu, Richter, Nielsen, Sheik, Indiveri, Qiao, "Live Demonstration: Face Recognition on an Ultra-Low Power Event-Driven CNN ASIC," CVPRW 2019, https://openaccess.thecvf.com/content_CVPRW_2019/papers/EventVision/Liu_Live_Demonstration_Face_Recognition_on_an_Ultra-Low_Power_Event-Driven_Convolutional_CVPRW_2019_paper.pdf | DynapCNN (predecessor to Speck2, physical) | 6-layer CNN (3 conv + 2 dense), 40K params, face recognition from live DVS feed | Custom recorded DVS face dataset | Sub-mW power on DynapCNN (real-time); peak SOps ≈200M; **98% recognition rate measured on recorded DVS dataset, validated against software SCNN simulation** (paper does not state accuracy was measured live on-chip, only power) | **E2** |
| Riverpublishers book chapter, "Deploying a Convolutional Neural Network on Edge MCU and Neuromorphic Hardware Platforms," https://www.riverpublishers.com/pdf/ebook/chapter/RP_9788770227902C10.pdf | DynapCNN devkit (physical), vs. Kendryte K210 and STM32L4R9 | Small CNN classifier | First 1000 MNIST test images, rate-coded (Bernoulli sampling per pixel, `tWindow`≈100) via a `to_spikes()` raster generator (equivalent to `raster_to_events`) | Balanced accuracy 98.79% at first-spike readout; DynapCNN was the fastest platform to provide a result; **energy is estimated (not directly measured) from average synaptic operations via Sinabs**, not from an on-board power sensor | **E2** (accuracy/latency measured on chip; energy is estimated, not measured) |
| Gesture recognition example, Samna docs, https://synsense-sys-int.gitlab.io/samna/0.38.5/devkits/dynapCnnSeries/examples/gesture_recognition.html | DynapcnnDevKit (physical) | 4-conv-layer gesture classifier (11-class), `from_model`→`DynapcnnNetwork` | DVXplorer live camera feed, IBM-DVS-Gesture-style 11 classes | Qualitative demo only; no accuracy/power/latency numbers reported in the documentation page | **E3** (documented working path, no published quantitative benchmark) |

**Object detection on physical DYNAP-CNN/Speck: NOT FOUND.** Spiking-YOLO
(Kim, Park, Na, Yoon, AAAI 2020, https://ojs.aaai.org/index.php/AAAI/article/view/6787/6641)
implements leaky-ReLU-based YOLO conversion and reports energy comparisons against
TrueNorth (simulated/estimated, not SynSense silicon) and GPU — it is unrelated to
the SynSense stack. No paper reporting an object-detection network measured on
physical DYNAP-CNN or Speck silicon was found in this search.

---

## 7. Availability / pricing

- Speck Dev Kit and Speck Demo Kit are real, purchasable/orderable hardware
  products, but **list pricing is not publicly posted**: "pricing is available only
  on application." [E4] — Hackster.io, "SynSense Launches Speck, Xylo Neuromorphic
  Development Kits," 2022,
  https://www.hackster.io/news/synsense-launches-speck-xylo-neuromorphic-development-kits-for-edge-ai-vision-and-audio-work-2897f0e6a7ac
- The Speck Demo Kit's early-bird pre-order batch "sold out"; the standard Demo Kit
  and the full Dev Kit remain available via SynSense's developer/sales channel.
  [E4] — SynSense, "Early bird offer for Speck Demo Kit sold out...", 2023,
  https://www.synsense.ai/early-bird-offer-for-speck-demo-kit-sold-out-explore-synsenses-range-of-neuromorphic-kits-and-open-source-tools/
- Hardware requirement: Speck Dev Kit needs a **USB 3.1** host connection (not
  USB 3.0), per the current manual — an earlier datasheet revision states USB 3.0.
  [E4] — Speck Dev Kit Manual 2025.12,
  https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf
- Xylo Audio Dev Kit is likewise available with pricing on application; compatible
  with Ubuntu 18.04/20.04 (Xylo-Audio also supports macOS 10.15+). [E4] —
  Hackster.io (URL above).
- NOT FOUND: a public list price (USD/EUR) for either Speck or Xylo devkits in any
  source retrieved.

---

## 8. Limitations for rate-coded conversion of static images

- Sinabs's own core tutorials demonstrate exactly this scenario **in software**:
  a static image (MNIST) is converted to a rate-coded spike raster by treating
  each pixel's normalized intensity as a Bernoulli firing probability per
  timestep: `img = (torch.rand(time_window, *img.shape) < img).float()`. Longer
  `time_window` gives a more precise (lower L2-error) reconstruction of the
  original static image, at the cost of more spikes/timesteps. [E3] — Sinabs
  "Signal-to-spike" tutorial,
  https://sinabs.readthedocs.io/v0.2.1/notebooks/Signal-to-spike.html ; weight
  transfer MNIST tutorial (URL above, §3.2).
- The toolchain **does** support presenting such a rate-coded raster to physical
  hardware: `ChipFactory.raster_to_events(raster, layer, dt)` converts the
  `[Time, Channel, H, W]` raster into a list of individually timestamped `Spike`
  events (§4.5), which is exactly the code path used by the Riverpublishers
  MNIST-on-DynapCNN deployment (§6, "E2" row) — the only found instance of a
  rate-coded *static-image* network actually run on physical DYNAP-CNN silicon.
- However, the two most-developed Speck/DYNAP-CNN deployment tutorials found in
  Sinabs's own documentation (`nir_to_speck`, the NMNIST EXODUS tutorial, and the
  Samna gesture-recognition example) exclusively use **event-native data**
  (NMNIST saccade recordings, DVS-Gesture, live DVS camera feed) fed via
  `xytp_to_events`, not synthetic rate-coded rasters. [E3] — URLs in §4.5, §6.
- No SynSense/Sinabs documentation page found makes an explicit *stated* claim
  that "rate-coded static images are a poor fit for this architecture" — that
  characterization is an inference from the architecture's design goals (§1.3–1.9:
  the entire pipeline — integrated DVS, per-event µs-scale asynchronous
  propagation, resting power near 0, readout tied to sparse event arrival) is
  optimized for naturally sparse, temporally structured event streams. Feeding it
  a dense Bernoulli-rate-coded raster forces an artificially high, temporally
  unstructured event rate at the input layer, which works (it is a plain sequence
  of AER events like any other, and is documented as supported via
  `raster_to_events`) but does not exercise the chip's headline advantages (near-zero
  idle power, sparsity-proportional energy) the way genuinely event-native input
  does. This is analytical framing on top of the primary sources above, not a
  quoted SynSense claim, and is flagged as such.

---

## Source list

1. SynSense/Sinabs, "Overview" (Speck), https://sinabs.readthedocs.io/main/speck/overview.html
2. SynSense, docs mirror, https://github.com/synsense/sinabs/blob/develop/docs/speck/overview.md
3. Samna docs, "Dynap-CNN series — Samna 0.39.9," https://synsense-sys-int.gitlab.io/samna/0.39.9/models/dynapCnnSeries/summary.html
4. SynSense, Speck2e Dev Kit Datasheet (PDF), https://www.synsense.ai/wp-content/uploads/2023/05/20221223_speck2e_devkit_datasheet_final.pdf
5. SynSense, Speck Dev Kit Datasheet, June 2023 (PDF), https://www.synsense.ai/wp-content/uploads/2023/06/Speck-devkit-datasheet.pdf
6. SynSense, Speck Dev Kit Datasheet, Aug 2023 (PDF), https://www.synsense.ai/wp-content/uploads/2023/08/Speck-Dev-Kit-Datasheet.pdf
7. SynSense, Speck Dev Kit Manual, Dec 2024 (PDF), https://www.synsense.ai/wp-content/uploads/2024/12/Speck-Dev-Kit-Manual.pdf
8. SynSense, Speck Dev Kit Manual, Dec 2025 V2 (PDF), https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf
9. Sinabs docs, "Available network architecture" FAQ, https://sinabs.readthedocs.io/develop/speck/faqs/available_network_arch.html
10. Richter, Xing, De Marchi, Nielsen, Katsimpris, Cattaneo, Ren, Hu, Liu, Sheik, Demirci, Qiao, "Speck: A Smart event-based Vision Sensor with a low latency 327K Neuron Convolutional Neural Network Processing Pipeline," arXiv:2304.06793, https://arxiv.org/html/2304.06793
11. Yao, Richter, Zhao, Qiao, Xing, Wang, Hu, Fang, Demirci, De Marchi, Deng, Yan, Nielsen, Sheik, Wu, Tian, Xu, Li, "Spike-based dynamic computing with asynchronous sensing-computing neuromorphic chip," *Nature Communications* 15:4464 (2024), https://doi.org/10.1038/s41467-024-47811-6 (also https://pubmed.ncbi.nlm.nih.gov/38796464/, https://europepmc.org/article/med/38796464)
12. SynSense, "DYNAP-CNN — the World's First 1M Neuron, Event-Driven Neuromorphic AI Processor for Vision Processing," 2019, https://www.synsense.ai/dynap-cnn-the-worlds-first-1m-neuron-event-driven-neuromorphic-ai-processor-for-vision-processing/
13. SynSense, XyloAudio 3 Devkit Datasheet, March 2026 (PDF), https://www.synsense.ai/wp-content/uploads/2026/03/XyloAudio-3-Devkit-datasheet_2026.03.pdf
14. SynSense, XyloAudio 3 Devkit Datasheet, Oct 2024 (PDF), https://www.synsense.ai/wp-content/uploads/2024/11/XyloAudio-3-Devkit-datasheet_2024.10-.pdf
15. Rockpool docs, "Overview of the Xylo family," https://rockpool.ai/devices/xylo-overview.html
16. SynSense, Xylo-Audio datasheet (PDF), https://www.synsense.ai/wp-content/uploads/2023/06/Xylo-Audio-datasheet.pdf
17. SynSense, XyloAudio dev kit datasheet 2022 (PDF), https://www.synsense.ai/wp-content/uploads/2023/09/XyloAudio-dev-kit-datasheet-2022.pdf
18. Bos, Muir, et al., "Micro-power spoken keyword spotting on Xylo Audio 2," arXiv:2406.15112, https://arxiv.org/html/2406.15112v1
19. Samna docs, "Xylo-Audio v3," https://synsense-sys-int.gitlab.io/samna/0.39.4/models/xyloSeries/xylo_audio_v3.html
20. Rockpool reference, `devices.xylo.syns61201.cycles_model`, https://rockpool.ai/reference/_autosummary/devices.xylo.syns61201.cycles_model.html
21. Sinabs API, `sinabs.from_torch.from_model`, https://sinabs.readthedocs.io/main/api/from_torch.html
22. Sinabs source, `from_torch.py` (multiple versions), e.g. https://sinabs.readthedocs.io/v3.1.2/_modules/sinabs/from_torch.html, https://sinabs.readthedocs.io/develop/_modules/sinabs/from_torch.html
23. Sinabs tutorial, "Weight transfer (MNIST)," https://sinabs.readthedocs.io/main/tutorials/weight_transfer_mnist.html, https://sinabs.readthedocs.io/v1.1.2/tutorials/weight_transfer_mnist.html
24. Sinabs, "The Basics" (Speck deployment guide), https://sinabs.readthedocs.io/v3.1.3/speck/the_basics.html, https://sinabs.readthedocs.io/v3.1.1/speck/the_basics.html, https://sinabs.readthedocs.io/develop/speck/the_basics.html
25. Sinabs discretize API, https://sinabs.readthedocs.io/v3.0.4/speck/api/dynapcnn/discretize.html, https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html
26. Sinabs `DynapcnnLayer` source, https://sinabs.readthedocs.io/develop/_modules/sinabs/backend/dynapcnn/dynapcnn_layer.html, https://sinabs.readthedocs.io/v3.0.3/_modules/sinabs/backend/dynapcnn/dynapcnn_layer.html
27. Samna docs, "Chip Models," https://synsense-sys-int.gitlab.io/samna/0.48.0/models/models.html, https://synsense-sys-int.gitlab.io/samna/0.47.1/models/models.html, https://synsense-sys-int.gitlab.io/samna/0.38.2/models/models.html
28. Samna docs, `samna.events`, https://synsense-sys-int.gitlab.io/samna/0.48.0/reference/events/index.html
29. SynSense, "SAMNA | Developer Interface to SynSense Toolchain," https://www.synsense.ai/products/samna/
30. Samna docs, "Quick Start," https://synsense-sys-int.gitlab.io/samna/0.48.0/quickStart.html
31. Samna docs, "How do I?," https://synsense-sys-int.gitlab.io/samna/0.43.4/howto.html
32. Samna docs, "Welcome to Samna's Documentation!," https://synsense-sys-int.gitlab.io/samna/0.48.2/index.html
33. Sinabs `chip_factory.py` source, https://sinabs.readthedocs.io/v2.0.1/_modules/sinabs/backend/dynapcnn/chip_factory.html
34. Sinabs tutorial, "Signal-to-spike," https://sinabs.readthedocs.io/v0.2.1/notebooks/Signal-to-spike.html
35. Sinabs tutorial, "NMNIST (EXODUS)," https://sinabs.readthedocs.io/v3.1.3/tutorials/nmnist.html, https://sinabs.readthedocs.io/main/tutorials/nmnist.html
36. Sinabs tutorial, "NIR to Speck," https://sinabs.readthedocs.io/v3.1.3/tutorials/nir_to_speck.html, https://sinabs.readthedocs.io/v3.0.0/tutorials/nir_to_speck.html
37. Sinabs tutorial, "NMNIST quick start" (Speck notebooks), https://sinabs.readthedocs.io/develop/speck/notebooks/nmnist_quick_start.html
38. Sinabs tutorial, "How To Leak The Neurons On The Devkit," https://sinabs.readthedocs.io/main/speck/notebooks/leak_neuron.html
39. Liu, Richter, Nielsen, Sheik, Indiveri, Qiao, "Live Demonstration: Face Recognition on an Ultra-Low Power Event-Driven Convolutional Neural Network ASIC," CVPRW 2019, https://openaccess.thecvf.com/content_CVPRW_2019/papers/EventVision/Liu_Live_Demonstration_Face_Recognition_on_an_Ultra-Low_Power_Event-Driven_Convolutional_CVPRW_2019_paper.pdf
40. Samna docs, "Gesture recognition with Dynap-CNN dev kit," https://synsense-sys-int.gitlab.io/samna/0.38.5/devkits/dynapCnnSeries/examples/gesture_recognition.html
41. Amir, Taba, Berg, Melano, McKinstry, Di Nolfo, Nayak, Andreopoulos, Garreau, Mendoza, Kusnitz, Debole, Esser, Delbruck, Flickner, Modha, "A Low Power, Fully Event-Based Gesture Recognition System," CVPR 2017, https://doi.org/10.1109/cvpr.2017.781 (TrueNorth, not SynSense — cited for the DVS128-Gesture dataset origin and as a clocked-hardware comparison point)
42. Richter, Wu, Whatley, Köstinger, Nielsen, Qiao, Indiveri, "DYNAP-SE2: a scalable multi-core dynamic neuromorphic asynchronous spiking neural network processor," arXiv:2310.00564 / *Neuromorphic Computing and Engineering*, https://doi.org/10.1088/2634-4386/ad1cd7
43. Rockpool / DynapSim paper, "Gradient-descent hardware-aware training and deployment for mixed-signal neuromorphic processors," *Neuromorphic Computing and Engineering* (2024), https://doi.org/10.1088/2634-4386/ad2ec3
44. "Deploying a Convolutional Neural Network on Edge MCU and Neuromorphic Hardware Platforms," book chapter, River Publishers, https://www.riverpublishers.com/pdf/ebook/chapter/RP_9788770227902C10.pdf
45. Kim, Park, Na, Yoon, "Spiking-YOLO: Spiking Neural Network for Energy-Efficient Object Detection," AAAI 2020, https://ojs.aaai.org/index.php/AAAI/article/view/6787/6641 (not SynSense hardware; cited to confirm absence of object-detection-on-SynSense-silicon result)
46. Hackster.io, "SynSense Launches Speck, Xylo Neuromorphic Development Kits for Edge AI Vision and Audio Work," 2022, https://www.hackster.io/news/synsense-launches-speck-xylo-neuromorphic-development-kits-for-edge-ai-vision-and-audio-work-2897f0e6a7ac
47. SynSense, "Early bird offer for Speck Demo Kit sold out! Explore SynSense's range of neuromorphic kits and open-source tools," 2023, https://www.synsense.ai/early-bird-offer-for-speck-demo-kit-sold-out-explore-synsenses-range-of-neuromorphic-kits-and-open-source-tools/
48. SynSense, "Spiking neural network dev kits for sound and vision," 2023, https://www.synsense.ai/spiking-neural-network-dev-kits-for-sound-and-vision/
49. SynSense, "SynSense releases the Speck Demo kit," https://www.synsense.ai/developercommunity/events-and-news/synsense-releases-the-speck-demo-kit/
50. SynSense, "Speck Dev Kit Quick Start Guide," https://www.synsense.ai/speck-quick-start-guide/
51. SynSense, "Developer" firmware page, https://www.synsense.ai/developer/
52. Rockpool tutorial, "Using XyloSamna and XyloMonitor to deploy a model on XyloAudio 3 HDK," https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html
53. Rockpool tutorial, "Quick-start with Xylo SNN core," https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html
54. Rockpool tutorial, "Training a spiking network to deploy to the Xylo digital SNN," https://rockpool.ai/devices/torch-training-spiking-for-xylo.html
55. Rockpool docs, "Torch transformation-in-training pipeline prototype," https://rockpool.ai/advanced/QuantTorch.html
56. Rockpool reference, `rockpool.devices.xylo.syns65302.xylo_mapper`, https://rockpool.ai/reference/_autosummary/rockpool.devices.xylo.syns65302.xylo_mapper.html
57. Rockpool tutorial, "Quick start with XyloAudio 3," https://rockpool.ai/devices/xylo-a3/xylo-audio3-intro.html

Also consulted but not separately cited above: sinabs.readthedocs.io (main),
rockpool.ai (main landing), synsense.ai (main landing) per task instructions.
