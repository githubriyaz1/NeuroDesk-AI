.PHONY: setup backend frontend test migrate docker-up docker-down lint format

setup:
	@echo "--> Setting up Backend Virtual Environment..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "--> Setting up Frontend Dependencies..."
	cd frontend && npm install

backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && . venv/bin/activate && pytest -v
	cd frontend && npm run test:run

lint:
	cd backend && . venv/bin/activate && ruff check app/ tests/
	cd frontend && npm run lint

format:
	cd backend && . venv/bin/activate && ruff format app/ tests/

migrate:
	cd backend && . venv/bin/activate && alembic upgrade head

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down
