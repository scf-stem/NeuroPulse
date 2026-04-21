# Backend Setup

## Local development

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database

- Alembic config lives in `backend/alembic.ini`
- migrations live under `backend/alembic/`
