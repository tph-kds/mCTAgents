"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

export interface DebateArenaProps {
  phase: string;
  round: number;
}

export function DebateArena({ phase, round }: DebateArenaProps) {
  const floorRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;

    if (floorRef.current) {
      const mat = floorRef.current.material as THREE.MeshStandardMaterial;
      mat.emissiveIntensity = 0.05 + Math.sin(t * 0.5) * 0.02;
    }

    if (ringRef.current) {
      ringRef.current.rotation.z += 0.005;
      const scale = 1 + Math.sin(t * 0.3) * 0.05;
      ringRef.current.scale.setScalar(scale);
    }
  });

  const phaseColors: Record<string, string> = {
    queued: "#374151",
    framing: "#3b82f6",
    society_planning: "#8b5cf6",
    claim_proposal: "#06b6d4",
    evidence_attachment: "#eab308",
    criticism: "#f97316",
    revision: "#ec4899",
    judging: "#10b981",
    escalation: "#ef4444",
    synthesis: "#a855f7",
    completed: "#22c55e",
    failed: "#ef4444",
    cancelled: "#6b7280",
  };

  const currentColor = phaseColors[phase] || "#374151";

  return (
    <group>
      {/* Central platform */}
      <mesh ref={floorRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <circleGeometry args={[3, 64]} />
        <meshStandardMaterial
          color="#1a1a2e"
          emissive={currentColor}
          emissiveIntensity={0.05}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Outer ring */}
      <mesh ref={ringRef} position={[0, -0.49, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.8, 3.0, 64]} />
        <meshBasicMaterial
          color={currentColor}
          transparent
          opacity={0.5}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Grid lines */}
      <gridHelper
        args={[6, 20, "#1e293b", "#1e293b"]}
        position={[0, -0.5, 0]}
      />

      {/* Phase indicator ring on floor */}
      {phase !== "queued" && (
        <mesh position={[0, -0.48, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[1.5, 1.6, 32]} />
          <meshBasicMaterial
            color={currentColor}
            transparent
            opacity={0.3}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      )}

      {/* Center label */}
      <Text
        position={[0, 0.2, 0]}
        fontSize={0.2}
        color={currentColor}
        anchorX="center"
        anchorY="middle"
      >
        {phase.replace(/_/g, " ").toUpperCase()}
      </Text>

      {/* Round indicator */}
      {round > 0 && (
        <Text
          position={[0, -0.1, 0]}
          fontSize={0.12}
          color="#6b7280"
          anchorX="center"
          anchorY="middle"
        >
          {`ROUND ${round}`}
        </Text>
      )}

      {/* Ambient particles */}
      <ambientLight intensity={0.3} />
      <pointLight position={[0, 3, 0]} intensity={0.5} color={currentColor} />
      <pointLight position={[3, 1, 0]} intensity={0.2} color="#3b82f6" />
      <pointLight position={[-3, 1, 0]} intensity={0.2} color="#f97316" />
    </group>
  );
}
