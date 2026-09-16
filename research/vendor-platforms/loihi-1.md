# Intel Loihi 1

## Audited route

`snn-toolbox-to-nxtf` → `nxtf-to-nxsdk` → `nxsdk-to-loihi1`

The evidence stack classifies this as a physical route. The route preserves the classical SNN Toolbox subtraction-reset model by using NxTF's two-compartment construction. This is a transformation with an explicit resource cost, not native single-compartment subtraction reset.

## Sources

The technical source is `loihi2`, the Intel Loihi 2 technology brief. Its comparison table supports a bounded set of first-generation properties. It remains metadata-only and provisional in the source registry. The historical `slayer-nxtf-gesture` repository is not used as an exercised example because it does not exercise the SNN Toolbox upstream route.

## Remaining gaps

- A generation-specific, fully inspected NxSDK or NxTF manual is still required for several detailed field claims.
- NxSDK 0.9.5 is identified at the route boundary, but a complete NxTF release identifier is not established.
- No field-level exercised-example reference is assigned until the example is shown to use the complete named route.

These gaps require every Loihi 1 capability record to remain provisional.
