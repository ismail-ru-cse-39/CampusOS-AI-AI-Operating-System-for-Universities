"use client";

import { useState } from "react";
import { sendChatMessage, getDevToken, type ChatResponse } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { VoiceInputStub } from "./VoiceInputStub";

interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  citations?: ChatResponse["citations"];
}

const ROLES = [
  { value: "student", label: "Student" },
  { value: "faculty", label: "Faculty" },
  { value: "admin", label: "Administrator" },
  { value: "admissions", label: "Admissions" },
  { value: "executive", label: "Executive" },
];

export default function ChatInterface() {
  const { token, role, loginWithToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedRole, setSelectedRole] = useState(role);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ensureToken(): Promise<string | undefined> {
    if (token) return token;
    try {
      const newToken = await getDevToken("demo.student@campusos.edu", selectedRole);
      await loginWithToken(newToken);
      return newToken;
    } catch {
      return undefined;
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const authToken = token || (await ensureToken());
      const response = await sendChatMessage(userMessage, selectedRole, authToken ?? undefined);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.message,
          agent: response.agent,
          citations: response.citations,
        },
      ]);
    } catch {
      setError("Failed to reach CampusOS API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: "1rem" }}>
        <label style={{ fontSize: "0.85rem", color: "var(--muted)", marginRight: "0.5rem" }}>
          Role:
        </label>
        <select
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text)",
            padding: "0.4rem 0.75rem",
            borderRadius: 4,
          }}
        >
          {ROLES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          minHeight: 400,
          maxHeight: 500,
          overflowY: "auto",
          padding: "1rem",
          marginBottom: "1rem",
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: "var(--muted)", textAlign: "center", marginTop: "2rem" }}>
            Try: &quot;How many credits do I have left?&quot; or &quot;When is registration?&quot;
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: "1rem",
              textAlign: msg.role === "user" ? "right" : "left",
            }}
          >
            <div
              style={{
                display: "inline-block",
                maxWidth: "85%",
                background: msg.role === "user" ? "var(--accent)" : "var(--bg)",
                border: msg.role === "assistant" ? "1px solid var(--border)" : "none",
                padding: "0.75rem 1rem",
                borderRadius: 8,
                textAlign: "left",
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.role === "assistant" && msg.agent && (
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "0.25rem" }}>
                  {msg.agent.replace(/_/g, " ")} agent
                </div>
              )}
              {msg.content}
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: "var(--muted)" }}>
                  <strong>Sources:</strong>
                  {msg.citations.map((c, j) => (
                    <div key={j} style={{ marginTop: "0.25rem" }}>
                      {c.source_url ? (
                        <a href={c.source_url} target="_blank" rel="noopener noreferrer">
                          {c.document_title}
                        </a>
                      ) : (
                        c.document_title
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>Thinking...</p>
        )}
      </div>

      {error && (
        <p style={{ color: "#ef4444", marginBottom: "0.5rem", fontSize: "0.9rem" }}>{error}</p>
      )}

      <div style={{ marginBottom: "0.5rem" }}>
        <VoiceInputStub onTranscript={(text) => setInput(text)} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask CampusOS anything..."
          disabled={loading}
          style={{
            flex: 1,
            background: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text)",
            padding: "0.75rem 1rem",
            borderRadius: 6,
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            background: "var(--accent)",
            color: "white",
            border: "none",
            padding: "0.75rem 1.25rem",
            borderRadius: 6,
            fontWeight: 600,
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
