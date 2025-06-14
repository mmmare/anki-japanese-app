#!/bin/bash

# Manual VPS Setup Commands
# Run these commands one by one on your VPS

echo "🏗️ Manual VPS Setup for Japanese Anki App (Non-sudo version)"

# Check if user has sudo privileges
if sudo -n true 2>/dev/null; then
    echo "✅ User has sudo privileges"
    HAS_SUDO=true
    
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install required packages
    sudo apt install -y curl wget git nginx ufw htop unzip software-properties-common
else
    echo "⚠️  User does not have sudo privileges - skipping system updates"
    echo "Please ask your system administrator to install: curl wget git"
    HAS_SUDO=false
fi

# Verify Docker is installed
if ! command -v docker &> /dev/null; then
    if [ "$HAS_SUDO" = true ]; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    else
        echo "⚠️  Docker not found. Please ask admin to install Docker."
        echo "Installation command: curl -fsSL https://get.docker.com | sudo sh"
        exit 1
    fi
else
    echo "✅ Docker is already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    if [ "$HAS_SUDO" = true ]; then
        echo "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        echo "⚠️  Docker Compose not found. Installing in user directory..."
        mkdir -p ~/.local/bin
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o ~/.local/bin/docker-compose
        chmod +x ~/.local/bin/docker-compose
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi
else
    echo "✅ Docker Compose is already installed"
fi

# Create directories (in user's home if no sudo)
if [ "$HAS_SUDO" = true ]; then
    sudo mkdir -p /var/www/anki-japanese-app
    sudo mkdir -p /var/backups/anki-japanese-app
    sudo chown $USER:$USER /var/www/anki-japanese-app
    sudo chown $USER:$USER /var/backups/anki-japanese-app
    APP_DIR="/var/www/anki-japanese-app"
    BACKUP_DIR="/var/backups/anki-japanese-app"
else
    echo "Creating directories in user home..."
    mkdir -p ~/anki-japanese-app
    mkdir -p ~/anki-backups
    APP_DIR="$HOME/anki-japanese-app"
    BACKUP_DIR="$HOME/anki-backups"
fi

echo "App directory: $APP_DIR"
echo "Backup directory: $BACKUP_DIR"

# Clone repository - try SSH first, fallback to HTTPS with token
echo "Attempting to clone repository..."
if git clone git@github.com:mmmare/anki-japanese-app.git $APP_DIR 2>/dev/null; then
    echo "✅ Cloned successfully with SSH"
else
    echo "❌ SSH failed. Please provide GitHub Personal Access Token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Generate new token with 'repo' scope"
    echo "3. Copy the token and paste it here:"
    read -s GITHUB_TOKEN
    
    if [ -n "$GITHUB_TOKEN" ]; then
        git clone https://mmmare:$GITHUB_TOKEN@github.com/mmmare/anki-japanese-app.git $APP_DIR
        echo "✅ Cloned successfully with token"
    else
        echo "❌ No token provided. Exiting."
        exit 1
    fi
fi

cd $APP_DIR

# Make scripts executable
chmod +x scripts/*.sh

# Configure firewall (only if sudo available)
if [ "$HAS_SUDO" = true ]; then
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8000/tcp
    sudo ufw --force enable
else
    echo "⚠️  Skipping firewall configuration (requires sudo)"
    echo "Please ask admin to open ports: 22, 80, 443, 8000"
fi

# Deploy application
./scripts/deploy.sh

echo "✅ Setup complete!"
echo "Your app should be running at http://$(curl -s ifconfig.me)"
