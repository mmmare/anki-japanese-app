#!/bin/bash

# Public VPS Setup Script for Japanese Anki App
# This script can be run directly on your VPS

set -e

echo "🏗️ Setting up VPS for Japanese Anki App..."

# Check for sudo privileges
if sudo -n true 2>/dev/null; then
    echo "✅ User has sudo privileges"
    HAS_SUDO=true
    
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    APP_DIR="/var/www/anki-japanese-app"
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    PORT=80
else
    echo "⚠️ No sudo privileges - using user installation"
    HAS_SUDO=false
    
    # Install Docker Compose in user directory
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose in user directory..."
        mkdir -p ~/.local/bin
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o ~/.local/bin/docker-compose
        chmod +x ~/.local/bin/docker-compose
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi
    
    APP_DIR="$HOME/anki-japanese-app"
    mkdir -p $APP_DIR
    PORT=8080
fi

# Clone repository
echo "Cloning repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd $APP_DIR
    git pull
else
    echo "Please enter your GitHub Personal Access Token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Generate new token with 'repo' scope"
    echo "3. Paste token here:"
    read -s GITHUB_TOKEN
    
    if [ -n "$GITHUB_TOKEN" ]; then
        git clone https://mmmare:$GITHUB_TOKEN@github.com/mmmare/anki-japanese-app.git $APP_DIR
        cd $APP_DIR
    else
        echo "❌ No token provided. Exiting."
        exit 1
    fi
fi

# Create docker-compose override for port configuration
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  frontend:
    ports:
      - "${PORT}:80"
EOF

# Build and deploy
echo "Building and starting services..."
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check health
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️ Frontend might still be starting..."
fi

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️ Backend might still be starting..."
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "🎉 Deployment complete!"
echo "Your Japanese Anki App is running at:"
echo "   http://$PUBLIC_IP:$PORT"
echo ""
echo "Backend API is available at:"
echo "   http://$PUBLIC_IP:8000"
echo ""
echo "To check logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To restart: docker-compose restart"
