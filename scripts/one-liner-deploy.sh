#!/bin/bash

# One-liner deployment command for VPS
# Usage: Copy and paste this entire command into your VPS terminal

set -e

echo "🚀 Quick deployment started..."

# Create the deployment directory and navigate to it
cd ~ && \
mkdir -p anki-japanese-app && \
cd anki-japanese-app && \

# If git repo doesn't exist, clone it (you'll need to provide token)
if [ ! -d ".git" ]; then
    echo "Repository not found. Please provide your GitHub Personal Access Token:"
    read -s GITHUB_TOKEN
    git clone https://mmmare:$GITHUB_TOKEN@github.com/mmmare/anki-japanese-app.git .
fi && \

# Pull latest changes
git pull origin main && \

# Make scripts executable
chmod +x scripts/*.sh && \

# Run the VPS deployment script
./scripts/vps-deploy.sh

echo "✅ Quick deployment complete!"
