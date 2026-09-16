# Vendor platform capability notes

These notes record the source and route boundary behind the generated capability matrix. They do not replace the canonical records in `data/platform-capabilities.json`.

Every capability record remains provisional. A platform can have a physically exercised route while the field-level claim remains provisional. This occurs when the canonical vendor source is still registered as metadata-only, when an example exercises a different upstream route, or when a compound contract field has only partial support.

The `route_ids` arrays contain ordered edge identifiers from `data/evidence-stack.json`. A `blocked` route state means that the named source model cannot traverse the complete chain under the audited default semantics. It does not imply that the target chip lacks all possible implementations of the requested behavior.

The platform notes are as follows.

- `loihi-1.md`
- `loihi-2.md`
- `spinnaker-1.md`
- `spinnaker-2.md`
- `speck-2f.md`
- `xylo-audio-2.md`
- `brainscales-2.md`
- `akida-1.md`
- `akida-2.md`
