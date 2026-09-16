# SynSense Xylo Audio 2

## Audited route

`rockpool-to-xylo-mapper` → `xylo-mapper-to-xylo`

The evidence stack classifies the Rockpool mapping and Xylo execution path as physical. The fixed recurrent core provides native synchronous integer LIF execution. Graph extraction, parameter quantization, sample duration, monitoring, and application decoding remain software responsibilities.

## Sources

The technical source is `rockpool-xylo-docs`, and `rockpool-quickxylo-docs` is the candidate deployment example. Both remain metadata-only and provisional. Rockpool 3.1.0 is identified, while the exact samna runtime version and documentation date are not established.

## Remaining gaps

- No field-level example locator has been verified against the current Rockpool tutorial.
- The core supports decaying synaptic states but not general learned axonal-delay tensors.
- The audio front end is native, while task decoding and run termination are host-assisted.
- Persistent neuron and synaptic state is supported, but online weight plasticity is not documented.

All records remain provisional until the documentation and example are inspected in full.
