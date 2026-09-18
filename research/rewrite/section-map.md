# Section and Anchor Map

Reviewed 2026-09-18.

This map freezes the article order and stable anchors before prose is rewritten. The
displayed titles match `data/site-manifest.json`. Writers may add lower-level anchors,
but they must not rename the section or subsection anchors listed here without an
integration review.

| Section | Stable section anchor | Stable subsection anchors | Required function |
|---|---|---|---|
| 1. Introduction | `introduction` | `existing-surveys`, `survey-contributions`, `survey-roadmap` | Establish the deployment question, scope, family-level prior-work synthesis, motivating two-population question, contributions, and reading order. Keep the complete 37-work matrix. |
| 2. Computation and Representation | `computation-and-representation` | `one-stack-many-vocabularies`, `values-state-events`, `dense-sparse-conditional`, `neuromorphic-event-driven`, `representation-execution`, `foundations-referrals` | Place the survey in the one stack that neuroscience, electronics, and machine learning describe in different vocabularies, and define the computational objects that later equations, codes, and deployment claims use. State where the survey enters that stack and refer the layers it does not treat to their primary sources. |
| 3. Neuron and Synapse Dynamics | `neuron-and-synapse-dynamics` | `membrane-circuit-model`, `common-state-update`, `neuron-model-family`, `synaptic-state-and-delay`, `reset-and-refractory`, `continuous-discrete-hardware`, `load-bearing-semantics` | Derive neuron and synapse variants from one update model. Separate mathematical dynamics, numerical discretization, and hardware realization. |
| 4. Temporal Semantics, Neural Codes, and Decoding | `temporal-semantics-codes-decoding` | `time-vocabulary`, `encoder-channel-decoder`, `code-families`, `code-tradeoffs`, `deployment-terminology` | Define all meanings of time before comparing codes. Compare every code through the same encoder, transmitted representation, decoder, horizon, precision, and cost template. |
| 5. Where an SNN Runs | `where-an-snn-runs` | `evidence-guide`, `three-targets-one-network`, `conventional-platforms`, `simulated-emulated-neuromorphic`, `event-npu`, `physical-neuromorphic-silicon` (with the six execution families as 5.6.1 through 5.6.6, `synchronous-digital`, `asynchronous-digital`, `programmable-manycore`, `analog-mixed-signal`, `fpga-asic`, `conventional-emerging`), `targets-referrals` | Define the E1 through E5 grade every deployment claim carries, state the three questions that separate every target (where the memory sits, the axis of Figure 18; what the silicon computes; how time passes), name the three targets and compare the paths between them, place the conventional, simulated, and event NPU targets on the first two questions and cross them in the matrix of Table 11 and Figure 20, then describe each execution family of the physical bucket, sorted by the third question, before any network is fitted to it. Use platform examples only with generation, toolchain version, capability status, and evidence limits. |
| 6. The Two Branches | `learning-paradigms-two-branches` | `spike-learning-problem`, `direct-conversion-hybrid`, `branch-convergence` | Introduce direct training, conversion, and hybrid routes as a fork whose outputs must satisfy one deployable contract. The claim-level evidence classes E1 through E5 are defined once, in Section 5.1, and applied to every deployment claim throughout. |
| 7. Direct SNN Training | `direct-snn-training` | `local-learning`, `surrogate-gradients`, `online-learning`, `training-cost`, `hardware-aware-learning`, `direct-training-output`, `learning-referrals` | Explain only the distinctions that affect deployment. Refer outward for specialist learning theory and algorithms. |
| 8. ANN-to-SNN Conversion | `classical-ann-to-snn-conversion` | `classical-conversion` (8.1.1 through 8.1.8, the eight classical subsections), `finite-time-error-low-latency` (8.2.1 through 8.2.7, the seven error subsections), `advanced-conversion-methods` (8.3.1 through 8.3.6, the six low-latency interventions by lever), `conversion-toward-hardware` (8.4.1 through 8.4.3) | Give one complete derivation and end-to-end pipeline before introducing remedies. Locate each error at the pipeline stage where it enters, separating deterministic finite-window error from stochastic encoding variance. Organize interventions by which of those named errors they target, keeping evidence class and hardware status claim-specific. |
| 9. The Deployable SNN Contract | `deployable-snn-contract` | `contract-purpose`, `contract-fields`, `definition-representation-execution`, `contract-conformance`, `platform-contract-comparison` | Define the 11 fields that both learning branches must make explicit, distinguishing mathematical definition, software representation, and faithful execution, and compare platforms directly against those fields, using platform examples only with generation, toolchain version, capability status, and evidence limits. |
| 10. Software, Interchange, and Compilation | `software-interchange-compilation` | `framework-boundary`, `simulator-library-catalog`, `serialization-ir`, `export-compile-map`, `runtime-host-io`, `semantic-transformations`, `software-referrals` | Catalog simulators and libraries, then follow the software path in process order. Type every edge by input, output, preservation, transformation, rejection, route state, and evidence. |
| 11. Complete Deployment Routes | `complete-deployment-routes` | `route-definition`, `physical-routes`, `routes-conventional-targets`, `approximate-transformed-routes`, `blocked-unexercised-routes`, `route-selection` | Trace named routes edge by edge. Do not infer a route from compatible-looking nodes. Place the interactive map after the prose synthesis. |
| 12. Deployment Measurement | `deployment-measurement` | `deployment-metrics`, `measurement-boundaries`, `baseline-and-batching`, `event-rate-static-power`, `uncertainty-pareto`, `measurement-checklist` | Define what was measured and where. Make chip, board, host, sensor-to-decision, modeled, and physical boundaries explicit. |
| 13. Deployment Evidence and Findings | `applications-deployment-evidence` | `vision-workloads`, `audio-temporal-workloads`, `control-robotics`, `scientific-industrial`, `cross-workload-evidence`, `population-counts`, `rate-code-falsifier`, `semantic-findings`, `route-measurement-findings`, `evidence-interpretation-boundary` | Organize cases by workload, recording input provenance, learning route, code, on-device portion, boundary, baseline, reproducibility, and evidence class, then answer the motivating question using generated counts and verified counterexamples, separating demonstrated findings from causal or sociological interpretation. |
| 14. Open Problems and Research Agenda | `open-problems-research-agenda` | `failed-contract-edges`, `algorithm-hardware-codesign`, `portable-semantics`, `measurement-reproducibility`, `access-and-maintenance`, `research-agenda` | Derive research problems from failed or unverified contract edges rather than listing generic future work. |
| 15. Researcher Entry Guide and Conclusion | `researcher-entry-guide-conclusion` | `reading-paths`, `route-choice-guide`, `minimum-reporting-checklist`, `specialist-referrals`, `conclusion` | Give field-entry paths, practical questions, minimum reporting requirements, and a concise conclusion. |

Folded anchors kept inline are hardware-execution-models (5.6) and what-the-evidence-shows (13.6); Section 8 keeps its twenty-four original subsections as h4 headings under four h3 parts.

## Cross-section placement rules

1. Define a term at its earliest required section. Later sections link back instead of
   defining it again.
2. Define E1 through E5 only in `evidence-guide`. Later sections apply the labels per
   claim.
3. Introduce the two-population proposition only as a motivating question in Section 1.
   Present counts, falsifiers, and qualifications in Section 13.
4. Introduce time vocabulary in Section 4. Sections 8 through 14 must distinguish an
   algorithmic horizon from hardware time and wall-clock latency.
5. Introduce the 11-field contract in Section 9. Sections 10 through 14 use those field
   names without inventing parallel taxonomies.
6. Present targets and families in Section 5, the platform comparison in Section 9.5,
   software and the catalog in Section 10, routes in Section 11, measurement in
   Section 12, workload evidence and findings in Section 13. A platform inventory does
   not replace a route or measurement analysis.
7. Put specialized referrals at the boundary of the topic they delimit. Each referral
   states what the cited source explains and why the survey stops there.
