import { useState } from "react";
import PageHeader from "../components/PageHeader";
import DevicePicker from "../components/DevicePicker";
import { getRootCause } from "../services/api";

export default function RootCause() {
  const [device, setDevice] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!device) return;
    setLoading(true);
    setError("");
    try {
      setData(await getRootCause(device));
    } catch (e) {
      setData(null);
      setError(e?.message || "Unable to analyze root cause.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader title="Root Cause Analysis" description="Correlate operational signals and rank contributing factors." />
      <div className="page-card">
        <div className="toolbar">
          <DevicePicker value={device} onChange={setDevice} />
          <button className="btn-primary" onClick={run} disabled={!device || loading}>
            {loading ? "Analyzing..." : "Analyze root cause"}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {data && (
        <>
          <div className="stats-grid">
            <div className="stat-card"><div className="stat-label">Current energy</div><div className="stat-value">{data.current_energy_kwh ?? "—"}</div></div>
            <div className="stat-card"><div className="stat-label">Baseline</div><div className="stat-value">{data.baseline_energy_kwh ?? "—"}</div></div>
            <div className="stat-card"><div className="stat-label">Deviation</div><div className="stat-value">{data.energy_deviation_percent ?? "—"}%</div></div>
            <div className="stat-card"><div className="stat-label">Confidence</div><div className="stat-value">{typeof data.confidence === "number" ? `${(data.confidence * 100).toFixed(1)}%` : "—"}</div></div>
          </div>

          <div className="two-col">
            <div className="page-card">
              <h3>Primary root cause</h3>
              <h2>{data.root_cause || "No root cause identified"}</h2>
              {data.recommended_action && <p className="muted">Recommended action: {data.recommended_action}</p>}
            </div>

            <div className="page-card">
              <h3>Ranked factors</h3>
              {(data.ranked_factors || []).length === 0 ? (
                <p className="muted">No contributing factors returned.</p>
              ) : (
                data.ranked_factors.map((x, i) => {
                  const score = Number(x.score) || 0;
                  const width = Math.min(100, Math.max(0, score * 100));
                  return (
                    <div key={i} style={{ marginBottom: 12 }}>
                      <div className="toolbar" style={{ justifyContent: "space-between" }}>
                        <span>{x.factor}</span>
                        <strong>{x.score}</strong>
                      </div>
                      <div className="progress"><span style={{ width: `${width}%` }} /></div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}
