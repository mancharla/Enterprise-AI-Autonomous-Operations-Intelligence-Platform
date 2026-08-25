import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const WS_BASE_URL =
  import.meta.env.VITE_WS_URL ||
  API_BASE_URL.replace(/^http/, "ws");

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach the JWT to every request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize FastAPI error bodies into a single readable message,
// and force a logout on 401 so the app never gets stuck in a broken state.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error.response?.data;
    let message = "Something went wrong. Please try again.";

    if (Array.isArray(data?.detail)) {
      message = data.detail
        .map((item) => {
          const field = Array.isArray(item.loc)
            ? item.loc[item.loc.length - 1]
            : "field";
          return `${field}: ${item.msg}`;
        })
        .join(", ");
    } else if (typeof data?.detail === "string") {
      message = data.detail;
    } else if (typeof data?.message === "string") {
      message = data.message;
    } else if (error.message) {
      message = error.message;
    }

    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }

    return Promise.reject(new Error(message));
  }
);

// Every function below returns response.data directly, so callers
// never have to think about axios's response envelope.
const unwrap = (promise) => promise.then((res) => res.data);

/* ===================== AUTH ===================== */
export const authApi = {
  login: (email, password) =>
    unwrap(client.post("/auth/login", { email, password })),
  register: (payload) => unwrap(client.post("/auth/register", payload)),
  forgotPassword: (email) =>
    unwrap(client.post("/auth/forgot-password", { email })),
  resetPassword: (payload) =>
    unwrap(client.post("/auth/reset-password", payload)),
  me: () => unwrap(client.get("/auth/me")),
};

/* ===================== DASHBOARD ===================== */
export const dashboardApi = {
  get: (forecastHorizon = 24) =>
    unwrap(
      client.get("/dashboard/", {
        params: { forecast_horizon: forecastHorizon },
      })
    ),
};

/* ===================== DEVICES ===================== */
export const devicesApi = {
  list: () => unwrap(client.get("/devices")),
  get: (deviceId) => unwrap(client.get(`/devices/${deviceId}`)),
};

/* ===================== ALERTS ===================== */
export const alertsApi = {
  list: () => unwrap(client.get("/alerts")),
  summary: () => unwrap(client.get("/alerts/summary")),
  byDevice: (deviceId) => unwrap(client.get(`/alerts/device/${deviceId}`)),
  acknowledge: (alertId) =>
    unwrap(client.put(`/alerts/${alertId}/acknowledge`)),
  resolve: (alertId) => unwrap(client.put(`/alerts/${alertId}/resolve`)),
};

/* ===================== ANALYTICS ===================== */
export const analyticsApi = {
  overview: () => unwrap(client.get("/analytics/overview")),
  byDevice: (deviceId) =>
    unwrap(client.get(`/analytics/device/${deviceId}`)),
  byFacility: (facilityId) =>
    unwrap(client.get(`/analytics/facility/${facilityId}`)),
  trend: () => unwrap(client.get("/analytics/trend")),
  riskDistribution: () => unwrap(client.get("/analytics/risk-distribution")),
};

/* ===================== FORECASTING ===================== */
export const forecastingApi = {
  forDevice: (deviceId, horizonHours = 24) =>
    unwrap(
      client.get(`/forecasting/device/${deviceId}`, {
        params: { horizon_hours: horizonHours },
      })
    ),
  compareModels: (deviceId) =>
    unwrap(client.get(`/forecasting/device/${deviceId}/compare`)),
};

/* ===================== ANOMALIES ===================== */
export const anomaliesApi = {
  forDevice: (deviceId) => unwrap(client.get(`/anomalies/device/${deviceId}`)),
  summaryForDevice: (deviceId) =>
    unwrap(client.get(`/anomalies/device/${deviceId}/summary`)),
};

/* ===================== ROOT CAUSE ===================== */
export const rootCauseApi = {
  forDevice: (deviceId) => unwrap(client.get(`/root-cause/device/${deviceId}`)),
};

/* ===================== OPTIMIZATION ===================== */
export const optimizationApi = {
  forDevice: (deviceId) =>
    unwrap(client.get(`/optimization/device/${deviceId}`)),
};

/* ===================== RECOMMENDATIONS ===================== */
export const recommendationsApi = {
  forDevice: (deviceId) =>
    unwrap(client.get(`/recommendations/device/${deviceId}`)),
};

/* ===================== AUTONOMOUS OPERATIONS ===================== */
export const autonomousApi = {
  analyzeDevice: (deviceId, forecastHorizon = 24) =>
    unwrap(
      client.get(`/autonomous/device/${deviceId}`, {
        params: { forecast_horizon: forecastHorizon },
      })
    ),
  listActions: () => unwrap(client.get("/autonomous/actions")),
  getAction: (actionId) =>
    unwrap(client.get(`/autonomous/actions/${actionId}`)),
  updateActionStatus: (actionId, status) =>
    unwrap(
      client.patch(`/autonomous/actions/${actionId}/status`, { status })
    ),
};

export default client;
