.PHONY: migrate api ui test

migrate:
	alembic upgrade head

api:
	PYTHONPATH=src uvicorn budget_app.interfaces.api.main:app --reload

ui:
	PYTHONPATH=src streamlit run src/budget_app/interfaces/streamlit/app.py

test:
	pytest
