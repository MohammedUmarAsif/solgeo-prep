# SolGeo: A Reusable Local Earth-Observation Toolkit

## Executive conclusion

The strongest direction is a single, installable Python package named **SolGeo** that turns repeated EO work into tested commands and functions: data discovery, quality-controlled preprocessing, scientifically labelled super-resolution, multi-sensor change detection, segmentation, embedding extraction, validation, and evidence-grounded reporting. The existing UAE project becomes its first real use case, while future projects reuse the same core rather than copying notebook cells.

The first flagship module should be **SolGeo SR**: a Sentinel-2 super-resolution and validation pipeline built around ESA OpenSR/SEN2SR, not a new model trained from scratch. It should add the practical pieces that research repositories often leave to users: STAC/COG ingestion, cloud masking, tiled 8 GB-VRAM inference, georeferenced output, uncertainty and quality layers, before/after task evaluation, and unambiguous metadata saying how much of the output is AI-derived.

## Can satellite data be upscaled like DLSS?

Yes, with an essential scientific qualification. A model can infer a higher-resolution image from spatial, spectral, and sometimes temporal patterns, but it cannot retroactively measure details that the sensor never observed. The result is **model-derived super-resolution**, not a new 2.5 m observation.

ESA OpenSR already provides open-source models and tooling for Sentinel-2 super-resolution up to a nominal 2.5 m output grid.^1 Its 2025 latent-diffusion work explicitly emphasizes trustworthy multispectral super-resolution, and the companion `opensr-test` project provides a real-world benchmark rather than relying only on visually pleasing examples.^2 Real-ESRGAN is far more popular on GitHub, but it is a generic photographic restoration model trained with synthetic degradations; it should be included only as a visual baseline, never as the scientific default for multispectral EO.^3

Every SolGeo SR product should carry these fields:

| Field | Example |
|---|---|
| Source sensor/product | Sentinel-2 L2A |
| Native ground sampling distance | 10 m for RGB/NIR; 20 m for selected SWIR bands |
| Output pixel spacing | 2.5 m |
| AI scale factor | 4× from a 10 m source |
| Product status | Model-derived super-resolution; not sensor-measured 2.5 m data |
| Model and checksum | OpenSR model name, version, weight hash |
| Input acquisition IDs | Exact STAC item IDs |
| Preprocessing | Scale, SCL mask, resampling, normalization |
| Uncertainty/quality | confidence or ensemble-variance raster plus valid-data mask |
| Appropriate use | visual interpretation or tested downstream task |
| Prohibited claim | cadastral, engineering, legal-boundary, or sub-pixel ground truth |

This metadata is a genuine differentiator: it makes the tool useful to EO professionals without misrepresenting generative detail.

## What to reuse rather than rebuild

Repository popularity is a useful maintenance signal, not proof of scientific suitability. Approximate GitHub stars below reflect the pages reviewed in September 2026 and will change.

| Project | Approx. stars | Reuse in SolGeo | Do not duplicate |
|---|---:|---|---|
| `torchgeo/torchgeo` | 4.1k | CRS-aware datasets, samplers, transforms, pretrained EO weights | Generic geospatial ML data plumbing |
| `opengeos/GeoAI` | 3.3k | High-level segmentation/detection and map integration | Generic GeoAI wrappers |
| `opengeos/segment-geospatial` | ~4.0k | SAM-based raster segmentation and vector export | Promptable segmentation engine |
| `torchgeo/terratorch` | ~850 | Parameter-efficient fine-tuning and benchmarking of Prithvi, Clay, DOFA and related GeoFMs | Foundation-model training framework |
| `ESAOpenSR/SEN2SR` | ~170 | Sentinel-2 super-resolution inference | Core pretrained SR model |
| `ESAOpenSR/opensr-model` | ~140 | Trustworthy latent-diffusion SR experiments | Diffusion architecture and weights |
| `xinntao/Real-ESRGAN` | 35.8k | Optional non-scientific visual baseline | General photographic restoration |
| `ggml-org/llama.cpp` | 123k+ | Efficient local quantized LLM/VLM inference with CUDA and CPU/GPU split | Low-level local inference runtime |
| DuckDB Spatial | first-party extension | Local GeoParquet/GeoJSON spatial SQL and analytical summaries | Embedded spatial query engine |

TorchGeo and TerraTorch already cover a broad collection of geospatial foundation models and repeatable segmentation/classification/regression workflows.^4 OpenGeoAI and SamGeo already cover general AI-assisted geospatial segmentation and vector export.^5 SolGeo should therefore specialize in **reliable orchestration, UAE-relevant recipes, low-VRAM execution, provenance, and evaluation**, not create inferior replacements.

## Recommended toolkit architecture

Keep one repository and one public API:

```text
solgeo/
  catalog/       STAC search, item ranking, provenance
  prep/          AOI grids, masking, scaling, compositing, QA
  sr/            model adapters, tiling, blending, uncertainty
  change/        temporal baselines, CCDC-style adapters, SAR/optical fusion
  segment/       SAMGeo and supervised-model adapters
  embeddings/    Clay/Prithvi/TorchGeo embedding adapters
  validate/      spatial splits, metrics, spectral/task fidelity, reports
  report/        deterministic evidence cards; optional local LLM summary
  io/            COG, GeoTIFF, GeoParquet, Zarr, STAC output
  cli.py          solgeo prep|sr|change|segment|audit
```

The notebook remains a short orchestration and teaching layer. Production logic lives in typed modules with tests. A run configuration and manifest should be sufficient to reproduce every output.

## Progressive project sequence

### 1. SolGeo Core — cloud-native EO preparation

**Problem:** every project repeats scene search, duplicate handling, cloud masks, resampling, CRS alignment, compositing, and output naming.

**Build:** STAC-to-analysis-cube pipeline using PySTAC Client, ODC-STAC, xarray/Dask, Rasterio/Rioxarray, COG/Zarr, and structured run manifests.

**Novel value:** UAE-aware AOI/grid presets, explicit valid-pixel gates, deterministic scene-ranking, memory estimates, and a quality report before computation.

**Learning:** CRS, affine transforms, spectral scaling, masks, lazy computation, chunking, STAC, COGs, tests, and profiling.

### 2. SolGeo SR — trustworthy Sentinel-2 super-resolution

**Problem:** existing SR code often produces attractive images but leaves geospatial IO, memory constraints, uncertainty, metadata, and downstream validation to the user.

**Build:** an adapter over SEN2SR/OpenSR with overlapping tiled inference, half precision, edge blending, automatic VRAM-safe tile selection, COG export, and native-vs-AI product labels.

**Required baselines:** bicubic/Lanczos, DSen2 where compatible, and Real-ESRGAN for visual comparison only. Do not train a new network until these are reproduced.

**Evaluation:** PSNR/SSIM/SAM where paired reference data exists, spectral-angle and index preservation, edge consistency, uncertainty calibration, and downstream building/road/vegetation task performance. Visual sharpness alone is insufficient.

**Research contribution opportunity:** determine whether OpenSR improves UAE arid-urban boundary mapping without corrupting reflectance-derived indices; publish failure cases where bright sand, rooftops, coastlines, or shadows are hallucinated.

### 3. SolGeo Change — persistent urban-edge change

**Problem:** one before/after NDVI difference confuses seasonality, atmosphere, construction, landscaping, and sensor artefacts.

**Build:** robust temporal baselines, persistence rules, spectral-mixture/change features, Sentinel-1 confirmation, and uncertainty-aware candidate polygons.

**Research basis:** a 2024 broad-area construction study tested Landsat/Sentinel time-series and CCDC-style methods in Dubai; this provides a defensible baseline rather than an invented score.^6

**Output:** review candidates with evidence dates and alternative explanations—not automatic construction labels.

### 4. SolGeo Segment — review-assisted asset and land-cover extraction

**Problem:** planners need polygons, not only rasters, but hand digitization is slow.

**Build:** SAMGeo-assisted extraction of buildings, vegetation patches, water edges, construction footprints, or mangroves; add topology cleaning, minimum-mapping-unit rules, and GeoPackage/GeoParquet export.

**Novel value:** prompts and edits become versioned training evidence; human corrections are retained rather than discarded after export.

### 5. SolGeo Embeddings — semantic search and low-label modelling

**Problem:** labelled UAE EO datasets are scarce, while repeated training from pixels is expensive.

**Build:** extract frozen Clay, Prithvi, DOFA, or TorchGeo embeddings; compare lightweight classifiers on top of them against Random Forest and spectral baselines. Clay produces location/time-aware EO embeddings, while Prithvi-EO-2.0 is designed for multi-temporal EO tasks.^7

**8 GB strategy:** frozen backbone inference, small batches, FP16/BF16 where supported, gradient accumulation, parameter-efficient fine-tuning, and cropped patches. Start with embeddings; fine-tune only after a labelled split exists.

### 6. SolGeo Audit — scientific validation and model cards

**Problem:** many EO demos lack spatial splits, leakage checks, provenance, calibration, or limitations.

**Build:** spatial train/validation/test partitions, area-adjusted accuracy where applicable, confusion matrices, per-land-cover error, spectral fidelity, sensitivity analysis, run manifests, model cards, and reproducible HTML reports.

**Novel value:** one command—`solgeo audit run.yaml`—checks whether an output is fit for its declared use.

### 7. SolGeo Local Analyst — evidence-grounded local LLM

**Problem:** EO outputs are difficult for non-specialists to interrogate, but an LLM must not invent raster evidence.

**Build:** local structured reporting over manifests, statistics, methods, and retrieved documentation. The LLM may explain, draft reports, generate SQL, or suggest validation steps; deterministic code executes approved queries and computes all measurements.

**Runtime:** Ollama offers tool calling from Python, while llama.cpp supports CUDA kernels and CPU/GPU hybrid inference for models larger than VRAM.^8 On an 8 GB RTX 4070, favor a good 3B–8B quantized instruct model, short context, constrained JSON output, and one tool call at a time. Do not place a local LLM in the pixel-processing path.

## 8 GB RTX 4070 engineering profile

The GPU is sufficient for serious inference and small-scale fine-tuning if the design is disciplined:

- tiled inference with 128–512 pixel patches selected by measured memory;
- overlap plus weighted blending to prevent seams;
- FP16/BF16 inference and `torch.inference_mode()`;
- channels-last tensors and pinned-memory loaders where measured beneficial;
- one model loaded at a time;
- frozen encoders and small task heads before full fine-tuning;
- gradient accumulation and activation checkpointing for training;
- CPU/Dask for geospatial IO and GPU only for tensor-heavy kernels;
- cache embeddings and intermediate COG/Zarr products instead of recomputing them;
- benchmark wall time, peak VRAM, quality, and energy-relevant workload size.

The toolkit should detect available VRAM and choose a conservative tile/batch preset, then record the actual setting in the run manifest.

## Where the first genuine research gap is

Do not try to beat OpenSR by architecture novelty immediately. The achievable and credible gap is **task-aware, uncertainty-labelled super-resolution for arid UAE landscapes on consumer hardware**:

1. Reproduce OpenSR/SEN2SR on a fixed UAE benchmark.
2. Build paired or pseudo-paired evaluation using legitimately higher-resolution open imagery where licensing and alignment permit.
3. Test spectral/index preservation and downstream segmentation/change-detection improvement.
4. Characterize hallucination around sand/building edges, roads, coasts, shadows, and irrigated vegetation.
5. Add an abstention/quality layer that marks locations where SR should not be trusted.
6. Compare 10 m native, classical interpolation, and AI SR; publish wins and failures.

This is smaller than inventing a new foundation model, but more scientifically valuable than another unvalidated upscaling demo.

## Learning and review protocol

Each module should be built in four passes:

1. **Reproduce:** run an official baseline and explain its inputs, outputs, licence, assumptions, and metrics.
2. **Implement:** independently build one bounded adapter or missing workflow component.
3. **Validate:** create tests, a failure case, and a benchmark against a simple baseline.
4. **Teach back:** explain the data flow, mathematics, memory profile, and limitations without reading the code.

Every pull request should contain a small decision record, tests, measured output, one failure example, and a statement of what was learned independently. Git history then becomes evidence of engineering growth, not merely a collection of AI-generated files.

## GitHub strategy

Use one repository initially: `solgeo`. Tag stable releases and expose a small Python/CLI contract. Keep examples under `examples/uae-urban-edge`, `examples/mangrove-change`, and later use cases. A future project should require only a YAML configuration, AOI, and task-specific analysis—not copied loader or preprocessing code.

Recommended milestones:

- `v0.1`: STAC search, preprocessing, QA, COG export, UAE notebook.
- `v0.2`: OpenSR/SEN2SR adapter with tiled 8 GB inference and provenance.
- `v0.3`: SR benchmark, uncertainty/failure maps, spectral and task metrics.
- `v0.4`: optical/SAR persistent-change pipeline.
- `v0.5`: SAMGeo-assisted review and vector export.
- `v0.6`: frozen GeoFM embeddings and lightweight classifier benchmark.
- `v1.0`: stable CLI/API, documentation, regression datasets, model cards, and reproducible demonstrations.

## Immediate recommendation

Finish `v0.1` by making the current UAE notebook consume a stable `solgeo` API; then build `v0.2` as a thin SEN2SR/OpenSR inference adapter. Avoid a new SR architecture until the official model, classical baselines, geospatial metadata, 8 GB memory envelope, and evaluation suite all work end to end.

## Sources

1. ESA OpenSR. “[ESA OpenSR GitHub organization](https://github.com/ESAOpenSR).” Accessed September 2026.
2. Donike et al. “[Trustworthy Super-Resolution of Multispectral Sentinel-2 Imagery With Latent Diffusion](https://github.com/ESAOpenSR/opensr-model).” IEEE JSTARS, 2025; ESA OpenSR, “[opensr-test](https://github.com/ESAOpenSR/opensr-test).”
3. Wang et al. “[Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data](https://github.com/xinntao/Real-ESRGAN).” ICCVW, 2021.
4. TorchGeo. “[TorchGeo](https://github.com/torchgeo/torchgeo)” and “[TerraTorch](https://github.com/torchgeo/terratorch).” Accessed September 2026.
5. OpenGeoAI. “[GeoAI](https://github.com/opengeos/GeoAI)” and “[segment-geospatial](https://github.com/opengeos/segment-geospatial).” Accessed September 2026.
6. Science of Remote Sensing. “[Broad-area-search of new construction using time series analysis of Landsat and Sentinel-2 data](https://doi.org/10.1016/j.srs.2024.100138).” 2024.
7. Clay Foundation. “[Clay Foundation Model](https://clay-foundation.github.io/model/)”; NASA/IBM. “[Prithvi-EO-2.0](https://ntrs.nasa.gov/api/citations/20240015391/downloads/RSE%20Prithvi%20Global.pdf?attachment=true).”
8. Ollama. “[Tool calling](https://github.com/ollama/ollama/blob/main/docs/capabilities/tool-calling.mdx)”; ggml-org. “[llama.cpp](https://github.com/ggml-org/llama.cpp).” Accessed September 2026.
