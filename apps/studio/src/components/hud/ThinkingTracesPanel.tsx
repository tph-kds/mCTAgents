"use client";

import { useEffect, useRef } from "react";

interface ThinkingStep {
  step_type: string;
  content: string;
  agent_id: string;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  duration_ms?: number;
  sequence: number;
}

const AGENT_COLORS: Record<string, string> = {
  problem_framer: "text-blue-400 border-blue-400",
  architect_agent: "text-cyan-400 border-cyan-400",
  evidence_agent: "text-green-400 border-green-400",
  critic_agent: "text-orange-400 border-orange-400",
  judge_agent: "text-purple-400 border-purple-400",
  synthesizer_agent: "text-emerald-400 border-emerald-400",
};

const STEP_TYPE_LABELS: Record<string, string> = {
  reasoning: "THINKING",
  tool_call: "ACTION",
  tool_result: "RESULT",
  observation: "OBSERVE",
};

function formatAgentName(agentId: string): string {
  return agentId.replace("_agent", "").replace("_", " ");
}

interface ThinkingTracesPanelProps {
  steps: ThinkingStep[];
}

export function ThinkingTracesPanel({ steps }: ThinkingTracesPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);

  return (
    <div className="glass-panel flex flex-col h-64">
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/5">
        <span className="text-[10px] uppercase tracking-widest text-white/50">
          Thinking Traces
        </span>
        <span className="text-[10px] text-white/30 bg-white/5 px-1.5 py-0.5 rounded">
          {steps.length}
        </span>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2">
        {steps.length === 0 ? (
          <div className="text-[10px] text-white/30 text-center py-4">
            Waiting for agent activity...
          </div>
        ) : (
          steps.map((step, i) => (
            <div
              key={i}
              className={`border-l-2 pl-2 py-1 ${AGENT_COLORS[step.agent_id] || "text-white/50 border-white/20"}`}
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[9px] font-mono uppercase opacity-60">
                  {formatAgentName(step.agent_id)}
                </span>
                <span className="text-[8px] px-1 py-0 rounded bg-white/5 text-white/40">
                  {STEP_TYPE_LABELS[step.step_type] || step.step_type}
                </span>
              </div>
              <p className="text-[10px] text-white/70 leading-relaxed line-clamp-3">
                {step.content}
              </p>
              {step.tool_name && (
                <span className="text-[8px] text-white/30 font-mono">
                  {step.tool_name}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
