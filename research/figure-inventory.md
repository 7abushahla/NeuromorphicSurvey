# Figure Inventory

Reviewed 2026-09-17. Supersedes the 2026-09-16 preservation inventory, whose integration defects (hard-coded build order, non-manifest installer, checker limited to five figures) are resolved.

The manifest `data/figure-manifest.json` is authoritative for semantic id, display number, destination section, status and question. Display numbers follow article order and are regenerated from the manifest whenever a figure is added or moved; nothing else may hard-code one. Static fragments live in `site/figures/<semantic-id>.html` with a matching `.css`.

## Policy

- **Additive set.** The original survey figures are kept beside their revised successors. Their drawings and comparative layouts are preserved; their captions are scoped to what the drawing shows, their platform labels carry a documented status, and any number beyond the drawn window cites the derivation it comes from.
- **Provenance in the caption.** Every implemented figure states whether it is a conceptual illustration, derived from stated equations or a stated input sequence (with the equations and inputs recorded in a comment inside the fragment), or carries documented or measured platform values, each cited beside the platform.
- **Notation.** Survey symbols from `research/rewrite/notation.md`. A figure that keeps its original symbols maps them to the survey's in its caption.
- **Visual system.** Persistent state blue, binary spikes as red vertical marks, thresholds black dashed, real-valued values and currents green, encoders and decoders as distinct boundary boxes, documented or measured annotations visibly different from conceptual ones.
- **Sources.** Private notes, screenshots, `SNN.png` and `LIFillustration.pdf` in the thesis tree are not sources and are not reproduced. Figure `neuron-through-time` is a conceptual illustration computed from stated equations; no `adapted from` claim is made.
- **Placement.** Every figure sits after the prose that defines the terms it uses and is introduced by a lead-in sentence. Planned figures hold a caption-only placeholder in their destination section.

## Figures

| No. | Semantic id | Section | Status | Kind |
|---|---|---|---|---|
| 1 | survey-architecture | 1 Introduction | planned | placeholder caption in 1.3 |
| 2 | lineage-tree | 2 Computation and Representation | implemented | conceptual lineage tree; fourteen dated nodes cite their primary sources; landmark strip ordinal |
| 3 | representation-comparison | 2 | implemented | derived (preserved as approved) |
| 4 | network-snn-architecture | 2 | implemented | conceptual |
| 5 | ann-snn-computation | 2 | implemented | conceptual |
| 6 | rc-if-lif-origin | 3 Neuron and Synapse Dynamics | implemented | conceptual |
| 7 | model-menu | 3 | implemented | derived (Izhikevich 2004 Fig. 2 numbers, plus count over 22 columns; platform tags carry registry statuses) |
| 8 | neuron-through-time | 3 | implemented | derived (LIF, forward Euler, inputs in fragment) |
| 9 | neuron-model-comparison | 3 | implemented | derived (staged update, mini-traces computed) |
| 10 | original-neuron-model-comparison | 3 | implemented, original | derived traces; documented platform statuses |
| 11 | original-reset-rule-comparison | 3 | implemented, original | derived (eight-step window; asymptotic claim cited) |
| 12 | reset-rule-comparison | 3 | implemented | derived (five-step window) |
| 13 | encoder-snn-decoder | 4 Temporal Semantics, Neural Codes, and Decoding | implemented | conceptual |
| 14 | input-encoding-modes | 4 | implemented | conceptual |
| 15 | neural-code-comparison | 4 | implemented | conceptual template |
| 16 | original-neural-code-comparison | 4 | implemented, original | illustrative value per code; reported costs cited |
| 17 | hardware-time-model-comparison | 4, end of 4.4 | implemented | conceptual lanes; no measured quantity drawn |
| 18 | original-hardware-time-model-comparison | 4, end of 4.4 | implemented, original | schematic timing; documented Speck, Loihi and BrainScaleS-2 values cited |
| 19 | classical-conversion-pipeline | 7 Classical ANN-to-SNN Conversion | planned | placeholder caption in 7.6 |
| 20 | finite-time-error-propagation | 8 Finite-Time Error and Low-Latency Conversion | planned | placeholder caption in 8.1 |
| 21 | deployable-snn-contract | 10 The Deployable SNN Contract | planned | placeholder caption in 10.2 |
| 22 | software-boundary | 11 Software, Interchange, and Compilation | planned | placeholder caption in 11.3 |
| 23 | deployment-stack-map | 13 Complete Deployment Routes | implemented, interactive | `site/shell-figure.html`, generated from `data/generated/route-index.json` |
| 24 | measurement-boundary | 14 Deployment Measurement | planned | placeholder caption in 14.2 |

## Pending

- The six planned figures belong to the figures-site plan and are not drawn.

## Renumbering procedure

`tools/renumber-figures.py` performs steps 1 and 2 (dry run by default, `--apply` to write).

1. Read article order from the site manifest's fragment order and, inside each fragment, the order of `<figure id="figure-N">` elements (the interactive map by its `<figcaption id>`).
2. Map old to new display numbers from that order and rewrite, from the one mapping, the manifest, each fragment's `id`, caption label and `fN` id prefix, each CSS scope, and every `figure-N` anchor and `Figure N` text token in section and shell fragments (never the template CSS in `shell-head.html`).
3. Run `tools/install-figures.py`, `tools/build-site.py`, `tools/check-figures.py`, `tools/validate-manifests.py`, and confirm the built page's captions run 1 to N with no dangling anchors.

## Verification result

`check-figures.py` passes for all 17 implemented static figures; `validate-manifests.py` passes; the built page carries captions 1 to 24 in order with zero dangling anchors. The foundations lineage pass of 2026-09-17 added `lineage-tree` (Figure 2, Section 2.1) and `model-menu` (Figure 7, Section 3.1) and moved the two hardware-time figures to the end of 4.4 (Figures 17 and 18); both new figures were rendered at 720 px and 400 px and reviewed for overlap, clipping, registry fidelity and source fidelity before commit. Each implemented figure was rendered at 720 px and 400 px column width during the 2026-09-17 audit and inspected for overlap and clipping. This verifies markup, numbering and layout; the derived values were recomputed by the figure worker from the equations recorded in each fragment.
