# Audit B. Reset semantics and boundary behavior

Reviewed 16 September 2026.

## Verdict

Reset behavior is not a property that can be assigned once to a framework name. It must be
tracked across five separate boundaries. These are the mathematical neuron, the framework
constructor or conversion default, the exporter or importer, the compiler representation, and
the hardware execution primitive. The same toolchain can change classification at each boundary.

The audit supports six conclusions.

1. NIR 1.0.8 represents a post-spike reset to a fixed `v_reset`. It has no field for reset by
   subtraction. The reset field was added in May 2025, after the 2024 NIR paper artifact [1], [2].
2. SpikingJelly 2.0.0rc1 generic IF and LIF neurons default to hard reset at zero. Its rate-coding
   ANN-to-SNN recipes instead create `IFNode(v_reset=None)`, which means subtractive reset. Both
   the NIR exporter and Lava exporter reject that conversion default [3], [4].
3. Lava 0.10.0 and Lava-DL 0.6.0 built-in LIF and CUBA dynamics reset the membrane to zero.
   NetX `reset_interval` clears state at a sample or network boundary. It is not a subtractive
   post-spike reset [5], [6].
4. NxTF implements subtractive reset on Loihi 1 by transforming one logical neuron into two
   hardware compartments. This behavior is emulated, not native. The paper reports E1 physical
   measurements, and the measurement includes active neurocores and embedded x86 processors [7].
5. Sinabs 3.1.3 defaults ANN conversion to subtractive reset. Its DYNAP-CNN mapper maps this
   behavior to Speck's native `return_to_zero=False` mode [8].
6. Sinabs 3.1.3 does not preserve current NIR reset fields. `from_nir` ignores `v_reset` and
   instantiates Sinabs neurons with the subtractive default. `to_nir` omits the reset mechanism,
   after which NIR defaults the field to zero. The route is transformed in both directions [1],
   [8].

These conclusions replace any prose that treats NIR compatibility, Lava compatibility, or
Sinabs compatibility as proof that reset semantics survive the route.

## Audit method

The audit used official release tags where a release exists. NxTF has no retained release tag in
the archived repository, so the archived head and the primary paper were used. Every
consequential conclusion has at least two inspection paths. These paths include source plus
documentation, source plus an executed notebook record, or source plus a primary paper.

Exa search was attempted for four queries. Every request returned HTTP 402 because the available
Exa credits were exhausted. This prevented Exa-based coverage expansion. It did not prevent
verification because all decisive artifacts were available from official repositories or primary
papers. PDF extraction used `pypdf` in an isolated temporary virtual environment. No repository
dependency was changed.

The capability labels have narrow meanings in this audit.

| Label | Meaning |
|---|---|
| `native` | The target built-in neuron or chip configuration directly exposes the behavior. |
| `transformed` | The bridge changes the representation or the semantics. |
| `emulated` | Additional target components reproduce a behavior absent from the native primitive. |
| `host-assisted` | Host action is required during execution or between samples. |
| `unsupported` | The inspected path explicitly rejects the input contract. |
| `undocumented` | No official artifact establishes support or rejection. |

An absent document is not evidence of impossibility. The `undocumented` label is therefore used
for Loihi 2 custom-microcode soft reset. The hardware is programmable, but the reviewed public
Lava and NetX artifacts do not establish a supported reset-preserving route for this case.

## Claim audit

### NIR mathematical semantics

NIR 1.0.8 defines `CubaLIF`, `IF`, and `LIF` with the same reset form. A spike assigns
`v_reset`; a non-spike retains the state. `None` does not mean subtractive reset. The constructor
replaces `None` with a zero-valued array. The official primitive table gives the same fixed-value
equation [1]. This result is limited to NIR 1.0.8. Commit
`6189cacd1b1e89d1e587afd90f0f8930361bae98` added `v_reset` on 30 May 2025. The 2024 paper and
its artifact must not be used as evidence for the later field-level contract.

NIR is declarative. Its documentation states that backends can implement primitives differently.
The paper reports differences in integration order, spike timing, reset timing, quantization, and
determinism [2]. Therefore, a syntactically accepted graph does not establish execution-equivalent
neuron dynamics.

Inspection path A used the tagged primitive implementation and the official primitive table.
Inspection path B used the field-introduction commit and the NIR paper's mismatch analysis.

### SpikingJelly framework and exporter defaults

The generic SpikingJelly neuron default is `v_reset=0.0`. This is hard reset. Setting
`v_reset=None` selects subtraction by `v_threshold` [3]. The rate-coding conversion recipe makes
a different choice. It creates `IFNode(v_reset=None)` for both layer-wise and channel-wise
conversion unless the caller supplies another neuron factory [4]. A statement about the generic
constructor is therefore not a statement about the ANN-to-SNN conversion output.

The NIR exporter calls `_hard_reset`. It raises `NotImplementedError` when `v_reset is None` and
serializes a fixed `v_reset` otherwise. This is an `unsupported` edge for the default conversion
output. It is conservative behavior because current NIR has no subtractive-reset field [1], [4].

The Lava exporter also rejects any IF or LIF for which `v_reset != 0.0`. Python comparison makes
this reject `None` as well as nonzero fixed reset. The accepted path maps the neuron to Lava-DL
CUBA parameters, quantizes the model, and applies additional operator restrictions. It is an
`unsupported` edge for the conversion default. A separately configured hard-zero model can enter
the path, but that is not preservation of the default converted network [4].

Inspection path A used the 2.0.0rc1 recipe, NIR exporter, and Lava exporter source. Inspection
path B used the official neuron and NIR-exchange documentation.

### Lava, Lava-DL, and NetX

Lava 0.10.0 documents the built-in LIF equation as `v[t] = 0` after a spike. Its floating-point
and fixed-point CPU process models assign zero to every spiking voltage. The fixed-point model is
tagged as bit accurate with Loihi hardware [5]. This establishes the public built-in semantics. It
does not make the open CPU model itself a hardware execution result.

Lava-DL 0.6.0 applies the same behavior. The SLAYER leaky-integrator equation multiplies state by
`1-s`, and the integer implementation replaces the recurrent state with zero after threshold
crossing [6]. NetX maps HDF5 `LOIHI` and `CUBA` neurons to Lava `LIF` or `LIFReset`. The HDF5
neuron record contains threshold and decay parameters, not a post-spike reset-mode parameter.

`LIFReset` and NetX `reset_interval` are easy to misread. They periodically clear both current and
voltage state. Ordinary spikes still reset voltage to zero. This mechanism supports sample or
network boundary clearing. It does not implement soft reset.

The official NIR-to-Lava example creates Lava `LIF` or SLAYER CUBA neurons without reading the
NIR node's `v_reset`. A NIR fixed reset is therefore changed to hard zero unless its value was
already zero. The example also warns that the Lava-DL current and voltage states require manual
reset after each forward pass. The post-spike route is `transformed`; the sample-boundary route is
`host-assisted` [1], [5], [6].

Inspection path A used the Lava process definition and two CPU process models. Inspection path B
used the SLAYER dynamics and NetX loader. The NIR bridge conclusion was checked independently in
the Lava and Lava-DL branches of the official NIR example.

### NxTF and Loihi 1

NxTF distinguishes hard and soft reset. The constructor fallback is `hard`. Soft reset sets
`neuronSize=2`, creates recurrent inhibitory connectivity, and subtracts a quantized threshold
from the soma after a spike. The paper describes the same two-compartment mechanism and states
that it doubles compartment allocation [7]. This is an `emulated` hardware capability. Calling it
native would hide the resource cost and would misstate the Loihi 1 primitive.

The NxTF paper provides E1 deployment evidence. All reported measurements used NxSDK 0.9.5 on a
Nahuku32 Loihi 1 board. Execution time includes spiking and management phases. Energy multiplies
execution time by static and dynamic power from active neurocores and embedded x86 processors.
Unused neurocores and x86 cores are excluded. External workstation preprocessing and the host are
outside this boundary [7].

The deployment evidence does not prove that every reported NxTF benchmark used soft reset. The
paper explicitly states that the SLAYER models used hard reset. Converted models use the SNN
Toolbox bridge, while the archived backend defaults to hard reset if `reset_mode` is absent. The
official CIFAR tutorial explicitly selects soft reset. Claims must identify the configuration
rather than generalize from the compiler capability.

Inspection path A used the paper's algorithm and measurement sections. Inspection path B used the
archived compiler source, the SNN Toolbox backend, and the official tutorial configuration.

### Sinabs and Speck

Sinabs 3.1.3 `from_model` defaults to `MembraneSubtract()`. The implementation subtracts the
threshold unless a separate subtraction value is supplied. The DYNAP-CNN mapper converts
`MembraneSubtract` to `return_to_zero=False` and `MembraneReset` to `return_to_zero=True` [8]. The
official Speck documentation states that both modes are provided by the devkit and that
subtraction is the default. This is a `native` mapping for reset semantics. Other parts of the
route remain transformed. Average pooling becomes sum pooling, linear layers become 1 by 1
convolutions, and parameters are quantized to the chip formats [9].

The NIR bridge is not reset-preserving. `sinabs.from_nir` constructs `IAFSqueeze` and `LIFSqueeze`
without passing `node.v_reset`. Those classes inherit Sinabs's subtractive default. The exporter
constructs NIR IF and LIF nodes without `v_reset`, which NIR 1.0.8 then replaces with zero [1],
[8]. These are silent `transformed` edges rather than explicit rejection.

The official NIR-to-Speck notebook exercises the transformed route on a physical Speck 2F module.
Its stored output reports 90 percent accuracy on 50 subsampled N-MNIST examples. This is E2. The
measurement boundary contains chip output accuracy only. It includes host-side event conversion,
injection, and readout, and it reports no latency or energy [10]. The result proves that the route
runs. It does not prove that current NIR fixed-reset semantics are preserved.

Inspection path A used Sinabs source and Speck documentation. Inspection path B used the pinned
NIR bridge source and the stored physical-device notebook output.

## Route findings

| Route | Post-spike reset result | Classification | Deployment evidence | Boundary consequence |
|---|---|---|---|---|
| SpikingJelly rate conversion to NIR exporter | Soft-reset default is rejected | `unsupported` | None | The model cannot be exported as-is. |
| SpikingJelly rate conversion to Lava exporter | Soft-reset default is rejected | `unsupported` | E3 only for a separately configured hard-zero path | Reset behavior must be changed before export. |
| NIR 1.0.8 to official NIR Lava importer | `v_reset` is ignored and built-in hard zero is selected | `transformed` | None for this example | Only a zero-reset NIR node retains reset value. |
| NIR Lava-DL forward to the next sample | State is not reset automatically | `host-assisted` | None | The caller must clear current and voltage. |
| NetX HDF5 CUBA or LOIHI to Lava LIF | Hard zero is retained | `native` | E3 as a documented path | `reset_interval` is a separate boundary mechanism. |
| NxTF soft-reset logical neuron to Loihi 1 | Two compartments reproduce subtraction | `emulated` | E1 for the NxTF physical route | Compartment count doubles. |
| Sinabs converted SNN to Speck | Subtraction maps to `return_to_zero=False` | `native` | E3 for the general documented route | Operator and precision transformations remain. |
| NIR 1.0.8 to Sinabs | Fixed reset is ignored and becomes subtraction | `transformed` | E2 for the official Speck notebook | Physical execution does not imply semantic preservation. |
| Sinabs to NIR 1.0.8 | Reset function is omitted and becomes fixed zero | `transformed` | None | A round trip changes the neuron contract. |
| Loihi 2 custom microcode soft reset through public Lava or NetX | No reviewed public route establishes the mapping | `undocumented` | None | Do not infer support or impossibility. |

## Required corrections to current research records

The current provisional NIR claim is substantively correct, but its citation and scope require a
version correction. The fixed `v_reset` field is a 2025 addition. The decisive authority is NIR
1.0.8 source and documentation, not the 2024 paper alone.

The raw audit statement that NIR defines subtractive reset as a primitive is rejected. The paper
experiments compare reset discretizations, but the current graph schema does not encode a
subtractive mode. Backend experiment configuration is not a NIR field.

The current `sinabs-to-nir` edge lists the reset behavior as unknown. It is no longer unknown.
Sinabs 3.1.3 omits the reset function on export and ignores the NIR reset value on import. Both
directions are transformed.

The current `nir-to-lava-dl` edge says that IF, LIF, and CUBA-LIF node structure is preserved. It
must add that reset value is not preserved by the official importer. The physical E2 evidence in
the 2024 NIR paper applies to the historical artifact and tested configurations. It must not be
treated as validation of the reset field added in 2025.

The current SpikingJelly NIR route should include the explicit rejection of the rate-conversion
default. The restriction is not merely limited neuron coverage.

## Version and source ledger

| Artifact | Version scope | Date | Exact inspection location |
|---|---|---|---|
| NIR | 1.0.8, commit `490ce8e03d74c24efeb9a120a6caaf5a67d34aee` | 6 July 2026 | `nir/ir/neuron.py`; `docs/source/primitives.md`; official Lava example |
| SpikingJelly | 2.0.0rc1, commit `f923407992b8428041cbe177a38f0962740eafb4` | 29 August 2026 | rate recipe; `nir_exchange/to_nir.py`; `lava_exchange.py`; neuron tutorial |
| Lava | 0.10.0, commit `223307ecfad126442e59bedf36322401a38adf3b` | 7 August 2024 | `lava/proc/lif/process.py`; `lava/proc/lif/models.py` |
| Lava-DL and NetX | 0.6.0, commit `8b3c9e03dc5fd6e9989f34630fea3f0a1d008845` | 7 August 2024 | SLAYER leaky-integrator dynamics; NetX HDF5 loader |
| NxTF | archived head `3dc53bfcfae1efe8772b8cb5e2c512bb28c872f8` | 9 October 2023 | `dnn_layers.py`; SNN Toolbox backend; primary paper |
| Sinabs | 3.1.3, commit `d84078e0af1bc40f716b61de199880bd8713bd2d` | 4 February 2026 | `from_torch.py`; reset mechanisms; DYNAP-CNN mapper; `nir.py`; Speck docs and notebook |

## References

[1] NIR contributors, "NIR neuron primitives and documentation," version 1.0.8,
[source](https://github.com/neuromorphs/NIR/tree/490ce8e03d74c24efeb9a120a6caaf5a67d34aee),
Jul. 2026.

[2] J. E. Pedersen et al., "Neuromorphic intermediate representation. A unified
instruction set for interoperable brain-inspired computing," *Nature Communications*,
vol. 15, art. 8122, 2024, doi: 10.1038/s41467-024-52259-9.

[3] SpikingJelly contributors, "Neuron reset documentation," version 2.0.0rc1,
[source](https://github.com/fangwei123456/spikingjelly/blob/f923407992b8428041cbe177a38f0962740eafb4/docs/source/tutorials/en/neuron.rst),
Aug. 2026.

[4] SpikingJelly contributors, "Rate-coding, NIR, and Lava exchange implementations,"
version 2.0.0rc1,
[source](https://github.com/fangwei123456/spikingjelly/tree/f923407992b8428041cbe177a38f0962740eafb4/spikingjelly/activation_based),
Aug. 2026.

[5] Lava contributors, "LIF process and process models," version 0.10.0,
[source](https://github.com/lava-nc/lava/tree/223307ecfad126442e59bedf36322401a38adf3b/src/lava/proc/lif),
Aug. 2024.

[6] Lava-DL contributors, "SLAYER neuron dynamics and NetX HDF5 loader," version 0.6.0,
[source](https://github.com/lava-nc/lava-dl/tree/8b3c9e03dc5fd6e9989f34630fea3f0a1d008845/src/lava/lib/dl),
Aug. 2024.

[7] B. Rueckauer et al., "NxTF. An API and compiler for deep spiking neural networks
on Intel Loihi," *ACM Journal on Emerging Technologies in Computing Systems*, vol. 18,
no. 3, 2022, doi: 10.1145/3501770. Archived
[source](https://github.com/intel-nrc-ecosystem/models/tree/3dc53bfcfae1efe8772b8cb5e2c512bb28c872f8/nxsdk_modules_ncl).

[8] Sinabs contributors, "Conversion, reset, DYNAP-CNN, and NIR implementations,"
version 3.1.3,
[source](https://github.com/synsense/sinabs/tree/d84078e0af1bc40f716b61de199880bd8713bd2d/sinabs),
Feb. 2026.

[9] SynSense, "Sinabs Speck deployment basics and training guidance," Sinabs 3.1.3,
[source](https://github.com/synsense/sinabs/tree/d84078e0af1bc40f716b61de199880bd8713bd2d/docs/speck),
Feb. 2026.

[10] SynSense, "Import a model from NIR and deploy it to Speck," notebook commit
`8b87dc310dc9f626c6ba7fe3a8271ab253d5e95b`,
[source](https://github.com/synsense/sinabs/blob/8b87dc310dc9f626c6ba7fe3a8271ab253d5e95b/docs/tutorials/nir_to_speck.ipynb),
Oct. 2025.
