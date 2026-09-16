# S26. Chen et al. (2026), neuromorphic chips

## Identity and retrieval

G. Chen, M. Xu, Y. Chen, F. Yuan, L. Qin, and J. Ren, "A New Era in Computing: A Review of Neuromorphic Computing Chip Architecture and Applications," *Chips*, vol. 5, no. 1, art. 3, 2026, doi: 10.3390/chips5010003. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16.

Local full text:

- `/Users/hamza/Downloads/papers-review/chips-05-00003-v3.pdf`

Inspected URLs:

- https://www.mdpi.com/2673-8024/5/1/3
- https://doi.org/10.3390/chips5010003

## Scope and contribution

This review surveys neuromorphic chips through five comparison dimensions. These are process technology, scale, power consumption, neuronal models, and architectural features. It organizes platforms into analog-digital hybrid, digital-only, and memristor implementations, then surveys applications in artificial intelligence, embodied intelligence, neuroscience, and adaptive control.

Its strongest contribution is the breadth of its architecture and workload inventory. The application section includes selected quantitative claims, such as sub-100 mW DYNAPs robotic navigation and reported energy-efficiency improvements for memristor systems. Table 7 also distinguishes several weak evidence states, including proposed low power with no data and inferred low power. This is useful evidence discipline, but it is not a general classification applied consistently across all chip and application claims.

The paper does not explain ANN-to-SNN conversion, software deployment pathways, or compiler behavior. NEST, Brian 2, mapping, and integrated toolchains appear primarily as limitations or future needs. Several deployment statements identify a chip and workload, but the paper does not trace the model, training procedure, compiler, hardware configuration, and measurement method as one reproducible route.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | full | Sections 2.1 and 2.2, pp. 3-7, cover HH, IF, LIF, memristive Izhikevich, feedforward, convolutional, and recurrent SNN models and relate them to hardware. |
| B | mentioned | Sections 2.2 and 2.3, pp. 6-7, identify spikes as spatiotemporal codes. Section 3.1.3, p. 13, notes temporal coding as a circuit trade-off. No coding or decoding taxonomy is developed. |
| C | mentioned | Sections 2 and 3, pp. 5-16, repeatedly identify STDP, temporal backpropagation, surrogate-gradient engines, and on-chip learning support, but do not compare direct-training methods. |
| D | none | No substantive ANN-to-SNN conversion method or conversion-error analysis was identified. |
| E | mentioned | Section 5, p. 40, names NEST and Brian 2 and discusses the lack of integrated deployment solutions. No framework capabilities are compared. |
| F | mentioned | Sections 3.2 and 5-6, pp. 19 and 40-41, mention programmable mapping and the need for integrated deployment toolchains. No compiler or mapper is explained. |
| G | none | No interchange format or portable semantic representation is treated. |
| H | full | Section 3, pp. 8-31, provides sustained treatment of Neurogrid, BrainScaleS, DYNAPs, ROLLS, Loihi, SpiNNaker, TrueNorth, Tianjic, PAICORE, ODIN, Loihi 2, SpiNNaker 2, and memristor systems. |
| I | partial | Sections 3.1.5, 3.2.7, and 5, pp. 13-14, 23-24, and 40-41, compare flexibility, plasticity, timing, scalability, architecture diversity, and integration limits. The discussion does not identify semantic loss across model, framework, compiler, and platform boundaries. |
| J | partial | The five-dimensional framework and Tables 2-7 compare physical metrics. Table 7, p. 31, explicitly marks no-data and inferred entries. The survey does not consistently separate silicon measurement, simulation, and analytical proxy across all claims. |
| K | full | Section 4, pp. 31-39, covers image and speech processing, NLP, robotics, BCI, closed-loop biomedical systems, autonomous driving, smart homes, and energy management, with several reported power and efficiency results. |
| L | partial | Sections 3.3.5 and 4, pp. 29-38, describe a physically mapped memristor reinforcement-learning network and named chip deployments in robotics, speech, prosthetics, and control. The routes omit the complete training, compiler, configuration, and measurement chain. |

## Verification limits

All 45 PDF pages were inspected. Pages 42-45 are references. Pages 8-41 received section-level review, and Table 7 was rendered to verify that its no-data and inferred labels were visually present. The local open-access PDF resolves the former retrieval failure. Reported application measurements were checked for presence in the review but not independently validated against every cited primary study.
