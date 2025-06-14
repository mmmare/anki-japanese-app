#!/bin/bash

# Quick Deploy Script for VPS (Non-sudo)
# Run this on your VPS after GitHub Actions complete

set -e

echo "🚀 Deploying Japanese Anki App to VPS..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found. Are you in the right directory?"
    echo "Please cd to your anki-japanese-app directory first"
    exit 1
fi

# Pull latest code
log_info "Pulling latest code from GitHub..."
git pull origin main

# Create non-sudo version of docker-compose if needed
if [ ! -f "docker-compose-user.yml" ]; then
    log_info "Creating user-friendly docker-compose file..."
    cp docker-compose.yml docker-compose-user.yml
    
    # Change ports to avoid needing sudo
    sed -i 's/"80:80"/"8080:80"/g' docker-compose-user.yml
    sed -i 's/"443:443"/"8443:443"/g' docker-compose-user.yml 2>/dev/null || true
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running or not accessible"
    log_info "You may need to add your user to the docker group:"
    log_info "sudo usermod -aG docker $USER"
    log_info "Then log out and back in"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    log_warn "docker-compose not found. Checking for user installation..."
    if [ -f ~/.local/bin/docker-compose ]; then
        export PATH="$HOME/.local/bin:$PATH"
        log_info "Using user-installed docker-compose"
    else
        log_error "docker-compose not found. Please install it first"
        exit 1
    fi
fi

# Stop existing containers
log_info "Stopping existing containers..."
docker-compose -f docker-compose-user.yml down 2>/dev/null || true

# Pull latest images (if using pre-built images)
log_info "Pulling latest Docker images..."
docker-compose -f docker-compose-user.yml pull 2>/dev/null || log_warn "Could not pull images, will build locally"

# Build and start containers
log_info "Building and starting containers..."
docker-compose -f docker-compose-user.yml up --build -d

# Wait for services to start
log_info "Waiting for services to start..."
sleep 30

# Get VPS IP
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-vps-ip")

# Health checks
log_info "Performing health checks..."

# Check frontend
if curl -f http://localhost:8080 >/dev/null 2>&1; then
    log_info "✅ Frontend is healthy"
    echo "   Access at: http://$VPS_IP:8080"
else
    log_warn "❌ Frontend health check failed"
    log_info "Checking frontend logs..."
    docker-compose -f docker-compose-user.yml logs frontend | tail -10
fi

# Check backend
if curl -f http://localhost:8000/docs >/dev/null 2>&1; then
    log_info "✅ Backend is healthy"
    echo "   API docs at: http://$VPS_IP:8000/docs"
else
    log_warn "❌ Backend health check failed"
    log_info "Checking backend logs..."
    docker-compose -f docker-compose-user.yml logs backend | tail -10
fi

# Show container status
log_info "Container status:"
docker-compose -f docker-compose-user.yml ps

echo ""
log_info "🎉 Deployment completed!"
echo ""
echo "Your application is available at:"
echo "  Frontend: http://$VPS_IP:8080"
echo "  Backend:  http://$VPS_IP:8000/docs"
echo ""
echo "To view logs: docker-compose -f docker-compose-user.yml logs"
echo "To stop:      docker-compose -f docker-compose-user.yml down"
