#!/bin/bash

# Hetzner Deployment Script for Paycrypt CCA
# Run this script on your Hetzner server as root

set -e  # Exit on any error

echo "🚀 Starting Paycrypt CCA deployment on Hetzner..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"
APP_USER="paycrypt"
APP_DIR="/home/paycrypt/paycrypt-cca"
REPO_URL="https://github.com/yourusername/paycrypt-cca.git"  # Update this

echo -e "${BLUE}📋 Please update the following before running:${NC}"
echo -e "${YELLOW}  - DOMAIN: $DOMAIN${NC}"
echo -e "${YELLOW}  - EMAIL: $EMAIL${NC}"
echo -e "${YELLOW}  - REPO_URL: $REPO_URL${NC}"
echo ""
read -p "Have you updated the configuration above? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please update the configuration and run again.${NC}"
    exit 1
fi

# Update system
echo -e "${BLUE}🔄 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
apt install -y python3 python3-pip python3-venv python3-dev \
    nginx supervisor git certbot python3-certbot-nginx \
    postgresql postgresql-contrib libpq-dev \
    redis-server ufw fail2ban htop \
    build-essential curl wget unzip

# Configure firewall
echo -e "${BLUE}🔥 Configuring firewall...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Create application user
echo -e "${BLUE}👤 Creating application user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    usermod -aG sudo $APP_USER
    echo "$APP_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$APP_USER
fi

# Set up PostgreSQL
echo -e "${BLUE}🐘 Setting up PostgreSQL...${NC}"
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER paycrypt_user WITH PASSWORD 'secure_password_change_me';
CREATE DATABASE paycrypt_prod OWNER paycrypt_user;
GRANT ALL PRIVILEGES ON DATABASE paycrypt_prod TO paycrypt_user;
\q
EOF

# Clone repository as application user
echo -e "${BLUE}📥 Cloning repository...${NC}"
sudo -u $APP_USER bash << EOF
cd /home/$APP_USER
if [ -d "$APP_DIR" ]; then
    rm -rf $APP_DIR
fi
git clone $REPO_URL $APP_DIR
cd $APP_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install gunicorn psycopg2-binary
pip install -r requirements.txt
EOF

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
sudo -u $APP_USER mkdir -p $APP_DIR/logs
sudo -u $APP_USER mkdir -p $APP_DIR/instance
sudo -u $APP_USER mkdir -p $APP_DIR/uploads
sudo -u $APP_USER mkdir -p /home/$APP_USER/backups

# Copy configuration files
echo -e "${BLUE}⚙️  Setting up configuration...${NC}"
cp $APP_DIR/deployment/.env.production $APP_DIR/.env
cp $APP_DIR/deployment/supervisor/paycrypt.conf /etc/supervisor/conf.d/
cp $APP_DIR/deployment/nginx/paycrypt.conf /etc/nginx/sites-available/paycrypt

# Update domain in nginx config
sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/paycrypt

# Enable nginx site
ln -sf /etc/nginx/sites-available/paycrypt /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Initialize database
echo -e "${BLUE}💾 Initializing database...${NC}"
sudo -u $APP_USER bash << EOF
cd $APP_DIR
source venv/bin/activate
export FLASK_APP=run:create_app
flask db init || true
flask db migrate -m "Initial migration" || true
flask db upgrade
EOF

# Set up SSL certificate
echo -e "${BLUE}🔐 Setting up SSL certificate...${NC}"
systemctl stop nginx
certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
systemctl start nginx

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
systemctl reload supervisor
supervisorctl reread
supervisorctl update
supervisorctl start paycrypt
systemctl reload nginx

# Set up automatic SSL renewal
echo -e "${BLUE}🔄 Setting up SSL auto-renewal...${NC}"
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

# Set up log rotation
echo -e "${BLUE}📋 Setting up log rotation...${NC}"
cat > /etc/logrotate.d/paycrypt << EOF
$APP_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $APP_USER $APP_USER
    postrotate
        supervisorctl restart paycrypt
    endscript
}
EOF

# Set up fail2ban
echo -e "${BLUE}🛡️  Configuring fail2ban...${NC}"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Create backup script
echo -e "${BLUE}💾 Setting up backup script...${NC}"
cat > /home/$APP_USER/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/paycrypt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U paycrypt_user -h localhost paycrypt_prod > $BACKUP_DIR/db_$DATE.sql

# Application files backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C /home/paycrypt paycrypt-cca --exclude=paycrypt-cca/venv --exclude=paycrypt-cca/logs

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/$APP_USER/backup.sh
chown $APP_USER:$APP_USER /home/$APP_USER/backup.sh

# Set up daily backups
echo "0 2 * * * /home/$APP_USER/backup.sh" | sudo -u $APP_USER crontab -

# Create update script
echo -e "${BLUE}🔄 Creating update script...${NC}"
cat > /home/$APP_USER/update.sh << 'EOF'
#!/bin/bash
cd /home/paycrypt/paycrypt-cca
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
supervisorctl restart paycrypt
systemctl reload nginx
echo "Application updated successfully!"
EOF

chmod +x /home/$APP_USER/update.sh
chown $APP_USER:$APP_USER /home/$APP_USER/update.sh

# Final status check
echo -e "${BLUE}🔍 Checking service status...${NC}"
systemctl status nginx --no-pager -l
supervisorctl status paycrypt

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "${YELLOW}  1. Update $APP_DIR/.env with your actual configuration${NC}"
echo -e "${YELLOW}  2. Update database credentials in .env${NC}"
echo -e "${YELLOW}  3. Create admin user: cd $APP_DIR && source venv/bin/activate && python -c 'from app.models import AdminUser; AdminUser.create_admin()'${NC}"
echo -e "${YELLOW}  4. Test your application at https://$DOMAIN${NC}"
echo -e "${YELLOW}  5. Set up monitoring and alerting${NC}"
echo ""
echo -e "${BLUE}📁 Important files:${NC}"
echo -e "${YELLOW}  - Application: $APP_DIR${NC}"
echo -e "${YELLOW}  - Logs: $APP_DIR/logs/${NC}"
echo -e "${YELLOW}  - Nginx config: /etc/nginx/sites-available/paycrypt${NC}"
echo -e "${YELLOW}  - Supervisor config: /etc/supervisor/conf.d/paycrypt.conf${NC}"
echo -e "${YELLOW}  - SSL certs: /etc/letsencrypt/live/$DOMAIN/${NC}"
echo ""
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo -e "${YELLOW}  - Restart app: supervisorctl restart paycrypt${NC}"
echo -e "${YELLOW}  - Check logs: tail -f $APP_DIR/logs/supervisor.log${NC}"
echo -e "${YELLOW}  - Update app: /home/$APP_USER/update.sh${NC}"
echo -e "${YELLOW}  - Backup: /home/$APP_USER/backup.sh${NC}"
echo ""
echo -e "${GREEN}🎉 Your Paycrypt CCA is now deployed on Hetzner!${NC}"
