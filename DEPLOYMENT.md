# Deployment Guide

This guide covers deploying the Ad Intelligence Platform to production.

## Architecture Overview

```
┌─────────────┐
│  Cloudflare │ (CDN, DDoS protection)
└──────┬──────┘
       │
┌──────▼──────┐
│   Vercel    │ (Next.js frontend)
└──────┬──────┘
       │ API calls
┌──────▼──────┐
│  Render.com │ (FastAPI backend)
└──────┬──────┘
       │
   ┌───┴───┬────────┬─────────┐
   │       │        │         │
┌──▼───┐ ┌▼────┐ ┌▼───┐ ┌────▼────┐
│ RDS  │ │Redis│ │ S3 │ │ Sentry  │
└──────┘ └─────┘ └────┘ └─────────┘
```

## Prerequisites

- AWS Account (for RDS, S3, ElastiCache)
- Render.com account (or Fly.io/Railway)
- Vercel account (or Netlify)
- Domain name (optional but recommended)

## Step 1: Database Setup (AWS RDS)

### Create PostgreSQL Instance

```bash
# Create RDS PostgreSQL 15 instance
aws rds create-db-instance \
  --db-instance-identifier adspy-prod-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --backup-retention-period 7 \
  --publicly-accessible
```

### Initialize Database

```bash
# Connect to RDS
psql -h adspy-prod-db.xxxxx.rds.amazonaws.com -U admin -d postgres

# Create database
CREATE DATABASE adspy;

# Enable extensions
\c adspy
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

## Step 2: Redis Setup (AWS ElastiCache)

### Create Redis Cluster

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id adspy-prod-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx
```

## Step 3: S3 Bucket Setup

### Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://adspy-prod-thumbs

# Set public read policy
aws s3api put-bucket-policy \
  --bucket adspy-prod-thumbs \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::adspy-prod-thumbs/*"
    }]
  }'

# Enable CORS
aws s3api put-bucket-cors \
  --bucket adspy-prod-thumbs \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"]
    }]
  }'
```

## Step 4: Backend Deployment (Render.com)

### Create Web Service

1. Go to Render.com Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: adspy-api
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Starter ($7/month) or higher

### Environment Variables

Set the following in Render dashboard:

```env
DATABASE_URL=postgresql+asyncpg://admin:password@adspy-prod-db.xxxxx.rds.amazonaws.com:5432/adspy
REDIS_URL=redis://adspy-prod-redis.xxxxx.cache.amazonaws.com:6379/0
S3_ENDPOINT=
S3_ACCESS_KEY=<aws-access-key>
S3_SECRET_KEY=<aws-secret-key>
S3_BUCKET=adspy-prod-thumbs
S3_REGION=us-east-1
CORS_ORIGINS=["https://yourdomain.com"]
DEBUG=false
LOG_LEVEL=INFO
SENTRY_DSN=<sentry-dsn>
AI_TAGGING_ENABLED=true
OPENAI_API_KEY=<openai-key>
```

### Alternative: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
cd backend
fly launch --name adspy-api

# Set secrets
fly secrets set DATABASE_URL="..." REDIS_URL="..." ...

# Deploy
fly deploy
```

## Step 5: Frontend Deployment (Vercel)

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Or connect via GitHub in Vercel dashboard
```

### Environment Variables

Set in Vercel dashboard:

```env
NEXT_PUBLIC_API_URL=https://adspy-api.onrender.com/api/v1
```

### Custom Domain

1. Add domain in Vercel dashboard
2. Update DNS records:
   ```
   A     @       76.76.21.21
   CNAME www     cname.vercel-dns.com
   ```

## Step 6: Cloudflare Setup (Optional)

### Add Site to Cloudflare

1. Add your domain to Cloudflare
2. Update nameservers at registrar
3. Enable:
   - CDN/Proxy
   - DDoS protection
   - Auto-minify (JS, CSS, HTML)
   - Brotli compression
   - Always Use HTTPS

### Page Rules

```
adspy.com/api/*
  - Cache Level: Bypass

adspy.com/_next/static/*
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 year
```

## Step 7: Monitoring Setup

### Sentry

```bash
# Sign up at sentry.io
# Create new project: "Ad Intelligence Platform"
# Copy DSN and add to environment variables
```

### Uptime Monitoring

Use UptimeRobot or BetterUptime:
- Monitor: https://yourdomain.com/api/v1/healthz
- Interval: 5 minutes
- Alerts: Email/SMS

## Step 8: Load Seed Data

```bash
# Import seed data to production
curl -X POST https://adspy-api.onrender.com/api/v1/ingest/import \
  -H "Content-Type: application/json" \
  -d @seed/seed_data.json
```

## Step 9: Setup Cron Jobs

### Ingest Job (run every 15 minutes)

On Render.com:
1. Add Cron Job
2. Command: `curl -X POST https://adspy-api.onrender.com/api/v1/ingest/run`
3. Schedule: `*/15 * * * *`

Alternatively, use GitHub Actions:

```yaml
# .github/workflows/ingest.yml
name: Periodic Ingest
on:
  schedule:
    - cron: '*/15 * * * *'
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Ingest
        run: |
          curl -X POST https://adspy-api.onrender.com/api/v1/ingest/run
```

## Step 10: Backups

### Database Backups

```bash
# Automated RDS snapshots (already enabled)
# Manual backup
pg_dump -h adspy-prod-db.xxxxx.rds.amazonaws.com -U admin adspy > backup.sql

# Restore
psql -h adspy-prod-db.xxxxx.rds.amazonaws.com -U admin adspy < backup.sql
```

### S3 Versioning

```bash
aws s3api put-bucket-versioning \
  --bucket adspy-prod-thumbs \
  --versioning-configuration Status=Enabled
```

## Performance Optimization

### Database Indexes

Ensure all indexes are created (auto-created on startup):
- `idx_creators_name` (GIN trigram)
- `idx_ads_text` (GIN trigram)
- `idx_ads_platform`
- `idx_ads_detected_at`

### Query Optimization

Monitor slow queries:
```sql
-- Enable pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Frontend Optimization

- Enable Vercel Edge Caching
- Use Next.js Image Optimization
- Implement Incremental Static Regeneration (ISR)

## Security Checklist

- [ ] Database: Private VPC, no public access
- [ ] API: Rate limiting enabled
- [ ] S3: Public read only, no write
- [ ] Secrets: All in environment variables
- [ ] CORS: Restricted to domain only
- [ ] HTTPS: Enforced everywhere
- [ ] Monitoring: Sentry error tracking
- [ ] Backups: Daily automated backups

## Scaling Considerations

### Vertical Scaling
- RDS: db.t3.micro → db.t3.small → db.t3.medium
- Render: Starter → Standard → Pro

### Horizontal Scaling
- Add read replicas for database
- Use Redis Cluster for high availability
- Deploy API to multiple regions

### Caching Strategy
- Redis for API response caching
- CloudFlare for static assets
- Browser caching for images

## Cost Estimate

Monthly costs (approximate):

- **RDS (t3.micro)**: $15
- **ElastiCache (t3.micro)**: $12
- **S3**: $1 (per GB stored)
- **Render (Starter)**: $7
- **Vercel (Hobby)**: $0
- **Total**: ~$35-40/month

For higher traffic:
- **RDS (t3.small)**: $30
- **Render (Standard)**: $25
- **Total**: ~$70-80/month

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql -h <rds-endpoint> -U admin -d adspy

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Redis Connection Issues
```bash
# Test Redis
redis-cli -h <elasticache-endpoint> ping

# Check network access
telnet <elasticache-endpoint> 6379
```

### API Not Starting
```bash
# Check Render logs
render logs -a adspy-api

# Check environment variables
render env -a adspy-api
```

## Support

For production issues:
- Render Support: support@render.com
- AWS Support: Console → Support Center
- Sentry: sentry.io/support

---

**Production Deployment Complete!** 🚀
