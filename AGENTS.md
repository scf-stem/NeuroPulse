# Repository Guidelines

## Project Structure & Module Organization
- `mpu6050_init/` contains ESP32 + MPU6050 firmware sketches.
- `web/backend/app/` is the FastAPI service; `api/` routes, `models/` ORM, `core/` config, `services/` business logic.
- `web/frontend/src/` is the Vue 3 app; `views/` pages, `components/` UI, `stores/` Pinia, `api/` Axios clients, `types/` shared TS types, `assets/` static files.
- `web/Dockerfile` and `web/zbpack.json` are used for container deployment; deeper docs live in `PROJECT_DEVELOPMENT_GUIDE.md` and `web/ZEABUR_DEPLOY.md`.

## Build, Test, and Development Commands
Backend (`web/backend`):
- `pip install -r requirements.txt` installs dependencies.
- `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` runs the API locally.
- `pytest` runs backend tests.
- `black .` formats, `flake8 .` lints.

Frontend (`web/frontend`):
- `npm install` installs dependencies.
- `npm run dev` starts Vite dev server (5173, proxies `/api`).
- `npm run build` produces a production build.
- `npm run lint` runs ESLint with autofix; `npm run format` runs Prettier.

Docker (repo root):
- `docker build -t tremor-guard:latest -f web/Dockerfile .`
- `docker run -p 8000:8000 -e DATABASE_URL="..." -e ANTHROPIC_API_KEY="..." tremor-guard:latest`

## Coding Style & Naming Conventions
- Python: `black` formatting (4-space indent), `flake8` for lint; modules and functions in `snake_case`, classes in `PascalCase`.
- FastAPI endpoints live under `web/backend/app/api/` and should be async.
- Frontend uses Vue 3 Composition API with `<script setup>`, TypeScript, ESLint + Prettier.
- Vue component files use `PascalCase` (example: `RealTimeWaveCheck.vue`); use `@/` path alias for `src/`.

## Testing Guidelines
- Backend uses `pytest` + `pytest-asyncio`; name files `test_*.py` and place new tests under `web/backend/tests/` (create if missing) or next to the module.
- No frontend test runner is configured; rely on `npm run lint` and `npm run build` to catch issues.

## Commit & Pull Request Guidelines
- Follow Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`; optional scopes like `fix(frontend):`.
- Keep the subject short and imperative; body may be in English or Chinese.
- PRs should include a summary, linked issues, steps to verify, and screenshots for UI changes.

## Configuration & Secrets
- Backend config: `web/backend/.env` (see `web/backend/.env.example`).
- Frontend config: `web/frontend/.env` (see `web/frontend/.env.example`).
- Never commit secrets; required keys include `DATABASE_URL`, `ANTHROPIC_API_KEY`, `JWT_SECRET_KEY`, `DEVICE_API_KEY`, and `VITE_API_BASE_URL`.
