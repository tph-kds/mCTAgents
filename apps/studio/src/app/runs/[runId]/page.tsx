"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { useSSE } from "@/hooks/useSSE";
import { getRun, getClaims, getEvidence } from "@/lib/api";
import { StatusBar, MiniTimeline } from "@/components/hud/StatusBar";
import { ControlsPanel } from "@/components/hud/ControlsPanel";
import { ClaimsSidebar } from "@/components/hud/ClaimsSidebar";
import { ThinkingTracesPanel } from "@/components/hud/ThinkingTracesPanel";
import { EvidenceBoard } from "@/components/studio/EvidenceBoard";
import { FinalAnswerPanel } from "@/components/studio/FinalAnswerPanel";
import type { Claim, Evidence, Objection, SSEEvent } from "@/lib/types";

const Workspace = dynamic(
  () => import("@/components/three/Workspace").then((mod) => ({ default: mod.Workspace })),
  { ssr: false, loading: () => <div className="w-full h-full bg-black rounded-xl animate-pulse" /> }
);

function computePhase(events: SSEEvent[]): string {
  const phaseEvents = events.filter(
    (e) => e.type === "agent_started" || e.type === "agent_completed" || e.type.startsWith("debate_") || e.type.startsWith("synthesis_")
  );
  if (phaseEvents.length === 0) return "queued";
  const last = phaseEvents[phaseEvents.length - 1];
  if (last.type === "synthesis_completed") return "completed";
  if (last.type === "synthesis_started") return "synthesis";
  if (last.type === "debate_round_completed") return "judging";
  if (last.type === "debate_round_started") return "criticism";
  if (last.agent_id === "critic_agent") return "criticism";
  if (last.agent_id === "judge_agent") return "judging";
  if (last.agent_id === "evidence_agent") return "evidence_attachment";
  if (last.agent_id === "architect_agent") return "claim_proposal";
  if (last.agent_id === "problem_framer") return "framing";
  return "queued";
}

function computeRound(events: SSEEvent[]): number {
  const debateStarts = events.filter((e) => e.type === "debate_round_started");
  return debateStarts.length;
}

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;
  const { events, connected, thinkingSteps } = useSSE(runId);
  const [run, setRun] = useState<Record<string, unknown> | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [objections, setObjections] = useState<any[]>([]);
  const [finalAnswer, setFinalAnswer] = useState<any>(null);

  useEffect(() => {
    if (!runId) return;
    getRun(runId).then(setRun).catch(console.error);
    getClaims(runId).then(setClaims).catch(console.error);
    getEvidence(runId).then(setEvidence).catch(console.error);
  }, [runId]);

  // Derive objections from events
  useEffect(() => {
    const objectionEvents = events.filter(e => e.type === "objection_raised");
    const parsed = objectionEvents.map(e => ({
      id: e.event_id,
      run_id: runId,
      target_claim_id: (e.payload?.target_claim_id as string) || "",
      author_agent_id: e.agent_id || "",
      reason: (e.payload?.reason as string) || "",
      severity: (e.payload?.severity as string) || "low",
      requested_fix: (e.payload?.requested_fix as string) || null,
    }));
    setObjections(parsed);
  }, [events, runId]);

  // Derive final answer from synthesis_completed event
  useEffect(() => {
    const synthesisEvent = events.find(e => e.type === "synthesis_completed");
    if (synthesisEvent?.payload) {
      setFinalAnswer({
        text: (synthesisEvent.payload.text as string) || "",
        confidence: (synthesisEvent.payload.confidence as number) || 0,
        risks: (synthesisEvent.payload.risks as any[]) || [],
        accepted_claim_ids: (synthesisEvent.payload.accepted_claim_ids as string[]) || [],
        next_steps: (synthesisEvent.payload.next_steps as string[]) || [],
      });
    }
  }, [events]);

  const phase = useMemo(() => computePhase(events), [events]);
  const round = useMemo(() => computeRound(events), [events]);

  if (!run) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="glass-panel p-8 text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-slate-400">Loading run...</p>
          <p className="text-xs text-slate-600 mt-1 font-mono">{runId}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Status bar at top */}
      <div className="px-3 pt-3">
        <StatusBar
          phase={phase}
          round={round}
          eventCount={events.length}
          connected={connected}
          runId={runId}
        />
      </div>

      {/* Main workspace: 3D canvas + sidebar */}
      <div className="flex-1 flex gap-3 p-3 min-h-0">
        {/* Left sidebar: controls + timeline */}
        <div className="w-64 shrink-0 flex flex-col gap-3 overflow-y-auto">
          <ControlsPanel runId={runId} phase={phase} connected={connected} />
          <MiniTimeline events={events} />
          <ThinkingTracesPanel steps={thinkingSteps} />
        </div>

        {/* Center: 3D workspace */}
        <div className="flex-1 min-w-0 relative scanlines rounded-xl overflow-hidden">
          <Workspace events={events} phase={phase} round={round} claims={claims} objections={objections} />

          {/* Corner HUD decorations */}
          <div className="absolute top-3 left-3 text-[9px] font-mono text-blue-500/40 pointer-events-none">
            MCTAGENTS v0.1.0
          </div>
          <div className="absolute bottom-3 right-3 text-[9px] font-mono text-slate-600 pointer-events-none">
            {events.length} events | {claims.length} claims
          </div>
        </div>

        {/* Right sidebar: claims */}
        <div className="w-72 shrink-0 overflow-y-auto">
          <ClaimsSidebar claims={claims} />
        </div>
      </div>

      {/* Bottom panels: Evidence + Final Answer */}
      <div className="px-3 pb-3 grid grid-cols-2 gap-3">
        <EvidenceBoard evidence={evidence} />
        <FinalAnswerPanel answer={finalAnswer} />
      </div>
    </div>
  );
}
