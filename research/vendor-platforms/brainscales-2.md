# BrainScaleS-2

## Audited route

`hxtorch-to-brainscales2`

The matrix selects one coherent hxtorch route. It no longer combines the independent PyNN and NIR possibilities into one disconnected route list. The evidence stack classifies the selected route as physical.

## Sources

The technical source is `hxtorch`, referenced through documentation commit `7821187`. It remains metadata-only and provisional. The hxtorch introduction is a candidate hardware example, but no example is assigned to individual records until its cells and observed outputs are inspected.

## Remaining gaps

- A package release corresponding to the documentation commit is not established.
- Analog LIF and synaptic behavior require calibration and are not bit-exact software execution.
- Supported analog synaptic dynamics do not establish arbitrary software delay preservation.
- Hardware-in-the-loop learning combines ASIC state with host-side optimization and must remain host-assisted.

All records remain provisional because the sole canonical technical source has not been promoted beyond metadata-only inspection.
