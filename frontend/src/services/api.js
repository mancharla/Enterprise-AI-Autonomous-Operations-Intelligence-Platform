/* ============================================================
   API CONFIGURATION
============================================================ */

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");


/* ============================================================
   TOKEN
============================================================ */

function getToken() {
  return localStorage.getItem("access_token");
}


/* ============================================================
   BUILD URL
============================================================ */

function buildUrl(endpoint) {

  // Allow absolute URLs
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }

  const path = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  return `${API_BASE_URL}${path}`;
}


/* ============================================================
   ERROR FORMATTER
============================================================ */

function formatError(data, status) {

  // FastAPI validation errors
  if (Array.isArray(data?.detail)) {

    return data.detail
      .map((error) => {

        const field =
          Array.isArray(error.loc)
            ? error.loc[error.loc.length - 1]
            : "field";

        return `${field}: ${error.msg}`;
      })
      .join("; ");
  }


  // FastAPI HTTPException
  if (typeof data?.detail === "string") {
    return data.detail;
  }


  // Custom API message
  if (typeof data?.message === "string") {
    return data.message;
  }


  // HTTP status messages
  if (status === 400) {
    return "Invalid request.";
  }

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to perform this action.";
  }

  if (status === 404) {
    return "The requested resource was not found.";
  }

  if (status === 409) {
    return "This operation conflicts with existing data.";
  }

  if (status >= 500) {
    return "Server error. Please try again later.";
  }

  return `Request failed (${status}).`;
}


/* ============================================================
   CORE API REQUEST
============================================================ */

export async function apiRequest(
  endpoint,
  options = {}
) {

  const token = getToken();


  /*
     Do NOT set Content-Type for FormData.
     Browser will automatically set:
     multipart/form-data; boundary=...
  */

  const headers = {
    ...(options.body instanceof FormData
      ? {}
      : {
        "Content-Type": "application/json",
      }),

    ...(options.headers || {}),
  };


  // JWT authentication
  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }


  const url = buildUrl(endpoint);


  console.log(
    `[API] ${options.method || "GET"} ${url}`
  );


  let response;

  try {

    response = await fetch(
      url,
      {
        ...options,
        headers,
      }
    );

  } catch (error) {

    console.error(
      "[API] Network error:",
      error
    );

    throw new Error(
      "Unable to connect to the backend server."
    );
  }


  /*
     204 No Content
  */

  if (response.status === 204) {
    return null;
  }


  /*
     Read response safely
  */

  const contentType =
    response.headers.get("content-type") || "";

  let data;


  try {

    if (
      contentType.includes(
        "application/json"
      )
    ) {

      data = await response.json();

    } else {

      data = await response.text();
    }

  } catch {

    data = {};
  }


  /*
     Handle errors
  */

  if (!response.ok) {

    console.error(
      `[API ERROR] ${response.status} ${url}`,
      data
    );


    /*
       Unauthorized
    */

    if (response.status === 401) {

      localStorage.removeItem(
        "access_token"
      );

      localStorage.removeItem(
        "user"
      );

      window.dispatchEvent(
        new Event("auth:expired")
      );
    }


    throw new Error(
      formatError(
        data,
        response.status
      )
    );
  }


  return data;
}


/* ============================================================
   GENERIC API METHODS
============================================================ */

const api = {

  get(endpoint) {

    return apiRequest(
      endpoint,
      {
        method: "GET",
      }
    );
  },


  post(endpoint, data) {

    return apiRequest(
      endpoint,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  },


  put(endpoint, data) {

    return apiRequest(
      endpoint,
      {
        method: "PUT",
        body: JSON.stringify(data),
      }
    );
  },


  patch(endpoint, data) {

    return apiRequest(
      endpoint,
      {
        method: "PATCH",
        body: JSON.stringify(data),
      }
    );
  },


  delete(endpoint) {

    return apiRequest(
      endpoint,
      {
        method: "DELETE",
      }
    );
  },


  upload(endpoint, formData) {

    return apiRequest(
      endpoint,
      {
        method: "POST",
        body: formData,
      }
    );
  },
};


/* ============================================================
   AUTHENTICATION
============================================================ */


/*
   LOGIN
*/

export async function loginUser(
  email,
  password
) {

  return apiRequest(
    "/auth/login",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );
}


/*
   REGISTER
*/

export async function registerUser(
  data
) {

  return apiRequest(
    "/auth/register",
    {
      method: "POST",

      body: JSON.stringify(data),
    }
  );
}


/*
   GET CURRENT USER
*/

export async function getMe() {

  return api.get(
    "/auth/me"
  );
}


/*
   FORGOT PASSWORD
*/

export async function forgotPassword(
  email
) {

  return api.post(
    "/auth/forgot-password",
    {
      email,
    }
  );
}


/*
   RESET PASSWORD
*/

export async function resetPassword(
  data
) {

  return api.post(
    "/auth/reset-password",
    data
  );
}


/* ============================================================
   DASHBOARD
============================================================ */

export async function getDashboard(
  horizon = 24
) {

  return api.get(
    `/dashboard/?forecast_horizon=${horizon}`
  );
}


/* ============================================================
   ORGANIZATION
============================================================ */

export async function getOrganization() {

  return api.get(
    "/organizations/me"
  );
}


export async function getOrganizationUsers() {

  return api.get(
    "/organizations/users"
  );
}


/* ============================================================
   FACILITIES
============================================================ */

export async function getFacilities() {

  return api.get(
    "/facilities"
  );
}


export async function getFacility(
  id
) {

  return api.get(
    `/facilities/${id}`
  );
}


export async function createFacility(
  data
) {

  return api.post(
    "/facilities",
    data
  );
}


export async function updateFacility(
  id,
  data
) {

  return api.put(
    `/facilities/${id}`,
    data
  );
}


export async function deleteFacility(
  id
) {

  return api.delete(
    `/facilities/${id}`
  );
}


/* ============================================================
   DEVICES
============================================================ */

export async function getDevices(
  facilityId
) {

  if (facilityId) {

    return api.get(
      `/devices?facility_id=${facilityId}`
    );
  }

  return api.get(
    "/devices"
  );
}


export async function getDevice(
  id
) {

  return api.get(
    `/devices/${id}`
  );
}


export async function createDevice(
  data
) {

  return api.post(
    "/devices",
    data
  );
}


export async function updateDevice(
  id,
  data
) {

  return api.put(
    `/devices/${id}`,
    data
  );
}


export async function deleteDevice(
  id
) {

  return api.delete(
    `/devices/${id}`
  );
}


/* ============================================================
   DATASETS
============================================================ */

export async function getDatasets() {

  return api.get(
    "/datasets"
  );
}


export async function uploadDataset(
  file
) {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  return api.upload(
    "/datasets/upload",
    formData
  );
}


export async function deleteDataset(
  id
) {

  return api.delete(
    `/datasets/${id}`
  );
}


/* ============================================================
   ANALYTICS
============================================================ */

export async function getAnalyticsOverview() {

  return api.get(
    "/analytics/overview"
  );
}


export async function getAnalyticsComparison() {

  return api.get(
    "/analytics/comparison"
  );
}


export async function getAnalyticsTrend() {

  return api.get(
    "/analytics/trend"
  );
}


export async function getRiskDistribution() {

  return api.get(
    "/analytics/risk-distribution"
  );
}


export async function getDeviceTrend(
  id
) {

  return api.get(
    `/analytics/device/${id}/trend`
  );
}


/* ============================================================
   FORECASTING
============================================================ */

export async function getForecast(
  id,
  horizon = 24
) {

  return api.get(
    `/forecasting/device/${id}?horizon_hours=${horizon}`
  );
}


export async function compareForecast(
  id
) {

  return api.get(
    `/forecasting/device/${id}/compare`
  );
}


export async function getForecastAccuracy(
  id
) {

  return api.get(
    `/forecasting/accuracy/device/${id}`
  );
}


export async function compareForecastAccuracy(
  id
) {

  return api.get(
    `/forecasting/accuracy/device/${id}/compare`
  );
}


/* ============================================================
   ANOMALIES
============================================================ */

export async function getAnomalies(
  id
) {

  return api.get(
    `/anomalies/device/${id}`
  );
}


export async function getAnomalySummary(
  id
) {

  return api.get(
    `/anomalies/device/${id}/summary`
  );
}


/* ============================================================
   ROOT CAUSE
============================================================ */

export async function getRootCause(
  id
) {

  return api.get(
    `/root-cause/device/${id}`
  );
}


/* ============================================================
   OPTIMIZATION
============================================================ */

export async function getOptimization(
  id
) {

  return api.get(
    `/optimization/device/${id}`
  );
}


/* ============================================================
   RECOMMENDATIONS
============================================================ */

export async function getRecommendation(
  id
) {

  return api.get(
    `/recommendations/device/${id}`
  );
}


/* ============================================================
   AUTONOMOUS OPERATIONS
============================================================ */

export async function getAutonomous(
  id,
  horizon = 24
) {

  return api.get(
    `/autonomous/device/${id}?forecast_horizon=${horizon}`
  );
}


export async function getAutonomousActions() {

  return api.get(
    "/autonomous/actions"
  );
}


export async function updateAutonomousAction(
  id,
  status
) {

  return api.patch(
    `/autonomous/actions/${id}/status`,
    {
      status,
    }
  );
}


/* ============================================================
   ALERTS
============================================================ */

export async function getAlerts() {

  return api.get(
    "/alerts"
  );
}


export async function getAlertSummary() {

  return api.get(
    "/alerts/summary"
  );
}


export async function getDeviceAlerts(
  deviceId
) {

  return api.get(
    `/alerts/device/${deviceId}`
  );
}


export async function getAlert(
  alertId
) {

  return api.get(
    `/alerts/${alertId}`
  );
}


export async function acknowledgeAlert(
  id
) {

  return api.put(
    `/alerts/${id}/acknowledge`
  );
}


export async function resolveAlert(
  id
) {

  return api.put(
    `/alerts/${id}/resolve`
  );
}


/* ============================================================
   SIMULATION
============================================================ */

export async function simulate(
  id,
  data
) {

  return api.post(
    `/simulation/device/${id}`,
    data
  );
}


export async function compareSimulation(
  id,
  data
) {

  return api.post(
    `/simulation/device/${id}/compare`,
    data
  );
}


/* ============================================================
   MACHINE LEARNING
============================================================ */

export async function getModels() {

  return api.get(
    "/ml/models"
  );
}


export async function runPipeline() {

  return api.post(
    "/ml/pipeline/run"
  );
}


export async function retrainModel(
  id
) {

  return api.post(
    `/ml/models/${id}/retrain`
  );
}


/* ============================================================
   REPORTS
============================================================ */

export async function getReport(
  id
) {

  return api.get(
    `/reports/device/${id}`
  );
}


export async function downloadReport(
  id,
  format
) {

  const token =
    getToken();

  const headers = {};

  if (token) {

    headers.Authorization =
      `Bearer ${token}`;
  }


  const response =
    await fetch(
      buildUrl(
        `/reports/device/${id}/${format}`
      ),
      {
        method: "GET",
        headers,
      }
    );


  if (!response.ok) {

    throw new Error(
      `Unable to download ${format.toUpperCase()} report (${response.status}).`
    );
  }


  return response.blob();
}


/* ============================================================
   STREAMING
============================================================ */

export async function ingestStreamEvent(
  data
) {

  return api.post(
    "/stream/events",
    data
  );
}


/* ============================================================
   WEBSOCKET
============================================================ */

export function getWebSocketUrl(
  organizationId
) {

  const base =
    API_BASE_URL.replace(
      /^http/,
      "ws"
    );


  const token =
    encodeURIComponent(
      getToken() || ""
    );


  return (
    `${base}/ws/organization/` +
    `${organizationId}?token=${token}`
  );
}


/* ============================================================
   LOGOUT
============================================================ */

export function logoutUser() {

  localStorage.removeItem(
    "access_token"
  );

  localStorage.removeItem(
    "user"
  );
}


/* ============================================================
   EXPORTS
============================================================ */

export {
  API_BASE_URL,
};

export default api;