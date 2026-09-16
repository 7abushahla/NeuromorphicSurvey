# S28. Hu et al. (2024), large-scale SNNs

## Identity and retrieval

Yangfan Hu, Qian Zheng, Guoqi Li, Huajin Tang, and Gang Pan, "Toward Large-scale Spiking Neural Networks: A Comprehensive Survey and Future Directions," arXiv:2409.02111, 2024, doi: 10.48550/arXiv.2409.02111. Source type, preprint. Retrieval status, full text verified on 2026-09-16.

Inspected URLs:

- https://arxiv.org/html/2409.02111
- https://arxiv.org/abs/2409.02111
- https://doi.org/10.48550/arxiv.2409.02111

## Scope and contribution

This survey targets deep and large-scale SNNs, especially spiking Transformers. Its organizing taxonomy has two principal branches, learning methods, ANN-to-SNN conversion and direct surrogate-gradient training, and network architectures, DCNNs and Transformer architectures. Tables I through III synthesize reported benchmark accuracy and model results. The strongest explanatory contribution is the account of conversion error sources, reset-by-subtraction, temporal quantization, and methods for deep SNN construction. Deployment depth remains algorithm and benchmark reporting. It does not trace an implementation through a specific hardware toolchain.

Material omissions include framework and compiler comparison, interchange formats, physical hardware-platform evidence, evidence classes, and an end-to-end deployment route. Its discussion of reset is conversion-method analysis, not a cross-platform edge-semantics taxonomy.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | mentioned | Section 2.1.1 explains IF neurons and reset behavior in conversion, without a broad neuron-model taxonomy. |
| B | mentioned | Sections 2-3 refer to binary spikes and temporal information, without a dedicated encoding taxonomy. |
| C | full | Section 2.1 divides learning methods into ANN-to-SNN conversion and direct surrogate-gradient training. |
| D | full | Section 2.1.1 explains conversion mechanisms, conversion errors, normalization, calibration, and Table I. |
| E | none | No SNN framework comparison is supplied. |
| F | none | No compiler or mapper taxonomy is supplied. |
| G | none | No interchange-format treatment is supplied. |
| H | none | Hardware platforms are not a survey axis. |
| I | none | Reset and quantization are analyzed within methods, not as deployment-boundary semantics. |
| J | none | Benchmark tables do not classify physical, simulated, and estimated evidence. |
| K | partial | Tables I-III compare accuracy across CIFAR-10, ImageNet, DVS data, and Transformer applications. |
| L | none | No complete trained-network-to-chip route is documented. |
