"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import { MapTrifold, SpinnerGap } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";

type EvidenceMapProps = {
  imagePath: string;
  bbox: [number, number, number, number];
};

export function EvidenceMap({ imagePath, bbox }: EvidenceMapProps) {
  const mapNode = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!mapNode.current) return;
    let map: import("maplibre-gl").Map | undefined;
    let cancelled = false;

    void import("maplibre-gl").then(({ Map, NavigationControl }) => {
      if (cancelled || !mapNode.current) return;
      const [west, south, east, north] = bbox;
      map = new Map({
        container: mapNode.current,
        style: {
          version: 8,
          sources: {
            evidence: {
              type: "image",
              url: imagePath,
              coordinates: [[west, north], [east, north], [east, south], [west, south]],
            },
          },
          layers: [{ id: "evidence", type: "raster", source: "evidence", paint: { "raster-opacity": 0.92 } }],
        },
        center: [(west + east) / 2, (south + north) / 2],
        zoom: 9,
        attributionControl: false,
      });
      map.addControl(new NavigationControl({ showCompass: false }), "bottom-right");
      map.once("load", () => setReady(true));
    });

    return () => {
      cancelled = true;
      map?.remove();
    };
  }, [bbox, imagePath]);

  return (
    <section className="map-block" aria-labelledby="map-heading">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">02 / Locate</p>
          <h2 id="map-heading">Where should a human look?</h2>
        </div>
        <span className="tool-chip"><MapTrifold size={16} /> local raster workspace</span>
      </div>
      <div className="map-frame">
        {!ready && <div className="map-loading"><SpinnerGap className="spin" size={22} /> loading local layer</div>}
        <div ref={mapNode} className="map-canvas" aria-label="Interactive evidence map" />
      </div>
      <div className="map-meta"><span>EPSG:32640 analysis grid</span><span>20 m screening layer</span><span>no remote basemap required</span></div>
    </section>
  );
}
