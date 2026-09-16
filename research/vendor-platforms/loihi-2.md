# Intel Loihi 2

## Audited route

`spikingjelly-to-lava-exchange` → `lava-exchange-to-netx` → `netx-to-loihi2`

The route is blocked at the first edge for the default SpikingJelly rate-conversion output. That output uses subtraction reset with `v_reset=None`, while the Lava exporter rejects this configuration. The downstream NetX and Loihi 2 capabilities are conditional on changing the source contract to a supported fixed reset.

## Sources

`lava-dl-netx-docs` and `lava-github-archived` have verified full text in the source registry. The hardware source `loihi2` and the gated-access source `intel-inrc-confluence` remain metadata-only and provisional. The PilotNet NetX workflow is not assigned as the exercised example for this route because it does not begin with the audited SpikingJelly conversion output.

## Remaining gaps

- No official example exercises the complete SpikingJelly-to-Loihi 2 chain.
- No public source establishes an exact custom Loihi 2 subtraction-reset process model for this route.
- The proprietary hardware extension and successor to the archived Lava stack remain access-limited.

The threshold-reset capability is therefore `unsupported` for the named route, the route state is `blocked`, and all field records remain provisional.
