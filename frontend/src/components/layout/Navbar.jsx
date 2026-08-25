import { Bell, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
export default function Navbar() {
  const { user, logout } = useAuth();
  return <header className="navbar">
    <div><h1>Operations Intelligence</h1><p>Enterprise AI Autonomous Operations Platform</p></div>
    <div className="navbar-actions"><div className="user-info"><div className="avatar">{(user?.full_name || "U").slice(0,2).toUpperCase()}</div><div><strong>{user?.full_name || "User"}</strong><span>{user?.role?.replaceAll("_", " ") || "User"}</span></div></div><button className="icon-button" title="Notifications"><Bell size={19}/></button><button className="logout-button" onClick={logout} title="Logout"><LogOut size={18}/></button></div>
  </header>;
}
