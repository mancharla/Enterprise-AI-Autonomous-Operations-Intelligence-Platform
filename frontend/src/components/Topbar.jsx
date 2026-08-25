function Topbar() {
    return (
        <header className="topbar">

            <div>
                <h1>
                    Enterprise AI Operations
                </h1>

                <p>
                    Autonomous Operations Intelligence Platform
                </p>
            </div>

            <div className="topbar-right">

                <div className="status-indicator">
                    <span></span>
                    System Operational
                </div>

                <div className="user-profile">
                    <div className="avatar">
                        OM
                    </div>

                    <div>
                        <strong>
                            Operations Manager
                        </strong>

                        <small>
                            Organization Admin
                        </small>
                    </div>
                </div>

            </div>

        </header>
    );
}

export default Topbar;