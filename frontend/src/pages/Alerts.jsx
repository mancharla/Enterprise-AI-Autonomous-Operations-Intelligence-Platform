import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import { getAlerts, getAlertSummary, acknowledgeAlert, resolveAlert } from "../services/api";

const arr = v => Array.isArray(v) ? v : (Array.isArray(v?.items) ? v.items : []);

export default function Alerts() {
  const [rows, setRows] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [a, s] = await Promise.all([getAlerts(), getAlertSummary()]);
      setRows(arr(a));
      setSummary(s || null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function action(id, type) {
    try {
      setError("");
      if (type === "ack") await acknowledgeAlert(id);
      else await resolveAlert(id);
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return <>
    <PageHeader title="Operational Alerts" description="Monitor and resolve high-impact operational events." />
    {error && <div className="error-message">{error}</div>}
    {summary && <div className="stats-grid">
      <div className="stat-card"><div className="stat-label">Total</div><div className="stat-value">{summary.total_alerts ?? 0}</div></div>
      <div className="stat-card"><div className="stat-label">Open</div><div className="stat-value">{summary.open_alerts ?? 0}</div></div>
      <div className="stat-card"><div className="stat-label">Critical</div><div className="stat-value">{summary.critical_alerts ?? 0}</div></div>
      <div className="stat-card"><div className="stat-label">High</div><div className="stat-value">{summary.high_alerts ?? 0}</div></div>
    </div>}

    <div className="page-card">
      <h3>Alerts ({rows.length})</h3>
      {loading ? <div className="empty-state">Loading alerts…</div> :
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>Severity</th><th>Type</th><th>Facility</th><th>Device</th><th>Message</th><th>Status</th><th>Created</th><th /></tr></thead>
            <tbody>
              {rows.map(r => <tr key={r.id}>
                <td><span className={`badge ${(r.severity || "").toLowerCase()}`}>{r.severity || "—"}</span></td>
                <td>{r.alert_type || "—"}</td>
                <td>#{r.facility_id ?? "—"}</td>
                <td>#{r.device_id ?? "—"}</td>
                <td>{r.message || "—"}</td>
                <td>{r.status || "—"}</td>
                <td>{r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</td>
                <td><div className="toolbar">
                  {r.status === "OPEN" && <button className="btn-secondary" onClick={() => action(r.id, "ack")}>Acknowledge</button>}
                  {r.status !== "RESOLVED" && <button className="btn-danger" onClick={() => action(r.id, "resolve")}>Resolve</button>}
                </div></td>
              </tr>)}
            </tbody>
          </table>
          {!rows.length && <div className="empty-state">No alerts have been generated for this organization yet.</div>}
        </div>}
    </div>
  </>;
}
