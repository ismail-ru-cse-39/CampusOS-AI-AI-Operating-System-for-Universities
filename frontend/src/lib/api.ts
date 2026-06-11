const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Citation {
  document_title: string;
  source_url: string | null;
  excerpt: string;
}

export interface ChatResponse {
  agent: string;
  message: string;
  citations: Citation[];
  metadata: Record<string, unknown>;
}

export async function sendChatMessage(
  message: string,
  userRole: string = "student"
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, user_role: userRole }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function checkHealth(): Promise<{ status: string; agents_registered: number }> {
  const res = await fetch(`${API_URL}/api/v1/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
