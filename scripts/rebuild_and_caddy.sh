#!/bin/bash
set -e
export HOME=/root

echo "=== [1/3] Pulling Latest Code ==="
cd /home/azureuser/finpilot-ai
git fetch origin main
git reset --hard origin/main

echo "=== [2/3] Rebuilding Frontend Container ==="
docker compose build frontend
docker compose up -d --no-deps frontend

echo "=== [3/3] Installing and Configuring Caddy ==="
apt-get update -y
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg || true
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update -y
apt-get install -y caddy

# Flush previous iptables redirect rule
iptables -t nat -F PREROUTING || true

# Set Caddy config
cat << 'EOF' > /etc/caddy/Caddyfile
:80 {
    reverse_proxy localhost:3000
}
EOF

systemctl enable --now caddy
systemctl restart caddy

echo "Caddy and updated frontend running on port 80 and 3000!"
