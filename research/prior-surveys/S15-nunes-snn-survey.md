# S15. Nunes et al., SNN Survey

## Identity and retrieval

J. D. Nunes, M. Carvalho, D. Carneiro, and J. S. Cardoso, "Spiking Neural Networks: A Survey," *IEEE Access*, vol. 10, pp. 60738-60764, 2022. DOI 10.1109/ACCESS.2022.3179968.

The complete 27-page publisher PDF was inspected. The local file used for verification was `/Users/hamza/Downloads/papers-review/Spiking_Neural_Networks_A_Survey.pdf`. Retrieval status is `full_text` and verification status is `verified`.

Inspected URLs are <https://doi.org/10.1109/ACCESS.2022.3179968>, <https://ieeexplore.ieee.org/document/9798188>, <https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9798188>, and <https://www.researchgate.net/publication/360977407_Spiking_Neural_Networks_A_Survey>.

## Scope and taxonomy

The survey is organized around biological inspiration rather than deployment. It begins with LIF dynamics and STDP, follows the visual pathway from retina to cortex, separates rate and temporal codes, and then compares ANN-to-SNN conversion with unsupervised and supervised direct training. Section VI adds a practical component. It reproduces STDP and surrogate-gradient experiments with BindsNET and snnTorch, tabulates reported accuracies, and discusses autonomous-driving examples.

Its strongest explanatory contribution is the connection between biological mechanisms, coding choices, and learning rules. Section IV explains why rate and temporal codes make different latency and information-preservation trade-offs. Section V then relates those codes to conversion, STDP, surrogate gradients, and temporal backpropagation. Table 1 provides a compact cross-study view of architecture, learning method, encoding, time steps, dataset, and accuracy.

Deployment treatment remains bounded. The survey identifies conversion-specific operator limitations, distinguishes a training-time layer-response model from the neuron used for hardware inference, compares a small set of software frameworks, and cites one Loihi deployment. It does not review compilers, mapping toolchains, interchange formats, or vendor-specific execution constraints. It also does not classify whether each reported energy or efficiency claim is measured on silicon, simulated, or estimated.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | partial | Section II derives LIF membrane, threshold, reset, refractory, and STDP dynamics, while other neuron models are named rather than compared. PDF pp. 3-4, publication pp. 60740-60741. |
| B | full | Section IV develops count, density, population-rate, TTFS, rank-order, phase, and burst coding with equations, biological evidence, and latency trade-offs. PDF pp. 9-11, publication pp. 60746-60748. |
| C | full | Section V treats STDP-based unsupervised learning, surrogate-gradient supervision, temporal backpropagation, EventProp, DIET-SNN, PLIF, and residual SNNs. PDF pp. 11-16, publication pp. 60748-60753. |
| D | partial | Section V.A explains rate-based conversion, near-lossless normalization approaches, activation mismatch, operator restrictions, firing-rate cost, and conversion accuracy limitations, but does not provide a broad conversion taxonomy. PDF pp. 11-12, publication pp. 60748-60749. |
| E | partial | Section VI implements BindsNET and snnTorch and compares their abstractions, GPU support, intended learning modes, and simulation-time behavior, with Brian used as a reference point. PDF pp. 16-21, publication pp. 60753-60758. |
| F | none | No compiler, graph partitioner, mapper, placement tool, or hardware toolchain is reviewed. Full-text inspection, Sections I-VII. |
| G | none | No interchange representation or cross-framework intermediate format is discussed. Full-text inspection, Sections I-VII. |
| H | mentioned | Neuromorphic hardware motivates efficiency claims, SpiNNaker appears in a reviewed example, and one Loihi implementation is summarized, but platforms are not surveyed comparatively. PDF pp. 8, 21-22, publication pp. 60745 and 60758-60759. |
| I | partial | The paper identifies conversion mismatches in firing-rate assumptions and ANN operator support, and Figure 11 distinguishes a training abstraction from the inference neuron. It does not generalize these issues into a stack-wide or cross-platform semantic taxonomy. Section V.A and Fig. 11, PDF pp. 12 and 14, publication pp. 60749 and 60751. |
| J | none | Tables report accuracy and isolated efficiency claims, but the paper does not classify claims by physical measurement, hardware simulation, analytical model, or software-only evidence. Table 1 and Section VI, PDF pp. 16-22, publication pp. 60753-60759. |
| K | partial | Table 1 and Tables 2-4 report benchmark accuracies, and Section VI discusses measured computer-vision and autonomous-driving results. Coverage is concentrated on classification and a few autonomous-driving examples rather than a cross-domain measured-results synthesis. PDF pp. 16-22, publication pp. 60753-60759. |
| L | mentioned | The survey names a SOEL model trained for N-CARS and implemented on Loihi at a reported 350 mW, but it does not document the software, mapping, configuration, or measurement route needed to reproduce the deployment. PDF p. 21, publication p. 60758. |

## Omissions and verification limits

The paper does not provide a deployment contract, a compiler or mapper comparison, an interchange-format analysis, or a claim-level evidence taxonomy. Its framework discussion is based mainly on two packages used by the authors. Its Loihi example is a literature summary rather than a worked deployment case.

The coverage audit used the complete PDF and visually inspected the pages containing the coding taxonomy, conversion discussion, algorithm table, application results, and conclusion. The audit verifies what the survey covers. It does not independently reproduce the experiments or validate every quantitative claim that the survey attributes to its cited studies.
