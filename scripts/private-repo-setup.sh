#!/bin/bash

# Private Repository VPS Setup Script
# This script helps set up deployment for a private GitHub repository

set -e

echo "🔐 Setting up private GitHub repository on VPS..."

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

# Configuration
REPO_URL="https://github.com/mmmare/anki-japanese-app.git"
APP_DIR="/var/www/anki-japanese-app"
BACKUP_DIR="/var/backups/anki-japanese-app"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

log_info "Private GitHub Repository Setup"
echo "Repository: $REPO_URL"
echo "Installation directory: $APP_DIR"
echo ""

# Ask for authentication method
echo "Choose authentication method:"
echo "1) Personal Access Token (recommended for automation)"
echo "2) SSH Key (more secure for manual access)"
echo "3) GitHub CLI (interactive)"
read -p "Enter choice (1-3): " auth_method

case $auth_method in
    1)
        # Personal Access Token method
        log_info "Setting up with Personal Access Token..."
        echo ""
        log_warn "You need to create a Personal Access Token first:"
        echo "1. Go to: https://github.com/settings/tokens"
        echo "2. Click 'Generate new token (classic)'"
        echo "3. Select 'repo' scope for private repositories"
        echo "4. Copy the generated token"
        echo ""
        read -p "Enter your GitHub username: " github_username
        read -s -p "Enter your Personal Access Token: " github_token
        echo ""
        
        # Create authenticated URL
        AUTH_URL="https://${github_username}:${github_token}@github.com/mmmare/anki-japanese-app.git"
        
        # Create directories
        log_info "Creating directories..."
        sudo mkdir -p $APP_DIR $BACKUP_DIR
        sudo chown $USER:$USER $APP_DIR $BACKUP_DIR
        
        # Clone repository
        log_info "Cloning private repository..."
        if [ -d "$APP_DIR/.git" ]; then
            cd $APP_DIR
            git remote set-url origin $AUTH_URL
            git pull origin main
        else
            git clone $AUTH_URL $APP_DIR
        fi
        ;;
        
    2)
        # SSH Key method
        log_info "Setting up with SSH Key..."
        
        # Generate SSH key if it doesn't exist
        if [ ! -f ~/.ssh/github_vps ]; then
            log_info "Generating SSH key..."
            read -p "Enter your email for SSH key: " email
            ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/github_vps -N ""
        fi
        
        # Add to SSH agent
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/github_vps
        
        # Display public key
        echo ""
        log_warn "Add this SSH public key to your GitHub account:"
        echo "Go to: https://github.com/settings/ssh/new"
        echo ""
        cat ~/.ssh/github_vps.pub
        echo ""
        read -p "Press Enter after adding the SSH key to GitHub..."
        
        # Test SSH connection
        log_info "Testing SSH connection..."
        ssh -T git@github.com || true
        
        # Create directories
        log_info "Creating directories..."
        sudo mkdir -p $APP_DIR $BACKUP_DIR
        sudo chown $USER:$USER $APP_DIR $BACKUP_DIR
        
        # Clone repository
        log_info "Cloning private repository..."
        SSH_URL="git@github.com:mmmare/anki-japanese-app.git"
        if [ -d "$APP_DIR/.git" ]; then
            cd $APP_DIR
            git remote set-url origin $SSH_URL
            git pull origin main
        else
            git clone $SSH_URL $APP_DIR
        fi
        ;;
        
    3)
        # GitHub CLI method
        log_info "Setting up with GitHub CLI..."
        
        # Install GitHub CLI if not present
        if ! command -v gh &> /dev/null; then
            log_info "Installing GitHub CLI..."
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install gh
        fi
        
        # Authenticate
        log_info "Authenticating with GitHub..."
        gh auth login
        
        # Create directories
        log_info "Creating directories..."
        sudo mkdir -p $APP_DIR $BACKUP_DIR
        sudo chown $USER:$USER $APP_DIR $BACKUP_DIR
        
        # Clone repository
        log_info "Cloning private repository..."
        if [ -d "$APP_DIR/.git" ]; then
            cd $APP_DIR
            gh repo sync
        else
            gh repo clone mmmare/anki-japanese-app $APP_DIR
        fi
        ;;
        
    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac

# Verify clone was successful
if [ ! -d "$APP_DIR/.git" ]; then
    log_error "Repository clone failed"
    exit 1
fi

cd $APP_DIR

# Make scripts executable
log_info "Making scripts executable..."
chmod +x scripts/*.sh

# Continue with standard setup
log_info "Continuing with application setup..."

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
log_info "Installing required packages..."
sudo apt install -y curl wget git nginx ufw htop unzip software-properties-common

# Verify Docker
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    log_warn "Please log out and log back in to use Docker without sudo"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Configure firewall
log_info "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable

# Deploy application
log_info "Deploying application..."
./scripts/deploy.sh

log_info "✅ Private repository setup complete!"
log_info ""
log_info "Your app should be running at:"
log_info "- Frontend: http://$(curl -s ifconfig.me || echo 'your-server-ip')"
log_info "- Backend: http://$(curl -s ifconfig.me || echo 'your-server-ip'):8000/docs"
log_info ""
log_info "To update the application:"
log_info "cd $APP_DIR && git pull && ./scripts/deploy.sh"
