"use client";
import type { SSEEvent } from "@/lib/types";

const EVENT_COLORS: Record<string, string> = {
  run_started: "bg-blue-500",
  run_completed: "bg-green-500",
  run_failed: "bg-red-500",
  run_cancelled: "bg-gray-500",
  agent_started: "bg-purple-500",
  agent_completed: "bg-purple-400",
  claim_created: "bg-cyan-500",
  claim_revised: "bg-cyan-400",
  claim_accepted: "bg-green-400",
  claim_rejected: "bg-red-400",
  evidence_attached: "bg-yellow-500",
  objection_raised: "bg-orange-500",
  debate_round_started: "bg-indigo-500",
  debate_round_completed: "bg-indigo-400",
  synthesis_started: "bg-pink-500",
  synthesis_completed: "bg-pink-400",
};

function EventPayload({ payload }: { payload: Record<string, unknown> }) {
  const entries = Object.entries(payload).filter(([k]) => k !== "run_id");
  if (entries.length === 0) return null;
  return (
    <div className="mt-1 text-xs text-gray-500">
      {entries.slice(0, 3).map(([k, v]) => (
        <span key={k} className="mr-3">
          {k}: <span className="text-gray-400">{typeof v === "string" ? v.slice(0, 60) : JSON.stringify(v).slice(0, 40)}</span>
        </span>
      ))}
      {entries.length > 3 && <span className="text-gray-600">+{entries.length - 3} more</span>}
    </div>
  );
}

export function DebateTimeline({ events }: { events: SSEEvent[] }) {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold mb-4">Debate Timeline</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {events.map((event, i) => {
          const color = EVENT_COLORS[event.type] || "bg-gray-500";
          const timeStr = event.created_at ? new Date(event.created_at).toLocaleTimeString() : "";
          return (
            <div key={event.event_id || i} className="flex gap-3 items-start">
              <div className={`w-2 h-2 mt-2 rounded-full ${color} shrink-0`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-300">{event.type.replace(/_/g, " ")}</span>
                  {event.agent_id && (
                    <span className="text-xs bg-gray-800 px-1.5 py-0.5 rounded text-gray-400">{event.agent_id}</span>
                  )}
                  {timeStr && <span className="text-xs text-gray-600">{timeStr}</span>}
                </div>
                <EventPayload payload={event.payload} />
              </div>
            </div>
          );
        })}
      </div>
      {events.length === 0 && <p className="text-gray-500 text-sm">Waiting for events...</p>}
    </div>
  );
}
