# Neuromorphic Deployment Survey, Handover

Written 2026-09-16. Consolidates the intent behind this survey and every substantive
finding from the research phase. Read this before resuming work on the survey or on the
deployment leg of the thesis.

---

## 1. The question that started it

The thesis works on quantization-aware ANN-to-SNN conversion, anchored on QCFS. Reading
that literature alongside the neuromorphic hardware literature produced a persistent
unease. The conversion papers advance accuracy at ever lower timestep counts and speak
about neuromorphic hardware constantly, yet none of them appear to run on any. The
hardware papers report real measurements on real chips, yet appear not to know the
conversion literature exists.

The suspicion was that the low-latency conversion research never actually reaches
silicon, and that this was being hidden by each population citing the other as
motivation rather than as method.

The suspicion was correct. It is not a failure of searching, and it is sharper than
"there is a gap."

## 2. What the survey is for

The survey is a standalone organizing instrument. It is not a restructured Chapter 2 and
does not have to follow it. Its job is to connect application, learning path, neural
code, neuron model, software framework, export format, compiler, runtime, and chip into
one traceable structure, so that any claim of the form "this method runs on that chip"
can be checked edge by edge.

The organizing device is the full-stack figure, a neuromorphic parallel to Figure 17 of
the quantization survey. A traversal such as trained CNN, then SNN Toolbox, then NxTF,
then physical Loihi 1 is one path among many, and the figure records what each handoff
preserves, what it breaks, and how strong the evidence is at the destination.

Deployment claims are classified on a five-level scale. E1 is physical silicon with
measurements. E2 is physical silicon with accuracy or fidelity only. E3 is a documented
path that was never exercised. E4 is a hardware model or synthesis flow. E5 is software
simulation only. Applying this scale to a literature, rather than to a benchmark, is one
of the survey's three contributions.

## 3. The two populations

**Algorithm papers do not deploy.** Two independent passes over the QCFS lineage, one at
16 papers and one at 13, both found zero that report their own hardware run. Every one is
E5. The classical conversion literature is the same, 0 of 9. Even papers co-authored by
the people who built the hardware, Furber on QFFS and on Dynamic Confidence, report
GPU-only results.

**Deployment papers do not use new algorithms.** Of the four hardware conversion papers
(Stromatias 2015, Patiño-Saucedo 2020, Massa 2020, NxTF 2021), zero cite or use any
post-2020 method. All four run classical SNN Toolbox threshold balancing.

**The toolchain freeze is precisely dated.** SNN Toolbox's last release was March 2021
and its last commit August 2022. Both precede the bulk of the low-latency literature. Its
issue tracker contains zero QCFS-family feature requests. Nobody asked.

Two qualifications must travel with the claim, or it overreaches. QCFS itself cites Massa
2020 and Singh 2021 as genuine prior art in related work, not as throat-clearing, so
"cites hardware only as motivation" is false for the founding paper. Twelve of its
thirteen descendants do revert to pure motivation. And Adaptive Fission (NeurIPS 2025)
did measure a rate-coded QCFS and SRP baseline on physical Lynxi HP201 silicon, though
only as a comparison inside someone else's population-coding paper, never by QCFS's or
SRP's own authors.

## 4. The refined claim, which is stronger than the original

Two genuine counterexamples exist. Quartz (Lenz, Orchard, Sheik 2023) proposes a new
conversion method and deploys to physical Loihi. Brehove et al. (ICONS 2026) proposes
sigma-delta conversion and measures it on physical Loihi 2.

Both abandon rate coding. Quartz uses time-to-first-spike. Brehove uses graded spikes.
Adaptive Fission, the third E1 case, uses population coding.

> No paper was found that keeps rate coding, proposes a new conversion algorithm, and
> reaches physical silicon.

The exceptions prove the rule by the route they take out of it. Reaching silicon with a
new method has so far required abandoning the correspondence the entire QCFS literature
is built on.

## 5. The mechanism, found in code

Reset by subtraction is the most consistently dropped feature in the stack, and per
Rueckauer 2017 it is worth roughly twenty accuracy points.

The clearest instance sits inside a single framework. SpikingJelly's `ann2snn` produces
soft-reset neurons by default, and both of its export paths refuse them. `lava_exchange`
raises `ValueError("lava only supports for v_reset == 0!")` at five call sites, and
`nir_exchange` rejects `v_reset=None` as well. One framework converts correctly and
cannot export its own output.

Across hardware, soft reset is native on TrueNorth, on Speck via `return_to_zero=False`,
and on the FPGA frameworks. On Loihi 1 and 2 it requires the two-compartment workaround
that doubles neuron count. SpiNNaker requires a hand-written neuron model. BrainScaleS-2
cannot do it. Signed spikes are native only on Loihi 2.

The seams have prices, and the price is usually a factor of two in whichever resource is
scarce.

## 6. Route verdicts for the deployment leg

**SpikingJelly into NxTF into Loihi 1 is blocked.** NxTF inherits from the Keras `Model`
and `Layer` interface. No PyTorch bridge exists, and the only bridge ever built was
SNN-Toolbox-specific. Its host repository carries a discontinuation notice, and INRC has
redirected users to Lava since 2022. NxTF on Loihi 2 does not exist.

**SpikingJelly into Lava into Loihi 2 is blocked** at reset semantics, as above.
Compounding that, `lava_exchange` dispatches only `Linear`, `Conv2d`, `AvgPool2d` and
`Flatten`, so a VGG's max pooling or a ResNet's skip connection fails immediately. Intel
archived Lava on 13 May 2026.

**The one live route is Sinabs into Speck.** `from_model()` defaults to
`MembraneSubtract()`, feeding `DynapcnnNetwork` and then `samna` onto Speck or DYNAP-CNN.
The chip supports subtractive reset natively. Sinabs' own documentation recommends it for
ANN-converted models. A Speck Demo Kit presold at $199 with no approval gate.

That path does not involve Loihi, and does not involve SpikingJelly.

## 7. What T actually means

T is not one thing, which is why the question kept producing contradictory answers.

| Platform | What T is |
|---|---|
| Loihi 1 and 2 | Barrier-synchronization steps. Real, but wall-clock duration varies with spike traffic |
| SpiNNaker | A timer interrupt, conventionally 1 ms, pinned to biological real time |
| Speck and DYNAP-CNN | Nothing. No global clock. Measured 3.36 µs across nine layers regardless of software timesteps |
| Xylo | A genuine hardware tick, same vendor as Speck, opposite answer |
| Akida | Collapsed to one |

NeuroScale (Li, Imam and Manohar, Nature Communications 16, 10329, 2025) confirms in a
single citation that TrueNorth, Loihi, Loihi 2 and Tianjic all advance through one global
barrier. It replaces the three separate platform citations previously used in Section 2.5.

## 8. The energy premise does not hold as stated

Static and leakage power dominate measured energy on synchronous neuromorphic chips, as
documented on Loihi 2. Cutting T does not cut energy proportionally. Measurement-boundary
choices alone produce 14x swings for the identical chip and network. A SynOps figure is an
operation-count ratio under an unstated hardware model, not joules.

On MorphIC, rate coding cost 205 µJ per MNIST classification against 21.8 µJ for rank
order coding on the same silicon. The code the whole conversion literature depends on is
the expensive one, measured.

## 9. Why the gap exists

The gap is sociological rather than technically forced. Nobody built the bridge because
the incentives in each population point elsewhere, not because a soft-reset QCFS network
cannot in principle be mapped to accessible silicon. A toy two-neuron QCFS-to-SpiNNaker
bridge already exists on GitHub, which is enough to show the obstacle is not a theorem.

That is good news for the thesis. A gap that is structural but not impossible is exactly
the kind a thesis can close. It also means the deployment leg should be scoped as
engineering with a known route, Sinabs into Speck, rather than as a research risk with an
unknown one.

## 10. What the survey can honestly claim

The gap is real at the level of a systematic cross-toolchain taxonomy, not as a vacuum.
Six works come close, and Section 1.1 engages each by name. NIR, Kudithipudi et al. 2025,
NeuroBench, the EdgeSNN survey, Davies et al. 2021, and Huynh, Balaji and Das 2022.
Thirty-seven surveys are scored across twelve research axes, merged into eight table
columns, which is the Section 1.1 table.

The defensible contribution is threefold. A cross-toolchain taxonomy that records edges
rather than enumerating nodes. A five-way evidence classification applied to a literature
rather than to a benchmark. The two-population structural claim with its refinement, that
every confirmed instance of a new method reaching silicon abandons rate coding.

## 11. What this does for the three thesis contributions

**Contribution 1 gains a commercial witness.** Akida's CNN2SNN computes `y = x / act_step`
with a static threshold absorbing BatchNorm scale and shift, folded once at conversion
time. There is no membrane potential and no exposed T. Two independent papers describe it
as squashing the rate-code approximation of ReLU into one timestep. A shipping processor
marketed as neuromorphic executes exactly the ANN-mode quantizer the equivalence proof
identifies. The low-latency trajectory taken to its limit is the quantized ANN, and
someone already built and sold that.

**Contribution 2's critique gets sharper.** PASCAL had a working RTL flow, Synopsys Design
Compiler at 40 nm and 560 MHz plus a cycle-accurate simulator, and used it for the uniform
T=4 case only. The mixed-timestep configuration behind its headline effective T of 3.14
never went through it, so that number is E5 while the uniform check is E4. QAC did no
synthesis at all, while its own appendix describes the stall that makes its number
unachievable. The one physical deployment of heterogeneous timing, MTT on Speck2e, works
by choosing a chip that has no timesteps at all.

**Contribution 3 gets a named target.** No conversion method targets rank order coding,
because every conversion theorem matches cardinal firing rates and an ordinal code has no
analogue to converge toward. That is the "non-uniform grid, non-rate code" question with a
concrete instance, a shipping processor that uses it, and a measured 9.4x efficiency
argument for why anyone would want it.

## 12. State of the artifact

Nine sections, assembled from fragments by `tools/build-site.py`. The page shell is copied
verbatim from the quantization survey by `tools/clone-template.py`, so the two are the same
publication object with different content. Citations are distill's own `d-cite`, backed by
`assets/bibliography/references.bib`, generated by `tools/build-bib.py` from the fragments'
inline entries. 302 bibliography entries, 292 cited, 842 citation tags, zero unresolved
keys, verified by running distill's own parser and formatters over the output.

Evidence base is in `research/`, `data/evidence-stack.json` (114 nodes, 118 edges, 136
sources) and `data/evidence-papers.json` (74 papers). Population counts are 39 algorithm
papers, 33 of them pure E5 and none at E1 or E2, against 31 deployment papers, with 3
papers in both populations and all 3 abandoning rate coding.

Open items. Five figures in Section 2 are still dashed placeholders reading "FIGURE TO
DRAW", covering the biological and artificial neuron pair, the six-model neuron
comparison, the dual reset-rule membrane trace, the eight-code encoding comparison, and
the three-time-model diagram. Three bibliography entries record the survey's own analysis
rather than a published source. The byline reads "Anonymous", inherited from the
quantization survey's review state. `return_to_zero=False`, Speck's native soft-reset
flag, is missing from the Section 6 text and should be added.

## 13. Verification discipline

One claim was nearly recorded wrongly in both directions. PASCAL's RTL synthesis was first
asserted, then retracted on the strength of two WebFetch passes that had truncated a
24-page PDF, then confirmed by triple-independent verification of Appendix A.10. No
appendix-level claim is accepted or rejected on a single fetch. The same discipline caught
a false claim that NIR defines a subtractive primitive, which direct inspection of
`neuromorphs/NIR/nir/ir/neuron.py` disproved, since all three spiking primitives document
reset to a fixed value.
