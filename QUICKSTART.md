# Quick Start Guide

Get the Ad Intelligence Platform running in under 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 4GB RAM available
- Internet connection

## Steps

### 1. Clone and Setup

```bash
git clone <repo-url>
cd Spy-Tool
make setup
```

This will:
- Copy environment files
- Generate 300 creators and 6000+ ads seed data

### 2. Start Services

```bash
make up
```

This starts:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- MinIO S3 (ports 9000, 9001)
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)

Wait 30-60 seconds for services to initialize.

### 3. Load Seed Data

```bash
make seed
```

This imports all creators and ads into the database.

### 4. Access the Platform

Open your browser:

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## What to Try

### Search for Creators
1. Go to http://localhost:3000
2. Search for "Hormozi" in the search bar
3. Click on the creator card to see their ads

### Filter Ads
1. Click "Global Feed" tab
2. Select platform: Meta
3. Select tag: VSL
4. See results update instantly

### View Creator Details
1. Click any creator card
2. See their profile with aggregated tags
3. Browse their active ads
4. Click "Go to Funnel" or "View Live Ad"

### API Exploration
1. Go to http://localhost:8000/api/docs
2. Try the `/creators` endpoint
3. Try the `/ads` endpoint with filters

## Common Commands

```bash
# View logs
make logs

# Stop services
make down

# Clean up everything
make clean

# Restart services
make down && make up
```

## Troubleshooting

### Port Already in Use

If ports 3000, 8000, 5432, 6379, 9000, or 9001 are in use:

```bash
# Stop conflicting services
docker ps
docker stop <container-id>

# Or change ports in docker-compose.yml
```

### Services Not Starting

```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs api
docker-compose logs web
docker-compose logs postgres
```

### Seed Data Not Loading

```bash
# Check API is running
curl http://localhost:8000/api/v1/healthz

# Check seed file exists
ls -lh seed/seed_data.json

# Try loading manually
curl -X POST http://localhost:8000/api/v1/ingest/import \
  -H "Content-Type: application/json" \
  -d @seed/seed_data.json
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the codebase:
  - Backend: `backend/app/`
  - Frontend: `frontend/src/`
  - Adapters: `backend/app/adapters/`

## Performance Tips

For better local performance:

```bash
# Increase Docker memory
# Docker Desktop → Settings → Resources → Memory: 4GB+

# Use production build (faster frontend)
cd frontend
npm run build
npm start
```

## Development Mode

To develop with hot reload:

```bash
# Backend (auto-reload on file changes)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (auto-reload on file changes)
cd frontend
npm run dev
```

---

**Enjoy exploring the Ad Intelligence Platform!** 🚀

Questions? Check the docs or open an issue.
