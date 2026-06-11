"use client";

import { useEffect, useState } from "react";
import { getDevToken, listDocuments } from "@/lib/api";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Array<Record<string, unknown>>>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const loadDocs = async () => {
    try {
      const token = await getDevToken("admin@campusos.edu", "admin");
      const data = await listDocuments(token);
      setDocs(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const token = await getDevToken("admin@campusos.edu", "admin");
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const form = new FormData();
      form.append("file", file);
      form.append("category", "policy");
      const res = await fetch(`${API_URL}/api/v1/documents/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      await loadDocs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Document Management</h1>
      <p style={{ color: "var(--muted)", marginBottom: "2rem" }}>
        Admin document upload and catalog (requires admin role).
      </p>

      <div style={{ marginBottom: "2rem" }}>
        <label
          style={{
            display: "inline-block",
            padding: "0.5rem 1rem",
            background: "var(--primary, #2563eb)",
            color: "#fff",
            borderRadius: 6,
            cursor: uploading ? "wait" : "pointer",
          }}
        >
          {uploading ? "Uploading..." : "Upload Document"}
          <input type="file" hidden onChange={handleUpload} accept=".txt,.md,.html,.pdf" />
        </label>
      </div>

      {error && <p style={{ color: "var(--error)", marginBottom: "1rem" }}>{error}</p>}

      <div style={{ display: "grid", gap: "1rem" }}>
        {docs.map((doc) => (
          <div
            key={String(doc.id)}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "1rem",
            }}
          >
            <strong>{doc.title as string}</strong>
            <div style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
              {doc.category as string}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
