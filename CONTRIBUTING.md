# Contributing

## Workflow

1. Keep firmware, backend, and frontend changes scoped where possible.
2. Update shared docs when contracts, setup, or deployment assumptions change.
3. Run the smallest relevant validation command before opening a pull request.

## Validation

- Backend: `cd backend && python -m compileall .`
- Frontend: `cd frontend && npm ci && npm run build`
- Firmware: verify the main sketch under `firmware/mpu6050_init/` remains intact and documented

## Secrets

- Do not commit filled `.env` files.
- Keep deployment credentials in CI secrets or platform settings, not in tracked config.
