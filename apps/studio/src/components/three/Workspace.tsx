"use client";

import { Suspense, useMemo, useCallback, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars, Environment } from "@react-three/drei";
import { AgentAvatar, AgentProps } from "./AgentAvatar";
import { AgentPopover } from "./AgentPopover";
import { DebateArena } from "./DebateArena";
import { ParticleBeam } from "./ParticleBeam";
import { ClaimParticle, EvidenceParticle } from "./Particles";
import type { SSEEvent } from "@/lib/types";

export interface AgentState {
  id: string;
  name: string;
  role: string;
  color: string;
  position: [number, number, number];
  isActive: boolean;
  isSpeaking: boolean;
}

const AGENT_CONFIG: (Omit<AgentProps, "isActive" | "isSpeaking" | "onClick"> & { description: string })[] = [
  { id: "framer", name: "ProblemFramer", role: "ProblemFramer", color: "#3b82f6", position: [0, 0.5, 2.5], description: "Frames the problem and defines scope" },
  { id: "architect", name: "Architect", role: "Architect", color: "#06b6d4", position: [2.2, 0.5, 1.2], description: "Designs system architecture and structure" },
  { id: "evidence", name: "EvidenceAgent", role: "Evidence", color: "#eab308", position: [2.2, 0.5, -1.2], description: "Gathers and evaluates supporting evidence" },
  { id: "critic", name: "Critic", role: "Critic", color: "#f97316", position: [0, 0.5, -2.5], description: "Challenges claims and finds weaknesses" },
  { id: "judge", name: "Judge", role: "Judge", color: "#10b981", position: [-2.2, 0.5, -1.2], description: "Evaluates and arbitrates between agents" },
  { id: "synthesizer", name: "Synthesizer", role: "Synthesizer", color: "#a855f7", position: [-2.2, 0.5, 1.2], description: "Synthesizes final conclusions" },
];

interface WorkspaceProps {
  events: SSEEvent[];
  phase: string;
  round: number;
}

export function Workspace({ events, phase, round }: WorkspaceProps) {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const agentStates = useMemo(() => {
    const states: AgentState[] = AGENT_CONFIG.map(a => ({
      ...a,
      isActive: false,
      isSpeaking: false,
    }));

    // Process events to determine agent states
    for (const event of events) {
      if (event.type === "agent_started" && event.agent_id) {
        const agent = states.find(a => a.id === event.agent_id || a.name === event.agent_id);
        if (agent) {
          agent.isActive = true;
          agent.isSpeaking = true;
        }
      }
      if (event.type === "agent_completed" && event.agent_id) {
        const agent = states.find(a => a.id === event.agent_id || a.name === event.agent_id);
        if (agent) {
          agent.isSpeaking = false;
        }
      }
    }

    return states;
  }, [events]);

  const activeAgent = agentStates.find(a => a.isSpeaking) || agentStates.find(a => a.isActive);

  // Generate beams between active agent and center
  const beams = useMemo(() => {
    if (!activeAgent) return [];
    return [{
      from: activeAgent.position,
      to: [0, 0.3, 0] as [number, number, number],
      color: activeAgent.color,
      type: "claim" as const,
      active: true,
    }];
  }, [activeAgent]);

  // Generate claim particles from events
  const claimParticles = useMemo(() => {
    return events
      .filter(e => e.type === "claim_created" || e.type === "claim_revised")
      .slice(-8)
      .map((e, i) => {
        const angle = (i / 8) * Math.PI * 2;
        const radius = 1.5 + Math.random() * 0.5;
        return {
          id: e.event_id,
          position: [Math.cos(angle) * radius, 0.3, Math.sin(angle) * radius] as [number, number, number],
          status: (e.payload?.status as string) || "proposed",
          confidence: (e.payload?.confidence as number) || 0.5,
        };
      });
  }, [events]);

  // Generate evidence particles
  const evidenceParticles = useMemo(() => {
    return events
      .filter(e => e.type === "evidence_attached")
      .slice(-6)
      .map((e, i) => {
        const angle = (i / 6) * Math.PI * 2 + 0.3;
        return {
          position: [Math.cos(angle) * 2.0, 0.2, Math.sin(angle) * 2.0] as [number, number, number],
          reliability: (e.payload?.reliability_score as number) || 0.5,
        };
      });
  }, [events]);

  return (
    <div className="w-full h-full rounded-xl overflow-hidden border border-gray-800 bg-black">
      <Canvas
        camera={{ position: [0, 3, 6], fov: 50 }}
        gl={{ antialias: true, alpha: false }}
        dpr={[1, 2]}
      >
        <color attach="background" args={["#0a0a1a"]} />

        <Suspense fallback={null}>
          {/* Starfield background */}
          <Stars radius={50} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />

          {/* Arena */}
          <DebateArena phase={phase} round={round} />

          {/* Agent avatars */}
          {agentStates.map((agent) => (
            <AgentAvatar key={agent.id} {...agent} onClick={setSelectedAgentId} />
          ))}

          {/* Particle beams */}
          {beams.map((beam, i) => (
            <ParticleBeam key={i} {...beam} />
          ))}

          {/* Claim particles */}
          {claimParticles.map((p) => (
            <ClaimParticle key={p.id} {...p} />
          ))}

          {/* Evidence particles */}
          {evidenceParticles.map((p, i) => (
            <EvidenceParticle key={i} {...p} />
          ))}

          {/* Environment lighting */}
          <Environment preset="night" />
        </Suspense>

        {/* Camera controls */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          minDistance={3}
          maxDistance={12}
          minPolarAngle={Math.PI / 6}
          maxPolarAngle={Math.PI / 2.2}
          autoRotate={!activeAgent}
          autoRotateSpeed={0.3}
        />
      </Canvas>

      {selectedAgentId && (() => {
        const agent = AGENT_CONFIG.find(a => a.id === selectedAgentId);
        if (!agent) return null;
        return (
          <AgentPopover
            agent={agent}
            claims={[]}
            objections={[]}
            events={events}
            onClose={() => setSelectedAgentId(null)}
          />
        );
      })()}
    </div>
  );
}
