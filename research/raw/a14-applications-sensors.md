# A14 — Real Neuromorphic Applications and Event-Based Sensing: What Actually Consumes the Events

Research pass date: 2026-09-15. Primary tool: Exa web search/fetch. Scope: event cameras/DVS hardware, the compute platform behind published event-vision applications, frame-reconstruction prevalence, genuine end-to-end neuromorphic (sensor→spiking chip) systems, non-vision neuromorphic applications, measured latency/energy figures, and commercial deployment status.

**Classification key** (applied throughout): **E1** = physical silicon, latency and/or energy measured. **E2** = physical silicon, accuracy only (no latency/energy). **E5** = software/GPU simulation only, no physical neuromorphic silicon. Distinguish peer-reviewed measured results from demos/press releases explicitly.

---

## 1. Event cameras / DVS: what they actually output and how they connect

All commercial event sensors output an asynchronous stream of **(x, y, timestamp, polarity)** tuples — Address-Event Representation (AER) at the wire-protocol level, or a proprietary packed format at the interface level. None of them output spikes destined for a spiking neuron substrate by default; they output an *address-event log*, which is a necessary but not sufficient condition for "neuromorphic" downstream processing.

- **iniVation DAVIS346**: 346×260 px, combines a DVS array with a global-shutter APS frame sensor on one die. Event output: <1 µs latency, 1 µs timestamp resolution, up to 12M events/s, 120 dB dynamic range. Interfaces: **USB 3.0** (data+power, primary) and an optional **raw AER connector** (16-pin, 2.54 mm, 3.3 V, four-phase asynchronous handshake — REQ/ACK bundled-async protocol) for direct FPGA/neuromorphic-hardware interfacing. The AER connector cannot carry frames or IMU data; USB must always be connected for power/config. [inivation.com/DAVIS346]
- **iniVation DVXplorer**: 640×480, built on a **Samsung DVS Gen3** sensor die, up to 165M events/s, <1 ms typical latency, 200 µs timestamp resolution, 90–110 dB dynamic range. Interface: **USB 3.0** only (no raw AER breakout on the standard DVXplorer); supports multi-camera sync via daisy-chain. [inivation.com/DVXplorer]
- **Prophesee/Sony IMX636** (EVK4 HD, 1280×720, the sensor behind most recent automotive/robotics event papers): outputs (x, y, t, polarity) events in proprietary **EVT2.1 (64-bit)** or **EVT3.0 (16-bit compressed)** stream formats. Physical interface at the die: **MIPI CSI-2 (1 or 2 lane) or SLVS**; the EVK4 evaluation camera bridges MIPI→**USB 3.0 (USB-C)** internally via a Cypress CX3 controller. Pixel latency <100 µs at 1000 lux, <1000 µs at 5 lux, max throughput 3 Gevents/s, standby 5 mW / max 205 mW. [prophesee.ai IMX636 product brief; EVK4 camera manual]
- **Prophesee GenX320**: 320×320, "world's smallest and most power-efficient" event sensor, aimed explicitly at embedded/AIoT: 1-lane MIPI D-PHY *or* 8-bit parallel/CMOS-Parallel-Interface (CPI) output, I2C control, ultra-low-power mode 36 µW, active 3 mW, <150 µs latency @1klux. Prophesee's own documentation states the **CPI/AER output path "is mainly destined for integration with neuromorphic systems"** — implying the default MIPI path is not. Reference kits exist for **Raspberry Pi 5** (MIPI CSI-2 direct connector) and an **STM32F746G Discovery Kit** adapter via STM32 DCMI (parallel camera interface) — i.e., the vendor's own reference designs plug the sensor straight into a Raspberry Pi or an STM32 microcontroller. [prophesee.ai GenX320 product catalogue; Metavision docs encoding formats]
- **Samsung DVS Gen3**: not independently specified in this pass beyond its use inside the DVXplorer (above). NOT FOUND (standalone datasheet not retrieved in this search pass).
- **CeleX**: NOT FOUND — no CeleX-specific specification was retrieved in this research pass; excluded rather than reconstructed from memory.

**Take-away for Section 1**: every major commercial event sensor's *primary, production* interface is USB 3.0 or MIPI CSI-2 — i.e., the same interfaces used by conventional CMOS image sensors and consumed by conventional hosts (PCs, SoCs, MCUs). A raw AER pin header exists on some cameras (DAVIS346, GenX320-CPI) explicitly *for* neuromorphic hardware integration, but it is a secondary, low-bandwidth option, and the vendor's own flagship reference designs (Raspberry Pi 5, Jetson Orin NX, STM32 Discovery kits) target conventional processors, not spiking chips.

---

## 2. What actually processes the events in published application work

Surveyed across optical flow, object detection/tracking, automotive, SLAM/VIO, high-speed robotics/drones, and gesture recognition. Below, each example is tagged with its compute category.

### (a) GPU / workstation
- E-RAFT, RAFT-spline / bflow (dense optical flow, DSEC/MVSEC benchmarks) — trained and evaluated on CUDA GPUs, no embedded or neuromorphic deployment. [uzh-rpg/E-RAFT; uzh-rpg/bflow]
- EvRT-DETR (event object detection, Gen1/Gen4 automotive datasets) — PyTorch/CUDA Docker container, explicitly notes the pipeline is "CPU-bound" for data loading even with a GPU doing inference. [realtime-intelligence/evrt-detr]
- rt_of_low_high_res_event_cameras (real-time-labeled optical flow) — requires CUDA + the `optical-flow-filter` GPU library; "real-time" here means GPU real-time, not embedded. [heudiasyc GitHub]
- Prophesee's own Metavision SDK detection/tracking tutorial defaults to `DEVICE = "cpu"` with an explicit CUDA fallback — i.e., Prophesee's reference automotive detection pipeline is a PyTorch/TorchScript model run on a workstation CPU or GPU. [docs.prophesee.ai detection_and_tracking tutorial]
- IBM's "Neuromorphic Optical Flow" work (CVPR 2023) explicitly frames the problem as needing model simplification because full accuracy optical-flow networks are "prohibitive for application at the edge or in robots" — evidence that the default/baseline compute target for these networks is a GPU. [research.ibm.com]

### (b) Embedded CPU / Raspberry Pi / Jetson
- **High-Speed Altitude Regulation with Neuromorphic Camera** (fixed-wing UAV, 21M events/s at 15 m/s): optical flow computed on a **Raspberry Pi 5**, with an optimized Lucas-Kanade variant specifically engineered because "large event rates ... challenge real-time processing on lightweight embedded platforms." [doi.org/10.1002/aisy.202500904]
- **AERO-VIS** (first purely event-based inertial SLAM with closed-loop UAV control, ETH Zürich/TUM 2026): runs on an **NVIDIA Jetson Orin NX** onboard a custom UAV with two Prophesee EVK4 cameras; TensorRT-compiled CUDA-graph inference. [arxiv 2605.07885; ethz-mrl.github.io/AERO-VIS]
- **EV-Catcher** (ping-pong ball catching, 13 m/s, 81% success): perception + control on an **NVIDIA Jetson NX** (384-core Volta GPU), chosen specifically for its sub-1 ms GPIO latency; the paper notes only single-shot inference is possible on this "compute-constrained embedded platform." [arxiv 2304.07200]
- **Event-based Agile Object Catching with a Quadrupedal Robot** (ANYmal C, 15 m/s, 83% success): detection at 100 Hz on an **NVIDIA Jetson Orin** dev kit; catching policy on the robot's onboard Intel i7 PC. [rpg.ifi.uzh.ch ICRA23_Forrai]
- RidgeRun's GenX320 developer guide documents **two** reference embedded paths: Raspberry Pi 5 and Jetson Orin NX — no neuromorphic-chip path is offered as a standard integration. [ridgerun.com]
- `ole_ros` (on-device event learning) targets Jetson Orin NX via `jetson-containers`. [tudelft/ole_ros]

### (c) Conventional MCU
- Prophesee's own GenX320 + **STM32F746G Discovery Kit** reference design (STM32 DCMI parallel camera interface, demonstration firmware in flash) — a bare-metal Cortex-M7 MCU consuming raw events directly, with **no spiking computation** in the reference firmware (it visualizes events on an LCD). [prophesee.ai product catalogue]
- FPGA-drone obstacle avoidance (below) also uses a quad-core **ARM Cortex-A53** (APU) plus a real-time **Cortex-R5** (RPU) for orchestration and decision logic around the FPGA accelerator. [CVPR2025W EventVision, Bonazzi et al.]

### (d) FPGA (non-spiking CNN/algorithm accelerators)
- **Kria-Prophesee-Event-VitisAI**: runs YOLOv4-tiny/YOLOv7(-tiny) object detectors on an AMD/Xilinx **KV260 Kria board using the Vitis-AI DPU** — a conventional systolic-array CNN accelerator, not a spiking substrate — fed by the Prophesee IMX636 (CCAM5) sensor. [github.com/LogicTronixInc/Kria-Prophesee-Event-VitisAI]
- **Towards Low-Latency Event-based Obstacle Avoidance on a FPGA-Drone** (CVPR-W 2025): event aggregation into 80×80 frames on FPGA fabric, inference on the AMD Xilinx **DPU** (`dpuczdx8g`), a commercial conventional-CNN inference module — end-to-end 2.14 ms measured latency (event aggregation 1 ms + inference 0.94 ms). This is a **conventional CNN accelerator**, explicitly not spiking. [openaccess.thecvf.com CVPR2025W]
- **TrinitySLAM** (event-image fusion SLAM for drones): Xilinx **Zynq UltraScale+** heterogeneous SoC, hardware/software co-accelerated pipeline; 28% accuracy gain, half the latency, 1.2× lower energy vs. the best prior heterogeneous accelerator. [doi.org/10.1145/3696420]
- **EventBoost** (event-fusion drone localization): Zynq SoC accelerator, 24.33% accuracy gain, **30 ms** latency on a resource-constrained platform. [doi.org/10.1109/infocom52122.2024.10621101]
- **FRME** (FPGA rotational-motion estimator for SLAM): 14.17× speedup vs. SOTA CPU/GPU baselines, algorithmic (event-warping / contrast maximization) FPGA accelerator, not a neural/spiking design. [doi.org/10.1109/icfpt67023.2025.00025]

### (e) Actual spiking/neuromorphic chip
- **IBM TrueNorth + DVS128**, DvsGesture (Amir et al., CVPR 2017) — the canonical "genuine end-to-end" example; see §4.
- **Intel Loihi + DVS**, gesture recognition (Massa et al. 2020) — see §4 for the important caveat that events are pre-converted to frames before the DNN→SNN conversion step.
- **SynSense Speck** (DVS + DYNAP-CNN spiking CNN co-integrated on one die) — gesture recognition and (via GelSight optical-tactile events) texture recognition; see §4.
- **SpiNNaker + silicon retina (DVS)** — goalkeeper robot (Cheng & Nikolić 2020), optic-flow corridor-centering and stereopsis robot (Galluppi et al. 2014), and hexapod terrain/target adaptation fusing DVS + force sensors (López Osorio et al. 2024); see §5/§6.

### Rough count (this survey pass, not exhaustive)
Across the ~20 application papers/products directly reviewed here: **GPU/workstation majority for algorithm development and training** (essentially all learning-based methods), **embedded CPU/Jetson/RPi dominant for "real-time" onboard robotics demos** (5 of 6 high-speed robotics/drone/SLAM papers surveyed), **FPGA a distinct and fairly common third category especially for drone/SLAM acceleration** (5 papers), and **genuine spiking/neuromorphic silicon a small minority**, concentrated almost entirely in gesture recognition and closed-loop simple-robot demonstrations rather than SLAM, optical flow, automotive detection, or high-speed catching/robotics. This is consistent with, and quantitatively supports, the author's observation.

---

## 3. Frame reconstruction vs. native/spiking event processing: how common is it?

This is **very common** and is stated directly in recent literature:

> "We observe that most event-based deep learning pipelines convert asynchronous events into dense representations (particularly voxel grids) before neural network processing." — V2V: Scaling Event-Based Vision through Efficient Video-to-Voxel Simulation (NeurIPS 2025). [proceedings.neurips.cc/.../b14cf0a01f7a8b9cd3e365e40f910272]

The "Deep Learning for Event-based Vision" survey (arXiv 2302.08890, IEEE TPAMI) taxonomizes event representations into six families — **image-based, surface-based, learning-based, voxel-based, graph-based, spike-based** — and of these, only the last (spike-based) is native to spiking hardware; the other five all collapse the asynchronous stream into a dense tensor and hand it to a conventional CNN/Transformer. The same survey's own summary table lists dozens of representative works, and the overwhelming majority (image, surface, voxel, learning-based) target conventional dense backbones.

The "Systematic Survey on Event Camera Representation Learning" (2026) frames the field as split between "dense-based representations... to leverage mature RGB backbones" and "sparse-based representations... to preserve fine-grained temporal dynamics" — and explicitly notes dense/voxel formats "remain widely adopted when spatial alignment and pixel-level prediction are required" because of compatibility with mature convolutional/Transformer backbones.

Concretely in this pass:
- Prophesee's own production object-detection/tracking pipeline (automotive pedestrian/vehicle detection) explicitly accumulates events into a frame buffer at a fixed accumulation time before calling the neural network (`cdproc.process_events` → `object_detector.process`), i.e., **event camera → frame reconstruction → conventional CNN (TorchScript, CPU/CUDA)**. [docs.prophesee.ai]
- Prophesee's own `ev-ultralytics` (YOLO fork) trains YOLO detectors on **event histograms**, explicitly described as substituting for RGB frames. [github.com/prophesee-ai/ev-ultralytics]
- The pedestrian-detection comparison paper (Prophesee 2025) frames its central research question as *video-frame CNNs vs. asynchronous sparse CNNs* — i.e., frame reconstruction is one of exactly two mainstream options, and remains the baseline against which "native" processing is benchmarked. [prophesee.ai/2025/02/07]
- Loihi DVS-gesture (Massa et al. 2020, §4) explicitly states: "we cannot train a DNN on the event-series coming from the DVS camera... we first need to collect the events into frames, and then train the DNN." The Loihi deployment is a DNN→SNN *conversion* of a frame-trained network, not a spiking network trained natively on events. This means even a "Loihi paper" can be frame-reconstruction-under-the-hood before conversion.
- Automotive datasets (Prophesee Gen1, 1-Megapixel/Gen4) ship pre-converted to frame/histogram representations for standard mAP-style evaluation pipelines (COCO API). [prophesee-ai/prophesee-automotive-dataset-toolbox]

**Quantitative honesty**: no single peer-reviewed study surveyed here reports an exact percentage of "event papers that reconstruct frames." The above is qualitative but consistent and repeated across four independent survey/vendor sources: frame/voxel-grid reconstruction feeding a conventional (non-spiking) network is described as the **dominant, default approach** in the event-vision deep-learning literature, with native asynchronous/spike-domain processing as the minority, specialized alternative.

---

## 4. Genuine end-to-end neuromorphic applications (sensor → spiking chip, no frame reconstruction)

- **SynSense Speck + gesture recognition** [E1, vendor datasheet, not independently peer-reviewed in this pass]: Speck is "a fully event-driven neuromorphic vision SoC" integrating a **DVS pixel array and the DYNAP-CNN spiking-convolutional core on one die**, up to 320k neurons. Vendor-measured: **<5 mW power** (typical application), **<50 ms response latency** for gesture recognition, claimed "100–1000× lower than GPU solutions," and an AA battery lasting up to 100 days. No frame reconstruction — events go directly into the on-chip sCNN. [synsense.ai/wp-content/.../Speck-Gesture-recognition.pdf] — treat as **vendor datasheet, not peer-reviewed**.
- **GelNeuro** (2026, tactile not vision, but architecturally identical: sensor → on-chip DVS-style events → Speck2f DYNAP-CNN sCNN) [E1, peer-reviewed]: a GelSight optical-tactile front end generates DVS-like marker-motion events consumed directly by a **Speck2f** SoC running a spiking CNN, 15-class texture recognition. Hardware-in-the-loop on the physical chip: **96.3% accuracy, 80 ms inference window, 19.6 mW board-level active power** — "over three orders of magnitude lower than conventional CPU/GPU baselines on the same benchmark." [pubdb.com/paper/2607.05241]
- **IBM TrueNorth + DVS128, DvsGesture** (Amir et al., CVPR 2017) [E1, peer-reviewed, landmark]: "the first gesture recognition system implemented end-to-end on event-based hardware" — live DVS event stream fed directly into a TrueNorth CNN (1M spiking neurons). Measured: **105 ms gesture-onset latency, <200 mW power, 96.5% accuracy** on 11 gestures / 29 subjects. This is the strongest E1 example of true sensor-to-spiking-chip processing with no host-side frame accumulation in the deployed path. [CVPR 2017; research.ibm.com]
- **DYNAP-SE + iCub closed-loop motor control** [E1, peer-reviewed]: mixed-signal analog neuromorphic chip implementing a spiking "P controller" that reads encoder feedback and drives the iCub humanoid's head-yaw joint in closed loop, characterized by step response and target-pursuit tasks. [arxiv 2009.09081]
- **DYNAP-SE tactile localization** (Ortone et al. 2026) [E1, peer-reviewed]: FBG-based e-skin → SNN mimicking early somatosensory processing → implemented on **DYNAP-SE** (4096 adaptive-exponential analog neurons). Measured: **5.33 ± 0.15 mm localization error (only 8% worse than software), 185 µW median inference power, 8.7 µW resting power**; the paper explicitly contrasts this against an estimated ~mW-class ARM implementation of the same dynamics.
- **SpiNNaker goalkeeper robot** (Cheng & Nikolić 2020) [E1, peer-reviewed]: DVS (AER camera) → SNN on SpiNNaker → servo motor, fully closed-loop, disconnected from any PC. Measured: **6.5 ms response latency, 85% interception accuracy (balls up to 1 m/s), 7.15 W max system power**.

**Caveat worth flagging for the thesis**: several "Loihi + DVS" papers (e.g., Massa et al. 2020) are *not* fully native end-to-end pipelines — they pre-accumulate events into frames to train a conventional DNN, then convert that DNN to an SNN for Loihi deployment. The DVS→frame step happens off-chip in these pipelines; only inference happens natively on spiking hardware. This is architecturally different from TrueNorth/Speck/DYNAP examples above, where no frame ever exists.

---

## 5. Non-vision neuromorphic applications reaching physical hardware

| Domain | System | Physical chip | Measured result | Class |
|---|---|---|---|---|
| Keyword spotting | 2-layer NN keyword spotter | Loihi (research) | Energy-per-inference lower than CPU/GPU/Jetson TX1/Movidius NCS at equivalent accuracy; advantage grows with network size | E1 |
| Keyword spotting | Spiking-DCNN, 23 KB | **BrainChip Akida** (commercial) | **0.72 ms latency, >1300 keywords/s throughput**; on-chip few-shot learning: 1.5 ms latency, 41 mW, 62 µJ | E1 |
| Image classification | SNN on NPU fabric | Akida | ~41 ms latency, 24 FPS, 215 mW, 9 mJ | E1 |
| Video object detection | SNN | Akida | ~160 ms latency, 6 FPS, 78 mW, 13 mJ | E1 |
| Olfaction | Odor-learning algorithm modeled on mammalian olfactory bulb | Loihi (research) | **92% accuracy** single-shot (vs. 3000 samples/class needed by a DNN autoencoder for parity); **<3 ms, <1 mJ** per classification, scaled 20–128 cores | E1 (but see caveat below) |
| Tactile / e-skin | Fiber-Bragg-grating e-skin + SNN | DYNAP-SE | 5.33 mm localization error, 185 µW inference, 8.7 µW idle | E1 |
| Tactile / e-skin | GelSight optical-tactile + sCNN | Speck2f | 96.3% accuracy (15-class texture), 80 ms window, 19.6 mW | E1 |
| EMG gesture classification | RSNN, DEXAT neurons | Loihi (Nahuku 32) | 90% accuracy; **983×/19× energy/latency gain vs. GPU** (batch=50); 0.37 mJ/inference | E1 |
| EMG gesture classification | SNN, 12 gestures, NinaPro DB5 | Loihi (Kapoho Bay) | 74% accuracy, **5.7 ms latency, 41 mW** | E1 |
| EMG + DVS gesture fusion (sign language) | SNN, tri-modal | Loihi + ODIN/MorphIC | Accuracy on par with GPU baseline; **30–600× better energy-delay product**, 20–40% slower inference than GPU | E1 |
| EEG seizure prediction | Graded SNN (GSNN) | Loihi 2 | **99.14% accuracy**, 21.6 segments/s throughput, **25.1 mJ/input** | E1 |
| EEG motor-imagery decoding | SNN | Loihi (via NxSDK/Kapoho Bay) | "95% more energy-efficient than DNNs at similar accuracy" (claim from repo README; full paper not independently re-verified in this pass) | E1 (self-reported) |
| Radar (automotive, real sensor) | SNN, FFT + non-coherent integration + CFAR | **Loihi 2** (vehicle-mounted) | First Loihi-2 pipeline on real vehicle-mounted radar; real-time on-chip execution; latency/throughput/power characterized across 8–40 channels; ~W-scale dynamic power | E1 |
| Radar (simulated data) | Spiking neural resonators + spiking CFAR | Loihi 2 (single chip) | Idle power measured, full-activation power **2.62 W**, activity-gated sparsity cuts energy **~60%** | E1 |
| LiDAR object detection (KITTI) | Spiking encoder-decoder BEV detector | **Estimate only** — "when ported onto neuromorphic hardware" (25×) / "estimated 43× on dedicated neuromorphic hardware" | Real measurement is GPU-based (3.33× synaptic-energy reduction under "conservative loop-based operation"); neuromorphic-hardware numbers are projections, not chip measurements | **E5** (mislabel risk — read carefully, headline "25×"/"43×" figures are *not* physical-silicon measurements) |
| Robot locomotion (hexapod CPG) | Spiking central pattern generator | SpiNNaker (SpiNN-3, 4 chips) | 23 ms worst-case gait-transition delay, ~3.5 µs added by FPGA glue logic | E1 |
| Robot goalkeeper | SNN + DVS | SpiNNaker | 6.5 ms response latency, 85% accuracy, 7.15 W | E1 |
| Robot terrain/target adaptation | SNN fusing FSR + DVS | SpiNNaker | Functional adaptation demonstrated; no absolute latency/energy figure extracted in this pass | E2 |
| Closed-loop joint control | Spiking P-controller | DYNAP-SE (iCub) | Step-response and target-pursuit characterized; no absolute power figure extracted in this pass | E2 |

**Olfaction caveat**: a 2023 replication study (Dennler, van Schaik & Schmuker, arXiv 2309.11555) found the Imam & Cleland Loihi olfaction dataset suffers from **sensor drift and non-randomized measurement protocol**, and that the claimed generalization does not hold under a proper train/test split with separate repetitions — a simple 8-line hash-table baseline matches or beats the Loihi network's accuracy. This does not invalidate the *hardware* latency/energy measurement, but it substantially undercuts the algorithmic/scientific claim (advertised as a landmark neuromorphic result), and should be cited in the thesis as a cautionary example of how a striking E1-labeled result can rest on a flawed benchmark.

---

## 6. Latency / energy numbers actually measured in applications (consolidated)

All figures below are **measured on physical silicon** unless marked otherwise; measurement conditions given where available.

- TrueNorth + DVS128 gesture recognition: **105 ms** gesture-onset latency, **<200 mW**, 96.5% accuracy (live camera feed, real-time). [Amir et al. 2017]
- Loihi DVS gesture recognition (frame-preprocessed, then converted): **11.43 ms** per-frame classification + 150 ms preprocessing = 161.4 ms total, 6.24 FPS effective throughput, 89.64% accuracy, 37 cores used. [Massa et al. 2020]
- Speck (vendor): **<5 mW**, **<50 ms** response, up to 320k neurons on-chip. [SynSense datasheet — not independently peer-reviewed]
- GelNeuro (Speck2f): **96.3%** accuracy, **80 ms** window, **19.6 mW** board power. [peer-reviewed, 2026]
- DYNAP-SE tactile: **185 µW** median inference power, **8.7 µW** resting power, 5.33 mm localization error.
- Loihi EMG (Bezugam et al. 2022/2023): **0.37 mJ/inference**, 983×/19× energy/latency vs. GPU at batch=1; ~3363×/4× vs. CPU.
- Loihi EMG (Donati/Vitale et al. 2022, Kapoho Bay): **5.7 ms latency, 41 mW**, 74% accuracy.
- Loihi olfaction: **<3 ms, <1 mJ** per classification, 92% accuracy, scaled 20–128 cores.
- Loihi 2 EEG seizure prediction: **25.104 mJ/input**, 21.6 inputs/s throughput, 99.14% accuracy.
- Loihi 2 automotive radar (real vehicle sensor): dynamic power scaling from low single-digit W up to tens of W across 8→40 channels; "average overhead of approximately [X] per channel" (exact numeric value not extracted cleanly in text scrape — flagged for follow-up); latency stays below real-time budget across configurations. [IOP 2026]
- Loihi 2 radar resonators (simulated data): idle power measured; **2.62 W** at full activation, **~60% energy reduction** via activity-gated sparsity.
- SpiNNaker goalkeeper: **6.5 ms** response latency, **7.15 W** max system power, 85% accuracy, balls up to 1 m/s.
- SpiNNaker hexapod CPG: **23 ms** worst-case gait-change convergence delay.
- FPGA obstacle-avoidance drone (non-spiking DPU): **2.14 ms** end-to-end latency (1 ms event aggregation + 0.94 ms DPU inference + overhead), vs. an estimated 21.14 ms for an RGB baseline. [not spiking — included for latency-scale comparison]
- Akida (commodity neuromorphic processor) across four workloads: image classification 41 ms/215 mW/9 mJ; video detection 160 ms/78 mW/13 mJ; keyword spotting 0.72 ms/>1300 KPS; on-chip learning 1.5 ms/41 mW/62 µJ.

---

## 7. Commercial deployments — honest assessment

**Is any neuromorphic chip in a shipping consumer/commercial product today?** The evidence is mixed and mostly **"available for integration / early production," not "inside a shipped mass-market consumer product."**

- **BrainChip Akida**: AKD1000 has been sellable since ~2022–2024 as PCIe/M.2 cards and a Raspberry-Pi-based "Edge AI Box" ($799, pre-order Feb 2024) — this is **commercially available hardware**, but targeted at developers/integrators, not embedded inside a named shipping consumer device. The newer **AKD1500** (Nov 2025 announcement) is reported (June 2026 press release) as in **"commercial availability and initial production shipments"** to defense and wearable customers, still undergoing "extreme environmental qualification" — i.e., real but early-stage/low-volume industrial-defense shipments, not consumer retail. Frontgrade Gaisler has **licensed** (not yet shipped) Akida IP for space-grade SoCs (Dec 2024 announcement) — a design win, not a flown product. All of the above should be read with appropriate skepticism: these are vendor press releases, not independently audited shipment volumes.
- **SynSense Speck / DYNAP-CNN**: sold as evaluation modules/dev kits; no evidence found in this pass of Speck being embedded in a named mass-market shipping product (only application demonstrators such as GelNeuro).
- **Prophesee event sensors (IMX636/GenX320) in smartphones**: Prophesee + Sony + Qualcomm jointly announced (Feb 2023) and declared "production-ready" (Feb 2024) a **Metavision Image Deblur** module for Snapdragon 8 Gen 3 phones. As of the most recent article retrieved (PetaPixel, March 2024): **no confirmed shipping phone model** had been named — "it's unclear what devices, if any, might have Prophesee's tech included... no one is saying." This is the clearest example in this research pass of the gap between "production-ready" press language and an actual verified shipping consumer product — **treat as NOT CONFIRMED shipping as of the sources retrieved.**
- **Prophesee event sensors in commercial (non-phone) products**: **Xperi** is reported to already have a **driver-monitoring system** shipping/deployed using Prophesee's previous-generation sensor (EE Times, Oct 2023) — this is the strongest "real commercial deployment" evidence found for an *event sensor* (not a spiking chip) in this pass, though it is trade-press reporting, not independently audited. **YunX** (Taiwanese OEM) was reported planning a GenX320-based fall-detection product for the following year (i.e., a near-term plan, not yet confirmed shipped). **Zinn Labs** has an event-based eye tracker for AR/VR in prototype/pre-mass-production stage with GenX320.
- **GrAI Matter Labs (NeuronFlow/GrAI VIP)**: chip demonstrated (PilotNet steering-angle inference, <50 mW, 20× latency improvement from sparsity), positioned for automotive/robotics edge AI; no evidence of mass shipment found in this pass.

**Bottom line for Section 7**: the *sensor* side of event-based vision (Prophesee/Sony IMX636-family chips) has plausible, partially-confirmed commercial deployment (Xperi driver monitoring; smartphone deblur "production-ready" but unconfirmed as shipped). The *processor* side — actual spiking/neuromorphic compute chips (Loihi, Speck, Akida, GrAI) — remains overwhelmingly in the evaluation-kit / early-production / design-win stage, not verified high-volume shipping products, as of the sources retrieved in this pass (through mid-2026).

---

## 8. "Is the event processor actually neuromorphic?" — the critical distinction

This is the crux of the survey author's observation, and the literature substantiates it directly. Two clearly distinguishable categories of "event processor" exist, and they get conflated in marketing and even in some paper titles:

### Category A — genuinely spiking / IF-or-LIF-based, event-driven at the neuron level
- **Intel Loihi / Loihi 2**: explicit LIF-type neuron compartments, asynchronous mesh, microcode-programmable neuron dynamics, on-chip learning engine. Genuinely spiking.
- **IBM TrueNorth**: 1M digital spiking neurons, deterministic leaky-integrate-and-fire, fully event-driven crossbar.
- **SynSense Speck / DYNAP-CNN**: "fully event-driven neuromorphic vision SoC," asynchronous digital circuit implementing spiking convolutional layers with LIF-like dynamics, co-integrated with the DVS pixel array on one die.
- **SynSense/ETH DYNAP-SE**: mixed-signal analog circuits directly implementing neuronal/synaptic differential equations in transistor physics (adaptive-exponential neurons) — arguably the *most* biologically faithful "genuinely spiking" hardware in this survey.
- **SpiNNaker**: general-purpose ARM cores running numerically-integrated LIF (or other) neuron models in software, but with an event-driven (spike-packet) communication fabric between cores — spiking at the *model* level, though not at the *circuit* level (it is a digital multicore, not dedicated spiking silicon).

### Category B — "event-driven" or "neuromorphic-branded" but NOT spiking/IF at the neuron level
- **GrAI Matter Labs NeuronFlow (GrAIOne / GrAI VIP)**: an EE Times interview with the company is explicit — *"While GrAI Matter describes its technology as 'brain-inspired,' its NeuronFlow technology is based on a digital SoC architecture optimized for deep learning acceleration (**no spiking networks here**)."* The core primitive, "SpArNet," performs **change-based/delta quantization of a conventional ANN's activations** ("valued events... not simple spikes as usual in neuromorphic systems," per the architecture paper itself) — i.e., it exploits *temporal sparsity* (skip unchanged pixels/activations between frames) inside an otherwise conventional MAC-based dataflow accelerator. This is architecturally and mathematically a **sparse conventional CNN accelerator**, not a spiking/rate-coded neuromorphic chip, despite "neuromorphic" branding in its own papers and press.
- **AMD/Xilinx DPU (Vitis AI) fed by an event sensor** (e.g., the Kria-Prophesee-Event-VitisAI project, and the FPGA-drone obstacle-avoidance DPU): a commercial, general-purpose **systolic-array CNN inference engine** running YOLO-family detectors — zero spiking neurons, zero IF dynamics. The "event" part is confined entirely to the sensor and the frame-accumulation front end; from the DPU's perspective it is an ordinary CNN accelerator consuming ordinary frames.
- **BrainChip Akida**: markets itself as "the world's first commercial producer of ... event-based, neuromorphic AI." Its CNN2SNN conversion path and "event" semantics (spike counts / multi-bit activations transmitted only on change) are architecturally closer to GrAI's delta-quantization scheme than to true binary-spike LIF hardware — worth flagging as a borderline case rather than a clean member of either category; Akida's own technical materials describe multi-bit "events," and its newer TENNs product line is explicitly **state-space-model** based, further diluting the "spiking" claim. Treat vendor "neuromorphic" self-labeling with skepticism unless the neuron model (LIF/IF, binary spike output) is independently confirmed.

### Why this distinction matters for the thesis
The author's observation — that published applications overwhelmingly run on "conventional MCU, Raspberry Pi, or a non-IF event processor" — is validated on **two independent axes**:
1. Most application papers route the event stream through a conventional CPU/GPU/FPGA-CNN pipeline after a frame/voxel reconstruction step (§3), never touching any chip marketed as neuromorphic.
2. Even among the processors that *are* marketed as "neuromorphic" or "event-driven," a meaningful fraction (GrAI NeuronFlow explicitly, Akida arguably) achieve their efficiency through **temporal/data sparsity exploited by a conventional dataflow architecture**, not through IF/LIF spiking neuron dynamics or rate/temporal coding. This is a legitimate and useful efficiency technique, but it is not the same computational primitive as Loihi/TrueNorth/Speck/DYNAP, and conflating the two overstates how much of the "neuromorphic applications" literature involves genuinely spiking computation.

---

## Summary table: compute-platform categorization with representative examples

| Category | Representative examples | Approx. share of surveyed papers |
|---|---|---|
| (a) GPU/workstation | E-RAFT, bflow, EvRT-DETR, Prophesee detection SDK default, IBM neuromorphic-optical-flow baseline | Majority for algorithm development/training |
| (b) Embedded CPU/RPi/Jetson | Altitude-regulation UAV (RPi 5), AERO-VIS SLAM (Jetson Orin NX), EV-Catcher (Jetson NX), quadruped ball-catching (Jetson Orin), GenX320 RPi5/Jetson reference designs | Dominant for "real-time onboard" robotics demos |
| (c) Conventional MCU | GenX320 + STM32F746G Discovery Kit reference design | Present, vendor reference designs |
| (d) FPGA (non-spiking) | Kria-Prophesee VitisAI (Xilinx DPU), FPGA obstacle-avoidance drone (Xilinx DPU), TrinitySLAM/EventBoost (Zynq), FRME | Common third category, esp. SLAM/drones |
| (e) Actual neuromorphic chip | TrueNorth+DVS128 gesture (E1), Loihi+DVS gesture (E1, frame-preprocessed), Speck/DYNAP-CNN gesture & GelNeuro tactile (E1), SpiNNaker goalkeeper/hexapod (E1), DYNAP-SE tactile/motor control (E1) | Small minority, concentrated in gesture recognition and simple closed-loop robot control; essentially absent from SLAM, optical flow, automotive detection, high-speed catching |

---

## Source list

1. Prophesee Metavision SDK — Data Encoding Formats: https://docs.prophesee.ai/stable/data/encoding_formats/index.html
2. iniVation DAVIS346 AER hardware docs: https://docs.inivation.com/hardware/current-products/davis346-aer.html
3. Prophesee IMX636 Product Brief (PDF): https://www.prophesee.ai/wp-content/uploads/2024/05/IMX636-Product-Brief-2024-v3.0.pdf
4. Prophesee EVK4 HD Camera Manual (PDF): https://www.prophesee.ai/wp-content/uploads/2024/10/EVK4_HD_Prophesee_Evaluation_Kit_Camera_Manual_1.2_OK.pdf
5. iniVation product specifications (DAVIS346/DVXplorer family, PDF): https://inivation.com/wp-content/uploads/2025/06/Product-Specifications-1.pdf
6. iniVation DVXplorer hardware docs: https://docs.inivation.com/hardware/current-products/dvxplorer.html
7. Prophesee IMX636-AAMR-C Product Brief (PDF): https://prophesee.ai/wp-content/uploads/2024/09/IMX636-AAMR-C-Product-Brief-2024.pdf
8. Prophesee Products Catalogue 2025 (PDF): https://www.prophesee.ai/wp-content/uploads/2025/09/Prophesee_Products_Catalogue_2025_Double_Page_OK.pdf
9. High-Speed Altitude Regulation With Neuromorphic Camera (Jeger et al., Adv. Intell. Syst. 2026): https://doi.org/10.1002/aisy.202500904
10. RidgeRun — Event Cameras on Raspberry Pi 5 and Jetson Orin NX: https://www.ridgerun.com/post/event-cameras-in-practice-a-faster-path-to-prototyping-on-raspberry-pi-5-and-jetson-orin-nx
11. tudelft/ole_ros (GitHub): https://github.com/tudelft/ole_ros
12. heudiasyc/rt_of_low_high_res_event_cameras (GitHub): https://github.com/heudiasyc/rt_of_low_high_res_event_cameras
13. IBM Research — Neuromorphic Optical Flow (CVPR 2023): https://research.ibm.com/publications/neuromorphic-optical-flow-and-real-time-implementation-with-event-cameras
14. uzh-rpg/E-RAFT (GitHub): https://github.com/uzh-rpg/E-RAFT
15. uzh-rpg/bflow (GitHub): https://www.github.com/uzh-rpg/bflow
16. dhyuan99/VecKM_flow (GitHub): https://www.github.com/dhyuan99/VecKM_flow
17. Prophesee — Detection and Tracking Tutorial: https://docs.prophesee.ai/stable/tutorials/ml/inference/detection_and_tracking.html
18. Prophesee — Inference Pipeline of Detection and Tracking (Python): https://docs.prophesee.ai/stable/samples/modules/ml/detection_and_tracking_inference_py.html
19. LogicTronixInc/Kria-Prophesee-Event-VitisAI (GitHub): https://github.com/LogicTronixInc/Kria-Prophesee-Event-VitisAI
20. realtime-intelligence/evrt-detr (GitHub): https://github.com/realtime-intelligence/evrt-detr
21. Prophesee — Pedestrian Detection with High-Resolution Event Cameras (2025): https://www.prophesee.ai/2025/02/07/pedestrian-detection-high-resolution-event-camera/
22. prophesee-ai/prophesee-automotive-dataset-toolbox (GitHub): https://github.com/prophesee-ai/prophesee-automotive-dataset-toolbox
23. prophesee-ai/ev-ultralytics (GitHub): https://github.com/prophesee-ai/ev-ultralytics
24. Deep Learning for Event-based Vision: A Comprehensive Survey and Benchmarks: https://arxiv.org/html/2302.08890 (also v3: https://arxiv.org/html/2302.08890v3)
25. Benchmarking Keyword Spotting Efficiency on Neuromorphic Hardware (Blouw et al. 2019): https://doi.org/10.1145/3320288.3320304
26. Advancing Neuromorphic Computing With Loihi: A Survey of Results and Outlook (Davies et al., Proc. IEEE 2021): https://doi.org/10.1109/jproc.2021.3067593
27. IEEE Spectrum — Intel's Neuromorphic Nose Learns Scents in One Sniff: https://spectrum.ieee.org/intels-neuromorphic-nose-learns-scents-in-just-one-sniff
28. VentureBeat — Intel trains neuromorphic chip to detect 10 odors: https://venturebeat.com/ai/intel-trains-neuromorphic-chip-to-detect-10-different-odors/
29. EE Times — Brain-Inspired Chip Enables Efficient 'Electronic Nose': https://www.eetimes.com/brain-inspired-chip-enables-efficient-electronic-nose/
30. Intel press release — Computers That Smell: https://www.intc.com/news-events/press-releases/detail/13/computers-that-smell-intels-neuromorphic-chip-can-sniff
31. Limitations in odour recognition and generalisation in a neuromorphic olfactory circuit (Dennler, van Schaik, Schmuker 2023): https://doi.org/10.48550/arxiv.2309.11555
32. AERO-VIS (Burkhardt et al., ETH/TUM 2026): arXiv PDF via https://arxiv.org/pdf/2605.07885v1; project page https://ethz-mrl.github.io/AERO-VIS/
33. TrinitySLAM (Cai et al. 2024): https://doi.org/10.1145/3696420
34. EventBoost (Cao et al., INFOCOM 2024): https://doi.org/10.1109/infocom52122.2024.10621101
35. FRME — FPGA-Accelerated Event-Based Rotational Motion Estimator (2025): https://doi.org/10.1109/icfpt67023.2025.00025
36. Towards Low-Latency Event-based Obstacle Avoidance on a FPGA-Drone (Bonazzi et al., CVPR-W 2025): https://openaccess.thecvf.com/content/CVPR2025W/EventVision/papers/Bonazzi_Towards_Low-Latency_Event-based_Obstacle_Avoidance_on_a_FPGA-Drone_CVPRW_2025_paper.pdf
37. AsynEVO (arXiv 2402.16398): https://arxiv.org/html/2402.16398v2
38. Event-based SLAM Benchmark for High-Speed Maneuvers: https://pubdb.com/paper/2604.24033
39. Fingertip-Mimicking e-skin Taxel Readout Chip (VLSI 2023): https://doi.org/10.23919/vlsitechnologyandcir57934.2023.10185346
40. An Event-Driven E-Skin System with Dynamic Binary Scan (arXiv 2603.10537): https://arxiv.org/html/2603.10537
41. Bioinspired spiking architecture enables energy constrained touch encoding (Ortone et al., Nat. Commun. 2026): https://doi.org/10.1038/s41467-026-68858-7
42. GelNeuro (2026): https://pubdb.com/paper/2607.05241
43. A neuro-inspired artificial peripheral nervous system for scalable electronic skins (ACES, Sci. Robotics): https://www.science.org/doi/10.1126/scirobotics.aax2198
44. An event-based opto-tactile skin (PMC 2026): https://pmc.ncbi.nlm.nih.gov/articles/PMC12878655/
45. Neuromorphic Recurrent SNNs for EMG Gesture Classification on Loihi (Bezugam et al., ISCAS 2023): https://doi.org/10.1109/iscas46773.2023.10181510
46. Low Power Neuromorphic EMG Gesture Classification (Bezugam et al., arXiv 2206.02061): https://doi.org/10.48550/arxiv.2206.02061
47. Neuromorphic Edge Computing for Biomedical Applications: EMG Gesture Classification (Vitale, Donati, Germann, Magno 2022): https://doi.org/10.1109/jsen.2022.3194678
48. Predicting EEG seizures using graded SNNs on Loihi 2 (2025): https://beta.iopscience.iop.org/article/10.1088/1741-2552/adb455
49. combra-lab/snn-eeg (GitHub): https://github.com/combra-lab/snn-eeg
50. BrainChip — Neuromorphic AI on M.2: Akida Processor: https://brainchip.com/press/brainchip-brings-neuromorphic-capabilities-to-m-2-form-factor/
51. BrainChip — Akida Edge AI Box Partner Ecosystem: https://brainchip.com/press/brainchip-unveils-edge-ai-box-partner-ecosystem-for-gestures-cybersecurity-image-recognition-and-computer-vision/
52. Frontgrade Gaisler Licenses BrainChip's Akida IP for Space: https://www.businesswire.com/news/home/20241215304799/en/
53. BrainChip — AKD1500 Edge AI Co-Processor launch: https://brainchip.com/press/brainchip-unveils-breakthrough-akd1500-edge-ai-co-processor-at-embedded-world-north-america/
54. BrainChip — AKD1500 Commercial Availability/Production Shipments: https://brainchip.com/press/brainchip-announces-commercial-availability-and-production-shipments-of-akd1500-neuromorphic-processors/
55. BrainChip — M.2 Form Factor (BusinessWire): https://www.businesswire.com/news/home/20250108897286/en/
56. CNX Software — BrainChip Akida Edge AI Box pre-orders: https://www.cnx-software.com/2024/02/26/brainchips-neuromorphic-akida-edge-ai-box/
57. BrainChip — DigiKey distribution / Akida boards: https://investor.brainchip.com/brainchip-expands-global-reach-announces-akida-boards-and-ai-development-kits-available-at-digikey/
58. Enabling Efficient Processing of SNNs on commodity neuromorphic processors (Akida benchmarks, arXiv 2504.00957): https://arxiv.org/html/2504.00957v1
59. NeuronFlow: A Hybrid Neuromorphic–Dataflow Processor Architecture (Moreira et al., AICAS 2020): https://doi.org/10.1109/aicas48895.2020.9073999
60. EE Times — GrAI Matter Raises $14M for Sparsity-Driven AI SoC: https://www.eetimes.com/grai-matter-raises-14m-for-sparsity-driven-ai-soc/
61. NeuronFlow: a neuromorphic processor architecture for Live AI (DATE 2020): https://doi.org/10.23919/date48585.2020.9116352 and PDF https://past.date-conference.com/proceedings-archive/2020/pdf/1022.pdf
62. NeuronFlow: An Architecture for Edge AI (lecture slides): https://heco.estue.nl/courses/IA-5LIL0/Topic10a-GrAI-VIP-architecture-lecture.pdf
63. GrAI Matter Labs Reveals NeuronFlow (BusinessWire 2019): https://www.businesswire.com/news/home/20190918005241/en
64. System integration of neuromorphic DVS+SpiNNaker+servomotor robot (Cheng & Nikolić 2020): https://doi.org/10.36227/techrxiv.11854254
65. NeuroPod: real-time neuromorphic spiking CPG for robotics (arXiv): https://export.arxiv.org/pdf/1904.11243
66. Neuromorphic Vision and Feedback Sensor Fusion for Robot Adaptation (López Osorio et al. 2024): https://doi.org/10.1002/aisy.202300646
67. Galluppi et al. — SpiNNaker robotic platform (2014, PDF): https://compneuro.uwaterloo.ca/files/publications/galluppi.2014.pdf
68. Closed-loop spiking control on a neuromorphic processor implemented on the iCub (arXiv 2009.09081): https://ar5iv.labs.arxiv.org/html/2009.09081
69. Roboy/LSM_SpiNNaker_MyoArm (GitHub): https://github.com/Roboy/LSM_SpiNNaker_MyoArm
70. Fast Trajectory End-Point Prediction with Event Cameras for Reactive Robot Control (arXiv 2302.13796): https://www.alphaxiv.org/abs/2302.13796
71. EV-Catcher: High-Speed Object Catching (arXiv 2304.07200): https://ar5iv.labs.arxiv.org/html/2304.07200
72. Event-based Agile Object Catching with a Quadrupedal Robot (Forrai et al., ICRA 2023): https://rpg.ifi.uzh.ch/docs/ICRA23_Forrai.pdf
73. Learning coordinated badminton skills for legged manipulators (Science Robotics): https://doi.org/10.1126/scirobotics.adu3922
74. Hamlet: Whole-Body Badminton Robot Control (arXiv 2504.17771): https://arxiv.org/html/2504.17771
75. DTG-IRRL badminton striking (Frontiers in Neurorobotics 2025): https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2025.1649870/pdf
76. Prophesee — Event-based Vision for Mobile Imaging: https://www.prophesee.ai/event-based-vision-mobile/
77. eeNews Europe — Prophesee looks to neuromorphic AI in smartphones: https://www.eenewseurope.com/en/prophesee-looks-to-neuromorphic-ai-in-smartphones/
78. EE Times — Prophesee Reinvents DVS Camera For AIoT Applications (GenX320, Xperi, YunX, Zinn Labs): https://www.eetimes.com/prophesee-reinvents-dvs-camera-for-aiot-applications/
79. Digital Trends — Prophesee/Qualcomm smartphone deblur: https://www.digitaltrends.com/phones/prophesee-metavision-sensor-could-end-blurry-smartphone-camera-photos-for-good/
80. ProVideo Coalition — Prophesee deblur production-ready: https://www.provideocoalition.com/prophesees-deblur-solution-for-smartphones-is-now-production-ready/
81. PetaPixel — New Technology Aims to Eliminate Blurry Photos (no confirmed shipping phone): https://petapixel.com/2024/03/01/ai-tech-and-unique-image-sensor-eliminate-blurry-smartphone-photos/
82. Prophesee/Qualcomm collaboration announcement (2023): https://prophesee-1.reportablenews.com/pr/prophesee-announces-collaboration-with-qualcomm-to-optimize-neuromorphic-vision-technologies-for-the-next-generation-of-smartphones-unlocking-a-new-image-quality-paradigm-for-photography-and-video
83. Prophesee — IMX636 product page (Sony collaboration): https://www.prophesee.ai/event-based-sensor-imx636-sony-prophesee/
84. Towards real-time neuromorphic radar processing on Loihi 2 (2026): https://google.iopscience.iop.org/article/10.1088/2634-4386/ae8694
85. Neuromorphic LiDAR-based BEV Object Detection using SNNs (arXiv 2605.25293): https://arxiv.org/html/2605.25293v1
86. Edge-AI Accelerated Neuromorphic VLSI Architectures for Sensor Fusion (2025): https://matjournals.net/engineering/index.php/IJESVD/article/view/2162
87. SpikeClouds: Streaming Spike-Based Processing of LiDAR (Neumeier et al. 2025): https://doi.org/10.1109/lra.2025.3585394
88. Accelerating Sensor Fusion in Neuromorphic Computing: Loihi-2 case study (arXiv 2408.16096): https://arxiv.org/html/2408.16096
89. Energy-efficient radar detection with spiking neural resonators on Loihi 2: https://iopscience.iop.org/article/10.1088/2634-4386/ae629d
90. A Low Power, Fully Event-Based Gesture Recognition System (Amir et al., CVPR 2017): https://doi.org/10.1109/cvpr.2017.781; IBM Research page https://research.ibm.com/publications/a-low-power-fully-event-based-gesture-recognition-system; CVF open access https://openaccess.thecvf.com/content_cvpr_2017/html/Amir_A_Low_Power_CVPR_2017_paper.html; dataset page https://neuromorphicsystems.github.io/land/dvs-gesture
91. An Efficient SNN for Recognizing Gestures with a DVS Camera on Loihi (Massa et al., IJCNN 2020): https://doi.org/10.1109/ijcnn48605.2020.9207109
92. Hand-Gesture Recognition Based on EMG and Event-Based Camera Sensor Fusion (Ceolini et al., Loihi + ODIN/MorphIC): https://pmc.ncbi.nlm.nih.gov/articles/PMC7438887/
93. A Systematic Survey on Event Camera Representation Learning (2026): https://arxiv.org/html/2606.23078
94. An Application-Driven Survey on Event-Based Neuromorphic Vision (MDPI Information 2024): https://www.mdpi.com/2078-2489/15/8/472
95. V2V: Scaling Event-Based Vision through Efficient Video-to-Voxel Simulation (NeurIPS 2025): https://proceedings.neurips.cc/paper_files/paper/2025/file/b14cf0a01f7a8b9cd3e365e40f910272-Paper-Conference.pdf
96. Event-Based Vision: A Survey (IEEE TPAMI, computer.org CSDL listing): https://www.computer.org/csdl/journal/tp/2022/01/09138762/1llK3L5znva

---

## Explicit gaps / NOT FOUND

- CeleX sensor specifications: NOT FOUND in this research pass.
- Samsung DVS Gen3 standalone datasheet (outside its use inside DVXplorer): NOT FOUND.
- Exact per-channel dynamic-power overhead figure for the Loihi 2 automotive radar pipeline (IOP 2026 paper): text-extraction was incomplete on this specific number; flagged rather than guessed.
- A citable, peer-reviewed percentage figure for "share of event-vision papers using frame/voxel reconstruction" was NOT FOUND; the claim is supported qualitatively by four independent sources (§3) but no single study quantifies it numerically.
- Confirmed shipping smartphone model containing the Prophesee/Sony/Qualcomm deblur module: NOT FOUND as of the most recent (2024) source retrieved.
