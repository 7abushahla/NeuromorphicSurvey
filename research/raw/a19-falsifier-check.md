# A19 — Falsifier Check: "Temporal Flexibility in SNNs" (ICLR 2025) vs. the rate-coding-abandonment claim

**Task:** adversarially test whether Du, Wu, Deng & Gu, "Temporal Flexibility in Spiking Neural
Networks: Towards Generalization Across Time Steps and Deployment Friendliness" (arXiv:2503.17394,
ICLR 2025; OpenReview id `9HsfTgflT7`; also indexed at
`https://proceedings.iclr.cc/paper_files/paper/2025/file/960842d58e6608407137f542a7b3f3be-Paper-Conference.pdf`)
breaks the claim: *"Every confirmed instance of a paper that both (a) proposes a new conversion or
low-timestep SNN method AND (b) deploys it to physical neuromorphic silicon, abandons rate coding
for a platform-native code (TTFS, graded sigma-delta, population coding)."*

Sources read in full: arXiv HTML (`arxiv.org/html/2503.17394v1`), the ICLR camera-ready PDF (fetched
and parsed to text locally, 20 pages incl. appendix), the paper's GitHub repo
(`github.com/brain-intelligence-lab/temporal_flexibility_in_SNN`), and the OpenReview /
ICLR-proceedings abstract pages. All quotations below are verbatim from the ICLR PDF unless noted.

---

## 1. What exactly does it propose?

The paper's own framing is explicit and appears repeatedly:

> "SNNs trained with current direct training approaches are constrained to a specific time step.
> This 'temporal inflexibility' 1) hinders SNNs' deployment on time-step-free fully event-driven
> chips and 2) prevents energy-performance balance based on dynamic inference time steps... We then
> introduce Mixed Time-step Training (MTT), a novel method that improves the temporal flexibility of
> SNNs..."

Section 2 draws a hard line between "Direct Training" and "ANN-SNN Conversion" as two separate,
pre-existing families, and places MTT in the direct-training family:

> "ANN-SNN Conversion. ANN-SNN conversion uses SNN firing rates to approximate the activation of
> ANN... Although SNNs obtained by conversion show some temporal flexibility for large time steps
> (e.g., above 100), they do not exhibit temporal flexibility for ultra-low time steps. Additionally,
> the conversion method is unable to handle DVS datasets and can only procure SNNs with IF neurons."

MTT is trained by surrogate-gradient BPTT/STBP (standard direct-training machinery), with the single
methodological novelty being that each training iteration samples *random* time-step values per
network stage and back-propagates the summed loss across several such "partitioned SNNs" that share
one set of weights (Fig. 1). After training, per the abstract of the OpenReview / earlier version:

> "Following training, the TFSNN can be simplified to an SNN operating at any chosen fixed time step,
> eliminating the need for fine-tuning."

So: **this is a direct-training regularization/generalization technique, not a conversion method.**
It is not "low-timestep" in the sense of the established cases either — its central claim is
*timestep-agnosticism* (one weight set, many T), not driving T down to 1–4 via a new
conversion/quantization mechanism. It does report competitive accuracy at T=1/T=2 versus
low-latency conversion baselines, but only as a downstream consequence, evaluated purely on GPU,
never on the physical chip (see §3, §5 below). The registry's "both" population tag (conversion-or-
low-timestep method + physical-silicon deployment) is defensible only if "low-timestep SNN method"
is read very loosely; on the paper's own self-classification it sits outside the conversion literature
entirely and its low-T results are a training-time by-product, not what gets deployed to silicon.

---

## 2. What neural code does it actually use?

**The string "rate coding" (or "rate-coded") does not appear anywhere in the 20-page ICLR PDF.** I
grepped the full extracted text (all sections, all appendices, all 60+ references) for "rate cod",
"Poisson", "population cod", "TTFS", "sigma-delta" — zero hits for all of them. The paper never
characterizes its own encoding scheme with any of the terms the survey's taxonomy uses.

What it does say about input handling differs sharply between static-image and DVS/event experiments:

- **Static images (CIFAR/ImageNet, GPU only, never on chip):**
  > "On static datasets, inputs are repeated for T times as previous works where T is the inference
  > time step."
  This is the conventional "repeat/direct" encoding used throughout the direct-training SNN
  literature (same real-valued input replayed at every timestep, not a Poisson/rate-coded spike
  train). It is arguably closer to "rate coding" than the DVS case, but it is never run on physical
  silicon.

- **NMNIST on the physical Speck2e chip (the only hardware experiment):**
  Input is native DVS event data. Section 3.3 states the general design intent for event platforms:
  > "the industry uses time-stepped simulation to approximate event-driven behavior and directly
  > deploys weights trained in the time-stepped framework onto fully event-driven hardware... We use
  > IF neurons with Vth = 1 for all event-based experiments because most of the existing fully
  > event-driven neuromorphic chips mainly support IF for its suitability to asynchronous scenarios."
  On the chip itself there is no "timestep" and no windowed spike-count readout at all — Speck is
  asynchronous, event-by-event. The network is IF neurons integrating individual DVS spikes and
  firing individual output spikes, i.e., the chip's own default asynchronous spiking mode. Calling
  this "rate coding" describes neither the input (native DVS events, not a rate/Poisson code imposed
  on a static image) nor the readout (the paper never describes a rate-decoding window on-chip; its
  own fidelity metric, spike difference, compares raw spike trains, not spike counts/rates — see §3).

**Verdict on Q2: the registry's "rate coding, not abandoned" flag is not supported by the paper's own
language and is a poor description of what runs on Speck2e.** The one thing that *could* loosely be
called rate-like ("inputs repeated for T times" on static images) is confined to GPU simulation and
never touches silicon; what actually runs on silicon is native asynchronous event-driven IF spiking
with no stated coding scheme at all, closer to "the platform's own default mode" than to any of the
three named platform-native alternatives (TTFS / sigma-delta / population) — but also not "rate
coding" in the sense the survey's other three cases mean it (fixed-window spike-count integration).

---

## 3. What was actually measured on silicon?

This is the load-bearing question. The full "Event-driven Friendliness" results paragraph, quoted in
full:

> "To verify the event-driven friendliness of our TFSNN, we employed Synsense Speck2e as the testing
> platform. The Speck series chips are among the most advanced real-time, fully event-driven
> neuromorphic chips available today, boasting extremely low power consumption and latency (Richter
> et al., 2023; Li et al., 2023b). However, due to their limited size, Speck cannot support the
> mainstream backbones used for DVS datasets in recent studies (e.g. VGGSNN). Therefore, we developed
> an easy-to-use parallelized event-driven chip software simulator and aligned it with Speck on small
> datasets. To quantify the mismatch between a given output and the real hardware output, we define
> spike difference (SD) as..."
>
> "Since MTT-trained models have improved temporal flexibility, they are more suitable for deployment
> on fully event-driven chips as we claimed. To prove this, we deploy and test our MTT-trained models
> on event-driven neuromorphic systems. We first train two networks on NMNIST using SDT and MTT
> respectively, and then deploy them directly on Speck2e Devkit (Richter et al., 2023). We then
> develop an easy-to-use software simulator for event-driven chips to test MTT on large-scale datasets
> and models. Experiments show that our simulator accurately mimics the chip behavior. On the NMNIST
> dataset, the spike difference (SD, see Eq. 16) between the simulator's output and the actual on-chip
> output is only 3.92%, comparable to the 2.81% SD between two identical model tests on the same chip,
> much lower than the 28.77% SD between time-step-based inference and the on-chip output. Our
> supportive results in Tab. 5 on various datasets and backbones strongly demonstrate the event-driven
> friendliness of MTT-trained models. In this section, our models show slightly lower PyTorch test
> accuracy compared to models with similar backbones because they are bias-free to be deployed on
> chips. Fully event-driven chips like Speck eliminate time-step-wise operations, including clocked
> bias addition, making them extremely energy-efficient and ideal for always-on scenarios."

Key facts:

- The **only quantity actually measured on the physical Speck2e chip is spike difference (SD)** — a
  fidelity/consistency metric comparing the chip's raw output spike train against (a) the software
  simulator's output and (b) another run of the identical model on the same chip. It answers "does
  the chip reproduce what the simulator predicts," not "how fast/efficient is the chip."
- Every claim about power and latency ("extremely low power consumption and latency," "extremely
  energy-efficient") is a **citation to prior Speck hardware papers** (Richter et al. 2023; Li et al.
  2023b), not a number this paper measured itself. I searched the entire PDF for "mW", "mJ", "ms",
  "µJ", "FPS", "power" and "latency" in numeric/results context — the only occurrences of "power" and
  "latency" in the whole document are the two qualitative sentences quoted above; there is no
  measured wattage, energy-per-inference, or on-chip inference-time figure anywhere in the paper,
  appendix included.
- Table 5 (the results table referenced) reports SD percentages across datasets/backbones, not
  latency or energy.

**Classification: this is E2 (physical silicon, fidelity/accuracy check only), not E1.** No latency
or energy was measured on the physical chip. The registry's evidence class assignment (implicitly
E1, since it is being weighed against E1 comparison cases Quartz/Brehove/Adaptive Fission) is
incorrect on the paper's own reported results.

---

## 4. Does the deployed network use reset by subtraction?

Yes, explicitly, and it is stated as a deliberate hardware-compatibility choice, quoted in full from
Appendix A.3 ("Training Details for Event-driven Experiments"):

> "We carefully learned Synsense's documentation. To obtain Spiking Neural Networks (SNNs) more
> suitable for deployment on asynchronous chips, we utilized a soft reset mechanism and multistep-IF
> neurons during training (neurons emit mem/Vth spikes per event to simulate multiple event
> transmissions and generations). Note that, however, the neurons realistically employed on our
> simulator and Speck chip are still IF neurons."

Earlier, the reset function is defined generically (Sec. 3.1):

> "R(·) is reset function... For hard reset R(u) = 0 and for soft reset R(u) = u − Vth."

"Soft reset" = R(u) = u − Vth is literally reset-by-subtraction. So the chip-deployed network uses
reset-by-subtraction IF neurons, consistent with Speck's native `return_to_zero=False` mode.

On toolchain: the paper does **not** name Sinabs or samna anywhere in the text (I confirmed zero
occurrences of both strings). It only names:

> "All trainings for event-driven platforms in this paper are conducted by Speck deployment toolkit-
> Tonic... For experiments on event-driven platforms, we follow Speck handbook and use the default
> single exponential SG (Shrestha and Orchard, 2018) in Tonic (Lenz et al., 2021)."

Tonic (Lenz et al. 2021) is an event-dataset/transform library, not the on-chip deployment SDK.
Deployment itself is referred to only generically as "Speck2e Devkit (Richter et al., 2023)" and
"Synsense's documentation." The GitHub repo (`brain-intelligence-lab/temporal_flexibility_in_SNN`,
6 stars, MIT license) was checked directly — as of this check its README states "Code repo in process
of organizing" and contains no deployment script referencing Sinabs or samna, so the exact toolchain
used to flash the Speck2e cannot be confirmed beyond "SynSense's own documented workflow" (which in
practice is Sinabs+samna for this device family, but the paper does not say so itself).

---

## 5. Per-layer horizons or a single global T?

**Single global T, with heterogeneous per-stage T used only as a training-time augmentation, not as
the deployed architecture.** MTT's mechanism during *training* samples a distinct random Ti for each
of G network stages per iteration (Fig. 1: "each assigning a set of random time steps to different
stages... These configurations create s partitioned SNNs with distinct temporal structures, all
sharing the same weights"). But the deployment story is explicitly about collapsing this back to one
number:

> "the TFSNN can be simplified to an SNN operating at any chosen fixed time step, eliminating the
> need for fine-tuning."

And for the one physical-silicon experiment (Speck2e/NMNIST), timesteps do not exist on the device at
all — Speck is asynchronous, so there is no "T" to be heterogeneous or homogeneous across layers in
deployment; the per-stage-T mechanism is purely a GPU-training-time trick to produce weights that
generalize. This is a fundamentally different axis from "block-wise heterogeneous (L,T) deployment"
(the kind of thing QCFS++/ActMPQ in the thesis's own vocabulary address) — MTT never deploys
different, persistent per-layer horizons to hardware; it deploys one weight set that is agnostic to
whatever single global T (or no T) the target platform uses.

---

## 6. THE VERDICT

**(b) — misclassified in the registry; the correct classification leaves the claim intact.** This is
not a case of "genuinely breaks the claim, weaken it" nor primarily "needs added scope language" —
the paper simply does not clear the bar the established three cases (Quartz, Brehove et al.,
Adaptive Fission) all clear, on two independent grounds:

1. **Wrong evidence class.** The claim's force (and the reason E1 cases are the interesting ones) is
   that the paper *measured* efficiency (latency/energy) on silicon and *still* found it necessary to
   abandon rate coding. This paper measured only spike-train fidelity (SD = 3.92%) on silicon — a
   sanity check that the chip matches the simulator, not an efficiency result at all. It belongs in
   the E2 bucket (physical silicon, accuracy/fidelity only), the same bucket the survey already
   treats as weaker/non-decisive evidence elsewhere. Compared on a like-for-like basis (E1 vs. E1),
   there is no conflict with Quartz/Brehove/Adaptive Fission at all.

2. **Wrong population / wrong encoding tag.** MTT is a direct-training temporal-generalization
   technique, explicitly distinguished by the authors from ANN-SNN conversion; its low-T results are
   GPU-only and never touch the chip. And the term "rate coding" appears nowhere in the paper — the
   one physical-hardware experiment runs native, un-windowed, asynchronous DVS events through
   reset-by-subtraction IF neurons, which is arguably closer to "the platform's own default event-driven
   mode" than to rate coding as the taxonomy's fourth (implicit) category. Tagging this entry "rate
   coding, not abandoned" overstates what the paper describes about its own encoding.

Recommended registry fix, not a claim rewrite: reclassify this entry as **direct-training /
temporal-generalization technique, E2 (fidelity-only), encoding unstated by authors (native
asynchronous IF spiking on DVS events, not rate coding)**. With that correction it drops out of the
comparison set the claim is about, and the claim as stated survives untouched. If the survey wants to
preempt this exact objection from a reviewer, one defensive sentence naming this paper explicitly as
an examined-and-rejected candidate (with the E2/non-conversion reasons above) would be stronger than
silence, per the standing instruction to lead with counterexamples rather than bury them.

---

## Search for other papers fitting the same profile (new low-T/conversion method + physical silicon + kept rate coding)

Multiple query phrasings were run via Exa deep search:

- "low-latency ANN-SNN conversion method deployed on Loihi Loihi2 Speck physical chip rate coding
  measured latency energy 2024 2025"
- "new SNN conversion method deployed on Loihi rate coding firing rate physical chip measured energy
  latency 2024 2025 2026"
- "rate-coded spiking neural network deployed Akida SpiNNaker Tianjic BrainScaleS chip measured
  latency energy consumption ANN-SNN conversion 2025"

Findings:

- **"Sigma-Delta Neural Network Conversion on Loihi 2"** (arXiv:2505.06417, also the source for a
  later v2 dated 2026-07-01 covering YOLO-KP + PilotNet + a Navy field trial) is the same
  sigma-delta/Loihi 2 work already counted as the established "Brehove et al. 2026" supporting case —
  not a new counterexample. Its own introduction explicitly frames itself as a rate-coding
  *departure*: "Attempts to convert trained ANNs to SNNs have largely used the rate of spikes to
  represent activation values... This approach requires many timesteps per input... [we use] graded
  spikes." This reinforces the claim rather than threatening it.

- **"Differential Coding for Training-Free ANN-to-SNN Conversion"** (Huang et al., PMLR v267,
  2025) is a *new* conversion method that explicitly abandons rate coding for a differential
  ("delta") code, framed the same way as the claim predicts:
  > "many conversion methods are based on rate coding, which requires numerous spikes and longer
  > time-steps... This article introduces differential coding for ANN-SNN conversion, a novel coding
  > scheme that reduces spike counts... by transmitting changes in rate information rather than rates
  > directly." No evidence found (in the fetched abstract/highlights) that this method was deployed to
  physical silicon — appears to be simulation-only. Not a counterexample; consistent with the claim,
  and not eligible for the "both" population regardless.

- **"Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 Neuromorphic Platform"**
  (arXiv:2507.23562, 2025) is the most interesting near-miss found. It explicitly states:
  > "we build upon the model architecture proposed in [17], used SnnTorch for training the rate-coded
  > SNN models... Input states are converted into spike trains using rate coding and propagated
  > through the network over a fixed simulation window... The spike-based representation is generated
  > using poisson-distributed spike trains sampled over T discrete timesteps."
  It quantizes to 8-bit and deploys to **physical SpiNNaker2** hardware, reporting a real E1-grade
  Table III with measured Power [W], Energy [J], and Duration [s] against a GTX 1650 GPU baseline
  (e.g., 0.006 J vs. 0.145 J for CartPole-v0). This is genuine rate coding, genuine physical silicon,
  genuine measured energy/latency. **However**, it does not propose a new conversion or low-timestep
  algorithm — it is a reinforcement-learning application paper doing hardware-aware quantization
  fine-tuning of an existing architecture ("[17]") for Q-learning control tasks; timestep reduction
  and encoding design are not its contribution. On a strict reading of "proposes a new conversion or
  low-timestep SNN method" it falls outside the claim's population (methodology, not algorithm), but
  it is close enough that the survey author should be aware of it — a reviewer could plausibly argue
  it counts, in which case it would be a genuine E1 counterexample and the claim would need explicit
  scoping to exclude RL/control-task quantization papers that reuse pre-existing rate-coded
  architectures rather than proposing new conversion/low-latency algorithms.

- **BrainChip Akida deployment papers** ("Enabling Efficient Processing of SNNs with On-Chip Learning
  on Commodity Neuromorphic Processors," arXiv:2504.00957; and the IIoT/Akida-vs-Orin energy study,
  ACM DOI 10.1145/3770501.3770529) both report real measured latency/energy on physical Akida chips
  via BrainChip's standard **CNN2SNN/MetaTF** ANN-to-SNN conversion toolkit. Neither paper proposes a
  *new* conversion algorithm — both reuse BrainChip's existing off-the-shelf converter as a black box
  inside a systems/deployment-methodology or comparative-benchmarking study. Same disposition as the
  SpiNNaker2 RL paper: real E1 physical measurements with (likely) rate/count-based Akida-native
  coding, but not a "new conversion or low-timestep method" contribution, so outside the claim's
  population on the "proposes a new method" prong.

**Summary for the author:** no clean second counterexample was found. The SpiNNaker2 RL paper and the
two Akida deployment papers are worth having on file as boundary cases — they show that E1-grade,
rate-coded, physical-silicon SNN deployments do exist in the 2024-2026 literature — but all three are
disqualified from the claim's population because none of them proposes a new conversion or
low-timestep algorithm; they apply existing conversion tooling (CNN2SNN/MetaTF, or a cited prior
architecture) to a downstream application or systems-engineering problem. If the claim's population
criterion is ever loosened to "any conversion, new or reused" the claim would need re-auditing against
these three.

---

## Source list

1. Du, K., Wu, Y., Deng, S., Gu, S. "Temporal Flexibility in Spiking Neural Networks: Towards
   Generalization Across Time Steps and Deployment Friendliness." ICLR 2025.
   arXiv:2503.17394 — https://arxiv.org/abs/2503.17394 (academic, primary source; PDF fetched and
   parsed in full, 20 pages incl. appendix).
2. ICLR 2025 camera-ready PDF —
   https://proceedings.iclr.cc/paper_files/paper/2025/file/960842d58e6608407137f542a7b3f3be-Paper-Conference.pdf
   (academic, primary source, identical content to arXiv v1 used for page-accurate quoting).
3. OpenReview forum — https://openreview.net/forum?id=9HsfTgflT7 (academic, TL;DR and abstract).
4. GitHub repo — https://github.com/brain-intelligence-lab/temporal_flexibility_in_SNN (non-academic,
   code/README; confirms no Sinabs/samna reference, repo "in process of organizing").
5. ICLR virtual poster page — https://www.iclr.cc/virtual/2025/poster/30705 (non-academic, conference
   listing, abstract only).
6. Brehove et al., "Sigma-Delta Neural Network Conversion on Loihi 2," arXiv:2505.06417 —
   https://arxiv.org/abs/2505.06417 / v2 https://arxiv.org/html/2505.06417v2 (academic; already an
   established survey case, re-confirmed here, not a new counterexample).
7. Huang et al., "Differential Coding for Training-Free ANN-to-SNN Conversion," PMLR v267 —
   https://proceedings.mlr.press/v267/huang25i.html (academic; simulation-only, not deployed to
   silicon per available abstract).
8. "Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 Neuromorphic Platform,"
   arXiv:2507.23562 — https://arxiv.org/html/2507.23562v1 (academic; near-miss candidate, logged
   above).
9. "Enabling Efficient Processing of Spiking Neural Networks with On-Chip Learning on Commodity
   Neuromorphic Processors for Edge AI Systems," arXiv:2504.00957 —
   https://ar5iv.labs.arxiv.org/html/2504.00957 (academic; near-miss candidate, BrainChip
   CNN2SNN/MetaTF reuse, logged above).
10. "Towards an Energy-Efficient and Sustainable IIoT using Embedded Neuromorphic AI," ACM,
    DOI 10.1145/3770501.3770529 (academic; near-miss candidate, BrainChip Akida vs. NVIDIA Orin
    energy comparison, logged above).
11. "Fast Switching Serial and Parallel Paradigms of SNN Inference on Multi-core Heterogeneous
    Neuromorphic Platform SpiNNaker2," arXiv:2406.17049 (academic; reviewed and excluded — a
    compiler/mapping paper, not a conversion/low-timestep method).
