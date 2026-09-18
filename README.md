# From Neural Networks to Neuromorphic Execution

A deployment-centered survey of ANN-to-SNN conversion, software stacks, and silicon. The built page is `index.html`, served with GitHub Pages from the root of `main`.

## Layout

- `site/` the fifteen section fragments and the figure fragments that `tools/build-site.py` assembles into `index.html`
- `data/` the source registry, evidence records, platform capabilities, and the site and figure manifests
- `tools/` the build and gate scripts (registry, bibliography, data views, figures, site, checks)
- `assets/` scripts, styles, and the generated bibliography
- `research/` the research notes, inventories, and the writing handoff behind the text

## Build

From the repository root, the full chain is

```
python3 tools/build-source-registry.py && python3 tools/validate-sources.py && python3 tools/verify-source-registry-build.py && python3 tools/build-bib.py && python3 tools/check-bibliography.py
python3 tools/build-data-views.py && python3 tools/check-counts.py && python3 tools/check-consistency.py && python3 tools/validate-evidence.py && python3 tools/verify-target-tools.py && python3 tools/validate-manifests.py
python3 tools/build-figure-architecture.py && python3 tools/install-figures.py && python3 tools/build-figure-guide.py && python3 tools/build-site.py
python3 tools/check-figures.py && python3 tools/check-section-refs.py && python3 tools/check-evidence-markers.py && python3 tools/check-figure-map.py && node tools/verify-figure-engine.mjs && python3 tools/verify-renumber-tools.py && python3 tools/verify-figure-tools.py
```

Generated files (`index.html`, `assets/figures.css`, `assets/bibliography/references.bib`, `data/source-registry.json`, `data/generated/`) are never edited by hand.
