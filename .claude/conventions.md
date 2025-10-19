# Code Conventions & Best Practices

## Python Code Style

### General Principles
- Follow PEP 8 with modifications from Ruff configuration
- Maximum line length: 120 characters
- Use type hints for all function signatures
- Prefer async/await for I/O operations
- Use f-strings for string formatting

### Naming Conventions

```python
# Classes: PascalCase
class URLService:
    pass

# Functions/Methods: snake_case
def create_short_url():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_URL_LENGTH = 2000

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Type variables: PascalCase with suffix
ModelType = TypeVar("ModelType")
```

### File Organization

```python
"""Module docstring explaining purpose."""

# 1. Standard library imports
import asyncio
from datetime import datetime

# 2. Third-party imports
from fastapi import APIRouter
from sqlalchemy import select

# 3. Local imports - organized by subdirectory
from src.core.config import settings
from src.core.exceptions import NotFoundError
from src.models.url import URL
from src.schemas.common import ApiResponse
```

**Import Order:**
1. Standard library
2. Third-party packages
3. Local application imports (organized by module: core, models, schemas, services)

### Type Hints

Always use type hints:

```python
from collections.abc import Sequence

async def get_urls(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> Sequence[URL]:
    """Get all URLs with pagination."""
    result = await db.execute(
        select(URL).offset(skip).limit(limit)
    )
    return result.scalars().all()
```

### Docstrings

Use Google-style docstrings:

```python
def create_short_url(url: str, custom_code: str | None = None) -> URL:
    """Create a new shortened URL.

    Args:
        url: The original URL to shorten
        custom_code: Optional custom short code

    Returns:
        The created URL object

    Raises:
        ValueError: If custom_code is already taken
    """
    pass
```

## FastAPI Patterns

### Standardized API Response Pattern

All API endpoints MUST follow the standardized response format:

**Success Response:**
```python
from src.schemas.common import ApiResponse

@router.post("/", response_model=ApiResponse[URLResponse], status_code=status.HTTP_201_CREATED)
async def create_url(
    url_create: URLCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create endpoint with standardized response wrapper."""
    try:
        url = await URLService.create_short_url(db, url_create)
        url_response = URLResponse(
            id=url.id,
            short_code=url.short_code,
            # ... other fields
        )
        return ApiResponse.success_response(url_response)
    except ValueError as e:
        # Use custom exceptions, not HTTPException
        raise ConflictError(message=str(e)) from e
```

**Error Response Pattern:**
All errors should use custom exception classes from `src.core.exceptions`:

```python
from src.core.exceptions import NotFoundError, ConflictError, ValidationError

# 404 errors
if not url:
    raise NotFoundError(message=f"Short URL '{short_code}' not found")

# 409 conflicts
if code_exists:
    raise ConflictError(message=f"Short code '{code}' is already taken")

# 422 validation errors
if not is_valid:
    raise ValidationError(message="Invalid input", data={"field": "url"})
```

### Response Format Structure

**All responses include:**
- `success`: boolean indicating if request succeeded
- `data`: response data (null on error)
- `error_code`: machine-readable error code (null on success)
- `error_message`: human-readable error message (null on success)

**Example Responses:**

```python
# Success
{
    "success": true,
    "data": {"id": 1, "short_code": "abc123"},
    "error_code": null,
    "error_message": null
}

# Error
{
    "success": false,
    "data": null,
    "error_code": "NOT_FOUND",
    "error_message": "Short URL 'abc123' not found"
}
```

### Exception Handling

**Exception Handlers Location:**
All exception handlers are centralized in `src/core/exception_handlers.py`:
- `api_error_handler`: Handles custom APIError exceptions
- `validation_exception_handler`: Handles Pydantic validation errors
- `generic_exception_handler`: Catches unexpected exceptions

**Using Exceptions:**
Never use `HTTPException` directly. Use custom exceptions:

```python
# Bad - Don't do this
raise HTTPException(status_code=404, detail="Not found")

# Good - Use custom exceptions
raise NotFoundError(message="Resource not found")
```

**Registering Handlers:**
Exception handlers are registered in `main.py`:

```python
from src.core.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

### Endpoint Structure

```python
@router.post("/", response_model=ApiResponse[URLResponse], status_code=status.HTTP_201_CREATED)
async def create_url(
    url_create: URLCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create endpoint with standardized response."""
    try:
        url = await URLService.create_short_url(db, url_create)
        url_response = URLResponse.from_orm(url)
        return ApiResponse.success_response(url_response)
    except ValueError as e:
        if "already taken" in str(e):
            raise ConflictError(message=str(e)) from e
        raise InternalServerError(message=str(e)) from e
```

### Dependency Injection

```python
# Good: Use FastAPI's Depends
async def endpoint(db: AsyncSession = Depends(get_db)):
    pass

# Bad: Don't create dependencies manually
async def endpoint():
    db = AsyncSessionLocal()  # Don't do this
```

### Error Handling

Use custom exceptions from `src.core.exceptions`:

```python
from src.core.exceptions import (
    NotFoundError,
    ConflictError,
    ValidationError,
    BadRequestError,
    InternalServerError,
)

# 404 - Resource not found
if not url:
    raise NotFoundError(message="URL not found")

# 409 - Resource conflict
if code_exists:
    raise ConflictError(message="Short code already exists")

# 422 - Validation error
if not is_valid:
    raise ValidationError(
        message="Validation failed",
        data={"validation_errors": errors}
    )

# 500 - Internal error
try:
    result = await service_call()
except Exception as e:
    raise InternalServerError(message="Operation failed") from e
```

### Available Error Codes

All error codes are defined in `src.core.exceptions.ErrorCode`:
- `VALIDATION_ERROR` (422)
- `NOT_FOUND` (404)
- `CONFLICT` (409)
- `BAD_REQUEST` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_ERROR` (500)
- `DATABASE_ERROR` (500)
- `SERVICE_UNAVAILABLE` (503)

## Database Patterns

### Models

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True
    )
```

### Queries

```python
# Good: Use select() and scalars()
result = await db.execute(select(URL).where(URL.id == url_id))
url = result.scalar_one_or_none()

# Good: Use flush() in services, commit in endpoints
url.clicks += 1
await db.flush()  # In service
await db.commit()  # In endpoint
```

### Sessions

```python
# Sessions managed by dependency injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Service Layer Pattern

Keep business logic in services:

```python
# services/url_service.py
class URLService:
    @staticmethod
    async def create_short_url(
        db: AsyncSession,
        url_create: URLCreate
    ) -> URL:
        """Business logic here."""
        # Validation
        # Database operations
        # Return model
        pass

# endpoints/urls.py
@router.post("/")
async def create_url(
    url_create: URLCreate,
    db: AsyncSession = Depends(get_db),
):
    """Thin controller layer."""
    try:
        url = await URLService.create_short_url(db, url_create)
        return to_response(url)
    except ValueError as e:
        raise HTTPException(...) from e
```

## Testing Conventions

### Test Organization

```python
# tests/integration/test_urls.py
@pytest.mark.integration
async def test_create_url(client: AsyncClient):
    """Test what the test does."""
    # Arrange
    payload = {"url": "https://example.com"}

    # Act
    response = await client.post("/api/v1/urls/", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
```

### Fixtures

```python
# tests/conftest.py
@pytest.fixture
async def client(async_session):
    """Create test client with overridden dependencies."""
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
```

## Pydantic Schemas

### Base Schema Pattern

All schemas inherit from `BaseSchema` for consistent configuration:

```python
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )

class URLCreate(BaseSchema):
    """Request schema with validation."""
    url: HttpUrl = Field(..., description="URL to shorten", max_length=2048)
    custom_code: str | None = Field(
        None,
        min_length=4,
        max_length=10,
        pattern="^[a-zA-Z0-9_-]+$"
    )
    tags: list[str] | None = Field(None, max_length=10)

    @field_validator("url")
    @classmethod
    def validate_url_safety(cls, v: HttpUrl) -> HttpUrl:
        """Validate URL for security concerns."""
        url_str = str(v)
        is_safe, error_msg = validate_url_safety(url_str)
        if not is_safe:
            raise ValueError(f"URL validation failed: {error_msg}")
        return v

class URLResponse(BaseSchema):
    """Response schema."""
    id: int
    short_code: str
    short_url: str
    clicks: int
    created_at: datetime
```

### Validation Patterns

**Field Validators:**
```python
from pydantic import field_validator

@field_validator("custom_code")
@classmethod
def validate_custom_code(cls, v: str | None) -> str | None:
    """Validate custom code against rules."""
    if v is None:
        return v
    is_valid, error_msg = validate_custom_code(v, DEFAULT_SHORT_CODE_RULES)
    if not is_valid:
        raise ValueError(error_msg)
    return v
```

**Model Validators:**
```python
from pydantic import model_validator

@model_validator(mode="after")
def validate_tags_uniqueness(self) -> Self:
    """Ensure tags are unique (case-insensitive)."""
    if self.tags:
        self.tags = list(dict.fromkeys(tag.lower() for tag in self.tags))
    return self
```

### Security Validation

Always validate user input for security:

```python
def validate_url_safety(url: str) -> tuple[bool, str | None]:
    """Validate URL for security concerns."""
    url_lower = url.lower()
    suspicious_patterns = [
        "javascript:", "data:", "vbscript:", "file:",
        "<script", "onerror=", "onclick=",
        "../", "..\\",
        "%00", "\x00"
    ]
    for pattern in suspicious_patterns:
        if pattern in url_lower:
            return False, f"URL contains suspicious pattern: {pattern}"
    return True, None
```

## Git Commit Messages

Follow conventional commits:

```
feat: add custom short code support
fix: resolve duplicate code generation
docs: update API documentation
test: add integration tests for URL deletion
refactor: extract URL validation logic
chore: update dependencies
```

## Code Review Checklist

- [ ] Type hints added to all functions
- [ ] Docstrings for public functions/classes
- [ ] Error handling with proper status codes
- [ ] Tests added/updated
- [ ] No hardcoded secrets or URLs
- [ ] Database sessions properly managed
- [ ] Async/await used correctly
- [ ] Follows service layer pattern
- [ ] Linting passes (`make lint`)
- [ ] Tests pass (`make test`)

## Performance Guidelines

1. **Use async/await consistently**
   ```python
   # Good
   urls = await URLService.get_all_urls(db)

   # Bad - blocks event loop
   urls = sync_get_all_urls()
   ```

2. **Optimize database queries**
   ```python
   # Good - single query
   url = await db.execute(
       select(URL).where(URL.short_code == code)
   )

   # Bad - N+1 queries
   for code in codes:
       url = await get_url(code)  # Multiple queries
   ```

3. **Use pagination**
   ```python
   @router.get("/")
   async def list_urls(skip: int = 0, limit: int = 100):
       """Always paginate list endpoints."""
       pass
   ```

## Middleware Patterns

### Rate Limiting Middleware

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window algorithm."""

    async def dispatch(self, request: Request, call_next):
        # Extract client identifier
        client_id = self._get_client_identifier(request)

        # Check rate limit
        endpoint = request.url.path
        is_allowed, current_count, reset_time = self.limiter.is_allowed(
            client_id, endpoint, limit, window
        )

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time),
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current_count))
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response
```

### Adding Middleware to App

```python
from src.middleware.rate_limiting import RateLimitMiddleware

app = FastAPI()

# Add middleware (order matters - last added runs first)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Guidelines

1. **Never log sensitive data**
2. **Use environment variables for secrets**
3. **Validate all user input with Pydantic**
   - Use field validators for complex validation
   - Implement security checks (XSS, path traversal)
   - Validate length, format, and patterns
4. **Use parameterized queries (SQLAlchemy does this)**
5. **Set proper CORS origins**
6. **Use HTTPS in production**
7. **Implement rate limiting to prevent abuse**
8. **Sanitize URLs for suspicious patterns**
9. **Block reserved codes and keywords**
10. **Limit input sizes to prevent DoS**

## Documentation

- Keep README.md updated
- Document new API endpoints
- Add docstrings to all public functions
- Update OpenAPI descriptions
- Document environment variables
- Keep QUICKSTART.md accurate
