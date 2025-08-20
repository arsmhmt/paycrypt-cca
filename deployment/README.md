# Paycrypt CCA - Production Deployment Guide for Hetzner

## Server Requirements
- **OS**: Ubuntu 22.04 LTS
- **RAM**: Minimum 2GB (Recommended 4GB+)
- **Storage**: Minimum 20GB SSD
- **CPU**: 2+ cores recommended

## Pre-deployment Checklist

### 1. Domain Setup
- Point your domain to Hetzner server IP
- Configure DNS A records
- Set up SSL certificate (Let's Encrypt)

### 2. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash paycrypt
sudo usermod -aG sudo paycrypt
```

### 3. Application Setup
```bash
# Switch to paycrypt user
sudo su - paycrypt

# Clone repository
git clone <your-repo-url> /home/paycrypt/paycrypt-cca
cd /home/paycrypt/paycrypt-cca

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration Files

### Environment Variables (.env.production)
- Database: PostgreSQL (recommended) or SQLite
- Security: Strong secrets and keys
- SSL: Force HTTPS in production
- Logging: Configure proper logging levels

### Nginx Configuration
- Reverse proxy to Gunicorn
- SSL termination
- Static file serving
- Rate limiting

### Supervisor Configuration
- Process management
- Auto-restart on failure
- Logging configuration

## Database Migration
- Backup existing data
- Set up production database
- Run migrations
- Verify data integrity

## Security Hardening
- Firewall configuration (UFW)
- SSH key authentication
- Fail2Ban setup
- Regular security updates

## Monitoring & Logging
- Application logs
- Nginx access/error logs
- System monitoring
- Database monitoring

## Backup Strategy
- Database backups
- Application files backup
- Configuration backup
- Automated backup scheduling

## SSL Certificate
- Let's Encrypt setup
- Auto-renewal configuration
- HTTPS redirection

Next steps: Would you like me to create specific configuration files for any of these components?
