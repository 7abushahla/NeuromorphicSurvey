# S13. Ivanov et al., Neuromorphic AI Systems

## Identity and retrieval

D. Ivanov, A. Chezhegov, M. Kiselev, A. Grunin, and D. Larionov, "Neuromorphic artificial intelligence systems," *Frontiers in Neuroscience*, vol. 16, art. 959626, 2022. DOI: 10.3389/fnins.2022.959626. Publisher HTML and PDF were inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs: <https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.959626/full>; <https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.959626/pdf>.

## Scope and assessment

The paper classifies neuromorphic AI systems by brain-inspired features such as connectionism, parallelism, asynchrony, impulse communication, local learning, sparsity, analog computation, and in-memory computation. It then surveys named projects and memristive prospects. Its strongest explanatory contribution is this feature-based hardware taxonomy. The coverage remains architectural and project descriptive. It does not develop SNN training or conversion methodology, toolchain analysis, deployment-semantics auditing, or a traceable network-to-chip route.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | mentioned | Impulse communication and brain features are discussed, without a neuron-model taxonomy. Locator: Abstract. |
| B | none | No encoding taxonomy was identified. Locator: full-text inspection. |
| C | none | No SNN training-method taxonomy was identified. Locator: full-text inspection. |
| D | none | No ANN-to-SNN conversion treatment was identified. Locator: full-text inspection. |
| E | none | No software-framework comparison was identified. Locator: full-text inspection. |
| F | none | No compiler or mapping-toolchain comparison was identified. Locator: full-text inspection. |
| G | none | No interchange-format analysis was identified. Locator: full-text inspection. |
| H | full | The review inventories TrueNorth, Loihi, Tianjic, SpiNNaker, BrainScaleS, NeuronFlow, DYNAP, Akida, Mythic, and memristive approaches. Locator: Abstract and project overview. |
| I | none | Feature classification does not analyze semantic breaks between toolchain boundaries. Locator: Abstract and full-text inspection. |
| J | none | No evidence-type classification was identified. Locator: full-text inspection. |
| K | mentioned | Recent neuromorphic application advances are cited, not consolidated as measured applications. Locator: Abstract. |
| L | none | No end-to-end deployment case route was identified. Locator: full-text inspection. |

## Verification limits

The paper's system taxonomy should not be conflated with deployment compatibility or execution-fidelity evidence.
