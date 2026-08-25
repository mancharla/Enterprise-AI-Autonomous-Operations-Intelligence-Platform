import { useEffect, useState } from "react";
import { devicesApi } from "../../lib/api";

export default function DeviceSelect({ value, onChange, className = "" }) {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    devicesApi
      .list()
      .then((data) => {
        if (!active) return;
        setDevices(data);
        if (!value && data.length > 0) {
          onChange(String(data[0].id));
        }
      })
      .catch(() => {})
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <select
      className={`field-input ${className}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={loading}
    >
      {loading && <option>Loading devices…</option>}
      {!loading && devices.length === 0 && (
        <option value="">No devices found</option>
      )}
      {devices.map((device) => (
        <option key={device.id} value={device.id}>
          #{device.id} · {device.name}
        </option>
      ))}
    </select>
  );
}
