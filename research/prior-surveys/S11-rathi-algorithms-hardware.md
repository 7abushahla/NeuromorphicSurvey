# S11. Rathi et al., Algorithms to Hardware

## Identity and retrieval

N. Rathi, I. Chakraborty, A. K. Kosta, A. Sengupta, A. Ankit, P. Panda, and K. Roy, "Exploring Neuromorphic Computing Based on Spiking Neural Networks: Algorithms to Hardware," *ACM Computing Surveys*, vol. 55, no. 12, art. 243, pp. 1-49, 2023. DOI: 10.1145/3571155. The ACM article page and its open PDF were inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs: <https://dl.acm.org/doi/10.1145/3571155>; <https://dl.acm.org/doi/pdf/10.1145/3571155>.

## Scope and assessment

The review connects deep-SNN algorithms to hardware. Its organization proceeds from algorithmic fundamentals and training to neuromorphic APIs and libraries, hardware technologies, and open challenges. Its strongest explanatory contribution is the explicitly multistack framing of SNN learning and hardware constraints. It inventories platforms and applications, but does not trace a fixed trained network through a reproducible compiler-to-chip route. It also does not define deployment-boundary semantics or an evidence-class taxonomy separating silicon measurement, simulation, and operation-count estimates.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Neuron dynamics and models are treated in the Algorithms section. Locator: Sec. 2, Algorithms. |
| B | full | Spike-train representation and temporal encoding are explicit algorithmic topics. Locator: Sec. 2, Algorithms. |
| C | full | Local, conversion-assisted, and gradient-based learning are surveyed. Locator: Sec. 2, Algorithms. |
| D | full | ANN-to-SNN conversion appears as a named training route. Locator: Sec. 2, Algorithms, "Spike-based backpropagation: ANN-to-SNN." |
| E | partial | APIs and libraries are reviewed, without a deployment-fidelity comparison. Locator: Sec. 2.5, Neuromorphic APIs and Libraries. |
| F | partial | The article relates workload requirements to platforms but does not systematically compare compiler or mapper toolchains. Locator: Introduction and hardware discussion. |
| G | none | No interchange representation or cross-framework IR taxonomy was identified. Locator: full-text inspection of organization and APIs discussion. |
| H | full | Dedicated hardware discussion names multiple neuromorphic architectures and device technologies. Locator: Introduction and hardware sections. |
| I | none | No taxonomy of semantic failures at training, conversion, mapping, and execution boundaries was identified. Locator: full-text inspection. |
| J | none | No literature-wide classification of physical, simulated, and proxy evidence was identified. Locator: full-text inspection. |
| K | partial | Applications are used to motivate and illustrate algorithms and hardware, but not normalized as a measured-results registry. Locator: Introduction and hardware examples. |
| L | none | The review does not provide a complete, reproducible trained-network-to-named-chip route. Locator: full-text inspection. |

## Verification limits

The review is broad rather than deployment-audit oriented. Absence scores concern its organizing treatment, not the absence of isolated primary studies in its reference list.
