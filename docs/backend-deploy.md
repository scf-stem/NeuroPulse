# Backend Deploy Notes

Deployment-specific files were moved out of runtime code and into `deploy/`.

## Current layout

- `deploy/backend.Dockerfile`
- `deploy/vercel.root.json`
- `deploy/vercel.frontend.json`
- `deploy/zbpack.root.json`
- `deploy/zbpack.web.json`

## Repository intent

This repository keeps deployment configuration separate from backend and frontend source code. The CI workflows build artifacts only; they do not perform a live deployment.

## Practical guidance

- Treat `backend/` as the deployable FastAPI application root.
- Treat `frontend/` as the deployable Vue application root.
- Use the files in `deploy/` as templates for platform-specific deployment setup.
