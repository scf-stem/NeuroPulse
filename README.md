# NeuroPulse

NeuroPulse is an AI-enhanced Parkinson's tremor monitoring platform that combines an ESP32 + MPU6050 wearable device, a FastAPI backend, and a Vue 3 frontend for home monitoring, analysis, and care guidance.

## Repository Layout

- `mpu6050_init/`: ESP32 firmware and MPU6050 integration
- `web/backend/`: FastAPI service, data models, APIs, and app configuration
- `web/frontend/`: Vue 3 + TypeScript frontend
- `api/`: serverless API entrypoints used for deployment
- `web/Dockerfile`: single-container deployment image

## Local Development

### Backend

```bash
cd web/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd web/frontend
npm install
npm run dev
```

## Build and Validation

### Backend

```bash
cd web/backend
pytest
black .
flake8 .
```

### Frontend

```bash
cd web/frontend
npm run lint
npm run build
```

## Configuration

Create environment files from the provided examples before running the app:

- `web/backend/.env.example`
- `web/frontend/.env.example`

Never commit production credentials. Common required variables include `DATABASE_URL`, `ANTHROPIC_API_KEY`, `JWT_SECRET_KEY`, `DEVICE_API_KEY`, and `VITE_API_BASE_URL`.

## Documentation

- [Project Overview](./about.md)
- [Development Guide](./PROJECT_DEVELOPMENT_GUIDE.md)
- [Zeabur Deployment Guide](./web/ZEABUR_DEPLOY.md)
