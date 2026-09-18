# NeuromorphicSurvey Writing Handoff

## Purpose and stopping point

This handoff is for the agent that will write the redesigned survey. The research,
evidence normalization, bibliography migration, generated evidence views, figure-tool
hardening, and source-registry authority repair are complete. This session must not
write, replace, or place survey prose.

The target is a deployment-centered field-entry reference. It must give a new researcher
the conceptual path from representation and dynamics through learning or conversion to a
specific executable route, a measurement boundary, and a defensible deployment claim. It
is not a generic encyclopedia of SNNs, a paper-by-paper literature review, or a vendor
catalog.

Work from the isolated worktree and branch below. Do not edit the main thesis checkout.

```text
worktree  /Users/hamza/Documents/GitHub/Thesis/.worktrees/neuromorphic-survey-redesign
branch    codex/neuromorphic-survey-redesign
```

## What is frozen and authoritative

Read these documents before drafting. They resolve the important scope and structure
decisions. Do not reopen them unless a canonical validator exposes an inconsistency.

1. `docs/superpowers/specs/2026-09-16-neuromorphic-survey-redesign.md`
2. `docs/superpowers/plans/2026-09-16-neuromorphic-survey-prose.md`
3. `NeuromorphicSurvey/research/rewrite/section-map.md`
4. `NeuromorphicSurvey/research/rewrite/notation.md`
5. `NeuromorphicSurvey/research/rewrite/salvage-map.md`
6. `NeuromorphicSurvey/research/quantization-survey-writing-audit.md`
7. `NeuromorphicSurvey/research/figure-inventory.md`

The prose plan is the execution plan. It defines file ownership, section-by-section
tasks, and integration checks. This document adds the evidence state, writing rules, and
decisions that must survive the session boundary.

### Canonical evidence inputs

Use generated inputs for all counts, evidence classes, route state, platform status, and
measurement claims. Do not recalculate counts in prose and do not copy them from an old
dossier.

| Need | Canonical input |
| --- | --- |
| Prior survey synthesis and the 37 by 12 matrix | `data/prior-survey-coverage.json`, `data/generated/prior-survey-family-summary.json` |
| Claim wording, scope, caveats, locators, conflicts, and E class | `data/claims.json`, `data/generated/claim-index.json` |
| Software and deployment route semantics | `data/evidence-stack.json`, `data/generated/route-index.json` |
| Measurement boundary and comparability | `data/generated/measurement-index.json` |
| Figure conceptual or measured labels and provenance | `data/generated/figure-inputs.json` |
| Sources and aliases | `data/source-registry.json`, `data/refmap.json` |
| Bibliography diagnostics | `data/bibliography-report.json` |

The source registry has 352 canonical records. The generated bibliography contains 352
definitions. It resolves 375 cited legacy keys to 284 canonical works, has 265 aliases,
and has zero unresolved cited keys. Seven unresolved reference-only entries are retained
as visible legacy cleanup debt. They are not citations and must not be invented into
prose.

`source-registry.json` is the bibliographic authority. `references.bib` and `refmap.json`
are generated downstream outputs. Never edit either by hand. The old builder cycle was
removed by `data/legacy-citation-aliases.json`, which is the upstream record of historic
alias assignments.

### Evidence rules that cannot be weakened

- E1 through E5 classify an individual claim, not a paper or a platform. Define the
  five classes once in Section 1. Apply them later without redefining them.
- Preserve the distinction among `verified`, `provisional`, `conflicted`, and `rejected`.
  A provisional vendor capability is not a confirmed route.
- Preserve route states `exact`, `approximate`, `blocked`, `obsolete`, `unexercised`, and
  `physical`. A compatible node sequence is not a demonstrated route.
- Preserve capability statuses `native`, `transformed`, `emulated`, `host-assisted`,
  `unsupported`, and `undocumented`.
- A measurement claim requires its stated boundary. Use only `chip-only`, `board-level`,
  `host-inclusive`, `sensor-to-decision`, `modeled`, and `physical`.
- Never infer a physical measurement from an analytical model, a documented compiler
  path, an accuracy-only hardware result, or an operation count.
- Do not turn an E3, E4, E5, metadata-only, or provisional capability record into a
  measured or verified figure datum.

The following non-equivalences are mandatory editorial checks.

- Fewer algorithmic steps do not by themselves prove lower wall-clock latency.
- Fewer spikes do not by themselves prove fewer hardware operations or lower energy.
- Asynchronous execution does not prove independent per-layer horizons.
- Event-native input does not prove end-to-end event-driven execution.
- A documented exporter does not prove a physically exercised route.
- Equal nominal bit width does not prove equal represented information.
- An analytical hardware model does not prove a silicon measurement.

## Approved article architecture

The order below is fixed. It is the pedagogical dependency chain approved by the author.

```text
computation and representation
  -> neuron and synapse dynamics
  -> temporal semantics, neural codes, and decoding
  -> where an SNN runs
  -> learning paradigms and the two branches
  -> ANN-to-SNN conversion, errors, and interventions
  -> the deployable SNN contract
  -> software and compiler stack
  -> deployment routes and measurement
  -> deployment evidence and open problems
```

The direct-training and conversion branches are deliberately bounded and meet at the
deployable SNN contract. Both routes must explain what executable semantics they produce
before platform, route, or measurement claims are made.

| Section | Required job |
| --- | --- |
| 1. Introduction | Reach the model-to-chip question in the first two paragraphs. State reader and scope. Synthesize the 37 earlier surveys by seven families, not row by row. Retain the complete matrix. Motivate and then define E1 through E5 once. Pose the two-population issue as a question only. Give the 15-section roadmap and precise referrals. |
| 2. Computation and Representation | Define values, state, events, time, dense computation, sparse activity, conditional execution, and sparse communication. Bound biology and device physics through referrals. Do not give platform conclusions. |
| 3. Neuron and Synapse Dynamics | Start from the shared staged state update in `notation.md`. Derive IF, LIF, CUBA-LIF, ALIF, and multi-compartment variants. Separate model, numerical discretization, and hardware realization. Make reset semantics load-bearing. |
| 4. Temporal Semantics, Neural Codes, and Decoding | Define every meaning of time before comparing codes. Compare rate, TTFS, phase, burst, population, sigma-delta, rank-order, and direct coding through encoder, channel, decoder, horizon, precision, and cost. |
| 5. Where an SNN Runs | Name the three targets and compare the paths between them, then compare execution families through contract fields. Use versioned vendor manuals, SDKs, devkits, mapper constraints, release notes, model zoos, and official examples. Do not create a vendor-by-vendor tour. |
| 6. The Two Branches | Explain the optimization difficulty introduced by spikes. Define direct training, conversion, and hybrid routes. Make the future convergence at the contract explicit. |
| 7. Direct SNN Training | Cover STDP and local learning, surrogate gradients and BPTT, online learning, and hardware-aware learning only to the depth required for deployment comparison. End with specialist referrals. Do not reproduce a general learning survey. |
| 8. ANN-to-SNN Conversion | Give one complete reference derivation and walkthrough, covering ReLU-rate correspondence, input and readout, weight and threshold scaling, bias, batch-normalization folding, pooling, residuals, output decoding, assumptions, and finite-T limits. Explain clipping, saturation, count discretization, residual membrane, reset, unevenness, timing, and layerwise errors by where they enter that pipeline, separating deterministic finite-window error from stochastic encoding variance. Organize interventions by intervention point and named error, not chronology or paper, covering activation shaping, potential and reset, calibration, neuron changes, temporal allocation, early exit, alternative codes, co-design, and hybrid fine-tuning; tables hold datasets and measurements. |
| 9. The Deployable SNN Contract | Define the 11 fields and the three distinct questions of mathematical definition, software representation, and faithful execution. This is the convergence point of the two learning branches. Compare platforms directly against those fields, using platform examples only with generation, toolchain version, capability status, and evidence limits. |
| 10. Software, Interchange, and Compilation | Catalog simulators and libraries, then follow framework, serialization, IR, compiler, mapper, runtime, and host boundaries in process order. Every edge needs input, output, preservation, transformation, rejection, route state, source, and version where available. |
| 11. Complete Deployment Routes | Trace verified named routes edge by edge. Label physical, transformed, blocked, and unexercised routes honestly. Place the interactive map only after its prose synthesis. |
| 12. Deployment Measurement | Define metrics and their boundaries before comparing applications. Address baseline matching, batching, event rate, static power, uncertainty, and Pareto interpretation. |
| 13. Deployment Evidence and Findings | Organize cases by vision, audio and temporal sensing, control and robotics, and scientific or industrial workloads. For each case, record input provenance, learning route, code, on-device work, baseline, boundary, reproducibility, and E class. Answer the Section 1 motivating question, regenerate inclusive and exclusive population counts, state the narrow low-T rate-code falsifier and its counterexamples, and separate evidence from sociological interpretation. |
| 14. Open Problems and Research Agenda | Derive problems from failed, transformed, blocked, obsolete, or unexercised contract edges. Do not use a generic future-work list. |
| 15. Researcher Entry Guide and Conclusion | Give reading paths, route-choice questions, a minimum reporting checklist, specialist referrals, and a concise deployment-centered conclusion. Do not repeat the outline. |

### Two conclusions that need careful placement

The two-population observation is a motivating question in Section 1 and a tested finding
in Section 13. Do not use it as an opening result. Its narrow falsifier is a paper that
both proposes a new low-T rate-coded conversion method and measures that method on named
silicon. No audited paper meets that condition. This does not imply that no low-T
rate-coded SNN reaches silicon. Verified counterexamples and qualifications include
direct-training and platform-native-code cases. Use the claim index, not memory, for the
final wording and citations.

The contract is not an abstract taxonomy imposed on the literature. It is the mediator
between algorithm semantics, software representations, and vendor-supported execution.
For a hardware-support statement, provide official provenance, generation, relevant SDK
or toolchain version where available, and capability status. All current platform
capability records are deliberately provisional unless an exercised official route proves
the field.

## Writing method and style

### The QuantizationSurvey pattern to inherit

Use the local QuantizationSurvey as a writing model, not as a factual source.

1. Build the dependency ladder before the taxonomy. A later section must not require an
   undefined earlier concept.
2. Use a four-part technical paragraph. Define the mechanism. State the semantic or
   mathematical effect. Explain the trade-off or failure mode. State the deployment
   consequence and evidence boundary.
3. Group papers by a shared mechanism, assumption, intervention, workload, or evidence
   boundary. Do not explain the survey paper by paper.
4. Put record-level detail in tables. Adjacent prose states the inference, qualification,
   or decision consequence. Never read a table aloud.
5. Use figures to answer one explicit question after terminology is introduced. Captions
   state whether the visual is conceptual or measured and name its limits.
6. End each substantial section with a short bridge that states the next dependency.
7. Bound scope through referrals. Use this form.

   > The present discussion stops after [deployment-relevant capability]. For a fuller
   > treatment of [bounded topic], see [source], which is particularly useful for
   > [specific strength].

### Mandatory prose rules

- Use formal American English and IEEE numeric citations.
- Use short declarative sentences. Prefer full stops and commas to long stitched clauses.
- Do not use em dashes. Avoid colons in running prose.
- Remove empty framing such as "It is worth noting" and "This section presents."
- Expand each acronym on first use.
- Define a term at the earliest section that needs it. Link backward later instead of
  redefining it.
- State whether a claim is mechanism, inference, capability, route, or measurement.
- Cite a factual engineering or scientific claim. Flag any statement that lacks a
  canonical source or has only provisional support.
- Never use absolute language such as `never`, `every`, `only`, or `no platform` unless
  the claim index gives the searched population, scope, and falsifier.
- Do not copy stale numerical counts from `site/`, dossiers, thesis chapters, or notes.

### Citation and bibliography rules

- Use canonical source IDs or aliases validated by `data/refmap.json` in the site citation
  syntax. Existing fragments use `<a class="cite" data-ref="key" href="#ref-key">`.
- Do not invent a key. Run `python NeuromorphicSurvey/tools/check-bibliography.py` after
  a citation batch.
- Do not hand-edit `assets/bibliography/references.bib`, `data/refmap.json`, or
  `data/bibliography-report.json`. Regenerate them with `build-bib.py`.
- Use old dossiers only as reading reservoirs. Their prose and reference lists are not
  authority. Reuse a passage only when the source ID, locator, status, and evidence class
  agree with the generated inputs.

## Figure and table instructions

The manifest at `data/figure-manifest.json` is authoritative. It contains 34 figures, all
implemented (33 static plus the interactive route map, Figure 33), none planned. Display numbers
follow article order and are regenerated from the manifest whenever a figure is added or
moved; a display number is never hand-coded in prose, fragments, CSS, or tools. Static
fragments are named by semantic id under `site/figures/` (for example
`rc-if-lif-origin.html`), not by number. The per-figure state, provenance, and policy
are recorded in `research/figure-inventory.md`.

The four original survey figures (`original-neuron-model-comparison`,
`original-reset-rule-comparison`, `original-hardware-time-model-comparison`,
`original-neural-code-comparison`) are retired to `research/retired-figures/`. Their
drawings are kept there as read-only records; they are not on the page and do not appear
in `data/figure-manifest.json`.

| Rule | Requirement |
| --- | --- |
| Question | A figure answers its manifest question and nothing else, after the prose has defined every term it uses. |
| Lead-in | Every figure and table is introduced by a sentence that names it and says what it adds. Prose interprets, it does not read the figure aloud. |
| Provenance | The caption states whether the visual is a conceptual illustration, derived from stated equations or a stated input, or carries documented or measured platform values; a measured value cites its source beside the platform. |
| Notation | Survey symbols from `notation.md`; a figure that keeps original symbols maps them in its caption. |
| Placement | Planned figures carry a caption-only placeholder `<figure id="figure-N">` in their destination section so the installer can place them. |

Figure tooling is manifest-driven and strict. `tools/check-figures.py` validates every
implemented static fragment (one figure, one caption opening with its display number,
one inline SVG scaled by viewBox, ids prefixed `fN`, no external assets, no dark mode).
`tools/install-figures.py` places fragments by display number and regenerates
`assets/figures.css`; `tools/validate-manifests.py` checks the manifest itself. Use
generated `figure-inputs.json` to label a figure element as conceptual or measured. An
unqualified axis, decorative number, or unrelated unit text is not acceptable evidence of
a measured plot.

## Suggested execution sequence

The prose plan already divides writers into Foundations, Methods, Deployment, Synthesis,
and Integration groups. If using parallel workers, keep file ownership disjoint and make
the integration owner the only worker that changes shells, manifests, generated outputs,
or cross-section references.

1. Read the frozen sources above and run the readiness commands below.
2. Create the missing `sec-04.html`, `sec-05.html`, and `sec-09.html` through
   `sec-15.html` fragments from the manifest. Do not write all sections in one pass.
3. Draft Sections 1 through 4 first. Review terminology, equations, citations, and
   Figure 2 before moving on.
4. Draft Sections 5 through 9. Keep direct training bounded, establish the classical
   conversion derivation and its interventions, and end at the deployable contract.
5. Draft Sections 10 through 13. Make the contract drive the software, route,
   measurement, and workload analysis.
6. Draft Sections 14 and 15 last, after all generated tables and cross-references
   are in place.
7. Add figures only at their synthesis points. Do not let a figure determine section
   order.
8. Run a cross-section editorial pass using the notation, salvage, evidence, and figure
   rules. Build and inspect the rendered site.

Commit after each independently reviewed section group. Do not blend unreviewed prose
with generated-data changes.

## Readiness and completion checks

Run the first group before starting and after each major section group. It verifies the
frozen evidence base without requiring the currently missing prose fragments. The global
check scripts are present and required.

```bash
python NeuromorphicSurvey/tools/validate-survey-coverage.py
python NeuromorphicSurvey/tools/validate-sources.py
python NeuromorphicSurvey/tools/validate-evidence.py
python NeuromorphicSurvey/tools/verify-research-evidence-contracts.py
python NeuromorphicSurvey/tools/verify-source-registry-build.py
python NeuromorphicSurvey/tools/build-source-registry.py --check
python NeuromorphicSurvey/tools/build-data-views.py --check
python NeuromorphicSurvey/tools/build-bib.py --check
python NeuromorphicSurvey/tools/check-bibliography.py
python NeuromorphicSurvey/tools/check-counts.py
python NeuromorphicSurvey/tools/check-consistency.py
python NeuromorphicSurvey/tools/validate-manifests.py
python NeuromorphicSurvey/tools/verify-figure-tools.py
python NeuromorphicSurvey/tools/check-figures.py
git diff --check
```

Only after the writer has created every manifest-declared section fragment and placed the
necessary anchors, run the site-integration group. `install-figures.py --check` is
supposed to fail before that point and must not be forced to succeed.

```bash
python NeuromorphicSurvey/tools/build-table1.py
python NeuromorphicSurvey/tools/install-figures.py --check
python NeuromorphicSurvey/tools/build-site.py
python NeuromorphicSurvey/tools/verify-survey.py
git diff --check
```

Before handoff or publication, also verify the following manually.

- Every section title and stable anchor agrees with `section-map.md`.
- E1 through E5 appears as one definition only.
- The matrix has all 37 records and 12 axes.
- The Section 13 population counts come from generated data and state the counting policy.
- Each hardware statement has explicit provenance and qualification.
- Each deployment result names a route state and each metric has a measurement boundary.
- Each table and figure is introduced and interpreted, but no paragraph restates every row.
- Each bounded topic ends in a precise referral.
- The conclusion is a synthesis, not another outline.

## Existing material and exclusions

Existing `site/sec-01.html`, `sec-02.html`, `sec-03.html`, `sec-06.html`, `sec-07.html`,
and `sec-08.html` are sources to salvage, not text to preserve wholesale. The exact
retain, rewrite, move, and remove decisions are in `salvage-map.md`. Existing thesis
chapters are useful background drafts but are neither complete nor the desired structure.

The author specifically rejected the prior placement where the five-way evidence
classification and the two-population result appeared as dense opening claims before the
table that explains them. Preserve the table, but first provide concise motivation. Pose
the two-population issue as a bridge from the prior-survey gap to the contract, then test
it later.

Do not add another literature-mining phase unless a generated claim, citation, route, or
measurement field is concretely missing. The present registry and evidence corpus are the
writing base.
