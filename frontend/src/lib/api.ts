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

export interface StudentProgress {
  profile: Record<string, unknown>;
  graduation: Record<string, unknown>;
  roadmap: Record<string, unknown>;
  progress_percent: number;
}

export interface ExecutiveMetrics {
  metrics: Record<string, { value: number; unit: string; trend: string }>;
  department_performance: Array<{ department: string; retention: number; enrollment: number }>;
  retention_trends: Array<{ semester: string; rate: number }>;
}

export async function sendChatMessage(
  message: string,
  userRole: string = "student",
  token?: string
): Promise<ChatResponse> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers,
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

export async function getDevToken(
  email: string = "demo@campusos.edu",
  role: string = "student"
): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/auth/dev-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
  if (!res.ok) throw new Error("Failed to get dev token");
  const data = await res.json();
  return data.access_token;
}

export async function getStudentProgress(token: string): Promise<StudentProgress> {
  const res = await fetch(`${API_URL}/api/v1/students/progress`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Progress API error: ${res.status}`);
  return res.json();
}

export async function getExecutiveMetrics(token: string): Promise<ExecutiveMetrics> {
  const res = await fetch(`${API_URL}/api/v1/analytics/executive`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Analytics API error: ${res.status}`);
  return res.json();
}

export async function listDocuments(token: string): Promise<Array<Record<string, unknown>>> {
  const res = await fetch(`${API_URL}/api/v1/documents/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Documents API error: ${res.status}`);
  return res.json();
}
