# Conflict. Sinabs and NIR reset preservation

Status resolved on 16 September 2026.

## Interpretation A

The current stack record marks Sinabs reset preservation through NIR as unknown. The physical
NIR-to-Speck tutorial and the 2024 NIR paper can be read as evidence that an accepted route
preserves the represented neuron contract.

## Interpretation B

Sinabs 3.1.3 changes the reset rule in both directions. `sinabs.from_nir` constructs
`IAFSqueeze` and `LIFSqueeze` without passing the NIR node's `v_reset`. The instantiated Sinabs
neurons therefore use the subtractive default. `sinabs.to_nir` creates NIR IF and LIF nodes without
recording the Sinabs `reset_fn`. NIR 1.0.8 converts the omitted field to fixed zero.

## Resolution

Interpretation B is verified for Sinabs 3.1.3 and NIR 1.0.8. The import and export edges are
`transformed`. The official NIR-to-Speck notebook remains valid E2 deployment evidence because it
stores accuracy from a physical Speck 2F module. It does not establish semantic equivalence. The
notebook reaches native subtractive reset on Speck after the NIR fixed-reset field has been ignored.

This is a silent mismatch. Unlike SpikingJelly's NIR exporter, Sinabs does not reject an
unrepresentable or unhandled reset. The survey should therefore state the transformation directly.

## Evidence

- Sinabs 3.1.3, commit `d84078e0af1bc40f716b61de199880bd8713bd2d`, `sinabs/nir.py`,
  import lines 86-108 and export lines 156-171.
- Sinabs 3.1.3, `sinabs/from_torch.py` and `sinabs/activation/reset_mechanism.py`, subtractive
  defaults.
- NIR 1.0.8, `nir/ir/neuron.py`, missing `v_reset` handling.
- Sinabs NIR-to-Speck notebook, commit `8b87dc310dc9f626c6ba7fe3a8271ab253d5e95b`, cells 5,
  9, and 15.
