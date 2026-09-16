# SNN Toolbox vs. SpikingJelly `ann2snn`: source-level equivalence test

**Claim under test** (author's own framing): "SNN Toolbox and SpikingJelly are based on the same papers so they are almost internally equivalent."

**Method**: read actual source (not docs/abstracts) from both repos, current `master` and, for SpikingJelly, also the last classic pre-refactor branch (`0.0.0.0.14`), since the two differ substantially. All code quoted verbatim from files fetched via `raw.githubusercontent.com` on 2026-09-15.

---

## 0. A precondition finding: SpikingJelly's `ann2snn` has been completely rewritten

Before any axis-by-axis comparison is meaningful, note that `spikingjelly/activation_based/ann2snn/converter.py` on `master` (pushed 2026-09-14, i.e. the day before this research) is **not** the module described in the SpikingJelly paper, most blog posts, and most tutorials citing SpikingJelly's ann2snn. It has been refactored into an FX-graph "recipe" framework:

```python
class FXConverter:
    def __init__(self, recipe: Union[str, FXConversionRecipe], device=...):
        """
        ``FXConverter`` 只负责 device 解析、FX tracing 和固定转换模板调度；
        具体算法参数与图变换由 ``recipe`` 定义。
        """
```

`converter.py` itself now contains **no neuron construction, no normalization logic, and no paper citations** — it is pure orchestration (`validate → before_trace → symbolic_trace → after_trace → insert_observers → calibrate → replace → finalize`), delegated entirely to a `recipes/` package: `local_threshold_balancing.py`, `rate_coding.py`, `transformer_td_equivalent.py`, `sta_transformer.py`, `spikezip_qann.py`, `qwen2.py`, `step_mode_adapters.py`, plus a new `qcfs.py` (a `SignedQCFSSequenceEncoder`, directly adjacent to this thesis's own subject matter) and a new `nir_exchange/` and `lynxi_exchange.py`.

The classic API (branch `0.0.0.0.14`, confirmed still the one most tutorials/forum answers describe) is a single ~340-line `Converter(nn.Module)` with `VoltageHook`/`VoltageScaler`/`IFNode` — this is the version most survey material implicitly means by "SpikingJelly's ann2snn."

**This is itself a finding for a survey on neuromorphic deployment tooling: a framework whose conversion core has been substantially rewritten within the life of a single thesis is a moving target, unlike SNN Toolbox, which has been dormant (and therefore stable) since ~2021–2022.**

I report both versions below where semantics differ.

---

## 1. Which papers does each implement?

**SNN Toolbox** (`snntoolbox/conversion/utils.py`): the file's own docstring credits `@author: rbodo` — Bodo Rueckauer, first author of Rueckauer et al. 2017 (Frontiers in Neuroscience). The GitHub README states explicitly:

> "See also the accompanying articles [Rueckauer et al., 2017], [Rueckauer and Liu, 2018], and [Rueckauer and Liu, 2021]."

So SNN Toolbox is not merely "based on" Rueckauer 2017 — it is the reference implementation, written by the same author, of that paper's algorithm (percentile-based weight/threshold normalization + reset-by-subtraction IF neurons), later extended to hardware deployment via the NxTF paper (Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild — arXiv:2101.04261 / ACM JETC 2022).

**SpikingJelly `ann2snn` (current, `master`)**: grepping every `.py` file in `ann2snn/` and `ann2snn/recipes/` for `Rueckauer|Diehl|arXiv|Reference` turns up exactly one citation, in `recipes/local_threshold_balancing.py`:

```python
参考文献：Bu T, Li M, Yu Z. Inference-Scale Complexity in ANN-SNN
Conversion for High-Performance and Low-Power Applications.
arXiv:2409.03368, 2024. Accepted by CVPR 2025.
```

**No docstring in the current `ann2snn` package cites Rueckauer 2017 or Diehl 2015.** The primary, best-performing current recipe (`LocalThresholdBalancingRecipe`) is instead an original-author implementation of a 2024/2025 CVPR paper (Bu, Li, Yu) that postdates Rueckauer by seven years and uses a different normalization principle (see §2). The legacy `RateCodingRecipe` (the direct descendant of the old `Converter`) carries no citation at all in its docstring, though its `MaxNorm`/`RobustNorm`/scaling-fraction modes are functionally the ones from Diehl et al. 2015 / Rueckauer et al. 2017.

The community-facing tutorial (`spikingjelly.readthedocs.io/.../ann2snn.html`) references "[3]" for the LTB paper and cites "[1]" for a max-pooling gating technique, but does not mention Rueckauer or Diehl by name anywhere in the current tutorial text retrieved.

**Verdict on lineage**: partial, and getting weaker over time. The *legacy* SpikingJelly `Converter` (branch `0.0.0.0.14`) is a direct, acknowledged-in-spirit reimplementation of the Diehl/Rueckauer normalization + reset-by-subtraction algorithm (see code in §3). The *current* `master` conversion module has moved its flagship recipe onto a different, newer paper (Bu et al. 2024/2025) and no longer cites Rueckauer/Diehl anywhere in the code. SNN Toolbox is the Rueckauer lineage's own reference implementation. So "based on the same papers" is true for legacy SpikingJelly, false as a description of current SpikingJelly's primary recipe.

---

## 2. Normalization method

**SNN Toolbox** (`snntoolbox/config_defaults`):

```ini
[normalization]
percentile = 99.9
normalization_schedule = False
```

`snntoolbox/conversion/utils.py`:

```python
def get_scale_fac(activations, percentile):
    """Determine the activation value at ``percentile`` of the layer distribution."""
    return np.percentile(activations, percentile) if activations.size else 1

def apply_normalization_schedule(perc, layer_idx):
    """... decreases scale factor in higher layers ..."""
    return int(perc - layer_idx * 0.02)
```

Global default is a 99.9th-percentile robust norm per layer (equivalent to SpikingJelly's legacy `"99.9%"` `RobustNorm`), with an optional layer-index-dependent percentile schedule. `normalize_parameters()` scales weights and biases directly (not just at inference), and explicitly extracts BatchNorm `moving_mean`/`moving_variance`/`gamma`/`beta` for fusion (`snntoolbox/parsing/model_libs/keras_input_lib.py`).

**SpikingJelly, legacy (`0.0.0.0.14`) `VoltageHook`**:

```python
def forward(self, x):
    if isinstance(self.mode, str):
        if self.mode[-1] == '%':
            s_t = torch.tensor(np.percentile(x.detach().cpu(), float(self.mode[:-1])))
        elif self.mode.lower() in ['max']:
            s_t = x.max().detach()
    elif isinstance(self.mode, float) and 0 < self.mode <= 1:
        s_t = x.max().detach() * self.mode
    ...
    self.scale = (1 - self.momentum) * self.scale + self.momentum * s_t
```

This is algorithmically the same family as SNN Toolbox: a per-layer scalar computed from a percentile (or max) of that layer's ReLU activations, with an EMA (`momentum`) across calibration batches rather than SNN Toolbox's static compute-once-then-freeze. `mode='Max'` = SNN Toolbox's max-norm; `mode='99.9%'` = SNN Toolbox's default 99.9th-percentile RobustNorm. **This axis is genuinely convergent** between SNN Toolbox and legacy SpikingJelly — same algorithm, same granularity (per layer, scalar), same two named modes.

**SpikingJelly, current `master`**: the flagship `LocalThresholdBalancingRecipe` replaces the *scalar-per-layer* threshold with a **channel-wise, online-updated threshold** (`LocalThresholdBalancingHook`):

```python
overflow = torch.clamp(x_stat - threshold_view, min=0)
threshold = threshold + 2.0 * overflow.mean(dim=reduce_dims)
threshold = torch.clamp(threshold, min=self.eps)
```

This is a materially different, per-channel, iterative-update algorithm (an implementation of Bu/Li/Yu 2024/2025), not a percentile computation. The legacy scalar `RobustNorm` mode still exists in `RateCodingRecipe` (renamed, same percentile math as before), but the current documentation's own benchmark shows why this distinction is not cosmetic (from `spikingjelly.readthedocs.io/.../ann2snn.html`):

| Method | Timesteps | ImageNet ResNet-18 Top-1 |
|---|---|---|
| ANN | — | 69.756% |
| RobustNorm (legacy, scalar, per-layer) | 32 | **12.462%** |
| LocalThresholdBalancingRecipe (channel-wise) | 32 | **65.472%** |

A >50-point accuracy gap between SpikingJelly's own two normalization granularities on the same network at the same T. SNN Toolbox's default is the *scalar* per-layer percentile method (matching SpikingJelly's *legacy*/now-deprecated-in-spirit path), not the channel-wise LTB method that current SpikingJelly recommends. **If someone converts a modern deep CNN with SNN Toolbox's default settings and compares to SpikingJelly's current recommended recipe, they are not comparing the same algorithm, and the accuracy gap this alone produces (>50 points on ResNet-18/ImageNet per SpikingJelly's own numbers) dwarfs anything attributable to framework "equivalence."**

**Verdict**: convergent for legacy SpikingJelly vs. SNN Toolbox (same percentile algorithm, per-layer granularity). Not convergent for current SpikingJelly (per-channel iterative threshold, different paper, materially different accuracy profile at low T on deep nets).

---

## 3. Neuron model and reset semantics — the critical axis

**SNN Toolbox default** (`snntoolbox/config_defaults`):

```ini
[cell]
v_thresh = 1
v_reset = 0
reset = Reset by subtraction
```

`snntoolbox/simulation/backends/inisim/temporal_mean_rate_tensorflow.py`, `set_reset_mem`:

```python
elif self.config.get('cell', 'reset') == 'Reset by subtraction':
    if hasattr(self, '_v_thresh'):
        new = tf.where(tf.greater(spikes, 0), mem - self.v_thresh, mem)
        new = tf.where(tf.less(spikes, 0), new + self.v_thresh, new)
elif self.config.get('cell', 'reset') == 'Reset by modulo':
    new = tf.where(tf.not_equal(spikes, 0), mem % self.v_thresh, mem)
else:  # 'Reset to zero'
    ...
```

Default is **reset by subtraction**, the exact mechanism Rueckauer et al. 2017 showed matters (their paper's ~20-point finding). "Reset to zero" and "Reset by modulo" exist as configurable alternatives but are not the default.

**SpikingJelly, legacy (`0.0.0.0.14`)**, `replace_by_ifnode`:

```python
m1 = neuron.IFNode(v_threshold=1., v_reset=None)
```

`v_reset=None` is SpikingJelly's soft-reset (reset-by-subtraction) convention. **This matches SNN Toolbox's default exactly** — same mechanism, same lineage.

**SpikingJelly, current `master`**. Two live recipes were checked directly:

`recipes/rate_coding.py` (twice, for calibration and final replacement):
```python
neuron.IFNode(v_reset=None)
```

`recipes/local_threshold_balancing.py` uses a dedicated neuron, `neuron.HalfThresholdIFNode`, whose constructor **hardcodes** the reset mode (not user-configurable):
```python
super().__init__(
    v_threshold=v_threshold,
    v_reset=None,
    ...
)
half_threshold = self.v_threshold / 2.0
self.set_reset_value("v", half_threshold)
self.v = half_threshold
```

So **both current SpikingJelly ann2snn recipes default to soft reset (reset-by-subtraction)**, matching SNN Toolbox/Rueckauer on this specific axis — contrary to what one might fear from a framework rewrite, this is one axis that survived. (Note separately: SpikingJelly's *general-purpose* `neuron.IFNode`, used outside ann2snn for directly-trained SNNs, now defaults to `v_reset: Optional[float] = 0.0`, i.e. hard reset — so a careless reader of SpikingJelly's neuron-module docs alone, without checking the ann2snn recipe call sites specifically, could wrongly conclude ann2snn uses hard reset by default. It does not.)

**However — and this is the internal contradiction the survey should flag** — SpikingJelly's own two paths for taking a converted model to hardware/interop **reject the soft-reset neurons its own converter produces**:

`spikingjelly/activation_based/lava_exchange.py` (repeated at five separate call sites, e.g. line 746, 764, 1177, 1186):
```python
if sj_ms_neuron.v_reset != 0.0:
    raise ValueError("lava only supports for v_reset == 0!")
```
and for the CUBA-LIF path (line 418):
```python
assert v_reset == 0.0, (
    "CubaLIFNode only supports for hard reset with v_reset = 0. !"
)
```

`spikingjelly/activation_based/nir_exchange/to_nir.py`:
```python
def _hard_reset(module: neuron.BaseNode) -> float:
    if module.v_reset is None:
        raise NotImplementedError("NIR does not distinguish soft reset.")
    return module.v_reset
```

Note this is specifically a limitation of **SpikingJelly's `to_nir.py` exporter implementation**, not of the NIR specification itself: the NIR primitive spec (Nature Communications 2024, "Neuromorphic Intermediate Representation") *does* define subtractive reset as a primitive (`v(t+) = v(t) - θ_reset`) alongside hard reset (`v(t+) = 0`); SpikingJelly's exporter simply never implements the subtractive branch and raises `NotImplementedError` unconditionally whenever `v_reset is None`.

**Net effect**: SpikingJelly's `ann2snn.convert()` produces soft-reset (`v_reset=None`) neurons by default (in agreement with SNN Toolbox), but *neither* of SpikingJelly's own subsequent export paths (`lava_exchange`, `nir_exchange`) can accept that output without either (a) the user silently re-parameterizing to hard reset — which reintroduces exactly the accuracy gap Rueckauer 2017 measured — or (b) writing new code. **A model converted by SpikingJelly's own ann2snn module cannot be handed to SpikingJelly's own Lava or NIR export code as-is.** This is a self-consistency failure internal to one framework, distinct from (and additional to) the SNN-Toolbox-vs-SpikingJelly equivalence question.

**Verdict on this axis**: SpikingJelly's ann2snn conversion module (legacy and current) and SNN Toolbox agree on reset-by-subtraction as the default — this is the one axis where the "same papers, same behavior" claim holds up under direct code inspection. But SpikingJelly's own downstream deployment code does not honor that default, which matters directly for §7/§8 below.

---

## 4. Input encoding

**SNN Toolbox** (`snntoolbox/config_defaults`):
```ini
[input]
poisson_input = False
```
Default is **not** Poisson — constant/analog current input by default (`input_rate` and Poisson generation exist as an option, off by default).

**SpikingJelly**: the current `ann2snn` tutorial states explicitly:

> "During simulation, the converted SNN should receive a constant analog input under this conversion theory. A Poisson encoder can introduce additional accuracy loss."

**Verdict**: convergent. Both frameworks default to constant/analog current input and treat Poisson encoding as an optional, accuracy-degrading alternative rather than the primary mode — this is a real point of agreement, and a place where a common misconception ("ANN-SNN conversion = Poisson rate coding") is wrong for both tools.

---

## 5. Output decoding

Both frameworks decode by **spike-count / average firing rate** read out over the simulation window (not membrane-potential readout, not softmax-over-votes as a default). SNN Toolbox's `temporal_mean_rate` coding scheme name states this directly (`[conversion] spike_code = temporal_mean_rate` is the default in `config_defaults`, among alternatives `temporal_pattern`, `ttfs`, `ttfs_dyn_thresh`, `ttfs_corrective`). SpikingJelly's `VoltageScaler`/output-node structure likewise reads out accumulated spikes over `T` steps (both legacy and current recipes; the tutorial's own reported numbers are of the form "SNN accuracy (simulation N time-steps)" computed from top-1 over accumulated output). **Convergent** on this axis, though SNN Toolbox additionally offers three other coding schemes (`temporal_pattern`, `ttfs*`) that SpikingJelly's ann2snn does not appear to implement (NOT FOUND in code searched).

---

## 6. Supported layers and operators

**SNN Toolbox**: explicit BatchNorm parameter extraction and fusion (`keras_input_lib.py` pulls `moving_mean`, `moving_variance`, `gamma`, `beta` directly from the Keras layer for folding into the preceding Conv/Dense). Restriction list (`config_defaults`) names supported spiking layer types: `Dense, Conv1D, Conv2D, DepthwiseConv2D, Conv2DTranspose, UpSampling2D, MaxPooling2D, AveragePooling2D, Sparse, SparseConv2D, SparseDepthwiseConv2D`, plus `Reshape, Flatten, Concatenate, ZeroPadding2D`. **MaxPooling2D is explicitly supported** (via `maxpool_type = fir_max` / `exp_max` / `avg_max` spiking approximations), unlike the common folklore that ANN2SNN tools require avg-pool only.

**SpikingJelly**, legacy `Converter.fuse()`: explicit Conv-BN fusion via `torch.nn.utils.fusion.fuse_conv_bn_eval`, pattern-matched for `Conv1d/2d/3d + BatchNorm1d/2d/3d`. Current `recipes/rate_coding.py` and `local_threshold_balancing.py` both call a shared `_fuse_conv_bn` helper — so **BN folding is present in both current and legacy SpikingJelly**, contradicting an assumption that this might be SNN-Toolbox-only.

Pooling: SpikingJelly's own tutorial (current) explicitly warns there is **no general max-pooling conversion rule** in the rate-coding recipe and recommends `AvgPool2d`, citing the literature's momentum-based gating approach as unimplemented in this recipe. `lava_exchange.py`'s operator dispatch (`isinstance(net[i], ...)`) supports only `nn.Linear`, `nn.Conv2d`, `nn.AvgPool2d` (as `SumPool2d`), and `nn.Flatten` — **no `nn.MaxPool2d`, no explicit residual/skip-add handling** found in the branches checked; anything else raises `ValueError(type(net[i]))` or `NotImplementedError(type(net[i]))`.

**Verdict**: SNN Toolbox supports max-pooling natively (with a choice of three spiking approximations) and Concatenate; SpikingJelly's ann2snn path (both generations) does not, and its own docs recommend architectural workarounds (swap to avg-pool) rather than a built-in conversion rule. Residual/skip connections: NOT FOUND to be explicitly handled in either the legacy `Converter` or the current recipes/`lava_exchange` operator-dispatch code inspected (both appear to assume a feed-forward `nn.Sequential`-like structure for the FX-traced graph, though the FX-tracing approach in principle can traverse arbitrary `forward()` graphs — the *hardware export* paths, `lava_exchange` in particular, are the ones restricted to the enumerated sequential ops above).

---

## 7. Scope and deployment reach

**SNN Toolbox** (`config_defaults` `[restrictions]`):
```ini
simulators_pyNN = {'nest', 'brian', 'neuron', 'spiNNaker'}
simulators_other = {'INI', 'brian2', 'MegaSim', 'loihi'}
```
Plus NxTF (a dedicated Keras-native compiler for Loihi 1, built by the same author, with an explicit SNN-Toolbox-to-NxTF bridge module in `intel-nrc-ecosystem/models/nxsdk_modules_ncl/snntoolbox`). Total distinct backend families: INI (built-in), Brian2, MegaSim, Loihi (via NxTF), and the whole pyNN family (NEST, Brian, NEURON, SpiNNaker).

**SpikingJelly `ann2snn`**: emits a plain `torch.fx.GraphModule` of SpikingJelly neuron/layer modules — runs only inside SpikingJelly/PyTorch simulation by default. Two further export modules exist elsewhere in the SpikingJelly codebase (not part of `ann2snn` itself, but the only bridges out of it): `lava_exchange.py` (→ Lava/Loihi) and `nir_exchange/` (→ NIR, a cross-framework IR) and `lynxi_exchange.py` (→ Lynxi hardware, a Chinese neuromorphic chip vendor; contents not deeply audited here beyond confirming the file exists — NOT FOUND further detail within this task's time budget). No pyNN, Brian2, NEST, or SpiNNaker bridge was found in the SpikingJelly source tree searched.

**Verdict**: SNN Toolbox's backend list is broader and, critically, was purpose-built for the exact conversion pipeline (percentile-norm + reset-by-subtraction) it ships. SpikingJelly's bridges are structurally adjacent modules with their own independent constraints (see §3, §8 below) that do not automatically honor what `ann2snn` produces.

---

## 8. Maintenance status

**SNN Toolbox**: PyPI/CHANGELOG shows v0.6.0 released 2021-03-17 ("Updated docs for release 0.6.0", commit `1f1adda`). Last commits found via GitHub API search: `9d421f4` (2022-08-08, "Fixed deprecated import in GUI") and `047cedd` (2022-08-13, "Fixed kernel_conversion slicing issue"), both by `rbodo`. No commits found after August 2022 in the search performed. 399 GitHub stars, 3 open issues (low issue count consistent with a dormant, low-traffic repo rather than an actively triaged one). **Effectively dormant since mid-2022.**

**SpikingJelly**: `pushed_at: 2026-09-14T18:01:44Z` (one day before this research), 2133 stars, actively developed — the `ann2snn` subpackage was rewritten into the FX-recipe framework within recent history (evidenced by the `converter.py` docstring explicitly handling `"Torch 2.6/2.7 validates reshape's shape..."` compatibility code, i.e. code written against very recent PyTorch releases). **Actively maintained, and specifically actively maintained in the ann2snn area.**

---

## 9. Published/community comparisons found

**Direct empirical comparison of SNN Toolbox vs. SpikingJelly on the same network**: **NOT FOUND.** No paper, preprint, or blog post located that converts one trained ANN through both tools and reports the resulting SNN accuracies side by side.

Adjacent evidence gathered:
- SpikingJelly's own docs report **within-framework** comparisons (its legacy scalar RobustNorm vs. its own current LTB recipe) — see the ResNet-18/ImageNet table in §2 — showing large internal divergence.
- GitHub issues on the SpikingJelly repo (`fangwei123456/spikingjelly#259`, `#289`) document users getting poor ann2snn accuracy (e.g., VGG-16/CIFAR-10 dropping from 94% ANN to 71-76% SNN at low T, or a converted VGG-16/ImageNet model collapsing to 0.1% accuracy at T=4) and being told by maintainers that architecture choices (avg-pool vs max-pool) and larger T are the fix — useful as qualitative evidence that ann2snn conversion accuracy is highly sensitive to exactly the axes flagged above (normalization granularity, T, pooling type), but not a controlled comparison against SNN Toolbox.
- A 2025 conference paper (Thienbutr & Massagram, ICSEC 2025, DOI 10.1109/icsec67360.2025.11298123) benchmarks SpikingJelly-trained LIF SNNs against ANNs on MNIST — this is a directly-trained-SNN study, not an ann2snn conversion comparison, and does not involve SNN Toolbox.

**Conclusion for this axis**: the equivalence claim has apparently never been empirically tested by a third party. The author's claim is untested folklore, not a documented result.

---

## 10. Half 2 — deployment reach: named live toolchains, evaluated route by route

### Route A: SpikingJelly → NxTF → physical Loihi 1

1. **NxTF's input format**: NxTF "inherits from the Keras Model and Layer interface" (Rueckauer et al., arXiv:2101.04261 / ACM JETC 2022 — direct quote: *"This objective is achieved by inheriting from the Keras Model and Layer interface and providing a specialized DNN compiler."*). It is a TensorFlow/Keras-native compiler layered on Intel's proprietary NxSDK. SpikingJelly is PyTorch. **No generic PyTorch→NxTF bridge exists**; the only bridge that exists is the one built specifically for SNN Toolbox (`intel-nrc-ecosystem/models/nxsdk_modules_ncl/snntoolbox`, referenced directly in the NxTF paper: *"For convenience we developed an interface between NxTF and a common conversion software, the SNN toolbox."*). That interface is SNN-Toolbox-specific glue code, not a general Keras/NxTF adapter a SpikingJelly user could reuse without rewriting it against SpikingJelly's own module tree.
2. **Is a PyTorch→ONNX→Keras path a real option?** NOT FOUND as a documented, working path for this purpose anywhere in the sources retrieved; ONNX→Keras conversion is not a standard, reliably-lossless operation for arbitrary architectures and nobody in this ecosystem documents doing it for NxTF. This would be original engineering, not a supported feature.
3. **Is NxSDK/NxTF still obtainable?** The `intel-nrc-ecosystem/models` GitHub repo (which hosts the NxTF↔SNN-Toolbox bridge) carries a blanket **"DISCONTINUATION OF PROJECT"** notice: *"This project will no longer be maintained by Intel... Intel no longer accepts patches to this project."* Separately, Intel's own current INRC guidance (Confluence, "Access Intel Loihi Hardware") states: *"As of 2022, INRC members should use the open-source Lava framework to develop and evaluate spiking neural networks for Loihi 2. Older NxSDK models should be easily re-implemented in Lava."* This is Intel directing its own community away from NxSDK/NxTF since 2022, independent of anything to do with SpikingJelly.
4. **Does NxTF run on Loihi 2?** NOT FOUND — no source located states NxTF supports Loihi 2; every official signal (the 2022 INRC guidance above) points users to Lava instead for Loihi 2, treating NxTF/NxSDK as a Loihi-1-era, now-superseded toolchain.

**Route A verdict: BLOCKED**, on at least three independent, compounding grounds: (a) a framework-boundary blocker (Keras-native compiler, no PyTorch bridge exists for SpikingJelly specifically), (b) the specific software (`intel-nrc-ecosystem/models`) is marked discontinued by Intel, (c) Intel's own community guidance since 2022 has already redirected users to Lava, and Loihi 1 itself is superseded hardware not the current INRC access target. None of these are within Master's-thesis scope to fix — (a) alone would mean writing and validating a full PyTorch→NxTF compiler bridge, and (b)/(c) require access to hardware/software Intel has stated it no longer supports.

### Route B: SpikingJelly → `lava_exchange` → Lava → Loihi 2

5. **Soft-reset workaround inside SpikingJelly/Lava**: `lava_exchange.py` hard-codes the rejection (`raise ValueError("lava only supports for v_reset == 0!")`, repeated at 5 call sites, plus a separate `assert v_reset == 0.0` for `CubaLIFNode`) with **no override parameter and no documented two-compartment or custom-`ProcessModel` workaround found in either the SpikingJelly source or the Lava tutorial/API docs retrieved** (`lava.proc.lif` exposes `LIFReset`, but that process resets state *periodically on a fixed interval*, not *subtractively on spike* — a different feature entirely, not a subtractive-reset neuron). Lava's `ProcessModel` mechanism is explicitly extensible (a user can write a custom `PyLoihiProcessModel` with arbitrary `run_spk()` dynamics, as shown in Lava's own tutorial code), so a subtractive-reset neuron *could* be hand-written — this is architecturally feasible and within the scope of a thesis-level software contribution — but it does not exist today in either codebase, and the coordinator's claim of a "doubling neuron count" documented workaround was **NOT FOUND** in any source reached in this research; it may exist in NxTF-adjacent Loihi literature not indexed by these searches, but nothing in the SpikingJelly or Lava documentation retrieved describes it.
6. **`lava_exchange` operator coverage**: from `lava_exchange.py`'s explicit `isinstance` dispatch, only `nn.Linear`, `nn.Conv2d`, `nn.AvgPool2d` (wrapped as `SumPool2d`), and `nn.Flatten` are handled; anything else raises `ValueError(type(net[i]))` / `NotImplementedError(type(net[i]))`. **A VGG would hit this immediately if it uses `nn.MaxPool2d`** (VGG's canonical pooling); **a ResNet would hit this at every residual add** (no elementwise-add / skip-connection handling found in the operator dispatch checked) and at every `BatchNorm2d` not already fused away.
7. **Does archived Lava still work against live Loihi 2 hardware via INRC?** Partially confirmed, partially NOT FOUND. Confirmed: Lava's own README states Loihi 1/2 access is exclusively through INRC membership (*"Loihi 1 and 2 research systems are currently not available commercially... join the INRC"*), and INRC's Confluence "Access Intel Loihi Hardware" page (still live) describes an active Neuromorphic Research Cloud and on-site loan program for **Loihi 2**, gated behind a research proposal and participation agreement. NOT FOUND: whether the *archived* Lava codebase (frozen 2026-05-13, "Intel will not provide or guarantee development of or support for this project... Patches to this project are no longer accepted") continues to be the software INRC issues to new members, or whether INRC has already migrated to the "new SDK" Intel's archival notice promises ("developing the next-generation Loihi architecture and SDK... stay tuned"). Either way, the software stack a new user would be handed is in flux and its relationship to today's `lava_exchange` code is uncertain.

**Route B verdict: BLOCKED at the reset-semantics component specifically**, with a compounding, separate operator-coverage blocker for any non-trivial CNN (VGG/ResNet). Writing a custom subtractive-reset `ProcessModel` for Lava is *architecturally* within thesis scope (Lava's `ProcessModel` API is designed for exactly this kind of extension) — but reaching *physical silicon* additionally requires INRC hardware access, which is gated, proposal-based, not guaranteed, and now sits behind a software stack (Lava) that Intel has explicitly stopped supporting as of 13 May 2026. That access gate is outside thesis scope: it cannot be secured by engineering effort alone, and its terms are currently unclear even to well-resourced groups.

### Comparator: Sinabs → `DynapcnnNetwork` → `samna` → Speck / DYNAP-CNN

This is a structurally different toolchain (not a SpikingJelly export path at all), but it is the one live route found that preserves reset-by-subtraction end to end without contradiction:

- `sinabs.from_torch.from_model(...)` signature (from `sinabs.readthedocs.io/main/api/from_torch.html`):
  ```
  from_model(model, ..., reset_fn: Callable = MembraneSubtract(subtract_value=None), ...)
  ```
  and the underlying `IAF` layer constructor (`sinabs/layers/iaf.py`):
  ```python
  def __init__(self, spike_threshold=..., reset_fn: Callable = MembraneSubtract(), ...):
  ```
  **Soft reset (reset-by-subtraction) is Sinabs's own default**, not an opt-in.
- The Speck chip natively implements both reset modes, selected by a boolean hardware register (`samna_config.cnn_layers[i].return_to_zero`), and Sinabs's own docs explicitly instruct users converting from ANNs to pick subtraction: *"If you use an ANN-to-SNN conversion, then you should choose the second one strategy for resetting membrane-potential"* (`sinabs.readthedocs.io/v3.0.3/speck/faqs/tips_for_training.html`); the chip default is stated to already be the subtract strategy (*"By default, our devkit use the second strategy for membrane potential reset"*).
- Hardware is **commercially available without a gatekeeping research-membership process**: a "Speck Demo Kit" was presold at **$199** (SynSense press material, per elecfans.com coverage of the launch). The primary "Speck Dev Kit" is sold through SynSense's standard sales channel (`sales@synsense.ai`); an exact list price for the Dev Kit itself was **NOT FOUND** in the sources retrieved, but no approval/proposal gate analogous to INRC is described anywhere in the Speck documentation — it is presented as an ordinary purchase.
- Software (`sinabs`, `sinabs-dynapcnn`, `samna`) is `pip install`-able, actively documented (dated manuals through December 2025 found), and not flagged discontinued or archived anywhere in the sources checked.

---

## Bottom line

No live toolchain was found that takes SpikingJelly's own `ann2snn` output to physical neuromorphic silicon while preserving the soft-reset semantics that module itself defaults to: both of SpikingJelly's own export paths (`lava_exchange`, `nir_exchange`) explicitly refuse `v_reset=None`, and the historical Loihi-1 route (NxTF) is Keras-native, discontinued, and was never built to accept SpikingJelly. The Loihi-2 route through Lava is software-extensible in principle (a custom subtractive-reset `ProcessModel` is a scoped, thesis-sized software task) but gated on the hardware-access side by INRC approval and destabilized by Lava's archival on 2026-05-13. The one live, reset-consistent, commercially-purchasable, actively-maintained route to physical silicon for a rate-coded, subtractive-reset converted CNN found in this research does not involve SpikingJelly or Loihi at all: **Sinabs `from_model()` → `DynapcnnNetwork` → `samna` → Speck/DYNAP-CNN**, where subtractive reset is the documented default on both the software and hardware side.

---

## Source list

**SpikingJelly (GitHub, `fangwei123456/spikingjelly`)** — code, type: primary source
- `spikingjelly/activation_based/ann2snn/converter.py` (master) — https://raw.githubusercontent.com/fangwei123456/spikingjelly/master/spikingjelly/activation_based/ann2snn/converter.py
- `spikingjelly/activation_based/ann2snn/modules.py` (master)
- `spikingjelly/activation_based/ann2snn/recipes/local_threshold_balancing.py` (master)
- `spikingjelly/activation_based/ann2snn/recipes/rate_coding.py` (master)
- `spikingjelly/activation_based/ann2snn/recipes/base.py` (master)
- `spikingjelly/activation_based/ann2snn/qcfs.py` (master)
- `spikingjelly/activation_based/neuron/integrate_and_fire.py` (master)
- `spikingjelly/activation_based/lava_exchange.py` (master)
- `spikingjelly/activation_based/nir_exchange/to_nir.py`, `from_nir.py` (master)
- `spikingjelly/activation_based/lynxi_exchange.py` (master, existence confirmed, not deeply audited)
- Legacy branch `0.0.0.0.14`: `ann2snn/converter.py`, `ann2snn/modules.py`, `ann2snn/utils.py` — https://raw.githubusercontent.com/fangwei123456/spikingjelly/0.0.0.0.14/...
- Repo metadata via GitHub API (`api.github.com/repos/fangwei123456/spikingjelly`, `/branches`, `/releases`, `/tags`, `/contents/...`) — type: primary source (repo metadata)
- ann2snn tutorial — https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/ann2snn.html — type: vendor documentation
- Legacy tutorial (branch 0.0.0.0.4) — https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.4/clock_driven_en/5_ann2snn.html — type: vendor documentation
- Issue #259 "SNN accuracy is less as compared to ANN accuracy" — https://github.com/fangwei123456/spikingjelly/issues/259 — type: community/issue tracker
- Issue #289 "performance degradation of vgg16 imagenet conversion model" — https://github.com/fangwei123456/spikingjelly/issues/289 — type: community/issue tracker

**SNN Toolbox (GitHub, `NeuromorphicProcessorProject/snn_toolbox`)** — code, type: primary source
- `snntoolbox/conversion/utils.py` — https://raw.githubusercontent.com/NeuromorphicProcessorProject/snn_toolbox/master/snntoolbox/conversion/utils.py
- `snntoolbox/simulation/backends/inisim/temporal_mean_rate_tensorflow.py`
- `snntoolbox/config_defaults`
- `snntoolbox/parsing/model_libs/keras_input_lib.py`
- Repo metadata / releases / commits via GitHub — type: primary source
- Docs — https://snntoolbox.readthedocs.io/en/latest/index.html, `/guide/intro.html` — type: vendor documentation

**Lava / Intel neuromorphic ecosystem** — type: primary source (repo status) + vendor documentation
- lava-nc/lava, lava-dl, lava-dnf, lava-docs repo status (archived 2026-05-13) — https://github.com/lava-nc/lava
- Lava ProcessModel tutorials — https://lava-nc.org/lava/notebooks/in_depth/tutorial02_processes.html, tutorial03_process_models.html
- `lava.proc.lif` API docs — https://lava-nc.org/lava/lava.proc.lif.html
- INRC "Access Intel Loihi Hardware" — https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1810432001 — type: vendor documentation
- INRC "Join the INRC" — https://intel-ncl.atlassian.net/wiki/spaces/INRC/pages/1784807425/Join+the+INRC
- INRC service-interruption blog post (2022-11-09) — https://intel-ncl.atlassian.net/wiki/spaces/INRC/blog/2022/11/09/1845133313/...
- `intel-nrc-ecosystem/models` (discontinued) — https://www.github.com/intel-nrc-ecosystem/models
- NxTF paper — Rueckauer, Bybee, Goettsche, Singh, Mishra, Wild, "NxTF: An API and Compiler for Deep Spiking Neural Networks on Intel Loihi," arXiv:2101.04261 / ACM JETC 2022, https://doi.org/10.1145/3501770 — type: peer-reviewed paper
- nengo-zoo discussion on NengoLoihi maintenance status — https://github.com/nengo/nengo-zoo/discussions/1339 — type: community

**NIR (Neuromorphic Intermediate Representation)** — type: peer-reviewed paper + docs
- Nature Communications 2024, "Neuromorphic intermediate representation: A unified instruction set..." — https://www.nature.com/articles/s41467-024-52259-9
- NIR primitives docs — https://neuroir.org/docs/primitives/
- neuromorphs/NIR repo — https://github.com/neuromorphs/NIR
- emergentmind NIR summary — https://www.emergentmind.com/topics/neuromorphic-intermediate-representation-nir — type: secondary/summary

**Sinabs / SynSense (Speck, DYNAP-CNN)** — type: vendor documentation + code
- `sinabs.from_torch.from_model` API docs — https://sinabs.readthedocs.io/main/api/from_torch.html
- `sinabs/layers/iaf.py` source — https://sinabs.readthedocs.io/main/_modules/sinabs/layers/iaf.html
- `sinabs/activation/reset_mechanism.py` source — https://sinabs.readthedocs.io/1.2.8/_modules/sinabs/activation/reset_mechanism.html
- Speck reset-mechanism FAQ — https://sinabs.readthedocs.io/v3.0.3/speck/faqs/tips_for_training.html
- Speck Dev Kit Manual (PDF, 2024-12) — https://www.synsense.ai/wp-content/uploads/2024/12/Speck-Dev-Kit-Manual.pdf
- Speck Demo Kit launch / $199 presale price — https://www.elecfans.com/d/2106374.html — type: vendor press (Chinese-language trade press)
- GitHub — https://github.com/synsense/sinabs

**Rockpool / Xylo (SynSense)** — type: peer-reviewed / preprint + vendor docs
- Deployment pipeline paper — https://arxiv.org/html/2412.11047v1
- Rockpool Xylo quick-start docs — https://rockpool.ai/devices/quick-xylo/deploy_to_xylo.html, https://rockpool.ai/devices/xylo-overview.html
- Original Rockpool/Xylo paper — https://export.arxiv.org/pdf/2208.12991v3.pdf

**Other**
- Thienbutr & Massagram, "Benchmarking SpikingJelly-Based SNNs Against Conventional ANNs: An MNIST Case Study on Accuracy and Synops," ICSEC 2025, DOI 10.1109/icsec67360.2025.11298123 — type: peer-reviewed paper (conference)
