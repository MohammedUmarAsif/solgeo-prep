# SolGeo project sequence

This workspace is the first implementation slice of the SolGeo family. Each
project has a meaningful standalone name, a small public API, tests, a README,
and a documented boundary. The projects can later be composed into one desktop
or web application without moving scientific logic into the UI.

| Order | Project name | Purpose | Current state |
|---:|---|---|---|
| 1 | **SolGeo Prep** | STAC discovery, QA, indices, compositing, provenance | [Published](https://github.com/MohammedUmarAsif/solgeo-prep) |
| 2 | **SolGeo Resolve** | Trustworthy Sentinel-2 model-derived super-resolution | [Published](https://github.com/MohammedUmarAsif/solgeo-resolve) |
| 3 | **SolGeo Change** | Persistent optical/SAR change candidates | [Published](https://github.com/MohammedUmarAsif/solgeo-change) |
| 4 | **SolGeo Segment** | Human-correctable feature extraction and vector export | Planned |
| 5 | **SolGeo Embed** | Frozen EO embeddings and low-label task heads | Planned |
| 6 | **SolGeo Audit** | Spatial validation, uncertainty, model cards | Planned |
| 7 | **SolGeo Report** | Evidence-grounded local reporting | Planned |
| 8 | **SolGeo Studio** | Final composed interface using the stable modules | Deferred until 1–7 are usable |

## Shared contract

Every project should expose:

- a small importable Python API;
- a CLI or script for one reproducible workflow;
- deterministic tests using synthetic or tiny fixture data;
- provenance and explicit limitations in outputs;
- no unsupported scientific claims hidden behind a visual result;
- a README that explains intent, installation, capability, and failure modes.

The names are intentionally verbs or action-oriented concepts. **Prep** creates
analysis-ready inputs, **Resolve** improves spatial representation while
declaring that it is model-derived, **Change** finds persistent candidates,
**Segment** produces editable geometry, **Embed** creates reusable features,
**Audit** tests fitness for use, and **Report** explains only verified evidence.

## GitHub packaging decision

The first three implementations are now separate public repositories, each using
the same README, test, versioning, and packaging conventions. The original UAE
monitor and the sequence document remain in this workspace as the teaching and
composition context. Future projects should follow the same repository boundary;
the final SolGeo Studio repository can depend on their stable APIs.
