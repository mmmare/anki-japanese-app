#!/bin/bash

echo "🔍 Japanese Anki App - Troubleshooting Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found"
    echo "Please run this script from the anki-japanese-app directory"
    exit 1
fi

echo -e "\n1. 📋 Container Status:"
echo "----------------------"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n2. 🌐 Network Connectivity:"
echo "---------------------------"
echo "Checking if services are responding..."

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|404"; then
    echo "✅ Frontend (port 3000) is responding"
else
    echo "❌ Frontend (port 3000) is not responding"
fi

# Check backend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo "✅ Backend (port 8000) is responding"
else
    echo "❌ Backend (port 8000) is not responding"
fi

# Check nginx
if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200\|404"; then
    echo "✅ Nginx (port 80) is responding"
elif curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200\|404"; then
    echo "✅ Nginx (port 8080) is responding"
else
    echo "❌ Nginx is not responding on port 80 or 8080"
fi

echo -e "\n3. 📝 Container Logs (Last 20 lines):"
echo "-------------------------------------"

echo -e "\n🔹 Frontend logs:"
docker logs --tail=20 anki-frontend 2>/dev/null || echo "No frontend container found"

echo -e "\n🔹 Backend logs:"
docker logs --tail=20 anki-backend 2>/dev/null || echo "No backend container found"

echo -e "\n🔹 Nginx logs:"
docker logs --tail=20 anki-nginx 2>/dev/null || echo "No nginx container found"

echo -e "\n4. 🔧 System Resources:"
echo "----------------------"
echo "Memory usage:"
free -h

echo -e "\nDisk usage:"
df -h /

echo -e "\nCPU load:"
uptime

echo -e "\n5. 🐳 Docker System Info:"
echo "-------------------------"
docker system df

echo -e "\n6. 🌍 External IP and Ports:"
echo "----------------------------"
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to get external IP")
echo "External IP: $EXTERNAL_IP"
echo "Your app should be accessible at:"
echo "  - http://$EXTERNAL_IP (if running on port 80)"
echo "  - http://$EXTERNAL_IP:8080 (if running on port 8080)"

echo -e "\n7. 🔍 Common Issues Check:"
echo "-------------------------"

# Check if containers are using correct networks
if docker network ls | grep -q anki; then
    echo "✅ Anki network exists"
else
    echo "❌ Anki network missing"
fi

# Check if volumes exist
if docker volume ls | grep -q anki; then
    echo "✅ Anki volumes exist"
else
    echo "⚠️  No Anki volumes found"
fi

# Check nginx configuration
if docker exec anki-nginx nginx -t 2>/dev/null; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
fi

echo -e "\n8. 🛠️  Quick Fix Commands:"
echo "-------------------------"
echo "If containers are not running, try:"
echo "  docker-compose down && docker-compose up -d"
echo ""
echo "If you see permission errors, try:"
echo "  sudo chown -R \$USER:docker /var/run/docker.sock"
echo ""
echo "If ports are blocked, check firewall:"
echo "  sudo ufw status"
echo ""
echo "To rebuild everything from scratch:"
echo "  docker-compose down -v"
echo "  docker system prune -f"
echo "  docker-compose up -d --build"

echo -e "\n✅ Troubleshooting complete!"
