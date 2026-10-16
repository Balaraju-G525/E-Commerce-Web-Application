import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api.js";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        await api("/csrf/"); // sets the csrftoken cookie
        setUser((await api("/auth/me/")).user);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const authenticate = async (mode, email, password) => {
    const data = await api(`/auth/${mode}/`, { method: "POST", body: { email, password } });
    setUser(data.user);
  };

  const logout = async () => {
    await api("/auth/logout/", { method: "POST" });
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login: (e, p) => authenticate("login", e, p),
               register: (e, p) => authenticate("register", e, p), logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
