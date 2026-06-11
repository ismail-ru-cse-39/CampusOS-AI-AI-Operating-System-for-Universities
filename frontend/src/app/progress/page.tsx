"use client";

import { useEffect, useState } from "react";
import { getDevToken, getStudentProgress, StudentProgress } from "@/lib/api";

export default function ProgressPage() {
  const [data, setData] = useState<StudentProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const token = await getDevToken();
        const progress = await getStudentProgress(token);
        setData(progress);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load progress");
      }
    })();
  }, []);

  if (error) {
    return (
      <div style={{ maxWidth: 800, margin: "2rem auto", padding: "0 2rem" }}>
        <p style={{ color: "var(--error)" }}>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ maxWidth: 800, margin: "2rem auto", padding: "0 2rem" }}>
        <p style={{ color: "var(--muted)" }}>Loading student progress...</p>
      </div>
    );
  }

  const profile = data.profile as Record<string, string | number | string[]>;

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Student Progress</h1>
      <p style={{ color: "var(--muted)", marginBottom: "2rem" }}>
        {profile.full_name as string} — {profile.program as string}
      </p>

      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <div style={{ marginBottom: "0.75rem" }}>
          <strong>{data.progress_percent}%</strong> degree complete
        </div>
        <div
          style={{
            height: 12,
            background: "var(--border)",
            borderRadius: 6,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${data.progress_percent}%`,
              height: "100%",
              background: "var(--primary, #2563eb)",
            }}
          />
        </div>
        <p style={{ marginTop: "0.75rem", color: "var(--muted)", fontSize: "0.9rem" }}>
          {profile.credits_earned as number} / {profile.credits_required as number} credits
        </p>
      </div>

      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <h2 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Graduation Status</h2>
        <p>{(data.graduation as Record<string, string>).summary}</p>
      </div>

      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "1.5rem",
        }}
      >
        <h2 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Current Courses</h2>
        <ul>
          {((profile.current_courses as string[]) || []).map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
