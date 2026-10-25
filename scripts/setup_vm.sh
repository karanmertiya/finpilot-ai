#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "=== [1/4] Configuring Git and Docker ==="
git config --global --add safe.directory '*'

echo "=== [2/4] Pulling Latest FinPilot AI Code ==="
cd /home/azureuser
if [ -d "finpilot-ai" ]; then
    cd finpilot-ai
    git fetch origin main
    git reset --hard origin/main
else
    git clone https://github.com/karanmertiya/finpilot-ai.git
    cd finpilot-ai
fi

chown -R azureuser:azureuser /home/azureuser/finpilot-ai

echo "=== [3/4] Building and Starting Containers ==="
docker compose down || true
docker compose up --build -d

echo "Waiting for services to become healthy..."
sleep 15

echo "=== [4/4] Seeding PostgreSQL Database with Synthetic Indian Data ==="
docker compose exec -T backend python scripts/seed_data.py || true

echo "=== Container Status ==="
docker compose ps
docker ps

echo "FinPilot AI is LIVE on http://4.240.114.82:3000 !"
