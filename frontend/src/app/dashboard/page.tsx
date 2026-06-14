"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ExecutiveMetrics, getExecutiveMetrics } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function DashboardPage() {
  const { token, loading: authLoading, loginDev } = useAuth();
  const [data, setData] = useState<ExecutiveMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    (async () => {
      try {
        let authToken = token;
        if (!authToken) {
          await loginDev("exec@campusos.edu", "executive");
          return;
        }
        const metrics = await getExecutiveMetrics(authToken);
        setData(metrics);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load dashboard");
      }
    })();
  }, [token, authLoading, loginDev]);

  if (error) {
    return (
      <div style={{ maxWidth: 1100, margin: "2rem auto", padding: "0 2rem" }}>
        <p style={{ color: "var(--muted)" }}>{error} — <Link href="/login">Sign in as executive</Link></p>
      </div>
    );
  }

  const metrics = data?.metrics ?? {
    student_satisfaction: { value: 4.2, unit: "/ 5", trend: "+0.3" },
    retention_rate: { value: 87.4, unit: "%", trend: "+1.2%" },
    enrollment_forecast: { value: 12450, unit: "students", trend: "+3.1%" },
    at_risk_students: { value: 2, unit: "students", trend: "-8" },
    support_tickets: { value: 1203, unit: "tickets", trend: "-15%" },
    avg_response_time: { value: 2.4, unit: "min", trend: "-40%" },
  };

  const labels: Record<string, string> = {
    student_satisfaction: "Student Satisfaction",
    retention_rate: "Retention Rate",
    enrollment_forecast: "Enrollment Forecast",
    at_risk_students: "At-Risk Students",
    support_tickets: "Support Tickets",
    avg_response_time: "Avg. Response Time",
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Executive Dashboard</h1>
      <p style={{ color: "var(--muted)", marginBottom: "2rem" }}>
        Live metrics from analytics service (executive role required).
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        {Object.entries(metrics).map(([key, m]) => (
          <div
            key={key}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "1.25rem",
            }}
          >
            <div style={{ color: "var(--muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
              {labels[key] || key}
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>
              {typeof m.value === "number" && m.value > 1000
                ? m.value.toLocaleString()
                : m.value}
              {m.unit !== "students" && m.unit !== "tickets" ? ` ${m.unit}` : ""}
            </div>
            <div style={{ color: "var(--success)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
              {m.trend}
            </div>
          </div>
        ))}
      </div>

      {data?.department_performance && (
        <div
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            padding: "1.5rem",
            marginBottom: "2rem",
          }}
        >
          <h2 style={{ marginBottom: "1rem", fontSize: "1.1rem" }}>Department Performance</h2>
          {data.department_performance.map((d) => (
            <div key={d.department} style={{ marginBottom: "0.5rem" }}>
              {d.department}: {d.retention}% retention, {d.enrollment.toLocaleString()} enrolled
            </div>
          ))}
        </div>
      )}

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
          Fetch full report at <code>/api/v1/analytics/weekly-report</code>. Focus areas:
          retention improvement in Engineering, registration bottleneck reduction, career placement.
        </p>
      </div>
    </div>
  );
}
