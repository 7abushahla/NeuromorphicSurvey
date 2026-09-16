# SpiNNaker 1 and SpiNNaker 2: Research Notes

Scope: SpiNNaker 1 (Manchester, ARM968) and SpiNNaker 2 (TU Dresden / SpiNNcloud, ARM Cortex-M4F)
architecture, software stack, and — the central question for this survey — whether a converted
(offline-trained, rate-coded) CNN has actually been run on physical SpiNNaker silicon, and what a
"timestep" means on this platform. Classification codes (E1–E5) are assigned per result.

---

## 1. SpiNNaker 1 architecture

**Core building block.** SpiNNaker ("Spiking Neural Network Architecture") is a chip multiprocessor
(CMP): 18 ARM968E-S cores per chip, organized as a globally-asynchronous, locally-synchronous (GALS)
system — synchronous "islands" (the cores) surrounded by an asynchronous, packet-switched
communications fabric. Each chip has 100M transistors on a 102 mm² die (UMC 130 nm process), peak
performance 3.96 GIPS, and peak power 1 W when all 18 cores run at the nominal 180–200 MHz clock.
[Painkras et al. 2013, IEEE JSSC; Furber et al. 2012, IEEE TC]

Each ARM968 core has 32 KB instruction tightly-coupled memory (ITCM) and 64 KB data tightly-coupled
memory (DTCM), a DMA controller, a communications controller, a vectored interrupt controller, and a
timer/counter that generates the simulation timestep interval. One core per chip is normally reserved
as the "monitor processor" for system management, so 17 (commonly quoted as 16 usable + 1 spare + 1
monitor) are available for neuron/synapse simulation. Each core is designed to simulate ~1000 spiking
neurons in real time. [Furber et al. 2012, IEEE TC; SpiNNaker datasheet v2.02]

**Communications fabric.** Inter-core and inter-chip communication uses Address Event Representation
(AER): a spike is a 40- or 72-bit packet carrying (mainly) a 32-bit source-neuron ID; the packet's
arrival time implicitly conveys the spike time. Packets are source-routed and multicast by a bespoke
hardware router (associative multicast lookup, ~1024 routing table entries per chip); router latency
is nominally 0.1 μs per hop, and inter-chip link bandwidth is ~250 Mbit/s over 6 bidirectional
self-timed links per chip, arranged in a triangular/hexagonal mesh. Aggregate bisection bandwidth
exceeds 5 billion packets/s at full (million-core) system scale. [Furber et al. 2012, IEEE TC;
Painkras et al. 2013, IEEE JSSC]

Critically, the fabric provides **no guarantee of delivery**: "if the routing fabric becomes
congested... packets will, in the first instance, be re-routed (causing them to arrive late) or even
dropped (if there is no space to hold them). A design axiom of SpiNNaker is that nothing can ever
prevent a packet from being launched." Packet ordering is non-transitive and arrival time is
non-deterministic under load. [Furber et al. 2012, IEEE TC, eprints.soton.ac.uk/350495]

**Scale.** The architecture scales from a single chip (18 cores) up to a "million-core" machine: the
full design target is 57,600 chips / 1,036,800 cores, with named milestone machines at 1, 4, 48, 576,
6912, and 65,520 nodes (18 cores/node). The Manchester machine reached the full 1,036,800-core /
10-cabinet scale. [eprints.soton.ac.uk/350495; SpiNNaker Human Brain Project Portal Introduction PDF]

**Time model.** SpiNNaker simulates spiking neuron dynamics with a discrete timer interrupt, standardly
**1 ms per timestep**, matched to biological real time: "as long as [communication latency] is small
compared with biological time constants (which in practice means... well under 1 ms) the error
introduced by this latency is negligible." Each core's timer/counter peripheral generates this
interval; on each tick, every simulated neuron's state is updated, and neurons that cross threshold
emit a spike packet immediately (packets travel at electronic, not biological, speed — nanoseconds per
hop). The 1 ms convention is a software/API default, not a hardware limit — sub-millisecond timesteps
(e.g., 0.1 ms) have been used for higher accuracy at the cost of proportionally slower real-time factor
(see §5). [eprints.soton.ac.uk/350495 (Furber overview); van Albada et al. 2018, Frontiers Neurosci.;
Pals et al. 2021 cite a reported 10 μs timestep capability for the chip's timer resolution]

**Neuron models.** SpiNNaker's compute is software-defined: cores run arbitrary C code implementing
whatever neuron/synapse model is compiled into the sPyNNaker "neural_modelling" C library. Standard
provided models include current- and conductance-based leaky integrate-and-fire (LIF), Izhikevich,
and (via plugins) more exotic models; synapse dynamics include STDP and structural plasticity.
[sPyNNaker neural_modelling docs, spinnakermanchester.github.io/sPyNNaker/c/; Knight et al. 2016, PMC]

**Numerical precision.** ARM968 has no floating-point unit; arithmetic is fixed-point (SpiNNaker 1
weight representations commonly use Q-format fixed point, e.g., Q6.16 for 16-bit fractional weights in
one deep-belief-network implementation). [Furber et al. 2013, IEEE Int'l Symp. Electron. Systems (DBN
paper, pure.manchester.ac.uk); confirmed generically by ARM968E-S being an integer-only core]

**Availability.** SpiNNaker 1 machines are hosted at the University of Manchester (up to the ~1M-core,
10-cabinet machine), plus standalone 4-chip and 48-chip boards used for real-time robotics work.
Access is free for evaluation/basic research via an EBRAINS account: create an account, email
neuromorphic@humanbrainproject.eu (or use the EBRAINS Collaboratory directly), get a "Collab" with test
quota, then submit PyNN scripts via a Jupyter interface or a batch "Job Manager." As of 2026 the
EBRAINS wiki lists ongoing SpiNNaker hands-on tutorials (Oct 2026 EBRAINS user days). SpiNNaker 1 is
reported in use by "dozens of research groups across 23 countries." [wiki.ebrains.eu Getting
access page; wiki.ebrains.eu/.../SpiNNaker; ebrains.eu/data-tools-services/tools/spinnaker;
SpiNNcloud Newswire press release May 2024 (23-country figure)]

**Primary citations (Furber et al.):**
- S. Furber, D. Lester, L. A. Plana, J. Garside, E. Painkras, S. Temple, A. D. Brown, "Overview of the
  SpiNNaker System Architecture," IEEE Trans. Computers, 62(12), 2454–2467, 2012.
  https://doi.org/10.1109/tc.2012.142
- E. Painkras, L. A. Plana, J. Garside, S. Temple, F. Galluppi, C. Patterson, D. R. Lester, A. D. Brown,
  S. Furber, "SpiNNaker: A 1-W 18-Core System-on-Chip for Massively-Parallel Neural Network
  Simulation," IEEE J. Solid-State Circuits, 48(8), 1943–1953, 2013.
  https://doi.org/10.1109/jssc.2013.2259038
- S. Furber, F. Galluppi, S. Temple, L. Plana, "The SpiNNaker Project," Proc. IEEE, 2014.
  https://ieeexplore.ieee.org/document/6750072

---

## 2. SpiNNaker 2 architecture

**What changed.** SpiNNaker 2 moves from 130 nm CMOS / ARM968 to 22 nm FDSOI CMOS with ARM Cortex-M4F
cores (Cortex-M4 with a single-precision FPU, extending SpiNNaker 1's fixed-point-only arithmetic).
Each Processing Element (PE) additionally integrates: a fixed-point/floating-point exponential and
natural-log accelerator (s16.15 and s0.31 fixed-point plus fp32, 1–16 configurable iterations, 7–22
clock cycles, 1–2 ULP accuracy); true and pseudo random-number generators (TRNG uses phase-frequency
detection noise from multiple ADPLL clock generators as an entropy source; PRNG implements
MARSKISS64); a rounding/BFloat16 accelerator; and — the key deep-learning-relevant addition — a
**Machine Learning Accelerator (MLA)**: a 16×4 output-stationary 8-bit (fusable to 16-bit)
multiply-accumulate (MAC) array supporting 2D convolution and matrix multiplication, with 8/16/32-bit
signed/unsigned output. [Höppner/Yan et al., "The SpiNNaker 2 Processing Element Architecture...,"
arXiv:2103.08392; Scholze et al., "The SpiNNaker2 chip: a many-core platform...," arXiv:2607.24396]

**Dynamic voltage and frequency scaling (DVFS).** Each PE has fine-grained DVFS, switching between two
VDD rails, with adaptive body biasing (ABB) in the 22 nm FDSOI/FDX process enabling near-threshold
operation; energy scales with spiking/computational activity on the core. [arXiv:2103.08392; Scholze
et al. arXiv:2607.24396]

**Chip/system organization.** PEs are grouped 4-to-a-Quad-Processing-Element (QPE); a full SpiNNaker2
chip integrates 36 QPEs = 144 PEs (some sources round to "152 cores/chip" including support cores),
connected by a network-on-chip and a SpiNNaker-style multicast router for off-chip spike traffic.
Each chip has a DRAM interface (LPDDR4/2GB per node in commercial systems). Commercial boards carry
48 chips; racks carry up to 90 boards. [Kelber et al. 2020 "Mapping DNNs on SpiNNaker2"; Gonzalez et
al., "SpiNNaker2: A Large-Scale Neuromorphic System...," arXiv:2401.04491; EE Times, Leipzig report]

**Dense ANN vs. spiking support.** SpiNNaker2 explicitly targets a **hybrid** SNN/DNN/rule-based
execution model: the same PE can run event-driven spiking code on the Cortex-M4F and, via the MAC
array, dense 8/16-bit convolution or matrix multiplication for conventional (non-spiking) DNN layers.
Reported theoretical peak per-chip throughput is 5.4 TOPS (realistic utilization ~5.0 TOPS per Dresden
deployment figures); system-level figures for the half-scale Dresden machine: 1.5 PFLOPS (32-bit, ARM
cores) and 179 POPS (8-bit, MAC accelerators, aggregate over the system). [EE Times, "SpiNNaker-Based
Supercomputer Launches in Dresden," 2024-05-28]

**Numerical precision.** Per py-spinnaker2 documentation, the actual deployed configuration uses 8-bit
signed synapse weights and 32-bit floating-point neuron state/parameters (LIF/CuBa-LIF), i.e., mixed
precision: quantized weights, float32 dynamics. The MLA supports 8-bit and 16-bit MAC with 8/16/32-bit
output for DNN-style layers. [Arfa et al. 2025, "Efficient Deployment of SNNs on SpiNNaker2..."
arXiv:2504.06748; Scholze et al. arXiv:2607.24396]

**Availability as of 2026 (SpiNNcloud commercialization).** SpiNNcloud Systems GmbH (Dresden spinout,
2021) commercialized SpiNNaker2 under the technical leadership of Steve Furber and Christian Mayr.
Timeline:
- May 8, 2024: SpiNNcloud announces first commercially available neuromorphic supercomputer platform;
  cloud access planned H2 2024, on-prem production shipments planned H1 2025; first customers named
  as Sandia National Laboratories, TU München, Universität Göttingen. [Newswire.com, 2024-05-08;
  SiliconANGLE, 2024-05-08]
- May 2024: Dresden system offering up to 5 billion neurons deployed (half of a planned 16-rack,
  69,120-chip, 10.5-billion-neuron full system); 48 chips/board, 90 boards/rack. [EE Times,
  "SpiNNaker-Based Supercomputer Launches in Dresden," 2024-05-28]
- June 2025: Sandia National Labs deployment reported live, simulating ~150–180 million neurons; among
  the top-5 largest neuromorphic systems deployed globally at the time. [Next Platform, 2025-06-16;
  DataCenterDynamics, 2025-07-28]
- July 2025: University of Leipzig system announced — 4,320 SpiNNaker2 chips, 656,640 cores, ≥650
  million neurons, single rack (25 kW power budget), for protein-folding / drug-discovery research.
  [EE Times, "SpiNNcloud Sells Neuromorphic Supercomputer For Drug Discovery," 2025-07-28;
  DataCenterDynamics, 2025-07-28]
- Largest system stood up to date (per SpiNNcloud CEO, mid-2025): 30,000 chips (>5 billion PEs) at TU
  Dresden. Company reports "double-digit millions of Euros" commercial traction in 2025, engagements
  with US national labs and European supercomputing centers. Marketing claims 18× higher energy
  efficiency than GPUs (vendor claim, not independently verified in the sources reviewed). [EE Times,
  2025-07-28; SpiNNcloud homepage, spinncloud.com/home]

**Primary citations (Mayr/Höppner et al. and SpiNNcloud):**
- Y. Yan, S. Höppner, ... C. Mayr et al., "The SpiNNaker 2 Processing Element Architecture for
  Hybrid Digital Neuromorphic Computing," arXiv:2103.08392, 2021. https://arxiv.org/pdf/2103.08392
- S. Scholze, J. Partzsch, S. Höppner, F. Kelber, ... S. Furber, C. Mayr, "The SpiNNaker2 chip: a
  many-core platform for flexible and scalable brain-inspired computing," arXiv:2607.24396, 2026.
  https://arxiv.org/html/2607.24396
- H. A. Gonzalez, J. Huang, F. Kelber, ... C. Mayr, "SpiNNaker2: A Large-Scale Neuromorphic System for
  Event-Based and Asynchronous Machine Learning," arXiv:2401.04491, 2024.
  https://ar5iv.labs.arxiv.org/html/2401.04491
- SpiNNcloud Systems, "SpiNNcloud Systems Announces First Commercially Available Neuromorphic
  Supercomputer," Newswire, May 8, 2024.
  https://www.newswire.com/news/spinncloud-systems-announces-first-commercially-available-neuromorphic-22325275

---

## 3. Software stack: PyNN → machine

**sPyNNaker.** The primary front end is `sPyNNaker`, a PyNN-language backend (`pyNN.spiNNaker`) that
translates a PyNN-described network (populations, projections/connectors, neuron/synapse models) into
an "application graph" of vertices (neuron populations) and edges (projections). [Rhodes et al. 2018,
"sPyNNaker: A Software Package for Running PyNN Simulations on SpiNNaker," Frontiers in Neuroscience,
https://doi.org/10.3389/fnins.2018.00816]

**SpiNNTools.** Underneath sPyNNaker sits `SpiNNTools`, a generic graph-mapping execution engine
(usable independently of PyNN via `SpiNNakerGraphFrontEnd`). The full compile-and-map pipeline is:
1. **Partitioning**: the application graph is split into a "machine graph" — each application
   population is subdivided ("256 atoms per core" is a common practical limit) so every resulting
   machine vertex fits on a single SpiNNaker core, respecting per-core SDRAM/DTCM budgets.
2. **Placement**: machine-graph vertices are assigned to specific cores on a (possibly faulty-component
   aware) virtual model of the target machine.
3. **Routing**: chip-level multicast routing tables are generated for every projection/edge, then
   compressed to fit the ~1024-entry router table per chip, and IP tags are allocated for any
   Ethernet-connected I/O.
4. **Data generation and loading**: per-core neuron/synapse parameter blocks (destined for DTCM) and
   synaptic-matrix data (destined for per-core SDRAM regions) are generated on the host and loaded,
   along with the compiled C executable, into each core's ITCM.
5. **Execution**: all cores are signaled to start together; the event-driven SpiN1API operating system
   on each core then runs for the configured duration.
6. **Extraction**: results (spikes, recorded state) are read back off-machine for analysis via the PyNN
   API.
[Rowley et al. 2019, "SpiNNTools: The Execution Engine for the SpiNNaker Platform," Frontiers in
Neuroscience, https://doi.org/10.3389/fnins.2019.00231; Rhodes et al. 2018 as above]

**Layer/operator support for convolutional networks.** sPyNNaker itself is a general PyNN neuron/
synapse simulator, not a CNN-layer framework; convolutional structure is expressed as ordinary
projections with `FromListConnector`/convolution-shaped connectivity generated by a higher-level tool
(see §4, SNN Toolbox's `build_convolution`). Memory is the binding constraint for CNN mapping on
SpiNNaker 1: each chip has 128 MB shared SDRAM split dynamically across its 18 cores, giving roughly
8 MB/core on average, with most models limited in practice to ~256 "atoms" (neurons) per core.
[SpiNNaker EBRAINS Portal Introduction, spinnakermanchester.github.io/common_pages/8.0.0/
spinnaker_ebrains_portal_use.pdf]

**SpiNNaker 2 software: py-spinnaker2 and NIR.** For SpiNNaker2, the analogous Python interface is
`py-spinnaker2` (PyNN-inspired API), which partitions and maps SNNs/hybrid DNN-SNN models onto
single-chip or 48-chip SpiNNaker2 systems, executes via an "experiment runner," and can fall back to a
Brian2-based software emulation of the SpiNNaker2 backend when no chip is available. Deep SNNs (trained
via deep-learning toolchains such as snnTorch/Norse) are imported through the **Neuromorphic
Intermediate Representation (NIR)** exchange format; the SpiNNaker2 NIR importer supports Conv1d,
Conv2d, Flatten, Affine, Linear, CuBaLIF, IF, LIF, and SumPool2d node types (but does not yet support
*exporting* arbitrary nodes back to NIR). [py-spinnaker2 docs, spinnaker2.gitlab.io/py-spinnaker2;
NIR SpiNNaker2 import docs, neuroir.org/docs/examples/spinnaker2/import; Pedersen et al. 2024, "NIR:
unified instruction set for interoperable brain-inspired computing," Nature Communications 15:8122]

**Citations:**
- A. D. Rhodes, L. Bogdan, C. Brenninkmeijer, S. Davidson, D. Fellows, A. Gait, D. R. Lester, M.
  Mikaitis, L. A. Plana, A. G. D. Rowley, C. Simpson, S. B. Furber, "sPyNNaker: A Software Package for
  Running PyNN Simulations on SpiNNaker," Frontiers in Neuroscience, 12:816, 2018.
  https://doi.org/10.3389/fnins.2018.00816
- A. G. D. Rowley, C. Brenninkmeijer, S. Davidson, S. Fellows, A. Gait, D. R. Lester, L. A. Plana, F.
  Rostami, A. B. Stokes, S. B. Furber, "SpiNNTools: The Execution Engine for the SpiNNaker Platform,"
  Frontiers in Neuroscience, 13:231, 2019. https://doi.org/10.3389/fnins.2019.00231
- B. Vogginger, F. Kelber, M. Jobst, G. Béna, S. Arfa, Y. Yan, et al., "py-spinnaker2," Zenodo, 2024.
  https://doi.org/10.5281/zenodo.10202109

---

## 4. Conversion support: SNN Toolbox and converted rate-coded CNNs on physical SpiNNaker

**SNN Toolbox has a SpiNNaker backend — documented.** SNN-TB (Rueckauer et al.) explicitly lists
SpiNNaker as a deployment target: "If you have access to Intel's neuromorphic processor Loihi, or the
SpiNNaker system from the University of Manchester, you may use the SNN toolbox to deploy your
converted model on this dedicated hardware." The toolbox's `spiNNaker_target_sim.py` module builds
PyNN-based `Conv2D`/`DepthwiseConv2D`/`Conv1D`/dense/pooling layers from a parsed Keras/PyTorch model,
handles weight scaling and Poisson-rate input encoding, and drives the sPyNNaker PyNN backend
directly. [snntoolbox.readthedocs.io/en/latest/guide/intro.html; snntoolbox.readthedocs.io source,
target_simulators/spiNNaker_target_sim.py; NeuromorphicProcessorProject/snn_toolbox GitHub repo]

**Converted CNNs have been run on physical SpiNNaker 1 hardware — E1, digit-recognition scale.**
The clearest documented case:

- **Patiño-Saucedo, Rostro-González, Serrano-Gotarredona, Linares-Barranco (2019/2020), "Event-driven
  implementation of deep spiking convolutional neural networks for supervised classification using the
  SpiNNaker neuromorphic platform," Neural Networks 121:319–328.** A LeNet CNN was trained
  conventionally in Keras on MNIST, converted to a spiking CNN using SNN-TB following the Rueckauer et
  al. (2017) method, and physically deployed on a **SpiNNaker 103 machine** (48 chips, 864 ARM
  cores) via PyNN. Measured on-chip accuracy: **98.20%** on MNIST (reported as the best MNIST accuracy
  achieved on the SpiNNaker platform at the time). The whole 10,000-sample MNIST test set was
  propagated through the physical hardware; **15 ms of activity** was recorded per sample on the
  SpiNNaker implementation, with a measured wall-clock inference time of **~0.4 s/sample on the
  neuromorphic hardware** (vs. ~10 s/sample in a NEST software simulation of the same PyNN model). A
  second, separately-trained STBP spiking CNN for event-based N-MNIST was also deployed on the same
  physical machine (97.92% accuracy). The authors additionally introduce a spike-regularization loss
  that shrinks average spike counts up to 19× (convolutional net) or 34× (dense net) with <2%/<1%
  accuracy loss and report up to 6% reduction in measured inference time on SpiNNaker from the reduced
  spike traffic. The paper explicitly notes a **limitation**: "it is difficult to assess [SpiNNaker's]
  energy consumption" from within this experimental setup — no energy number is reported for this
  specific deployment. **Classification: E1** (physical silicon, latency measured; accuracy measured;
  no energy figure in this paper). https://doi.org/10.1016/j.neunet.2019.09.008

- **Galanis, Anagnostopoulos, Nguyen, Bares (2020), "Efficient Deployment of Spiking Neural Networks on
  SpiNNaker Neuromorphic Platform," IEEE TCAS-II.** A design-space-exploration framework for
  hardware-related conversion parameters, targeting the SpiNNaker board; reports **98.85%** SNN
  accuracy on MNIST with 3× faster configuration search than exhaustive search. Deployment target and
  accuracy are documented; the abstract does not report energy/latency numbers in the search results
  retrieved. **Classification: E1/E2** (physical SpiNNaker target implied by "target board"
  configuration search; accuracy reported — treat as E2 pending confirmation of on-chip vs.
  architecture-search-only measurement). https://doi.org/10.1109/tcsii.2020.3047425

- **O'Connor et al. / Stromatias et al. (2015), "Scalable Energy-Efficient, Low-Latency
  Implementations of Spiking Deep Belief Networks on SpiNNaker."** A spiking Deep Belief Network
  (784-500-500-10, MNIST) — trained via the Deep Belief Network→SNN conversion method of O'Connor et
  al. (2013) — was run in real time on a **single physical SpiNNaker chip**. Measured classification
  accuracy: **95.01%** (vs. 96.06%/95.07% for MATLAB/Brian double-precision software references, and
  92% for an FPGA "Minitaur" baseline). Measured power: **0.3 W** during network runtime; measured mean
  classification latency: **~20 ms**. This is a DBN→SNN conversion (rate-coded, Poisson-rate MNIST
  pixel encoding), not a CNN, but it is a directly relevant rate-coded-conversion result on physical
  SpiNNaker 1. **Classification: E1** (physical silicon, accuracy + latency + power all measured).
  https://pure.manchester.ac.uk/ws/files/32800773/FULL_TEXT.PDF

- **Pals, Perez Belizon, Berberich, Ehrlich, Nassour, Cheng (2021), "Demonstrating the Viability of
  Mapping Deep Learning Based EEG Decoders to Spiking Networks on Low-powered Neuromorphic Chips,"
  IEEE EMBC.** A continuous-valued CNN for motor-imagery EEG classification was directly mapped to a
  spiking CNN and deployed on physical SpiNNaker ("through server access," i.e., remote
  EBRAINS-style hardware access). Measured on-chip mean accuracy: **73.72%** (±11.73), vs. 75.63%
  (±12.25) for the original CNN — a **1.91-percentage-point** accuracy drop from conversion +
  deployment. States the chip simulates neurons "with a timestep of 10 μs." **Classification: E1**
  (physical silicon, accuracy measured; no energy/latency figures reported in the retrieved excerpt).
  https://doi.org/10.1109/embc46164.2021.9629621

- **Serrano-Gotarredona, Linares-Barranco, Galluppi, Plana, Furber (2015), "ConvNets experiments on
  SpiNNaker," ISCAS 2015.** An earlier (2015) physical-hardware demonstration: a 5-layer ConvNet for
  DVS-camera symbol recognition, exploiting weight sharing to fit up to 2048 neurons/core (32k
  neurons/chip) in local SRAM DTCM rather than DRAM. This is event-driven/DVS input rather than a
  rate-coded static-image conversion, and the search snippets retrieved do not report a quantitative
  accuracy figure for the deployed network. **Classification: E1 for architecture proof-of-concept
  (physical silicon), but NOT FOUND for a numeric accuracy on this specific run** in the sources
  reviewed. https://doi.org/10.1109/iscas.2015.7169169

**No CIFAR-10-or-larger, ImageNet-scale, or otherwise "deep" (VGG/ResNet-class) rate-coded CNN
conversion was found run on physical SpiNNaker 1 or SpiNNaker 2 silicon.** All physical-hardware
conversion results located are digit-recognition-scale (MNIST/N-MNIST) or EEG-classifier-scale
networks (few-layer CNNs). This is an important negative finding for the survey: **NOT FOUND** —
no published measurement of a large, modern-CNN-scale converted network running on physical SpiNNaker
hardware.

**SpiNNaker2 VGG-16/ResNet-50 "deployment" is a simulation, not silicon — flag this explicitly.**
Kelber, Wu, Vogginger, Partzsch, Liu, Stolba, Mayr (2020), "Mapping Deep Neural Networks on
SpiNNaker2," NICE '20 workshop paper, reports VGG-16 and ResNet-50 inference in 43.5 ms and 19.5 ms
respectively using an optimized data-reuse mapping strategy across 144 simulated processing elements.
The paper states explicitly: **"As the SpiNNaker2 chip is not yet available, we developed a Python
simulator that replicates the timings of computation steps (ARM and MAC array) and data transfer
(SRAM, NoC, DRAM)."** The reported 43.5 ms/19.5 ms figures come from this **timing simulator**, not
measured silicon. **Classification: E4/E5** (architectural/cycle-timing simulation, not physical
hardware — explicitly NOT E1). This paper documents a mapping *procedure* that is directly relevant to
CNN-on-SpiNNaker2 deployment, but its quantitative results must not be cited as physical-hardware
measurements. https://dl.acm.org/doi/10.1145/3381755.3381778

**SpiNNaker2 physical-hardware SNN deployments that exist (not CNN-conversion, but relevant
context).** Arfa, Vogginger, Liu, Partzsch, Schöne, Mayr (2025), "Efficient Deployment of Spiking
Neural Networks on SpiNNaker2 for DVS Gesture Recognition Using Neuromorphic Intermediate
Representation," NICE 2025, deploys natively-trained (not ANN-converted) 8-bit quantized SNNs on a
**physical single-chip SpiNNaker2 test board** via py-spinnaker2 + NIR, achieving **94.13%** on-chip
accuracy on DVS Gesture recognition (vs. ~94.6% FP32 software baseline), with PTQ and QAT pipelines
compared; reports per-inference energy for comparator methods (TrueNorth 18.8 mJ, Speck-class ~459 mJ
for some GPU baselines in the comparison table) but the SpiNNaker2-specific energy-per-inference figure
was not resolved in the excerpts retrieved (see "energy" table row is present but SpiNNaker2 column
values were not legible in the search snippet — **NOT FOUND** as a clean number; would need direct PDF
read to confirm). This is an SNN-native deployment (event-based DVS input, not an ANN-to-SNN rate-code
conversion of a static-image CNN), so it answers "does physical SpiNNaker2 run deep SNNs" (yes,
E1) but not the specific "converted rate-coded CNN" question. https://doi.org/10.1109/nice65350.2025.11065119
/ arXiv:2504.06748

**Summary answer to the central question:** Yes, but only at small scale. A converted (ANN-trained,
then SNN-toolbox-converted), rate-coded CNN **has** been run on physical SpiNNaker 1 hardware — most
clearly in Patiño-Saucedo et al. 2019/2020 (LeNet, MNIST, 98.20% accuracy, SpiNNaker-103 machine, 15 ms
of recorded spiking activity per sample) and in the earlier DBN-based Stromatias-line work (O'Connor
DBN→SNN, 95.01% on a single chip, 0.3 W, ~20 ms latency). No evidence was found of a CIFAR-10-scale or
larger converted CNN running on physical SpiNNaker 1 or SpiNNaker 2 silicon; the one SpiNNaker2 result
at VGG-16/ResNet-50 scale (Kelber et al. 2020) is a pre-silicon timing simulation, not a hardware
measurement.

---

## 5. Energy/latency measurement on physical hardware

Multiple independent physical-hardware power studies on SpiNNaker 1 report **energy per synaptic
event**, which is the standard SpiNNaker efficiency metric (rather than energy per inference, which is
architecture-dependent on spike count and per-core neuron density):

| Study | Hardware config | Energy per synaptic event | Notes |
|---|---|---|---|
| Sharp et al. 2012 (cited in van Albada et al. 2018) | 4-chip board, 10,000 neurons, 4M synapses, 1 ms timestep | **110 nJ** total (43 nJ incremental) | ~2 W board power |
| Stromatias, Galluppi, Patterson, Furber 2013, IJCNN | 48-chip board, up to 250k LIF neurons, 1.8B synaptic events/s | **~20 nJ** total (8 nJ incremental, baseline-subtracted) | <1 W/chip at most complex configs; https://doi.org/10.1109/ijcnn.2013.6706927 |
| van Albada et al. 2018, Frontiers Neurosci. (cortical microcircuit, 0.1 ms timestep) | 24-board rack, 6 boards active | **5.9 μJ** (SpiNNaker) vs. **5.8 μJ** (NEST/HPC cluster at its optimum, 144 virtual processes) | https://doi.org/10.3389/fnins.2018.00291; higher than earlier figures because of 10× finer timestep (0.1 ms vs. 1 ms) and sparse mapping (fewer synaptic events per amortized baseline-power chip) |
| Rowley et al. (heterogeneous-parallelization follow-up), "Real-time cortical simulation on neuromorphic hardware," Phil. Trans. R. Soc. A, 2019 | 12-board SpiNNaker machine, hard real-time (10 s bio-time in 10 s wall-clock) | **0.601–0.628 μJ/synaptic event** | 10× lower than van Albada 2018 config; comparable to GPU (Jetson TX2: 0.3 μJ/event at 25× slowdown; Tesla V100: ~0.47 μJ/event at 2× slowdown); ~10× lower energy than modern HPC cluster for matched accuracy. https://doi.org/10.1098/rsta.2019.0160 |
| Knight, Tully, Kaplan, Lansner, Furber 2016, PMC | Large-scale plastic-network sim, SpiNNaker vs. Cray XC-30 | SpiNNaker uses **≥45× less power** than a matched-runtime Cray XC-30 allocation (up to 200× with software optimizations) | Peak-power estimate, not integrated energy; https://pmc.ncbi.nlm.nih.gov/articles/PMC4823276/ |

**Per-neuron overhead vs. fixed-function ASICs.** No direct single-number "per-neuron-update energy on
SpiNNaker vs. a fixed-function neuromorphic ASIC (e.g., Loihi, TrueNorth)" comparison was found in a
peer-reviewed physical-hardware-to-physical-hardware format within this search pass; the DVS-gesture
NIR paper (Arfa et al. 2025) tabulates energy-per-inference across TrueNorth, Loihi, and SpiNNaker2 for
comparable tasks but the SpiNNaker2-specific number was not confirmed legible in the retrieved
excerpt — **flagged NOT FOUND / needs direct-PDF follow-up**, not to be asserted from this pass.
General qualitative conclusion supported by the literature: SpiNNaker is a **general-purpose,
software-programmable** neuromorphic platform whose energy/synaptic-event is roughly GPU-competitive
at matched accuracy (Rowley et al. 2019) but is expected to be higher than a fixed-function
event-driven ASIC (TrueNorth-class) per spike, because each SpiNNaker "neuron update" is executed as
general ARM instructions rather than dedicated hardware datapath — this is stated as an architectural
expectation in multiple sources but a rigorously matched physical-to-physical comparison number was
not located in this pass.

**Idle/background power is a large fraction of total SpiNNaker energy.** van Albada et al. 2018 report
that background power (network switch, cooling, PSU) accounts for roughly half of total measured
system power even when actively simulating; Stromatias et al. (IJCNN 2014 optimization paper) measured
~22 W idle power for a 48-chip board before any optimization, dominated (~70%) by processor-block clock
domains even when idle.

**Citations:**
- E. Stromatias, F. Galluppi, C. Patterson, S. Furber, "Power analysis of large-scale, real-time neural
  networks on SpiNNaker," IJCNN 2013. https://doi.org/10.1109/ijcnn.2013.6706927
- S. J. van Albada, A. Rowley, J. Senk, M. Hopkins, M. Schmidt, A. B. Stokes, D. R. Lester, M. Diesmann,
  S. B. Furber, "Performance Comparison of the Digital Neuromorphic Hardware SpiNNaker and the Neural
  Network Simulation Software NEST for a Full-Scale Cortical Microcircuit Model," Frontiers in
  Neuroscience, 12:291, 2018. https://doi.org/10.3389/fnins.2018.00291
- A. B. Stokes / A. G. D. Rowley et al., "Real-time cortical simulation on neuromorphic hardware,"
  Phil. Trans. R. Soc. A, 378(2164), 2019. https://doi.org/10.1098/rsta.2019.0160
- J. C. Knight, P. Tully, B. Kaplan, A. Lansner, S. Furber, "Large-Scale Simulations of Plastic Neural
  Networks on Neuromorphic Hardware," Frontiers in Neuroanatomy/Neuroinformatics, 2016.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4823276/
- P. A. Merolla / E. Stromatias et al. (DBN paper): "Scalable Energy-Efficient, Low-Latency
  Implementations of Spiking Deep Belief Networks on SpiNNaker" (see §4).

---

## 6. Limitations for rate-coded conversion

**Real-time constraint / timestep-vs-slowdown tradeoff.** The 1 ms default timestep is a *software*
convention tied to biological realism, not a hard hardware floor, but shrinking the timestep to
increase numerical accuracy (e.g., for STDP or fine temporal dynamics) directly costs real-time factor:
van Albada et al. 2018 needed **0.1 ms** timesteps to match NEST's accuracy for a cortical microcircuit
model and consequently required a **~20× slowdown** relative to real time (400,000 clock-cycle timer
period) to keep all cores within their processing deadline without dropped packets. Rate-coded
ANN→SNN conversion, which typically needs many-hundred-timestep integration windows per input to
approximate a real-valued activation via spike count, therefore trades off achievable per-inference
wall-clock latency against timestep granularity and rate/count accuracy — this is the same
accuracy/latency/energy tradeoff widely noted in ANN→SNN conversion literature generally, now bounded
by SpiNNaker's specific real-time deadline mechanics.

**Packet drop / congestion under high spike load.** By design axiom, "nothing can ever prevent a packet
from being launched," so under sustained high firing rates the router can be driven into a state where
packets are re-routed (late arrival) or **dropped outright** for lack of buffer space; the fabric is
explicitly engineered for high peak but low *average* traffic ("expected to be lightly loaded on
average"). High-firing-rate networks — which is exactly the profile of an early-layer rate-coded
CNN conversion feeding a Poisson/rate-based input encoding, before spike-count regularization is
applied — are therefore the worst case for this fabric. Rast, Navaridas, Jin, Galluppi, Plana,
Miguel-Alonso, Furber, "Managing Burstiness and Scalability in Event-Driven Models on the SpiNNaker
Neuromimetic System" (Int'l J. Parallel Programming, 2011), analyzes exactly this: SpiNNaker
communication has "no instantaneous global state," is "fire-and-forget" from the source and
"use-it-or-lose-it" at the destination (a packet not processed immediately at arrival must be
dropped), and the router itself has "finite and unbuffered local network capacity." This is a direct,
documented architectural limitation for high-firing-rate rate-coded conversion workloads.
https://doi.org/10.1007/s10766-011-0180-7

Patiño-Saucedo et al. 2019/2020 independently motivate their spike-count-regularization contribution
(19–34× reduction in average firing rate) partly on these grounds — fewer spikes per sample reduces
both energy and the risk of router/timestep-deadline pressure at high input rates, and they report a
measured **up to 6% reduction in inference wall-clock time** on physical SpiNNaker as a direct
consequence of reduced spike traffic.

**Memory per core.** Each SpiNNaker 1 chip has 128 MB SDRAM shared dynamically across its 18 cores
(≈8 MB/core average), plus 64 KB DTCM / 32 KB ITCM local to each core; the EBRAINS portal documentation
states most models are, in practice, **limited to ~256 "atoms" (neurons) per core** given this budget,
which directly bounds how large a converted CNN layer's neuron population can be before requiring
partitioning across many cores (with attendant routing-table and communication overhead).
[spinnakermanchester.github.io/common_pages/8.0.0/spinnaker_ebrains_portal_use.pdf]

For SpiNNaker 2, each PE has 128 KB local SRAM (64 KB instruction / 64 KB data in the SpiNNaker2
prototype description), materially larger than SpiNNaker 1's per-core TCM but still a binding
constraint for large convolutional feature maps and weight tensors, motivating the explicit
layer-splitting/data-reuse mapping strategies described in Kelber et al. 2020 (§4) and the
sparsity/pruning-driven memory-efficiency work of Liu, Bellec, Vogginger, Kappel, Partzsch, Neumärker,
Höppner, Basu, Mayr, Legenstein (2018), "Memory-Efficient Deep Learning on a SpiNNaker 2 Prototype,"
Frontiers in Neuroscience, https://doi.org/10.3389/fnins.2018.00840 (4-PE SpiNNaker2 prototype, DEEP-R
sparse training, CIFAR-10 memory-footprint analysis — note this is a *memory-footprint* analysis for
training, not a physical-hardware CIFAR-10 inference-accuracy result).

---

## Source list

1. E. Painkras, L. A. Plana, J. Garside, S. Temple, F. Galluppi, C. Patterson, D. R. Lester, S. Furber,
   "SpiNNaker: A 1-W 18-Core System-on-Chip for Massively-Parallel Neural Network Simulation," IEEE J.
   Solid-State Circuits, 48(8), 1943–1953, 2013. https://doi.org/10.1109/jssc.2013.2259038
2. S. Furber, D. Lester, L. A. Plana, J. Garside, E. Painkras, S. Temple, A. D. Brown, "Overview of the
   SpiNNaker System Architecture," IEEE Trans. Computers, 62(12), 2454–2467, 2012.
   https://doi.org/10.1109/tc.2012.142 (full text: https://eprints.soton.ac.uk/350495/1/TCv2.pdf)
3. SpiNNaker Project Team, "SpiNNaker datasheet version 2.02," Univ. Manchester, 2011.
   https://spinnakermanchester.github.io/docs/SpiNN2DataShtV202.pdf
4. S. Furber, F. Galluppi, S. Temple, L. Plana, "The SpiNNaker Project," Proc. IEEE, 2014.
   https://ieeexplore.ieee.org/document/6750072
5. K. Dugan, J. S. Reeve, A. D. Brown, S. Furber, "Interconnection system for the SpiNNaker
   biologically inspired multi-computer," IET Computers & Digital Techniques, 2013.
   https://doi.org/10.1049/iet-cdt.2012.0139
6. Y. Yan, S. Höppner, et al., C. Mayr, "The SpiNNaker 2 Processing Element Architecture for Hybrid
   Digital Neuromorphic Computing," arXiv:2103.08392, 2021. https://arxiv.org/pdf/2103.08392
7. S. Scholze, J. Partzsch, S. Höppner, F. Kelber, A. Dixius, M. Stolba, S. Arfa, M. Berthel, G.
   Ellguth, J. Garside, H. A. Gonzalez, S. Hartmann, T. Kiel-Hocker, D. Hu, M. Jobst, K. Khan Nazeer,
   T. Langer, C. Liu, G. Liu, M. Lohrmann, M. Mikaitis, F. Neumärker, A. Rostami, S. Schiefer, T.
   Schubert, D. Shang, B. Vogginger, Y. Yan, S. Furber, C. Mayr, "The SpiNNaker2 chip: a many-core
   platform for flexible and scalable brain-inspired computing," arXiv:2607.24396, 2026.
   https://arxiv.org/html/2607.24396
8. H. A. Gonzalez, J. Huang, F. Kelber, K. Khan Nazeer, T. Langer, C. Liu, M. Lohrmann, M. Rostami, A.
   Schönwälder, S. Vogel, ... C. Mayr, "SpiNNaker2: A Large-Scale Neuromorphic System for Event-Based
   and Asynchronous Machine Learning," arXiv:2401.04491, 2024.
   https://ar5iv.labs.arxiv.org/html/2401.04491
9. SpiNNcloud Systems, "SpiNNcloud Systems Announces First Commercially Available Neuromorphic
   Supercomputer," Newswire press release, 2024-05-08.
   https://www.newswire.com/news/spinncloud-systems-announces-first-commercially-available-neuromorphic-22325275
10. S. Ward-Foxton, "SpiNNaker-Based Supercomputer Launches in Dresden," EE Times, 2024-05-28.
    https://www.eetimes.com/spinnaker-based-neuromorphic-supercomputer-launches-in-dresden/
11. S. Ward-Foxton, "SpiNNcloud Sells Neuromorphic Supercomputer For Drug Discovery," EE Times,
    2025-07-28. https://www.eetimes.com/spinncloud-sells-neuromorphic-supercomputer-for-drug-discovery/
12. C. Trueman, "SpiNNcloud to deploy neuromorphic supercomputer at Leipzig University,"
    DataCenterDynamics, 2025-07-28.
    https://www.datacenterdynamics.com/en/news/spinncloud-to-deploy-worlds-largest-neuromorphic-supercomputer-at-leipzig-university/
13. J. Burt, "Sandia Deploys SpiNNaker2 Neuromorphic System," The Next Platform, 2025-06-16.
    https://www.nextplatform.com/compute/2025/06/16/sandia-deploys-spinnaker2-neuromorphic-system/1658175
14. N. Flaherty, "World's largest neuromorphic supercomputer aims at 10bn neurons," eeNews Europe,
    2024-05-08. https://www.eenewseurope.com/en/worlds-largest-neuromorphic-supercomputer-aims-at-10bn-neurons/
15. A. D. Rhodes, L. Bogdan, C. Brenninkmeijer, S. Davidson, D. Fellows, A. Gait, D. R. Lester, M.
    Mikaitis, L. A. Plana, A. G. D. Rowley, C. Simpson, S. B. Furber, "sPyNNaker: A Software Package
    for Running PyNN Simulations on SpiNNaker," Frontiers in Neuroscience, 12:816, 2018.
    https://doi.org/10.3389/fnins.2018.00816
16. A. G. D. Rowley, C. Brenninkmeijer, S. Davidson, S. Fellows, A. Gait, D. R. Lester, L. A. Plana, F.
    Rostami, A. B. Stokes, S. B. Furber, "SpiNNTools: The Execution Engine for the SpiNNaker
    Platform," Frontiers in Neuroscience, 13:231, 2019. https://doi.org/10.3389/fnins.2019.00231
    (also: https://pmc.ncbi.nlm.nih.gov/articles/PMC6444189/)
17. University of Manchester, "PyNN on SpiNNaker Installation Guide."
    https://spinnakermanchester.github.io/spynnaker/8.0.0/PyNNOnSpinnakerInstall.html
18. University of Manchester, "SpiNNaker Human Brain Project Portal Introduction."
    https://spinnakermanchester.github.io/common_pages/8.0.0/spinnaker_ebrains_portal_use.pdf
19. B. Vogginger, F. Kelber, M. Jobst, G. Béna, S. Arfa, Y. Yan, P. Gerhards, M. Weih, M. Akl, H. A.
    Gonzalez, C. Mayr, "py-spinnaker2," Zenodo, 2024. https://doi.org/10.5281/zenodo.10202109
    (docs: https://spinnaker2.gitlab.io/py-spinnaker2/)
20. J. E. Pedersen, S. Abreu, M. Jobst, G. Lenz, V. Fra, F. C. Bauer, D. R. Muir, P. Zhou, B.
    Vogginger, K. Heckel, G. Urgese, S. Shankar, T. C. Stewart, S. Sheik, J. K. Eshraghian,
    "Neuromorphic intermediate representation: A unified instruction set for interoperable
    brain-inspired computing," Nature Communications, 15:8122, 2024.
    https://doi.org/10.1038/s41467-024-52259-9 (NIR SpiNNaker2 docs:
    https://neuroir.org/docs/examples/spinnaker2/import/)
21. B. Rueckauer, I.-A. Lungu, Y. Hu, M. Pfeiffer, S.-C. Liu, "Conversion of Continuous-Valued Deep
    Networks to Efficient Event-Driven Networks for Image Classification," Frontiers in Neuroscience,
    2017 (SNN Toolbox foundational paper; toolbox docs:
    https://snntoolbox.readthedocs.io/en/latest/guide/intro.html; GitHub:
    https://github.com/NeuromorphicProcessorProject/snn_toolbox)
22. A. Patiño-Saucedo, H. Rostro-González, T. Serrano-Gotarredona, B. Linares-Barranco, "Event-driven
    implementation of deep spiking convolutional neural networks for supervised classification using
    the SpiNNaker neuromorphic platform," Neural Networks, 121:319–328, 2020.
    https://doi.org/10.1016/j.neunet.2019.09.008
23. I. Galanis, I. Anagnostopoulos, C. K. Nguyen, G. Bares, "Efficient Deployment of Spiking Neural
    Networks on SpiNNaker Neuromorphic Platform," IEEE Trans. Circuits and Systems II, 2020.
    https://doi.org/10.1109/tcsii.2020.3047425
24. E. Stromatias, D. Neil, F. Galluppi, M. Pfeiffer, S.-C. Liu, S. Furber, "Scalable
    Energy-Efficient, Low-Latency Implementations of Spiking Deep Belief Networks on SpiNNaker," IJCNN
    2015 (full text: https://pure.manchester.ac.uk/ws/files/32800773/FULL_TEXT.PDF)
25. M. Pals, R. J. Perez Belizon, N. Berberich, S. K. Ehrlich, J. Nassour, G. Cheng, "Demonstrating the
    Viability of Mapping Deep Learning Based EEG Decoders to Spiking Networks on Low-powered
    Neuromorphic Chips," IEEE EMBC 2021. https://doi.org/10.1109/embc46164.2021.9629621
26. T. Serrano-Gotarredona, B. Linares-Barranco, F. Galluppi, L. A. Plana, S. Furber, "ConvNets
    experiments on SpiNNaker," IEEE ISCAS 2015, pp. 2405–2408. https://doi.org/10.1109/iscas.2015.7169169
27. F. Kelber, B. Wu, B. Vogginger, J. Partzsch, C. Liu, M. Stolba, C. Mayr, "Mapping Deep Neural
    Networks on SpiNNaker2," NICE '20 Workshop, ACM, 2020.
    https://dl.acm.org/doi/10.1145/3381755.3381778
28. S. Arfa, B. Vogginger, C. Liu, J. Partzsch, M. Schöne, C. Mayr, "Efficient Deployment of Spiking
    Neural Networks on SpiNNaker2 for DVS Gesture Recognition Using Neuromorphic Intermediate
    Representation," NICE 2025. https://doi.org/10.1109/nice65350.2025.11065119
    (preprint: arXiv:2504.06748, https://arxiv.org/html/2504.06748v1)
29. E. Stromatias, F. Galluppi, C. Patterson, S. Furber, "Power analysis of large-scale, real-time
    neural networks on SpiNNaker," IJCNN 2013. https://doi.org/10.1109/ijcnn.2013.6706927
30. S. J. van Albada, A. Rowley, J. Senk, M. Hopkins, M. Schmidt, A. B. Stokes, D. R. Lester, M.
    Diesmann, S. B. Furber, "Performance Comparison of the Digital Neuromorphic Hardware SpiNNaker and
    the Neural Network Simulation Software NEST for a Full-Scale Cortical Microcircuit Model,"
    Frontiers in Neuroscience, 12:291, 2018. https://doi.org/10.3389/fnins.2018.00291
31. A. G. D. Rowley et al., "Real-time cortical simulation on neuromorphic hardware," Phil. Trans. R.
    Soc. A, 378(2164), 2019. https://doi.org/10.1098/rsta.2019.0160
32. J. C. Knight, P. Tully, B. A. Kaplan, A. Lansner, S. B. Furber, "Large-Scale Simulations of Plastic
    Neural Networks on Neuromorphic Hardware," Frontiers in Neuroinformatics, 2016.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC4823276/
33. E. Stromatias et al., "Optimising the Overall Power Usage on the SpiNNaker Neuromimetic
    Architecture," IJCNN 2014.
    http://www.cmap.polytechnique.fr/~nikolaus.hansen/proceedings/2014/WCCI/IJCNN-2014/PROGRAM/N-14733.pdf
34. A. Rast, J. Navaridas, X. Jin, F. Galluppi, L. A. Plana, J. Miguel-Alonso, S. Furber, "Managing
    Burstiness and Scalability in Event-Driven Models on the SpiNNaker Neuromimetic System," Int'l J.
    Parallel Programming, 2011. https://doi.org/10.1007/s10766-011-0180-7
35. C. Liu, G. Bellec, B. Vogginger, D. Kappel, J. Partzsch, F. Neumärker, S. Höppner, W. Maass, S. B.
    Furber, R. Legenstein, C. Mayr, "Memory-Efficient Deep Learning on a SpiNNaker 2 Prototype,"
    Frontiers in Neuroscience, 12:840, 2018. https://doi.org/10.3389/fnins.2018.00840
36. EBRAINS, "Getting access to the NMC systems BrainScaleS and SpiNNaker," HBP Wiki.
    https://wiki.ebrains.eu/bin/view/Collabs/neuromorphic/Getting%20access/
37. EBRAINS, "Neuromorphic Computing" service page. https://ebrains.eu/data-tools-services/tools/spinnaker
    and https://ebrains.eu/data-tools-services/modelling-simulation/neuromorphic-computing
38. EBRAINS, "SpiNNaker" collab wiki page (tutorial schedule, machine description).
    https://wiki.ebrains.eu/bin/view/Collabs/neuromorphic/SpiNNaker/

---

## Notes on evidence gaps (explicit NOT FOUND flags)

- **NOT FOUND**: a CIFAR-10-scale or larger (VGG/ResNet-class) rate-coded CNN conversion measured on
  physical SpiNNaker 1 or SpiNNaker 2 silicon. The one VGG-16/ResNet-50 SpiNNaker2 result located
  (Kelber et al. 2020) is explicitly a pre-silicon timing simulation (E4/E5), not a hardware
  measurement (E1) — the authors state the chip was "not yet available" at time of writing.
- **NOT FOUND**: a clean, directly-comparable "energy per neuron update on SpiNNaker vs. a
  fixed-function ASIC (Loihi/TrueNorth), same task, both physically measured" single number. Individual
  physical-hardware energy-per-synaptic-event figures exist for SpiNNaker (§5 table) and for
  TrueNorth/Loihi separately in comparator tables (e.g., Arfa et al. 2025 Table), but a rigorously
  matched pairwise comparison was not confirmed legible in this search pass.
- **NOT FOUND**: a numeric accuracy figure for the Serrano-Gotarredona et al. 2015 "ConvNets
  experiments on SpiNNaker" DVS-symbol-recognition deployment, in the sources retrieved (would require
  direct PDF access to the ISCAS paper).
- Documented (not merely claimed) SpiNNaker2 commercial scale as of the 2026 present: largest
  system stood up is 30,000 chips at TU Dresden (per SpiNNcloud CEO statement in EE Times, mid-2025);
  full 16-rack/69,120-chip/10.5-billion-neuron design has been announced but full completion status
  as of the 2026 present was not independently confirmed beyond the "half-scale, 5 billion neurons"
  2024 report and the 30,000-chip 2025 statement — treat "16 racks completed" as **NOT FOUND** /
  unconfirmed, only the design target is documented.
