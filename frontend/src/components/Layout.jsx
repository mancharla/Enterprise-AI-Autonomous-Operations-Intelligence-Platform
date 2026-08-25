import {
    NavLink,
    useNavigate,
} from "react-router-dom";

import { logoutUser } from "../services/api";

export default function Layout({
    children,
}) {

    const navigate = useNavigate();

    function handleLogout() {

        logoutUser();

        navigate("/login", {
            replace: true,
        });
    }

    const menuItems = [

        {
            name: "Dashboard",
            path: "/dashboard",
            icon: "▣",
        },

        {
            name: "Devices",
            path: "/devices",
            icon: "▦",
        },

        {
            name: "Alerts",
            path: "/alerts",
            icon: "△",
        },

        {
            name: "Analytics",
            path: "/analytics",
            icon: "▥",
        },

        {
            name: "Forecasting",
            path: "/forecasting",
            icon: "◒",
        },

        {
            name: "Anomalies",
            path: "/anomalies",
            icon: "◇",
        },

        {
            name: "Root Cause",
            path: "/root-cause",
            icon: "⌁",
        },

        {
            name: "Optimization",
            path: "/optimization",
            icon: "⚙",
        },

        {
            name: "Recommendations",
            path: "/recommendations",
            icon: "★",
        },

        {
            name: "Autonomous Operations",
            path: "/autonomous",
            icon: "◆",
        },

        {
            name: "Real-Time Monitoring",
            path: "/real-time",
            icon: "●",
        },

    ];

    return (

        <div className="app-layout">

            <aside className="sidebar">

                <div className="brand">

                    <div className="brand-logo">
                        AI
                    </div>

                    <div>
                        <strong>
                            Enterprise AI
                        </strong>

                        <span>
                            Operations Intelligence
                        </span>
                    </div>

                </div>

                <nav className="sidebar-nav">

                    {menuItems.map((item) => (

                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                isActive
                                    ? "nav-item active"
                                    : "nav-item"
                            }
                        >

                            <span className="nav-icon">
                                {item.icon}
                            </span>

                            <span>
                                {item.name}
                            </span>

                        </NavLink>

                    ))}

                </nav>

                <div className="sidebar-bottom">

                    <NavLink
                        to="/settings"
                        className={({ isActive }) =>
                            isActive
                                ? "nav-item active"
                                : "nav-item"
                        }
                    >
                        <span className="nav-icon">
                            ⚙
                        </span>

                        Settings
                    </NavLink>

                    <button
                        className="logout-button"
                        onClick={handleLogout}
                    >
                        <span>
                            ↪
                        </span>

                        Logout
                    </button>

                </div>

            </aside>

            <div className="main-area">

                <header className="topbar">

                    <div>
                        <h2>
                            Enterprise AI Operations
                        </h2>

                        <span>
                            Autonomous Operations Intelligence Platform
                        </span>
                    </div>

                    <div className="user-section">

                        <div className="system-status">
                            <span></span>
                            System Operational
                        </div>

                        <div className="user-avatar">
                            OM
                        </div>

                        <div className="user-info">
                            <strong>
                                Operations Manager
                            </strong>

                            <span>
                                Organization Admin
                            </span>
                        </div>

                    </div>

                </header>

                <main className="content">
                    {children}
                </main>

            </div>

        </div>
    );
}