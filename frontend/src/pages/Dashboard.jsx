import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard, getFacilities, getDevices, getDatasets } from "../services/api";
import PageHeader from "../components/PageHeader";
import AsyncState from "../components/AsyncState";

const num = (v, d = 0) => Number.isFinite(Number(v)) ? Number(v) : d;
const fmt = (v, digits = 1) => num(v).toLocaleString(undefined, { maximumFractionDigits: digits });

function Card({ label, value, sub }) {
  return <div className="stat-card">
    <div className="stat-label">{label}</div>
    <div className="stat-value">{value}</div>
    {sub && <div className="muted" style={{ marginTop: 5, fontSize: 11 }}>{sub}</div>}
  </div>;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [fallback, setFallback] = useState(null);
  const [h, setH] = useState("24");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    getDashboard(Number(h))
      .then((result) => { if (active) setData(result); })
      .catch(async (e) => {
        // The backend intentionally returns 404 when an organization has no
        // OperationalRecord rows. Load resource counts so the dashboard is
        // still useful and clearly explains what is missing.
        if (!active) return;
        try {
          const [facilities, devices, datasets] = await Promise.all([
            getFacilities(), getDevices(), getDatasets()
          ]);
          setFallback({
            facilities: Array.isArray(facilities) ? facilities.length : 0,
            devices: Array.isArray(devices) ? devices.length : 0,
            datasets: Array.isArray(datasets) ? datasets.length : 0,
          });
          setError(e.message);
        } catch {
          setError(e.message);
        }
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [h]);

  return <>
    <PageHeader
      title="Operations Command Center"
      description="Enterprise-wide operational health, forecast risk and autonomous decision intelligence."
      action={<select value={h} onChange={e => setH(e.target.value)}>
        <option value="24">24 hour forecast</option>
        <option value="168">7 day forecast</option>
        <option value="720">30 day forecast</option>
        <option value="2160">90 day forecast</option>
      </select>}
    />

    <AsyncState loading={loading} error={data ? "" : ""}>
      {data ? <>
        <div className="stats-grid">
          <Card label="Facilities" value={num(data.organization?.total_facilities)} />
          <Card label="Devices" value={num(data.organization?.total_devices)} />
          <Card label="Total energy" value={`${fmt(data.energy?.total_energy_kwh, 2)} kWh`} />
          <Card label="Overall risk" value={data.risk?.overall_risk || "LOW"} sub={`Risk score ${fmt(data.risk?.risk_score, 2)}`} />
        </div>
        <div className="stats-grid">
          <Card label="Anomalies" value={num(data.anomalies?.total)} sub={`Critical ${num(data.anomalies?.critical)} · High ${num(data.anomalies?.high)}`} />
          <Card label="Avg load" value={fmt(data.operations?.average_load)} />
          <Card label="Utilization" value={`${fmt(data.operations?.average_utilization_percent)}%`} />
          <Card label="Expected savings" value={`${fmt(data.optimization?.expected_savings_percent)}%`} sub={`${fmt(data.optimization?.expected_energy_savings_kwh, 2)} kWh`} />
        </div>
        <div className="two-col">
          <div className="page-card">
            <h3>Recommended strategy</h3>
            <h2>{data.optimization?.recommended_strategy || "No strategy generated"}</h2>
            <p className="muted">{data.insights?.[0] || "Optimization strategy generated from current operational conditions."}</p>
            <div className="page-actions">
              <Link className="btn-primary" to="/optimization">Review optimization</Link>
              <Link className="btn-secondary" to="/autonomous">Open autonomous analysis</Link>
            </div>
          </div>
          <div className="page-card">
            <h3>Operational insights</h3>
            {(data.insights || []).map((x, i) => <p key={i} className="muted">• {x}</p>)}
          </div>
        </div>
      </> : fallback ? <>
        <div className="page-card">
          <h3>Operational data is not available yet</h3>
          <p className="muted">
            Your backend dashboard requires at least one valid operational record for this organization.
            The resource counts below confirm that the frontend and API connection are working.
          </p>
          {error && <p className="error-message">{error}</p>}
          <div className="stats-grid">
            <Card label="Facilities" value={fallback.facilities} />
            <Card label="Devices" value={fallback.devices} />
            <Card label="Datasets" value={fallback.datasets} />
            <Card label="Operational records" value="0" />
          </div>
          <div className="page-actions">
            <Link className="btn-primary" to="/datasets">Upload operational CSV</Link>
            <Link className="btn-secondary" to="/facilities">Check facilities</Link>
          </div>
        </div>
      </> : null}
    </AsyncState>
  </>;
}
