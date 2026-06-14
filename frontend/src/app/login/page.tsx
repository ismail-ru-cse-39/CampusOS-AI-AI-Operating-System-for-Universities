"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth";

const ROLES = [
  { value: "student", label: "Student" },
  { value: "faculty", label: "Faculty" },
  { value: "admin", label: "Administrator" },
  { value: "admissions", label: "Admissions" },
  { value: "executive", label: "Executive" },
];

function LoginForm() {
  const { loginDev, loginWithToken, startSsoLogin, token } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [email, setEmail] = useState("demo.student@campusos.edu");
  const [role, setRole] = useState("student");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const ssoToken = searchParams.get("token");
    if (ssoToken) {
      setLoading(true);
      loginWithToken(ssoToken)
        .then(() => router.replace("/chat"))
        .catch(() => setError("SSO session invalid"))
        .finally(() => setLoading(false));
    }
  }, [searchParams, loginWithToken, router]);

  useEffect(() => {
    if (token) router.replace("/chat");
  }, [token, router]);

  async function handleDevLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await loginDev(email, role);
      router.push("/chat");
    } catch {
      setError("Dev login failed. Is the backend running in development mode?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "3rem auto", padding: "0 2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Sign in to CampusOS</h1>
      <p style={{ color: "var(--muted)", marginBottom: "2rem" }}>
        Use university SSO or a development token for local testing.
      </p>

      <button
        type="button"
        onClick={startSsoLogin}
        disabled={loading}
        style={{
          width: "100%",
          background: "var(--accent)",
          color: "white",
          border: "none",
          padding: "0.75rem",
          borderRadius: 6,
          fontWeight: 600,
          marginBottom: "1.5rem",
          opacity: loading ? 0.5 : 1,
        }}
      >
        Sign in with University SSO
      </button>

      <div
        style={{
          borderTop: "1px solid var(--border)",
          paddingTop: "1.5rem",
          marginBottom: "1rem",
        }}
      >
        <h2 style={{ fontSize: "1rem", marginBottom: "1rem" }}>Development login</h2>
        <form onSubmit={handleDevLogin}>
          <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: "100%",
              marginBottom: "0.75rem",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text)",
              padding: "0.6rem 0.75rem",
              borderRadius: 6,
            }}
          />
          <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
            Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              width: "100%",
              marginBottom: "1rem",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text)",
              padding: "0.6rem 0.75rem",
              borderRadius: 6,
            }}
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text)",
              padding: "0.75rem",
              borderRadius: 6,
              fontWeight: 600,
              opacity: loading ? 0.5 : 1,
            }}
          >
            {loading ? "Signing in..." : "Get dev token"}
          </button>
        </form>
      </div>

      {error && <p style={{ color: "#ef4444", fontSize: "0.9rem" }}>{error}</p>}

      <p style={{ marginTop: "1.5rem", fontSize: "0.85rem", color: "var(--muted)" }}>
        <Link href="/">Back to home</Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<p style={{ textAlign: "center", marginTop: "3rem" }}>Loading...</p>}>
      <LoginForm />
    </Suspense>
  );
}
