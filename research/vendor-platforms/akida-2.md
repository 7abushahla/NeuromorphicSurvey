# BrainChip Akida 2.0

## Audited route

`quantizeml-to-cnn2snn` → `cnn2snn-to-akida`

These evidence-stack edges terminate at the generic Akida target. They establish the software route but do not by themselves demonstrate a particular Akida 2.0 FPGA or production-silicon execution. The route state is therefore `unexercised` for the generation-specific claim.

## Sources

`brainchip-cnn2snn-docs` has verified full text. `brainchip-akida-user-guide` and `brainchip-metatf-2-19-2-release` remain metadata-only and provisional. The release note establishes version and FPGA-image alignment. It is not an exercised deployment example and is never accepted as one by the validator.

## Remaining gaps

- A generation-specific device example with measured output is required.
- BufferTempConv and related blocks provide bounded temporal state, not general synaptic dynamics or learned delays.
- Current documentation restricts edge learning to Akida 1.0, although Akida 2.0 temporal processors may retain inference state.
- Public evidence does not establish a generally available AKD2000 production chip.

All records remain provisional. The release note supports version constraints only.
