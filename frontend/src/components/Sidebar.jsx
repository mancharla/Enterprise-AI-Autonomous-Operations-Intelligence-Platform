import { NavLink, useNavigate } from "react-router-dom";

const menu = [
    ["Dashboard", "/dashboard"],
    ["Devices", "/devices"],
    ["Alerts", "/alerts"],
    ["Analytics", "/analytics"],
    ["Forecasting", "/forecasting"],
    ["Anomalies", "/anomalies"],
    ["Root Cause", "/root-cause"],
    ["Optimization", "/optimization"],
    ["Recommendations", "/recommendations"],
    ["Autonomous Operations", "/autonomous-operations"],
    ["Real-Time Monitoring", "/real-time-monitoring"],
];

export default function Sidebar() {

    const navigate = useNavigate();

    const logout = () => {

        localStorage.removeItem("access_token");

        navigate("/login");
    };

    return (
        <aside className="w-60 bg-slate-950 text-white min-h-screen flex flex-col">

            <div className="p-6 border-b border-slate-800">

                <div className="flex items-center gap-3">

                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center font-bold">
                        AI
                    </div>

                    <div>
                        <h2 className="font-bold">
                            Enterprise AI
                        </h2>

                        <p className="text-xs text-slate-400">
                            Operations Intelligence
                        </p>
                    </div>

                </div>

            </div>

            <nav className="p-3 flex-1">

                {menu.map(([label, path]) => (

                    <NavLink
                        key={path}
                        to={path}
                        className={({ isActive }) =>
                            `block px-4 py-3 rounded-lg mb-1 text-sm ${isActive
                                ? "bg-blue-600 text-white"
                                : "text-slate-300 hover:bg-slate-800"
                            }`
                        }
                    >
                        {label}
                    </NavLink>

                ))}

            </nav>

            <div className="p-3 border-t border-slate-800">

                <NavLink
                    to="/settings"
                    className="block px-4 py-3 text-sm text-slate-300 hover:bg-slate-800 rounded-lg"
                >
                    Settings
                </NavLink>

                <button
                    onClick={logout}
                    className="w-full text-left px-4 py-3 text-sm text-red-400 hover:bg-slate-800 rounded-lg"
                >
                    Logout
                </button>

            </div>

        </aside>
    );
}