from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import ai, analysis, auth, config, data, device, health, medication, rehabilitation, report, test
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.i18n import get_locale, msg

AppMode = Literal["full", "vercel"]

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def _make_lifespan(mode: AppMode):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print(f"🚀 {settings.APP_NAME} booting in {mode} mode")
        print(f"📊 environment: {settings.APP_ENV}")

        should_init_db = mode != "vercel" and settings.AUTO_INIT_DB and settings.APP_ENV != "production"
        if should_init_db:
            await init_db()
            print("✅ database initialized from SQLAlchemy metadata")

        yield

        if mode != "vercel":
            await close_db()

        print(f"👋 {settings.APP_NAME} shutting down")

    return lifespan


def _base_app(mode: AppMode, docs_url: str | None, redoc_url: str | None) -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Parkinson's Tremor Monitoring Backend",
        version="1.0.0",
        lifespan=_make_lifespan(mode),
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def _register_api_routes(app: FastAPI, base_prefix: str) -> None:
    app.include_router(auth.router, prefix=f"{base_prefix}/auth", tags=["Authentication"])
    app.include_router(device.router, prefix=f"{base_prefix}/device", tags=["Device"])
    app.include_router(data.router, prefix=f"{base_prefix}/data", tags=["Data"])
    app.include_router(analysis.router, prefix=f"{base_prefix}/analysis", tags=["Analysis"])
    app.include_router(ai.router, prefix=f"{base_prefix}/ai", tags=["AI"])
    app.include_router(report.router, prefix=f"{base_prefix}/report", tags=["Report"])
    app.include_router(medication.router, prefix=f"{base_prefix}/medication", tags=["Medication"])
    app.include_router(rehabilitation.router, prefix=f"{base_prefix}/rehabilitation", tags=["Rehabilitation"])
    app.include_router(health.router, prefix=f"{base_prefix}/health", tags=["Health"])
    app.include_router(test.router, prefix=f"{base_prefix}/test", tags=["Test"])
    app.include_router(config.router, prefix=f"{base_prefix}/config", tags=["Config"])


def _api_info_payload(request: Request, api_base: str) -> dict:
    locale = get_locale(request)
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "message": msg(locale, "backend.api_running"),
        "endpoints": {
            "auth": f"{api_base}/auth",
            "device": f"{api_base}/device",
            "data": f"{api_base}/data",
            "analysis": f"{api_base}/analysis",
            "ai": f"{api_base}/ai",
            "report": f"{api_base}/report",
            "medication": f"{api_base}/medication",
            "rehabilitation": f"{api_base}/rehabilitation",
            "health": f"{api_base}/health",
            "config": f"{api_base}/config",
        },
    }


def create_full_app() -> FastAPI:
    app = _base_app(
        mode="full",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    _register_api_routes(app, "/api")

    @app.get("/api")
    async def api_info(request: Request):
        return _api_info_payload(request, "/api")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "database": "connected", "redis": "not-required"}

    if STATIC_DIR.exists():
        assets_dir = STATIC_DIR / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/", response_class=HTMLResponse)
        async def serve_frontend_root(request: Request):
            index_path = STATIC_DIR / "index.html"
            if index_path.exists():
                return FileResponse(
                    str(index_path),
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )
            return HTMLResponse(msg(get_locale(request), "backend.frontend_missing"))

        @app.get("/{path:path}")
        async def serve_frontend(path: str, request: Request):
            if path.startswith("api/") or path == "health":
                return {"error": "Not found"}, 404

            file_path = STATIC_DIR / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))

            index_path = STATIC_DIR / "index.html"
            if index_path.exists():
                return FileResponse(
                    str(index_path),
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )

            return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)
    else:
        @app.get("/")
        async def root(request: Request):
            locale = get_locale(request)
            return {
                "name": settings.APP_NAME,
                "version": "1.0.0",
                "status": "running",
                "message": msg(locale, "backend.api_only"),
                "docs": "/docs" if settings.DEBUG else None,
            }

    return app


def create_vercel_api_app() -> FastAPI:
    app = _base_app(mode="vercel", docs_url=None, redoc_url=None)
    _register_api_routes(app, "")

    @app.get("/")
    async def api_info(request: Request):
        return _api_info_payload(request, "/api")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "database": "connected", "redis": "not-required"}

    return app
