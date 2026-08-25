import {
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Devices from "../pages/Devices";
import DeviceDetails from "../pages/DeviceDetails";
import Alerts from "../pages/Alerts";
import Analytics from "../pages/Analytics";
import Forecasting from "../pages/Forecasting";
import Anomalies from "../pages/Anomalies";
import RootCause from "../pages/RootCause";
import Optimization from "../pages/Optimization";
import Recommendations from "../pages/Recommendations";
import AutonomousOperations from "../pages/AutonomousOperations";
import RealTimeMonitoring from "../pages/RealTimeMonitoring";
import Settings from "../pages/Settings";

import Layout from "../components/layout/Layout";

function ProtectedRoutes() {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <Layout>
            <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/devices" element={<Devices />} />
                <Route
                    path="/devices/:deviceId"
                    element={<DeviceDetails />}
                />

                <Route path="/alerts" element={<Alerts />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/forecasting" element={<Forecasting />} />
                <Route path="/anomalies" element={<Anomalies />} />
                <Route path="/root-cause" element={<RootCause />} />
                <Route path="/optimization" element={<Optimization />} />
                <Route
                    path="/recommendations"
                    element={<Recommendations />}
                />

                <Route
                    path="/autonomous"
                    element={<AutonomousOperations />}
                />

                <Route
                    path="/real-time"
                    element={<RealTimeMonitoring />}
                />

                <Route path="/settings" element={<Settings />} />

                <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                />
            </Routes>
        </Layout>
    );
}

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />

            <Route
                path="/*"
                element={<ProtectedRoutes />}
            />
        </Routes>
    );
}