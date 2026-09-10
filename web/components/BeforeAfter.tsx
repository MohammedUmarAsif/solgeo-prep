"use client";

import { ArrowsHorizontal, CaretLeft, CaretRight } from "@phosphor-icons/react";
import Image from "next/image";
import { useState } from "react";

type BeforeAfterProps = {
  before: string;
  after: string;
  beforeLabel: string;
  afterLabel: string;
};

export function BeforeAfter({ before, after, beforeLabel, afterLabel }: BeforeAfterProps) {
  const [position, setPosition] = useState(50);

  return (
    <section className="comparison-block" aria-labelledby="comparison-heading">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">01 / Compare</p>
          <h2 id="comparison-heading">What changed at a glance?</h2>
        </div>
        <span className="tool-chip"><ArrowsHorizontal size={16} /> draggable evidence</span>
      </div>
      <div className="comparison-frame">
        <div className="comparison-image comparison-image-after">
          <Image src={after} alt={`${afterLabel} satellite preview`} fill sizes="(max-width: 800px) 100vw, 1180px" />
          <span className="image-label image-label-right">{afterLabel}</span>
        </div>
        <div className="comparison-image comparison-image-before" style={{ width: `${position}%` }}>
          <Image src={before} alt={`${beforeLabel} satellite preview`} fill sizes="(max-width: 800px) 100vw, 1180px" />
          <span className="image-label image-label-left">{beforeLabel}</span>
        </div>
        <div className="comparison-handle" style={{ left: `${position}%` }} aria-hidden="true">
          <span><CaretLeft size={15} /><CaretRight size={15} /></span>
        </div>
        <label className="sr-only" htmlFor="comparison-slider">Move the comparison divider</label>
        <input
          id="comparison-slider"
          className="comparison-slider"
          type="range"
          min="0"
          max="100"
          value={position}
          onChange={(event) => setPosition(Number(event.target.value))}
        />
      </div>
      <p className="caption">The imagery shown here is a deterministic method fixture. The production case will use real seasonal composites with source dates, coverage, and QA beside the slider.</p>
    </section>
  );
}
