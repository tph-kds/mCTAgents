"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Text, Billboard } from "@react-three/drei";
import * as THREE from "three";

export interface AgentProps {
  id: string;
  name: string;
  role: string;
  color: string;
  position: [number, number, number];
  isActive: boolean;
  isSpeaking: boolean;
}

const ROLE_SHAPES: Record<string, "octahedron" | "dodecahedron" | "icosahedron" | "torus" | "cone" | "cylinder"> = {
  ProblemFramer: "cone",
  Architect: "octahedron",
  Evidence: "cylinder",
  Critic: "torus",
  Judge: "dodecahedron",
  Synthesizer: "icosahedron",
};

export function AgentAvatar({ id, name, role, color, position, isActive, isSpeaking }: AgentProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  const shape = ROLE_SHAPES[role] || "octahedron";
  const baseColor = new THREE.Color(color);
  const activeColor = new THREE.Color(color).multiplyScalar(1.3);

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;

    // Gentle floating
    meshRef.current.position.y = position[1] + Math.sin(t * 0.5 + position[0]) * 0.1;

    // Rotation when active
    if (isActive) {
      meshRef.current.rotation.y += 0.02;
      meshRef.current.rotation.x += 0.005;
    }

    // Glow pulse when speaking
    if (glowRef.current) {
      const scale = isSpeaking ? 1.4 + Math.sin(t * 3) * 0.2 : 1.2;
      glowRef.current.scale.setScalar(scale);
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = isSpeaking ? 0.3 + Math.sin(t * 4) * 0.1 : 0.08;
    }

    // Orbit ring when active
    if (ringRef.current) {
      ringRef.current.rotation.z += 0.03;
      ringRef.current.rotation.x = Math.PI / 2;
      (ringRef.current.material as THREE.MeshBasicMaterial).opacity = isActive ? 0.6 : 0.1;
    }
  });

  const geometry = useMemo(() => {
    switch (shape) {
      case "cone": return <coneGeometry args={[0.5, 0.8, 6]} />;
      case "octahedron": return <octahedronGeometry args={[0.5]} />;
      case "dodecahedron": return <dodecahedronGeometry args={[0.5]} />;
      case "icosahedron": return <icosahedronGeometry args={[0.5]} />;
      case "torus": return <torusGeometry args={[0.4, 0.15, 8, 16]} />;
      case "cylinder": return <cylinderGeometry args={[0.3, 0.3, 0.7, 8]} />;
      default: return <octahedronGeometry args={[0.5]} />;
    }
  }, [shape]);

  return (
    <group position={position}>
      {/* Glow sphere */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[0.7, 16, 16]} />
        <meshBasicMaterial color={activeColor} transparent opacity={0.08} />
      </mesh>

      {/* Orbit ring */}
      <mesh ref={ringRef}>
        <torusGeometry args={[0.8, 0.02, 8, 32]} />
        <meshBasicMaterial color={baseColor} transparent opacity={0.1} />
      </mesh>

      {/* Main agent shape */}
      <mesh ref={meshRef}>
        {geometry}
        <meshStandardMaterial
          color={isActive ? activeColor : baseColor}
          emissive={isActive ? baseColor : new THREE.Color(0x000000)}
          emissiveIntensity={isSpeaking ? 0.8 : isActive ? 0.4 : 0.1}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Name label */}
      <Billboard position={[0, 1.0, 0]}>
        <Text
          fontSize={0.15}
          color={isActive ? "#ffffff" : "#888888"}
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.01}
          outlineColor="#000000"
        >
          {name}
        </Text>
      </Billboard>

      {/* Role badge */}
      <Billboard position={[0, 0.8, 0]}>
        <Text
          fontSize={0.09}
          color={color}
          anchorX="center"
          anchorY="middle"
        >
          {role}
        </Text>
      </Billboard>

      {/* Active indicator */}
      {isActive && (
        <pointLight color={color} intensity={2} distance={3} />
      )}
    </group>
  );
}
