# Conflict. Does NIR encode subtractive reset?

Status resolved on 16 September 2026.

## Interpretation A

The raw source audit states that NIR defines subtractive reset as a primitive alongside hard reset.
It therefore attributes SpikingJelly's rejection of `v_reset=None` to an incomplete exporter. See
`research/raw/a18-snntoolbox-vs-spikingjelly.md`, line 196.

## Interpretation B

NIR 1.0.8 defines `CubaLIF`, `IF`, and `LIF` with a fixed `v_reset`. The equations assign
`v_reset` after a spike. The implementation replaces a missing or null value with zero. No reset
mode or subtract-threshold field exists. The official primitive table gives the same fixed-value
form.

## Resolution

Interpretation B is supported for NIR 1.0.8. SpikingJelly's exporter is conservative and correct
when it refuses to serialize subtractive reset into this schema. The 2024 NIR paper compares
networks trained with subtractive and zero-reset discretizations, but those experiment choices do
not establish a graph field for reset mode. Backend behavior and formal interchange semantics must
remain separate.

The version boundary is material. Commit
`6189cacd1b1e89d1e587afd90f0f8930361bae98` added `v_reset` on 30 May 2025. The 2024 paper
artifact predates the current field. The canonical claim should cite tagged NIR source and current
documentation, with the paper used for backend mismatch evidence.

## Evidence

- NIR 1.0.8, commit `490ce8e03d74c24efeb9a120a6caaf5a67d34aee`,
  `nir/ir/neuron.py`, `CubaLIF`, `IF`, and `LIF`.
- NIR 1.0.8, `docs/source/primitives.md`, primitive table.
- J. E. Pedersen et al., "Neuromorphic intermediate representation," *Nature
  Communications*, 2024, pp. 5-8, doi: 10.1038/s41467-024-52259-9.
- SpikingJelly 2.0.0rc1, `activation_based/nir_exchange/to_nir.py`, `_hard_reset`.
