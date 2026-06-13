FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /api-gateway ./cmd/api-gateway

FROM alpine:3.19 AS development
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=builder /api-gateway .
CMD ["./api-gateway"]

FROM alpine:3.19 AS production
RUN apk add --no-cache curl ca-certificates
COPY --from=builder /api-gateway /usr/local/bin/
CMD ["api-gateway"]
