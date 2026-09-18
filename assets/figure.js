/* The neuromorphic deployment stack figure.
   Selecting anything narrows the question rather than restarting it. Constraints
   accumulate, the surviving routes are ranked, and the best one is drawn.
   A route that cannot complete is drawn up to its snap point and then broken. */

const LAYERS = [
  { id: 'app', n: 1, name: 'Application', sub: 'the task, the sensor that feeds it, and the form the input takes', rows: [
    { label: 'Task', chips: [
      ['image-classification-static', 'Image classification'], ['object-detection', 'Object detection'],
      ['gesture-recognition', 'Gesture recognition'], ['tracking-motion', 'Tracking and motion'],
      ['keyword-spotting-audio', 'Keyword spotting'], ['biosignal-decoding', 'Biosignal decoding'],
      ['olfaction', 'Olfaction'], ['robotics-closed-loop-control', 'Robotics and control'],
      ['slam', 'SLAM'], ['optimization-constraint-satisfaction', 'Optimization and SAT'] ] },
    { label: 'Sensor', chips: [
      ['event-camera', 'Event camera (DVS)'], ['frame-camera', 'Frame camera'],
      ['silicon-cochlea', 'Silicon cochlea'], ['microphone', 'Microphone'],
      ['tactile-sensor', 'Tactile sensor'], ['chemical-sensor-array', 'Chemical sensor array'],
      ['imu-analog-sensor', 'IMU and analog sensors'], ['no-physical-sensor', 'No sensor (dataset or solver)'] ] },
    { label: 'Input representation', chips: [
      ['native-events', 'Native event stream'], ['frames-from-events', 'Frames reconstructed from events'],
      ['static-frames', 'Static frames'], ['time-series', 'Sampled time series'] ] } ] },

  { id: 'learn', n: 2, name: 'Learning path', sub: 'how the weights are obtained', rows: [
    { label: 'ANN-to-SNN', chips: [
      ['classical-conversion', 'Classical conversion'], ['low-latency-conversion', 'Low-latency conversion'],
      ['quant-aware-conversion', 'Quantization-aware conversion'], ['codesigned-conversion', 'Hardware co-designed conversion'] ] },
    { label: 'Direct and hybrid', chips: [
      ['direct-training-surrogate-gradient', 'Surrogate gradients'], ['spike-time-gradient-methods', 'Spike-time gradients'],
      ['local-learning-plasticity', 'Local learning and plasticity'], ['hand-designed-hybrid-finetuning', 'Hand-designed circuits'],
      ['hardware-in-the-loop-training', 'Hardware-in-the-loop'], ['hybrid-finetuning', 'Hybrid fine-tuning'] ] } ] },

  { id: 'code', n: 3, name: 'Representation', sub: 'what the spike train means', rows: [
    { label: 'Neural code', chips: [
      ['rate-coding', 'Rate coding'], ['ttfs', 'Time-to-first-spike (TTFS)'], ['phase-coding', 'Phase coding'],
      ['burst-coding', 'Burst coding'], ['population-coding', 'Population coding'], ['sigma-delta', 'Sigma-delta coding'],
      ['rank-order-coding', 'Rank order coding'], ['direct-input-encoding', 'Direct (constant-current) input'] ] },
    { label: 'Event payload', chips: [
      ['binary-spikes', 'Binary spikes'], ['signed-spikes', 'Signed spikes'], ['graded-spikes', 'Graded spikes'] ] } ] },

  { id: 'compute', n: 4, name: 'Computation', sub: 'the neuron and its execution contract', rows: [
    { label: 'Neuron model', chips: [
      ['if-neuron', 'Integrate-and-fire (IF)'], ['lif-neuron', 'Leaky IF (LIF)'], ['cuba-lif', 'Current-based LIF (CUBA)'],
      ['adaptive-neuron', 'Adaptive LIF (ALIF)'], ['multi-compartment', 'Multi-compartment'], ['pasc-if', 'PASC-IF'] ] },
    { label: 'Reset rule', chips: [
      ['reset-by-subtraction', 'Reset by subtraction (soft)'], ['reset-to-zero', 'Reset to zero (hard)'] ] },
    { label: 'Execution contract', chips: [
      ['sync-tick', 'Synchronous global tick'], ['async-events', 'Asynchronous event-driven'],
      ['analog-time', 'Analog continuous time'], ['single-pass', 'Single pass, T collapsed'] ] } ] },

  { id: 'sw', n: 5, name: 'Software stack', sub: 'in process order: train, export, compile, run', rows: [
    { label: 'Develop and train', chips: [
      ['spikingjelly', 'SpikingJelly'], ['snn-toolbox', 'SNN Toolbox'], ['snntorch', 'snnTorch'],
      ['norse', 'Norse'], ['sinabs', 'Sinabs'], ['rockpool', 'Rockpool'], ['lava', 'Lava'],
      ['lava-dl', 'Lava-DL'], ['hxtorch', 'hxtorch'], ['nengo', 'Nengo'], ['pynn', 'PyNN'],
      ['brian2', 'Brian2'], ['nest', 'NEST'], ['mlgenn', 'mlGeNN'], ['bidl', 'BIDL'],
      ['quantizeml', 'QuantizeML'], ['quartz', 'Quartz'] ] },
    { label: 'Export and interchange', chips: [
      ['nir', 'NIR'], ['lava-exchange', 'lava_exchange'], ['nir-exchange', 'nir_exchange'],
      ['backend-graph', 'Backend-specific graph'] ] },
    { label: 'Compile and map', chips: [
      ['nxtf', 'NxTF'], ['netx', 'NetX'], ['dynapcnn-mapper', 'DynapCNN mapper'],
      ['xylo-mapper', 'Xylo mapper'], ['spynnaker', 'sPyNNaker'], ['nengo-loihi', 'NengoLoihi'],
      ['cnn2snn', 'CNN2SNN'], ['ann2snn', 'ann2snn'],
      ['ttfs-cnn-to-snn-conversion', 'Custom TTFS conversion'], ['fenn-vector-program', 'FeNN vector program'] ] },
    { label: 'Run on device', chips: [
      ['nxsdk', 'NxSDK'], ['lava-runtime', 'Lava ProcessModels'], ['samna', 'samna'],
      ['spinnaker-runtime', 'SpiNNaker runtime'], ['akida-runtime', 'Akida runtime'],
      ['host-io', 'Host encoding and readout'],
      ['pytorch-cuda', 'PyTorch CUDA backend'], ['genn-cuda', 'GeNN generated CUDA'], ['nest-kernel', 'NEST kernel'],
      ['ttfs-mcu-firmware', 'Cortex-M deployment (TTFS)'], ['fenn-vivado-toolchain', 'FeNN soft core (Vivado)'] ] } ] },

  /* The hardware layer is grouped by what a run there can claim (data/target-kinds.json):
     a conventional processor, a model of the silicon, or the neuromorphic silicon itself.
     check-figure-map.py holds each chip's row to the target kind recorded for its node. */
  { id: 'hw', n: 6, name: 'Hardware', sub: 'where it actually runs', rows: [
    { label: 'Conventional processors', bucket: 'conventional', chips: [
      ['cpu-generic', 'CPU'], ['gpu-generic', 'GPU'], ['cortex-m-mcu', 'Cortex-M MCU'],
      ['riscv-accelerator', 'RISC-V accelerator'], ['northpole', 'NorthPole (NPU)'], ['akida', 'Akida (event NPU)'] ] },
    { label: 'Chip models and emulation', bucket: 'simulated', chips: [
      ['lava-loihi-sim', 'Lava Loihi simulator'], ['xylo-sim', 'Xylo simulator'], ['akida-sim', 'Akida software backend'],
      ['hxtorch-sim', 'hxtorch simulation'], ['fpga-truenorth-emulation', 'TrueNorth FPGA emulation'],
      ['apex', 'APEX (RTL)'], ['neuroflex', 'NeuroFlex (RTL)'] ] },
    { label: 'Synchronous digital', bucket: 'neuromorphic', chips: [
      ['loihi-1', 'Loihi 1'], ['loihi-2', 'Loihi 2'], ['spinnaker-1', 'SpiNNaker 1'],
      ['spinnaker-2', 'SpiNNaker 2'], ['truenorth', 'TrueNorth'], ['tianjic', 'Tianjic'],
      ['lynxi-ka200', 'Lynxi KA200'], ['xylo', 'Xylo'] ] },
    { label: 'Event-driven and analog', bucket: 'neuromorphic', chips: [
      ['speck', 'Speck'], ['dynapcnn', 'DYNAP-CNN'], ['brainscales-1', 'BrainScaleS-1'],
      ['brainscales-2', 'BrainScaleS-2'], ['dynap-se2', 'DYNAP-SE2'],
      ['innatera-pulsar', 'Innatera Pulsar'], ['morphic', 'MorphIC'] ] },
    { label: 'FPGA accelerators', bucket: 'neuromorphic', chips: [
      ['fpga', 'FPGA designs'], ['syncnn', 'SyncNN (FPGA)'], ['cerebron', 'Cerebron (FPGA)'] ] } ] },
];

/* Routes. `line` lists the chips on the path. `breakAt` names the chip where the chain
   snaps, and everything below it is unreachable by this route. `implied` chips are fixed
   by the route rather than chosen. */
const ROUTES = [
  { id: 'snntoolbox-loihi1', name: 'SNN Toolbox to Loihi 1', ev: 'E1', tk: 'neuromorphic', pc: '#2A8A7A', rec: true,
    story: 'A rate-coded converted MobileNet measured on physical Loihi 1 silicon at CIFAR-10 scale, reaching 8.52% error on 861 cores across 7 chips.',
    note: 'Historical. SNN Toolbox was last released on PyPI (0.6.0) in March 2021, its last GitHub release tag is v0.5.0 of June 2020, and its last code commit was in August 2022; the repository is not archived and took README-only commits in January 2023. Soft reset is an optional mode in the Intel bridge, not its default (reset_mode falls back to \'hard\'), it doubles the compartments per neuron, and the paper does not state which mode the 8.52% run used, so the line draws the hard reset. NxTF is Keras-native and its host repository carries a discontinuation notice. Loihi 1 is superseded.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-to-zero','sync-tick','snn-toolbox','nxtf','nxsdk','loihi-1'] },

  { id: 'snntoolbox-spinnaker', name: 'SNN Toolbox to SpiNNaker 1', ev: 'E1', tk: 'neuromorphic', pc: '#42647B',
    story: 'A converted Keras LeNet on a physical 48-chip machine, 98.20% on MNIST at roughly 0.4 s wall-clock per sample with 15 ms of simulated activity.',
    note: 'Nothing at CIFAR-10 scale or above was found on physical SpiNNaker silicon. The route runs the PyNN IF_curr_exp cell with a hard reset to zero and a 1000 ms membrane time constant, a current-based LIF that is effectively non-leaky over the 15 ms window. A timestep here is a timer interrupt, conventionally 1 ms, by default matched to real time.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','cuba-lif','reset-to-zero','sync-tick','snn-toolbox','spynnaker','spinnaker-runtime','spinnaker-1'] },

  { id: 'sinabs-speck', name: 'Sinabs to Speck', ev: 'E1', tk: 'neuromorphic', pc: '#237985', rec: true, live: true,
    story: 'The live conversion route that preserves reset by subtraction end to end, on hardware anyone can buy, measured at 3.36 us on Speck1 for a single event through nine 3x3 conv-and-pool layers at stride 1 and padding 1, pad to pad.',
    note: 'Sinabs from_model() defaults to MembraneSubtract(). Speck supports subtractive reset natively via return_to_zero=False. The IF label is the default; the optional leak is linear and driven by a slow clock. Speck has no BatchNorm operator, and DynapcnnNetwork folds BatchNorm into the preceding conv or linear layer automatically (merge_bn). A Demo Kit presold at $199, a price that comes from a June 2023 trade-press reprint of the SynSense release; no research-membership requirement is stated. Speck has no global clock, so T exists only at the raster-to-events boundary. The measured runs streamed external events and bypassed the on-die sensor, and the only classical-conversion run measured on Speck is N-MNIST at 86.17 percent; the gesture result on Speck was surrogate-gradient trained.',
    line: ['image-classification-static','event-camera','native-events','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','async-events','sinabs','dynapcnn-mapper','samna','speck'] },

  { id: 'rockpool-xylo', name: 'Rockpool to Xylo', ev: 'E1', tk: 'neuromorphic', pc: '#3F5FBF',
    story: 'Deployed quantized accuracy of 95.31 percent, with power measured on the HDK at 216 to 217 uW idle, 468 to 514 uW active and 251 to 298 uW dynamic, on audio and low-dimensional signals rather than vision.',
    note: 'Xylo documents a synchronous time-stepped architecture with a global dt, so T here is a genuine hardware tick. Reset is by subtraction as a fixed hardware property. The measured run used a simulated audio encoder with events streamed from the host in accelerated time, so the microphone chip is documented, not exercised. The readout is the membrane potential in training and any-spike detection at test, and only the input encoder is rate-like, so no neural-code chip is drawn. Same vendor as Speck, opposite time model.',
    line: ['keyword-spotting-audio','microphone','time-series','direct-training-surrogate-gradient','binary-spikes','lif-neuron','reset-by-subtraction','sync-tick','rockpool','xylo-mapper','samna','xylo'] },

  { id: 'spikingjelly-lava', name: 'SpikingJelly to Lava to Loihi 2', ev: 'BLOCKED', tk: 'neuromorphic', pc: '#C0392B',
    story: 'The obvious modern route, and it does not complete.',
    note: 'The recipe drawn is SpikingJelly\'s rate-coding ReLU-to-IF conversion with max or percentile threshold calibration; the QCFS-based recipe\'s ActivationAwareIFNode is rejected by lava_exchange with NotImplementedError instead. Three independent blockers. The first is structural, since to_lava_blocks accepts a flat list, tuple or nn.Sequential while the recipe returns an FX GraphModule with VoltageScaler modules, so the converted network fails on shape before any neuron is inspected. Then lava_exchange raises ValueError("lava only supports for v_reset == 0!") at four call sites, plus an assertion in CubaLIFNode.__init__, rejecting the soft-reset neurons the rate-coding recipe produces by default. Then layer dispatch covers only Linear, Conv2d, AvgPool2d and Flatten, so a VGG MaxPool fails there; a ResNet skip connection fails for the structural reason, not in dispatch. Intel archived all Lava repositories on 13 May 2026.',
    breakAt: 'lava-exchange',
    breakWhy: 'The converted network fails on shape before any neuron is inspected, then its soft reset is rejected, then its layers are not dispatched. The conversion produced a network the framework’s own exporter will not accept.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','lava-exchange','netx','lava-runtime','loihi-2'] },

  { id: 'spikingjelly-nxtf', name: 'SpikingJelly to NxTF to Loihi 1', ev: 'BLOCKED', tk: 'neuromorphic', pc: '#C0392B',
    story: 'Substituting the maintained framework into the route that actually reached silicon, and it does not connect.',
    note: 'The recipe drawn is SpikingJelly\'s rate-coding ReLU-to-IF conversion with max or percentile threshold calibration; the QCFS-based recipe\'s ActivationAwareIFNode is rejected by lava_exchange with NotImplementedError. NxTF inherits from the Keras Model and Layer interface. No bridge from a PyTorch SNN framework exists; SNN Toolbox ingests PyTorch ANNs through ONNX, and the only automated bridge into NxTF was specific to SNN Toolbox. The host repository carries a discontinuation notice, and INRC has redirected users to Lava since 2022. NxTF on Loihi 2 was not found.',
    breakAt: 'nxtf',
    breakWhy: 'NxTF is Keras-native and SpikingJelly is PyTorch. The framework boundary was only ever crossed automatically by an SNN-Toolbox-specific bridge that no longer has a maintained counterpart.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','nxtf','nxsdk','loihi-1'] },

  { id: 'spikingjelly-nir', name: 'SpikingJelly to NIR', ev: 'BLOCKED', tk: 'neuromorphic', pc: '#C0392B',
    story: 'The portability route, blocked by an exporter that refuses to export what the specification does not distinguish.',
    note: 'The recipe drawn is SpikingJelly\'s rate-coding ReLU-to-IF conversion with max or percentile threshold calibration; the QCFS-based recipe\'s ActivationAwareIFNode is rejected by lava_exchange with NotImplementedError. NIR defines seventeen primitives, six of them neuron models (I, IF, LI, LIF, CubaLI, CubaLIF). All three spiking ones (IF, LIF, CubaLIF) document reset as v = v_reset when a spike fires, and no NIR field distinguishes reset by subtraction from reset to a value, so which one a backend applies is left to the backend. SpikingJelly nir_exchange raises NotImplementedError("NIR does not distinguish soft reset.") whenever v_reset is None, a deliberate and conservative refusal; other exporters (snnTorch, Sinabs) export the same neurons with v_reset = 0 and leave the discretization to the importer, so the block is SpikingJelly\'s exporter policy.',
    breakAt: 'nir',
    breakWhy: 'The broadest interchange format in the ecosystem does not distinguish reset by subtraction from reset to a value, and SpikingJelly’s exporter refuses rather than guess.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','nir-exchange','nir','lava-dl','netx','lava-runtime','loihi-2'] },

  { id: 'quantizeml-akida', name: 'QuantizeML to CNN2SNN to Akida', ev: 'E1', tk: 'event NPU', pc: '#6D4C9F',
    story: 'A shipping commercial processor, where the conversion folds to a static threshold and the temporal dimension disappears.',
    note: 'CNN2SNN computes y = x / act_step for Akida 1.0 layers, with a static threshold absorbing BatchNorm scale and shift, folded once at conversion time. No membrane potential carries across timesteps and no T is exposed. One paper (Ziegler et al.) describes it as squashing the rate-code approximation of ReLU into one time step, and a second (Lunghi et al.) says the converted model reduces the computation to a single time step. BrainChip states 4-bit or 8-bit quantized inputs to its layers, so the events are graded rather than binary, and no BrainChip source names a reset rule; the threshold is a static comparator applied in a single pass. The rank-order-coding heritage is genuine as input-stage heritage, but no source shows order sensitivity operating in converted hidden layers, so no neural-code chip is drawn.',
    line: ['image-classification-static','frame-camera','static-frames','quant-aware-conversion','graded-spikes','if-neuron','single-pass','quantizeml','cnn2snn','akida-runtime','akida'] },

  { id: 'quartz-loihi', name: 'Quartz to Loihi 1', ev: 'E1', tk: 'neuromorphic', pc: '#A97818',
    story: 'A new method that reached silicon, by abandoning rate coding for TTFS.',
    note: 'Measured static, dynamic and total power, latency and energy per inference on a physical Nahuku 32 board, compared against the published NxTF numbers on the same platform (a different board, SDK version and network). The authors’ released implementation uses nxSDK 0.9.8 directly, as its code README states, while the paper\'s measurements were taken with NxSDK 1.0.0. The CIFAR-10 preferred energy-delay product uses an estimated static power, and the paper\'s 564 uJ energy label is a unit error for about 563 mJ.',
    line: ['image-classification-static','frame-camera','static-frames','codesigned-conversion','ttfs','binary-spikes','if-neuron','reset-to-zero','sync-tick','quartz','nxsdk','loihi-1'] },

  { id: 'slayer-loihi2', name: 'Lava-DL SLAYER to Loihi 2', ev: 'E1', tk: 'neuromorphic', pc: '#98622C',
    story: 'Direct training with a vendor toolchain, reaching silicon where rate-coded conversion did not.',
    note: 'The workload drawn is the PilotNet sigma-delta network of Shrestha et al., Table 1, a steering regression from dashboard-camera frames measured on an Oheo Gulch single-chip Loihi 2 system with Lava-DL 0.4.0 and Lava 0.8.0; the int8 network ran at 0.09 mJ per inference without I/O, 1.21 ms latency and 7403.80 samples per second. A sigma-delta ReLU unit has no membrane or reset, so no neuron or reset chip is drawn, and steering regression has no task chip. The PilotNet LIF result is a vendor tutorial notebook, not a peer-reviewed measurement. Intel moved Loihi 2 toward graded sigma-delta payloads, citing Loihi 1 experience that rate-coded converted models suffer long latencies and inter-chip congestion. An ANN-to-sigma-delta conversion (Brehove et al.) was separately measured on a 16-chip Loihi 2 board. Intel archived the Lava repositories on 13 May 2026.',
    line: ['frame-camera','static-frames','direct-training-surrogate-gradient','sigma-delta','graded-spikes','sync-tick','lava-dl','netx','lava-runtime','loihi-2'] },

  /* Five physical routes onto conventional targets. Each is E1 on a processor that is not
     a spiking substrate, so what it measures is a program's speed, not a chip's contract. */
  { id: 'spikingjelly-gpu', name: 'SpikingJelly to a GPU', ev: 'E1', tk: 'GPU', pc: '#2F5F9E',
    story: 'The framework\'s own benchmark, timed end to end on an NVIDIA A100, where training a Spiking ResNet-18 with surrogate gradients reached up to 11x the speed of Norse (8x over snnTorch) at T = 32 and inference at ANN2SNN-scale T up to 2x.',
    note: 'A conventional target. The paper states LIF neurons at SpikingJelly defaults with hard reset to zero, fed random 3x224x224 tensors at batch size 16 with mixed precision and no dataset. The training benchmark ran SpikingJelly\'s CuPy-compiled LIF kernels alongside PyTorch CUDA tensor operations, so nothing about a spiking substrate is measured. Training-iteration time was taken at T = 2, 4, 8, 16 and 32, and the ANN2SNN inference run is the same LIF network timed at T = 128 to 1024 with only T = 128 reported, on an Ubuntu 18.04 server with an Intel Xeon Silver 4210R host and 256 GB of memory.',
    line: ['direct-training-surrogate-gradient','lif-neuron','reset-to-zero','sync-tick','spikingjelly','pytorch-cuda','gpu-generic'] },

  { id: 'mlgenn-gpu', name: 'mlGeNN to GeNN to a GPU', ev: 'E1', tk: 'GPU', pc: '#5C7A99',
    story: 'A converted VGG-16 and ResNet-20 simulated as GeNN-generated CUDA code on a 12 GB Titan V, with rate-based and few-spike conversion both evaluated on CIFAR-10 and only few-spike conversion run at ImageNet scale, on VGG-16 and ResNet-34.',
    note: 'A conventional target. On CIFAR-10 the converted VGG-16 ran 2.5x faster than BindsNET, the few-spike ResNet-20 a little over 2x slower than the original TensorFlow ANN at large batch sizes (at batch size 1 the same network is 3.5x faster than the ANN), and the fastest rate-based model over 100x slower than that ANN. Rate-based conversion used T = 2500 for VGG-16 and T = 1000 for ResNet-20; few-spike conversion used K = 10 and K = 8. The IF neurons use a hard reset to zero, stated in the paper and in ml_genn 1.0\'s if_neurons.py.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','if-neuron','reset-to-zero','sync-tick','mlgenn','genn-cuda','gpu-generic'] },

  { id: 'nest-cpu', name: 'PyNN and NEST to a CPU cluster', ev: 'E1', tk: 'CPU', pc: '#2F6F5E',
    story: 'A full-scale cortical microcircuit of about 80,000 LIF neurons and 0.3 billion synapses, simulated by NEST on a 32-node Intel Xeon cluster and compared head to head with SpiNNaker in the same paper.',
    note: 'A conventional target. NEST runtime saturated around 3x real time with hybrid MPI and multithreading, and its lowest total energy came at about 144 threads and a 4.6x slowdown, where NEST and SpiNNaker had comparable energy per synaptic event. NEST used a 0.1 ms integration step. A separate performance report scales a later NEST-5g development build (a May 2017 snapshot) running the hpc_benchmark balanced random network from an SLI script under weak scaling to 82,944 nodes of the K computer, not the NEST 2.8 PyNN microcircuit run; there the connect phase stays near 80 seconds while prepare and run grow with node count. Not a classification workload; the record names no dataset, neural code or learning rule.',
    line: ['no-physical-sensor','lif-neuron','sync-tick','pynn','nest','nest-kernel','cpu-generic'] },

  { id: 'ttfs-cortex-m4', name: 'TTFS conversion to a Cortex-M4 MCU', ev: 'E1', tk: 'MCU', pc: '#B5651D',
    story: 'A quantized 8-bit CNN converted with time-to-first-spike encoding among others and deployed on the ARM Cortex-M4 MCU, where Table 1 reports 48 microjoules and about 6 ms per inference at 87.9%, with the task unstated, against an analog Innatera chip in the same paper.',
    note: 'A conventional target. Energy, latency and accuracy were read with an external power analyzer under the MLPerf Tiny windowed protocol. The 8-bit CNN on the same MCU took 60 microjoules at 89.5%, and the same network on the Innatera SNP analog chip 24 microjoules and about 0.8 ms at 88.2%, so the energy reduction is 20 percent by the paper\'s own numbers, where the paper writes 23. The paper names TTFS among other encodings and also firing-rate control, and never states which encoding the measured digital SNN used. The pipeline is the paper\'s own, with layer-wise normalization and threshold calibration; CMSIS-NN is named only as a comparator framework, SNN Toolbox is not mentioned, and the part number is not named. The paper names CIFAR-10 and Google Speech Commands as example benchmarks and an 8-bit MobileNetV2 as its example architecture, but Table 1 is attributed to none of them, so no task chip is drawn. The source is weak in stated ways, a proposed evaluation framework whose Table 1 holds round values without the promised confidence intervals, gives latency as 6.00 ms and 6.1 ms in different sections, and states no neuron model or timestep count.',
    line: ['ttfs','ttfs-cnn-to-snn-conversion','ttfs-mcu-firmware','cortex-m-mcu'] },

  { id: 'fenn-riscv', name: 'FeNN vector program to a RISC-V soft core', ev: 'E1', tk: 'RISC-V', pc: '#8C4A6B',
    story: 'A recurrent spiking spoken-digit classifier stepped by a custom RISC-V vector instruction set on a soft core synthesized onto a Kria KV260 FPGA, reported significantly faster than a similar model on Loihi and twice as fast as an embedded GPU at half the energy.',
    note: 'A conventional target in this survey\'s vocabulary, a programmable RISC-V processor rather than a fixed-function spiking accelerator, even though it is realized on an FPGA. FeNN uses adaptive LIF neurons with subtractive reset and 16-bit fixed-point arithmetic with stochastic rounding. The SNN itself is RISC-V assembly emitted by a host-side C++ JIT assembler on the Kria\'s Cortex-A53; Vivado synthesizes the soft core once. The Loihi comparison is against the time Rao et al. report for a similar ALIF RSNN on Loihi, not a measurement in the FeNN paper, and the energy comparison is whole-board mains energy of the KV260 against a Jetson Orin Nano, both under desktop Linux. The SHD input is cochlea-model spike trains. FeNN-DMA, the follow-on system-on-chip, measured simulation throughput of a balanced random network of up to 16,000 neurons from on-chip performance counters and accuracy on Spiking Heidelberg Digits, N-MNIST and Braille; only its 0.53 W figure is a vectorless Vivado estimate rather than a board reading, while the 175 MHz clock and the LUT and FF counts are implementation results. The route is drawn under keyword spotting, the nearest task chip, while the record\'s task is spoken-digit classification.',
    line: ['keyword-spotting-audio','adaptive-neuron','reset-by-subtraction','sync-tick','fenn-vector-program','fenn-vivado-toolchain','riscv-accelerator'] },

];

/* The three hardware buckets, named as in data/target-kinds.json. Their colors live in
   figure.css; check-figure-map.py holds both the names and the colors to that file. */
const BUCKETS = [
  ['conventional', 'The claim\'s target is a conventional processor, whatever software steps the network.'],
  ['simulated', 'The claim\'s target is a model of neuromorphic hardware that is not the silicon.'],
  ['neuromorphic', 'The claim\'s target is fabricated neuromorphic silicon, or a custom spiking accelerator on an FPGA measured as its own target.'],
];

/* Seams sit between layers and name what is lost crossing them. */
const SEAMS = {
  code:    [['S3', 'Input encoding and readout', 'Nearly all modern low-T conversion feeds the real-valued image as constant current, which makes layer one effectively an ANN layer. Readout cost and the decision window are rarely inside the reported measurement.']],
  compute: [['S4', 'Time model', 'T means a different thing under a synchronous tick, an asynchronous event stream, and analog continuous time. Software timesteps do not map one to one onto hardware steps.'],
            ['S5', 'Per-layer horizons', 'No framework expresses a per-layer timestep horizon in one forward pass. TrueNorth, Loihi, Loihi 2 and Tianjic all advance through a single global barrier.']],
  sw:      [['S1', 'Operator coverage', 'lava_exchange dispatches only Linear, Conv2d, AvgPool2d and Flatten. Speck has no BatchNorm operator, so the DynapCNN mapper folds it into the preceding layer. Akida caps Dense input at 57,334 features and requires bounded ReLU.'],
            ['S2', 'Reset semantics', 'The sharpest seam. Conversion requires reset by subtraction, worth roughly twenty accuracy points. NIR does not distinguish it from reset to a value. SpikingJelly rejects it at both export paths. Loihi needs a two-compartment workaround that doubles neuron count.']],
};

const RAIL_L = [
  ['Accuracy', 'What every reduction below trades against, and the reason the conversion literature exists.'],
  ['Latency', 'Set by the time model, the horizon T, and how much spike traffic the fabric carries per inference.'],
  ['Energy', 'Static and leakage power dominate measured energy on synchronous chips, so cutting T does not cut energy proportionally.'],
  ['Availability', 'A chip you cannot obtain is a different answer from a chip that does not suit. Access gates and dormant toolchains belong on this axis.'],
];

const RAIL_R = [
  ['R1', 'Measurement', 'A SynOps figure is an operation-count ratio under an unstated hardware model, not joules. Boundary choices alone produce 14x swings for the identical chip and network.'],
  ['R2', 'Toolchain decay', 'SNN Toolbox last released March 2021. Intel archived all Lava repositories on 13 May 2026 with no maintenance and no patches accepted. The only toolchain that reached silicon is dormant.'],
  ['R3', 'Portability', 'NIR reaches nine simulators and five hardware platforms, turning m x n integrations into m + n. Its primitive set still does not distinguish the one semantics this literature depends on from reset to a value.'],
  ['R4', 'Two populations', 'The division of labor that no survey states. Algorithm papers advance accuracy at low T and do not deploy; none of the algorithm-population records reaches physical silicon, and Section 13.6, Population Counts, counts them. Every confirmed instance of a new method reaching silicon abandons rate coding.'],
];

/* ---------- state ---------- */
const sel = new Set();
let active = null;
let tipEl = null;
let evidence = null;

const $ = (s, r = document) => r.querySelector(s);
const all = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ---------- build ---------- */
function build() {
  const layers = $('#nstk-layers');
  const rowHtml = (L, r) => `
      <div class="nstk-row${L.rows.length === 1 ? ' nstk-row-plain' : ''}"${r.bucket ? ` data-bucket="${r.bucket}"` : ''}>
        ${L.rows.length > 1 ? `<span class="nstk-rowlabel" data-row="${esc(r.label)}">${esc(r.label)}</span>` : ''}
        <span class="nstk-rowchips">${r.chips.map(([id, t]) =>
          `<span class="nstk-chip" data-k="${id}" tabindex="0" role="button">${esc(t)}</span>`).join('')}</span>
      </div>`;
  // Rows that share a bucket sit inside one band, so the hardware layer reads as three
  // groups rather than five rows.
  const groupRows = (L) => {
    const out = [];
    L.rows.forEach(r => {
      const last = out[out.length - 1];
      if (r.bucket && last && last.bucket === r.bucket) last.rows.push(r);
      else out.push({ bucket: r.bucket || null, rows: [r] });
    });
    return out.map(g => g.bucket
      ? `<div class="nstk-bucket" data-bucket="${g.bucket}">${g.rows.map(r => rowHtml(L, r)).join('')}</div>`
      : g.rows.map(r => rowHtml(L, r)).join('')).join('');
  };
  layers.innerHTML = LAYERS.map(L => {
    const rows = groupRows(L);
    const seam = (SEAMS[L.id] || []).map(([n, t, d]) =>
      `<span class="nstk-pin" data-pin="${n}" data-tip="<b>${n} ${esc(t)}.</b> ${esc(d)}" tabindex="0" role="button">${n}</span>`).join('');
    const legend = L.id === 'hw' ? `<div class="nstk-legend" aria-label="How the hardware layer is grouped">
        <span class="nstk-legend-lead">What a run there can claim</span>
        ${BUCKETS.map(([b, meaning]) =>
          `<span class="tk nstk-bkey" data-bucket="${b}" data-tip="<b>${esc(b)}.</b> ${esc(meaning)}" tabindex="0">${esc(b)}</span>`).join('')}
      </div>` : '';
    return `<div class="nstk-layer" data-layer="${L.id}">
      <div class="nstk-label" data-layer-label="${L.id}" tabindex="0" role="button">
        <span class="nstk-step">${L.n}</span><span class="nstk-name">${esc(L.name)}</span><span class="nstk-sub">${esc(L.sub)}</span>
      </div>
      <div class="nstk-chips">${rows}</div>
      ${seam ? `<div class="nstk-seam">${seam}</div>` : ''}
    </div>${legend}`;
  }).join('');

  $('#nstk-rail-l').innerHTML = RAIL_L.map(([t, d]) =>
    `<span class="nstk-rail-cell" data-tip="<b>${esc(t)}.</b> ${esc(d)}">${esc(t)}</span>`).join('');
  $('#nstk-rail-r').innerHTML = RAIL_R.map(([n, t, d]) =>
    `<span class="nstk-rail-cell" data-tip="<b>${n} ${esc(t)}.</b> ${esc(d)}" tabindex="0" role="button">${n} ${esc(t)}</span>`).join('');

  const quick = ['Image classification', 'Gesture recognition', 'Keyword spotting', 'Robotics and control',
                 'Event camera (DVS)', 'Frame camera', 'Rate coding', 'Reset by subtraction (soft)',
                 'SpikingJelly', 'Loihi 2', 'Speck', 'Akida'];
  $('#nstk-quick').innerHTML = quick.map(q => `<button type="button" class="nstk-quick" data-q="${esc(q)}">${esc(q)}</button>`).join('');

  tipEl = document.createElement('div');
  tipEl.className = 'nstk-tip';
  document.body.appendChild(tipEl);
}

/* ---------- ranking ---------- */
function matching() {
  let rs = ROUTES.filter(r => Array.from(sel).every(k => r.line.includes(k)));
  const q = ($('#nstk-q').value || '').trim().toLowerCase();
  if (q) {
    rs = rs.filter(r => {
      if (r.name.toLowerCase().includes(q) || r.story.toLowerCase().includes(q)) return true;
      return r.line.some(k => (label(k) || '').toLowerCase().includes(q));
    });
  }
  // A completing route outranks a broken one, and a recommended route outranks the rest.
  return rs.sort((a, b) => (!!a.breakAt - !!b.breakAt) || (!!b.rec - !!a.rec) || (!!b.live - !!a.live));
}

function label(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id, t] of r.chips) if (id === k) return t;
  return null;
}
function layerOf(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id] of r.chips) if (id === k) return L.id;
  return null;
}
/* The drawn line anchors once per ROW, not once per layer, so that the traversal inside
   the software stack (train, export, compile, run) is visible rather than collapsed. */
function rowOf(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id] of r.chips) if (id === k) return `${L.id}::${r.label}`;
  return null;
}

/* ---------- render ---------- */
function render() {
  const rs = matching();
  const route = rs[0] || null;
  active = route;
  const fig = $('#nstk-fig');
  const grid = $('#nstk-grid');

  all('.nstk-chip').forEach(c => c.classList.remove('nstk-line', 'nstk-branch', 'nstk-implied', 'nstk-break'));
  all('.nstk-rowlabel').forEach(l => l.classList.remove('nstk-on'));
  all('.nstk-layer').forEach(l => l.classList.remove('nstk-bridge'));

  // Nothing is drawn until the reader asks a question. With no chip chosen and
  // no text in the box the grid is bare, the panel is empty, and the figure
  // resets to that state on every reload.
  const constrained = sel.size > 0 || !!($('#nstk-q').value || '').trim();
  const tracing = constrained && !!route;
  if (!constrained) active = null;
  fig.classList.toggle('nstk-tracing', tracing);
  $('#nstk-clear').hidden = !constrained;
  all('.nstk-quick').forEach(b => b.classList.toggle('nstk-active', sel.has(keyFor(b.dataset.q))));

  if (tracing) {
    grid.style.setProperty('--pc', route.pc);
    const cut = route.breakAt ? route.line.indexOf(route.breakAt) : route.line.length - 1;
    route.line.forEach((k, i) => {
      const el = $(`.nstk-chip[data-k="${k}"]`);
      if (!el) return;
      if (route.breakAt && i > cut) el.classList.add('nstk-implied');
      else if (route.breakAt && i === cut) el.classList.add('nstk-break');
      else el.classList.add('nstk-line');
      const lab = el.closest('.nstk-row')?.querySelector('.nstk-rowlabel');
      if (lab) lab.classList.add('nstk-on');
    });
    // Alternatives reachable from the current constraints read as branches.
    const alt = new Set();
    rs.slice(1).forEach(r => r.line.forEach(k => { if (!route.line.includes(k)) alt.add(k); }));
    alt.forEach(k => {
      const el = $(`.nstk-chip[data-k="${k}"]`);
      if (el && !el.classList.contains('nstk-line') && !el.classList.contains('nstk-break') && !el.classList.contains('nstk-implied')) el.classList.add('nstk-branch');
    });
  }

  // Highlighting route chips changes their font weight and can reflow rows.
  // Measure the settled layout before drawing the SVG path.
  requestAnimationFrame(() => drawPath(active, true));
  panel(rs, tracing, constrained);
}

function keyFor(text) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id, t] of r.chips) if (t === text) return id;
  return text;
}

/* ---------- overlay ---------- */
const reducedMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
const svgEl = (tag, attrs) => {
  const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
};
/* The route is traced from the first chip downward when the reader chooses
   something, the way the QuantizationSurvey's map traces its route. A redraw
   after a resize repaints the finished line without replaying the trace. */
function drawPath(route, animate) {
  const svg = $('#nstk-overlay');
  svg.innerHTML = '';
  if (!route) return;
  const gb = $('#nstk-grid').getBoundingClientRect();
  const cut = route.breakAt ? route.line.indexOf(route.breakAt) : route.line.length - 1;

  const pts = [];
  const seen = new Set();
  route.line.forEach((k, i) => {
    if (i > cut) return;
    const el = $(`.nstk-chip[data-k="${k}"]`);
    if (!el) return;
    const row = rowOf(k);
    if (seen.has(row)) return;      // one anchor per row keeps the line readable
    seen.add(row);
    const b = el.getBoundingClientRect();
    pts.push([b.left - gb.left + b.width / 2, b.top - gb.top + b.height / 2]);
  });
  if (pts.length < 2) return;

  // An S-curve between rows keeps the line vertical where it leaves and enters a chip.
  const f = n => n.toFixed(1);
  const d = pts.map((p, i) => {
    if (!i) return `M ${f(p[0])} ${f(p[1])}`;
    const [ax, ay] = pts[i - 1];
    const my = f((ay + p[1]) / 2);
    return `C ${f(ax)} ${my} ${f(p[0])} ${my} ${f(p[0])} ${f(p[1])}`;
  }).join(' ');
  const halo = svgEl('path', { class: 'nstk-path-halo', d });
  const path = svgEl('path', { class: 'nstk-path', style: `stroke:${route.pc}`, d });
  svg.appendChild(halo); svg.appendChild(path);

  const tail = [];
  if (route.breakAt) {
    const [x, y] = pts[pts.length - 1];
    tail.push(svgEl('path', { class: 'nstk-path-broken', d: `M ${f(x)} ${f(y)} L ${f(x)} ${f(y + 42)}` }));
    const cx = x, cy = y + 52;
    tail.push(svgEl('path', { class: 'nstk-breakmark',
      d: `M ${f(cx - 7)} ${f(cy - 7)} L ${f(cx + 7)} ${f(cy + 7)} M ${f(cx + 7)} ${f(cy - 7)} L ${f(cx - 7)} ${f(cy + 7)}` }));
    tail.forEach(e => svg.appendChild(e));
  }

  if (animate && !reducedMotion) {
    const len = path.getTotalLength();
    const dur = Math.min(1.5, 0.35 + len / 1100);
    [halo, path].forEach(e => { e.style.transition = 'none'; e.style.strokeDasharray = len; e.style.strokeDashoffset = len; });
    tail.forEach(e => { e.style.transition = 'none'; e.style.opacity = '0'; });
    // The nodes were inserted this tick; their start state settles on the next
    // frame, and setting the target before then makes the value snap.
    requestAnimationFrame(() => {
      [halo, path].forEach(e => { e.style.transition = `stroke-dashoffset ${dur}s ease-out`; e.style.strokeDashoffset = '0'; });
      tail.forEach(e => { e.style.transition = `opacity 0.25s ease-out ${(dur * 0.7).toFixed(2)}s`; e.style.opacity = '1'; });
    });
  }
}

function routeSources(route) {
  if (!evidence) return '';
  const ids = new Set(route.line);
  const sources = new Map(evidence.sources.map(s => [s.id, s]));
  const ordered = [];
  const seen = new Set();
  const edges = evidence.edges.filter(e =>
    ids.has(e.from) && ids.has(e.to) &&
    (layerOf(e.from) === 'sw' || layerOf(e.to) === 'hw' || e.to === route.breakAt));
  // Put the chip-facing edge first, then the software handoffs. Every displayed
  // link is attached to an edge that the highlighted route actually traverses.
  edges.sort((a, b) =>
    (b.to === route.line[route.line.length - 1]) - (a.to === route.line[route.line.length - 1]));
  edges.forEach(e => (e.sources || []).forEach(id => {
    const src = sources.get(id);
    if (src && src.url && !seen.has(id)) { seen.add(id); ordered.push(src); }
  }));
  if (!ordered.length) return '';
  return `<details class="nstk-sources"><summary>Sources for the highlighted route (${ordered.length})</summary>
    <ul>${ordered.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a> <span>${esc(s.type || 'source')}</span></li>`).join('')}</ul>
  </details>`;
}

/* ---------- panel ---------- */
/* The target's chip word, one vocabulary with the prose and Table 1 (data/target-kinds.json). */
function tkChip(route) {
  if (!route.tk) return '';
  const css = route.tk.toLowerCase().replace(/ /g, '-');
  return `<span class="tk tk-${css}" title="target kind">${esc(route.tk)}</span>`;
}
function panel(rs, tracing, constrained) {
  const p = $('#nstk-panel');
  if (!constrained) { p.innerHTML = ''; return; }
  if (!tracing) {
    p.innerHTML = `<div class="nstk-guide">No documented route carries that combination. Clear a constraint to widen the question.</div>`;
    return;
  }
  const r = rs[0];
  if (!r) return;

  const cut = r.breakAt ? r.line.indexOf(r.breakAt) : r.line.length - 1;
  const chain = r.line.map((k, i) => {
    const t = label(k) || k;
    const cls = (r.breakAt && i === cut) ? 'nstk-step-chip nstk-step-break' : 'nstk-step-chip';
    const arr = i < r.line.length - 1 ? `<span class="nstk-arr${(r.breakAt && i === cut) ? ' nstk-arr-break' : ''}">${(r.breakAt && i === cut) ? '×' : '→'}</span>` : '';
    return `<span class="${cls}">${esc(t)}</span>${arr}`;
  }).join('');

  const others = rs.slice(1).map(o =>
    `<li class="nstk-route" data-route="${o.id}" style="--pc:${o.pc}" tabindex="0" role="button">
       <span class="nstk-rhead"><b>${esc(o.name)}</b><span class="nstk-evid${o.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${o.pc}">${o.ev}</span>${tkChip(o)}</span>
       <span class="nstk-rstory">${esc(o.story)}</span></li>`).join('');

  p.innerHTML = `
    <div class="nstk-ph" style="--pc:${r.pc}">
      <span class="nstk-dot" style="--pc:${r.pc}"></span><b>${esc(r.name)}</b>
      <span class="nstk-evid${r.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${r.pc}">${r.ev}</span>${tkChip(r)}
      ${r.live ? '<span class="nstk-evid" style="--pc:#237985">live route</span>' : ''}
    </div>
    <div class="nstk-pbody" style="--pc:${r.pc}">
      <div class="nstk-steps">${chain}</div>
      <p class="nstk-note">${esc(r.story)}</p>
      ${r.breakAt ? `<p class="nstk-break-note"><b>Breaks at ${esc(label(r.breakAt) || r.breakAt)}.</b> ${esc(r.breakWhy)}</p>` : ''}
      <p class="nstk-note">${esc(r.note)}</p>
      ${routeSources(r)}
      ${others ? `<ul class="nstk-routes">${others}</ul>` : ''}
      <p class="nstk-legendnote">
        <span class="nstk-key nstk-line"></span> on the route &nbsp;
        <span class="nstk-key nstk-branch"></span> a branch still open &nbsp;
        <span class="nstk-key nstk-implied"></span> fixed by the route, or unreachable past a break &nbsp;
        <span class="nstk-key nstk-break"></span> where the chain snaps
      </p>
    </div>`;
}

/* ---------- tooltip ---------- */
function tipOn(el) {
  const t = el.dataset.tip; if (!t) return;
  tipEl.innerHTML = t; tipEl.classList.add('nstk-tip-on');
  const b = el.getBoundingClientRect();
  const w = Math.min(300, window.innerWidth - 24);
  tipEl.style.left = Math.max(12, Math.min(b.left, window.innerWidth - w - 12)) + 'px';
  tipEl.style.top = (b.bottom + 8) + 'px';
}
const tipOff = () => tipEl.classList.remove('nstk-tip-on');

/* ---------- events ---------- */
function wire() {
  document.addEventListener('click', e => {
    const chip = e.target.closest('.nstk-chip');
    if (chip && !chip.classList.contains('nstk-implied')) {
      const k = chip.dataset.k;
      sel.has(k) ? sel.delete(k) : sel.add(k);
      render(); return;
    }
    const q = e.target.closest('.nstk-quick');
    if (q) { const k = keyFor(q.dataset.q); sel.has(k) ? sel.delete(k) : sel.add(k); render(); return; }
    const ro = e.target.closest('.nstk-route');
    if (ro) { const r = ROUTES.find(x => x.id === ro.dataset.route); if (r) { sel.clear(); r.line.forEach(k => sel.add(k)); render(); } return; }
    if (e.target.closest('#nstk-clear')) { sel.clear(); $('#nstk-q').value = ''; render(); return; }
  });

  $('#nstk-q').addEventListener('input', render);

  document.addEventListener('mouseover', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('mouseout', e => { if (e.target.closest('[data-tip]')) tipOff(); });
  document.addEventListener('focusin', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('focusout', tipOff);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { sel.clear(); $('#nstk-q').value = ''; render(); }
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList?.contains('nstk-chip')) { e.preventDefault(); e.target.click(); }
  });
  window.addEventListener('resize', () => drawPath(active && $('#nstk-fig').classList.contains('nstk-tracing') ? active : null, false));
}

$('#nstk-q').value = '';
build(); wire(); render();
window.addEventListener('load', () => drawPath(active, false));
fetch('data/evidence-stack.json')
  .then(response => { if (!response.ok) throw new Error('evidence registry unavailable'); return response.json(); })
  .then(data => { evidence = data; render(); })
  .catch(() => { /* The figure still works when opened without the local server. */ });
