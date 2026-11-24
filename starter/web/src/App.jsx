import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
const EXAMPLES = ["What are total sales by region?", "Top 3 products by sales in each category", "What percentage of orders were returned?"];

export default function App() {
  const [q, setQ] = useState(""); const [res, setRes] = useState(null); const [busy, setBusy] = useState(false);
  async function ask(text) {
    setBusy(true); setQ(text);
    try {
      const r = await fetch("/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: text }) });
      setRes(await r.json());
    } catch { setRes({ error: "Could not reach the API. Is it still running on port 8000?" }); }
    setBusy(false);
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
      {res?.sql && <details><summary>Show the SQL</summary><pre>{res.sql}</pre></details>}
      {res && !res.error && res.columns.length === 2 && typeof res.rows[0]?.[1] === "number" && (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={res.rows.map((r) => ({ name: String(r[0]), value: r[1] }))}>
            <XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
