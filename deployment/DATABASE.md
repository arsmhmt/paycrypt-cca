# Database Configuration for Production

## PostgreSQL Setup (Recommended)

### 1. Install PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib libpq-dev
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User
```bash
sudo -u postgres psql
```

```sql
-- Create user
CREATE USER paycrypt_user WITH PASSWORD 'your_secure_password_here';

-- Create database
CREATE DATABASE paycrypt_prod OWNER paycrypt_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE paycrypt_prod TO paycrypt_user;
ALTER USER paycrypt_user CREATEDB;

-- Exit
\q
```

### 3. Configure Connection
Update your `.env` file:
```env
DATABASE_URL=postgresql://paycrypt_user:your_secure_password_here@localhost/paycrypt_prod
SQLALCHEMY_DATABASE_URI=postgresql://paycrypt_user:your_secure_password_here@localhost/paycrypt_prod
```

## Database Migration Commands

### Initial Setup
```bash
# Navigate to app directory
cd /home/paycrypt/paycrypt-cca
source venv/bin/activate

# Set Flask app
export FLASK_APP=run:create_app

# Initialize migration repository (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### Regular Migrations
```bash
# After model changes
flask db migrate -m "Description of changes"
flask db upgrade
```

## Backup and Restore

### Automated Backup Script
```bash
#!/bin/bash
# /home/paycrypt/backup_db.sh

BACKUP_DIR="/home/paycrypt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="paycrypt_prod"
DB_USER="paycrypt_user"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/paycrypt_${DATE}.sql

# Compress backup
gzip $BACKUP_DIR/paycrypt_${DATE}.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "paycrypt_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: paycrypt_${DATE}.sql.gz"
```

### Restore from Backup
```bash
# Uncompress backup
gunzip /path/to/backup.sql.gz

# Drop existing database (CAUTION!)
sudo -u postgres dropdb paycrypt_prod

# Create new database
sudo -u postgres createdb -O paycrypt_user paycrypt_prod

# Restore from backup
psql -U paycrypt_user -h localhost -d paycrypt_prod < /path/to/backup.sql
```

## Performance Optimization

### PostgreSQL Configuration
Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# Logging
log_min_duration_statement = 1000  # Log slow queries (1 second)

# Checkpoint settings
checkpoint_completion_target = 0.7
wal_buffers = 7864kB
```

### Connection Pooling
Consider using pgbouncer for connection pooling:

```bash
sudo apt install pgbouncer
```

## Monitoring

### Check Database Status
```bash
# Connection count
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('paycrypt_prod'));"

# Table sizes
sudo -u postgres psql -d paycrypt_prod -c "
SELECT schemaname,tablename,pg_size_pretty(size) as size_pretty
FROM (
    SELECT schemaname,tablename,pg_total_relation_size(schemaname||'.'||tablename) as size
    FROM pg_tables WHERE schemaname NOT IN ('information_schema','pg_catalog')
) t ORDER BY size DESC;
"
```

### Log Analysis
```bash
# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Check slow queries
sudo grep "duration:" /var/log/postgresql/postgresql-14-main.log
```

## Security

### Database Security
1. **Firewall**: Only allow local connections by default
2. **Authentication**: Use strong passwords
3. **SSL**: Enable SSL for remote connections if needed
4. **Backups**: Encrypt backup files
5. **Updates**: Keep PostgreSQL updated

### User Permissions
```sql
-- Create read-only user for reporting
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE paycrypt_prod TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

## Troubleshooting

### Common Issues

#### Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check listening ports
sudo netstat -tulpn | grep :5432

# Test connection
psql -U paycrypt_user -h localhost -d paycrypt_prod -c "SELECT version();"
```

#### Permission Issues
```sql
-- Grant missing permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO paycrypt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO paycrypt_user;
```

#### Performance Issues
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM your_table WHERE condition;

-- Update table statistics
ANALYZE;

-- Reindex if needed
REINDEX TABLE your_table;
```
