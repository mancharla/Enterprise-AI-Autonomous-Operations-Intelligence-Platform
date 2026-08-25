import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import { getDatasets, uploadDataset, deleteDataset } from "../services/api";

const arr = (v) => Array.isArray(v) ? v : (Array.isArray(v?.items) ? v.items : []);

export default function Datasets() {
  const [rows, setRows] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const result = await getDatasets();
      setRows(arr(result));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function upload(e) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    setMessage("");
    try {
      const result = await uploadDataset(file);
      setMessage(result?.error_message
        ? `Dataset processed with warnings: ${result.error_message}`
        : `Dataset "${result?.original_filename || file.name}" uploaded successfully.`);
      setFile(null);
      e.target.reset();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function remove(id) {
    if (!window.confirm("Delete this dataset?")) return;
    try {
      await deleteDataset(id);
      setMessage("Dataset deleted successfully.");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return <>
    <PageHeader title="Datasets" description="Upload and monitor operational data quality for the current tenant." />
    {error && <div className="error-message">{error}</div>}
    {message && <div className="success-message">{message}</div>}

    <div className="page-card">
      <form onSubmit={upload} className="toolbar">
        <input type="file" accept=".csv,text/csv" onChange={e => setFile(e.target.files?.[0] || null)} required />
        <button className="btn-primary" disabled={uploading}>
          {uploading ? "Processing…" : "Upload CSV"}
        </button>
        <span className="muted">CSV is validated by the existing backend before operational records are created.</span>
      </form>
    </div>

    <div className="page-card">
      <h3>Uploaded datasets ({rows.length})</h3>
      {loading ? <div className="empty-state">Loading datasets…</div> :
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>File</th><th>Status</th><th>Rows</th><th>Valid</th><th>Invalid</th><th>Quality</th><th>Created</th><th /></tr></thead>
            <tbody>
              {rows.map(r => <tr key={r.id}>
                <td>{r.original_filename || r.name || `Dataset #${r.id}`}</td>
                <td><span className={`badge ${(r.status || "").toLowerCase()}`}>{r.status || "UNKNOWN"}</span></td>
                <td>{r.total_rows ?? 0}</td>
                <td>{r.valid_rows ?? 0}</td>
                <td>{r.invalid_rows ?? 0}</td>
                <td>{r.quality_score ?? 0}%</td>
                <td>{r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</td>
                <td><button className="btn-danger" onClick={() => remove(r.id)}>Delete</button></td>
              </tr>)}
            </tbody>
          </table>
          {!rows.length && <div className="empty-state">No datasets uploaded for this organization yet.</div>}
        </div>}
    </div>
  </>;
}
