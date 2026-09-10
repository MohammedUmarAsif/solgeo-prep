# SolGeo exercises and thinking prompts

These are deliberately small. Attempt each one before looking for a more
advanced implementation.

## Python and remote sensing

1. Why does NDVI use a ratio instead of a raw band difference?
2. What happens when the denominator is zero? Add a test for the chosen rule.
3. Create one cloudy SCL pixel and trace where it becomes NaN.
4. Explain why a 20 m analysis grid is not 2.5 m sensor data.
5. Print the dimensions of the demo cube and explain every axis.

## AlphaEarth and ML

1. Why must decoding happen before averaging embeddings?
2. What should happen when one year is nodata and the other is valid?
3. Create identical and orthogonal vectors. Predict their cosine distances.
4. Does a large vector norm alone mean change? Explain.
5. Why can embedding distance be useful without being a calibrated probability?
6. What leakage occurs when a full-year retrospective embedding is used for an
   alert claimed to have been issued before that year ended?

## GIS and validation

1. Why are adjacent pixels not independent validation samples?
2. Draw a spatial block split for an urban edge. Which pixels stay together?
3. Name three causes of false change in an arid city.
4. What does a COG add to a plain GeoTIFF?
5. Why should missing observations not become zero change?

## Portfolio communication

1. Explain the project in 30 seconds without saying “AI” first.
2. Which output would you show a recruiter first, and why?
3. Which result would you refuse to claim without labels?
4. Describe one negative result that would still improve the tool.
5. Point to one place where another analyst can reproduce your result.

## Build your own case

Choose a different AOI and write a one-page case contract containing the human
decision, baseline and comparison seasons, native resolution, evidence layers,
minimum mapping unit, independent validation source, three failure modes, and
one claim that is out of scope.

Do not start with a model. Start with the decision and the evidence needed to
support it.
