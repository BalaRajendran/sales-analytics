# URL Shortener - Project Knowledge

## Project Overview

A modern, full-stack URL shortener application built with FastAPI (backend) and React + Vite (frontend).

### Tech Stack

**Backend:**
- FastAPI (async web framework)
- SQLAlchemy (async ORM)
- Alembic (database migrations)
- Pydantic (validation)
- uv (package manager)
- Python 3.12+

**Frontend:**
- React 19
- Vite
- TypeScript
- ESLint

## Architecture

### Backend Architecture

```
src/
├── api/v1/endpoints/    # API route handlers
├── core/                # Core application components
│   ├── config.py        # Application settings
│   ├── database.py      # Database configuration
│   ├── exceptions.py    # Custom exception classes
│   └── exception_handlers.py  # Exception handler registration
├── middleware/          # Custom middleware (rate limiting)
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic request/response schemas
│   ├── common.py        # Common schemas (ApiResponse, etc.)
│   ├── url.py           # URL-specific schemas
│   └── validation.py    # Validation utilities
├── services/            # Business logic layer
└── utils/              # Helper utilities
```

**Key Patterns:**
- **Service Layer Pattern**: Business logic separated from API routes
- **Async/Await**: All database operations are async
- **Dependency Injection**: FastAPI's `Depends()` for database sessions
- **Type Safety**: Full type hints throughout codebase
- **Centralized Exception Handling**: All exception handlers in `src/core/exception_handlers.py`

### Database Schema

**URL Model:**
```python
- id: int (primary key)
- original_url: str (indexed)
- short_code: str (unique, indexed)
- clicks: int (default=0)
- created_at: datetime
- updated_at: datetime
```

## API Endpoints

Base URL: `/api/v1`

### Standardized Response Format

**All API endpoints follow a standardized response format:**

**Success Response:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "error_code": null,
  "error_message": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": { /* optional error context */ },
  "error_code": "ERROR_CODE",
  "error_message": "Human-readable message"
}
```

### URLs Endpoints (`/urls`)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | `/urls/` | Create shortened URL | ApiResponse[URLResponse] |
| GET | `/urls/` | List all URLs (paginated) | ApiResponse[list[URLResponse]] |
| GET | `/urls/{short_code}` | Redirect to original URL | HTTP 307 Redirect* |
| GET | `/urls/{short_code}/stats` | Get URL statistics | ApiResponse[URLStats] |
| DELETE | `/urls/{short_code}` | Delete a URL | ApiResponse[dict] |

*Note: Redirect endpoint returns HTTP redirect, not JSON response

## Development Workflow

### Backend Setup
```bash
# From project root
make dev              # Install dependencies
make migration        # Create migration
make migrate          # Apply migrations
make run              # Start server
```

### Testing
```bash
make test             # Run all tests
make lint             # Lint code
make format           # Format code
```

## Configuration

### Environment Variables

Located in `.env` (root directory):

```env
# Application
PROJECT_NAME="URL Shortener API"
DEBUG=true
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db

# URL Settings
SHORT_URL_LENGTH=6
BASE_URL=http://localhost:8000

# Security
SECRET_KEY=your-secret-key
```

## Error Handling

**Custom Exception Classes:**
All errors use custom exceptions from `src.core.exceptions`:
- `NotFoundError` (404)
- `ConflictError` (409)
- `ValidationError` (422)
- `BadRequestError` (400)
- `RateLimitError` (429)
- `InternalServerError` (500)
- `DatabaseError` (500)

**Error Codes:**
Machine-readable error codes for programmatic handling:
- `NOT_FOUND`, `CONFLICT`, `VALIDATION_ERROR`
- `BAD_REQUEST`, `UNAUTHORIZED`, `FORBIDDEN`
- `RATE_LIMIT_EXCEEDED`, `INTERNAL_ERROR`
- `DATABASE_ERROR`, `SERVICE_UNAVAILABLE`

See [docs/api/ERROR_CODES.md](../docs/api/ERROR_CODES.md) for complete reference.

## Code Quality

- **Linting**: Ruff (similar to reference project)
- **Formatting**: Ruff format
- **Pre-commit hooks**: Configured
- **Testing**: pytest with async support
- **Coverage**: Minimum 80% (configured in pyproject.toml)
- **Response Format**: Standardized JSON responses for all endpoints
- **Error Handling**: Custom exceptions with error codes

## Common Commands

```bash
# Backend
make dev           # Install all dependencies
make run           # Start dev server
make test          # Run tests
make lint          # Check code quality
make format        # Auto-format code
make migration     # Create new migration
make migrate       # Apply migrations
make clean         # Clean generated files

# Frontend
npm run dev        # Start dev server
npm run build      # Build for production
npm run lint       # Lint code
```

## Project Structure

```
url-shortner/
├── .claude/                    # Claude AI project context
├── docs/                       # Documentation
├── src/                        # Backend source code
│   ├── api/v1/                       # API endpoints
│   ├── core/                         # Config & database
│   ├── models/                       # Database models
│   ├── schemas/                      # Pydantic schemas
│   └── services/                     # Business logic
├── tests/                      # Backend tests
│   ├── unit/                         # Unit tests
│   └── integration/                  # Integration tests
├── migrations/                 # Alembic migrations
├── scripts/                    # Utility scripts
├── frontend/                   # React frontend
├── pyproject.toml              # Python dependencies
├── alembic.ini                 # Alembic configuration
├── Makefile                    # Development commands
├── .env                        # Environment config
└── README.md                   # Project overview
```

## Key Files

- `src/main.py` - FastAPI application entry point
- `src/core/config.py` - Settings with Pydantic
- `src/core/database.py` - Database setup
- `src/core/exceptions.py` - Custom exception classes
- `src/core/exception_handlers.py` - Centralized exception handlers
- `src/services/url_service.py` - Core business logic
- `src/schemas/common.py` - Common schemas and response wrappers
- `pyproject.toml` - Project configuration

## Testing Strategy

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test API endpoints end-to-end
- **Test Fixtures**: Shared in `tests/conftest.py`
- **In-memory DB**: Tests use SQLite in-memory for speed

## Deployment Considerations

### Database
- Development: SQLite
- Production: PostgreSQL recommended
- Change DATABASE_URL for PostgreSQL:
  ```
  postgresql+asyncpg://user:pass@host:5432/dbname
  ```

### Environment
- Set `DEBUG=false` in production
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set correct `BASE_URL`

## Dependencies Management

Using `uv` for ultra-fast dependency management:
- `uv sync` - Install dependencies
- `uv sync --all-extras` - Install with dev dependencies
- `uv add package` - Add new dependency
- `uv remove package` - Remove dependency

## Reference Project

This project is based on the structure of `/Volumes/aracor/repo/aracor-be-api`, adopting:
- Project structure and organization
- Ruff configuration
- Testing setup
- Pre-commit hooks
- Service layer pattern
- Async database patterns

## Rate Limiting

The API implements comprehensive rate limiting to prevent abuse:

**Implementation:**
- In-memory sliding window algorithm
- Per-endpoint rate limits
- Client identification via user_id > api_key > ip > user_agent
- Rate limit headers in all responses

**Default Limits:**
- General endpoints: 100 requests/minute
- Create URL: 30 requests/minute
- Bulk operations: 5 requests/minute
- Health check: 1000 requests/minute

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 45
```

**Configuration:**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_CREATE_URL=30
RATE_LIMIT_BULK_OPERATIONS=5
```

See [docs/api/RATE_LIMITING.md](../docs/api/RATE_LIMITING.md) for complete documentation.

## Input Validation

Comprehensive Pydantic validation ensures data integrity and security:

**URL Validation:**
- Scheme: Must be http/https
- Length: Maximum 2048 characters
- Safety checks: Blocks javascript:, data:, XSS patterns, path traversal
- Format validation with HttpUrl

**Custom Code Validation:**
- Length: 4-10 characters
- Pattern: `^[a-zA-Z0-9_-]+$`
- Reserved codes blocked (api, admin, health, etc.)
- Uniqueness check

**Tags Validation:**
- Maximum 10 tags per URL
- Each tag: 1-50 characters
- Pattern: `^[a-zA-Z0-9_-]+$`
- Duplicate removal (case-insensitive)

**Security Features:**
- XSS prevention
- Path traversal blocking
- Null byte detection
- Excessive URL encoding limits

See [docs/api/VALIDATION.md](../docs/api/VALIDATION.md) for complete documentation.

## Future Enhancements

Potential features to add:
- User authentication
- Custom domains
- Analytics dashboard
- QR code generation
- Link expiration
- Bulk URL creation
- API key authentication
- Distributed rate limiting with Redis
