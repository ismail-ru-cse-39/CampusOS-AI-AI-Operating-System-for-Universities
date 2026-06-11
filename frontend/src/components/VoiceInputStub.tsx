"use client";

import { useState } from "react";

/** Voice UI stub (T-049) — wire Web Speech API or cloud STT when credentials available. */
export function VoiceInputStub({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [listening, setListening] = useState(false);

  const toggle = () => {
    if (listening) {
      setListening(false);
      return;
    }
    setListening(true);
    // Stub: simulate voice capture after 1s
    setTimeout(() => {
      setListening(false);
      onTranscript("[Voice stub] How many credits do I have left?");
    }, 1000);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={listening ? "Stop listening" : "Start voice input"}
      style={{
        padding: "0.5rem 1rem",
        borderRadius: 6,
        border: "1px solid var(--border)",
        background: listening ? "var(--primary, #2563eb)" : "var(--surface)",
        color: listening ? "#fff" : "var(--text)",
        cursor: "pointer",
      }}
    >
      {listening ? "Listening..." : "Voice (stub)"}
    </button>
  );
}
