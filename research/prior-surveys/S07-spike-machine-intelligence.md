# S07. Towards Spike-Based Machine Intelligence With Neuromorphic Computing

## Identity and retrieval

- **Citation:** K. Roy, A. Jaiswal, and P. Panda, “Towards spike-based machine intelligence with neuromorphic computing,” *Nature*, vol. 575, pp. 607-617, 2019, doi: 10.1038/s41586-019-1677-2.
- **Source type:** Peer-reviewed perspective/review.
- **Retrieval status:** `verified`. The complete 11-page publisher PDF was inspected on 2026-09-16.
- **Inspected local PDF:** `/Users/hamza/Downloads/papers-review/s41586-019-1677-2.pdf`.
- **Inspected URLs:** <https://www.nature.com/articles/s41586-019-1677-2>; <https://doi.org/10.1038/s41586-019-1677-2>.

## Assessment

**Scope.** The article connects SNN models and learning methods to digital, mixed-signal, and emerging-device hardware. Its central concern is algorithm-hardware co-design for energy-efficient machine intelligence.

**Organizing taxonomy.** The discussion moves from SNN representation and learning to hardware realization. The algorithmic branch separates conversion-based learning from direct spike-based learning. The hardware branch separates GPU execution, large-scale neuromorphic chips, beyond-von-Neumann devices, and cross-layer co-design.

**Strongest explanatory contribution.** The article explains why an SNN method cannot be evaluated independently of its execution substrate. It relates conversion error and latency to rate-based execution, then relates device variation, limited precision, interconnect limits, and analog peripheral cost to accuracy and efficiency.

**Deployment depth.** The hardware treatment is substantial. It explains Neurogrid, TrueNorth, Loihi, address-event routing, networks-on-chip, and memristive crossbars. It does not trace one trained network through a named software stack, mapper, chip configuration, and measurement protocol.

**Material omissions.** Software frameworks are only named in passing. Compiler and mapping toolchains, interchange formats, claim-level evidence classes, and a reproducible end-to-end deployment route are absent.

**Verification limits.** Every article page, figure, and caption in the supplied publisher PDF was inspected. No supplementary material is embedded in the file. The article is a perspective rather than a systematic review, so its selected examples should not be read as an exhaustive platform or application catalog.

| Axis | Score | Basis | Locator |
|---|---|---|---|
| A | partial | LIF dynamics, Hodgkin-Huxley, refractory behavior, and STDP are explained, but neuron and synapse models are not surveyed systematically. | Nature pp. 608-610; Fig. 3 |
| B | partial | Temporal processing, rate coding, rank-order coding, event sensors, and address-event communication are explained. Decoding choices and a broader code taxonomy are not developed. | Nature pp. 608-610 and 613; Figs. 3d and 5b |
| C | full | The learning section distinguishes conversion, supervised spike-based backpropagation, local STDP, hybrid local-global learning, and reinforcement-learning directions, including their principal limitations. | Nature pp. 610-612; Fig. 4 |
| D | partial | A dedicated subsection explains weight rescaling and normalization, ANN-SNN functional mismatches, firing-rate calibration, accuracy loss, and the latency cost of long inference windows. It is not a comprehensive conversion taxonomy. | Nature p. 610, “Conversion-based approaches” |
| E | mentioned | TensorFlow is named for ANN training, while PyTorch and Caffe appear in the historical timeline. SNN framework capabilities are not compared. | Nature pp. 609-610; Fig. 2 |
| F | none | No compiler or hardware-mapping toolchain is described. | Full-text review, Nature pp. 607-615 |
| G | none | No model interchange representation is described. Address-event representation is treated as spike communication, not model interchange. | Full-text review, especially Nature p. 613 and Fig. 5b |
| H | full | The hardware half compares GPU execution, Neurogrid, TrueNorth, Loihi, address-event routing, networks-on-chip, in-memory computing, and several nonvolatile device families. | Nature pp. 612-615; Figs. 5-6 |
| I | partial | The article identifies failures across the ANN-to-SNN and algorithm-to-device boundaries, including sign and firing-rate mismatch, long simulation windows, process variation, crossbar nonidealities, converter cost, and limited precision. It does not provide a software-edge or cross-platform semantic taxonomy. | Nature p. 610 and pp. 614-615, “Conversion-based approaches” and “Algorithm-hardware codesign” |
| J | none | The article calls for better datasets and metrics but does not distinguish physical measurement, simulation, and analytical or operation-count estimates when assessing claims. | Nature p. 609; full-text review |
| K | partial | Vision, robotics, recognition, sequential processing, and control examples are connected to reported accuracy or efficiency results, but there is no structured catalog of measured deployments. | Nature pp. 609 and 611-613 |
| L | none | Algorithms and hardware are connected conceptually, but no case study traces a trained network through conversion, software, mapping, physical execution, and measurement. | Full-text review, Nature pp. 607-615 |
