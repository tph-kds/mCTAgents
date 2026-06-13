export interface MCTAgentsConfig {
  baseUrl: string;
  apiKey?: string;
}

export interface ReasoningEvent {
  event_id: string;
  run_id: string;
  type: string;
  sequence: number;
  agent_id?: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface Run {
  run_id: string;
  status: string;
  events_url: string;
}

export class MCTAgentsClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(config: MCTAgentsConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.apiKey = config.apiKey;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) h["X-API-Key"] = this.apiKey;
    return h;
  }

  get runs() {
    const self = this;
    return {
      async create(params: { problem: string; mode?: string; evidence_policy?: string; budget?: Record<string, number> }): Promise<Run> {
        const resp = await fetch(`${self.baseUrl}/v1/runs`, {
          method: "POST",
          headers: self.headers(),
          body: JSON.stringify(params),
        });
        if (!resp.ok) throw new Error(`Failed to create run: ${resp.statusText}`);
        return resp.json();
      },

      async get(runId: string): Promise<Record<string, unknown>> {
        const resp = await fetch(`${self.baseUrl}/v1/runs/${runId}`, { headers: self.headers() });
        if (!resp.ok) throw new Error(`Failed to get run: ${resp.statusText}`);
        return resp.json();
      },

      async *stream(runId: string): AsyncGenerator<ReasoningEvent> {
        const es = new EventSource(`${self.baseUrl}/v1/runs/${runId}/events`);
        const queue: ReasoningEvent[] = [];
        let resolve: (() => void) | null = null;

        const handler = (e: MessageEvent) => {
          try {
            queue.push(JSON.parse(e.data));
            resolve?.();
          } catch {}
        };

        // Listen for all named SSE events and generic message events
        es.addEventListener("message", handler);
        // Also catch any custom event types by polling readyState
        const originalOnOpen = es.onopen;
        es.onopen = () => {
          originalOnOpen?.call(es, new Event("open"));
          resolve?.();
        };

        es.onerror = () => resolve?.();

        try {
          while (es.readyState !== EventSource.CLOSED) {
            if (queue.length === 0) {
              await new Promise<void>((r) => (resolve = r));
            }
            if (queue.length > 0) {
              yield queue.shift()!;
            }
          }
        } finally {
          es.close();
        }
      },

      async cancel(runId: string): Promise<void> {
        const resp = await fetch(`${self.baseUrl}/v1/runs/${runId}/cancel`, { method: "POST", headers: self.headers() });
        if (!resp.ok) throw new Error(`Failed to cancel run: ${resp.statusText}`);
      },
    };
  }
}
