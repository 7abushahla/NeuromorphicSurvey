# S35 NeuroTrain Local Learning Survey

## Identity and retrieval

Alessio Caviglia, Filippo Marostica, Roberta Bardini, Alessandro Savino, and Stefano Di Carlo. *NeuroTrain: Surveying Local Learning Rules for Spiking Neural Networks with an Open Benchmarking Framework*. arXiv:2605.15058, 2026. DOI 10.48550/arXiv.2605.15058. Substantive arXiv HTML full text was inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://arxiv.org/abs/2605.15058, https://arxiv.org/html/2605.15058, and https://arxiv.org/pdf/2605.15058. The PDF retrieval timed out. The HTML inspection is the evidentiary basis.

## Scope and assessment

This preprint surveys SNN training algorithms, with local learning as its principal organizing lens. It pairs taxonomy with NeuroTrain, an open snnTorch-based framework for controlled comparisons. The strongest contribution is the explicit taxonomy by training strategy, supervision, and locality together with a reusable benchmarking environment. The paper does not supply a physical deployment route or classify literature evidence as silicon, simulation, and proxy measurements.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | partial | Section 2.1 explains spiking computation, LIF behavior, thresholding, reset, and refractoriness, but does not provide a broad model taxonomy. |
| B | mentioned | Sections 2.1 and 2.2 discuss spike timing and temporal state, without a coding taxonomy. |
| C | full | Abstract, Sections 1 to 4, and the declared taxonomy cover surrogate gradients, local and three-factor rules, plasticity, conversion, and non-standard optimization. |
| D | partial | Abstract and Sections 1 and 3 include ANN-to-SNN conversion among reviewed training strategies, while direct training is central. |
| E | full | Abstract and Section 5 define NeuroTrain as an open, snnTorch-based, modular implementation and benchmarking framework. |
| F | none | No compiler or hardware-mapping toolchain taxonomy is provided. |
| G | none | No interchange format is covered. |
| H | mentioned | Sections 1 and 2.5 discuss neuromorphic hardware suitability in general terms. |
| I | none | Locality concerns learning-signal availability, not semantic compatibility at deployment boundaries. |
| J | mentioned | Sections 1 and 5 emphasize controlled reproducible benchmarks, but do not classify physical, simulation, and proxy deployment evidence. |
| K | none | Benchmark datasets are used, but the paper is not an applications-with-measured-results survey. |
| L | none | No end-to-end trained-network-to-chip route is reported. |

## Verification limits

The arXiv record labels the work for *Neurocomputing*, but publication status beyond the preprint was not independently verified. Claims should cite the retrieved preprint unless a version of record is located.
