#!/bin/bash

echo "🔐 GitHub Actions VPS Deployment Setup Guide"
echo "=============================================="
echo ""
echo "This script will help you configure GitHub Actions to automatically deploy to your VPS"
echo "when you push code to the main branch."
echo ""

# Get VPS information
echo "📝 VPS Information Setup"
echo "========================"
echo ""

read -p "🌐 Enter your VPS IP address: " VPS_IP
read -p "👤 Enter your VPS username (e.g., appadmin): " VPS_USER
read -p "🔌 Enter SSH port (press Enter for default 22): " VPS_PORT
VPS_PORT=${VPS_PORT:-22}

echo ""
echo "🔑 SSH Key Setup"
echo "================"
echo ""

# Check if SSH key exists
SSH_KEY_PATH="$HOME/.ssh/id_rsa"
if [ -f "$SSH_KEY_PATH" ]; then
    echo "✅ SSH key found at $SSH_KEY_PATH"
    echo ""
    echo "📋 Your SSH public key (copy this to your VPS ~/.ssh/authorized_keys):"
    echo "----------------------------------------------------------------------"
    cat "$SSH_KEY_PATH.pub"
    echo "----------------------------------------------------------------------"
else
    echo "❌ SSH key not found. Generating a new one..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N ""
    echo ""
    echo "✅ SSH key generated!"
    echo ""
    echo "📋 Your SSH public key (copy this to your VPS ~/.ssh/authorized_keys):"
    echo "----------------------------------------------------------------------"
    cat "$SSH_KEY_PATH.pub"
    echo "----------------------------------------------------------------------"
fi

echo ""
echo "🔐 GitHub Secrets Configuration"
echo "==============================="
echo ""
echo "You need to add these secrets to your GitHub repository:"
echo "Go to: https://github.com/mmmare/anki-japanese-app/settings/secrets/actions"
echo ""

echo "1️⃣ VPS_HOST"
echo "   Value: $VPS_IP"
echo ""

echo "2️⃣ VPS_USERNAME" 
echo "   Value: $VPS_USER"
echo ""

echo "3️⃣ VPS_PORT"
echo "   Value: $VPS_PORT"
echo ""

echo "4️⃣ VPS_SSH_KEY"
echo "   Value: (copy the PRIVATE key content below)"
echo "   =========================================="
cat "$SSH_KEY_PATH"
echo "   =========================================="
echo ""

echo "📋 Setup Instructions"
echo "====================="
echo ""
echo "1. Copy your SSH public key to your VPS:"
echo "   ssh-copy-id -i $SSH_KEY_PATH.pub $VPS_USER@$VPS_IP"
echo "   OR manually add it to ~/.ssh/authorized_keys on your VPS"
echo ""
echo "2. Test SSH connection:"
echo "   ssh -i $SSH_KEY_PATH $VPS_USER@$VPS_IP -p $VPS_PORT"
echo ""
echo "3. Add the GitHub secrets listed above to:"
echo "   https://github.com/mmmare/anki-japanese-app/settings/secrets/actions"
echo ""
echo "4. Push a commit to the main branch to trigger deployment!"
echo ""

echo "🚀 Automated Deployment Process"
echo "==============================="
echo ""
echo "Once configured, every push to main branch will:"
echo "✅ Run tests"
echo "✅ Build Docker images"
echo "✅ SSH into your VPS"
echo "✅ Pull latest code"
echo "✅ Deploy the application"
echo "✅ Run health checks"
echo ""
echo "Your app will be automatically updated at: http://$VPS_IP"
echo ""

echo "🛠️ Quick VPS Setup Commands"
echo "==========================="
echo ""
echo "If you haven't set up your VPS yet, run these commands on your VPS:"
echo ""
echo "# Install dependencies"
echo "curl -fsSL https://get.docker.com | sudo sh"
echo "sudo usermod -aG docker $VPS_USER"
echo ""
echo "# Clone repository"
echo "git clone https://github.com/mmmare/anki-japanese-app.git ~/anki-japanese-app"
echo "cd ~/anki-japanese-app"
echo ""
echo "# Initial deployment"
echo "./scripts/deploy.sh"
echo ""

echo "✅ Setup guide complete!"
echo ""
echo "⚡ Quick Test: After setting up GitHub secrets, make a small change to README.md"
echo "   and push to main branch. GitHub Actions will automatically deploy to your VPS!"
