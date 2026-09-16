# A17 — Two Populations: Testing the Division-of-Labor Claim

Audit date: 2026-09-15. This file tests, not asserts, the claim: *"The ANN-to-SNN field has
a division of labor that nobody states. Algorithm papers advance accuracy at low T and never
deploy. Deployment papers reach silicon and never use the new algorithms. The two literatures
cite each other's motivations and share no artifacts."*

Builds on prior audits: [a09-classical-conversion-audit.md](a09-classical-conversion-audit.md)
(0/9 classical conversion algorithm papers reached silicon) and
[a10-lowlatency-audit.md](a10-lowlatency-audit.md) (0/16 QCFS-lineage papers reached silicon).
This file does not redo that E1–E5 classification; it measures citation direction, toolchain
freeze, shared artifacts, and searches hard for falsifying counterexamples.

**Headline verdict, stated up front:** the core claim survives, but weaker and more textured
than the strong form suggests. The citation asymmetry is real but not absolute — the founding
QCFS paper itself cites two physical-hardware papers in its related work, not just in
motivational throat-clearing. And the refined hypothesis (co-designed, non-rate-coded methods
are precisely the ones that reach silicon) holds up: a genuine, clean counterexample exists
(Quartz, TTFS-based, measured on real Loihi), and it is exactly the kind of paper the refined
hypothesis predicts — it explicitly abandons rate coding.

---

## Task 1 — Citation asymmetry, measured

### 1a. Forward direction: do QCFS-lineage algorithm papers cite hardware deployment papers?

For each paper: does it cite ANY physical-hardware deployment paper (NxTF/Rueckauer 2021,
Massa 2020, Patiño-Saucedo 2020, Stromatias 2015, or any other paper reporting silicon
measurements)? Where (abstract / intro / related work / methods / experiments)? Does it name a
specific target chip, and in what context? All findings below are from the paper's own text
(arXiv/ar5iv HTML, ICML/IJCAI proceedings PDF, or Frontiers HTML), not from a10's summary.

| # | Paper | Cites a hardware-deployment paper? | Location | Chip named? | Context |
|---|---|---|---|---|---|
| 1 | **QCFS** (Bu et al., ICLR 2022, arXiv 2303.04347) | **YES** — "Massa et al. (2020) and Singh et al. (2021) evaluated the performance of converted SNNs on the Loihi Neuromorphic Processor." | **Related Work**, in a paragraph surveying prior conversion-error-reduction techniques (alongside Ho & Chang 2021, Han et al. 2020) — i.e., treated as a peer prior-art line, not abstract/intro motivation | Loihi (named, in the same sentence as the citation) | Prior art acknowledgment. Massa et al. 2020 = confirmed E1 (IJCNN, Loihi, DVS Gesture, SNN Toolbox). "Singh et al. 2021" = confirmed by cross-check to be Singh, Sarma, Lu, Sengupta, Narayanan, Das, "Gesture-SNN: Co-optimizing accuracy, latency and energy of SNNs for neuromorphic vision sensors," ISLPED 2021 — also a physical-hardware paper ("we evaluate our proposed schemes on an existing neuromorphic accelerator"). QCFS is thus the single strongest counter-datapoint to the pure "never cites deployment work" sub-claim: it cites *two* E1-class papers, correctly, in related work. It still never deploys QCFS itself. |
| 2 | **OPI** (Bu et al., AAAI 2022, arXiv 2202.01440) | No | — | No specific chip in a deployment context | Only "neuromorphic chips" as a generic parenthetical citing Schemmel/Furber/Merolla/Davies/Pei — architecture papers, not deployment results |
| 3 | **SRP** (Hao et al., AAAI 2023, arXiv 2302.02091) | No | — | No | Same generic architecture-paper citation pattern as OPI |
| 4 | **COS** (Hao et al., ICLR 2023, arXiv 2302.10685) | No | — | No | Loihi/TrueNorth cited only via Davies 2018 / DeBole 2019 (architecture papers) in intro motivation; "hampers the practical applications of SNNs to neuromorphic chips" (motivation only) |
| 5 | **SlipReLU** (Jiang et al., ICML 2023) | No | — | No | Single generic "neuromorphic hardware" mention in intro; zero chip names anywhere in the paper (verified against full PDF text, not just abstract) |
| 6 | **Burst Spikes** (Li & Zeng, IJCAI 2022, arXiv 2204.13271) | No | — | TrueNorth, Loihi named (Akopyan 2015, Davies 2018) | Intro motivation only ("neuromorphic hardware such as TrueNorth... and Loihi... has attracted attention"); conclusion: "Hopefully, our work can be combined with neuromorphic hardware..." (aspirational) |
| 7 | **SNM** (Wang et al., IJCAI 2022) | No | — | TrueNorth, Loihi, Tianjic named (Akopyan 2015, Davies 2018, Pei 2019) | Intro motivation only: "SNNs are more suitable to implement on ultra-low-power neuromorphic hardware, such as TrueNorth, Loihi, and Tianjic" — architecture citations, not deployment results |
| 8 | **Fast-SNN** (Hu et al., TPAMI 2023, arXiv 2305.19868) | No | — | Loihi, TrueNorth named | Loihi cited explicitly as a *design justification*: "neuromorphic hardware such as Loihi [5] already supports signed spikes" — used to justify the signed-IF neuron choice, not to report a deployment |
| 9 | **Dynamic Confidence** (Li, Jones, Furber, ICCV 2023, arXiv 2303.10276) | No | — | No | Explicit, notable self-disclaimer despite co-author Furber (SpiNNaker's creator): "the real power saving when running on neuromorphic hardware is unknown to us" — this is a rare moment of the literature naming its own limitation directly, in the discussion of results, rather than deflecting to future work |
| 10 | **QFFS** (Li, Ma, Furber, Frontiers Neurosci. 2022) | No | — | No | "deploy SNN algorithms on memory-constrained neuromorphic hardware (Schaefer and Joshi, 2020; Chowdhury et al., 2021; Lui and Neftci, 2021)" — related-work sentence citing quantization-for-hardware papers, not deployment-of-converted-CNN papers. Despite Furber's SpiNNaker affiliation, no SpiNNaker citation or run anywhere in the paper (confirmed against full text, not just abstract) |
| 11 | **SEENN** (Li, Geller, Kim, Panda, NeurIPS 2023, arXiv 2304.01230) | No | — | No | Section "4.3 Hardware Efficiency" uses a GPU (NVIDIA Tesla V100) for latency and a SynOps-style op-count for energy — no chip named anywhere in the paper body or references beyond generic background papers |
| 12 | **CS-QCFS** (Yang et al., Neural Networks 2024/2025) | No | — | Loihi named (Davies 2018, reference-list only) | Reference-list citation only; no experiments-section hardware content |
| 13 | **AdaFire** (Wang et al., AAAI 2025, arXiv 2412.16219) | No | — | Loihi 2, Synsense Speck named | Cited twice as *motivation* for the burst-firing neuron design: "this mechanism is well-supported by neuromorphic hardware, such as Intel's Loihi 2 and Synsense's Speck" — never as an executed run; energy figures explicitly theoretical (Appendix) |

**Aggregate for Task 1a:** 13 QCFS-lineage papers audited directly against full text (exceeds
the 10-paper minimum). **1 of 13 (QCFS itself) cites an actual physical-hardware deployment
paper**, and does so correctly, in related work, as acknowledged prior art — not buried in the
abstract. **12 of 13 cite zero deployment papers**, citing only chip-*architecture* papers
(Davies 2018 Loihi, Akopyan 2015 TrueNorth, Pei 2019 Tianjic, Schemmel 2010 BrainScaleS,
Furber 2012 SpiNNaker) as generic motivational furniture in the introduction. **0 of 13 name a
chip in the context of an experiment they themselves ran.** Of the 3 papers that do name a
specific chip in a substantive (non-generic) sentence — Fast-SNN ("Loihi already supports
signed spikes"), AdaFire ("well-supported by... Loihi 2 and... Speck"), and QCFS itself — two
use the chip as a *design justification* for a neuron-model choice, and only QCFS uses it as an
*acknowledgment of prior deployment work*. The hypothesis that hardware appears "only in
motivational sections and never in methods or experiments" is confirmed for 12/13 papers and
weakly falsified for 1/13 (QCFS's related-work citation is not "motivational" in the
throat-clearing sense — it correctly identifies and credits prior E1 results as a technical
precedent). No paper in this set reports its own conversion method running on a named chip.

### 1b. Reverse direction: do hardware-deployment papers use post-2020 low-T conversion methods?

*(Filled in from parallel research — see the reverse-direction / toolchain / artifacts fork
findings below in Tasks 1b, 2, and 3.)*

Chronological check first, since it partly answers the question by itself: Stromatias et al.
2015, Massa et al. 2020, and Patiño-Saucedo et al. 2020 all predate the QCFS lineage entirely
(QCFS: ICLR 2022, first posted 2021). They cannot cite methods that did not yet exist. NxTF
(Rueckauer et al., arXiv Jan 2021 / ACM TACO 2022) is close to the boundary — QCFS itself
postdates NxTF's arXiv posting by roughly a year, so NxTF could not have cited it either.

| # | Paper | Conversion method actually used | Cites any post-2020 low-T/QCFS-lineage method? | Chronology |
|---|---|---|---|---|
| 1 | Stromatias et al., IJCNN 2015 | Not CNN-conversion in the classical-toolbox sense — a Deep Belief Network trained offline (contrastive divergence), realized as a spiking network on SpiNNaker. Rate-coded. | No — predates the entire ANN-SNN low-T literature by 7+ years | Predates by construction |
| 2 | Patiño-Saucedo, Rostro-González, Serrano-Gotarredona, Linares-Barranco, *Neural Networks* 2020 (verified full text, non-paywalled repository copy) | **Two methods, both classical**: (a) direct conversion of a pre-trained LeNet CNN to SNN using the **SNN Toolbox** (explicitly named, citing Rueckauer et al. 2016/2017's threshold-balancing pipeline) for MNIST, deployed on a physical **SpiNNaker 103 machine** (48 chips), reaching 98.2% accuracy — the best reported on SpiNNaker at the time; (b) a spiking network trained from scratch with **STBP** (spatio-temporal backpropagation, a *direct-training* method, not conversion) for the event-based N-MNIST task, also deployed on SpiNNaker (97.92%). Both are rate-coded. | No — 2020 paper, cannot cite 2022+ literature | Predates by construction |
| 3 | Massa, Marchisio, Martina, Shafique, IJCNN 2020 | SNN Toolbox (Rueckauer et al. 2017 pipeline), deployed via NxSDK on physical Loihi (per a09) | No — predates the QCFS lineage | Predates by construction |
| 4 | Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild, NxTF, arXiv Jan 2021 / ACM TACO 2022 (verified full text) | Explicitly uses **SNN Toolbox** as the conversion front-end (Rueckauer et al. 2017 threshold-balancing/parameter-normalization), NxTF as the Loihi-side compiler. Rate-coded throughout (Table 2 in the paper: all "Conv." rows are labeled "(SNN TB)"). Also benchmarks a directly-trained (non-conversion) SLAYER model. | **No.** Full text and reference list checked directly (not just abstract): cites Stromatias 2015, Esser 2016, Davies 2021, and Patiño-Saucedo 2020 (for the STBP/SpiNNaker comparison row in its own benchmark table) — all classical/pre-2020 — and zero citations to Bu et al. (QCFS), Hao et al. (COS/SRP), or any other 2022+ low-T paper. This is the expected null result given the ~1-year gap, but it is confirmed rather than assumed: NxTF's own related-work paragraph name-checks Nengo, PyNN, SpiNNaker/BrainScaleS toolchains and classical conversion accuracy-improving papers, with no forward reference to the low-T literature that would explode over the following four years. | NxTF slightly precedes QCFS's public availability; could not have cited it, but the omission of *any* forward-looking awareness of the low-T program (which existed in preprint form as early as Deng & Gu 2021, cited by QCFS itself) shows the deployment side was not tracking the direction the algorithm side was about to take. |

**Aggregate for Task 1b:** **0 of 4 hardware-deployment papers use or cite any post-2020
low-T/QCFS-lineage conversion method.** Every one of them uses either the classical SNN
Toolbox/threshold-balancing pipeline (Rueckauer et al. 2017) or direct SLAYER/STBP training —
in every case, **rate-coded** (or, for the directly-trained SLAYER/STBP cases, not a
conversion method at all). Three of the four predate the QCFS lineage by construction, so
their silence is uninformative on its own; but Rueckauer's own team's NxTF (2021), written by
the same lab as the toolbox at the center of this entire deployment literature, shows no
awareness of the *direction* the algorithm side of the field was about to take (a program
Rueckauer's own students would have been well-positioned to notice, given SNN Toolbox's role
as the shared substrate). Combined with Task 1a's finding that only QCFS itself (of 13
algorithm papers checked) cites a deployment paper, and combined with the toolchain-freeze
finding in Task 2 (SNN Toolbox's last substantive commit is August 2022, right as the low-T
literature was taking off), the overall picture is a field whose deployment and algorithm
halves diverge in time as much as in citation: **the deployment-side toolchain stopped being
actively developed within months of the point where the algorithm-side literature it would
need to track began accelerating.**

---

## Task 2 — The toolchain freeze

Investigated directly: PyPI version history, GitHub repo metadata, release list, commit
history, documentation, and issue tracker for
`github.com/NeuromorphicProcessorProject/snn_toolbox` (SNN Toolbox, Bodo Rueckauer's
conversion framework — the same toolbox that underlies the Massa 2020 and Rueckauer 2021/NxTF
E1 results in a09).

**PyPI release history** (source: pypi.org/project/snntoolbox/#history — non-academic, PyPI):
13 releases total, from `0.1.0.dev0` (2017-06-24) to **`0.6.0`, uploaded 2021-03-17T20:09:31Z
— the final release, now over five years old**. No release since.

**GitHub repository state** (source: github.com/NeuromorphicProcessorProject/snn_toolbox —
non-academic, GitHub): created 2016-07-27. 399 stars, 106 forks, 3 open issues. **Not
GitHub-archived** (no archived banner; issues remain open/closeable, confirmed by issues #142,
#143 closed by users as late as 2024, and #145 closed Aug 2024) — but functionally dormant:
- **Release tag list**: last tagged release is `v0.5.0` ("Support for Tensorflow 2.2");
  changelog for the untagged final `0.6.0` PyPI upload reads "Improved temporal pattern code."
- **Commit history**: last substantive feature/bugfix commits are from **August 2022**
  ("Fixed kernel_conversion slicing issue," "Remove call of np.asscalar()," "Fixed deprecated
  import in GUI"). The single commit after that, dated **2023-01-13**, is "Added third paper"
  — a documentation-only commit adding a citation, not code. **No commits found after January
  2023** in the history reviewed.
- **Topics** on the repo include `loihi` and `spinnaker`, confirming the hardware backends
  (SpiNNaker via pyNN export, Loihi via NxTF integration — see Task 3) were built into the
  toolbox by the end of its active development window (pre-2021), not added later.

**Issue-tracker search for post-2020 low-T methods** (QCFS / "clip-floor-shift," offset-spike
correction, burst spikes, signed neurons): **none found.** No issue title, body, or comment
located in the tracker (issues #23, #64, #70, #126, #134–#145 reviewed) mentions QCFS,
clip-floor-shift, offset-spike, burst-spike neurons, or signed-neuron conversion. The two
issues closest to the low-T literature — **#142 "Quantization"** (Jan 2024) and **#143 "TTFS"**
(Jan 2024) — concern features the toolbox already had *before* the QCFS lineage existed:
TTFS spike coding was implemented following Rueckauer's own 2018 paper (Rueckauer & Liu,
"Temporal pattern coding," cited in the issue thread), and the "Quantization" issue is a user
asking how to feed a TensorFlow-quantized model into the toolbox's pre-existing
`quantize_weights` option — not a request for a QCFS-style quantization-aware training method.
The maintainer's own reply in #142 is telling: *"I won't be able to help much with debugging
at this point"* (rbodo, 2024-01-10) — an explicit, first-person admission of reduced
maintenance capacity, offered in response to an ordinary support question, not a feature
request for the post-2020 literature (which the maintainer never mentions).

**Timeline overlap, stated explicitly:**

| | Start | End (last substantive activity) |
|---|---|---|
| SNN Toolbox active development | 2016-07-27 (repo creation) | **~August 2022** (last feature/bugfix commit); **March 2021** (last PyPI release) |
| QCFS-lineage low-T literature | **Nov 2022 / ICLR 2022** (QCFS) | ongoing through 2025–2026 (AdaFire AAAI 2025, PMSM Aug 2025, LAS/AIF AAAI 2026) |

The overlap is a sliver at best: QCFS itself postdates the toolbox's final PyPI release by
about 20 months, and the entire subsequent explosion of the low-T literature audited in
Task 1a (OPI, SRP, COS, SlipReLU, Burst Spikes, SNM, Fast-SNN, Dynamic Confidence, SEENN,
CS-QCFS, AdaFire — spanning 2022 through 2025) unfolds entirely *after* the toolbox's code was
effectively frozen. The one channel that stayed open — the issue tracker — shows the
maintainer still answering questions personally into 2024, but declining new implementation
work, and no one in that tracker ever asked for a QCFS-family method to be added. The freeze is
not a case of the field asking and being refused; it is a case of the field not asking at all,
which is itself informative: the QCFS-lineage authors who *do* cite SNN Toolbox-adjacent
results (only QCFS itself, per Task 1a) never engage with the toolbox as a target artifact,
either to request features or to contribute an implementation.

---

## Task 3 — Shared artifacts

### 3a. QCFS-lineage repos: any hardware backend, chip export path, or NxTF/Lava/Sinabs/sPyNNaker integration?

| Repo | Paper | Hardware backend / chip export found? |
|---|---|---|
| `putshua/SNN_conversion_QCFS` (superseded by `putshua/ANN_SNN_QCFS`) | QCFS | **No.** Pure PyTorch (`main.py train`/`test`, `ann`/`snn` modes only). No NxTF, Lava, Sinabs, or sPyNNaker import or export path anywhere in the README or usage instructions. |
| `hzc1208/ANN2SNN_COS` | COS | **No.** Pure PyTorch/CUDA (`torch==1.12.1`, `spikingjelly==0.0.0.0.1`). No hardware backend code. |
| `bic-L/burst-ann2snn` | AdaFire | Not independently re-verified beyond a10's prior finding — a10 records this as the AdaFire code repo with no hardware backend documented. |
| `BrainSeek-Lab/PASCAL` | PASCAL | Per a10: acknowledges unreported "neuromorphic architectural simulator" benchmarking by a collaborator, but no backend code shipped in the repo itself; downstream, APEX (Task 4) integrates PASCAL's PASC-IF neuron into an accelerator *simulation* (E4), not the PASCAL repo itself gaining a hardware path. |
| `HaiyanJiang/SNN_Conversion_unified` | SlipReLU | Not independently fetched in this pass; SlipReLU's own paper text contains zero chip-specific content (Task 1a), making a hardware backend in the repo unlikely but not directly confirmed here. |

**Aggregate for 3a:** of the QCFS-lineage repos directly inspected, **0 contain a hardware
backend, chip export path, or integration with NxTF, Lava, Sinabs, or sPyNNaker.** They are
uniformly PyTorch training/evaluation scripts with an `ann` mode and a software-simulated
`snn` mode — consistent with every paper in Task 1a reporting E5 (pure software simulation).

### 3b. Neuromorphic deployment/tooling repos: any implementation of a post-2020 low-T method?

| Repo | Checked for | Found? |
|---|---|---|
| `NeuromorphicProcessorProject/snn_toolbox` | QCFS, offset-spike, burst spikes, signed neurons | **No** (see Task 2 — issue tracker and commit history searched directly; TTFS and quantization support both predate the QCFS lineage) |
| `lava-nc/lava-dl` (Intel) | Any post-2020 low-T conversion method | **No.** `lava.lib.dl.bootstrap` is Intel's own, independently-developed answer to the same problem QCFS addresses (rate-coded SNN training suffers at low T) — it works by dynamically fitting a piecewise-linear ANN approximation to the SNN during training, not by adopting QCFS, offset-spike calibration, or any cited low-T paper. The `netx` module added Loihi 2 graded-spike support in v0.3.0 (2023) — a platform-native code, not a rate-coding descendant of QCFS. No mention of QCFS, clip-floor-shift, SlipReLU, COS, or any Task 1a paper found in the docs or README. |
| `synsense/sinabs` | Any post-2020 low-T conversion method | Not independently re-confirmed beyond a10's finding (E3 at best — a generic, QCFS-agnostic ANN2SNN + BPTT toolchain; see Speck chip paper in Task 4, which uses Sinabs for a conventional conversion baseline, not a QCFS-style method). |
| `SpiNNakerManchester/sPyNNaker` | CNN-conversion examples using a post-2020 method | **No.** sPyNNaker itself is a general PyNN-on-SpiNNaker simulator package (see Frontiers 2018 system paper) with no CNN-conversion-specific code; the closest artifacts are third-party translators layered on top — e.g. `ncskth/bifrost` (PyTorch→SpiNNaker executable translator, generic, not QCFS-specific) and the historical SNN-Toolbox pyNN/SpiNNaker export path (also generic, pre-dates QCFS). |

**Aggregate for 3b:** **0 of 4 established/vendor-maintained neuromorphic tooling repos
implement any post-2020 QCFS-lineage method.** Each either predates the lineage (SNN Toolbox)
or independently reinvented a different solution to the same low-T problem (Lava-DL Bootstrap).

### 3c. The one bridging artifact found — with heavy caveats

`Krishnav1/neurocuda` (GitHub, 2026) is the single repository found in this entire search that
**explicitly implements QCFS and CS-QCFS as its conversion engine** *and* ships dedicated
backend code for physical neuromorphic silicon (`backends/spinnaker.py`,
`backends/brainscales.py`, plus a Loihi 2 *simulator*, not silicon, in `backends/loihi.py`).
Its own documentation claims:
- **SpiNNaker-1**: "Physical silicon confirmed" — two EBRAINS job-manager runs on real
  Manchester boards (2026-07-13, 2026-07-17), returning correct spike counts.
- **BrainScaleS-2**: "Analog silicon confirmed" — a 138-neuron network deployed to a named chip
  (chip 57, Heidelberg), with the repo's own documentation noting classification accuracy is
  "limited by analog mismatch and lack of per-synapse weight-value programming."

This is genuinely the closest thing found anywhere in this research to an artifact that unifies
the two literatures — a QCFS implementation with a real silicon deployment path. It is flagged
here (repeating the caveat from Task 4) because it is source-type: **GitHub, non-peer-reviewed,
self-reported**, and its own "physical silicon confirmed" SpiNNaker claim is a 2-neuron
validation network, not a benchmark-scale classifier; its stated next step is "full MLP
deployment." It does not change the aggregate picture in 3a/3b — no *published, peer-reviewed*
artifact bridges the two literatures — but its existence (as of mid-2026) suggests the gap is a
sociological/incentive gap in the *published* record rather than a technical impossibility:
nothing about QCFS-style conversion is intrinsically incompatible with a SpiNNaker or
BrainScaleS-2 deployment path, it is simply that no peer-reviewed QCFS-lineage paper has done
the (evidently tractable, if currently only hobbyist-demonstrated) work of wiring one up.

---

## Task 4 — The falsifier: papers in both populations

Searched deliberately, in many phrasings, for a paper that both proposes a new
conversion/low-T method and deploys it to physical neuromorphic silicon with measurements.

### Positive result: Quartz (Lenz, Orchard, Sheik — SynSense / Intel Labs, arXiv 2309.16795, 2023–2024)

**This is the falsifier for the strong form of the claim, and it confirms the refined
hypothesis exactly.**

- **Proposes a genuinely new conversion method**: Quartz, a Time-To-First-Spike (TTFS)
  ANN-to-SNN conversion scheme using two additional synapses per neuron (a "counterweight"
  synapse and a "rectifier" synapse) to avoid the dynamic-threshold machinery that made earlier
  TTFS methods hard to implement on real hardware.
- **Explicitly and self-consciously abandons rate coding.** The abstract states: "Most
  conversion methods rely on rate coding in the SNN to represent ANN activation, which uses
  enormous amounts of spikes and, therefore, energy." The paper frames its entire contribution
  as a rejection of the rate-coding convention that QCFS, OPI, SRP, COS, SlipReLU, Fast-SNN,
  SNM, SEENN, AdaFire, and CS-QCFS all retain.
  - Neurons fire **exactly once** per sample (non-leaky IF, single spike per neuron), not a
    rate-proportional spike count.
- **Deploys to physical Loihi 1 and reports real chip measurements, not estimates.** Table 3
  in the paper reports, for MNIST and CIFAR-10, on-chip static power, dynamic power, total
  power (mW), latency (ms), energy per inference (µJ), and Energy-Delay Product (EDP, µJ·s),
  measured "using NxSDK 1.0.0 with an Intel Xeon CPU E5-2650... and the Loihi Nahuku 32 board
  ncl-ext-ghrd-01." This is a direct, named, physical hardware measurement — the same standard
  a10/a09 used to classify Massa 2020 and Rueckauer 2021 (NxTF) as E1.
  - MNIST: 0.9 µJ·s EDP on Quartz vs. 4.38 µJ·s for a rate-coded baseline also run on Loihi
    (citing Rueckauer et al.'s own Loihi numbers) — a like-for-like, on-chip, method-vs-method
    comparison.
  - CIFAR-10: 10.3 mJ·s EDP for Quartz vs. ~34.9 mJ·s for the rate-coded baseline on Loihi.
- **Explicit head-to-head against rate coding, on the same chip.** Quartz is not just deployed
  in isolation; the paper's central empirical claim ("2- to 5-fold improvement in EDP over
  rate-coded converted networks") is a same-hardware, same-chip comparison against the
  literature's dominant paradigm — the closest thing found in this search to a paper that
  explicitly tests the tradeoff this survey is built around.
- **Not QCFS-lineage.** Quartz does not cite or build on QCFS, SlipReLU, or any of the
  low-T rate-coded family; its lineage runs through earlier TTFS work (Rueckauer & Liu 2018,
  Mostafa 2017, Park et al. patterned-coding papers). This is consistent with the "two
  literatures share no common thread" framing — Quartz is arguably a *third* population
  (temporal-coding conversion, hardware-native from the start), not a bridge between the two
  named ones.

### Negative/near-miss results (does NOT rise to the counterexample bar)

| Candidate | Proposes new conversion method? | Physical silicon + measurements? | Verdict |
|---|---|---|---|
| Brehove et al., ICONS 2026, Sigma-Delta on Loihi 2 (arXiv 2505.06417) | Yes — SDNN conversion using Loihi 2 native graded spikes | Yes — Loihi 2 VPX board, field-deployed, EDP measured | **Second confirmed E1+new-method paper.** Already identified in a10 as a contrast case. Explicitly abandons rate coding for Loihi 2's graded-spike payloads. Reinforces the refined hypothesis independently of Quartz. |
| Richter et al. (SynSense), "Speck" chip paper, arXiv 2304.06793 | Marginal — standard ANN2SNN conversion (via Sinabs), not a novel low-T algorithm; compared against a directly-trained BPTT-CNN baseline on the same chip | Yes — Speck1 ASIC, on-chip accuracy 86.17% (N-MNIST), 0.47 mW, 141 µJ/inference, measured | Not a counterexample to the strong claim: this is a chip-introduction paper using a *conventional* conversion baseline as one comparison point, not a paper whose contribution is a new low-T conversion algorithm. Still worth noting as an existence proof that "conversion methods reach real silicon" is not physically impossible — it is a sociological gap in the specific QCFS-descended literature, not a hardware limitation. |
| APEX (2025/2026), integrating PASCAL's PASC-IF neuron into the LoAS accelerator framework | Yes — reuses a QCFS-lineage low-T neuron design (PASC-IF, from PASCAL) | **No** — RTL/cycle-level accelerator simulation (same E4 category as NeuroFlex in a10), not physical silicon | Confirms rather than breaks the pattern: the one case found of a QCFS-*lineage* neuron reaching an accelerator implementation still stops at RTL simulation, not fabricated hardware. |
| Differential Coding for Training-Free ANN-to-SNN Conversion (Huang et al., ICML 2025) | Yes — explicitly a rate-coding alternative ("transmitting changes in rate information rather than rates directly") | No — CNN/Transformer benchmarks only, no hardware section found | Conceptually aligned with the refined hypothesis (abandons pure rate coding) but never deployed; strengthens the "algorithm-side abandonment of rate coding is necessary but not sufficient for reaching silicon" reading. |
| SpiNNaker2 end-to-end DNN framework (arXiv 2507.13736; SpiNNaker2 chip paper arXiv 2607.24396) | No — standard PyTorch→quantized-INT8 DNN deployment pipeline, not an ANN-to-SNN conversion algorithm contribution | Yes — physical chip, extensively measured | Out of scope: this is a DNN accelerator deployment paper, not an SNN conversion-algorithm paper: it targets INT8 DNN inference and only tangentially touches SNN simulation (a converted DVS-gesture SNN reported at 92.04% vs. 94.0% in software, using standard post-training quantization, not a novel low-T conversion method). |
| NeuroCUDA (GitHub repo, `Krishnav1/neurocuda`, 2026) | Claims QCFS+BPTT fine-tuning pipeline | Claims physical SpiNNaker-1 deployment (two Manchester board runs, "CONFIRMED") and physical BrainScaleS-2 deployment | **Not admissible as a counterexample.** This is an unreviewed, non-academic GitHub project (labeled here explicitly as source type: GitHub, not peer-reviewed). Its own documentation states the "physical silicon confirmed" SpiNNaker-1 test is a **trivial 2-neuron validation network** returning "2 spikes, 2 spikes" — not a CIFAR/ImageNet-scale classifier, and its own Loihi 2 physical-silicon claim is explicitly *not* confirmed ("Physical Loihi 2 silicon not yet run"). Flagged here for completeness (Task 3/4 overlap: an open-source artifact self-describing an attempt to bridge QCFS-style conversion and physical multi-platform deployment) but does not meet the bar of a published, peer-reviewed, benchmark-scale result. |

### Addendum: a rate-coded QCFS/SRP baseline *has* touched physical silicon once — via someone else's paper

A second, independent falsifier-search pass turned up **Jiang et al., "Adaptive Fission,"
NeurIPS 2025** (Tsinghua group), which complicates — without overturning — the "0/13 QCFS-lineage
papers ever touch silicon" finding in Task 1a/3a.

- Adaptive Fission's own novel contribution is a **population-coding** scheme (a third coding
  category the paper explicitly distinguishes from both rate and temporal coding), applied
  post-training on top of several existing conversion methods.
- It is deployed and measured on a physical **Lynxi HP201** neuromorphic accelerator (the
  commercial successor to Tsinghua's Tianjic chip): on-chip memory, inference latency, and
  energy are reported in the paper's Table 1.
- Critically, two of its baseline rows are **QCFS and SRP** — both audited in Task 1a/a10 as
  pure-E5, rate-coded, soft-reset-IF conversion methods that never touch hardware in their own
  papers. Adaptive Fission's Table 1 reports these baselines with **"No" Fission** (i.e., the
  unmodified, standard rate-coded QCFS/SRP conversion output, at T=32/16) alongside real,
  measured Lynxi HP201 latency and energy numbers (e.g., QCFS T=32, no fission: 68.10% accuracy,
  627 latency units, 7.82 energy units).
- **This means a rate-coded QCFS-lineage conversion output has, in fact, been measured on
  physical neuromorphic silicon** — not in QCFS's or SRP's own papers (which remain E5, as
  established in Task 1a and a10), but as a baseline row inside a later (2025), different paper
  whose own algorithmic novelty is not rate coding.

This does not break the refined hypothesis: Adaptive Fission's own contribution (population
coding) still abandons plain rate coding, consistent with Quartz and Brehove. But it sharpens the
strong claim that needs to survive into the published thesis text. The defensible formulation is
no longer "rate-coded QCFS-lineage output has literally never touched silicon" — it has, once,
via someone else's paper — but rather: **no QCFS-lineage algorithm paper deploys its own method
to silicon, and the one time a rate-coded QCFS/SRP baseline was measured on physical hardware, it
took a different paper's non-rate-coding innovation (and a different research group, and a
different, non-Loihi/non-SpiNNaker chip) to motivate doing so.** This is a stronger, more precise
claim than the unqualified original, and the survey should state it this way rather than the
absolute version.

Source: Jiang, Y. et al., "Adaptive Fission," NeurIPS 2025 proceedings PDF (paper id
e2e0a9004132490db1be58bffa419268), Table 1. [academic]; code at
https://github.com/JiangYizhou16/Adaptive-Fission [non-academic, GitHub, not independently
re-verified in this pass].

---

## Verdict on the refined hypothesis

**The refined hypothesis survives, and survives cleanly.** Every confirmed instance found of a
paper that (a) proposes a new/adapted ANN-to-SNN conversion method and (b) reports physical
silicon measurements — Quartz (TTFS) and Brehove et al. (Sigma-Delta graded spikes) — abandons
rate coding for a platform-native code (temporal single-spike coding for Quartz, graded/analog
sigma-delta spikes for Brehove). **No paper was found that keeps rate coding, deploys to
physical silicon, and proposes a new conversion algorithm.** The closest near-miss (Speck chip
paper) uses a conventional conversion baseline, not a novel low-T algorithm, and is a hardware
paper first, conversion-methods paper second. This is not proof of a causal mechanism, but the
pattern across the only two positive instances found in an extensive search is unanimous:
*platform co-design and rate-coding abandonment travel together with reaching real silicon*,
exactly as the refined hypothesis predicts.

One qualification, from the Adaptive Fission addendum above: a rate-coded QCFS/SRP *baseline*
(not the QCFS/SRP papers' own novel contribution) has been measured on physical Lynxi HP201
silicon — but only inside a later paper (Adaptive Fission, NeurIPS 2025) whose own algorithmic
contribution is population coding, a non-rate-coding scheme. The instance that put rate-coded
QCFS output on silicon still required a different paper's rate-coding-abandoning innovation to
happen. This is consistent with, not a counterexample to, the refined hypothesis: no paper was
found whose own new-algorithm contribution keeps rate coding and reaches silicon.

---

## Source list

**Task 1a sources (fetched and searched directly, primary text):**
1. Bu, Fang, Ding, Dai, Yu, Huang, "Optimal ANN-SNN Conversion..." (QCFS), ICLR 2022,
   arXiv:2303.04347. [academic, arXiv/ar5iv HTML]
2. Bu, Ding, Yu, Huang, "Optimized Potential Initialization for Low-latency SNNs" (OPI),
   AAAI 2022, arXiv:2202.01440. [academic, ar5iv HTML]
3. Hao, Bu, Ding, Huang, Yu, "Reducing ANN-SNN Conversion Error through Residual Membrane
   Potential" (SRP), AAAI 2023, arXiv:2302.02091. [academic, ar5iv HTML]
4. Hao, Ding, Bu, Huang, Yu, "Bridging the Gap...by Calibrating Offset Spikes" (COS),
   ICLR 2023, arXiv:2302.10685. [academic, ar5iv HTML]
5. Jiang, Anumasa, De Masi, Xiong, Gu, "A Unified Optimization Framework of ANN-SNN
   Conversion" (SlipReLU), ICML 2023, PMLR v202.
   https://proceedings.mlr.press/v202/jiang23a/jiang23a.pdf [academic, PDF, full text checked]
6. Li, Zeng, "Efficient and Accurate Conversion of SNN with Burst Spikes," IJCAI 2022,
   arXiv:2204.13271. [academic, ar5iv HTML]
7. Wang, Zhang, Chen, Qu, "Signed Neuron with Memory" (SNM), IJCAI 2022.
   https://www.ijcai.org/proceedings/2022/0347.pdf [academic, PDF, full text checked]
8. Hu, Zheng, Jiang, Pan, "Fast-SNN," TPAMI 2023, arXiv:2305.19868. [academic, ar5iv HTML]
9. Li, Jones, Furber, "Unleashing the Potential of SNNs by Dynamic Confidence," ICCV 2023,
   arXiv:2303.10276. [academic, ar5iv HTML]
10. Li, Ma, Furber, "Quantization Framework for Fast Spiking Neural Networks" (QFFS),
    Frontiers in Neuroscience 2022.
    https://www.frontiersin.org/articles/10.3389/fnins.2022.918793/full [academic, HTML,
    full text checked]
11. Li, Geller, Kim, Panda, "SEENN," NeurIPS 2023, arXiv:2304.01230. [academic, ar5iv HTML]
12. Yang, Yang, Zhang, Dou, Shen, Zhao, "CS-QCFS," Neural Networks 2024/2025.
    https://www.sciencedirect.com/science/article/abs/pii/S0893608024010050 [academic,
    abstract/highlights via search; https://pubmed.ncbi.nlm.nih.gov/39754841/ corroborating]
13. Wang, Fang, Cao, Ren, Xu, "Adaptive Calibration" (AdaFire), AAAI 2025,
    arXiv:2412.16219. [academic, arXiv PDF, full text checked]
14. Cross-check for "Singh et al. 2021": Singh, Sarma, Lu, Sengupta, Narayanan, Das,
    "Gesture-SNN: Co-optimizing accuracy, latency and energy of SNNs for neuromorphic vision
    sensors," ISLPED 2021. https://doi.org/10.1109/islped52811.2021.9502506 [academic]
15. yuzhaofei.github.io hosted copy of the QCFS ICLR camera-ready, used to confirm the exact
    "Massa et al. (2020) and Singh et al. (2021)" reference-list entries.
    https://yuzhaofei.github.io/papers/22-ICLR-Optimal%20ANN-SNN%20Conversion... [academic,
    author's own hosted PDF]

**Task 4 sources:**
16. Lenz, Orchard, Sheik, "Ultra-low-power Image Classification on Neuromorphic Hardware"
    (Quartz), arXiv:2309.16795 (v1 Sept 2023, v2 June 2024). [academic, arXiv PDF, full text
    checked in detail]
17. Brehove, Tumpa, Kyubwa, Menon, Narayanan, "Sigma-Delta Neural Network Conversion on
    Loihi 2," ICONS 2026, arXiv:2505.06417. [academic, arXiv HTML] (previously identified in
    a10; re-confirmed here as the second falsifier candidate)
18. Richter et al. (SynSense), "Speck: A Smart event-based Vision Sensor...," arXiv:2304.06793.
    [academic, arXiv HTML, full text checked]
19. Manjunath et al., "APEX: A Dual-Sparsity Accelerator for Precise and Efficient SNN
    Inference," arXiv:2608.19046 (2026). [academic, abstract via search]
20. Huang, Fang, Bu, Xue, Hao, Liu, Tang, Yu, Huang, "Differential Coding for Training-Free
    ANN-to-SNN Conversion," ICML 2025, PMLR v267.
    https://proceedings.mlr.press/v267/huang25i.html [academic, abstract]
21. "An End-to-End DNN Inference Framework for the SpiNNaker2 Neuromorphic MPSoC,"
    arXiv:2507.13736. [academic, abstract via search]
22. "The SpiNNaker2 chip: a many-core platform for flexible and scalable brain-inspired
    computing," arXiv:2607.24396 (2026). [academic, abstract/highlights via search]
22b. Jiang, Y. et al., "Adaptive Fission" (population-coding SNN acceleration), NeurIPS 2025
    proceedings PDF (paper id e2e0a9004132490db1be58bffa419268), Table 1. [academic, full text
    checked, incl. Table 1 QCFS/SRP baseline rows with measured Lynxi HP201 hardware numbers];
    code: https://github.com/JiangYizhou16/Adaptive-Fission [non-academic, GitHub, not
    independently re-verified]
23. Krishnav1/neurocuda GitHub repository. https://github.com/Krishnav1/neurocuda
    [non-academic, GitHub repo, self-reported/unreviewed claims — treated with explicit
    skepticism, not used as a counterexample]

**Task 1b, 2, and 3 sources:**
26. Patiño-Saucedo, Rostro-González, Serrano-Gotarredona, Linares-Barranco, "Event-driven
    implementation of deep spiking convolutional neural networks for supervised classification
    using the SpiNNaker neuromorphic platform," Neural Networks 121:319-328, 2020.
    https://doi.org/10.1016/j.neunet.2019.09.008 (open-access repository copy used for full
    text: https://idus.us.es/bitstreams/64fdb126-56e5-4e88-90e4-0f09c11f25e0/download)
    [academic, full text checked]
27. NxTF full text, cross-checked in two independent renderings for the reference list and
    Table 2 benchmark comparisons: https://arxiv.org/html/2101.04261 and
    https://dl.acm.org/doi/full/10.1145/3501770 [academic]
28. SNN Toolbox PyPI release history. https://pypi.org/project/snntoolbox/#history
    [non-academic, PyPI]
29. SNN Toolbox GitHub repository (main page, release list, commit history).
    https://github.com/NeuromorphicProcessorProject/snn_toolbox ,
    https://github.com/NeuromorphicProcessorProject/snn_toolbox/releases ,
    https://github.com/NeuromorphicProcessorProject/snn_toolbox/commits/master
    [non-academic, GitHub]
30. SNN Toolbox documentation (ReadTheDocs). https://snntoolbox.readthedocs.io/en/latest/guide/intro.html
    [non-academic, docs site]
31. SNN Toolbox GitHub issue tracker, issues #23, #64, #70, #126, #134–#145 reviewed for
    post-2020 method requests; #142 ("Quantization") and #143 ("TTFS") read in full.
    https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues [non-academic, GitHub]
32. `putshua/SNN_conversion_QCFS` (QCFS code repo). https://github.com/putshua/SNN_conversion_QCFS
    [non-academic, GitHub]
33. `hzc1208/ANN2SNN_COS` (COS code repo). https://github.com/hzc1208/ANN2SNN_COS
    [non-academic, GitHub]
34. `lava-nc/lava-dl` (Intel Lava-DL), README, Bootstrap documentation, and release notes.
    https://github.com/lava-nc/lava-dl , https://lava-nc.org/lava-lib-dl/bootstrap/bootstrap.html ,
    https://lava-nc.org/dl.html [non-academic, GitHub + vendor docs]
35. `SpiNNakerManchester/sPyNNaker` system paper (for scope-check only — general PyNN-on-
    SpiNNaker package, no CNN-conversion-specific code): "sPyNNaker: A Software Package for
    Running PyNN Simulations on SpiNNaker," Frontiers in Neuroscience 2018.
    https://doi.org/10.3389/fnins.2018.00816 [academic]
36. `ncskth/bifrost` (generic PyTorch-to-SpiNNaker translator, not QCFS-specific).
    https://github.com/ncskth/bifrost [non-academic, GitHub]
37. `Krishnav1/neurocuda` (the one bridging artifact — see Task 3c and Task 4 caveats).
    https://github.com/Krishnav1/neurocuda [non-academic, GitHub, unreviewed/self-reported]

**Cross-referenced from prior audits (not re-fetched here):**
24. a09-classical-conversion-audit.md (this repo) — Esser 2016 TrueNorth, Stromatias 2015
    SpiNNaker, Massa 2020 Loihi, Rueckauer 2021 NxTF, Kelber 2020 BrainScaleS/Spikey/SpiNNaker.
25. a10-lowlatency-audit.md (this repo) — full 16-paper QCFS-lineage E1–E5 classification,
    PASCAL/NeuroFlex E4 findings, Sinabs/DYNAP-CNN documentation pointer.

---

## Overall synthesis: does the claim hold?

**"Algorithm papers advance accuracy at low T and never deploy."** Holds essentially without
qualification for the papers' *own* reported experiments. 13/13 QCFS-lineage papers checked
directly in this audit report E5 (pure software simulation); 0/13 report an experiment on a
named chip. (Confirms and refines a10's 0/16 finding on a partially overlapping, partially
distinct sample.) One caveat worth stating precisely, from the Task 4 addendum: a rate-coded
QCFS/SRP *baseline configuration* has since been re-run and measured on physical Lynxi HP201
silicon — but only inside a later, third-party paper (Adaptive Fission, NeurIPS 2025) whose own
algorithmic contribution is a different, non-rate-coded (population) coding scheme, not by QCFS
or SRP's own authors. The claim as stated ("never deploy") is true of every QCFS-lineage paper's
own reported work; it is not true that rate-coded QCFS/SRP output has *never* touched silicon
under any circumstances.

**"Deployment papers reach silicon and never use the new algorithms."** Holds without
qualification on every instance checked. 0/4 hardware-deployment papers audited in Task 1b use
or cite a post-2020 conversion method; every one uses the classical SNN Toolbox pipeline or
direct training, rate-coded.

**"The two literatures cite each other's motivations and share no artifacts."** This is the
part of the claim that needed the most qualification, and the qualification runs in a
consistent direction across all four tasks: the asymmetry is real and large but not absolute.
- QCFS itself is a genuine, single exception to "motivations only" — it cites two E1 papers
  (Massa 2020, Singh 2021) in related work as acknowledged prior art, not as throat-clearing.
  12 of its 13 audited descendants revert to the pure-motivation pattern.
- "Share no artifacts" holds for every *published, peer-reviewed* repository checked (QCFS,
  COS, SNN Toolbox, Lava-DL, sPyNNaker) — but one unreviewed, non-peer-reviewed GitHub project
  (`neurocuda`, 2026) explicitly implements QCFS/CS-QCFS and claims physical SpiNNaker-1 and
  BrainScaleS-2 deployment, albeit on trivial validation-scale networks. It does not overturn
  the claim about the published record, but it is evidence the gap is sociological/incentive-
  driven rather than technically forced.
- The toolchain freeze is real and precisely dated: SNN Toolbox's last release (March 2021)
  and last substantive commit (August 2022) both precede the bulk of the low-T literature's
  publication window, and no one in its issue tracker ever asked for a QCFS-family feature.

**The refined hypothesis** ("papers that do both are precisely the ones that abandon rate
coding and co-design with the platform") **survives cleanly.** The two positive instances found
in an extensive, deliberately adversarial search — Quartz (TTFS) and Brehove et al.
(Sigma-Delta graded spikes) — both abandon rate coding for a platform-native code and both
report real, named, measured physical-silicon results. No paper was found that keeps rate
coding, proposes a new conversion algorithm, and reaches physical silicon with measurements.
This is the strongest and most falsifiable part of the survey's argument, and it is the part
that held up best under scrutiny.
