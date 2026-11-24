import { useState } from "react";
const API = "http://localhost:8000";
const EXAMPLES = ["What are total sales by region?", "Top 3 products by sales in each category", "What percentage of orders were returned?"];

export default function App() {
  const [q, setQ] = useState(""); const [res, setRes] = useState(null); const [busy, setBusy] = useState(false);
  async function ask(text) {
    setBusy(true); setQ(text);
    const r = await fetch(`${API}/ask`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: text }) });
    setRes(await r.json()); setBusy(false);
  }
  return (
    <div style={{ maxWidth: 820, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>Ask Gift and Bliss Supplies</h1>
      <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && ask(q)} placeholder="Ask a question about sales..." style={{ width: "100%", padding: 10 }} />
      <p>{EXAMPLES.map((x) => <button key={x} onClick={() => ask(x)} style={{ marginRight: 8 }}>{x}</button>)}</p>
      {busy && <p>Thinking...</p>}
      {res?.error && <p style={{ color: "crimson" }}>{res.error}</p>}
      {res && !res.error && (<table border="1" cellPadding="6"><thead><tr>{res.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>{res.rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{String(v)}</td>)}</tr>)}</tbody></table>)}
      {/* TODO (M7): collapsible SQL panel, auto chart (Recharts), loading and error states, remember the chat history */}
    </div>
  );
}
