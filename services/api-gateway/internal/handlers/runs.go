package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/tph-kds/mctagents/api-gateway/internal/config"
	"github.com/tph-kds/mctagents/api-gateway/internal/streaming"
)

type Handlers struct {
	cfg *config.Config
	hub *streaming.SSEHub
}

func NewHandlers(cfg *config.Config, hub *streaming.SSEHub) *Handlers {
	return &Handlers{cfg: cfg, hub: hub}
}

type CreateRunRequest struct {
	Problem        string         `json:"problem"`
	Mode           string         `json:"mode"`
	EvidencePolicy string         `json:"evidence_policy"`
	Budget         map[string]int `json:"budget"`
}

type RunResponse struct {
	RunID     string `json:"run_id"`
	Status    string `json:"status"`
	EventsURL string `json:"events_url"`
	CreatedAt string `json:"created_at"`
}

type RunDetail struct {
	RunID       string         `json:"run_id"`
	Status      string         `json:"status"`
	Problem     string         `json:"problem"`
	Mode        string         `json:"mode"`
	CreatedAt   string         `json:"created_at"`
	UpdatedAt   string         `json:"updated_at"`
	FinalAnswer string         `json:"final_answer,omitempty"`
	Budget      map[string]int `json:"budget,omitempty"`
}

type Claim struct {
	ID         string  `json:"id"`
	RunID      string  `json:"run_id"`
	Statement  string  `json:"statement"`
	Status     string  `json:"status"`
	Confidence float64 `json:"confidence"`
	CreatedAt  string  `json:"created_at"`
}

type Evidence struct {
	ID        string  `json:"id"`
	RunID     string  `json:"run_id"`
	ClaimID   string  `json:"claim_id"`
	Content   string  `json:"content"`
	Source    string  `json:"source"`
	Relevance float64 `json:"relevance"`
	CreatedAt string  `json:"created_at"`
}

type ClaimGraph struct {
	RunID    string     `json:"run_id"`
	Claims   []Claim    `json:"claims"`
	Evidence []Evidence `json:"evidence"`
}

type CancelRunResponse struct {
	RunID  string `json:"run_id"`
	Status string `json:"status"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type UploadDocumentResponse struct {
	DocumentID string `json:"document_id"`
	Filename   string `json:"filename"`
	Size       int64  `json:"size"`
}

func (h *Handlers) CreateRun(w http.ResponseWriter, r *http.Request) {
	var req CreateRunRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	defer r.Body.Close()

	if req.Problem == "" {
		writeError(w, http.StatusBadRequest, "problem is required")
		return
	}

	// Forward to reasoning engine
	backendURL := h.cfg.ReasoningEngineURL + "/v1/runs"
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) GetRun(w http.ResponseWriter, r *http.Request) {
	runID := chi.URLParam(r, "run_id")
	if runID == "" {
		writeError(w, http.StatusBadRequest, "run_id is required")
		return
	}

	backendURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) CancelRun(w http.ResponseWriter, r *http.Request) {
	runID := chi.URLParam(r, "run_id")
	if runID == "" {
		writeError(w, http.StatusBadRequest, "run_id is required")
		return
	}

	backendURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID + "/cancel"
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) GetClaimGraph(w http.ResponseWriter, r *http.Request) {
	runID := chi.URLParam(r, "run_id")
	if runID == "" {
		writeError(w, http.StatusBadRequest, "run_id is required")
		return
	}

	// Combine claims and evidence from the reasoning engine
	claimsURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID + "/claims"
	evidenceURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID + "/evidence"

	claimsResp, err := http.Get(claimsURL)
	if err != nil {
		writeError(w, http.StatusBadGateway, "failed to fetch claims from reasoning engine")
		return
	}
	defer claimsResp.Body.Close()

	evidenceResp, err := http.Get(evidenceURL)
	if err != nil {
		writeError(w, http.StatusBadGateway, "failed to fetch evidence from reasoning engine")
		return
	}
	defer evidenceResp.Body.Close()

	var claimsData struct {
		Claims []json.RawMessage `json:"claims"`
	}
	var evidenceData struct {
		Evidence []json.RawMessage `json:"evidence"`
	}

	json.NewDecoder(claimsResp.Body).Decode(&claimsData)
	json.NewDecoder(evidenceResp.Body).Decode(&evidenceData)

	graph := map[string]interface{}{
		"run_id":   runID,
		"claims":   claimsData.Claims,
		"evidence": evidenceData.Evidence,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(graph)
}

func (h *Handlers) ListClaims(w http.ResponseWriter, r *http.Request) {
	runID := chi.URLParam(r, "run_id")
	if runID == "" {
		writeError(w, http.StatusBadRequest, "run_id is required")
		return
	}

	backendURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID + "/claims"
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) ListEvidence(w http.ResponseWriter, r *http.Request) {
	runID := chi.URLParam(r, "run_id")
	if runID == "" {
		writeError(w, http.StatusBadRequest, "run_id is required")
		return
	}

	backendURL := h.cfg.ReasoningEngineURL + "/v1/runs/" + runID + "/evidence"
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) UploadDocument(w http.ResponseWriter, r *http.Request) {
	// Forward multipart upload to evidence service
	backendURL := h.cfg.EvidenceServiceURL + "/v1/documents"
	proxyRequest(w, r, backendURL)
}

func (h *Handlers) StreamEvents(w http.ResponseWriter, r *http.Request) {
	streaming.HandleSSE(h.hub)(w, r)
}

func writeError(w http.ResponseWriter, statusCode int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	resp := ErrorResponse{Error: message}
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		http.Error(w, `{"error":"internal error"}`, http.StatusInternalServerError)
	}
}

func generateRunID() string {
	return fmt.Sprintf("run_%d", time.Now().UnixNano())
}
