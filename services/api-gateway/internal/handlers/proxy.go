package handlers

import (
	"io"
	"net/http"
	"strings"
)

// proxyRequest forwards an HTTP request to the target URL and streams the response back.
func proxyRequest(w http.ResponseWriter, r *http.Request, targetURL string) {
	// Build the proxied request
	proxyReq, err := http.NewRequestWithContext(r.Context(), r.Method, targetURL, r.Body)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create proxy request")
		return
	}

	// Copy relevant headers
	for key, values := range r.Header {
		if is_hop_header(key) {
			continue
		}
		for _, v := range values {
			proxyReq.Header.Add(key, v)
		}
	}
	proxyReq.Header.Set("X-Forwarded-For", r.RemoteAddr)
	proxyReq.ContentLength = r.ContentLength

	// Execute the proxy request
	client := &http.Client{Timeout: 0} // no timeout for streaming
	resp, err := client.Do(proxyReq)
	if err != nil {
		writeError(w, http.StatusBadGateway, "backend service unavailable")
		return
	}
	defer resp.Body.Close()

	// Copy response headers
	for key, values := range resp.Header {
		if is_hop_header(key) {
			continue
		}
		for _, v := range values {
			w.Header().Add(key, v)
		}
	}
	w.WriteHeader(resp.StatusCode)

	// Stream the response body
	if _, err := io.Copy(w, resp.Body); err != nil {
		// Connection may have been closed by client; log but don't error
		return
	}
}

// is_hop_header returns true for HTTP hop-by-hop headers that should not be forwarded.
func is_hop_header(key string) bool {
	hopHeaders := []string{
		"Connection", "Keep-Alive", "Proxy-Authenticate",
		"Proxy-Authorization", "Te", "Trailers",
		"Transfer-Encoding", "Upgrade",
	}
	lower := strings.ToLower(key)
	for _, h := range hopHeaders {
		if strings.ToLower(h) == lower {
			return true
		}
	}
	return false
}
