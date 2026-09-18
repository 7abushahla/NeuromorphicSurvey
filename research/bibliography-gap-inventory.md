# Task 6 canonical bibliography gap inventory

> Provenance. Generated from the pre-migration bibliography and canonical source-registry state on 2026-09-16. Promoted from `.superpowers/sdd/2026-09-16-neuromorphic-survey-research-evidence/implementer-task-6.md`, SHA-256 `b491709911e450dc7740252f150e8363f8daa55bbdc83481dec0e64687c2162d`.

Generated deterministically from the pre-migration worktree state. The source implementer report was ignored by Git and made no production changes.

## Scope and result

- Site HTML fragments scanned: 14
- Fragment reference records: 424
- Distinct fragment reference keys: 394
- Distinct raw cited keys: 375
- Distinct cited legacy targets after the current `refmap.json`: 294
- Existing generated BibTeX entries: 304
- Existing alias-map entries: 90
- Canonical source-registry records: 246
- Uniquely matched cited targets: 184
- Ambiguous cited targets: 0
- Unresolved cited targets: 110
- Unresolved distinct-work groups under exact DOI, URL, or title identity: 108
- Explicit internal analysis targets: 3
- External unresolved distinct works: 105
- Cited targets missing from the existing BibTeX file: 0

Unique-match methods were applied in this order. Registry ID, canonical key, or explicit plain alias; current refmap propagation from an explicit registry alias; normalized DOI; normalized URL; normalized title. No fuzzy title match and no inferred metadata were used.

Resolved target counts by first successful method are as follows.

- registry key or explicit alias: 65
- normalized DOI: 74
- normalized URL: 32
- normalized title: 13

The zero-unresolved Task 6 gate is not currently satisfiable without extending the canonical registry. Generating from fragment prose would create a second metadata authority. Generating placeholder publication fields would fabricate metadata.

## Internal analysis classification

| Legacy target | Classification | Required correction |
|---|---|---|
| `A18-Research` | analysis-only | Internal source-level synthesis. The registry contains the likely canonical candidate `a18-sourcecode-comparison`, but exact DOI, URL, and title matching does not bind the legacy key. Treat as analysis-only pending an explicit alias. |
| `a14-application-survey` | analysis-only | Internal application survey conducted for this work. The fragment already says `analysis conducted for this survey`. It is not an external publication. |
| `a17-two-populations` | analysis-only | Internal citation-direction and toolchain audit conducted for this work. The fragment already says `analysis conducted for this survey`. It is not an external publication. |

## Unresolved targets grouped into distinct works

Grouping uses transitive exact equality of normalized DOI, normalized URL, or normalized title. There are two multi-key duplicate groups and 106 singleton groups. The three internal analysis groups are labeled separately from 105 external-source gaps.

| Group | Legacy target(s) | Class | Exact identity evidence | Existing generated title(s) |
|---:|---|---|---|---|
| G001 | `A18-Research` | analysis-only | title=`source level comparison of the snn toolbox and spikingjelly ann2snn conversion pipelines by direct inspection of both codebases and their documentation` | Source-level comparison of the SNN Toolbox and SpikingJelly ann2snn conversion pipelines, by direct inspection of both codebases and their documentation |
| G002 | `Akopyan15-TrueNorth` | external registry gap | title=`truenorth design and tool flow of a 65 mw 1 million neuron programmable neurosynaptic chip` | TrueNorth: Design and Tool Flow of a 65 mW 1 Million Neuron Programmable Neurosynaptic Chip |
| G003 | `BindsNET18` | external registry gap | doi=`10.3389/fninf.2018.00089` | BindsNET: A Machine Learning-Oriented Spiking Neural Networks Library in Python |
| G004 | `BrainChip-AKD1000Brief` | external registry gap | url=`https://brainchip.com/wp-content/uploads/2025/08/Akida-AKD1000-SoC-Product-Brief-V2.3-Aug.25.pdf` | BrainChip, AKD1000 SoC Product Brief V2.3 |
| G005 | `BrainChip-AKD1500Brief` | external registry gap | url=`https://brainchip.com/wp-content/uploads/2025/11/AKD1500-Product-Brief-V2.4-Oct.25.pdf` | BrainChip, AKD1500 Product Brief V2.4 and commercial-availability press release |
| G006 | `CNN2SNN-Source` | external registry gap | title=`author s local copy of brainchip s cnn2snn 2 19 1 source cnn2snn quantizeml outputs py set output v1 variables and activations py parse relu v1` | Author's local copy of BrainChip's cnn2snn 2.19.1 source, cnn2snn/quantizeml/outputs.py (set_output_v1_variables) and activations.py (parse_relu_v1) |
| G007 | `EBRAINS-Access` | external registry gap | url=`https://wiki.ebrains.eu/bin/view/Collabs/neuromorphic/Getting\ access` | Getting access to the NMC systems BrainScaleS and SpiNNaker |
| G008 | `EBRAINS-BSS` | external registry gap | url=`https://ebrains.eu/data-tools-services/tools/brainscales` | EBRAINS, "BrainScaleS" platform page |
| G009 | `HBP-Guidebook` | external registry gap | url=`https://electronicvisions.github.io/hbp-sp9-guidebook/using_the_platform.html` | HBP Neuromorphic Computing Platform Guidebook |
| G010 | `Innatera-EETimes` | external registry gap | url=`https://eetimes.com/innatera-productizes-snn-accelerator-as-neuromorphic-microcontroller` | Innatera Productizes SNN Accelerator As 'Neuromorphic Microcontroller' |
| G011 | `Innatera-Talamo` | external registry gap | url=`https://innatera.com/software-and-tools` | Innatera, Talamo SDK page |
| G012 | `Lynxi-HP300` | external registry gap | url=`https://lynxi.com/ka2003/21.html` | Lynxi, HP300 product page / PDF datasheet |
| G013 | `Lynxi-KA200` | external registry gap | url=`https://lynxi.com/lq2001/18.html` | Lynxi, KA200 product page |
| G014 | `NIR-Porting`, `nir-porting-guide` | external registry gap | url=`https://neuroir.org/docs/porting-nir` | NIR project, porting-to-hardware guide; Porting to a New Platform |
| G015 | `NIR-Primitives` | external registry gap | url=`https://neuroir.org/docs/primitives` | NIR project, primitives documentation |
| G016 | `NengoDL-Rasmussen19` | external registry gap | doi=`10.48550/arxiv.1805.11144` | NengoDL: Combining deep learning and neuromorphic modelling methods |
| G017 | `NengoLoihi-Docs` | external registry gap | url=`https://nengo.ai/nengo-loihi/overview.html` | NengoLoihi documentation, overview and hardware/installation guides |
| G018 | `Norse-Docs` | external registry gap | url=`https://norse.github.io/norse/auto_api/norse.torch.functional.lif.html` | Norse docs, norse.torch.functional.lif and norse.torch.module.lif |
| G019 | `PyNN-Docs` | external registry gap | url=`https://pynn.readthedocs.io/en/latest/introduction.html` | Introduction |
| G020 | `PynnBSS2-Docs` | external registry gap | url=`https://electronicvisions.github.io/documentation-brainscales2/latest/pynn-brainscales/index.html` | PyNN for BrainScaleS-2 documentation |
| G021 | `SJ-ANN2SNNDocs` | external registry gap | url=`https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/ann2snn.html` | SpikingJelly docs, "ANN2SNN" tutorial |
| G022 | `SJ-LavaExchangeSource`, `jelly-lava-source` | external registry gap | url=`https://spikingjelly.readthedocs.io/zh-cn/0.0.0.0.12/_modules/spikingjelly/clock_driven/lava_exchange.html` | SpikingJelly lava_exchange.py module source; SpikingJelly lava_exchange module source (v_reset == 0 hard constraint, operator dispatch) |
| G023 | `SJ-NIRExchangeSource` | external registry gap | title=`spikingjelly nir exchange to nir py module source hard reset helper` | SpikingJelly nir_exchange/to_nir.py module source (_hard_reset helper) |
| G024 | `SJ-NeuronDocs` | external registry gap | url=`https://spikingjelly.readthedocs.io/zh-cn/latest/tutorials/en/neuron.html` | SpikingJelly docs, "Neuron" tutorial |
| G025 | `Shidqi22-SENECAThesis` | external registry gap | url=`http://resolver.tudelft.nl/uuid:3b6a47f2-bde5-4652-8e6a-8fb6155a4740` | Benchmarking and Algorithm Optimization for SENeCA: A RISC-V-based Neuromorphic Processor |
| G026 | `Sinabs-FromTorch` | external registry gap | url=`https://sinabs.readthedocs.io/main/api/from_torch.html` | Sinabs API reference, sinabs.from_torch.from_model |
| G027 | `Sinabs-TrainingTips` | external registry gap | url=`https://sinabs.readthedocs.io/v3.0.3/speck/faqs/tips_for_training.html` | Troubleshooting and Tips |
| G028 | `SpiNNcloud24-PR` | external registry gap | url=`https://newswire.com/news/spinncloud-systems-announces-first-commercially-available-neuromorphic-22325275` | SpiNNcloud Systems Announces First Commercially Available Neuromorphic Supercomputer |
| G029 | `Spyx-Docs` | external registry gap | url=`https://spyx.readthedocs.io/en/latest` | Spyx documentation / GitHub README |
| G030 | `SynSense-SpeckDatasheet` | external registry gap | url=`https://synsense.ai/wp-content/uploads/2023/06/Speck-devkit-datasheet.pdf` | SynSense, Speck Dev Kit Datasheet |
| G031 | `SynSense-SpeckOverview` | external registry gap | url=`https://sinabs.readthedocs.io/main/speck/overview.html` | SynSense/Sinabs, "Overview" (Speck) |
| G032 | `Thorpe98-RankOrder` | external registry gap | title=`rank order coding` | Rank Order Coding |
| G033 | `Turner22-mlGeNN` | external registry gap | doi=`10.1088/2634-4386/ac5ac5` | mlGeNN: accelerating SNN inference using GPU-enabled neural networks |
| G034 | `a14-application-survey` | analysis-only | title=`survey of approximately twenty published neuromorphic application results classified by compute platform and by evidence class conducted for this work` | Survey of approximately twenty published neuromorphic application results, classified by compute platform and by evidence class, conducted for this work |
| G035 | `a17-two-populations` | analysis-only | title=`audit of citation direction toolchain release history and shared artifacts across the qcfs lineage conversion literature and the hardware deployment literature conducted for this work` | Audit of citation direction, toolchain release history, and shared artifacts across the QCFS-lineage conversion literature and the hardware-deployment literature, conducted for this work |
| G036 | `ace-snn2022` | external registry gap | doi=`10.3389/fnins.2022.815258` | ACE-SNN: Algorithm-Hardware Co-Design of Energy-Efficient and Low-Latency Deep Spiking Neural Networks for 3D Image Recognition |
| G037 | `akida-hw-constraints` | external registry gap | url=`https://doc.brainchipinc.com/user_guide/hardware/1.0.html` | BrainChip Akida hardware constraints documentation |
| G038 | `akida-story-2016` | external registry gap | url=`https://akida.io/story` | The Brainchip Story, 2016 to December 2020 |
| G039 | `arfa-2025-spinnaker2` | external registry gap | doi=`10.1109/nice65350.2025.11065119` | Efficient Deployment of Spiking Neural Networks on SpiNNaker2 for DVS Gesture Recognition Using Neuromorphic Intermediate Representation |
| G040 | `bellec2018` | external registry gap | title=`long short term memory and learning to learn in networks of spiking neurons` | Long Short-Term Memory and Learning-to-Learn in Networks of Spiking Neurons |
| G041 | `bhattacharjee-2023-hardware` | external registry gap | doi=`10.48550/arxiv.2309.03388` | Are SNNs Truly Energy-efficient? A Hardware Perspective |
| G042 | `brainscales-accel` | external registry gap | doi=`10.48550/arxiv.2003.11996` | Accelerated Analog Neuromorphic Computing |
| G043 | `bsnn-2022` | external registry gap | doi=`10.3389/fnins.2022.991851` | BSNN: Towards faster and better conversion of artificial neural networks to spiking neural networks with bistable neurons |
| G044 | `cerco-spikenet-docs` | external registry gap | url=`https://cerco.cnrs.fr/pagesp/arno/spikenet/order.html` | What is order coding |
| G045 | `cnn2snn-source-inspection` | external registry gap | title=`direct inspection of the cnn2snn 2 19 1 toolkit source cnn2snn quantizeml outputs py function set output v1 variables and activations py function parse relu v1` | Direct inspection of the cnn2snn 2.19.1 toolkit source, cnn2snn/quantizeml/outputs.py, function set_output_v1_variables, and activations.py, function parse_relu_v1 |
| G046 | `convlca-2025-lca` | external registry gap | title=`convolutional sparse coding via the locally competitive algorithm on loihi 2` | Convolutional Sparse Coding via the Locally Competitive Algorithm on Loihi 2 |
| G047 | `ding-2021-optimalconv` | external registry gap | doi=`10.24963/ijcai.2021/321` | Optimal ANN-SNN Conversion for Fast and Accurate Inference in Deep Spiking Neural Networks |
| G048 | `eeg-motor-imagery-repo` | external registry gap | title=`combra lab snn eeg github com combra lab snn eeg` | combra-lab/snn-eeg. github.com/combra-lab/snn-eeg |
| G049 | `eetimes-graimatter` | external registry gap | title=`grai matter raises 14m for sparsity driven ai soc` | GrAI Matter Raises $14M for Sparsity-Driven AI SoC |
| G050 | `ettfs-2024` | external registry gap | doi=`10.48550/arxiv.2410.23619` | Efficiently Training Time-to-First-Spike Spiking Neural Networks from Scratch |
| G051 | `galanis-2020-spinnaker` | external registry gap | doi=`10.1109/tcsii.2020.3047425` | Efficient Deployment of Spiking Neural Networks on SpiNNaker Neuromorphic Platform |
| G052 | `gelneuro-2026` | external registry gap | title=`gelneuro 2026 pubdb com paper 2607 05241` | "GelNeuro" (2026). pubdb.com/paper/2607.05241 |
| G053 | `guo-2026-mtsnn-withdrawn` | external registry gap | url=`https://openreview.net/forum?id=4dwAZRr9L5` | Mixed-Timestep Spiking Neural Networks with Temporal Alignment for Ultra-Low Latency Conversion |
| G054 | `guo2021` | external registry gap | doi=`10.3389/fnins.2021.638474` | Neural Coding in Spiking Neural Networks: A Comparative Study for Robust Neuromorphic Systems |
| G055 | `hbp-guidebook` | external registry gap | url=`https://flagship.kip.uni-heidelberg.de/jss/FileExchange/HBPNeuromorphicComputingPlatformGuidebook.pdf` | HBP Neuromorphic Computing Platform Guidebook (BrainScaleS and SpiNNaker access via EBRAINS) |
| G056 | `hodgkin1952` | external registry gap | title=`a quantitative description of membrane current and its application to conduction and excitation in nerve` | A Quantitative Description of Membrane Current and Its Application to Conduction and Excitation in Nerve |
| G057 | `horowitz-2014` | external registry gap | doi=`10.1109/isscc.2014.6757323` | 1.1 Computing's Energy Problem (and what we can do about it) |
| G058 | `ijcai2025negspike` | external registry gap | url=`https://ijcai.org/proceedings/2025/0719.pdf` | A Fast and Accurate ANN-SNN Conversion Algorithm with Negative Spikes |
| G059 | `izhikevich2003` | external registry gap | title=`simple model of spiking neurons` | Simple Model of Spiking Neurons |
| G060 | `jelly-nir-source` | external registry gap | title=`spikingjelly nir exchange to nir py source notimplementederror on soft reset` | SpikingJelly nir_exchange/to_nir.py source (NotImplementedError on soft reset) |
| G061 | `jiang-2025-adaptive-fission` | external registry gap | url=`https://github.com/JiangYizhou16/Adaptive-Fission` | Adaptive Fission |
| G062 | `kelber-2020-spinnaker2sim` | external registry gap | doi=`10.1145/3381755.3381778` | Mapping Deep Neural Networks on SpiNNaker2 |
| G063 | `kim-2020-roc-scnn` | external registry gap | doi=`10.1016/j.neucom.2020.06.107` | Rank order coding based spiking convolutional neural network architecture with energy-efficient membrane voltage updates |
| G064 | `kim-2022-rate-vs-direct` | external registry gap | doi=`10.48550/arxiv.2202.03133` | Rate Coding or Direct Coding: Which One is Better for Accurate, Robust, and Energy-efficient Spiking Neural Networks? |
| G065 | `kria-prophesee-vitisai` | external registry gap | title=`logictronixinc kria prophesee event vitisai` | LogicTronixInc/Kria-Prophesee-Event-VitisAI |
| G066 | `latency-framework2026` | external registry gap | doi=`10.48550/arxiv.2603.23206` | A Latency Coding Framework for Deep Spiking Neural Networks with Ultra-Low Latency |
| G067 | `lava-archived-2026` | external registry gap | title=`lava nc github organization archive banner on lava lava dl lava dnf repositories 2026 github com lava nc lava` | Lava-nc GitHub organization, archive banner on lava, lava-dl, lava-dnf repositories, 2026. github.com/lava-nc/lava |
| G068 | `lava-dl-docs` | external registry gap | url=`https://lava-nc.org/dl.html` | Deep Learning |
| G069 | `lava-dl-readme` | external registry gap | url=`https://github.com/lava-nc/lava-dl/blob/main/README.md` | lava-nc/lava-dl GitHub README, archival notice (13 May 2026) |
| G070 | `liu-2019-facedemo` | external registry gap | title=`live demonstration face recognition on an ultra low power event driven convolutional neural network asic` | Live Demonstration: Face Recognition on an Ultra-Low Power Event-Driven Convolutional Neural Network ASIC |
| G071 | `maass1997` | external registry gap | title=`networks of spiking neurons the third generation of neural network models` | Networks of Spiking Neurons: The Third Generation of Neural Network Models |
| G072 | `moyer-2020-semieng` | external registry gap | url=`https://semiengineering.com/spiking-neural-networks-research-projects-or-commercial-products` | Spiking Neural Networks: Research Projects or Commercial Products? |
| G073 | `narduzzi-2025-eflop` | external registry gap | doi=`10.1088/2634-4386/addee8` | EFLOP: a sparsity-aware metric for evaluating computational cost in spiking and non-spiking neural networks |
| G074 | `nengoloihi-cifar10-example` | external registry gap | url=`https://nengo.ai/nengo-loihi/v1.0.0/examples/cifar10-convnet.html` | NengoLoihi CIFAR-10 convnet example (off-chip input layer) |
| G075 | `neuronflow-2020` | external registry gap | doi=`10.1109/aicas48895.2020.9073999` | NeuronFlow: A Hybrid Neuromorphic-Dataflow Processor Architecture |
| G076 | `pals-2021-eeg-spinnaker` | external registry gap | doi=`10.1109/embc46164.2021.9629621` | Demonstrating the Viability of Mapping Deep Learning Based EEG Decoders to Spiking Networks on Low-powered Neuromorphic Chips |
| G077 | `pehle-2022-bmtk` | external registry gap | doi=`10.3389/fninf.2022.883360` | BMTK-Loihi mapping paper (native hard reset on Loihi). *Frontiers in Neuroinformatics* (2022) |
| G078 | `prophesee-2025-pedestrian` | external registry gap | title=`pedestrian detection with high resolution event cameras` | Pedestrian Detection with High-Resolution Event Cameras |
| G079 | `prophesee-docs-detection` | external registry gap | title=`detection and tracking tutorial` | Detection and Tracking Tutorial |
| G080 | `prophesee-genx320-docs` | external registry gap | title=`prophesee genx320 product catalogue and ridgerun genx320 developer guide prophesee ai ridgerun com` | Prophesee, GenX320 product catalogue and RidgeRun GenX320 developer guide. prophesee.ai; ridgerun.com |
| G081 | `radar-automotive-2026` | external registry gap | url=`https://google.iopscience.iop.org/article/10.1088/2634-4386/ae8694` | Towards real-time neuromorphic radar processing on Loihi 2 |
| G082 | `radar-resonator-2025` | external registry gap | url=`https://iopscience.iop.org/article/10.1088/2634-4386/ae629d` | Energy-efficient radar detection with spiking neural resonators on Loihi 2 |
| G083 | `satcsp-2020` | external registry gap | title=`solving constraint satisfaction problems using the loihi processor` | Solving Constraint Satisfaction Problems Using the Loihi Processor |
| G084 | `serrano-2015-convnets` | external registry gap | doi=`10.1109/iscas.2015.7169169` | ConvNets experiments on SpiNNaker |
| G085 | `shen-2024-cvpr` | external registry gap | url=`https://openaccess.thecvf.com/content/CVPR2024/papers/Shen_Are_Conventional_SNNs_Really_Efficient_A_Perspective_from_Network_Quantization_CVPR_2024_paper.pdf` | Are Conventional SNNs Really Efficient? A Perspective from Network Quantization |
| G086 | `sia-fpga` | external registry gap | doi=`10.48550/arxiv.2410.16298` | SIA hardware-software co-optimized FPGA SNN accelerator (subtractive reset as default) |
| G087 | `sinabs-discretize-api` | external registry gap | url=`https://sinabs.readthedocs.io/main/speck/api/dynapcnn/dynapcnn.html` | Sinabs documentation, discretize/DynapcnnLayer API (BatchNorm is folded automatically by the graph extractor's `merge_bn`, not by the discretize module itself; default MembraneSubtract() reset) |
| G088 | `sinabs-docs-overview` | external registry gap | title=`synsense sinabs documentation overview speck and related api discretization pages sinabs readthedocs io` | SynSense/Sinabs documentation, "Overview" (Speck) and related API/discretization pages. sinabs.readthedocs.io |
| G089 | `sinabs-nmnist-tutorial` | external registry gap | url=`https://sinabs.readthedocs.io/v3.1.3/tutorials/nmnist.html` | Sinabs NMNIST quick-start tutorial (bias-as-leak, BN-free architecture convention) |
| G090 | `singh-2021-gesture-snn` | external registry gap | doi=`10.1109/islped52811.2021.9502506` | Gesture-SNN: Co-optimizing accuracy, latency and energy of SNNs for neuromorphic vision sensors |
| G091 | `snnTorch-Docs` | external registry gap | url=`https://snntorch.readthedocs.io/en/latest/snn.neurons_leaky.html` | snnTorch docs, snn.Leaky API reference and Tutorial 2 |
| G092 | `snntoolbox-docs` | external registry gap | url=`https://snntoolbox.readthedocs.io/en/latest` | SNN Toolbox documentation, introduction and simulation API (operator coverage, output coding schemes) |
| G093 | `snntoolbox-issues` | external registry gap | url=`https://github.com/NeuromorphicProcessorProject/snn_toolbox/issues` | SNN Toolbox GitHub issue tracker, issues #142 and #143 (2024) |
| G094 | `snntorch-pr-426` | external registry gap | url=`https://github.com/jeshraghian/snntorch/pull/426` | snnTorch GitHub pull request #426, reset-mechanism refactor (subtract vs. zero confusion) |
| G095 | `speck-datasheet` | external registry gap | title=`speck dev kit manual datasheet 2023 2025 revisions` | Speck Dev Kit Manual / Datasheet, 2023-2025 revisions |
| G096 | `spiker-2022` | external registry gap | doi=`10.48550/arxiv.2201.06993` | Spiker: an FPGA-optimized Hardware accelerator for Spiking Neural Networks |
| G097 | `spiker-plus-fpga` | external registry gap | doi=`10.48550/arxiv.2401.01141` | Spiker+ FPGA SNN accelerator generator (native subtractive reset) |
| G098 | `spikingjelly-issue543` | external registry gap | title=`limitations when deploying snns to loihi` | Limitations when deploying SNNs to loihi |
| G099 | `spikingjelly-loihi2-2026` | external registry gap | title=`real time frame and event based object detection with spiking neural networks on edge neuromorphic hardware design deployment and benchmark` | Real-Time Frame- and Event-based Object Detection with Spiking Neural Networks on Edge Neuromorphic Hardware: Design, Deployment and Benchmark |
| G100 | `spinnaker-1ms` | external registry gap | title=`spinnaker documentation furber et al` | SpiNNaker documentation / Furber et al |
| G101 | `spinnaker-neuron-lab-manual` | external registry gap | url=`https://spinnakermanchester.github.io/` | Creating New Neuron Models |
| G102 | `swsc2024` | external registry gap | doi=`10.48550/arxiv.2408.17245` | Stepwise Weighted Spike Coding for Deep Spiking Neural Networks |
| G103 | `synsense-speck-gesture-datasheet` | external registry gap | title=`speck gesture recognition` | Speck Gesture Recognition |
| G104 | `thorpe-spikebased` | external registry gap | url=`https://sccn.ucsd.edu/~arno/mypapers/ThorpeSpiking_Neurons.pdf` | Spike-based strategies for rapid processing |
| G105 | `yao-spikedriven` | external registry gap | title=`spike driven transformer meta spikeformer v2` | Spike-driven Transformer / Meta-SpikeFormer V2 |
| G106 | `yoso2020` | external registry gap | doi=`10.48550/arxiv.2006.09982` | You Only Spike Once: Improving Energy-Efficient Deep SNN with Temporal Coding |
| G107 | `zhou-2024-spikformerv2` | external registry gap | doi=`10.48550/arxiv.2401.02020` | Spikformer V2: Join the High Accuracy Club on ImageNet with an SNN Ticket |
| G108 | `zou2023negspike` | external registry gap | doi=`10.1002/aisy.202300383` | Toward a Lossless Conversion for Spiking Neural Networks with Negative-Spike Dynamics |

## Complete cited legacy-target inventory

Aliases include the target and every current `refmap.json` source key found in the fragment reference lists. Match status names the unique canonical key and the deterministic identity mechanism, or records the gap.

| Legacy target | Fragment aliases | Canonical match status |
|---|---|---|
| `A18-Research` | `A18-Research` | UNRESOLVED, analysis-only |
| `ABR-PressRelease` | `ABR-PressRelease` | matched `abr-pressrelease-nengoloihi` by normalized URL |
| `Akopyan15-TrueNorth` | `Akopyan15-TrueNorth` | UNRESOLVED, external registry gap |
| `BIDL-GitHub` | `BIDL-GitHub` | matched `bidl` by normalized URL |
| `BIDL-PMC` | `BIDL-PMC` | matched `bidl-pmc-paper` by normalized URL |
| `BindsNET18` | `BindsNET18` | UNRESOLVED, external registry gap |
| `BrainChip-AKD1000Brief` | `BrainChip-AKD1000Brief` | UNRESOLVED, external registry gap |
| `BrainChip-AKD1500Brief` | `BrainChip-AKD1500Brief` | UNRESOLVED, external registry gap |
| `BrainChip-AkidaUserGuide` | `BrainChip-AkidaUserGuide` | matched `brainchip-akida-user-guide` by normalized URL |
| `BrainChip-CNN2SNNDocs` | `BrainChip-CNN2SNNDocs` | matched `brainchip-cnn2snn-docs` by normalized URL |
| `BrainChip-QuantizeMLDocs` | `BrainChip-QuantizeMLDocs` | matched `brainchip-quantizeml-docs` by normalized URL |
| `CNN2SNN-Source` | `CNN2SNN-Source` | UNRESOLVED, external registry gap |
| `Cassidy13-TNNeuron` | `Cassidy13-TNNeuron`, `truenorth-neuron` | matched `truenorth-neuron-model-doc` by registry key or explicit alias |
| `DeWolf23-NengoArm` | `DeWolf23-NengoArm` | matched `dewolf2023-nengoloihi-arm` by normalized DOI |
| `EBRAINS-Access` | `EBRAINS-Access` | UNRESOLVED, external registry gap |
| `EBRAINS-BSS` | `EBRAINS-BSS` | UNRESOLVED, external registry gap |
| `Esser16-Eedn` | `Esser16-Eedn`, `esser-2016-eedn` | matched `truenorth` by registry key or explicit alias |
| `Frenkel19-ODIN` | `Frenkel19-ODIN` | matched `odin` by normalized DOI |
| `FrenkelIndiveri22-ReckOn` | `FrenkelIndiveri22-ReckOn` | matched `reckon` by normalized DOI |
| `Furber12-SpiNNOverview` | `Furber12-SpiNNOverview` | matched `furber2012-spinnaker` by normalized DOI |
| `HBP-Guidebook` | `HBP-Guidebook` | UNRESOLVED, external registry gap |
| `Innatera-EETimes` | `Innatera-EETimes` | UNRESOLVED, external registry gap |
| `Innatera-Pulsar-PR` | `Innatera-Pulsar-PR` | matched `innatera-pulsar-vendor` by normalized URL |
| `Innatera-Talamo` | `Innatera-Talamo` | UNRESOLVED, external registry gap |
| `IntelBrief-L2` | `IntelBrief-L2`, `intel-2021-loihi2-brief` | matched `loihi2` by registry key or explicit alias |
| `LavaDL-NetX-Docs` | `LavaDL-NetX-Docs` | matched `netx` by normalized URL |
| `LavaDocs-Overview` | `LavaDocs-Overview` | matched `lava-nc-homepage` by normalized URL |
| `LavaGH-Archive` | `LavaGH-Archive` | matched `lava-github-archived` by normalized URL |
| `Li24-FireFlyv2` | `Li24-FireFlyv2` | matched `firefly` by normalized DOI |
| `Lynxi-HP300` | `Lynxi-HP300` | UNRESOLVED, external registry gap |
| `Lynxi-KA200` | `Lynxi-KA200` | UNRESOLVED, external registry gap |
| `NIR-Porting` | `NIR-Porting` | UNRESOLVED, external registry gap |
| `NIR-Primitives` | `NIR-Primitives` | UNRESOLVED, external registry gap |
| `NengoDL-Rasmussen19` | `NengoDL-Rasmussen19` | UNRESOLVED, external registry gap |
| `NengoLoihi-Docs` | `NengoLoihi-Docs` | UNRESOLVED, external registry gap |
| `Norse-Docs` | `Norse-Docs` | UNRESOLVED, external registry gap |
| `Orchard21-Loihi2Sig` | `Orchard21-Loihi2Sig` | matched `orchard2021-loihi2signal` by normalized DOI |
| `Pedersen24-NIR` | `Pedersen24-NIR`, `pedersen-2024-nir` | matched `pedersen-2024-nir` by registry key or explicit alias |
| `Pehle22-BSS2` | `Pehle22-BSS2`, `brainscales-pehle2022`, `pehle-2022-brainscales-multicomp` | matched `bss` by registry key or explicit alias |
| `Pehle22-hxtorchsnn` | `Pehle22-hxtorchsnn` | matched `spilger2022-hxtorchsnn` by normalized DOI |
| `Pei19-Tianjic` | `Pei19-Tianjic` | matched `tianjic` by normalized title |
| `PyNN-Docs` | `PyNN-Docs` | UNRESOLVED, external registry gap |
| `PynnBSS2-Docs` | `PynnBSS2-Docs` | UNRESOLVED, external registry gap |
| `Rhodes18-sPyNNaker` | `Rhodes18-sPyNNaker` | matched `rhodes2018-spynnaker` by normalized DOI |
| `Rockpool-XyloA3Tutorial` | `Rockpool-XyloA3Tutorial` | matched `rockpool-xyloa3-docs` by normalized URL |
| `Rockpool-XyloDeploy` | `Rockpool-XyloDeploy` | matched `rockpool-quickxylo-docs` by normalized URL |
| `Rowley19-SpiNNTools` | `Rowley19-SpiNNTools` | matched `rowley2019-spinntools` by normalized DOI |
| `SJ-ANN2SNNDocs` | `SJ-ANN2SNNDocs` | UNRESOLVED, external registry gap |
| `SJ-GitHub` | `SJ-GitHub` | matched `a18-sourcecode-comparison` by normalized URL |
| `SJ-LavaExchangeSource` | `SJ-LavaExchangeSource` | UNRESOLVED, external registry gap |
| `SJ-NIRExchangeSource` | `SJ-NIRExchangeSource` | UNRESOLVED, external registry gap |
| `SJ-NeuronDocs` | `SJ-NeuronDocs` | UNRESOLVED, external registry gap |
| `SNNToolbox-Docs` | `SNNToolbox-Docs` | matched `toolbox` by normalized URL |
| `SNNToolbox-GitHub` | `SNNToolbox-GitHub` | matched `snn-toolbox-github` by normalized URL |
| `Sawada16-TNEcosystem` | `Sawada16-TNEcosystem` | matched `sawada2016-truenorth-ecosystem` by normalized URL |
| `Scholze26-SpiNN2Chip` | `Scholze26-SpiNN2Chip` | matched `scholze2026-spinnaker2chip` by normalized DOI |
| `Shidqi22-SENECAThesis` | `Shidqi22-SENECAThesis` | UNRESOLVED, external registry gap |
| `Sinabs-Basics` | `Sinabs-Basics` | matched `sinabs` by normalized URL |
| `Sinabs-FromTorch` | `Sinabs-FromTorch` | UNRESOLVED, external registry gap |
| `Sinabs-TrainingTips` | `Sinabs-TrainingTips` | UNRESOLVED, external registry gap |
| `SpiNNcloud24-PR` | `SpiNNcloud24-PR` | UNRESOLVED, external registry gap |
| `Spyx-Docs` | `Spyx-Docs` | UNRESOLVED, external registry gap |
| `Stromatias15-DBN` | `Stromatias15-DBN`, `stromatias-2015-dbn`, `stromatias-2015-spinnaker` | matched `stromatias2015-dbn-spinnaker` by registry key or explicit alias |
| `SynSense-SpeckDatasheet` | `SynSense-SpeckDatasheet` | UNRESOLVED, external registry gap |
| `SynSense-SpeckDevKitManual` | `SynSense-SpeckDevKitManual` | matched `speck-manual` by normalized URL |
| `SynSense-SpeckOverview` | `SynSense-SpeckOverview` | UNRESOLVED, external registry gap |
| `Tang23-SENECA` | `Tang23-SENECA` | matched `seneca` by normalized DOI |
| `Thorpe98-RankOrder` | `Thorpe98-RankOrder` | UNRESOLVED, external registry gap |
| `Turner22-mlGeNN` | `Turner22-mlGeNN` | UNRESOLVED, external registry gap |
| `Weis20-hxtorch` | `Weis20-hxtorch` | matched `spilger2020-hxtorch` by normalized DOI |
| `a14-application-survey` | `a14-application-survey` | UNRESOLVED, analysis-only |
| `a17-two-populations` | `a17-two-populations` | UNRESOLVED, analysis-only |
| `ace-snn2022` | `ace-snn2022` | UNRESOLVED, external registry gap |
| `akida-hw-constraints` | `akida-hw-constraints` | UNRESOLVED, external registry gap |
| `akida-roc` | `Lunghi25-SpaceSNN`, `akida-roc`, `lunghi-2025-space-snn` | matched `lunghi2025-akida-space` by registry key or explicit alias |
| `akida-story-2016` | `akida-story-2016` | UNRESOLVED, external registry gap |
| `alabdulwahid-2024` | `alabdulwahid-2024` | matched `prior-s30-alabdulwahid-2024` by normalized DOI |
| `amir-2017-truenorth-gesture` | `amir-2017-truenorth-gesture` | matched `truenorth-dvs-gesture` by normalized DOI |
| `anon-edge-survey` | `anon-edge-survey` | matched `anon-edge-survey` by registry key or explicit alias |
| `apex-2026` | `apex-2026` | matched `apex` by normalized DOI |
| `arfa-2025-spinnaker2` | `Arfa25-SpiNN2NIR`, `arfa-2025-spinnaker2` | UNRESOLVED, external registry gap |
| `auge-2021-encoding-survey` | `auge-2021-encoding-survey`, `auge2021` | matched `auge` by registry key or explicit alias |
| `basu-2022` | `basu-2022` | matched `basu-2022` by registry key or explicit alias |
| `bauer-2023-exodus` | `bauer-2023-exodus` | matched `exodus` by normalized DOI |
| `bellec2018` | `bellec2018` | UNRESOLVED, external registry gap |
| `bezugam-2023-emg` | `bezugam-2023-emg` | matched `bezugam2023-emg-loihi` by normalized DOI |
| `bhattacharjee-2023-hardware` | `bhattacharjee-2023-hardware` | UNRESOLVED, external registry gap |
| `blouw-2019-kws` | `blouw-2019-kws` | matched `blouw2019-kws-loihi` by normalized DOI |
| `boeshertz2024` | `boeshertz-2024-alif`, `boeshertz-2024-rnn`, `boeshertz2024` | matched `boeshertz2024-rnn-mapping` by registry key or explicit alias |
| `bonazzi-2025-fpgadrone` | `bonazzi-2025-fpgadrone` | matched `bonazzi2025-fpga-drone-dpu` by normalized title |
| `bos-2024-xylo` | `Bos24-XyloKWS`, `bos-2024-xylo` | matched `xylo-kws` by registry key or explicit alias |
| `bouvier-2019` | `bouvier-2019` | matched `bouvier-2019-hardware-implementations` by normalized title |
| `brainchip-akida-techbrief` | `brainchip-akida-techbrief` | matched `brainchip-akida-techbrief` by registry key or explicit alias |
| `brainscales-accel` | `brainscales-accel` | UNRESOLVED, external registry gap |
| `brehove-2026` | `Brehove26-SigmaDelta`, `brehove-2026`, `brehove2025` | matched `brehove` by registry key or explicit alias |
| `bsnn-2022` | `bsnn-2022` | UNRESOLVED, external registry gap |
| `bu-2022-opi` | `bu-2022-opi` | matched `opi` by normalized DOI |
| `bu-2022-qcfs` | `bu-2022-qcfs` | matched `qcfs` by normalized DOI |
| `cao-2015` | `cao-2015`, `cao2015` | matched `cao-2015` by registry key or explicit alias |
| `caviglia-2026` | `caviglia-2026` | matched `prior-s35-caviglia-2026` by normalized DOI |
| `ceolini-emg-dvs` | `ceolini-emg-dvs` | matched `ceolini-emgdvs-fusion` by normalized URL |
| `cerco-spikenet-docs` | `cerco-spikenet`, `cerco-spikenet-docs` | UNRESOLVED, external registry gap |
| `cerebron-2022` | `ChenGaoFu22-Cerebron`, `cerebron-2022` | matched `cerebron` by registry key or explicit alias |
| `cheng-2020-goalkeeper` | `cheng-2020-goalkeeper` | matched `spinnaker-goalkeeper` by normalized DOI |
| `chips-2026` | `chips-2026` | matched `chen-2026-neuromorphic-chips` by normalized DOI |
| `cimarelli-2025` | `cimarelli-2025` | matched `prior-s32-cimarelli-2025` by normalized DOI |
| `clpsnn-2025` | `clp-snn-2025`, `clpsnn-2025` | matched `clp-snn` by registry key or explicit alias |
| `cnn2snn-source-inspection` | `cnn2snn-source-inspection` | UNRESOLVED, external registry gap |
| `convlca-2025-lca` | `convlca-2025-2026`, `convlca-2025-lca` | UNRESOLVED, external registry gap |
| `cramer-2022-surrogate` | `Cramer22-SurrogateGrad`, `cramer-2022-surrogate` | matched `cramer2022-surrogate` by registry key or explicit alias |
| `davies-2021-loihi` | `Davies21`, `davies-2021-loihi` | matched `davies-2021-loihi` by registry key or explicit alias |
| `deneve-2022-ttfs` | `deneve-2022-ttfs`, `deneve2022` | matched `deneve2022-ttfs-unifying` by registry key or explicit alias |
| `deng-2021-optconv` | `deng-2021-optconv` | matched `opt-conv` by normalized DOI |
| `deng-2022-tet` | `deng-2022-tet` | matched `tet` by normalized DOI |
| `deng-2025-edgesnn` | `deng-2025-edgesnn` | matched `deng-2025-edgesnn` by registry key or explicit alias |
| `dennler-2023-olfaction-critique` | `dennler-2023-olfaction-critique` | matched `dennler2023-olfaction-replication` by normalized DOI |
| `dewolf-2020-nengo-loihi` | `dewolf-2020-nengo-loihi` | matched `dewolf2020-nengo-hw` by normalized URL |
| `diehl-2015` | `diehl-2015` | matched `diehl` by registry key or explicit alias |
| `ding-2021-optimalconv` | `ding-2021-optimalconv`, `ding2021` | UNRESOLVED, external registry gap |
| `donati-2022-emg` | `donati-2022-emg` | matched `vitale2022-emg-loihi` by normalized DOI |
| `du-2025-temporal-flexibility` | `du-2025-temporal-flexibility` | matched `temporal-flexibility` by normalized DOI |
| `dynapse-icub-2020` | `dynapse-icub-2020` | matched `dynapse-icub-pcontroller` by normalized title |
| `edge-bench-2026` | `edge-bench-2026` | matched `prior-s36-du-2026` by normalized DOI |
| `eeg-motor-imagery-repo` | `eeg-motor-imagery-repo` | UNRESOLVED, external registry gap |
| `eeg-seizure-2025` | `eeg-seizure-2025` | matched `eeg-seizure-loihi2` by normalized URL |
| `eetimes-graimatter` | `eetimes-graimatter` | UNRESOLVED, external registry gap |
| `epjb-2024` | `epjb-2024` | matched `zolfagharinejad-2024-brain-inspired-systems` by normalized DOI |
| `eshraghian-2023` | `Eshraghian23-snnTorch`, `eshraghian-2023` | matched `eshraghian-2023-training-snns` by registry key or explicit alias |
| `ettfs-2024` | `ettfs-2024`, `ettfs2024` | UNRESOLVED, external registry gap |
| `eventvision-survey-2023` | `eventvision-survey-2023` | matched `eventvision2023-survey` by normalized DOI |
| `fang-2021-plif` | `fang-2021-plif` | matched `plif` by normalized DOI |
| `fang-2021-sew` | `fang-2021-sew` | matched `sew-resnet` by normalized DOI |
| `fang-2023-spikingjelly` | `SJ23-SciAdv`, `fang-2023-spikingjelly`, `fang-2023-spikingjelly-sciadv` | matched `spj` by registry key or explicit alias |
| `fang-2023-spikingjelly-lava` | `SJ-LavaExchangeDocs`, `fang-2023-spikingjelly-lava` | matched `spj-lava` by registry key or explicit alias |
| `farsa-2026` | `farsa-2026` | matched `prior-s37-farsa-2026` by normalized URL |
| `ferreira-2025` | `ferreira-2025` | matched `ferreira-2025-edge-ai-circuits` by normalized DOI |
| `forcecontrol-2024` | `forcecontrol-2024` | matched `force-control` by normalized DOI |
| `frenkel-2019-morphic` | `Frenkel19-MorphIC`, `frenkel-2019-morphic`, `frenkel2019` | matched `morphic` by registry key or explicit alias |
| `galanis-2020-spinnaker` | `galanis-2020-spinnaker` | UNRESOLVED, external registry gap |
| `gallego-2022` | `gallego-2022` | matched `gallego-2022-event-based-vision` by normalized DOI |
| `gebregiorgis-2025` | `gebregiorgis-2025` | matched `gebregiorgis-2025-spike-based-overview` by normalized DOI |
| `gelneuro-2026` | `gelneuro-2026` | UNRESOLVED, external registry gap |
| `guo-2025-qac` | `guo-2025-qac` | matched `qac` by normalized URL |
| `guo-2026-mtsnn-frontiers` | `guo-2026-mtsnn-frontiers` | matched `mt-snn` by normalized title |
| `guo-2026-mtsnn-withdrawn` | `guo-2026-mtsnn-withdrawn` | UNRESOLVED, external registry gap |
| `guo2021` | `guo-2021-neuralcoding`, `guo2021` | UNRESOLVED, external registry gap |
| `han-2020-rmpsnn` | `han-2020-rmpsnn` | matched `rmp` by normalized DOI |
| `han-2020-tsc` | `han-2020-tsc` | matched `tsc` by normalized DOI |
| `hao-2023-aaai-srp` | `hao-2023-aaai-srp`, `hao-2023-srp` | matched `srp` by registry key or explicit alias |
| `hao-2023-cos` | `hao-2023-cos` | matched `cos` by normalized DOI |
| `hbp-guidebook` | `hbp-guidebook` | UNRESOLVED, external registry gap |
| `hiaer-cri-docs` | `cri-2025-hiaerspike`, `hiaer-cri-docs` | matched `hiaer-spike-cri` by registry key or explicit alias |
| `ho-2021-tcl` | `ho-2021-tcl` | matched `tcl` by normalized title |
| `hodgkin1952` | `hodgkin1952` | UNRESOLVED, external registry gap |
| `horowitz-2014` | `horowitz-2014`, `horowitz-2014-isscc` | UNRESOLVED, external registry gap |
| `hu-2023-fastsnn` | `hu-2023-fastsnn` | matched `fast-snn` by normalized DOI |
| `huynh-2022` | `huynh-2022` | matched `huynh-2022-implementing-snns` by normalized DOI |
| `ijcai2025negspike` | `ijcai2025negspike` | UNRESOLVED, external registry gap |
| `imam-2020-olfaction` | `imam-2020-olfaction` | matched `imam-cleland-olfaction` by normalized DOI |
| `inrc-loihi-access` | `IntelINRC-Access`, `inrc-loihi-access` | matched `intel-inrc-confluence` by registry key or explicit alias |
| `intel-nxtf-slayer-gestures` | `intel-nxtf-slayer-gestures` | matched `slayer-nxtf-gesture` by normalized URL |
| `ivanov-2022` | `ivanov-2022` | matched `ivanov-2022` by registry key or explicit alias |
| `izhikevich2003` | `izhikevich2003` | UNRESOLVED, external registry gap |
| `jelly-lava-source` | `jelly-lava-source` | UNRESOLVED, external registry gap |
| `jelly-nir-source` | `jelly-nir-source` | UNRESOLVED, external registry gap |
| `jiang-2025-adaptive-fission` | `jiang-2025-adaptive-fission` | UNRESOLVED, external registry gap |
| `jiang2023` | `jiang-2023-sliprelu`, `jiang2023` | matched `slip-relu` by registry key or explicit alias |
| `kelber-2020-benchmark` | `kelber-2020-benchmark` | matched `kelber-2020` by normalized DOI |
| `kelber-2020-spinnaker2sim` | `Kelber20-SpiNN2Map`, `kelber-2020-spinnaker2sim` | UNRESOLVED, external registry gap |
| `khan-2025` | `khan-2025` | matched `khan-2025` by registry key or explicit alias |
| `kim-2020-roc-scnn` | `kim-2020-roc-scnn` | UNRESOLVED, external registry gap |
| `kim-2022-rate-vs-direct` | `kim-2022-rate-vs-direct` | UNRESOLVED, external registry gap |
| `kim2018phase` | `kim-2018-weightedspikes`, `kim2018phase` | matched `kim2018-weightedspikes` by registry key or explicit alias |
| `kreiser-2020-icub` | `kreiser-2020-icub` | matched `kreiser2020-icub-headpose` by normalized title |
| `kria-prophesee-vitisai` | `kria-prophesee-vitisai` | UNRESOLVED, external registry gap |
| `kudithipudi-2025` | `kudithipudi-2025` | matched `kudithipudi-2025-neuromorphic-scale` by normalized DOI |
| `latency-framework2026` | `latency-framework2026`, `latencycoding-2026` | UNRESOLVED, external registry gap |
| `lava-archived-2026` | `lava-archived-2026` | UNRESOLVED, external registry gap |
| `lava-dl` | `lava-dl`, `lavadl-slayer-docs` | matched `lava-dl-slayer-docs` by registry key or explicit alias |
| `lava-dl-docs` | `lava-dl-docs` | UNRESOLVED, external registry gap |
| `lava-dl-readme` | `lava-dl-readme` | UNRESOLVED, external registry gap |
| `lenz-2023-quartz` | `lenz-2023-quartz` | matched `quartz` by normalized DOI |
| `li-2021-calibration` | `li-2021-calibration` | matched `snn-calibration` by normalized DOI |
| `li-2022-qffs` | `li-2022-qffs` | matched `qffs` by normalized title |
| `li-2023-dynconf` | `li-2023-dynconf` | matched `dynamic-confidence` by normalized DOI |
| `li-2023-seenn` | `li-2023-seenn` | matched `seenn` by normalized DOI |
| `li-2025-neuroscale` | `li-2025-neuroscale` | matched `neuroscale2025-natcomm` by normalized DOI |
| `li2022burst` | `li-2022-burstspikes`, `li2022burst` | matched `burst-spikes` by registry key or explicit alias |
| `liu-2019-facedemo` | `liu-2019-facedemo`, `liu-2019-facerecognition` | UNRESOLVED, external registry gap |
| `liu-2022-spikeconverter` | `liu-2022-spikeconverter` | matched `spikeconverter` by normalized title |
| `loihi-barrier` | `Davies18`, `davies-2018-loihi`, `loihi-barrier` | matched `loihi1` by registry key or explicit alias |
| `luu-2026` | `luu-2026` | matched `prior-s34-luu-2026` by normalized title |
| `maass1997` | `maass1997` | UNRESOLVED, external registry gap |
| `manjunath-2025-neuroflex` | `manjunath-2025-neuroflex` | matched `neuroflex` by normalized DOI |
| `manna-2023` | `manna-2023` | matched `manna-2023-frameworks` by normalized DOI |
| `massa-2020-loihi-dvs` | `massa-2020`, `massa-2020-loihi-dvs` | matched `massa-2020` by registry key or explicit alias |
| `mdpi-tutorial-2025` | `mdpi-tutorial-2025` | matched `prior-s29-ayasi-2025` by normalized DOI |
| `meszaros-2025-delays` | `meszaros-2025-delays`, `meszaros-2025-loihi2-delays` | matched `eventprop-delays` by registry key or explicit alias |
| `moyer-2020-semieng` | `Moyer20-SemiEng`, `moyer-2020-semieng` | UNRESOLVED, external registry gap |
| `muBrain21` | `muBrain21` | matched `ubrain` by normalized URL |
| `narduzzi-2025-eflop` | `narduzzi-2025-eflop` | UNRESOLVED, external registry gap |
| `nengoloihi-cifar10-example` | `nengoloihi-cifar10-example` | UNRESOLVED, external registry gap |
| `neuroflex-2025` | `neuroflex-2025` | matched `neuroflex` by normalized DOI |
| `neuronflow-2020` | `neuronflow-2020` | UNRESOLVED, external registry gap |
| `nir-porting-guide` | `nir-porting-guide` | UNRESOLVED, external registry gap |
| `npl-2026` | `npl-2026` | matched `prior-s33-hegao-2026` by normalized DOI |
| `nunes-2022` | `nunes-2022` | matched `nunes-2022` by registry key or explicit alias |
| `nxsdk-models-repo` | `nxsdk-models-repo` | matched `slayer-nxtf-gesture` by normalized URL |
| `openneuromorphic-akida` | `openneuromorphic-akida` | matched `open-neuromorphic-akida` by normalized URL |
| `ortone-2026-tactile` | `ortone-2026-tactile` | matched `dynap-se-tactile` by normalized DOI |
| `pals-2021-eeg-spinnaker` | `pals-2021-eeg-spinnaker` | UNRESOLVED, external registry gap |
| `park-2020-t2fsnn` | `park-2020-t2fsnn` | matched `t2fsnn` by normalized title |
| `parpart-2023-lca` | `lca-loihi2-2023`, `parpart-2023-lca`, `parpart-2023-lca-loihi2` | matched `parpart2023-lca-loihi2` by registry key or explicit alias |
| `pascal-2025` | `pascal-2025`, `ramesh-2025-pascal` | matched `pascal` by registry key or explicit alias |
| `patel-2020-sddpg` | `patel-2020-sddpg`, `sddpg-2020` | matched `sddpg` by registry key or explicit alias |
| `patino-saucedo-2020-spinnaker` | `PatinoSaucedo20-SpiNNConv`, `patino-saucedo-2020-spinnaker` | matched `patino-saucedo-2020` by registry key or explicit alias |
| `pehle-2022-bmtk` | `pehle-2022-bmtk` | UNRESOLVED, external registry gap |
| `pmc-loihi-backprop` | `pmc-loihi-backprop` | matched `backprop-loihi-pmc` by normalized title |
| `prophesee-2025-pedestrian` | `prophesee-2025-pedestrian` | UNRESOLVED, external registry gap |
| `prophesee-docs-detection` | `prophesee-docs-detection` | UNRESOLVED, external registry gap |
| `prophesee-genx320-docs` | `prophesee-genx320-docs` | UNRESOLVED, external registry gap |
| `radar-automotive-2026` | `radar-automotive-2026` | UNRESOLVED, external registry gap |
| `radar-resonator-2025` | `radar-resonator-2025` | UNRESOLVED, external registry gap |
| `rathi-2023` | `rathi-2023` | matched `rathi-2023` by registry key or explicit alias |
| `richter-2023-speck` | `Richter23-SpeckASIC`, `richter-2023-speck`, `richter2023speck` | matched `richter` by registry key or explicit alias |
| `richter-2023-speck1` | `richter-2023-speck1` | matched `richter` by normalized DOI |
| `riverpub-mcu-dynapcnn` | `riverpub-mcu-chapter`, `riverpub-mcu-dynapcnn` | matched `riverpub-mnist-dynapcnn` by registry key or explicit alias |
| `rockpool-xylo` | `Rockpool-XyloOverview`, `rockpool-xylo`, `rockpool-xylo-overview` | matched `rockpool-xylo-docs` by registry key or explicit alias |
| `roy-2019` | `roy-2019` | matched `roy-2019-spike-machine-intelligence` by normalized DOI |
| `rueckauer-2022-nxtf` | `Rueckauer21-NxTF`, `nxtf2021`, `rueckauer-2021-nxtf`, `rueckauer-2022-nxtf` | matched `nxtf` by registry key or explicit alias |
| `rueckauer2017` | `Rueckauer17-SNNTB`, `rueckauer-2017`, `rueckauer-2017-frontiers`, `rueckauer2017` | matched `rueckauer` by registry key or explicit alias |
| `satcsp-2020` | `satcsp-2020` | UNRESOLVED, external registry gap |
| `schmitt-2017-brainscales` | `Schmitt17-HITL`, `schmitt-2017-brainscales` | matched `schmitt2017-hitl` by registry key or explicit alias |
| `schuman-2017` | `schuman-2017` | matched `schuman-2017-hardware-survey` by normalized DOI |
| `schuman-2022` | `schuman-2022` | matched `schuman-2022-opportunities` by normalized DOI |
| `sengupta-2019-spikenorm` | `sengupta-2019-spikenorm` | matched `sengupta` by normalized DOI |
| `serrano-2015-convnets` | `serrano-2015-convnets` | UNRESOLVED, external registry gap |
| `shen-2024-cvpr` | `shen-2024-bitbudget`, `shen-2024-cvpr` | UNRESOLVED, external registry gap |
| `shrestha-2018-slayer` | `shrestha-2018-slayer` | matched `slayer` by normalized DOI |
| `shrestha-2022` | `shrestha-2022` | matched `shrestha-2022-models-hardware` by normalized DOI |
| `shrestha-2023-video-audio` | `Shrestha23-VideoAudio`, `shrestha-2023-loihi2`, `shrestha-2023-loihi2video`, `shrestha-2023-video-audio`, `shrestha2023` | matched `sdnn` by registry key or explicit alias |
| `sia-fpga` | `sia-fpga` | UNRESOLVED, external registry gap |
| `sinabs-discretize-api` | `sinabs-discretize-api` | UNRESOLVED, external registry gap |
| `sinabs-docs` | `sinabs-docs` | matched `sinabs-docs` by registry key or explicit alias |
| `sinabs-docs-overview` | `sinabs-docs-overview` | UNRESOLVED, external registry gap |
| `sinabs-nmnist-tutorial` | `sinabs-nmnist-tutorial` | UNRESOLVED, external registry gap |
| `singh-2021-gesture-snn` | `singh-2021-gesture-snn` | UNRESOLVED, external registry gap |
| `snnTorch-Docs` | `snnTorch-Docs` | UNRESOLVED, external registry gap |
| `snntoolbox-docs` | `snntoolbox-docs` | UNRESOLVED, external registry gap |
| `snntoolbox-github` | `snntoolbox-github` | matched `snn-toolbox-github` by normalized URL |
| `snntoolbox-issues` | `snntoolbox-issues` | UNRESOLVED, external registry gap |
| `snntorch-pr-388` | `snnTorch-PR388`, `snntorch-pr-388` | matched `snntorch-pr388` by registry key or explicit alias |
| `snntorch-pr-426` | `snntorch-pr-426` | UNRESOLVED, external registry gap |
| `song-2024-xpikeformer` | `song-2024-xpikeformer` | matched `xpikeformer` by normalized DOI |
| `speck-datasheet` | `speck-datasheet` | UNRESOLVED, external registry gap |
| `speck-devkit-manual` | `speck-devkit-manual` | matched `synsense-speck-datasheet` by normalized URL |
| `speck-t-question` | `speck-t-question` | matched `sinabs-docs` by normalized URL |
| `spiker-2022` | `spiker-2022` | UNRESOLVED, external registry gap |
| `spiker-plus-fpga` | `spiker-plus-fpga` | UNRESOLVED, external registry gap |
| `spikerplus-2024` | `Carpegna24-SpikerPlus`, `spiker-fpga`, `spikerplus-2024` | matched `spikerplus` by registry key or explicit alias |
| `spiking-transformers-2024` | `spiking-transformers-2024` | matched `hu-2024-large-scale-snns` by normalized DOI |
| `spikingjelly-issue543` | `spikingjelly-issue543` | UNRESOLVED, external registry gap |
| `spikingjelly-loihi2-2026` | `objdet-2026-loihi2-preprint`, `spikingjelly-loihi2-2026` | UNRESOLVED, external registry gap |
| `spinnaker-1ms` | `spinnaker-1ms` | UNRESOLVED, external registry gap |
| `spinnaker-neuron-lab-manual` | `spinnaker-neuron-lab`, `spinnaker-neuron-lab-manual` | UNRESOLVED, external registry gap |
| `stradmann-2021-mobile` | `Stradmann21-Mobile`, `stradmann-2021-mobile` | matched `stradmann2021-mobile` by registry key or explicit alias |
| `swsc2024` | `swsc-2024`, `swsc2024` | UNRESOLVED, external registry gap |
| `syncnn-2022` | `Panchapakesan22-SyncNN`, `syncnn-2022` | matched `syncnn` by registry key or explicit alias |
| `synsense-speck-gesture-datasheet` | `synsense-speck-gesture-datasheet` | UNRESOLVED, external registry gap |
| `tang-2017-lca-theory` | `tang-2017-lca-theory` | matched `tang2017-lca-sparsecoding` by normalized DOI |
| `tang-2019-slam` | `tang-2019-slam` | matched `tang-slam-loihi` by normalized DOI |
| `tayarani-2021` | `tayarani-2021` | matched `prior-s31-tayaraninajaran-2021` by normalized DOI |
| `thorpe-spikebased` | `thorpe-spikebased` | UNRESOLVED, external registry gap |
| `thorpe1996` | `ThorpeGautrais96-SpikeAsync`, `thorpe-1996`, `thorpe1996` | matched `thorpe1996-rankorder` by registry key or explicit alias |
| `truenorth-neuron-model` | `truenorth-neuron-model` | matched `truenorth-neuron-model-doc` by normalized URL |
| `v2v-2025` | `v2v-2025` | matched `v2v2025-neurips` by normalized title |
| `wang-2023-ijcai-snm` | `wang-2023-ijcai-snm` | matched `snm` by normalized URL |
| `wang-2025-adafire` | `wang-2025-adafire` | matched `adafire` by normalized DOI |
| `wang2022signed` | `wang-2022-snm`, `wang2022signed` | matched `snm` by registry key or explicit alias |
| `weis-2020-brainscales2` | `Weis20-ANNMode`, `weis-2020-brainscales2` | matched `weis2020-annmode` by registry key or explicit alias |
| `xie-2024` | `xie-2024` | matched `xie-2024` by registry key or explicit alias |
| `yamazaki-2022` | `yamazaki-2022` | matched `yamazaki-2022` by registry key or explicit alias |
| `yang-2024-csqcfs` | `yang-2024-csqcfs` | matched `cs-qcfs` by normalized DOI |
| `yao-2024-speck` | `Yao24-SpeckNatComm`, `speck-natcomm`, `yao-2024-speck`, `yao-2024-speck-naturecomm` | matched `speck-dynamic-snn` by registry key or explicit alias |
| `yao-spikedriven` | `yao-spikedriven` | UNRESOLVED, external registry gap |
| `yik-2025-neurobench` | `yik-2025-neurobench` | matched `yik-2025-neurobench` by registry key or explicit alias |
| `yoso2020` | `yoso-2020`, `yoso2020` | UNRESOLVED, external registry gap |
| `zheng-2021-tdbn` | `zheng-2021-tdbn` | matched `tdbn` by normalized DOI |
| `zheng-2022` | `zheng-2022` | matched `zheng-2022` by registry key or explicit alias |
| `zhou-2023-spikformer` | `zhou-2023-spikformer` | matched `spikformer` by normalized DOI |
| `zhou-2023-spikingformer` | `zhou-2023-spikingformer` | matched `spikingformer` by normalized DOI |
| `zhou-2024-spikformerv2` | `zhou-2024-spikformerv2` | UNRESOLVED, external registry gap |
| `ziegler-2024-fastobjects` | `Ziegler24-FastObjects`, `ziegler-2024-fastobjects` | matched `ziegler2024-akida-robotics` by registry key or explicit alias |
| `zou2023negspike` | `zou2023negspike` | UNRESOLVED, external registry gap |

## Required canonical-registry correction

1. Add or reconcile the 105 external unresolved work groups in the canonical source registry. Each record needs defensible authors, year, venue, DOI or null, URL, source type, retrieval status, verification status, retrieval date, locators, aliases, and notes under the existing schema.
2. Add every legacy target and alias from the inventory to exactly one canonical record. Preserve the two exact-URL duplicate groups as aliases rather than separate records.
3. Bind `A18-Research` explicitly to `a18-sourcecode-comparison` if manual review confirms identity. Keep `a14-application-survey` and `a17-two-populations` as explicitly labeled analysis-only records under the bibliography policy, not fabricated external publications.
4. Re-run this inventory after Task 3 correction. Task 6 can proceed only when every external cited target has one unique canonical match and the only non-registry entries are the explicitly approved internal analyses.

## Determinism checks encoded in the inventory

- Every cited target has a BibTeX input row: True.
- Every resolved target has exactly one canonical match: True.
- Unresolved accounting identity: 110 keys = 108 work groups + 2 duplicate-key excess.
- Work-group classification identity: 108 groups = 105 external + 3 internal analysis.

## Post-migration canonical generation

Recomputed on 2026-09-16 after the reviewed migration records entered the canonical
source registry. The pre-migration inventory above remains unchanged as the audit trail.

- Section fragments scanned: 6
- Distinct inline reference keys: 394
- Distinct cited keys: 375
- Reference-only keys: 19
- Canonical source-registry records and generated BibTeX definitions: 352
- Canonical works reached by the 375 cited keys: 284
- Canonical works not cited by the current fragments: 68
- Generated legacy alias mappings: 265, including 255 cited keys
- Ambiguous exact matches: 0
- Unresolved cited keys: 0
- Unresolved reference-only keys that are not cited: 7
- Duplicate generated BibTeX keys: 0
- Explicit internal-analysis records: 3, all cited

Exact matching used canonical IDs and aliases first, then normalized DOI, normalized
URL, and exact normalized title. The 387 resolved inline keys comprise 216 registry-key
or alias matches, 50 DOI matches, 92 URL matches, and 29 title matches. No fuzzy match
was used. Fragment reference prose supplied identity evidence only. All generated
BibTeX fields came from `data/source-registry.json`.

The seven unresolved reference-only keys are `NIR-Support`, `Shukla19-TNCarCount`,
`furber-2004-nofm`, `furber2004`, `gerstner2002`, `perez2013`, and `speck-2019`.
They occur only in inline reference lists that the site assembler removes. None occurs
in a citation marker, so they do not weaken the zero-unresolved citation result.

The analysis-only records are `a14-application-survey`, `a17-two-populations`, and
`a18-sourcecode-comparison`. Generated BibTeX labels each one as internal analysis and
states that it is not an external publication. The legacy `SJ-GitHub` key resolves to
`a18-sourcecode-comparison` by the exact reviewed SpikingJelly repository URL. This
identity edge is reported explicitly because its legacy label describes repository
state while the canonical record represents the tracked source-level comparison.
