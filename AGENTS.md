# Repository Guidelines

## Project Structure & Module Organization
- `firmware/mpu6050_init/` contains the ESP32 + MPU6050 sketch and helper files.
- `backend/app/` is the FastAPI service; `api/` routes, `models/` ORM, `core/` config, `services/` business logic.
- `backend/api/` contains deployment-oriented API entrypoints moved out of the repository root.
- `frontend/src/` is the Vue 3 app; `views/`, `components/`, `stores/`, and `api/` hold the client-side code.
- `deploy/` holds deployment configuration artifacts. Shared architecture and setup docs live in `docs/`.

## Build, Test, and Development Commands
Backend (`backend`):
- `pip install -r requirements.txt`
- `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- `python -m compileall .`

Frontend (`frontend`):
- `npm ci`
- `npm run dev`
- `npm run build`

Firmware:
- Open `firmware/mpu6050_init/mpu6050_init.ino` in Arduino IDE or your ESP32 toolchain.

## Coding Style & Naming Conventions
- Python modules and functions use `snake_case`; classes use `PascalCase`.
- FastAPI endpoints live under `backend/app/api/`.
- Frontend uses Vue 3 Composition API with TypeScript.
- Vue component files use `PascalCase` and `@/` path aliases from `frontend/src/`.

## Testing Guidelines
- Backend validation currently uses import and compile checks; add tests under `backend/tests/` when backend behavior grows.
- No frontend test runner is configured; rely on `npm run build` for CI validation.
- Firmware changes must keep the main sketch entrypoint and helper files in sync.

## Configuration & Secrets
- Backend config: `backend/.env` from `backend/.env.example`
- Frontend config: `frontend/.env.example`
- Never commit secrets, Wi-Fi credentials, or environment-specific deployment values.
