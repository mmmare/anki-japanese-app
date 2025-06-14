#!/bin/bash

echo "🔧 Complete Fix for Package Lock and Node Version Issues"
echo "======================================================="

# Stop all running containers
echo "Stopping all containers..."
docker-compose down

# Remove ALL Docker artifacts to ensure clean build
echo "Performing complete Docker cleanup..."
docker system prune -a -f --volumes
docker builder prune -a -f

# Pull latest code with fixes
echo "Pulling latest fixes from GitHub..."
git pull

# Remove any local frontend artifacts that could cause conflicts
echo "Cleaning up local frontend artifacts..."
rm -rf csv-to-anki-app/frontend/node_modules
rm -f csv-to-anki-app/frontend/package-lock.json
rm -rf csv-to-anki-app/frontend/build
rm -rf csv-to-anki-app/frontend/.npm

# Make sure all scripts are executable
chmod +x scripts/*.sh

# Build with verbose output to see what's happening
echo "Building services with complete rebuild..."
echo "This may take several minutes as we're rebuilding everything from scratch..."
docker-compose up -d --build --force-recreate --no-cache

# Monitor the build process
echo ""
echo "Monitoring build progress..."
echo "You can also run 'docker logs -f anki-frontend' in another terminal to see detailed build logs"

# Wait longer for the complete rebuild
echo "Waiting for services to fully initialize (this takes longer on first build)..."
sleep 60

# Comprehensive health check
echo ""
echo "🏥 Comprehensive Health Check:"
echo "============================="

# Check if containers exist and are running
echo "Checking container status..."
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(anki-frontend|anki-backend|anki-nginx)"; then
    echo "✅ Some Anki containers are running"
else
    echo "❌ No Anki containers found running"
    echo ""
    echo "📋 All containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    echo ""
    echo "🔍 Recent container logs:"
    echo "Frontend build logs:"
    docker logs anki-frontend --tail=20 2>/dev/null || echo "No frontend container logs"
    echo ""
    echo "Backend logs:"
    docker logs anki-backend --tail=10 2>/dev/null || echo "No backend container logs"
    echo ""
    echo "Nginx logs:"
    docker logs anki-nginx --tail=10 2>/dev/null || echo "No nginx container logs"
fi

# Test connectivity
echo ""
echo "Testing service connectivity..."

# Check backend
if curl -s -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    if docker ps | grep -q anki-backend; then
        echo "Backend container is running but not responding - checking logs:"
        docker logs anki-backend --tail=15
    fi
fi

# Check if any nginx is responding
NGINX_WORKING=false
if curl -s -f http://localhost &>/dev/null; then
    echo "✅ Nginx is serving content on port 80"
    NGINX_WORKING=true
elif curl -s -f http://localhost:8080 &>/dev/null; then
    echo "✅ Nginx is serving content on port 8080"
    NGINX_WORKING=true
else
    echo "❌ Nginx is not responding on port 80 or 8080"
    if docker ps | grep -q anki-nginx; then
        echo "Nginx container is running but not responding - checking logs:"
        docker logs anki-nginx --tail=15
    fi
fi

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "localhost")

echo ""
echo "🎯 Final Status Report:"
echo "======================"
echo "External IP: $EXTERNAL_IP"

if [ "$NGINX_WORKING" = true ]; then
    if curl -s -f http://localhost &>/dev/null; then
        echo "🌐 Your app should be accessible at: http://$EXTERNAL_IP"
    else
        echo "🌐 Your app should be accessible at: http://$EXTERNAL_IP:8080"
    fi
    echo "✅ Deployment appears successful!"
else
    echo "❌ Deployment has issues. See logs above for details."
    echo ""
    echo "🔧 Try these debugging steps:"
    echo "1. Check detailed logs: docker-compose logs"
    echo "2. Check individual service logs: docker logs anki-frontend"
    echo "3. Restart specific services: docker-compose restart frontend"
    echo "4. Complete restart: docker-compose down && docker-compose up -d"
fi

echo ""
echo "🛠️  For further troubleshooting, run: ./scripts/troubleshoot.sh"
echo "✅ Complete rebuild and fix attempt finished!"
