# A06 — Conversion and Interoperability Tooling: SNN Toolbox, NIR, Nengo/NengoLoihi, and Cross-Platform Portability

Research pass for the neuromorphic deployment survey. Every factual claim below carries an inline source URL. Edge classification key used throughout:

- **E1** — physical silicon measured (accuracy AND energy/latency reported on real chip)
- **E2** — physical silicon, accuracy only (chip run reported, but no energy/latency, or vice versa with accuracy as the only quantitative outcome)
- **E3** — documented software path exists, but no published run of *this specific model class* on that hardware
- **E4** — hardware model / cycle-accurate or bit-accurate simulator of the chip, not the chip itself
- **E5** — software simulation only (no hardware target claimed)

---

## 1. SNN Toolbox (Rueckauer et al., 2017)

### 1.1 Core paper and conversion algorithm

Rueckauer, Lungu, Hu, Pfeiffer, Liu, "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image Classification," *Frontiers in Neuroscience* 11:682, 2017.
https://doi.org/10.3389/fnins.2017.00682 (full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC5770641/)

- The paper formalizes **two reset mechanisms** for the IF neuron used in conversion:
  - *Reset-to-zero*: `V(t) = (V(t-1) + z(t)) · (1 - Θ)` — membrane forced to a fixed baseline (typically 0) whenever it fires.
  - *Reset-by-subtraction* ("linear reset mode," following Cassidy et al. 2013 and Diehl et al. 2016): `V(t) = V(t-1) + z(t) - V_thr · Θ` — the threshold is subtracted, and the residual charge above threshold is carried into the next timestep.
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC5770641/)
- **The paper explicitly recommends reset-by-subtraction over reset-to-zero.** The residual charge discarded at reset-to-zero introduces a firing-rate error term (Eq. 5a) that accumulates across deep layers; reset-by-subtraction removes this term (Eq. 5b), with firing rate converging exactly to the target ANN activation as t→∞. The paper's own CIFAR-10 ablation quantifies this: switching only the reset mechanism (holding everything else fixed) improved accuracy by roughly 20 percentage points (error dropped from ~40% to a further improved value en route to the paper's best 12.18% error, matching the ANN's 12.14%). (https://pmc.ncbi.nlm.nih.gov/articles/PMC5770641/)
- **Weight normalization / threshold balancing**: extends Diehl et al. (2015)'s data-based weight normalization to handle biases, and introduces percentile-based robust normalization (scaling by the *p*-th percentile of the activation distribution, p ∈ [99.0, 99.999], rather than the hard max) to avoid outlier-driven under-firing. This is the "weight/threshold balancing" step later papers cite as SNN Toolbox's core contribution alongside spiking softmax, max-pooling, and batch-norm folding. (https://doi.org/10.3389/fnins.2017.00682)
- This is a companion paper to Diehl et al. 2015 ("Fast-classifying, high-accuracy spiking deep networks through weight and threshold balancing," IJCNN 2015, doi:10.1109/IJCNN.2015.7280696), from which the normalization scheme and the term "threshold balancing" originate.

### 1.2 Input formats

The toolbox accepts models from **Keras/TensorFlow, PyTorch, Lasagne, and Caffe**. The 2017 paper states the toolbox transforms models "written in Keras, Lasagne and Caffe"; PyTorch support was added later (see release notes below) and is confirmed by the GitHub topic tags (`pytorch`, `caffe`, `keras`, `lasagne`, `tensorflow`). (https://doi.org/10.3389/fnins.2017.00682; https://github.com/NeuromorphicProcessorProject/snn_toolbox)

### 1.3 Backends — full enumeration and status

From the official documentation (https://snntoolbox.readthedocs.io/en/latest/guide/intro.html and https://snntoolbox.readthedocs.io/en/latest/api/simulation.html) and the GitHub repo (https://github.com/NeuromorphicProcessorProject/snn_toolbox):

| Backend | Type | Maintenance / functionality note | Published hardware use |
|---|---|---|---|
| **INIsim** (`INI_temporal_mean_rate`, `INI_temporal_pattern`, `INI_ttfs*`) | Built-in Keras-based simulator (TensorFlow or Theano backend) | Docs state explicitly: "This simulator backend is **recommended as it supports the most features and its integration is maintained best**." Theano backend retained only because it implements MaxPooling, which the TF backend lacks. | E5 — software only, not hardware |
| **pyNN** (routes to Brian, NEST, NEURON) | Simulator-independent interface | Docs recommend **NEST version 2.14** specifically if using a pyNN backend. | E5 |
| **Brian2** (`brian2_target_sim`) | Direct Brian2 simulator export | Present since v0.3.1/v0.3.2 ("Brian2 extensions," 2020 release). | E5 |
| **MegaSim** (`MegaSim_target_sim`) | Custom asynchronous event-driven simulator developed at University of Seville | Niche academic simulator; integrated into the toolbox for the TTFS/timing-based encoding modes. | E5 (asynchronous digital *simulator*, not physical silicon) |
| **SpiNNaker** (`spiNNaker_target_sim`) | Deployment to University of Manchester's SpiNNaker neuromorphic system, via SpyNNaker software (dependency: SpyNNaker) | Added in v0.4.0 ("SpiNNaker support," 2020 releases). Uses pyNN-style connection files. No SNN Toolbox-authored paper reports classification results measured on physical SpiNNaker silicon using this pipeline; the toolbox's own docs point to "Examples" tutorials for end-to-end use but the accuracy/energy numbers published on SpiNNaker for converted CNNs in the literature (e.g., MNIST 1.80% error, Table 2 of Rueckauer et al. 2022, NxTF paper) are attributed to a separately-trained STBP direct-training pipeline, **not** SNN-TB's SpiNNaker backend specifically, in the one cross-platform comparison table found (see §1.4). | E3 (documented path; no SNN-TB-attributed published accuracy number found run on physical SpiNNaker for a converted CNN) |
| **Loihi** (`loihi_target_sim`) | Deployment to Intel Loihi via NxTF/NxSDK | This is the backend with the clearest, best-documented published hardware run: Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild, "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi," *ACM JETC* 2022 (arXiv:2101.04261), explicitly built an interface between NxTF and SNN-TB and reported converted-CNN accuracy **measured on physical Loihi silicon**: CIFAR-10 (MobileNet-derived, 413k neurons, 3M params) 8.52% error, 102 mJ/sample, 340 ms delay; MNIST 0.79% error, 0.66 mJ/sample; N-MNIST 1.57% error, 0.29 mJ/sample. (https://doi.org/10.1145/3501770, https://arxiv.org/html/2101.04261) | **E1** for the NxTF+SNN-TB→Loihi CIFAR-10/MNIST/N-MNIST runs — this is the single clearest end-to-end case of a rate-coded, reset-by-subtraction conversion pipeline producing a published physical-hardware result |
| GUI | Standalone visualization tool | Toolbox source explicitly notes: **"The GUI has not been maintained since 2017 and is most likely broken."** | N/A |

(https://snntoolbox.readthedocs.io/en/latest/api/simulation.html; https://github.com/NeuromorphicProcessorProject/snn_toolbox/blob/master/docs/source/guide/intro.rst)

### 1.4 Current maintenance status (checked 2026)

- PyPI release history: v0.1.0 (2017) through **v0.6.0 (2021-03-17)**, the last tagged release, adding TensorFlow 2.4 support, Conv1D layers, and a spiking maxpool for the TF backend. (https://pypi.org/project/snntoolbox)
- GitHub commit history shows only sparse bugfix commits after that: e.g., `047cedd` "Fixed kernel_conversion slicing issue" (2022-08-13) and `9d421f4` "Fixed deprecated import in GUI" (2022-08-08), both single-file patches by the original author (rbodo). No feature commits found after 2022. (https://github.com/NeuromorphicProcessorProject/snn_toolbox/commit/047cedd869adad7dc0b2cd09b8f8c796152f6742; https://github.com/NeuromorphicProcessorProject/snn_toolbox/commit/9d421f43dd6cd14c2f204aae4c2a68b770e88e7d)
- deps.dev's OpenSSF-style activity score for the repo: **0/10**, citing "0 commits and 0 issue activity in the last 90 days." (https://deps.dev/project/github/neuromorphicprocessorproject%2fsnn_toolbox)
- Repository stats: 399 stars, 106 forks, 3 open issues, MIT license, default branch `master`, created 2016-07-27. (https://github.com/NeuromorphicProcessorProject/snn_toolbox)
- A Loihi-loading issue from a user in Nov 2020 (`Loading SNN on Loihi #75`) documents version-compatibility breakage between SNN-TB-saved models and updated NxSDK/TensorFlow versions, closed May 2021 with only a partial workaround (retrain rather than reload). This is evidence the Loihi backend already had bit-rot problems by 2020–21, i.e., before the toolbox effectively stopped receiving updates. (https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues/75)

**Verdict**: SNN Toolbox is best described as **dormant, not actively maintained** as of 2026 — last substantive release in March 2021, last bugfix patches in August 2022, no activity since. Its INIsim (software) backend remains the best-supported path; its hardware backends (SpiNNaker, Loihi) depend on external SDKs (SpyNNaker, NxSDK) that have themselves moved on, so functional deployment today would require pinning old SDK versions.

---

## 2. NIR — Neuromorphic Intermediate Representation

Pedersen, Abreu, Jobst, Lenz, Fra, Bauer, Muir, Zhou, Vogginger, Heckel, Urgese, Shankar, Stewart, Sheik, Eshraghian, "Neuromorphic intermediate representation: A unified instruction set for interoperable brain-inspired computing," *Nature Communications* 15:8122, 2024.
https://doi.org/10.1038/s41467-024-52259-9 (open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC11405706/; arXiv preprint: https://arxiv.org/html/2311.14641)

### 2.1 Computational primitives

NIR defines **17 primitives** (11 "fundamental" primitives in the original arXiv version, extended to 17 in the published version), each specified as a hybrid continuous-time dynamical system with declared parameters, computation, and (where applicable) reset rule. Full table: https://neuroir.org/docs/primitives/ and Table 2 of the paper (https://nature.com/articles/s41467-024-52259-9/tables/2).

Primitives include: Input, Output, Affine (`W·I + b`), Convolution, Linear (`W·I`), Flatten, Delay, Integrator (`v̇ = R·I`), Leaky Integrator / LI (`τv̇ = (v_leak − v) + R·I`), **Integrate-and-fire (I&F)** = Integrator + Threshold with reset, **Leaky integrate-and-fire (LIF)** = LI + Threshold with reset, **Current-based LIF (CuBa-LIF)** = LIF ∘ Linear ∘ LI (a higher-order composition).

**Critical limitation on reset semantics**: The official primitive table specifies the reset rule for I&F and LIF as:
```
v ← { v_reset  if Spike
    { v        otherwise
```
i.e., reset to a **fixed target value `v_reset`** — this is formally **reset-to-zero-style (hard) reset**, not reset-by-subtraction (soft reset, `v ← v − v_threshold`). The NIR spec as published does not define a subtract-reset primitive. (https://neuroir.org/docs/primitives/; https://nature.com/articles/s41467-024-52259-9/tables/2)

This creates a real interoperability gap for anything trained with soft/subtract reset — which includes SNN Toolbox's own recommended reset-by-subtraction mode (§1.1) and QCFS-style conversion (see §5). Concrete evidence this is a live problem, not a theoretical one:
- snnTorch's own neuron classes internally implement subtract-reset (`v ← v − v_threshold`, the mode the snnTorch team calls their "hard reset," confusingly) but historically **exported `v_reset = 0` to NIR**, silently losing the distinction. A snnTorch GitHub PR, "nir: add missing v_reset parameter on export" (https://github.com/jeshraghian/snntorch/pull/388), and a related reset-mechanism refactor PR that documents the "hard reset resets by subtraction… soft reset resets to zero" confusion in the codebase (https://github.com/jeshraghian/snntorch/pull/426) both confirm this is an actively-tracked bug/ambiguity in the reference NIR-exporting implementation, not merely a documentation nuance.
- A third-party project reproducing an NIR importer independently found the same gap and had to add an explicit `reset_mode="subtract"` parameter absent from the NIR spec's default (`reset_mode="reset"`, i.e., `v = v_reset`) to correctly round-trip snnTorch models (https://anulum.github.io/sc-neurocore/guides/nir_integration/). This is a small, non-peer-reviewed side project, cited here only as corroborating evidence that the reset-semantics mismatch is a reproducible implementation issue, not authoritative in its own right.

**Does NIR cover the plain IF neuron used in rate-coded conversion (à la Rueckauer 2017 / QCFS)?** Yes, structurally — I&F is a defined primitive (Integrator + Threshold + reset). But the reset it encodes by default is the fixed-value/hard variant; QCFS-style reset-by-subtraction with a *learnable* threshold is not a first-class NIR primitive and must be approximated or hand-patched per the reset-mode workaround above.

### 2.2 Frameworks supporting NIR

Per the official support matrix (https://neuroir.org/docs/support/), **9 simulators** and **5 hardware platforms** currently interoperate via NIR (this count is post-publication growth from the original paper's "7 simulators, 4 hardware platforms"):

| Framework | Write to NIR | Read from NIR |
|---|---|---|
| hxtorch (BrainScaleS-2) | ✓ | ✓ |
| jaxsnn (BrainScaleS-2) | — | ✓ |
| Lava-DL | — | ✓ |
| Nengo | ✓ | ✓ |
| Norse | ✓ | ✓ |
| Rockpool (targets SynSense Xylo) | ✓ | ✓ |
| Sinabs (targets SynSense Speck) | ✓ | ✓ |
| snnTorch | ✓ | ✓ |
| SpiNNaker2 | — | ✓ |
| Spyx | ✓ | ✓ |

Hardware platforms reached: **BrainScaleS-2** (analog/mixed-signal, via hxtorch/jaxsnn), **Intel Loihi 2** (via Lava-DL), **SynSense Speck** (via Sinabs), **SpiNNaker2**, **SynSense Xylo** (via Rockpool). (https://neuroir.org/docs/support/)

### 2.3 What the paper actually demonstrated on hardware

The paper's own hardware-facing experiments (not just documentation claims) used three model classes of increasing complexity, each cross-checked across all 11 platforms available at publication time:
1. A single LIF neuron
2. A spiking convolutional network (SCNN) with IF neurons
3. A spiking recurrent network (SRNN) with CuBa-LIF neurons, trained in snnTorch via BPTT+surrogate gradients on a Braille letter-recognition task

Quantized/bit-precision details reported per platform: **Loihi 2** used 24-bit state variables, 16-bit activations, 12-bit time constants, 17-bit thresholds, 8-bit weights in these experiments. **SpiNNaker2** (via py-spinnaker2) uses 8-bit signed synapse weights and 32-bit float neuron state, with IF/LIF/CuBa-LIF neuron models supporting **both** reset-by-subtraction and reset-to-zero (a hardware/software capability the *formal NIR primitive spec* does not itself expose, per §2.1 — SpiNNaker2's own backend implements more than NIR's declared primitive covers). **SynSense Xylo** (Audio 2 / SYNS61201) uses an integer-logic CuBa-LIF core: 8-bit weights, 16-bit synaptic/membrane state, 1000 hidden neurons max, 8 output channels. (All figures from the Methods section, https://pmc.ncbi.nlm.nih.gov/articles/PMC11405706/)

The paper found **faithful cross-platform agreement for feedforward dynamics** (single LIF neuron, SCNN with IF neurons) but **diverging activation patterns and accuracy for the recurrent (SRNN) case**, attributed to platform-specific discretization choices; the authors note explicitly that achieving the highest accuracies for the recurrent case required "platform-dependent optimization, such as quantization-aware training." (https://doi.org/10.1038/s41467-024-52259-9)

### 2.4 Stated limitations (verbatim from the paper's own discussion)

> "The current version of NIR excludes other important mechanisms such as adaptive threshold mechanisms, gating, resonate-and-fire, and multicompartmental neuron models." — and — "The present set of primitives is limited, and many platforms are not included in our analysis." (https://doi.org/10.1038/s41467-024-52259-9)

Additional practical limitation documented on the project's own porting guide: **hardware backends are permitted to simply *ignore* unsupported NIR nodes** rather than being required to approximate them faithfully — "If your platform does not support the node, you can simply ignore it… we advise that you simply raise an exception… In our roadmap, we plan to work on optimization and approximation strategies for these cases" (i.e., as of the current docs, approximation strategies for unsupported primitives are future work, not implemented). (https://neuroir.org/docs/porting-nir/)

**Bottom line for the survey's portability claim**: NIR is a genuine, working, and unusually broad interchange format — the strongest thing in this space by a wide margin — but it (a) does not natively express soft/subtract reset (the reset mode QCFS and SNN-TB's own best-practice recommendation both depend on), (b) its own reported hardware validation is strongest for simple feedforward IF/LIF models and visibly degrades for recurrent/stateful models, and (c) explicitly leaves gating, adaptive thresholds, and multicompartmental models — and by extension anything requiring precise reproduction of a *learnable*, per-layer threshold under a specific reset rule — outside its current primitive set. It reduces an *m×n* interoperability problem to *m+n* (https://arxiv.org/html/2311.14641, Fig. 2) but does not by itself guarantee bit-accurate transfer of a specific trained IF configuration to silicon.

---

## 3. Nengo / NengoLoihi / NengoDL

### 3.1 What Nengo is, and how it differs from rate-coded conversion

Nengo implements the **Neural Engineering Framework (NEF)** (Eliasmith & Anderson, 2003): a "white-box" method for encoding numerical values into populations of (often LIF) spiking neurons via tuning curves and decoding weights solved analytically/least-squares, rather than backprop-trained rate matching. This is fundamentally a different construction principle from QCFS/SNN-Toolbox-style ANN→SNN conversion, which instead trains a continuous-valued network and translates its ReLU activations into IF/LIF firing rates post hoc. Nengo's **NengoDL** package bridges the two worlds: it lets users build/train models with the Keras/TensorFlow API and *also* provides a `nengo_dl.Converter` that swaps ReLU activations for spiking equivalents — i.e., NengoDL supports rate-coded ANN-to-SNN conversion as one of its modes, in addition to native NEF modeling. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/; https://ar5iv.labs.arxiv.org/html/1805.11144)

### 3.2 NengoLoihi mapping and published hardware results

NengoLoihi is a backend that compiles a Nengo network (built via NEF or via NengoDL conversion) onto Intel's Loihi chip, and also ships a Loihi *emulator* for development without hardware access. Constraints it must account for: discretized neuron activation profiles (`LoihiLIF` / `LoihiSpikingRectifiedLinear` neuron classes model Loihi's quantization during training), per-core neuron/connectivity limits (1024 neurons/core), connection-weight discretization, and on-/off-chip communication latency. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/; https://google.iopscience.iop.org/article/10.1088/2634-4386/acb286/pdf)

Published, physical-hardware (**E1**) results:
- **CIFAR-10 convolutional net on one Loihi chip** (NengoDL-converted, tutorial-scale, not SOTA-accuracy): demonstrates the ANN→spiking-conversion + on-chip-block-partitioning workflow but is explicitly described by the authors as "not particularly powerful" and not competitive with SOTA — included to show feasibility of fitting a CNN on one chip, block-shape-constrained to ≤1024 neurons/core. (https://www.nengo.ai/nengo-loihi/v1.0.0/examples/cifar10-convnet.html)
- **Keyword-spotting deep network on Loihi vs. GPU/CPU**: Nengo DL on Loihi used **38× less energy per inference** than an architecturally identical network on an NVIDIA Quadro K4000 GPU; also beat Jetson TX1 (7.3× less energy), Xeon E5-2630 CPU (8.2× less), Movidius NCS (1.9× less). Reported jointly by Applied Brain Research and Intel's Mike Davies (Director, Neuromorphic Computing Lab). (https://www.prnewswire.com/news-releases/applied-brain-research-inc-shows-nengo-spiking-real-time-ai-deep-learning-networks-on-intel-loihi-use-38x-less-energy-than-on-nvidia-quadro-k4000-gpu-300761243.html; underlying study arXiv:1812.01739)
- **7-DOF robot-arm operational-space control (adaptive controller)**, running fully spiking on Loihi hardware (Nahuku/Kapoho Bay boards, NxSDK 0.9): RMSE only 4.13% worse than the analytic (non-spiking) controller; **two orders of magnitude less dynamic energy per inference** than CPU/GPU baselines; described by the authors as "the most advanced neuromorphic implementation of neurorobotics developed to date" at time of publication (2023, *Neuromorphic Computing and Engineering*). (https://doi.org/10.1088/2634-4386/acb286)
- Real-world Kinova Jaco2 arm reaching task with on-chip PES learning: Loihi implementation showed lowest power and near-CPU latency, outperforming CPU/GPU on a normalized adaptive-control error metric after 50 trials. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/)

All of the above are **E1** (physical Loihi silicon, both accuracy/task-performance and energy measured) for models trained through Nengo's LIF/NEF-based pipeline (not QCFS-style IF conversion).

### 3.3 What's supported more broadly

Nengo's documented backend list spans CPU (core Nengo), GPU (NengoOCL), FPGA, Intel Loihi (NengoLoihi), and SpiNNaker (via `nengo_spinnaker`) — i.e., Nengo independently reaches nearly the same hardware surface NIR aggregates, but through Nengo-specific compilers rather than a shared IR (Nengo itself is one of NIR's 9 supported simulators, per §2.2). (https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/)

---

## 4. Other converters

### 4.1 NxTF (Intel's Keras-derived Loihi compiler)

Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild, "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi," *ACM Journal on Emerging Technologies in Computing Systems* 18(2), 2022. https://doi.org/10.1145/3501770 (arXiv: https://arxiv.org/html/2101.04261)

- NxTF is a Keras-Model/Layer-derived programming interface within Intel's NxSDK, distinct from **NxNet** (Intel's own low-level, full-featured but generality-first API) and from the third-party **Nengo** API — all three sit atop the same register-level **NxCore** API. NxTF trades NxNet's full generality for DNN-focused compilation (partitioner + register-level mapper), exploiting CNN weight-sharing to compress models across cores. (https://arxiv.org/html/2101.04261)
- Explicitly built an **interface between NxTF and SNN Toolbox** (github.com/intel-nrc-ecosystem/models, `nxsdk_modules_ncl/dnn/…/snntoolbox`) so that SNN-TB's Keras/PyTorch/Caffe/Lasagne-ingested, weight-normalized conversions can be compiled directly onto Loihi. (https://arxiv.org/html/2101.04261)
- **Neurons in this pipeline use hard reset** when derived from SLAYER-trained models ("Neurons in SLAYER models use a hard reset and thus require only a single compartment"); the paper does not claim its NxTF+SNN-TB conversion use case switches this — the compiled network inherits SNN-TB's own configured reset mode (which SNN-TB's authors recommend be reset-by-subtraction per §1.1, though the specific NxTF benchmark runs in this paper are not stated to have used one mode vs. the other explicitly in the excerpts retrieved).
- Achieved **80% resource utilization across 16 Loihi chips** for a 28-layer, 4M-parameter MobileNet (128×128 input) and reported **8.52% error on CIFAR-10 — the lowest error rate reported on neuromorphic hardware for that dataset** at time of publication, all via the SNN-TB conversion route. **E1.**

### 4.2 Quartz-on-Loihi (temporal/TTFS conversion, not rate-coded)

Lenz, Orchard, Sheik, "Ultra-low-power Image Classification on Neuromorphic Hardware" (Quartz), arXiv:2309.16795, 2023. https://doi.org/10.48550/arxiv.2309.16795; code: https://github.com/biphasic/Quartz-on-Loihi

- **Not** a rate-coded conversion tool — Quartz is a **time-to-first-spike (TTFS)** ANN→SNN converter, included here because it is directly informative about reset semantics: the paper states explicitly **"No soft reset of membrane potentials needed"** for TTFS coding, because neurons fire at most once — the opposite design choice from SNN Toolbox's rate-coded recommendation (reset-by-subtraction) in §1.1. This underlines that reset-by-subtraction is specifically a *rate-coding* concern, not a universal ANN-to-SNN requirement.
- Measured on **physical Loihi hardware** for MNIST and CIFAR-10: MNIST 0.77% error (vs. 0.73% ANN, 5.4k spikes, 65 timesteps); CIFAR-10 25.14% error (vs. 24.04% ANN, 48k spikes, 1211 timesteps), compared directly against rate-coded Loihi baselines (Rate-Loihi CIFAR-10: 8.52% error — the NxTF/SNN-TB result from §4.1 — at 400 timesteps but with far fewer spikes reported per the paper's own accounting caveats). Code publicly available. **E1**, but note the CIFAR-10 accuracy is considerably worse than the rate-coded NxTF+SNN-TB result — Quartz trades accuracy for spike-count/energy efficiency at this scale. (https://arxiv.org/pdf/2309.16795)
- The paper also states plainly that prior temporal-coding conversion methods, while promising in simulation, "have yet to show that they can be implemented on neuromorphic hardware" — i.e., Quartz's own contribution is explicitly framed as closing a hardware-validation gap that other temporal methods had not closed. This is direct evidence that **most TTFS/temporal ANN-to-SNN conversion literature remains E5 (simulation only)**, with Quartz as a documented exception.

### 4.3 Lava-DL NetX (HDF5 export)

`lava.lib.dl.netx` — https://lava-nc.org/lava-lib-dl/netx/netx.html ; https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/netx/README.md

- Training happens in `lava.lib.dl.slayer` (event-based, SLAYER 2.0) or `lava.lib.dl.bootstrap` (rate-coded SNN training), producing a **platform-independent HDF5 network description**. `netx.hdf5.Network(net_config=...)` then reconstructs the model as a runnable Lava Process graph.
- Supported layer types in the HDF5 schema: `input`, `flatten`, `average`, `concat`, `dense`, `pool`, `conv` — each `dense`/`pool`/`conv` entry carries a `neuron` sub-field describing compartment parameters (default neuron type: **CUBA-LIF**), with fields like `iDecay`, `vDecay`, `vThMant`, `refDelay`. (https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/netx/README.md)
- Published examples run **on physical Loihi 2 hardware** (Kapoho Point / Oheo Gulch systems): an Oxford audio-classification tutorial and a **YOLO-KP** (TinyYOLOv3-derived, fully convolutional, 8-Loihi-2-chip "Kapoho Point" form factor) object-detection network, with quantized (6-bit fractional weight_exp) input and a working Loihi-2 hardware run-config path (`Loihi2HwCfg`). (https://github.com/lava-nc/lava-dl/blob/main/tutorials/lava/lib/dl/netx/yolo_kp/run.ipynb; https://github.com/lava-nc/lava-dl/blob/main/tutorials/lava/lib/dl/netx/oxford/run.ipynb) These are **E1/E2**-class demonstrations (hardware execution confirmed in the tutorial code; the retrieved excerpts show execution logs and compiler behavior on Loihi 2, though full accuracy tables were not captured in this pass) — but note this is for **SLAYER/bootstrap-trained CUBA-LIF networks**, not QCFS-style IF-with-learnable-threshold conversion.

### 4.4 SpikingJelly `lava_exchange` (see also §6 below)

Covered in full in §6; summarized here for completeness of the converter enumeration: SpikingJelly → Lava DL (HDF5) → Lava → Loihi, IF/LIF only, hard reset only (`v_reset` must equal 0), no bias support in exported Conv2d/Linear layers.

### 4.5 Rockpool → Xylo

Zhou, Muir, "Deployment Pipeline from Rockpool to Xylo for Edge Computing," arXiv:2412.11047, 2024. https://doi.org/10.48550/arxiv.2412.11047

- Pipeline: build network in Rockpool → `mapper()` (maps computational graph to Xylo's CuBa-LIF architecture, DRC-checks constraints) → `rockpool.transform.quantize_methods` (**global_quantize** or **channel_quantize**, both producing integer weights/thresholds/dash — 8-bit weights, 16-bit thresholds by default) → `config_from_specification()` (validates + builds hardware config object) → `XyloSamna` / `XyloMonitor` (deploys to physical Xylo HDK, either accelerated-time or real-time streaming mode). (https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html; https://doi.org/10.48550/arxiv.2412.11047)
- Concrete physical-hardware example: an audio-classification (keyword-spotting) model deployed to a **XyloAudio 3 HDK**, run in both accelerated (`XyloSamna`) and real-time streaming (`XyloMonitor`, using the chip's onboard microphone) modes, with on-device power recording (`record_power=True`, io/analog/digital breakdown). (https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html) **E1** for audio/keyword-spotting workloads on Xylo — not vision/CNN-scale workloads; Xylo's CuBa-LIF core (max ~1000 hidden neurons, 64k synaptic weights on Xylo Audio 2) is explicitly a small-scale, sensory-inference-class device, not a CIFAR-scale accelerator.

### 4.6 Sinabs → Speck (SynSense DVS+SNN SoC)

- Sinabs library (`sinabs.from_nir` for NIR import) + `sinabs-dynapcnn`/`DynapcnnNetwork` for hardware-config generation and deployment. Speck integrates a DYNAP-CNN asynchronous neuromorphic processor with an on-chip Dynamic Vision Sensor; up to 320K configurable spiking neurons across 9 DYNAP-CNN cores (Conv → IAF spiking neuron → SumPool per core), 8-bit weights, 16-bit membrane states. (https://sinabs.readthedocs.io/main/speck/overview.html; https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf)
- Documented **NIR-to-Speck deployment tutorial**: import a NIR graph → sinabs → collapse per-neuron thresholds to a single per-layer value (**Speck does not support individual per-neuron parameters** — an explicit hardware constraint the tutorial works around) → `DynapcnnNetwork` → stream N-MNIST events to the chip → **90.00% test accuracy reported on physical Speck silicon** in the worked example. (https://sinabs.readthedocs.io/main/tutorials/nir_to_speck.html) **E1**, though this is a tutorial-scale demonstration (N-MNIST, single-value-threshold-per-layer), not a large CNN benchmark.
- The chip only supports Conv→spike→pool per core, requires `AvgPool2d`→`SumPool2d` and `Linear`→1×1 `Conv2d` rewriting to fit the hardware's layer model — additional evidence that "deploys to hardware" universally implies **architectural rewriting**, not a transparent 1:1 mapping, even within a single vendor's own toolchain.

### 4.7 ONNX-based SNN paths

- **`onnx-snn`** (neurom-iot): an ONNX extension mapping DNN activation ops (Sigmoid/ReLU/tanh) to spike neuron types (LIF/softLIF), feeding into NengoDL for rate-neuron training, with round-trip conversion utilities (`convert_snnOnnx.py`, `onnxToNengoCode.py`, `onnxToNengoModel.py`). The project's own README marks several round-trip directions as failing (`nengo_dl model -> onnx-snn -> onnx -> keras model --> X`; `onnx model, weight -> onnx-snn -> nengo_dl model --> X`), i.e., **this is an incomplete, research-grade prototype, not a robust general ONNX-SNN standard**, and it is not part of the official ONNX project. (https://github.com/neurom-iot/onnx-snn) **E5 at best; no evidence of hardware deployment.**
- No evidence was found of an ONNX operator-set extension for spiking neurons adopted by the mainstream ONNX project (onnx/onnx) itself. **NOT FOUND**: an official, maintained, ONNX-native SNN standard.
- `snnTorch.export_nir` explicitly routes through **NIR**, not ONNX, for cross-framework portability (`snntorch.export_nir.export_to_nir()`, using `nirtorch` to trace the computational graph). (https://snntorch.readthedocs.io/en/latest/snntorch.export_nir.html) This is the mainstream, actively maintained snnTorch export path — ONNX is not it.
- One GitHub repo search surfaced ONNX-mediated deployment to **BrainChip Akida hardware** (explicitly excluded from this survey's scope per the task instructions, so noted only for completeness and not analyzed further) and a `.fbz` format conversion chain (`torch.onnx.export → akida import-onnx`). Per scope instructions, Akida is skipped.

---

## 5. The portability question: does anything take a trained QCFS-style network (IF neuron, reset-by-subtraction, learnable per-layer threshold, finite T) and emit a configuration for accessible neuromorphic silicon?

This was searched directly and repeatedly (queries combining "QCFS," "quantization clip floor shift," "reset-by-subtraction," "learnable threshold," "Loihi," "SpiNNaker," "hardware deployment"). Findings:

- **The one directly QCFS-related hardware-facing result found is APEX** (arXiv:2608.19046, "APEX: A Dual-Sparsity Accelerator for Precise and Efficient SNN Inference"), which builds on a companion work "PASCAL" defining the **PASC-IF** neuron as an improvement on the plain IF neuron used in QCFS conversion. Critically, **APEX targets a proposed, non-fabricated accelerator design (integrated into the "LoAS" hardware framework as a synthesized/simulated combinational circuit), not an existing, accessible, commercially/academically available neuromorphic chip.** The paper reports area/power overhead and energy reduction from RTL-level or architectural simulation, not measurement on a chip that a third party could obtain and run. **This is E4 (hardware model), not E1/E2 — it is not a deployment of a QCFS network onto real, accessible silicon.**
- **NxTF+SNN-TB→Loihi (§4.1, §1.3)** is the closest thing to a QCFS-adjacent published hardware run: it uses the same *family* of technique — rate-coded ANN→SNN conversion, weight-normalized IF neurons, reset-by-subtraction recommended by the same toolbox — and achieves a real, physical-Loihi, competitive CIFAR-10 result (8.52% error). However, this predates QCFS (2017–2022 work vs. QCFS's 2022 ICLR publication) and uses SNN-TB's own IF/threshold-balancing scheme, **not** QCFS's specific quantization-clip-floor-shift activation function or its learnable-global/per-layer threshold formulation. It is evidence that *the reset-by-subtraction rate-coded IF family generally* has a documented hardware path — not that QCFS specifically has been run on hardware.
- **No published work was found** that takes a QCFS-trained network (with its specific clip-floor-shift quantized activation, learnable threshold λ, and reset-by-subtraction IF neuron used at finite T) and emits a configuration for Loihi, Loihi 2, SpiNNaker, SpiNNaker2, Xylo, or Speck, with results measured on that physical chip. Searches for "QCFS Loihi," "QCFS SpiNNaker," "quantization clip floor shift neuromorphic chip," and variants combining QCFS-specific terminology with each accessible chip name returned no such paper.
- The **structural barriers** are visible across every converter surveyed above and are consistent with why this gap exists:
  1. NIR's own primitive spec does not natively encode subtract-reset (§2.1) — the exact reset rule QCFS and SNN-TB's own best practice both depend on.
  2. Hardware backends that *do* support subtract-reset (SpiNNaker2's py-spinnaker2, per the NIR paper's own Methods section) do so as a hardware/software capability outside NIR's formal spec, requiring bespoke, non-NIR-mediated glue.
  3. Chips with the largest published CNN-scale results (Loihi via NxTF) use 8-bit weight quantization and up to 24-bit state variables baked into the compiler — a QCFS network's specific *learnable* threshold would need re-quantization/re-calibration for that hardware's fixed-point representation, a step no surveyed tool automates for QCFS specifically.
  4. Every hardware deployment surveyed (Speck, Xylo, NxTF/Loihi) required non-trivial architectural rewriting (threshold collapsing to one value per layer, `Linear`→1×1`Conv2d`, `AvgPool2d`→`SumPool2d`, per-core neuron-count partitioning) — there is no "drop-in" path even for architectures the tools do support well.

**Conclusion for this question, stated explicitly**: **NOT FOUND.** No tool or published pipeline was located that takes a trained QCFS-style network as such and emits a working configuration measured on accessible neuromorphic silicon. The closest analogues are (a) NxTF+SNN-TB→Loihi, which is the same *conversion family* (rate-coded IF, reset-by-subtraction) but not QCFS's specific formulation, run on real hardware; and (b) APEX/PASCAL, which is QCFS-specific but targets a simulated/proposed accelerator, not accessible fabricated silicon.

---

## 6. SpikingJelly `lava_exchange`

Tutorial: https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html (English) / module source: https://spikingjelly.readthedocs.io/zh-cn/latest/_modules/spikingjelly/activation_based/lava_exchange.html

### 6.1 What it converts and the workflow

Documented pipeline: **SpikingJelly → Lava DL → Lava → Loihi**. `spikingjelly.activation_based.lava_exchange` provides:
- Data-format conversion (`TNX_to_NXT` / `NXT_to_TNX`) between SpikingJelly's multi-step `[T, N, *]` layout and Lava DL's `[N, *, T]` layout.
- Neuron conversion via `to_lava_neuron()`.
- `BlockContainer`, mimicking Lava's `Blocks` (fused synapse+neuron), convertible via `.to_lava_block()` into a real `lava.lib.dl.slayer.block.cuba` block.
- A final `export_hdf5()` step producing the same HDF5 network-exchange format `lava.lib.dl.netx` consumes (§4.3), so the end target is loadable by Lava and runnable "on Loihi, or the CPU-simulated Loihi." (https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html)

### 6.2 Neuron models supported

**Only IF and LIF**, explicitly limited by design: "Due to the limited time and energy of developers, SpikingJelly only supports the IF neuron and the LIF neuron... Other neurons will be considered to add according to user requirements." (https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html) `BlockContainer` internally converts both IF and LIF into a unified `CubaLIFNode` representation to match Lava's native current-based LIF compartment model.

### 6.3 Reset semantics — hard reset only

The module source code enforces this as a hard constraint, not a soft recommendation:
```python
if sj_ms_neuron.v_reset != 0.:
    raise ValueError('lava only supports for v_reset == 0!')
```
found in `to_lava_neuron_param_dict()` for both `MultiStepIFNode` and `MultiStepLIFNode`. (https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html) This means **`lava_exchange` only supports reset-to-a-fixed-value (v_reset = 0), not reset-by-subtraction** — the same limitation identified in NIR's formal spec (§2.1). A network trained with SNN Toolbox's recommended reset-by-subtraction mode, or with QCFS's soft-reset IF neuron, **cannot be exported through `lava_exchange` as-is**; it would need to be retrained or converted to hard-reset semantics first, with the attendant accuracy risk the Rueckauer 2017 ablation quantifies (§1.1).

Additional hard constraints found directly in source:
```python
if isinstance(sj_ms_neuron, neuron.MultiStepLIFNode):
    if sj_ms_neuron.decay_input:
        raise ValueError('lava only supports for decay_input == False!')
```
and, in the synapse checks:
```python
if conv2d_nn.bias is not None:
    raise ValueError('lava does not support for convolutional synapse with bias!')
if fc.bias is not None:
    raise ValueError('lava does not support for dense synapse with bias!')
```
(https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html)

Weight quantization: `to_lava_block_dense`/`to_lava_block_conv` default to `quantize_to_8bit=True`, matching Lava/Loihi's native 8-bit weight precision.

### 6.4 Documented limitations (explicit, from source and docs)

- IF/LIF neurons only (no PLIF, no adaptive-threshold, no other SpikingJelly-native neuron types).
- Hard reset only (`v_reset` must be exactly 0).
- LIF must have `decay_input=False`.
- No bias terms in exported Conv2d/Linear layers.
- Only Loihi is targeted (via Lava); no other hardware backend is exposed through this module.
- SpikingJelly's broader "Interchange and Deployment" page also lists a separate **NIR exchange** (`nir_exchange.html`) and a **Lynxi deployment** path as parallel/alternative interoperability routes, distinct from `lava_exchange` and covering different hardware. (https://github.com/fangwei123456/spikingjelly README, "Interchange and Deployment" section)

This is directly relevant to the survey's central portability claim: even SpikingJelly, a framework explicitly designed for SNN research and equipped with a first-party Loihi export path, **cannot carry a reset-by-subtraction or otherwise soft-reset IF neuron to hardware without violating its own hard-coded assertion**. It is one more independent confirmation (alongside NIR's formal spec in §2.1 and the snnTorch export bug in §2.1) that **reset-by-subtraction is the single most consistently-dropped feature across every surveyed interoperability path to real hardware.**

---

## Source list

1. Rueckauer, Lungu, Hu, Pfeiffer, Liu (2017), "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image Classification," *Frontiers in Neuroscience* 11:682. https://doi.org/10.3389/fnins.2017.00682
2. SNN Toolbox documentation, introduction/guide. https://snntoolbox.readthedocs.io/en/latest/guide/intro.html
3. SNN Toolbox documentation, simulation API / backend list. https://snntoolbox.readthedocs.io/en/latest/api/simulation.html
4. SNN Toolbox GitHub repository. https://github.com/NeuromorphicProcessorProject/snn_toolbox
5. SNN Toolbox `intro.rst` (GUI-not-maintained note). https://github.com/NeuromorphicProcessorProject/snn_toolbox/blob/master/docs/source/guide/intro.rst
6. SNN Toolbox PyPI release history. https://pypi.org/project/snntoolbox
7. SNN Toolbox commit 047cedd (2022-08-13). https://github.com/NeuromorphicProcessorProject/snn_toolbox/commit/047cedd869adad7dc0b2cd09b8f8c796152f6742
8. SNN Toolbox commit 9d421f4 (2022-08-08). https://github.com/NeuromorphicProcessorProject/snn_toolbox/commit/9d421f43dd6cd14c2f204aae4c2a68b770e88e7d
9. deps.dev activity score for snn_toolbox. https://deps.dev/project/github/neuromorphicprocessorproject%2fsnn_toolbox
10. SNN Toolbox GitHub issue #75, Loihi loading breakage. https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues/75
11. Pedersen et al. (2024), "Neuromorphic intermediate representation…," *Nature Communications* 15:8122. https://doi.org/10.1038/s41467-024-52259-9
12. NIR open-access PMC copy. https://pmc.ncbi.nlm.nih.gov/articles/PMC11405706/
13. NIR arXiv preprint (2311.14641). https://arxiv.org/html/2311.14641
14. NIR primitives documentation. https://neuroir.org/docs/primitives/
15. NIR Table 2 (computational primitives). https://nature.com/articles/s41467-024-52259-9/tables/2
16. NIR supported frameworks/hardware matrix. https://neuroir.org/docs/support/
17. NIR porting-to-hardware guide. https://neuroir.org/docs/porting-nir/
18. NIR project GitHub. https://github.com/neuromorphs/NIR
19. NIR SpiNNaker2 import example (reset method options). https://neuroir.org/docs/examples/spinnaker2/import/
20. snnTorch PR #388 (missing v_reset on NIR export). https://github.com/jeshraghian/snntorch/pull/388
21. snnTorch PR #426 (reset-mechanism refactor, subtract vs zero confusion). https://github.com/jeshraghian/snntorch/pull/426
22. sc-neurocore NIR integration guide (third-party corroboration of reset-mode gap; non-authoritative). https://anulum.github.io/sc-neurocore/guides/nir_integration/
23. DeWolf, Jaworski, Eliasmith (2020), "Nengo and Low-Power AI Hardware for Robust, Embedded Neurorobotics," *Frontiers in Neurorobotics*. https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/
24. Rasmussen (2019), "NengoDL: Combining deep learning and neuromorphic modelling methods." https://ar5iv.labs.arxiv.org/html/1805.11144
25. NengoLoihi CIFAR-10 convnet example. https://www.nengo.ai/nengo-loihi/v1.0.0/examples/cifar10-convnet.html
26. Nengo Keras-to-Loihi tutorial. https://www.nengo.ai/nengo-examples/loihi/keras-to-loihi.html
27. Applied Brain Research press release, Nengo DL on Loihi 38× energy result. https://www.prnewswire.com/news-releases/applied-brain-research-inc-shows-nengo-spiking-real-time-ai-deep-learning-networks-on-intel-loihi-use-38x-less-energy-than-on-nvidia-quadro-k4000-gpu-300761243.html
28. DeWolf et al. (2023), "Neuromorphic control of a simulated 7-DOF arm using Loihi," *Neuromorphic Computing and Engineering* 3:014007. https://doi.org/10.1088/2634-4386/acb286
29. Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild (2022), "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi," *ACM JETC* 18(2). https://doi.org/10.1145/3501770 / arXiv version https://arxiv.org/html/2101.04261
30. Lenz, Orchard, Sheik (2023), "Ultra-low-power Image Classification on Neuromorphic Hardware" (Quartz), arXiv:2309.16795. https://doi.org/10.48550/arxiv.2309.16795
31. Quartz-on-Loihi code repository. https://github.com/biphasic/Quartz-on-Loihi
32. Lava-DL NetX documentation. https://lava-nc.org/lava-lib-dl/netx/netx.html
33. Lava-DL NetX README (HDF5 schema). https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/netx/README.md
34. Lava Deep Learning overview page. https://lava-nc.org/dl.html
35. Lava-DL YOLO-KP Loihi-2 tutorial. https://github.com/lava-nc/lava-dl/blob/main/tutorials/lava/lib/dl/netx/yolo_kp/run.ipynb
36. Lava-DL Oxford NetX tutorial (Loihi 2 execution check). https://github.com/lava-nc/lava-dl/blob/main/tutorials/lava/lib/dl/netx/oxford/run.ipynb
37. Rockpool Xylo quick-start deployment guide. https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html
38. Rockpool XyloAudio 3 deployment tutorial (XyloSamna/XyloMonitor). https://rockpool.ai/devices/xylo-a3/Using_XyloSamna_and_XyloMonitor.html
39. Rockpool quantize_methods documentation. https://rockpool.ai/reference/_autosummary/transform.quantize_methods.channel_quantize.html
40. Zhou, Muir (2024), "Deployment Pipeline from Rockpool to Xylo for Edge Computing," arXiv:2412.11047. https://doi.org/10.48550/arxiv.2412.11047
41. Sinabs NIR-to-Speck deployment tutorial. https://sinabs.readthedocs.io/main/tutorials/nir_to_speck.html
42. Sinabs Speck "The Basics" deployment guide. https://sinabs.readthedocs.io/main/speck/the_basics.html
43. Sinabs Speck overview. https://sinabs.readthedocs.io/main/speck/overview.html
44. SynSense Speck Dev Kit Manual (2025.12). https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf
45. onnx-snn project (incomplete round-trip conversion). https://github.com/neurom-iot/onnx-snn
46. snnTorch export_nir documentation. https://snntorch.readthedocs.io/en/latest/snntorch.export_nir.html
47. APEX: A Dual-Sparsity Accelerator for Precise and Efficient SNN Inference (PASC-IF / QCFS-derived, simulated accelerator), arXiv:2608.19046. https://arxiv.org/html/2608.19046
48. SpikingJelly `lava_exchange` tutorial (English). https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html
49. SpikingJelly `lava_exchange` module source (v_reset==0 hard constraint). https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html
50. SpikingJelly GitHub README (Interchange and Deployment section: NIR / Lava / Lynxi). https://github.com/fangwei123456/spikingjelly
