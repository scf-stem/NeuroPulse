# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tremor Guard** (震颤卫士) is an AI-enhanced Parkinson's tremor monitoring system:
- IoT wearable device (ESP32-C3 + MPU6050) for real-time tremor detection via FFT analysis (4-6Hz band)
- FastAPI backend with PostgreSQL database
- Vue 3 + TypeScript frontend with Tailwind CSS
- Claude AI integration for health analysis
- Single-container Docker deployment on Zeabur

## Build Commands

### Frontend (`web/frontend/`)
```bash
npm install              # Install dependencies
npm run dev              # Dev server (Vite, port 5173, proxies /api to :8000)
npm run build            # Production build
npm run lint             # Lint & fix
npm run format           # Format code
```

### Backend (`web/backend/`)
```bash
pip install -r requirements.txt                           # Install dependencies
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Dev server
pytest                                                     # Run tests
black .                                                    # Format
flake8 .                                                   # Lint
```

### Docker (`web/Dockerfile`)
```bash
docker build -t tremor-guard:latest -f web/Dockerfile .
docker run -p 8000:8000 -e DATABASE_URL="..." -e ANTHROPIC_API_KEY="..." tremor-guard:latest
```

## Architecture

```
ESP32 Device ──HTTP──┐
                     ▼
Browser ────────► FastAPI (port 8000) ────► PostgreSQL
(Vue SPA)           │
                    ├────► Claude API (AI analysis)
                    ├────► Redis (caching, optional)
                    └────► Static Files (serves frontend build)
```

### Data Flow
1. **ESP32**: Collects IMU data → FFT analysis (4-6Hz) → calculates severity (0-4) → batch uploads to `/api/data/upload`
2. **Backend**: Validates device auth → stores TremorSession/TremorData → exposes analysis endpoints
3. **Frontend**: Fetches sessions → renders charts → integrates AI assistant

## Key Directories

| Path | Purpose |
|------|---------|
| `web/frontend/src/views/` | Vue page components |
| `web/frontend/src/api/` | Axios API clients |
| `web/frontend/src/stores/` | Pinia state (auth.ts, tremor.ts) |
| `web/frontend/src/types/index.ts` | TypeScript interfaces |
| `web/backend/app/api/` | FastAPI route handlers |
| `web/backend/app/models/` | SQLAlchemy ORM models |
| `web/backend/app/core/` | Config & database setup |
| `mpu6050_init/` | Arduino/ESP32 firmware |

## API Routes

- `/api/auth/*` - JWT authentication (login, register, refresh)
- `/api/device/*` - ESP32 device management
- `/api/data/*` - Tremor data upload & queries
- `/api/analysis/*` - Statistics & trends
- `/api/ai/chat` - Claude AI health insights
- `/api/report/*` - PDF report generation
- `/api/config/*` - ESP32 configuration sync
- `/api/test/*` - Debug endpoints

## Database Models

- **User**: id, email, username, password_hash, role (user/doctor/admin)
- **Device**: device_id, owner_id, firmware_version, battery_level, is_online
- **TremorSession**: user_id, device_id, timestamps, aggregated stats
- **TremorData**: session_id, timestamp, frequency, severity (0-4), amplitude, etc.

## Development Patterns

**Frontend (Vue 3)**:
- Use Composition API with `<script setup>`
- API calls only via `api/` modules, not in components
- Path alias: `@/` → `src/`
- Tailwind primary color: coral orange (#F97316)

**Backend (FastAPI)**:
- Async/await everywhere (asyncpg driver)
- Dependency injection: `db: AsyncSession = Depends(get_db)`
- Pydantic schemas for request/response validation

## Environment Variables

Backend (`web/backend/.env`):
- `DATABASE_URL` - PostgreSQL async connection string
- `ANTHROPIC_API_KEY` - Claude API key
- `JWT_SECRET_KEY` - JWT signing secret
- `DEVICE_API_KEY` - ESP32 device authentication

Frontend (`web/frontend/.env`):
- `VITE_API_BASE_URL` - Backend URL (default: http://localhost:8000)

## Zeabur Deployment

- Root directory: `web/` (configured in zbpack.json)
- Database variables auto-constructed from POSTGRES_* env vars
- Port must be 8000
- CORS auto-configured for `*.zeabur.app` domains

## Documentation

- [PROJECT_DEVELOPMENT_GUIDE.md](PROJECT_DEVELOPMENT_GUIDE.md) - Comprehensive Chinese docs
- [.claude/hardware-spec.md](.claude/hardware-spec.md) - Hardware technical specifications
- [web/ZEABUR_DEPLOY.md](web/ZEABUR_DEPLOY.md) - Deployment guide

## Commit Convention

- `feat:` - New feature
- `fix:` - Bug fix
- `chore:` - Maintenance
- `docs:` - Documentation
- Commit messages typically in Chinese
