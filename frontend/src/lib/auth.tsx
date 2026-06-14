"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "campusos_token";
const ROLE_KEY = "campusos_role";
const EMAIL_KEY = "campusos_email";

export interface AuthState {
  token: string | null;
  role: string;
  email: string | null;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  loginDev: (email: string, role: string) => Promise<void>;
  loginWithToken: (token: string) => Promise<void>;
  logout: () => void;
  startSsoLogin: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

async function fetchDevToken(email: string, role: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/auth/dev-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
  if (!res.ok) throw new Error("Dev login failed");
  const data = await res.json();
  return data.access_token;
}

async function fetchMe(token: string): Promise<{ email: string | null; role: string }> {
  const res = await fetch(`${API_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Session invalid");
  return res.json();
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState("student");
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const persistSession = useCallback((newToken: string, newRole: string, newEmail: string | null) => {
    setToken(newToken);
    setRole(newRole);
    setEmail(newEmail);
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(ROLE_KEY, newRole);
    if (newEmail) localStorage.setItem(EMAIL_KEY, newEmail);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setRole("student");
    setEmail(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(EMAIL_KEY);
  }, []);

  const loginWithToken = useCallback(
    async (newToken: string) => {
      const me = await fetchMe(newToken);
      persistSession(newToken, me.role, me.email);
    },
    [persistSession]
  );

  const loginDev = useCallback(
    async (devEmail: string, devRole: string) => {
      const newToken = await fetchDevToken(devEmail, devRole);
      await loginWithToken(newToken);
    },
    [loginWithToken]
  );

  const startSsoLogin = useCallback(() => {
    window.location.href = `${API_URL}/api/v1/auth/login`;
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setLoading(false);
      return;
    }
    loginWithToken(stored).catch(() => {
      logout();
    }).finally(() => setLoading(false));
  }, [loginWithToken, logout]);

  return (
    <AuthContext.Provider
      value={{ token, role, email, loading, loginDev, loginWithToken, logout, startSsoLogin }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}
