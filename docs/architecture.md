# Architecture

NeuroPulse is a multi-part system made of firmware, backend APIs, and a web client.

## Main parts

- `firmware/mpu6050_init/` ESP32 + MPU6050 firmware sketch and helpers
- `backend/app/` FastAPI application code
- `backend/api/` backend-facing API entrypoints for deployment integration
- `frontend/src/` Vue 3 application
- `deploy/` platform configuration separated from runtime source

## Runtime flow

1. Device firmware captures motion data and communicates with backend services.
2. The backend stores, analyzes, and exposes health and device APIs.
3. The frontend visualizes monitoring data and care workflows.
