import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import { getModels, runPipeline, retrainModel } from "../services/api";
import DevicePicker from "../components/DevicePicker";

const arr = v => Array.isArray(v) ? v : (Array.isArray(v?.models) ? v.models : []);

export default function MLModels() {
  const [models, setModels] = useState([]);
  const [device, setDevice] = useState("");
  const [h, setH] = useState("24");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const result = await getModels();
      setModels(arr(result));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function run() {
    setRunning(true);
    setError("");
    setMessage("");
    try {
      // Backend POST /ml/pipeline/run accepts no request body.
      const result = await runPipeline();
      setMessage(result?.message || "ML pipeline completed successfully.");
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  async function retrain(id) {
    try {
      setError("");
      const result = await retrainModel(id);
      setMessage(result?.message || "Model retrained successfully.");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return <>
    <PageHeader title="ML Pipeline & Models" description="Inspect registered model versions and run the existing backend ML pipeline." />
    {error && <div className="error-message">{error}</div>}
    {message && <div className="success-message">{message}</div>}

    <div className="page-card">
      <div className="toolbar">
        <DevicePicker value={device} onChange={setDevice} />
        <select value={h} onChange={e => setH(e.target.value)}>
          <option value="24">24h</option>
          <option value="168">7d</option>
          <option value="720">30d</option>
        </select>
        <button className="btn-primary" onClick={run} disabled={running}>
          {running ? "Running pipeline…" : "Run ML pipeline"}
        </button>
        <span className="muted">The current backend pipeline endpoint does not accept device or horizon parameters.</span>
      </div>
    </div>

    <div className="page-card">
      <h3>Registered models ({models.length})</h3>
      {loading ? <div className="empty-state">Loading models…</div> :
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>ID</th><th>Model</th><th>Type</th><th>Version</th><th>Status</th><th>Accuracy</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>Created</th><th /></tr></thead>
            <tbody>
              {models.map(m => {
                const id = m.model_id ?? m.id;
                return <tr key={id}>
                  <td>#{id}</td>
                  <td>{m.model_name || m.name || "Model"}</td>
                  <td>{m.model_type || "—"}</td>
                  <td>{m.version || "—"}</td>
                  <td>{m.status || "—"}</td>
                  <td>{m.accuracy != null ? `${m.accuracy}%` : "—"}</td>
                  <td>{m.mae ?? "—"}</td>
                  <td>{m.rmse ?? "—"}</td>
                  <td>{m.mape != null ? `${m.mape}%` : "—"}</td>
                  <td>{m.created_at ? new Date(m.created_at).toLocaleString() : "—"}</td>
                  <td>{id != null && <button className="btn-secondary" onClick={() => retrain(id)}>Retrain</button>}</td>
                </tr>;
              })}
            </tbody>
          </table>
          {!models.length && <div className="empty-state">No registered models returned by the backend. Run the ML pipeline to create the first model.</div>}
        </div>}
    </div>
  </>;
}
