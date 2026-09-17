# Simulator and Library Catalog: Per-Tool Fact Sheet

Read on 2026-09-17

## Brain Simulators

### NEST

**Registry key** No prior record was NEST's own page. vanalbada2018-spinnaker-nest is a SpiNNaker-vs-NEST performance comparison paper, not NEST documentation, so a new record was created, nest-docs.

**Page read** https://nest-simulator.readthedocs.io/en/stable/ ("Welcome to the NEST Simulator documentation!"); https://nest-simulator.readthedocs.io/en/stable/models/index.html ("Model directory"); https://nest-simulator.readthedocs.io/en/stable/installation/index.html ("Install and run NEST")

**Executes** "NEST is used in computational neuroscience to model and study behavior of large networks of neurons." The model directory states NEST "has over 100 models" of neurons, synapses, and devices, naming leaky/exponential/adaptive integrate-and-fire variants, Hodgkin-Huxley, Izhikevich, static and short-term-plasticity (Tsodyks) synapses, STDP variants, and gap junctions.

**Runs on** Linux, macOS, Windows, and cross-platform Docker, per the installation page; a dedicated section to "Optimize performance of HPC Systems" and a "Guide to parallel computing" for cluster/supercomputer use. GPU support not stated on the pages read.

**Reaches** not stated on the pages read (no neuromorphic hardware backend mentioned)

**A run can claim** "A NEST simulation is created with input from stimulation devices, neuron models, and synapse models, along with connection rules," a numerical simulation of network dynamics, not hardware execution.

**Quoted** "NEST is used in computational neuroscience to model and study behavior of large networks of neurons" (landing page); "has over 100 models" (Model directory); "Optimize performance of HPC Systems" (installation page)

### NEURON

**Registry key** No prior record was NEURON's own page. SJ-NeuronDocs is a SpikingJelly tutorial page that references NEURON concepts, not NEURON documentation, so a new record was created, neuron-docs.

**Page read** https://www.neuronsimulator.org/en/latest/ (landing page; redirect target of https://nrn.readthedocs.io/en/latest/). quickstart.html and about.html on the same site both returned 404 on retry.

**Executes** "NEURON is a simulator for neurons and networks of neurons." The landing page does not state which neuron/model classes (compartmental, ion-channel-based, or otherwise) it executes.

**Runs on** "runs efficiently on your local machine, in the cloud, or on an HPC," with Google Colab, the Neuroscience Gateway, and EBRAINS mentioned as hosted options. No CPU/GPU/MPI parallelization detail stated on the page read.

**Reaches** not stated on the page read (no neuromorphic hardware backend mentioned)

**A run can claim** not stated in those terms; the page says only that users "Build and simulate models using Python, HOC, and/or NEURON's graphical interface."

**Quoted** "NEURON is a simulator for neurons and networks of neurons"; "runs efficiently on your local machine, in the cloud, or on an HPC"; "Build and simulate models using Python, HOC, and/or NEURON's graphical interface"

### Brian2

**Registry key** New, staged as brian2-stimberg2019. The eLife article body (doi 10.7554/eLife.47314) was read directly, and `retrieval_status` is now `full_text` and `verification_status` is now `verified`, confirming the record's bibliographic metadata (Stimberg, Brette, Goodman; eLife 2019).

**Page read** https://elifesciences.org/articles/47314, sections: Abstract, eLife digest, Introduction, Materials and methods (Design and implementation; Mathematical level; Computational experiment level; Implementation level), Discussion, Appendix 1 (Design details)

**Executes** Neuron and synapse dynamics specified as differential equations in strings ("Differential equations are specified in strings using mathematical notation"), supporting hybrid systems of continuous dynamics and discrete events; point integrate-and-fire neurons, graded synapses with continuous post-synaptic effects, and limited multi-compartment models.

**Runs on** CPU by default, either a runtime mode calling generated C++ via the weave library, or a standalone mode that "executes an independent binary file compiled from C++ code," across Windows, OS X, and Linux. GPU acceleration is reached only through separate companion projects, not Brian2 itself (see Reaches).

**Reaches** No neuromorphic hardware backend stated anywhere in the body read. GPU is reached only via companion projects, "Brian2GeNN uses the GPU-enhanced Neural Network simulator (GeNN) to accelerate simulations," and Brian2CUDA is mentioned as an ongoing project at the time of writing.

**A run can claim** Numerical simulation of the specified differential-equation spiking-network model, not hardware execution.

**Quoted** "Differential equations are specified in strings using mathematical notation" (Materials and methods); "Standalone mode executes an independent binary file compiled from C++ code" (Materials and methods); "Brian2GeNN uses the GPU-enhanced Neural Network simulator (GeNN) to accelerate simulations" (Discussion)

### GeNN

**Registry key** No prior record was GeNN's own page. Turner22-mlGeNN is the mlGeNN paper, a library built on top of GeNN, not GeNN's own page, so a new record was created, genn-docs.

**Page read** https://genn-team.github.io/ (GeNN project homepage). https://genn-brian2.readthedocs.io/ (attempted first, 404) is not GeNN's own site. Fix round 2 added a documentation body page, https://genn-team.github.io/genn/documentation/4/html/d2/dba/SpineML.html ("GeNN: SpineML and SpineCreator," GeNN 4.9.0), since the homepage alone is a landing page, not a documentation body.

**Executes** "GeNN is a GPU enhanced Neuronal Network simulation environment based on NVIDIA CUDA technology," described as "a code generation framework for accelerated brain simulations." Specific neuron/synapse model classes are not enumerated on the homepage. The SpineML page describes running an already-built model through the GeNN simulator from the SpineCreator graphical editor, not the neuron/synapse model classes either.

**Runs on** NVIDIA GPUs via CUDA. The homepage states no CPU-only execution path, but the SpineML page names a "GENN_SPINEML_CPU_ONLY" environment variable, "If you would like SpineCreator to use GeNN in CPU only mode, add an environment variable called 'GENN_SPINEML_CPU_ONLY'," so a CPU-only mode exists for at least the SpineML integration, qualifying the homepage's stronger claim.

**Reaches** not stated as a backend; the homepage instead cites a claim that GPUs running GeNN "Outperform Current HPC and Neuromorphic Solutions in Terms of Speed and Energy When Simulating a Highly-Connected Cortical Model," positioning GeNN as an alternative to neuromorphic hardware, not a path onto it.

**A run can claim** GPU-executed, code-generated simulation of the specified brain model. Maintained by the GeNN Team (J. Knight, T. Nowotny, University of Sussex); foundational publication Yavuz, Turner and Nowotny 2016, Scientific Reports, doi 10.1038/srep18854 (cited by the team page; its own body was not re-read for this record).

**Quoted** "GeNN is a GPU enhanced Neuronal Network simulation environment based on NVIDIA CUDA technology"; "a code generation framework for accelerated brain simulations"; "Outperform Current HPC and Neuromorphic Solutions in Terms of Speed and Energy When Simulating a Highly-Connected Cortical Model"; "If you would like SpineCreator to use GeNN in CPU only mode, add an environment variable called 'GENN_SPINEML_CPU_ONLY'" (SpineML page, fix round 2)

### mlGeNN

**Registry key** Existing record: Turner22-mlGeNN. Task 2 separately registered the same paper as its own `mlgenn` source record, with a full-text read (Abstract, Section 2.1 GPU architecture, Figures 4-5, Table 2).

**Page read** Not re-fetched this pass; the fact below is carried from Task 2's full-text read of the same paper (`mlgenn` source record locators, Section 2.1 GPU architecture).

**Executes** A Python library that converts Keras-specified artificial neural networks to spiking networks via rate-based and few-spike ANN-to-SNN conversion, simulated using the GeNN framework.

**Runs on** NVIDIA GPUs via CUDA, through GeNN. No AMD support is stated in the text Task 2 read.

**Reaches** Not stated on the page read.

**A run can claim** GPU-executed, GeNN-simulated inference of a converted spiking network.

**Quoted** "GeNN (and therefore mlGeNN) utilises NVIDIA graphics processing units (GPUs) to compute neuronal and synaptic updates" (Section 2.1 GPU architecture, per the `mlgenn` source record).

### CARLsim

**Registry key** New, staged as carlsim. Authors corrected in fix round 2 to "T.-S. Chou, H. J. Kashyap, J. Xing, S. Listopad, E. L. Rounds, M. Beyeler, N. Dutt, J. L. Krichmar," the citation the GitHub README itself gives for CARLsim 4, in place of the earlier informal "Carrillo, S., Ros, E., and others."

**Page read** https://github.com/UCI-CARL/CARLsim5 (README and documentation)

**Executes** Izhikevich spiking neurons with realistic synaptic dynamics

**Runs on** CPU (generic x86), GPU (CUDA-enabled, compute capability 2.0+)

**Reaches** No neuromorphic hardware backends; simulation-only

**A run can claim** Efficient, GPU-accelerated simulation of large-scale spiking neural networks with high degree of biological detail

**Quoted** "an efficient, easy-to-use, GPU-accelerated library for simulating large-scale spiking neural network (SNN) models with a high degree of biological detail"

## Deep-SNN Libraries

### SpikingJelly

**Registry key** Existing records: spikingjelly-source-tonir, spikingjelly-loihi2-2026, SJ-ANN2SNNDocs, SJ-NeuronDocs

**Page read** https://spikingjelly.readthedocs.io/en/latest/tutorials/en/ann2snn.html (404 error); https://spikingjelly.readthedocs.io/en/latest/tutorials/en/neuron.html (available)

**Executes** Neuron models (LIF and others documented in registry); ANN to SNN conversion tools

**Runs on** CPU, GPU (PyTorch framework)

**Reaches** Lava (NIR exchange through spikingjelly-source-tonir), Loihi 2 (mentioned in spikingjelly-loihi2-2026)

**A run can claim** Simulation of spiking neural networks; ANN-to-SNN conversion

**Quoted** Registry titles: "SpikingJelly nir_exchange/to_nir.py module source", "SpikingJelly docs, ANN2SNN tutorial"

### snnTorch

**Registry key** Existing records: snnTorch-Docs, snntorch-docs, snntorch

**Page read** https://snntorch.readthedocs.io/en/latest/snn.neurons_leaky.html (excerpt)

**Executes** First-order leaky integrate-and-fire neuron model where membrane potential decays exponentially with configurable rate beta

**Runs on** CPU, GPU through PyTorch framework

**Reaches** Conversion to Norse through NIR (Neuromorphic Intermediate Representation) mentioned in registry

**A run can claim** Simulation of spiking neural networks; support for deep learning with SNNs

**Quoted** "First-order leaky integrate-and-fire neuron model" with "membrane potential decays exponentially with rate beta"

### Norse

**Registry key** Existing records: Norse-Docs, norse-docs, norse-nir-thirdparty

**Page read** https://norse.github.io/norse/auto_api/norse.torch.functional.lif.html (excerpt)

**Executes** LIF (Leaky Integrate-and-Fire) with variants: LIF with refractory periods, correlation-based LIF, adaptive exponential LIF; IAF, Izhikevich, LSNN, COBA LIF

**Runs on** CPU, GPU through PyTorch framework

**Reaches** Conversion capability through NIR to other tools

**A run can claim** Deep learning with spiking neural networks; gradient-based training of SNNs

**Quoted** "A library to do deep learning with spiking neural networks"

### Lava

**Registry key** Existing records: lava-nc-homepage, lava-v0-10-release, lava-github-archived, lava-exec, and others

**Page read** https://lava-nc.org/ (homepage excerpt)

**Executes** LIF (Leaky-Integrate-and-Fire) neurons, Dense connections, Convolutional operations, Spike generation utilities, Learning rules including STDP

**Runs on** CPU, GPU

**Reaches** Intel Loihi neuromorphic chips (primary commercial target)

**A run can claim** Neuromorphic processing with "gains in energy efficiency and speed compared to conventional computer architectures"; asynchronous, event-based message passing

**Quoted** "LIF (Leaky-Integrate-and-Fire) neurons"; "platform-agnostic so that applications can be prototyped on conventional CPUs/GPUs and deployed to heterogeneous system architectures spanning both conventional processors as well as a range of neuromorphic chips"

### Lava-DL

**Registry key** Existing records: lava-dl-docs, lava-dl-readme, lava-dl-netx-docs, lava-dl-slayer-docs

**Page read** https://lava-nc.org/lava-lib-dl/bootstrap/bootstrap.html (landing page); registry documents archived status

**Executes** Deep learning training and deployment framework for neuromorphic inference

**Runs on** CPU, GPU

**Reaches** Designed for Loihi neuromorphic hardware (via Lava core)

**A run can claim** Training and deployment of deep SNNs for neuromorphic hardware execution

**Quoted** Registry note: "lava-nc/lava-dl GitHub repository (archived)" with archival notice May 2026

### Nengo

**Registry key** Existing records: NengoDL-Rasmussen19, nengo-dl, and NengoLoihi-specific records

**Page read** https://nengo.ai/nengo-dl/examples/from-tensorflow.html (excerpt); https://nengo.ai/nengo-loihi/overview.html (excerpt)

**Executes** Neural network simulations supporting both traditional and spiking neural networks; Nengo models with learnable parameters

**Runs on** CPU, GPU (NengoDL via TensorFlow); can reach Loihi hardware through NengoLoihi

**Reaches** Intel Loihi (via NengoLoihi backend); multiple neuromorphic backends listed in documentation (NengoFPGA, NengoOCL, NengoSpiNNaker)

**A run can claim** Deep learning parameter optimization; SNN training; hardware execution on Loihi via emulator or direct hardware backend

**Quoted** From registry: "Simulating a network with NengoDL"; "Running on neuromorphic hardware"; NengoLoihi "runs Nengo models on Loihi boards"

### NengoDL

**Registry key** Existing records: NengoDL-Rasmussen19, nengo-dl

**Page read** https://nengo.ai/nengo-dl/ (landing page excerpt)

**Executes** Neural network simulations with Nengo, supporting batch processing and deep learning

**Runs on** CPU, GPU (via TensorFlow backend)

**Reaches** Can route to neuromorphic hardware through other Nengo backends

**A run can claim** Deep learning parameter optimization for SNNs; training with gradient descent

**Quoted** Documentation references "Simulating a network with NengoDL" and multiple "neuromorphic backends"

### NengoLoihi

**Registry key** Existing records: NengoLoihi-Docs, nengo-loihi, nengoloihi-cifar10-example

**Page read** https://nengo.ai/nengo-loihi/overview.html (excerpt)

**Executes** Nengo models with neural components; runs large-scale neural simulations

**Runs on** Host CPU (for emulator); Loihi hardware itself

**Reaches** Intel Loihi neuromorphic processor with two execution pathways: emulator backend (pure Python with NumPy) and hardware backend (via NxSDK API)

**A run can claim** Emulation of models on CPU; direct execution on Loihi hardware, though with performance degradation due to float-to-integer conversion; optimization can recover performance

**Quoted** "emulator backend: pure Python implementation using NumPy"; "hardware backend uses Intel's NxSDK API to execute models directly on Loihi boards"; "degraded performance due to the discretization process"

### BindsNET

**Registry key** Existing record: BindsNET18 (journal paper, not direct tooling documentation)

**Page read** BindsNET18 is peer-reviewed publication, not official documentation page

**Executes** Machine learning-oriented spiking neural networks

**Runs on** not stated on available page

**Reaches** not stated on available page

**A run can claim** Library for machine learning with SNNs

**Quoted** "BindsNET: A Machine Learning-Oriented Spiking Neural Networks Library in Python" (journal title)

### Rockpool

**Registry key** Existing records: rockpool-quickxylo-docs, rockpool-xylo-docs, rockpool-xyloa3-docs

**Page read** https://rockpool.ai/ (homepage excerpt)

**Executes** Dynamical neural network architectures, particularly Leaky Integrate-and-Fire (LIF) neurons for event-driven networks

**Runs on** CPU, GPU (supports JAX, PyTorch training backends)

**Reaches** Xylo family (digital SNN cores: Xylo, Xylo Audio 2, Xylo Audio 3, Xylo IMU); DYNAP-SE2 mixed-signal processor

**A run can claim** Training and evaluation of spiking neural networks; interoperability through NIR for import/export to other toolchains

**Quoted** "A Python package for working with dynamical neural network architectures, particularly for designing event-driven networks for Neuromorphic computing hardware"; "supports multiple training backends: JAX, PyTorch"

### Sinabs

**Registry key** Existing records: Sinabs-FromTorch, sinabs, sinabs-docs, sinabs-docs-overview, sinabs-nir, Sinabs-TrainingTips

**Page read** https://sinabs.readthedocs.io/main/api/from_torch.html (excerpt)

**Executes** Integrates PyTorch models, converting ReLUs and NeuromorphicReLUs into SpikingLayers; supports Integrate-and-Fire (IAF) neurons including IAFSqueeze

**Runs on** CPU, GPU (PyTorch backend)

**Reaches** Speck neuromorphic chip (via sinabs-nir-to-speck-tutorial in registry)

**A run can claim** Conversion of standard PyTorch models to SNNs; deployment to neuromorphic hardware (Speck)

**Quoted** "analyzes the modules in the model and returns a copy, with all ReLUs and NeuromorphicReLUs turned into SpikingLayers"

### SNN Toolbox

**Registry key** Existing records: snntoolbox-docs, snntoolbox-issues, snn-toolbox-github

**Page read** https://snntoolbox.readthedocs.io/en/latest (homepage excerpt)

**Executes** Transforms rate-based artificial neural networks into spiking neural networks using various spike encodings

**Runs on** CPU (simulation focus)

**Reaches** SpiNNaker neuromorphic hardware; Loihi processors; simulation backends (pyNN, Brian2)

**A run can claim** ANN-to-SNN conversion; simulation and neuromorphic hardware deployment

**Quoted** "transform[s] rate-based artificial neural networks into spiking neural networks" and "runs them using various spike encodings"

## Chip Backends and Emulators

### Lava Loihi Simulator

**Registry key** Covered by Lava records (lava-nc-homepage, lava-exec); no separate simulator-specific record

**Page read** Loihi simulator functionality documented within Lava framework pages

**Executes** LIF neurons and Lava processes, emulating Loihi behavior

**Runs on** CPU

**Reaches** Intel Loihi (emulation of behavior, not execution on hardware)

**A run can claim** Bit-accurate simulation of Loihi neuromorphic processor behavior

**Quoted** From Lava documentation: "can be prototyped on conventional CPUs/GPUs"

### NxSDK

**Registry key** New, staged as nxsdk (unchanged; page still unreadable, see below)

**Page read** Retried this pass, https://github.com/IntelLabs/nxsdk (404, no such repository) and https://intel-ncl.atlassian.net/wiki/spaces/NIC/overview (Confluence "Page Not Found," login-gated). No accessible NxSDK documentation page was found; the staged record is kept as-is.

**Executes** not stated on pages attempted

**Runs on** Not fully documented; implied CPU and Loihi hardware interface

**Reaches** Intel Loihi neuromorphic processor

**A run can claim** Execution on Intel Loihi hardware

**Quoted** Referenced in NengoLoihi documentation: "hardware backend uses Intel's NxSDK API to execute models directly on Loihi boards"

### sPyNNaker

**Registry key** Existing records: rhodes2018-spynnaker, spynnaker, spynnaker-v8-docs

**Page read** https://pmc.ncbi.nlm.nih.gov/articles/PMC6257411 (journal article excerpt)

**Executes** Spiking neural networks defined through PyNN interface; supported neuron models include Leaky Integrate-and-Fire (LIF) current-based, Izhikevich, custom extensible models

**Runs on** SpiNNaker neuromorphic hardware exclusively. Re-checked this pass against the cited page (`rhodes2018-spynnaker`, the PMC article), which does state the core and memory figures. "Each core contains an ARM968 (ARM, 2004)... Each core operates at 200 MHz clock speed... Each core has 96 kB of tightly coupled memory (TCM), which to avoid contention is split, 32 kB for instructions (ITCM) and 64 kB for data (DTCM)... Each chip has an additional 128 MB of shared memory (SDRAM), directly accessible by all cores on the chip."

**Reaches** SpiNNaker neuromorphic processor

**A run can claim** Realtime execution of large-scale networks on SpiNNaker hardware; processes over 5000 synaptic events per core

**Quoted** "Leaky Integrate-and-Fire (LIF): current-based formulation"; "Izhikevich neuron"; "realtime execution of large-scale networks"; "processes over 5,000 synaptic events on cores simulating 255 neurons"; "Each core contains an ARM968 (ARM, 2004)... Each core operates at 200 MHz clock speed... Each core has 96 kB of tightly coupled memory (TCM)... Each chip has an additional 128 MB of shared memory (SDRAM)" (fix round 2, traced to the page)

### hxtorch

**Registry key** Existing records: hxtorch, spilger2020-hxtorch, spilger2022-hxtorchsnn. The `hxtorch` record's own url was opened this pass, https://electronicvisions.github.io/documentation-brainscales2/latest/brainscales2-demos/ts_12-hxtorch_snn_intro.html ("hxtorch.snn Introduction"), confirming it is BrainScaleS-2's own documentation, not merely a mention.

**Page read** https://electronicvisions.github.io/documentation-brainscales2/latest/brainscales2-demos/ts_12-hxtorch_snn_intro.html (the `hxtorch` registry record's own url; the previously attempted `.../brainscale` path 404'd because it was truncated)

**Executes** Spiking leaky integrate-and-fire (LIF) neurons and a non-spiking leaky-integrator (LI) output neuron layer, combined with Synapse layers for weighted connections, built as PyTorch-like modules ("Network layers in `hxtorch` are derived from a parent class `HXModule` (similar to `torch.nn.Module` in PyTorch)").

**Runs on** Two modes, actual hardware execution on the BrainScaleS-2 chip, or a mock/simulation mode enabled by "setting `mock=True` in the `Experiment` instance."

**Reaches** The BrainScaleS-2 neuromorphic chip; membrane potentials are read out via the chip's columnar ADC (CADC) and membrane ADC (MADC), and weights on hardware are constrained to the range -63 to 63.

**A run can claim** Either genuine execution on BrainScaleS-2 hardware (with "returned hardware data ... mapped to a dense time grid") or a numerical mock/simulation when `mock=True`; the page distinguishes the two rather than treating them as equivalent.

**Quoted** "spiking leak-integrate and fire (LIF)"; "non-spiking leak-integrator (LI) output neuron"; "Network layers in `hxtorch` are derived from a parent class `HXModule` (similar to `torch.nn.Module` in PyTorch)"; "Weights on hardware are between -63 to 63"

### Akida (MetaTF)

**Registry key** Existing records: akida-benchmarks2025, akida-hw-constraints, brainchip-akida-techbrief, brainchip-akida-user-guide

**Page read** https://doc.brainchipinc.com/user_guide/hardware/1.0.html (excerpt)

**Executes** Spiking neural networks converted from convolutional neural networks (CNN2SNN conversion); neuron models not explicitly specified in page read

**Runs on** CPU, GPU (for model preparation and conversion); Akida 1.0 IP-based solutions (AKD1000, AKD1500 reference SoCs)

**Reaches** BrainChip Akida neuromorphic processors (AKD1000, AKD1500)

**A run can claim** Power-efficient inference execution on Akida neuromorphic hardware; energy per inference tracking via PowerMeter

**Quoted** "CNN2SNN conversion tools that transform standard CNN architectures into SNN-compatible formats"; "Akida 1.0 IP-based solutions, such as the AKD1000 and AKD1500 reference SoCs"

### Xylo Simulator

**Registry key** Covered by Rockpool records (rockpool-xylo-docs, rockpool-quickxylo-docs)

**Page read** https://rockpool.ai/devices/xylo-overview.html (excerpt)

**Executes** Spiking leaky integrate-and-fire neurons with exponential input synapses; digital LIF with configurable per-neuron time constants, thresholds, biases

**Runs on** CPU

**Reaches** Xylo SNN neuromorphic core (for deployment after training/simulation)

**A run can claim** Simulation and training of spiking networks for deployment to Xylo hardware; ultra-low-power (sub-mW) inference

**Quoted** "spiking leaky integrate-and-fire neurons with exponential input synapses in a synchronous, time-stepped architecture"; "Training a spiking network to deploy to the Xylo digital SNN"

### samna for Speck

**Registry key** rockpool-xyloa3-docs is a Rockpool/Xylo page and sinabs-nir-to-speck-tutorial is a Sinabs page; neither is samna's own documentation, and `grep -c '"id": "samna' data/source-registry.json` returned 0, so a new record was created, samna-docs.

**Page read** https://synsense-sys-int.gitlab.io/samna/0.48.6/index.html ("Welcome to Samna's Documentation!"), the redirect target of https://synsense-sys-int.gitlab.io/samna/. Fix round 2 added a chip-specific page, https://synsense-sys-int.gitlab.io/samna/0.46.1/models/speckSeries/summary.html ("Speck Series," samna v0.46.1 documentation).

**Executes** "Samna is the API to interact with SynSense devices from your PC." It provides device configuration, event-data routing, and device management, not a neuron model in its own right.

**Runs on** Host PC via Python bindings; specific supported operating systems not stated on the page read.

**Reaches** The Speck Series page (fix round 2) names the chip directly, "Speck is a comprehensive, multicore spiking neural network processing chip which is able to support large-scale spiking convolutional neural network (SCNN) with an fully asynchronous chip architecture," and states it integrates a dynamic vision sensor for "fully event-driven based, real-time, highly integrated solution for varies dynamic visual scene," with "a response latency in few ms" at milliwatt-scale power. This resolves the earlier gap, the landing page alone did not name Speck, Xylo, or DYNAP.

**A run can claim** Direct interaction with and control of the physical SynSense device from the host PC, not a simulation.

**Quoted** "Samna is the API to interact with SynSense devices from your PC."; "Speck is a comprehensive, multicore spiking neural network processing chip which is able to support large-scale spiking convolutional neural network (SCNN) with an fully asynchronous chip architecture"; "a response latency in few ms" (Speck Series page, fix round 2)

## Hardware Emulation

### APEX

**Registry key** Existing record: apex

**Page read** https://arxiv.org/abs/2608.19046 (paper abstract and section excerpts)

**Executes** PASC-IF (Precise ANN-SNN Conversion Integrate-and-Fire) neuron for efficient inference

**Runs on** Specialized hardware accelerator (fully combinational circuit)

**Reaches** No external neuromorphic backends; APEX itself is a hardware emulation device

**A run can claim** Bit-accurate ANN-to-SNN conversion with mathematical equivalence; energy reduction up to 40%, accuracy within 3% of source ANN

**Quoted** "integrates the PASC-IF neuron into the LoAS hardware framework"; "Up to 3% higher accuracy than the standard IF neuron"; "40% energy reduction for best accuracy configurations"

### NeuroFlex

**Registry key** Existing record: neuroflex

**Page read** https://arxiv.org/abs/2511.05215 (paper abstract and results excerpts)

**Executes** Hybrid execution of artificial neural networks and spiking neural networks; supports VGG-16, ResNet-34, GoogLeNet, BERT models

**Runs on** Dedicated column-level accelerator for edge computing (INT8 storage with integrated spike generation)

**Reaches** No external backends; NeuroFlex itself is a hardware accelerator

**A run can claim** Fine-grained hybrid ANN-SNN execution; 57-67% energy-delay product reduction versus ANN-only; up to 2.5x speedup compared to LoAS

**Quoted** "co-executes artificial and spiking neural networks to minimize energy-delay product on sparse edge workloads"; "fine-grained and integer-exact hybridization outperforms single-mode designs"

### SENECA

**Registry key** Existing records: seneca, Shidqi22-SENECAThesis

**Page read** https://www.frontiersin.org/articles/10.3389/fnins.2023.1187252/full (journal article excerpt)

**Executes** Digital neuromorphic architecture executing special operations common among many neuron models (construct IF through instruction sequences without hardware specialization)

**Runs on** GF-22 nm synthesized silicon (0.47 mm2 per core, scalable through network-on-chip)

**Reaches** No external backends; SENECA itself is a neuromorphic processor

**A run can claim** Programmable execution of diverse neural network algorithms; on-device learning (e-prop); energy efficiency at 2.8 pJ per synaptic operation

**Quoted** "digital neuromorphic architecture that balances the trade-offs between flexibility and efficiency"; "2.8 pJ per synaptic operation"; "supports fully-connected layers, convolutional processing, and on-device learning"

### FPGA emulation of a named chip

**Registry key** No prior registry record covers an FPGA emulating a named neuromorphic chip; the seven existing FPGA-family records (APEX, NeuroFlex, SENECA, plus SyncNN, Cerebron, Firefly, XpikeFormer already in `data/evidence-papers.json`) are accelerators of their own, not emulations of another named chip's architecture. New record created, `fpga-truenorth-emulation`.

**Query and date** exa search (`mcp__plugin_exa_exa__web_search_exa`), 2026-09-17, "FPGA emulation of Loihi or TrueNorth or SpiNNaker or BrainScaleS chip, cycle-accurate hardware emulator, published 2015 or later." Returned Valancius et al., "FPGA Based Emulation Environment for Neuromorphic Architectures" (2020 IEEE IPDPSW), among other results (a 2018 IEEE TCAD "FPGA-Based Hardware Emulator for Neuromorphic Chip With RRAM," and Brian2Loihi, a software, not FPGA, Loihi emulator).

**Page read** https://ar5iv.labs.arxiv.org/html/2004.06061 (arXiv mirror of the published paper; Abstract, Section I Introduction, Section II Reference Architecture Overview and Implementation, Table II)

**Executes** A per-core reimplementation of IBM TrueNorth's five components, neuron block, core SRAM, router, scheduler, and token controller, "we recreate and implement the TrueNorth architecture as a reference design on the Xilinx Zynq UltraScale+ MPSoC ZCU102."

**Runs on** A Xilinx Zynq UltraScale+ MPSoC ZCU102 development board (XCZU9EG FPGA, per Table II's resource-usage breakdown).

**Reaches** Not applicable; the FPGA design is itself the emulated target, not a path onto physical TrueNorth silicon.

**A run can claim** Functional verification against IBM's own TrueNorth simulator (Compass) on an MNIST network and a vector-matrix-multiplication case study, plus a demonstrated architectural change (an asymmetric-threshold fix) that "reduces the resource requirements of the VMM networks by 50%" without accuracy loss on either case study.

**Quoted** "We prototype IBM's TrueNorth architecture as a reference design"; "we recreate and implement the TrueNorth architecture as a reference design on the Xilinx Zynq UltraScale+ MPSoC ZCU102"; "reduces the resource requirements of the VMM networks by 50%"

## Pages Not Read

- NxSDK: No official standalone documentation page located after retrying https://github.com/IntelLabs/nxsdk (404) and Intel's INRC Confluence space (login-gated, page not found); referenced only through NengoLoihi and Lava documentation. Staged record `nxsdk` kept as-is.
- NEURON: quickstart.html and about.html on neuronsimulator.org both returned 404; only the landing page (https://www.neuronsimulator.org/en/latest/) was read, so neuron-docs is staged `metadata_only`.

Resolved this pass (previously listed here, now read): GeNN, at its own homepage https://genn-team.github.io/ (the earlier https://genn-brian2.readthedocs.io/ 404 was never GeNN's own site); hxtorch, at the existing registry record's own url (the earlier attempt 404'd on a truncated path).

Resolved in fix round 2 (previously listed here, now read): samna's chip-specific pages, the Speck Series page under https://synsense-sys-int.gitlab.io/samna/0.46.1/models/speckSeries/summary.html names and describes the Speck chip directly.
