#!/bin/bash

# Production Environment Variable Generator
# This script generates secure environment variables for production deployment

echo "🔐 Generating Production Environment Variables for Paycrypt CCA"
echo "================================================================"

# Function to generate random string
generate_secret() {
    python3 -c "import secrets; print(secrets.token_hex(32))"
}

# Function to generate JWT secret
generate_jwt_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(64))"
}

# Get domain from user
read -p "Enter your domain name (e.g., paycrypt.com): " DOMAIN
read -p "Enter your email for SSL certificate: " EMAIL
read -p "Enter admin username: " ADMIN_USER
read -s -p "Enter admin password: " ADMIN_PASS
echo

# Generate secrets
FLASK_SECRET=$(generate_secret)
JWT_SECRET=$(generate_jwt_secret)
CSRF_SECRET=$(generate_secret)

# Generate database password
DB_PASSWORD=$(generate_secret | cut -c1-16)

echo ""
echo "📋 Generated Production Environment Variables:"
echo "=============================================="

cat > .env.production << EOF
# Flask Configuration
FLASK_APP=run:create_app
ENV=production
FLASK_ENV=production
SECRET_KEY=${FLASK_SECRET}
FLASK_SECRET_KEY=${FLASK_SECRET}

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://paycrypt_user:${DB_PASSWORD}@localhost/paycrypt_prod
SQLALCHEMY_DATABASE_URI=postgresql://paycrypt_user:${DB_PASSWORD}@localhost/paycrypt_prod

# API Configuration
RATE_LIMIT=1000
PAYMENT_GATEWAY_URL=https://${DOMAIN}/api
PAYCRYPT_BASE_URL=https://api.${DOMAIN}/v1

# Admin Credentials
ADMIN_USERNAME=${ADMIN_USER}
ADMIN_PASSWORD=${ADMIN_PASS}
ADMIN_EMAIL=${EMAIL}

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ACCESS_TOKEN_EXPIRES=86400
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Security
CSRF_ENABLED=True
CSRF_SESSION_KEY=${CSRF_SECRET}

# Application Settings
FLASK_DEBUG=0
TESTING=False

# SSL/HTTPS Configuration
PREFERRED_URL_SCHEME=https
FORCE_HTTPS=True

# Session Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/paycrypt/paycrypt-cca/logs/app.log

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/home/paycrypt/paycrypt-cca/uploads

# Gunicorn Configuration
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
GUNICORN_BIND=127.0.0.1:8000

# Rate Limiting per Client Type
RATE_LIMIT_FLAT_RATE=2000
RATE_LIMIT_COMMISSION=500

# Webhook Configuration
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3

# Backup Configuration
BACKUP_DIR=/home/paycrypt/backups
BACKUP_RETENTION_DAYS=30
EOF

echo "✅ Environment file created: .env.production"
echo ""
echo "🔑 Database Setup Commands:"
echo "=========================="
echo "sudo -u postgres psql << EOF"
echo "CREATE USER paycrypt_user WITH PASSWORD '${DB_PASSWORD}';"
echo "CREATE DATABASE paycrypt_prod OWNER paycrypt_user;"
echo "GRANT ALL PRIVILEGES ON DATABASE paycrypt_prod TO paycrypt_user;"
echo "\\q"
echo "EOF"
echo ""
echo "📋 Next Steps:"
echo "============="
echo "1. Copy .env.production to your server"
echo "2. Run the database setup commands above"
echo "3. Update domain in nginx config"
echo "4. Run the deployment script"
echo ""
echo "⚠️  IMPORTANT: Save these credentials securely!"
echo "   Database Password: ${DB_PASSWORD}"
echo "   Flask Secret: ${FLASK_SECRET}"
echo "   JWT Secret: ${JWT_SECRET}"
