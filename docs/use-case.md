# Chosen UAE problem: desert-edge urban expansion and cooling/water trade-offs

## Decision question

**When a UAE urban area expands into desert, agricultural, or coastal land, where are the likely environmental trade-offs greatest, and which locations deserve human planning review for green-blue infrastructure, ecological protection, or further evidence?**

This is deliberately a planning-intelligence question, not an automated approval system.

## Why this problem is grounded in UAE needs

- The UAE National Strategy to Combat Desertification 2030 targets land restoration, water-efficiency improvements, and modern technology/scientific research.
- The UAE Water Security Strategy 2036 and the national hydrogeological map make water-resource protection a real spatial-planning concern.
- Dubai 2040 explicitly links coordinated development with parks/open space, environmental spatial quality, resilience, and efficient land use.
- Abu Dhabi’s current planning technology work emphasizes connecting many spatial/operational sources to improve planning and livability decisions.
- Recent UAE research has already demonstrated the relevance of long-term LULC mapping, urban expansion, construction detection, and heat-risk stratification. Our contribution is to combine these ideas into an auditable, open, reproducible planning workflow rather than reproduce one isolated index map.

## What the tool will produce

For a selected urban edge and time window:

1. **Expansion signal:** areas with persistent increases in built-up/soil-brightness proxies and structural change.
2. **Ecological sensitivity signal:** vegetation, water, mangrove/coastal, protected-context, or restoration-relevant land-cover indicators.
3. **Cooling/water opportunity signal:** developed or developing areas with low vegetation/water adjacency, high surface dryness, or poor green-blue connectivity.
4. **Evidence card:** acquisition dates, data sources, index definitions, confidence/quality flags, and alternative explanations.
5. **Planning shortlist:** ranked locations for human review, not a prescriptive land-use decision.

## Research-inspired methods

| Question | First method | Later method |
|---|---|---|
| Where is new construction likely? | Temporal change in Sentinel-2 spectral/texture proxies; Landsat time series | CCDC/BASC-style change detection; Sentinel-1 coherence/backscatter |
| What type of land is affected? | ESA WorldCover and spectral features | UAE-specific supervised LULC model with spatial splits |
| Is vegetation/water stress present? | NDVI/EVI/NDWI/NDBI and robust temporal anomalies | Harmonized Landsat-Sentinel time series and drought covariates |
| Where might cooling/green-blue investment help? | Explainable adjacency/connectivity and deficit score | LST/LCZ fusion using Landsat or MODIS; calibrated priority index |
| How reliable is the result? | Cloud/SCL quality, temporal persistence, provenance | Human review set, precision/recall, spatial uncertainty, sensitivity analysis |

## What we will not claim

- Sentinel-2 spectral change is not proof of construction, desertification, groundwater depletion, or causality.
- NDVI is not a complete vegetation-health or restoration-success measure in hyper-arid environments.
- A cooling opportunity proxy is not land-surface temperature until thermal data are added and validated.
- A ranked shortlist is not a planning approval, environmental impact assessment, or government recommendation.

## Portfolio differentiation

The impressive part is the reasoning chain: an EO data cube, multi-sensor-ready architecture, spatially explicit change detection, uncertainty/provenance, a planning objective, and a human-review boundary. It demonstrates GIS/EO science and engineering judgment rather than only a colourful NDVI map.
