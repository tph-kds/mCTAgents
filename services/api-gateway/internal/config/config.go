package config

import "os"

type Config struct {
	ListenAddr         string
	DatabaseURL        string
	RedisURL           string
	ModelGatewayURL    string
	ReasoningEngineURL string
	EvidenceServiceURL string
	AuthEnabled        bool
	APIKey             string
	RateLimitRPS       int
	LogLevel           string
}

func LoadConfig() *Config {
	return &Config{
		ListenAddr:         getEnv("LISTEN_ADDR", ":8080"),
		DatabaseURL:        getEnv("DATABASE_URL", "postgres://mctagents:devpassword@localhost:5432/mctagents"),
		RedisURL:           getEnv("REDIS_URL", "redis://localhost:6379"),
		ModelGatewayURL:    getEnv("MODEL_GATEWAY_URL", "http://localhost:8081"),
		ReasoningEngineURL: getEnv("REASONING_ENGINE_URL", "http://localhost:8082"),
		EvidenceServiceURL: getEnv("EVIDENCE_SERVICE_URL", "http://localhost:8083"),
		AuthEnabled:        getEnv("AUTH_ENABLED", "false") == "true",
		APIKey:             getEnv("API_KEY", ""),
		RateLimitRPS:       100,
		LogLevel:           getEnv("LOG_LEVEL", "info"),
	}
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}
