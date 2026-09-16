# SpiNNaker 1

## Audited route

`snn-toolbox-to-spynnaker` → `spynnaker-to-spinnaker1`

The evidence stack contains physical deployment evidence for this route family. SpiNNaker executes software-defined neuron and synapse kernels natively on its ARM cores. The capability matrix therefore does not label ordinary kernel execution as emulation. Graph lowering and fixed-point conversion remain transformations.

## Sources

The canonical technical source is `spynnaker-v8-docs`. It remains metadata-only and provisional. Generic sPyNNaker installation and execution documentation is not treated as a field-level exercised example for the SNN Toolbox route.

## Remaining gaps

- The documentation date is not established independently of the versioned URL.
- The exact SpiNNTools component version paired with sPyNNaker 8.0.0 is not established.
- Built-in cells do not preserve SNN Toolbox subtraction reset. A bespoke C model is possible, but the named route does not establish that implementation.

The threshold-reset field is `unsupported` for the selected route. All records remain provisional until the versioned documentation and route-specific example are inspected at field level.
