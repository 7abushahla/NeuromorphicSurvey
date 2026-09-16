#!/usr/bin/env python3
"""Regenerate the site shell from the quantization survey's page, verbatim.

The two surveys are meant to look and behave identically, so the shell is not
re-implemented here. It is copied out of QuantizationSurvey/index.html byte for byte
and only the content strings are substituted: title, abstract, keywords, contents.
Everything else, the TMLR chrome, the front matter, the inline paper stylesheet, the
citation machinery, the attribution box, the back-to-top control, carries over as is.

Run this when the upstream template changes. It rewrites site/shell-head.html and
site/shell-tail.html; the section fragments are untouched.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT.parent.parent / 'QuantizationSurvey' / 'index.html'

Q_TITLE = ('Neural Network Quantization for Microcontrollers: A Comprehensive Survey '
           'of Methods, Platforms, and Applications')
Q_SUB = ('This survey provides a hardware-oriented perspective on neural network '
         'quantization, systematically reviewing the quantization methods most relevant '
         'to MCUs and extreme-edge devices.')

TITLE = ('From Neural Networks to Neuromorphic Execution: A Deployment-Centered Survey '
         'of ANN-to-SNN Conversion, Software Stacks, and Silicon')

SUB = ('This survey traces the handoffs a converted spiking network must survive to reach '
       'a physical neuromorphic chip, recording at each one what is preserved, what is '
       'broken, and how strong the evidence is at the destination.')

ABSTRACT = (
    'Spiking neural networks promise inference at a fraction of the energy cost of '
    'conventional accelerators, and ANN-to-SNN conversion is the most accessible route to '
    'a trained spiking model. A line of work anchored by quantization-clip-floor-shift '
    'conversion has driven the timestep count needed to match ANN accuracy from the '
    'hundreds into the single digits. Whether those gains reach silicon is a separate '
    'question, and it is the question this survey answers. A trained network that reaches '
    'a chip passes through a sequence of handoffs, each governed by a different toolchain, '
    'reset rule, spike payload, and time model, and each able to break the '
    'activation-to-spike-count correspondence the algorithm paper established. This survey '
    'records those handoffs. It presents the preliminaries a reader needs, namely neuron '
    'models, neural codes, and the execution contracts that hardware imposes, then reviews '
    'the primary training paths, advanced conversion techniques, and the alternative codes '
    'that abandon rate entirely. It then maps the deployment stack itself, covering '
    'neuromorphic platforms, training and simulation frameworks, export and interchange '
    'formats, compilers, and runtimes, and traces every documented route from a trained '
    'model to a named chip. Deployment claims are classified on a five-level evidence '
    'scale separating measured silicon from software simulation. Applying that scale to '
    'the literature exposes a division of labor that no prior survey states: algorithm '
    'papers advance accuracy at low timestep counts and do not deploy, while deployment '
    'papers reach silicon and do not adopt the new algorithms. Every confirmed case of a '
    'new conversion method reaching measured silicon abandons rate coding. The survey '
    'closes with the open challenges that division creates, from reset-semantics mismatch '
    'and operator coverage to toolchain decay and incomparable efficiency reporting.')

KEYWORDS = ('spiking-neural-networks, neuromorphic-computing, ANN-to-SNN-conversion, '
            'Loihi, SpiNNaker, Speck, Akida, event-based-vision, deployment, TMLR')

INDEX_TERMS = ('Spiking Neural Networks, Neuromorphic Hardware, ANN-to-SNN Conversion, '
               'Neural Coding, Event-Based Vision, Deployment Toolchains, Edge Inference, '
               'Energy-Efficient Computing')

TOC = [
    (1, 'abstract', 'Abstract'),
    (1, 'introduction', '1&ensp;Introduction'),
    (2, 'existing-surveys', '1.1&ensp;Existing Surveys'),
    (2, 'contributions', '1.2&ensp;Contributions'),
    (2, 'organization', '1.3&ensp;Organization'),
    (1, 'preliminaries', '2&ensp;Preliminaries'),
    (2, 'biological-neurons', '2.1&ensp;From Biological Neurons to Spiking Models'),
    (2, 'neuron-models', '2.2&ensp;Spiking Neuron Models'),
    (2, 'neural-codes', '2.3&ensp;Neural Codes'),
    (2, 'formalization', '2.4&ensp;Formalization'),
    (2, 'execution-contracts', '2.5&ensp;Execution Contracts for Deployment'),
    (1, 'training-paths', '3&ensp;Primary Training Paths'),
    (2, 'direct-training', '3.1&ensp;Direct Training'),
    (2, 'classical-conversion', '3.2&ensp;Classical ANN-to-SNN Conversion'),
    (1, 'advanced-conversion', '4&ensp;Advanced Conversion Techniques'),
    (2, 'low-latency-conversion', '4.1&ensp;Low-Latency Conversion'),
    (2, 'quantization-distribution-aware', '4.2&ensp;Quantization- and Distribution-Aware Conversion'),
    (2, 'mixed-timestep', '4.3&ensp;Mixed-Timestep and Per-Layer Allocation'),
    (2, 'hardware-aware-conversion', '4.4&ensp;Hardware-Aware and Co-Designed Conversion'),
    (2, 'hybrid-calibration-finetuning', '4.5&ensp;Hybrid and Calibration-Based Fine-Tuning'),
    (1, 'alternative-codes', '5&ensp;Alternative Codes and Non-Rate Representations'),
    (2, 'temporal-ttfs', '5.1&ensp;Temporal and Time-to-First-Spike'),
    (2, 'phase-weighted-slot', '5.2&ensp;Phase and Weighted-Slot'),
    (2, 'sigma-delta-payloads', '5.3&ensp;Differential, Sigma-Delta, and Graded Payloads'),
    (2, 'rank-order-coding', '5.4&ensp;Rank Order Coding'),
    (1, 'deployment-stack', '6&ensp;Hardware and Software Deployment Stack'),
    (2, 'hardware-platforms', '6.1&ensp;Neuromorphic Hardware Platforms'),
    (3, 'per-platform-notes', '6.1.1&ensp;Per-Platform Notes'),
    (3, 'akida-examined-critically', '6.1.2&ensp;Akida, Examined Critically'),
    (2, 'frameworks', '6.2&ensp;Training and Simulation Frameworks'),
    (2, 'export-compile', '6.3&ensp;Export, Interchange, and Compilation'),
    (2, 'runtime', '6.4&ensp;Runtime and Host I/O'),
    (2, 'routes', '6.5&ensp;Documented Routes'),
    (1, 'applications', '7&ensp;Applications and Deployment Evidence'),
    (2, 'loihi-deployments', '7.1&ensp;Loihi-Family Deployments'),
    (2, 'speck-deployments', '7.2&ensp;DYNAP-CNN and Speck Event-Vision Deployments'),
    (2, 'spinnaker-brainscales', '7.3&ensp;SpiNNaker and BrainScaleS Deployments'),
    (2, 'fpga-asic', '7.4&ensp;FPGA and Custom ASIC Implementations'),
    (2, 'event-sensing', '7.5&ensp;Event-Based Sensing'),
    (2, 'cross-case', '7.6&ensp;Cross-Case Evidence Table'),
    (2, 'measurement', '7.7&ensp;Measurement and Comparability'),
    (1, 'figure-1', 'Figure 1&ensp;The Deployment Stack'),
    (1, 'challenges', '8&ensp;Challenges and Future Directions'),
    (2, 'ch-operators', '8.1&ensp;Operator Coverage in SNN Toolchains'),
    (2, 'ch-reset', '8.2&ensp;Reset-Semantics Mismatch'),
    (2, 'ch-encoding', '8.3&ensp;Input Encoding and Output Readout'),
    (2, 'ch-timemodel', '8.4&ensp;Time-Model Mismatch'),
    (2, 'ch-perlayer', '8.5&ensp;Per-Layer Timestep Horizons'),
    (2, 'ch-measurement', '8.6&ensp;Measurement Boundaries'),
    (2, 'ch-decay', '8.7&ensp;Device Availability and Toolchain Decay'),
    (2, 'ch-portability', '8.8&ensp;Interoperability and the Portability Gap'),
    (2, 'ch-populations', '8.9&ensp;The Two-Population Division of Labor'),
    (1, 'conclusion', '9&ensp;Conclusion'),
]

# Styles this survey adds on top of the template's stylesheet. The template already
# carries the paper tables, the coverage heat map, the figure chrome, the contents
# nav, the cross-reference links and the back-to-top control, so none of that is
# restated here. Only what is specific to tracing deployment evidence is.
EXTRA_CSS = """
      /* ---- Additions for this survey ---- */
      /* Evidence classes. The argument rests on keeping these apart, so they are
         colour-coded consistently wherever a claim is classified. */
      .ev { display: inline-block; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.05em;
            padding: 0.06rem 0.4rem; border-radius: 3px; color: #fff; vertical-align: 0.06rem; }
      .ev-e1 { background: #1F7A4D; }
      .ev-e2 { background: #2A8A7A; }
      .ev-e3 { background: #8A6D1F; }
      .ev-e4 { background: #98622C; }
      .ev-e5 { background: #7B8494; }
      .ev-blocked { background: #C0392B; }

      d-article .caveat { padding: 0.55rem 0.85rem; border-left: 3px solid #C0392B;
        background: #fbeceb; border-radius: 0 6px 6px 0; color: #7d2820; font-size: 0.92rem; }
      d-article .keypoint { padding: 0.55rem 0.85rem; border-left: 3px solid #1f2430;
        background: #f3f4f7; border-radius: 0 6px 6px 0; font-size: 0.95rem; }
      .src-type { font-size: 0.62rem; color: #778; font-style: italic; }

      /* The coverage heat map is scoped to #table-1 upstream. This survey scores more
         than one table that way, so the same rules are restated for .cov-table. */
      .cov-table td.cov-full, .cov-table td.cov-part, .cov-table .hw, .cov-table .sw {
        -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .cov-table td.cov-full { background: #2698BA; }
      .cov-table td.cov-full span { color: #fff; font-weight: 700; font-size: 0.94em; }
      .cov-table td.cov-part { background: #D8EBF2; }
      .cov-table td.cov-part span { color: #145E75; font-weight: 500; font-size: 0.94em; }
      .cov-table td.cov-ment { background: #F2F6F8; }
      .cov-table td.cov-ment span { color: #7b8794; font-weight: 400; font-size: 0.9em; font-style: italic; }
      .cov-table td.cov-full, .cov-table td.cov-part,
      .cov-table td.cov-ment, .cov-table td.cov-none { text-align: center; }
      .cov-table td.hwcell { text-align: center; white-space: nowrap; }
      .t1-legend .sw-ment { background: #F2F6F8; border-color: #e2e8ec; }

      /* Hardware families, one colour each, so a row reads at a glance. */
      .cov-table .hw, .hw { display: inline-block; font-size: 0.8em; font-weight: 600;
        letter-spacing: 0.02em; padding: 1px 5px; margin: 0 1px; border-radius: 3px; border: 1px solid; }
      .hw.loihi   { color: #155F8F; background: #E4F0F9; border-color: #1F77B4; }
      .hw.spinn   { color: #8F4A06; background: #FBEBDA; border-color: #D9760C; }
      .hw.synsense{ color: #64408C; background: #EEE7F7; border-color: #9467BD; }
      .hw.bss     { color: #1F6F5C; background: #E1F2EE; border-color: #2A8A7A; }
      .hw.akida   { color: #8A2F2F; background: #FBE9E7; border-color: #C0392B; }
      .hw.tn      { color: #4A4F5C; background: #ECEEF1; border-color: #6B7280; }
      .hw.fpga    { color: #7A5C00; background: #FBF3DF; border-color: #A97818; }

      /* Categorical badge under a survey name in the scope comparison. */
      .survey-tag { display: inline-block; margin-top: 0.12rem; padding: 1px 6px;
        border: 1px solid; border-radius: 3px; font-size: 0.66rem;
        font-weight: 700; letter-spacing: 0.02em; white-space: nowrap; }
      .tag-methods    { color: #344E9D; background: #E8ECF8; border-color: #3F5FBF; }
      .tag-hardware   { color: #38404E; background: #E8EAEE; border-color: #697482; }
      .tag-software   { color: #1F6F5C; background: #E1F2EE; border-color: #2A8A7A; }
      .tag-evaluation { color: #7A5C00; background: #FBF3DF; border-color: #A97818; }
      .tag-overview   { color: #64408C; background: #EEE7F7; border-color: #6D4C9F; }

      /* Toolbar above a filterable table. */
      .tbl-toolbar { display: flex; flex-wrap: wrap; gap: 0.45rem; align-items: center; margin: 0 0 0.55rem; }
      .tbl-toolbar input { font-size: 0.74rem; padding: 0.28rem 0.55rem; border: 1px solid #c8cfd8;
        border-radius: 7px; min-width: 190px; }
      .tbl-toolbar .chip { display: inline-block; padding: 0.2rem 0.65rem; border: 1px solid #c8cfd8;
        border-radius: 100px; font-size: 0.7rem; cursor: pointer; user-select: none; background: #fff;
        font-family: inherit; line-height: 1.4; color: inherit; }
      .tbl-toolbar .chip.active { background: #2698BA; border-color: #2698BA; color: #fff; }
      .tbl-toolbar .treset { font-size: 0.7rem; color: #2698BA; cursor: pointer;
        border: none; background: none; padding: 0; font-family: inherit; line-height: 1.4; }
      .tbl-toolbar .tcount { font-size: 0.68rem; color: #8a94a0; margin-left: auto; }
      table.ptable th .th-sort { font: inherit; color: inherit; background: none; border: 0;
        padding: 0; cursor: pointer; text-align: inherit; }
      table.ptable th .th-sort:hover { color: #2698BA; }
      table.ptable th.sorted .sort-ind { opacity: 1; color: #2698BA; }
      table.ptable tbody tr:hover { background: #f3fafc; }

      /* A four-digit year must never wrap, and the widest value here is a range. */
      table.ptable td.yr, table.ptable th.yr, table.ptable td.ctr {
        overflow-wrap: normal; word-break: keep-all; hyphens: none; }
      table.ptable th.yr, table.ptable td.yr { white-space: nowrap;
        min-width: 4.6em; width: 4.6em; font-variant-numeric: tabular-nums; text-align: center; }

      /* Genuinely wide data tables scroll inside their own container, never the page. */
      .ptable-wrap.t-scroll { overflow-x: auto; }
      .ptable-wrap.t-scroll table.ptable { min-width: 900px; }
      .ptable-wrap.t1-wide table.ptable { min-width: 0; }
      @media (max-width: 760px) {
        .ptable-wrap.t1-wide { overflow-x: auto; }
        .ptable-wrap.t1-wide table.ptable { min-width: 760px; }
      }

      .fig-todo { padding: 2rem; border: 2px dashed #b9c2cc; border-radius: 8px;
                  text-align: center; color: #778; font-size: 0.8rem; background: #f8f9fb; }
      d-article d-contents { grid-row: auto / span 26; }
"""


def main():
    if not TPL.exists():
        raise SystemExit(f'template not found: {TPL}')
    src = TPL.read_text()
    lines = src.split('\n')

    head = '\n'.join(lines[:758])          # through </d-contents>
    tail = '\n'.join(lines[1813:])         # from </d-article> to EOF

    # --- content substitutions, head ---
    head = head.replace(Q_TITLE, TITLE)
    # The abstract is replaced before the subtitle: upstream the subtitle is a verbatim
    # sentence of the abstract, so substituting it first would corrupt the longer string.
    qabs = re.search(r'let description = "(.*?)";', src, re.S).group(1)
    head = head.replace(qabs, ABSTRACT)
    head = head.replace(Q_SUB, SUB)
    head = re.sub(r'(<meta name="keywords" content=")[^"]*(")', r'\1' + KEYWORDS + r'\2', head)

    toc_rows = []
    for lvl, anchor, label in TOC:
        cls = '' if lvl == 1 else f' class="toc-sub{"" if lvl == 2 else "2"}"'
        toc_rows.append(f'            <div{cls}><a href="#{anchor}">{label}</a></div>')
    head = re.sub(r'(<h3>Contents</h3>\n).*?(\n\s*</nav>)',
                  lambda m: m.group(1) + '\n'.join(toc_rows) + m.group(2), head, flags=re.S)

    # The figure and the interactive tables need their own sheets; the rest of the
    # visual system is the template's and is left exactly as it is.
    head = head.replace('<link rel="stylesheet" href="assets/css/main.css?v=20260910w">',
                        '<link rel="stylesheet" href="assets/css/main.css?v=20260910w">\n'
                        '    <link rel="stylesheet" href="assets/figure.css">')
    head = head.replace('    </style>', EXTRA_CSS + '    </style>', 1)

    # The abstract block opens the article, exactly as upstream.
    head += (f'\n\n        <h2 id="abstract">Abstract</h2>\n\n<p>{ABSTRACT}</p>\n\n'
             f'<p class="index-terms"><strong>Index Terms</strong>&#8212;{INDEX_TERMS}</p>\n')

    # --- tail ---
    tail = re.sub(r'<d-bibliography src="[^"]*">',
                  '<d-bibliography src="assets/bibliography/references.bib">', tail)
    tail = re.sub(r'\n?\s*<script src="assets/js/(data|supplements|figs)\.js[^"]*"></script>', '', tail)
    tail = tail.replace('  </body>',
                        '  <script src="assets/tables.js"></script>\n'
                        '  <script type="module" src="assets/figure.js"></script>\n\n  </body>')

    (ROOT / 'site/shell-head.html').write_text(head)
    (ROOT / 'site/shell-tail.html').write_text(tail)
    print(f'shell-head.html : {len(head.split(chr(10)))} lines')
    print(f'shell-tail.html : {len(tail.split(chr(10)))} lines')


if __name__ == '__main__':
    main()
