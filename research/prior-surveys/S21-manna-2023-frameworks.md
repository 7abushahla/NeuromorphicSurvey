# S21. Manna et al. (2023), SNN frameworks

## Identity and retrieval

Davide Liberato Manna, Alex Vicente, Paul Kirkland, Trevor Bihl, and Gaetano Di Caterina, "Frameworks for SNNs: a Review of Data Science-oriented Software and an Expansion of SpykeTorch," arXiv:2302.07624, 2023. Source type, preprint. Retrieval status, full text verified on 2026-09-16.

Inspected URLs:

- https://arxiv.org/html/2302.07624
- https://arxiv.org/abs/2302.07624

## Scope and contribution

The paper reviews nine Python-oriented, data-science SNN frameworks and introduces SpykeTorch-Extended. Its organizing taxonomy is framework-by-framework. Table 1 compares framework features, while Sections 3.1 through 3.4.6 explain Nengo, SNN Toolbox, Lava, Norse, PySNN, snnTorch, SpikingJelly, BindsNet, and SpykeTorch. The strongest contribution is the feature-level framework inventory, including available neuron models, learning rules, conversion support, and destination backends. Deployment depth is compatibility reporting only. It does not validate an export or measurement route.

Material omissions include a common semantic contract for exports, operator and reset fidelity, hardware evidence classes, and measured end-to-end deployment. Claims about a framework destination backend are not proof that every model reaches that backend.

## Coverage scores

| Axis | Score | Basis and locator |
|---|---|---|
| A | partial | Abstract and Section 3 compare framework availability of neuron models, rather than offering a model taxonomy. |
| B | none | No coding taxonomy was located in Sections 1-5. |
| C | partial | Abstract and Sections 3.1-3.4.6 inventory STDP, BP, surrogate gradients, and related learning rules. |
| D | partial | Sections 3.1 and 3.2 discuss NengoDL, SNN Toolbox, Lava, BindsNet, and SpikingJelly conversion support. |
| E | full | Abstract, Section 3, and Table 1 are a nine-framework review. |
| F | partial | Sections 3.1-3.2 identify destination platforms and conversion targets, but do not compare compiler constraints or mapping semantics. |
| G | none | No interchange representation is surveyed. |
| H | partial | Sections 3.1-3.2 name Loihi, SpiNNaker, FPGA, and other destinations as framework backends. |
| I | none | No cross-framework edge-semantics analysis is supplied. |
| J | none | No evidence-classification scheme is supplied. |
| K | none | The review does not organize applications by measured results. |
| L | mentioned | Section 3 lists reachable destination backends, but presents neither a validated route nor deployment measurements. |
