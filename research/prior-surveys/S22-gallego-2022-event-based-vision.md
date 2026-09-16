# S22. Gallego et al. (2022), event-based vision

## Identity and retrieval

Guillermo Gallego, Tobi Delbruck, Garrick Orchard, Chiara Bartolozzi, Brian Taba, Andrea Censi, Stefan Leutenegger, Andrew J. Davison, Jorg Conradt, Kostas Daniilidis, and Davide Scaramuzza, "Event-based Vision: A Survey," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 44, no. 1, pp. 154-180, 2022. doi: 10.1109/TPAMI.2020.3008413. Source type, peer reviewed. Retrieval status, full text verified on 2026-09-16 from the accepted manuscript.

Inspected URLs:

- https://arxiv.org/pdf/1904.08405
- https://www.semanticscholar.org/reader/dd971c07879e1ce12b06991319528c06280eeb9b
- https://www.research-collection.ethz.ch/handle/20.500.11850/397839
- https://doi.org/10.1109/TPAMI.2020.3008413

## Scope and contribution

This is an event-camera and event-vision survey, not an SNN deployment survey. Its structure follows sensor operation and properties, event processing methodologies, applications, neuromorphic processors and embedded systems, then software, datasets, and simulators. Its strongest explanatory contribution is the sensor-to-algorithm account of asynchronous events, including the event-generation model and sensor limitations. Deployment depth reaches sensing hardware and embedded processing, not trained SNN compilation.

Material omissions include ANN-to-SNN conversion, SNN framework comparison, compiler mapping, interchange formats, an evidence-class scheme, and a complete trained-network-to-chip route. Its discussion of sensor constraints is not an I-axis taxonomy of layer or platform semantics.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | none | The paper concerns camera and event models, not SNN neuron-model coverage. |
| B | full | Sections 2.1-2.4 define event output, polarity, timestamps, contrast thresholds, and event-generation models. |
| C | mentioned | The abstract and Section 4 mention learning-based techniques without a training-method taxonomy. |
| D | none | No ANN-to-SNN conversion treatment was located. |
| E | partial | Section 6 surveys software, datasets, and simulators for event cameras. |
| F | none | Section 5 discusses processors and embedded systems, not compiler or mapper toolchains. |
| G | none | No interchange-format treatment was located. |
| H | full | Sections 2.1-2.5 and 5 survey event cameras, their hardware properties, and embedded processors. |
| I | mentioned | Section 2.3 explains sensing-specific representation, noise, and timing challenges, but not deployment-edge semantics. |
| J | mentioned | Section 2.5 warns that camera characteristics are not measured under a common testbed, without evidence classes. |
| K | full | Sections 1 and 4 organize applications from low-level vision to recognition, reconstruction, and robotics. |
| L | none | No trained SNN to named-chip route is demonstrated. |
