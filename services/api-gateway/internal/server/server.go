package server

import (
	"net/http"

	"github.com/go-chi/chi/v5"
	chimw "github.com/go-chi/chi/v5/middleware"
	"github.com/tph-kds/mctagents/api-gateway/internal/config"
	"github.com/tph-kds/mctagents/api-gateway/internal/handlers"
	"github.com/tph-kds/mctagents/api-gateway/internal/streaming"
)

type Server struct {
	*http.Server
	hub *streaming.SSEHub
}

func NewServer(cfg *config.Config) (*Server, error) {
	r := chi.NewRouter()
	hub := streaming.NewSSEHub()

	r.Use(chimw.Recoverer)
	r.Use(chimw.Logger)
	r.Use(chimw.RealIP)

	h := handlers.NewHandlers(cfg, hub)

	r.Get("/health", h.Health)

	r.Route("/v1", func(r chi.Router) {
		r.Post("/runs", h.CreateRun)
		r.Get("/runs/{run_id}", h.GetRun)
		r.Get("/runs/{run_id}/events", h.StreamEvents)
		r.Post("/runs/{run_id}/cancel", h.CancelRun)
		r.Get("/runs/{run_id}/claim-graph", h.GetClaimGraph)
		r.Get("/runs/{run_id}/claims", h.ListClaims)
		r.Get("/runs/{run_id}/evidence", h.ListEvidence)
		r.Post("/documents", h.UploadDocument)
	})

	srv := &http.Server{
		Addr:    cfg.ListenAddr,
		Handler: r,
	}

	return &Server{
		Server: srv,
		hub:    hub,
	}, nil
}
