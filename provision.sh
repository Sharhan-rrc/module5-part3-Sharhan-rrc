#!/usr/bin/env bash
set -Eeuo pipefail
dnf install -y dnf-plugins-core rsync openssl
if [[ ! -f /etc/yum.repos.d/docker-ce.repo ]]; then
  dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
fi
dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker vagrant
install -d -m 755 /opt/ymb-module5
rsync -a --exclude='.git' --exclude='.vagrant' --exclude='node_modules' --exclude='.env' /vagrant/ /opt/ymb-module5/
cd /opt/ymb-module5
if [[ ! -f .env ]]; then
  umask 077
  printf 'SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > .env
fi
# Docker Desktop is loopback-only. In this guest publish only the gateway
# on the explicitly configured host-only adapter so the laptop can reach it.
cat > compose.vm.yml <<'YAML'
services:
  nginx:
    ports: !override
      - "192.168.56.55:80:80"
YAML
docker compose -f docker-compose.yml -f compose.vm.yml up --build -d --wait
docker compose -f docker-compose.yml -f compose.vm.yml ps
echo 'YMB VM deployment: http://192.168.56.55'
