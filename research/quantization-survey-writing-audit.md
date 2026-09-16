# Writing Audit of the Quantization Survey

Reviewed 2026-09-16 from the local published source at
`/Users/hamza/Documents/GitHub/QuantizationSurvey/index.html`.

## What the neuromorphic survey should inherit

### A dependency order that answers progressively harder questions

The quantization survey does not begin with a catalog of methods. It first defines
numerical representations and formalizes quantization. It then explains deployment
design choices, distinguishes the primary training routes, organizes advanced methods,
introduces alternative representations, and only then moves to hardware, software,
applications, and open problems. Each section gives the reader the vocabulary needed by
the next one.

The approved neuromorphic order follows the same successful principle at greater
resolution. Sections 2 through 4 define computation, state, time, encoding, and decoding.
Sections 5 through 9 explain how an SNN is obtained and why finite-time conversion fails.
Section 10 makes the resulting executable semantics explicit. Sections 11 through 15
then trace representation, execution, measurement, and applications. Sections 16 through
18 synthesize findings and guide new researchers.

The practical writing rule follows. A section may use a concept from an earlier section,
but it must not require an undefined concept from a later one. Platform verdicts therefore
cannot appear while basic neuron or code semantics are still being introduced.

### Mechanism-first explanations followed by design consequences

The strongest technical passages in the quantization survey use a repeated pattern.
They define one mechanism, give its mathematical or operational consequence, explain the
trade-off, and then connect it to deployment. The calibration discussion, granularity
discussion, mixed-precision taxonomy, and redistribution synthesis use this pattern well.

The neuromorphic survey should apply the same four-part paragraph architecture.

1. Define the mechanism in the frozen notation.
2. State what quantity or semantic property it changes.
3. Explain the trade-off or failure mode.
4. State the deployment consequence and evidence boundary.

This pattern is especially important for reset rules, finite-time error, temporal
allocation, code changes, exporter transformations, and measurement boundaries. It
prevents a paragraph from becoming a sequence of paper summaries.

### Taxonomies that are tied to the problem being solved

The quantization survey is strongest when a taxonomy is not merely descriptive. Its
advanced-method sections separate integer training, extreme low bit width, mixed
precision, hardware-aware methods, redistribution, and data-agnostic methods because
these categories answer different design problems.

Section 9 of the neuromorphic survey should do the same. Its primary grouping must be the
intervention point and the Section 8 error being addressed. Activation shaping,
potential and reset changes, calibration, neuron changes, temporal allocation, adaptive
termination, code changes, hardware-aware co-design, and hybrid fine-tuning remain useful
only when each group states which error it targets and which classical assumption it
changes.

### Boundary referrals that state what the source adds

The quantization survey controls scope through referrals placed after a bounded treatment.
Its strongest referrals do not merely say that another survey exists. They identify the
topic being bounded and the specific value of the referred source. Examples include
calibration comparisons, adaptive quantization, data-agnostic quantization, emerging
number systems, Posit arithmetic, RISC-V embedded machine learning, and micro-NPU
architectures.

The neuromorphic survey should use the following referral form.

> The present discussion stops after [deployment-relevant capability]. For a fuller
> treatment of [bounded topic], see [survey or tutorial], which is particularly useful
> for [specific strength].

Referrals should close a topic rather than interrupt its first explanation. They are
mandatory at the chosen boundaries for neuroscience, biophysical neuron detail, STDP,
surrogate-gradient theory, online learning, event-sensor physics, analog circuit design,
emerging devices, and benchmark methodology.

### Tables that store detail while prose states the inference

The quantization survey places paper-level or device-level detail in coverage, hardware,
and application tables. Its better adjacent paragraphs state the consequence of that
detail. They do not reproduce every row. The survey matrix also gives the reader a compact
scope comparison after the prose has established the literature families.

The neuromorphic survey should apply a stricter version of this rule. Section 1 prose
must synthesize the seven prior-work families. The 37-row matrix carries individual
coverage judgments. Sections 9, 12, 13, and 15 should state cross-row patterns and
qualifications, while generated tables carry paper, platform, route, and measurement
details. A paragraph should be deleted if it only converts an adjacent row into a
sentence.

### Figures that answer one explicit question

The quantization survey uses figures to orient the reader before dense detail. Its survey
overview establishes the reading path. Design-choice figures compare alternatives after
the terms are introduced. Taxonomy figures precede detailed method families. The final
interactive map changes perspective and begins from a practitioner application.

The neuromorphic figure manifest already captures this practice by assigning one question
to every figure. Captions should answer that question and state the limits of the visual.
Conceptual examples must be labeled conceptual. Platform numbers must be labeled measured
and cite the measurement boundary. The interactive deployment map may preserve an
application-first view, but it must render only validated edge chains.

### Section endings that perform synthesis and establish the next dependency

Several strong quantization passages end by identifying the decision that follows. The
design-choice synthesis explains that quantization is a design space rather than one
operation. The redistribution synthesis distinguishes data shaping from bit allocation.
The data-agnostic synthesis identifies the conditions under which that route is useful.

Each neuromorphic section should end with one short bridge. Section 3 identifies the
semantics that later become contract fields. Section 4 identifies which code properties
constrain learning and execution. Section 7 identifies the assumptions that create
finite-time error. Section 8 identifies the intervention problem for Section 9. Section 9
identifies the need for an explicit executable contract. Sections 11 and 12 identify
which complete routes must be tested. Section 14 supplies the vocabulary required to
compare the applications in Section 15.

## What should not be copied

### Generic motivation should be shortened

The quantization introduction spends several paragraphs on general DNN success, IoT
growth, MCU constraints, TinyML, and compression before reaching its distinct deployment
question. This is defensible for a broad audience but longer than necessary for the
neuromorphic survey. The new introduction should reach the model-to-chip question within
the first two paragraphs and defer definitions to Sections 2 through 4.

### Prior-work prose should remain family-level

The quantization prior-work discussion begins with three useful families but then names
many surveys sequentially. The neuromorphic survey has a larger 37-work matrix, so the
same approach would become repetitive. Its prose should discuss shared strengths and
omissions by family. Selected papers should appear only as representative referrals or
as exceptions that alter the family-level conclusion.

### Applications should not be organized by platform

The quantization application section is divided into ARM, RISC-V, and NPU-integrated
hardware. That organization fits a platform-selection survey but makes cross-workload
comparison difficult. The approved neuromorphic structure is stronger. Section 15 should
group vision, audio and temporal sensing, control and robotics, and scientific or
industrial workloads. Platform becomes one comparison field rather than the section
hierarchy.

### Deployment evidence requires stronger boundaries

The quantization survey connects algorithms to devices but does not apply a per-claim
evidence ladder or a typed edge model. Its prose can therefore move quickly from a method
to a platform capability without always distinguishing documentation, modeled execution,
physical accuracy, and measured latency or energy. The neuromorphic survey must retain
its stricter E1 through E5 classification, route states, capability statuses, and explicit
measurement boundaries.

### Conclusions should synthesize rather than repeat the outline

The quantization conclusion repeats several section inventories before presenting its
cross-cutting conclusions. The neuromorphic conclusion should be shorter. Section 16 will
already contain the evidence synthesis and Section 17 the research agenda. Section 18
should state the central deployment argument, give the minimum route and reporting logic,
and close without another section-by-section recap.

## Section-specific writing directives

| Neuromorphic section group | Technique to adopt |
|---|---|
| Sections 1 through 4 | Use the quantization survey's staged preliminaries, but reach the deployment question earlier and separate mathematical abstraction from platform consequence. |
| Sections 5 and 6 | Use compact branch comparison and specialist referrals. Do not reproduce a general SNN-learning survey. |
| Sections 7 through 9 | Use one complete derivation before a mechanism-first taxonomy. Every method group must point back to a named error. |
| Sections 10 through 13 | Improve on the quantization survey by using the 11-field contract and typed routes. Compare families in prose and carry vendor details in generated tables. |
| Sections 14 and 15 | Define measurement before applications. Group cases by workload and interpret cross-case evidence rather than narrating devices. |
| Sections 16 through 18 | State only regenerated findings. Separate evidence from interpretation, derive open problems from failed edges, and finish with actionable reading and reporting paths. |

## Editorial checklist for every subsection

1. The opening sentence states the question or mechanism, not the paper being discussed.
2. Terms and symbols have already been defined or are defined immediately.
3. Papers are grouped by a shared mechanism, assumption, or evidence boundary.
4. An adjacent table carries detailed records. Prose states the inference and caveat.
5. A figure answers one named question and does not imply an unproved equivalence.
6. Deployment statements identify the route state, capability status, evidence class,
   and measurement boundary where applicable.
7. A bounded topic ends with a precise referral.
8. The final sentence establishes the next dependency without summarizing the entire
   subsection.

