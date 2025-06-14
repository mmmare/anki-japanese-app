# CI/CD Setup Guide for Japanese Anki Generator

This guide explains how to set up Continuous Integration and Continuous Deployment (CI/CD) for the Japanese Anki Generator on your VPS using Docker.

## 🏗️ Architecture Overview

Our CI/CD pipeline uses:
- **Docker** for containerization
- **GitHub Actions** for automated testing and building
- **Self-hosted runner** on VPS for deployment
- **Docker Compose** for orchestration
- **Nginx** for reverse proxy (optional)

## 📋 Prerequisites

- **VPS** with Ubuntu 20.04+ or similar
- **Docker** installed on VPS
- **GitHub repository** with admin access
- **Domain name** (optional but recommended)

## 🚀 Quick Setup

### Step 1: Initial VPS Setup

SSH into your VPS and run the setup script:

```bash
# Download and run the VPS setup script
curl -sSL https://raw.githubusercontent.com/mmmare/anki-japanese-app/main/scripts/setup-vps.sh | bash
```

Or manually:

```bash
# Clone repository
git clone https://github.com/mmmare/anki-japanese-app.git /var/www/anki-japanese-app
cd /var/www/anki-japanese-app

# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup-vps.sh
```

### Step 2: Configure GitHub Actions Runner

1. Go to your GitHub repository: `https://github.com/mmmare/anki-japanese-app`
2. Navigate to **Settings** → **Actions** → **Runners**
3. Click **New self-hosted runner**
4. Follow the instructions to download and configure the runner on your VPS

```bash
# On your VPS
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure (replace TOKEN with your actual token)
./config.sh --url https://github.com/mmmare/anki-japanese-app --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

## 🔄 CI/CD Pipeline

### Automated Workflow

The pipeline triggers on:
- **Push to main branch** → Full CI/CD (test → build → deploy)
- **Pull requests** → Testing only
- **Manual trigger** → Full CI/CD

### Pipeline Stages

1. **Test Stage**
   - Backend: Python tests with pytest
   - Frontend: TypeScript check, build test
   - Runs in parallel for faster execution

2. **Build Stage** (main branch only)
   - Builds Docker images
   - Pushes to GitHub Container Registry
   - Uses layer caching for efficiency

3. **Deploy Stage** (main branch only)
   - Pulls latest images on VPS
   - Updates containers with zero-downtime
   - Performs health checks
   - Automatic rollback on failure

## 🐳 Docker Configuration

### Services

- **Backend**: FastAPI server on port 8000
- **Frontend**: React app served by Nginx on port 80
- **Database**: In-memory storage (can be extended)

### Images

- `ghcr.io/mmmare/anki-japanese-app-backend:main`
- `ghcr.io/mmmare/anki-japanese-app-frontend:main`

### Local Development

```bash
# Start development environment
docker-compose up --build

# Run tests
docker-compose -f docker-compose.test.yml up --build

# View logs
docker-compose logs backend
docker-compose logs frontend
```

## 📊 Monitoring and Logs

### Health Checks

- **Frontend**: `http://your-vps-ip/`
- **Backend API**: `http://your-vps-ip:8000/docs`

### Log Locations

- **Application logs**: `docker-compose logs`
- **Deployment logs**: `/var/log/anki-deploy.log`
- **System logs**: `/var/log/syslog`

### Container Status

```bash
# Check running containers
docker-compose ps

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Container stats
docker stats
```

## 🔧 Manual Operations

### Manual Deployment

```bash
# SSH to VPS
ssh user@your-vps-ip

# Navigate to project
cd /var/www/anki-japanese-app

# Deploy latest changes
./scripts/deploy.sh
```

### Rollback

```bash
# View available backups
ls -la /var/backups/anki-japanese-app/

# Rollback to specific backup
cd /var/backups/anki-japanese-app/backup-YYYYMMDD-HHMMSS
docker-compose up -d
```

### Update Configuration

```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Restart services
docker-compose down
docker-compose up -d
```

## 🔐 Security

### Firewall Rules

```bash
# Check firewall status
sudo ufw status

# Allow required ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### SSL/HTTPS Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Troubleshooting

### Common Issues

**1. Container fails to start**
```bash
# Check logs
docker-compose logs backend

# Check resources
docker system df
docker system prune -f
```

**2. GitHub Actions failing**
```bash
# Check runner status
sudo ./svc.sh status

# Restart runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

**3. Port conflicts**
```bash
# Check what's using ports
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# Kill conflicting processes
sudo fuser -k 80/tcp
```

**4. Disk space issues**
```bash
# Clean Docker
docker system prune -a -f
docker volume prune -f

# Clean old backups
find /var/backups/anki-japanese-app -type d -mtime +30 -delete
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
./scripts/deploy.sh

# Run containers in foreground
docker-compose up --no-deps backend
```

## 📈 Performance Optimization

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

### Caching

- **Docker layer caching** in GitHub Actions
- **Nginx static file caching**
- **Browser caching** with proper headers

## 🔄 Webhook Auto-Deployment

For automatic deployments on git push:

```bash
# Setup webhook endpoint
sudo apt install webhook

# Configure webhook
sudo nano /etc/webhook.conf

# Start webhook service
sudo systemctl enable webhook
sudo systemctl start webhook
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Review health checks: `curl -f http://localhost/health`
3. Verify GitHub Actions: Check the Actions tab in your repository
4. Manual deployment: `./scripts/deploy.sh`

---

**Next Steps:**
1. Set up your VPS with the setup script
2. Configure GitHub Actions runner
3. Push changes to trigger your first deployment
4. Set up SSL certificates for production
5. Configure monitoring and alerts
