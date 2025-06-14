#!/bin/bash

# Authentication Setup for Private GitHub Repository
# Choose between SSH key or Personal Access Token

set -e

echo "🔐 GitHub Authentication Setup for Private Repository"
echo ""
echo "Choose your authentication method:"
echo "1) SSH Key (recommended for servers)"
echo "2) Personal Access Token (simpler)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔑 Setting up SSH Key Authentication"
        echo ""
        
        # Generate SSH key
        echo "Generating SSH key..."
        ssh-keygen -t ed25519 -C "mikemarre@gmail.com" -f ~/.ssh/github_vps -N ""
        
        # Add to SSH agent
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/github_vps
        
        # Display public key
        echo ""
        echo "🚨 COPY THIS PUBLIC KEY TO GITHUB:"
        echo "=================================================="
        cat ~/.ssh/github_vps.pub
        echo "=================================================="
        echo ""
        echo "Steps to add to GitHub:"
        echo "1. Go to: https://github.com/settings/ssh"
        echo "2. Click 'New SSH key'"
        echo "3. Title: 'VPS Server Key'"
        echo "4. Paste the key above"
        echo "5. Click 'Add SSH key'"
        echo ""
        read -p "Press Enter when you've added the key to GitHub..."
        
        # Test connection
        echo "Testing SSH connection..."
        if ssh -T -i ~/.ssh/github_vps git@github.com 2>&1 | grep -q "successfully authenticated"; then
            echo "✅ SSH authentication successful!"
            
            # Clone repository
            echo "Cloning repository with SSH..."
            sudo mkdir -p /var/www/anki-japanese-app
            sudo chown $USER:$USER /var/www/anki-japanese-app
            GIT_SSH_COMMAND="ssh -i ~/.ssh/github_vps" git clone git@github.com:mmmare/anki-japanese-app.git /var/www/anki-japanese-app
            
        else
            echo "❌ SSH authentication failed. Please check your key setup."
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo "🎫 Setting up Personal Access Token Authentication"
        echo ""
        echo "First, create a Personal Access Token:"
        echo "1. Go to: https://github.com/settings/tokens"
        echo "2. Click 'Generate new token (classic)'"
        echo "3. Name: 'VPS Deployment'"
        echo "4. Scopes: Check 'repo' (full control)"
        echo "5. Generate and copy the token"
        echo ""
        read -p "Enter your GitHub Personal Access Token: " -s token
        echo ""
        
        if [ -z "$token" ]; then
            echo "❌ No token provided. Exiting."
            exit 1
        fi
        
        # Clone repository with token
        echo "Cloning repository with token..."
        sudo mkdir -p /var/www/anki-japanese-app
        sudo chown $USER:$USER /var/www/anki-japanese-app
        git clone https://mmmare:$token@github.com/mmmare/anki-japanese-app.git /var/www/anki-japanese-app
        
        # Store token for future use (optional)
        read -p "Save token for future deployments? (y/n): " save_token
        if [ "$save_token" = "y" ]; then
            cd /var/www/anki-japanese-app
            git remote set-url origin https://mmmare:$token@github.com/mmmare/anki-japanese-app.git
            echo "✅ Token saved for future git operations"
        fi
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Repository cloned successfully!"
echo "📁 Location: /var/www/anki-japanese-app"
echo ""
echo "Next steps:"
echo "1. cd /var/www/anki-japanese-app"
echo "2. chmod +x scripts/*.sh"
echo "3. ./scripts/manual-setup.sh"
