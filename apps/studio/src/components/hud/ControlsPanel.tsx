"use client";

import { cancelRun } from "@/lib/api";

interface ControlsPanelProps {
  runId: string;
  phase: string;
  connected: boolean;
  onCameraPreset?: (preset: "top" | "front" | "side") => void;
}

export function ControlsPanel({ runId, phase, connected, onCameraPreset }: ControlsPanelProps) {
  const isActive = phase !== "completed" && phase !== "failed" && phase !== "cancelled" && phase !== "queued";

  async function handleCancel() {
    if (!confirm("Cancel this reasoning run?")) return;
    try {
      await cancelRun(runId);
    } catch (err) {
      console.error("Failed to cancel:", err);
    }
  }

  return (
    <div className="glass-panel p-3">
      <div className="text-[10px] font-mono text-slate-500 mb-3 uppercase tracking-wider">Controls</div>

      {/* Phase indicator */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-slate-400">Phase</span>
          <span className="text-[10px] font-mono text-blue-400">{phase.replace(/_/g, " ")}</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-500"
            style={{ width: isActive ? "100%" : phase === "completed" ? "100%" : "0%" }}
          />
        </div>
      </div>

      {/* Camera presets */}
      <div className="mb-3">
        <div className="text-[10px] text-slate-400 mb-1.5">Camera</div>
        <div className="flex gap-1">
          {(["top", "front", "side"] as const).map((preset) => (
            <button
              key={preset}
              onClick={() => onCameraPreset?.(preset)}
              className="flex-1 px-2 py-1 text-[10px] font-mono text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 rounded transition-colors capitalize"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-1.5">
        {isActive && (
          <button
            onClick={handleCancel}
            className="w-full px-3 py-1.5 text-[10px] font-medium text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 rounded transition-colors"
          >
            Cancel Run
          </button>
        )}
        <a
          href={`/runs/new`}
          className="block w-full px-3 py-1.5 text-[10px] font-medium text-center text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 rounded transition-colors"
        >
          New Session
        </a>
      </div>
    </div>
  );
}
