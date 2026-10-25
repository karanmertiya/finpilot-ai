#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "=== [1/4] Installing Docker and Prerequisites ==="
apt-get update -y
apt-get install -y ca-certificates curl gnupg git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
usermod -aG docker azureuser

echo "=== [2/4] Cloning FinPilot AI Repository ==="
cd /home/azureuser
if [ -d "finpilot-ai" ]; then
    cd finpilot-ai
    git pull origin main
else
    git clone https://github.com/karanmertiya/finpilot-ai.git
    cd finpilot-ai
fi

chown -R azureuser:azureuser /home/azureuser/finpilot-ai

echo "=== [3/4] Building and Starting FinPilot AI Containers ==="
docker compose down || true
docker compose up --build -d

echo "=== [4/4] Verifying Containers Status ==="
docker compose ps
docker ps

echo "FinPilot AI successfully deployed and running on Azure VM!"
