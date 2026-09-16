# S32 Neuromorphic Vision Sensor Review

## Identity and retrieval

Claudio Cimarelli, Jose Andres Millan-Romera, Holger Voos, and José Luis Sánchez-López. *Hardware, Algorithms, and Applications of the Neuromorphic Vision Sensor: a Review*. arXiv:2504.08588, 2025. DOI 10.48550/arXiv.2504.08588. Substantive arXiv HTML full text was inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://doi.org/10.48550/arxiv.2504.08588, https://arxiv.org/abs/2504.08588, https://arxiv.org/html/2504.08588, and https://arxiv.org/pdf/2504.08588.

## Scope and assessment

The review follows a sensor-to-algorithm-to-application sequence. Its strongest contribution is its hardware-evolution timeline and its organization of event-camera algorithms and practical use cases. It describes AER event packets and the adaptation burden imposed by sparse asynchronous data, but it does not analyze SNN deployment semantics or provide a route from trained network to neuromorphic chip.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | none | No spiking-neuron model taxonomy is part of the review. |
| B | partial | Sections I and II explain event packets, timestamps, polarity, and AER representations, but do not survey neural coding schemes. |
| C | none | No SNN training taxonomy is provided. |
| D | none | ANN-to-SNN conversion is outside scope. |
| E | none | No SNN-framework comparison is provided. |
| F | none | No SNN compiler or hardware-mapping taxonomy is provided. |
| G | none | AER is a sensor protocol here, not a reviewed general interchange format. |
| H | full | Section II and the sensor timeline compare neuromorphic vision hardware generations and models. |
| I | none | The paper identifies the need to adapt vision algorithms to event data, but does not formalize deployment-boundary semantics. |
| J | none | Case studies are not categorized by evidence class. |
| K | full | Section IV presents practical application case studies across industries and scenarios. |
| L | none | No trained SNN is traced through software to a named compute chip. |

## Verification limits

The paper concerns vision sensing and computer-vision processing. Its hardware treatment does not establish SNN compute-platform compatibility.
