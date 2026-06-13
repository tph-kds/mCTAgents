package main

import (
	"context"
	"log"
	"net/http"
	"os/signal"
	"syscall"
	"time"

	gateway "github.com/tph-kds/mctagents/model-gateway/internal"
)

func main() {
	cfg := gateway.LoadConfig()

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok","service":"model-gateway"}`))
	})

	mux.HandleFunc("/v1/chat", gateway.HandleChat(cfg))
	mux.HandleFunc("/v1/chat/stream", gateway.HandleChatStream(cfg))
	mux.HandleFunc("/v1/embed", gateway.HandleEmbed(cfg))
	mux.HandleFunc("/v1/models", gateway.HandleListModels(cfg))

	srv := &http.Server{Addr: cfg.ListenAddr, Handler: mux}

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	go func() {
		log.Printf("Model Gateway listening on %s", cfg.ListenAddr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	<-ctx.Done()
	log.Println("Shutting down...")
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()
	srv.Shutdown(shutdownCtx)
}
