# S19. Xie et al., DSNN Compression Survey

## Identity and retrieval

H. Xie, G. Yang, and W. Gao, "Toward Efficient Deep Spiking Neuron Networks: A Survey on Compression," in *Generalizing from Limited Resources in the Open World*, pp. 18-31, 2024. DOI: 10.1007/978-981-97-6125-8_2. The arXiv HTML full text and Springer chapter landing page were inspected through Exa. Retrieval status is `full_text`; verification status is `verified`.

Inspected URLs: <https://arxiv.org/html/2407.08744>; <https://arxiv.org/abs/2407.08744>; <https://link.springer.com/chapter/10.1007/978-981-97-6125-8_2>.

## Scope and assessment

This specialized survey is organized around DSNN background, computational units, pruning, quantization, knowledge distillation, firing-rate reduction, and time-step pruning. Its strongest explanatory contribution is the explicit compression taxonomy, which recognizes spike activity and temporal-horizon reduction as SNN-specific efficiency levers. It treats deployment to neuromorphic hardware as motivation, not as an audited execution pipeline. It does not compare toolchains, formalize edge semantics, classify evidence types, or trace a model to a named chip.

## A-L coverage

| Axis | Score | Basis and locator |
|---|---|---|
| A | mentioned | LIF and other neuron models provide background, not the core taxonomy. Locator: Sec. 2.1, Biological Background. |
| B | none | No encoding taxonomy was identified. Locator: full-text inspection. |
| C | partial | Compression methods include training-time pruning, quantization, and distillation mechanisms. Locator: Sec. 3, Methods. |
| D | none | ANN-to-SNN conversion is cited in the literature but is not a surveyed compression axis. Locator: Sec. 3 and full-text inspection. |
| E | none | No framework comparison was identified. Locator: full-text inspection. |
| F | none | No compiler or mapper comparison was identified. Locator: full-text inspection. |
| G | none | No interchange-format discussion was identified. Locator: full-text inspection. |
| H | mentioned | Neuromorphic chips motivate efficient DSNNs, without a platform taxonomy. Locator: Abstract and Introduction. |
| I | none | No deployment-boundary semantic taxonomy was identified. Locator: full-text inspection. |
| J | none | No evidence-classification framework was identified. Locator: full-text inspection. |
| K | none | Compression results are discussed, but the survey does not organize applications with measured deployment results. Locator: Sec. 3 and full-text inspection. |
| L | none | No end-to-end route from trained network to named hardware was identified. Locator: full-text inspection. |

## Verification limits

The Springer record supplies metadata and references only. The substantive scoring is based on the inspected arXiv HTML full text.
