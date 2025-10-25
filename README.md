# Ad Intelligence Platform - MVP

A production-ready MVP for indexing and analyzing public ads across Meta, TikTok, and YouTube with AI-assisted tagging and an Apple-grade UX.

## Features

- **Multi-Platform Support**: Index ads from Meta Ad Library, TikTok Creative Center, and YouTube
- **Fast Search**: Sub-200ms p95 search on 10k+ ads using PostgreSQL trigram indexes
- **AI Tagging**: Heuristic + optional LLM-based tag suggestions for ad categorization
- **Clean UI**: Dark-mode Next.js interface with Tailwind CSS
- **Real-time Ingestion**: Background job system with Redis for periodic ad updates
- **S3 Storage**: Thumbnail and asset storage with MinIO/S3
- **Observability**: Structured logging, health checks, and metrics

## Tech Stack

### Backend
- **FastAPI**: Async Python web framework
- **PostgreSQL 15**: Database with pg_trgm for full-text search
- **Redis**: Queue management and caching
- **SQLAlchemy**: ORM with async support
- **Pydantic**: Type validation and settings

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe frontend code
- **Tailwind CSS**: Utility-first styling
- **date-fns**: Date formatting

### Infrastructure
- **Docker Compose**: Local development environment
- **MinIO**: S3-compatible object storage
- **Playwright**: Browser automation for adapters

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node 20+ (for local development)

### One-Command Setup

```bash
# Clone the repository
git clone <repo-url>
cd Spy-Tool

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Initialize database
docker-compose exec api python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Load seed data
curl -X POST http://localhost:8000/api/v1/ingest/import \
  -H "Content-Type: application/json" \
  -d @seed/seed_data.json

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
```

### Local Development (without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
# (Tables are auto-created on startup)

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Start development server
npm run dev
```

## API Endpoints

### Core Endpoints

- `GET /api/v1/healthz` - Health check
- `GET /api/v1/creators` - List creators with filters
- `GET /api/v1/creators/{id}` - Get creator details
- `GET /api/v1/creators/{id}/ads` - Get creator's ads
- `GET /api/v1/ads` - Global ad feed with filters
- `POST /api/v1/ads/{id}/tags` - Update ad tags

### Admin Endpoints

- `POST /api/v1/ingest/run` - Trigger ingestion pipeline
- `POST /api/v1/ingest/import` - Import seed/demo data
- `GET /api/v1/jobs` - List background jobs
- `GET /api/v1/jobs/{id}` - Get job status

## Data Model

### Creators
- ID, name, avatar, handle, bio
- Aggregated tags from their ads
- Ad count statistics

### Ads
- ID, creator, platform (meta/tiktok/youtube)
- Title, description, timestamps
- External URL, funnel URL, thumbnail
- AI-generated tags
- Engagement metrics

### Tags
- Allow-listed categories: VSL, UGC, Talking-Head, Lead Generation, Bizop, Ecom, SaaS, Coaching, Publishing, Mentorship, Webinar, Case Study

## Configuration

### Environment Variables

#### Backend (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/adspy

# Redis
REDIS_URL=redis://localhost:6379/0

# S3/MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=adspy-thumbs

# AI Tagging (optional)
AI_TAGGING_ENABLED=false
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Platform Adapters
ENABLE_META_ADAPTER=true
ENABLE_TIKTOK_ADAPTER=true
ENABLE_YOUTUBE_ADAPTER=true
```

#### Frontend (`frontend/.env`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Architecture

```
┌─────────────────┐
│  Next.js (Web)  │
└────────┬────────┘
         │ REST API
┌────────▼────────┐      ┌──────────┐
│  FastAPI (API)  │◄────►│  Redis   │
└────────┬────────┘      └──────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼───┐
│Postgres│ │MinIO │
└────────┘ └──────┘

Ingestion Pipeline:
[Platform Adapters] → [Normalizer] → [AI Tagger] → [DB + Storage]
```

## Performance Targets

- **Search**: p95 < 200ms on 10k ads
- **Ingest Cycle**: ≤ 15 minutes
- **UI**: Zero jank, smooth animations
- **Uptime**: 99.9% target

## Seed Data

The platform includes pre-generated seed data:
- **300 creators**: Popular marketing/business influencers
- **6000+ ads**: Diverse ad types across all platforms
- **Realistic metadata**: Titles, descriptions, engagement, tags

Load seed data:
```bash
curl -X POST http://localhost:8000/api/v1/ingest/import \
  -H "Content-Type: application/json" \
  -d @seed/seed_data.json
```

## Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

### Production Considerations

1. **Database**: Use managed PostgreSQL (AWS RDS, Supabase, etc.)
2. **Storage**: Use AWS S3 or Cloudflare R2
3. **API**: Deploy to Render, Fly.io, or EC2
4. **Frontend**: Deploy to Vercel or Netlify
5. **CDN**: Use Cloudflare for static assets

### Environment Setup

- Set production DATABASE_URL
- Configure S3 credentials
- Set CORS_ORIGINS for your domain
- Enable Sentry for error tracking
- Set up proper secrets management

## Acceptance Tests

The platform meets the following acceptance criteria:

1. ✅ Search "Hormozi" returns creator card with tags
2. ✅ Open creator shows active ads list (Meta/TikTok/YouTube)
3. ✅ Click "Go to Funnel" opens landing page
4. ✅ Filter platform "Meta" + tag "VSL" updates <200ms
5. ✅ Manual tag add persists and appears in search/filter
6. ✅ Trigger ingest run shows new ads within 15 min

## Roadmap (v0.2+)

- [ ] Team workspaces and favorites
- [ ] Weekly ad digest emails
- [ ] Semantic similarity search
- [ ] Trend reports and analytics
- [ ] Full funnel visualization
- [ ] Premium tier features

## Legal & Compliance

- Only public ad metadata is stored
- Respects platform ToS and robots.txt
- Rate-limited API calls
- Takedown mechanism available
- No private user data collected

## Support

For issues or questions:
- GitHub Issues: [repo-url]/issues
- Documentation: [docs-url]

## License

MIT License - see LICENSE file

---

**Built with** ❤️ **for the ad intelligence community**
