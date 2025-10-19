# Architecture Overview

This document describes the architecture and design decisions of the URL Shortener application.

## System Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────┐
│        React Frontend           │
│    (Vite + TypeScript)          │
└──────────┬──────────────────────┘
           │ REST API
           ▼
┌────────────────────────────────┐
│      FastAPI Backend           │
│  ┌──────────────────────────┐  │
│  │    API Layer (v1)        │  │
│  │  - Route Handlers        │  │
│  │  - Request Validation    │  │
│  │  - Response Serialization│  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │    Service Layer         │  │
│  │  - Business Logic        │  │
│  │  - Data Validation       │  │
│  │  - Short Code Generation │  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │    Data Access Layer     │  │
│  │  - SQLAlchemy Models     │  │
│  │  - Async Database Ops    │  │
│  └──────────┬───────────────┘  │
└─────────────┼───────────────────┘
              │
              ▼
       ┌─────────────┐
       │  Database   │
       │(SQLite/PG)  │
       └─────────────┘
```

## Backend Architecture

### Layered Architecture

The backend follows a clean layered architecture:

#### 1. API Layer (`src/api/`)
- **Responsibility**: HTTP request/response handling
- **Components**: FastAPI routers, endpoint functions
- **Key Files**: `api/v1/endpoints/urls.py`

```python
# Thin controller layer
@router.post("/", response_model=URLResponse)
async def create_url(
    url_create: URLCreate,
    db: AsyncSession = Depends(get_db)
):
    """Handle HTTP request, delegate to service."""
    try:
        url = await URLService.create_short_url(db, url_create)
        return to_response(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 2. Service Layer (`src/services/`)
- **Responsibility**: Business logic
- **Components**: Service classes with static methods
- **Key Files**: `services/url_service.py`

```python
# Business logic encapsulated
class URLService:
    @staticmethod
    async def create_short_url(
        db: AsyncSession,
        url_create: URLCreate
    ) -> URL:
        """Create shortened URL with business logic."""
        # Validation
        # Code generation
        # Database operations
        return url
```

#### 3. Data Access Layer (`src/models/`)
- **Responsibility**: Database operations
- **Components**: SQLAlchemy models
- **Key Files**: `models/url.py`

```python
# Database model
class URL(Base):
    __tablename__ = "urls"
    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(unique=True)
```

#### 4. Schema Layer (`src/schemas/`)
- **Responsibility**: Data validation and serialization
- **Components**: Pydantic models
- **Key Files**: `schemas/url.py`

```python
# Request/Response schemas
class URLCreate(BaseModel):
    url: HttpUrl
    custom_code: str | None = None

class URLResponse(BaseModel):
    id: int
    short_code: str
    short_url: str
```

### Core Components

#### Configuration (`src/core/config.py`)
- Centralized configuration using Pydantic Settings
- Environment variable management
- Type-safe settings

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
```

#### Database (`src/core/database.py`)
- Async SQLAlchemy engine setup
- Session management
- Dependency injection for database sessions

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

## Design Patterns

### 1. Dependency Injection

Using FastAPI's `Depends()` for clean dependency management:

```python
async def endpoint(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    pass
```

**Benefits:**
- Testable (easy to mock dependencies)
- Maintainable (centralized dependency creation)
- Type-safe (IDE support)

### 2. Service Layer Pattern

Business logic separated from HTTP concerns:

```python
# Good - Service contains logic
class URLService:
    @staticmethod
    async def create_short_url(db, data):
        # Business logic here
        pass

# Controller delegates to service
@router.post("/")
async def create(data: URLCreate, db = Depends(get_db)):
    return await URLService.create_short_url(db, data)
```

**Benefits:**
- Reusable logic
- Testable without HTTP layer
- Single responsibility

### 3. Repository Pattern (Implicit)

SQLAlchemy acts as our repository:

```python
# Query through SQLAlchemy
result = await db.execute(
    select(URL).where(URL.short_code == code)
)
url = result.scalar_one_or_none()
```

**Benefits:**
- Abstracted database operations
- Type-safe queries
- Async support

### 4. Factory Pattern (Session Factory)

Database sessions created via factory:

```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

## Data Flow

### Creating a Short URL

```
1. Client sends POST request
   └─> {"url": "https://example.com"}

2. FastAPI validates against URLCreate schema
   └─> Pydantic validation

3. API layer receives validated data
   └─> create_url(url_create: URLCreate)

4. Service layer processes
   ├─> Generate or validate short code
   ├─> Check for duplicates
   └─> Create database record

5. Database layer persists
   └─> SQLAlchemy creates URL record

6. Response serialized
   └─> URLResponse schema

7. Client receives response
   └─> {"id": 1, "short_code": "abc123", ...}
```

### Redirecting (Click Tracking)

```
1. Client requests GET /{short_code}

2. Service layer fetches URL
   └─> Query by short_code

3. Service increments click count
   └─> url.clicks += 1

4. Transaction committed
   └─> db.commit()

5. HTTP 307 redirect issued
   └─> Location: original_url
```

## Database Design

### Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY,
    original_url VARCHAR NOT NULL,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_original_url ON urls(original_url);
CREATE INDEX idx_short_code ON urls(short_code);
```

### Indexes

- `short_code`: Unique index for fast lookups on redirect
- `original_url`: Index for potential duplicate detection

### Constraints

- `short_code`: UNIQUE constraint prevents duplicates
- `original_url`: NOT NULL ensures data integrity

## Async Architecture

### Why Async?

1. **I/O Bound Operations**: Database queries, HTTP requests
2. **Concurrency**: Handle multiple requests simultaneously
3. **Performance**: Non-blocking operations

### Async Flow

```python
# Async all the way
async def endpoint(db: AsyncSession = Depends(get_db)):
    # Async service call
    url = await URLService.create_short_url(db, data)
    return url

# Service uses async database
class URLService:
    @staticmethod
    async def create_short_url(db: AsyncSession, data):
        # Async database query
        result = await db.execute(select(URL))
        return result.scalar_one()
```

### Session Management

```python
# Async context manager
async with AsyncSessionLocal() as session:
    try:
        yield session
        await session.commit()  # Async commit
    except Exception:
        await session.rollback()  # Async rollback
```

## Error Handling

### Layered Error Handling

```python
# Service layer raises domain exceptions
class URLService:
    async def create_short_url(...):
        if exists:
            raise ValueError("Code already taken")

# API layer converts to HTTP errors
@router.post("/")
async def create_url(...):
    try:
        url = await URLService.create_short_url(...)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Error Response Format

```json
{
  "detail": "Error message"
}
```

## API Versioning

### URL-based Versioning

```
/api/v1/urls/     <- Version 1
/api/v2/urls/     <- Future version 2
```

**Benefits:**
- Clear version separation
- Backward compatibility
- Easy to maintain multiple versions

### Version Structure

```
api/
├── __init__.py
├── v1/
│   ├── __init__.py
│   └── endpoints/
│       └── urls.py
└── v2/           # Future
    └── endpoints/
```

## Security Considerations

### Input Validation

- Pydantic schemas validate all inputs
- URL format validation (HttpUrl)
- Custom code pattern validation

### SQL Injection Prevention

- SQLAlchemy ORM (parameterized queries)
- No raw SQL in application code

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True
)
```

### Future Security Features

- Rate limiting
- API key authentication
- Request signing
- IP whitelisting

## Scalability Considerations

### Current Design

- **Vertical Scaling**: Increase server resources
- **Connection Pooling**: SQLAlchemy manages connections
- **Async**: Handle many concurrent requests

### Future Enhancements

#### 1. Caching Layer
```
┌─────────┐
│  Redis  │  <- Cache hot short codes
└────┬────┘
     │
     ▼
┌─────────┐
│Database │
└─────────┘
```

#### 2. Read Replicas
```
┌─────────┐
│ Primary │  <- Writes
└────┬────┘
     │
     ├─> Read Replica 1
     └─> Read Replica 2
```

#### 3. Horizontal Scaling
```
Load Balancer
    ├─> App Server 1
    ├─> App Server 2
    └─> App Server 3
         │
         ▼
    Shared Database
```

## Monitoring & Observability

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": VERSION}
```

### Metrics (Future)

- Request count
- Response times
- Error rates
- Click-through rates

### Logging

- Structured logging with context
- Error tracking
- Performance monitoring

## Frontend Architecture

### Component Structure (Planned)

```
src/
├── components/
│   ├── URLShortener.tsx    # Main form
│   ├── URLList.tsx         # List view
│   └── URLStats.tsx        # Statistics
├── services/
│   └── api.ts              # API client
├── hooks/
│   └── useURLs.ts          # Custom hooks
└── types/
    └── url.ts              # TypeScript types
```

### State Management

- React hooks for local state
- Context API for global state
- Future: Consider Zustand/Redux for complex state

## Development Workflow

```
Developer
    │
    ├─> Code Changes
    │
    ├─> Run Tests (pytest)
    │
    ├─> Linting (ruff)
    │
    ├─> Commit (pre-commit hooks)
    │
    └─> CI/CD Pipeline
         ├─> Run Tests
         ├─> Check Coverage
         ├─> Deploy
         └─> Monitor
```

## Deployment Architecture

### Development
```
Local Machine
├─> SQLite Database
└─> Single Process
```

### Production
```
Load Balancer
    ├─> App Server 1 (Docker)
    ├─> App Server 2 (Docker)
    └─> App Server 3 (Docker)
         │
         ▼
    PostgreSQL (RDS)
         │
         ▼
    Backup Storage
```

## Technology Choices

### Why FastAPI?
- **Performance**: Async support, fast
- **Type Safety**: Pydantic integration
- **Documentation**: Auto-generated OpenAPI docs
- **Modern**: Python 3.12+ features

### Why SQLAlchemy?
- **Async Support**: Native async/await
- **Type Safety**: 2.0 style with Mapped types
- **Flexibility**: Works with multiple databases
- **Migrations**: Alembic integration

### Why uv?
- **Speed**: 10-100x faster than pip
- **Simplicity**: Single tool for everything
- **Modern**: Built in Rust
- **Compatible**: Works with existing projects

### Why React + Vite?
- **Performance**: Fast build times
- **Modern**: Latest React features
- **Developer Experience**: HMR, TypeScript
- **Ecosystem**: Large community

## Future Enhancements

### Phase 1 (MVP) - ✅ Complete
- URL shortening
- Custom codes
- Click tracking
- Basic API

### Phase 2 (Planned)
- User authentication
- URL expiration
- Analytics dashboard
- QR code generation

### Phase 3 (Future)
- Custom domains
- A/B testing
- Team collaboration
- Advanced analytics

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [React Documentation](https://react.dev/)
