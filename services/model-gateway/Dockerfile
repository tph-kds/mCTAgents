FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /model-gateway ./cmd/model-gateway

FROM alpine:3.19 AS development
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=builder /model-gateway .
CMD ["./model-gateway"]

FROM alpine:3.19 AS production
RUN apk add --no-cache curl ca-certificates
COPY --from=builder /model-gateway /usr/local/bin/
CMD ["model-gateway"]
