from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import engine

# --------------------------------------------------
# API ROUTERS
# --------------------------------------------------

from app.api.auth import router as auth_router
from app.api.organizations import router as organizations_router
from app.api.facilities import router as facilities_router
from app.api.devices import router as devices_router
from app.api.datasets import router as datasets_router
from app.api.analytics import router as analytics_router
from app.api.forecasting import router as forecasting_router
from app.api.forecast_accuracy import (
    router as forecast_accuracy_router,
)
from app.api.anomalies import router as anomalies_router
from app.api.root_cause import router as root_cause_router
from app.api.optimization import router as optimization_router
from app.api.simulation import router as simulation_router
from app.api.recommendations import (
    router as recommendations_router,
)
from app.api.reports import router as reports_router
from app.api.websocket import router as websocket_router
from app.api.dashboard import router as dashboard_router
from app.api.streaming import router as streaming_router
from app.api.ml import router as ml_router
from app.api.alerts import router as alerts_router
from app.api.autonomous import router as autonomous_router


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Enterprise AI Autonomous Operations Intelligence Platform",
    version="1.0.0",
    description=(
        "Enterprise AI platform for autonomous operations, "
        "forecasting, anomaly detection, root-cause analysis, "
        "optimization, recommendations, alerts and real-time monitoring."
    ),
)


# --------------------------------------------------
# CORS
# --------------------------------------------------
# Allows the React frontend to communicate with FastAPI.
#
# React/Vite:
# http://localhost:5173
#
# FastAPI:
# http://127.0.0.1:8000
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# AUTHENTICATION & ORGANIZATION
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(organizations_router)


# --------------------------------------------------
# FACILITIES & DEVICES
# --------------------------------------------------

app.include_router(facilities_router)
app.include_router(devices_router)


# --------------------------------------------------
# DATA & ANALYTICS
# --------------------------------------------------

app.include_router(datasets_router)
app.include_router(analytics_router)


# --------------------------------------------------
# AI FORECASTING
# --------------------------------------------------

app.include_router(forecasting_router)
app.include_router(forecast_accuracy_router)


# --------------------------------------------------
# AI INTELLIGENCE
# --------------------------------------------------

app.include_router(anomalies_router)
app.include_router(root_cause_router)


# --------------------------------------------------
# OPTIMIZATION & SIMULATION
# --------------------------------------------------

app.include_router(optimization_router)
app.include_router(simulation_router)


# --------------------------------------------------
# RECOMMENDATIONS & REPORTS
# --------------------------------------------------

app.include_router(recommendations_router)
app.include_router(reports_router)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

app.include_router(dashboard_router)


# --------------------------------------------------
# MACHINE LEARNING
# --------------------------------------------------

app.include_router(ml_router)


# --------------------------------------------------
# OPERATIONAL ALERTS
# --------------------------------------------------

app.include_router(alerts_router)


# --------------------------------------------------
# AUTONOMOUS OPERATIONS
# --------------------------------------------------

app.include_router(autonomous_router)


# --------------------------------------------------
# REAL-TIME STREAMING
# --------------------------------------------------

app.include_router(streaming_router)


# --------------------------------------------------
# WEBSOCKET
# --------------------------------------------------

app.include_router(websocket_router)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Enterprise AI Operations Platform is running",
        "version": "1.0.0",
        "status": "online",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }