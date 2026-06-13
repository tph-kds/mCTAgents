"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export interface ParticleBeamProps {
  from: [number, number, number];
  to: [number, number, number];
  color: string;
  type: "claim" | "evidence" | "objection" | "revision";
  active: boolean;
}

export function ParticleBeam({ from, to, color, type, active }: ParticleBeamProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const lineRef = useRef<THREE.Line>(null);

  const particleCount = 20;
  const curve = useMemo(() => {
    const midX = (from[0] + to[0]) / 2;
    const midY = (from[1] + to[1]) / 2 + 0.5;
    const midZ = (from[2] + to[2]) / 2;
    return new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(...from),
      new THREE.Vector3(midX, midY, midZ),
      new THREE.Vector3(...to),
    );
  }, [from, to]);

  const positions = useMemo(() => {
    const arr = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const t = i / particleCount;
      const point = curve.getPoint(t);
      arr[i * 3] = point.x;
      arr[i * 3 + 1] = point.y;
      arr[i * 3 + 2] = point.z;
    }
    return arr;
  }, [curve]);

  useFrame((state) => {
    if (!pointsRef.current || !active) return;
    const t = state.clock.elapsedTime;
    const posAttr = pointsRef.current.geometry.attributes.position as THREE.BufferAttribute;

    for (let i = 0; i < particleCount; i++) {
      const progress = ((t * 0.3 + i / particleCount) % 1);
      const point = curve.getPoint(progress);
      posAttr.setXYZ(i, point.x, point.y + Math.sin(t * 2 + i) * 0.05, point.z);
    }
    posAttr.needsUpdate = true;
  });

  const size = type === "claim" ? 0.06 : type === "evidence" ? 0.04 : type === "objection" ? 0.05 : 0.03;
  const colorObj = new THREE.Color(color);

  return (
    <group>
      {/* Particle trail */}
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={positions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={size}
          color={colorObj}
          transparent
          opacity={active ? 0.8 : 0.2}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>

      {/* Thin guide line */}
      <line ref={lineRef as any}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={curve.getPoints(20).length}
            array={new Float32Array(curve.getPoints(20).flatMap(p => [p.x, p.y, p.z]))}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={colorObj}
          transparent
          opacity={active ? 0.3 : 0.05}
          blending={THREE.AdditiveBlending}
        />
      </line>
    </group>
  );
}
