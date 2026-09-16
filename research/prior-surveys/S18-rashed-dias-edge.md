# S18. Rashed and Dias, Neuromorphic Edge Survey

## Identity and retrieval

A. Rashed and J. Dias, "Towards Neuromorphic Computing on Edge: A Survey on Efficient Techniques for Spiking Neural Networks," *EdgeAI4R* poster, 2025. OpenReview ID WuiVAPrgi3. The OpenReview record and downloadable PDF were inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs and metadata: <https://openreview.net/forum?id=WuiVAPrgi3>; <https://openreview.net/pdf?id=WuiVAPrgi3>; <https://api.openreview.net/notes?forum=WuiVAPrgi3> (fallback unavailable). OpenReview metadata identifies this as an EdgeAI4R poster; peer-review status was not established.

## Scope and assessment

The short survey organizes efficient SNN techniques around neuronal and spiking dynamics, activation mismatch in ANN-to-SNN conversion, error propagation, and latency-accuracy comparisons on ImageNet and CIFAR benchmarks. Its strongest explanatory contribution is the direct connection between temporal horizon T, latency, and model efficiency. It does not investigate software deployment, platform mapping, or on-chip execution. Its treatment of activation mismatch is adjacent to deployment semantics but remains within learning and conversion, not an inter-layer or cross-platform taxonomy.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | LIF dynamics and neuronal-dynamics techniques are surveyed. Locator: Sec. II, Background, and PDF introduction. |
| B | mentioned | Temporal processing and spike patterns are discussed, not a broad coding taxonomy. Locator: Abstract and Introduction. |
| C | partial | Surrogate-gradient approximation and efficiency techniques are reviewed. Locator: Introduction. |
| D | partial | ANN-to-SNN activation mismatch is named as a central training complication, but no comprehensive conversion taxonomy is developed. Locator: OpenReview PDF, abstract and Sec. I, Introduction, pp. 1-2. |
| E | none | No framework comparison was identified. Locator: full-text inspection. |
| F | none | No compiler or mapper analysis was identified. Locator: full-text inspection. |
| G | none | No interchange-format analysis was identified. Locator: full-text inspection. |
| H | none | No named hardware-platform comparison was identified. Locator: full-text inspection. |
| I | none | The paper discusses the ANN-to-SNN learning boundary, not deployment-boundary semantic failures. Locator: OpenReview PDF, abstract and Sec. I, Introduction, pp. 1-2. |
| J | none | Latency-accuracy reports are not an evidence-classification taxonomy. Locator: Abstract and PDF inspection. |
| K | partial | ImageNet, CIFAR-10, and CIFAR-100 latency-accuracy results are reported for reviewed methods. Locator: Introduction. |
| L | none | No trained-network-to-specific-chip route was identified. Locator: full-text inspection. |

## Verification limits

This is a workshop poster and a concise document. Its route and hardware omissions should be understood as scope limits, not evidence that the cited primary methods lack deployment results.
