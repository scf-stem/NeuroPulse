from pathlib import Path
import os
import sys


BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("AUTO_INIT_DB", "true")

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
    )
