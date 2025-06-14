#!/bin/bash

# Quick Docker Deployment
# Minimal setup to get the app running

set -e

echo "🚀 Quick Docker Deployment for Japanese Anki App"

# Clone repository
git clone https://github.com/mmmare/anki-japanese-app.git
cd anki-japanese-app

# Build and run with Docker Compose
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Health check
echo "Performing health checks..."
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Frontend is running: http://localhost:80"
else
    echo "❌ Frontend health check failed"
fi

if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is running: http://localhost:8000/docs"
else
    echo "❌ Backend health check failed"
fi

echo "🎉 Deployment complete!"
echo "Access your app at http://$(curl -s ifconfig.me)"
