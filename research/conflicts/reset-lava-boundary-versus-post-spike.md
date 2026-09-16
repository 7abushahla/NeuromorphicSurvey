# Conflict. Lava boundary reset and post-spike reset

Status resolved on 16 September 2026.

## Interpretation A

The names `LIFReset` and `reset_interval` can be read as evidence that Lava or NetX exposes a
configurable post-spike reset mechanism, possibly including reset by subtraction.

## Interpretation B

Lava 0.10.0 `LIFReset` periodically clears both current and voltage according to an interval and
offset. It retains the ordinary LIF hard-zero rule after a spike. NetX 0.6.0 selects `LIFReset`
only when `reset_interval` is present. The HDF5 CUBA and LOIHI neuron schema has no post-spike
reset-mode field.

## Resolution

Interpretation B is verified. `reset_interval` is a sample or network boundary mechanism. It must
not be cited as support for subtractive post-spike reset. The distinction also applies to the
official NIR-to-Lava-DL example, which requires the caller to clear persistent current and voltage
after a forward pass. That step is `host-assisted` boundary management. It does not change the
built-in neuron's hard-zero post-spike rule.

## Evidence

- Lava 0.10.0, `src/lava/proc/lif/process.py`, `LIF` and `LIFReset`.
- Lava 0.10.0, `src/lava/proc/lif/models.py`, `reset_voltage` and
  `PyLifResetModelFloat.run_spk`.
- Lava-DL 0.6.0, `src/lava/lib/dl/netx/hdf5.py`, `reset_interval` and
  `get_neuron_params`.
- NIR 1.0.8, `docs/source/examples/lava/nir_to_lava.py`, module warning.
