#!/usr/bin/env python3
"""Build the versioned vendor-grounded platform capability registry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data/platform-capabilities.json"
REVIEWED_ON = "2026-09-16"

FIELDS = (
    "graph_operators",
    "neuron_dynamics",
    "synaptic_dynamics_delays",
    "threshold_reset",
    "neural_code_payload",
    "encoder_decoder",
    "numeric_precision",
    "time_termination",
    "connectivity_routing",
    "plasticity_state",
    "host_operations",
)


def field(
    status: str,
    requirement: str,
    detail: str,
    locator: str,
    source_id: str | None = None,
) -> dict[str, str]:
    result = {
        "capability_status": status,
        "contract_requirement": requirement,
        "support_detail": detail,
        "source_locator": locator,
    }
    if source_id is not None:
        result["official_technical_source_id"] = source_id
    return result


PLATFORMS: tuple[dict[str, object], ...] = (
    {
        "platform_id": "loihi-1",
        "manufacturer": "Intel",
        "chip_generation": "Loihi 1",
        "route_ids": ["snn-toolbox-to-nxtf", "nxtf-to-nxsdk", "nxsdk-to-loihi1"],
        "route_state": "physical",
        "official_technical_source_id": "loihi2",
        "document_date": "2021-09-30",
        "document_version": "Intel Loihi 2 technology brief, September 2021",
        "toolchain_version": "NxSDK 0.9.5 through archived NxTF",
        "mapper_limits": "NxTF lowers supported Keras-derived layers to fixed Loihi 1 compartment, axon, synapse, and routing resources. Soft reset consumes two compartments per logical neuron.",
        "precision_constraints": "The official comparison records fixed 24-byte neuron allocation. The Loihi architecture paper reports signed synaptic weights up to 9 bits.",
        "routing_constraints": "Spike messages traverse the asynchronous mesh. Multi-chip execution is synchronized by barrier messages and is sensitive to congestion.",
        "host_responsibilities": "The host performs conversion, compilation, placement, loading, input orchestration, monitoring, and readout through the discontinued NxSDK stack.",
        "access_path": "Historical INRC research access only. Loihi systems were not commercial products.",
        "fields": {
            "graph_operators": field("transformed", "Lower a converted feedforward graph to Loihi 1 resources.", "Loihi 1 exposes neuron cores rather than a native deep-learning operator set. NxTF performed the graph-to-compartment transformation.", "Table 2 comparison and Loihi base architecture"),
            "neuron_dynamics": field("native", "Execute a documented discrete current-based generalized LIF update in its specified state-update order.", "Loihi 1 updates synaptic current and compartment voltage in discrete algorithmic timesteps, applies threshold comparison after integration, emits a spike, and then applies the configured reset action. Exact decay scaling and ordering must follow the NxSDK compartment model rather than a generic LIF equation.", "Table 2, Neuron Models"),
            "synaptic_dynamics_delays": field("native", "Represent filtered synaptic current and axonal delay.", "The first-generation architecture provides synaptic state, programmable decay, and delay fields within fixed resource limits.", "Table 2 and first-generation comparison"),
            "threshold_reset": field("emulated", "Preserve reset by subtraction used by classical rate conversion.", "Native Loihi 1 reset clears the compartment. NxTF emulates subtraction reset with a two-compartment recurrent inhibition construction that doubles compartment allocation for every neuron configured this way.", "Table 2 comparison; historical route documented by the official example repository"),
            "neural_code_payload": field("native", "Transmit sparse binary spike events between mapped neurons.", "Loihi 1 uses binary-valued spike messages. Integer-valued graded payloads are a Loihi 2 capability and are not attributed to the first generation.", "Table 2, Information Coding"),
            "encoder_decoder": field("host-assisted", "Encode input samples and decode output spike activity.", "Embedded processors and the host coordinate input and output. The historical conversion route uses host-managed sample presentation and readout.", "Base architecture and processor comparison"),
            "numeric_precision": field("transformed", "Map trained parameters into Loihi 1 fixed-point state.", "Weights, thresholds, decay constants, and state are quantized into hardware representations during compilation.", "Table 2, Memory and neuron-state allocation"),
            "time_termination": field("native", "Run a fixed number of synchronized algorithmic timesteps.", "Asynchronous cores advance through globally coordinated algorithmic timesteps. Wall-clock time per timestep is workload dependent.", "Base architecture comparison"),
            "connectivity_routing": field("transformed", "Place fan-in, fan-out, and multicast connectivity within chip resources.", "The compiler partitions and routes the graph. Resource fragmentation and inter-chip traffic can change placement efficiency and latency.", "Table 2, core and memory comparison"),
            "plasticity_state": field("native", "Maintain neuron state and execute supported on-chip learning rules.", "Loihi 1 includes programmable learning machinery and persistent compartment state, although the NxTF inference route does not require on-chip training.", "Table 2, Learning Rules"),
            "host_operations": field("host-assisted", "Identify computation that remains outside neuromorphic cores.", "Configuration, model loading, experiment control, encoding, monitoring, and result extraction remain host or embedded-processor responsibilities.", "Base architecture, Microprocessor Cores"),
        },
    },
    {
        "platform_id": "loihi-2",
        "manufacturer": "Intel",
        "chip_generation": "Loihi 2",
        "route_ids": ["spikingjelly-to-lava-exchange", "lava-exchange-to-netx", "netx-to-loihi2"],
        "route_state": "blocked",
        "official_technical_source_id": "loihi2",
        "document_date": "2021-09-30",
        "document_version": "Intel Loihi 2 technology brief, September 2021",
        "toolchain_version": "Lava 0.10.0 and Lava-DL 0.6.0, archived 2026-05-13",
        "mapper_limits": "NetX accepts a bounded HDF5 layer schema. The SpikingJelly Lava exporter rejects subtraction reset, biases, and selected LIF configurations before the platform compiler is reached.",
        "precision_constraints": "Loihi 2 supports programmable fixed-point neuron state, eight-bit-oriented synaptic storage, and graded messages up to 32 bits. Exact widths remain model and microcode dependent.",
        "routing_constraints": "Up to 128 asynchronous neuron cores communicate through spike messages. Global algorithmic progress still uses synchronization messages.",
        "host_responsibilities": "The host exports HDF5, invokes NetX and the Lava compiler, selects a run configuration, handles I/O, and profiles execution.",
        "access_path": "INRC-gated research access. Lava and Lava-DL are archived, and Intel has not published the successor SDK or a migration contract.",
        "fields": {
            "graph_operators": field("transformed", "Lower the exported SpikingJelly graph through Lava-DL NetX.", "NetX reconstructs supported HDF5 input, flatten, average, concat, dense, pool, and convolution blocks as Lava processes.", "NetX HDF5 workflow", "lava-dl-netx-docs"),
            "neuron_dynamics": field("native", "Execute a documented programmable discrete neuron update with explicit integration, threshold, spike, and reset phases.", "Loihi 2 microcode can implement CUBA-LIF and specialized dynamics, but equation coefficients and update order belong to the selected process model. The blocked SpikingJelly route does not by itself verify a matched process model.", "Programmable Neuron Models"),
            "synaptic_dynamics_delays": field("native", "Represent route-level synaptic current and delay state.", "Flexible neuron memory and programmable microcode support synaptic filtering and delay within allocated resource limits.", "Flexible Memory Organization and Programmable Neuron Models"),
            "threshold_reset": field("unsupported", "Preserve subtraction reset from a converted SpikingJelly model.", "The named route is blocked because the SpikingJelly Lava exporter rejects v_reset=None before NetX or Loihi 2 compilation. Possible custom Loihi 2 microcode is a separate, undocumented route and does not change this route-level result.", "Programmable Neuron Models; spikingjelly-to-lava-exchange edge"),
            "neural_code_payload": field("native", "Transmit binary or graded events required by the mapped model.", "Loihi 2 generalizes spike messages to graded payloads of up to 32 bits and retains binary event operation.", "Graded Spikes"),
            "encoder_decoder": field("host-assisted", "Encode external data and decode model output.", "Embedded processors accelerate spike I/O, but application-specific encoding, orchestration, and readout remain part of the host or process graph.", "Faster, More Flexible Input-Output Interface"),
            "numeric_precision": field("transformed", "Quantize weights and state to the selected Loihi 2 process model.", "Compiler and microcode choices determine weight, state, threshold, and payload widths. The route commonly uses eight-bit weights.", "Flexible Memory Organization and Graded Spikes"),
            "time_termination": field("native", "Execute synchronized algorithmic timesteps with an explicit run condition.", "Cores operate asynchronously but coordinate global algorithmic timesteps. Applications select fixed-step, pipelined, or fall-through orchestration.", "Base Architecture"),
            "connectivity_routing": field("transformed", "Place the process graph within core, memory, and NoC limits.", "The proprietary Loihi extension performs hardware compilation and placement after the open-source process graph is built.", "Lava extension access statement", "lava-github-archived"),
            "plasticity_state": field("native", "Retain state and execute programmable learning rules where exposed.", "Loihi 2 adds programmable three-factor learning support, although the audited NetX inference route does not establish on-chip training for the converted model.", "Generalized Learning Rules"),
            "host_operations": field("host-assisted", "Separate on-chip execution from required host services.", "Host and embedded processors configure the network, provide data I/O, manage runs, and collect measurements. The Loihi hardware extension is INRC-gated.", "Microprocessor Cores and Lava extension access", "intel-inrc-confluence"),
        },
    },
    {
        "platform_id": "spinnaker-1",
        "manufacturer": "University of Manchester",
        "chip_generation": "SpiNNaker 1",
        "route_ids": ["snn-toolbox-to-spynnaker", "spynnaker-to-spinnaker1"],
        "route_state": "physical",
        "official_technical_source_id": "spynnaker-v8-docs",
        "document_date": None,
        "document_version": "sPyNNaker 8.0.0 documentation",
        "toolchain_version": "sPyNNaker 8.0.0; exact SpiNNTools component version not established",
        "mapper_limits": "PyNN populations and projections are partitioned across ARM cores subject to DTCM, SDRAM, router-table, per-core neuron, and real-time processing budgets.",
        "precision_constraints": "Neuron and synapse computations use software-defined fixed-point arithmetic on ARM968 cores. Precision depends on the selected implementation.",
        "routing_constraints": "Multicast AER routing is best effort. Packets may arrive late or be dropped under congestion, and router-table capacity constrains placement.",
        "host_responsibilities": "The host builds the PyNN graph, partitions, places, routes, loads binaries and data, starts runs, and extracts recordings.",
        "access_path": "Physical boards and remotely hosted Manchester or EBRAINS systems. Access and supported software versions vary by service.",
        "fields": {
            "graph_operators": field("transformed", "Execute a converted CNN expressed through PyNN populations and projections.", "Convolution, pooling, and dense layers are lowered into populations, projections, and software kernels. This is graph transformation, not emulation of a missing SpiNNaker execution mode.", "PyNN execution documentation"),
            "neuron_dynamics": field("native", "Execute the selected discrete IF or LIF equation and its documented update order as a SpiNNaker application kernel.", "SpiNNaker natively executes software-defined neuron kernels on ARM cores. Each kernel integrates synaptic input and membrane state on the timer tick, compares threshold, emits a packet, and applies its compiled reset rule. Exact equations remain cell-model specific.", "Supported PyNN neuron models"),
            "synaptic_dynamics_delays": field("native", "Execute supported synaptic kernels and delays in real time.", "Software-defined synaptic processing and delay scheduling are the platform's native execution model, subject to per-core compute, memory, and real-time limits.", "PyNN synapse and delay documentation"),
            "threshold_reset": field("unsupported", "Preserve the SNN Toolbox subtraction-reset rule through the named route.", "Built-in sPyNNaker cells use their documented fixed-reset semantics. Subtraction reset requires a bespoke C neuron model, and the named SNN Toolbox route does not establish that substitution.", "Creating new neuron models guide; spynnaker-to-spinnaker1 edge"),
            "neural_code_payload": field("native", "Route sparse binary spike events.", "The multicast fabric natively carries source-addressed spike packets. Numeric activation payloads require a different software protocol.", "External devices and live-spike I/O guides"),
            "encoder_decoder": field("host-assisted", "Generate input spikes and decode output populations.", "Spike sources, live I/O, and recorded outputs require host-side or external-device configuration.", "Simple input and output guide"),
            "numeric_precision": field("transformed", "Represent converted parameters in software fixed point.", "Weights and neuron state are transformed into implementation-specific fixed-point formats rather than one platform-wide precision contract.", "Neuron implementation documentation"),
            "time_termination": field("native", "Advance the model for the requested biological time and stop at the configured run boundary.", "The native runtime uses timer-driven discrete steps, commonly 1 ms, and terminates after the host-configured biological duration. Real-time feasibility depends on the mapped workload.", "Running PyNN simulations on SpiNNaker"),
            "connectivity_routing": field("transformed", "Partition, place, and multicast-route the PyNN graph.", "SpiNNTools converts the application graph to per-core machine vertices and compressed routing tables.", "SpiNNTools execution flow"),
            "plasticity_state": field("native", "Maintain persistent model state and execute selected PyNN plasticity rules.", "Persistent neuron and synaptic state plus supported STDP and structural-plasticity kernels are native software-defined SpiNNaker execution capabilities. The selected conversion route uses fixed inference weights.", "Plasticity guides"),
            "host_operations": field("host-assisted", "Identify setup, control, and readout outside the mapped SNN.", "Graph construction, deployment, run control, external I/O, provenance, and extraction are host responsibilities.", "Installation and execution guides"),
        },
    },
    {
        "platform_id": "spinnaker-2",
        "manufacturer": "SpiNNcloud Systems and TU Dresden",
        "chip_generation": "SpiNNaker 2",
        "route_ids": ["spikingjelly-to-nir-exchange", "nir-exchange-to-nir", "nir-to-spinnaker2"],
        "route_state": "blocked",
        "official_technical_source_id": "spinnaker2-tools",
        "document_date": "2026-09-09",
        "document_version": "py-spinnaker2 documentation dated 2026-09-09",
        "toolchain_version": "py-spinnaker2 0.8.1",
        "mapper_limits": "The NIR importer supports Conv1d, Conv2d, Flatten, Affine, Linear, CuBaLIF, IF, LIF, and SumPool2d. Unsupported nodes block the import path.",
        "precision_constraints": "The documented stack uses quantized synaptic weights with floating-point state on Cortex-M4F processing elements. Accelerator widths vary by operation.",
        "routing_constraints": "The mapper partitions the graph over processing elements and packet routing resources. Large payloads are possible but are not equivalent to ordinary binary forward spikes.",
        "host_responsibilities": "The host imports NIR, maps the graph, loads the machine, controls the experiment, and receives results.",
        "access_path": "Commercial or institutional SpiNNaker 2 systems. Public per-board access conditions are not specified in the audited documentation.",
        "fields": {
            "graph_operators": field("transformed", "Import a supported NIR graph into py-spinnaker2.", "The importer accepts a bounded operator and neuron subset. It is not a general NIR backend for arbitrary nodes.", "NIR import support list", "spinnaker2-nir-import-docs"),
            "neuron_dynamics": field("native", "Execute the selected discrete IF, LIF, or CuBaLIF equation in the py-spinnaker2 kernel update order.", "Cortex-M4F processing elements natively execute software-defined neuron kernels. Supported kernels integrate current and voltage, compare threshold, emit spikes, and apply the configured reset in model-specific order. The blocked upstream exporter prevents the default converted model from reaching this stage.", "Neuron model API"),
            "synaptic_dynamics_delays": field("native", "Represent supported synaptic filtering and delays.", "Software-defined synaptic dynamics on processing elements are native to SpiNNaker 2. Exact delay coverage remains model specific and must be checked before import.", "Synapse and population APIs"),
            "threshold_reset": field("unsupported", "Preserve the default SpikingJelly subtraction-reset model through NIR.", "The named route is blocked because the SpikingJelly NIR exporter rejects v_reset=None. Downstream py-spinnaker2 reset options cannot repair a graph that was never exported.", "NIR importer neuron mapping; spikingjelly-to-nir-exchange edge", "spinnaker2-nir-import-docs"),
            "neural_code_payload": field("native", "Transmit spike events between mapped populations.", "Binary spikes are native. The packet system can also carry larger payloads for specialized algorithms.", "Communication API"),
            "encoder_decoder": field("host-assisted", "Supply event or frame input and interpret output.", "The host constructs inputs, runs experiments, and collects output unless a mapped peripheral supplies the events.", "Examples and experiment runner"),
            "numeric_precision": field("transformed", "Quantize parameters for mapped processing elements and accelerators.", "Weights and selected operations are quantized while software neuron state can remain floating point.", "Quantization and hardware model documentation"),
            "time_termination": field("native", "Run the imported network for an explicit model duration and stop at the host-configured boundary.", "Timer-driven discrete model time and experiment termination are native runtime services exposed through the host API.", "Experiment runner"),
            "connectivity_routing": field("transformed", "Map populations and projections onto processing elements and routers.", "Placement and routing transform the imported graph to the available system topology.", "Mapping API"),
            "plasticity_state": field("undocumented", "Execute the route's required persistent state or learning rule.", "Stateful inference is supported, but the audited NIR import documentation does not establish a general on-chip plasticity contract for imported graphs.", "NIR import example", "spinnaker2-nir-import-docs"),
            "host_operations": field("host-assisted", "Identify functions outside the neuromorphic processing elements.", "Import, mapping, loading, run control, and result collection remain host functions.", "Getting started and experiment runner"),
        },
    },
    {
        "platform_id": "speck-2f",
        "manufacturer": "SynSense",
        "chip_generation": "Speck 2f and DYNAP-CNN core",
        "route_ids": ["sinabs-to-dynapcnn-mapper", "dynapcnn-mapper-to-samna", "samna-to-speck"],
        "route_state": "physical",
        "official_technical_source_id": "synsense-speck-datasheet",
        "document_date": "2025-12-01",
        "document_version": "Speck Development Kit Manual 2025.12 V2",
        "toolchain_version": "Sinabs 3.1.3; exact samna runtime version not established",
        "mapper_limits": "DynapcnnNetwork accepts a sequential convolution-spike-pooling structure, rewrites average pooling and dense layers, requires uniform per-layer thresholds, and maps each layer within per-core memory budgets.",
        "precision_constraints": "The mapped path uses eight-bit weights and biases with sixteen-bit membrane state and hardware threshold registers.",
        "routing_constraints": "Convolutional cores form a feedforward event pipeline. Core ordering and destination configuration must satisfy per-core kernel and neuron memory limits.",
        "host_responsibilities": "The host converts the model, discretizes parameters, selects core placement, applies samna configuration, streams or receives events, and performs task-level decoding.",
        "access_path": "Commercial Speck development kit with USB host connection and the SynSense software stack.",
        "fields": {
            "graph_operators": field("transformed", "Map a Sinabs convolutional SNN to the Speck pipeline.", "The mapper restructures supported convolution, spike, and pooling stages and rejects graphs that cannot fit the core sequence.", "Architecture, configuration, and supported operation chapters"),
            "neuron_dynamics": field("native", "Execute the documented event-driven integrate-and-fire update and configured leakage in hardware order.", "For each received event the DYNAP-CNN core accumulates the mapped weight into membrane state, applies configured leakage according to the device timing mode, compares against threshold, emits events, and applies the return-to-zero or subtractive reset setting.", "Neuron and CNN layer configuration"),
            "synaptic_dynamics_delays": field("unsupported", "Preserve arbitrary synaptic filters and trainable delays.", "The deployed convolutional path provides event accumulation and optional neuron leak, not a general arbitrary-delay synapse model.", "CNN layer register description"),
            "threshold_reset": field("native", "Preserve subtraction reset used by Sinabs conversion.", "The hardware return-to-zero control distinguishes reset-to-zero from subtractive reset. Sinabs maps its default subtraction behavior to the chip.", "CNN layer threshold and return_to_zero configuration"),
            "neural_code_payload": field("native", "Process address events produced by the sensor or host.", "Events carry address, feature, polarity, and timestamp information. Compute is asynchronous and event driven.", "Event types and DVS interface"),
            "encoder_decoder": field("host-assisted", "Accept event-camera input and produce an application decision from output events.", "The integrated DVS supplies native input events, but frame conversion and final class aggregation remain host operations in the documented route.", "DVS configuration and output monitoring"),
            "numeric_precision": field("transformed", "Discretize trained parameters to chip integer ranges.", "DynapcnnNetwork quantizes weights, biases, thresholds, and membrane-related parameters before configuration.", "CNN layer configuration and discretization"),
            "time_termination": field("host-assisted", "Process timestamped events and define a reproducible sample termination condition.", "The compute pipeline is asynchronously event driven, while the host or sensor stream defines the frame, sample, or observation window used to terminate an inference.", "Event streaming and timestamp handling"),
            "connectivity_routing": field("transformed", "Place sequential layers and configure destinations within core budgets.", "Automatic placement can fail when no legal ordering satisfies neuron, kernel, and bias memory constraints.", "CNN layer destinations and mapping constraints"),
            "plasticity_state": field("unsupported", "Retain inference state and apply online weight learning within the deployed DYNAP-CNN path.", "Membrane state persists during event processing, but the documented route configures fixed inference weights and exposes no online synaptic plasticity. The aggregate status is unsupported because the requested learning component is absent.", "Configuration workflow"),
            "host_operations": field("host-assisted", "Separate autonomous event processing from host configuration and decoding.", "samna applies configuration and transports monitored events. Host code commonly resets sample timestamps and converts output event counts to decisions.", "USB, samna, and output monitoring chapters"),
        },
    },
    {
        "platform_id": "xylo-audio-2",
        "manufacturer": "SynSense",
        "chip_generation": "Xylo Audio 2, SYNS61201",
        "route_ids": ["rockpool-to-xylo-mapper", "xylo-mapper-to-xylo"],
        "route_state": "physical",
        "official_technical_source_id": "rockpool-xylo-docs",
        "document_date": None,
        "document_version": "Rockpool 3.1.0 Xylo documentation",
        "toolchain_version": "Rockpool 3.1.0; exact samna runtime version not established",
        "mapper_limits": "The device exposes 16 inputs, 1000 hidden neurons, 8 outputs, bounded fan-out, two hidden synaptic states, one output synaptic state, and per-step spike-count limits.",
        "precision_constraints": "Weights are 8 bit. Synaptic state, membrane state, and threshold are 16 bit. Decay is encoded with four-bit shift parameters.",
        "routing_constraints": "The global hidden recurrent matrix and input or output projections must satisfy fixed dimensions, fan-out, and alias constraints.",
        "host_responsibilities": "Rockpool extracts the graph, maps and quantizes it, generates a hardware configuration, connects through samna, selects operating mode, and collects output or power traces.",
        "access_path": "Commercial Xylo Audio 2 hardware development kit.",
        "fields": {
            "graph_operators": field("transformed", "Map a Rockpool graph to the fixed Xylo recurrent SNN core.", "The mapper assigns supported graph nodes to input, hidden recurrent, and output matrices. Unsupported structures or excess dimensions fail mapping.", "SNN core logical architecture and quick-start mapping"),
            "neuron_dynamics": field("native", "Execute the documented synchronous integer LIF recurrence in its hardware update order.", "At each global timestep the core updates bit-shift synaptic states, integrates membrane state with configured decay and bias, compares threshold, emits bounded spike counts, and applies fixed subtractive reset.", "SNN core logical architecture"),
            "synaptic_dynamics_delays": field("transformed", "Represent required synaptic dynamics and delays.", "Hidden neurons provide one or two exponentially decaying synaptic states through bit-shift recurrences. Arbitrary learned axonal-delay tensors are unavailable and require graph reformulation.", "Neuron model and bit-shift decay"),
            "threshold_reset": field("native", "Use subtraction reset after threshold crossings.", "Reset by subtraction is a fixed documented core behavior. Hidden neurons may emit up to 31 events per global timestep.", "SNN core logical architecture"),
            "neural_code_payload": field("native", "Carry integer spike counts across a synchronous timestep.", "Input and hidden channels may represent multiple events per step within device limits. Output neurons emit at most one event per step.", "Xylo in numbers and neuron model"),
            "encoder_decoder": field("host-assisted", "Use the audio front end and convert readout activity into a task decision.", "Xylo Audio integrates a microphone-oriented front end, while Rockpool and host code configure encoding, monitoring, and application-level decoding.", "Family design and Audio 2 device entry"),
            "numeric_precision": field("transformed", "Quantize graph parameters to Xylo integer representations.", "Rockpool global or channel quantization maps floating-point weights, thresholds, and decays to documented integer widths.", "Quick-start quantization step"),
            "time_termination": field("host-assisted", "Execute one hardware update per global timestep and terminate a sample reproducibly.", "Xylo provides synchronous hardware timesteps in real-time or accelerated modes. The host-side deployment specifies the number of steps or streaming observation boundary used for termination.", "SNN core logical architecture and deployment workflow"),
            "connectivity_routing": field("transformed", "Fit input, recurrent, and output connectivity into fixed matrices.", "The mapper must satisfy neuron counts, fan-out, alias, and projection limits before configuration is valid.", "Xylo in numbers and mapper output"),
            "plasticity_state": field("unsupported", "Retain recurrent inference state and update deployed synaptic weights online.", "The core natively retains neuron and synaptic state, but the documented deployment exposes no online weight-learning rule. The aggregate status is unsupported because plasticity is absent.", "Family overview and deployment workflow"),
            "host_operations": field("host-assisted", "Configure the HDK and obtain decisions or measurements.", "The host performs graph preparation and configuration. The device can then run streaming input autonomously while the host monitors outputs.", "Quick-start deployment and operating modes"),
        },
    },
    {
        "platform_id": "brainscales-2",
        "manufacturer": "Heidelberg University Electronic Vision(s)",
        "chip_generation": "BrainScaleS-2",
        "route_ids": ["hxtorch-to-brainscales2"],
        "route_state": "physical",
        "official_technical_source_id": "hxtorch",
        "document_date": "2026-09-11",
        "document_version": "BrainScaleS-2 documentation commit 7821187",
        "toolchain_version": "hxtorch.snn documentation commit 7821187; package release not established",
        "mapper_limits": "hxtorch maps supported dense spiking layers to calibrated analog neuron circuits and digital routing resources. Hardware size and routing constrain topology.",
        "precision_constraints": "Analog neuron and synapse dynamics are calibrated rather than bit exact. Digital weights and readout are quantized to hardware representations.",
        "routing_constraints": "Connectivity is mapped to the on-chip synapse array and event routing fabric. Placement and calibration influence the realized dynamics.",
        "host_responsibilities": "The host constructs and trains the model, applies calibration, maps the graph, schedules hardware execution, and reads observables through the experiment stack.",
        "access_path": "Remote EBRAINS or Heidelberg research access. The ASIC is not a generally purchasable development board.",
        "fields": {
            "graph_operators": field("transformed", "Map a supported PyTorch or PyNN spiking graph to BrainScaleS-2.", "hxtorch lowers supported network modules to hardware populations, projections, and observables rather than executing arbitrary PyTorch operators.", "hxtorch.snn network construction"),
            "neuron_dynamics": field("native", "Execute the calibrated analog LIF-like differential equation with the documented threshold and reset sequence.", "Calibrated analog circuits continuously evolve membrane and synaptic state at accelerated physical time. Threshold crossing produces an event and invokes the configured reset. Exact parameters and update semantics depend on the calibrated hardware neuron model.", "Hardware execution and neuron module"),
            "synaptic_dynamics_delays": field("transformed", "Realize required synaptic integration and delay semantics in analog hardware.", "Supported synaptic dynamics are physical and calibrated, but arbitrary software delay semantics are not preserved automatically and require an explicit mapping or graph transformation.", "Synapse and projection modules"),
            "threshold_reset": field("native", "Execute the calibrated hardware threshold and reset behavior.", "Threshold crossing and reset are properties of the analog neuron circuit. Exact software equivalence depends on calibration and model choice.", "Neuron calibration and execution"),
            "neural_code_payload": field("native", "Transmit timestamped spike events through the digital fabric.", "Spikes are event messages between analog neuron circuits and digital routing resources.", "Hardware execution overview"),
            "encoder_decoder": field("host-assisted", "Provide input events and convert recorded observables to task outputs.", "Experiment inputs and readout are scheduled by the host-facing stack, although network dynamics execute on the ASIC.", "Experiment construction and observables"),
            "numeric_precision": field("transformed", "Map trained parameters to calibrated analog and quantized digital settings.", "Mismatch and finite control resolution require calibration and hardware-aware training rather than bit-exact parameter transfer.", "Calibration workflow"),
            "time_termination": field("native", "Relate accelerated hardware time to the model time interval.", "The hardware evolves in accelerated time. The experiment specifies runtime and converts between hardware and biological time scales.", "Hardware runtime configuration"),
            "connectivity_routing": field("transformed", "Place network connectivity within synapse-array and routing limits.", "The software stack maps projections and rejects or restructures graphs that exceed physical resources.", "Network mapping"),
            "plasticity_state": field("host-assisted", "Retain state or update parameters during hardware-in-the-loop learning.", "Hybrid plasticity combines on-chip observables or local mechanisms with host computation. Support depends on the selected experiment path.", "Training and observables"),
            "host_operations": field("host-assisted", "Identify calibration, optimization, and control outside the ASIC.", "Calibration, graph construction, gradient computation for many workflows, experiment control, and result extraction remain on the host.", "hxtorch.snn workflow"),
        },
    },
    {
        "platform_id": "akida-1",
        "manufacturer": "BrainChip",
        "chip_generation": "Akida 1.0, AKD1000 and AKD1500",
        "route_ids": ["quantizeml-to-cnn2snn", "cnn2snn-to-akida"],
        "route_state": "physical",
        "official_technical_source_id": "brainchip-akida-user-guide",
        "document_date": "2026-07-09",
        "document_version": "MetaTF 2.19.2 documentation",
        "toolchain_version": "QuantizeML 1.2.4, CNN2SNN 2.19.2, Akida runtime 2.19.2",
        "mapper_limits": "Akida 1.0 uses a serial feedforward sequence of input convolution, convolution, separable convolution, pooling, and dense functions with ordering, padding, stride, bit-width, and memory constraints.",
        "precision_constraints": "Input convolution weights are eight bit. Later weights and activations use supported low-bit combinations, commonly one, two, or four bits. Edge learning requires one-bit input and weights.",
        "routing_constraints": "Layers map sequentially across neural processing cores. Unsupported branches or layer arrangements must be sanitized, transformed, split, or rejected.",
        "host_responsibilities": "The host trains or imports the model, calibrates and quantizes it, converts it with CNN2SNN, maps the .fbz graph, loads hardware, and interprets outputs.",
        "access_path": "Commercial AKD1000 and AKD1500 devices and development systems. Exact product availability must be checked against the current vendor catalog.",
        "fields": {
            "graph_operators": field("transformed", "Convert a supported quantized Keras or ONNX graph to Akida 1.0.", "QuantizeML sanitizes and quantizes the graph. CNN2SNN maps supported patterns and rejects hardware-incompatible combinations.", "Akida 1.0 layer support and CNN2SNN conversion", "brainchip-cnn2snn-docs"),
            "neuron_dynamics": field("native", "Execute the documented Akida event-domain accumulate, threshold, event-emission, and state-transition sequence.", "The converted-CNN path accumulates low-bit event-domain activations, applies the configured thresholded activation, emits sparse quantized events, and advances layer state as defined by the Akida processor. It is not an exposed multi-timestep LIF recurrence.", "Akida 1.0 hardware model"),
            "synaptic_dynamics_delays": field("unsupported", "Preserve arbitrary synaptic filtering and learned delay dynamics.", "The standard Akida 1.0 CNN2SNN path exposes feedforward event-domain layers, not arbitrary synaptic kernels or delay tensors.", "Akida 1.0 supported layers"),
            "threshold_reset": field("transformed", "Preserve the converted quantized activation behavior.", "CNN2SNN folds scaling, batch normalization, quantization, and activation behavior into thresholds. There is no exposed subtraction-reset sequence over T.", "CNN2SNN toolkit, conversion principles", "brainchip-cnn2snn-docs"),
            "neural_code_payload": field("native", "Propagate sparse nonzero quantized activations as events.", "Akida events carry low-bit activation information. This differs from representing an activation as a binary spike count over many timesteps.", "Akida 1.0 model and precision rules"),
            "encoder_decoder": field("host-assisted", "Prepare quantized input and interpret output tensors or events.", "The runtime handles mapped inference, while preprocessing and application-level decoding commonly remain on the host or embedded processor.", "Runtime and device workflow"),
            "numeric_precision": field("native", "Execute supported low-bit weights and activations.", "Akida 1.0 natively targets integer event-domain computation with layer-dependent one-, two-, four-, and eight-bit constraints.", "Akida 1.0 hardware capabilities"),
            "time_termination": field("native", "Complete one mapped feedforward inference without a user-selected rate horizon.", "The standard converted path is a single event-domain pass. It does not expose the conversion literature's global simulation length T.", "Inference workflow"),
            "connectivity_routing": field("transformed", "Map the serial graph within processing-core and memory limits.", "The mapper assigns layers to available neural processing cores and can reject incompatible orderings or capacity requirements.", "Model mapping and hardware capabilities"),
            "plasticity_state": field("native", "Use the documented Akida 1.0 edge-learning mode where its strict contract is satisfied.", "Edge learning is limited to the final fully connected layer with one-bit input and weights. It is not general end-to-end online training.", "Edge learning constraints"),
            "host_operations": field("host-assisted", "Separate quantization, conversion, mapping, and I/O from on-device inference.", "QuantizeML and CNN2SNN run before deployment. The runtime and host configure devices, submit data, and retrieve outputs.", "QuantizeML and CNN2SNN workflow", "brainchip-cnn2snn-docs"),
        },
    },
    {
        "platform_id": "akida-2",
        "manufacturer": "BrainChip",
        "chip_generation": "Akida 2.0 IP and FPGA development targets",
        "route_ids": ["quantizeml-to-cnn2snn", "cnn2snn-to-akida"],
        "route_state": "unexercised",
        "official_technical_source_id": "brainchip-akida-user-guide",
        "document_date": "2026-07-09",
        "document_version": "MetaTF 2.19.2 documentation",
        "toolchain_version": "QuantizeML 1.2.4, CNN2SNN 2.19.2, Akida runtime 2.19.2",
        "mapper_limits": "Akida 2.0 expands graph support to skip connections, temporal convolutions, attention-related blocks, and multiple processor types, but the exact combination must satisfy the selected IP or FPGA target.",
        "precision_constraints": "Akida 2.0 supports broader eight-, four-, and one-bit arithmetic combinations with processor-specific restrictions and selected lookup-table activations.",
        "routing_constraints": "Skip and merge paths consume dedicated resources. Release notes identify processor-ordering and unsupported-combination checks that vary by FPGA image.",
        "host_responsibilities": "The host sanitizes and quantizes Keras or ONNX, converts the graph, selects a virtual or physical target, maps it, loads the FPGA or IP runtime, and handles application I/O.",
        "access_path": "Licensable IP and supported FPGA development targets. Public evidence does not establish a generally available AKD2000 production chip.",
        "fields": {
            "graph_operators": field("transformed", "Convert a supported quantized Keras or ONNX graph to an Akida 2.0 target.", "Sanitization and mapping cover a broader operator set than Akida 1.0 but retain target-specific pattern and topology restrictions.", "Akida 2.0 supported layers and hardware capabilities"),
            "neuron_dynamics": field("native", "Execute each documented Akida 2.0 processor's ordered accumulation, activation, event-emission, and state update.", "Convolutional, temporal, attention, and related processors use distinct event-domain state transitions. The vendor processor specification, not a generic LIF equation, defines their update order.", "Akida 2.0 processor descriptions"),
            "synaptic_dynamics_delays": field("transformed", "Represent required synaptic dynamics or temporal delays in the mapped graph.", "BufferTempConv and related temporal blocks transform bounded sequence context into supported processor state. This is not a general arbitrary synaptic-filter or learned-delay mechanism.", "Temporal convolution layer support"),
            "threshold_reset": field("transformed", "Preserve quantized activation semantics after conversion.", "Quantized activations and normalization are lowered into target operations. Classical subtraction reset over a rate horizon is not the route contract.", "CNN2SNN conversion principles", "brainchip-cnn2snn-docs"),
            "neural_code_payload": field("native", "Carry supported low-bit event-domain activations.", "Events convey quantized activation values and exploit activation sparsity rather than requiring binary rate counts.", "Akida 2.0 precision and layer behavior"),
            "encoder_decoder": field("host-assisted", "Provide model input and interpret runtime output.", "Temporal front ends may retain sequence state, while dataset preprocessing and task decoding remain model and host responsibilities.", "Runtime workflow"),
            "numeric_precision": field("native", "Execute supported one-, four-, and eight-bit operations.", "Precision combinations are processor and layer dependent. Release notes document additional constraints for input convolution and FPGA targets.", "Hardware capabilities and MetaTF 2.19.2 release", "brainchip-metatf-2-19-2-release"),
            "time_termination": field("native", "Complete feedforward or bounded temporal-block execution.", "Standard CNN2SNN inference remains pass based. Temporal blocks retain bounded sequence context without becoming a user-selected global rate horizon.", "Temporal model and runtime documentation"),
            "connectivity_routing": field("transformed", "Map branches, merge operations, and processor sequences to the selected target.", "Mapping checks enforce processor order, skip resources, layer compatibility, and target capacity.", "Mapping constraints and MetaTF release notes", "brainchip-metatf-2-19-2-release"),
            "plasticity_state": field("unsupported", "Retain processor state and perform on-device edge learning through the Akida 2.0 route.", "Temporal processors may retain bounded inference state, but current documentation restricts edge learning to Akida 1.0 models and devices. The aggregate status is unsupported because on-device learning is absent.", "Edge learning support statement"),
            "host_operations": field("host-assisted", "Identify conversion and orchestration outside the Akida target.", "Quantization, graph sanitization, conversion, mapping, device selection, and application I/O remain host operations.", "QuantizeML and CNN2SNN workflow", "brainchip-cnn2snn-docs"),
        },
    },
)


def build() -> dict[str, object]:
    records: list[dict[str, object]] = []
    for platform in PLATFORMS:
        details = platform["fields"]
        if not isinstance(details, dict) or set(details) != set(FIELDS):
            raise ValueError(
                f"{platform['platform_id']} must define exactly the 11 contract fields"
            )
        for contract_field in FIELDS:
            capability = details[contract_field]
            if not isinstance(capability, dict):
                raise ValueError(
                    f"{platform['platform_id']} {contract_field} must be an object"
                )
            source_id = capability.get(
                "official_technical_source_id",
                platform["official_technical_source_id"],
            )
            records.append({
                "id": f"cap-{platform['platform_id']}-{contract_field}",
                "platform_id": platform["platform_id"],
                "manufacturer": platform["manufacturer"],
                "chip_generation": platform["chip_generation"],
                "contract_field": contract_field,
                "contract_requirement": capability["contract_requirement"],
                "capability_status": capability["capability_status"],
                "support_detail": capability["support_detail"],
                "mapper_limits": platform["mapper_limits"],
                "precision_constraints": platform["precision_constraints"],
                "routing_constraints": platform["routing_constraints"],
                "host_responsibilities": platform["host_responsibilities"],
                "access_path": platform["access_path"],
                "route_ids": platform["route_ids"],
                "route_state": platform["route_state"],
                "official_technical_source_id": source_id,
                "source_locator": capability["source_locator"],
                "document_date": platform["document_date"],
                "document_version": platform["document_version"],
                "toolchain_version": platform["toolchain_version"],
                "official_exercised_example_source_id": capability.get(
                    "official_exercised_example_source_id"
                ),
                "official_exercised_example_locator": capability.get(
                    "official_exercised_example_locator"
                ),
                "verification_status": "provisional",
                "reviewed_on": REVIEWED_ON,
            })
    records.sort(key=lambda record: str(record["id"]))
    return {"schema_version": 1, "records": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.exists() else ""
        if current != rendered:
            print("build-platform-capabilities: generated output is stale", file=sys.stderr)
            return 1
        print("build-platform-capabilities: generated output current")
        return 0
    OUTPUT.write_text(rendered)
    print(f"build-platform-capabilities: wrote {len(build()['records'])} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
