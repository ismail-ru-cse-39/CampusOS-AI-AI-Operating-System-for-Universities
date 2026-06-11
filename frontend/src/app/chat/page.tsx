import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>CampusOS Chat</h1>
      <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>
        Ask anything about academics, policies, career, or campus services.
      </p>
      <ChatInterface />
    </div>
  );
}
