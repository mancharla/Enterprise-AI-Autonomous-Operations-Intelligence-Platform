# Enterprise AI Autonomous Operations Intelligence — Frontend

React + Vite client for the existing FastAPI backend. The backend is treated as the source of truth; no backend endpoints, schemas, authentication logic, or database code are changed by this frontend.

## Run locally

```cmd
cd frontend
npm install
copy .env.example .env
npm run dev
```

PowerShell alternative:

```powershell
Copy-Item .env.example .env
```

Default URL: `http://localhost:5173`

Backend default: `http://127.0.0.1:8000`

## Frontend modules

- Authentication: register, login, logout, password recovery
- Tenant: organization and users
- Infrastructure: facilities and devices
- Data: CSV upload and dataset quality
- Analytics: KPIs, energy trend, risk distribution, facility comparison
- Forecasting: 24h/7d/30d/90d horizons, confidence intervals, model comparison
- Anomaly detection and severity views
- Root-cause analysis
- Optimization strategy ranking
- AI recommendations
- Autonomous operations
- Scenario simulation and comparison
- Real-time organization WebSocket monitoring and event ingestion
- Alerts and lifecycle actions
- ML model/pipeline controls exposed by the backend
- PDF/CSV device reports

## API integration

All API calls are centralized in `src/services/api.js`. JWT tokens returned by `/auth/login` are sent as `Authorization: Bearer <token>`. A 401 clears the session and redirects through the protected-route flow. File uploads use `multipart/form-data` exactly as required by `/datasets/upload`.

Set `VITE_API_BASE_URL` if the FastAPI server runs on a different host/port.
