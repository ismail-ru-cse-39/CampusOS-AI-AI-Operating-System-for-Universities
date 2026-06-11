const METRICS = [
  { label: "Student Satisfaction", value: "4.2 / 5", trend: "+0.3" },
  { label: "Retention Rate", value: "87.4%", trend: "+1.2%" },
  { label: "Enrollment Forecast", value: "12,450", trend: "+3.1%" },
  { label: "At-Risk Students", value: "142", trend: "-8" },
  { label: "Support Tickets", value: "1,203", trend: "-15%" },
  { label: "Avg. Response Time", value: "2.4 min", trend: "-40%" },
];

export default function DashboardPage() {
  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Executive Dashboard</h1>
      <p style={{ color: "var(--muted)", marginBottom: "2rem" }}>
        Predictive intelligence and operational metrics (Phase 5 stub).
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        {METRICS.map((m) => (
          <div
            key={m.label}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "1.25rem",
            }}
          >
            <div style={{ color: "var(--muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
              {m.label}
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{m.value}</div>
            <div style={{ color: "var(--success)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
              {m.trend}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "1.5rem",
        }}
      >
        <h2 style={{ marginBottom: "1rem", fontSize: "1.1rem" }}>Weekly Executive Report</h2>
        <p style={{ color: "var(--muted)" }}>
          AI-generated strategic recommendations will appear here in Phase 5.
          Current focus areas: retention improvement in Engineering, registration
          bottleneck reduction, career placement acceleration.
        </p>
      </div>
    </div>
  );
}
