# 8 Challenges and Future Directions

Each subsection below is a seam: a point where a trained network passes from one layer of the
stack to the next and something is lost. Each becomes a numbered pin in the survey's main figure,
linking the layer bands to the specific mechanism that breaks at that handoff.

## 8.1 Operator coverage in SNN toolchains

Every documented software path from a trained network to physical silicon accepts a narrower set
of operators than a standard vision CNN uses, and closing the gap is architectural rewriting, not
configuration.

SpikingJelly's `lava_exchange` module, the only first-party bridge from SpikingJelly to Loihi,
dispatches on layer type and handles exactly four cases: `nn.Linear`, `nn.Conv2d`, `nn.AvgPool2d`
(rewritten internally as a Lava `SumPool2d`), and `nn.Flatten`. Anything else raises
`ValueError(type(net[i]))` or `NotImplementedError(type(net[i]))` [fang-2023-spikingjelly-lava]
[jelly-lava-source]. A VGG-family network hits this immediately, since VGG's canonical pooling is
`nn.MaxPool2d`, which the dispatch does not handle. A ResNet hits it at every residual addition,
since no elementwise-add or skip-connection handling appears in the operator dispatch, and again
at any `BatchNorm2d` layer not already fused away before export [jelly-lava-source]. The module
also asserts no bias term on exported `Conv2d`/`Linear` layers and rejects any LIF neuron with
`decay_input=True` [jelly-lava-source].

Sinabs, SynSense's PyTorch library for the Speck/DYNAP-CNN line, has no built-in BatchNorm
folding. Its `DynapcnnLayer` template is fixed to a `conv → spike → pool` sequence, and the
`discretize` module's public functions (`discretize_conv`, `discretize_conv_spike`,
`discretize_spk`) operate only on `(Conv2d, IAF)` pairs; there is no `discretize_bn` or `fold_bn`
counterpart [sinabs-discretize-api]. Sinabs's own hardware-targeted tutorials avoid the problem
by construction, building bias-free convolutional layers followed directly by IF layers with no
BatchNorm in the architecture at all, which places the burden of BN removal on the user before the
model reaches `from_model()` [sinabs-nmnist-tutorial]. A `Conv2d` bias, where present, is
repurposed on-chip as the per-timestep leak current rather than an ordinary additive bias, a
further departure from what a standard trained CNN expects [sinabs-nmnist-tutorial].

BrainChip's Akida, evaluated here only as a constraint-list illustration and not as a deployment
target this survey otherwise covers, documents perhaps the most exhaustive operator contract of
any platform reviewed. Input width must fall between 5 and 256 pixels; exceeding 256 forces the
convolutional layers back onto software execution, a silent performance cliff rather than a hard
failure. Input channels are restricted to 1 or 3. Activations must be a bounded ReLU
(`ReLU(max_value=6.0)`) expressed as a separate layer; an unbounded `QuantizedReLU` raises
`ValueError: unbounded QuantizedReLU is not supported in AkidaVersion.v1`. All convolutional
layers after the first must use `'same'` padding only, a `'valid'`-padded intermediate layer
raises `RuntimeError`, and no dilated or grouped convolutions are supported at all. Dense layers
must receive a spatially flattened input, with total input features capped at 57,334
[akida-hw-constraints]. This is the contract of a quantized, integer-only CNN accelerator with a
strict graph-compiler front end, comparable in spirit to a TFLite Micro or TensorRT deployment
target, not a general-purpose spiking-network simulator willing to accept an arbitrary topology
[akida-hw-constraints].

The older SNN Toolbox pipeline, by contrast, supports max-pooling natively, offering a choice of
three spiking approximations (`fir_max`, `exp_max`, `avg_max`), and extracts BatchNorm parameters
directly from the source Keras layer for fusion into the preceding convolution
[rueckauer-2017-frontiers] [snntoolbox-docs]. Its operator coverage is broader on exactly the two
axes (max-pooling, BatchNorm) that the newer, purpose-built export paths above either drop or push
back onto the user. No toolchain surveyed accepts a standard VGG or ResNet as trained; every one
requires either an architectural rewrite before conversion (avg-pool in place of max-pool, no
BatchNorm, bounded activations, same-padding-only convolutions) or a bespoke translation step
after it.

## 8.2 Reset-semantics mismatch

This is the sharpest finding in the survey. ANN-to-SNN conversion under IF neurons requires reset
by subtraction, not reset to a fixed value. Rueckauer et al. derive analytically that reset to zero
discards a systematic, input-dependent residual charge at every spike, a bias that compounds
across layers rather than averaging out with longer simulation; reset by subtraction instead
carries that residual into the next integration window, and the firing-rate estimator converges
exactly to the target ReLU activation as `T → ∞` [rueckauer-2017-frontiers]. Their own CIFAR-10
ablation, switching only the reset mechanism while holding Poisson input and weight normalization
fixed, improves accuracy by roughly twenty percentage points [rueckauer-2017-frontiers]. This
result is now treated as settled practice throughout the conversion literature
[wang-2023-ijcai-snm] [hao-2023-aaai-srp].

Despite this, the interoperability layer built after the fact does not carry the mechanism. NIR's
own primitive specification defines the reset rule for its Integrate-and-Fire and LIF primitives
as reset to a fixed target value (`v ← v_reset` if spiking, `v` otherwise); the published primitive
table contains no subtract-reset primitive [pedersen-2024-nir]. The gap is not theoretical.
snnTorch's neuron classes internally implement subtract-reset but historically exported
`v_reset = 0` to NIR, silently discarding the distinction, a bug tracked in two separate pull
requests against the reference exporter [snntorch-pr-388] [snntorch-pr-426]. SpikingJelly's own
exporters go further and refuse the case outright: `lava_exchange.py` raises `ValueError('lava
only supports for v_reset == 0!')` at five separate call sites, and asserts the same for its
`CubaLIFNode` path; its `nir_exchange/to_nir.py` raises `NotImplementedError("NIR does not
distinguish soft reset.")` whenever `v_reset is None` [jelly-lava-source] [jelly-nir-source]. A
network converted by SpikingJelly's own `ann2snn` module, which itself defaults to soft reset,
cannot be handed to either of SpikingJelly's own export modules without either re-parameterizing
to hard reset, and reintroducing the twenty-point cost above, or writing new code
[jelly-lava-source].

On hardware, the picture splits three ways. Loihi 1 and Loihi 2 hard-reset the membrane voltage to
zero natively, in a single compartment [pehle-2022-bmtk]. NxTF's compiler works around this with a
two-compartment neuron: one compartment plays the soma, the second is recurrently connected and
activates only once the soma crosses threshold, then inhibits the soma by an amount equal to the
threshold, reproducing subtraction at the cost of doubling the compartment count per neuron
[rueckauer-2022-nxtf]. The paper's own authors recommend that future hardware add a built-in soft
reset specifically to eliminate this duplication [rueckauer-2022-nxtf]. SpiNNaker is not
hard-wired to either mode; its ARM cores are fully software-programmable, and a
`neuron_model_has_spiked()` callback lets a user implement subtraction in a custom C neuron model,
but this is not one of sPyNNaker's built-in cell types (`IF_curr_exp` and its relatives use
conventional PyNN hard-reset semantics), so soft reset on SpiNNaker means writing and compiling a
bespoke neuron kernel [spinnaker-neuron-lab-manual]. BrainScaleS-2's native analog AdEx circuit
clamps the membrane to a fixed reset potential for a refractory period on every spike, a hard reset
by construction; no source describes a native or workaround soft-reset mode on BrainScaleS-2,
despite the chip's otherwise extensive multi-compartment capability, which is used there for
genuine dendritic computation rather than as a reset workaround [pehle-2022-brainscales-multicomp].

Native support exists in three places. TrueNorth's digital neuron model implements a "linear mode"
reset as a first-class, natively configurable hardware option, in which the residual potential
above threshold is not discarded but carried forward exactly as reset-by-subtraction requires
[truenorth-neuron-model]. Speck/DYNAP-CNN exposes the choice as a single hardware register,
`return_to_zero`; `False` selects subtractive reset and is the devkit's documented default, with
SynSense's own guidance explicitly directing ANN-to-SNN conversion users to that setting
[speck-devkit-manual]. FPGA-targeted SNN accelerator generators (Spiker+, SIA) support subtractive
reset as a synthesizable, and in SIA's case preferred, option because it measurably improves
classification accuracy [spiker-plus-fpga] [sia-fpga]. Sinabs, the software library targeting
Speck, defaults its `IAF` layer to `MembraneSubtract()`, matching the hardware default
[sinabs-discretize-api]. Taken together, the mechanism proven worth roughly twenty accuracy points
is the single most consistently dropped feature across every interoperability path to accessible
hardware surveyed in this report.

## 8.3 Input encoding and output readout

Direct (analog, constant-current) input encoding applies the raw, real-valued input at every
timestep as a constant current to the first hidden layer, rather than first converting it into a
spike train. Rueckauer et al. introduce this explicitly as one of three mechanisms, alongside
reset-by-subtraction and robust weight normalization, that close the ANN-SNN accuracy gap:
replacing Poisson spike-train input with constant analog current for the first layer alone raised
CIFAR-10 accuracy from roughly 59.8 percent to 83.6 percent, holding weight normalization and
reset-to-zero fixed [rueckauer-2017-frontiers]. Deterministic count coding under a fixed threshold
achieves quantization error that scales as `1/T`, while Poisson coding's variance scales only as
`1/√T`, so Poisson input needs quadratically more timesteps for equivalent precision
[auge-2021-encoding-survey]. This is the direct reason essentially all modern low-latency
conversion work, including the QCFS lineage, uses direct encoding at the input layer rather than
Poisson.

The consequence for hardware is that the first layer is, in effect, an ANN layer. Because its
computation is a real-valued multiply-accumulate rather than an accumulate over binary spikes, it
forfeits the accumulate-only efficiency the rest of the network enjoys; one Eyeriss-scale energy
study measured rate coding costing roughly fifty percent less energy than direct coding
specifically because the direct-encoded first layer carries sixteen-bit precision
[kim-2022-rate-vs-direct]. Toolchains that document this explicitly route the first layer off the
spiking core entirely: Nengo-Loihi's own tooling notes that the input-encoding layer "should run
off-chip" [nengoloihi-cifar10-example], and FPGA accelerator designs place a conventional MAC array
ahead of the spiking core rather than attempt to spike it [spiker-plus-fpga]. No source located
confirms or denies whether Speck, Xylo, BrainScaleS-2, or SpiNNaker support a direct-encoded first
layer as a hardware-native path; there is no architectural reason it should be infeasible, since a
constant input current is a basic capability, but no worked deployment example was found, so the
gap is recorded as unconfirmed rather than assumed closed [kim-2022-rate-vs-direct].

Readout cost is not free either. SNN Toolbox's default output decoding is `temporal_mean_rate`,
spike count divided by `T`, with `temporal_pattern` and three TTFS-family variants offered as
alternatives [snntoolbox-docs]. TTFS decoding instead reads a winner-take-all over first-spike
time, or a learned temporal-weighting decoder over decayed contributions
[park-2020-t2fsnn]. The decision window is not a modeling abstraction; it is real latency paid on
the chip. NxTF's CIFAR-10 run on physical Loihi 1 required a 340 ms per-sample decision delay at
102 mJ per sample [rueckauer-2022-nxtf]. Quartz's TTFS conversion trades this differently: measured
on the same chip family, it reaches 0.9 µJ·s energy-delay product on MNIST against 4.38 µJ·s for a
rate-coded Loihi baseline, but its CIFAR-10 accuracy (25.14 percent error) is markedly worse than
the rate-coded NxTF result (8.52 percent error), even though the TTFS run uses far fewer total
spikes [lenz-2023-quartz]. Reducing the readout window is a real design axis with a real accuracy
cost, not a free efficiency lever.

## 8.4 Time-model mismatch

`T` names three physically different things depending on the platform. Under a synchronous tick,
exemplified by SynSense's own Xylo line, the hardware genuinely advances all state once per a
global `dt`; up to fifteen input events per channel and up to thirty-one output spikes per neuron
can be processed within a single tick, and `T` corresponds to a real, chip-wide clock edge
[rockpool-xylo-overview]. Under an asynchronous event stream, exemplified by SynSense's own Speck
line, there is no clock in the compute path at all: computation is triggered directly by changes
arriving at each block, communicated via a request/acknowledge protocol, and a measured per-layer
propagation latency of roughly 0.37 µs (3.36 µs across nine layers) is a hardware propagation
delay, not a multiple of any chosen simulation `Δt` [richter-2023-speck]. The paper's own
comparison table draws this out explicitly against clocked chips: "Loihi1/2 and TrueNorth... which
architecturally introduce a latency of one timestep `Δt` on event generation in each layer," a
delay stated as 1 ms for TrueNorth's clocked design [richter-2023-speck]. Under analog continuous
time, exemplified by BrainScaleS-2, the substrate runs accelerated, physical-model dynamics at
roughly ten-thousand times real time, with no discretized tick at all [dewolf-2020-nengo-loihi].

The Speck-versus-Xylo contrast is instructive precisely because it sits inside one vendor's product
line. On Xylo, a software `num_timesteps`/`dt` parameter is a hardware-level guarantee: the chip is
architecturally a synchronous time-stepped machine, and per-layer heterogeneous `T` is physically
impossible as currently built [rockpool-xylo-overview]. On Speck, the equivalent software parameter
(Sinabs's `num_timesteps`) exists only at the boundary where a discrete-time raster is converted
into individually timestamped address-event-representation spikes; past that conversion point the
chip has no notion of a timestep whatsoever, and it reacts continuously to each event's arrival
regardless of how many software timesteps were used to construct the input stream
[richter-2023-speck]. The only clocked element anywhere in the Speck2e-and-later compute path is an
auxiliary slow clock governing leak, DVS-filter, and readout-averaging behavior, not the
convolutional datapath itself [richter-2023-speck]. A `T` value reported in a software simulation
paper is therefore not a portable physical quantity across platforms, and on a fully event-driven
chip there may be no hardware `T` to map it onto at all.

## 8.5 Per-layer timestep horizons have no execution model

No framework surveyed expresses a per-layer timestep horizon, layer A running `T=2` while layer B
runs `T=4`, in a single forward pass. SpikingJelly drives every layer from one shared scalar `T`,
either through a user-written `for t in range(T)` loop in single-step mode or a shared `[T, N, *]`
tensor in multi-step mode [fang-2023-spikingjelly]. snnTorch, Norse, and Lava follow the identical
pattern: one external loop, one sequence length, one `RunSteps(total_run_time)` condition applied
to the whole compiled process graph [fang-2023-spikingjelly-lava] [lava-dl-docs]. Rockpool/Xylo
enforces this at the hardware level, not merely in software, since the chip is architecturally a
single global-clock machine (8.4). PyNN inherits whatever global-clock convention its chosen
backend uses. The underlying reason is architectural, stated most plainly in SpikingJelly's own
paper: because a stateful spiking layer's output at time `t` depends on hidden state carried from
`t-1, t-2, ..., 0`, "the for-loop concerning time steps is inevitable," and every framework builds
exactly one such loop per network, not one per layer [fang-2023-spikingjelly].

This is not merely a software-abstraction limit. NeuroScale (Li, Imam, and Manohar, *Nature
Communications* 16, 10329, 2025) confirms it architecturally for the four most-cited large-scale
digital neuromorphic platforms: "The TrueNorth system uses an externally controlled signal that is
distributed to all the hardware components of the architecture... typically operating with a
frequency of 1 kHz... Intel's Loihi and Loihi 2 architectures also implement barrier
synchronization to advance time. Tianjic uses a global clock for all its coordination processes,
including advancing time" [li-2025-neuroscale]. No core on any of these four chips can proceed past
tick `t` until every core has finished tick `t`; there is no hardware primitive corresponding to
"layer 3 is at tick 8 while layer 4 is still at tick 2" [li-2025-neuroscale].

Two papers that assign a different quantization step, and hence a different unrolled timestep
count, to each layer make the resulting cost explicit without resolving it. QAC's own
hardware-efficiency appendix states that under sequential dataflow-accelerator execution (one layer
computed at a time, iterating across the network), cost scales as `O(N·T)`, layers times timesteps,
a sum over layers, which is precisely QAC's own motivation for moving to mixed timesteps in the
first place [guo-2025-qac]. Under the alternative, pipelined multi-core execution that is the
standard model for chips like TrueNorth and Loihi, the same appendix states plainly: "Layer 2 must
wait until Layer 1 completes `T_l1` timesteps before it can start computation... pipeline stalling
may occur, introducing computational delays and preventing the hardware from achieving optimal
performance" [guo-2025-qac]. Under pipelining, the pipeline's overlap benefit is lost exactly at
the boundary between two layers of unequal horizon, so the effective latency again accumulates as a
sum, this time via stall rather than via sequential iteration. QAC's own headline number, 2.76
average timesteps for ResNet-18 on CIFAR-10, is computed as an unweighted mean across layers, not
either of these two costs, and the gap between the accuracy-optimized mean and the
hardware-realizable sum is flagged by the paper's own text but never closed [guo-2025-qac].
PASCAL's analogous `T_eff` of 3.14 for the same architecture and dataset is likewise a weighted
arithmetic mean over layers (Eq. 16), and PASCAL's own hardware section, RTL synthesis via Synopsys
Design Compiler at 40 nm and 560 MHz with a cycle-accurate simulator, validates only that its
modified IF neuron adds negligible overhead relative to a standard IF neuron at a single, uniform
`T=4`; it never synthesizes, simulates, or measures the mixed-timestep execution model that
produces the 3.14 headline [ramesh-2025-pascal]. No paper surveyed, PASCAL, QAC, or QAC's
ICLR-2026-withdrawn successor, performs RTL synthesis, cycle-accurate simulation, or a physical
chip run of the actual heterogeneous-`T` execution path itself.

The one physical deployment of heterogeneous timing found in this survey, Mixed Time-step Training
(Du, Wu, Deng, and Gu, ICLR 2025 poster), works only by targeting a timestep-free chip. MTT trains
a network whose stages are randomly assigned different `T` during training, so the resulting
weights transfer across many single global `T` values and onto a fully event-driven chip that has
no discrete tick to be heterogeneous about in the first place. Deployed on a Speck2e devkit, the
measured spike-difference between the training-time software simulator and the physical chip's
output is 3.92 percent, close to the 2.81 percent difference measured between two identical on-chip
runs, and far below the 28.77 percent difference between a conventional time-stepped simulator and
the chip's actual behavior [du-2025-temporal-flexibility]. This confirms physical deployment of a
temporally flexible model, not execution of a genuine `T_1 ≠ T_2 ≠ ... ≠ T_L` schedule on
synchronous silicon; the two problems, mixed-timestep training for cross-platform generalization
and per-layer heterogeneous-horizon execution, are only superficially related, and MTT's Speck2e
result is evidence for the former, not the latter.

## 8.6 Measurement boundaries and incomparable efficiency claims

SynOps is not joules. The per-operation energy figures nearly every SNN paper cites, roughly 0.9 pJ
for a multiply-accumulate against 0.1 pJ for an accumulate, trace to Mark Horowitz's ISSCC 2014
plenary talk, a table specific to a 45 nm process at 0.9 V [horowitz-2014-isscc]. The talk itself
states that a 32 KB SRAM access already costs 5 pJ, an off-chip DRAM access costs 640 pJ, and a
programmable processor's instruction fetch and register overhead adds roughly 70 pJ per
instruction, none of which a SynOps-times-constant estimate captures [horowitz-2014-isscc]. Three
independent hardware-realistic studies converge on the same conclusion from three different
angles. Bhattacharjee, Yin, Moitra, and Panda benchmark published SNN algorithms on two
hardware-realistic accelerator models (a sparsity-aware systolic array, an RRAM crossbar simulator)
and report that "the actual energy-efficiency improvements of recent SNN algorithmic works differ
significantly from their estimated values" [bhattacharjee-2023-hardware]. Shen, Zhao, Li, Li, and
Zeng propose replacing SynOps with a unified "Bit Budget" metric specifically because comparisons
against unquantized ANN baselines are not fair comparisons [shen-2024-cvpr]. Narduzzi, Zenke, Liu,
and Dunbar find that SynOps and spike-count metrics "fail to account for" membrane-update and
gating-dynamics overhead and propose an alternative, EFLOP, that does [narduzzi-2025-eflop]. None
of these are marginal corrections; all three report the gap between the SynOps estimate and
measured hardware energy as large and systematic.

Static power dominates, so cutting `T` does not cut energy proportionally. On Loihi 2, a sigma-delta
conversion study reports total power "remained relatively consistent for all experiments as it is
dominated by static draw," even as throughput rose from 176 to 362 frames per second with
increasing sparsity [brehove-2026]. A separate Loihi 2 study of the Locally Competitive Algorithm
shows static power nearly constant (approximately 0.54 W) across sparsity settings while dynamic
power varies only modestly (0.17 to 0.39 W), so at the sparsest, most favorable operating point,
static power still exceeds dynamic power [lca-loihi2-2023]. No source in this survey sweeps `T`
alone on identical silicon holding everything else fixed, but the underlying mechanism, an
SRAM-per-core design that draws static power continuously regardless of whether a given tick
performs useful spiking work, is confirmed independently by both studies; reducing `T` shrinks only
the dynamic term, and can even raise energy per inference if the reduction also lowers achievable
throughput.

Boundary choice alone produces order-of-magnitude swings. Shrestha, Timcheck, Frady, Campos-Macías,
and Davies report, for the identical Loihi 2 chip and identical PilotNet network, 0.09 mJ total
energy and 1.21 ms latency per frame when host I/O is excluded from the measurement window (weights
pre-staged), against 1.26 mJ and 65.41 ms when streaming from the host is included, a fourteen-fold
energy difference and a fifty-four-fold latency difference from the boundary choice alone
[shrestha-2023-loihi2]. In the host-inclusive configuration, over ninety-four percent of the
reported energy is static leakage, not spiking computation [shrestha-2023-loihi2]. Other boundary
choices swing the number further: ANN baseline energy on the same Jetson Orin Nano differs by
roughly 3.5 times between batch sizes one and sixteen; input-encoding circuitry (the Poisson
spike-generator itself) is frequently excluded from rate-coded SNN energy totals, though one
sixteen-bit Eyeriss-scale study costs it explicitly and finds it material
[kim-2022-rate-vs-direct]; and quantizing the ANN comparison baseline from fp32 to int8 on the same
Jetson cuts its energy by roughly thirty-seven percent and its energy-delay product by roughly
sixty-three percent, narrowing without eliminating the reported SNN advantage
[shrestha-2023-loihi2]. The field itself names the underlying cause structurally rather than
accidentally: NeuroBench identifies "lack of a formal definition," "implementation diversity" (no
ONNX-equivalent exchange format for SNNs), and "rapid research evolution" as the three reasons a
single enforced measurement protocol is currently infeasible, and settles for transparency and
reporting guidelines instead of a strict standard [yik-2025-neurobench].

## 8.7 Device availability and toolchain decay

SNN Toolbox's last PyPI release, v0.6.0, shipped 2021-03-17; its last substantive code commits date
to August 2022 (a kernel-conversion slicing fix, a deprecated GUI import fix); one further,
documentation-only commit in January 2023 adds a citation, and no commit has been found after
[snntoolbox-github]. The issue tracker was still answered personally by the maintainer into 2024,
but with an explicit admission of reduced capacity ("I won't be able to help much with debugging at
this point"), and no issue in the tracker ever requests a feature from the post-2020, QCFS-family
literature [snntoolbox-issues].

Intel archived all Lava repositories on 13 May 2026: "Intel is developing the next-generation Loihi
architecture and SDK to power the coming era physical AI... All Lava repositories are archived.
Stay tuned for announcements about our new SDK and next generation Loihi processor"
[lava-dl-readme]. No patches are accepted and no maintenance is offered; a successor SDK is named
only as forthcoming, with no release as of this survey. NxTF's own host repository,
`intel-nrc-ecosystem/models`, which carries the only bridge between SNN Toolbox and NxTF, carries a
blanket "DISCONTINUATION OF PROJECT" notice, and Intel's own INRC guidance has redirected users to
Lava for Loihi 2 development since 2022, treating NxSDK and NxTF as Loihi-1-era and superseded even
before Lava's own archival [inrc-loihi-access] [nxsdk-models-repo]. Loihi 1 itself is superseded
hardware, not the current INRC access target.

Access to this hardware is gated, while the hardware that supports reset-by-subtraction natively is
not. Loihi 1 and 2 access runs through INRC membership, behind a research proposal and
participation agreement, not a guaranteed or open channel [inrc-loihi-access]; BrainScaleS and
SpiNNaker access runs through EBRAINS's queued-job Neuromorphic Computing Platform
[hbp-guidebook]. Speck, by contrast, was presold as a 199 US dollar demo kit, and its dev kit is
sold through an ordinary sales channel with no described approval process; Xylo development kits
are likewise commercially purchasable [speck-devkit-manual]. The two toolchains with the deepest
published CNN-scale conversion results in this survey, SNN Toolbox through NxTF to Loihi 1, and
Lava-DL's NetX to Loihi 2, sit behind the least accessible, least currently maintained
software-hardware combination surveyed. Reproducing NxTF's own published CIFAR-10 result on Loihi 1
today would require pinning software Intel no longer distributes support for, against a chip
Intel's own current community guidance no longer directs new users toward.

## 8.8 Interoperability and the portability gap

NIR's reach is genuine and, among the interchange formats surveyed, unmatched. Nine simulators
write and or read NIR (hxtorch and jaxsnn for BrainScaleS-2, Lava-DL read-only, Nengo, Norse,
Rockpool, Sinabs, snnTorch, SpiNNaker2 read-only, and Spyx), reaching five physical hardware
platforms: BrainScaleS-2, Loihi 2, Speck, SpiNNaker2, and Xylo, up from the seven simulators and
four hardware platforms reported at initial publication [pedersen-2024-nir]. This reduces what
would otherwise be an `m × n` interoperability problem, every framework needing a bespoke exporter
to every chip, to `m + n`: every framework needs only one NIR exporter, and every chip needs only
one NIR importer [pedersen-2024-nir].

The paper's own hardware validation shows where this degrades. Cross-platform agreement is reported
as faithful for feedforward dynamics, a single LIF neuron and a spiking convolutional network with
IF neurons, but diverges for a recurrent current-based LIF network, where the authors state
explicitly that reaching the highest accuracy required "platform-dependent optimization, such as
quantization-aware training" [pedersen-2024-nir]. NIR by itself does not guarantee bit-accurate
transfer even for the model classes it covers well. And it stops well short of the full primitive
space a conversion paper needs: its own stated limitations exclude adaptive-threshold mechanisms,
gating, resonate-and-fire, and multicompartmental neuron models from the current primitive set, and
its own porting guide permits a hardware backend to simply ignore an unsupported node rather than
approximate it, with approximation strategies for such cases listed as future work, not implemented
[pedersen-2024-nir] [nir-porting-guide]. Section 8.2 documents the same gap for reset by
subtraction specifically.

No universal exporter exists because every hardware deployment surveyed required nontrivial,
platform-specific rewriting on top of whatever the interchange format carried. Per-neuron
thresholds are collapsed to a single value per layer for Speck, whose hardware does not support
individual per-neuron parameters [sinabs-nmnist-tutorial]. `Linear` layers are rewritten as `1×1`
`Conv2d` layers and `AvgPool2d` as `SumPool2d` to fit a fixed per-core template
[jelly-lava-source]. Multi-core targets require explicit per-core neuron-count partitioning. A
working IR handoff is therefore a starting point for hand adaptation, not a drop-in compile step,
and framework-native export paths compound the problem: SpikingJelly's own `lava_exchange` and
`nir_exchange` modules both reject the soft-reset neurons its own `ann2snn` converter produces by
default, so a model converted by one first-party SpikingJelly module cannot be handed to another
first-party SpikingJelly export module without either reintroducing the reset-related accuracy cost
documented in 8.2 or writing new code [jelly-lava-source] [jelly-nir-source].

No QCFS-to-silicon route is asserted by any source reviewed. The nearest analogues are, first,
NxTF and SNN Toolbox to Loihi 1, which realizes the same conversion family, rate-coded IF neurons
under reset by subtraction, on physical hardware, but not QCFS's specific clip-floor-shift
activation or learnable per-layer threshold [rueckauer-2022-nxtf]; and second, APEX and its
predecessor PASCAL, which are QCFS-specific in their neuron design but target a synthesized,
simulated accelerator, not fabricated, accessible silicon [ramesh-2025-pascal].

## 8.9 The two-population division of labor

Thirteen QCFS-lineage papers audited directly against full text report E5, pure software
simulation, for thirteen of thirteen of their own experiments; zero report a run on a named chip.
Twelve of the thirteen cite neuromorphic hardware only as generic architecture-paper motivational
material, Davies 2018 for Loihi, Akopyan 2015 for TrueNorth, in their introductions, never in
methods or experiments. QCFS itself is the sole partial exception, citing two genuine
physical-silicon deployment papers, Massa et al. 2020 and Singh et al. 2021, as acknowledged prior
art in its related work section rather than as introductory motivation [bu-2022-qcfs].

The deployment side mirrors this. Four hardware-deployment papers audited (Stromatias 2015,
Patiño-Saucedo 2020, Massa 2020, and NxTF 2021/2022) use zero post-2020 low-latency conversion
methods between them; every one runs SNN Toolbox's classical threshold-balancing pipeline or direct
STBP or SLAYER training, rate-coded throughout [rueckauer-2022-nxtf]. NxTF's own related-work
section, written by the same laboratory that authors SNN Toolbox, shows no forward awareness of the
low-latency program about to accelerate [rueckauer-2022-nxtf]. The toolchain freeze overlaps almost
exactly with that acceleration: SNN Toolbox's last substantive commit, August 2022, falls within
months of QCFS's own publication window, and the entire subsequent low-latency literature audited
here, spanning 2022 through 2025, unfolds after the toolbox's code was already frozen
[snntoolbox-github].

The falsifier was searched for deliberately, and every confirmed instance found abandons rate
coding. Quartz (Lenz, Orchard, and Sheik) proposes a time-to-first-spike conversion scheme, states
in its own abstract that "most conversion methods rely on rate coding in the SNN to represent ANN
activation, which uses enormous amounts of spikes," and reports measured results on physical Loihi
1: 0.9 µJ·s energy-delay product on MNIST against 4.38 µJ·s for a rate-coded Loihi baseline, and
10.3 mJ·s against roughly 34.9 mJ·s on CIFAR-10, a same-chip, method-versus-method comparison, not
an isolated demonstration [lenz-2023-quartz]. Brehove et al. propose a sigma-delta, graded-payload
conversion targeting Loihi 2's native graded-spike hardware and report measured, field-deployed
results on a Loihi 2 VPX board [brehove-2026]. No paper was found that keeps rate coding, proposes
a new conversion algorithm, and reaches physical silicon with measurements; the nearest near-miss,
a Speck chip-introduction paper, uses a conventional conversion baseline rather than a novel
low-latency algorithm and is a hardware paper first [richter-2023-speck].

One qualification is owed here, stated honestly rather than smoothed over. A rate-coded QCFS and
SRP baseline configuration has, once, been measured on physical silicon, as a comparison row inside
Adaptive Fission (Jiang et al., NeurIPS 2025), whose own algorithmic contribution is a
population-coding scheme layered on top of existing conversion methods, deployed on a Lynxi HP201
accelerator [jiang-2025-adaptive-fission]. QCFS and SRP's own authors never ran this measurement; a
different group's non-rate-coding innovation motivated the one instance that exists. The defensible
claim is therefore not that rate-coded QCFS-lineage output has never touched silicon under any
circumstances, but that no QCFS-lineage algorithm paper deploys its own method to silicon, and the
one time it happened, it required a different paper's rate-coding-abandoning innovation to make it
happen [jiang-2025-adaptive-fission]. A second, weaker qualification: one non-peer-reviewed,
self-reported GitHub project claims a QCFS implementation with dedicated SpiNNaker and BrainScaleS-2
backends and reports "physical silicon confirmed" runs, but its own documentation describes a
two-neuron validation network, not a benchmark-scale classifier, and does not rise to the bar of a
published counterexample; it suggests the gap may be sociological rather than technically forced,
without closing it in the published record.

The two-population claim above was tested against a candidate counterexample, sought out
deliberately rather than merely asserted. The candidate was "Temporal Flexibility in Spiking Neural
Networks" (Du, Wu, Deng, and Gu, ICLR 2025, arXiv:2503.17394) [du-2025-temporal-flexibility],
initially recorded in the survey's own registry as a both-population instance, E1, deployed on
physical Speck2e, and not abandoning rate coding. On closer reading it does not clear the bar, on two
independent grounds. First, population. The paper is a direct-training temporal-generalization
technique, Mixed Time-step Training, and its own related-work section draws an explicit line between
direct training and ANN-SNN conversion, placing itself in the former; its low-timestep results are
reported on GPU only, never on the chip. Second, evidence class. The only quantity measured on the
physical Speck2e chip is spike difference (SD), a fidelity check against the software simulator, not
an efficiency measurement; SD reaches 3.92 percent on NMNIST, and no latency or energy figure is
measured on the chip itself, the paper's own statements about power and latency cite prior Speck
hardware papers rather than report new numbers. That is E2, not E1.

The phrase "rate coding" appears nowhere in the paper. What actually runs on Speck2e is native
asynchronous DVS events through reset-by-subtraction IF neurons, the chip's own default event-driven
mode, not a rate code the authors chose to keep or abandon. A further search for papers matching the
same profile, a new low-timestep or conversion method reaching physical silicon while keeping rate
coding, turned up genuine E1 rate-coded silicon deployments, but every one of them reuses existing
conversion tooling, CNN2SNN/MetaTF or a previously cited architecture, for a downstream application
rather than proposing a new method; these are logged as boundary cases, not counterexamples. The
claim survives, and it survives because the candidate was reclassified on two independently
sufficient grounds, not because it was waved away.

# 9 Conclusion

This survey set out to answer whether the ReLU-to-integrate-and-fire correspondence that anchors
the low-`T` ANN-to-SNN conversion literature is realized on physical silicon or only in simulation,
and where the disconnect between that literature and the accessible neuromorphic landscape actually
lies. The seam-by-seam audit in Section 8 answers both questions concretely rather than by
assertion. A trained network passing from a conversion paper toward physical silicon loses at least
one of its pooling or skip-connection topology (8.1), its BatchNorm folding (8.1), its reset rule
(8.2), its encoding scheme's energy accounting (8.3), or its timestep semantics (8.4, 8.5) at
nearly every handoff surveyed, and no single documented toolchain preserves all of them
simultaneously. The two-population finding (8.9) is not an artifact of an incomplete search: it
rests on full-text citation audits of thirteen algorithm papers and four deployment papers, a dated
toolchain-freeze overlap, and a deliberately adversarial search for a falsifier that returned
exactly two positive instances, Quartz and Brehove et al., both of which abandon rate coding to
reach silicon. Whether a Lava-to-Loihi-2 deployment direction is viable for further work on this
thesis (design question 6) has a direct answer: the software stack was archived on 13 May 2026,
accepting no further patches, with an unnamed successor SDK, and the reset-semantics blocker (8.2)
together with the operator-coverage blocker (8.1) both apply before the gated, proposal-based
hardware access (8.7) is even reached.

Four concrete problems remain open, and each follows directly from a seam documented above rather
than from a general appeal to future work.

A conversion theorem for an ordinal, non-rate code is missing. The correspondence proved for IF
neurons under reset by subtraction, that a spike count over `T` steps realizes exactly a uniform
`T`-level quantizer, has no published analogue for the codes that actually reach silicon alongside
a new algorithm: time-to-first-spike (Quartz) and graded sigma-delta (Brehove et al.). Until such a
theorem exists, "abandon rate coding to reach hardware" and "prove the QCFS-as-QAT correspondence"
remain two separate, currently incompatible research programs rather than one.

An execution model for heterogeneous per-layer timestep horizons is missing. NeuroScale confirms
that every major digital neuromorphic chip audited here, TrueNorth, Loihi, Loihi 2, and Tianjic,
advances through a single global synchronization barrier. No simulator or chip surveyed executes a
genuine `T_1 ≠ T_2 ≠ ... ≠ T_L` schedule within one forward pass, and the two papers that compute an
average-timestep headline, QAC and PASCAL, do not resolve, and in QAC's case do not even quantify,
the sequential-sum or pipeline-stall cost their own appendices identify as the consequence of
mapping that schedule onto real hardware.

A maintained, soft-reset-preserving export path is missing. Every framework-native bridge surveyed,
SpikingJelly's `lava_exchange` and `nir_exchange`, and the NIR primitive specification itself,
rejects or fails to express reset by subtraction, the one mechanism independently shown worth
roughly twenty accuracy points. The platforms that support it natively, TrueNorth, Speck via
`return_to_zero=False`, and the FPGA frameworks, are either legacy hardware or require bespoke,
per-project glue rather than offering a general, maintained tool.

A measured comparison of a modern low-`T` method against a quantized ANN baseline on the same
silicon is missing. The single closest data point found, Loihi 2 against an int8-quantized Jetson
Orin Nano on PilotNet, shows that quantizing the ANN baseline closes a substantial fraction, though
not all, of the reported SNN advantage. No equivalent same-chip comparison exists for a post-2021
low-`T` conversion method measured against an INT8 or lower ANN baseline of matching bit budget.

Chapter 2's inability to connect conversion methods to hardware execution, noted at the outset of
this survey as motivation rather than as a flaw in the author's own literature review, is not a gap
in that review. It is a gap in the field's published record, confirmed here across nine research
passes and eighteen source files rather than assumed. This survey's edge structure, tracing what
each handoff preserves and what it breaks, is offered as a first attempt to make that gap itself an
object of study, rather than an implicit background condition every subsequent conversion paper
continues to work around without naming.

---

## References

- [rueckauer-2017-frontiers] Rueckauer, B., Lungu, I.-A., Hu, Y., Pfeiffer, M., Liu, S.-C.
  "Conversion of Continuous-Valued Deep Networks to Efficient Event-Driven Networks for Image
  Classification." *Frontiers in Neuroscience* 11:682 (2017). https://doi.org/10.3389/fnins.2017.00682.
  Peer-reviewed.
- [rueckauer-2022-nxtf] Rueckauer, B., Bybee, C., Goettsche, R., Singh, Y., Mishra, J., Wild, A.
  "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi." *ACM Journal on
  Emerging Technologies in Computing Systems* 18(2) (2022). https://doi.org/10.1145/3501770
  (arXiv:2101.04261). Peer-reviewed.
- [pedersen-2024-nir] Pedersen, J. E. et al. "Neuromorphic intermediate representation: A unified
  instruction set for interoperable brain-inspired computing." *Nature Communications* 15:8122
  (2024). https://doi.org/10.1038/s41467-024-52259-9. Peer-reviewed.
- [nir-porting-guide] NIR project, "Porting to a New Platform." Official documentation.
  https://neuroir.org/docs/porting-nir/.
- [snntorch-pr-388] snnTorch GitHub pull request #388, "nir: add missing v_reset parameter on
  export." Repository state. https://github.com/jeshraghian/snntorch/pull/388.
- [snntorch-pr-426] snnTorch GitHub pull request #426, reset-mechanism refactor (subtract vs. zero
  confusion). Repository state. https://github.com/jeshraghian/snntorch/pull/426.
- [fang-2023-spikingjelly] Fang, W. et al. "SpikingJelly: An open-source machine learning
  infrastructure platform for spike-based intelligence." *Science Advances* 9(40), eadi1480 (2023).
  https://www.science.org/doi/pdf/10.1126/sciadv.adi1480. Peer-reviewed.
- [fang-2023-spikingjelly-lava] SpikingJelly documentation, "Convert to Lava for Loihi Deployment."
  Official documentation. https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/lava_exchange.html.
- [jelly-lava-source] SpikingJelly `lava_exchange` module source (`v_reset == 0` hard constraint,
  operator dispatch). Repository state.
  https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html.
- [jelly-nir-source] SpikingJelly `nir_exchange/to_nir.py` source (`NotImplementedError` on soft
  reset). Repository state, retrieved via `raw.githubusercontent.com/fangwei123456/spikingjelly`.
- [sinabs-discretize-api] Sinabs documentation, discretize/DynapcnnLayer API (no BatchNorm-fold
  utility; default `MembraneSubtract()` reset). Official documentation.
  https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html.
- [sinabs-nmnist-tutorial] Sinabs NMNIST quick-start tutorial (bias-as-leak, BN-free architecture
  convention). Official documentation. https://sinabs.readthedocs.io/v3.1.3/tutorials/nmnist.html.
- [akida-hw-constraints] BrainChip Akida hardware constraints documentation. Official
  documentation. https://doc.brainchipinc.com/user_guide/hardware/1.0.html and
  https://brainchip-inc.github.io/akida_examples_2.4.0-doc-1/user_guide/1.0_hw_constraints.html.
- [snntoolbox-docs] SNN Toolbox documentation, introduction and simulation API (operator coverage,
  output coding schemes). Official documentation. https://snntoolbox.readthedocs.io/en/latest/.
- [snntoolbox-github] SNN Toolbox GitHub repository, release history and commit log. Repository
  state. https://github.com/NeuromorphicProcessorProject/snn_toolbox.
- [snntoolbox-issues] SNN Toolbox GitHub issue tracker, issues #142 and #143 (2024). Repository
  state / community commentary. https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues.
- [pehle-2022-bmtk] BMTK-Loihi mapping paper (native hard reset on Loihi). *Frontiers in
  Neuroinformatics* (2022). https://doi.org/10.3389/fninf.2022.883360. Peer-reviewed.
- [pehle-2022-brainscales-multicomp] Pehle, C. et al. "The BrainScaleS-2 Accelerated Neuromorphic
  System With Hybrid Plasticity." *Frontiers in Neuroscience* (2022).
  https://doi.org/10.3389/fnins.2022.795876. Peer-reviewed.
- [spinnaker-neuron-lab-manual] SpiNNaker Manchester, "Creating New Neuron Models" lab manual, and
  sPyNNaker "Models and Limitations" documentation. Official documentation.
  https://spinnakermanchester.github.io/.
- [truenorth-neuron-model] "Cognitive Computing Building Block: neuron model of TrueNorth."
  Technical report. https://viplab.fudan.edu.cn/vip/attachments/download/3248/neuron-model_of_truenorth.pdf.
- [speck-devkit-manual] SynSense, Speck Dev Kit Manual / Datasheet. Vendor material.
  https://www.synsense.ai/wp-content/uploads/2025/12/Speck-Dev-Kit-Manual-2025.12-V2.pdf.
- [spiker-plus-fpga] Spiker+ FPGA SNN accelerator generator (native subtractive reset). Preprint,
  arXiv:2401.01141.
- [sia-fpga] SIA hardware-software co-optimized FPGA SNN accelerator (subtractive reset as
  default). Preprint, arXiv:2410.16298.
- [auge-2021-encoding-survey] Auge, D., Hille, J., Mueller, E., Knoll, A. "A Survey of Encoding
  Techniques for Signal Processing in Spiking Neural Networks." *Neural Processing Letters* (2021).
  https://doi.org/10.1007/s11063-021-10562-2. Peer-reviewed.
- [kim-2022-rate-vs-direct] Kim, Y., Park, H., Moitra, A., Bhattacharjee, A., Venkatesha, Y.,
  Panda, P. "Rate Coding or Direct Coding: Which One is Better for Accurate, Robust, and
  Energy-efficient Spiking Neural Networks?" arXiv:2202.03133 (2022). Preprint.
- [nengoloihi-cifar10-example] NengoLoihi CIFAR-10 convnet example (off-chip input layer). Official
  documentation. https://www.nengo.ai/nengo-loihi/v1.0.0/examples/cifar10-convnet.html.
- [park-2020-t2fsnn] Park, S. et al. "T2FSNN: Deep Spiking Neural Networks with Time-to-First-Spike
  Coding." arXiv:2003.11741 (2020). Preprint.
- [lenz-2023-quartz] Lenz, G., Orchard, G., Sheik, S. "Ultra-low-power Image Classification on
  Neuromorphic Hardware" (Quartz). arXiv:2309.16795 (2023-2024). Preprint.
- [richter-2023-speck] Richter, O. et al. (SynSense), "Speck: A Smart event-based Vision Sensor
  with a low latency 327K Neuron Convolutional Neuronal Network Processing Pipeline."
  arXiv:2304.06793 (2023). Preprint.
- [rockpool-xylo-overview] Rockpool documentation, "Overview of the Xylo family." Official
  documentation. https://rockpool.ai/devices/xylo-overview.html.
- [dewolf-2020-nengo-loihi] DeWolf, T., Jaworski, P., Eliasmith, C. "Nengo and Low-Power AI
  Hardware for Robust, Embedded Neurorobotics." *Frontiers in Neurorobotics* (2020).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7581863/. Peer-reviewed.
- [li-2025-neuroscale] Li, C., Imam, N., Manohar, R. "A deterministic neuromorphic architecture
  with scalable time synchronization" (NeuroScale). *Nature Communications* 16, 10329 (2025).
  https://doi.org/10.1038/s41467-025-65268-z. Peer-reviewed.
- [guo-2025-qac] Guo, M., Li, Q., Li, Y., Cheng, J., Chen, L. "QAC: Quantization-Aware Conversion
  for Mixed-Timestep Spiking Neural Networks." ICLR 2025 submission #8774.
  https://openreview.net/forum?id=D4sQzdMvcG. Preprint (venue/acceptance status unconfirmed).
- [ramesh-2025-pascal] Ramesh, P., Srinivasan, G. "PASCAL: Precise and Efficient ANN-SNN Conversion
  using Spike Accumulation and Adaptive Layerwise Activation." *Transactions on Machine Learning
  Research* (2025). arXiv:2505.01730. Peer-reviewed.
- [du-2025-temporal-flexibility] Du, K., Wu, Y., Deng, S., Gu, S. "Temporal Flexibility in Spiking
  Neural Networks: Towards Generalization Across Time Steps and Deployment Friendliness." ICLR 2025
  Poster. https://arxiv.org/html/2503.17394v1. Peer-reviewed.
- [horowitz-2014-isscc] Horowitz, M. "1.1 Computing's Energy Problem (and what we can do about
  it)." ISSCC 2014. https://doi.org/10.1109/ISSCC.2014.6757323. Peer-reviewed (conference).
- [bhattacharjee-2023-hardware] Bhattacharjee, A., Yin, R., Moitra, A., Panda, P. "Are SNNs Truly
  Energy-efficient? — A Hardware Perspective." arXiv:2309.03388 (2023). Preprint.
- [shen-2024-cvpr] Shen, G., Zhao, D., Li, T., Li, J., Zeng, Y. "Are Conventional SNNs Really
  Efficient? A Perspective from Network Quantization." CVPR 2024.
  https://openaccess.thecvf.com/content/CVPR2024/papers/Shen_Are_Conventional_SNNs_Really_Efficient_A_Perspective_from_Network_Quantization_CVPR_2024_paper.pdf.
  Peer-reviewed.
- [narduzzi-2025-eflop] Narduzzi, S., Zenke, F., Liu, S.-C., Dunbar, L. A. "EFLOP: a sparsity-aware
  metric for evaluating computational cost in spiking and non-spiking neural networks."
  *Neuromorphic Computing and Engineering* 5, 034011 (2025). https://doi.org/10.1088/2634-4386/addee8.
  Peer-reviewed.
- [brehove-2026] Brehove, T., Tumpa, S. N., Kyubwa, E., Menon, A., Narayanan, V. "Sigma-Delta
  Neural Network Conversion on Loihi 2." ICONS 2026, arXiv:2505.06417. Peer-reviewed (conference).
- [lca-loihi2-2023] "Implementing and Benchmarking the Locally Competitive Algorithm on the Loihi 2
  Neuromorphic Processor." arXiv:2307.13762 (2023). Preprint.
- [shrestha-2023-loihi2] Shrestha, S. B., Timcheck, J., Frady, P., Campos-Macías, L., Davies, M.
  "Efficient Video and Audio Processing with Loihi 2." arXiv:2310.03251; ICASSP 2024.
  https://doi.org/10.1109/icassp48485.2024.10448003. Peer-reviewed.
- [yik-2025-neurobench] Yik, J. et al. "The NeuroBench framework for benchmarking neuromorphic
  computing algorithms and systems." *Nature Communications* 16, 1545 (2025).
  https://doi.org/10.1038/s41467-025-56739-4. Peer-reviewed.
- [lava-dl-readme] `lava-nc/lava-dl` GitHub README, archival notice (13 May 2026). Repository
  state. https://github.com/lava-nc/lava-dl/blob/main/README.md.
- [lava-dl-docs] Lava documentation, "Deep Learning" (SLAYER/Bootstrap/NetX overview, `RunSteps`
  execution model). Official documentation. https://lava-nc.org/dl.html.
- [inrc-loihi-access] Intel Neuromorphic Research Community, "Access Intel Loihi Hardware."
  Vendor material (Confluence). https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001.
- [nxsdk-models-repo] `intel-nrc-ecosystem/models` GitHub repository, discontinuation notice.
  Repository state. https://www.github.com/intel-nrc-ecosystem/models.
- [hbp-guidebook] HBP Neuromorphic Computing Platform Guidebook (BrainScaleS and SpiNNaker access
  via EBRAINS). Vendor/official documentation.
  https://flagship.kip.uni-heidelberg.de/jss/FileExchange/HBPNeuromorphicComputingPlatformGuidebook.pdf.
- [bu-2022-qcfs] Bu, T., Fang, W., Ding, J., Dai, P., Yu, Z., Huang, T. "Optimal ANN-SNN Conversion
  for High-accuracy and Ultra-low-latency Spiking Neural Networks." ICLR 2022, arXiv:2303.04347.
  Peer-reviewed (conference).
- [wang-2023-ijcai-snm] Wang, Y., Zhang, M., Chen, Y., Qu, H. "Signed Neuron with Memory" (SNM).
  IJCAI 2022. https://www.ijcai.org/proceedings/2022/0347.pdf. Peer-reviewed (conference).
- [hao-2023-aaai-srp] Hao, Z., Bu, T., Ding, J., Huang, T., Yu, Z. "Reducing ANN-SNN Conversion
  Error through Residual Membrane Potential" (SRP). AAAI 2023, arXiv:2302.02091. Peer-reviewed
  (conference).
- [jiang-2025-adaptive-fission] Jiang, Y. et al. "Adaptive Fission." NeurIPS 2025 proceedings.
  Peer-reviewed (conference). Code repository (not independently re-verified): repository state,
  https://github.com/JiangYizhou16/Adaptive-Fission.
