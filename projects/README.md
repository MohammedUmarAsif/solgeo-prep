# SolGeo portfolio projects

These projects are intentionally small, composable tools rather than one
opaque application. Each package has deterministic tests, explicit provenance,
and a scientific boundary.

| Project | Remote-sensing question | Reusable output |
| --- | --- | --- |
| [01 SolGeo Prep](01-solgeo-prep/README.md) | Can public Sentinel-2 data be prepared reproducibly? | validated xarray cube and evidence package |
| [02 SolGeo Resolve](02-solgeo-resolve/README.md) | Can model-derived resolution be tiled and audited safely? | bounded inference, spectral metrics, uncertainty, warning mask |
| [03 SolGeo Change](03-solgeo-change/README.md) | Is a change persistent across time and direction? | change classes, persistence, uncertainty, review mask |
| [04 SolGeo Segment](04-solgeo-segment/README.md) | Which candidate features need human correction? | reviewable components and pixel-space GeoJSON |
| [05 SolGeo Embed](05-solgeo-embed/README.md) | Can frozen EO embeddings reduce label burden safely? | low-label classifier, confidence, leakage-aware evaluation |

The packages share a simple contract: validate inputs, return arrays plus
evidence, preserve uncertainty, and state what the output does not prove.
