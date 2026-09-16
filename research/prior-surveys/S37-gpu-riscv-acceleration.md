# S37 GPU and RISC-V Acceleration Survey

## Identity and retrieval

Edris Zaman Farsa, Amirhossein Ilkhani, Marc Reichenbach, Amirreza Yousefzadeh, Arash Ahmadi, Alexander Serb, and J. Harkin. *GPU and RISC-V Acceleration for Neuromorphic Computing Based on Spiking Neural Networks: Taxonomy, Comparison, and Open Challenges*. *Neuromorphic Computing and Engineering*, accepted manuscript, 2026. DOI 10.1088/2634-4386/aea4eb. The publisher page and accepted-manuscript full text were substantively inspected on 2026-09-16. Retrieval status is `verified`.

Inspected URLs include https://iopscience.iop.org/article/10.1088/2634-4386/aea4eb and https://iopscience.iop.org/article/10.1088/2634-4386/aea4eb/pdf.

## Scope and assessment

This accepted manuscript reviews 71 studies from 2015 to 2025. It organizes GPU work into simulation frameworks, training acceleration, large-scale and multi-GPU simulation, and application deployments. It organizes RISC-V work into instruction-set extensions and tightly coupled cores, accelerator SoCs, programmable processors, and edge deployments. Its strongest contribution is a metric-coverage analysis that explains why reported GPU and RISC-V results cannot support fair head-to-head comparison. It does not construct an NIR-like interchange taxonomy or trace a common trained model through multiple named chips.

## Coverage A-L

| Axis | Score | Basis and locator |
| --- | --- | --- |
| A | partial | Section II and Figure 1 introduce LIF and Izhikevich models, but this is not a broad neuron-model survey. |
| B | partial | Section II and Figure 1 distinguish rate, temporal, population, and phase coding in accelerator context. |
| C | partial | Section II and Figure 1 identify STDP, surrogate gradients, and ANN-to-SNN conversion, but learning is not the principal taxonomy. |
| D | mentioned | Section II names ANN-to-SNN conversion as a learning strategy without a conversion-method survey. |
| E | full | Sections II and IV catalog GPU software ecosystems and simulation frameworks, including CUDA, OpenCL, PyTorch, TensorFlow, and SNN tools. |
| F | full | Sections III to V provide the GPU and RISC-V taxonomy, including instruction-set extensions, tightly coupled cores, accelerator SoCs, and programmable processors. |
| G | none | No general SNN interchange format is reviewed. |
| H | full | Sections II to V compare GPU, RISC-V, FPGA, ASIC, and dedicated neuromorphic hardware roles. |
| I | partial | Sections II and VI identify fixed neuron, precision, connectivity, memory, and integration constraints across accelerator classes, but do not formalize layer-by-layer semantic preservation. |
| J | partial | Abstract and Section VI analyze disjoint reporting of runtime, speedup, power, latency, memory, throughput, and energy, but do not define the physical-silicon, simulation, and proxy tripartite scheme. |
| K | none | Application deployment is a taxonomy category, but no cross-application measured-results synthesis is the paper’s focus. |
| L | mentioned | The RISC-V edge-deployment category identifies deployment studies, without tracing one standardized model through a complete route. |

## Verification limits

The text is an accepted manuscript published online on 2026-09-09. It is peer reviewed but is not yet a finalized version of record. Its comparative conclusions should retain the manuscript-status qualifier.
