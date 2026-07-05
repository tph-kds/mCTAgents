#!/bin/bash
# Docker Storage Migration: Move Docker data root from / (root) to /home
# Run with: sudo bash scripts/fix-docker-storage.sh
set -euo pipefail

DOCKER_DATA_ROOT="/home/zyelyhero/mctagents-data"
DAEMON_JSON="/etc/docker/daemon.json"

echo "=== Docker Storage Migration ==="
echo "Moving Docker data root to: $DOCKER_DATA_ROOT"
echo ""

# Step 1: Stop Docker
echo "[1/4] Stopping Docker..."
systemctl stop docker docker.socket containerd 2>/dev/null || true

# Step 2: Create target directory
echo "[2/4] Creating target directory..."
mkdir -p "$DOCKER_DATA_ROOT"

# Step 3: Migrate existing data if any
if [ -d "/var/lib/docker" ] && [ "$(ls -A /var/lib/docker 2>/dev/null)" ]; then
    echo "[3/4] Migrating existing Docker data..."
    rsync -av --progress /var/lib/docker/ "$DOCKER_DATA_ROOT/"
    echo "Data migrated. Original at /var/lib/docker will be preserved as backup."
else
    echo "[3/4] No existing Docker data to migrate."
fi

# Step 4: Write daemon.json
echo "[4/4] Writing Docker daemon configuration..."
cat > "$DAEMON_JSON" << 'EOF'
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    },
    "data-root": "/home/zyelyhero/mctagents-data"
}
EOF

echo ""
echo "Configuration written to $DAEMON_JSON:"
cat "$DAEMON_JSON"
echo ""

# Step 5: Restart Docker
echo "Restarting Docker..."
systemctl start docker

# Step 6: Verify
echo ""
echo "=== Verification ==="
docker info 2>/dev/null | grep -E "Docker Root Dir|Storage Driver"
echo ""
echo "Docker data root is now: $DOCKER_DATA_ROOT"
echo ""
echo "To free root space after confirming everything works:"
echo "  sudo rm -rf /var/lib/docker"
