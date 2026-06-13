package main

import (
	"context"
	"log"
	"net/http"
	"os/signal"
	"syscall"
	"time"

	"github.com/tph-kds/mctagents/api-gateway/internal/config"
	"github.com/tph-kds/mctagents/api-gateway/internal/server"
)

func main() {
	cfg := config.LoadConfig()
	srv, err := server.NewServer(cfg)
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	log.Printf("Starting API Gateway on %s", cfg.ListenAddr)

	errCh := make(chan error, 1)
	go func() {
		if listenErr := srv.ListenAndServe(); listenErr != nil && listenErr != http.ErrServerClosed {
			errCh <- listenErr
		}
		close(errCh)
	}()

	select {
	case <-ctx.Done():
	case listenErr := <-errCh:
		if listenErr != nil {
			log.Fatalf("Server error: %v", listenErr)
		}
	}

	log.Println("Shutting down...")
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	if shutdownErr := srv.Shutdown(shutdownCtx); shutdownErr != nil {
		log.Fatalf("Shutdown error: %v", shutdownErr)
	}

	log.Println("Server stopped")
}
