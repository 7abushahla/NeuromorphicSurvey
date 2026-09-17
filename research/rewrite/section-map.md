# Section and Anchor Map

Reviewed 2026-09-16.

This map freezes the article order and stable anchors before prose is rewritten. The
displayed titles match `data/site-manifest.json`. Writers may add lower-level anchors,
but they must not rename the section or subsection anchors listed here without an
integration review.

| Section | Stable section anchor | Stable subsection anchors | Required function |
|---|---|---|---|
| 1. Introduction | `introduction` | `survey-question`, `scope-and-reader`, `existing-surveys`, `survey-contributions`, `survey-roadmap` | Establish the deployment question, scope, family-level prior-work synthesis, E1 through E5 guide, motivating two-population question, contributions, and reading order. Keep the complete 37-work matrix. |
| 2. Computation and Representation | `computation-and-representation` | `one-stack-many-vocabularies`, `values-state-events`, `dense-sparse-conditional`, `neuromorphic-event-driven`, `representation-execution`, `foundations-referrals` | Place the survey in the one stack that neuroscience, electronics, and machine learning describe in different vocabularies, and define the computational objects that later equations, codes, and deployment claims use. State where the survey enters that stack and refer the layers it does not treat to their primary sources. |
| 3. Neuron and Synapse Dynamics | `neuron-and-synapse-dynamics` | `membrane-circuit-model`, `common-state-update`, `neuron-model-family`, `synaptic-state-and-delay`, `reset-and-refractory`, `continuous-discrete-hardware`, `load-bearing-semantics` | Derive neuron and synapse variants from one update model. Separate mathematical dynamics, numerical discretization, and hardware realization. |
| 4. Temporal Semantics, Neural Codes, and Decoding | `temporal-semantics-codes-decoding` | `time-vocabulary`, `encoder-channel-decoder`, `code-families`, `code-tradeoffs`, `deployment-terminology` | Define all meanings of time before comparing codes. Compare every code through the same encoder, transmitted representation, decoder, horizon, precision, and cost template. |
| 5. Learning Paradigms and the Two Branches | `learning-paradigms-two-branches` | `spike-learning-problem`, `direct-conversion-hybrid`, `branch-convergence`, `evidence-guide` | Introduce direct training, conversion, and hybrid routes as a fork whose outputs must satisfy one deployable contract. Close by defining the claim-level evidence classes E1 through E5 that every deployment claim from Section 6 onward carries. |
| 6. Direct SNN Training | `direct-snn-training` | `local-learning`, `surrogate-gradients`, `online-learning`, `training-cost`, `hardware-aware-learning`, `direct-training-output`, `learning-referrals` | Explain only the distinctions that affect deployment. Refer outward for specialist learning theory and algorithms. |
| 7. Classical ANN-to-SNN Conversion | `classical-ann-to-snn-conversion` | `conversion-purpose-assumptions`, `relu-rate-correspondence`, `input-and-readout`, `parameter-mapping`, `architecture-preparation`, `conversion-walkthrough`, `asymptotic-finite-time`, `classical-failure-cases` | Give one complete derivation and end-to-end pipeline before introducing remedies. |
| 8. Finite-Time Error and Low-Latency Conversion | `finite-time-error-low-latency` | `finite-time-error-model`, `clipping-discretization`, `residual-reset`, `unevenness-timing`, `architecture-dependent-error`, `encoding-readout-error`, `low-t-design-problem` | Locate each error at the pipeline stage where it enters. Separate deterministic finite-window error from stochastic encoding variance. |
| 9. Advanced Conversion Methods | `advanced-conversion-methods` | `activation-shaping`, `potential-reset-calibration`, `neuron-interventions`, `temporal-allocation`, `adaptive-inference`, `alternative-code-conversion`, `hardware-aware-conversion`, `hybrid-fine-tuning`, `emerging-architectures` | Organize methods by intervention and the Section 8 error they target. Keep evidence class and hardware status claim-specific. |
| 10. The Deployable SNN Contract | `deployable-snn-contract` | `contract-purpose`, `contract-fields`, `definition-representation-execution`, `contract-conformance` | Define the 11 fields that both learning branches must make explicit. Distinguish mathematical definition, software representation, and faithful execution. |
| 11. Where an SNN Runs | `where-an-snn-runs` | `three-targets-one-network`, `conventional-platforms`, `simulated-emulated-neuromorphic`, `simulator-library-catalog`, `physical-neuromorphic-silicon`, `targets-referrals` | Names the three targets, compares the paths, catalogs simulators and libraries. |
| 12. Software, Interchange, and Compilation | `software-interchange-compilation` | `framework-boundary`, `serialization-ir`, `export-compile-map`, `runtime-host-io`, `semantic-transformations`, `software-referrals` | Follow the software path in process order. Type every edge by input, output, preservation, transformation, rejection, route state, and evidence. |
| 13. Hardware Execution Models | `hardware-execution-models` | `synchronous-digital`, `asynchronous-digital`, `programmable-manycore`, `analog-mixed-signal`, `fpga-asic`, `conventional-emerging`, `platform-contract-comparison` | Compare execution families through contract fields. Use platform examples only with generation, toolchain version, capability status, and evidence limits. |
| 14. Complete Deployment Routes | `complete-deployment-routes` | `route-definition`, `physical-routes`, `routes-conventional-targets`, `approximate-transformed-routes`, `blocked-unexercised-routes`, `route-selection` | Trace named routes edge by edge. Do not infer a route from compatible-looking nodes. Place the interactive map after the prose synthesis. |
| 15. Deployment Measurement | `deployment-measurement` | `deployment-metrics`, `measurement-boundaries`, `baseline-and-batching`, `event-rate-static-power`, `uncertainty-pareto`, `measurement-checklist` | Define what was measured and where. Make chip, board, host, sensor-to-decision, modeled, and physical boundaries explicit. |
| 16. Applications and Deployment Evidence | `applications-deployment-evidence` | `vision-workloads`, `audio-temporal-workloads`, `control-robotics`, `scientific-industrial`, `cross-workload-evidence` | Organize cases by workload. Record input provenance, learning route, code, on-device portion, boundary, baseline, reproducibility, and evidence class. |
| 17. What the Evidence Shows | `what-the-evidence-shows` | `population-counts`, `rate-code-falsifier`, `semantic-findings`, `route-measurement-findings`, `evidence-interpretation-boundary` | Answer the motivating question using generated counts and verified counterexamples. Separate demonstrated findings from causal or sociological interpretation. |
| 18. Open Problems and Research Agenda | `open-problems-research-agenda` | `failed-contract-edges`, `algorithm-hardware-codesign`, `portable-semantics`, `measurement-reproducibility`, `access-and-maintenance`, `research-agenda` | Derive research problems from failed or unverified contract edges rather than listing generic future work. |
| 19. Researcher Entry Guide and Conclusion | `researcher-entry-guide-conclusion` | `reading-paths`, `route-choice-guide`, `minimum-reporting-checklist`, `specialist-referrals`, `conclusion` | Give field-entry paths, practical questions, minimum reporting requirements, and a concise conclusion. |

## Cross-section placement rules

1. Define a term at its earliest required section. Later sections link back instead of
   defining it again.
2. Define E1 through E5 only in `evidence-guide`. Later sections apply the labels per
   claim.
3. Introduce the two-population proposition only as a motivating question in Section 1.
   Present counts, falsifiers, and qualifications in Section 17.
4. Introduce time vocabulary in Section 4. Sections 7 through 18 must distinguish an
   algorithmic horizon from hardware time and wall-clock latency.
5. Introduce the 11-field contract in Section 10. Sections 12 through 18 use those field
   names without inventing parallel taxonomies.
6. Present targets in Section 11, families in Section 13, routes in Section 14,
   measurement in Section 15, workload evidence in Section 16. A platform inventory does
   not replace a route or measurement analysis.
7. Put specialized referrals at the boundary of the topic they delimit. Each referral
   states what the cited source explains and why the survey stops there.

