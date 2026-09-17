# Target classification

Each line covers one evidence-papers.json record, giving its id, target_kind, qualifier, the field text that decided it, and the rule number from task-1-brief.md Step 4. Records split from a single source paper are listed as two lines.

## papers

- `cao-2015` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `diehl-2015` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `rueckauer-2017` is **none**, qualifier "", decided by target_hardware "none (in this paper)"; evidence E5 (rule 6).
- `sengupta-2019` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `rmp-snn` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `tsc` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `opt-conv` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `snn-calibration` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `tcl` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `eedn` is **neuromorphic**, qualifier "IBM TrueNorth (NS1e/NS16e boards)", decided by target_hardware "IBM TrueNorth (NS1e/NS16e boards)" (rule 1).
- `stromatias-2015` is **neuromorphic**, qualifier "SpiNNaker (single chip; power-scaling estimates extrapolated to 48-chip board)", decided by target_hardware of the same text (rule 1).
- `massa-2020` is **neuromorphic**, qualifier "Intel Loihi (37 cores)", decided by target_hardware "Intel Loihi (37 cores)" (rule 1).
- `nxtf` is **neuromorphic**, qualifier "Intel Loihi (up to 16 chips)", decided by target_hardware "Intel Loihi (up to 16 chips)" (rule 1).
- `kelber-2020` is **neuromorphic**, qualifier "BrainScaleS, Spikey, SpiNNaker", decided by target_hardware "BrainScaleS, Spikey, SpiNNaker" (rule 1).
- `qcfs` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `opi` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `srp` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `cos` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `slip-relu` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `burst-spikes` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `snm` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `fast-snn` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `dynamic-confidence` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `qffs` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `seenn` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `cs-qcfs` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `adafire` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `pascal-none` is **none**, qualifier "", decided by target_hardware "none for the T_eff headline"; evidence E5 (rule 6). Split from `pascal`, following site/sec-09.html's own two-row treatment of the T_eff headline versus the uniform-T=4 hardware check.
- `pascal-simulator` is **simulator**, qualifier "custom in-house LoAS/SparTen-based accelerator (RTL synthesis)", decided by target_hardware "custom in-house LoAS/SparTen-based accelerator (RTL synthesis) for the uniform-T=4 neuron-overhead check", PASCAL named explicitly (rule 4). Split from `pascal`.
- `neuroflex` is **simulator**, qualifier "RTL synthesis model only", decided by target_hardware "none (RTL synthesis model only)", NeuroFlex named explicitly (rule 4).
- `spikeconverter` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `brehove-2026` is **neuromorphic**, qualifier "Intel Loihi 2, in-house 16-chip VPX development board", decided by target_hardware "in-house 16-chip Intel Loihi 2 VPX development board" (rule 1).
- `qac` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `mt-snn-withdrawn-iclr` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `mt-snn-frontiers-2026` is **none**, qualifier "", decided by target_hardware "none established from the accepted abstract"; evidence E5 (rule 6).
- `temporal-flexibility` is **neuromorphic**, qualifier "SynSense Speck2e Devkit", decided by target_hardware "Speck2e Devkit (SynSense)" (rule 1).
- `sew-resnet` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `tdbn` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `plif` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `tet` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `spikformer` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `spikingformer` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `spike-driven-transformer` is **none**, qualifier "", decided by target_hardware "none"; evidence E5 (rule 6).
- `xpikeformer` is **simulator**, qualifier "NeuroSim circuit simulation; FPGA prototype of attention-tile sub-block only", decided by target_hardware "FPGA (attention tile sub-block only, not full-chip silicon)", XpikeFormer named explicitly (rule 4).
- `slayer` is **GPU**, qualifier "GPU (unspecified, CUDA training/simulation)", decided by what_was_measured "accuracy in GPU simulation" (rule 5). Evidence is E3, not E5, so rule 6's "none" cannot apply.
- `slayer-nxtf-gesture` is **neuromorphic**, qualifier "Intel Loihi 1 board (ncl-ext-ghrd-01)", decided by target_hardware of the same text (rule 1).
- `exodus` is **none**, qualifier "", decided by target_hardware "none (deployment only possible downstream via Sinabs -> DynapCNN/Speck, not exercised in this paper)"; evidence E5 (rule 6).
- `eventprop-delays` is **neuromorphic**, qualifier "Intel Loihi 2 (single-chip, Oheo Gulch)", decided by target_hardware of the same text (rule 1).
- `clp-snn` is **neuromorphic**, qualifier "Intel Loihi 2, INT8", decided by target_hardware "Intel Loihi 2, INT8" (rule 1).
- `speck1` is **neuromorphic**, qualifier "Speck1 (SynSense)", decided by target_hardware "Speck1 (SynSense)" (rule 1).
- `speck-dynamic-snn` is **neuromorphic**, qualifier "SynSense Speck", decided by target_hardware "SynSense Speck" (rule 1).
- `hiaer-spike-cri` is **FPGA**, qualifier "UCSD HiAER-Spike (CRI FPGA-based neuromorphic hardware)", decided by target_hardware "CRI FPGA-based neuromorphic hardware (UCSD HiAER-Spike)" (rule 3).
- `imam-cleland-olfaction` is **neuromorphic**, qualifier "Intel Loihi (72-core network)", decided by target_hardware of the same text (rule 1).
- `tang-slam-loihi` is **neuromorphic**, qualifier "Intel Loihi (Nahuku 8-chip board), 82 cores", decided by target_hardware of the same text (rule 1).
- `sddpg` is **neuromorphic**, qualifier "Intel Loihi (Kapoho Bay, 2 chips)", decided by target_hardware of the same text (rule 1).
- `force-control` is **neuromorphic**, qualifier "Intel Loihi 1 (Kapoho Bay) and Loihi 2 (Oheo Gulch, remote)", decided by target_hardware of the same text (rule 1).
- `xylo-kws` is **neuromorphic**, qualifier "Xylo Audio 2 (SynSense, commercial)", decided by target_hardware of the same text (rule 1).
- `quartz` is **neuromorphic**, qualifier "Intel Loihi 1 (Nahuku 32 board, ncl-ext-ghrd-01)", decided by target_hardware of the same text (rule 1).
- `adaptive-fission` is **neuromorphic**, qualifier "Lynxi HP201 (commercial successor to Tianjic)", decided by target_hardware of the same text (rule 1).
- `northpole` is **NPU**, qualifier "IBM NorthPole, non-spiking digital accelerator", decided by target_hardware "IBM NorthPole (12nm, physical PCIe card)" naming NorthPole (rule 2).
- `tianjic` is **neuromorphic**, qualifier "Tianjic chip (physical, single chip)", decided by target_hardware of the same text (rule 1).
- `odin` is **neuromorphic**, qualifier "ODIN ASIC (28nm FDSOI, 9 fabricated chips tested)", decided by target_hardware of the same text (rule 1).
- `reckon` is **neuromorphic**, qualifier "ReckOn ASIC (28nm FDSOI, 5 fabricated chips)", decided by target_hardware of the same text (rule 1).
- `seneca` is **simulator**, qualifier "SENECA (not yet fabricated)", decided by target_hardware "none (not yet fabricated)", SENECA named explicitly (rule 4).
- `morphic` is **neuromorphic**, qualifier "MorphIC ASIC (65nm, fabricated)", decided by target_hardware of the same text (rule 1).
- `ubrain` is **neuromorphic**, qualifier "mu-Brain ASIC (fabricated 40nm prototype)", decided by target_hardware of the same text (rule 1).
- `syncnn` is **FPGA**, qualifier "Xilinx ARM-FPGA SoC boards (ZCU102, ZCU104, ZED)", decided by target_hardware of the same text, SyncNN named explicitly (rule 3).
- `spikerplus` is **FPGA**, qualifier "Xilinx FPGA (physical synthesis + deployment)", decided by target_hardware of the same text (rule 3).
- `firefly` is **FPGA**, qualifier "Zynq UltraScale+ edge FPGA boards (xczu3eg/xczu5ev/xczu7ev, KV260, ZCU104)", decided by target_hardware of the same text, Firefly named explicitly (rule 3).
- `cerebron` is **FPGA**, qualifier "Xilinx XC7Z100 FPGA (200MHz, physical implementation)", decided by target_hardware of the same text, Cerebron named explicitly (rule 3).
- `apex` is **simulator**, qualifier "RTL synthesis model only (40nm CMOS)", decided by target_hardware "none (RTL synthesis model only)", APEX named explicitly (rule 4).
- `truenorth-dvs-gesture` is **neuromorphic**, qualifier "IBM TrueNorth (physical)", decided by target_hardware of the same text (rule 1).
- `gelneuro` is **neuromorphic**, qualifier "SynSense Speck2f", decided by target_hardware "SynSense Speck2f" (rule 1).
- `dynap-se-tactile` is **neuromorphic**, qualifier "DYNAP-SE (physical, mixed-signal)", decided by target_hardware of the same text (rule 1).
- `spinnaker-goalkeeper` is **neuromorphic**, qualifier "SpiNNaker (physical)", decided by target_hardware "SpiNNaker (physical)" (rule 1).
- `patino-saucedo-2020` is **neuromorphic**, qualifier "SpiNNaker (103-machine, 48 chips)", decided by target_hardware of the same text (rule 1).
- `andrei2024-deep-unrolling-spinnaker2` is **neuromorphic**, qualifier "physical single-chip SpiNNaker2 board", decided by target_hardware of the same text (rule 1).
- `arfa2025-spiking-q-spinnaker2` is **neuromorphic**, qualifier "physical SpiNNaker2 board", decided by target_hardware of the same text (rule 1).
- `datta2025-snn-meets-ann` is **none**, qualifier "", decided by evidence E5 (rule 6); target_hardware reads "Loihi route asserted but no generation or physical board identified," an unconfirmed route rather than a stated target.

## ambiguous records (target_kind assigned by judgment beyond a literal rule match)

- `kelber-2020`. target_hardware lists Spikey alongside BrainScaleS and SpiNNaker. Spikey is not one of rule 1's named chips, but the record measures it as physical analog neuromorphic hardware alongside the two named chips. Classified neuromorphic under the bucket's stated meaning rather than the named-chip list.
- `adaptive-fission`. target_hardware names Lynxi HP201, described as the commercial successor to Tianjic, not literally "Lynxi KA200" from rule 1's list. Classified neuromorphic (fabricated silicon, evidence E1) by the bucket's stated meaning.
- `odin`. ODIN is a fabricated 28nm FDSOI ASIC (9 chips tested) but is not one of the chips named in rule 1's parenthetical list. Classified neuromorphic because it is fabricated neuromorphic silicon per the bucket's stated meaning, and no other rule fits (not RTL-only, not conventional, evidence is E1 not E5).
- `reckon`. Same reasoning as ODIN. A fabricated 28nm FDSOI ASIC (5 chips), not named in rule 1's list, classified neuromorphic by bucket meaning.
- `ubrain`. mu-Brain is a fabricated 40nm ASIC prototype, not named in rule 1's list, classified neuromorphic by bucket meaning.
- `slayer`. target_hardware reads "none (in original paper)," but evidence is E3, not E5, so rule 6 (which requires E5) cannot apply. what_was_measured literally states "accuracy in GPU simulation," so classified GPU under rule 5 by elimination.
- `datta2025-snn-meets-ann`. target_hardware names a Loihi route, but the field itself says the route is "asserted but no generation or physical board identified," and the record's own top-level evidence field is E5 (framework-level accuracy only). evidence_notes separately grades the asserted Lava-DL-to-Loihi route E3, but that note does not change the record's top-level evidence field. Classified none (rule 6) rather than neuromorphic, since no board is actually confirmed.
- `xylo-kws`. evidence_notes and what_was_measured name GPU, CPU, Jetson, Movidius, Loihi, and SpiNNaker2 as comparators. The brief's own example ids ("xylo-kws-neuromorphic", "xylo-kws-gpu") suggest a split, but site/sec-15.html cites xylo-kws as a single table row (target "Physical (commercial chip)," comparators listed in a separate "Compared To" column, not as an independently measured claim). Not split; classified as a single neuromorphic record.
- `force-control`. what_was_measured and evidence_notes name CPU and GPU comparators. site/sec-15.html and site/sec-14.html cite force-control as a single table row (target "Physical (Loihi 1 and 2)," comparators in a separate column). Not split; classified as a single neuromorphic record.

## hardware nodes (evidence-stack.json)

- `loihi-1` is **neuromorphic**
- `loihi-2` is **neuromorphic**
- `spinnaker-1` is **neuromorphic**
- `spinnaker-2` is **neuromorphic**
- `speck` is **neuromorphic**
- `dynapcnn` is **neuromorphic**
- `xylo` is **neuromorphic**
- `brainscales-1` is **neuromorphic**
- `brainscales-2` is **neuromorphic**
- `truenorth` is **neuromorphic**
- `northpole` is **NPU**
- `tianjic` is **neuromorphic**
- `lynxi-ka200` is **neuromorphic**
- `akida` is **neuromorphic**
- `morphic` is **neuromorphic**
- `dynap-se2` is **neuromorphic**
- `innatera-pulsar` is **neuromorphic**
- `cerebron` is **FPGA**
- `apex` is **simulator**
- `syncnn` is **FPGA**
- `neuroflex` is **simulator**
- `fpga` is **FPGA**
- `lynxi-hp201` is **neuromorphic**

## ambiguous hardware nodes

- `lynxi-hp201`. Classified neuromorphic as a physical, commercially deployed Lynxi accelerator, matching the neuromorphic bucket's stated meaning, though it is a different product from Lynxi KA200, the chip named in rule 1's list; evidence-stack.json's own summary for this node states it is "kept distinct from the KA200 platform."
