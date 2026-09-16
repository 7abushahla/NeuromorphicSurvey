# A05 — Other Neuromorphic Substrates: TrueNorth, Tianjic/Lynxi, Innatera, Academic ASICs, FPGA SNN Accelerators

Scope note: BrainChip Akida is explicitly excluded per task instructions.

Evidence classes used throughout:
- **E1** — physical silicon, latency and/or energy measured on hardware
- **E2** — physical silicon, accuracy only (no latency/energy measurement reported)
- **E3** — documented deployment path, no published run
- **E4** — hardware model: RTL synthesis, cycle-accurate simulation, or analytical/EDA-tool energy model, not measured on fabricated silicon
- **E5** — software simulation only

---

## 1. IBM TrueNorth

### 1.1 Architecture

TrueNorth is a fully digital, non-von-Neumann, event-driven neurosynaptic chip: 4,096 neurosynaptic cores, 1 million neurons, 256 million synapses, 5.4 billion transistors, fabricated in 28 nm CMOS, consuming ~65–70 mW at real-time operation [Merolla et al. 2014, Science; Akopyan et al. 2015 IEEE TCAD]. Each core contains 256 input axons, a 256×256 binary synaptic crossbar, and 256 neurons, time-multiplexed onto a single physical neuron computation circuit [Akopyan et al. 2015].
https://redwood.berkeley.edu/wp-content/uploads/2021/08/Akopyan2015.pdf
https://research.ibm.com/publications/truenorth-design-and-tool-flow-of-a-65-mw-1-million-neuron-programmable-neurosynaptic-chip

**Time model.** TrueNorth uses a global 1 kHz synchronization signal called a "tick." All neurons are evaluated once per tick (1 ms), and all core computation must complete within that window; the architecture author-defines "real-time" as one full network evaluation per millisecond. Higher tick rates are possible but 1 kHz is the typical/reference operating point [Esser et al. 2016 PNAS; Akopyan et al. 2015].
http://arxiv.org/pdf/1603.08270v1.pdf (Esser et al., Eedn/PNAS preprint)
https://redwood.berkeley.edu/wp-content/uploads/2021/08/Akopyan2015.pdf

**Neuron model.** A configurable but constrained variant of an augmented integrate-and-fire (IF) model, described formally in Cassidy et al., "Cognitive Computing Building Block: A Versatile and Efficient Digital Neuron Model for Neurosynaptic Cores." The neuron has 23 configurable parameters, supports leak (deterministic or stochastic, with convergent/divergent leak-reversal modes), a positive threshold and a negative threshold ("floor" or "bounce" behavior), stochastic thresholds via a masked PRNG, and three reset modes (normal/hard reset to Rj, linear/residual-preserving reset, and non-reset stochastic mode). It reproduces all 20 Izhikevich behavioral classes via combinations of 1-3 simple neuron instances.
https://viplab.fudan.edu.cn/vip/attachments/download/3248/neuron-model_of_truenorth.pdf

**Spike payload and connectivity.** All intra- and inter-core communication is via 1-bit binary spikes. Connectivity is block-wise: each neuron connects to one axon on one target core through a spike router, and to any neuron on that core via the local crossbar. Encoding schemes documented for the AER bus include pulse-density (rate) coding, thermometer coding, time-slot encoding, and stochastic encoding [Andreou et al. 2016 ISCAS].
https://doi.org/10.1109/iscas.2016.7539214

**Weight precision — four trinary axon types.** TrueNorth does not natively support multi-bit weights. Each axon is assigned one of 4 possible "axon types" (Gi ∈ {0,1,2,3}); each neuron carries a 4-entry lookup table mapping axon type to a signed integer synaptic strength in the range [-255, 255]. For the Eedn convolutional-network mapping specifically, weights are constrained to trinary {-1, 0, +1}: a feature is represented by a pair of neuron copies, one wired with axon type 1 (LUT value +1) and one with axon type 2 (LUT value -1); turning on neither, one, or the other synapse yields weight 0, +1, or -1. This is a construction built on top of the more general 4-type/9-bit-signed-integer LUT mechanism, not a native trinary datatype.
http://arxiv.org/pdf/1603.08270v1.pdf
https://escholarship.org/uc/item/3n66b3rv (independent restatement of the 4-entry LUT / trinary construction, medical-imaging application)

**On-chip learning.** None. TrueNorth is inference-only; all training (Eedn) happens off-chip, and learned weights are mapped to hardware via the Corelet compilation flow. No SDSP/STDP or other online-learning rule is implemented on TrueNorth (contrast with ODIN, ReckOn, MorphIC below, which are explicitly online-learning academic ASICs).

### 1.2 Eedn / Corelet toolchain and coding scheme

Eedn ("Energy-efficient deep neuromorphic networks," Esser et al., PNAS 2016, building on the 2015 arXiv preprint) is the training-and-mapping methodology: backpropagation-trained CNNs with (i) trinary weights, (ii) binary-valued neurons with an approximated derivative (triangle function) for the non-differentiable step activation, and (iii) block-wise-constrained convolutional filter groups that map to the 256×256 crossbar limit. The output of training (Caffe/MatConvNet-based) is compiled by the Corelet stage into a hardware-ready TrueNorth configuration; the Corelet programming language, Corelet Programming Environment (CPE), and Compass simulator constitute the software ecosystem, described in Sawada et al., "TrueNorth Ecosystem for Brain-Inspired Computing" (SC 2016).
https://www.pnas.org/doi/10.1073/pnas.1604850113
https://research.ibm.com/publications/truenorth-ecosystem-for-brain-inspired-computing-scalable-systems-software-and-applications

**Is Eedn rate coding or something else?** Eedn is *not* conventional multi-timestep rate coding. Per Esser et al. 2016 PNAS: "Testing was performed at one classification per hardware tick" — i.e., a single tick evaluates the whole network once; the "rate" that encodes the activation magnitude is realized spatially, via the number of physically-instantiated redundant neuron copies (each network activation is represented as the aggregate spike count across a population of trinary-weighted neuron copies within one tick), not temporally, via repeated ticks accumulating a firing rate the way IF-based ANN-to-SNN-conversion literature (Diehl/Rueckauer/QCFS-style) does. This is a materially different coding scheme from the temporal rate coding used in the ANN-to-SNN conversion literature this thesis builds on; TrueNorth/Eedn should not be cited as a hardware validation of temporal-rate-coded, IF-with-reset-by-subtraction converted SNNs.
https://www.pnas.org/doi/10.1073/pnas.1604850113

### 1.3 Measured physical results (E1)

From Esser et al. 2016 PNAS, Table 3 (measured on the NS1e board for accuracy/throughput and the separate NS1t board for power, both at 1.0 V, single TrueNorth chip):

| Dataset | TrueNorth 1-chip accuracy | Cores used | FPS | Power (mW) | FPS/W |
|---|---|---|---|---|---|
| CIFAR-10 | 83.41% | 4,042 | 1,249 | 204.4 | 6,108.6 |
| CIFAR-100 | 55.64% | 4,042 | 1,526 | 207.8 | 7,343.7 |
| SVHN | 96.66% | 4,042 | 2,526 | 256.5 | 9,849.9 |
| GTSRB | 96.50% | 4,042 | 1,615 | 200.6 | 8,051.8 |
| LOGO32 | 85.70% | 3,236 | 1,775 | 171.7 | 10,335.5 |
| VAD | 95.42% | 423 | 1,539 | 26.1 | 59,010.7 |
| TIMIT (classification) | 79.16% | 1,943 | 2,610 | 142.6 | 18,300.1 |
| TIMIT (frames) | 71.17% | 2,476 | 2,107 | 165.9 | 12,698.0 |

Aggregate headline figures reported: single-chip throughput 1,200–2,600 FPS at 25–275 mW, >6,000 FPS/W across the eight benchmark datasets. Multi-chip (2, 4, 8-chip) configurations were evaluated only in simulation for accuracy scaling, not measured on physical multi-chip hardware for throughput/power in the PNAS paper, except where explicitly stated (Sawada et al. SC-2016 companion paper measured NS16e board results below).
https://www.pnas.org/doi/10.1073/pnas.1604850113

Multi-chip physical measurement, from Sawada et al. 2016 (TrueNorth Ecosystem for Brain-Inspired Computing, SC-2016), NS1e (1 chip) vs NS16e (4/8-chip) boards, CIFAR-10/100:

| Task | System | Active chips | Throughput (FPS) | System power (W) | TrueNorth power (W) | FPS/W | Accuracy |
|---|---|---|---|---|---|---|---|
| CIFAR10 | NS1e | 1 | 1,249 | 3.52 | 0.204 | 6,109 | 83.41% |
| CIFAR10 | NS16e | 4 | 1,324 | 8.64 | 0.936 | 1,414 | 87.97% |
| CIFAR10 | NS16e | 8 | 1,040 | 8.88 | 1.497 | 695 | 89.00% |
| CIFAR100 | NS1e | 1 | 1,526 | 3.52 | 0.208 | 7,344 | 55.64% |
| CIFAR100 | NS16e | 4 | 1,257 | 8.64 | 0.891 | 1,410 | 63.86% |
| CIFAR100 | NS16e | 8 | 432 | 8.28 | 1.192 | 362 | 66.32% |

This is a genuine E1 physical multi-chip measurement (16-chip NS16e board, only 4 or 8 chips active for these specific networks).
https://dl.dropboxusercontent.com/s/brj18cmy9vy5oq5/TrueNorthEcosystem.pdf

Additional independently-measured physical deployments (E1/E2):
- MNIST/COIL-20/COIL-100 object recognition on NS1e, up to 99.07% (MNIST), 99.36% (COIL-20), 96.8% (COIL-100) — accuracy-only characterization of wide vs. deep network structure on physical TrueNorth [Alom et al. 2018 IJCNN]. E2 (accuracy characterization; no independent energy/FPS measurement beyond citing the PNAS >6,000 FPS/W figure).
https://doi.org/10.1109/ijcnn.2018.8489635
- Spinal MRI image segmentation on TrueNorth NS1e/NS16e: >20× speedup vs. GPU-accelerated network, <0.1 W, using the Eedn trinary-weight training flow [Moran et al. 2018]. E1 (measured speed/power claim, though absolute latency numbers are not tabulated in the excerpt retrieved).
https://escholarship.org/uc/item/3n66b3rv
- Car detection/counting on a 16-chip NS16e (all 16 chips used for a single network): 97.60% detection accuracy, 69.04% counting accuracy, throughput 3.38 FPS at an aggregate measured active power of 1.76 W (0.775 V) / 2.87 W (1.0 V), idle+peak system power up to 8.73 W; tick period had to be relaxed to 1.75 ms (571.43 Hz) from the nominal 1 kHz to avoid inter-chip spike-routing bottlenecks [Shukla et al. 2019, Frontiers in Neuroscience]. E1, physical NS16e board measurement, and notable for showing TrueNorth's 1 kHz tick is not always achievable at multi-chip scale.
https://doi.org/10.3389/fnins.2019.00004

Third-party comparative measurement (TrueNorth vs. GPU vs. FPGA on CIFAR-10, tuned to matched ~83–84.5% accuracy): TrueNorth (NS1e) achieves the best FPS/Watt (6,122) among TrueNorth/GPU/FPGA, but has the lowest raw FPS versus GPU (GPU: 3,333–55,556 FPS with cuDNN) [Cheng et al. 2017 DATE].
https://past.date-conference.com/proceedings-archive/2017/pdf/7025.pdf

### 1.4 Availability

TrueNorth is not commercially available and has not been in active production since the mid-2010s research/DARPA SyNAPSE program era; it was distributed only to a limited research ecosystem (>30 universities, national labs, and corporate research centers per Sawada et al. 2016) via NS1e/NS16e development boards. It is effectively discontinued as a product; IBM's active successor effort is NorthPole (below).

### 1.5 IBM NorthPole (2023) — neuromorphic or digital NPU?

NorthPole (Modha et al., "Neural inference at the frontier of energy, space, and time," Science, Oct 2023) is explicitly described by IBM as a "brain-inspired" architecture that is nonetheless a **purely digital, low-precision (8-/4-/2-bit), spatial-dataflow inference accelerator with no spiking/event-driven neuron model and no membrane potential dynamics.** It is architecturally a descendant of TrueNorth (Modha calls it "an extension of TrueNorth") in the sense of eliminating off-chip memory and co-locating memory with compute, but it does not use spikes, ticks, or an IF/LIF neuron abstraction; it is a conventional (non-spiking) digital neural-network inference chip organized as a 16×16 array of cores linked by two on-chip networks-on-chip, executing standard 8-bit MAC-style operations (with 4-bit and 2-bit modes) rather than event-driven synaptic operations. NorthPole should be classified as a digital in/near-memory NPU inspired by brain architecture principles (data locality, distributed memory), not as a spiking neuromorphic chip. This distinction matters for this thesis because NorthPole's efficiency gains derive from memory-locality and low-bit-precision MAC execution, not from event-driven/temporal sparsity as in TrueNorth, Loihi, or the FPGA/ASIC SNN accelerators discussed below.
https://www.science.org/doi/10.1126/science.adh1174
https://research.ibm.com/blog/northpole-ibm-ai-chip

NorthPole specs (12 nm process, 22 billion transistors, 795–800 mm², 256 cores, 192 MB distributed SRAM, up to 2,048/4,096/8,192 int8/int4/int2 ops per core per cycle at nominal 400 MHz): E1, physical fabricated chip, deployed as a PCIe card, measured against GPU/CPU baselines on ResNet-50 and YOLOv4 (25× higher FPS/W, 5× higher FPS/transistor, 22× lower latency vs. a comparable-node GPU). This is genuine measured silicon performance, but for a non-spiking digital inference chip, out of scope for direct comparison to the IF/rate-coded SNN hardware this survey otherwise covers.
https://research.ibm.com/publications/ibm-northpole-an-architecture-for-neural-network-inference-with-a-12nm-chip

---

## 2. Tsinghua Tianjic / Lynxi

### 2.1 Tianjic (Pei et al., Nature 2019)

Tianjic ("Towards artificial general intelligence with hybrid Tianjic chip architecture," Pei, Deng, Song, Zhao, et al., Nature 572, 106–111, 2019) is a many-core, reconfigurable hybrid chip explicitly designed to run **both** computer-science-oriented ANNs and neuroscience-oriented SNNs on the same silicon, using a shared cross-paradigm building-block abstraction (axon, synapse, dendrite, soma, router) that lets synapse/dendrite hardware be shared between ANN and SNN modes while axon/soma are independently reconfigurable per-core (FCore). Time model: SNN layers use spike-event/temporal dynamics with membrane-potential integration, threshold crossing and reset; ANN layers instead accumulate weighted activations and refresh every cycle (no persistent temporal state). A key architectural feature: some FCores can be configured in "ANN mode" to relay full-precision (non-spiking) membrane potentials between dendritic compartments rather than communicating via binary spikes, which the authors show improves large-scale-SNN accuracy by 11.5 percentage points relative to an SNN-only configuration with equal neuron count, at negligible extra hardware overhead — i.e., hybrid intra-network fusion, not merely co-location of separate ANN and SNN subnetworks.
https://www.nature.com/articles/s41586-019-1424-8.epdf
https://aiichironakano.github.io/cs596/Pei-ArtificialGeneralIntelligenceChip-Nature19.pdf

**Demonstrated system (E1, physical chip):** a single Tianjic chip drove an unmanned bicycle performing simultaneous real-time object detection, tracking, voice-command recognition, obstacle avoidance, and balance control — a genuine hardware-in-the-loop robotics demonstration, not simulation. The paper also reports throughput improvements of 1.6×–10²× and power-efficiency improvements of 12×–10⁴× over GPU baselines for the networks tested, in a streaming execution mode.
https://www.nature.com/articles/s41586-019-1424-8.epdf

Tsinghua's own release notes state Tianjic (2nd generation, 2017, described in the 2019 Nature paper) offers, versus IBM TrueNorth: more comprehensive functionality/flexibility, 20% higher density, 10× higher speed, 100× higher internal bandwidth, and ships with a first-generation automatic model-mapping/compiling toolchain. This is a self-reported comparative claim from the Tsinghua press release, not an independently verified benchmark; treat as vendor/developer claim, not measured comparison. Collaborating institutions on the paper include Beijing Lynxi Technologies (the commercial spinout, see below), Beijing Normal University, SUTD, and UC Santa Barbara.
https://www.tsinghua.edu.cn/en/info/1244/3005.htm

### 2.2 Lynxi commercial products (KA200 / HP300) and BIDL toolchain

**Lynxi (灵汐科技)** is the commercial spinout building on the Tianjic lineage. Its "领启" (Lingqi) KA200(-S) chip is described as based on a compute-in-memory, many-core-parallel, heterogeneous-fusion architecture, natively supporting both deep-learning ANNs and brain-inspired SNNs, with mixed-precision compute (48 TOPS@INT8, 24 TFLOPS@FP16 per the KA200 product page). A single KA200 chip integrates 250,000 neurons / 25,000,000 synapses in dense mode, scaling to 2,000,000 neurons / 2,000,000,000 synapses in sparse mode.
https://lynxi.com/lq2001/18.html

**HP300** accelerator card carries 3× KA200 chips; product-page figures diverge slightly across two cited Lynxi documents — one gives 144 TOPS@INT8 / 72 TFLOPS@FP16 at ≤70 W peak board power, another (PDF datasheet) gives 96 TOPS@INT8 / 48 TFLOPS@FP16 at 65–68 W — likely reflecting different KA200 revisions (KA200 vs. KA200-S) or firmware/clock configurations; both are vendor datasheet figures, not independently measured (E3, documented product spec, no independent benchmark located). Framework support listed: DNN frameworks TensorFlow/PyTorch/PaddlePaddle/Caffe/MXNet/Keras/ONNX; SNN frameworks "Nengo, Neuron" (HP300 PDF) or generically "Neuron, etc." (product page).
https://www.lynxi.com/ka2003/21.html
https://quanai200dk-1258994165.cos.ap-shanghai.myqcloud.com/lynxi/HP300%E7%B1%BB%E8%84%91%E8%AE%A1%E7%AE%97%E6%9D%BF%E5%8D%A1.pdf

**BIDL (Brain-Inspired Deep Learning)** is Lynxi's open-source (GitHub: LynxiTech/BIDL) PyTorch-based training and deployment framework, jointly developed with the Nanhu Research Institute. It supports LIF and "LIF+" neuron models (spike-firing and analog-value-firing variants), hybrid ANN+SNN "DSNN" networks (interleaving Conv/BN/pooling ANN layers with ConvLIF/ConvLIAF spatiotemporal SNN layers, directly analogous to a ResNet/VGG backbone with SNN layers inserted for temporal processing), VGG-like/ResNet-like/Transformer-like/YOLOv5-like topologies, and both internal-iteration (GPU-friendly) and external-iteration (chip-native, timestep-driven) execution modes reconciled via a state-variable computational graph. Compilation to hardware goes through the "Lyngor" compiler, execution through "LynSDK" (C++/Python). Supported deployment targets: SL800 (server), HP280/HP300 (accelerator cards), HS100/HS110/HS120 (edge boxes), HM100 (chip module). Training requires a GPU; only inference targets the Lynxi chips (batch size B=1 only on-chip).
https://github.com/LynxiTech/BIDL
https://bidl-user-manual.readthedocs.io/en/latest/overview.html
https://pmc.ncbi.nlm.nih.gov/articles/PMC10410154/ (BIDL, Frontiers/PMC paper, describes DSNN design flow, video/DVS/3D-medical/NLP experiments, "deployed in the brain-inspired chip Lynchip KA200")

**Time model on Lynxi hardware:** per the BIDL documentation, "most brain-inspired chips operate in a timestep driven manner, where a timestep iteration is located outside the neural network" — i.e., the device computes all layers for one timestep, then advances, in contrast to GPU-style SNN frameworks (e.g., SpikingJelly) that keep the timestep loop inside each layer for parallelism. This confirms Lynxi/Tianjic-lineage hardware is fundamentally clock/timestep-driven, matching the IF/LIF-with-explicit-timestep execution model this thesis's SNN pipeline assumes, though BIDL's LIF/LIF+ default is leaky-integrate-and-fire, not the reset-by-subtraction IF specifically used in QCFS-style conversion (BIDL supports custom user-defined neuron classes, so a QCFS-style IF module could in principle be mapped, but no such mapping is documented in the sources retrieved).
https://bidl-user-manual.readthedocs.io/en/latest/principle_explanation.html

**Availability outside China:** NOT FOUND. No evidence in the retrieved sources of Lynxi HP300/KA200/HM100 hardware being sold, distributed, or benchmarked by any group outside mainland China; product pages and the Nanhu Research Institute cloud-image access route ("nanhubrain@cnaeit.com") are China-facing. Treat Lynxi hardware access as effectively unavailable to this thesis's development environment absent further evidence.

**Published deployments with measured results (E1):** DVS gesture recognition, video-clip processing, 3D medical imaging classification, and NLP tasks are reported as BIDL experiments demonstrating accuracy and computational-cost reduction versus Conv3D/ConvLSTM baselines, with the note that results "have been deployed in the brain-inspired chip Lynchip KA200" — but the retrieved sources do not tabulate specific latency/energy/power numbers measured on physical Lynxi silicon; the PMC paper's efficiency claims are framed at the algorithm/computation-count level (FLOPs/MACs saved) rather than as board-measured watts or milliseconds. Classify as E3 (documented deployment, computational-cost comparison only) pending a source with hardware-measured numbers.
https://pmc.ncbi.nlm.nih.gov/articles/PMC10410154/

---

## 3. Innatera

Innatera (Delft, Netherlands) is **explicitly out-of-scope-adjacent to Akida** but distinct and in-scope. Its product line:

- **SNP T1** ("Spiking Neural Processor T1"): the company's first integrated SNN SoC, sampled to lead customers starting early 2024. Integrates an **analog/mixed-signal** SNN accelerator (described by CEO Sumeet Kumar as "a sea of programmable neurons and synapses," functionally an analog-FPGA-like fabric) alongside a small RISC-V CPU (CV32E40P core) and a small CNN accelerator, plus sensor interfaces (QSPI, I2C, UART, JTAG, GPIO, AER, front-end ADC).
https://www.eetimes.com/innatera-productizes-snn-accelerator-as-neuromorphic-microcontroller/
https://flagship.kip.uni-heidelberg.de/jss/HBPm?m=displayPresentation&mEID=9649&mI=263

- **Pulsar**: the commercial (2Q25 production) second-generation, "world's first mass-market neuromorphic microcontroller." Mixed-signal: it integrates **both** an analog SNN engine (capacitor-based neuron-state storage, 16K-parameter capacity, four independently-processed array segments to mitigate cross-die transistor-mismatch) **and** a separate digital SNN engine (49K-parameter capacity, same design principles implemented digitally, for longer-timescale/state-retention applications), plus a 32-MAC/cycle INT8 CNN accelerator, an FFT/IFFT accelerator, and a CV32E40P RISC-V core (≤160 MHz). Process: TSMC 28 nm. Die: 2.8×2.6 mm, 36-pin WLCSP package. Power: 10 mW max, ~0.5 mW typical; claimed 100× lower latency and 500× lower energy vs. conventional digital AI accelerators (vendor claim). Temperature range -40 to +125°C.
https://xpu.pub/2025/07/22/innatera-pulsar/
https://www.innatera.com/newsroom/innatera-unveils-pulsar-the-worlds-first-mass-market-neuromorphic-microcontroller-for-the-sensor-edge/
https://open-neuromorphic.org/neuromorphic-computing/hardware/pulsar-by-innatera/

**Talamo SDK:** PyTorch-extension-based SNN development stack. Provides spike encoders/decoders (e.g., an `IFEncoder`, i.e., encoding is done with an integrate-and-fire process, not necessarily rate coding by default — the retrieved documentation shows an `MFCC → IFEncoder → Snn → MaxRateDecoder` pipeline, implying rate-style *decoding* at the output but encoder-side IF-based spike generation), a PyTorch `Snn` container, and a device-deployment API (`pipe.to(innatera_soc)`) that compiles PyTorch-defined SNNs directly onto the T1/Pulsar hardware without requiring the developer to understand chip internals.
https://www.innatera.com/software-and-tools/

**Target applications:** always-on sensing at the edge — audio/keyword spotting, radar, motion, vibration, infrared — for wearables, IoT, and industrial systems, emphasizing sub-millisecond response at microwatt power for "wake-up"/trigger-style always-on tasks rather than deep image classification.

**Published benchmarks:** NOT FOUND — no third-party, peer-reviewed benchmark of T1 or Pulsar (latency/energy/accuracy on a named public dataset, independently measured) was located in this search. All quantitative claims retrieved (100× latency, 500× energy reduction; "five generations of test chips") are vendor-sourced (company statements to trade press, EE Times/XPU.pub/company site), not independent academic evaluation. Classify Innatera hardware claims as **E3** (documented product with a defined deployment path) rather than E1/E2 until an independent, dataset-referenced benchmark is found.

**Availability:** Pulsar is in production as of 2Q25 (per XPU.pub), sold as a discrete MCU-class part; T1 was distributed as engineering/evaluation silicon to lead customers from early 2024. Both are commercially orderable (Innatera advertises developer kits and a developer program), unlike Lynxi.

---

## 4. Academic / research ASICs

### 4.1 ODIN (UCLouvain, Frenkel et al., 2018/2019)

"A 0.086-mm² 12.7-pJ/SOP 64k-Synapse 256-Neuron Online-Learning Digital Spiking Neuromorphic Processor in 28-nm CMOS," Frenkel, Lefebvre, Legat, Bol, IEEE TBioCAS 2019 (arXiv 1804.07858). Single 256-neuron, 64k-synapse crossbar core, 28 nm FDSOI CMOS, 0.086 mm². Embeds the spike-driven synaptic plasticity (SDSP) online-learning rule at 0.68 μm² per 4-bit synapse — i.e., online learning is a first-class design goal, unlike TrueNorth/Tianjic/Innatera. Neurons independently configurable as standard LIF or a custom phenomenological model reproducing all 20 Izhikevich behaviors, entirely event-driven (no per-timestep update requirement for the Izhikevich mode).

**Measured results (E1, 9 fabricated chips tested):** minimum energy per synaptic operation (SOP) 12.7 pJ at 0.55 V (accelerated-time regime, 75 MHz max clock at 0.55 V vs. 100 MHz at nominal 0.8 V); incremental SOP energy 8.43 pJ; at biological-time firing rates (~10 Hz/neuron) energy per SOP rises to 54 pJ (leakage-dominated, 78% of power). On a single presentation of 6k 16×16 MNIST training images to a single-layer 10-neuron fully-connected network with on-chip SDSP learning: 84.5% classification accuracy, 15 nJ/inference at 0.55 V using rank-order coding.
https://arxiv.org/abs/1804.07858
https://github.com/ChFrenkel/ODIN (open-source HDL)

### 4.2 ReckOn (UZH/ETH Zurich, Frenkel & Indiveri, ISSCC 2022)

"ReckOn: A 28-nm Sub-mm² Task-Agnostic Spiking Recurrent Neural Network Processor Enabling On-Chip Learning over Second-Long Timescales" (arXiv 2208.09759). Spiking RNN processor, 0.45 mm² core, 28 nm FDSOI, up to 256 LIF neurons with all-to-all input+recurrent connectivity via 8-bit weights (two 64 kB SRAMs). Implements a modified feed-forward-eligibility-trace approximation to e-prop/BPTT that is local in space and time, enabling on-chip supervised learning over second-long timescales at millisecond temporal resolution with only 0.8% memory overhead vs. an inference-only design.

**Measured results (E1, 5 fabricated chips):** peak efficiency 5.3 pJ/SOP at 0.5 V. Demonstrated end-to-end on-chip learning on three benchmarks: DVS Gestures (spiking-retina input) — 87.3% accuracy, 10-class hand-gesture classification; Spiking Heidelberg Digits (spiking-cochlea input) — 90.7% accuracy, 1-word keyword spotting; synthetic rodent-navigation task — 96.4% accuracy binary-decision navigation. Nominal 0.8 V/115 MHz supports 37×–600× accelerated-time processing of pregenerated datasets; at 0.5 V/13 MHz, 4×–98× acceleration within 150 μW (learning) / 80 μW (inference) budgets, or real-time on-the-fly processing of neuromorphic-sensor spikes within 46 μW (learning) / 20 μW (inference). Energy per processing step: 0.6–42 nJ (inference), 1.5–178 nJ (learning) at 0.5 V.
https://arxiv.org/pdf/2208.09759
https://github.com/ChFrenkel/ReckOn (open-source HDL)

### 4.3 SENECA / SENeCA (imec, RISC-V-based digital neuromorphic processor)

SENECA ("Scalable Energy-efficient Neuromorphic Computer Architecture") is imec's fully-digital, RISC-V-based neuromorphic processor with a hierarchical-controlling design: each core pairs a flexible RISC-V controller with an optimized "loop buffer" controller and vector-like Neuron Processing Elements (NPEs), aiming to balance flexibility (programmable neuron models, on-device learning, pre/post-processing) against efficiency.
https://doi.org/10.3389/fnins.2023.1187252 (Tang et al. 2023, Frontiers in Neuroscience, full architecture paper)
https://doi.org/10.1109/aicas54282.2022.9870025 (Yousefzadeh et al. 2022, original SENeCA architecture paper)

**Status: NOT yet fabricated as of the retrieved sources.** A SENECA core "consumes 0.47 mm² when *synthesized* in the GF-22nm technology node and consumes around 2.8 pJ per synaptic operation" — this is a **synthesis result**, not measured silicon. A TU Delft MSc thesis on SENECA benchmarking explicitly states: "Since no physical chip implementation of SENeCA exists at the time of writing, the program was run on SENeCA using a HDL simulator ... the power consumption of SENeCA ... was measured using a power estimation software." This confirms SENECA is **E4** (RTL/synthesis + power-estimation-tool modeling), not physical silicon, across all retrieved sources.
https://doi.org/10.3389/fnins.2023.1187252
http://resolver.tudelft.nl/uuid:3b6a47f2-bde5-4652-8e6a-8fb6155a4740

Reported synthesis/simulation-based efficiency figures: 2.8 pJ/SOP (with data-reuse optimization) at the instruction level; a design-space-exploration paper (Xu et al. 2024, Frontiers) reports layer/algorithm-level optimizations (spike-grouping, event-driven depth-first convolution) yielding 6×–300× energy improvement, 3×–15× latency improvement, and 3×–100× area-efficiency improvement versus other neuromorphic/conventional accelerators, again via synthesis/simulation, not fabricated chip measurement.
https://doi.org/10.3389/fnins.2024.1335422

### 4.4 MorphIC (UCLouvain, Frenkel et al., 2019, ISCAS)

"MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning" (arXiv 1904.08513). Quad-core, 65 nm CMOS, 2.86 mm² active area (3.50 mm² incl. pads), 2,048 LIF neurons, >2M binary (1-bit) plastic synapses (738k synapses/mm² density), embedding a stochastic SDSP (S-SDSP) online-learning rule and a hierarchical routing fabric intended for large-scale multi-chip interconnection.

**Measured results (E1, fabricated in UMC 65 nm LP CMOS):** Energy per SOP 30 pJ at 0.8 V / 65 pJ at 1.2 V; max clock 55 MHz (0.8 V) / 210 MHz (1.2 V). On MNIST with offline-trained binary weights: 97.8% test accuracy using conventional rate coding, at 205 μJ per classification (0.8 V, 55 MHz) — the high energy cost is attributed explicitly to rate coding's inefficient spike use. Switching to **rank-order coding** (class inferred from which output neuron spikes first) drops energy to 21.8 μJ per classification (a 10× improvement) at the cost of 1.9 percentage points of accuracy (down to ~95.9%), at 5.45 mW average power for 250 classifications/second. This is a directly relevant data point for this thesis: on real fabricated neuromorphic silicon, rate coding is measured to cost roughly an order of magnitude more energy than rank-order (first-spike) coding for equivalent accuracy.
https://doi.org/10.48550/arxiv.1904.08513

### 4.5 μBrain (uBrain, event-driven fully-synthesizable SNN ASIC — not to be confused with the unrelated "uBrain" EEG-BCI accelerator, section 4.6)

"μBrain: An Event-Driven and Fully Synthesizable Architecture for Spiking Neural Networks" (Frontiers in Neuroscience, 2021). A fully digital, **clockless** (no global clock; local on-demand oscillators plus a custom delay-cell mechanism) event-driven SNN IC, 40 nm CMOS, 2.82 mm² including pads (1.42 mm² core), designed for <100 μW always-on edge/IoT inference with co-located memory and computation (no separate on- or off-chip memory blocks). Prototype network: 336 neurons (256-neuron recurrent fully-connected reservoir layer at ~30% random connectivity + two fully-connected 64/16-neuron readout layers), 4-bit weights, 37,366 total synapses.

**Measured results (E1, fabricated 40 nm prototype):** radar-based hand-gesture classification at 70 μW power, 340 nJ per classification. MNIST (ANN-trained-then-converted to SNN, using an ISI/inter-spike-interval readout and a ReLU-to-accumulator-wraparound mapping "to ease ANN to SNN conversion" — directly relevant methodologically): 93.4% accuracy, 340 nJ/classification (Table 1 in the paper reports 308 nJ/MNIST-classification as the headline comparison figure), average per-classification time 4.2 ms at input frequencies of 100 Hz–655 kHz. Comparison table in the paper positions μBrain (73 μW) against ODIN (35–447 μW), a 10.08 mm² unnamed chip (23.6 mW), a 2.56 mm² 4,096-neuron design (46.6 mW, 2.3 μW/neuron), a 1.7 mm² chip (94 mW), an analog-mixed-signal design (400 μW at 10 Hz average firing rate, explicitly the only entry in the table that is NOT fully synthesizable), and a 60 mm² chip (110 mW) — μBrain is reported as the smallest and lowest-power fully-digital, fully-synthesizable entry in that specific comparison set.
https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2021.664208/full

### 4.6 uBrain (unary-computing EEG/BCI accelerator — distinct from μBrain above)

"uBrain: A Unary Brain Computer Interface," Wu, Li, Pan, Kim, San Miguel, ISCA 2022. This is a **different, unrelated design** using stochastic/unary computing (not spiking neurons in the IF/LIF sense) for EEG-based brain-computer-interface DNN inference (cascaded CNN+RNN), evaluated only against CPU/systolic-array/stochastic-computing baselines, not physical fabricated silicon in the retrieved sources — the paper reports simulated/estimated on-chip power efficiency (9.0×, 6.2×, 2.0× improvements vs. CPU/systolic/stochastic baselines respectively), not a measured fabricated ASIC. Classify **E4/E5** (architectural simulation/estimation, not spiking-neuron hardware, and out of direct scope for this thesis's IF/rate-coding focus; included here only to disambiguate the name clash with μBrain above, since both appear in neuromorphic-adjacent literature under near-identical names).
https://doi.org/10.1145/3470496.3527401
https://jsm.ece.wisc.edu/docs/wu-isca2022.pdf

### 4.7 Mixed-signal analog academic ASICs (DYNAP-SE2, for context)

A 2025 Scientific Reports paper ("Event driven neural network on a mixed signal neuromorphic processor for EEG based epileptic seizure detection," Bartels, Gallou, et al.) validates a two-layer SNN on the DYNAP-SE2 mixed-signal (analog front-end + asynchronous digital routing) neuromorphic chip, entirely on-chip signal conditioning + spike encoding + SNN inference (classification is done off-chip with a linear classifier on the SNN's output spikes). Measured/estimated power: 150 μW average across patients (2.8 μW per input channel) at 1.8 V supply. This is **E1/E2 hybrid**: the SNN computation itself and the analog front-end are measured on fabricated silicon, but the final classification stage is off-chip, and the power figure is described as "estimated" from measured firing rates rather than directly wall-plug-measured, so treat as E2-leaning-E1 (physical chip, computed/estimated rather than directly instrumented power).
https://doi.org/10.1038/s41598-025-99272-6

---

## 5. FPGA SNN accelerators — faithfulness to IF+reset-by-subtraction+rate coding, and measurement type

### 5.1 SyncNN (Panchapakesan, Fang, Li; FPL 2021 / ACM TRETS 2022)

Explicitly targets **rate-encoding-based SNNs using the IF model**, and explicitly implements reset-by-subtraction: the paper's own neuron-encoding pseudocode subtracts the threshold voltage from the membrane potential on spike (`Vm[o] -= Vth`), and states directly: "we focus on the IF model: the membrane potential is just added or subtracted by the weight of the connection ... and is reset immediately once it reaches the threshold value," with Poisson-based rate encoding of the input image. SyncNN's core contribution is a mathematically-proven-equivalent *synchronous* reformulation: instead of stepping the whole network T timesteps, only the input (Poisson) encoding layer runs for the full T-step encoding window; all downstream layers run **once**, aggregating the full T-step membrane-potential contribution in one shot and computing the equivalent spike count via `Vm / Vth` division rather than iterative threshold-and-subtract — proven mathematically equivalent to the standard multi-timestep asynchronous IF execution. T (the "encoding window"/number of simulation steps) is dataset/network-dependent and not fixed in the paper; small networks (LeNet, MLP) need a small window, larger networks (NiN, VGG) need a much larger one, and this dependency is exactly the bottleneck SyncNN's synchronous reformulation is designed to remove from the downstream layers (input-layer Poisson encoding still needs the full T).

**Measured (E1, Xilinx ARM-FPGA SoC boards — ZCU102, ZCU104, ZED):** 99.6% accuracy and 13,086 FPS on MNIST (the paper's headline state-of-the-art throughput claim); also evaluated on SVHN and CIFAR-10 using LeNet, Network-in-Network, and VGG architectures, with 16/8/4-bit weight quantization. Deployed and measured across three real FPGA boards (hardware mode built via Vitis HLS/SDSoC), not just synthesis estimates.
https://doi.org/10.1145/3514253
https://www.sfu.ca/~zhenman/files/C21-FPL2021-SyncNN.pdf
https://github.com/SFU-HiAccel/SyncNN

### 5.2 Spiker / Spiker+ / Spiker-LL (Politecnico di Torino, Carpegna, Savino, Di Carlo)

**Spiker** (ISVLSI 2022) uses a **Leaky Integrate-and-Fire (LIF)** neuron, not the pure IF model this thesis's QCFS-style conversion targets, and is **clock-driven** (membrane potential updated every clock cycle even absent input spikes, an explicit design trade-off favoring simplicity over pure event-driven sparsity savings). Trained offline via unsupervised STDP (not ANN-to-SNN conversion) on MNIST with a single 400-neuron layer.
https://export.arxiv.org/pdf/2201.06993v3.pdf

**Measured (E1, synthesized on Xilinx Artix-7 FPGA, physical board):** 215 μs/image computation time (fastest among accelerators compared in the paper, at a normalized 100 MHz), 13 mJ/image energy (slightly higher than the most energy-optimized competitor), ~55% LUT / 25% FF / 32% BRAM utilization for a single-layer 400-neuron network.

**Spiker+** (IEEE TETC 2024) generalizes the framework to a configurable multi-layer architecture with a library of **six neuron models: IF, first-order LIF, and second-order LIF, each with a choice of hard or subtractive (reset-by-subtraction) reset** — i.e., Spiker+ is the first accelerator in this survey to offer reset-by-subtraction as an explicit, named, user-selectable configuration option, directly matching the QCFS-style IF-with-reset-by-subtraction neuron this thesis uses. Supports BPTT-trainable (via snnTorch) as well as offline-trained networks.

**Measured (E1, Xilinx FPGA, physical synthesis+deployment):** MNIST — 93.85% accuracy, 780 μs/image latency (using a 100-timestep encoding window), 180 mW, 7,612 logic cells + 18 BRAMs. Spiking Heidelberg Dataset (SHD) — 72.99%/75% accuracy (two papers give slightly different figures), 540 μs (2024 arXiv version) or 54 μs (TETC abstract states differently — discrepancy present across the two source documents, flagged rather than resolved), 430 mW, 18,268 logic cells + 51 BRAMs. AudioMNIST: 95% accuracy, 290 mW, 10,124 logic cells + 16 BRAMs.
https://doi.org/10.1109/tetc.2024.3511676
https://arxiv.org/html/2401.01141v1

**Spiker-LL** (2026 arXiv) extends Spiker+ with on-device local learning (STSF rule) rather than inference-only; up to 93% accuracy, sub-millisecond latency, <0.1 mJ/inference, DSP-free, on MNIST/Fashion-MNIST/DIGITS — again E1, FPGA-measured.
https://arxiv.org/html/2605.18003

### 5.3 FireFly / FireFly v2 (BrainCog Lab / Chinese Academy of Sciences, Li, Shen, Zhao, Zhang, Zeng)

Targets a generalized "multiplex-accumulate" operation for LIF-type spiking dynamics, mapped efficiently onto Xilinx UltraScale DSP48E2 hard blocks. FireFly v1 explicitly notes it does *not* include the direct/analog input-coding layer in its measured inference latency (a caveat the authors flag directly when comparing to v2, which does measure end-to-end including coding). No explicit statement was found in the retrieved excerpts that FireFly implements reset-by-subtraction specifically (as opposed to hard reset) — **NOT FOUND** in the retrieved text; the neuron-dynamics description given (`τm du/dt = -u + R·I(t), u < Vth`) is a generic LIF ODE without reset-mode detail visible in the excerpt.

**Measured (E1, physical FPGA boards — Zynq UltraScale+ edge devices xczu3eg/xczu5ev/xczu7ev):** FireFly v1 peak performance 1,382.4 GOP/s (144×16 array) to 5,529.6 GOP/s (288×32 array) at 300 MHz, evaluated on MNIST, CIFAR-10, CIFAR-100, DVS-Gesture, and other datasets on off-the-shelf edge FPGA boards. FireFly v2 (TCAD 2024) raises clock to 500–600 MHz (highest reported clock among FPGA SNN accelerators surveyed), doubling throughput/DSP-efficiency vs. v1, with a spatiotemporal dataflow that eliminates membrane-potential storage entirely (spikes generated on-the-fly); peak power efficiency 835.9 GOP/s/W at 4.9 W (KV260 board), peak throughput 8,192 GOP/s (ZCU104). FireFly v2 is also, per the authors, the first SNN accelerator supporting "non-spike operations" used in some SOTA SNN training algorithms — i.e., not restricted to pure binary-spike dataflow.
https://doi.org/10.1109/tvlsi.2023.3279349
https://doi.org/10.1109/tcad.2024.3380550

### 5.4 Cerebron (Chen, Gao, Fu; TVLSI 2022)

Targets **converted** SNNs explicitly: "Conversion of DNNs to SNNs is a more straightforward way to obtain an SNN with equivalent accuracy to the DNN... we use an open-source SNNtoolbox [Rueckauer et al. conversion methodology]." This is the clearest FPGA accelerator in this survey explicitly built around the ANN-to-SNN conversion literature (Rueckauer/Diehl-style), rather than direct SNN training. Architecture: a reconfigurable compute engine (inter- and intra-compute-unit reconfiguration) targeting spatiotemporal sparsity in both standard, depthwise, and pointwise convolutions, plus an online channel-wise workload-scheduling mechanism to balance the irregular workload caused by dynamic spike sparsity.

**Measured (E1, Xilinx XC7Z100 FPGA, 200 MHz, physical implementation):** MNIST ConvNet — 99.40% accuracy, 0.026 ms/image, 0.04 mJ/image (best-in-class among the designs Cerebron itself tabulates, including versus FireFly per FireFly's own comparison). CIFAR-10 (thinner-MobileNet variant) — 91.90% accuracy, 10.63 ms/image, 14.88 mJ/image. Lane-segmentation SegNet (MLND-Capstone driving dataset) — 97.30% accuracy, 0.80 ms/image, 1.12 mJ/image. Claims ≥17.5× prediction-energy reduction and ≥20× speedup vs. prior SOTA FPGA SNN accelerators (self-reported comparison). Effective SOP throughput after sparsity/scheduling optimizations: 40.1–45.0 GSOP/s across the three network/dataset combinations, up from a 50 GOP/s theoretical peak baseline before optimization (13× speedup from combined sparsity exploitation + workload scheduling).
https://doi.org/10.1109/tvlsi.2022.3196839
https://repository.tudelft.nl/file/File_9e4815fd-0e65-4d94-b3ab-b54ad68d91ad

### 5.5 Other FPGA designs noted but not deeply investigated

- **DeepFire2**: referenced repeatedly as the strongest prior-art comparison point for FireFly v2 (larger xcvu9p FPGA); not independently searched in this pass — NOT FOUND (own primary source not retrieved; only cited via FireFly v2's comparison table).
- **A Robust, Open-Source Framework for SNNs on Low-End FPGAs** (2025 arXiv, im-afan/snn-fpga): targets low-end Xilinx Artix-7 (Digilent Basys3), no-leak IF neurons, strictly synchronous computation (explicitly no non-spiking speedup — i.e., does not exploit spike sparsity for performance, unlike SyncNN/Cerebron). Measured (E1, physical low-end board): MNIST (784-128-10 network), 0.52 ms/image, 0.381 W, 0.198 mJ/image, 6,358 LUTs + 40.5 BRAM (SNN portion only), 100 timesteps.
https://arxiv.org/html/2507.07284
- **HyNITA** (ISCAS 2025) and **PAICORE** (JSSC 2024): hybrid ANN-SNN training+inference accelerators cited in the same literature cluster; not deeply investigated in this pass (out of the requested SyncNN/Spiker/FireFly/Cerebron/PASCAL focus list) — flagged as candidates for a follow-up pass if the survey needs broader hybrid-ANN-SNN hardware coverage.
https://doi.org/10.1109/iscas56072.2025.11043533

---

## 6. Custom RTL / ASIC designs specifically for converted / low-timestep SNNs

### 6.1 PASCAL (Ramesh & Srinivasan, arXiv 2505.01730)

**Important correction to the task's framing:** the PASCAL paper itself (arXiv 2505.01730, "Precise and Efficient ANN-SNN Conversion using Spike Accumulation and Adaptive Layerwise Activation") does **not** perform RTL synthesis or cycle-accurate hardware simulation. PASCAL is a **software/algorithmic** contribution: it proves a mathematically exact equivalence between an ANN with QCFS activation and a converted SNN using a spike-accumulation/spike-inhibition IF neuron with soft reset ("PASC-IF"), reducing required inference timesteps from ~1024 (for QCFS on ImageNet-scale problems) down to values dependent only on network structure (T = L per layer), and separately proposes an "Adaptive Layerwise" (AL) method for choosing per-layer quantization step L. Its "hardware efficiency" results are an **analytical energy model** (counting AC/MAC operation ratios per layer, e.g., `E_PASC_IF ≈ (5L-2)·E_IF`), not a synthesized circuit or cycle-accurate simulator. On ResNet-34/ImageNet, PASCAL reports ≈74% accuracy with a 56×–64× reduction in inference timesteps versus prior QCFS-based conversion (two slightly different multiplier figures appear across the arXiv v1 HTML and the DOI-indexed abstract — 64× in the HTML version, 56× in the abstract metadata, likely reflecting a revision between preprint versions). PASCAL's neuron uses **soft reset** (not the standard hard/subtractive reset used elsewhere in this survey) and explicitly relies on **inhibitory (negative) spikes**, a departure from the binary-only spike convention used in TrueNorth/most FPGA accelerators surveyed above. Classify PASCAL itself as **E5/E4-borderline** (analytical energy model derived from operation counts, not measured on any real or synthesized circuit).
https://arxiv.org/html/2505.01730v1
https://doi.org/10.48550/arxiv.2505.01730
https://github.com/BrainSeek-Lab/PASCAL

### 6.2 APEX — the actual RTL/hardware realization of PASCAL's neuron (arXiv 2608.19046)

APEX ("A Dual-Sparsity Accelerator for Precise and Efficient SNN Inference," 2026 arXiv) is the paper that does what the task description attributes to PASCAL: it takes the PASC-IF neuron from PASCAL and integrates it into the LoAS accelerator framework, implementing the three-stage PASC-IF spike-generation datapath as a fully combinational circuit (exploiting LoAS's fully-temporal-parallel dataflow, which resolves the entire post-synaptic input tensor across all T timesteps before invoking the neuron unit, removing the temporal loop-carried dependency that would otherwise force sequential PASC-IF execution). APEX additionally supports mixed-precision (INT4/INT8) execution via a split processing-element array and exploits dual sparsity (both spikes and weights).

**Hardware evaluation (E4 — RTL synthesis + cycle-level simulation, not fabricated silicon):** "APEX is implemented in RTL and synthesized using Synopsys Design Compiler at 400 MHz on 40 nm CMOS technology," 16 TPPEs (split INT4/INT8), 256 KB double-buffered global cache, 128 GB/s HBM off-chip model. Evaluated at T ∈ {4, 8, 16} timesteps and INT4/INT8 weight precision, compared against the LoAS baseline (with a standard, non-PASC IF neuron) at matched configurations. Reported overhead of the PASC-IF neuron itself: 1.3%–5.4% power overhead, 2.1%–2.7% area overhead versus plain LoAS, for up to 3 percentage points higher accuracy on average. Concrete example: on a task where LoAS needs T=32 timesteps and still shows ~5% accuracy degradation, APEX (PASC-IF) reaches the target accuracy at T=8, consuming 69.23 mJ/inference vs. LoAS's 181.76 mJ/inference at T=32 (a 61.9% energy reduction) — and the paper states LoAS would require T=1024 to match APEX's accuracy, directly echoing the "56×–64× fewer timesteps" claim from the original PASCAL paper, now grounded in an actual synthesized-and-simulated hardware comparison rather than an analytical model alone.
https://arxiv.org/html/2608.19046

### 6.3 NeuroFlex — a second, independent RTL realization building on PASCAL (arXiv 2511.05215)

NeuroFlex ("a flexible ANN–SNN accelerator for sparse edge inference") extends PASCAL's layer-level lossless ANN/SNN equivalence to **column-level** hybrid execution — within a single layer, individual output columns can independently execute in ANN mode or SNN (PASC-IF) mode, chosen offline by a profiling-driven scheduler to maximize PE utilization, while preserving PASCAL's proof of exact equivalence (since the proof depends only on local per-neuron integer arithmetic). At L=8 quantization levels, the paper states lossless conversion requires (3L−1) = 23 timesteps under the PASCAL formulation, and stores all intermediate activations in a unified INT8 format regardless of ANN/SNN execution mode for a given column.

**Hardware evaluation (E4 — RTL synthesis + cycle-level simulation, not fabricated silicon):** "We implement key components of NeuroFlex and all baselines in RTL and synthesize with Synopsys Design Compiler at 560 MHz in 40 nm technology node. We use CACTI 7.0 to model the memory structures. We develop a Python cycle-level simulator..." Reports PE-array utilization of 98.6%–99.3% (VGG-16, ResNet-34, GoogLeNet) and 97.5% (BERT) under its cost-based column-scheduling algorithm, versus 71.0%–83.9% for coarser layer-wise hybrid scheduling and 91.8%–92.9% for random column assignment — demonstrating that fine-grained (column-level) ANN/SNN hybridization meaningfully improves hardware utilization over layer-level hybridization, though absolute latency/energy/power numbers beyond utilization percentages were not captured in the retrieved excerpt.
https://arxiv.org/html/2511.05215

### 6.4 Design Space Exploration of Sparsity-Aware Application-Specific SNN Accelerators (2310.16745)

Not built specifically for QCFS/PASCAL-style conversion, but directly relevant as a **methodological** template: a cycle-accurate, SystemC/TLM-based simulation-and-RTL-generation framework that automatically produces SystemVerilog RTL for a given SNN topology, synthesizes it via Xilinx Vivado onto a Virtex UltraScale+ FPGA (100 MHz) for area, and separately runs cycle-accurate SystemC simulation (validated by spike-to-spike comparison against snnTorch-trained reference spikes) for latency, varying a "logical-to-hardware neuron ratio" (LHR) design knob per layer. This is **E4** (RTL synthesis for area + cycle-accurate simulation for latency, not measured on a running chip/board), reporting up to 76% hardware-resource reduction and up to 31.25× speedup versus fixed-configuration prior FPGA SNN designs on MNIST/FashionMNIST/DVSGesture, by tuning per-layer hardware-neuron multiplexing ratios.
https://ar5iv.labs.arxiv.org/html/2310.16745

---

## Summary table — evidence class by substrate

| Substrate | Native IF? | Reset-by-subtraction? | Rate coding? | Strongest evidence class | Notes |
|---|---|---|---|---|---|
| TrueNorth | Constrained IF variant (23-param) | Not the primary mechanism; Eedn uses one-tick spatial spike-count, not multi-tick temporal accumulation | No (see §1.2 — Eedn is spatial population coding within one tick, not temporal rate coding) | **E1** (Esser 2016 PNAS, Sawada 2016 SC, Shukla 2019) | Discontinued; trinary weights via 4-axon-type LUT trick, not native |
| NorthPole | No (non-spiking digital NPU) | N/A | N/A | **E1** | Not a spiking substrate; out of direct scope despite "brain-inspired" framing |
| Tianjic | Yes (SNN-mode FCores) | NOT FOUND explicitly | Not specified in retrieved sources | **E1** (unmanned-bicycle demo) | Hybrid ANN+SNN fusion is the headline feature |
| Lynxi (KA200/HP300, BIDL) | LIF/LIF+ (custom neurons possible) | NOT FOUND explicitly | Not specified | **E3** (documented deployments, computational-cost claims, no tabulated board power/latency found) | Not available outside China per retrieved sources |
| Innatera (T1/Pulsar) | IF-based encoder (Talamo `IFEncoder`); underlying neuron circuit details proprietary | NOT FOUND | Decoder-side "MaxRateDecoder" implies rate-style output | **E3** (vendor claims only; no independent benchmark found) | Mixed analog+digital; commercially available |
| ODIN | LIF or custom Izhikevich-like | NOT FOUND explicitly (SDSP-driven reset behavior, not the standard IF hard/subtractive framing) | Rank-order coding used for the reported inference-energy figure | **E1** | Online learning (SDSP) is the design focus |
| ReckOn | LIF | NOT FOUND explicitly | Not applicable (e-prop-based) | **E1** | Online learning (e-prop) focus |
| SENECA | Programmable/RISC-V-defined | Configurable (user-defined) | Configurable | **E4** (no fabricated chip found in any retrieved source) | Explicitly stated "no physical chip implementation exists" in a 2022 TU Delft thesis |
| MorphIC | LIF | NOT FOUND explicitly | Yes — directly measured: rate coding costs ~10× more energy per classification than rank-order coding on the same fabricated chip | **E1** | Best directly-relevant silicon data point on the cost of rate coding vs. alternatives |
| μBrain | ReLU-to-accumulator-wraparound (ANN-to-SNN-conversion-friendly), ISI readout | Wraparound reset (accumulator overflow), not classic subtractive reset | ISI-based, not classic rate coding | **E1** | Explicitly designed to ease ANN-to-SNN conversion |
| SyncNN | Yes, explicit IF | **Yes, explicit** (`Vm -= Vth`) | **Yes, explicit** (Poisson rate encoding) | **E1** (multi-board FPGA measurement) | Closest FPGA match to this thesis's QCFS-style IF+reset-by-subtraction+rate-coding assumptions |
| Spiker | LIF | Hard reset (clock-driven, STDP-trained) | Not specified as rate coding | **E1** | |
| Spiker+ | IF, 1st/2nd-order LIF | **Yes, user-selectable hard or subtractive reset** | Not explicitly stated as rate coding | **E1** | First accelerator surveyed with reset-by-subtraction as a named configuration option |
| FireFly / v2 | LIF (generic ODE given) | NOT FOUND | NOT FOUND | **E1** | Highest clock frequency (500-600 MHz) among FPGA SNN accelerators surveyed |
| Cerebron | Converted via Rueckauer-style SNNtoolbox (implies IF, standard reset-by-subtraction per that toolbox's convention, not independently confirmed in Cerebron's own text) | Not explicitly restated in Cerebron's own text (inherited from SNNtoolbox) | Not explicitly restated (inherited from SNNtoolbox) | **E1** | Explicitly framed around ANN-to-SNN conversion (SNNtoolbox) |
| PASCAL (algorithm) | PASC-IF, explicit soft reset + inhibitory spikes | **No — soft reset, not subtractive/hard** | No (spike-count based, not rate coding) | **E5/E4-borderline** (analytical energy model only) | Not itself hardware; corrected from task's framing |
| APEX (PASCAL's RTL realization) | PASC-IF, soft reset | No (soft reset) | No | **E4** (Design Compiler synthesis + cycle-level sim, 40 nm, 400 MHz) | Actual hardware implication study for PASCAL's neuron |
| NeuroFlex (PASCAL, column-hybrid) | PASC-IF, soft reset | No (soft reset) | No | **E4** (Design Compiler synthesis + cycle-level sim, 40 nm, 560 MHz) | Column-granularity ANN/SNN hybrid scheduling |

---

## Full source list

1. Esser et al., "Convolutional Networks for Fast, Energy-Efficient Neuromorphic Computing," PNAS 113(41), 2016. https://www.pnas.org/doi/10.1073/pnas.1604850113 / preprint http://arxiv.org/pdf/1603.08270v1.pdf
2. Akopyan et al., "TrueNorth: Design and Tool Flow of a 65 mW 1 Million Neuron Programmable Neurosynaptic Chip," IEEE TCAD 2015. https://redwood.berkeley.edu/wp-content/uploads/2021/08/Akopyan2015.pdf / https://research.ibm.com/publications/truenorth-design-and-tool-flow-of-a-65-mw-1-million-neuron-programmable-neurosynaptic-chip
3. Cassidy et al., "Cognitive Computing Building Block: A Versatile and Efficient Digital Neuron Model for Neurosynaptic Cores." https://viplab.fudan.edu.cn/vip/attachments/download/3248/neuron-model_of_truenorth.pdf
4. Sawada et al., "TrueNorth Ecosystem for Brain-Inspired Computing," SC 2016. https://research.ibm.com/publications/truenorth-ecosystem-for-brain-inspired-computing-scalable-systems-software-and-applications / https://dl.dropboxusercontent.com/s/brj18cmy9vy5oq5/TrueNorthEcosystem.pdf
5. Andreou et al., "Real-time sensory information processing using the TrueNorth Neurosynaptic System," ISCAS 2016. https://doi.org/10.1109/iscas.2016.7539214
6. Merolla et al., "A million spiking-neuron integrated circuit with a scalable communication network and interface," Science 345(6197), 2014. (cited within Akopyan 2015 / Andreou 2016)
7. Moran et al., "Deep learning for medical image segmentation using the IBM TrueNorth Neurosynaptic System," 2018. https://escholarship.org/uc/item/3n66b3rv
8. Alom et al., "Deep Versus Wide Convolutional Neural Networks for Object Recognition on Neuromorphic System," IJCNN 2018. https://doi.org/10.1109/ijcnn.2018.8489635
9. Cheng et al., "Understanding the design of IBM neurosynaptic system and its tradeoffs: A user perspective," DATE 2017. https://past.date-conference.com/proceedings-archive/2017/pdf/7025.pdf
10. Shukla et al., "REMODEL: Rethinking Deep CNN Models to Detect and Count on a NeuroSynaptic System," Frontiers in Neuroscience 2019. https://doi.org/10.3389/fnins.2019.00004
11. Modha et al., "Neural inference at the frontier of energy, space, and time," Science 382, 2023. https://www.science.org/doi/10.1126/science.adh1174
12. "IBM NorthPole: An Architecture for Neural Network Inference with a 12nm Chip," ISSCC 2024. https://research.ibm.com/publications/ibm-northpole-an-architecture-for-neural-network-inference-with-a-12nm-chip
13. IBM Research blog, "IBM Research's new NorthPole AI chip," 2023. https://research.ibm.com/blog/northpole-ibm-ai-chip
14. Pei, Deng, Song, Zhao, et al., "Towards artificial general intelligence with hybrid Tianjic chip architecture," Nature 572, 2019. https://www.nature.com/articles/s41586-019-1424-8.epdf / https://aiichironakano.github.io/cs596/Pei-ArtificialGeneralIntelligenceChip-Nature19.pdf
15. Tsinghua University press release on Tianjic (Luping Shi lab). https://www.tsinghua.edu.cn/en/info/1244/3005.htm
16. Lynxi KA200 product page. https://lynxi.com/lq2001/18.html
17. Lynxi HP300 product page. https://www.lynxi.com/ka2003/21.html
18. Lynxi HP300 PDF datasheet. https://quanai200dk-1258994165.cos.ap-shanghai.myqcloud.com/lynxi/HP300%E7%B1%BB%E8%84%91%E8%AE%A1%E7%AE%97%E6%9D%BF%E5%8D%A1.pdf
19. Lynxi LynOS product page. https://lynxi.com/LynOS/22.html
20. LynxiTech/BIDL GitHub repository. https://github.com/LynxiTech/BIDL
21. BIDL user manual. https://bidl-user-manual.readthedocs.io/en/latest/overview.html and /principle_explanation.html
22. BIDL Frontiers/PMC paper, "BIDL: a brain-inspired deep learning framework for spatiotemporal processing," 2023. https://pmc.ncbi.nlm.nih.gov/articles/PMC10410154/
23. EE Times, "Innatera Productizes SNN Accelerator As 'Neuromorphic Microcontroller'," 2024. https://www.eetimes.com/innatera-productizes-snn-accelerator-as-neuromorphic-microcontroller/
24. Innatera Talamo SDK page. https://www.innatera.com/software-and-tools/
25. Innatera Pulsar product page. https://www.innatera.com/product/
26. Innatera Pulsar launch press release. https://www.innatera.com/newsroom/innatera-unveils-pulsar-the-worlds-first-mass-market-neuromorphic-microcontroller-for-the-sensor-edge/
27. Open Neuromorphic, "A Look at Pulsar - Innatera." https://open-neuromorphic.org/neuromorphic-computing/hardware/pulsar-by-innatera/
28. XPU.pub, "Pulsar Adds Hardware to Innatera's Neuromorphic AI Base," 2025. https://xpu.pub/2025/07/22/innatera-pulsar/
29. Electronic Design video feature on Pulsar. https://www.electronicdesign.com/technologies/embedded/machine-learning/video/55291658/electronic-design-innateras-pulsar-mixes-analog-digital-snns-for-low-power-sensors
30. Innatera T1 slide deck (Heidelberg HBP flagship presentation). https://flagship.kip.uni-heidelberg.de/jss/HBPm?m=displayPresentation&mEID=9649&mI=263
31. Frenkel, Lefebvre, Legat, Bol, "ODIN: A 0.086-mm² 12.7-pJ/SOP 64k-Synapse 256-Neuron Online-Learning Digital Spiking Neuromorphic Processor in 28nm CMOS," IEEE TBioCAS 2019. https://arxiv.org/abs/1804.07858 / https://github.com/ChFrenkel/ODIN
32. Frenkel & Indiveri, "ReckOn: A 28nm Sub-mm² Task-Agnostic Spiking Recurrent Neural Network Processor Enabling On-Chip Learning over Second-Long Timescales," ISSCC 2022. https://arxiv.org/pdf/2208.09759 / https://github.com/ChFrenkel/ReckOn
33. Tang, Vadivel, Xu, Bilgic, et al., "SENECA: building a fully digital neuromorphic processor, design trade-offs and challenges," Frontiers in Neuroscience 2023. https://doi.org/10.3389/fnins.2023.1187252
34. Yousefzadeh et al., "SENeCA: Scalable Energy-efficient Neuromorphic Computer Architecture," AICAS 2022. https://doi.org/10.1109/aicas54282.2022.9870025
35. Xu, Shidqi, van Schaik, et al., "Optimizing event-based neural networks on digital neuromorphic architecture," Frontiers in Neuroscience 2024. https://doi.org/10.3389/fnins.2024.1335422
36. Shidqi, "Benchmarking and Algorithm Optimization for SENeCA: A RISC-V-based Neuromorphic Processor," TU Delft MSc thesis, 2022. http://resolver.tudelft.nl/uuid:3b6a47f2-bde5-4652-8e6a-8fb6155a4740
37. Frenkel, Legat, Bol, "MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning," ISCAS 2019 / journal version. https://doi.org/10.48550/arxiv.1904.08513
38. "μBrain: An Event-Driven and Fully Synthesizable Architecture for Spiking Neural Networks," Frontiers in Neuroscience 2021. https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2021.664208/full
39. Wu, Li, Pan, Kim, San Miguel, "uBrain: A Unary Brain Computer Interface," ISCA 2022. https://doi.org/10.1145/3470496.3527401 / https://jsm.ece.wisc.edu/docs/wu-isca2022.pdf
40. Bartels, Gallou, Ito, Cook, Sarnthein, Indiveri, et al., "Event driven neural network on a mixed signal neuromorphic processor for EEG based epileptic seizure detection," Scientific Reports 2025. https://doi.org/10.1038/s41598-025-99272-6
41. Panchapakesan, Fang, Li, "SyncNN: Evaluating and Accelerating Spiking Neural Networks on FPGAs," FPL 2021 / ACM TRETS 2022. https://doi.org/10.1145/3514253 / https://www.sfu.ca/~zhenman/files/C21-FPL2021-SyncNN.pdf / https://github.com/SFU-HiAccel/SyncNN
42. Carpegna, Savino, Di Carlo, "Spiker: an FPGA-optimized Hardware accelerator for Spiking Neural Networks," ISVLSI 2022. https://export.arxiv.org/pdf/2201.06993v3.pdf
43. Carpegna, Savino, Di Carlo, "Spiker+: A Framework for the Generation of Efficient Spiking Neural Networks FPGA Accelerators for Inference at the Edge," IEEE TETC 2024. https://doi.org/10.1109/tetc.2024.3511676 / https://arxiv.org/html/2401.01141v1
44. "Spiker-LL: An Energy-Efficient FPGA Accelerator Enabling Adaptive Local Learning in Spiking Neural Networks," 2026 arXiv. https://arxiv.org/html/2605.18003
45. Li, Shen, Zhao, Zhang, Zeng, "FireFly: A High-Throughput Hardware Accelerator for Spiking Neural Networks With Efficient DSP and Memory Optimization," IEEE TVLSI 2023. https://doi.org/10.1109/tvlsi.2023.3279349
46. Li, Shen, Zhao, Zhang, Zeng, "FireFly v2: Advancing Hardware Support for High-Performance Spiking Neural Network With a Spatiotemporal FPGA Accelerator," IEEE TCAD 2024. https://doi.org/10.1109/tcad.2024.3380550 / https://arxiv.org/html/2309.16158v1
47. Chen, Gao, Fu, "Cerebron: A Reconfigurable Architecture for Spatiotemporal Sparse Spiking Neural Networks," IEEE TVLSI 2022. https://doi.org/10.1109/tvlsi.2022.3196839 / https://repository.tudelft.nl/file/File_9e4815fd-0e65-4d94-b3ab-b54ad68d91ad
48. Ramesh & Srinivasan, "PASCAL: Precise and Efficient ANN-SNN Conversion using Spike Accumulation and Adaptive Layerwise Activation," arXiv 2505.01730. https://arxiv.org/html/2505.01730v1 / https://github.com/BrainSeek-Lab/PASCAL
49. "APEX: A Dual-Sparsity Accelerator for Precise and Efficient SNN Inference," arXiv 2608.19046, 2026. https://arxiv.org/html/2608.19046
50. "NeuroFlex: a flexible ANN–SNN accelerator for sparse edge inference," arXiv 2511.05215. https://arxiv.org/html/2511.05215
51. "Design Space Exploration of Sparsity-Aware Application-Specific Spiking Neural Network Accelerators," arXiv 2310.16745. https://ar5iv.labs.arxiv.org/html/2310.16745
52. "A Robust, Open-Source Framework for Spiking Neural Networks on Low-End FPGAs," arXiv 2507.07284. https://arxiv.org/html/2507.07284
53. HyNITA, ISCAS 2025 (noted, not deeply investigated). https://doi.org/10.1109/iscas56072.2025.11043533
