# A12 — Deployment Audit of Directly Trained SNNs (SpikingJelly-focused)

**Question:** where do directly trained (surrogate-gradient/BPTT) SNNs actually get deployed, if anywhere — and does direct training reach physical neuromorphic silicon more often than ANN-to-SNN conversion?

**Classification key**
- **E1** — physical silicon, latency and/or energy measured
- **E2** — physical silicon, accuracy only (no latency/energy)
- **E3** — documented deployment path exists, but no run reported in the paper
- **E4** — hardware *model* / cycle-accurate simulator only (not silicon)
- **E5** — pure software (GPU/CPU) simulation, no hardware path attempted

---

## 1. Surrogate-gradient / BPTT deep SNNs (image-classification lineage)

| Work | Framework | Neuron | T | Datasets | Hardware run? | Class |
|---|---|---|---|---|---|---|
| SEW-ResNet (Fang et al. 2021, NeurIPS) | PyTorch + SpikingJelly (`clock_driven`) | IF / PLIF | 4 (ImageNet), 16 (DVS Gesture), 16 (CIFAR10-DVS) | ImageNet, DVS Gesture, CIFAR10-DVS | NOT FOUND — no hardware execution reported in the paper or repo | E5 |
| Spiking ResNet w/ tdBN / STBP-tdBN (Zheng et al. 2021, AAAI) | Custom PyTorch (STBP) | LIF | 2–6 | CIFAR-10, ImageNet, DVS-CIFAR10, DVS Gesture | Paper explicitly frames tdBN as "enabling... efficient implementation of its inference on neuromorphic hardware" (batchnorm-fold makes the network fully-spiking/foldable) but reports **no actual chip run** — purely a design argument | E5 (E3-adjacent: hardware-compatible design, not executed) |
| PLIF (Fang et al. 2021, ICCV) | SpikingJelly | PLIF | 8 (static), 10–20 (neuromorphic) | MNIST, Fashion-MNIST, CIFAR-10, N-MNIST, CIFAR10-DVS, DVS128 Gesture | NOT FOUND | E5 |
| TET (Deng et al. 2022, ICLR) | PyTorch (uses SEW-ResNet/Spiking-ResNet-tdBN backbones) | LIF | 2–6 | CIFAR-10/100, ImageNet, DVS-CIFAR10 | NOT FOUND | E5 |
| Spikformer / Spikformer V2 (Zhou et al. 2023/2024) | PyTorch + SpikingJelly + timm | LIF (spike Q/K/V, no softmax) | 4 (ImageNet), 10–16 (DVS Gesture/CIFAR10-DVS) | ImageNet, CIFAR, CIFAR10-DVS, DVS128 Gesture | NOT FOUND. Only *theoretical* SOP-based energy (45 nm MAC/AC constants), never measured on silicon | E5 |
| Spikingformer (Zhou et al. 2023) | PyTorch + SpikingJelly | LIF, MS-residual (spike-driven) | 4 | 13 datasets incl. ImageNet | NOT FOUND — but paper explicitly argues Spikformer/SEW-ResNet's **non-spike (int-float) residual computations make them unsuitable for deployment on mainstream neuromorphic hardware**, motivating a spike-driven redesign; still evaluated only via theoretical 45 nm energy model | E5 |
| Spike-driven Transformer / Meta-SpikeFormer V2 (Yao et al.) | PyTorch + SpikingJelly | LIF, MS-residual | 1–4 | ImageNet, COCO, ADE20K | NOT FOUND (theoretical energy only) | E5 |
| Xpikeformer (Song et al. 2024) | Custom hybrid analog/digital *accelerator design* for spiking transformers | LIF | not applicable (hardware-level sim) | ImageNet-1K, wireless symbol detection | Evaluated via **NeuroSim-based circuit simulation + FPGA prototype for the attention tile only**; not a full physical ASIC of a full spiking transformer | E4 (hardware model/FPGA sub-block, not full-chip silicon) |

**Reading:** every headline surrogate-gradient/BPTT ImageNet-scale lineage (SEW-ResNet → tdBN → TET → Spikformer family → Spike-driven Transformer) is GPU-only. Energy numbers reported in these papers ("mJ", "µJ" figures) are *theoretical* SOP×45nm-energy-constant estimates, never measured on a chip. Spikingformer's own related-work section is explicit that SEW-ResNet/Spikformer-style residual connections are **not deployable** on mainstream neuromorphic hardware because of the leftover integer-float multiplications at the shortcut — an architecture-level admission that this entire lineage was not designed with a hardware target in mind.

---

## 2. SLAYER / EXODUS / Lava-DL lineage (documented Loihi path)

| Work | Framework | Neuron | T | Task | Hardware run? | Measured | Class |
|---|---|---|---|---|---|---|---|
| SLAYER (Shrestha & Orchard 2018, NeurIPS) | Custom CUDA (predecessor of Lava-DL slayer) | CUBA-LIF | ~300 (DVS Gesture), 350 | MNIST, N-MNIST, DVS Gesture, TIDIGITS | **No hardware run in the original paper.** Paper explicitly states SLAYER's role is "an offline training system to configure a network before deploying it to a chip" — i.e., documents the *intended* path, not an executed one | E3 (no run in the original paper) |
| SLAYER-trained CNN on Loihi 1 via NxTF (Intel `nxsdk_modules_ncl`, `d_slayer_nxtf_gestures.py`) | SLAYER (training) → NxTF/NxSDK (deployment) | CUBA/IF | ~24–1024 bins | DVS Gesture | Yes — physical Loihi board (`ncl-ext-ghrd-01`), execution-time and energy probes built into the script | Latency, energy (via `PerformanceProbeCondition`) | **E1** |
| Hybrid SNN-ANN via SLAYER+Lava (2024 report, "Towards Efficient Deployment of Hybrid SNNs") | PyTorch/TensorFlow (ANN) + SLAYER/Lava (SNN) | LIF | not stated in excerpt | image classification (hybrid) | Yes — Loihi 1 via **NengoLoihi**, not the Lava power tools (Lava power measurement was unreliable at time of writing) | Power (via NengoLoihi profiler), core count, latency (spike-propagation delay) | **E1** |
| Lava-DL tutorials: MNIST Dense-SNN (R-Gaurav), PilotNet SDNN/LIF regression | SLAYER (train) → NetX (deploy) | CUBA-LIF | 32 (MNIST), regression steps for PilotNet | MNIST; PilotNet steering-angle regression | Yes — physical Loihi 2 (`Loihi2HwCfg`, INRC cloud `ncl-ext-og-01`/Oheo Gulch) | Accuracy (MNIST: Sim 94.27%; reported accuracy drop vs. GPU noted in a GitHub discussion — Loihi board acc. ~55% vs. 96% off-chip on one user's NMNIST reproduction); PilotNet: throughput (16.87–408.91 fps), power/execution/memory/activity via `loihi2_profiler` | **E1** for PilotNet (full profiling suite); **E2** for the MNIST tutorial's typical run (accuracy-only unless profiling enabled) |
| EXODUS (Bauer et al. 2022/2023, Frontiers Neurosci.) | Custom CUDA (Sinabs plugin, exact-gradient variant of SLAYER) | IAF/LIF/ExpLeak | task-dependent | DVS Gesture, Spiking Heidelberg Digits, Spiking Speech Commands | NOT FOUND in the paper itself — EXODUS is purely a **training-speed** algorithm paper (GPU only, benchmarked against un-optimized BPTT and SLAYER on an NVIDIA 1080 Ti). Deployment is only possible downstream via Sinabs → DynapCNN/Speck, not exercised in this paper | E5 |
| Complete pipeline with synaptic delays on Loihi 2 (Mészáros, Knight, Timcheck, Nowotny 2025) | mlGeNN (EventProp — exact-gradient BPTT) → NetX → Loihi 2 | LIF w/ exponential synapses + learned delays | up to 62 delay steps | Spiking Heidelberg Digits (SHD), Spiking Speech Commands (SSC) — keyword spotting | Yes — physical single-chip Loihi 2 ("Oheo Gulch"), IO-unconstrained steady-state measurement | Latency (feedforward: 1.46 ms w/ delay, 1.47 ms w/o; recurrent: 1.54/1.49 ms), total & dynamic energy (feedforward: 0.46/0.28 mJ w/ delay; recurrent: 0.36/0.21 mJ), EDP; **18× faster, 250× less energy than NVIDIA Jetson Orin Nano (batch=1)** | **E1** |
| CLP-SNN — Online Continual Learning on Loihi 2 (2025) | Custom local three-factor learning rule, contributed to Lava | Spiking neural state machine | not applicable (online) | OpenLORIS few-shot robotic vision | Yes — physical Loihi 2, INT8 | Latency (0.33 ms), total/dynamic energy (0.05/0.01 mJ), EDP; 113× lower latency, 6,600× lower energy vs. strongest edge-GPU (Jetson Orin Nano) baseline | **E1** (note: on-chip *learning*, not offline-trained-then-deployed in the strict sense, but directly trained/adapted on Loihi) |

**Reading:** SLAYER/Lava-DL is the one lineage in this audit with a *consistently exercised* silicon path — Intel's own tutorials/tooling (NxTF, NetX, `loihi2_profiler`) make the GPU-train → Loihi-deploy → profile loop a first-class, repeatable workflow, and independent groups (Nowotny/Knight/mlGeNN; Loihi continual-learning work) have used it for real energy/latency benchmarking against edge GPUs. EXODUS, despite descending from SLAYER, has not itself been run on hardware — it is a training-speed contribution whose deployment story is inherited from Sinabs, not exercised in the paper.

---

## 3. Event-vision direct training deployed to physical chips (DYNAP-CNN / Speck / CRI)

| Work | Framework | Neuron | T | Dataset | Hardware | Measured | Class |
|---|---|---|---|---|---|---|---|
| Face recognition demo (Liu, Richter, Nielsen, Sheik, Indiveri, Qiao — CVPRW 2019) | Sinabs (ANN→SCNN conversion, **not direct training**) | IF | — | live DVS face stream | Physical DynapCNN ASIC | Power (sub-mW, estimated from SOPs for the live demo) | E2/E1-adjacent (conversion, not direct training — listed for completeness) |
| Speck1 direct-training benchmark ("Speck: A Smart event-based Vision Sensor…", arXiv 2304.06793 / IEEE) | Sinabs + BPTT direct training (explicitly contrasted with ANN2SNN in the same table) | IF | 300 ms exposure window | N-MNIST | Physical Speck1 chip | On-chip accuracy 98.50% (BPTT) vs. 98.56% offline; energy **180 µJ/inference** (BPTT-CNN) vs. 141 µJ (ANN2SNN on same chip); also compares to **Loihi1-SLAYER: 620 µJ** and **Loihi1-SNN-TB: 290 µJ** (both on NMNIST) | **E1** |
| Speck / dynamic-SNN Nature Communications 2024 (Yao, Richter, Zhao, Qiao, Xing, Wang, Hu, **Fang (SpikingJelly author)**, Demirci, De Marchi, Deng, Yan, Nielsen, Sheik, Wu, Tian, Xu, Li) | Sinabs (training the "dynamic SNN"/temporal-attention framework) | IF | task-dependent | DVS128 Gesture, DVS128 Gait-day, DVS128 Gait-night, HAR-DVS | Physical Speck chip | Real-time power as low as **0.70 mW**; processor resting power 0.42 mW; per-input latency 3.36 µs (chip spec); accuracy gains from input masking (e.g., +9.0% on Gesture with 50% masking, power 9.5→3.8 mW) | **E1** |
| N-MNIST quick-start (Sinabs docs) — explicitly recommends **direct BPTT training** via `sinabs-exodus` over ANN2SNN, then `DynapcnnNetwork.to(device="speck2fdevkit:0")` | Sinabs + sinabs-exodus | IAF | — | N-MNIST | Physical Speck2f dev-kit (tutorial, not a benchmarked paper) | Not a measured publication — a documented, working pathway (E3-adjacent tutorial, confirms the tooling exists) | E3 (tutorial-level; no measured numbers to cite) |
| CNN on Edge MCU vs. DynapCNN (Riverpublishers book chapter) | PyTorch → Sinabs (appears to be ANN2SNN-style conversion, training method not fully specified in excerpt) | IF | rate-coded spike frames | MNIST | Physical DynapCNN | Accuracy (98.79%/99.09% for first-spike/full-sim), latency (41.3/294.9 ms), energy (144.5 µJ) | E1/E2 (training method ambiguous — likely conversion, not confirmed direct-trained) |
| DVS128 Gesture on HiAER-Spike / CRI (UCSD) | **SpikingJelly** (training) → `hs_api` CRI-format conversion | stride-2 conv SCNN | 10 frames + 6 drain steps | DVS128 Gesture | Physical CRI FPGA-based neuromorphic hardware | Accuracy, clock cycles, HBM accesses recorded per sample (energy/latency derivable from hardware counters) | **E1/E2** — this is a **SpikingJelly-trained network reaching physical (FPGA-based) neuromorphic silicon**, independent of the Lava/Loihi path |

**Reading:** DYNAP-CNN/Speck is the *other* lineage (alongside SLAYER/Lava-DL) where direct training routinely reaches physical silicon, and — critically — the Speck1 paper is one of the only sources in this audit that runs a **head-to-head, same-chip comparison of direct BPTT training vs. ANN2SNN conversion**, finding BPTT direct training gives *higher* on-chip accuracy (98.50% vs. 86.17% in the Speck1 table, comparing different rows) at a modest energy cost. Note training method is not always disclosed cleanly in DynapCNN application papers — several (face-recognition demo, MCU-comparison chapter) are ANN2SNN conversions wearing "SCNN" language, so care is needed not to over-attribute direct training here.

---

## 4. Intel Loihi application papers (INRC ecosystem) — direct vs. converted vs. hand-designed

| Work | SNN origin | Task | Hardware | Measured | Class |
|---|---|---|---|---|---|
| Imam & Cleland, "Rapid online learning and robust recall in a neuromorphic olfactory circuit" (Nat. Mach. Intell. 2020) | **Hand-designed** (biologically derived STDP circuit, not gradient-trained; "trained" via one-shot local plasticity rules, not backprop) | Odor identification under occlusion, wind-tunnel chemosensor data | Physical Loihi (72-core network) | Latency 2.75 ms/sniff (5 gamma cycles, 200 timesteps); energy 0.43 mJ total (0.12 mJ dynamic) per sniff; scalability shown (time-to-solution independent of problem size) | **E1** |
| Tang, Shah, Michmizos — Unidimensional SLAM on Loihi (2019) | **Hand-designed** (biologically constrained head-direction/Bayesian-inference circuit) | Robot head-direction localization + mapping | Physical Loihi (Nahuku 8-chip board), 82 cores | Dynamic power: 100× less than GMapping on CPU; comparable localization accuracy | **E1** |
| Patel, Hazan, ... Krichmar-style SDDPG (Michmizos group) — "Reinforcement co-Learning of Deep and Spiking Neural Networks for Energy-Efficient Mapless Navigation" | **Directly trained** — spiking actor network co-trained end-to-end with a deep critic via gradient descent (STBP extension) | Mapless robot navigation (real-world TurtleBot2) | Physical Loihi (Kapoho Bay, 2 chips) | Idle/dynamic power, inf/s, µJ/inf for T=5,10,25,50 (e.g., T=5: 15.53 µJ/inf); **75× less energy per inference than DDPG on Jetson TX2 (MAXQ)** | **E1** — this is one of the few **directly-trained (gradient-based)** Loihi robotics papers in this list |
| Kreiser et al. — On-chip SNN for iCub head-pose estimation (Frontiers Neurorobotics 2020) | **Hand-designed** path-integration circuit with on-chip plasticity | Robot head-pose estimation | Physical Loihi (Kapoho Bay) | RMSE (1.93–2.43° integration-only; 4.47–8.98° w/ visual reset), real-time loop <10 ms | E2 (accuracy/latency reported qualitatively; no energy) |
| Neuromorphic force-control (industrial peg-in-hole, arXiv 2403.08928) | **Directly trained** — SNN policy trained via spiking RL in simulation (PyTorch), ported to Loihi 1 (NxSDK) / Loihi 2 (Lava) | Industrial object insertion with KUKA arm + force-torque sensor | Physical Loihi 1 (Kapoho Bay) and Loihi 2 (Oheo Gulch, remote) | Latency: Loihi 1 1.8 ms, Loihi 2 1.5±0.10 ms; dynamic energy Loihi 2: 53±17 µJ/inference; compared to CPU (3800 µJ) and GPU (~100s µJ) | **E1** |
| Davies et al. 2018 (Loihi intro paper) — Spiking LCA for LASSO | **Hand-designed** (Spiking Locally Competitive Algorithm, provably converges to LASSO fixed point — Tang, Lin, Davies 2017) | Sparse coding / LASSO optimization | Loihi predecessor chip (pre-silicon + early post-silicon) | EDP improvement of >3 orders of magnitude vs. Atom CPU (LARS/FISTA); energy/delay ratios tabulated by problem size (up to 5760× EDP advantage at 32,256 unknowns) | **E1** |
| Parpart, Risbud, Kenyon, Watkins — LCA on Loihi 2 (2023) | Hand-designed (LCA, extended for Loihi 2 custom neuron models) | Sparse coding benchmarking vs. CPU/GPU | Physical Loihi 2 | Orders-of-magnitude efficiency/speed advantage for large sparsity penalties (qualitative in excerpt) | E1 (efficiency claims; specifics not fully captured in excerpt) |
| Convolutional LCA on Loihi 2 (arXiv, 2025/2026) | Hand-designed (LCA) | Convolutional sparse coding | Physical single-chip Loihi 2 | Latency, dynamic power/energy per inference, PSNR, vs. GPU — regime-dependent (GPU faster, Loihi 2 lower dynamic energy) | **E1** |
| SAT/CSP solving on Loihi (DATE 2020 workshop paper) | Hand-designed (SNN encoding of CNF/DPLL-style search) | Boolean satisfiability | Physical Loihi | Static + dynamic power (linear model fit); first reported CSP/SAT implementation on embedded neuromorphic hardware | **E1** (power only, no accuracy — SAT solving is exact/deterministic) |
| Intel's own slide deck (Rao Mangalore, TUM 2023) — aggregate claims | Mixed (hand-designed optimization solvers + "Direct & HW-aware training" family for DNN-style workloads) | Optimization (LASSO, CSP/SAT/ILP/QUBO): "1000–100,000× lower energy" (LASSO), "2,800× lower energy and 44× faster" (CSP/SAT/ILP/QUBO) vs. CPU | Physical Loihi (aggregated results across cited papers) | Aggregated EDP/energy claims | E1 (secondary/aggregated; underlying papers already listed above) |

**Reading:** this is where the survey's "E1 evidence concentrates," confirming the prompt's expectation — but the concentration is **not** dominated by surrogate-gradient direct training. The largest, most consistently measured E1 body of Loihi application work (olfaction, SLAM, iCub pose estimation, LASSO/sparse coding, SAT/CSP) is **hand-designed / biologically-derived SNNs with local plasticity rules**, not BPTT/surrogate-gradient trained networks. The clearest **directly-trained** (gradient-based) Loihi deployments with full energy/latency measurement are the *robotics-control* papers — SDDPG mapless navigation and the industrial force-control peg-in-hole task — both of which train a spiking policy end-to-end via gradient descent (adapted STBP) in simulation and then port weights to physical Loihi.

---

## 5. Audio / keyword spotting on neuromorphic hardware

| Work | Chip | Training | Task | Measured (physical device) | Class |
|---|---|---|---|---|---|
| "Micro-power spoken keyword spotting on Xylo Audio 2" (Bos & Muir 2024) | Xylo Audio 2 (SynSense) | Directly trained SNN (LIF, quantized via Rockpool) | Aloha KWS benchmark | 95% accuracy (>benchmark's 93%); dynamic power 291 µW; dynamic energy/inf **6.6 µJ**; active energy/inf 11 µJ — **best-in-class among compared devices** (Table: GPU 29.67 mJ, CPU 6.32 mJ, Jetson 5.58 mJ, MOVIDIUS 1.5 mJ, **Loihi 0.27/0.037 mJ**, SpiNNaker2 0.0071 mJ, Xylo 0.0066 mJ) | **E1** |
| Xylo KWS ("export.arxiv.org/pdf/2208.12991", earlier Xylo report) | Xylo | Directly trained | Audio classification (KWS) | Real total power 542 µW; idle 219 µW; dynamic inference 93 µW; per-inference dynamic energy 9.3 µJ (median latency), 93 nJ per network timestep | **E1** |
| DCASE 2020 Acoustic Scene Classification on Xylo Audio 2 (NeuroBench, 2024) | Xylo Audio 2 | Directly trained | Acoustic scene classification | Active power 692 µW, active energy/inf 57.6 µJ, dynamic energy/inf 28.4 µJ | **E1** |
| Loihi KWS comparisons (as cited within the Xylo benchmark table, sourced from Blouw et al. and related work) | Loihi | Reported as directly-trained/converted KWS network (not detailed in excerpt; cited secondarily) | Aloha-style KWS | Idle 29 mW, active 110/40 mW, dynamic energy/inf 0.27/0.037 mJ (two different source papers) | **E1** (secondary citation within Xylo paper — original source not independently verified here) |
| SpiNNaker2 KWS (cited secondarily in Xylo table) | SpiNNaker2 | Not detailed in excerpt | KWS | Dynamic power 7.1 mW → 0.0071 mJ/inf | **E1** (secondary citation, not independently verified here) |

**Reading:** Xylo is the strongest E1 audio/KWS lineage found — directly trained SNNs, physical silicon, continuously measured power on real hardware, beating Loihi and SpiNNaker2 on the same benchmark task in the comparison table. This is a genuinely **commercial, purpose-built chip** (SynSense product line) rather than a research prototype, and the deployment pipeline (Rockpool → Xylo) is explicitly built around direct SNN training, not conversion.

---

## 6. Commercial / industrial deployment

- **Xylo (SynSense)** is the clearest example of a *commercial* neuromorphic product with a documented, benchmarked, directly-trained-SNN deployment pipeline (Rockpool), sold as an audio/IMU inference chip for edge devices (Section 5).
- **Speck (SynSense)** is likewise a commercial SoC (DVS + DYNAP-CNN) with public dev kits, an open-source training/deployment stack (Sinabs + Samna), and at least one Nature Communications-level, physically-measured, low-power deployment (Section 3) with real-world smart-home/gesture-recognition framing.
- **DynapCNN (SynSense)** — commercial-adjacent research chip, used in live demos (face recognition) but conversion-based, not direct training, in the sources found.
- **Loihi / Loihi 2 (Intel)** remains a **research** chip distributed through the Intel Neuromorphic Research Community (INRC), not a commercial product; all Loihi results above (Sections 2 and 4) come from INRC-affiliated academic groups, not shipping industrial deployments.
- NOT FOUND: no evidence in this search of a directly-trained deep SNN (SEW-ResNet/Spikformer/TET-style) shipping in *any* commercial product or industrial pipeline. The industrial-facing examples that do exist (Xylo KWS, the KUKA-arm force-control demo) are either small task-specific networks or explicitly framed as "proof of concept," not production deployment.

---

## Direct answer to the SpikingJelly-specific question

**Does SpikingJelly's own documented `lava_exchange` path (SpikingJelly → Lava-DL → Lava → Loihi) show up in published, hardware-measured work — and beyond that, what fraction of SpikingJelly-trained papers reach hardware at all?**

- SpikingJelly's own Science Advances paper (Fang et al. 2023) demonstrates the `exchange` subpackage end-to-end as one of its three headline case studies: train a deep convolutional SNN on DVS Gesture in SpikingJelly, then "deploy the SNN on the neuromorphic Loihi chip for inference purposes" (Fig. 4A). The paper does **not** report separate accuracy/latency/energy numbers for that Loihi run distinct from the GPU-trained baseline — it is presented as a capability demonstration, not a hardware benchmark. Classified **E3** (documented, exercised path; no distinct hardware measurement reported).
- A genuinely independent, hardware-measured example was found: **"Real-Time Frame- and Event-based Object Detection with SNNs on Edge Neuromorphic Hardware"** (2026 preprint, code repo `Realtime-frame-and-event-based-detection-with-SNN-on-Neuromorphic-hardware`) trains SNNs explicitly **with the SpikingJelly library** (repo file names: `spjelly_to_sl...`), exports to Lava-DL-compatible format, and benchmarks on **physical Loihi 2** (Oheo Gulch) against Jetson Orin Nano / Jetson Nano B01 / Apple M2, reporting inference rate, dynamic energy, total power, and EDP. This is the clearest case found of a third-party paper taking SpikingJelly-trained weights all the way to measured Loihi 2 silicon. Classified **E1**.
- A second independent example: DVS128 Gesture networks **trained with SpikingJelly**, converted via `hs_api` to the CRI format, and run on **physical CRI FPGA-based neuromorphic hardware** (UCSD HiAER-Spike project) — a non-Loihi hardware target, with accuracy and hardware performance counters (clock cycles, HBM accesses) recorded per sample. Classified **E1/E2**.
- A live GitHub issue (fangwei123456/spikingjelly #543, May 2024) shows users actively hitting **hardware constraints** when trying to deploy SpikingJelly-trained convolutional layers to Loihi (axon-count limits: "Loihi only supports 4096 input and output axons"), confirming the path is used in practice but is non-trivial and architecture-constrained.
- **Fraction estimate:** of the very large number of published works that cite or use SpikingJelly (it is the default framework for most of the surrogate-gradient lineage in Section 1 — SEW-ResNet, PLIF, Spikformer family, Spikingformer, Spike-driven Transformer, plus many robotics/RL papers), only a small handful were found in this search to have taken a SpikingJelly-trained network to *any* physical chip (Loihi 2 object detector; CRI FPGA gesture classifier; the SpikingJelly paper's own DVS Gesture demo). The overwhelming majority — including every headline ImageNet-scale architecture paper in Section 1 — remain GPU/CPU simulation only. This is consistent with a rough **fraction well under 5%** of SpikingJelly-based publications reaching hardware, based on the papers surveyed here (not a formal census).

---

## Comparative evidence: does direct training reach hardware more often than conversion, and why?

**Evidence that direct training reaches hardware less often, when the workload is static-image classification.** The single most-cited, most benchmarked directly-trained SNN lineage (SEW-ResNet → Spikformer → Spike-driven Transformer, all ImageNet-scale, all surrogate-gradient/BPTT) has **zero** confirmed physical-chip deployments in this audit (Section 1). By contrast, the ANN-to-SNN conversion literature this thesis's own repo already tracks (QCFS-lineage) targets exactly this same static-image, large-T regime and is, by the design of that literature, oriented toward eventual hardware inference — though this audit did not re-examine conversion-side hardware evidence directly (out of scope here; see the companion conversion-deployment audit if one exists).

**Evidence that direct training reaches hardware *more* often when (a) the workload is event-native, and/or (b) hardware constraints are folded into training.** Every E1 example of a *directly trained* SNN reaching silicon in this audit shares one or both of these properties:
1. **Event-native inputs** — DVS Gesture/Gait/HAR-DVS on Speck (Section 3), SHD/SSC keyword spotting on Loihi 2 (Section 2), Xylo audio KWS (Section 5). These tasks are naturally temporal/sparse, so a directly-trained recurrent/temporal SNN is the natural model class, and the deployment toolchains (Sinabs→DynapCNN, mlGeNN→NetX, Rockpool→Xylo) were built by the same vendors as the hardware, closing the loop deliberately.
2. **Hardware-in-the-loop or hardware-aware training** — the SDDPG robot-navigation paper trains with the *same neuron model Loihi supports* so "all other hyperparameters remained the same as the ones used in training," and explicitly designs a rescaling technique for Loihi's 8-bit integer weights; the mlGeNN/Loihi-2 delay paper trains with EventProp specifically because its exact-gradient formulation maps cleanly onto event-driven hardware and quantizes to INT8 for deployment; the Speck1 paper trains directly with BPTT specifically to close the "synchronous training / asynchronous deployment" gap the authors identify as the source of accuracy loss when converting frame-trained networks to event-driven asynchronous chips.

**A third factor, not purely "direct vs. converted": chip vendor incentive structure.** The two hardware families with the deepest E1 track record (Loihi/Lava-DL, DYNAP-CNN/Speck) are backed by **first-party training-to-deployment toolchains built by the chip vendor itself** (Intel: SLAYER→Lava-DL→NetX; SynSense: Sinabs/EXODUS→DynapcnnNetwork; SynSense: Rockpool→Xylo). Where such a toolchain exists, direct training reaches hardware routinely and is even benchmarked against edge GPUs as standard practice. Where it does not (no vendor-maintained bridge from SpikingJelly's ImageNet-scale architectures to any commercial chip beyond the narrow, axon-limited Lava export), direct training stays in simulation regardless of the underlying algorithm's merits. This suggests hardware reach is driven less by "direct training is inherently more hardware-compatible" and more by **whether a matched, vendor-maintained training→deployment pipeline exists for the target workload** — which happens to correlate strongly with event-native, edge-inference workloads (KWS, gesture, small-scale control) rather than ImageNet-scale vision backbones.

**Against the "direct training is inherently better suited" narrative:** the hand-designed (non-gradient-trained) Loihi lineage — olfaction (Imam & Cleland), SLAM (Tang et al.), sparse coding/LASSO (Davies et al., Parpart et al.), SAT/CSP solving — is *at least as large and at least as rigorously measured* (E1 throughout) as the gradient-trained Loihi lineage. This body of work reaches hardware not because it is "directly trained" in the surrogate-gradient sense, but because it was designed from the outset as a spiking algorithm with local, on-chip-compatible update rules — a different notion of "direct" (bio-inspired/local-plasticity) than the BPTT/surrogate-gradient sense used elsewhere in this audit. A survey conflating "directly trained" with "not ANN2SNN-converted" risks overstating how much of the Loihi E1 evidence base is actually attributable to the surrogate-gradient training paradigm that dominates the SpikingJelly/SEW-ResNet/Spikformer literature.

---

## Source list

1. Fang et al., "Deep Residual Learning in Spiking Neural Networks" (SEW-ResNet), NeurIPS 2021. arXiv:2102.04159. https://arxiv.org/abs/2102.04159
2. `fangwei123456/Spike-Element-Wise-ResNet` GitHub repo. https://github.com/fangwei123456/Spike-Element-Wise-ResNet
3. Zheng, Wu, Deng, Hu, Li, "Going Deeper With Directly-Trained Larger Spiking Neural Networks" (tdBN/STBP-tdBN), AAAI 2021. https://ojs.aaai.org/index.php/AAAI/article/view/17320 ; arXiv:2011.05280
4. Fang et al., "Incorporating Learnable Membrane Time Constant to Enhance Learning of Spiking Neural Networks" (PLIF), ICCV 2021. arXiv:2007.05785. https://arxiv.org/abs/2007.05785
5. `fangwei123456/Parametric-Leaky-Integrate-and-Fire-Spiking-Neuron` GitHub repo.
6. Deng, Wu, ... "Temporal Efficient Training of Spiking Neural Network via Gradient Re-weighting" (TET), ICLR 2022. arXiv:2202.11946. http://arxiv.org/pdf/2202.11946
7. Zhou et al., "Spikformer: When Spiking Neural Network Meets Transformer," 2022. arXiv:2209.15425. https://ar5iv.labs.arxiv.org/html/2209.15425
8. Zhou et al., "Spikformer V2: Join the High Accuracy Club on ImageNet with an SNN Ticket," 2024. arXiv:2401.02020.
9. Zhou, Yu, Zhou, Zhang, Wang, Zhou, Ma, Tian, "Spikingformer: A Key Foundation Model for Spiking Neural Networks," AAAI 2026 (published version) / arXiv:2304.11954. `TheBrainLab/Spikingformer` GitHub.
10. Song, Katti, Simeone, Rajendran, "Xpikeformer: Hybrid Analog-Digital Hardware Acceleration for Spiking Transformers," 2024. arXiv:2408.08794.
11. Shrestha & Orchard, "SLAYER: Spike Layer Error Reassignment in Time," NeurIPS 2018. arXiv:1810.08646.
12. Intel `intel-nrc-ecosystem/models` repo, `nxsdk_modules_ncl/dnn/tutorials/d_slayer_nxtf_gestures.py`. https://github.com/intel-nrc-ecosystem/models
13. "Towards Efficient Deployment of Hybrid SNNs on..." (hybrid SNN-ANN on Loihi 1 via NengoLoihi). https://par.nsf.gov/servlets/purl/10586400
14. Mészáros, Knight, Timcheck, Nowotny, "A Complete Pipeline for deploying SNNs with Synaptic Delays on Loihi 2," 2025. arXiv:2510.13757.
15. "Online Continual Learning on Intel Loihi 2 via a Co-designed Spiking Neural Network" (CLP-SNN), 2025. arXiv:2511.01553.
16. Bauer, Lenz, Haghighatshoar, Sheik, "EXODUS: Stable and Efficient Training of Spiking Neural Networks," Frontiers in Neuroscience 2023 (also arXiv:2205.10242). `synsense/sinabs-exodus` GitHub.
17. `R-Gaurav/mnist-on-loihi` GitHub repo + tutorial blog: https://r-gaurav.github.io/2024/04/13/Lava-Tutorial-MNIST-Training-on-GPU-and-Evaluation-on-Loihi2.html
18. `lava-nc/lava-dl` tutorials: PilotNet SDNN/LIF `benchmark.ipynb`, Oxford `run.ipynb`. https://github.com/lava-nc/lava-dl
19. `lava-nc/lava` GitHub Discussion #891 (Loihi vs. SLAYER accuracy drop report).
20. Yao, Richter, Zhao, Qiao, Xing, Wang, Hu, Fang, Demirci, De Marchi, Deng, Yan, Nielsen, Sheik, Wu, Tian, Xu, Li, "Spike-based dynamic computing with asynchronous sensing-computing neuromorphic chip" (Speck), Nature Communications 2024. https://doi.org/10.1038/s41467-024-47811-6
21. Richter et al., "Speck: A Smart event-based Vision Sensor with a low latency 327K Neuron Convolutional..." arXiv:2304.06793.
22. Liu, Richter, Nielsen, Sheik, Indiveri, Qiao, "Live Demonstration: Face Recognition on an Ultra-Low Power Event-Driven Convolutional Neural Network ASIC," CVPRW 2019.
23. SynSense Speck / DYNAP-CNN datasheets and Sinabs docs (`sinabs.readthedocs.io`), `sinabs-dynapcnn`.
24. "Deploying a Convolutional Neural Network on Edge MCU and Neuromorphic Hardware Platforms," River Publishers book chapter. https://www.riverpublishers.com/pdf/ebook/chapter/RP_9788770227902C10.pdf
25. Imam & Cleland, "Rapid online learning and robust recall in a neuromorphic olfactory circuit," Nature Machine Intelligence 2020. arXiv:1906.07067.
26. Tang, Shah, Michmizos, "Spiking Neural Network on Neuromorphic Hardware for Energy-Efficient Unidimensional SLAM," 2019. arXiv:1903.02504.
27. "Reinforcement co-Learning of Deep and Spiking Neural Networks for Energy-Efficient Mapless Navigation with Neuromorphic Hardware" (SDDPG), arXiv:2003.01157.
28. Kreiser, Renner, ... Sandamirskaya, "An On-chip Spiking Neural Network for Estimation of the Head Pose of the iCub Robot," Frontiers in Neurorobotics 2020.
29. "Neuromorphic force-control in an industrial task: validating energy and latency benefits," arXiv:2403.08928.
30. Davies et al., "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning," IEEE Micro 2018.
31. Tang, Lin, Davies, "Sparse Coding by Spiking Neural Networks: Convergence Theory and Computational Results," arXiv:1705.05475.
32. Parpart, Risbud, Kenyon, Watkins, "Implementing and Benchmarking the Locally Competitive Algorithm on the Loihi 2 Neuromorphic Processor," 2023.
33. "Convolutional Sparse Coding via the Locally Competitive Algorithm on Loihi 2," arXiv (2025/2026 preprint).
34. "Solving Constraint Satisfaction Problems Using the [Loihi processor]" (SAT/CSP), DATE 2020 workshop paper.
35. Rao Mangalore (Intel), "Low-power, low-latency computing with Loihi 2," TUM Venture Labs slide deck, 2023.
36. Bos & Muir (SynSense), "Micro-power spoken keyword spotting on Xylo Audio 2," 2024. arXiv:2406.15112.
37. Earlier Xylo KWS report, arXiv:2208.12991.
38. "Neurobench: DCASE 2020 Acoustic Scene Classification benchmark on Xylo™ Audio 2," arXiv:2410.23776.
39. Rockpool docs, "Measuring power consumption on Xylo Audio HDK." https://rockpool.ai/devices/quick-xylo/xylo-audio-power.html
40. Fang et al., "SpikingJelly: An open-source machine learning infrastructure platform for spike-based intelligence," Science Advances 2023. https://www.science.org/doi/10.1126/sciadv.adi1480
41. SpikingJelly docs, "Convert to Lava for Loihi Deployment" (`lava_exchange` tutorial). https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html
42. `fangwei123456/spikingjelly` GitHub Issue #543, "Limitations when deploying SNNS to loihi."
43. "Real-Time Frame- and Event-based Object Detection with Spiking Neural Networks on Edge Neuromorphic Hardware: Design, Deployment and Benchmark," 2026 preprint. `gwgknudayanga/Realtime-frame--and-event-based-detection-with-SNN-on-Neuromorphic-hardware` GitHub repo.
44. HiAER-Spike / CRI hardware docs (UCSD ISN), "DVS128 Gesture Inference on HiAER-Spike Hardware." https://isn.ucsd.edu/hiaer-spike/auto_examples/plot_dvs_gesture_inference.html
45. Karki, Chavez Arana, Sornborger, Caravelli, "Neuromorphic on-chip reservoir computing with spiking neural network architectures," arXiv:2407.20547.
46. Uludağ et al., "Bio-realistic neural network implementation on Loihi 2 with Izhikevich neurons," Neuromorphic Computing and Engineering 2024.
47. "Transductive Spiking Graph Neural Networks for Loihi," arXiv:2404.17048.

---

## Notes on search completeness

- Checked experiments/methods sections, not just abstracts, for every entry classified E1/E2 above (hardware section text, tables, and code repos were read where available).
- NOT FOUND, explicitly: any physical-hardware run for SEW-ResNet, tdBN/STBP-tdBN, PLIF, TET, Spikformer (V1/V2), Spikingformer, or Spike-driven Transformer as originally published. All energy numbers in those papers are theoretical (45 nm MAC/AC constant) estimates, not measurements.
- NOT FOUND: a full-chip physical ASIC implementation of any spiking transformer (Xpikeformer is a NeuroSim+FPGA-tile hardware *model*, not full silicon).
- NOT FOUND: any explicit statement that EXODUS itself (as opposed to downstream Sinabs/DynapCNN users) was run on physical hardware.
- Did not exhaustively survey the ANN2SNN/conversion side for a symmetric hardware-reach count; this would be needed to make the comparative claim in the final section fully quantitative rather than qualitative.
