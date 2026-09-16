# SpiNNaker 2

## Audited route

`spikingjelly-to-nir-exchange` → `nir-exchange-to-nir` → `nir-to-spinnaker2`

The route is blocked because the SpikingJelly exporter rejects the default subtraction-reset conversion output. A downstream SpiNNaker 2 importer may support additional reset configuration, but it cannot recover a graph that the upstream exporter did not produce.

## Sources

The technical sources are `spinnaker2-tools` and `spinnaker2-nir-import-docs`. Both remain metadata-only and provisional. The generic NIR importer example is not assigned as an exercised example for the complete SpikingJelly route.

## Remaining gaps

- No official example starts with a default SpikingJelly rate-conversion graph and reaches SpiNNaker 2.
- The importer documentation does not establish a general plasticity contract for imported graphs.
- Exact delay coverage is model-specific and requires a versioned mapping test.

The route state is `blocked`, threshold reset is `unsupported` for this route, and plasticity remains `undocumented`. Software-defined neuron and time execution are classified as native platform behavior rather than emulation. All records remain provisional.
