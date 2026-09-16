# Temporal-horizon conflicts requiring canonical correction

Review date: 2026-09-16

This file records conflicts only. Proposed claim records and full evidence are in `../claim-audits/audit-A-temporal-horizons.json` and `../claim-audits/audit-A-temporal-horizons.md`.

## PASCAL is not physical hardware validation

The dossier says at one location that PASCAL reports “physical hardware validation.” Appendix A.10 instead reports RTL synthesis in a 40 nm library and a cycle-accurate simulator. No fabricated processor is reported. The correct class is E4.

The dossier also says elsewhere that PASCAL's hardware-adjacent claim remains E5 with an unreported E4 gesture. That is also incorrect. Appendix A.10 reports explicit synthesis and cycle-simulation results. The correct scoped statement is E4 for the uniform `T = 4` PASC-IF overhead experiment, with no hardware evidence for the Adaptive Layerwise schedule.

Affected locations include `research/dossier.md` around lines 913, 2335-2342, and 2476 in the audited worktree.

## PASCAL `T_eff = 3.14` has an undocumented cardinality mismatch

Table 4 lists 17 ResNet-18 CIFAR-10 timestep values. The released `get_Teff.py` contains 10 coefficients for that network. Python `zip()` drops seven values, and the script averages the remaining ten terms. This produces 3.1361557645729463 and explains the printed 3.14. The paper does not document the mapping from 17 choices to 10 energy terms.

Any prose calling `T_eff` a fully specified network-wide weighted mean should carry this reproducibility qualification.

## QAC energy appendix is misattributed

The raw audit says QAC Section 7.8 is “Energy Comparison” and uses Horowitz and Potipireddi. Both accessible OpenReview revisions instead label Section 7.8 “Time Step vs. Bit Width.” Neither contains the cited energy analysis.

The later withdrawn MT-SNN manuscript contains an Appendix C energy analysis using Horowitz, Nagendra, Potipireddi and Asati, and Panda et al. The survey appears to have transferred that appendix backward to QAC.

Affected location: `research/raw/a11-mixed-timestep-audit.md` around lines 99-101.

## QAC and MT-SNN do not establish E3 toolchain paths

Both papers describe how a temporal loop might be changed and warn that temporal alignment may stall a multicore pipeline. Neither provides a target compiler invocation, mapped artifact, runnable hardware configuration, RTL realization, or device execution. Under the survey's definition, this is conceptual execution analysis rather than a documented but unexercised toolchain path.

The evidence class should remain null for those hardware-feasibility claims. Their accuracy results are software results, but this audit does not attach evidence classes to non-deployment claims.

## MT-SNN alignment changed between records

The supplied 23-page manuscript is the withdrawn ICLR 2026 version. It uses average-and-repeat temporal alignment in Eq. 20 and Algorithm 1. The accepted Frontiers abstract instead names Scaled Synaptic Current Accumulation, a fused synaptic-current-domain mechanism.

The records agree on static layerwise timestep allocation and the ImageNet headline. They should not be treated as interchangeable evidence for the alignment implementation until the accepted full text is posted and inspected.

## Temporal Flexibility metadata was reconciled

The canonical source is `temporal-flexibility`. The legacy `mtt` identifier is retained
only as an alias. The registry uses the paper title “Temporal Flexibility in Spiking
Neural Networks: Towards Generalization Across Time Steps and Deployment Friendliness”
and the verified authors Kangrui Du, Yuhang Wu, Shikuang Deng, and Shi Gu.

## The no-hardware conclusion must remain bounded

The existing raw audit uses universal language such as “no simulator or chip can execute” heterogeneous per-layer timesteps. The audited sources do not prove impossibility. They support a narrower statement. None of PASCAL, QAC, MT-SNN, or Temporal Flexibility demonstrates physical execution of a static heterogeneous per-layer discrete-timestep schedule.

NeuroScale and the Loihi 2 LLM paper establish that asynchronous core operation can coexist with a globally synchronized algorithmic timestep. Temporal Flexibility establishes that Speck2e can execute the trained weights in a timestep-free event-driven mode. Neither fact proves a universal platform limitation.
