import Link from "next/link";
import { ArrowLeft, CheckCircle, TerminalWindow } from "@phosphor-icons/react/dist/ssr";

export default function ReproducePage() {
  return <main><nav className="site-nav page-shell"><Link href="/" className="brand"><span className="brand-mark">S</span><span>SolGeo / field notes</span></Link><Link href="/" className="text-link"><ArrowLeft size={16} /> home</Link></nav><section className="article-hero page-shell"><p className="eyebrow">Reproduce / start here</p><h1>A small loop you can understand.</h1><p className="lead">The project grows from a deterministic fixture into real evidence one contract at a time.</p></section><article className="article-body page-shell"><section><div className="step-heading"><span>01</span><h2>Install the project</h2></div><div className="code-block"><TerminalWindow size={18} /><pre><code>uv sync
uv run pytest
uv run ruff check .</code></pre></div><p>These commands create the environment, run the tests, and check the Python style. Start here even if you remember very little.</p></section><section><div className="step-heading"><span>02</span><h2>Build the case bundle</h2></div><div className="code-block"><TerminalWindow size={18} /><pre><code>uv run solgeo-prep case build \
  --config configs/abu-dhabi-urban-edge.yaml \
  --output runs/abu-dhabi-urban-edge-preview</code></pre></div><p>Open the output folder. Read <code>case-study.json</code> first, then inspect the images, COGs, GeoJSON, and manifest.</p></section><section><div className="step-heading"><span>03</span><h2>Run the interface</h2></div><div className="code-block"><TerminalWindow size={18} /><pre><code>cd web
npm install
npm run dev</code></pre></div><p>The browser interface is a static reader for the bundle. Processing remains offline and reproducible.</p></section><section><div className="step-heading"><span>04</span><h2>Try one exercise</h2></div><ul className="clean-list"><li><CheckCircle size={17} />Change the fusion weights in <code>change.py</code>.</li><li><CheckCircle size={17} />Rebuild the bundle and compare candidate area.</li><li><CheckCircle size={17} />Explain why the score is not a probability.</li><li><CheckCircle size={17} />Write one test before changing the function again.</li></ul></section></article></main>;
}
