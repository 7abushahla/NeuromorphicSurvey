# Conventional deployment evidence (Task 2)

Eleven new `papers[]` records (ten in the first pass, one more, `anglo-mixed-snn-mcu`, in fix
round 1) were added to `data/evidence-papers.json` to fill the conventional-hardware gap (`GPU`,
`CPU`, `MCU`, `RISC-V`, `NPU`) that Task 1's audit of the original 79 records left empty. Their
sources, plus seven catalog-tool sources merged in from Task 3's staged output in fix round 1, are
registered in `data/targets-sources.json` (rank 6 input to `tools/build-source-registry.py`). This
file records the candidate search (Step 2, done by a retrieval agent), the reading and grading of
each candidate (Step 3), which kinds still lack a measured run, and the fix-round-1 corrections
directed by the controller (see "Fix round 1" below).

## Seeds and queries

Carried from `.superpowers/sdd/2026-09-17-where-an-snn-runs/task-2-candidates.md` (built by the
retrieval agent per the brief's Step 2):

- (a) `research/prior-surveys/S37-gpu-riscv-acceleration.md`: GPU and RISC-V acceleration for SNNs
- (a) `research/prior-surveys/S36-edge-modalities-benchmark.md`: Edge device benchmarks and SNN deployment
- (b) `site/sec-12.html` subsection 12.6: mlGeNN on GPU, BIDL with CPU/GPU fallback, Lynxi KA200
- (b) `site/sec-06.html`: EventProp against Jetson Orin Nano baseline
- (c) `data/evidence-papers.json`: records mentioning GPU, CPU, Jetson, Cortex, RISC-V, x86, Xeon, NVIDIA, RTX, A100, V100

Exa queries executed 2026-09-17 by the retrieval agent:

1. GPU: "paper reporting measured latency and energy of a spiking neural network trained or run with SpikingJelly or snnTorch on an NVIDIA GPU"
2. GPU: "paper benchmarking GeNN or mlGeNN spiking network simulation throughput on NVIDIA GPUs"
3. CPU cluster: "paper reporting NEST spiking network simulation wall-clock time on a CPU cluster or supercomputer"
4. MCU: "paper deploying a converted spiking neural network on an ARM Cortex-M microcontroller with measured latency and energy"
5. NPU/RISC-V: "paper running a spiking neural network on a neural processing unit such as Jetson Orin, Coral Edge TPU or a phone NPU with measured latency" and "paper reporting a RISC-V core or RISC-V based accelerator running a spiking neural network with measured performance"

All five queries returned candidates; 30 were tabled (see the candidate table below). This task
(Steps 1, 3, 4, 5, 6) read, graded, and reduced that table to ten accepted records.

## Candidate table (as carried from the retrieval agent, with corrections noted)

| # | Title | Year | Venue | Kind (table) | Disposition |
|----|-------|------|-------|------|-------------|
| 1 | SpikingJelly: An open-source ML infrastructure platform for spike-based intelligence | 2024→**2023** | Science Advances | GPU | **Accepted**, `spikingjelly` |
| 2 | mlGeNN: accelerating SNN inference using GPU-enabled neural networks | 2022 | Neuromorphic Computing and Engineering | GPU | **Accepted**, `mlgenn` |
| 3 | Benchmarking SpikingJelly-Based SNNs Against Conventional ANNs (MNIST, accuracy/SynOps) | 2025 | IEEE ICSEC | GPU | **Rejected**, no machine named |
| 4 | NEST-5g performance assessment report | 2017→**2018** | POP CoE | CPU | **Accepted**, `nest5g-k-computer` |
| 5 | Performance Comparison of SpiNNaker and NEST for a Full-Scale Cortical Microcircuit Model | 2018 | Frontiers in Neuroscience | CPU | **Accepted**, `van-albada-nest-spinnaker` |
| 6 | Fast Simulation of a Multi-Area Spiking Network Model of Macaque Cortex on an MPI-GPU Cluster | 2022 | Frontiers in Neuroinformatics | GPU, CPU | Not pursued (time budget; redundant with 4/5) |
| 7 | Spiking network simulation code for petascale computers | 2014 | Frontiers in Neuroinformatics | CPU | Not pursued (time budget; redundant with 4) |
| 8 | Deploying and Optimizing Embodied Simulations of Large-Scale SNNs on HPC Infrastructure | 2022 | Frontiers in Neuroinformatics | CPU | Not pursued (time budget; redundant with 4/5) |
| 9 | Efficient parameter calibration and real-time simulation of large-scale SNN with GeNN and NEST | 2023 | Frontiers in Neuroinformatics | GPU, CPU | Not pursued (time budget; ambiguous single-record headline kind; redundant with 2/5) |
| 10 | EdgeSpike: SNNs for Low-Power Autonomous Sensing in Edge IoT Architectures | 2025→2026 | arXiv:2604.27004 | MCU, GPU, CPU | **Rejected**, unreliable/fabricated indicators |
| 11 | Event Driven Spiking Neural Network Using Analog Mixed Signals | 2026 | Springer (SCIS 2025) | MCU | **Accepted**, `anglo-mixed-snn-mcu` (fix round 1) |
| 12 | Implementing Spiking Neural Networks on NPU-Equipped Microcontroller | 2025 | KTH degree project (DiVA) | MCU, NPU | **Accepted**, `onoszko-stm32n6-npu` |
| 13 | Memory-Decoupled Event-Driven SNN Deployment on Edge Microcontrollers | 2026 | IEEE ICSP | MCU | **Accepted**, `memory-decoupled-mcu` |
| 14 | Compression and Inference of SNNs on Resource-Constrained Hardware | 2025 | arXiv:2511.12136 | MCU, CPU | **Accepted**, `snntorch-portenta-h7` |
| 15 | When Spike Sparsity Does Not Translate to Deployed Cost: VS-WNO on Jetson Orin Nano | 2026 | arXiv:2604.17040 | NPU→**GPU** | Not pursued (Jetson is `GPU` per vocabulary, not `NPU`; GPU kind already covered twice) |
| 16 | High-Speed, Real-Time, Spike-Based Object Tracking and Prediction on Google Coral Edge TPU | 2020 | IEEE AICAS | NPU | **Accepted**, `coral-edge-tpu-tracking` |
| 17 | NeuromorphicRT: A Production-Grade SNN Runtime for Energy-Efficient Edge AI | 2026 | Zenodo | GPU, NPU, CPU | **Rejected**, unverifiable self-deposit |
| 18 | Ev-Edge: Efficient Execution of Event-based Vision Algorithms on Commodity Edge Platforms | 2024 | arXiv:2403.15717 | GPU, CPU, NPU | Not pursued (time budget; all three kinds already covered) |
| 19 | Realtime Facial Expression Recognition: Neuromorphic Hardware vs. Edge AI Accelerators | 2024 | arXiv:2403.08792 | GPU, NPU, CPU | Not pursued (time budget; all three kinds already covered) |
| 20 | FeNN: A RISC-V vector processor for SNN acceleration | 2025 | NICE 2025 / arXiv:2506.11760 | RISC-V | **Accepted**, `fenn-riscv` |
| 21 | FeNN-DMA: A RISC-V system-on-chip for SNN acceleration | 2026 | Neuromorphic Computing and Engineering | RISC-V | **Accepted**, `fenn-dma-riscv` |
| 22 | RV-SCNN: A RISC-V Processor With Customized Instruction Set for SNN and CNN Inference Acceleration | 2024 | IEEE TCAD | RISC-V | Not pursued (time budget; RISC-V already covered twice) |
| 23 | SNAP-V: A RISC-V SoC with Configurable Neuromorphic Acceleration |, | arXiv:2603.11939 | RISC-V | Not pursued (time budget; RISC-V already covered twice) |
| 24 | Spike-RISC: Algorithm/ISA Co-Optimization for Efficient SNNs on RISC-V | 2025 | IEEE Access | RISC-V | Not pursued (time budget; RISC-V already covered twice) |
| 25 | Polaris 23: high throughput neuromorphic processing element by RISC-V custom instruction extension | 2025 | Journal of Supercomputing | RISC-V | Not pursued (time budget; RISC-V already covered twice) |
| 26 | RSPE: A High Energy Efficient SNN Inference Processor with RISC-V based Dynamic Pruning | 2025 | IEEE AICAS | RISC-V | Not pursued (time budget; RISC-V already covered twice) |
| 27 | A Complete Pipeline for deploying SNNs with Synaptic Delays on Loihi 2 (EventProp) | 2025 | arXiv:2510.13757 | GPU | **Rejected**, duplicate of existing neuromorphic record `eventprop-delays`; Jetson number is a cited comparator |
| 28 | Online Continual Learning on Intel Loihi 2 via Co-designed SNN | 2025 | arXiv:2511.01553 | NPU | **Rejected**, duplicate of existing neuromorphic record `clp-snn`; Jetson number is a cited comparator |
| 29 | SNN on Neuromorphic Hardware for Energy-Efficient SLAM | 2019 | arXiv:1903.02504 | CPU | **Rejected**, duplicate of existing neuromorphic record `tang-slam-loihi`; CPU number is a comparator |
| 30 | Reinforcement co-Learning of Deep and SNNs for Energy-Efficient Mapless Navigation | 2020 | arXiv:2003.01157 | GPU | **Rejected**, duplicate of existing neuromorphic record `sddpg`; Jetson TX2 number is a cited comparator |

Corrections made while reading the primary sources (candidate table values were provisional,
per the brief): candidate 1's year is 2023, not 2024 (Science Advances volume 9, issue 40, confirmed
via a citing paper's reference list; the primary publisher page could not be fully re-crawled).
Candidate 4's report is dated 2018-04-09, not 2017 (2017 is the date of the pre-release NEST
version tag named inside the report, not the report's own date). Candidate 15 is mis-typed as
`NPU` in the retrieval table; per the target vocabulary, "a graphics processor, including embedded
modules such as Jetson" is `GPU`, so Jetson Orin Nano is never `NPU`.

## Accepted records

For each, the id, kind, qualifier, evidence grade, and the two sentences read: the one naming the
machine and the one stating the measurement, quoted from the retrieved text.

### `spikingjelly`, GPU, E1
Qualifier (updated, fix round 1): "NVIDIA A100-SXM-80GB GPU, PyTorch-based SpikingJelly CUDA
training acceleration". Confirmed against the arXiv preprint full text (arXiv:2310.16620v1, the
same work as the Science Advances publication: same title, authors, abstract, and 11x claim),
retrieved via curl + pypdf after the publisher page (science.org) remained blocked past the
introduction.
Machine sentence (arXiv:2310.16620v1, Experimental setup): "The experiments are performed on an
Ubuntu 18.04 server with an Intel Xeon Silver 4210R CPU, an NVIDIA A100-SXM-80GB GPU, and 256 GB
of memory."
Measurement sentence (Fig. 1d and surrounding text): "SpikingJelly has a notable training speed
advantage over other frameworks, yielding higher speedup when T is larger, e.g., up to 11× when
T = 32" (Spiking ResNet-18, surrogate-gradient training, vs. Norse 1.0.0 and SNNTorch 0.6.0); "As
Fig. 1d shows, SpikingJelly also achieves up to 2× speedup over other frameworks" for ANN2SNN
inference at T=128.
Author list confirmed from the arXiv PDF byline: Fang, W., Chen, Y., Ding, J., Yu, Z., Masquelier,
T., Chen, D., Huang, L., Zhou, H., Li, G., Tian, Y.

### `mlgenn`, GPU, E1
Qualifier: "NVIDIA Titan V GPU (12 GB), GeNN CUDA simulation".
Machine sentence (Figure 5 caption, full PDF): "A 12 GB Titan V GPU was used for all experiments."
Measurement sentence (abstract): "...performing inference using a VGG-16 model, trained on the
CIFAR-10 dataset, is 2.5× faster than BindsNet and, when using a ResNet-20 model trained on
CIFAR-10 with FewSpike ANN to SNN conversion, mlGeNN is only a little over 2× slower than
TensorFlow."

### `van-albada-nest-spinnaker`, CPU, E1
Qualifier: "Intel Xeon E5-2680v3 HPC cluster (NEST simulation); comparator SpiNNaker (physical
digital neuromorphic hardware) measured in the same paper".
Machine sentence (Materials and Methods, full PDF): "The NEST (version 2.8; Eppler et al., 2015)
simulations are performed on a high-performance computing (HPC) cluster with 32 compute nodes.
Each node is equipped with 2 Intel Xeon E5-2680v3 processors with a clock rate of 2.5 GHz, 128 GB
RAM, 240 GB SSD local storage, and InfiniBand QDR (40 Gb/s)."
Measurement sentence (Abstract/Results): "The lowest total energy consumption for NEST is reached
at around 144 parallel threads and 4.6 times slowdown. At this setting, NEST and SpiNNaker have a
comparable energy consumption per synaptic event."

### `nest5g-k-computer`, CPU, E1
Qualifier: "K computer (Fujitsu SPARC64 VIIIfx CPU nodes), up to 82,944 compute nodes / 663,552
threads".
Machine sentence (Section 1, full PDF): "Machine Description: K computer at RIKEN AICS, comprising
82,944 compute nodes connected by proprietary Tofu interconnect in a 6D mesh/torus... Each node has
a single Fujitsu SPARC64 VIIIfx 8-core 2.0 GHz processor..."
Measurement sentence (Section 4): "Figure 3 shows the weak scaling performance of NEST-5g from 128
to all 82,944 compute nodes of K computer. connect (build edge) time is roughly constant 80
seconds, whereas both prepare (presim) and run (sim) take exponentially longer with increasing
numbers of compute nodes."

### `onoszko-stm32n6-npu`, NPU, E1
Qualifier: "STM32N657X0 MCU-embedded ST Neural-ART NPU; comparator Cortex-M55 CPU measured in the
same thesis".
Machine sentence (Chapter 5 Results, full PDF): "The values in Table 5.1 and Table 5.2 were
recorded during inference on the ST Neural-ART processor... The values in Tables 5.3 and 5.4 were
recorded during inference on the Cortex-M55 processor."
Measurement sentence (Tables 5.1-5.4): for the 1000-node, 10-layer model, the NPU takes 277.16 ms
and 50,965.60 µJ per sample versus 2096.48 ms and 225,784.64 µJ per sample on the Cortex-M55 CPU.

### `snntorch-portenta-h7`, MCU, E1
Qualifier: "Arduino Portenta H7 / STM32H747 Cortex-M7 @ 480 MHz; comparator desktop Intel Core
i3-10100F CPU measured in the same paper. Model is directly trained with surrogate gradients and
compiled to C, not an ANN-to-SNN converted network."
Machine sentence (Section III-B, full text): "The embedded target was an Arduino Portenta H7 board
..., featuring an STM32H747 microcontroller (Cortex-M7 @ 480 MHz with 512 KB SRAM, plus a
lower-power Cortex-M4)."
Measurement sentence (Section IV Results): "...a single-sample inference that took about 2.39 s on
SNNTorch (interpreted Python) executed in only 0.22 s with our C implementation – an ∼11×
speedup;" Figure 6 additionally reports a 7.4-7.5× speedup for the Arduino runtime over the
SNNTorch baseline on ST-MNIST.

### `memory-decoupled-mcu`, MCU, E1
Qualifier: "STM32H7 ARM Cortex-M7 MCU, physical benchmark".
Machine sentence (Abstract, metadata-only): "...our hardware-software co-optimization architecture
tailored for ARM Cortex-M7 processors... Physical benchmarks on the STM32H7 MCU across both static
MNIST and continuous Speech wake-word tasks..."
Measurement sentence (Abstract): "Evaluated on the MNIST task using a recurrent SNN (784-256-10)
with partial readout, the system achieves an inference latency of 197.69 ms and an energy
consumption of 76.98 mJ..."

### `fenn-riscv`, RISC-V, E1
Qualifier: "RISC-V (custom-ISA SNN vector processor, soft core on Kria KV260 FPGA); comparator
embedded GPU and Loihi cited in the same paper".
Machine sentence (Abstract, full PDF): "...we present a novel RISC-V-based soft vector processor
(FeNN), tailored to simulating SNNs on FPGAs."
Measurement sentence (Abstract/Section II-C): "...a single FeNN core can simulate an SNN classifier
faster than both an embedded GPU and the Loihi neuromorphic system"; and, more precisely, "This
classifier runs significantly faster than a similar model running on Loihi and twice as fast as
the same model running on an embedded GPU while using half the energy."

### `fenn-dma-riscv`, RISC-V, E1
Qualifier: "RISC-V (custom-ISA SNN system-on-chip, softcore on Kria KV260 FPGA)".
Machine sentence (Abstract, full PDF): "...here we present a novel, system-on-chip design using a
RISC-V softcore with a vector co-processor (FeNN-DMA), tailored to simulating SNNs on modern
UltraScale+ FPGAs."
Measurement sentence (fix round 2, re-read of Section 3.3 and Figure 6): "Points represent measured
simulation times... running on a single FeNN core," and "'Measured' is based on total simulation
time, 'Measured synapses' is calculated using performance counters around the event propagation
process group." This is a run of the design on the physical single-core FeNN-DMA SoC, with
simulation time and throughput read from on-chip performance counters, so E1 stands. Separately,
Results Section 3.1 and Table 2 give post-implementation EDA tool figures, not probe measurements
on the board. "...we achieved an operating frequency of 175 MHz for our single-core design..." and
Table 2's 0.53 W dynamic power, 54,984 LUTs, 47,759 FFs, all reported from Vivado
synthesis/implementation of the same design on the Kria KV260 device. Table 2's own footnote marks
some of the compared designs' power figures as produced "using a more accurate methodology based
on switching activity files," confirming these are post-implementation estimates, not physical
power-probe readings.

### `coral-edge-tpu-tracking`, NPU, E1
Qualifier: "Google Coral Edge TPU Dev Board (commercial NPU); comparator Intel Compute Stick
measured in the same paper".
Machine sentence (Section II Demo Setup, full text): "...these two tasks were implemented on two
different compact, computational platforms: the Intel Compute Stick, a full 64-bit, floating point
architecture and the aforementioned Google Edge TPU Dev, a 8-bit, fixed point architecture."
Measurement sentence (Table I): Power 5.48 W / Model Size 1.8 MB / Latency 27 ms / Computational
Efficiency 0.052 GOPS/mW (Intel Compute Stick) versus Power 1.72 W / Model Size 0.5 MB / Latency
4 ms / 1.057 GOPS/mW (Google Edge TPU).

## Fix round 1 (controller-directed correction)

Candidate 11 was originally rejected on a first, abstract-only reading, on the assumption that it
matched the comparator pattern of candidates 27-30 (a chip paper's own claim, with an externally
cited conventional-hardware number). The controller directed a re-read of the full chapter page,
which the earlier pass had not gone past the abstract for. The full text shows the paper measures
its own converted SNN on the Cortex-M4 directly, as one of its own two head-to-head hardware
platforms, not as a citation to another paper's number; and this is also the "converted network on
a Cortex-M MCU" case the brief's minimum set names, closing the one route gap noted in the first
pass (see "Kinds with no measured run," updated below). Accepted as `anglo-mixed-snn-mcu`, MCU, E1.

### `anglo-mixed-snn-mcu`, MCU, E1 (accepted in fix round 1)
Qualifier: "MCU (Cortex-M4 family, part not named; converted-SNN baseline in an analog-chip
paper)".
Machine sentence (Section 6.3 Hardware Platforms, full chapter page): "Digital MCU Baseline: All
models are deployed on the ARM Cortex-M4 MCU, representative of processors commonly used in
real-edge devices."
Measurement sentence (Section 7 Results): "the analog SNNs consume merely 24 microjoules per
inference, less than half the energy per inference of the 8-bit CNN on the MCU at 60 microjoules
and lower than that of the digital SNN at 48 microjoules"; and "digital SNNs on the Cortex-M4...
take about five to six milliseconds per inference." Section 4 gives the same digital-SNN baseline
more precisely: "The digital SNN intermediate baseline (48 uJ, 6.1 ms) achieves a 23% reduction in
energy compared to the 8-bit CNN."
Correction to the controller's ruling: the ruling's premise was that the analog comparator chip is
unnamed. The fuller text does name it: Section 5.2 ("There is limited evaluation to date on one AMS
platform only: Innatera SNP") and Section 6.3 ("Neuromorphic Deployment: ... more advanced
hardware such as Innatera SNP") both name it as the Innatera SNP. The qualifier's "analog-chip
paper" wording is kept (per the ruling's exact instruction), and the chip's name is recorded in
`target_hardware`, `evidence_notes`, and here, rather than repeated as unknown. The specific
Cortex-M4 part number (vendor, exact MCU model) is still not stated anywhere in the retrieved text,
which is what "part not named" refers to.
Title correction: the retrieval-agent candidate table's title, "Event Driven Spiking Neural
Network Using Anglo Mix Signals," is a transcription artifact; the publisher page's own rendered
title reads "Event Driven Spiking Neural Network Using Analog Mixed Signals." The source record
uses the corrected title.

## Rejected candidates, with reasons

- **#3** (SpikingJelly-Based SNNs vs Conventional ANNs, ICSEC 2025). Rejected: the abstract names
  no execution hardware (no GPU/CPU model). It measures only accuracy and SynOps, a software
  operation-count proxy, and explicitly states the study "sets the stage for future studies on...
  direct hardware energy measurements," meaning this paper does not itself perform one. A paper
  that does not name its machine is not evidence of a conventional target (Step 3's rule).
- **#10** (EdgeSpike, arXiv:2604.27004). Rejected as unreliable. Read in full: the byline credits a
  "Research Assistant" in a university Department of *Economics* for leading the SNN
  hardware-aware NAS and firmware work, paired with an implausible compound Nordic/Turkish
  invented-looking author name; the abstract claims a suspiciously over-precise and very broad set
  of results for a single, uncited arXiv preprint (five sensing tasks, three hardware targets,
  8,400-candidate NAS, a seven-month 64-node field deployment with day-level battery-life
  projections). These are the pattern of a fabricated or AI-generated paper-mill submission rather
  than a verifiable primary source, so it was not used as evidence.
- **#11**: no longer rejected. Accepted in fix round 1 as `anglo-mixed-snn-mcu`; see the "Fix round
  1" section above for the corrected reading and reasoning.
- **#15** (VS-WNO on Jetson Orin Nano). Rejected as an `NPU` candidate: per `data/target-kinds.json`,
  a Jetson module is `GPU` ("a graphics processor, including embedded modules such as Jetson"), not
  `NPU`. Not pursued as a third GPU record within the task's time budget, since GPU was already
  satisfied twice.
- **#17** (NeuromorphicRT, Zenodo). Rejected. A Zenodo self-deposit with no peer review, no
  citation record, and no independently verifiable venue found; combined with implausibly broad,
  polished multi-platform claims (Jetson Orin Nano and Raspberry Pi 5) that could not be checked
  against a reviewed or indexed publication, it was treated as unverifiable and not used as
  evidence.
- **#27, #28, #29, #30** (EventProp-delays Loihi 2 pipeline; Online Continual Learning on Loihi 2;
  SLAM on Loihi; SDDPG Loihi navigation). All four rejected as conventional-hardware evidence: each
  is the same paper already present in `data/evidence-papers.json` as an existing **neuromorphic**
  record (`eventprop-delays`, `clp-snn`, `tang-slam-loihi`, `sddpg` respectively, all graded E1 on
  physical Loihi). The Jetson Orin Nano / Jetson TX2 / CPU figure the candidate table lists for each
  is that paper's own *cited comparator* number, not a machine the paper itself measures as its
  subject. Per the controller ruling ("the machine their claim describes is the chip... prefer
  papers whose own claim is the conventional run"), these are not used a second time as
  conventional-hardware evidence.

Eleven further RISC-V, CPU-cluster, and multi-platform-comparator candidates (#6, #7, #8, #9, #18,
#19, #22, #23, #24, #25, #26) were not pursued within the task's time budget once their target
kind was already satisfied by two accepted records (or, for #6/#7/#8/#9, redundant with the
accepted CPU/NEST or GPU/GeNN routes); none of these were read in enough depth to grade,
so they are recorded here as "not pursued," not "rejected on the merits."

## Kinds with no measured run

All five conventional kinds (`GPU`, `CPU`, `MCU`, `RISC-V`, `NPU`) have at least one E1 measured
record; `MCU` now has three (`snntorch-portenta-h7`, `memory-decoupled-mcu`,
`anglo-mixed-snn-mcu`). The gap noted in the first pass is closed by fix round 1:
`anglo-mixed-snn-mcu` deploys its own CNN-to-SNN (TTFS) converted network on the Cortex-M4,
satisfying the brief's "one converted-network run on a Cortex-M MCU" minimum-set item literally.
The other two MCU records remain directly-trained (surrogate-gradient or hand-designed) SNNs
compiled or programmed onto Cortex-M7 hardware rather than converted networks, which is still
flagged in their own `target_qualifier` / `evidence_notes`, but with `anglo-mixed-snn-mcu` in hand
that no longer leaves the "converted network on Cortex-M" route without a record. No kind and no
named map route is left without a measured run.

## Step 5 command output (fix round 1, current)

```
python3 tools/build-source-registry.py && python3 tools/validate-sources.py && python3 tools/verify-source-registry-build.py && python3 tools/build-bib.py && python3 tools/check-bibliography.py 2>&1 | grep -o "'unresolved': [0-9]*" && python3 tools/build-data-views.py && python3 tools/check-counts.py && python3 tools/check-consistency.py && python3 tools/validate-evidence.py && python3 tools/verify-target-tools.py
```

```
build-source-registry: wrote 400 canonical records
validate-sources: 400 source record(s) valid
verify-source-registry-build: 30 contract checks passed
defined      : 400 canonical BibTeX entries
cited        : 228 canonical works from 234 keys
uncited      : 172 canonical works
aliased      : 7 reference keys (7 cited)
unresolved   : 0 cited keys; 0 uncited reference-only keys
duplicate    : 0 BibTeX definition keys
analysis-only: 3 canonical works (1 cited)
'unresolved': 0
wrote 5 data views to .../data/generated
check-counts: population exclusive algorithm=43 deployment=40 both=7 total_unique=90
check-counts: population inclusive algorithm=50 deployment=47 total_unique=90
check-counts: survey coverage surveys=37 axes=12
check-counts: 5 generated artifact(s), no stale unqualified population headlines
check-consistency: 6 regression contracts passed; sources=400 claims=48 nodes=138 edges=140 papers=90 surveys=37 platform_capabilities=99
check-consistency: all IDs and references resolve; evidence scope, measurement boundaries, and hardware-support provenance are explicit
validate-evidence: 48 claim record(s) and 99 platform capability record(s) valid
..... (5 tests) OK
```

The full chain exits 0. Counts moved from the original pass (392 registry records, 89 papers) to
400 registry records and 90 papers: +1 paper/source for `anglo-mixed-snn-mcu` (fix round 1, item
1), and +7 sources for Task 3's merged catalog records (fix round 1, item 3; these are sources
only, with no matching `papers[]` entries, so the paper count did not move for them).
`tools/check-bibliography.py` on its own prints `check-bibliography: FAILED: bibliography report
changed: {...}` and exits non-zero, because that script compares today's freshly built
bibliography against a hardcoded `EXPECTED_REPORT` snapshot pinned inside the script itself
(`defined: 352`, `cited: 284`, etc.), which was already stale before Task 2 (the committed
`data/source-registry.json` already held more records than that snapshot expects, independent of
Task 2's additions). `tools/build-bib.py` regenerates `assets/bibliography/references.bib` and
`data/bibliography-report.json` from the current source registry as an ordinary, expected side
effect of running it (the same way `build-source-registry.py` regenerates
`data/source-registry.json`); the new sources are added as uncited canonical BibTeX entries (no
`site/*.html` prose cites them yet, since Task 2's brief does not ask for
citation wiring). The brief's own Step 5 command only pipes `check-bibliography.py`'s output
through `grep -o "'unresolved': [0-9]*"`, which is satisfied (`'unresolved': 0`), so the overall
chain's exit code is 0. Updating `EXPECTED_REPORT` and the committed bibliography snapshot to a new
pinned baseline is not in Task 2's file list and was left untouched.

## Prose headline count check

`site/sec-16.html` states "Each of its 78 records..." and "Table 28: The 78-record audited corpus
in `data/evidence-papers.json`..." The actual record count is now 90 (79 before Task 2's first pass
added ten, 90 after fix round 1 added `anglo-mixed-snn-mcu`). This was already a stale prose count
before Task 2 ran: Task 1's own split of the `pascal` record into `pascal-none` and
`pascal-simulator` had already moved the true count from 78 to 79 without updating this sentence.
Task 2's additions widen the same gap (78 quoted in prose vs. 90 actual). Per this task's brief,
prose headline counts are Task 12's responsibility; this is reported, not edited, here.
