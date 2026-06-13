"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export interface ClaimParticleProps {
  id: string;
  position: [number, number, number];
  status: string;
  confidence: number;
}

export function ClaimParticle({ id, position, status, confidence }: ClaimParticleProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  const statusColors: Record<string, string> = {
    proposed: "#6b7280",
    supported: "#22c55e",
    challenged: "#f59e0b",
    accepted: "#10b981",
    rejected: "#ef4444",
    uncertain: "#eab308",
    revised: "#3b82f6",
  };

  const color = statusColors[status] || "#6b7280";

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;

    meshRef.current.rotation.y += 0.01;
    meshRef.current.rotation.x += 0.005;

    // Float based on confidence
    meshRef.current.position.y = position[1] + Math.sin(t * 0.8 + position[0]) * 0.05 * confidence;

    // Scale based on confidence
    const scale = 0.3 + confidence * 0.4;
    meshRef.current.scale.setScalar(scale);
  });

  return (
    <mesh ref={meshRef} position={position}>
      <octahedronGeometry args={[0.3]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.5}
        metalness={0.6}
        roughness={0.3}
        transparent
        opacity={0.8}
      />
    </mesh>
  );
}

export interface EvidenceParticleProps {
  position: [number, number, number];
  reliability: number;
}

export function EvidenceParticle({ position, reliability }: EvidenceParticleProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;
    meshRef.current.position.y = position[1] + Math.sin(t + position[0] * 2) * 0.03;
    meshRef.current.rotation.y += 0.02;
  });

  const color = reliability > 0.7 ? "#22c55e" : reliability > 0.4 ? "#eab308" : "#ef4444";

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.15, 0.15, 0.15]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.3}
        metalness={0.5}
        roughness={0.4}
        transparent
        opacity={0.7}
      />
    </mesh>
  );
}
