.PHONY: help install dev run migrate migration test lint format clean dev-up dev-down dev-cleanup dev-logs dev-restart dev-build prod-up prod-down prod-logs db-shell db-reset docker-clean

help:
	@echo "Available commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make install       - Install dependencies using uv"
	@echo "  make dev           - Install dev dependencies"
	@echo "  make run           - Run the development server"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migration     - Create a new migration"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean up generated files"
	@echo ""
	@echo "Docker Development:"
	@echo "  make dev-up        - Start development environment with Docker"
	@echo "  make dev-down      - Stop development environment"
	@echo "  make dev-cleanup   - Stop and remove all containers, volumes, and networks"
	@echo "  make dev-logs      - Show development logs"
	@echo "  make dev-restart   - Restart development services"
	@echo "  make dev-build     - Rebuild development images"
	@echo ""
	@echo "Docker Production:"
	@echo "  make prod-up       - Start production environment with Docker"
	@echo "  make prod-down     - Stop production environment"
	@echo "  make prod-logs     - Show production logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell      - Open database shell"
	@echo "  make db-reset      - Reset database (drop and recreate)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make docker-clean  - Remove all Docker resources (containers, images, volumes)"

install:
	uv sync

dev:
	uv sync --all-extras

run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

migration:
	@read -p "Enter migration message: " message; \
	uv run alembic revision --autogenerate -m "$$message"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	rm -f *.db

# Docker Development Commands
dev-up:
	docker-compose up -d
	@echo "Development environment is running!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Use 'make dev-logs' to view logs"

dev-down:
	docker-compose down

dev-cleanup:
	docker-compose down -v --remove-orphans
	@echo "Development environment cleaned up!"

dev-logs:
	docker-compose logs -f

dev-restart:
	docker-compose restart

dev-build:
	docker-compose build --no-cache

# Docker Production Commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production environment is running!"
	@echo "Application: http://localhost"

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Database Commands
db-shell:
	docker-compose exec db psql -U postgres -d url_shortener

db-reset:
	docker-compose down -v
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 3
	docker-compose up -d backend
	docker-compose exec backend uv run alembic upgrade head
	@echo "Database reset complete!"

# Docker Cleanup Commands
docker-clean:
	docker-compose down -v --remove-orphans
	docker system prune -af --volumes
	@echo "All Docker resources cleaned!"
