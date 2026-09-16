# Conflict. Current NIR reset fields and historical Lava evidence

Status resolved on 16 September 2026.

## Interpretation A

The 2024 NIR paper reports NIR execution through Lava and Loihi 2. This can be read as validation
that the current NIR reset field survives the NIR-to-Lava route.

## Interpretation B

The current `v_reset` field was added in May 2025. The NIR 1.0.8 official Lava example does not
read this field in either its Lava LIF branch or its Lava-DL IF and CUBA-LIF branches. Those target
neurons use hard reset to zero.

## Resolution

Interpretation B governs the current route. The 2024 paper remains E2 physical evidence for the
historical NIR artifact and the tested configurations. It cannot validate a field that did not yet
exist. Under NIR 1.0.8, a nonzero fixed reset is `transformed` to zero by the official example.
Only a zero-valued reset is preserved at this boundary.

The paper's subtractive and zero-reset SRNN experiments also do not change this conclusion. Their
reset choice was part of experiment and backend configuration. It was not a current NIR reset-mode
field.

## Evidence

- NIR commit `6189cacd1b1e89d1e587afd90f0f8930361bae98`, 30 May 2025.
- NIR 1.0.8 official Lava example, `_nir_node_to_lava` and `_nir_node_to_lava_dl`.
- Lava 0.10.0 LIF process models and Lava-DL 0.6.0 leaky-integrator dynamics.
- J. E. Pedersen et al., "Neuromorphic intermediate representation," *Nature
  Communications*, 2024, doi: 10.1038/s41467-024-52259-9.
