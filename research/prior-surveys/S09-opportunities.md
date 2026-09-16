# S09. Opportunities for Neuromorphic Computing Algorithms and Applications

## Identity and retrieval

- **Citation:** C. D. Schuman, S. R. Kulkarni, M. Parsa, J. P. Mitchell, P. Date, and B. Kay, “Opportunities for neuromorphic computing algorithms and applications,” *Nature Computational Science*, vol. 2, pp. 10-19, 2022, doi: 10.1038/s43588-021-00184-y.
- **Source type:** Peer-reviewed perspective/review.
- **Retrieval status:** `verified`. The complete 10-page publisher PDF was inspected on 2026-09-16.
- **Inspected local PDF:** `/Users/hamza/Downloads/papers-review/s43588-021-00184-y.pdf`.
- **Inspected URLs:** <https://www.osti.gov/biblio/1881146>; <https://www.researchgate.net/publication/358255092_Opportunities_for_neuromorphic_computing_algorithms_and_applications>; <https://doi.org/10.1038/s43588-021-00184-y>.

## Assessment

**Scope.** The article reviews neuromorphic algorithms and applications, then identifies barriers that separate research demonstrations from real-world use. Its remit includes machine-learning and non-machine-learning workloads.

**Organizing taxonomy.** Machine-learning methods are grouped as spike-based quasi-backpropagation, pretrained-DNN mapping, reservoir computing, evolutionary methods, and plasticity. A separate branch covers graph algorithms, random walks, optimization, and constraint problems. The final sections organize deployment barriers around access, heterogeneous integration, benchmarks, programming abstractions, and full-stack co-design.

**Strongest explanatory contribution.** The article connects algorithm choice to practical deployment failure modes. It explains that DNN-to-SNN mapping can lose accuracy at both conversion and hardware realization, and that host communication can erase a neuromorphic accelerator's apparent performance advantage.

**Deployment depth.** Named demonstrations include keyword spotting, medical-image analysis, and object detection on Loihi or TrueNorth, as well as optimization problems on TrueNorth, Loihi, and SpiNNaker. These examples establish task-to-chip links. They do not provide the model transformations, software versions, mapper constraints, runtime configuration, or measurement boundaries needed for a reproducible route.

**Material omissions.** The article does not survey compilers, executable interchange formats, or vendor toolchains. It diagnoses benchmarking problems but does not classify published evidence by measurement boundary. No example is traced from a trained model to a fully specified physical deployment.

**Verification limits.** Every article page, figure, box, and caption in the supplied publisher PDF was inspected. No supplementary material is embedded in the file. The article is a forward-looking perspective, so some platform and application statements are illustrative rather than exhaustive.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | partial | Box 1 explains integrate-and-fire through Hodgkin-Huxley models, leakage, thresholds, delays, synaptic weights, and plasticity. It does not offer a systematic neuron-model comparison. | Nature Computational Science p. 12, Box 1 |
| B | partial | Spike time, magnitude, and shape are introduced as information carriers. Rate, latency, and population encoding are later identified, but decoding semantics are not treated. | Nature Computational Science pp. 10 and 14 |
| C | full | The article organizes and explains five major learning approaches, including surrogate-gradient methods, reservoir computing, evolutionary optimization, STDP, and direct temporal learning. | Nature Computational Science pp. 12-14; Fig. 2 |
| D | partial | The pretrained-DNN mapping subsection covers normalization, pooling substitution, constrained ANN training, few-spike neurons, accuracy loss, latency reduction, and hardware precision or variation. It is not a comprehensive conversion survey. | Nature Computational Science pp. 12-13, “Mapping a pre-trained deep neural network” |
| E | partial | NEST, Brian, and Nengo are compared by intended use, backend reach, accessibility, and scaling limitations. The treatment diagnoses ecosystem limitations rather than surveying complete framework APIs. | Nature Computational Science p. 15, “Widening usability and access to hardware and simulators” |
| F | mentioned | The article discusses the missing programming abstractions, host-side deployment dependence, and mapping burden, but does not describe a compiler or hardware mapper. | Nature Computational Science pp. 15-16, “Enabling more diverse computing environments” and “Defining programming abstractions” |
| G | none | No model interchange representation is described. | Full-text review, Nature Computational Science pp. 10-19 |
| H | partial | SpiNNaker, BrainScaleS, ODIN, Tianjic, TrueNorth, Loihi, DYNAPs, Neurogrid, and IFAT are situated by purpose and implementation, but hardware architecture is supporting context rather than the organizing focus. | Nature Computational Science p. 11 |
| I | partial | The paper identifies loss at the ANN-to-SNN and SNN-to-hardware boundaries, weight precision and device-variation effects, simulator specialization, host communication overhead, and heterogeneous-integration problems. It does not systematize operator, state, or reset semantics across platforms. | Nature Computational Science pp. 13 and 15 |
| J | none | A dedicated subsection argues that benchmarks and metrics are inadequate, but it does not classify claims as silicon measurement, simulation, or analytical estimate. | Nature Computational Science p. 15, “Defining benchmarks and metrics” |
| K | partial | The review relates machine-learning, control, graph, random-walk, optimization, and constraint workloads to reported accuracy, energy, or time-to-solution results. It does not normalize or tabulate measurements. | Nature Computational Science pp. 13-14 |
| L | mentioned | Several tasks are tied to Loihi, TrueNorth, or SpiNNaker, but the article supplies citations rather than reproducible model-to-toolchain-to-chip traces. | Nature Computational Science pp. 13-14 |
