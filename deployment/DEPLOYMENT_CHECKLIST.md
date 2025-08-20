# 🚀 Hetzner Deployment Checklist for Paycrypt CCA

## Pre-Deployment Preparation

### 1. Server Setup
- [ ] Create Hetzner Cloud server (Ubuntu 22.04 LTS)
- [ ] Configure SSH key authentication
- [ ] Set up firewall rules
- [ ] Update server hostname
- [ ] Configure timezone

### 2. Domain & DNS
- [ ] Purchase/configure domain name
- [ ] Point A record to server IP
- [ ] Configure www subdomain
- [ ] Set up MX records (if needed)

### 3. Code Preparation
- [ ] Push code to Git repository
- [ ] Update repository URL in deployment script
- [ ] Create production branch (optional)
- [ ] Test application locally

## Deployment Steps

### 1. Server Access
```bash
# SSH into your Hetzner server
ssh root@your-server-ip

# Update deployment script variables
nano /path/to/deploy_hetzner.sh
```

**Update these variables:**
- `DOMAIN="yourdomain.com"`
- `EMAIL="admin@yourdomain.com"`
- `REPO_URL="https://github.com/yourusername/paycrypt-cca.git"`

### 2. Generate Environment Variables
```bash
# Run the environment generator
chmod +x deployment/generate_env.sh
./deployment/generate_env.sh
```

### 3. Run Deployment Script
```bash
# Make script executable
chmod +x deployment/deploy_hetzner.sh

# Run deployment (as root)
./deployment/deploy_hetzner.sh
```

### 4. Post-Deployment Configuration

#### Update Environment Variables
```bash
sudo -u paycrypt nano /home/paycrypt/paycrypt-cca/.env
```

**Critical settings to update:**
- Database credentials
- Admin credentials  
- Secret keys
- Domain names
- Email configuration

#### Initialize Database
```bash
cd /home/paycrypt/paycrypt-cca
sudo -u paycrypt bash
source venv/bin/activate
export FLASK_APP=run:create_app
flask db upgrade
```

#### Create Admin User
```bash
python3 -c "
from app import create_app, db
from app.models.admin import AdminUser
app = create_app()
with app.app_context():
    admin = AdminUser.create_admin(
        username='admin',
        email='admin@yourdomain.com', 
        password='your-secure-password'
    )
    db.session.commit()
    print('Admin user created successfully!')
"
```

### 5. SSL Certificate Setup
```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com --email admin@yourdomain.com --agree-tos --non-interactive

# Start nginx
sudo systemctl start nginx
```

### 6. Service Management
```bash
# Restart application
sudo supervisorctl restart paycrypt

# Check status
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
```

## Testing & Verification

### 1. Basic Functionality Tests
- [ ] Visit https://yourdomain.com
- [ ] Test admin login: https://yourdomain.com/admin/login
- [ ] Test client login: https://yourdomain.com/client/login
- [ ] Check API health: https://yourdomain.com/health
- [ ] Test API endpoints with Postman/curl

### 2. Security Tests
- [ ] SSL certificate valid (A+ rating on SSLLabs)
- [ ] HTTPS redirection working
- [ ] Security headers present
- [ ] Rate limiting functional
- [ ] Firewall configured correctly

### 3. Performance Tests
- [ ] Page load times acceptable (<2s)
- [ ] Database queries optimized
- [ ] Static files served efficiently
- [ ] Gzip compression enabled

## Monitoring & Maintenance

### 1. Set Up Monitoring
```bash
# Add health check to crontab
sudo crontab -e

# Add this line:
0 */6 * * * /home/paycrypt/paycrypt-cca/deployment/health_monitor.sh > /var/log/paycrypt_health.log 2>&1
```

### 2. Log Management
```bash
# Set up log rotation
sudo nano /etc/logrotate.d/paycrypt

# Monitor logs
sudo tail -f /home/paycrypt/paycrypt-cca/logs/supervisor.log
sudo tail -f /var/log/nginx/paycrypt_error.log
```

### 3. Backup Configuration
```bash
# Set up automated backups
sudo -u paycrypt crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/paycrypt/backup.sh
```

## Production URLs

After successful deployment, your application will be available at:

- **Main Application**: https://yourdomain.com
- **Admin Panel**: https://yourdomain.com/admin/login
- **Client Portal**: https://yourdomain.com/client/login  
- **API Base**: https://api.yourdomain.com/v1
- **Health Check**: https://yourdomain.com/health

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo tail -f /home/paycrypt/paycrypt-cca/logs/supervisor.log

# Check supervisor status
sudo supervisorctl status

# Restart application
sudo supervisorctl restart paycrypt
```

#### Database Connection Issues
```bash
# Test database connection
sudo -u paycrypt psql -h localhost -U paycrypt_user -d paycrypt_prod

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### SSL Certificate Issues
```bash
# Renew certificate manually
sudo certbot renew

# Check certificate expiry
sudo certbot certificates
```

#### Nginx Configuration Issues
```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Security Hardening

### Additional Security Measures
- [ ] Configure fail2ban
- [ ] Set up automatic security updates
- [ ] Enable log monitoring/alerting
- [ ] Regular backup testing
- [ ] Implement intrusion detection
- [ ] Set up monitoring alerts

### Regular Maintenance Tasks
- [ ] Weekly: Check logs and system health
- [ ] Monthly: Update system packages
- [ ] Monthly: Rotate API keys
- [ ] Quarterly: Security audit
- [ ] Quarterly: Backup restoration test

## Performance Optimization

### Database Optimization
- [ ] Configure PostgreSQL for production
- [ ] Set up connection pooling
- [ ] Implement query optimization
- [ ] Monitor slow queries

### Application Optimization  
- [ ] Enable Redis caching
- [ ] Configure CDN for static files
- [ ] Implement API response caching
- [ ] Monitor application metrics

## Scaling Considerations

### Horizontal Scaling
- [ ] Load balancer configuration
- [ ] Database replication
- [ ] Session store externalization
- [ ] File storage optimization

### Monitoring & Alerting
- [ ] Set up application monitoring (Prometheus/Grafana)
- [ ] Configure email/SMS alerts
- [ ] Implement log aggregation
- [ ] Monitor business metrics

---

## 🎉 Deployment Complete!

Your Paycrypt CCA application is now deployed on Hetzner and ready for production use. 

**Important**: Save all credentials securely and ensure regular backups are working before going live!
