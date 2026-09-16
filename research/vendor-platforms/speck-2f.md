# SynSense Speck 2f

## Audited route

`sinabs-to-dynapcnn-mapper` → `dynapcnn-mapper-to-samna` → `samna-to-speck`

The evidence stack classifies this as a physical route. The Sinabs NIR-to-Speck tutorial is a verified full-text candidate example, but the generated matrix leaves example fields null until each contract field is tied to an exact tutorial cell or device output.

## Sources

The technical source is `synsense-speck-datasheet`, the Speck Development Kit Manual 2025.12 V2. It remains metadata-only and provisional in the source registry. The route also depends on Sinabs 3.1.3. The exact samna runtime version is not established.

## Remaining gaps

- The manual must be inspected and registered at full-text level with stable section locators.
- The inference path retains membrane state but exposes no online synaptic learning.
- The integrated DVS is native, while output aggregation and the sample termination window are host responsibilities.
- Arbitrary synaptic filters and learned delay tensors are unsupported by the audited convolutional path.

These distinctions produce host-assisted encoder-decoder and time-termination records. All records remain provisional pending source promotion and field-specific example grounding.
