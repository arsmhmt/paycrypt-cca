#!/bin/bash

# Monitoring and Maintenance Script for Paycrypt CCA
# Run this script regularly to monitor application health

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_DIR="/home/paycrypt/paycrypt-cca"
LOG_DIR="$APP_DIR/logs"

echo -e "${BLUE}🔍 Paycrypt CCA Health Check Report${NC}"
echo -e "${BLUE}===================================${NC}"
echo "Generated: $(date)"
echo ""

# Check system resources
echo -e "${BLUE}💻 System Resources:${NC}"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"
echo ""

# Check services
echo -e "${BLUE}🚀 Service Status:${NC}"
services=("nginx" "postgresql" "supervisor")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo -e "  ✅ $service: ${GREEN}Running${NC}"
    else
        echo -e "  ❌ $service: ${RED}Stopped${NC}"
    fi
done

# Check application status
echo ""
echo -e "${BLUE}📱 Application Status:${NC}"
if supervisorctl status paycrypt | grep -q "RUNNING"; then
    echo -e "  ✅ Paycrypt App: ${GREEN}Running${NC}"
else
    echo -e "  ❌ Paycrypt App: ${RED}Stopped${NC}"
fi

# Check SSL certificate
echo ""
echo -e "${BLUE}🔐 SSL Certificate:${NC}"
if [ -f "/etc/letsencrypt/live/$(hostname -f)/fullchain.pem" ]; then
    cert_expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$(hostname -f)/fullchain.pem | cut -d= -f2)
    echo "  ✅ Certificate expires: $cert_expiry"
else
    echo -e "  ❌ ${RED}SSL certificate not found${NC}"
fi

# Check database
echo ""
echo -e "${BLUE}🐘 Database Status:${NC}"
if sudo -u postgres psql -c "\l" > /dev/null 2>&1; then
    echo -e "  ✅ PostgreSQL: ${GREEN}Connected${NC}"
    db_size=$(sudo -u postgres psql -d paycrypt_prod -c "SELECT pg_size_pretty(pg_database_size('paycrypt_prod'));" -t | xargs)
    echo "  📊 Database size: $db_size"
    
    # Check table sizes
    echo "  📋 Largest tables:"
    sudo -u postgres psql -d paycrypt_prod -c "
    SELECT schemaname,tablename,pg_size_pretty(size) as size_pretty
    FROM (
        SELECT schemaname,tablename,pg_total_relation_size(schemaname||'.'||tablename) as size
        FROM pg_tables WHERE schemaname NOT IN ('information_schema','pg_catalog')
    ) t ORDER BY size DESC LIMIT 5;
    " -t | head -5 | while read line; do
        echo "    $line"
    done
else
    echo -e "  ❌ PostgreSQL: ${RED}Connection failed${NC}"
fi

# Check logs for errors
echo ""
echo -e "${BLUE}📋 Recent Errors (last 24 hours):${NC}"
if [ -f "$LOG_DIR/supervisor.log" ]; then
    error_count=$(grep -i "error\|exception\|traceback" "$LOG_DIR/supervisor.log" | wc -l)
    echo "  Application errors: $error_count"
fi

if [ -f "/var/log/nginx/paycrypt_error.log" ]; then
    nginx_errors=$(grep "$(date --date='1 day ago' '+%Y/%m/%d')" /var/log/nginx/paycrypt_error.log | wc -l)
    echo "  Nginx errors: $nginx_errors"
fi

# Check disk space
echo ""
echo -e "${BLUE}💾 Disk Usage:${NC}"
df -h | grep -E '^/dev/' | awk '{print "  " $1 ": " $5 " used (" $4 " free)"}'

# Check backup status
echo ""
echo -e "${BLUE}💼 Backup Status:${NC}"
if [ -d "/home/paycrypt/backups" ]; then
    latest_backup=$(ls -t /home/paycrypt/backups/*.sql.gz 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        backup_date=$(stat -c %y "$latest_backup" | cut -d' ' -f1)
        echo "  ✅ Latest backup: $backup_date"
    else
        echo -e "  ❌ ${RED}No backups found${NC}"
    fi
else
    echo -e "  ❌ ${RED}Backup directory not found${NC}"
fi

# Check network connectivity
echo ""
echo -e "${BLUE}🌐 Network Connectivity:${NC}"
if ping -c 1 google.com > /dev/null 2>&1; then
    echo -e "  ✅ Internet: ${GREEN}Connected${NC}"
else
    echo -e "  ❌ Internet: ${RED}Disconnected${NC}"
fi

# Check application endpoint
echo ""
echo -e "${BLUE}🔗 Application Health:${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "  ✅ Health endpoint: ${GREEN}Responding${NC}"
else
    echo -e "  ❌ Health endpoint: ${RED}Not responding${NC}"
fi

# Performance metrics
echo ""
echo -e "${BLUE}⚡ Performance Metrics:${NC}"
if [ -f "$LOG_DIR/gunicorn_access.log" ]; then
    # Response times (last 1000 requests)
    avg_response=$(tail -1000 "$LOG_DIR/gunicorn_access.log" | awk '{print $NF}' | awk '{sum+=$1; n++} END {if(n>0) print sum/n; else print 0}')
    echo "  Average response time: ${avg_response}ms"
    
    # Request count (last hour)
    hour_ago=$(date -d '1 hour ago' '+%d/%b/%Y:%H')
    requests_last_hour=$(grep "$hour_ago" "$LOG_DIR/gunicorn_access.log" 2>/dev/null | wc -l)
    echo "  Requests last hour: $requests_last_hour"
fi

echo ""
echo -e "${BLUE}🔧 Maintenance Suggestions:${NC}"

# Check log sizes
log_size=$(du -sh $LOG_DIR 2>/dev/null | cut -f1)
echo "  Log directory size: $log_size"

# Check for large log files
find $LOG_DIR -name "*.log" -size +100M 2>/dev/null | while read logfile; do
    echo -e "  ⚠️  Large log file: $logfile"
done

# Check system updates
if [ -f /var/run/reboot-required ]; then
    echo -e "  ⚠️  ${YELLOW}System reboot required${NC}"
fi

updates=$(apt list --upgradable 2>/dev/null | wc -l)
if [ $updates -gt 1 ]; then
    echo -e "  ⚠️  ${YELLOW}$((updates-1)) package updates available${NC}"
fi

echo ""
echo -e "${GREEN}✅ Health check completed!${NC}"
