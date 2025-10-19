# Development Setup Guide

Complete guide for setting up the URL Shortener development environment.

## Prerequisites

### Required Software

1. **Python 3.12+**
   ```bash
   python --version  # Should be 3.12 or higher
   ```

2. **uv (Python Package Manager)**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip
   pip install uv
   ```

3. **Bun 1.0+** (for frontend)
   ```bash
   bun --version  # Should be 1.0 or higher

   # Install Bun
   # macOS/Linux
   curl -fsSL https://bun.sh/install | bash

   # Windows
   powershell -c "irm bun.sh/install.ps1|iex"
   ```

4. **Git**
   ```bash
   git --version
   ```

### Optional Tools

- **Make** - For using Makefile commands
- **PostgreSQL** - For production-like database
- **Docker** - For containerized development
- **VS Code** - Recommended IDE with Python extension

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
# Install all dependencies including dev tools
make dev

# Or manually
uv sync --all-extras
```

This will:
- Create a virtual environment automatically
- Install all dependencies from `pyproject.toml`
- Install dev dependencies (pytest, ruff, etc.)

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Key settings to configure:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db

# Or PostgreSQL for production-like environment
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/url_shortener

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# URL Settings
SHORT_URL_LENGTH=6
BASE_URL=http://localhost:8000
```

### 4. Set Up Database

```bash
# Create initial migration
make migration
# When prompted, enter: "Initial migration"

# Apply migrations to create tables
make migrate
```

**Alternative (using uv directly):**
```bash
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

### 5. Run the Development Server

```bash
make run
```

**Alternative (using uvicorn directly):**
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### 6. Verify Installation

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "version": "0.1.0"}
```

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
bun install
```

### 3. Start Development Server

```bash
bun run dev
```

The frontend will be available at: http://localhost:5173

## Development Tools Setup

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
cd backend
uv run pre-commit install
```

This will run linting and formatting before each commit.

### VS Code Setup

Recommended VS Code extensions:

1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **Ruff** (charliermarsh.ruff)
4. **ES Lint** (dbaeumer.vscode-eslint)

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.lint.run": "onSave",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

## Database Setup Options

### SQLite (Development)

Default configuration, no additional setup needed:

```env
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db
```

### PostgreSQL (Production-like)

1. **Install PostgreSQL:**
   ```bash
   # macOS
   brew install postgresql@16
   brew services start postgresql@16

   # Ubuntu
   sudo apt install postgresql-16
   sudo systemctl start postgresql
   ```

2. **Create Database:**
   ```bash
   createdb url_shortener
   ```

3. **Update .env:**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/url_shortener
   ```

4. **Run Migrations:**
   ```bash
   make migrate
   ```

### Docker PostgreSQL

```bash
# Start PostgreSQL container
docker run -d \
  --name url-shortener-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=url_shortener \
  -p 5432:5432 \
  postgres:16

# Update .env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/url_shortener

# Run migrations
make migrate
```

## Running Tests

### Run All Tests

```bash
cd backend
make test
```

### Run Specific Tests

**Advanced pytest usage (for fine-grained control):**
```bash
# Integration tests only
uv run pytest tests/integration/

# Specific test file
uv run pytest tests/integration/test_urls.py

# Specific test function
uv run pytest tests/integration/test_urls.py::test_create_url

# With coverage report
uv run pytest --cov=src --cov-report=html
```

### View Coverage Report

```bash
# After running: make test
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Code Quality Tools

### Linting

```bash
make lint

# Alternative (using ruff directly)
uv run ruff check .
```

### Formatting

```bash
make format

# Alternative (using ruff directly)
uv run ruff format .
uv run ruff check --fix .
```

### Type Checking

```bash
# Install mypy
uv add --dev mypy

# Run type checking
uv run mypy src
```

## Common Development Tasks

### Create New Migration

```bash
make migration
# Enter migration message when prompted

# Alternative (using alembic directly)
uv run alembic revision --autogenerate -m "Add new field to URL model"
```

### Apply Migrations

```bash
make migrate

# Alternative (using alembic directly)
uv run alembic upgrade head
```

### Rollback Migration

**Advanced alembic commands:**
```bash
# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>
```

### View Migration History

**Advanced alembic commands:**
```bash
uv run alembic history
```

### Add New Dependency

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name
```

### Remove Dependency

```bash
uv remove package-name
```

### Clean Up Generated Files

```bash
make clean
```

## Troubleshooting

### Backend Won't Start

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.12+
   ```

2. **Reinstall dependencies:**
   ```bash
   make dev
   ```

3. **Check for port conflicts:**
   ```bash
   lsof -i :8000  # See what's using port 8000
   ```

### Database Errors

1. **Delete database and recreate:**
   ```bash
   rm url_shortener.db
   make migration
   make migrate
   ```

2. **Check database URL:**
   ```bash
   echo $DATABASE_URL
   cat .env | grep DATABASE_URL
   ```

### Migration Errors

1. **View current revision:**
   ```bash
   # Advanced alembic command
   uv run alembic current
   ```

2. **Reset migrations (development only):**
   ```bash
   # Delete migrations
   rm migrations/versions/*.py

   # Delete database
   rm url_shortener.db

   # Recreate
   make migration  # Enter message when prompted
   make migrate
   ```

### Import Errors

1. **Check PYTHONPATH:**
   ```bash
   echo $PYTHONPATH
   ```

2. **Run from backend directory:**
   ```bash
   cd backend
   uv run python -c "import src; print(src.__file__)"
   ```

### Frontend Won't Start

1. **Delete node_modules:**
   ```bash
   rm -rf node_modules bun.lockb
   bun install
   ```

2. **Check Bun version:**
   ```bash
   bun --version  # Should be 1.0+
   ```

## Development Workflow

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   cd backend && make dev
   cd ../frontend && bun install
   ```

3. **Run migrations:**
   ```bash
   cd backend && make migrate
   ```

4. **Start servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && make run

   # Terminal 2 - Frontend
   cd frontend && bun run dev
   ```

5. **Make changes and test:**
   ```bash
   # Run tests
   cd backend && make test

   # Check code quality
   make lint
   make format
   ```

6. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

## Next Steps

- Read [API Reference](../api/API_REFERENCE.md) for API details
- Check [Testing Guide](TESTING_GUIDE.md) for testing best practices
- Review [Code Conventions](../../.claude/conventions.md) for coding standards
- See [Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md) for production setup
