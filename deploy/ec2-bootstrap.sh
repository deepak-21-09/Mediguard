#!/usr/bin/env bash
# =============================================================================
# MediGuard — EC2 one-shot bootstrap + deploy
# Target: Ubuntu 22.04 / 24.04, t3.small or larger
# Usage : bash ec2-bootstrap.sh
# =============================================================================
set -euo pipefail

# ── Grab public IP from instance metadata ────────────────────────────────────
EC2_PUBLIC_IP=$(curl -sf --max-time 3 http://169.254.169.254/latest/meta-data/public-ipv4 \
  || curl -sf --max-time 3 https://checkip.amazonaws.com \
  || echo "UNKNOWN")

echo "============================================================"
echo "  MediGuard EC2 Bootstrap"
echo "  Public IP : $EC2_PUBLIC_IP"
echo "============================================================"

# ── 1. Install Docker CE ──────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo ""
  echo "==> Installing Docker..."
  sudo apt-get update -qq
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -qq
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
  echo "==> Docker installed. NOTE: log out + back in (or run 'newgrp docker') if"
  echo "    the next step fails with a permission error, then re-run this script."
else
  echo "==> Docker already installed: $(docker --version)"
fi

# ── 2. Clone / update repo ───────────────────────────────────────────────────
REPO_DIR="$HOME/Mediguard"
# If you used scp instead of git, comment out this block.
if [ ! -d "$REPO_DIR/.git" ]; then
  echo ""
  echo "==> Cloning repo..."
  # Replace with your actual repo URL if using git clone:
  # git clone https://github.com/<ORG>/Mediguard.git "$REPO_DIR"
  echo "ERROR: $REPO_DIR not found. Either:"
  echo "  a) scp the project here first, or"
  echo "  b) uncomment the git clone line above with your repo URL."
  exit 1
fi
cd "$REPO_DIR"

# ── 3. Write production backend/.env ─────────────────────────────────────────
# Values are sourced from the existing .env (already has Supabase creds etc.)
# We only override CORS_ORIGINS to include this instance's public IP.
echo ""
echo "==> Patching backend/.env for production (CORS_ORIGINS)..."

# Remove any existing CORS_ORIGINS line, then append the correct one.
sed -i '/^CORS_ORIGINS/d' backend/.env
echo "CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://${EC2_PUBLIC_IP}:3000,http://${EC2_PUBLIC_IP}" \
  >> backend/.env

echo "    CORS_ORIGINS set to:"
grep "^CORS_ORIGINS" backend/.env

# ── 4. Write production frontend/.env.local ───────────────────────────────────
echo ""
echo "==> Writing frontend/.env.local pointing at EC2 backend..."
cat > frontend/.env.local <<EOF
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_placeholder
CLERK_SECRET_KEY=sk_test_placeholder

NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Backend API on this EC2 instance
NEXT_PUBLIC_API_URL=http://${EC2_PUBLIC_IP}:8000
EOF

# ── 5. Build and start ────────────────────────────────────────────────────────
echo ""
echo "==> Building and starting containers (this takes a few minutes)..."
docker compose -f docker-compose.prod.yml up -d --build

# ── 6. Wait for backend health ────────────────────────────────────────────────
echo ""
echo "==> Waiting for backend to become healthy..."
ATTEMPTS=0
MAX=30
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX" ]; then
    echo "ERROR: Backend did not become healthy after ${MAX} attempts."
    echo "Check logs: docker compose -f docker-compose.prod.yml logs backend"
    exit 1
  fi
  echo "    Waiting... ($ATTEMPTS/$MAX)"
  sleep 5
done
echo "    Backend is healthy!"

# ── 7. Verify CORS ────────────────────────────────────────────────────────────
echo ""
echo "==> Verifying CORS header for origin http://${EC2_PUBLIC_IP}:3000 ..."
CORS_HEADER=$(curl -sI \
  -H "Origin: http://${EC2_PUBLIC_IP}:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  http://localhost:8000/health \
  | grep -i "access-control-allow-origin" || echo "NOT FOUND")
echo "    $CORS_HEADER"

# ── 8. Run e2e test suite ────────────────────────────────────────────────────
echo ""
echo "==> Running e2e test suite against http://localhost:8000 ..."
cd "$REPO_DIR/backend"
if command -v python3 &>/dev/null; then
  pip install httpx --quiet 2>/dev/null || true
  python3 e2e_test.py
else
  echo "WARN: python3 not found on host — run e2e_test.py inside the container:"
  echo "  docker exec mediguard_backend python e2e_test.py"
fi
cd "$REPO_DIR"

# ── Final summary ─────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  MediGuard is LIVE"
echo ""
echo "  Frontend  :  http://${EC2_PUBLIC_IP}:3000"
echo "  Backend   :  http://${EC2_PUBLIC_IP}:8000"
echo "  Health    :  http://${EC2_PUBLIC_IP}:8000/health"
echo ""
echo "  Decisions needed from you:"
echo "  1. Domain name? → Add to CORS_ORIGINS + set up nginx reverse proxy"
echo "  2. HTTPS/SSL?   → Provide domain and run: bash deploy/setup-ssl.sh"
echo "  3. Clerk auth?  → Replace pk_test_placeholder keys in frontend/.env.local"
echo "============================================================"
