# NeuroPulse

NeuroPulse is an AI-enhanced Parkinson's tremor monitoring platform that combines embedded firmware, a FastAPI backend, and a Vue web client in one repository.

## Repository Layout

- `firmware/` ESP32 and MPU6050 firmware projects
- `backend/` FastAPI service, Alembic config, and backend API entrypoints
- `frontend/` Vue 3 web client
- `deploy/` deployment-oriented config files kept separate from runtime code
- `docs/` architecture, setup guides, and product material

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm ci
npm run build
npm run dev
```

### Firmware

Open the sketch under `firmware/mpu6050_init/` in Arduino IDE or your ESP32-compatible toolchain.

## Documentation

- [Architecture](docs/architecture.md)
- [API Summary](docs/api.md)
- [Backend Setup](docs/backend-setup.md)
- [Frontend Setup](docs/frontend-setup.md)
- [Firmware Setup](docs/firmware-setup.md)

## Release and CI

- Backend CI validates the FastAPI service layout and Python dependencies.
- Frontend CI builds the Vue application.
- Firmware check validates the expected sketch entrypoint and project layout.
- Release workflow publishes build artifacts for tags and manual runs.

## Contributing

Review [CONTRIBUTING.md](CONTRIBUTING.md) and keep backend, frontend, and firmware changes aligned with the shared documentation in `docs/`.
