# S10. Training Spiking Neural Networks Using Lessons From Deep Learning

## Identity and retrieval

- **Citation:** J. K. Eshraghian *et al.*, “Training Spiking Neural Networks Using Lessons From Deep Learning,” *Proceedings of the IEEE*, vol. 111, no. 9, pp. 1016-1054, 2023, doi: 10.1109/JPROC.2023.3308088.
- **Source type:** Peer-reviewed tutorial/review.
- **Retrieval status:** `verified`. Substantive IEEE text, including article structure and technical sections, was inspected on 2026-09-16.
- **Inspected URLs:** <https://doi.org/10.1109/JPROC.2023.3308088>; <https://ieeexplore.ieee.org/document/10223685>.

## Assessment

**Scope.** Neuron dynamics, encoding, objectives, and gradient-based training. **Organizing taxonomy.** From spike/neuron fundamentals to encoding, optimization, and gradient approaches. **Strongest explanatory contribution.** It explains direct gradient training, surrogate gradients, spike-time gradients, and ANN-to-SNN conversion in a unified training perspective. **Deployment depth.** Application context only. **Material omissions.** No compiler, interchange, cross-platform semantic, or evidence-taxonomy coverage. **Verification limits.** This is a tutorial focused on learning rather than deployment evaluation.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | partial | A spiking neuron model is derived from first principles. | Sec. II |
| B | full | Encoding strategies and their learning effects are treated explicitly. | Sec. III |
| C | full | Gradient, surrogate-gradient, spike-time, and BPTT training are developed. | Sec. IV; Fig. 9-10 |
| D | partial | Shadow-ANN conversion is explained as one path around dead neurons. | Sec. IV, “Backpropagation Using Spike Times” |
| E | mentioned | Deep-learning tooling motivates the tutorial but frameworks are not compared. | Introduction; Sec. IV |
| F | none | No compiler or mapping-toolchain review is provided. | Article overview; Secs. II-IV |
| G | none | No interchange format is treated. | Article overview; Secs. II-IV |
| H | mentioned | Specialized hardware motivates SNNs, without platform taxonomy. | “Neuromorphic Systems in the Wild” |
| I | none | No platform-boundary semantic taxonomy is provided. | Article overview; Secs. II-IV |
| J | none | No physical-versus-proxy evidence-classification scheme is provided. | Article overview; Secs. II-IV |
| K | mentioned | Application domains are enumerated, not reviewed as measured deployment evidence. | “Neuromorphic Systems in the Wild” |
| L | none | No end-to-end deployment route is traced. | Article overview; “Neuromorphic Systems in the Wild” |
