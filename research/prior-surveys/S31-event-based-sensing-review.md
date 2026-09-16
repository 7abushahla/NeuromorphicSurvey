# S31 Event-Based Sensing and Signal Processing Review

## Identity and retrieval

Mohammad-Hassan Tayarani-Najaran and Michael Schmuker. *Event-Based Sensing and Signal Processing in the Visual, Auditory, and Olfactory Domain: A Review*. *Frontiers in Neural Circuits*, 15, 610446, 2021. DOI 10.3389/fncir.2021.610446. Publisher full text was substantively inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://doi.org/10.3389/fncir.2021.610446, https://public-pages-files-2025.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2021.610446/text, and https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2021.610446/full.

## Scope and assessment

This is a tri-modal event-sensing review. It organizes the literature by vision, audition, and olfaction, after explaining signal-driven sampling and address-event representation. Its strongest contribution is comparison of shared sensing principles and modality-specific maturity. It covers sensors and applications rather than SNN training, ANN-to-SNN conversion, or post-training deployment. AER is discussed as a sensor communication protocol, not as a general model interchange layer.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | none | The focus is sensing and signal processing, not a neuron-model taxonomy. |
| B | full | Sections 1 and 1.1 analyze event-driven sampling, send-on-delta, AER, timing, and address representations. |
| C | none | No SNN training-method taxonomy is present. |
| D | none | ANN-to-SNN conversion is outside scope. |
| E | none | No SNN software-framework treatment is provided. |
| F | none | No compiler or mapper taxonomy is provided. |
| G | none | Section 1.1 discusses AER, but not NIR or model interchange. |
| H | full | Sections 3 to 5 review visual event cameras, silicon cochleae, and olfactory sensing systems. |
| I | none | The sensor interface is explained, but the paper does not assess neural-model boundary semantics. |
| J | none | No physical-versus-simulation-versus-proxy evidence taxonomy is supplied. |
| K | full | Sections 3 to 5 synthesize visual, auditory, and olfactory applications. |
| L | none | No complete trained-SNN-to-specific-chip deployment route is given. |

## Verification limits

Sensor AER should not be conflated with NIR-level interchange or with end-to-end SNN deployment evidence.
