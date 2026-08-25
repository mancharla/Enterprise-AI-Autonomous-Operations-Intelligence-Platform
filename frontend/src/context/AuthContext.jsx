import { createContext, useContext, useEffect, useState } from "react";
import { getMe, loginUser, logoutUser as clearSession } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user") || "null"); } catch { return null; }
  });
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("access_token")));

  const logout = () => { clearSession(); setUser(null); };

  useEffect(() => {
    const expired = () => logout();
    window.addEventListener("auth:expired", expired);
    if (localStorage.getItem("access_token")) {
      getMe().then((u) => { setUser(u); localStorage.setItem("user", JSON.stringify(u)); }).catch(() => logout()).finally(() => setLoading(false));
    } else setLoading(false);
    return () => window.removeEventListener("auth:expired", expired);
  }, []);

  const login = async (email, password) => {
    const tokenData = await loginUser(email, password);
    localStorage.setItem("access_token", tokenData.access_token);
    const me = await getMe();
    localStorage.setItem("user", JSON.stringify(me));
    setUser(me);
    return me;
  };

  return <AuthContext.Provider value={{ user, isAuthenticated: Boolean(user && localStorage.getItem("access_token")), loading, login, logout }}>{children}</AuthContext.Provider>;
}
export function useAuth() { return useContext(AuthContext); }
