# Audit C, rate-coded conversion on physical silicon

Reviewed 2026-09-16. The ordinary web search route was used because Exa returned a
credit error. Primary papers, official vendor documentation, released source code, and
the repository's full-text corpus were then inspected directly.

## Result

No true falsifier was found for the narrow claim.

> Through 16 September 2026, no paper in the audited corpus both introduces a recent
> low-timestep, spike-count or firing-rate-coded ANN-to-SNN conversion algorithm and
> reports that same proposed algorithm on named physical neuromorphic silicon with an
> on-device measurement.

This is a bounded paper-level search result. It is not evidence that rate-coded SNNs
cannot run on silicon. It is not evidence that QCFS has never been run on silicon. It
must not be generalized to direct training or to application papers that reuse an
existing converter.

The strongest correction to the previous wording comes from Adaptive Fission. Its
Table 1 places unmodified, no-Fission QCFS and SRP baselines on a physical Lynxi HP201
accelerator. Rate-coded QCFS-lineage models have therefore reached silicon. Their own
method papers did not report those runs, and Adaptive Fission's new contribution uses
population coding.

## Definitions used in the audit

The falsifier had to satisfy every condition below in one paper.

1. The paper introduces an ANN-to-SNN conversion algorithm, rather than a compiler,
   application, hardware-aware port, or direct-training method.
2. The new method targets a short inference horizon relative to classical rate
   conversion.
3. Hidden activations are represented by binary spike counts or firing rates over a
   window. Direct current input alone is not enough to establish rate coding.
4. The proposed method, rather than only a baseline, is executed on a named physical
   neuromorphic chip.
5. The paper reports an on-device measurement. E1 requires a measured performance,
   latency, power, energy, or resource result. E2 covers physical accuracy or fidelity
   only.

The classification is claim-level. A paper can be E1 for one result and E3 or E5 for
another.

## Confirmed qualifying deployments that abandon rate coding

| Work | What is new | Neural code on silicon | Physical route | Evidence and measurement boundary | Verdict |
|---|---|---|---|---|---|
| Quartz [C1] | TTFS ANN-to-SNN conversion with counterweight and rectifier synapses | Time to first spike, with one information-bearing spike per neuron | Custom NxSDK 1.0.0 implementation to Loihi 1, Nahuku 32 board | E1. Table 3 reports latency, static and dynamic power, energy, and EDP. The MNIST boundary includes neuromorphic cores and Lakemont x86. The paper's preferred CIFAR-10 EDP uses a placement-based static-power correction. | Qualifies and abandons rate coding. |
| Brehove et al. [C2] | Quantized ANN-to-SDNN conversion with modified Loihi 2 microcode | Signed graded sigma-delta payloads that encode activation changes | nxkernel 0.3.0 to a 16-chip Loihi 2 VPX board | E1. Loihi probes measure chip power and timing. Table 3 reports energy, latency, throughput, and EDP under normal-I/O and on-chip-replay conditions. Host delta generation and output accumulation remain outside the neurocores. | Qualifies and abandons rate coding. |
| Adaptive Fission [C3] | Post-training adaptive population expansion applied to converted and directly trained SNNs | Population code. Binary sub-neurons carry unequal fixed weights | LynBIDL to physical Lynxi HP201 | E1. Table 1 reports memory, time per evaluation epoch, and system energy per epoch at batch size 32. Board sensors include memory, I/O, and peripheral power. | Qualifies as a new conversion-adjacent encoding method and abandons unchanged rate coding. |
| Andrei et al. [C4] | Complex-valued extension of Few-Spikes conversion for an unfolded MHR network | Serialized Few-Spikes temporal binary code, not a firing-rate estimate | Custom mapping to a physical single-chip SpiNNaker2 board | E1. Section IV and Figure 4 report board power against Jetson Xavier. The method extends temporal FS conversion and explicitly separates it from rate-coded LIF conversion. | Additional supporting case. It was absent from the earlier three-case summary. |

The last row materially strengthens the synthesis. The physical-silicon population is
not limited to three examples. It also shows why the claim should be framed around the
representation change, not around a closed list of methods.

## Rate-coded silicon cases that do not satisfy the falsifier

| Candidate | What is physically established | Why it does not falsify the narrow claim |
|---|---|---|
| QCFS and SRP rows in Adaptive Fission [C3] | E1 system-level HP201 time and energy measurements for no-Fission baselines | The deployed paper does not introduce QCFS or SRP. The original QCFS and SRP papers report software results. This disproves “the methods never reached silicon,” but not the paper-level claim. |
| Hardware-aware Spiking Q-Networks on SpiNNaker2 [C5] | E1. A rate-coded, subtract-reset, directly trained DSQN runs for 10 or 20 ticks on a physical SpiNNaker2 board. Table III reports power, episode energy, and duration. | This is surrogate-gradient reinforcement learning with post-training quantization and threshold calibration. It is not ANN-to-SNN conversion. The broad phrase “new low-timestep SNN method” would be unsafe because this paper is a plausible counterexample. |
| Classical SNN Toolbox and NxTF deployments [C6] | E1 rate-coded conversion exists on Loihi 1 | These works use classical threshold balancing rather than a recent low-T conversion contribution. They establish feasibility of rate-coded deployment, not uptake of the post-2020 low-T algorithms. |
| Akida deployment papers [C7]-[C9] | E1 latency, power, and energy measurements on physical Akida hardware | They reuse BrainChip's existing QuantizeML to CNN2SNN route. They do not introduce a new low-T rate-coded conversion. The route has no user-exposed multi-timestep rate window and is described independently as a one-timestep, stepwise quantized ReLU. |

## Rejected apparent falsifiers

### When SNN Meets ANN

The TMLR submission “When SNN Meets ANN” [C10] is the most important wording trap.
It introduces a QCFS-based low-timestep conversion and its appendix is titled
“Deployment of Proposed SNN on Loihi.” The appendix implements the neuron in Lava-DL
and reports a PyTorch versus Lava-DL accuracy table. It does not name a physical Loihi
board, state that a hardware run occurred, use a hardware profiler, or report any chip
measurement. The paper's main energy results are analytical operation estimates.

The correct split follows.

- The Lava-DL implementation is E5 for the reported accuracy result.
- The stated Lava-DL to Loihi path is at most E3 unless a physical run is documented.
- The paper is not a physical-silicon falsifier.

The final TMLR record is registered as `datta2025-snn-meets-ann`. The inspected full
text includes the 24-page submission lineage and the final April 2025 TMLR record.
Separate claim records retain the E5 accuracy result and the E3 route assertion.

### Temporal Flexibility in Spiking Neural Networks

Du et al. [C11] physically execute an MTT-trained network on Speck2e. The method is
direct training, not conversion. The physical experiment reports spike difference on
NMNIST, not latency or energy for the proposed method. Static-image low-timestep
results remain software-only. The silicon claim is E2 and does not satisfy either the
population or measurement condition.

### Akida

BrainChip's documentation establishes the vendor route [C7], [C8]. QuantizeML produces
integer-only uniformly quantized models. CNN2SNN converts those models to the Akida
runtime. Two independent hardware papers then describe the standard converted-CNN path
as collapsing the rate approximation into one timestep [C9], [C12].

The released CNN2SNN 2.19.3 source provides a stronger operational locator. In
`cnn2snn/quantizeml/outputs.py`, `set_output_v1_variables()` states that Akida 1.0
evaluates outputs as `y = x / act_step`, then folds a rounded half-step into the layer
threshold. In `cnn2snn/quantizeml/conv_common.py`, quantized bias is stored in the
threshold variable. These are static integer-quantizer mappings. They do not expose a
window in which spike count converges to an ANN activation.

This finding should remain scoped to the standard converted-CNN route. Akida includes
other sequential and recurrent layer types. The available sources do not justify a
universal statement about every Akida execution mode or undocumented circuit state.

## Measurement cautions

### Quartz CIFAR-10

Table 3 labels energy per inference in microjoules, but the CIFAR-10 power and latency
imply approximately 563 millijoules under the raw placement. The table's reported EDP
is consistent with millijoules, not with 564 microjoules. The text then replaces the raw
static power with an estimate based on 60 percent core utilization and obtains a 10.3
millijoule-second EDP. That corrected result is not a direct measurement of the reported
placement. The survey should cite the raw and corrected boundaries separately and should
not repeat 564 microjoules as a measured CIFAR-10 energy value.

### Adaptive Fission

Table 1 reports time and watt-hours per epoch at batch size 32. It does not report
single-sample latency or energy. Appendix E.1 states that closed HP201 interfaces prevent
core-only power or operation measurement. The sensor reading includes peripherals,
memory, and I/O. This remains E1, but cross-paper energy ratios require boundary labels.

### Brehove et al.

Loihi 2 power is chip-side, whereas Jetson power is whole-SoC. Host-side delta generation,
output accumulation, and decoding are outside the neurocores. The paper discloses the
asymmetry. The cross-platform ratio should carry it.

## Search log

The following ordinary web-search queries were run, followed by primary-source inspection.

- `recent low latency ANN-to-SNN conversion physical neuromorphic hardware rate coding chip deployment`
- `QCFS neuromorphic chip deployment hardware Loihi Lynxi physical`
- `rate-coded Loihi 2 ANN-to-SNN conversion low latency`
- `rate coding physical neuromorphic chip ANN-SNN conversion QCFS SRP`
- `low latency rate-coded SNN hardware ANN-to-SNN conversion chip`
- `physical chip QCFS SNN conversion`
- `deployed on Loihi ANN-to-SNN conversion 2024 2025`
- `rate-coded SpiNNaker2 conversion neuromorphic hardware measured energy`
- `low timestep neuromorphic chip ANN-SNN deployment`
- `novel ANN-to-SNN conversion SpiNNaker2`
- `new ANN-to-SNN conversion Loihi hardware`
- `novel conversion spiking neural network neuromorphic chip energy`
- `conversion method SNN physical neuromorphic chip deployed`

Search hits were admitted only after checking the paper itself. “Runs on Lava,” “Loihi
compatible,” estimated SynOps, RTL synthesis, and hardware motivation were not treated as
physical execution.

## Sources

[C1] C. Lenz, G. Orchard, and S. Sheik, “Ultra-low-power Image Classification on
Neuromorphic Hardware,” arXiv:2309.16795v2, 2024. Source ID `quartz`.
<https://arxiv.org/abs/2309.16795>

[C2] M. Brehove et al., “Sigma-Delta Neural Network Conversion on Loihi 2,” ICONS,
2026, doi: 10.1145/3822454.3822490. Source ID `brehove`.
<https://arxiv.org/abs/2505.06417>

[C3] Y. Jiang et al., “Adaptive Fission: Post-training Encoding for Low-latency Spike
Neural Networks,” NeurIPS 38, 2025. Source ID `adaptive-fission`.
<https://openreview.net/forum?id=2zZzdAMyYi>

[C4] V. C. Andrei et al., “Deep-Unrolling Multidimensional Harmonic Retrieval
Algorithms on Neuromorphic Hardware,” Asilomar, 2024, doi:
10.1109/IEEECONF60004.2024.10942794. Source ID
`andrei2024-deep-unrolling-spinnaker2`.
<https://arxiv.org/abs/2412.04008>

[C5] S. Arfa, B. Vogginger, and C. Mayr, “Hardware-Aware Fine-Tuning of Spiking
Q-Networks on the SpiNNaker2 Neuromorphic Platform,” ICONS, 2025, doi:
10.1109/ICONS69015.2025.00021. Source ID
`arfa2025-spiking-q-spinnaker2`.
<https://arxiv.org/abs/2507.23562>

[C6] C. Rueckauer et al., “NxTF: An API and Compiler for Deep Spiking Neural Networks
on Intel Loihi,” ACM JETC, 2022. Source ID `nxtf`.
<https://doi.org/10.1145/3501770>

[C7] BrainChip, “QuantizeML toolkit,” MetaTF 2.19.3. Source ID
`brainchip-quantizeml-docs`.
<https://doc.brainchipinc.com/user_guide/quantizeml.html>

[C8] BrainChip, “CNN2SNN toolkit,” MetaTF 2.19.3. Source ID
`brainchip-cnn2snn-docs`.
<https://doc.brainchipinc.com/user_guide/cnn2snn.html>

[C9] J. Ziegler et al., “Detection of Fast-Moving Objects with Neuromorphic Hardware,”
arXiv:2403.10677, 2024. Source ID `ziegler2024-akida-robotics`.
<https://arxiv.org/abs/2403.10677>

[C10] G. Datta et al., “When SNN Meets ANN: Error-Free ANN-to-SNN Conversion for
Extreme Edge Efficiency,” TMLR, 2025. Source ID `datta2025-snn-meets-ann`.
<https://openreview.net/forum?id=WOwQKguWT0>

[C11] K. Du, Y. Wu, S. Deng, and S. Gu, “Temporal Flexibility in Spiking Neural
Networks,” ICLR, 2025. Source ID `temporal-flexibility`.
<https://arxiv.org/abs/2503.17394>

[C12] P. Lunghi et al., “Energy efficiency analysis of Spiking Neural Networks for
space applications,” arXiv:2505.11418, 2025. Source ID `lunghi2025-akida-space`.
<https://arxiv.org/abs/2505.11418>

[C13] R. V. W. Putra, P. Wickramasinghe, and M. Shafique, “Enabling Efficient
Processing of Spiking Neural Networks with On-Chip Learning on Commodity
Neuromorphic Processors for Edge AI Systems,” arXiv:2504.00957, 2025. Source ID
`akida-benchmarks2025`.
<https://arxiv.org/abs/2504.00957>

## Access gaps

- No access gap remains for Quartz, Brehove et al., Adaptive Fission, the two Akida
  documentation pages, the CNN2SNN 2.19.3 source distribution, or the three Akida
  papers inspected here.
- Lynxi's low-level HP201 interfaces are closed. Adaptive Fission therefore cannot
  expose core-only power or operation counts, as its appendix states.
- The “When SNN Meets ANN” appendix does not disclose whether its Lava-DL result used
  CPU simulation, a Loihi emulator, or physical Loihi. In the absence of a named board
  and physical measurement, the silicon route remains unverified.
- Andrei et al., Arfa et al., and “When SNN Meets ANN” are registered canonically.
  Their six claim-level records preserve the separation between method semantics,
  physical E1 measurements, E5 framework accuracy, and the E3 Lava-DL route.
