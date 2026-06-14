"use client";

import Link from "next/link";
import { AuthProvider, useAuth } from "@/lib/auth";

function NavBar() {
  const { token, email, role, logout, loading } = useAuth();

  return (
    <nav
      style={{
        borderBottom: "1px solid var(--border)",
        padding: "1rem 2rem",
        display: "flex",
        alignItems: "center",
        gap: "2rem",
        background: "var(--surface)",
      }}
    >
      <Link href="/" style={{ fontWeight: 700, fontSize: "1.1rem", color: "var(--text)" }}>
        CampusOS AI
      </Link>
      <Link href="/chat">Chat</Link>
      <Link href="/progress">Progress</Link>
      <Link href="/documents">Documents</Link>
      <Link href="/dashboard">Dashboard</Link>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "1rem" }}>
        {!loading && token ? (
          <>
            <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
              {email || role}
            </span>
            <button
              type="button"
              onClick={logout}
              style={{
                background: "transparent",
                border: "1px solid var(--border)",
                color: "var(--text)",
                padding: "0.35rem 0.75rem",
                borderRadius: 4,
                fontSize: "0.85rem",
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <Link href="/login">Sign in</Link>
        )}
      </div>
    </nav>
  );
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <NavBar />
      <main>{children}</main>
    </AuthProvider>
  );
}
