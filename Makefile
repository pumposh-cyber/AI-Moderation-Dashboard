.PHONY: help build up down logs restart test lint clean migrate backup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-db: ## View database logs
	docker-compose logs -f db

restart: ## Restart all services
	docker-compose restart

test: ## Run tests
	pytest tests/ -v

test-docker: ## Run tests in Docker
	docker-compose exec backend pytest tests/ -v

lint: ## Run linters
	flake8 backend/ tests/ --max-line-length=120 --extend-ignore=E203,W503
	black --check backend/ tests/
	isort --check-only backend/ tests/

format: ## Format code
	black backend/ tests/
	isort backend/ tests/

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

migrate: ## Initialize database
	docker-compose exec backend python -c "from backend import database; database.init_db()"

backup: ## Backup database
	docker-compose exec db pg_dump -U moderation_user moderation > backup_$$(date +%Y%m%d_%H%M%S).sql

restore: ## Restore database (usage: make restore FILE=backup.sql)
	docker-compose exec -T db psql -U moderation_user moderation < $(FILE)

health: ## Check health status
	curl http://localhost/health

ready: ## Check readiness status
	curl http://localhost/ready

metrics: ## View Prometheus metrics
	curl http://localhost/metrics

shell: ## Open shell in backend container
	docker-compose exec backend /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U moderation_user moderation

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install flake8 black isort mypy

dev: ## Run in development mode
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

