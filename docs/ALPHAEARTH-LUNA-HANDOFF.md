# SolGeo research and implementation handoff

Evidence checked: 10 September 2026. Target execution: a new Luna task with High reasoning, in this project. This document supersedes the earlier recommendation to prioritize super-resolution: first deliver reliable preprocessing and an AlphaEarth/Sentinel change benchmark, then a radar application. All modules below are proposed unless explicitly described as existing.

## Decision

Build **SolGeo Change Evidence**: an inexpensive, reproducible pipeline that tests whether annual AlphaEarth representations improve detection and classification of persistent urban and ecological change in Abu Dhabi, while dated Sentinel-1/2 observations establish supporting evidence and timing. Add a separate flood-recovery case study, followed by an InSAR deformation benchmark aligned with Synspective roles.

The research question is: **Under a fixed annotation budget, do annual embeddings improve spatial transfer and reduce false change alarms over seasonal optical/SAR baselines in arid landscapes?** This is a testable hypothesis, not an established research gap or a promised improvement. Search for overlapping studies before claiming novelty. A publishable contribution requires reproducible experiments and independent assessment; adding models alone does not confer PhD or senior-engineer standing.

## AlphaEarth: what we can actually use

Google's annual Satellite Embedding product represents locations using 64 learned features at 10 m spacing. These features summarize observations; they are not reflectance bands, finer imagery, or an event feed. Use them for classifiers, clustering, similarity and annual change candidates, retaining native imagery for interpretation. The Earth Engine collection is `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`. [Google dataset catalog](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL).

The original 2025 paper establishes the sparse-label mapping motivation. It is background evidence, not proof of performance in UAE cities. [AlphaEarth paper](https://arxiv.org/abs/2507.22291).

For local access, Google's July 2026 documentation describes provider-paid COG hosting for 2017–2025, a GeoParquet spatial index, signed-byte storage with -128 nodata, and nonlinear decoding. Filter the index by AOI/year, read raster windows, mask nodata, cast to float, then decode `sign(q) * (q / 127.5)**2`. Aggregate decoded vectors and normalize; averaging raw encoded bytes is incorrect. Preserve A00–A63 order and reject zero-norm vectors. Record the required Google/DeepMind attribution. [Official GCS specification](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme).

Access implementation must discover actual filenames through the official index; never guess tile paths. Use the local COG route first, with Earth Engine an optional authenticated adapter. Verify quota/terms before using hosted computation. Free data does not imply unlimited free compute. Do not assume model weights or a local AlphaEarth training implementation are available: this plan consumes released embeddings.

For temporal comparison, normalize valid decoded vectors and compute cosine distance as a candidate feature. A high distance is not a calibrated change probability. Train and evaluate an independent transition classifier. Do not assign physical meanings to individual embedding axes.

**Leakage rule:** for any forecast issued in April 2024, the full 2024 embedding is unavailable and includes later observations. Use only a prior embedding demonstrably published by the issue date; record both observation time and release/availability time. A retrospective analysis can use full-year embeddings only when clearly labelled retrospective. Dataset version changes also require checking cross-year comparability.

## Employer evidence and portfolio mapping

These were accessible first-party vacancy pages on the research date; availability and language requirements must be rechecked before applying. English titles below translate Japanese titles where relevant.

| Employer / evidence | Actual requirement or priority | Portfolio evidence to produce | Remaining gap |
|---|---|---|---|
| Synspective SAR Image Processing Engineer | Pipeline ownership, SAR formation and DSP, maintainable Python/C++/Rust, product QA and English; typically 3+ years; Tokyo attendance | Tested radar product workflow, calibration/geometry QA, profiling, failure recovery, architecture and review history | A Sentinel downstream notebook does not demonstrate raw SAR focusing or professional experience |
| Synspective SAR Research Engineer | Mathematics, Python prototyping, reading technical literature, independent hypothesis testing | Reproduction plus ablations, uncertainty, negative results, concise technical report | Research claims need independent evaluation |
| Synspective Mission Analysis Systems Engineer | Python development, web applications, Git teamwork, GCP/AWS; data pipelines and anomaly detection valued | Versioned API, repeatable jobs, idempotency, logs and failure tests | Local execution does not establish deployed cloud experience |
| Synspective Customer Engineer | GIS, explaining technical results to clients; Japanese report/proposal skills; optical/SAR/InSAR valued | Planner brief, limitation-aware maps, reproducible analysis and teach-back | Language and client-facing experience remain separate requirements |
| DMT, public operational evidence | Integrated planning data, infrastructure context, planning analytics and livability | Validated change polygons, GIS-ready data contracts, exposure summaries and data-quality reports | No current DMT GIS vacancy was verified in this search; do not invent job requirements |

Sources: [SAR processing vacancy](https://careers.synspective.com/o/sar-image-processing-engineer), [SAR research vacancy](https://careers.synspective.com/o/kr8lcfsbty), [mission analysis vacancy](https://careers.synspective.com/o/v5gaga6sn1), [customer engineer vacancy](https://careers.synspective.com/o/914nlkffuw), [DMT digital planning announcement, June 2026](https://dmt.gov.ae/en/Media-Centre/News/DMT-Launches-Digital-Planning-Technologies-To-Shape-More-Livable-Communities).

DMT is a government department. Its planning work provides a relevant use case, not evidence that it commissioned this project. Older ADM planning-submission specifications may inform schema exercises, but their current authority must be checked before claiming compliance. [ADM historical specification](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf).

## Ranked applications and scientific boundaries

| Priority | Application and decision | Data and method | Evaluation and limits |
|---|---|---|---|
| 1 | Abu Dhabi persistent land-change review: which polygons should analysts inspect? | AlphaEarth annual features; seasonal Sentinel-2; matched Sentinel-1 geometry; logistic/RF baselines and feature fusion | Independent annotated transitions, spatial holdouts, false alarms per km², polygon precision/recall, temporal detection delay from dated scenes |
| 2 | UAE flood extent and recovery: where was water detected and which mapped roads intersect it? | Event and pre-event Sentinel-1, optical checks, terrain and permanent-water context | Event-held-out IoU/F1, false positives on sand/shadow, mapping latency; an observation after the peak cannot measure peak inundation |
| 3 | Infrastructure ground movement and earthquake displacement case study | Sentinel-1 SLC interferometry with established processing, MintPy time series, independent GNSS/reference products | Line-of-sight displacement, coherence, atmosphere, reference point and residuals; no automatic vertical-motion or structural-damage claim |
| 4 | Reservoir/river surface-water decline, then forecast | Sentinel/Landsat water series, suitable SWOT reaches/lakes, gauges and weather where available | Seasonal/persistence baselines, blocked forecasting tests, missingness and interval coverage; area is not volume or discharge |
| 5 | Flood forecasting research | Gauged catchment precipitation/discharge and weather forecasts available at issue time; OpenHydroNet or NeuralHydrology adapter | Lead-time-specific skill, event precision/recall, reliability and persistence baseline; riverine models do not transfer automatically to UAE urban flash flooding |
| 6 | Does AI super-resolution improve a particular mapping task? | Native imagery vs interpolation vs ESA OpenSR on identical labelled test areas | Spectral and task metrics, alignment and hallucination review; finer output spacing does not prove finer measured resolution |

Start flood work with a documented UAE historical event after verifying satellite coverage and independent labels. If labels or suitable acquisition timing are absent, retain the case as exploratory and evaluate on a public labelled flood benchmark first. National operational predictions need gauges, drainage/culvert information, terrain quality and agency validation beyond this portfolio.

For river drying, choose a gauged river outside the UAE for a transferable forecast demonstration; use UAE reservoirs/wadis for monitoring only where observations support it. Require a defined endpoint such as probability of water extent falling below a specified threshold at a stated lead time. Account for reservoir operations where data exist. SWOT provides surface-water measurements and recent discharge estimates, but local reach coverage, uncertainty and revisit gaps must be checked. [NASA SWOT](https://science.nasa.gov/mission/swot/), [2026 river-discharge release](https://science.nasa.gov/blogs/science-news/2026/01/05/swot-offers-river-discharge-estimate/).

Earthquake measurement should mean a retrospective coseismic displacement map validated against a published reference. Exact earthquake occurrence prediction is not a defensible deliverable. [USGS scientific position](https://www.usgs.gov/programs/earthquake-hazards/earthquake-facts-earthquake-fantasy).

## Current tools worth incorporating

- **AlphaEarth COG adapter:** highest immediate value; reusable features without local foundation-model inference.
- **OlmoEarth Nano/Tiny through rslearn:** a current alternative for date-controlled S1/S2 features and small-model experiments. Its official repository publishes multiple sizes and inference-only uv setup. Benchmark the smallest supported model first; model size alone does not guarantee 8 GB fit. Inspect code, weights and dataset licences separately before use. [Model repository](https://github.com/allenai/olmoearth_pretrain), [official rslearn integration](https://github.com/allenai/rslearn/blob/master/docs/foundation_models/OlmoEarth.md).
- **Google OpenHydroNet:** open implementations of riverine forecasting architectures, including the repository's December 2025 production-model reference. Use for reproduction on a suitable catchment before any local adaptation; code availability is not a guarantee of weights, forecasts or gauge access. [Repository](https://github.com/google-research/flood-forecasting).
- **MintPy plus established interferogram processing:** MintPy consumes processed, coregistered/unwrapped interferograms; it is not a raw Sentinel-1 focusing engine. Keep SLC/InSAR processing in a separately documented environment if native dependencies demand it. [MintPy input/output contract](https://github.com/insarlab/MintPy/blob/main/docs/README.md).
- **Dolphin/OPERA validation workflows:** useful references for displacement processing, masks and independent GNSS comparisons; check product footprint before choosing a study area. Do not assume US OPERA examples cover UAE/Japan. [OPERA validation](https://github.com/OPERA-Cal-Val/calval-DISP).
- **Existing TorchGeo/TerraTorch/OpenSR adapters:** retain as optional experiments after a baseline passes. Avoid installing every framework into the core environment. See the earlier `research-toolkit-roadmap.md` for original sources; recheck releases and licences at implementation time.

Select repositories by task fit, reproducibility, releases, licensing and maintainability. Star counts do not establish accuracy. Local LLMs may explain validated statistics and retrieved methods; a deterministic report template should remain the default, preserving token and GPU budgets.

## Research design that supports serious claims

Freeze a benchmark definition before model selection: AOIs, observation periods, transitions, annotation protocol, label provenance and minimum mapping unit. Use several separate urban-edge windows with water, sand, vegetation, construction and stable controls. Lock test labels; allocate disjoint polygons/regions, not random neighbouring pixels. Assign every crop from a parent scene/site to the same split. Include an unobserved region and an unobserved year where feasible.

Compare B0 spectral/seasonal features + logistic/RF; B1 AlphaEarth + the same classifier; B2 B0 + AlphaEarth; B3 B2 + matched SAR; B4 optional small OlmoEarth features. Give baselines comparable tuning budgets. Evaluate label efficiency at fixed annotation budgets, per-class precision/recall, area and boundary error, false alarms per km², confidence calibration, abstention coverage, inference time and peak memory. Estimate intervals with site/block resampling rather than treating adjacent pixels as independent.

Explicitly test bright-sand/roof confusion, seasonal irrigation, tides, partial coverage, cloud edges, radar layover and registration offsets. Embedding distances are scores; train/calibrate probabilities separately on validation data. Check whether pretrained models used evaluation labels or derived products: WorldCover-derived labels cannot by themselves prove independent performance of a model exposed to WorldCover. An uncertainty map requires a defined method; ensemble disagreement alone is not calibrated accuracy.

Publish a short paper-style report: question, prior work, reproducible method, ablation table, uncertainty, failure gallery, limitations, compute cost and data/code licence. A null result can be useful. Do not describe the work as state of the art without a fair external benchmark.

## Existing repository: repair before extending

Previous tests and syntax checks do not establish that the live notebook is correct. Audit these specific risks visible in the earlier implementation:

1. STAC `max_items` truncates history silently; implement explicit pagination or a clearly reported budget stop. Deduplicate using acquisition/tile/processing metadata, not missing tile fallbacks.
2. The loader guesses reflectance scale from a global maximum, triggering large computation and potentially mishandling Sentinel processing offsets. Verify the provider's encoding, scale and offset; apply them exactly once before ratios.
3. `add_indices` captures band arrays before replacing them with cleaned arrays. Ensure index formulas consume the cleaned, common-valid mask.
4. QA based only on inverse SCL membership can count NaN/nodata as valid. Require finite data in every used band and explicit AOI coverage. Separate cloud fraction from missing coverage.
5. Categorical SCL needs nearest-neighbour alignment; continuous bands require a documented resampler and common grid. Never interpolate class IDs.
6. A default <=10% scene cloud filter is a selection rule, not a guarantee. Apply per-pixel QA, provide actual clear-AOI fractions, and explain when a strict threshold leaves insufficient observations.
7. Monthly gaps and the first-half/latest comparison introduce seasonality and insufficient-baseline errors. Add per-pixel counts, matched-season baselines, minimum observations and persistence tests. Never convert missing change into zero change.
8. The current linear NDVI score is a heuristic; it neither establishes stress nor detects urban expansion. Name it accordingly until validated transitions exist.
9. Colab currently depends on a local `src` directory and broad unpinned installs. Provide a project ZIP bootstrap or a real tagged GitHub URL once published; discover project roots from notebook/subdirectory/Colab paths. Do not invent a repository URL.
10. Audit GeoTIFF CRS, affine transform, nodata and outputs; add a unique run folder, configs, versions, QA, source item IDs, checksums and exclusions. Keep signed asset tokens out of durable manifests.

## Implementation sequence and acceptance gates

**M0 — repository audit and corrected small pipeline.** Read nearest AGENTS.md, `C:/Users/sayed/.agents/skills/modern-python/SKILL.md` and the shared toolkit index. Inspect actual files and preserve unrelated changes. Use uv, Ruff, pytest and the skill's type-check guidance. Add meaningful tests for masking, scaling, nodata, temporal leakage, geometry and export; no broad imagery execution is needed at this stage.

**M1 — AlphaEarth adapter and short notebook.** Create an installable `solgeo` package with config, IO, QA and embedding modules. Resolve index entries, perform bounded reads, decode signed bytes correctly and produce features plus a manifest. Include a tiny synthetic encoding fixture with known expected values; label it synthetic. Notebook sections: objective, environment, config, discovery, QA, feature extraction, baseline, evaluation, GIS export and interpretation. Offline tests plus source-verified interfaces can be completed now; mark live read verification pending user testing.

**M2 — first benchmark.** Provide annotation templates and a fixed split manifest. Until reviewed labels exist, export candidates and evaluation code with an explicit incomplete-benchmark status. Do not generate accuracy numbers from synthetic fixtures or weak labels and present them as UAE results.

**M3 — radar flood case.** Add same-orbit/date-pair handling, calibrated backscatter, terrain/quality masks, permanent-water context and event mapping. Preserve units and distinguish linear values from dB; diagnose urban double bounce rather than assuming all flood water is radar-dark. Produce native-resolution rasters and review polygons.

**M4 — InSAR learning case.** Reproduce one supported reference dataset, then design a UAE/Japan case only after coverage, RAM/disk and validation evidence are established. Report LOS sign convention, wavelength, reference point, coherence and corrections. Use SLC phase or processed interferograms; GRD intensity cannot replace phase.

**M5 — prediction and optional SR.** Implement hydrological forecasting only when issue-time inputs and held-out outcomes are available. Add SR only as a separately measured ablation. Separate these extensions from M0–M3 completion.

Suggested layout: `src/solgeo/{config,catalog,quality,embeddings,change,io,evaluation}.py`, optional `sar/` and `hydrology/`, `notebooks/`, `configs/`, `tests/`, `docs/`, and ignored `runs/<run-id>/{inputs,qa,features,models,metrics,figures,exports}`. Use functions and immutable config objects; add classes only at external-provider/model boundaries. Expose the same functions through notebook and CLI.

Target 8 GB VRAM; verify actual hardware when GPU work begins. AlphaEarth + linear/RF baselines can run on CPU. Window rasters and sample training rows rather than loading whole 64-channel tiles. Measure RAM/VRAM before choosing batches. Use optional model environments and small inference batches; do not claim FP16 or GPU acceleration improves a workload without measurement. InSAR may be constrained more by disk and RAM than GPU.

## Learning and cost discipline

For each milestone, provide one independently attempted exercise, one failure to diagnose, one source to read and a five-minute explanation challenge. Examples: calculate cosine distance, demonstrate leakage with an annual feature, repair a nodata mask, interpret LOS versus vertical displacement, or compare a flood forecast to persistence. Keep an evidence ledger distinguishing authored, AI-assisted and independently reproduced work.

Read this brief once, reuse the source list, batch independent inspection, and keep changes bounded by milestones. Revisit research only for an unresolved implementation contract or outdated dependency. Keep a concise progress file for new sessions. Strong engineering evidence includes reproducibility, debugging and readable interfaces; it does not require cloud spend, a giant agent framework or continual model calls.

## Prompt for a new Luna High task

Read `docs/ALPHAEARTH-LUNA-HANDOFF.md` in the Remote Sensing project and implement M0 and M1 first, then the M2 annotation/evaluation scaffolding. Follow the shared AGENTS conventions and modern-python skill. Inspect actual repository state; do not trust previous completion claims. Make a concise plan and implement a small reusable package plus a polished, runnable Colab/VS Code notebook. Preserve existing work and make the earlier notebook a compatible entry point where practical. Verify with bounded offline tests, lint/type checks and notebook validation. Do not run large satellite downloads, full imagery analyses, GPU training or paid services; the user will test the live notebook. Be explicit about pending live verification and missing independent labels. Save a learning guide and continuation status. Use the verified AlphaEarth COG specification, preserve provenance and prevent temporal leakage. Prefer stable dependencies and compact modules. Do not claim PhD-level novelty, validated predictions or hiring readiness without evidence. Continue until the scoped deliverables are complete or a concrete external dependency prevents progress.
