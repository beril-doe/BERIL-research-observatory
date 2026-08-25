// The search island: a text field, an optional max-results input, and a list of
// result cards showing each hit's summary (abstract). Deliberately minimal — the
// goal is the end-to-end flow (input -> /api/search -> rendered summaries).
import { useState } from "react";

const DEFAULT_LIMIT = 10;
const MAX_LIMIT = 50;

export function SearchApp({ searchEndpoint }) {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [notice, setNotice] = useState(null); // {message} for a friendly error

  async function runSearch(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) {
      setNotice({ message: "Enter a search term." });
      return;
    }
    setStatus("loading");
    setNotice(null);

    const params = new URLSearchParams({ q, limit: String(clampLimit(limit)) });
    try {
      const resp = await fetch(`${searchEndpoint}?${params.toString()}`, {
        headers: { Accept: "application/json" },
      });
      const body = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        // Backend always sends {error, message} on expected failures.
        setStatus("error");
        setResults([]);
        setTotal(0);
        setNotice({ message: body.message || `Search failed (HTTP ${resp.status}).` });
        return;
      }
      setResults(Array.isArray(body.results) ? body.results : []);
      setTotal(typeof body.total === "number" ? body.total : (body.results || []).length);
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setResults([]);
      setTotal(0);
      setNotice({ message: `Could not reach the search service: ${err.message}` });
    }
  }

  return (
    <div>
      <form onSubmit={runSearch} style={FORM_STYLE}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search BERIL projects…"
          aria-label="Search query"
          style={{ ...INPUT_STYLE, flex: 1, minWidth: "12rem" }}
        />
        <input
          type="number"
          value={limit}
          min={1}
          max={MAX_LIMIT}
          onChange={(e) => setLimit(e.target.value === "" ? "" : Number(e.target.value))}
          aria-label="Max results"
          title={`Max results (1–${MAX_LIMIT})`}
          style={{ ...INPUT_STYLE, width: "6rem" }}
        />
        <button type="submit" className="btn" disabled={status === "loading"}>
          {status === "loading" ? "Searching…" : "Search"}
        </button>
      </form>

      {notice && (
        <div className="card" style={NOTICE_STYLE} role="status">
          {notice.message}
        </div>
      )}

      {status === "done" && !notice && (
        <p className="text-muted text-small" style={{ marginBottom: "var(--space-4)" }}>
          {total} result{total === 1 ? "" : "s"}
        </p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        {results.map((r) => (
          <ResultCard key={r.uri} result={r} />
        ))}
      </div>

      {status === "done" && results.length === 0 && !notice && (
        <div className="card" style={{ padding: "var(--space-6)", textAlign: "center" }}>
          <p className="text-muted">No matches. Try different terms.</p>
        </div>
      )}
    </div>
  );
}

function ResultCard({ result }) {
  const { uri, score, abstract } = result;
  return (
    <article className="card" style={{ padding: "var(--space-4)" }}>
      <header style={CARD_HEADER_STYLE}>
        <code className="text-small" style={{ wordBreak: "break-all" }}>{uri}</code>
        {typeof score === "number" && (
          <span className="text-muted text-small" style={{ whiteSpace: "nowrap" }}>
            score {score.toFixed(3)}
          </span>
        )}
      </header>
      <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{abstract || "(no summary available)"}</p>
    </article>
  );
}

function clampLimit(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return DEFAULT_LIMIT;
  return Math.max(1, Math.min(Math.trunc(n), MAX_LIMIT));
}

const FORM_STYLE = {
  display: "flex",
  gap: "var(--space-3)",
  flexWrap: "wrap",
  marginBottom: "var(--space-6)",
};
const INPUT_STYLE = {
  padding: "var(--space-2) var(--space-3)",
  borderRadius: "var(--radius, 6px)",
  border: "1px solid var(--border-color, #444)",
  background: "var(--input-bg, #1a1a1a)",
  color: "inherit",
  fontSize: "1rem",
};
const NOTICE_STYLE = {
  padding: "var(--space-4)",
  marginBottom: "var(--space-4)",
  borderLeft: "3px solid #ffb454",
};
const CARD_HEADER_STYLE = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "baseline",
  gap: "var(--space-3)",
  marginBottom: "var(--space-2)",
};
