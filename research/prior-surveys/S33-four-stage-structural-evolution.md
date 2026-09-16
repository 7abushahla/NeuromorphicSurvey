# S33 Four-Stage Structural Evolution Framework

## Identity and retrieval

Hao He and Shuang Gao. *A Four-Stage Structural Evolution Framework for Spiking Neural Networks: A Review and Perspective from Binary ANN to Event-Driven Models*. *Neural Processing Letters*, 58, article 14, 2026. DOI 10.1007/s11063-025-11832-z. Publisher open-access full text was substantively inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://link.springer.com/article/10.1007/s11063-025-11832-z.

## Scope and assessment

The review deliberately restricts its scope to discrete-time, directly trained, ANN-style LIF SNNs. It organizes models into binary ANN, temporal dimension introduction, temporal accumulation, and reset and sparsity control. The strongest contribution is this structural decomposition, especially its explanation of reset and accumulation. It is not a hardware deployment survey. ANN-to-SNN conversion appears only as a complementary route.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | mentioned | Sections 1 and 2 specify the target as discrete-time LIF-style SNNs, without a broad neuron-model survey. |
| B | none | Section 2.2 explicitly states that exhaustive encoding classification is outside scope. |
| C | partial | Sections 1 and 2 frame the analysis around directly trained SNNs and surrogate-gradient difficulty. |
| D | partial | Section 2 and Table 1 position ANN-to-SNN conversion as a complementary training route rather than reviewing it in depth. |
| E | none | No framework comparison is supplied. |
| F | none | No compiler or hardware-mapping analysis is supplied. |
| G | none | No interchange format is discussed. |
| H | none | Hardware is motivational context, not a reviewed platform taxonomy. |
| I | none | Section 2.4 discusses within-neuron reset dynamics, not semantic failures between deployment layers or platforms. |
| J | none | No evidence-classification framework is provided. |
| K | none | Applications with measured results are outside the review scope. |
| L | none | No end-to-end deployment route is reported. |

## Verification limits

The publication date is 2026-01-07. The paper is recent but is a published open-access review. Its conclusions apply only to the declared ANN-style, directly trained LIF subset.
