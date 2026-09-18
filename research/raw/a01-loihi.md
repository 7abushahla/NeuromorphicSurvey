# The Intel Loihi 1 / Loihi 2 Stack — Research Notes

Compiled for the neuromorphic-deployment survey. Every factual claim is sourced inline
with `[n]` pointing to the source list at the end. Where no evidence could be located,
this is stated explicitly as **NOT FOUND** rather than inferred.

---

## 1. Loihi 1 architecture

**Chip-level numbers.** Loihi 1 is a 60 mm² chip fabricated in Intel's 14 nm process,
2.07 billion transistors, 33 MB of SRAM, 128 neuromorphic cores plus 3 embedded x86
processor cores ("Lakemont" cores), functional over a 0.50–1.25 V supply range [1].
Officially quoted capacity: up to 128 K neurons and 128M synapses per chip [1][7]; the
Proceedings-of-the-IEEE survey gives a more precise 131,072 neurons over 128 cores, each
core holding 128 kB of synaptic state plus 20 kB of routing tables allocatable across its
1,024 neurons/compartments [2]. The mesh protocol supports scaling to 4,096 on-chip
cores and, hierarchically, up to 16,384 chips [1]. Loihi systems were scaled up to
Pohoiki Springs, a rack-mounted mesh of 768 Loihi chips implementing 100 million neurons,
made available to INRC members over the cloud [9][17].

**Time model / synchronization.** Loihi uses a fixed-size, discrete-time-step model:
"all neurons need to maintain a consistent understanding of time so their distributed
dynamics can evolve in a well-defined, synchronized manner" [1]. Synchronization across
cores (and, at scale, across the 98,304-core Pohoiki Springs mesh) is achieved via
explicit **barrier messages** exchanged between cores over the asynchronous
network-on-chip (NoC); the NoC carries write, read-request, read-response, spike, and
barrier message types, and the asynchronous blocking barrier handshake lets a timestep's
real-world duration vary with how much computation/communication the mesh needs to do on
that step [1][16]. The paper stresses that "these fixed-size, synchronized time steps
relate to the algorithmic time of the computation and need not have a direct
relationship to the hardware execution time" [1] — i.e., "T" (the number of algorithmic
timesteps) is a logical/synchronization unit, not a fixed wall-clock duration; wall-clock
time per timestep depends on spike traffic and congestion.

**Neuron model.** Loihi natively implements a two-stage cascaded discrete-time CUBA
(current-based) leaky-integrate-and-fire (LIF) neuron: a synaptic response current
u_i(t) (decaying, filtered sum of incoming weighted spikes plus bias) that is further
integrated into a leaky membrane potential v_i(t); a spike is emitted when v_i crosses
threshold θ_i, and v_i is "reset to 0 right after a spiking event occurs" [1][3]. This
hard reset-to-zero is the *native* mechanism; Loihi 1 has no built-in soft-reset
(reset-by-subtraction) primitive [3][8].

**Reset-by-subtraction on Loihi 1.** Because the chip only offers hard reset natively,
the NxTF compiler (Rueckauer et al.) implements soft reset via a **two-compartment
trick**: the neuron is split into a "soma" compartment that integrates voltage and fires,
and a second, recurrently-connected compartment that is silent until the soma spikes, at
which point it inhibits the soma with charge equal to the firing threshold — retaining
any excess charge above threshold rather than discarding it. This doubles the number of
compartments (hence neurons/memory) the network consumes on-chip, and NxTF's authors
explicitly list "a built-in soft reset as opposed to a hard reset mechanism" as a desired
future hardware feature so this compartment-duplication trick would no longer be needed
[3][8]. Directly-trained SLAYER models used hard reset (single compartment) [3].

**Spike payload.** Loihi 1's basic communication primitive is the binary spike. However,
"all communication between neurons occurs over spike events, 32-bit messages containing
destination addressing, and, **sometimes**, source addressing and graded-value payloads"
[2] — i.e., Loihi 1 already supported an optional graded (multi-bit) spike payload
mechanism at the message-format level, even though its dominant/idiomatic use in the
literature (and in the neuron model above) is binary spiking. Loihi 2 is the generation
that generalizes and prioritizes this into a first-class, microcode-driven graded-spike
feature (Section 2).

**Weight/state precision.** Loihi 1 synaptic weights support variable precision from 1
to signed 9 bits, and weight precision may be mixed with scale normalization even within
a single neuron's fan-out [1][2]. The full synaptic-variable/learning-engine microcode
table lists precisions for other variables: presynaptic spike count 5 b, traces 7 b,
synaptic weight 9 b (signed), delay 6 b, tag 9 b (signed), reward trace 8 b (signed) [1].
Total synaptic memory per chip is 16 MB; at Loihi's densest 1-bit synapse format this
gives 2.1 million unique synaptic variables per mm² [1].

**On-chip learning.** Each Loihi core includes a programmable microcode learning engine
operating on filtered pre-/post-synaptic spike traces, expressed in a sum-of-products
form over synaptic variables (weight, delay, tag) [1][2]. It supports simple pairwise
STDP as well as more complex rules: triplet STDP, reinforcement learning via synaptic tag
assignment, and rules referencing both rate-averaged and spike-timing traces [1]. This is
first-generation, single-compartment-oriented plasticity; genuine three-factor
(neuromodulated) learning with arbitrary microcode-computed modulatory terms is a Loihi 2
addition (Section 2).

**Core / neuron counts (summary table).**

| Metric | Loihi 1 |
|---|---|
| Process | Intel 14 nm [7] |
| Die area | 60 mm² [1] / 64 mm² (NICE talk slide) [6] |
| Neuromorphic cores | 128 [1][2] |
| Embedded x86 cores | 3 [1] |
| Max neurons/chip | 128,000 (128 K) [7] / 131,072 exact [2] |
| Max synapses/chip | 128 million [7] |
| Weight precision | 1–9 bits, signed, mixable [1][2] |
| Neuron state allocation | fixed at 24 bytes/neuron [7] |
| Spike format | binary by default; optional graded payload in 32-bit message [2] |

---

## 2. Loihi 2 architecture

**Chip-level numbers.** Loihi 2 is fabricated on Intel 4 (vs. Intel 14 nm for Loihi 1),
31 mm² die (vs. 60 mm²), 0.21 mm² core area (vs. 0.41 mm²), 2.3 billion transistors [7].
Officially: up to 128 neuron cores/chip (same max core count as Loihi 1, but denser),
6 embedded processors (up from 3), up to 1 million neurons/chip (vs. 128,000) and up to
120 million synapses/chip [7]. Independent papers describe "120" or "126–128" neuro
cores per chip depending on chip revision, each supporting up to ~8,192 (also reported as
8,190 or "~8k") programmable neurons [4][10][11][19]. Loihi 2 systems: single-chip "Oheo
Gulch" boards, 8-chip "Kapoho Point" boards (stackable in multiples of 8), and larger
systems including "Hala Point," described as scaling to 1 billion neurons and 128
billion synapses in fully digital stacked systems [11][14][19].

**What changed vs. Loihi 1 (Intel's own comparison table) [7]:**

| Resource/Feature | Loihi 1 | Loihi 2 |
|---|---|---|
| Process | Intel 14 nm | Intel 4 |
| Die area | 60 mm² | 31 mm² |
| Core area | 0.41 mm² | 0.21 mm² |
| Transistors | 2.1 billion | 2.3 billion |
| Max neuron cores/chip | 128 | 128 |
| Max processors/chip | 3 | 6 |
| Max neurons/chip | 128,000 | 1 million |
| Max synapses/chip | 128 million | 120 million |
| Memory/neuron core | 208 KB, fixed allocation | 192 KB, flexible allocation |
| Neuron models | Generalized LIF | Fully programmable (microcode) |
| Neuron state allocation | Fixed at 24 bytes/neuron | Variable, 0–4096 bytes/neuron, model-dependent |
| Information coding | Binary spike events | Graded spike events (up to 32-bit payload) |

**Programmable neuron models / microcode.** Loihi 2's central architectural change is a
microcode-programmable neural engine: "Users can allocate variables and execute a wide
range of instructions organized as short programs using an assembly language," with
access to neural state memory, the accumulated synaptic input for the current timestep,
random bits for stochastic models, and a timestep counter; the instruction set supports
conditional branching, bitwise logic, and fixed-point arithmetic via hardware
multipliers [4]. This is used to implement, beyond CUBA-LIF: Resonate-and-Fire (RF, a
complex-valued oscillatory neuron) [4][10], Izhikevich neurons [12], sigma-delta neurons
[15][19], and Hopf resonators for cochlea modeling [4]. Loihi implements the discrete
LIF as a_i[t] = Σ w_ij s_j[t−1]; u_i[t] = λ_u u_i[t−1] + a_i[t]; v_i[t] = λ_v v_i[t−1] +
u_i[t]; spike when v_i[t] exceeds threshold, with v_i[t] reset to 0 [4]. Loihi 2 keeps
this as one selectable microcode program among many rather than a fixed hardware
datapath.

**Graded (integer-payload) spikes.** Loihi 2 neurons can optionally generate and
transmit graded spikes, "a generalization of Loihi's binary spike messages," carrying a
**32-bit spike payload** specified by microcode; the integer payload multiplies the
weights of downstream synapses. Intel's own technical brief notes: "Typically, only
eight bits of precision are used, representing a negligible extra energy cost compared
to binary spike processing" [7]. Independent papers give overlapping but not identical
figures: an OSTI report on graded-spike arithmetic on Loihi 2 states each spike can pass
a **32-bit** integer value (0 to 2³²−1) [13]; the Sigma-Delta conversion paper describes
Loihi 2 graded spikes as holding "up to 16 bit signed integer payloads" in the neuron
microcode used for that project [15]; the S4D streaming-sequence paper reports using
**24-bit spike messages** and 24-bit neuron state in its own quantization scheme [19];
the MatMul-free-LLM-on-Loihi2 paper states "up to 32 bits for messages" and up to 160
million 32-bit integer messages/second for host I/O [20]. These are consistent with a
32-bit *architectural maximum* payload field that individual projects then configure
down (8-, 16-, or 24-bit) depending on microcode and use case; treat any specific
non-32-bit number as that paper's chosen configuration, not a hardware ceiling.

**Weight/state precision.** Intel's brief: "Neuron State Allocation... Variable from 0
to 4096 [bytes] per neuron depending on neuron model requirements" (vs. fixed 24 bytes on
Loihi 1) [7]. The MatMul-free-LLM paper states Loihi 2 synaptic weights are 8-bit by
default (extendable to 8n-bit via n chained 8-bit synapses with different fixed-point
exponents), with activations/messages up to 32-bit [20]. The Izhikevich-neuron
implementation paper reports Compartment (Cx) state registers with a 64-bit capacity,
internally composed of 8-, 16-, or 24-bit sub-fields depending on variable, and 8-bit
synaptic weights with 4 fractional bits in that specific implementation [12]. The S4D
paper's own PTQ scheme used 8-bit weights, 24-bit spike messages, 24-bit neuron state
[19]. **Caveat:** the "Catalyst N2" document that surfaced in search (a third-party,
self-published, non-peer-reviewed project claiming an independently built "full Loihi 2
feature parity" FPGA reimplementation) reports much more granular numbers (four graded
spike formats up to 24-bit, 1/2/4/8/16-bit weight packing) — this source is **not
official Intel documentation** and is excluded from the claims above; it is flagged here
only so it is not mistaken for a primary source if encountered elsewhere.

**Three-factor learning.** Loihi 2 "programmable neuron models may now manipulate
synaptic input received from its dendritic compartments with arbitrary microcode and
assign the results to third-factor modulatory terms available to a neuron's synaptic
learning rules" [7]. Lava's tutorial/documentation demonstrates reward-modulated STDP
(R-STDP), a three-factor rule, in simulation, noting: "though the RSTDPLIF Process can
currently only be executed on CPU backend, it is modeled from Loihi 2's ability to
compute custom post-traces in microcoded neuron instructions. Lava support for on-chip
execution will be available soon!" [18] — i.e., as documented, three-factor learning via
Lava was validated in CPU simulation with on-chip execution stated as forthcoming, not
confirmed as already running on physical Loihi 2 silicon in that tutorial. **NOT FOUND**:
a published, peer-reviewed paper demonstrating three-factor learning actually executing
on physical Loihi 2 silicon (as opposed to simulation or documentation claims). A related
Master's thesis (Politecnico di Torino) implements three-factor STDP rules for a
hippocampal-cortical memory model "in Lava" targeting Loihi 2, but the available excerpt
does not confirm physical-chip execution vs. simulation [21].

**Barrier synchronization on Loihi 2.** Confirmed to work the same way structurally:
"While the cores and chips of Loihi 2 system execute their computations asynchronously,
they synchronize via messages to adhere to a global, algorithmic time-step" [10][20]. Two
execution modes are described in practice: *pipelined* (a new input enters the network
every timestep, throughput-optimized) and *fall-through* (an input is injected only once
the prior input has fully propagated through the network, latency-optimized) [10][15].

---

## 3. Software stacks — precise chip targeting

| Stack | Targets | Status |
|---|---|---|
| **NxSDK / NxTF** | Loihi 1 only | Superseded; the codebase and workflow described in Rueckauer et al. are explicitly Loihi-1-era (NxCore register-level API, NxNet, NxTF) [3][8][23]. |
| **Lava (core) / Lava-DL / NetX** | Initially Loihi 2 only, later intended to extend to Loihi 1 | Archived by Intel, ~May 2026 [24][25][26]. |
| **NxTF on Loihi 2?** | **NOT FOUND.** No source located states NxTF/NxSDK was ported to or run on Loihi 2. INRC's own migration guidance instead tells members to move to Lava: "As of 2022, INRC members should use the open-source Lava framework to develop and evaluate spiking neural networks for Loihi 2. Older NxSDK models should be easily re-implemented in Lava" [22] — this explicitly implies NxSDK/NxTF was Loihi-1-targeted and not the forward path for Loihi 2. |
| **Lava on Loihi 1?** | Ambiguous/contested. | Lava's own v0.4.0 release notes state: "Lava does currently not support on-chip learning, **Loihi 1** and a variety of connectivity compression features" [23] (i.e., as of that release, Lava explicitly did *not* support Loihi 1). Separately, Lava's Developer Guide roadmap page lists "Loihi 1, 2" as a target for the Magma/Compiler/Runtime/process library, stating "Compiler, Runtime and the process library will be upgraded to support Loihi 1 and 2 architectures" [5] — phrased as a forward-looking upgrade, not a completed one. No source was found confirming Loihi 1 support was ever shipped and used in a published research result. Treat "Lava on Loihi 1" as, at best, a stated intention rather than a demonstrated capability. |

**NxSDK's own internal structure** supported three high-level APIs: the third-party
Nengo API, Intel's NxNet (full low-level structural access to cells/populations/synapses
with learning), and NxTF (the Keras-derived, DNN-application-focused API and compiler
introduced by Rueckauer et al.) — all compiling down through the register-level NxCore
API [3][8].

**Lava's own architecture**: a high-level, platform-agnostic Process/Process-model API
(CSP-style communicating sequential processes) on top of a low-level compiler/runtime
layer called Magma. Core Lava (BSD-3/LGPL-2.1) is openly available on GitHub; the
specific Magma components that compile processes to Intel Loihi hardware are proprietary
to Intel and released only as the "Lava extension for Loihi," gated to INRC members
[5][22][23]. Lava libraries: `lava` (core), `lava-optimization`, `lava-dl` (deep learning:
`slayer` for direct spike-based training, `bootstrap` for rate-coded SNN training, `netx`
for inference/deployment), `lava-dnf` (dynamic neural fields, robotics) [5][6][23].

---

## 4. NxTF specifics (physical Loihi 1)

**Networks converted and run on physical Loihi 1** (via SNN Toolbox / SNN TB conversion,
then NxTF compilation) [3][8]:

- **MNIST**: 4-layer CNN trained in Keras, 0.74% ANN error; converted via
  Rueckauer-et-al.-2017 rate-based encoding; mapped to **14 neurocores**. Reported: 0.79%
  error, 0.66 mJ energy, 6.65 ms delay, 4.38 µJ·s EDP on Loihi (vs. 0.74% error / 19 mJ /
  0.4 ms on CPU-Tensorflow and 0.74% / 111 mJ / 2 ms on GPU-Tensorflow) [3][8]. A separate
  comparison table (Quartz paper, citing this same NxTF/Rueckauer result) lists **100
  timesteps** for this MNIST rate-coded run [17].
- **CIFAR-10**: an off-the-shelf MobileNet converted and run on Loihi. Reported: **8.52%
  error rate** (lowest reported at the time for neuromorphic hardware), 102 mJ energy,
  340 ms delay, 34,926 µJ·s EDP; compared to 8.07% / 157 mJ / 3 ms (CPU) and 8.07% / 1035
  mJ / 18 ms (GPU) for the same ANN [3][8]. NxTF's own Sec. 3.2.3 states this MobileNet
  "fits on 861 cores when compiled by NxTF" across "the 7 chips required by MobileNet"
  [3][8]. The Quartz paper's comparison table cites the same NxTF result at **400
  timesteps**, but its **1,753 neuromorphic cores across 14 Loihi chips** figure
  describes Quartz's *own* CIFAR-10 network, not the NxTF MobileNet: "our SNN ends up
  being distributed across 1753 neuromorphic cores and 14 chips" [17], using on average
  only 3% of neurons per core because Loihi 1 lacked convolutional weight-sharing without
  heavy low-level engineering effort at the time [17].
- **N-MNIST** (event-based) and **DVS Gestures** (event-based): both a directly
  SLAYER-trained SNN and, for comparison in some cases, converted models were run and
  benchmarked; N-MNIST converted: 522 neurons, 597K params, 1.57% error, 0.29 mJ, 6.46 ms
  delay, 1.87 µJ·s EDP [3][8].
- **A 28-layer, 4M-parameter MobileNet at 128×128 input** was used to test the compiler's
  resource-distribution capability, achieving "near optimal resource utilization of 80%
  across 16 Loihi chips" [3][8] (this is a compiler/memory-utilization benchmark, not
  necessarily reported with accuracy/energy/latency in the same breath).

**What was measured**: classification error (%), energy per inference (mJ), execution
time/delay (ms), and energy-delay product (EDP, µJ·s), each benchmarked against the same
ANN run on CPU and GPU (Tensorflow) [3][8].

**Reset-by-subtraction implementation**: the two-compartment "soft reset" trick described
in Section 1 — used for the converted (SNN-Toolbox-based) models to reduce the
information loss of hard reset; SLAYER-trained models used hard reset/single compartment
instead [3][8].

**Operator/layer support (NxTF compiler)**: `input`, `flatten`, `average`, `concat`
(skip/recurrent connections), `dense`, `pool`, `conv` layer types, each carrying a
`neuron` field (default type CUBA-LIF) with compartment parameters (iDecay, vDecay,
vThMant, refDelay, etc.) [3][8] — this is the same HDF5 schema later reused, nearly
unchanged, by Lava-DL NetX (Section 5). Synaptic weight precision on Loihi supported up
to 9 bits in this framework [3][8].

**Identified limitations reported by the NxTF authors themselves**: approximation error
increases with network depth for converted models (mitigated by increasing algorithmic
timesteps, at the cost of higher latency/delay); firing-rate-based information
transmission is inherently inefficient in time and energy; inter-chip mesh link
congestion slows execution for networks spanning many chips; lack of a built-in soft
reset forces the compartment-doubling workaround; memory utilization per core is often
poor because synapse/axon/neuron budgets are not fungible against each other on Loihi 1
[3][8].

---

## 5. Lava / Lava-DL NetX specifics (Loihi 2)

**Export path.** The documented workflow is: (1) **train** with `lava.lib.dl.slayer`
(direct training on spike-based/event data) or `lava.lib.dl.bootstrap` (training
rate-coded SNNs), producing a **platform-independent HDF5 network description**; (2)
**load/deploy** that HDF5 file with `lava.lib.dl.netx.hdf5.Network(net_config=...)`,
which automatically instantiates a Lava Process graph from it, runnable on CPU
simulation or, for INRC members, physical Loihi 2 hardware by switching the `RunConfig`
(e.g., `Loihi2HwCfg` vs. a CPU sim config) [5][6][27][28].

**HDF5 schema / supported layer types**: `input`, `flatten`, `average`, `concat`,
`dense`, `pool`, `conv`, each with `shape`, `type`, and (for weighted layers) a `neuron`
field describing compartment parameters; default neuron type is `CUBA-LIF` [27][28].

**Neuron models supported via NetX**: primarily CUBA-LIF (default); the broader Lava
Process library additionally exposes LIF, and (via custom/microcode Loihi 2 process
models) Resonate-and-Fire, sigma-delta, and other programmable dynamics, though NetX's
HDF5 exchange format itself is documented around CUBA-LIF-style compartment parameters
[4][10][27][28].

**Reset semantics.** NetX-deployed networks are explicitly reset on a schedule rather
than continuously: the PilotNet LIF tutorial resets internal state every `reset_interval`
timesteps (one input frame per `reset_interval` timesteps), with a `reset_offset` to
stagger per-layer reset timing so each subsequent layer resets one timestep after its
input layer ("pipelined orchestration of layer reset") [28][29]. **Soft reset /
reset-by-subtraction**: **NOT FOUND** as a documented, named feature of Lava-DL NetX or
the CUBA-LIF process model in the sources reviewed; the example `PyLifModel` code shown
in Lava's own tutorial explicitly hard-resets voltage to zero on spike ("`self.v[s_out] =
0  # Reset voltage to 0. This is Loihi-1 compatible.`") [5][6]. This suggests hard reset
remains the default/documented behavior for the standard LIF process model in Lava, with
the comment implying deliberate backward compatibility with Loihi 1's native reset
behavior; no equivalent to NxTF's two-compartment soft-reset workaround was found
documented for Lava/NetX. Note this is an absence-of-evidence finding, not a proof that
soft reset is unsupported on Loihi 2 hardware in principle (Loihi 2's programmable
microcode could in principle implement it; no documentation describing this was located).

**8-bit quantized weights.** A third-party (non-Intel) Lava-DL tutorial write-up notes
that "the `netx`-loaded networks have 8-bit quantized integer weights" once trained via
SLAYER and exported [30].

**Published examples of a CONVERTED (not directly trained) CNN on physical Loihi 2.**
The clearest and most directly on-point result found:

- **Sigma-Delta Neural Network Conversion on Loihi 2** (Brehove et al., ChromoLogic LLC
  and Penn State, ICONS 2026 preprint) [15]: explicitly converts a trained, PyTorch
  post-training-quantized (8-bit weight/activation) ANN into a Sigma-Delta Neural Network
  and **deploys it on physical Loihi 2** hardware (a 16-chip VPX board), benchmarking
  against an NVIDIA Jetson Xavier. This is presented by the authors as demonstrating "the
  feasibility of running converted SDNNs on neuromorphic hardware" [15]. Caveat for this
  thesis's specific interest: this is a **sigma-delta (delta-coded, event-driven)
  conversion**, not classic rate-coded binary-IF conversion — the authors themselves
  frame this as an alternative *specifically because* traditional rate coding "required
  many simulation time steps per inference, which degraded efficiency" [15]. It measures
  latency and energy-delay-product on physical silicon, i.e., **evidence class E1**
  for this specific (sigma-delta) conversion methodology, but it does **not** constitute
  evidence of a classic rate-coded IF conversion running on physical Loihi 2.
- **PilotNet SDNN / directly-trained LIF-PilotNet on Loihi 2** (Shrestha et al., "Efficient
  Video and Audio Processing with Loihi 2," arXiv 2310.03251) [10]: benchmarks PilotNet
  (steering-angle regression) implemented as an SDNN and run on physical Loihi 2 with
  measured energy/latency/EDP against a Jetson Orin Nano / Intel i9 CPU. This network was
  trained natively with Lava-DL (SLAYER/bootstrap), **not converted from a separately
  pretrained ANN via rate-coding** — it does not answer the "converted rate-coded CNN"
  question directly, though it is a legitimate E1 physical-silicon deployment for a
  natively-trained SDNN/LIF network [10].
- **NOT FOUND**: a published, peer-reviewed paper running a classic **rate-coded,
  IF-neuron, ANN-to-SNN-converted CNN** (the QCFS/IF conversion style used in this
  thesis) on **physical Loihi 2** silicon, with measured latency and/or energy. The
  closest analogues found are (a) the sigma-delta conversion above [15], which is a
  different (non-rate) coding scheme purpose-built to avoid rate coding's inefficiency on
  Loihi 2, and (b) NxTF's rate-coded CIFAR-10/MNIST conversions [3][8], which ran on
  physical **Loihi 1**, not Loihi 2. Independent/unverified vendor claims exist (a
  self-published "NeuroCUDA" tool and its promotional site) stating a rate-coded/IF CNN
  (ResNet-18/CIFAR-10) was converted and validated only in software/simulator form, with
  the same source explicitly stating "Real silicon pending INRC application" for Loihi 2
  — i.e., **by the source's own admission, this is not yet run on physical Loihi 2
  silicon** [31][32]. This is included only to be explicit that it was checked and does
  **not** count as evidence; it is evidence class **E5** (software simulation only) at
  best, self-reported by a non-peer-reviewed, apparently one-person open-source project,
  and is not cited as a credible technical source elsewhere in this file.

---

## 6. Availability (as of September 2026)

**Chips are not commercially purchasable.** "Intel Loihi and Loihi 2 chips are not
currently available as Intel products. They can only be obtained for your research or
evaluation programs once you join the INRC" [33]. Commercial or government organizations
with longer-term needs can *purchase* an on-site Loihi 2 system (Kapoho Point), while
academic community members can get a free loan of up to one year; all such requests are
prioritized/evaluated by an Intel Labs checklist and still gated on INRC membership [33].

**INRC (Intel Neuromorphic Research Community).** Free, open membership (subject to
approval) for academic/government/industry research groups [11][34]. Two membership
tiers found: "Research Member – PI" (requires a permanent research-organization employee
submitting a project proposal, and a signed INRC Participation Agreement licensing
pre-production Loihi hardware/software) and "Affiliate Member" (community
participation only, no hardware/technology access) [34]. As of the 2021 press release the
community had grown to "nearly 150 members" [11]; INRC documentation elsewhere cites
"more than 140 members" [7]. **NOT FOUND**: an updated, current (2026) member count.

**Access mechanisms.** Primary access is the cloud-hosted **Neuromorphic Research Cloud**
(also called "vLab"), a shared pool of VMs with attached Loihi systems reachable via SSH
[33]. Two Loihi-2-based hardware systems are offered through this cloud: **Oheo Gulch**
(a single-chip board, Arria 10 FPGA interface over Ethernet, first system made available
to INRC partners, designed for lab testing/early evaluation) and **Kapoho Point** (a
compact, stackable 8-Loihi-2-chip board, ~4×4 inch, Ethernet interface, exposed GPIO,
stackable in multiples of 8 for larger systems; usable for portable/embedded/robotics
projects) [11][14]. Kapoho Point was described as "coming soon" / available for remote
access and loan as of the 2021 Loihi 2 launch brief [11].

**Critical 2026 status update: Lava has been archived.** As of a GitHub repository
snapshot, all `lava-nc` repositories (`lava`, `lava-dl`, `lava-dnf`, etc.) are marked
**ARCHIVED**, with the banner: "Intel will not provide or guarantee development of or
support for this project, including but not limited to, maintenance, bug fixes, new
releases or updates. Patches to this project are no longer accepted by Intel... Intel is
developing the next-generation Loihi architecture and SDK to power the coming era
physical AI. The new SDK is built on open-standard AI frameworks... All Lava
repositories are archived. Stay tuned for announcements about our new SDK and next
generation Loihi processor" [24][25][26]. Trade/community commentary (LinkedIn,
June 2026, citing an unnamed Intel source) frames this as: "Lava was not the right
software framework for commercialization. Just because we archived Lava does not mean we
have archived our neuromorphic technology" [26]. **Implication for anyone starting fresh
work on this stack as of the current date**: Lava/Lava-DL/NetX, the entire documented
Loihi-2 software path examined in Section 5, is no longer maintained by Intel and its
long-term status (successor SDK, whether it will support existing Loihi 2 hardware or
only a next-generation chip) is, per the sources found, **NOT FOUND** / unannounced as of
this research pass. `lava-dl`'s last code push recorded was 2026-05-13, latest release
v0.6.0 dated 2024-08-08 [25]. It is unclear from available sources whether INRC continues
to grant Loihi 2 hardware access under the (now-archived) Lava extension, or whether that
mechanism is being wound down alongside Lava itself; **NOT FOUND**.

---

## 7. Published deployments on physical Loihi silicon — inventory with evidence classes

| # | Work | Chip | Network | Conversion type | Dataset | T (timesteps) | Measured | Evidence class |
|---|---|---|---|---|---|---|---|---|
| 1 | Rueckauer et al., NxTF [3][8] | **Loihi 1** (physical) | 4-layer CNN | Rate-coded ANN→SNN conversion (SNN Toolbox) | MNIST | ~100 [17] | Error, energy (0.66 mJ), delay (6.65 ms), EDP | **E1** |
| 2 | Rueckauer et al., NxTF [3][8] | **Loihi 1** (physical) | off-the-shelf MobileNet | Rate-coded ANN→SNN conversion | CIFAR-10 | ~400 [17] | Error (8.52%), energy (102 mJ), delay (340 ms), EDP; 861 cores / 7 chips [3][8] (the 1,753-core/14-chip figure in [17] is Quartz's own CIFAR-10 network, not this MobileNet) | **E1** |
| 3 | Rueckauer et al., NxTF [3][8] | **Loihi 1** (physical) | SLAYER-trained conv. SNN | Directly trained (not converted) | N-MNIST | — | Error, energy, delay, EDP | E1 (not a conversion result) |
| 4 | Rueckauer et al., NxTF [3][8] | **Loihi 1** (physical) | SLAYER-trained conv. SNN | Directly trained | DVS Gestures | — | Error, energy, delay, EDP | E1 (not a conversion result) |
| 5 | Rueckauer et al., NxTF [3][8] | **Loihi 1** (physical) | 28-layer MobileNet, 4M params | Compiler resource benchmark | (128×128 input) | — | Resource utilization (80% across 16 chips) | E1 for utilization only, not accuracy/energy |
| 6 | Lenz, Orchard, Sheik, Quartz [17] | **Loihi 1** (physical) | MNIST/CIFAR-10 nets | Temporal (TTFS) ANN→SNN conversion (own method) | MNIST, CIFAR-10 | 24 (MNIST), 27 range (CIFAR-10) | Error, spikes, timesteps, energy/EDP (measured on Loihi cores) | **E1** |
| 7 | Boeshertz et al. [16] | **Loihi (1)** (physical) | lpRNN / ΣΔ-neuron RNN | Converted RNN→SNN mapping (own method), 3-bit weights | Speech/audio benchmarks | — | Classification accuracy, SOTA on-chip speech classification | **E1/E2** (accuracy-focused; energy not detailed in excerpt) |
| 8 | Shrestha et al., "Efficient Video and Audio Processing with Loihi 2" [10] | **Loihi 2** (physical) | PilotNet SDNN, audio denoising/spectral nets | Directly trained (SLAYER/bootstrap), **not** ANN-converted rate coding | Driving video (PilotNet), audio | — | Energy, latency, EDP vs. Jetson Orin Nano / i9 CPU | **E1** (not a rate-coded conversion) |
| 9 | Brehove, Tumpa, Kyubwa, Menon, Narayanan, "Sigma-Delta Neural Network Conversion on Loihi 2" [15] | **Loihi 2** (physical, 16-chip VPX board) | Converted ANN → Sigma-Delta Neural Network (YOLOv3-style detector) | ANN→SDNN conversion (own method; NOT rate-coded IF) | Video/RGB frames | 16 (fall-through mode) | Energy-delay product vs. Jetson Xavier | **E1** (conversion, but non-rate-coded scheme) |
| 10 | Orchard et al. [4] | **Loihi 2** (emulated/simulated hardware, per abstract: "simulation experiments on emulated Loihi 2 hardware") | RF-neuron STFT, optical-flow, audio classification nets | Novel neuron models, not ANN conversion | NTIDIGITS, Google Speech Commands | — | Bandwidth reduction, op-count reduction (simulated) | **E5** (explicitly simulation on emulated HW, not physical silicon, per own abstract) |
| — | Rate-coded, IF-based CNN conversion on **physical Loihi 2** | **Loihi 2** | — | — | — | — | — | **NOT FOUND.** No paper located demonstrating this specific combination (the ANN-to-SNN conversion style most directly comparable to this thesis's QCFS/IF approach) on physical Loihi 2 silicon. |

**Davies et al. 2021, "Advancing Neuromorphic Computing With Loihi: A Survey of Results
and Outlook," Proc. IEEE [2].** Key caveats relevant to when neuromorphic hardware does
**not** win, stated by Intel's own Loihi architects:

- "While conventional feedforward deep neural networks show modest if any benefit on
  Loihi, more brain-inspired networks using recurrence, precise spike-timing
  relationships, synaptic plasticity, stochasticity, and sparsity perform certain
  computation with orders of magnitude lower latency and energy" [2].
- Explicitly rejects the naive framing that Loihi is meant to out-MAC GPUs/ASICs on
  standard deep learning workloads: "it would be naïve to expect SNNs to outperform ANN
  accelerators on the very task that they have been optimized for" [2]. Per-synaptic-op
  energy on Loihi is in practice *greater* than a MAC on a dedicated ANN accelerator, due
  to the overhead of supporting sparse, event-driven, time-and-space-sparse computation
  that dense ANN accelerators don't need to pay for [2].
- Latency scaling is unfavorable for large/deep converted rate-coded networks: "higher
  layer counts demand an increasing number of time steps in order to achieve maximum
  accuracy" and "the need to distribute larger networks across multiple Loihi chips leads
  to congestion in the links between the chips," with inter-chip mesh links having
  "roughly 30× lower bandwidth than its on-chip links" [2].
- Direct conclusion on rate-coded conversion specifically: "ANNs converted to rate-coded
  deep SNNs on Loihi may offer significant gains in energy efficiency compared to ANNs on
  conventional architectures but generally result in **long latencies, especially for
  large-scale problems spanning multiple chips**... These attributes render converted
  rate-coded models less attractive for neuromorphic architectures optimized for
  sparsity, and therefore demand other approaches" [2] — this is Intel's own stated
  rationale for why Loihi 2's programmable/graded-spike/sigma-delta direction, rather
  than continued investment in classic rate-coded conversion, became the emphasis for
  deep-learning-style workloads on Loihi 2. This directly supports why post-2021 published
  Loihi 2 deployments (Sections 5, 7) skew toward sigma-delta/graded-spike conversion
  rather than classic rate-coded IF conversion.
- Batch-size caveat: Loihi is compared mostly at batch size 1 in the survey's own EDP
  plots; "the EDP of both CPU and GPU architectures improves significantly when batching
  is used," which is a regime Loihi (single-sample, low-latency-oriented) is not designed
  to exploit [2].

---

## Source list

[1] M. Davies, N. Srinivasa, T.-H. Lin, G. N. Chinya, Y. Cao, S. H. Choday, et al.,
"Loihi: A Neuromorphic Manycore Processor with On-Chip Learning," *IEEE Micro*, vol. 38,
no. 1, pp. 82–99, 2018. https://doi.org/10.1109/mm.2018.112130359 (full text mirror:
https://redwood.berkeley.edu/wp-content/uploads/2021/08/Davies2018.pdf)

[2] M. Davies, A. Wild, G. Orchard, Y. Sandamirskaya, G. A. Fonseca Guerra, P. Joshi, P.
Plank, S. R. Risbud, "Advancing Neuromorphic Computing With Loihi: A Survey of Results
and Outlook," *Proceedings of the IEEE*, vol. 109, no. 5, pp. 911–934, 2021.
https://doi.org/10.1109/jproc.2021.3067593 (full text mirror:
https://dynamicfieldtheory.org/upload/file/1631291311_c647b66b9e48f0a9baff/DavisEtAl2021.pdf)

[3] B. Rueckauer, C. Bybee, R. Goettsche, Y. Singh, J. Mishra, A. Wild, "NxTF: An API and
Compiler for Deep Spiking Neural Networks on Intel Loihi," arXiv:2101.04261, 2021.
https://arxiv.org/abs/2101.04261

[4] G. Orchard, E. P. Frady, D. Ben Dayan Rubin, S. Sanborn, S. B. Shrestha, F. T.
Sommer, M. Davies, "Efficient Neuromorphic Signal Processing with Loihi 2," in *2021 IEEE
Workshop on Signal Processing Systems (SiPS)*, Coimbra, Portugal, pp. 254–259, 2021.
https://doi.org/10.1109/sips52927.2021.00053 (preprint: arXiv:2111.03746,
https://ar5iv.labs.arxiv.org/html/2111.03746)

[5] Lava Developer Guide, https://lava-nc.org/developer_guide.html (archived project;
see [24])

[6] Lava Software Framework documentation, https://lava-nc.org/ (archived project; see
[24])

[7] Intel Corporation, "Taking Neuromorphic Computing to the Next Level with Loihi 2,"
technical brief,
https://www.intel.com/content/dam/www/central-libraries/us/en/documents/neuromorphic-computing-loihi-2-brief.pdf

[8] B. Rueckauer, C. Bybee, R. Goettsche, Y. Singh, J. Mishra, A. Wild, "NxTF: An API and
Compiler for Deep Spiking Neural Networks on Intel Loihi," *ACM Journal on Emerging
Technologies in Computing Systems*, 2022. https://doi.org/10.1145/3501770

[9] Intel Newsroom, "Intel Scales Neuromorphic Research System to 100 Million Neurons"
(Pohoiki Springs),
https://www.intel.com/content/www/us/en/newsroom/news/intel-scales-neuromorphic-research-system-100-million-neurons.html

[10] S. B. Shrestha, J. Timcheck, P. Frady, L. Campos-Macías, M. Davies, "Efficient Video
and Audio Processing with Loihi 2," arXiv:2310.03251, 2023.
https://doi.org/10.48550/arxiv.2310.03251

[11] Intel Corporation, press release, "Intel Advances Neuromorphic with Loihi 2, New
Lava Software Framework," 2021.
https://www.intc.com/news-events/press-releases/detail/1502/intel-advances-neuromorphic-with-loihi-2-new-lava-software

[12] "Bio-realistic neural network implementation on Loihi 2 with Izhikevich neurons,"
*Neuromorphic Computing and Engineering*, IOPscience, 2024.
https://google.iopscience.iop.org/article/10.1088/2634-4386/ad5584

[13] OSTI technical report on graded-spike arithmetic on Loihi 2 (DOE OSTI),
https://www.osti.gov/servlets/purl/3004360

[14] Intel Corporation, "Neuromorphic Computing and Engineering with AI" (Kapoho Point /
INRC overview page), https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html

[15] M. Brehove, S. A. Tumpa, E. Kyubwa, N. Menon, V. Narayanan, "Sigma-Delta Neural
Network Conversion on Loihi 2," preprint / ICONS 2026,
https://arxiv.org/html/2505.06417v2

[16] G. Boeshertz, G. Indiveri, M. V. Nair, A. Renner, "Accurate Mapping of RNNs on
Neuromorphic Hardware with Adaptive Spiking Neurons," arXiv:2407.13534, 2024.
https://doi.org/10.48550/arxiv.2407.13534

[17] G. Lenz, G. Orchard, S. Sheik, "Ultra-low-power Image Classification on Neuromorphic Hardware" (Quartz),
alphaXiv / arXiv:2309.16795. https://www.alphaxiv.org/abs/2309.16795

[18] "Three Factor Learning with Lava" tutorial,
https://lava-nc.org/lava/notebooks/in_depth/three_factor_learning/tutorial01_Reward_Modulated_STDP.html
(archived project; see [24])

[19] "A Diagonal Structured State Space Model on Loihi 2 for Efficient Streaming Sequence
Processing," arXiv:2409.15022. https://arxiv.org/pdf/2409.15022v1.pdf

[20] "Neuromorphic Principles for Efficient Large Language Models on Intel's Loihi 2,"
arXiv:2503.18002. https://arxiv.org/html/2503.18002v2

[21] Politecnico di Torino Master's thesis, "Implementation of a Hippocampal-Cortical
spiking neural network for memory semantization on Loihi 2 neuromorphic hardware,"
https://webthesis.biblio.polito.it/39912/1/tesi.pdf

[22] Intel INRC Confluence, "Request Loihi 2 Hardware,"
https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001/Access+Intel+Loihi+Hardware

[23] Lava GitHub, "Lava 0.4.0" release discussion,
https://github.com/lava-nc/lava/discussions/269

[24] Lava GitHub repository (archived), https://github.com/lava-nc/lava/

[25] Lava-DL GitHub repository (archived), https://github.com/lava-nc/lava-dl

[26] "Silently... Intel archived whole Neuromorphic LAVA 2 weeks ago. Why?!," LinkedIn
post, Neuromorphicism, June 2026,
https://www.linkedin.com/posts/neuromorphicism_silently-intel-archived-whole-neuromorphic-activity-7468686050119487488--Y1y

[27] Lava-DL NetX documentation, https://lava-nc.org/lava-lib-dl/netx/netx.html
(archived project; see [24])

[28] Lava-DL NetX README, https://github.com/lava-nc/lava-dl/blob/main/src/lava/lib/dl/netx/README.md

[29] Lava-DL PilotNet LIF tutorial notebook,
https://github.com/lava-nc/lava-dl/blob/main/tutorials/lava/lib/dl/netx/pilotnet_snn/run.ipynb

[30] R Gaurav, "Lava Tutorial: MNIST Training on GPU and Evaluation on Loihi2" (personal
blog, third-party, not an official source), 2024.
https://r-gaurav.github.io/2024/04/13/Lava-Tutorial-MNIST-Training-on-GPU-and-Evaluation-on-Loihi2.html

[31] "neurocuda" GitHub repository README (third-party, unverified, non-peer-reviewed
tool; cited only to document a checked-and-rejected claim, not as a credible technical
source), https://github.com/Krishnav1/neurocuda/blob/master/README.md

[32] QuantaraCore Technologies LLP, "Intel Lava Archived: Use NeuroCUDA Instead (2026)"
(vendor/promotional page, third-party, unverified; cited only to document a
checked-and-rejected claim), https://quantaracore.in/

[33] Intel INRC Confluence, "Access Intel Loihi Hardware,"
https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001

[34] Intel INRC Confluence, "Join the INRC,"
https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1784807425

**Additional background source consulted (not directly quoted above):**
M. Davies, "Lessons from Loihi: Progress in Neuromorphic Computing," *2021 Symposium on
VLSI Circuits*, 2021. https://doi.org/10.23919/vlsicircuits52068.2021.9492385

**Note on excluded/flagged sources:** a document titled "Catalyst N2" found at
catalyst-neuromorphic.com presents itself as an independently developed FPGA
reimplementation claiming "full Loihi 2 feature parity"; it is self-published, not
peer-reviewed, and not affiliated with Intel. It was not used as a source for any Loihi 2
architectural claim in this file and is noted here only so it is not mistaken for a
primary source. Likewise "neurocuda" [31] and its promotional mirror [32] are
self-published, non-peer-reviewed, single-source claims (one GitHub repo maintained by an
apparently individual developer) and were excluded from all architectural/capability
claims; they are cited only in Section 5 to document that a specific claim (converted CNN
on physical Loihi 2) was checked and found, by the source's own admission, not to be
backed by a physical-silicon run.
