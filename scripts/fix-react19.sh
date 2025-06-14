#!/bin/bash

echo "🔧 Fixing React 19 Compatibility and Docker Build Issues"
echo "========================================================"

# Stop all running containers
echo "Stopping all containers..."
docker-compose down

# Remove old images to force rebuild
echo "Cleaning up old images..."
docker system prune -f
docker rmi $(docker images -q --filter "dangling=true") 2>/dev/null || true

# Pull latest code with fixes
echo "Pulling latest fixes from GitHub..."
git pull

# Make sure all scripts are executable
chmod +x scripts/*.sh

# Clear npm cache in case of any issues
echo "Clearing any local npm cache..."
rm -rf csv-to-anki-app/frontend/node_modules
rm -rf csv-to-anki-app/frontend/package-lock.json

# Build and start with the fixed configuration
echo "Building and starting services with React 19 fixes..."
docker-compose up -d --build --force-recreate

# Wait for services to initialize
echo "Waiting for services to start..."
sleep 45

# Check service health
echo ""
echo "🏥 Health Check Results:"
echo "========================"

# Check backend
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "Backend logs (last 15 lines):"
    docker logs anki-backend --tail=15 2>/dev/null || echo "No backend container"
fi

# Check frontend build
if docker ps | grep -q anki-frontend; then
    echo "✅ Frontend container is running"
else
    echo "❌ Frontend container failed to start"
    echo "Frontend logs (last 15 lines):"
    docker logs anki-frontend --tail=15 2>/dev/null || echo "No frontend container"
fi

# Check nginx
if curl -f http://localhost &>/dev/null; then
    echo "✅ Nginx is serving content"
elif curl -f http://localhost:8080 &>/dev/null; then
    echo "✅ Nginx is serving content on port 8080"
else
    echo "❌ Nginx is not responding"
    echo "Nginx logs (last 15 lines):"
    docker logs anki-nginx --tail=15 2>/dev/null || echo "No nginx container"
fi

# Show final status
echo ""
echo "📊 Container Status:"
echo "==================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "🎯 Access Information:"
echo "====================="
if docker ps | grep -q ":80->"; then
    echo "🌐 Your app: http://$EXTERNAL_IP"
elif docker ps | grep -q ":8080->"; then
    echo "🌐 Your app: http://$EXTERNAL_IP:8080"
else
    echo "⚠️  App may not be accessible - check container logs above"
fi

echo ""
echo "🔍 If you still have issues, run:"
echo "  ./scripts/troubleshoot.sh"

echo ""
echo "✅ React 19 compatibility fix complete!"
