# BrainChip Akida 1.0

## Audited route

`quantizeml-to-cnn2snn` → `cnn2snn-to-akida`

The evidence stack records a physical Akida route. The route transforms a supported quantized graph into Akida event-domain operators. It is not a direct execution of a classical binary rate-coded IF network over a user-selected horizon.

## Sources

`brainchip-cnn2snn-docs` has verified full text. `brainchip-akida-user-guide`, which supports hardware-specific fields, remains metadata-only and provisional. The generic CNN2SNN workflow is not assigned as a field-level exercised example because the current source record does not identify a concrete device run and output boundary for every field.

## Remaining gaps

- The hardware guide needs full-text inspection with stable locators.
- Arbitrary synaptic filters and learned delay tensors are outside the documented CNN2SNN route.
- Edge learning is limited to the final fully connected layer under strict one-bit constraints.
- Product availability is time-sensitive and must be checked before publication.

The presence of one verified software source does not justify verified platform claims. All records therefore remain provisional.
