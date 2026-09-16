# S25. Shrestha et al. (2022), models and hardware

## Identity and retrieval

Amar Shrestha, Haowen Fang, Zaidao Mei, Daniel Patrick Rider, Qing Wu, and Qinru Qiu, "A Survey on Neuromorphic Computing: Models and Hardware," *IEEE Circuits and Systems Magazine*, vol. 22, no. 2, pp. 6-35, 2022, doi: 10.1109/MCAS.2022.3166331. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16.

Local full text:

- `/Users/hamza/Downloads/papers-review/A_Survey_on_Neuromorphic_Computing_Models_and_Hardware.pdf`

Inspected URLs:

- https://doi.org/10.1109/MCAS.2022.3166331

## Scope and contribution

This survey is organized around algorithm-hardware co-design. It explains computational models, neural codes, learning rules, implementation choices, communication, supporting software, and five platform case studies. Its strongest contribution for the present survey is the way it connects model semantics to concrete platform support. Examples include the incompatibility between temporal models and TrueNorth's simplified neuron dynamics, the encoding error caused by time-multiplexed updates, Loihi's compiler stages, SpiNNaker's PACMAN translation layer, and Tianjic's direct and indirect training paths.

The paper provides substantial software and mapping coverage rather than merely listing SDK names. It distinguishes mapping, programming, and simulation tools, then relates specific toolchains to TrueNorth, Loihi, BrainScaleS, SpiNNaker, and Tianjic. It remains a platform survey rather than a portability study. It does not compare one model across targets, define an interchange format, or classify the evidentiary status of reported performance numbers.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Section II-A and II-B, pp. 8-10, derive conductance-based and spike-based models, including HH, Izhikevich, IF, LIF, SRM, synaptic kernels, reset, and implementation implications. |
| B | full | Section II-C, pp. 10-11, compares rate, latency or TTFS, phase, and task-specific codes, with latency, spike-count, quantization, model, and hardware trade-offs. |
| C | full | Section II-E, pp. 13-14, covers STDP, supervised Hebbian learning, spike-domain backpropagation, local credit assignment, and Loihi demonstration constraints. Section V-A, pp. 25-26, treats online learning limits. |
| D | mentioned | Section IV-B.3, p. 21, notes Nengo-based DNN-to-SNN conversion for Loihi. Section IV-E.5, p. 24, distinguishes Tianjic direct training from ANN-to-SNN indirect training. Conversion algorithms are not reviewed. |
| E | full | Section III-E, p. 17, distinguishes mapping, programming, and simulation tools. Sections IV-A to IV-E, pp. 20-24, compare Corelet and Eedn, NxSDK and Nengo, PyNN, NEST, Brian, sPyNNaker, PACMAN, and platform APIs. |
| F | full | Section III-E, p. 17, states mapping objectives and hardware constraints. Sections IV-A.3, IV-B.3, IV-D.3, and IV-E.5, pp. 20-24, explain Eedn mapping, Loihi compiler stages, PACMAN, and Tianjic's automatic compiler. |
| G | none | No portable interchange representation or NIR-like semantic format is analyzed. |
| H | full | Sections III and IV, pp. 15-24, explain design choices and detailed TrueNorth, Loihi, BrainScaleS, SpiNNaker, and Tianjic case studies. Tables II and III compare platform capabilities. |
| I | partial | Sections II-C, III, and IV, pp. 10-24, identify model-support mismatches, time-multiplexing delay, fixed-point limits, routing constraints, and software abstractions. The paper does not systematize cross-platform semantic loss at every deployment boundary. |
| J | none | Tables II and III compare platform specifications but do not classify reported results by physical measurement, simulation, or analytical estimate. |
| K | partial | Sections IV-A.3, IV-B.3, and IV-E.6, pp. 20-24, report measured TrueNorth throughput and power and describe Loihi and Tianjic applications. Application evidence is selective rather than systematically tabulated. |
| L | partial | The TrueNorth Eedn discussion, pp. 20-21, and Tianjic toolchain and unmanned-bicycle case, p. 24, connect training or mapping support to named hardware and applications. Neither is documented as a reproducible end-to-end route. |

## Verification limits

All 30 PDF pages were inspected. Pages 23-30 are biographies and references. Pages 5-21 of the article, corresponding to PDF pages 1-17, received detailed review. Table II was rendered to verify platform model, architecture, and software-support entries. The local IEEE Xplore copy resolves the former access limitation.
