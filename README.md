# Budget Platform

Simple budget platform that ingests client CSV data, stores it in SQLite via SQLAlchemy, and exposes:
- API via FastAPI
- UI via Streamlit

Architecture follows DDD/Clean Architecture boundaries with ports/adapters so RabbitMQ and service split can evolve later.

## CSV schema
Required columns:
- `client_id`
- `client_name`
- `category`
- `amount`
- `date` (ISO format: `YYYY-MM-DD`)

## Quick start
1. Create env and install:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -e .`
2. Configure env:
   - `cp .env.example .env`
3. Run migrations:
   - `alembic upgrade head`
4. Start API:
   - `PYTHONPATH=src uvicorn budget_app.interfaces.api.main:app --reload`
5. Start Streamlit UI:
   - `PYTHONPATH=src streamlit run src/budget_app/interfaces/streamlit/app.py`

## Useful commands
- `make migrate`
- `make api`
- `make ui`
- `make test`

## Notes
- SQLite is used for MVP simplicity.
- RabbitMQ is optional in MVP (`RABBITMQ_ENABLED=false` by default).
