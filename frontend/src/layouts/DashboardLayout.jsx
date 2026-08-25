import { Outlet } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function DashboardLayout() {
    return (
        <div className="app-container">

            <Sidebar />

            <div className="main-container">

                <Topbar />

                <main className="page-content">
                    <Outlet />
                </main>

            </div>

        </div>
    );
}

export default DashboardLayout;