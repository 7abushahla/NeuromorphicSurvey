# BrainChip Akida, examined critically

Research notes for neuromorphic deployment survey. Evidence classes: **E1** physical
silicon, latency+energy measured. **E2** physical silicon, accuracy/power only (no
rigorous latency/energy benchmark). **E3** documented deployment path, no published
run of this model class. **E4** hardware model / architectural characterization
(datasheet, chip paper without an application benchmark). **E5** software simulation
only.

Source labels used throughout: **[peer-reviewed]**, **[preprint]**,
**[official documentation]**, **[repository state]** (the author's own hands-on repo,
treated as primary/ground-truth evidence of toolchain behavior), **[vendor material]**,
**[community commentary]** (forum posts, blogs, investor writeups — explicitly labeled,
never conflated with independently verified claims).

---

## 0. Bottom line up front

Akida is **not** a multi-timestep rate-coded IF/LIF accelerator in the sense the
ANN-to-SNN conversion literature (Diehl & Cook, Rueckauer, QCFS) assumes. The
converted-CNN deployment path — the one essentially all published Akida
results use — collapses to a **single hardware pass over quantized, integer-only
activations**, where a "spike"/"event" is a nonzero (or above-threshold) quantized
activation value, and the neuron's firing threshold is algebraically folded from the
quantization step size and (optionally) a batch-norm scale/shift. There is no
membrane potential that accumulates over T timesteps in the sense of a
software SNN simulator loop; there is no user-specified simulation horizon T for a
converted CNN; CNN2SNN documentation explicitly states scaling and quantized-activation
math "are never performed during inference" as separate float ops — they are folded
into the fire threshold at conversion time.

However, this is not simply "fake neuromorphic branding." Akida's own intellectual
lineage is genuinely from the **rank order coding (ROC)** literature (Thorpe,
Spikenet Technology, acquired by BrainChip in 2016), which is a real, peer-reviewed,
temporal neural code — just a *different* one from the rate code the conversion
literature assumes. ROC is about firing *order*, and a "single feedforward pass
where at most one spike per neuron matters" is the ROC-consistent behavior, not a
degenerate/fake version of rate coding. The honest framing is: **Akida computes
under a different neural code (rank/order-based, single-pass, integer-arithmetic)
from the one the ReLU→IF rate-coding conversion literature assumes**, so the
ReLU-to-IF correspondence that QCFS-style conversion work relies on does not
transfer to Akida's own CNN2SNN path, which is a materially different — and, per the
toolchain's own code, essentially QAT-with-threshold-folding — conversion.

BrainChip's own newest architecture, TENN, is a further departure: it is a
polynomial-kernel state-space/convolutional model (Chebyshev/Legendre expansions,
closely related to S4/HiPPO/LMU-style SSMs), not a spiking network, that BrainChip
maps onto Akida 2's event-based execution substrate. Even BrainChip's own TENNs
authors, in an academic paper, describe converting TENN to "a spiking system" as
*future work*, i.e., not yet true of the shipping architecture.

---

## 1. What Akida actually is

### 1.1 Chip / IP family overview

| Product | Status | Process | Peak perf / power | Notes |
|---|---|---|---|---|
| **AKD1000** (NSoC) | Shipping since Jan 2022 | 28 nm CMOS digital logic | up to 300 MHz clock; ~1.5 TOPS; "up to 10x" power reduction claimed by BrainChip | Arm Cortex-M4 host CPU on-die, 80 NPUs / 20 Neural Processing Cores (accounts differ — product briefs describe 20 "Neural Processing Cores" while a Linley 2019 slide says "80 NPUs"), 8 MB on-chip SRAM, PCIe 2.1 x2, USB 3.0, I3C/I2S/UART/JTAG. **[vendor material]** — BrainChip, AKD1000 SoC Product Brief V2.3, https://brainchip.com/wp-content/uploads/2025/08/Akida-AKD1000-SoC-Product-Brief-V2.3-Aug.25.pdf |
| **AKD1500** | Commercial availability / production shipments began June 30, 2026 | GlobalFoundries 22 nm FD-SOI | 5–400 MHz clock; up to 800 effective GOPS at <1 mW/GOP; <300 mW PCIe mode, <200 mW serial mode; 1 MB on-chip SRAM | PCIe Gen2 endpoint + SPI (S/D/Q/O) for MCU hosts; "essentially a modified version of the Akida 1000 core" per a shareholder-forum poster (**[community commentary]**, unverified against BrainChip engineering docs). **[vendor material]** — BrainChip, AKD1500 Product Brief V2.4, https://brainchip.com/wp-content/uploads/2025/11/AKD1500-Product-Brief-V2.4-Oct.25.pdf ; BrainChip press release, "BrainChip Announces Commercial Availability and Production Shipments of AKD1500," June 30 2026, https://brainchip.com/press/brainchip-announces-commercial-availability-and-production-shipments-of-akd1500-neuromorphic-processors/ |
| **Akida 2.0 IP** (basis for AKD2000) | IP available for licensing; reference silicon (AKD2000) not yet independently confirmed shipping in the sources gathered here | Process-agnostic IP; scalable 1–128 nodes, 4 NPUs/node, 128 MACs/node | 2 nodes @ 1 GHz = 1 TOPS; 256 nodes @ 1 GHz = 131 TOPS | Adds ViT/attention support, TENN support, 8/4/1-bit precision, skip connections. **[vendor material]** — BrainChip, Akida 2 IP Product Brief V2.0, https://brainchip.com/wp-content/uploads/2025/04/Akida-2-IP-Product-Brief-V2.0-1.pdf |
| **Akida Pico** | Announced 2024 (no ASX announcement — reported first via third-party blogs, per shareholder-forum commentary) | 22 nm, 0.18 mm² die | 1–400 MHz; µW–mW active power | Single NPU core, standalone (no host CPU required), 50K-word local RAM, 8-bit weights/activations, targeted at KWS / vital-signs / always-on wake tasks; runs TENN models specifically. **[vendor material]** — BrainChip, Akida Pico Brochure, https://brainchip.com/wp-content/uploads/2024/10/BC_Akida-Pico-Brochure.pdf |

Notes on internal consistency of BrainChip's own numbers: different product briefs
describe the AKD1000 fabric as "20 Neural Processing Cores" (2025 product brief) vs.
"80 NPUs" (2019 Linley presentation) vs. "1.2 million neurons / 10 billion synapses"
(2018 architecture announcement). These are not necessarily contradictory (NPU vs.
neuron vs. synapse are different units of count) but BrainChip's public material does
not reconcile them in one place. **[vendor material]** — BrainChip, "Introducing
Akida" Linley presentation, 2019,
https://brainchip.com/wp-content/uploads/2019/10/BrainChip-Linley-Akida-Presentation_v5.pdf;
BrainChip Investor Portal, Akida NSoC architecture announcement, Sept. 2018,
https://investor.brainchip.com/brainchip-announces-the-akida-architecture-a-neuromorphic-system-on-chip/

### 1.2 Is there a membrane potential? Is there a temporal dimension?

Yes and no, depending on which layer of the stack is being asked about, and this is
the crux of the whole entry (Section 3).

- At the **architectural/patent level**, Akida's neuron does integrate weighted
  inputs into an accumulator and fires when a threshold is exceeded — this is
  described, consistently, across BrainChip's technical briefs, as: "Synapses store
  weight values and are connected to neurons, which integrate the weight values when
  they're released by an incoming event... Power is consumed only when inputs to a
  neuron exceed the predetermined threshold." **[vendor material]** — BrainChip,
  "What Is the Akida Event Domain Neural Processor?",
  https://brainchip.com/case-studies/what-is-the-akida-event-domain-neural-processor/
- At the **converted-CNN deployment level** (the path essentially all published
  Akida results use), independent analysis states plainly: "the AKD1000 does not
  support leaky neurons... the implementation suggest[s] that the converted spiking
  model reduces the computation to a single time step." **[preprint]** — Lunghi,
  Silvestrini, Dold, Meoni, Hadjiivanov, Izzo, "Energy efficiency analysis of
  Spiking Neural Networks for space applications," arXiv:2505.11418,
  https://arxiv.org/abs/2505.11418
- Directly confirming this from an independent robotics group that trained and
  deployed on real AKD1000 hardware: "Quantized ReLUs are used because the Akida
  chip **squashes the rate-code approximation of the ReLU into one time step**,
  where it is then represented by a step-wise quantized ReLU... Akida uses an
  equivalent representation of an SNN using a step-wise quantized ReLU, which can be
  trained using quantization-aware training and **allows for processing in a single
  time step**." **[peer-reviewed / preprint]** — Ziegler, Vetter, Gossard, Tebbe,
  Otte, Zell, "Detection of Fast-Moving Objects with Neuromorphic Hardware,"
  arXiv:2403.10677 (v1: 15 Mar 2024; v2: 16 Sep 2024),
  https://arxiv.org/abs/2403.10677, https://arxiv.org/html/2403.10677v2
- This is corroborated at the source-code level (Section 3.3 below): the author's
  own copy of the `cnn2snn` 2.19.1 toolkit shows the Akida-1.0 output/threshold path
  is `y = x / act_step`, with the fire threshold adjusted by a rounded half-step
  offset — an algebraic fold of the quantization step into a static comparator, not
  an iterative accumulate-over-T loop. **[repository state]** — author's local copy,
  `cnn2snn-2.19.1/cnn2snn/quantizeml/outputs.py`, function `set_output_v1_variables`.

So: there **is** an accumulator/threshold structure at the circuit level (this is
real, and matches classical IF-neuron circuit design), but for the standard
converted-CNN workflow there is **no exposed, user-controlled multi-timestep
simulation horizon T**, and no rate-coded spike *count* being accumulated across
timesteps the way a QCFS-converted SNN or a SpikingJelly `MultiStepIFNode` would do.

---

## 2. Platform record (for the hardware comparison table)

| Field | Value | Evidence |
|---|---|---|
| **Time model** | No user-exposed multi-timestep simulation horizon for the standard converted-CNN path; execution is a single feedforward pass through the mapped network. Some layer types (`BufferTempConv`, `DepthwiseBufferTempConv`, TENN blocks) do carry an internal temporal buffer/recurrent state for sequence data, which is a different (non-rate-coding) notion of "time" — see §6. | [preprint] arXiv:2505.11418; [preprint] arXiv:2403.10677; [official documentation] doc.brainchipinc.com/user_guide/akida.html |
| **Neuron model** | Integrate-and-(single-)fire, no leak, no exposed decay constant on the standard path ("Akida does not support LIF neurons"). Circuit-level description is integrate-to-threshold, fire, generate one output event; the accumulate-and-compare is algebraically equivalent to a quantized/stepped ReLU for the converted-CNN case. | [community commentary, but code-consistent] Open Neuromorphic, "A Look at Akida," https://open-neuromorphic.org/neuromorphic-computing/hardware/akida-brainchip/ ; [repository state] author's cnn2snn source, `activations.py`/`outputs.py` |
| **Reset semantics** | Not reset-by-subtraction in the classical rate-coding sense (no residual membrane potential is carried to a next timestep on the standard path, because there is effectively one step). The threshold itself is offset by half the quantization step ("increase the precision... by increasing the threshold") rather than the membrane being reset-by-subtraction across T. | [repository state] `outputs.py`, `set_output_v1_variables` |
| **Spike payload** | Not necessarily binary. BrainChip's own material: "the burst can have a value that indicates neural behavior" — i.e., Akida events can carry a magnitude (this is consistent with quantized-activation values being propagated as "events," not just binary 0/1 spikes), except at the FullyConnected Edge-Learning layer, which is defined as strictly 1-bit in/1-bit weight. | [vendor material] brainchip.com "What Is the Akida..."; [official documentation] doc.brainchipinc.com/user_guide/akida.html |
| **Weight precision** | 1, 2, 4, or 8-bit, depending on layer type and Akida version. Akida 1.0: InputConv = 8-bit weights; Conv/Dense = 1/2/4-bit weights. Akida 2.0 IP: "8,4,1-bit arithmetic precision," Akida Pico: 8-bit only. FullyConnected Edge-Learning layer: 1-bit weights only (mandatory). | [official documentation] doc.brainchipinc.com/user_guide/akida.html ; [repository state] author's README/constraints docs; [vendor material] Akida-2-IP-Product-Brief-V2.0 |
| **Activation precision** | 1, 2, or 4-bit for Akida 1.0 Conv/Dense layers (InputConv activations also 1/2/4-bit off an 8-bit input); Akida 2.0 layers add 8-bit and LUT-based non-ReLU activations (GeLU, SiLU, HardSiLU, LeakyReLU, PReLU). | [official documentation] doc.brainchipinc.com/user_guide/akida.html ; [repository state] author's constraints doc |
| **Supported operators / layer types** | **Akida 1.0**: InputConvolutional, Convolutional, SeparableConvolutional, Dense/FullyConnected (incl. 1-bit Edge-Learning variant) — serial, feed-forward only, strict ordering/padding/stride rules (see §5). **Akida 2.0**: InputData, InputConv2D, Stem, Conv2D, Conv2DTranspose, Dense1D, Dense2D, DepthwiseConv2D, DepthwiseConv2DTranspose, Attention, VitEncoderBlock, Add, Concatenate, ExtractToken, BatchNormalization, MadNorm, Shiftmax, BufferTempConv, DepthwiseBufferTempConv, Dequantizer. | [official documentation] doc.brainchipinc.com/user_guide/akida.html ; https://brainchip-inc.github.io/akida_examples_2.9.0-doc-1/user_guide/akida.html |
| **On-chip learning** | "Akida Edge Learning": only the **last** layer of a model, must be type `FullyConnected`, must have 1-bit weights, must receive 1-bit (binary) input from the preceding feature extractor. Learning rule: `AkidaUnsupervised` optimizer — a competitive/homeostatic Hebbian-style rule (`num_weights`, `learning_competition`, `min_plasticity`, `plasticity_decay` params), described in marketing material as STDP-inspired. Only supported on **Akida 1.0** models/devices as of the current MetaTF docs ("Edge learning is only supported for Akida 1.0 models and devices"). | [official documentation] doc.brainchipinc.com/user_guide/akida.html ; https://doc.brainchipinc.com/examples/edge/plot_1_edge_learning_kws.html ; https://doc.brainchipinc.com/examples/edge/plot_2_edge_learning_parameters.html |
| **Host interface** | AKD1000: PCIe 2.1 x2 endpoint, USB 3.0 slave, I3C, I2S, UART, JTAG, LPDDR4 memory. AKD1500: PCIe Gen2 endpoint + SPI (S/D/Q/O) peripheral/memory-expansion interfaces, 1 MB on-chip SRAM (no external DRAM needed in typical config). Akida Pico: SPI only, no host CPU required for standalone operation. | [vendor material] product briefs cited above |
| **Official toolchain** | MetaTF (TensorFlow/Keras + PyTorch/ONNX front end) → **QuantizeML** (quantization-aware training / PTQ to integer-only layers, FixedPoint/QFloat representation) → **CNN2SNN** (`convert()` maps the quantized Keras/ONNX model to an Akida runtime `.fbz` model) → Akida runtime (hardware or software simulator). Also: Akida Models Zoo (pretrained models), Edge Impulse integration (FOMO object detector, transfer-learning blocks). | [official documentation] doc.brainchipinc.com/user_guide/quantizeml.html, doc.brainchipinc.com/user_guide/cnn2snn.html, doc.brainchipinc.com/api_reference/cnn2snn_apis.html |
| **Availability / pricing (2026)** | AKD1000 PCIe dev board: **$289**; AKD1000 Raspberry Pi 4 dev kit: **$995**; AKD1000 Raspberry Pi 5 dev kit: **$1,495**; original (2021) Raspberry Pi CM4 + Shuttle PC dev kits: **$4,995 / $9,995** (CNX Software, Oct 2021 — later superseded by the cheaper boards above); AKD1500 PCIe 5-pack (commercial temp): **$199.99** (5 chips, i.e., ~$40/chip at this tier); AKD1000/AKD1500 boards also distributed via DigiKey since Sept 2025. IP licensing model also offered (per-design or volume licensing; pricing not published). | [vendor material] shop.brainchipinc.com product pages; [vendor material] CNX Software, Oct 22 2021, https://www.cnx-software.com/2021/10/22/brainchip-akd1000-snn-ai-soc-gets-raspberry-pi-and-x86-development-kits/ ; [vendor material] brainchip.com DigiKey partnership press release, Sept 18 2025 |

---

## 3. The crux: what does a "spike" mean on Akida — detailed evidence

### 3.1 The two competing hypotheses, restated

(a) Multi-timestep integrate-and-fire with membrane accumulation over T steps
(what the ANN-to-SNN rate-coding conversion literature, e.g. Diehl-Rueckauer,
QCFS, assumes), vs.

(b) Single-pass, activation-sparsity-exploiting computation on low-bit quantized
activations, where a nonzero (or newly-changed) quantized activation is called an
"event"/"spike."

### 3.2 Evidence for (b) — single-pass, quantized-activation execution

- Author's own hands-on repository (primary source, hardware actually run):
  "The public documentation does **not** describe this conversion as a classical
  ANN-to-SNN transformation where ReLU activations become spike counts over T
  timesteps or are replaced by integrate-and-fire neurons... the model is lowered
  to an Akida event-domain representation... best described as **single-step
  SNN-equivalent execution** on event-driven neuromorphic hardware, rather than as
  an explicitly exposed multi-timestep rate-coded IF/LIF simulation." **[repository
  state]** — `/Users/hamza/Documents/GitHub/BrainChip_Akida/README.md` (author's
  own AKD1000-on-Raspberry-Pi-CM4 deployment notes).
- Independent robotics paper, trained and deployed on real AKD1000 hardware:
  "the Akida chip **squashes the rate-code approximation of the ReLU into one time
  step**, where it is then represented by a **step-wise quantized ReLU**." **[preprint]**
  — Ziegler et al., arXiv:2403.10677 (both v1 and v2 carry this sentence verbatim).
- Independent space-applications benchmarking paper: "the AKD1000 does not support
  leaky neurons... the implementation suggest[s] that the converted spiking model
  reduces the computation to a single time step." **[preprint]** — Lunghi et al.,
  arXiv:2505.11418.
- Direct source-code evidence (the mechanism, not just an inference from behavior):
  in `cnn2snn/quantizeml/outputs.py`, function `set_output_v1_variables`, the Akida
  1.0 activation output is computed as `y = x / act_step` where `act_step` is
  derived from the QuantizeML output-quantizer's scale and shift, and — critically
  — *"For activations, x is decreased by half the activation step before division to
  increase the precision. This is obtained by increasing the threshold"* (i.e., the
  code literally adds `round(0.5 * act_step)` to the neuron's stored `threshold`
  variable). This is rounding-to-nearest-quantization-bin folded into a static
  comparator threshold — the behavior of a quantized ReLU, not of an accumulator
  integrating over a simulation horizon. **[repository state]** — author's local
  copy, `cnn2snn-2.19.1/cnn2snn/quantizeml/outputs.py`.
- `parse_relu_v1` (in `activations.py`) returns `{'activation': True, 'act_bits':
  out_quantizer.bitwidth}` — i.e., the Akida-layer "activation" parameter passed to
  hardware is simply a bit-width for a quantized ReLU, with no timestep/leak/decay
  parameter anywhere in the parse path. **[repository state]** — same source tree.
- 2019 company slide deck, describing the mechanism plainly, years before any
  academic reverse-engineering: "Spiking Events are non-zero activations. We only
  process Events... Quantizing weights and activations to 1, 2 or 4 bits reduces
  memory requirements." **[vendor material]** — BrainChip, "Introducing Akida"
  (Linley presentation), 2019 (cited above).
- Community technical summary, independent of BrainChip: "Akida does not support
  LIF neurons. Instead, it operates similarly to an event camera, converting pixels
  to events and using Rank Order Coding (ROC) to encode the input." **[community
  commentary]** — Open Neuromorphic, "A Look at Akida" (cited above).
- CNN2SNN's own official documentation on how BatchNorm and the activation function
  are handled: "the associated scaling operations (multiplication and shift) are
  never performed during inference. The computational cost is reduced by wrapping
  the (optional) batch normalization function and quantized activation function
  into the spike generating thresholds and other parameters of the Akida model."
  This is an explicit, official confirmation that BN-fold-into-threshold (a
  standard QAT/inference-graph-optimization technique, not an SNN-specific
  mechanism) is what CNN2SNN does. **[official documentation]** —
  https://brainchip-inc.github.io/akida_examples_2.9.0-doc-1/user_guide/cnn2snn.html

### 3.3 Evidence complicating a purely "not neuromorphic" reading

- The circuit-level integrate/threshold/fire structure is real and documented
  consistently, not invented after the fact for marketing. **[vendor material]** —
  BrainChip technical briefs, multiple years (2018–2025), consistent description.
- The same independent papers that document the single-timestep collapse also state
  that "the use of ROC decoding and the integrate-and-fire behavior in the Akida
  processor is confirmed in [80]" (their citation to a separate technical source),
  i.e., they do not conclude Akida has *no* spiking behavior at all — only that the
  *converted-CNN* deployment path used in practice does not expose or require
  multi-timestep rate coding. **[preprint]** — Lunghi et al., arXiv:2505.11418.
- Event-driven **communication** (NPU-to-NPU routing only on nonzero activations,
  no clock-driven dense computation) is a real, hardware-level property distinct
  from the *coding scheme* question, and this part of the neuromorphic claim is not
  contested by any source found here — sparsity-triggered computation genuinely
  reduces switching activity relative to a dense systolic-array accelerator. This
  is the load-bearing claim behind Akida's low-power numbers, and it does not
  require rate coding or multi-timestep accumulation to be true.

### 3.4 Reading proposed by the survey author's own primary-source repo

The author's notes propose: *"If Akida collapses the rate code into one timestep and
represents it as a step-wise quantized ReLU, then Akida is executing something very
close to the ANN-mode quantized network itself, not a temporally unrolled SNN."*
This reading is **directly supported** by the `outputs.py` code path (§3.2) — the
Akida-1.0 activation computation is algebraically a quantized ReLU with a
threshold that has absorbed the BN scale/shift and a rounding offset, computed once,
not iterated. No source found in this research states this equivalence in exactly
these words as a general theoretical claim (i.e., no paper says "Akida proves
rate-coded IF ≡ quantized ReLU" as a formal result); the Ziegler et al. and Lunghi
et al. papers state the *empirical* fact (single time step, step-wise quantized
ReLU) without drawing the QAT-equivalence conclusion explicitly. **This reading is
therefore reported here as strongly evidence-supported by source code and
converging independent descriptions, but not as a claim any cited source states
in that generalized theoretical form** — flag accordingly if used in the thesis.

---

## 4. Rank order coding — lineage, definition, and whether Akida silicon implements it

### 4.1 Lineage: Thorpe → SpikeNet → BrainChip

- Rank order coding (ROC) was introduced by Simon Thorpe and Jacques Gautrais:
  "Rank Order Coding," in J. Bower (Ed.), *Computational Neuroscience: Trends in
  Research 1998*, pp. 113–118 (Plenum Press). Its empirical motivation is Thorpe's
  earlier finding that the human visual system can categorize a novel scene in
  <150 ms — too fast for multi-spike rate coding to be physiologically plausible
  given known neural firing rates. **[peer-reviewed]** — Thorpe & Gautrais 1998
  (book chapter); Thorpe, Fize, Marlot, "Speed of processing in the human visual
  system," *Nature* 381, 520–522 (1996).
- Foundational simulation work: Thorpe & Gautrais, "Rapid Visual Processing using
  Spike Asynchrony," NeurIPS 1996 — using **SPIKENET**, a simulator in which "even
  with activity in retinal output cells limited to **one spike per neuron per
  image**," sophisticated visual processing was possible using only the *order* of
  firing. **[peer-reviewed]** — https://proceedings.neurips.cc/paper_files/paper/1996/file/fd5c905bcd8c3348ad1b35d7231ee2b1-Paper.pdf
- SpikeNET as a real-time simulator/software product: Delorme, Guyonneau,
  Guilbaud, Allegraud, VanRullen, "SpikeNet: real-time visual processing with one
  spike per neuron," *Neurocomputing* (2004); Delorme & Thorpe, "SpikeNET: an
  event-driven simulation package for modelling large networks of spiking
  neurons," *Network: Computation in Neural Systems* 14(4), 613–627 (2003).
  **[peer-reviewed]**
- Corporate lineage into BrainChip: "On 1 September, 2016 the company completed the
  acquisition of a French based company **Spikenet Technology**, which specialised
  in AI computer vision technology... Spikenet had a relationship with Cerco
  Research Centre where Dr Simon Thorpe (now a member of the Brainchip Scientific
  Advisory Board) undertook research... and developed the JAST learning rules,"
  exclusively licensed to BrainChip on 20 March 2017. This produced the
  "BrainChip Studio" / "BrainChip Accelerator" video-analytics products (2017),
  predating the Akida chip announcement (2018). Simon Thorpe has since chaired/sat
  on BrainChip's Scientific Advisory Board. **[vendor material, company history
  page]** — "The Brainchip Story - 2016 to December 2020," https://akida.io/story
- Independent confirmation of the pivot away from rate coding, from a trade-press
  technical analysis: "BrainChip started with rate coding, but decided that wasn't
  commercially viable. Instead, it uses rank coding (or rank-order coding), which
  uses the order of arrival of spikes... to a neuron as a code." **[community
  commentary / trade press]** — Bryon Moyer, "Spiking Neural Networks: Research
  Projects or Commercial Products?", Semiconductor Engineering, May 18, 2020,
  https://semiengineering.com/spiking-neural-networks-research-projects-or-commercial-products/

### 4.2 What rank order coding means computationally

- Core mechanism, from Thorpe's own definitive treatment: "neurons can be made
  sensitive to the order of activation of their inputs by including a feed-forward
  **shunting inhibition** mechanism that progressively desensitizes the neuronal
  population during a wave of afferent activity. In such a case, maximum activation
  will only be produced when the afferent inputs are activated **in the order of
  their synaptic weights**." Each input neuron fires **at most one spike**; no
  rate/count information is used; up to log2(N!) bits of information can in
  principle be carried by the firing order of N neurons. **[peer-reviewed]** —
  Thorpe, Delorme, Van Rullen, "Spike-based strategies for rapid processing,"
  *Neural Networks* 14(6-7), 715–725 (2001).
- Distinguishing ROC from rate coding and from Time-To-First-Spike (TTFS)/latency
  coding, from a recent unifying framework paper (also by Thorpe's group): "In an
  early proposal, called rank-order coding (ROC), neurons are maximally activated
  when inputs arrive in the order of their synaptic weights, thanks to a shunting
  inhibition mechanism that progressively desensitizes the neurons as spikes
  arrive." TTFS is the broader family (information in the *latency* of a single
  spike per neuron); ROC is a *specific* TTFS-family scheme where what matters is
  *relative order* across a population, not each neuron's absolute latency in
  isolation. **[peer-reviewed]** — Bonilla, Gautrais, Thorpe, Masquelier,
  "Analyzing time-to-first-spike coding schemes: A theoretical approach,"
  *Frontiers in Neuroscience* (2022), https://pmc.ncbi.nlm.nih.gov/articles/PMC9548614/
- **N-of-M coding** (a related but distinct scheme, also traced to Thorpe's group
  and to Furber et al.): only the first N spikes among M afferents are propagated,
  read out by a neuron with **binary** (homogeneous) weights; unlike ROC, the exact
  *order* of those N spikes does not matter, only *which* N neurons fired. The same
  2022 paper introduces "Ranked-NoM" (R-NoM), a hybrid that is more
  hardware-friendly than ROC (integer weights/modulation) while retaining most of
  ROC's discriminative power, and explicitly argues R-NoM and NoM should be
  preferred over the original ROC scheme for hardware implementations. **[peer-reviewed]**
  — same source (Bonilla et al. 2022).
- Experimental (non-modeling) confirmation that ROC is a real decoding strategy
  usable on biological spike data, not just a simulation convenience: Portelli et
  al. (title: "Rank Order Coding: a Retinal Information Decoding Strategy Revealed
  by Large-Scale Multielectrode Array Retinal Recordings"), using a 4096-electrode
  MEA on mouse retina, found ROC-based decoders outperformed independent spike-count
  and latency decoders for population read-out, though the population lacked
  individually latency-tuned cells. **[peer-reviewed]** — PMC4891767,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4891767/

### 4.3 Does Akida silicon actually implement rank order coding today?

This is genuinely ambiguous in the public record, and the evidence points different
directions depending on which part of the pipeline is being described:

- **Input encoding**: Multiple independent, non-BrainChip sources — including a
  2025 medRxiv paper doing direct AKD1000 deployment — describe Akida's
  pixel-to-event conversion as using Rank Order Coding: "converting pixel activity
  into discrete events through **Rank Order Coding (ROC)** for input encoding."
  **[preprint, medical]** — Herbozo Contreras, Yu, Huang, Aguilar, Nikpour, Kavehei,
  "Neuromorphic Neuromodulation: A Low-Power Edge-Training Framework...," medRxiv
  2025.09.22.25336341, https://www.medrxiv.org/content/10.1101/2025.09.22.25336341v1
- The Lunghi et al. (2025) space-applications paper states explicitly that public
  BrainChip documentation is *not itself* clear on the neuron model, but that "the
  use of ROC decoding and the integrate-and-fire behavior in the Akida processor is
  **confirmed in [80]**" — i.e., they had to go outside BrainChip's own docs to a
  third source to confirm this, which is itself evidence that **BrainChip's own
  documentation does not clearly state whether/how ROC is implemented on current
  silicon** for the converted-CNN path. **[preprint]** — arXiv:2505.11418.
- **Internal (hidden-layer) processing**: no source gathered here — including the
  primary-source repository and the code inspection in §3.2 — shows evidence of an
  order-sensitive shunting-inhibition mechanism operating between hidden layers of
  a converted CNN on Akida hardware. The `outputs.py`/`activations.py` code path
  shows a magnitude-threshold comparator (quantized ReLU), which is order-agnostic
  within a layer — it does not care *which* input arrived first, only whether the
  weighted sum crosses a threshold. This is consistent with NoM-style ("did enough
  of the right things fire") computation, or with plain quantized-activation
  sparsity, but is **not** evidence of ROC's defining shunting-inhibition/order-
  sensitivity mechanism operating inside converted-CNN layers.
- **Best-supported overall reading**: Akida's *lineage and input/event-generation
  stage* draw on genuine ROC research (via the Spikenet Technology acquisition and
  Thorpe's continued advisory role), and BrainChip's own historical technical
  briefs describe "rank coding" as the chip's native encoding scheme at the level
  of "information expressed as the time and place it occurs." But the
  **converted-CNN inference path that essentially all published Akida benchmarks
  use** collapses to a single-pass, magnitude-threshold (quantized-ReLU)
  computation that does not require, and is not shown by any source here to
  implement, ROC's order-sensitive readout inside hidden layers. Whether Akida's
  **native SNN mode** (STDP-trained from scratch, as opposed to the
  QuantizeML/CNN2SNN converted-CNN mode) implements true order-sensitive ROC
  readout is **NOT FOUND** in this research — none of the sources gathered
  characterize the native-SNN-mode neuron model at this level of mechanistic
  detail. This is a real gap in the public record, not a settled negative.

### 4.4 MorphIC: an independent academic silicon comparison of ROC vs. rate coding

This is not a BrainChip chip, but it is the closest thing found here to a controlled,
same-silicon, same-task energy comparison between rank order coding and rate coding —
directly relevant to why a company might choose ROC-family coding for a commercial
low-power accelerator:

- MorphIC (Frenkel, Legat, Bol; 65 nm CMOS, quad-core, binary-weight, on-chip
  learning SNN ASIC) measured, on the **same silicon, same MNIST task**: rate coding
  reached 97.8% accuracy at **205 µJ/classification**; rank order coding reached
  95.9% accuracy (a 1.9-point drop) at **21.8 µJ/classification** — roughly a
  **10-fold energy improvement** for ROC over rate coding, with three further
  architectural optimizations projected to bring ROC energy down to 8.2
  µJ/classification. **[peer-reviewed / E1, physical silicon, measured]** —
  Frenkel, Legat, Bol, "MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight
  Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning,"
  arXiv:1904.08513 (also published in IEEE TBioCAS),
  https://ar5iv.labs.arxiv.org/html/1904.08513
- This result substantiates, on independent silicon, the general commercial logic
  a trade-press piece attributes to BrainChip's own design choice (§4.1): rate
  coding is measurably far more energy-expensive per classification than
  order/rank-based coding on real hardware, which is a plausible (though not
  independently Akida-specific) technical motivation for BrainChip's pivot away
  from rate coding after the Spikenet acquisition.
- No source found in this research reports a MorphIC-style controlled energy
  comparison performed **on Akida silicon itself** (rate-coded vs. rank/order-coded
  variants of the same task on the same AKD1000/AKD1500 chip). This specific
  comparison for Akida is **NOT FOUND**.

---

## 5. CNN2SNN / QuantizeML: what the toolkit actually does

(Primary-source verified against the author's own local copy of `cnn2snn` 2.19.1
and cross-checked against current `doc.brainchipinc.com` documentation.)

### 5.1 Pipeline

float Keras/ONNX CNN → **QuantizeML** (`quantize()`: replaces layers with quantized,
integer-only equivalents; either direct/PTQ or quantization-aware training/QAT
depending on accuracy needs) → **CNN2SNN** (`convert()`: maps the quantized model to
an Akida-runtime-compatible `.fbz` model, folding BN and activation-quantization
math into per-neuron thresholds/scales) → Akida runtime (hardware device or software
simulator). **[official documentation]** —
https://doc.brainchipinc.com/user_guide/quantizeml.html,
https://doc.brainchipinc.com/user_guide/cnn2snn.html. This matches the author's own
description exactly: "float CNN → QuantizeML quantized model → CNN2SNN conversion →
Akida runtime execution." **[repository state]**

### 5.2 Is this threshold balancing / weight normalization / rate-coding conversion à la Diehl-Rueckauer?

**No.** There is no weight-normalization pass calibrated to a target firing rate over
a chosen T, and no notion of "spike count over T approximates the ReLU" being
explicitly implemented as an iterative simulation. Instead:

- QuantizeML performs **uniform, symmetric, zero-centered** quantization: for a
  float tensor x, `x_int = clip(round(x/s), q_min, q_max)`, with scale `s =
  max(|x|) / (2^b - 1)`, and represents values with a FixedPoint/QFloat scheme
  (`x_float ≈ x_int · 2^-frac_bits`). This is standard integer quantization-aware
  training, not rate-coding calibration. **[repository state]** — author's README
  (quoting QuantizeML's own documented FixedPoint example: representing π at
  frac_bits=1/3/6 as 3.0/3.125/3.140625).
- CNN2SNN's official docs state directly that BN and quantized-activation math are
  "wrapp[ed]... into the spike generating thresholds and other parameters of the
  Akida model" and that the associated multiply/shift ops "are never performed
  during inference" as separate floating operations — i.e., this is BN-folding, a
  standard inference-graph optimization technique used across the entire QAT/edge-
  deployment industry (not unique or specific to spiking hardware). **[official
  documentation]** — https://brainchip-inc.github.io/akida_examples_2.9.0-doc-1/user_guide/cnn2snn.html

### 5.3 Bit-widths supported

Confirmed consistently across official docs and the author's hands-on constraints
notes: **Akida 1.0** — InputConvolutional: 8-bit input, 8-bit weights, 1/2/4-bit
activations; Convolutional and Dense: 1/2/4-bit input, weights, and activations.
**Akida 2.0** — up to 8-bit weights/activations, plus LUT-based non-ReLU activation
support. Edge-Learning FullyConnected layer: 1-bit weights and 1-bit input
(mandatory, not optional). **[official documentation + repository state]** —
doc.brainchipinc.com/user_guide/akida.html; author's `AKIDA_V1_CONSTRAINTS.md`.

### 5.4 Reset-by-subtraction / membrane potential accumulating over time?

**No**, not in the converted-CNN path (see §3 for full evidence). The threshold
mechanism is a single static comparator per neuron, with the threshold value
itself carrying the folded BN scale/shift and a rounding offset — there is no
iterative "integrate this timestep's input, compare to threshold, subtract
threshold and carry remainder to next timestep" loop visible in the reachable
source (`outputs.py`, `activations.py`) for the standard conversion path.

### 5.5 Hard deployment constraints hit in practice (author's primary-source hands-on record)

Verified against `AKIDA_V1_CONSTRAINTS.md` / `AKIDA_V1_CONSTRAINTS_COMPACT.md`,
cross-referenced by the author against BrainChip's official hardware-constraints
pages (https://brainchip-inc.github.io/akida_examples_2.4.0-doc-1/user_guide/1.0_hw_constraints.html
and https://doc.brainchipinc.com/user_guide/hardware/1.0.html):

- **Input**: width 5–256 px (exceeding 256 forces Conv layers to run in *software*,
  losing hardware acceleration entirely — not a hard failure, but a silent
  performance cliff); height ≥5 px; channels ∈ {1, 3} only.
- **Model API**: Keras Sequential/Functional only; subclassed `keras.Model` fails
  quantization with an `AttributeError` (no defined input shape).
- **Activations**: ReLU must be **bounded**, `ReLU(max_value=6.0)`, as a **separate**
  layer (not fused via `activation='relu'` in Conv/Dense) — unbounded
  `QuantizedReLU` raises `ValueError: unbounded QuantizedReLU is not supported in
  AkidaVersion.v1`. Non-ReLU activations (softmax, sigmoid) permitted **only** in
  the final output layer.
- **Convolutions**: first layer (InputConvolutional) kernel 3×3/5×5/7×7, stride
  1/2/3, padding 'same' or 'valid'; all subsequent Conv layers: kernel
  1×1/3×3/5×5/7×7, stride 1 or 2 (**stride 2 only with 3×3 kernels**), padding
  **'same' only** (a 'valid'-padded intermediate Conv raises `RuntimeError: Only
  padding same is supported`). No dilated or grouped convolutions.
- **Pooling**: MaxPool size 1×1/2×2 (InputConv layer additionally allows 1×2/2×1);
  stride ≤ pool size; padding must **match** the preceding Conv layer's padding
  exactly, or conversion raises a `ValueError`. GlobalAveragePooling: output width
  ≤32, conv output height ≥3 rows.
- **Ordering**: a Conv(+MaxPool) block must be followed by another Conv layer, not
  directly by Dense/Flatten; the **last** Conv before Dense must **not** have
  MaxPool (`RuntimeError: ...max pooling must be followed by another
  convolutional... layer`); BatchNorm, if used, must precede the activation;
  Flatten only directly before Dense.
- **Dense**: input must be spatially flattened (width=height=1); total input
  features capped at **57,334**.
- **Data types**: training/quantization in float32; hardware **inference requires
  uint8** input (`ValueError: Input dtype should be uint8` otherwise).

These are exactly the kind of practitioner-level constraints that do not appear in
BrainChip's marketing material but materially shape what models can be deployed —
and they are consistent with a **quantized, integer-only CNN accelerator** with a
strict, hardware-driven graph-compiler contract (comparable in spirit to a TFLite
Micro or TensorRT deployment contract), not with a general-purpose SNN simulator
accepting arbitrary spiking-network topologies.

---

## 6. Comparison to the conversion literature's assumptions

Explicit determination of which conversion-literature primitives (Diehl-Rueckauer /
QCFS-style ANN-to-SNN assumptions) Akida's standard converted-CNN path supports:

| Primitive assumed by the conversion literature | Supported by Akida's converted-CNN path? | Evidence |
|---|---|---|
| Multi-timestep temporal integration (user-set T) | **No** (for the standard CNN2SNN/QuantizeML path). Collapses to a single pass. Some newer layer types (`BufferTempConv`, TENN blocks) carry temporal buffers for genuinely sequential data, but this is not the rate-coding T of the conversion literature. | §3.2, §3.3; arXiv:2403.10677; arXiv:2505.11418; `outputs.py` |
| Membrane potential state carried across timesteps | **No**, not exposed/used in the standard path; threshold is a static, per-neuron comparator computed once at conversion time. | §3.2, §5.4; `outputs.py` |
| Reset-by-subtraction | **No** — no residual-potential carry-over mechanism found; instead a rounding offset is folded into the static threshold once. | §5.4; `outputs.py` |
| Rate coding of an activation as a spike count over T | **No** — explicitly and repeatedly described by independent sources as *replaced by* a step-wise quantized ReLU evaluated once. | §3.2; arXiv:2403.10677 (quote: "squashes the rate-code approximation... into one time step") |
| IF neuron dynamics (accumulate, compare, fire, reset, repeat) | **Partially** — the circuit-level description matches IF dynamics, but the *repeat* (multi-step) part is absent in the standard converted-CNN deployment; the "compare and fire" collapses to one evaluation equivalent to a quantized activation function. | §1.2, §3 |
| Signed spikes | Unclear/mixed — general "events" in BrainChip's marketing material "can have a value that indicates neural behavior" (i.e., not strictly binary), but the mandatory Edge-Learning FullyConnected layer is strictly 1-bit (unsigned binary). **NOT FOUND**: an explicit statement of whether general Akida events can be negative-valued. | §2 (Spike payload row); [vendor material] "What Is the Akida..." |
| Order/rank-sensitive readout (ROC's defining shunting-inhibition mechanism) inside hidden layers | **Not shown** to be present in the converted-CNN path by any source examined; magnitude-threshold comparators are order-agnostic within a layer. Input-encoding stage is described as ROC by several independent sources. Native-SNN-mode (non-converted) neuron model is **NOT FOUND** to be characterized at this level of detail by any source gathered. | §4.3 |
| Event-driven sparse communication reducing switching activity | **Yes** — consistently documented, not contested by any source, and architecturally distinct from the coding-scheme question. | §3.3, §1 |

---

## 7. Temporal Event-Based Neural Networks (TENN)

### 7.1 What TENN is

- TENN ("Temporal Event-based Neural Network") is BrainChip's newer architecture
  family, introduced publicly in June 2023, built around **temporal convolution
  with structured (orthogonal-polynomial) kernels** — specifically Chebyshev and
  Legendre polynomial expansions of the temporal kernel — combined with ordinary
  spatial convolution. **[vendor material]** — BrainChip, TENNs Whitepaper,
  https://brainchip.com/wp-content/uploads/2023/06/TENNs_Whitepaper_Final.pdf;
  BrainChip blog, "BrainChip Introduces Temporal Event-Based Neural Networks,"
  June 11 2023, https://brainchip.com/temporal-event-based-neural-networks-a-new-approach-to-temporal-processing/
- TENN has two mathematically equivalent execution modes: **"buffer"/convolution
  mode** (parallel, GPU/TPU-friendly, used for training) and **"recurrent" mode**
  (sequential, O(T), small memory footprint, used for edge inference). This
  train-as-convolution / infer-as-recurrence duality is the same mathematical
  property exploited by deep state-space models (S4, Mamba) and by the Legendre
  Memory Unit (LMU) / HiPPO framework. **[vendor material]** — TENNs Whitepaper
  (cited above); BrainChip presentation, "Temporal Event Neural Networks: A More
  Efficient Alternative to the Transformer," Edge AI Vision 2024,
  https://www.edge-ai-vision.com/wp-content/uploads/2024/06/E1R07_Jones_Brainchip_2024.pdf

### 7.2 Is it spiking, or a state-space/convolutional model?

**It is a state-space/convolutional model that BrainChip explicitly says is
distinct from prior SSMs but maps onto the same mathematical family, and it is not
itself a spiking network as shipped.**

- BrainChip's own whitepaper insists TENNs are distinct from state-space models
  ("TENNs efficiently learn both spatial and temporal correlations from data in
  contrast with state-space models that mainly treat time series data with no
  spatial components"), but this is a claim about *scope* (TENN handles spatial +
  temporal jointly), not about the underlying mathematical machinery, which is the
  same polynomial/recurrence-relation kernel-expansion family used by S4/HiPPO/LMU.
  **[vendor material]** — TENNs Whitepaper.
- BrainChip's own open-source implementation, `tenns-core`, is explicitly described
  as **"a standalone PyTorch library for efficient State Space Model (SSM) layers,"**
  with SSM modes named S5, DWS, Neck, Full, Gate — directly using SSM terminology,
  with dual FFT-convolution (training) / recurrent-step (inference) computation
  paths, and complex-valued state representations. **[repository state, public
  GitHub]** — https://github.com/Brainchip-Inc/tenns-core
- The clearest evidence that TENN as currently built is **not** itself a spiking
  network: PLEIADES, an academic paper built on the TENNs framework and explicitly
  crediting "a broader class of networks named Temporal Neural Networks (TENNs)
  developed by Brainchip Inc.," states as **future work**: *"Another direction is
  to adapt/convert this architecture into a spiking system by leveraging the
  structure of the polynomial kernels to provide richer dynamics to neurons beyond
  the typical and arbitrary leaky integrate-and-fire neurons... It offers the
  possibility for such spiking systems to be trained as a convolutional network
  without having to simulate any differential equation of the internal neural
  dynamics."* If converting TENN to a spiking system were already true of the
  shipping architecture, this sentence would not be phrased as a future
  possibility. **[preprint]** — Chen et al. (PLEIADES team), "TENNs-PLEIADES:
  Building Temporal Kernels with Orthogonal Polynomials," arXiv:2405.12179,
  https://arxiv.org/html/2405.12179v3
- BrainChip's own trade-press presentation on TENN describes it explicitly as **"a
  highly efficient transformer replacement,"** used for language models,
  time-series, and spatiotemporal data — a framing under which TENN competes with
  Mamba/S4-style efficient-sequence-modeling architectures, not with spiking
  networks. **[vendor material]** — Edge AI Vision presentation (cited above);
  BrainChip blog, "Introducing TENN: Energy-Efficient Transformer,"
  https://brainchip.com/introducing-tenn-revolutionizing-computing-with-an-energy-efficient-transformer-replacement/

### 7.3 Why this matters (the pivot)

TENN's introduction, and its position as the flagship capability of Akida 2.0
("Akida 2.0's architecture is designed to fully exploit TENN's capabilities,
featuring a mesh network of nodes each equipped with an event-based TENN processing
unit"), is evidence of a **strategic pivot** from "spiking neural network
accelerator" toward "efficient recurrent/state-space sequence-model accelerator that
happens to run on the same event-driven, sparsity-exploiting hardware substrate."
The hardware property that is actually being sold (sparse, event-triggered,
at-memory compute) is orthogonal to whether the executed model is a spiking network,
a quantized CNN, or an SSM — TENN's success as a marketing narrative suggests
BrainChip itself increasingly treats "neuromorphic" as a hardware-execution-style
label rather than a strict commitment to spike-based neuron dynamics.
**[vendor material]** — Edge AI Vision presentation (cited above).

---

## 8. Independent evaluations and benchmarks

### 8.1 Peer-reviewed / preprint, physical silicon (E1/E2)

- **[E1, preprint]** Azadi, Anzengruber-Tanase, Sopidis, Haslgrübler, Ferscha,
  "Towards an Energy-Efficient and Sustainable IIoT using Embedded Neuromorphic
  AI," 2025 (ACM, DOI 10.1145/3770501.3770529). Directly compares BrainChip Akida
  against NVIDIA Jetson Orin NX on real hardware, MNIST inference plus 25-day
  long-term monitoring: **quantized model inference averaged 22.54 s on Akida vs.
  181.66 s on Orin NX for 10k MNIST test samples** (Akida faster); measured
  **average active power 4.36 W (Akida) vs. 9.17 W (Orin NX)**, and total energy
  over 25 days **2.6 kWh (Akida) vs. 5.5 kWh (Orin NX)**. Uses Shelly Plus Plug S
  smart plugs for independent real-world power measurement, not just simulator
  numbers. **[peer-reviewed]** — https://doi.org/10.1145/3770501.3770529
- **[E1, preprint]** Lunghi, Silvestrini, Dold, Meoni, Hadjiivanov, Izzo, "Energy
  efficiency analysis of Spiking Neural Networks for space applications,"
  arXiv:2505.11418 (2025). Trained/converted three CNN models on the EuroSAT scene-
  classification dataset for the AKD1000, using its "built-in power consumption
  reporting capabilities." Notes accuracy can drop drastically after quantization
  (e.g., "from 90% to 30%") absent calibration/retraining — a concrete,
  independently observed accuracy cost of the quantization step, not just a
  theoretical risk. **[preprint]** — https://arxiv.org/abs/2505.11418
- **[E2, preprint/medical]** Herbozo Contreras et al., "Neuromorphic
  Neuromodulation: A Low-Power Edge-Training Framework for the Future of
  Personalized and Closed-Loop Neurostimulation," medRxiv 2025.09.22.25336341.
  Deployed an 8-4-4-bit QAT model (with a final 1-bit Edge-Learning layer) on real
  Akida hardware for EEG-based seizure-related personalization; explicitly notes
  Akida "supports only integer arithmetic for both inference and on-chip learning,
  ruling out any floating-point operations." **[preprint]** —
  https://www.medrxiv.org/content/10.1101/2025.09.22.25336341v1
- **[E1/E2, preprint]** Ziegler, Vetter, Gossard, Tebbe, Otte, Zell, "Detection of
  Fast-Moving Objects with Neuromorphic Hardware," arXiv:2403.10677 (2024).
  Benchmarks Akida alongside DynapCNN and Intel Loihi 2 for table-tennis-ball
  detection; explicitly documents the ANN-to-SNN training/deployment asymmetry
  across the three platforms (direct SNN training for DynapCNN, Intel bootstrap
  method for Loihi 2, MetaTF quantization-aware training for Akida) precisely
  because Akida's toolchain does not support the same conversion assumptions as
  the other two. **[preprint]** — https://arxiv.org/abs/2403.10677
- **[E4, vendor-authored but citing an academic benchmark dataset]** BrainChip
  white paper comparing AKD1000 to Intel Loihi 2 on the UNSW TON-IoT cybersecurity
  dataset: claims 98.4% accuracy (Akida) vs. 90.2% (Loihi 2), 1 W power (Akida) vs.
  2.5 W (Loihi 2) — **this is BrainChip's own white paper, not an independent
  third-party benchmark**, and should be labeled as a marketing claim, not
  independently verified data, despite citing real datasets. **[vendor material]**
  — BrainChip, "A Game Changer in AI Computing for Cybersecurity" white paper,
  https://brainchip.com/wp-content/uploads/2025/01/BrainChip_White-Paper-A-Game-Changer-in-AI-Computing-for-Cybersecurity_v3.pdf

### 8.2 Non-academic / community-commentary evaluations (labeled, not conflated with verified data)

- **[community commentary]** Open Neuromorphic hardware page — a maintained,
  vendor-neutral community technical resource (not BrainChip-authored), states
  plainly Akida does not support LIF neurons and explains the ROC/event-camera-like
  input encoding; also flags a real software/documentation friction point:
  "AKD1500 and AKD2000 are not available for purchase [as of the page's writing],
  however the MetaTF SDK has already been updated to reflect the additional
  capabilities of the AKD2000 chip. This can lead to confusion when training models
  that will be mapped to the AKD1000 chip due to certain incompatibilities in the
  API and deprecated functions." — https://open-neuromorphic.org/neuromorphic-computing/hardware/akida-brainchip/
- **[community commentary, investor-skeptic]** Equity.Guru (financial commentary
  site), "BrainChip (ASX.BRN): Big promises, marketing slop, and an AI company that
  missed the AI boom," Nov 21 2025 — a sharply critical non-academic technical/
  financial writeup arguing BrainChip's investor materials omit benchmarks,
  revenue detail, customer names, and competitive comparisons (vs. Syntiant,
  SiFive, Nvidia Jetson, Edge TPU, Qualcomm); concedes "BrainChip is not a scam...
  They have real engineers, real patents, real silicon, and real partners," but
  argues the company's $300M ASX market cap implies commercial maturity the
  company has not demonstrated. **[community commentary]** —
  https://equity.guru/2025/11/21/brainchip-asx-brn-big-promises-marketing-slop-and-an-ai-company-that-missed-the-ai-boom/
- **[community commentary, investor-skeptic]** AInvest, "BrainChip Finally Ships
  Silicon. A Year of Cash Decides What Happens Next.", Sept 11 2026 — reports
  AKD1500 revenue ~$1.2M for the half-year through June 2026, 25% of initial chip
  inventory sold, a defense customer (Parsons) order of "several thousand chips,"
  but also **AKD1500 silicon yield issues under investigation** as of that report.
  **[community commentary]** — https://www.ainvest.com/news/brainchip-finally-ships-silicon-year-cash-decides-2609/
- **[community commentary, shareholder forum]** HotCopper forum threads (ASX
  retail-investor discussion board) contain both boosterish and skeptical posts;
  one substantive skeptical post explicitly notes "AKIDA 1000 is available for more
  than 4 years, with two IP signatory and still no sales" as of early 2026, and a
  separate poster's technical characterization that "AKIDA 1500... is essentially a
  modified version of the Akida 1000 core" (unverified against BrainChip
  engineering documentation — flagged here as unverified forum claim, not
  established fact). **[community commentary — explicitly unverified]** —
  https://hotcopper.com.au/threads/how-can-brainchip-turn-around-from-here.8999768/
  , https://hotcopper.com.au/threads/ibm-akd1000.9004561/

### 8.3 Independent evaluations found *underperforming* BrainChip's own claims

- The quantization-accuracy-drop finding in Lunghi et al. (§8.1: accuracy dropping
  "from 90% to 30%" without calibration/retraining) is a concrete, independently
  measured instance where naive deployment substantially underperforms accuracy
  expectations, though the paper also documents mitigation (calibration +
  retraining) that recovers most of the loss.
- The Open Neuromorphic page's note about AKD1500/AKD2000 SDK-vs-hardware
  incompatibility is evidence of real-world developer friction not disclosed in
  BrainChip marketing material.
- No source gathered here presents a *controlled, apples-to-apples* independent
  benchmark showing Akida underperforming its **specific published power/latency
  claims** on a task BrainChip itself has benchmarked (e.g., no independent
  reproduction attempt of the TON-IoT cybersecurity comparison in §8.1 was found).
  This specific type of "independent replication contradicts vendor claim" result
  is **NOT FOUND** in this research; the closest is the IIoT paper (§8.1), which if
  anything corroborates Akida's low-power/low-latency claims relative to a Jetson
  Orin NX on MNIST, under real (non-simulated) measurement.

---

## 9. Availability and commercial status (as of research date, mid-late 2026)

- **What can actually be bought today**: AKD1000 PCIe dev board ($289), AKD1000
  Raspberry Pi 4 dev kit ($995), AKD1000 Raspberry Pi 5 dev kit ($1,495), AKD1000
  M.2 card, AKD1500 PCIe commercial-temp 5-pack ($199.99, i.e., ~$40/chip at that
  tier). All available directly from shop.brainchipinc.com and, since September
  2025, via DigiKey. **[vendor material]** — shop.brainchipinc.com; DigiKey
  partnership press release (cited above).
- **AKD1500 commercial shipment status**: BrainChip announced "commercial
  availability and initial production shipments" of AKD1500 on June 30, 2026,
  manufactured by GlobalFoundries on 22nm FD-SOI. By late August 2026, BrainChip
  reported an initial production run of **2,000 AKD1500 processors shipped**, with
  H1-2026 revenue of $1.22M (up 19% YoY) against a widened net loss of $12.02M
  (from $9.36M). By September 2026, reporting indicated 25% of initial AKD1500
  inventory sold and a defense-sector order (Parsons) of "several thousand chips,"
  alongside disclosed **yield issues under investigation**. **[vendor material +
  community commentary, financial reporting]** — BrainChip press release (cited
  above); NewsCase, Aug 28 2026, https://www.newscase.com/brainchip-ships-its-first-commercial-processors-but-the-financial-hole-deepens/;
  AInvest, Sept 11 2026 (cited above).
- **IP licensing model**: Akida is offered both as packaged silicon (AKD1000,
  AKD1500, Akida Pico) and as licensable RTL IP ("fully synthesizable RTL... RTL
  synthesis scripts and timing constraints... Run time software C++ library...
  Processor and OS agnostic") for integration into partner SoCs on any process
  node. Specific per-design or volume license pricing is **NOT FOUND** in any
  source gathered (not published). **[vendor material]** — Akida 2 IP Product
  Brief, Akida 1.0 IP Product Brief (cited in §1.1 and §2).
- **Revenue history**: peak reported product/IP revenue was **A$5.07M in FY2022**,
  falling to **A$0.4M by FY2023** per one third-party financial-analysis site
  (unverified against BrainChip's own annual report in this research pass), with
  H1-2026 revenue reported as $1.22M (licenses $613,826 + product sales $110,362 +
  development services $498,557) — the company's first quarter with a
  licenses-plus-product-plus-services revenue mix of this composition, per the
  NewsCase report. **[community commentary, financial-analysis site — flagged as
  unverified against primary annual-report filings]** —
  https://koalagains.com/stocks/ASX/BRN ; NewsCase (cited above).
- **Shipping products containing Akida**: **NOT FOUND** — no source gathered in
  this research identifies a specific, named, currently-shipping consumer or
  industrial end product (as opposed to dev boards/reference designs) that
  contains an Akida chip, beyond the AKD1500-to-Parsons defense order (chip-level
  sale, not confirmed end-product name) and a "Neuromorphyx" go-to-market partner
  relationship reported for AKD1500 rugged industrial PCs (per AInvest, community
  commentary, unverified against a Neuromorphyx primary source in this pass).

---

## 10. Event-camera applications using Akida

Directly addresses the survey author's observation that applications pairing an
event camera with Akida exist — confirmed, and the underlying computation is
characterized below:

- **Prophesee + Akida 2, Embedded World 2025**: BrainChip demonstrated gesture
  recognition combining a **Prophesee EVK4 event-based camera** with an **Akida 2
  FPGA platform** (not yet packaged silicon at the time). Prophesee's own VP of
  Sales & Marketing framed the value proposition as exploiting event-stream
  sparsity: "Processing our event-based sensor data streams efficiently leverages
  their sparse nature, reducing computational and memory demands in the final
  product." **[vendor material, joint BrainChip/Prophesee press release]** —
  https://investor.wedbush.com/wedbush/article/bizwire-2025-3-10-brainchip-demonstrates-event-based-vision-at-embedded-world-2025
- **What Akida computes on the events, in this demo**: not independently
  characterized in mechanistic detail by any source found (the press release
  describes the application — gesture recognition, detect/classify/track — not the
  neuron-level computation). Given §3's findings, the most likely computational
  regime (based on the standard CNN2SNN/QuantizeML deployment path used for all
  other documented Akida applications) is a quantized-CNN/FOMO-style model running
  on event-accumulated frames or event histograms, not a native multi-timestep
  spiking simulation — but this specific demo's internal pipeline is **NOT FOUND**
  to be documented at that level of detail.
- **ARACHNID** (independent, non-BrainChip academic/hobbyist project): "A
  Neuromorphic Camera Array System for Space Situational Awareness," using 8
  Prophesee event-based cameras in a multi-view array with **BrainChip Akida
  v3.11** (software version) explicitly listed as a dependency, described by its
  authors as leveraging "Spiking Neural Networks (SNNs) for real-time, parallel
  detection." **[repository state, public GitHub, independent of BrainChip]** —
  https://github.com/s-valdivia-vasquez/ARACHNID-system — mechanistic detail on
  what Akida computes internally in this pipeline is not present in the repository
  README excerpt gathered; would require deeper repository inspection to verify
  the encoding/timestep assumptions used.
- **Edge Impulse + Akida, industrial inspection** (frame-camera, not event-camera,
  but relevant as the same FOMO-object-detector pattern likely used in event-camera
  pipelines): Edge Impulse's "Faster Objects, More Objects" (FOMO) object detector
  "has been ported to work on the AKD1000." This confirms the FOMO-style detector
  is a standard, documented Akida deployment pattern, supporting the inference in
  the bullet above about what likely runs on event-camera pipelines too. **[vendor
  material, joint Edge Impulse/BrainChip documentation]** —
  https://docs.edgeimpulse.com/projects/expert-network/brainchip-akida-industrial-inspection
- **General note on event-camera object detection literature** (context, not Akida-
  specific): the broader event-camera object-detection field — represented by
  Prophesee's own SDK tutorials, the EV-Ultralytics YOLO port, and academic
  detectors (MoE-HCO, RVT) — predominantly frames the ML component as a
  conventional CNN/Transformer operating on **accumulated event histograms/frames**
  (fixed-duration event accumulation windows converted to a tensor), not as an
  online multi-timestep SNN reading raw asynchronous events one at a time. This is
  the same "accumulate events into a frame/histogram, then run a quantized CNN"
  pattern consistent with Akida's own documented CNN2SNN deployment path. **[vendor
  material / preprint]** — Prophesee Metavision SDK docs
  (docs.prophesee.ai/stable/tutorials/ml/inference/detection_and_tracking.html);
  Wang et al., "Object Detection using Event Camera: A MoE Heat Conduction Based
  Detector and a New Benchmark Dataset," 2025,
  https://www.prophesee.ai/2025/03/13/object-detection-using-event-camera-a-moe-heat-conduction-based-detector-and-a-new-benchmark-dataset/

---

## 11. Claim-by-claim evidence classification (E1–E5)

| Claim | Class | Basis |
|---|---|---|
| AKD1000 architecture/specs (process node, clock, memory, interfaces) | E4 | Vendor datasheets, internally consistent across years |
| Akida squashes rate-coded ReLU into a single timestep, step-wise quantized ReLU | E3/E4 → corroborated by E1 deployments | arXiv:2403.10677 (E1, real hardware run), arXiv:2505.11418 (E1, real hardware run), author's repo (E3, code-level), CNN2SNN source (E4, mechanism) |
| Akida vs. Jetson Orin NX power/latency on MNIST (IIoT paper) | **E1** | Azadi et al. 2025, real-plug power measurement, real hardware inference timing |
| Akida vs. Loihi 2 on TON-IoT cybersecurity dataset | E2 (accuracy) claimed E1 (power) but **vendor-authored, not independently reproduced** | BrainChip white paper — treat as marketing claim, not verified |
| EuroSAT / space-applications Akida energy characterization | **E1** | Lunghi et al. 2025, AKD1000's built-in power-reporting used directly |
| EEG/neuromodulation Akida deployment | E2 (accuracy/quantization scheme documented; latency/energy not detailed in excerpt gathered) | Herbozo Contreras et al. 2025 |
| Rank order coding lineage (Thorpe/SpikeNet → BrainChip) | E4 (documented history, non-hardware) | akida.io/story, Thorpe et al. peer-reviewed papers |
| MorphIC ROC vs. rate-coding energy comparison | **E1** (but not Akida silicon — a different academic ASIC) | Frenkel et al., arXiv:1904.08513 |
| TENN as SSM/polynomial-kernel model, not yet spiking | E5 (software-level architectural characterization; PLEIADES benchmarks are E1/E2 on non-Akida hardware, GPU-trained) | tenns-core repo, PLEIADES paper, TENNs whitepaper |
| AKD1500 commercial shipment / revenue figures | E2-adjacent (self-reported by company, not independently audited in this research pass) | BrainChip press releases, financial commentary sites |
| Prophesee+Akida 2 event-camera gesture demo | E4 (demo announced; no independent latency/energy measurement found) | Joint press release |

---

## Source list

**Peer-reviewed:**
- Thorpe, Fize, Marlot, "Speed of processing in the human visual system," *Nature* 381, 520–522 (1996).
- Thorpe & Gautrais, "Rank Order Coding," in *Computational Neuroscience: Trends in Research 1998*, Plenum Press, 113–118.
- Thorpe, Delorme, Van Rullen, "Spike-based strategies for rapid processing," *Neural Networks* 14(6-7), 715–725 (2001). https://cerco.cnrs.fr/pagesp/arno/mypapers/ThorpeSpiking_Neurons.pdf
- Van Rullen & Thorpe, "Rate Coding Versus Temporal Order Coding: What the Retinal Ganglion Cells Tell the Visual Cortex," *Neural Computation* 13(6), 1255–1283 (2001). https://doi.org/10.1162/08997660152002852
- Gautrais & Thorpe, "Rate coding versus temporal order coding: a theoretical approach," *Biosystems* 48(1-3), 57–65 (1998).
- Delorme & Thorpe, "SpikeNET: an event-driven simulation package for modelling large networks of spiking neurons," *Network: Computation in Neural Systems* 14(4), 613–627 (2003). https://doi.org/10.1088/0954-898X/14/4/301
- Delorme, Guyonneau, Guilbaud, Allegraud, VanRullen, "SpikeNet: real-time visual processing with one spike per neuron," *Neurocomputing* (2004). https://doi.org/10.1016/j.neucom.2004.01.138
- Bonilla, Gautrais, Thorpe, Masquelier, "Analyzing time-to-first-spike coding schemes: A theoretical approach," *Frontiers in Neuroscience* (2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC9548614/
- Portelli et al., "Rank Order Coding: a Retinal Information Decoding Strategy Revealed by Large-Scale Multielectrode Array Retinal Recordings." https://pmc.ncbi.nlm.nih.gov/articles/PMC4891767/
- Frenkel, Legat, Bol, "MorphIC: A 65-nm 738k-Synapse/mm² Quad-Core Binary-Weight Digital Neuromorphic Processor with Stochastic Spike-Driven Online Learning," arXiv:1904.08513. https://ar5iv.labs.arxiv.org/html/1904.08513
- Azadi, Anzengruber-Tanase, Sopidis, Haslgrübler, Ferscha, "Towards an Energy-Efficient and Sustainable IIoT using Embedded Neuromorphic AI" (2025), DOI 10.1145/3770501.3770529.
- Vanarse, Osseiran, Rassau, van der Made, "A Hardware-Deployable Neuromorphic Solution for Encoding and Classification of Electronic Nose Data," *Sensors* 19(22), 4831 (2019). https://doi.org/10.3390/s19224831

**Preprint:**
- Lunghi, Silvestrini, Dold, Meoni, Hadjiivanov, Izzo, "Energy efficiency analysis of Spiking Neural Networks for space applications," arXiv:2505.11418. https://arxiv.org/abs/2505.11418
- Ziegler, Vetter, Gossard, Tebbe, Otte, Zell, "Detection of Fast-Moving Objects with Neuromorphic Hardware," arXiv:2403.10677 (v1 and v2). https://arxiv.org/abs/2403.10677
- Chen et al., "TENNs-PLEIADES: Building Temporal Kernels with Orthogonal Polynomials," arXiv:2405.12179. https://arxiv.org/html/2405.12179v3
- Herbozo Contreras, Yu, Huang, Aguilar, Nikpour, Kavehei, "Neuromorphic Neuromodulation: A Low-Power Edge-Training Framework for the Future of Personalized and Closed-Loop Neurostimulation," medRxiv 2025.09.22.25336341. https://www.medrxiv.org/content/10.1101/2025.09.22.25336341v1

**Official documentation:**
- BrainChip MetaTF docs, QuantizeML user guide. https://doc.brainchipinc.com/user_guide/quantizeml.html
- BrainChip MetaTF docs, CNN2SNN user guide. https://doc.brainchipinc.com/user_guide/cnn2snn.html
- BrainChip MetaTF docs, CNN2SNN API reference. https://doc.brainchipinc.com/api_reference/cnn2snn_apis.html
- BrainChip MetaTF docs, Akida user guide (layers, edge learning). https://doc.brainchipinc.com/user_guide/akida.html
- BrainChip Akida Examples docs, CNN2SNN advanced tutorial (BN-fold-into-threshold statement). https://brainchip-inc.github.io/akida_examples_2.9.0-doc-1/user_guide/cnn2snn.html
- BrainChip Akida 2.0 hardware capabilities page. https://doc.brainchipinc.com/user_guide/hardware/2.0.html

**Repository state (primary source, author's own hands-on work — treated as ground truth for toolchain behavior):**
- `/Users/hamza/Documents/GitHub/BrainChip_Akida/README.md`
- `/Users/hamza/Documents/GitHub/BrainChip_Akida/AKIDA_V1_CONSTRAINTS.md`
- `/Users/hamza/Documents/GitHub/BrainChip_Akida/AKIDA_V1_CONSTRAINTS_COMPACT.md`
- `/Users/hamza/Documents/GitHub/BrainChip_Akida/Akida_links.txt`
- `/Users/hamza/Documents/GitHub/BrainChip_Akida/cnn2snn-2.19.1/` (BrainChip's own `cnn2snn` 2.19.1 source, Apache 2.0, with local diagnostic additions) — specifically `cnn2snn/quantizeml/outputs.py` (`set_output_v1_variables`) and `cnn2snn/quantizeml/activations.py` (`parse_relu_v1`, `v1_relu_checks`)
- BrainChip-Inc/tenns-core (public GitHub). https://github.com/Brainchip-Inc/tenns-core
- s-valdivia-vasquez/ARACHNID-system (public GitHub, independent). https://github.com/s-valdivia-vasquez/ARACHNID-system

**Vendor material:**
- BrainChip, Akida AKD1000 SoC Product Brief V2.3. https://brainchip.com/wp-content/uploads/2025/08/Akida-AKD1000-SoC-Product-Brief-V2.3-Aug.25.pdf
- BrainChip, "What Is the Akida" tech brief v3. https://brainchip.com/wp-content/uploads/2020/03/BrainChip_tech-brief_What-is-Akida_v3-1.pdf
- BrainChip, "What Is the Akida Event Domain Neural Processor?" https://brainchip.com/case-studies/what-is-the-akida-event-domain-neural-processor/
- BrainChip, Akida 1.0 IP Product Brief. https://brainchip.com/wp-content/uploads/2022/06/Akida-1.0-IP-Product-Brief_final.pdf
- BrainChip, Akida 2 IP Product Brief V2.0. https://brainchip.com/wp-content/uploads/2025/04/Akida-2-IP-Product-Brief-V2.0-1.pdf
- BrainChip, second-generation IP Platform Brief. https://brainchip.com/wp-content/uploads/2023/03/BrainChip_second_generation_Platform_Brief.pdf
- BrainChip, "Introducing Akida" Linley presentation, 2019. https://brainchip.com/wp-content/uploads/2019/10/BrainChip-Linley-Akida-Presentation_v5.pdf
- BrainChip Investor Portal, Akida NSoC architecture announcement, Sept. 2018. https://investor.brainchip.com/brainchip-announces-the-akida-architecture-a-neuromorphic-system-on-chip/
- BrainChip, "The advantages of Unified Deep Learning technology" whitepaper. https://brainchip.com/wp-content/uploads/2023/03/The_advantages_of_Unified_Deep_Learning_technology.pdf
- BrainChip, "A Game Changer in AI Computing for Cybersecurity" white paper. https://brainchip.com/wp-content/uploads/2025/01/BrainChip_White-Paper-A-Game-Changer-in-AI-Computing-for-Cybersecurity_v3.pdf
- BrainChip, AKD1500 Product Brief V2.4. https://brainchip.com/wp-content/uploads/2025/11/AKD1500-Product-Brief-V2.4-Oct.25.pdf
- BrainChip press release, AKD1500 commercial availability, June 30 2026. https://brainchip.com/press/brainchip-announces-commercial-availability-and-production-shipments-of-akd1500-neuromorphic-processors/
- BrainChip, AKD1500 GlobalFoundries tape-out press release, Jan 2023. https://brainchip.com/press-releases/brainchip-tapes-out-akd1500-chip-in-globalfoundries-22nm-fd-soi-process/
- BrainChip, Akida Pico Brochure. https://brainchip.com/wp-content/uploads/2024/10/BC_Akida-Pico-Brochure.pdf
- BrainChip, Chips overview page. https://brainchip.com/chips/
- BrainChip, IP overview page. https://brainchip.com/ip/
- BrainChip, Dev Tools page. https://brainchip.com/dev-tools/
- BrainChip shop. https://shop.brainchipinc.com/
- BrainChip, "BrainChip Achieves Full Commercialization of AKD1000," Jan 2022. https://brainchip.com/brainchip-achieves-full-commercialization-akd1000/
- BrainChip, DigiKey distribution partnership press release, Sept 2025. https://brainchip.com/brainchip-expands-global-reach-announces-akida-boards-and-ai-development-kits-available-at-digikey/
- BrainChip, "Upgrade the Raspberry Pi for AI with a Neuromorphic Processor." https://brainchip.com/upgrade-the-raspberry-pi-for-ai-with-a-neuromorphic-processor/
- BrainChip, TENNs Whitepaper. https://brainchip.com/wp-content/uploads/2023/06/TENNs_Whitepaper_Final.pdf
- BrainChip blog, "BrainChip Introduces Temporal Event-Based Neural Networks," June 2023. https://brainchip.com/temporal-event-based-neural-networks-a-new-approach-to-temporal-processing/
- BrainChip blog, "Introducing TENN: Energy-Efficient Transformer." https://brainchip.com/introducing-tenn-revolutionizing-computing-with-an-energy-efficient-transformer-replacement/
- BrainChip / Edge AI Vision, "Temporal Event Neural Networks: A More Efficient Alternative to the Transformer," 2024. https://www.edge-ai-vision.com/wp-content/uploads/2024/06/E1R07_Jones_Brainchip_2024.pdf
- BrainChip / Wedbush investor portal, Prophesee event-vision demo press release, March 2025. https://investor.wedbush.com/wedbush/article/bizwire-2025-3-10-brainchip-demonstrates-event-based-vision-at-embedded-world-2025
- akida.io, "The Brainchip Story - 2016 to December 2020." https://akida.io/story
- BrainChip, "BrainChip Awarded Patent for AI Dynamic Neural Network," 2019. https://brainchip.com/brainchip-awarded-new-patent-for-artificial-intelligence-dynamic-neural-network/
- BrainChip, "BrainChip Earns Australian Patent for Improved Spiking Neural Network," 2024. https://brainchip.com/brainchip-earns-australian-patent-for-improved-spiking-neural-network/
- US Patent US20170024644A1, "Neural processor based accelerator system and method." https://patents.google.com/patent/US20170024644A1/en
- Edge Impulse / BrainChip joint docs, industrial inspection with Akida. https://docs.edgeimpulse.com/projects/expert-network/brainchip-akida-industrial-inspection
- CNX Software, "BrainChip AKD1000 SNN AI SoC gets Raspberry Pi and x86 development kits," Oct 2021. https://www.cnx-software.com/2021/10/22/brainchip-akd1000-snn-ai-soc-gets-raspberry-pi-and-x86-development-kits/
- Prophesee Metavision SDK docs, detection & tracking tutorial. https://docs.prophesee.ai/stable/tutorials/ml/inference/detection_and_tracking.html
- Prophesee, "Object Detection using Event Camera: A MoE Heat Conduction Based Detector," 2025. https://www.prophesee.ai/2025/03/13/object-detection-using-event-camera-a-moe-heat-conduction-based-detector-and-a-new-benchmark-dataset/

**Community commentary (explicitly labeled, not treated as verified fact):**
- Open Neuromorphic, "A Look at Akida - BrainChip - Neuromorphic Chip." https://open-neuromorphic.org/neuromorphic-computing/hardware/akida-brainchip/
- Bryon Moyer, "Spiking Neural Networks: Research Projects or Commercial Products?", Semiconductor Engineering, May 2020. https://semiengineering.com/spiking-neural-networks-research-projects-or-commercial-products/
- Equity.Guru, "BrainChip (ASX.BRN): Big promises, marketing slop, and an AI company that missed the AI boom," Nov 2025. https://equity.guru/2025/11/21/brainchip-asx-brn-big-promises-marketing-slop-and-an-ai-company-that-missed-the-ai-boom/
- AInvest, "BrainChip Keeps Printing Shares While the Neuromorphic Clock Runs Down," July 2026. https://www.ainvest.com/news/brainchip-printing-shares-neuromorphic-clock-runs-2607/
- AInvest, "BrainChip Finally Ships Silicon. A Year of Cash Decides What Happens Next.", Sept 2026. https://www.ainvest.com/news/brainchip-finally-ships-silicon-year-cash-decides-2609/
- NewsCase, "BrainChip Ships Its First Commercial Processors, But the Financial Hole Deepens," Aug 2026. https://www.newscase.com/brainchip-ships-its-first-commercial-processors-but-the-financial-hole-deepens/
- koalagains.com, BrainChip (BRN) stock analysis, Feb 2026 (financial-analysis site, unverified against primary filings). https://koalagains.com/stocks/ASX/BRN
- flash.stocksentinel.ai, BrainChip Holdings research report, May 2026. https://flash.stocksentinel.ai/research/BRN.AX
- HotCopper forum threads (ASX retail-investor board), various 2024–2026 threads on AKD1000/AKD1500 sales, Akida Pico, and management execution concerns. https://hotcopper.com.au/threads/how-can-brainchip-turn-around-from-here.8999768/ ; https://hotcopper.com.au/threads/ibm-akd1000.9004561/ ; https://hotcopper.com.au/threads/the-elephant-in-the-room.8552218/ ; https://hotcopper.com.au/threads/akida-pico.8237888/
- RobotToday, BrainChip company profile, Aug 2026. https://robottoday.com/suppliers-discovery/brainchip

---

## Open questions / NOT FOUND

1. Whether Akida's **native SNN mode** (STDP-trained from scratch, as distinct from
   the QuantizeML/CNN2SNN converted-CNN mode used in essentially all cited
   benchmarks) implements a genuine order-sensitive ROC readout mechanism inside
   hidden layers. No source examined characterizes native-mode neuron dynamics at
   this level of mechanistic detail.
2. Whether general (non-Edge-Learning) Akida events/spikes can carry negative
   values, or are strictly non-negative magnitudes.
3. A controlled, same-silicon comparison of rate-coded vs. rank/order-coded
   execution *on Akida hardware itself* (the MorphIC data in §4.4 is a different
   chip).
4. Mechanistic detail (neuron model, encoding, timestep structure) of the Akida-2/
   Prophesee gesture-recognition demo internals.
5. Independently-audited BrainChip revenue/shipment figures (all figures gathered
   here are either self-reported by BrainChip or drawn from financial-commentary
   sites, not verified against primary ASX filings in this research pass).
6. A specific, named, currently-shipping end product (beyond dev boards/reference
   designs) that contains an Akida chip.
7. Whether the reported "10x Akida 1500 is a modified Akida 1000 core" characterization (a forum claim) is accurate — not checked against BrainChip engineering documentation.
