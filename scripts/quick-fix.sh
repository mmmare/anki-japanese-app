#!/bin/bash

echo "🚀 Quick Fix for Anki App Issues"
echo "================================"

# Stop all containers
echo "Stopping all containers..."
docker-compose down

# Remove any orphaned containers
echo "Cleaning up..."
docker system prune -f

# Check for port conflicts
echo "Checking for port conflicts..."
if lsof -i :80 &>/dev/null; then
    echo "⚠️  Port 80 is in use. Switching to port 8080..."
    export NGINX_PORT=8080
else
    export NGINX_PORT=80
fi

# Set environment variables for proper networking
export FRONTEND_URL=http://localhost:3000
export BACKEND_URL=http://localhost:8000

# Rebuild and start with proper networking
echo "Starting services with proper configuration..."
docker-compose up -d --build

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check service health
echo "Checking service health..."

# Test backend
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "Backend logs:"
    docker logs anki-backend --tail=10
fi

# Test frontend
if curl -f http://localhost:3000 &>/dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not responding"
    echo "Frontend logs:"
    docker logs anki-frontend --tail=10
fi

# Test nginx
if curl -f http://localhost:$NGINX_PORT &>/dev/null; then
    echo "✅ Nginx is working on port $NGINX_PORT"
else
    echo "❌ Nginx not responding"
    echo "Nginx logs:"
    docker logs anki-nginx --tail=10
fi

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "🎉 Setup complete!"
echo "Your app should be accessible at:"
echo "  🌐 http://$EXTERNAL_IP:$NGINX_PORT"
echo ""
echo "If you still see errors, run: ./scripts/troubleshoot.sh"
