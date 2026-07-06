"use client";

import { useState, useEffect } from "react";
import type { Claim, Objection, SSEEvent } from "@/lib/types";

interface AgentInfo {
  id: string;
  name: string;
  description: string;
  role: string;
}

interface AgentPopoverProps {
  agent: AgentInfo;
  claims: Claim[];
  objections: Objection[];
  events: SSEEvent[];
  onClose: () => void;
}

type Tab = "claims" | "objections" | "activity";

const STATUS_STYLES: Record<string, { bg: string; text: string; dot: string }> = {
  proposed: { bg: "bg-gray-500/10", text: "text-gray-400", dot: "bg-gray-500" },
  evidence_requested: { bg: "bg-yellow-500/10", text: "text-yellow-400", dot: "bg-yellow-500" },
  supported: { bg: "bg-cyan-500/10", text: "text-cyan-400", dot: "bg-cyan-500" },
  challenged: { bg: "bg-orange-500/10", text: "text-orange-400", dot: "bg-orange-500" },
  revision_required: { bg: "bg-pink-500/10", text: "text-pink-400", dot: "bg-pink-500" },
  revised: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-500" },
  accepted: { bg: "bg-green-500/10", text: "text-green-400", dot: "bg-green-500" },
  rejected: { bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-500" },
  uncertain: { bg: "bg-yellow-500/10", text: "text-yellow-300", dot: "bg-yellow-300" },
};

const SEVERITY_STYLES: Record<string, { bg: string; text: string }> = {
  critical: { bg: "bg-red-500/10", text: "text-red-400" },
  high: { bg: "bg-orange-500/10", text: "text-orange-400" },
  medium: { bg: "bg-yellow-500/10", text: "text-yellow-400" },
  low: { bg: "bg-gray-500/10", text: "text-gray-400" },
};

export function AgentPopover({
  agent,
  claims,
  objections,
  events,
  onClose,
}: AgentPopoverProps) {
  const [activeTab, setActiveTab] = useState<Tab>("claims");

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  const agentClaims = claims.filter((c) => c.author_agent_id === agent.id);
  const agentObjections = objections.filter((o) => o.author_agent_id === agent.id);
  const agentEvents = events.filter((e) => e.agent_id === agent.id);

  const tabCounts: Record<Tab, number> = {
    claims: agentClaims.length,
    objections: agentObjections.length,
    activity: agentEvents.length,
  };

  return (
    <div className="absolute top-4 right-4 w-80 glass-panel z-50 animate-in fade-in">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div>
          <h3 className="text-sm font-medium text-white">{agent.name}</h3>
          <p className="text-[10px] text-white/50">{agent.description}</p>
        </div>
        <button
          onClick={onClose}
          className="text-white/30 hover:text-white/70 text-xs"
        >
          x
        </button>
      </div>

      <div className="flex border-b border-white/5">
        {(["claims", "objections", "activity"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-[10px] uppercase tracking-wider ${
              activeTab === tab
                ? "text-white border-b-2 border-cyan-400"
                : "text-white/30 hover:text-white/50"
            }`}
          >
            {tab} ({tabCounts[tab]})
          </button>
        ))}
      </div>

      <div className="max-h-64 overflow-y-auto p-3">
        {activeTab === "claims" && (
          <div className="space-y-2">
            {agentClaims.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">
                No claims yet
              </p>
            ) : (
              agentClaims.map((claim) => {
                const style = STATUS_STYLES[claim.status] || STATUS_STYLES.proposed;
                return (
                  <div
                    key={claim.id}
                    className={`p-2 rounded-lg ${style.bg} border border-white/5`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                      <span className={`text-[10px] font-medium ${style.text}`}>
                        {claim.status.replace(/_/g, " ")}
                      </span>
                      <span className="text-[9px] text-slate-500 ml-auto font-mono">
                        {(claim.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                      {claim.text}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        )}

        {activeTab === "objections" && (
          <div className="space-y-2">
            {agentObjections.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">
                No objections raised
              </p>
            ) : (
              agentObjections.map((obj) => {
                const style = SEVERITY_STYLES[obj.severity] || SEVERITY_STYLES.low;
                return (
                  <div
                    key={obj.id}
                    className={`p-2 rounded-lg ${style.bg} border border-white/5`}
                  >
                    <span className={`text-[10px] font-medium ${style.text}`}>
                      {obj.severity}
                    </span>
                    <p className="text-[11px] text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                      {obj.reason}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        )}

        {activeTab === "activity" && (
          <div className="space-y-1">
            {agentEvents.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">
                No activity yet
              </p>
            ) : (
              agentEvents.map((event) => (
                <div
                  key={event.event_id}
                  className="flex items-center gap-2 py-1"
                >
                  <span className="text-[10px] text-slate-400 font-mono">
                    {event.type.replace(/_/g, " ")}
                  </span>
                  <span className="text-[9px] text-slate-600 ml-auto">
                    {new Date(event.created_at).toLocaleTimeString()}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
