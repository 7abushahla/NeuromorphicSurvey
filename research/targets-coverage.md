# Task 4 dossier scoring: axis M (targets)

Scored from `research/prior-surveys/S01-*.md` through `S37-*.md` on 2026-09-17, per the
Task 4 brief for the "Where an SNN Runs" plan. A kind counts when the dossier's notes,
quoted scope, table of contents, or hardware basis names that hardware kind as something
the survey surveys, compares, or reports results on. A passing mention does not count.
Silence scores an empty list with basis "The dossier records no target kind" and locator
"dossier". Two surveys were flagged because their dossier is silent but their title names
an edge-execution term; both checks are logged in `research/source-validation-log.md` under
the 2026-09-17 heading.

**2026-09-17, round 1 fix (coordinator ruling):** see the dated section at the end of this
file. The table below reflects the corrected, final scoring.

| Survey | Kinds | Buckets | Basis | Locator |
|---|---|---|---|---|
| S01-pedersen-2024-nir | neuromorphic | neuromorphic | Four physical platforms and seven simulators are named and evaluated; three proof-of-concept graphs run across eleven platforms, including four chips. | H axis, Results, ‘Experiments’, Fig. 2; Deployment depth |
| S02-kudithipudi-2025-neuromorphic-scale | neuromorphic | neuromorphic | Scalable architectures and named system dimensions are central to the review. | H axis; Abstract p. 801; Figs. 1-3, pp. 802-805 |
| S03-deng-2025-edgesnn | neuromorphic | neuromorphic | Supporting hardware platforms form a stated foundation. | H axis; Sec. III |
| S04-yik-2025-neurobench | neuromorphic | neuromorphic | The systems track targets deployed hardware and names candidate systems. | H axis; System Track Benchmark Framework |
| S05-davies-2021-loihi | neuromorphic | neuromorphic | Advancing Neuromorphic Computing With Loihi: A Survey of Results and Outlook; chip, multichip systems, mesh, and I/O are described in depth. | Title; H axis, Sec. II-A-B, Fig. 1 |
| S06-huynh-2022-implementing-snns | neuromorphic | neuromorphic | Hardware capacities and constraints are tabulated as mapping context. | H axis; Sec. 1, Table 1; Sec. 2.1 |
| S07-roy-2019-spike-machine-intelligence | GPU, neuromorphic | conventional, neuromorphic | The hardware half compares GPU execution, Neurogrid, TrueNorth, Loihi, address-event routing, networks-on-chip, in-memory computing, and several nonvolatile device families. | H axis; Nature pp. 612-615, Figs. 5-6 |
| S08-schuman-2017-hardware-survey | neuromorphic | neuromorphic | Hardware implementations and devices are a principal section. | H axis; Sec. V |
| S09-schuman-2022-opportunities | neuromorphic | neuromorphic | SpiNNaker, BrainScaleS, ODIN, Tianjic, TrueNorth, Loihi, DYNAPs, Neurogrid, and IFAT are situated by purpose and implementation, but hardware architecture is supporting context rather than the organizing focus. | H axis; Nature Computational Science p. 11 |
| S10-eshraghian-2023-training-snns | (none) | (none) | The dossier records no target kind | dossier |
| S11-rathi-2023-algorithms-hardware | neuromorphic | neuromorphic | Dedicated hardware discussion names multiple neuromorphic architectures and device technologies. | H axis; Introduction and hardware sections |
| S12-yamazaki-2022-applications | neuromorphic | neuromorphic | Neuromorphic hardware is listed as deployment context. | H axis locator: Introduction, TrueNorth, Loihi, SpiNNaker, and NeuroGrid examples |
| S13-ivanov-2022-neuromorphic-ai | neuromorphic, event NPU | conventional, neuromorphic | The review inventories TrueNorth, Loihi, Tianjic, SpiNNaker, BrainScaleS, NeuronFlow, DYNAP, Akida, Mythic, and memristive approaches. | H axis; Abstract and project overview |
| S14-basu-2022-snn-ics | neuromorphic | neuromorphic | Dedicated SNN ICs are compared across multicore, digital, and mixed-signal designs. | H axis; Abstract; Secs. II-IV |
| S15-nunes-2022-snn-survey | GPU, neuromorphic | conventional, neuromorphic | Section VI implements BindsNET and snnTorch and compares their abstractions, GPU support, intended learning modes, and simulation-time behavior, with Brian used as a reference point; neuromorphic hardware motivates efficiency claims, SpiNNaker appears in a reviewed example, and one Loihi implementation is summarized. | E axis, Sec. VI, PDF pp. 16-21; H axis, PDF pp. 8, 21-22 |
| S16-khan-2025-comprehensive | neuromorphic | neuromorphic | Section 5 compares TrueNorth, Loihi, SpiNNaker, BrainScaleS, DYNAP-SE, Darwin, and emerging devices, including neuron support, precision, connectivity, learning mode, and energy figures in Tables 4-5. | H axis; PDF pp. 14-16, publication pp. 188-190 |
| S17-zheng-2022-introductory | (none) | (none) | The dossier records no target kind | dossier |
| S18-rashed-2025-edge | (none) | (none) | The dossier records no target kind; its registered abstract page returned only an OpenReview browser-verification challenge and could not be read. | dossier |
| S19-xie-2024-compression | (none) | (none) | The dossier records no target kind | dossier |
| S20-ferreira-2025-edge-ai-circuits | neuromorphic | neuromorphic | Section 3 and Table 1 compare digital and analog neuromorphic circuits, including SpiNNaker, TrueNorth, Loihi 2, and fabricated implementations. | H axis; Table 1 |
| S21-manna-2023-frameworks | neuromorphic, FPGA | neuromorphic | Sections 3.1-3.2 name Loihi, SpiNNaker, FPGA, and other destinations as framework backends. | H axis; Sections 3.1-3.2 |
| S22-gallego-2022-event-based-vision | (none) | (none) | The dossier records no target kind | dossier |
| S23-gebregiorgis-2025-spike-based-overview | neuromorphic | neuromorphic | Sections 6 and 7 cover analog, digital, mixed-signal, memory-device, and many-core SNN implementations with explicit architectural trade-offs. | H axis; pp. 11-20 |
| S24-bouvier-2019-hardware-implementations | neuromorphic, simulator, FPGA | neuromorphic, simulated | Sections 3, 4, and 6 cover analog and digital neurocores, crossbars, large-scale systems, and embedded accelerators, including BrainScaleS, Neurogrid, TrueNorth, SpiNNaker, and Loihi; Section 6.2 and Table 2 explicitly distinguish simulated, FPGA, and fabricated technologies and flag incomparable model types and missing values. | H axis, Sections 3-4 and 6, pp. 8-24; J axis, Section 6.2 and Table 2, pp. 22-24 |
| S25-shrestha-2022-models-hardware | neuromorphic | neuromorphic | Sections III and IV explain design choices and detailed TrueNorth, Loihi, BrainScaleS, SpiNNaker, and Tianjic case studies. | H axis; Sections III-IV, pp. 15-24 |
| S26-chen-2026-neuromorphic-chips | neuromorphic | neuromorphic | Section 3 provides sustained treatment of Neurogrid, BrainScaleS, DYNAPs, ROLLS, Loihi, SpiNNaker, TrueNorth, Tianjic, PAICORE, ODIN, Loihi 2, SpiNNaker 2, and memristor systems. | H axis; Section 3, pp. 8-31 |
| S27-zolfagharinejad-2024-brain-inspired-systems | neuromorphic | neuromorphic | This systematic review covers brain-inspired hardware, including neuromorphic, in-memory, reservoir, and hyperdimensional computing; Abstract and Sections 2-3 categorize dominant brain-inspired hardware platforms. | Scope; H axis, Abstract and Sections 2-3 |
| S28-hu-2024-large-scale-snns | (none) | (none) | The dossier records no target kind | dossier |
| S29-ayasi-2025-practical-tutorial | GPU | conventional | Abstract and Section 4 identify the reported energy as a GPU operation-count proxy; Section 4 reports GPU-proxy experiments only, with no end-to-end named-chip route. | J axis, Abstract and Section 4; L axis, Section 4 |
| S30-alabdulwahid-2024-neuromorphic-architectures | neuromorphic, event NPU | conventional, neuromorphic | Section 3 and Table 1 compare representative neuromorphic projects, including TrueNorth, Loihi, SpiNNaker, BrainScaleS, Tianjic, GrAIOne, Akida, and memristor systems. | H axis; Section 3, Table 1 |
| S31-tayaraninajaran-2021-event-based-sensing | (none) | (none) | The dossier records no target kind | dossier |
| S32-cimarelli-2025-neuromorphic-vision | (none) | (none) | The dossier records no target kind | dossier |
| S33-hegao-2026-four-stage | (none) | (none) | The dossier records no target kind | dossier |
| S34-luu-2026-foundation | neuromorphic | neuromorphic | Section XI surveys digital, analog, mixed-signal, memristive, photonic, and quantum-inspired substrates. Table 7 compares BrainScaleS, Neurogrid, TrueNorth, SpiNNaker, Loihi, Darwin, and Dynap-SE. | H axis; Section XI, Table 7, pp. 78534-78539 |
| S35-caviglia-2026-neurotrain | (none) | (none) | The dossier records no target kind | dossier |
| S36-du-2026-edge-modalities | CPU, GPU, NPU, simulator | conventional, simulated | Physical measurements use NCNN on CPUs, GPUs, and NPUs in named edge devices; the Loihi, Darwin3, TrueNorth, and SpiNNaker2 results are explicitly simulated. | Scope; H axis, Results pp. 6-7, Methods pp. 12-14, Fig. 4 p. 22 |
| S37-farsa-2026-gpu-riscv | GPU, RISC-V, neuromorphic, FPGA | conventional, neuromorphic | It organizes GPU work into simulation frameworks, training acceleration, large-scale and multi-GPU simulation, and application deployments; it organizes RISC-V work into instruction-set extensions and tightly coupled cores, accelerator SoCs, programmable processors, and edge deployments; Sections II to V compare GPU, RISC-V, FPGA, ASIC, and dedicated neuromorphic hardware roles. | Scope; H axis, Sections II-V |

37 surveys scored. 27 name at least one target kind; 10 are silent.

Flagged for abstract review (dossier silent, title names an edge-execution term):

- `S03-deng-2025-edgesnn` (title contains "Edge"). Abstract read at arXiv:2507.14069;
  it names only "supporting hardware platforms" and "conventional hardware" in general
  terms. Its dossier's H axis ("Supporting hardware platforms form a stated foundation")
  is treated as naming the `neuromorphic` class under the 2026-09-17 round 1 ruling
  (below); the flag concerned only whether a *specific* other kind was named, and none
  was.
- `S18-rashed-2025-edge` (title contains "Edge"). The registered OpenReview URL returned
  only a browser-verification challenge and could not be read. Scored from the dossier
  alone. `targets.kinds` remains empty (its H axis scores `none`: "No named
  hardware-platform comparison was identified").

## 2026-09-17, round 1 fix: neuromorphic-inference ruling

Coordinator ruling: the chip word `neuromorphic` means fabricated spiking silicon as a
class. A dossier that says the survey covers neuromorphic hardware, neuromorphic chips or
circuits, or dedicated SNN ICs as a surveyed subject (typically its axis H basis at "full"
or "partial") names that kind, even without naming a specific chip. This inference applies
to the `neuromorphic` kind only; GPU, CPU, MCU, RISC-V, NPU, event NPU, FPGA, and simulator
still require the dossier (or a read abstract) to name them by word or by specific chip.
"Edge devices" alone still maps to no kind. Re-examined all 20 surveys that scored empty
under the original (stricter) pass, plus the 17 already-scored surveys, to see whether the
same rule would add `neuromorphic` to any of them.

**Rows that gained `neuromorphic` (10 previously-silent surveys):**

- `S01-pedersen-2024-nir`: H axis full, "four physical platforms" and "four chips" are
  named and evaluated as the paper's own interoperability demonstration. The "seven
  simulators" of the same sentence are general SNN software frameworks, the axis E
  subject, not a model of a named chip, so the `simulator` kind is not recorded.
- `S02-kudithipudi-2025-neuromorphic-scale`: H axis full, "Scalable architectures ... are
  central to the review" of a paper titled "Neuromorphic computing at scale".
- `S03-deng-2025-edgesnn`: H axis full, "Supporting hardware platforms form a stated
  foundation" of the EdgeSNN taxonomy.
- `S04-yik-2025-neurobench`: H axis partial, "The systems track targets deployed hardware
  and names candidate systems."
- `S06-huynh-2022-implementing-snns`: H axis partial, "Hardware capacities and constraints
  are tabulated as mapping context" (Table 1), from a paper titled "Implementing Spiking
  Neural Networks on Neuromorphic Architectures".
- `S08-schuman-2017-hardware-survey`: H axis full, "Hardware implementations and devices
  are a principal section" (coordinator's own example).
- `S11-rathi-2023-algorithms-hardware`: H axis full, "Dedicated hardware discussion names
  multiple neuromorphic architectures and device technologies."
- `S14-basu-2022-snn-ics`: H axis full, "Dedicated SNN ICs are compared across multicore,
  digital, and mixed-signal designs" (coordinator's own example).
- `S23-gebregiorgis-2025-spike-based-overview`: H axis full, "Sections 6 and 7 cover
  analog, digital, mixed-signal, memory-device, and many-core SNN implementations with
  explicit architectural trade-offs."
- `S27-zolfagharinejad-2024-brain-inspired-systems`: H axis full, "Abstract and Sections
  2-3 categorize dominant brain-inspired hardware platforms"; the survey's own scope
  states it "covers brain-inspired hardware, including neuromorphic, in-memory, reservoir,
  and hyperdimensional computing."

**Row revisited among the already-scored 17 (rule adds a kind to an existing entry):**

- `S37-farsa-2026-gpu-riscv`: gains `neuromorphic` alongside its existing GPU, RISC-V, and
  FPGA. Its own basis text, already quoted before this fix, states "Sections II to V
  compare GPU, RISC-V, FPGA, ASIC, and dedicated neuromorphic hardware roles" — the
  original pass had required a *named chip* for `neuromorphic` and missed that this
  sentence already names the hardware class as a surveyed subject.

**Confirmed to stay empty (10 surveys, explicitly re-examined and rejected):**

- `S10-eshraghian-2023-training-snns`: H axis `mentioned`, "Specialized hardware motivates
  SNNs, without platform taxonomy" — training tutorial, hardware is motivation only.
- `S17-zheng-2022-introductory`: H axis `none`, "No substantive hardware-platform survey
  was identified."
- `S18-rashed-2025-edge`: H axis `none`, "No named hardware-platform comparison was
  identified."
- `S19-xie-2024-compression`: H axis `mentioned`, "Neuromorphic chips motivate efficient
  DSNNs, without a platform taxonomy" — named as motivation, explicitly not surveyed.
- `S22-gallego-2022-event-based-vision`: H axis full, but the surveyed hardware is event
  cameras and embedded sensor processors, not SNN-execution silicon.
- `S28-hu-2024-large-scale-snns`: H axis `none`, "Hardware platforms are not a survey axis."
- `S31-tayaraninajaran-2021-event-based-sensing`: H axis full, but the surveyed hardware is
  visual/auditory/olfactory event sensors, not SNN-execution silicon.
- `S32-cimarelli-2025-neuromorphic-vision`: H axis full, but the surveyed hardware is
  neuromorphic *vision sensors* (event cameras), a sensing chip class distinct from the
  SNN-execution `neuromorphic` target kind this vocabulary tracks.
- `S33-hegao-2026-four-stage`: H axis `none`, "Hardware is motivational context, not a
  reviewed platform taxonomy."
- `S35-caviglia-2026-neurotrain`: H axis `mentioned`, "Sections 1 and 2.5 discuss
  neuromorphic hardware suitability in general terms" — a local-learning-rules survey; the
  mention is explicitly general/motivational, not a surveyed subject.

Net effect: 10 previously-silent surveys plus 1 already-scored survey gained `neuromorphic`,
for 11 changed rows. Nonempty surveys rose from 17 to 27; silent surveys fell from 20 to 10.
No other kind (GPU, CPU, MCU, RISC-V, NPU, event NPU, FPGA, simulator) was added or removed
anywhere in this pass. Rebuilt `data/generated/prior-survey-targets-summary.json` and Table
1 after the edit; full chain reran clean.

