# SolGeo Embed

SolGeo Embed provides lightweight, reusable feature handling for low-label
Earth-observation modelling. It extracts deterministic patches, normalizes
feature vectors, compares embeddings by cosine similarity, and trains a small
prototype classifier without fine-tuning a foundation model.

The design leaves Clay, Prithvi, DOFA, and TorchGeo adapters optional. Frozen
embeddings and a transparent task head are the default path for an 8 GB GPU.

## Capability

- non-overlapping and overlapping patch extraction;
- NaN-safe feature standardization using training statistics;
- cosine similarity search;
- class prototypes and confidence margins;
- serializable feature-cache fingerprints;
- leakage-resistant spatial group splits and explicit review-rate metrics;
- NumPy-only tests and no hidden model downloads.

## Scientific boundary

Embeddings do not replace labels, spatial splits, or task-specific baselines.
Always compare a prototype head against a spectral or Random Forest baseline and
report spatial leakage, class imbalance, and uncertainty.

Keep neighbouring patches in the same spatial split, then report accuracy,
macro-F1, and the fraction routed to human review.
