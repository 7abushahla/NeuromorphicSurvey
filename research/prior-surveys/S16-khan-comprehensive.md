# S16. Khan et al., Comprehensive Survey

## Identity and retrieval

A. H. Khan, X. Cao, C. Luo, S. Zhang, W. Guo, V. N. Katsikis, and S. Li, "Spiking Neural Networks: A Comprehensive Survey of Training Methodologies, Hardware Implementations and Applications," *Artificial Intelligence Science and Engineering*, vol. 1, no. 3, pp. 175-207, 2025. DOI 10.23919/AISE.2025.000013.

The complete 33-page publisher PDF was inspected. The local file used for verification was `/Users/hamza/Downloads/papers-review/Spiking_Neural_Networks_A_Comprehensive_Survey_of_Training_Methodologies_Hardware_Implementations_and_Applications.pdf`. Retrieval status is `full_text` and verification status is `verified`.

Inspected URLs are <https://doi.org/10.23919/AISE.2025.000013> and <https://aise-journal.org/article/view/13>.

## Scope and taxonomy

This is a broad tutorial survey. It progresses from biological principles and computational neuron models to spike coding, four training routes, specialized hardware, application domains, ANN-SNN comparison, and open challenges. The training taxonomy separates ANN-to-SNN conversion, direct gradient-based training, STDP, and hybrid approaches. The hardware taxonomy separates digital, analog and mixed-signal, and emerging implementations. The application taxonomy covers vision, robotics, edge and IoT, brain-computer interfaces, temporal signals, cognitive computing, and emerging uses.

Its strongest explanatory contribution is the explicit convergence of algorithmic and hardware constraints. Section 4 presents equations and practical limitations for the four learning routes. Sections 5.4 and 5.7 then connect weight precision, connectivity, learning support, placement, routing, and hardware-aware optimization to target platforms. Sections 8.4-8.6 identify software immaturity, incompatible programming models, neuron-model differences, precision limits, and routing constraints as barriers to deployment.

The paper nevertheless stops short of an executable deployment route. It discusses mapping and compilation at the level of requirements and research directions. It does not compare concrete compiler pipelines, SDKs, mapper behavior, or vendor-supported operator sets. Its application survey is extensive, but the narrative does not systematically preserve measurement provenance. The hardware comparison also places reported values in one table without classifying whether they come from fabricated silicon, simulation, or analytical estimates.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Sections 3.4-3.6 compare Hodgkin-Huxley, LIF, EIF, AdEx, Izhikevich, SRM, stochastic neurons, synaptic dynamics, and adaptive behavior with equations and complexity trade-offs. PDF pp. 9-12, publication pp. 183-186. |
| B | full | Sections 3.3-3.5 explain rate, temporal, first-spike, phase, population-vector, sparse, and timing-dependent representations and connect them to learning. PDF pp. 8-10, publication pp. 182-184. |
| C | full | Sections 4.2.2-4.3 cover surrogate-gradient direct training, STDP, hybrid training, temporal credit assignment, regularization, adaptive thresholds, progressive training, and memory constraints. PDF pp. 12-14, publication pp. 186-188. |
| D | partial | Section 4.2.1 explains rate-based ANN-to-SNN conversion, weight normalization, burst and temporal coding refinements, and latency concerns. The treatment is a compact route summary rather than a systematic conversion-method taxonomy. PDF p. 12, publication p. 186. |
| E | partial | Sections 8.3.4, 8.4, and 8.5.2 compare the maturity and capabilities of SpikingJelly, Norse, and Brian2 with conventional ML ecosystems and discuss missing debugging, model-zoo, MLOps, and deployment support. PDF pp. 24-25, publication pp. 198-199. |
| F | partial | Sections 5.4, 5.7, and 8.6 discuss neuron placement, communication routing, mapping objectives, compilation, memory hierarchy, and hardware-aware optimization, but do not compare named compiler or mapper toolchains. PDF pp. 15-16 and 26, publication pp. 189-190 and 200. |
| G | mentioned | Neuromorphic Intermediate Representation is presented as a hardware-agnostic graph and neuron representation for portability, without a format-level analysis. Section 6.7, PDF p. 20, publication p. 194. |
| H | full | Section 5 compares TrueNorth, Loihi, SpiNNaker, BrainScaleS, DYNAP-SE, Darwin, and emerging devices, including neuron support, precision, connectivity, learning mode, and energy figures in Tables 4-5. PDF pp. 14-16, publication pp. 188-190. |
| I | partial | The survey identifies incompatible programming models and neuron implementations, precision and dynamic-range limits, connectivity and routing constraints, and platform-specific learning support. These are not organized as a boundary-by-boundary semantic contract. Sections 5.4, 8.5.3, and 8.6, PDF pp. 15 and 25-26, publication pp. 189 and 199-200. |
| J | none | Sections 5.5 and 8.3 discuss metrics and standardization, but the paper does not classify the provenance of literature claims as physical measurement, hardware simulation, model estimate, or software-only result. PDF pp. 15-16 and 23-24, publication pp. 189-190 and 197-198. |
| K | partial | Section 6 surveys applications across seven workload families and cites selected performance claims. It does not present a normalized measured-results registry or consistently state measurement conditions. PDF pp. 16-22, publication pp. 190-196. |
| L | none | No case study traces a trained network through a named framework, conversion or compilation path, mapping configuration, physical chip, and measurement protocol. Sections 5-8, PDF pp. 14-28, publication pp. 188-202. |

## Omissions and verification limits

The survey does not provide an operator-level deployment contract, a concrete toolchain comparison, a claim-level evidence taxonomy, or a reproducible network-to-chip route. Its treatment of NIR is brief. Its wide application coverage is primarily descriptive, and deployment measurements are not normalized across hardware or workloads.

The coverage audit used the complete PDF and visually inspected the pages containing coding, training, hardware constraints, platform comparison, software infrastructure, and deployment challenges. The audit verifies coverage and stated structure. It does not independently validate every numerical hardware value, forecast, or application claim reproduced by the survey.
