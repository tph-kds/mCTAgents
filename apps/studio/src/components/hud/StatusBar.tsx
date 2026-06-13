"use client";

import type { SSEEvent } from "@/lib/types";

const PHASE_COLORS: Record<string, string> = {
  queued: "text-gray-500",
  framing: "text-blue-400",
  society_planning: "text-purple-400",
  claim_proposal: "text-cyan-400",
  evidence_attachment: "text-yellow-400",
  criticism: "text-orange-400",
  revision: "text-pink-400",
  judging: "text-emerald-400",
  escalation: "text-red-400",
  synthesis: "text-violet-400",
  completed: "text-green-400",
  failed: "text-red-400",
  cancelled: "text-gray-400",
};

interface StatusBarProps {
  phase: string;
  round: number;
  eventCount: number;
  connected: boolean;
  runId: string;
}

export function StatusBar({ phase, round, eventCount, connected, runId }: StatusBarProps) {
  const phaseColor = PHASE_COLORS[phase] || "text-gray-400";
  const shortId = runId.slice(0, 8);

  return (
    <div className="glass-panel px-3 py-2 flex items-center justify-between text-xs font-mono">
      {/* Left: run info */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-slate-500">{connected ? "LIVE" : "OFFLINE"}</span>
        </div>
        <span className="text-slate-600">|</span>
        <span className="text-slate-500">ID:{shortId}</span>
      </div>

      {/* Center: phase */}
      <div className="flex items-center gap-2">
        <span className={`${phaseColor} font-semibold`}>
          {phase.replace(/_/g, " ").toUpperCase()}
        </span>
        {round > 0 && (
          <>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">R{round}</span>
          </>
        )}
      </div>

      {/* Right: stats */}
      <div className="flex items-center gap-3">
        <span className="text-slate-500">{eventCount} events</span>
      </div>
    </div>
  );
}

interface MiniTimelineProps {
  events: SSEEvent[];
  maxVisible?: number;
}

export function MiniTimeline({ events, maxVisible = 8 }: MiniTimelineProps) {
  const visible = events.slice(-maxVisible);

  if (visible.length === 0) {
    return (
      <div className="glass-panel p-3">
        <div className="text-[10px] font-mono text-slate-500 mb-2 uppercase tracking-wider">Event Stream</div>
        <div className="text-xs text-slate-600 italic">Waiting for events...</div>
      </div>
    );
  }

  return (
    <div className="glass-panel p-3">
      <div className="text-[10px] font-mono text-slate-500 mb-2 uppercase tracking-wider">Event Stream</div>
      <div className="space-y-1.5">
        {visible.map((event, i) => {
          const time = event.created_at
            ? new Date(event.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
            : "";
          const typeLabel = event.type.replace(/_/g, " ");
          const agentLabel = event.agent_id || "";
          return (
            <div key={event.event_id || i} className="flex items-center gap-2 text-[11px]">
              <span className="text-slate-600 font-mono shrink-0">{time}</span>
              <span className="text-slate-300 truncate">{typeLabel}</span>
              {agentLabel && (
                <span className="text-[9px] px-1 py-0.5 rounded bg-white/5 text-slate-400 shrink-0">
                  {agentLabel}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
