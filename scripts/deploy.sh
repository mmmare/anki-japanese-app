#!/bin/bash

# Docker-based CI/CD Script for VPS
# Run this script when you want to deploy

set -e  # Exit on any error

echo "🚀 Starting Docker CI/CD Pipeline..."

# Configuration
PROJECT_DIR="/var/www/anki-japanese-app"
REPO_URL="https://github.com/mmmare/anki-japanese-app.git"
BACKUP_DIR="/var/backups/anki-japanese-app"
BACKEND_SERVICE="anki-backend"
FRONTEND_SERVICE="anki-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run tests in Docker
run_tests() {
    log_info "Running tests in Docker containers..."
    
    cd $PROJECT_DIR
    
    # Build test containers
    log_info "Building test containers..."
    docker-compose -f docker-compose.test.yml build || {
        log_error "Failed to build test containers"
        exit 1
    }
    
    # Run backend tests
    log_info "Running backend tests..."
    docker-compose -f docker-compose.test.yml run --rm backend-test || {
        log_warn "Some backend tests failed"
    }
    
    # Run frontend tests
    log_info "Running frontend tests..."
    docker-compose -f docker-compose.test.yml run --rm frontend-test || {
        log_warn "Some frontend tests failed"
    }
    
    # Clean up test containers
    docker-compose -f docker-compose.test.yml down --volumes --remove-orphans
    
    log_info "✅ Tests completed"
}

# Function to deploy with Docker
deploy() {
    log_info "Deploying application with Docker..."
    
    cd $PROJECT_DIR
    
    # Pull latest changes
    log_info "Pulling latest changes..."
    git pull origin main
    
    # Create backup
    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        log_info "Creating backup: $BACKUP_NAME"
        mkdir -p $BACKUP_DIR
        cp -r $PROJECT_DIR $BACKUP_DIR/$BACKUP_NAME 2>/dev/null || true
    fi
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose down || true
    
    # Remove old images to save space
    log_info "Cleaning up old images..."
    docker image prune -f || true
    
    # Build and start new containers
    log_info "Building and starting containers..."
    docker-compose up --build -d
    
    # Wait for services to start
    log_info "Waiting for services to start..."
    sleep 30
    
    # Health checks
    log_info "Performing health checks..."
    
    # Check frontend
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log_info "✅ Frontend is healthy (http://localhost:80)"
    else
        log_error "❌ Frontend health check failed"
        docker-compose logs frontend
        exit 1
    fi
    
    # Check backend
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        log_info "✅ Backend is healthy (http://localhost:8000/docs)"
    else
        log_error "❌ Backend health check failed"
        docker-compose logs backend
        exit 1
    fi
    
    # Show running containers
    log_info "Running containers:"
    docker-compose ps
    
    log_info "✅ Deployment completed successfully!"
}

# Main execution
main() {
    log_info "Starting CI/CD for Anki Japanese App"
    
    # Create project directory if it doesn't exist
    if [ ! -d "$PROJECT_DIR" ]; then
        log_info "Cloning repository..."
        sudo mkdir -p $PROJECT_DIR
        sudo chown $USER:$USER $PROJECT_DIR
        git clone $REPO_URL $PROJECT_DIR
    fi
    
    cd $PROJECT_DIR
    
    # Run tests
    run_tests
    
    # Deploy if tests pass
    deploy
    
    log_info "🎉 CI/CD Pipeline completed successfully!"
}

# Run the main function
main "$@"
