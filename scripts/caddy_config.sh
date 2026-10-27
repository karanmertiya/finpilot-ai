#!/bin/bash
set -e

cat > /etc/caddy/Caddyfile << 'CADDY_CONFIG'
finpilot.karanmertiya.me {
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        reverse_proxy 127.0.0.1:3000
    }
}

:80 {
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        reverse_proxy 127.0.0.1:3000
    }
}
CADDY_CONFIG

systemctl daemon-reload
systemctl restart caddy
systemctl status caddy --no-pager
