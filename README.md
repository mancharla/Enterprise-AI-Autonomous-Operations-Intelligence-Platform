# Enterprise AI Autonomous Operations Intelligence Platform

## Overview
A full-stack AI-powered enterprise platform that monitors operations, forecasts future demand, detects anomalies, identifies root causes, generates optimization recommendations, and performs scenario simulations across multiple organizations, facilities, and devices.

## Main Features
- Multi-tenant organization management
- JWT authentication and RBAC
- Facility and device management
- Dataset upload and validation
- Time-series forecasting
- ML model management
- Anomaly detection
- Root-cause analysis
- Optimization engine
- Scenario simulation
- AI recommendations
- Real-time alerts and analytics
- Dashboard and reporting
- PDF/CSV exports

## Architecture
React Frontend → FastAPI Backend → ML/Business Logic → PostgreSQL  
                                                     ↓  
                                                Redis/Celery  
                                                     ↓  
                                                ML Processing

## Technology Stack
### Frontend
- React
- Vite
- React Router
- Axios
- Recharts
- Lucide React

### Backend
- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT
- Pydantic

### AI/ML
- Pandas
- NumPy
- Scikit-learn
- Prophet
- Statsmodels
- XGBoost

### Supporting Technologies
- WebSockets
- ReportLab
- OpenPyXL

## Core AI Workflow

Operational Data
→ Data Validation
→ Forecasting
→ Anomaly Detection
→ Root Cause Analysis
→ Optimization
→ Simulation
→ Recommendation
→ Alert/Action

## Forecasting Engine
Predicts future operational behavior using historical time-series data.

Supports:
- Resource consumption
- Operational load
- Device usage
- Facility demand
- 24-hour, 7-day, 30-day and 90-day forecasts

## Anomaly Detection
Identifies unusual operational behavior such as:
- Usage spikes
- Device abnormalities
- Sensor inconsistencies
- Resource leakage
- Performance degradation

Techniques include Isolation Forest, One-Class SVM and statistical methods.

## Optimization Engine
Determines the best operational action based on forecasts, costs, resources and risks.

Example:
"Redistribute workload from an overloaded facility to an available facility."

## Simulation Engine
Performs what-if analysis without affecting the real system.

Examples:
- Demand increase
- Device failure
- Facility shutdown
- Resource shortage
- Workforce reduction

## Root Cause Analysis
Analyzes correlations and important features to identify possible causes of anomalies.

Example:
High energy consumption → High cooling usage → Possible cooling inefficiency.

## Multi-Tenant Architecture
Each organization operates as an isolated tenant.

Organization
→ Users
→ Facilities
→ Devices
→ Datasets
→ Forecasts
→ Anomalies
→ Recommendations
→ Alerts

Roles:
- Super Admin
- Operations Manager
- Analyst
- Viewer

## Authentication
JWT-based authentication is used.

Access Token:
Short-lived token used to access protected APIs.

Refresh Token:
Longer-lived token used to obtain a new access token after expiration.

## Project Structure

backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ml/
│   └── main.py
├── alembic/
└── requirements.txt

frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── routes/
│   └── App.jsx
└── package.json

## Installation

### Backend

```cmd
cd backend
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
