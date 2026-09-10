"use client";

import { ArrowUpRight, CheckCircle, DownloadSimple, Info, LockKey, SlidersHorizontal } from "@phosphor-icons/react";
import { useMemo, useState } from "react";
import { BeforeAfter } from "./BeforeAfter";
import { EvidenceMap } from "./EvidenceMap";
import { InsightChart } from "./InsightChart";
import type { CaseStudy } from "../lib/types";

const DATA_ROOT = "/data/abu-dhabi-urban-edge";

export function CaseExplorer({ data }: { data: CaseStudy }) {
  const [activeLayer, setActiveLayer] = useState("after");
  const active = useMemo(
    () => data.layers.find((layer) => layer.id === activeLayer) ?? data.layers[1],
    [activeLayer, data.layers],
  );
  const before = `${DATA_ROOT}/${data.layers.find((layer) => layer.id === "before")?.path}`;
  const after = `${DATA_ROOT}/${data.layers.find((layer) => layer.id === "after")?.path}`;

  return (
    <main>
      <section className="case-hero page-shell">
        <div className="case-hero-copy">
          <div className="crumb"><span className="status-dot" /> case study / {data.case.case_id}</div>
          <p className="eyebrow">SolGeo Change Evidence</p>
          <h1>{data.case.title}</h1>
          <p className="lead">{data.question}</p>
          <div className="hero-actions"><a className="button button-dark" href="#explorer">Open evidence explorer <ArrowUpRight size={17} /></a><a className="text-link" href="/reproduce/">Read the build steps</a></div>
        </div>
        <aside className="status-panel">
          <div className="status-panel-top"><LockKey size={20} /><span>Claim gate active</span></div>
          <strong>{data.status.label}</strong>
          <p>{data.status.message}</p>
          <div className="status-rule" />
          <span className="micro-label">Next unlock</span>
          <span className="status-next">independently reviewed spatial labels</span>
        </aside>
      </section>

      <section className="case-facts page-shell" aria-label="Case facts">
        <div><span className="fact-label">Study window</span><strong>{data.case.baseline_period} → {data.case.comparison_period}</strong></div>
        <div><span className="fact-label">Location</span><strong>{data.case.aoi_name}</strong></div>
        <div><span className="fact-label">Analysis grid</span><strong>{data.case.analysis_resolution_m} m / {data.case.analysis_crs}</strong></div>
        <div><span className="fact-label">Evidence mode</span><strong>{data.case.data_mode}</strong></div>
      </section>

      <section id="explorer" className="explorer-shell page-shell">
        <BeforeAfter before={before} after={after} beforeLabel="baseline fixture" afterLabel="comparison fixture" />

        <div className="split-grid">
          <EvidenceMap imagePath={`${DATA_ROOT}/${active.path}`} bbox={data.case.bbox} />
          <section className="layer-block" aria-labelledby="layers-heading">
            <div className="section-heading compact-heading"><div><p className="eyebrow">Layer catalogue</p><h2 id="layers-heading">Follow the evidence</h2></div><SlidersHorizontal size={20} /></div>
            <div className="layer-list">
              {data.layers.map((layer) => (
                <button key={layer.id} className={`layer-button ${activeLayer === layer.id ? "is-active" : ""}`} onClick={() => setActiveLayer(layer.id)}>
                  <span className={`layer-swatch layer-${layer.kind}`} />
                  <span><strong>{layer.label}</strong><small>{layer.kind === "rgb" ? "visual context" : layer.kind === "agreement" ? "cross-sensor agreement" : "screening signal"}</small></span>
                  {activeLayer === layer.id && <CheckCircle size={17} weight="fill" />}
                </button>
              ))}
            </div>
            <div className="explain-note"><Info size={18} /><p><strong>How to read this.</strong> A layer is evidence only when its source, date, resolution, QA, and limitations travel with it. The score shown here helps prioritize review; it is not a probability.</p></div>
          </section>
        </div>

        <div className="split-grid lower-grid">
          <InsightChart points={data.time_series} />
          <section className="metrics-block" aria-labelledby="metrics-heading">
            <div className="section-heading compact-heading"><div><p className="eyebrow">04 / Measure</p><h2 id="metrics-heading">What the preview reports</h2></div><DownloadSimple size={20} /></div>
            <div className="metric-grid">
              <div><strong>{data.metrics.candidate_area_ha}</strong><span>candidate ha</span></div>
              <div><strong>{data.metrics.candidate_pixels}</strong><span>candidate pixels</span></div>
              <div><strong>{Math.round(data.metrics.agreement_fraction * 100)}%</strong><span>evidence agreement</span></div>
              <div><strong>{data.metrics.embedding_distance_p95}</strong><span>embedding p95</span></div>
            </div>
            <div className="download-row"><a className="button button-light" href={`${DATA_ROOT}/manifest.json`} download>Download manifest <DownloadSimple size={16} /></a><a className="text-link" href={`${DATA_ROOT}/candidates.geojson`} download>GeoJSON candidates</a></div>
          </section>
        </div>
      </section>

      <section className="methods-section page-shell">
        <div className="section-heading"><div><p className="eyebrow">05 / Understand</p><h2>Each tool has a job.</h2></div><p className="section-intro">The portfolio contribution is not “using AI.” It is showing how every method enters the evidence chain, where it helps, and where it must stop.</p></div>
        <div className="method-grid">{data.methods.map((method, index) => <article key={method.id} className="method-card"><span className="method-number">0{index + 1}</span><h3>{method.name}</h3><p>{method.role}</p><span className="method-line">contribution / documented</span></article>)}</div>
      </section>

      <section className="limitations-section page-shell"><div className="limitation-copy"><p className="eyebrow">Research discipline</p><h2>Strong work makes its uncertainty visible.</h2><p>Before this becomes a scientific result, the preview must be replaced by real source assets, independent labels, spatial holdouts, and a review of false alarms. That is not a disclaimer attached at the end. It is part of the product.</p></div><ul>{data.limitations.map((item) => <li key={item}><CheckCircle size={16} />{item}</li>)}</ul></section>
    </main>
  );
}
