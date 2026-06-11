import Link from "next/link";

export default function HomePage() {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "4rem 2rem" }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>
        CampusOS AI
      </h1>
      <p style={{ fontSize: "1.25rem", color: "var(--muted)", marginBottom: "2rem" }}>
        The AI Operating System for Higher Education — not a chatbot, but a coordinated
        multi-agent platform for students, faculty, and administrators.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "1rem",
          marginBottom: "3rem",
        }}
      >
        {[
          { title: "Students", q: "What do I need and what should I do next?" },
          { title: "Faculty", q: "How can I better support my students?" },
          { title: "Administrators", q: "What actions should we take to improve outcomes?" },
        ].map((item) => (
          <div
            key={item.title}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "1.5rem",
            }}
          >
            <h3 style={{ marginBottom: "0.5rem" }}>{item.title}</h3>
            <p style={{ color: "var(--muted)", fontSize: "0.95rem" }}>{item.q}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <Link
          href="/chat"
          style={{
            background: "var(--accent)",
            color: "white",
            padding: "0.75rem 1.5rem",
            borderRadius: 6,
            fontWeight: 600,
          }}
        >
          Open Chat
        </Link>
        <Link
          href="/dashboard"
          style={{
            border: "1px solid var(--border)",
            padding: "0.75rem 1.5rem",
            borderRadius: 6,
            color: "var(--text)",
          }}
        >
          Executive Dashboard
        </Link>
      </div>
    </div>
  );
}
