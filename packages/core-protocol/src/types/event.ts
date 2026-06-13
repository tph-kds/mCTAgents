import type { EventType } from "./enums.js";

export interface Event {
  id: string;
  event_id: string;
  run_id: string;
  sequence: number;
  type: EventType;
  agent_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}
