#!/bin/bash

# VPS Setup Script for CI/CD
# Run this once on your VPS to set up the environment

set -e

echo "🏗️  Setting up VPS for Japanese Anki App CI/CD..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
log_info "Installing required packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    nginx \
    ufw \
    htop \
    unzip \
    software-properties-common

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    log_info "Docker is already installed"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log_info "Docker Compose is already installed"
fi

# Create application directory
APP_DIR="/var/www/anki-japanese-app"
BACKUP_DIR="/var/backups/anki-japanese-app"

log_info "Creating application directories..."
sudo mkdir -p $APP_DIR
sudo mkdir -p $BACKUP_DIR
sudo chown $USER:$USER $APP_DIR
sudo chown $USER:$USER $BACKUP_DIR

# Clone repository if it doesn't exist
if [ ! -d "$APP_DIR/.git" ]; then
    log_info "Cloning repository..."
    git clone https://github.com/mmmare/anki-japanese-app.git $APP_DIR
else
    log_info "Repository already exists"
fi

# Make deploy script executable
chmod +x $APP_DIR/scripts/deploy.sh

# Configure firewall
log_info "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Backend API (optional, for direct access)
sudo ufw --force enable

# Configure nginx (optional - if you want to use nginx as reverse proxy)
log_info "Setting up nginx configuration..."
sudo tee /etc/nginx/sites-available/anki-japanese-app > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site (optional)
sudo ln -sf /etc/nginx/sites-available/anki-japanese-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Create systemd service for auto-deployment (optional)
log_info "Creating deployment service..."
sudo tee /etc/systemd/system/anki-deploy.service > /dev/null <<EOF
[Unit]
Description=Anki Japanese App Deployment
After=docker.service

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/scripts/deploy.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable anki-deploy.service

# Create cron job for automatic deployments (optional)
log_info "Setting up cron job for automatic deployments..."
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/scripts/deploy.sh >> /var/log/anki-deploy.log 2>&1") | crontab -

# Initial deployment
log_info "Running initial deployment..."
cd $APP_DIR
./scripts/deploy.sh

log_info "🎉 VPS setup completed!"
log_info ""
log_info "Next steps:"
log_info "1. Update your domain in /etc/nginx/sites-available/anki-japanese-app"
log_info "2. Set up SSL with Let's Encrypt: sudo certbot --nginx"
log_info "3. Configure GitHub webhook for auto-deployment (optional)"
log_info ""
log_info "Your app should be running at:"
log_info "- Frontend: http://$(curl -s ifconfig.me)"
log_info "- Backend API: http://$(curl -s ifconfig.me):8000/docs"
log_info ""
log_info "To deploy manually: cd $APP_DIR && ./scripts/deploy.sh"
