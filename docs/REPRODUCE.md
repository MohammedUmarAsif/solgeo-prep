# Reproduce SolGeo Change Evidence

## 1. Python environment

From the repository root:

```powershell
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## 2. Build the learning bundle

```powershell
uv run solgeo-prep case build `
  --config configs/abu-dhabi-urban-edge.yaml `
  --output runs/abu-dhabi-urban-edge-preview
```

The bundle contains teaching images, two COG screening rasters, a candidate
GeoJSON, `case-study.json`, and `manifest.json` with checksums and claim status.
The values are synthetic and are not a geographic conclusion.

## 3. Publish the bundle to the local website

```powershell
uv run solgeo-prep case publish `
  --run runs/abu-dhabi-urban-edge-preview `
  --web-root web/public
```

## 4. Run the website

```powershell
cd web
npm install
npm run dev
```

Open `http://localhost:3000`. The site is a static reader and does not need a
database, API key, GPU, or server-side raster processing.

## 5. Production checks

```powershell
npm run typecheck
npm run build
```

Before publishing real evidence, verify source dates, provider encoding,
coverage QA, CRS/transform, output checksums, independent labels, and the claim
gate. Replace synthetic assets only through the case bundle command.
