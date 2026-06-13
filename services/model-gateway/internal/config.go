package gateway

import (
	"os"
	"time"
)

type Config struct {
	ListenAddr      string
	OllamaBaseURL   string
	DefaultModel    string
	ProviderTimeout time.Duration
}

func LoadConfig() *Config {
	return &Config{
		ListenAddr:      getEnv("LISTEN_ADDR", ":8090"),
		OllamaBaseURL:   getEnv("OLLAMA_BASE_URL", "http://localhost:11434"),
		DefaultModel:    getEnv("DEFAULT_CHAT_MODEL", "qwen2.5:7b"),
		ProviderTimeout: 60 * time.Second,
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
