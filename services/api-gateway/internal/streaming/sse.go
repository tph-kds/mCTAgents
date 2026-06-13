package streaming

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/go-chi/chi/v5"
)

type SSEEvent struct {
	EventID   string          `json:"event_id"`
	RunID     string          `json:"run_id"`
	Type      string          `json:"type"`
	Sequence  int             `json:"sequence"`
	AgentID   string          `json:"agent_id,omitempty"`
	Payload   json.RawMessage `json:"payload"`
	CreatedAt string          `json:"created_at"`
}

type SSEClient struct {
	RunID string
	Chan  chan SSEEvent
	Done  chan struct{}
}

type SSEHub struct {
	clients map[string][]*SSEClient
	mu      sync.RWMutex
}

func NewSSEHub() *SSEHub {
	return &SSEHub{
		clients: make(map[string][]*SSEClient),
	}
}

func (h *SSEHub) Subscribe(runID string) *SSEClient {
	client := &SSEClient{
		RunID: runID,
		Chan:  make(chan SSEEvent, 64),
		Done:  make(chan struct{}),
	}

	h.mu.Lock()
	h.clients[runID] = append(h.clients[runID], client)
	h.mu.Unlock()

	return client
}

func (h *SSEHub) Publish(runID string, event SSEEvent) {
	if event.CreatedAt == "" {
		event.CreatedAt = time.Now().UTC().Format(time.RFC3339)
	}

	h.mu.RLock()
	defer h.mu.RUnlock()

	for _, client := range h.clients[runID] {
		select {
		case client.Chan <- event:
		default:
		}
	}
}

func (h *SSEHub) Unsubscribe(client *SSEClient) {
	close(client.Done)

	h.mu.Lock()
	defer h.mu.Unlock()

	clients := h.clients[client.RunID]
	for i, c := range clients {
		if c == client {
			h.clients[client.RunID] = append(clients[:i], clients[i+1:]...)
			break
		}
	}
}

func HandleSSE(hub *SSEHub) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		runID := chi.URLParam(r, "run_id")
		if runID == "" {
			http.Error(w, `{"error":"run_id is required"}`, http.StatusBadRequest)
			return
		}

		client := hub.Subscribe(runID)
		defer hub.Unsubscribe(client)

		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, `{"error":"streaming unsupported"}`, http.StatusInternalServerError)
			return
		}

		ctx := r.Context()
		for {
			select {
			case <-ctx.Done():
				return
			case <-client.Done:
				return
			case event := <-client.Chan:
				data, err := json.Marshal(event)
				if err != nil {
					continue
				}
				if _, err := fmt.Fprintf(w, "event: %s\n", event.Type); err != nil {
					return
				}
				if _, err := fmt.Fprintf(w, "data: %s\n\n", data); err != nil {
					return
				}
				flusher.Flush()
			}
		}
	}
}
