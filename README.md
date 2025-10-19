# Sales Dashboard API - FastAPI Template

A modern, production-ready FastAPI template for building sales analytics dashboards and APIs. This project provides a clean architecture with best practices, ready for you to build your sales dashboard APIs from scratch.

## 🎯 Purpose

This is a **template project** with established patterns and infrastructure. The URL shortener example has been replaced with generic templates. You can reuse the code patterns to build your sales dashboard APIs.

📖 **New here?** Check out the **[TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)** for a complete step-by-step walkthrough of building your first sales API!

## Project Structure

```
sales-dashboard-api/
├── .claude/                # Claude AI project context
├── docs/                   # 📚 Complete documentation
│   ├── QUICKSTART.md                # 5-minute setup guide
│   ├── api/                         # API documentation
│   ├── development/                 # Development guides
│   ├── deployment/                  # Deployment guides
│   └── architecture/                # Architecture docs
├── src/                    # Backend source code
│   ├── api/                         # API endpoints
│   │   └── v1/
│   │       └── endpoints/           # API route handlers
│   │           └── example_endpoints.py  # Template endpoint file
│   ├── core/                        # Configuration & database
│   │   ├── config.py                # Application settings
│   │   ├── database.py              # Database setup
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── exception_handlers.py   # Exception handlers
│   ├── models/                      # Database models (SQLAlchemy)
│   │   └── example_model.py        # Template model file
│   ├── schemas/                     # Pydantic schemas
│   │   ├── common.py                # Shared schemas
│   │   └── example_schema.py       # Template schema file
│   ├── services/                    # Business logic
│   │   └── example_service.py      # Template service file
│   └── middleware/                  # Custom middleware
├── tests/                  # Backend tests
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
├── migrations/             # Database migrations (Alembic)
├── scripts/                # Utility scripts
├── frontend/               # React + Vite frontend
├── pyproject.toml          # Python dependencies
├── alembic.ini             # Alembic configuration
├── Makefile                # Development commands
└── README.md               # This file
```

## ✨ Features & Patterns

This template includes:

- ✅ **Clean Architecture**: Layered design (API → Service → Model)
- ✅ **FastAPI Best Practices**: Async/await, dependency injection, Pydantic validation
- ✅ **Database Setup**: SQLAlchemy with async support, Alembic migrations
- ✅ **Error Handling**: Comprehensive exception handling with custom exceptions
- ✅ **API Patterns**: CRUD operations, pagination, filtering, sorting
- ✅ **Rate Limiting**: Built-in rate limiting middleware
- ✅ **CORS Configuration**: Ready for frontend integration
- ✅ **Docker Support**: Multi-container setup with Docker Compose
- ✅ **Testing Framework**: pytest with async support
- ✅ **Type Safety**: Full Python type hints
- ✅ **Code Quality**: Ruff for linting and formatting
- ✅ **Documentation**: Auto-generated OpenAPI/Swagger docs

## Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy** - Async ORM with SQLite/PostgreSQL support
- **Alembic** - Database migrations
- **uv** - Ultra-fast Python package manager
- **Ruff** - Fast Python linter and formatter
- **pytest** - Testing framework

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety
- **ESLint** - Code linting

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Bun](https://bun.sh) 1.0+ for frontend package management
- [uv](https://github.com/astral-sh/uv) for Python package management

### 1. Backend Setup

```bash
# Install dependencies
make dev

# Set up environment
cp .env.example .env

# Edit .env to configure your database and settings

# Run migrations (after creating your models)
make migration  # Create initial migration
make migrate    # Apply migrations

# Start server
make run
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/api/v1/docs

### 2. Create Your First Sales API

Follow this pattern to create your sales dashboard endpoints:

1. **Define Model** (`src/models/sale.py`):
   - Copy `example_model.py` as a reference
   - Define your database table structure

2. **Create Schema** (`src/schemas/sale.py`):
   - Copy `example_schema.py` as a reference
   - Define request/response schemas

3. **Build Service** (`src/services/sale_service.py`):
   - Copy `example_service.py` as a reference
   - Implement business logic

4. **Add Endpoint** (`src/api/v1/endpoints/sales.py`):
   - Copy `example_endpoints.py` as a reference
   - Create API routes

5. **Register Router** (`src/api/v1/__init__.py`):
   ```python
   from src.api.v1.endpoints import sales
   api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
   ```

6. **Create Migration**:
   ```bash
   make migration  # Creates migration for your new model
   make migrate    # Applies the migration
   ```

### 3. Frontend Setup (Optional)

```bash
cd frontend

# Install dependencies
bun install

# Start development server
bun run dev
```

Frontend will be available at: http://localhost:5173

## 📚 Documentation

Complete documentation is available in the [`docs/`](docs/) folder:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[API Reference](docs/api/API_REFERENCE.md)** - Complete API documentation
- **[Setup Guide](docs/development/SETUP_GUIDE.md)** - Detailed development setup
- **[Testing Guide](docs/development/TESTING_GUIDE.md)** - Write and run tests
- **[Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[EC2 Docker Deployment](docs/deployment/EC2_DOCKER_DEPLOYMENT.md)** - Complete Docker deployment to EC2
- **[Architecture](docs/architecture/ARCHITECTURE.md)** - System architecture
- **[Documentation Index](docs/README.md)** - Full documentation index

## Development

### Backend Commands

```bash
make install    # Install dependencies
make dev        # Install with dev dependencies
make run        # Start dev server
make migrate    # Run migrations
make migration  # Create new migration
make test       # Run tests
make lint       # Lint code
make format     # Format code
make clean      # Clean generated files
```

### Frontend Commands

```bash
cd frontend

bun run dev     # Start dev server
bun run build   # Build for production
bun run preview # Preview production build
bun run lint    # Lint code
```

## 🔌 API Documentation

Once the backend is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

### Example API Patterns Included

The template includes example endpoints demonstrating:

- ✅ **CRUD Operations**: Create, Read, Update, Delete
- ✅ **List with Pagination**: `GET /api/v1/examples?skip=0&limit=100`
- ✅ **Filtering & Search**: `GET /api/v1/examples?search=query`
- ✅ **Sorting**: `GET /api/v1/examples?sort_by=created_at&sort_order=desc`
- ✅ **Statistics**: `GET /api/v1/examples/stats/summary`

Build your sales dashboard endpoints following these patterns!

## Environment Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./sales_dashboard.db
# For PostgreSQL: postgresql+asyncpg://user:password@localhost/sales_db

# Application
DEBUG=true
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# CORS (adjust for your frontend URL)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

## Testing

### Backend Tests

```bash
# Run all tests
make test

# With coverage report (advanced)
make test
# Then view coverage: open htmlcov/index.html

# Or use pytest directly for custom coverage options
uv run pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend
bun run test  # When tests are set up
```

## 🚢 Deployment

### Docker Deployment (Recommended)

The template includes production-ready Docker configuration:

**Quick Docker Start:**
```bash
# Production deployment
make prod-up
```

For detailed deployment guides, see:
- **[EC2 Docker Deployment Guide](docs/deployment/EC2_DOCKER_DEPLOYMENT.md)** - Complete Docker deployment
- **[General Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - Traditional deployment options

### Deployment Checklist

Before deploying to production:

1. ✅ Update `SECRET_KEY` in `.env` with a strong secret
2. ✅ Set `DEBUG=false` in production environment
3. ✅ Configure production database (PostgreSQL recommended)
4. ✅ Update `CORS_ORIGINS` with your frontend domain
5. ✅ Set up SSL/TLS certificates
6. ✅ Configure rate limiting for your use case
7. ✅ Set up monitoring and logging
8. ✅ Run security audit: `make lint`

## 🏗️ Architecture

See the [Architecture Documentation](docs/architecture/ARCHITECTURE.md) for a detailed overview of the system design.

### Backend Architecture

- **FastAPI** application with async/await support
- **SQLAlchemy** for database operations with async sessions
- **Service layer** pattern for business logic
- **Pydantic** schemas for validation
- **Alembic** for database migrations

### Frontend Architecture

- **React** with hooks for state management
- **Vite** for fast builds and HMR
- **TypeScript** for type safety
- **Component-based** architecture

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on the GitHub repository.
