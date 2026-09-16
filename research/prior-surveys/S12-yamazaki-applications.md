# S12. Yamazaki et al., Applications Review

## Identity and retrieval

K. Yamazaki, V.-K. Vo-Ho, D. Bulsara, and N. Le, "Spiking Neural Networks and Their Applications: A Review," *Brain Sciences*, vol. 12, no. 7, art. 863, 2022. DOI: 10.3390/brainsci12070863. The publisher full text was inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs: <https://www.mdpi.com/2076-3425/12/7/863>; <https://www.mdpi.com/2076-3425/12/7/863/pdf> (fallback timed out).

## Scope and assessment

This broad review is organized around biological neurons, spike-based neuron and synapse models, ANN foundations, SNN training, frameworks, and applications in computer vision and robotics. Its strongest contribution is practical orientation for researchers entering SNN development, especially its explicit framework and application sections. It names hardware as context, but offers neither compiler or mapper analysis nor a reproducible end-to-end hardware route. It has no framework for deployment semantic drift or evidence class.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Multiple biological and spike-based neuron models are reviewed. Locator: Sec. 2, Biological Neurons, and neuron-model discussion. |
| B | partial | Temporal coding is motivated, but coding is not the principal taxonomy. Locator: Introduction and SNN foundations. |
| C | full | The stated contributions include detailed training guidance. Locator: Abstract, contribution (v), and training section. |
| D | partial | ANN and SNN distinctions and training pathways are discussed, but conversion is not a central organizing axis. Locator: Abstract and ANN/SNN training discussion. |
| E | full | Available spike-based implementation frameworks are explicitly reviewed. Locator: Abstract, contribution (vi), and frameworks section. |
| F | none | No comparative compiler or hardware-mapping toolchain taxonomy was identified. Locator: full-text inspection. |
| G | none | No interchange-format treatment was identified. Locator: full-text inspection. |
| H | mentioned | Neuromorphic hardware is listed as deployment context. Locator: Introduction, TrueNorth, Loihi, SpiNNaker, and NeuroGrid examples. |
| I | none | No deployment-boundary semantics taxonomy was identified. Locator: full-text inspection. |
| J | none | No evidence-classification framework was identified. Locator: full-text inspection. |
| K | full | Computer vision and robotics applications are a stated survey contribution. Locator: Abstract, contribution (vii), and applications sections. |
| L | none | No trained-network-to-specific-chip route with measured deployment evidence was identified. Locator: full-text inspection. |

## Verification limits

The PDF endpoint did not return through Exa, but the publisher HTML supplied substantive full text. Scores are limited to the review's own organization and stated coverage.
