import { ChartLineUp } from "@phosphor-icons/react";

type Point = { date: string; ndvi: number; ndbi: number };

export function InsightChart({ points }: { points: Point[] }) {
  const width = 640;
  const height = 180;
  const padding = 20;
  const values = points.flatMap((point) => [point.ndvi, point.ndbi]);
  const minimum = Math.min(...values, -0.5);
  const maximum = Math.max(...values, 0.5);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - minimum) / (maximum - minimum)) * (height - padding * 2);
  const line = (key: "ndvi" | "ndbi") => points.map((point, index) => `${x(index)},${y(point[key])}`).join(" ");

  return (
    <section className="chart-block" aria-labelledby="chart-heading">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">03 / Context</p>
          <h2 id="chart-heading">Does the signal persist?</h2>
        </div>
        <span className="tool-chip"><ChartLineUp size={16} /> index trace</span>
      </div>
      <div className="chart-frame">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="NDVI and NDBI index traces">
          <line x1={padding} x2={width - padding} y1={y(0)} y2={y(0)} className="chart-zero" />
          <polyline points={line("ndvi")} className="chart-line chart-line-ndvi" />
          <polyline points={line("ndbi")} className="chart-line chart-line-ndbi" />
        </svg>
        <div className="chart-legend"><span><i className="legend-dot ndvi-dot" /> NDVI</span><span><i className="legend-dot ndbi-dot" /> NDBI</span></div>
      </div>
      <p className="caption">A persistent-change review should use matched seasons and repeated observations. One unusual pixel is an invitation to inspect, not a conclusion.</p>
    </section>
  );
}
