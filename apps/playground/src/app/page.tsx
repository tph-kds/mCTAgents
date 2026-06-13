"use client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface Event {
  event_id: string;
  type: string;
  agent_id?: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export default function PlaygroundPage() {
  const [problem, setProblem] = useState("");
  const [events, setEvents] = useState<Event[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function runReasoning() {
    if (!problem.trim()) return;
    setLoading(true);
    setEvents([]);
    setStatus("creating");

    try {
      const resp = await fetch(`${API_URL}/v1/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem: problem.trim() }),
      });
      const run = await resp.json();
      setStatus("streaming");

      const es = new EventSource(`${API_URL}/v1/runs/${run.run_id}/events`);
      const handler = (e: MessageEvent) => {
        try {
          const event = JSON.parse(e.data);
          setEvents((prev) => [...prev, event]);
          if (event.type === "run_completed" || event.type === "run_failed") {
            es.close();
            setStatus(event.type === "run_completed" ? "completed" : "failed");
            setLoading(false);
          }
        } catch {}
      };
      es.addEventListener("message", handler);
      es.onerror = () => {
        es.close();
        setStatus("disconnected");
        setLoading(false);
      };
    } catch {
      setStatus("error");
      setLoading(false);
    }
  }

  const lastEvent = events[events.length - 1];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Social Reasoning Playground</h1>
        <p className="text-gray-400">Watch agents debate and refine claims in real-time.</p>
      </div>

      <div className="flex gap-4">
        <input
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="Enter a problem to reason about..."
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          onKeyDown={(e) => e.key === "Enter" && runReasoning()}
        />
        <button
          onClick={runReasoning}
          disabled={loading || !problem.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? "Running..." : "Run"}
        </button>
      </div>

      {status && (
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${status === "completed" ? "bg-green-500" : status === "failed" ? "bg-red-500" : "bg-yellow-500 animate-pulse"}`} />
          <span className="text-gray-400">{status}</span>
          <span className="text-gray-600">| {events.length} events</span>
        </div>
      )}

      {lastEvent && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-xs text-gray-500 mb-1">Latest Event</div>
          <div className="text-sm font-medium">{lastEvent.type.replace(/_/g, " ")}</div>
          {lastEvent.agent_id && <div className="text-xs text-gray-400 mt-1">Agent: {lastEvent.agent_id}</div>}
        </div>
      )}

      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {events.map((event, i) => (
          <div key={event.event_id || i} className="flex gap-3 items-start text-sm">
            <span className="text-xs text-gray-600 w-16 shrink-0">
              {event.created_at ? new Date(event.created_at).toLocaleTimeString() : ""}
            </span>
            <span className={`w-2 h-2 mt-1.5 rounded-full shrink-0 ${
              event.type.includes("completed") ? "bg-green-500" :
              event.type.includes("failed") ? "bg-red-500" :
              event.type.includes("claim") ? "bg-cyan-500" :
              event.type.includes("evidence") ? "bg-yellow-500" :
              event.type.includes("objection") ? "bg-orange-500" :
              "bg-blue-500"
            }`} />
            <div>
              <span className="text-gray-300">{event.type.replace(/_/g, " ")}</span>
              {event.agent_id && <span className="text-gray-600 ml-2">({event.agent_id})</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
