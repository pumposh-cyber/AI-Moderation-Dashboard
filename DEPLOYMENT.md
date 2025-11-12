# Production Deployment Guide

This guide covers deploying the AI Moderation Dashboard to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Database Migration](#database-migration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Security Checklist](#security-checklist)
8. [Scaling Considerations](#scaling-considerations)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL 15+ (for production)
- Domain name with DNS configured
- SSL/TLS certificates (Let's Encrypt recommended)
- Server with minimum 2GB RAM, 2 CPU cores

## Environment Setup

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://moderation_user:STRONG_PASSWORD_HERE@db:5432/moderation
POSTGRES_DB=moderation
POSTGRES_USER=moderation_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
API_KEY=GENERATE_SECURE_RANDOM_KEY

# CORS Configuration (update with your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# AI Service (if using real AI)
OPENAI_API_KEY=your_openai_key_here
AI_SERVICE_URL=

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_ENABLED=true
```

### 2. Generate Secure Secrets

```bash
# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost/health
```

### Production Deployment Steps

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd moderation-dashboard
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   nano .env
   ```

3. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

4. **Verify deployment**
   ```bash
   # Check all services are running
   docker-compose ps
   
   # Test health endpoint
   curl http://localhost/health
   
   # Check logs
   docker-compose logs backend
   ```

5. **Set up SSL/TLS** (see Nginx Configuration section)

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Run database migrations if needed
docker-compose exec backend python -m alembic upgrade head
```

## Manual Deployment

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE moderation;
CREATE USER moderation_user WITH PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE moderation TO moderation_user;
\q
```

### 3. Run Database Migrations

```bash
export DATABASE_URL="postgresql://moderation_user:PASSWORD@localhost:5432/moderation"
python -c "from backend import database; database.init_db()"
```

### 4. Run with Gunicorn

```bash
gunicorn backend.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

## Database Migration

### From SQLite to PostgreSQL

1. **Export data from SQLite**
   ```bash
   sqlite3 moderation.db .dump > dump.sql
   ```

2. **Convert SQLite dump to PostgreSQL format**
   - Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
   - Replace `?` placeholders with `%s`
   - Remove SQLite-specific syntax

3. **Import to PostgreSQL**
   ```bash
   psql -U moderation_user -d moderation < converted_dump.sql
   ```

### Using Alembic (Recommended)

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Monitoring & Observability

### Health Checks

- **Health endpoint**: `GET /health` - Basic health check
- **Readiness endpoint**: `GET /ready` - Readiness probe (checks database)
- **Metrics endpoint**: `GET /metrics` - Prometheus metrics

### Logging

Logs are structured JSON format. In production, configure log aggregation:

```bash
# View logs
docker-compose logs -f backend

# Export logs
docker-compose logs backend > app.log
```

### Prometheus Metrics

Metrics are available at `/metrics` endpoint:

- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram
- `database_connections_active` - Active database connections

### Setting up Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'moderation-dashboard'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable rate limiting (`RATE_LIMIT_ENABLED=true`)
- [ ] Configure CORS with specific origins
- [ ] Set up SSL/TLS certificates
- [ ] Enable security headers (already configured)
- [ ] Use strong database passwords
- [ ] Restrict database access to application server only
- [ ] Set up firewall rules
- [ ] Enable log monitoring
- [ ] Set up automated backups
- [ ] Configure API key authentication (if needed)
- [ ] Review and update dependencies regularly
- [ ] Set up intrusion detection
- [ ] Configure fail2ban for SSH protection

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or cloud load balancer
2. **Multiple Backend Instances**: Run multiple Gunicorn workers
3. **Database Connection Pooling**: Already configured in code
4. **Session Storage**: Use Redis for shared sessions (if adding auth)

### Vertical Scaling

- Increase Gunicorn workers: `--workers 8`
- Increase database connection pool size
- Add more RAM for caching

### Database Scaling

- Set up PostgreSQL read replicas
- Use connection pooling (PgBouncer)
- Add database indexes for frequently queried columns

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs backend

# Check database connectivity
docker-compose exec backend python -c "from backend import database; database.init_db()"

# Verify environment variables
docker-compose exec backend env | grep DATABASE
```

### Database connection errors

1. Verify database is running: `docker-compose ps db`
2. Check connection string format
3. Verify credentials
4. Check network connectivity: `docker-compose exec backend ping db`

### High memory usage

1. Reduce Gunicorn workers
2. Enable database connection pooling limits
3. Add memory limits to Docker containers

### Performance issues

1. Check database indexes: `\d+ flagged_items` in PostgreSQL
2. Review slow query logs
3. Monitor Prometheus metrics
4. Check Nginx access logs for patterns

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U moderation_user moderation > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U moderation_user moderation < backup_20240101.sql
```

### Automated Backups

Set up cron job:

```bash
0 2 * * * docker-compose exec db pg_dump -U moderation_user moderation > /backups/moderation_$(date +\%Y\%m\%d).sql
```

## Rollback Procedure

1. **Stop current version**
   ```bash
   docker-compose down
   ```

2. **Checkout previous version**
   ```bash
   git checkout <previous-commit>
   ```

3. **Rebuild and restart**
   ```bash
   docker-compose up -d --build
   ```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review health endpoints: `/health`, `/ready`
- Check Prometheus metrics: `/metrics`

