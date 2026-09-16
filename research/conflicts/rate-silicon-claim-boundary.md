# Conflict note, rate-coded silicon claim boundary

## Competing interpretations

### Interpretation A

No new SNN or ANN-to-SNN method that keeps rate coding reaches physical silicon.

This interpretation is false or at least indefensible. A 2025 SpiNNaker2 paper proposes
hardware-aware fine-tuning for rate-coded spiking Q-networks and reports physical power,
energy, and duration. Classical SNN Toolbox conversion also reaches Loihi. Adaptive
Fission measures no-Fission QCFS and SRP baselines on Lynxi HP201.

### Interpretation B

No paper was found that both introduces a recent low-timestep, spike-count or
firing-rate-coded ANN-to-SNN conversion algorithm and reports that same proposed
algorithm on named physical neuromorphic silicon with an on-device measurement.

This interpretation survived the deliberate falsifier search through 2026-09-16.

## Resolution

Use Interpretation B. State it as a bounded literature finding, not as an impossibility
theorem or a claim about every rate-coded SNN.

The paper-level condition matters. Adaptive Fission proves that QCFS and SRP models can
be run on physical HP201 hardware. It does not prove that their proposing papers closed
the deployment loop. The survey should therefore distinguish three questions.

1. Did the original method paper deploy its own contribution?
2. Was the method later deployed by another paper?
3. Does a documented toolchain route exist without a physical run?

For QCFS and SRP, the current answers are no, yes, and yes, respectively.

## Evidence-class resolution

| Case | Correct class | Reason |
|---|---|---|
| Quartz on Loihi 1 | E1 | Named board and measured latency, power, energy, and EDP |
| Brehove et al. on Loihi 2 | E1 | Named VPX board and measured chip-side performance and energy |
| Adaptive Fission on HP201 | E1 | Physical system-sensor time and energy measurements |
| QCFS and SRP baseline rows in Adaptive Fission | E1 for the later baseline run | Physical HP201 measurements, but not evidence in the original method papers |
| Temporal Flexibility on Speck2e | E2 | Physical spike-fidelity result, with no method-specific latency or energy measurement |
| When SNN Meets ANN in Lava-DL | E5 for reported accuracy and E3 for the claimed Loihi route | A framework result and a stated path, with no named physical board or chip measurement |
| Hardware-aware DSQN on SpiNNaker2 | E1 | Physical rate-coded direct-training result, outside the conversion population |
| Akida deployment studies | E1 | Physical measurements through an existing single-pass vendor route, outside the new-conversion population |

## Akida terminology conflict

BrainChip and application papers call the deployed model an SNN. That product label does
not establish multi-timestep firing-rate semantics. QuantizeML documents uniform integer
quantization. CNN2SNN documents conversion of the quantized model to the runtime. The
released 2.19.3 converter source maps the activation scale to `act_step`, folds bias and a
rounded half-step into static thresholds, and exposes no rate-window parameter. Ziegler
et al. and Lunghi et al. independently describe the standard path as one-timestep
execution.

The resolution is to record both facts. Akida is a physical neuromorphic deployment and
its standard converted-CNN route is not ordinary multi-timestep spike-count rate coding.
No claim is made about every Akida layer type or undocumented circuit mechanism.

## Quartz measurement conflict

Quartz Table 3 has an internal CIFAR-10 unit inconsistency. The printed power and latency
imply about 563 millijoules per inference, while the energy row is labeled microjoules.
The EDP row agrees with the millijoule interpretation. The paper's preferred 10.3
millijoule-second CIFAR-10 EDP additionally replaces measured static power with an
estimated better-placement value.

The resolution is to retain E1 while separating direct measurements from the placement
correction. Do not quote 564 microjoules for CIFAR-10.

## Recommended prose

> Rate-coded conversion is physically feasible, and later work has placed QCFS and SRP
> baselines on Lynxi HP201. The unresolved disconnect is narrower. In the literature
> audited through September 2026, no paper that introduced a recent low-timestep,
> rate-coded ANN-to-SNN conversion algorithm also measured that same contribution on
> physical neuromorphic silicon. Confirmed method-and-silicon papers instead changed the
> representation. Quartz used time to first spike, Brehove et al. used graded
> sigma-delta events, Adaptive Fission used population coding, and Andrei et al. extended
> Few-Spikes temporal coding. This is an empirical literature finding, not a claim that
> rate-coded networks cannot be deployed.

## Falsifier retained for future updates

A future paper weakens this claim if it satisfies every condition below.

- It introduces a new low-timestep ANN-to-SNN conversion algorithm.
- Its hidden activations retain binary spike-count or firing-rate representation over a
  finite window.
- The proposed method itself runs on named physical neuromorphic silicon.
- The paper reports at least one on-device measurement with a stated boundary.

An application that reuses a classical converter, a direct-training paper, an RTL
synthesis result, a simulator run, or an undocumented SDK route does not satisfy this
specific falsifier.
