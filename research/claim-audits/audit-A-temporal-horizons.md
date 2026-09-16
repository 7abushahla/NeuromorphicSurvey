# Audit A. Temporal horizons and deployment semantics

Review date: 2026-09-16

Machine-readable proposals: `audit-A-temporal-horizons.json`

## Audit question

This audit asks whether a reported timestep reduction denotes an executable deployment schedule. It separates four mechanisms that the current survey draft sometimes places too close together.

| Mechanism | Control variable | When chosen | Execution meaning | Audited physical evidence |
|---|---|---|---|---|
| Static per-layer horizons | One fixed `T_l` for each layer | Before inference | Adjacent layers produce tensors with different temporal lengths and require an alignment rule | None for a heterogeneous discrete schedule |
| Per-input early exit | One terminal horizon for each sample | During inference | The network stops once a confidence or policy condition is met | None in SEENN or Dynamic Confidence |
| Asynchronous execution | Events and cores progress without a conventional global circuit clock | Architecture-dependent | Event delivery may be asynchronous even when an algorithmic timestep is globally synchronized | Physical systems exist, but this does not establish independent layer horizons |
| Timestep-free event-driven execution | State updates occur on event arrival | At physical runtime | There is no vector of discrete layer horizons to execute | Temporal Flexibility reports a Speck2e run |

The central result is narrow but consequential. PASCAL, QAC, and MT-SNN evaluate static heterogeneous layer horizons in software. None demonstrates that schedule on physical hardware. Temporal Flexibility reaches physical Speck2e silicon, but the physical run is fully event-driven and timestep-free. Its mixed timestep vectors are a training intervention rather than the chip's inference schedule.

## Source and inspection ledger

Exa Search was attempted first and returned HTTP 402 because the available Exa credits were exhausted. Primary papers, official records, and author repositories were then retrieved directly. No search-result snippet is used as evidence.

| Source | Primary artifact | Integrity or revision identity | Second inspection path |
|---|---|---|---|
| PASCAL | TMLR PDF from [arXiv](https://arxiv.org/pdf/2505.01730) | SHA-256 `3d1f5a2d4373d3567be55d797700cf742a7d3eca2bd3d62528dfeef0e533d67e` | [Public repository](https://github.com/BrainSeek-Lab/PASCAL) at commit `a4e3afbdaf271f5a6e077c0f799c8bea9843e3d6`; rendered PDF pp. 12, 23, and 24 |
| QAC | [OpenReview revision p4ZjfNpLYo](https://openreview.net/notes/edits/attachment?id=p4ZjfNpLYo&name=pdf) | SHA-256 `e44c9b9816cf9101e89404f1b44944d14b731222e200d85da1ec230e617a9ea7` | Independent [revision rXoJz4T7cw](https://openreview.net/notes/edits/attachment?id=rXoJz4T7cw&name=pdf), SHA-256 `50a9ef700af518cb0346c641148eaef1aca5a05ad8f8cb103767025a07e072ce`; rendered pp. 21-23 |
| MT-SNN | User-supplied 23-page withdrawn ICLR manuscript | SHA-256 `6d7f507f6f35e8bf99afbab2ac53a11687b80f407061f9122466229817670845` | Complete extraction with PyMuPDF 1.28.2 and pypdf; visual checks of pp. 9 and 18; comparison with the [accepted Frontiers abstract](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2026.1783326/abstract) |
| Temporal Flexibility | ICLR 2025 PDF from [arXiv](https://arxiv.org/pdf/2503.17394) | SHA-256 `0bcb1ac7900850009a36b256fb0132869569dbf573cc740bf5bb4599d45b7c78` | Public repository at commit `c320f925b3894b7526a2adacc979610a2fb00f0d`; rendered PDF pp. 7-9 |
| SEENN | NeurIPS paper PDF | SHA-256 `6a14d544325035bab0a6e80312a900f2e7ff4ac18484fcee347f6f4debaa1a16` | Full-text extraction and rendered PDF p. 8 |
| Dynamic Confidence | ICCV paper PDF | SHA-256 `11220317d05d123aa5357e7bb9e6ab70652e8250c64ee7c5eb2eb23e23381ce2` | Full-text extraction and rendered PDF p. 9 |
| NeuroScale | [Europe PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12645053/) | DOI `10.1038/s41467-025-65268-z` | Cross-check against the Loihi 2 LLM paper |
| Loihi 2 LLM | [arXiv PDF](https://arxiv.org/pdf/2503.18002) | SHA-256 `78db860aa89d48aad6cb2365c08234b142ebe60c03b04146bfd17db5917368dd` | PDF pp. 4 and 11-12 independently state asynchronous core operation plus a global algorithmic timestep maintained by a barrier |

The temporary parsing environment was isolated under `/tmp`. It used PyMuPDF 1.28.2 and pypdf. No repository or project Python environment was modified.

## PASCAL

### Verified method semantics

Algorithm 1 on PDF p. 5 consumes an `L_(n-1)`-step tensor, accumulates its spikes, runs a relaxation loop of `max(L_(n-1), L_n) - 1`, and emits an `L_n`-step spike tensor. The reference implementation matches that sequence in `models/layer.py`, lines 59-149. The allocation is static by layer. It is not a sample-dependent termination decision.

### `T_eff` is a model, not latency

Equation 16 defines

`T_eff = (1 / |L_tot|) sum_l r_E^l T^l`.

The factor `r_E^l` is the analytical energy-overhead ratio defined by Eqs. 9-12. It is not an operation count or a measured duration. `T_eff` therefore omits synchronization, communication, temporal alignment, scheduling, and stalls.

The headline ResNet-18 CIFAR-10 value has an unresolved reproducibility defect. Table 4 lists 17 layerwise timestep values, while `get_Teff.py` defines 10 ResNet-18 coefficients. The script uses `zip()`, which silently drops the final seven timestep values, and then takes the mean of the resulting ten terms. That procedure reproduces the headline.

- Released-script computation: `3.1361557645729463`, which rounds to 3.14.
- Same weighted sum divided by the 17 listed timestep values: `1.8447975085723214`.
- Simple mean of the 17 listed timestep values: `2.411764705882353`.

The audit therefore verifies the formula and the mechanism by which 3.14 is reproduced, but marks the layer identity and cardinality mapping as conflicted.

### Hardware boundary

Appendix A.10 is genuine E4 evidence. It reports modified LoAS and SparTen RTL synthesized by Synopsys Design Compiler in 40 nm at 560 MHz, followed by cycle-accurate simulation. For VGG-16 on CIFAR-10 at uniform `T = 4`, it reports 445.47 mJ and 0.40 s for default IF and 446.02 mJ and 0.45 s for PASC-IF.

This evidence does not cover Adaptive Layerwise execution. Every hardware row uses uniform `T = 4`. The mixed-horizon configuration that yields `T_eff = 3.14` is neither synthesized nor cycle-simulated.

## QAC

### Verified method and metric

Sections 4.2-4.3 map learned layerwise activation quantization settings to static layerwise timestep counts. Eqs. 11-13 define temporal alignment. The selected method averages the entire source-layer temporal dimension, then repeats that average to the target layer's timestep length.

The reported 2.76 timesteps for ResNet-18 on CIFAR-10 at 95.29 percent accuracy is an average layerwise statistic. The paper does not report it as elapsed time or cycles. Section 4.2 separately describes uniform sequential latency as order `O(NT)`.

### Hardware boundary

Section 7.7 proposes a temporal-loop modification for ANN-style accelerators. It also warns that a multicore neuromorphic pipeline can stall because a downstream layer must wait for the upstream `T_l` steps. No compiler, mapping, simulator, RTL, or physical processor executes the proposal. This is useful execution reasoning, but it does not meet the survey's E3 definition of a documented toolchain path.

### Rejected inherited claim

The existing raw audit states that QAC Section 7.8 contains an analytical energy comparison using Horowitz and Potipireddi. That statement is false for both public OpenReview revision attachments. Section 7.8 is titled “Time Step vs. Bit Width.” Full-text searches find no Horowitz, Potipireddi, Synopsys, or cycle-accurate result. The energy appendix appears in the later MT-SNN manuscript, which is the likely source of the attribution error.

## MT-SNN

### Version identity matters

The supplied PDF is a withdrawn ICLR 2026 manuscript titled “Mixed-Timestep Spiking Neural Networks with Temporal Alignment for Ultra-Low Latency Conversion.” Its title page says “Withdrawn.” The later accepted Frontiers record has a revised title and abstract.

The method lineage is stable. Both records describe static layerwise timestep allocation derived from ANN quantization. The alignment implementation is not stable across the records.

- The supplied manuscript uses average-and-repeat alignment in Eq. 20 and Algorithm 1.
- The accepted Frontiers abstract names Scaled Synaptic Current Accumulation, described as a fused synaptic-current-domain mechanism.

These records should not be cited interchangeably for alignment details. The change is a version conflict, not evidence that either passage is internally false.

### Verified metric and GPU measurement

Section 5.1 explicitly defines average inference timesteps as the simple arithmetic mean `(sum_l T_l) / L`. Table 1 reports 73.63 percent ImageNet-1K top-1 accuracy for ResNet-34 at an average of 4.88 timesteps.

Section 5.4 provides a distinct GPU measurement. On four NVIDIA RTX 4090 GPUs with global batch size 64, the complete ImageNet-1K validation run takes 344.44 s for MT-SNN and 1893.38 s for the uniform `T = 32` baseline. Temporal alignment consumes 15.39 s, or 4.47 percent of the MT-SNN run. These values demonstrate software speedup on that GPU configuration. They do not convert the 4.88 layer mean into hardware latency.

### Energy and hardware boundary

Appendix C estimates energy from operation counts, firing rates, layer timesteps, and assumed 45 nm operation costs. Tables 7-8 and Eqs. 22-23 are analytical. No target-specific circuit or power measurement produces those values.

Appendix E repeats the two-path hardware discussion found in QAC. It states that ANN accelerator variants can replace unified `T` with layerwise `T_l`, and it warns that multicore neuromorphic pipelines can stall. No target implementation is reported. The hardware section therefore remains qualitative and is not E3 deployment evidence.

## Temporal Flexibility and MTT

The canonical paper is “Temporal Flexibility in Spiking Neural Networks: Towards Generalization Across Time Steps and Deployment Friendliness,” by Kangrui Du, Yuhang Wu, Shikuang Deng, and Shi Gu. The source registry now carries that verified identity, with `mtt` retained only as a legacy alias.

Mixed Time-step Training samples a vector of timestep values and assigns them to network stages during training. Algorithm 1 on PDF p. 7 and the public code both confirm this behavior. The time-stepped implementation samples stage values in `train-time-stepped/utils.py`, lines 63-83. The event-driven implementation samples configurations in `train-event-driven/utils.py`, lines 189-228.

The physical result is E2. The paper deploys MTT and single-timestep models to a SynSense Speck2e development kit for N-MNIST. Table 5 reports 99.16 percent PyTorch accuracy, 98.56 percent event-driven simulator accuracy, and 98.57 percent Speck accuracy for MTT. It also reports 3.92 percent simulator-to-chip spike difference, 2.81 percent repeated-chip difference, and 28.77 percent conventional time-stepped-to-chip difference.

The deployed execution is fully event-driven and timestep-free. The mixed stagewise timestep vector is used to train a temporally robust weight set. It is not scheduled as distinct discrete stage horizons on Speck2e. The public repository contains training and simulation code but no Speck deployment script, so reproduction of the device path is not fully supported by the released code.

## Early exit is a different branch

SEENN and Dynamic Confidence terminate inference per input using runtime confidence or a learned policy. Their reported average timestep denotes a distribution of whole-network terminal times across samples. It does not denote different fixed timesteps for layers within the same sample.

SEENN Section 4.3 measures throughput on an NVIDIA Tesla V100 and estimates energy from operation costs. Dynamic Confidence states explicitly on PDF p. 9 that its experiments are GPU simulations and that actual neuromorphic power savings are unknown. Neither supplies physical evidence for early-exit control.

This distinction should be maintained even if a future platform pipelines multiple samples. Pipeline overlap is an execution optimization. It does not change the algorithmic control variable from per-input stopping to per-layer allocation.

## Asynchronous execution is not mixed-horizon execution

NeuroScale states that TrueNorth advances all components with an externally distributed signal, Loihi and Loihi 2 use barrier synchronization to advance time, and Tianjic uses a global clock. The Loihi 2 LLM paper independently states that neurocores compute and communicate asynchronously while a global algorithmic timestep is maintained by barrier synchronization. It then distinguishes pipelined and fall-through schedules.

The appropriate conclusion is bounded. Asynchronous circuitry or event communication does not prove that layers have independent discrete time coordinates. This is not an impossibility theorem. Speck2e provides the complementary case, a fully event-driven substrate without explicit discrete timesteps.

## Claim decisions

- Verified. PASCAL, QAC, and MT-SNN use static layerwise horizons and explicit temporal realignment.
- Verified. Their headline average or effective timestep values are derived summaries, not hardware latency.
- Conflicted. PASCAL's published ResNet-18 `T_eff = 3.14` depends on an undocumented 17-to-10 truncation in the released script.
- Verified. PASCAL has E4 hardware-model evidence only for uniform `T = 4`.
- Rejected. QAC Section 7.8 does not contain the energy appendix attributed to it in the existing raw audit.
- Verified. The MT-SNN energy appendix is analytical, and its hardware appendix is qualitative.
- Conflicted. The withdrawn MT-SNN manuscript and accepted Frontiers abstract name different alignment mechanisms.
- Verified. Temporal Flexibility has E2 Speck2e evidence, but the physical execution is timestep-free rather than a discrete mixed-horizon schedule.
- Verified within the named corpus. None of the four target works physically executes a static heterogeneous per-layer discrete-timestep schedule.
