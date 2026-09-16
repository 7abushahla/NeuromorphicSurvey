# A15 — Coverage map of prior SNN / neuromorphic / ANN-to-SNN surveys

Purpose: establish what ~35 prior surveys (2017-2026) cover and, specifically, whether any of
them already cover axes I (edge semantics), J (evidence classification), and L (end-to-end
traceable routes) before this thesis's survey claims that gap. Method: Exa web search/fetch for
externally published surveys; `pypdf`-based text extraction (abstract + first pages + detected
section headings, since `pdftoppm`/poppler is not installed in this environment and the Read
tool's PDF-page rendering therefore fails) for the PDFs held in the author's Obsidian vault.

Scoring legend: **Full** / **Partial** / **Mentioned** / **—** (absent). Scores are argued from
the survey's own stated contributions, section structure, or (where full text was available)
direct keyword verification, not assumed from title alone. Source type is labeled for every
entry per the relaxed source policy: peer-reviewed / preprint / conference (peer-reviewed) /
book chapter (peer-reviewed) / vault-note-only (unverified against primary text).

Axes: A neuron models · B encodings/neural codes · C direct training methods · D ANN-to-SNN
conversion · E software frameworks · F compilers/hardware-mapping toolchains · G interchange
formats (NIR) · H hardware platforms · I edge semantics (what breaks between layers/platforms) ·
J evidence classification (silicon vs. simulation vs. op-count estimate) · K applications with
measured results · L end-to-end traceable route, trained network → specific chip.

---

## Headline finding (read this first)

The premise that axes I, J, and L are absent or weak in essentially all prior surveys **holds**,
but not by a clean margin. Six prior works come close enough that the new survey must position
itself explicitly against them rather than claim a clean gap:

1. **Pedersen et al. 2024, "Neuromorphic Intermediate Representation" (NIR), Nature
   Communications** [peer-reviewed] — the strongest counter-example on **I**. NIR is a real
   interchange format that (a) explicitly documents which neuron mechanisms are *excluded* from
   its representation (adaptive threshold, gating, resonate-and-fire, multicompartmental), (b)
   reports *measured divergence* between the idealized continuous-time model and 11 discretized
   platform implementations — "platform-specific constraints and discretization choices produced
   somewhat diverging activation patterns and accuracies" for a recurrent network — and (c)
   deploys three benchmark graphs end-to-end across 7 simulators and 4 physical chips (Loihi 2,
   Speck, SpiNNaker2, Xylo). That is a genuine, if narrow, I + J + L instance. Its scope is
   3 toy/benchmark graphs (1 LIF neuron, 1 conv SNN, 1 recurrent SNN), not full deployable
   networks, and it does not treat reset-policy semantics, operator coverage for conv/pool/
   residual blocks, or payload/precision as first-class deployment concerns the way an
   applications-oriented survey would. The new survey's contribution on I needs to be framed
   explicitly as *broader in scope* (full CNNs, not toy graphs) than NIR, not as filling a
   vacuum NIR left completely empty.

2. **Kudithipudi et al. 2025, "Neuromorphic computing at scale," Nature** [peer-reviewed] — the
   strongest counter-example on the *diagnostic* half of I and F. Its Fig. 4 is explicitly
   captioned "Case studies showcasing the gaps in the neuromorphic computing software ecosystem
   as compared to AI/ML," and its "Cross-platform neuromorphic software" section states plainly
   that interoperability across SNN frameworks is limited compared to ANN frameworks, that a
   "hardware abstraction layer" and "compilation scheme for porting arbitrary spiking neural
   network models to any hardware architecture" do not yet exist, and that "metrics for
   measuring hardware performance... do not have a consensus." This is a Nature-level authority
   *naming* exactly the problem the new survey addresses — but only diagnostically. It does not
   catalog what specifically breaks (reset semantics, operator coverage, time model) layer by
   layer, does not build a J-type evidence-classification scheme (it flags the absence of
   consensus metrics, it does not supply one), and gives no L-type worked case study. Score:
   Partial on I, F, J; absent on L. The new survey should cite this paper as the field's own
   acknowledgment that the gap exists, which strengthens rather than undercuts the survey's
   motivation.

3. **Yik et al. 2025, "The NeuroBench framework," Nature Communications** [peer-reviewed] and
   **Deng et al. 2025, "Edge Intelligence with Spiking Neural Networks" (EdgeSNN survey), arXiv**
   [preprint, under review] — both build an explicit **two-track** evidence structure
   (hardware-independent "algorithm track" using operation-count/complexity proxies vs.
   hardware-dependent "systems track" using real deployed measurement). This is a genuine
   physical-vs-proxy classification and the closest prior instance of axis J's spirit — but it
   is two-way (simulation/estimate vs. real hardware), not the three-way physical-silicon /
   simulation / operation-count-estimate split the new survey specifies, and in both cases it is
   a *benchmark design decision*, not a critical classification applied retrospectively to the
   literature's own claims. Deng et al. 2025 is the first paper found in this search to call
   itself, in its own words, "the first dedicated and comprehensive survey on EdgeSNNs" and to
   center the survey on exactly the deployment axis (on-device inference, resource-aware
   training, security) the thesis cares about. It is the single closest prior survey overall to
   the new survey's territory and must be discussed by name, not folded into a generic list.

4. **Davies et al. 2021, "Advancing Neuromorphic Computing With Loihi," Proc. IEEE**
   [peer-reviewed] — the strongest counter-example on **L**, scoped to one chip. It repeatedly
   traces specific trained/converted networks through to physical Loihi silicon with measured
   latency and energy across event-based data processing, adaptive control, constrained
   optimization, sparse regression, and graph search. This is real L-type evidence — but for a
   single hardware target, not a generalizable route-finding methodology across chips, and the
   survey does not attempt cross-chip comparison of what a given network configuration would
   look like elsewhere.

5. **Huynh/Balaji/Das et al. 2022, "Implementing Spiking Neural Networks on Neuromorphic
   Architectures: A Review," arXiv** [preprint] — the only survey found that is *entirely* about
   system-software / compiler frameworks for neuromorphic hardware (SentryOS/SentryC, TrueNorth's
   Corelet, PACMAN for SpiNNaker, SpiNeMap, PyCARL, DecomposeSNN, run-time managers, TENNLab).
   This is the closest prior survey to axis F's spirit, but it reviews a **different** toolchain
   family than the one the new survey names as its example (NxTF, NetX, DynapCNN mapper,
   sPyNNaker) — none of those four specific tools were found treated comparatively together in
   any survey located in this search. That absence is itself a finding worth stating explicitly:
   the compiler/mapping literature that exists is fragmented across incompatible toolchain
   families, and no survey unifies them.

6. Several hardware- and circuit-level surveys practice partial **evidence discipline** without
   building a taxonomy: Basu et al. 2022 (CICC) and the EPJB 2024 systematic review both
   *normalize* reported numbers to a common process node / supply voltage before comparing chips
   — a real methodological safeguard against the physical/estimate conflation the new survey's J
   axis targets, but applied as a cleanup step, not stated as a classification principle. The
   MDPI 2025 "Practical Tutorial" paper is unusually explicit that its own energy numbers are a
   "GPU-based operation-count energy proxy," i.e., it self-labels an estimate as an estimate —
   a positive individual practice, not a cross-literature framework.

**Net assessment:** the gap on I, J, L is real at the level of "no prior survey builds a
systematic taxonomy of what breaks across deployment boundaries, classifies evidence types across
the literature, and traces full deployable networks end-to-end across multiple named chips." It
is not real at the level of "no prior work has ever touched these concerns" — NIR, Kudithipudi
2025, NeuroBench, and the EdgeSNN survey all touch pieces of it seriously enough that the new
survey's contribution section needs comparison paragraphs against each of these four by name, not
a blanket "no one has looked at this" claim.

---

## Coverage table

Surveys are grouped by where they were found (web literature vs. author's vault) and ordered
roughly by relevance to deployment. `F`=Full, `P`=Partial, `M`=Mentioned, `–`=Absent.
Uncertain scores (based on abstract/reference-list only, not full text) are marked `†`.

| # | Survey (short name) | Year | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Pedersen et al. — NIR | 2024 | P | – | – | – | F | P | **F** | F | **F** | **P** | – | **P** |
| 2 | Kudithipudi et al. — Neuromorphic computing at scale | 2025 | M | M | M | – | P | **P** | M | F | **P** | **P** | P | – |
| 3 | Deng et al. — EdgeSNN survey | 2025 | F | P | F | F | M | M | – | F | **P** | **F** | F | P |
| 4 | Yik et al. — NeuroBench | 2025 | – | – | – | – | P | – | – | P | – | **F** | F | M |
| 5 | Davies et al. — Loihi survey | 2021 | P | P | P | P | M | P | – | F | M | P(single-chip) | F | **P**(single-chip) |
| 6 | Huynh/Balaji/Das et al. — Implementing SNNs on Neuromorphic Architectures | 2022 | – | – | – | – | – | **F** | – | P | P | M | – | P |
| 7 | Roy, Jaiswal & Panda | 2019 | P | P | F | P | – | – | – | F | – | – | P | – |
| 8 | Schuman et al. — 35-year survey | 2017 | F | P | F | M | P | – | – | F | – | – | F | – |
| 9 | Schuman et al. — Opportunities (Nat. Comp. Sci.) | 2022 | P | P | P | M | – | – | – | P | – | – | P | – |
| 10 | Eshraghian et al. — Training SNNs | 2023 | P | F | F | P | M | – | – | M | – | – | M | – |
| 11 | Rathi et al. — Algorithms to Hardware (ACM CSUR) | 2023 | F | F | F | F | M | P | – | F | – | – | P | – |
| 12 | Yamazaki et al. | 2022 | F | P | F | P | F | – | – | M | – | – | F | – |
| 13 | Ivanov et al. | 2022 | M | – | – | – | – | – | – | F | – | – | M | – |
| 14 | Basu et al. — SNN ICs (CICC) | 2022 | – | – | – | – | – | – | – | F | – | **P** | M | – |
| 15 | Nunes et al. — SNN survey (IEEE Access) | 2022 | F | F | F | M | M | – | – | M | – | – | P | – |
| 16 | Khan et al. — Comprehensive Survey (AISE) | 2025 | P | – | F | F | M | – | – | F | – | – | F | – |
| 17 | Zheng et al. — Introductory review | 2022 | F | M | F | M | – | – | – | – | – | – | – | – |
| 18 | "Towards Neuromorphic Computing on Edge" (authors unconfirmed) | n.d. | F | M | P | F | – | – | – | – | M | – | P | – |
| 19 | Xie, Yang & Gao — Compression survey | 2024 | M | – | P | – | – | – | – | M | – | – | – | – |
| 20 | Ferreira et al. — DNN/SNN edge-AI circuits | 2025 | F | M | M | – | – | – | – | F | – | **P** | F | – |
| 21 | Manna et al. — Frameworks for SNNs | 2023 | – | – | – | – | **F** | P | – | – | – | – | – | M |
| 22 | Gallego et al. — Event-based Vision | 2019/22 | – | – | M | – | M | – | – | P(sensor) | – | – | F | – |
| 23 | Gebregiorgis et al. — Spike-based NC overview | 2025 | F | M | F | M | – | F† | M† | F | M† | – | F | P† |
| 24 | Bouvier et al. — SNN HW implementations & challenges | 2019 | M | – | – | – | – | – | – | F | – | – | M | – |
| 25 | Shrestha et al. — Models and Hardware (IEEE CASM) | 2022 | F | – | M | – | – | – | – | F | – | – | M | – |
| 26 | "A New Era in Computing" (Chips, MDPI) | 2026 | P | – | – | – | – | – | – | F | – | **P** | M | – |
| 27 | "Brain-inspired computing systems" (EPJB) | 2024 | – | – | – | – | – | – | – | F | – | **P** | M | – |
| 28 | "Toward Large-scale SNNs" (Spiking Transformers) | 2024 | P | – | F | F | – | – | – | – | – | – | M | – |
| 29 | "A Practical Tutorial on SNNs" (MDPI) | 2025 | F | F | F | P | F | – | – | M | – | **P**(self only) | F | – |
| 30 | Al Abdul Wahid et al. — Neuromorphic Architectures survey | 2024 | F | – | P | – | – | – | – | F | – | – | M | – |
| 31 | Tayarani-Najaran & Schmuker — Event-based sensing | 2021 | – | F | – | – | – | – | – | F(sensor) | – | – | F | – |
| 32 | Cimarelli et al. — Neuromorphic Vision Sensor review | 2025 | – | – | – | – | – | – | – | F(sensor) | – | – | F | – |
| 33 | Four-Stage Structural Evolution SNN (NPL) | 2026 | M | – | P | P | – | – | – | – | – | – | – | – |
| 34 | Luu et al. — SNN Foundation and Recent Progress | 2026 | M† | M† | M† | M† | M† | – | – | M† | – | – | M† | – |
| 35 | Caviglia et al. — NeuroTrain | 2026 | M | – | F | P | P | – | – | – | – | P | – | – |
| 36 | "Benchmarking SNNs across sensing modalities on edge devices" | 2026 | – | – | – | – | – | – | – | P | – | P | F | M |
| 37 | Farsa et al. — GPU/RISC-V acceleration survey | 2026 | – | – | – | – | M | P | – | F | M | – | – | M |

---

## Per-survey notes

### 1. Pedersen, J. E. et al. "Neuromorphic intermediate representation: a unified instruction set
for interoperable brain-inspired computing." *Nature Communications* 15, 8122 (2024).
[peer-reviewed]

The interchange-format paper explicitly requested by the brief. NIR defines a fixed set of hybrid
continuous-time primitives (leaky integrator, integrate-and-fire) shared across 7 simulators
(Lava, Nengo, Norse, Rockpool, Sinabs, snnTorch, Spyx) and 4 physical hardware targets (Loihi 2,
Speck, SpiNNaker2, Xylo). Full text confirms: it explicitly lists excluded neuron mechanisms
(adaptive threshold, gating, resonate-and-fire, multicompartmental — i.e., states what the IR
does *not* preserve, a direct I-axis statement); it reports measured divergence between
idealized and platform-specific execution for a recurrent network (a real I+J instance); and it
demonstrates 3 computational graphs deployed end-to-end on all 11 platforms (a real, if narrow,
L instance). Not a survey of applications, and its worked examples are single-neuron/small-graph
toy problems rather than full CNNs — the new survey's deployable-network scope is a genuine point
of differentiation, not overlap.

### 2. Kudithipudi, D. et al. "Neuromorphic computing at scale." *Nature* 637, 801-812 (2025).
[peer-reviewed] (vault: `05-Neuromorphic-Background/03-General-Surveys/s41586-024-08253-8.pdf`)

Keyword-verified against full text (via NSF/gwern-hosted mirror): 0 hits for "toolchain"; the
word "compiler"/"compilation" appears only in the phrase "compilation scheme" describing a
*missing* capability the field needs to build. "Software" appears in a section header
("Cross-platform neuromorphic software") but the content is diagnostic — it names the
interoperability gap (Fig. 4 caption: "Case studies showcasing the gaps in the neuromorphic
computing software ecosystem as compared to AI/ML") and the missing hardware abstraction layer
without cataloging what breaks or building a classification. Explicitly states there is no
consensus on hardware-performance metrics — a direct acknowledgment of the J-axis problem without
solving it. No worked end-to-end case study (L = absent). This is a landmark venue (Nature) and
must be cited as the field's own top-level acknowledgment that the deployment-fidelity and
evidence-standardization problems the new survey addresses are real and unsolved.

### 3. Deng, S. et al. "Edge Intelligence with Spiking Neural Networks." arXiv:2507.14069 (2025).
[preprint]

Self-described as "the first dedicated and comprehensive survey on EdgeSNNs." Structure (from
full text): Sec. III network modeling/learning algorithm/hardware-support taxonomy; Sec. IV
three deployment-practical considerations (on-device inference with lightweight models,
resource-aware training/updating under non-stationary data, security/privacy); Sec. V a
"dual-track benchmarking strategy" explicitly built to separate conventional-hardware proxy
evaluation from hardware-aware/neuromorphic evaluation, citing and extending NeuroBench's
track split; Sec. VI open challenges. This is the closest prior survey in scope to the thesis's
own concerns (on-device SNN deployment, quantization/pruning/KD as lightweight-model techniques,
hardware heterogeneity as an open challenge) and should be treated as primary related work, not a
background citation. It does not, however, build an I-axis taxonomy of what specifically breaks
at each deployment boundary (reset policy, operator coverage, payload, time model), and has no
single worked L-axis case study tracing one network through one full pipeline to one named chip
with reported numbers — it inventories techniques and hardware categories rather than tracing a
route.

### 4. Yik, J. et al. "The NeuroBench framework for benchmarking neuromorphic computing
algorithms and systems." *Nature Communications* 16, 1545 (2025). [peer-reviewed]
(Earlier arXiv preprint: Yik et al., arXiv:2304.04640, 2023.)

A benchmark-design paper, not a literature survey, but its two-track structure is the clearest
prior instance of J-type thinking found in this search: the "algorithm track" explicitly reports
hardware-independent complexity proxies (e.g., synaptic operations, SOPs) while the "systems
track" explicitly defines protocols for measuring real deployed hardware speed and efficiency.
The paper is candid that this split exists precisely because "large-scale neuromorphic hardware
has not converged to a single platform," i.e., because algorithm-only estimates and physical
measurements are not interchangeable — the same concern the new survey's J axis targets, though
NeuroBench treats it as a benchmarking-protocol problem to solve going forward rather than a
critique of how existing literature reports evidence. No I-axis or L-axis content (it defines
metrics, not a deployment-fidelity taxonomy or a specific worked route).

### 5. Davies, M. et al. "Advancing Neuromorphic Computing With Loihi: A Survey of Results and
Outlook." *Proceedings of the IEEE* 109(5), 911-934 (2021). [peer-reviewed]

Single-chip survey of everything demonstrated on Loihi across deep-learning-style and
brain-inspired approaches. Contains dense measured-result tables (latency, energy) across event
data processing, adaptive control, constrained optimization, sparse regression, and graph search
— genuine physical-silicon evidence, repeatedly, which is unusual among general surveys. This
constitutes the strongest L-axis precedent found, but scoped entirely to one chip; there is no
cross-chip generalization or discussion of what changes if the same network targets a different
platform, so it does not anticipate a general "traceable route" methodology.

### 6. Huynh, P. K., Varshika, M. L., Paul, A., Isik, M., Balaji, A., Das, A. "Implementing
Spiking Neural Networks on Neuromorphic Architectures: A Review." arXiv:2202.08897 (2022).
[preprint]

The only survey located that is entirely organized around system-software/compiler frameworks:
platform-based design (SentryOS/SentryC compiler, TrueNorth's Corelet programming paradigm,
LCompiler, PACMAN partitioning/configuration manager for SpiNNaker, PyNN, Nengo, PSO-based SNN
mapping, SpiNeMap, PyCARL/CARLsim, DecomposeSNN, run-time managers, TENNLab, scalable
neuromorphic mapping frameworks) and hardware-software co-design approaches, organized by
performance/energy optimization vs. thermal/reliability optimization. This is real F-axis
coverage — but of a *different* toolchain family than the example the brief names (NxTF, NetX,
DynapCNN mapper, sPyNNaker): none of those four tools appear in this survey's reference set, and
no survey found in this search treats all four together. The compilation/mapping works it
reviews (especially SpiNeMap) implicitly touch graph-to-core mapping fidelity, which is adjacent
to but not the same as the I axis's reset-semantics/operator-coverage/payload framing.

### 7-13. General algorithm/hardware surveys (Roy 2019; Schuman 2017; Schuman 2022; Eshraghian
2023; Rathi 2023; Yamazaki 2022; Ivanov 2022; Basu 2022)

All previously well-known landmark surveys, confirmed via search (abstracts, section structure,
and in Schuman 2022's case, full-text keyword verification — 0 hits for "compiler"/"toolchain"/
"software" as section content, 2 hits "silicon" used only in passing). These form the algorithmic
and hardware backbone of the field's self-understanding but were written before (Roy 2019,
Schuman 2017/2022, Eshraghian 2023) or largely outside (Rathi 2023, Basu 2022) the current
software-ecosystem/interchange-format/deployment-benchmarking conversation that NIR, NeuroBench,
Kudithipudi 2025, and Deng 2025 represent. None discusses reset-semantics-level edge fidelity or
builds an evidence-classification scheme; Basu 2022 is a partial exception in that it normalizes
reported IC numbers to a common process node before comparing them (a J-adjacent methodological
practice, not a classification framework), and explicitly calls out the field's lack of
standardized benchmarks as an open problem — an early instance of the same complaint Kudithipudi
2025 repeats four years later.

### 14-20. Additional general/topical surveys found via web search (Nunes 2022, Khan 2025,
Zheng 2022, "Towards Neuromorphic Computing on Edge" [authors unconfirmed — the extracted PDF
text truncates the author list before the affiliations line; flagged for the author to
cross-check against the vault PDF's byline], Xie/Yang/Gao 2024, Ferreira 2025, Manna 2023)

Standard survey territory (neuron models, encodings, training taxonomies, applications). Notable
individual points: **Xie, Yang & Gao 2024** ("Toward Efficient Deep Spiking Neuron Networks: A
Survey on Compression," Springer LNCS/LNAI, ISBN 978-981-97-6125-8) is the vault survey closest
to the thesis's own quantization focus — it surveys pruning, quantization, knowledge distillation
and spike-firing/timestep reduction as SNN efficiency techniques, but frames these purely as
training-time compression methods, not as a deployment-boundary problem; it is a natural citation
for the thesis's related-work section on quantization but does not compete on I/J/L. **Ferreira
et al. 2025** is methodologically disciplined for a short "mini review": it normalizes energy
(J/OP) and area (μm²/OP) across fabricated works from different integration technologies before
comparing them — a real, if narrow, J-adjacent practice — and is explicit that "benchmarks remain
fragmented" as an open problem. **Manna et al. 2023**'s 9-framework comparison table includes a
"Destination Backend/Platform" column (e.g., SNN Toolbox → PyNN/Brian2/MegaSim/SpiNNaker/Loihi)
that is a compact, real instance of framework-to-hardware compatibility inventory — touching F
and gesturing at L — but it is a compatibility list, not a semantic-fidelity or measured-result
trace.

### 21-22. Gallego et al. (Event-based Vision) and event-camera-adjacent vault surveys
(Tayarani-Najaran & Schmuker 2021; Cimarelli et al. 2025)

The requested event-camera survey line. All three are sensor/vision surveys, not SNN-compute
deployment surveys — they cover encoding (spike/event representations) and application taxonomies
in depth but do not engage the SNN training/conversion/deployment-toolchain literature this
thesis sits in. Included for completeness per the brief's explicit request, scored accordingly
(strong on B/H(sensor)/K, absent elsewhere).

### 23. Gebregiorgis, A. et al. "Spike-based neuromorphic computing: An overview from
bio-inspiration to hardware architectures and learning mechanisms." *Microprocessors and
Microsystems* (2025). [peer-reviewed]

Assessed from abstract, reference list, and topic metadata only (full text not fetched — flagged
with `†` in the table). Its abstract explicitly names "mapping and compilation strategies" as a
dedicated later section, which would make it the strongest F-axis candidate among the tutorial-
style surveys if confirmed at depth; this is a provisional Full score that the author should
verify against the full text before relying on it, since abstract-level self-description can
overstate depth. Co-authored by several NIR/Rockpool-community researchers (Frenkel, Zenke,
Bohté, Das, Corradi), so likely NIR-aware, but G-axis coverage is unconfirmed.

### 24-25. Bouvier et al. 2019 (ACM JETC) and Shrestha et al. 2022 (IEEE CASM)

Hardware-survey citations pulled from NeuroBench's own related-work section; not independently
fetched in full. Included because they are cited as established hardware-implementation surveys
by more recent work and round out axis-H coverage; scored conservatively from title/citation
context only.

### 26-27. "A New Era in Computing" (Chips, MDPI, 2026) and "Brain-inspired computing systems"
(European Physical Journal B, 2024)

Both chip-architecture-comparison surveys with genuine normalization discipline: the Chips 2026
paper introduces "a novel five-dimensional comparative framework" (process technology, scale,
power, neuronal models, architectural features); the EPJB 2024 paper explicitly "adopt[s] a
normalization approach for... reported figures for the performance per watt... so that we can
fairly compare" different chips' claimed efficiency. Both are J-adjacent in the same way Basu
2022 and Ferreira 2025 are — real methodological rigor applied to make chip comparisons fair —
without building a physical/simulation/estimate classification scheme as such.

### 28-29. "Toward Large-scale Spiking Neural Networks" (Spiking Transformers survey, arXiv
2409.02111, 2024) and "A Practical Tutorial on Spiking Neural Networks" (MDPI, 2025)

The former is purely an algorithm/architecture survey (ANN-to-SNN conversion vs. direct training,
DCNN vs. Transformer architectures for SNNs) with no deployment content. The latter is notable for
one thing: it is unusually explicit that its own reported energy numbers come from "a GPU-based
operation-count energy proxy" — i.e., the paper *labels its own results as an estimate rather
than a measurement*. That is exactly the discipline the new survey's J axis calls for, practiced
correctly but only for the paper's own data, not extended into a framework for classifying claims
across the literature.

### 30-32. Al Abdul Wahid et al. 2024 (Electronics, vault); Tayarani-Najaran & Schmuker 2021
(Frontiers in Neural Circuits, vault); Cimarelli et al. 2025 (arXiv, vault)

Confirmed via full-text section-heading extraction (vault PDFs). Al Abdul Wahid et al. 2024's
Table 1 ("Summary of neuromorphic project properties") is a genuinely useful hardware comparison
(TrueNorth, Loihi, Loihi2, Tianjic, SpiNNaker, BrainScaleS, GrAIOne, Akida, IBM memristor chip)
covering in-memory computation, signal type, scale, on-device learning, event-driven-ness,
process node — but stops at the architecture-comparison level, no deployment-pipeline content.
The latter two are event-camera/sensor surveys (see #21-22 discussion above).

### 33-37. Vault-note-only 2026 surveys (Four-Stage Structural Evolution; Luu et al. SNN
Foundation; Caviglia et al. NeuroTrain; "Benchmarking SNNs... edge devices"; Farsa et al.
GPU/RISC-V acceleration survey)

These five entries exist in the vault only as short markdown notes written during a September
2026 literature-refresh pass; the underlying PDFs were not downloaded and the notes themselves
flag that abstracts were not independently retrieved at the time (arXiv API rate-limited). Scores
here are therefore necessarily provisional (marked `†` where most uncertain) and should not be
treated as verified in the way the fetched/full-text entries are. Two are worth flagging for
follow-up despite the uncertainty: **Caviglia et al., "NeuroTrain"** (arXiv:2605.15058) pairs a
local-learning-rules taxonomy with an "open benchmarking framework" built on snnTorch — another
instance of the benchmark-framework-as-evidence-discipline pattern seen in NeuroBench/EdgeSNN,
worth checking directly once the PDF is available. **Farsa et al.**, "GPU and RISC-V acceleration
for neuromorphic computing based on SNNs: taxonomy, comparison, and open challenges"
(*Neuromorphic Computing and Engineering*, accepted manuscript, 2026-09-09) is a deployment-
toolchain-adjacent survey by its own title ("taxonomy, comparison... open challenges") that
targets GPU/RISC-V acceleration rather than dedicated neuromorphic silicon — plausibly relevant
to F/H but for general-purpose accelerator mapping, not chip-specific compiler toolchains; also
worth a full-text check once accessible.

---

## Non-survey primary sources worth noting (not scored on the A-L table)

- **Smith, H., Seekings, J., Mohammadi, M., Zand, R. "Realtime Facial Expression Recognition:
  Neuromorphic Hardware vs. Edge AI Accelerators." arXiv:2403.08792 (2024).** [preprint, primary
  research] (vault: `05-Neuromorphic-Background/01-Intro/2403.08792v1.pdf`) — a real, measured,
  physical-silicon comparison (Intel Loihi vs. Raspberry Pi-4, Intel NCS, Jetson Nano, Coral TPU)
  reporting power, energy, accuracy, and latency for one deployed task. This is exactly the kind
  of L/J-type evidence the new survey argues is missing *at the survey level* — and its existence
  as a scattered primary paper, uncited by any general SNN survey found in this search, supports
  the argument that such evidence exists in the literature but has not been synthesized or
  classified by any prior survey.
- **Alkendi, Y., Azzam, R., Javed, S., Seneviratne, L., Zweiri, Y. "Neuromorphic Vision-Based
  Motion Segmentation With Graph Transformer Neural Network." IEEE Trans. Multimedia 27,
  385- (2025).** [peer-reviewed, primary research] (vault) — primary research on event-based
  motion segmentation, not a survey; noted only as an applications/K-axis data point encountered
  in the vault, not scored.

---

## Vault-search addendum: what the additional files (per coordinator correction) added

Reading the full `05-Neuromorphic-Background/` tree (not just `03-General-Surveys/`) and the
remaining `02-SNN-Fundamentals/01-Surveys/` PDFs added six items not previously identified from
web search alone:

1. **Confirmed Schuman et al. 2022's exact structure** via full-text keyword scan of the vault
   PDF (`s43588-021-00184-y.pdf`): 0 hits for "software," 0 for "compiler," 0 for "toolchain,"
   2 for "silicon" (used only in the sentence "all of the aforementioned large-scale neuromorphic
   computers are silicon-based"). This upgrades the I/E/F scores for this entry from
   search-abstract inference to full-text-verified absence.
2. **Confirmed Kudithipudi et al. 2025's ecosystem-gap argument** in more detail than the
   abstract alone conveyed (Fig. 4 caption, the "Cross-platform neuromorphic software" section
   text, and the explicit "no consensus" statement on hardware metrics) — this is the basis for
   the headline finding #2 above and substantially raised this survey's I/F/J scores from
   "likely absent" (pre-vault-read guess) to "Partial, and important" (post-read finding).
3. **Al Abdul Wahid, Asad & Mohammadi 2024** ("A Survey on Neuromorphic Architectures for
   Running Artificial Intelligence Algorithms," Electronics 13(15), 2963) — not found via the
   initial web searches; added as entry #30 with a genuinely useful hardware comparison table.
4. **Tayarani-Najaran & Schmuker 2021** ("Event-Based Sensing and Signal Processing in the
   Visual, Auditory, and Olfactory Domain: A Review," Frontiers in Neural Circuits) — a
   tri-modal event-sensing survey not surfaced by the Gallego-focused web search; adds
   completeness to the event-camera/encoding line (axis B) beyond vision alone.
5. **Cimarelli et al., "Hardware, Algorithms, and Applications of the Neuromorphic Vision
   Sensor: a Review"** (arXiv:2504.08588) — a 2025 event-camera hardware/algorithm/applications
   survey, more recent than Gallego et al. and worth citing alongside it for currency.
6. **Two non-survey primary papers** (Smith et al. 2024 facial-expression Loihi-vs.-edge-
   accelerator comparison; Alkendi et al. 2025 motion-segmentation paper) that are not surveys
   but materially strengthened the "such evidence exists but isn't synthesized" argument in the
   headline finding — particularly Smith et al. 2024, which is genuine physical-silicon L/J-type
   evidence sitting uncited in any general SNN survey located in this search.

None of these six additions changed the headline conclusion; if anything, items 2 and 6
sharpened it — Kudithipudi 2025 turned out to be a stronger near-miss than the abstract alone
suggested, and Smith et al. 2024 is direct evidence that physical-silicon comparison work exists
but sits outside any survey's synthesis, which is exactly the kind of "raw evidence uncollected"
situation the new survey's contribution argument should point to.

---

## Source list

**Peer-reviewed journal/venue:**
- Roy, K., Jaiswal, A., Panda, P. "Towards spike-based machine intelligence with neuromorphic
  computing." *Nature* 575, 607-617 (2019). https://doi.org/10.1038/s41586-019-1677-2
- Schuman, C. D. et al. "Opportunities for neuromorphic computing algorithms and applications."
  *Nature Computational Science* 2, 10-19 (2022). https://doi.org/10.1038/s43588-021-00184-y
- Kudithipudi, D. et al. "Neuromorphic computing at scale." *Nature* 637, 801-812 (2025).
  https://doi.org/10.1038/s41586-024-08253-8
- Pedersen, J. E. et al. "Neuromorphic intermediate representation: a unified instruction set for
  interoperable brain-inspired computing." *Nature Communications* 15, 8122 (2024).
  https://doi.org/10.1038/s41467-024-52259-9
- Yik, J. et al. "The NeuroBench framework for benchmarking neuromorphic computing algorithms and
  systems." *Nature Communications* 16, 1545 (2025). https://doi.org/10.1038/s41467-025-56739-4
- Eshraghian, J. K. et al. "Training Spiking Neural Networks Using Lessons From Deep Learning."
  *Proceedings of the IEEE* 111(9) (2023). https://doi.org/10.1109/JPROC.2023.3308088
- Davies, M. et al. "Advancing Neuromorphic Computing With Loihi: A Survey of Results and
  Outlook." *Proceedings of the IEEE* 109(5), 911-934 (2021).
  https://doi.org/10.1109/JPROC.2021.3067593
- Rathi, N. et al. "Exploring Neuromorphic Computing Based on Spiking Neural Networks: Algorithms
  to Hardware." *ACM Computing Surveys* 55(12), Art. 243 (2023). https://doi.org/10.1145/3571155
- Yamazaki, K., Vo-Ho, V.-K., Bulsara, D., Le, N. "Spiking Neural Networks and Their Applications:
  A Review." *Brain Sciences* 12(7), 863 (2022). https://doi.org/10.3390/brainsci12070863
- Ivanov, D., Chezhegov, A., Kiselev, M., Grunin, A., Larionov, D. "Neuromorphic artificial
  intelligence systems." *Frontiers in Neuroscience* 16, 959626 (2022).
  https://doi.org/10.3389/fnins.2022.959626
- Basu, A., Frenkel, C., Deng, L., Zhang, X. "Spiking Neural Network Integrated Circuits: A
  Review of Trends and Future Directions." *IEEE CICC 2022*.
  https://doi.org/10.1109/CICC53496.2022.9772783
- Nunes, J. D., Carvalho, M., Carneiro, D., Cardoso, J. S. "Spiking Neural Networks: A Survey."
  *IEEE Access* 10, 60738-60764 (2022). https://doi.org/10.1109/ACCESS.2022.3179968
- Khan, A. H. et al. "Spiking Neural Networks: A Comprehensive Survey of Training Methodologies,
  Hardware Implementations and Applications." *Artificial Intelligence Science and Engineering*
  (2025). https://doi.org/10.23919/aise.2025.000013
- Zheng, S. et al. "An Introductory Review of Spiking Neural Network and Artificial Neural
  Network." *CS & IT-CSCP 2022*, 129-145. https://doi.org/10.5121/csit.2022.121010
- Xie, H., Yang, G., Gao, W. "Toward Efficient Deep Spiking Neuron Networks: A Survey on
  Compression." Springer, ISBN 978-981-97-6125-8 (2024).
- Ferreira, P. M., Wang, S., Gao, Y., Benlarbi-Delai, A. "A comparative review of deep and
  spiking neural networks for edge AI neuromorphic circuits." *Frontiers in Neuroscience* 19,
  1676570 (2025). https://doi.org/10.3389/fnins.2025.1676570
- Gallego, G. et al. "Event-based Vision: A Survey." *IEEE TPAMI* 44(1), 154-180 (2022; arXiv
  2019). https://doi.org/10.1109/TPAMI.2020.3008413
- Gebregiorgis, A. et al. "Spike-based neuromorphic computing: An overview from bio-inspiration
  to hardware architectures and learning mechanisms." *Microprocessors and Microsystems* (2025).
  https://doi.org/10.1016/j.micpro.2025.105240
- Bouvier, M. et al. "Spiking neural networks hardware implementations and challenges: A survey."
  *ACM JETC* 15(2), 1-35 (2019).
- Shrestha, A. et al. "A Survey on Neuromorphic Computing: Models and Hardware." *IEEE Circuits
  and Systems Magazine* 22(2), 6-35 (2022). https://doi.org/10.1109/MCAS.2022.3166331
- "A New Era in Computing: A Review of Neuromorphic Computing Chip Architecture and
  Applications." *Chips* (MDPI) 5(1), 3 (2026). https://doi.org/10.3390/chips5010003
- "Brain-inspired computing systems: a systematic literature review." *European Physical Journal
  B* (2024). https://doi.org/10.1140/epjb/s10051-024-00703-6
- "A Practical Tutorial on Spiking Neural Networks: Comprehensive Review, Models, Experiments,
  Software Tools, and Implementation Guidelines." *MDPI* (2025).
  https://doi.org/10.3390/(see mdpi.com/2673-4117/6/11/304)
- Al Abdul Wahid, S., Asad, A., Mohammadi, F. "A Survey on Neuromorphic Architectures for
  Running Artificial Intelligence Algorithms." *Electronics* 13(15), 2963 (2024).
  https://doi.org/10.3390/electronics13152963
- Tayarani-Najaran, M.-H., Schmuker, M. "Event-Based Sensing and Signal Processing in the
  Visual, Auditory, and Olfactory Domain: A Review." *Frontiers in Neural Circuits* 15, 610446
  (2021). https://doi.org/10.3389/fncir.2021.610446
- Alkendi, Y. et al. "Neuromorphic Vision-Based Motion Segmentation With Graph Transformer
  Neural Network." *IEEE Trans. Multimedia* 27, 385- (2025).

**Preprint (arXiv, not yet or not formally peer-reviewed at time of writing):**
- Schuman, C. D. et al. "A Survey of Neuromorphic Computing and Neural Networks in Hardware."
  arXiv:1705.06963 (2017).
- Deng, S. et al. "Edge Intelligence with Spiking Neural Networks." arXiv:2507.14069 (2025).
- Huynh, P. K. et al. "Implementing Spiking Neural Networks on Neuromorphic Architectures: A
  Review." arXiv:2202.08897 (2022).
- Manna, D. L., Vicente, A., Kirkland, P., Bihl, T., Di Caterina, G. "Frameworks for SNNs: a
  Review of Data Science-oriented Software and an Expansion of SpykeTorch." arXiv:2302.07624
  (2023).
- "Toward Large-scale Spiking Neural Networks" (Spiking Transformers survey). arXiv:2409.02111
  (2024).
- Cimarelli, C. et al. "Hardware, Algorithms, and Applications of the Neuromorphic Vision
  Sensor: a Review." arXiv:2504.08588 (2025).
- Smith, H., Seekings, J., Mohammadi, M., Zand, R. "Realtime Facial Expression Recognition:
  Neuromorphic Hardware vs. Edge AI Accelerators." arXiv:2403.08792 (2024). [primary research,
  not a survey; cited for its physical-silicon evidence]
- "Towards Neuromorphic Computing on Edge: A Survey on Efficient Techniques for Spiking Neural
  Networks." (venue/authors unconfirmed — extracted text truncates the byline; vault PDF filename
  `1_Towards_Neuromorphic_Computi.pdf`.)

**Vault-note-only (not independently verified against primary text — flagged `†` in table):**
- "A Four-Stage Structural Evolution Framework for SNNs: A Review and Perspective from Binary
  ANN to Event-Driven Models." *Neural Processing Letters* 58:14 (2026).
  https://link.springer.com/article/10.1007/s11063-025-11832-z
- Luu, N. T., Luu, D. T., Nam, P. N., Thang, T. C. "A Survey on Spiking Neural Network Foundation
  and Recent Progress." IEEE (2026), document 11488853.
- Caviglia, A. et al. "NeuroTrain: Surveying Local Learning Rules for SNNs with an Open
  Benchmarking Framework." arXiv:2605.15058 (2026).
- "Benchmarking spiking neural networks across sensing modalities on edge devices."
  arXiv:2609.00026 (2026).
- Farsa, E. Z. et al. "GPU and RISC-V acceleration for neuromorphic computing based on SNNs:
  taxonomy, comparison, and open challenges." *Neuromorphic Computing and Engineering*, accepted
  manuscript (2026-09-09). https://iopscience.iop.org/article/10.1088/2634-4386/aea4eb

**Repository/tooling state referenced (not surveys, cited only for context on E-axis framework
comparisons):**
- Open Neuromorphic community pages, "SNN Framework Benchmarks" and "SNN Frameworks" listings
  (open-neuromorphic.org). [community commentary / repository state]
- `neuromorphs/NIR` GitHub repository (github.com/neuromorphs/NIR). [repository state]
- NeuroBench project site and documentation (neurobench.ai, neurobench.readthedocs.io).
  [official documentation]
