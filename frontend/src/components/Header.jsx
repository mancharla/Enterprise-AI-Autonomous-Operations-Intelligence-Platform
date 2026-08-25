export default function Header() {

    return (
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8">

            <div>
                <h1 className="font-bold text-xl text-slate-900">
                    Enterprise AI Operations
                </h1>

                <p className="text-xs text-slate-500">
                    Autonomous Operations Intelligence Platform
                </p>
            </div>

            <div className="flex items-center gap-4">

                <div className="flex items-center gap-2 text-sm text-green-600">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    System Operational
                </div>

                <div className="flex items-center gap-3">

                    <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                        OM
                    </div>

                    <div>
                        <p className="font-semibold text-sm">
                            Operations Manager
                        </p>

                        <p className="text-xs text-slate-500">
                            Organization Admin
                        </p>
                    </div>

                </div>

            </div>

        </header>
    );
}