.PHONY: help install dev run test lint format clean
.PHONY: migrate migrate-sql migrate-all migrate-down migrate-history migrate-current migrate-create
.PHONY: dev-up dev-down dev-cleanup dev-logs dev-restart dev-build
.PHONY: prod-up prod-down prod-logs prod-build
.PHONY: db-shell db-reset db-seed db-backup db-restore
.PHONY: cache-clear cache-info
.PHONY: celery-worker celery-beat celery-flower
.PHONY: docker-clean docker-prune
.PHONY: test-unit test-integration test-coverage test-load
.PHONY: check security-check deps-update

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║        ShopX Sales Analytics - Available Commands               ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)📦 Local Development:$(NC)"
	@echo "  make install           - Install dependencies using uv"
	@echo "  make dev              - Install dev dependencies with extras"
	@echo "  make run              - Run the development server with hot reload"
	@echo "  make test             - Run all tests with coverage"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage    - Generate test coverage report"
	@echo "  make test-load        - Run load tests with Locust"
	@echo "  make lint             - Run linter (ruff check)"
	@echo "  make format           - Format code with ruff"
	@echo "  make check            - Run all checks (lint + test)"
	@echo "  make security-check   - Run security vulnerability checks"
	@echo "  make clean            - Clean up generated files"
	@echo ""
	@echo "$(GREEN)🗄️  Database Migrations:$(NC)"
	@echo "  make migrate          - Run Alembic migrations (schema only)"
	@echo "  make migrate-sql      - Apply SQL optimization scripts"
	@echo "  make migrate-all      - Run all migrations (Alembic + SQL)"
	@echo "  make migrate-down     - Downgrade migration by 1 revision"
	@echo "  make migrate-history  - Show migration history"
	@echo "  make migrate-current  - Show current migration revision"
	@echo "  make migrate-create   - Create new migration (prompts for message)"
	@echo ""
	@echo "$(GREEN)🐳 Docker Development:$(NC)"
	@echo "  make dev-up           - Start development with HOT-RELOAD (Uvicorn)"
	@echo "  make dev-down         - Stop development environment"
	@echo "  make dev-cleanup      - Stop and remove all containers, volumes, networks"
	@echo "  make dev-logs         - Show development logs (follow mode)"
	@echo "  make dev-restart      - Restart development services"
	@echo "  make dev-build        - Rebuild development images from scratch"
	@echo "  make dev-backend      - Start only database and Redis (for local dev)"
	@echo ""
	@echo "$(GREEN)🚀 Docker Production:$(NC)"
	@echo "  make prod-up          - Start production environment with Docker"
	@echo "  make prod-down        - Stop production environment"
	@echo "  make prod-logs        - Show production logs (follow mode)"
	@echo "  make prod-build       - Build production images"
	@echo ""
	@echo "$(GREEN)💾 Database Operations:$(NC)"
	@echo "  make db-shell         - Open PostgreSQL database shell"
	@echo "  make db-reset         - Reset database (drop and recreate)"
	@echo "  make db-seed          - Seed database with sample data"
	@echo "  make db-backup        - Backup database to file"
	@echo "  make db-restore       - Restore database from backup"
	@echo ""
	@echo "$(GREEN)🗂️  Cache Operations:$(NC)"
	@echo "  make cache-clear      - Clear all Redis cache"
	@echo "  make cache-info       - Show Redis cache statistics"
	@echo ""
	@echo "$(GREEN)⚙️  Celery Tasks:$(NC)"
	@echo "  make celery-worker    - Start Celery worker"
	@echo "  make celery-beat      - Start Celery beat scheduler"
	@echo "  make celery-flower    - Start Celery Flower monitoring"
	@echo ""
	@echo "$(GREEN)🧹 Cleanup:$(NC)"
	@echo "  make docker-clean     - Remove all Docker resources"
	@echo "  make docker-prune     - Prune unused Docker resources"
	@echo ""
	@echo "$(GREEN)🔧 Utilities:$(NC)"
	@echo "  make deps-update      - Update all dependencies"
	@echo ""

# ============================================================================
# LOCAL DEVELOPMENT
# ============================================================================

install:
	@echo "$(CYAN)📦 Installing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)✓ Dependencies installed successfully$(NC)"

dev:
	@echo "$(CYAN)📦 Installing dev dependencies with all extras...$(NC)"
	uv sync --all-extras
	@echo "$(GREEN)✓ Dev dependencies installed successfully$(NC)"

run:
	@echo "$(CYAN)🚀 Starting development server...$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:8000$(NC)"
	@echo "$(YELLOW)GraphQL Playground: http://localhost:8000/graphql$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# DATABASE MIGRATIONS
# ============================================================================

migrate:
	@echo "$(CYAN)🗄️  Running Alembic migrations...$(NC)"
	uv run alembic upgrade head
	@echo "$(GREEN)✓ Alembic migrations completed$(NC)"

migrate-sql:
	@echo "$(CYAN)🗄️  Applying SQL optimization scripts...$(NC)"
	@if ! docker compose ps | grep -q postgres; then \
		echo "$(RED)✗ ERROR: PostgreSQL container is not running$(NC)"; \
		echo "$(YELLOW)Start it with: make dev-up or make dev-backend$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Applying: 001_create_indexes.sql$(NC)"
	@docker compose exec -T postgres psql -U shopx -d shopx_analytics < migrations/versions/001_create_indexes.sql && echo "$(GREEN)✓ Indexes created$(NC)" || echo "$(RED)✗ Failed to create indexes$(NC)"
	@echo "$(YELLOW)Applying: 002_partition_orders.sql$(NC)"
	@docker compose exec -T postgres psql -U shopx -d shopx_analytics < migrations/versions/002_partition_orders.sql && echo "$(GREEN)✓ Partitions created$(NC)" || echo "$(RED)✗ Failed to create partitions$(NC)"
	@echo "$(YELLOW)Applying: 003_materialized_views.sql$(NC)"
	@docker compose exec -T postgres psql -U shopx -d shopx_analytics < migrations/versions/003_materialized_views.sql && echo "$(GREEN)✓ Materialized views created$(NC)" || echo "$(RED)✗ Failed to create materialized views$(NC)"
	@echo "$(YELLOW)Applying: 004_aggregation_tables.sql$(NC)"
	@docker compose exec -T postgres psql -U shopx -d shopx_analytics < migrations/versions/004_aggregation_tables.sql && echo "$(GREEN)✓ Aggregation tables created$(NC)" || echo "$(RED)✗ Failed to create aggregation tables$(NC)"
	@echo "$(GREEN)✓ All SQL optimizations applied successfully$(NC)"

migrate-all: migrate migrate-sql
	@echo "$(GREEN)✓ All migrations completed successfully!$(NC)"

migrate-down:
	@echo "$(CYAN)⬇️  Downgrading migration by 1 revision...$(NC)"
	uv run alembic downgrade -1
	@echo "$(GREEN)✓ Migration downgraded$(NC)"

migrate-history:
	@echo "$(CYAN)📋 Migration history:$(NC)"
	uv run alembic history

migrate-current:
	@echo "$(CYAN)📍 Current migration revision:$(NC)"
	uv run alembic current

migrate-create:
	@read -p "Enter migration message: " message; \
	echo "$(CYAN)📝 Creating new migration: $$message$(NC)"; \
	uv run alembic revision --autogenerate -m "$$message" && \
	echo "$(GREEN)✓ Migration created successfully$(NC)"

# ============================================================================
# TESTING
# ============================================================================

test:
	@echo "$(CYAN)🧪 Running all tests with coverage...$(NC)"
	uv run pytest
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-unit:
	@echo "$(CYAN)🧪 Running unit tests only...$(NC)"
	uv run pytest -m unit
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration:
	@echo "$(CYAN)🧪 Running integration tests only...$(NC)"
	uv run pytest -m integration
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

test-coverage:
	@echo "$(CYAN)📊 Generating test coverage report...$(NC)"
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated at htmlcov/index.html$(NC)"

test-load:
	@echo "$(CYAN)⚡ Running load tests with Locust...$(NC)"
	@if [ -f tests/performance/locustfile.py ]; then \
		uv run locust -f tests/performance/locustfile.py; \
	else \
		echo "$(RED)✗ locustfile.py not found in tests/performance/$(NC)"; \
	fi

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "$(CYAN)🔍 Running linter...$(NC)"
	uv run ruff check .
	@echo "$(GREEN)✓ Linting completed$(NC)"

format:
	@echo "$(CYAN)✨ Formatting code...$(NC)"
	uv run ruff format .
	uv run ruff check --fix .
	@echo "$(GREEN)✓ Code formatted successfully$(NC)"

check: lint test
	@echo "$(GREEN)✓ All checks passed!$(NC)"

security-check:
	@echo "$(CYAN)🔒 Running security checks...$(NC)"
	@echo "$(YELLOW)Checking for known vulnerabilities...$(NC)"
	uv run pip-audit 2>/dev/null || echo "$(YELLOW)Install pip-audit for security scanning: uv pip install pip-audit$(NC)"

clean:
	@echo "$(CYAN)🧹 Cleaning up generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	rm -f *.db
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

# ============================================================================
# DOCKER DEVELOPMENT
# ============================================================================

dev-up:
	@echo "$(CYAN)🐳 Starting development environment with HOT-RELOAD...$(NC)"
	@echo "$(YELLOW)⚡ Using Uvicorn with file watcher for auto-reload$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development environment is running with HOT-RELOAD!$(NC)"
	@echo "$(YELLOW)Backend API:        http://localhost:8000$(NC)"
	@echo "$(YELLOW)GraphQL Playground: http://localhost:8000/graphql$(NC)"
	@echo "$(YELLOW)API Docs:           http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)Frontend:           http://localhost:3000$(NC)"
	@echo "$(YELLOW)Redis:              localhost:6379$(NC)"
	@echo "$(YELLOW)PostgreSQL:         localhost:5432$(NC)"
	@echo ""
	@echo "$(CYAN)💡 Code changes will auto-reload! Watch logs: make dev-logs$(NC)"
	@echo "$(CYAN)📚 See docs/HOT_RELOAD.md for details$(NC)"

dev-backend:
	@echo "$(CYAN)🐳 Starting backend services only (no frontend)...$(NC)"
	docker compose up -d postgres redis
	@echo "$(GREEN)✓ Backend services are running!$(NC)"
	@echo "$(YELLOW)Redis:              localhost:6379$(NC)"
	@echo "$(YELLOW)PostgreSQL:         localhost:5432$(NC)"
	@echo ""
	@echo "$(CYAN)Now you can run migrations with: make migrate-all$(NC)"

dev-down:
	@echo "$(CYAN)🛑 Stopping development environment...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Development environment stopped$(NC)"

dev-cleanup:
	@echo "$(CYAN)🧹 Cleaning up development environment...$(NC)"
	docker compose down -v --remove-orphans
	@echo "$(GREEN)✓ Development environment cleaned up!$(NC)"

dev-logs:
	@echo "$(CYAN)📋 Showing development logs (Ctrl+C to exit)...$(NC)"
	@echo "$(YELLOW)💡 Look for 'WatchFiles detected changes' messages$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-restart:
	@echo "$(CYAN)🔄 Restarting development services...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

dev-build:
	@echo "$(CYAN)🔨 Building development images from scratch...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
	@echo "$(GREEN)✓ Development images built$(NC)"

# ============================================================================
# DOCKER PRODUCTION
# ============================================================================

prod-up:
	@echo "$(CYAN)🚀 Starting production environment...$(NC)"
	docker compose -f docker compose.prod.yml up -d
	@echo "$(GREEN)✓ Production environment is running!$(NC)"
	@echo "$(YELLOW)Application: http://localhost$(NC)"

prod-down:
	@echo "$(CYAN)🛑 Stopping production environment...$(NC)"
	docker compose -f docker compose.prod.yml down
	@echo "$(GREEN)✓ Production environment stopped$(NC)"

prod-logs:
	@echo "$(CYAN)📋 Showing production logs (Ctrl+C to exit)...$(NC)"
	docker compose -f docker compose.prod.yml logs -f

prod-build:
	@echo "$(CYAN)🔨 Building production images...$(NC)"
	docker compose -f docker compose.prod.yml build
	@echo "$(GREEN)✓ Production images built$(NC)"

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

db-shell:
	@echo "$(CYAN)💾 Opening database shell...$(NC)"
	@if docker compose ps | grep -q postgres; then \
		docker compose exec postgres psql -U shopx -d shopx_analytics; \
	else \
		echo "$(RED)✗ PostgreSQL container is not running$(NC)"; \
		echo "$(YELLOW)Start it with: make dev-up$(NC)"; \
	fi

db-reset:
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(CYAN)🔄 Resetting database...$(NC)"; \
		docker compose down -v; \
		docker compose up -d postgres redis; \
		echo "$(YELLOW)Waiting for database to be ready...$(NC)"; \
		sleep 5; \
		docker compose up -d backend; \
		docker compose exec backend uv run alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

db-seed:
	@echo "$(CYAN)🌱 Seeding database with sample data...$(NC)"
	@if [ -f scripts/seed_data.py ]; then \
		read -p "Enter number of records (default: 10000): " records; \
		records=$${records:-10000}; \
		uv run python scripts/seed_data.py --records $$records; \
		echo "$(GREEN)✓ Database seeded with $$records records$(NC)"; \
	else \
		echo "$(RED)✗ scripts/seed_data.py not found$(NC)"; \
	fi

db-backup:
	@echo "$(CYAN)💾 Creating database backup...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE="backups/db_backup_$$(date +%Y%m%d_%H%M%S).sql"; \
	if [ -n "$$DATABASE_URL" ]; then \
		pg_dump $$DATABASE_URL > $$BACKUP_FILE && \
		echo "$(GREEN)✓ Backup created: $$BACKUP_FILE$(NC)"; \
	else \
		docker compose exec -T postgres pg_dump -U shopx shopx_analytics > $$BACKUP_FILE && \
		echo "$(GREEN)✓ Backup created: $$BACKUP_FILE$(NC)"; \
	fi

db-restore:
	@echo "$(CYAN)💾 Restoring database from backup...$(NC)"
	@ls -1 backups/*.sql 2>/dev/null | tail -1 | xargs -I {} sh -c 'echo "Latest backup: {}"' || echo "$(RED)No backups found$(NC)"
	@read -p "Enter backup file path: " backup_file; \
	if [ -f "$$backup_file" ]; then \
		echo "$(YELLOW)Restoring from $$backup_file...$(NC)"; \
		if [ -n "$$DATABASE_URL" ]; then \
			psql $$DATABASE_URL < $$backup_file && \
			echo "$(GREEN)✓ Database restored$(NC)"; \
		else \
			docker compose exec -T postgres psql -U shopx shopx_analytics < $$backup_file && \
			echo "$(GREEN)✓ Database restored$(NC)"; \
		fi \
	else \
		echo "$(RED)✗ Backup file not found$(NC)"; \
	fi

# ============================================================================
# CACHE OPERATIONS
# ============================================================================

cache-clear:
	@echo "$(CYAN)🗑️  Clearing Redis cache...$(NC)"
	@if docker compose ps | grep -q redis; then \
		docker compose exec redis redis-cli -a changeme FLUSHALL && \
		echo "$(GREEN)✓ Cache cleared$(NC)"; \
	elif command -v redis-cli >/dev/null 2>&1; then \
		redis-cli FLUSHALL && \
		echo "$(GREEN)✓ Cache cleared$(NC)"; \
	else \
		echo "$(RED)✗ Redis is not running$(NC)"; \
	fi

cache-info:
	@echo "$(CYAN)📊 Redis cache statistics:$(NC)"
	@if docker compose ps | grep -q redis; then \
		docker compose exec redis redis-cli -a changeme INFO stats; \
	elif command -v redis-cli >/dev/null 2>&1; then \
		redis-cli INFO stats; \
	else \
		echo "$(RED)✗ Redis is not running$(NC)"; \
	fi

# ============================================================================
# CELERY TASKS
# ============================================================================

celery-worker:
	@echo "$(CYAN)⚙️  Starting Celery worker...$(NC)"
	uv run celery -A src.celery_app worker --loglevel=info

celery-beat:
	@echo "$(CYAN)⏰ Starting Celery beat scheduler...$(NC)"
	uv run celery -A src.celery_app beat --loglevel=info

celery-flower:
	@echo "$(CYAN)🌸 Starting Celery Flower monitoring...$(NC)"
	@echo "$(YELLOW)Flower UI: http://localhost:5555$(NC)"
	uv run celery -A src.celery_app flower

# ============================================================================
# DOCKER CLEANUP
# ============================================================================

docker-clean:
	@echo "$(RED)⚠️  WARNING: This will remove ALL Docker resources for this project!$(NC)"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(CYAN)🧹 Cleaning Docker resources...$(NC)"; \
		docker compose down -v --remove-orphans; \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ All Docker resources cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)Docker cleanup cancelled$(NC)"; \
	fi

docker-prune:
	@echo "$(CYAN)🧹 Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Unused Docker resources pruned$(NC)"

# ============================================================================
# UTILITIES
# ============================================================================

deps-update:
	@echo "$(CYAN)📦 Updating dependencies...$(NC)"
	uv sync --upgrade
	@echo "$(GREEN)✓ Dependencies updated$(NC)"
