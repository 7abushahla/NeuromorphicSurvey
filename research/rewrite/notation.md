# Notation and Terminology Contract

Reviewed 2026-09-16.

This notation is shared by all 18 sections. A writer may introduce a local symbol only
when the quantity is not already represented here. Every equation must state its update
order and indexing convention.

## Neural state and events

| Symbol | Meaning | Required qualification |
|---|---|---|
| $l \in \{1,\ldots,L_{\mathrm{net}}\}$ | Network layer index | Do not use $L$ for both layer count and quantization level count. |
| $i,j$ | Postsynaptic and presynaptic unit indices | State the layer when ambiguity remains. |
| $t$ | Discrete algorithmic step index | Never use $t$ alone for physical latency. |
| $\tau$ | Continuous physical or modeled time | Give units when it denotes physical time. |
| $\Delta t$ | Numerical integration interval or hardware tick duration | State which interpretation applies. They need not be equal. |
| $u_i^l[t]$ | Membrane state after the declared update stage | Each derivation must state whether this is pre-reset or post-reset. |
| $\tilde{u}_i^l[t]$ | Pre-reset membrane candidate | Use when thresholding and reset order matter. |
| $q_i^l[t]$ | Synaptic state or filtered current | State the filter equation and units or normalization. |
| $a_i^l[t]$ | Adaptation or dynamic-threshold state | Omit for models without adaptation. |
| $z_i^l[t]$ | Emitted binary event in a discrete-time model | $z \in \{0,1\}$ unless a signed or graded payload is declared. |
| $s_i^l(\tau)$ | Continuous-time spike train $\sum_k p_{ik}\delta(\tau-\tau_{ik})$ | Declare the payload $p_{ik}$ and whether event times are quantized. |
| $p_{ik}$ | Spike payload | Distinguish binary, signed, integer, and graded payloads. |
| $w_{ij}^l$ | Synaptic weight | State numeric precision and sign constraints when deployment is discussed. |
| $b_i^l$ | Bias or constant input term | State whether it is folded, represented on chip, or host supplied. |
| $\theta_i^l[t]$ | Threshold | Use $\theta_i^l$ for a fixed threshold. |
| $r_i^l[t]$ | Reset term applied after a spike decision | Specify reset-to-zero, reset-by-subtraction, or another rule explicitly. |
| $d_{ij}^l$ | Synaptic delay | State whether it is measured in steps, ticks, or physical time. |

The common discrete update uses separate stages rather than one overloaded recurrence.

\[
q_i^l[t] = \mathcal{S}^l\!\left(q_i^l[t-1],\{z_j^{l-1}[t-d_{ij}^l]\}_j,\{w_{ij}^l\}_j\right),
\]

\[
\tilde{u}_i^l[t] = \mathcal{M}^l\!\left(u_i^l[t-1],q_i^l[t],a_i^l[t-1],b_i^l\right),
\qquad
z_i^l[t] = \mathcal{H}\!\left(\tilde{u}_i^l[t]-\theta_i^l[t]\right),
\]

\[
u_i^l[t] = \mathcal{R}^l\!\left(\tilde{u}_i^l[t],z_i^l[t],\theta_i^l[t]\right).
\]

This form establishes an update-order vocabulary. It does not claim that every simulator
or chip executes these stages in the same order.

## Representation, coding, and decoding

| Symbol | Meaning | Required qualification |
|---|---|---|
| $x$ | Source variable presented to an encoder | State its domain, normalization, and acquisition boundary. |
| $\mathcal{E}$ | Encoder that maps $x$ to a current, event train, or spike representation | Direct current injection is an input convention, not automatically a neural code. |
| $\mathcal{C}$ | Network channel or transformation | State neuron, code, payload, and time model. |
| $\mathcal{D}$ | Decoder or readout | State whether it uses count, rate, first-spike time, membrane state, class accumulator, or host processing. |
| $\hat{x}$ or $\hat{y}$ | Decoded estimate or decision | State the observation window and stopping rule. |
| $N_i^l(T)=\sum_{t=1}^{T}z_i^l[t]$ | Spike count in a finite horizon | Valid only for a binary discrete-time event variable. |
| $\rho_i^l(T)=N_i^l(T)/T$ | Discrete firing fraction | Do not call this a physical rate unless divided by a stated physical duration. |
| $T$ | Maximum algorithmic inference horizon in discrete steps | $T$ is not wall-clock latency, spike count, energy, or numeric precision. |
| $T_l$ | Static layer-specific algorithmic horizon | Distinguish it from per-input early exit and asynchronous execution. |
| $T_{\mathrm{stop}}(x)$ | Input-dependent stopping step | Report the distribution, maximum, and stopping criterion where available. |
| $T_{\mathrm{eff}}$ | Reported effective or averaged horizon | Define the weighting, truncation, and denominator. Do not infer latency from it. |

## Conversion and precision

| Symbol | Meaning | Required qualification |
|---|---|---|
| $a^l$ | ANN activation at layer $l$ | State activation function and clipping range. |
| $\lambda^l$ | Activation or threshold scale used by a conversion method | Do not assume the same interpretation across methods. |
| $Q^l$ | Number of representable activation intervals or levels | State whether zero is included and give the exact quantizer. |
| $b_w,b_\theta,b_u$ | Bit widths for weights, threshold, and state | Keep each precision separate. Do not infer a bit width from $T$. |
| $\epsilon_{\mathrm{clip}}$ | Clipping or saturation error | Define relative to the chosen activation range. |
| $\epsilon_{\mathrm{disc}}$ | Finite-count or quantization error | State whether it arises from count resolution, numeric quantization, or both. |
| $\epsilon_{\mathrm{reset}}$ | Error associated with reset semantics or residual state | State the reference reset rule and the finite window. |
| $\epsilon_{\mathrm{time}}$ | Temporal alignment or timing error | Define the compared trajectories or readouts. |

The survey may decompose a layer error as a conceptual sum of named mechanisms. It must
not imply independence, additivity, or a universal propagation law unless the cited
derivation proves those properties.

## Hardware time and measurement

| Symbol | Meaning | Required qualification |
|---|---|---|
| $\tau_{\mathrm{tick}}$ | Duration of a hardware update tick | State whether it is fixed, configurable, or only a scheduler convention. |
| $\tau_{\mathrm{inf}}$ | Wall-clock inference latency | State start and stop events, batching, and included host work. |
| $\tau_{\mathrm{decision}}$ | Time until a valid decision becomes available | It may be smaller than a fixed maximum inference window. |
| $R$ | Throughput | Give decisions per second and batch size. |
| $P_{\mathrm{static}}$ | Static or idle power | State measurement boundary. |
| $P_{\mathrm{dyn}}$ | Dynamic power above the declared baseline | State subtraction method. |
| $E_{\mathrm{inf}}$ | Energy per inference | State whether it is measured directly or computed from power and latency. |
| $N_{\mathrm{spk}}$ | Spike count within the declared boundary | State layers, duration, and whether input or routing events are included. |
| $N_{\mathrm{synop}}$ | Synaptic operations or events | State the platform or benchmark definition. |

Measurement boundaries use the fixed terms `chip-only`, `board-level`,
`host-inclusive`, `sensor-to-decision`, `modeled`, and `physical`. A metric without one
of these boundaries is incomplete for cross-system comparison.

## Evidence and capability vocabulary

Evidence classes $E1$ through $E5$ apply to individual claims. They are not paper-level
quality scores. Their definitions appear once in Section 1.

Route states use `exact`, `approximate`, `blocked`, `obsolete`, `unexercised`, and
`physical`. Platform capability statuses use `native`, `transformed`, `emulated`,
`host-assisted`, `unsupported`, and `undocumented`. Verification states use `verified`,
`provisional`, `conflicted`, and `rejected`.

These vocabularies answer different questions. A capability may be native but supported
only by provisional documentation. An edge may be physically exercised while a separate
measurement claim remains E2. `Undocumented` is not evidence of impossibility.

## Prohibited equivalences

The survey must not equate any of the following without a cited derivation or measurement.

- fewer algorithmic steps and lower wall-clock latency;
- fewer spikes and fewer hardware operations;
- fewer operations and lower energy;
- asynchronous core execution and independent per-layer horizons;
- event-driven input and event-driven execution throughout the system;
- a documented exporter and a physically exercised deployment route;
- equal nominal bit width and equal represented information;
- an analytical hardware model and a silicon measurement.

