"use client";
import { useEffect, useRef, useCallback, useState } from "react";
import type { SSEEvent, ThinkingStep } from "@/lib/types";

const SSE_EVENT_TYPES = [
  "run_started", "run_completed", "run_failed", "run_cancelled",
  "agent_started", "agent_completed",
  "claim_created", "claim_revised", "claim_accepted", "claim_rejected",
  "evidence_attached", "objection_raised",
  "debate_round_started", "debate_round_completed",
  "synthesis_started", "synthesis_completed",
] as const;

export function useSSE(runId: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([]);
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!runId) return;
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
    const es = new EventSource(`${API_URL}/v1/runs/${runId}/events`);
    esRef.current = es;
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    const handler = (e: MessageEvent) => {
      try {
        const parsed = JSON.parse(e.data);
        setEvents((prev) => [...prev, parsed as SSEEvent]);
        if (parsed.type === "agent_started" || parsed.type === "tool_called" || parsed.type === "tool_result") {
          const payload = parsed.payload as Record<string, unknown>;
          if (payload.thinking_steps && Array.isArray(payload.thinking_steps)) {
            setThinkingSteps(prev => [...prev, ...payload.thinking_steps as ThinkingStep[]]);
          }
        }
      } catch { /* ignore malformed */ }
    };

    for (const eventType of SSE_EVENT_TYPES) {
      es.addEventListener(eventType, handler);
    }
    es.addEventListener("message", handler);
  }, [runId]);

  useEffect(() => {
    connect();
    return () => { esRef.current?.close(); };
  }, [connect]);

  return { events, connected, thinkingSteps };
}