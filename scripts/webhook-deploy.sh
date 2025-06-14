#!/bin/bash

# GitHub Webhook Handler
# This script can be called by a webhook to trigger deployments

set -e

# Configuration
PROJECT_DIR="/var/www/anki-japanese-app"
LOG_FILE="/var/log/anki-deploy.log"
LOCK_FILE="/tmp/anki-deploy.lock"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a $LOG_FILE
}

# Check if another deployment is running
if [ -f "$LOCK_FILE" ]; then
    log_error "Another deployment is already running. Exiting."
    exit 1
fi

# Create lock file
touch $LOCK_FILE

# Cleanup function
cleanup() {
    rm -f $LOCK_FILE
}
trap cleanup EXIT

log_info "=== Webhook deployment started ==="

# Change to project directory
cd $PROJECT_DIR

# Fetch latest changes
git fetch origin main

# Check if there are new commits
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    log_info "No new commits. Deployment skipped."
    exit 0
fi

log_info "New commits detected. Starting deployment..."

# Run deployment script
./scripts/deploy.sh

log_info "=== Webhook deployment completed ==="
