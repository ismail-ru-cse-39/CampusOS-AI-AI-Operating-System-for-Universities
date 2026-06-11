import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "CampusOS AI",
  description: "The AI Operating System for Higher Education",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
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
          <Link href="/dashboard">Dashboard</Link>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
