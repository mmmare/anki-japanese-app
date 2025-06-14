#!/bin/bash

# Simple VPS Setup for Non-Sudo Users
# Run this after you've successfully cloned the repository

echo "🚀 Simple Japanese Anki App Setup (Non-sudo version)"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the anki-japanese-app directory"
    echo "Usage: cd ~/anki-japanese-app && ./scripts/simple-setup.sh"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please ask your admin to install Docker."
    echo "Installation command: curl -fsSL https://get.docker.com | sudo sh"
    exit 1
fi

echo "✅ Docker is available"

# Install Docker Compose in user directory if needed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose in user directory..."
    mkdir -p ~/.local/bin
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o ~/.local/bin/docker-compose
    chmod +x ~/.local/bin/docker-compose
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose is available"
fi

# Create user-friendly docker-compose file (using ports that don't require sudo)
echo "Creating non-sudo docker-compose configuration..."
cp docker-compose.yml docker-compose-user.yml

# Change ports to avoid needing sudo (port 80 requires root access)
sed -i 's/"80:80"/"8080:80"/g' docker-compose-user.yml

# Create data directory
mkdir -p ~/anki-data

# Update volume mapping to user directory
sed -i 's|./data:/app/data|~/anki-data:/app/data|g' docker-compose-user.yml

echo "✅ Configuration updated for non-sudo user"

# Build and start the application
echo "Building and starting the application..."
docker-compose -f docker-compose-user.yml up --build -d

# Wait a moment for services to start
echo "Waiting for services to start..."
sleep 30

# Check status
echo "Checking application status..."
docker-compose -f docker-compose-user.yml ps

# Test if services are responding
echo "Testing application..."
if curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend is running on port 8080"
else
    echo "⚠️  Frontend may still be starting..."
fi

if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend API is running on port 8000"
else
    echo "⚠️  Backend API may still be starting..."
fi

# Get server IP for external access
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Your Japanese Anki Generator is running at:"
echo "- Frontend: http://$SERVER_IP:8080"
echo "- Backend API: http://$SERVER_IP:8000/docs"
echo ""
echo "Local access:"
echo "- Frontend: http://localhost:8080"
echo "- Backend API: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "- View logs: docker-compose -f docker-compose-user.yml logs"
echo "- Stop app: docker-compose -f docker-compose-user.yml down"
echo "- Restart app: docker-compose -f docker-compose-user.yml restart"
echo "- Update app: git pull && docker-compose -f docker-compose-user.yml up --build -d"
