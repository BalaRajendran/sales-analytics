# Testing Guide

Comprehensive guide for testing the URL Shortener application.

## Testing Philosophy

- **Test Coverage**: Aim for 80%+ code coverage
- **Fast Tests**: Tests should run quickly (< 5 seconds total)
- **Isolated Tests**: Each test should be independent
- **Clear Names**: Test names should describe what they test
- **Arrange-Act-Assert**: Follow AAA pattern

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_services.py    # Service layer tests
│   └── test_utils.py       # Utility function tests
└── integration/            # Integration tests
    └── test_urls.py        # API endpoint tests
```

## Running Tests

### Run All Tests

```bash
cd backend
make test
```

This is the recommended way to run tests. It runs all tests with coverage reporting.

### Run Specific Test Types

**Advanced pytest usage (for fine-grained control):**
```bash
# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# Tests with specific marker
uv run pytest -m integration
```

### Run Specific Tests

**Advanced pytest usage:**
```bash
# Specific file
uv run pytest tests/integration/test_urls.py

# Specific test function
uv run pytest tests/integration/test_urls.py::test_create_url

# Tests matching pattern
uv run pytest -k "create"
```

### Coverage Reports

```bash
# Generate HTML coverage report (standard)
make test

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Advanced coverage options:**
```bash
# Terminal coverage report
uv run pytest --cov=src --cov-report=term-missing

# XML report (for CI/CD)
uv run pytest --cov=src --cov-report=xml

# Custom HTML report
uv run pytest --cov=src --cov-report=html
```

### Parallel Testing

**Advanced pytest option (requires pytest-xdist):**
```bash
# Install pytest-xdist
uv add --dev pytest-xdist

# Run tests in parallel
uv run pytest -n auto
```

## Writing Tests

### Test Structure (AAA Pattern)

```python
async def test_create_url(client: AsyncClient):
    """Test creating a shortened URL."""
    # Arrange - Set up test data
    payload = {
        "url": "https://example.com"
    }

    # Act - Perform the action
    response = await client.post("/api/v1/urls/", json=payload)

    # Assert - Verify the results
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
    assert "short_code" in data
```

### Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
async def test_create_url_with_custom_code_returns_custom_code()
async def test_redirect_increments_click_count()
async def test_create_duplicate_custom_code_returns_400()

# Bad
async def test_urls()
async def test_1()
async def test_endpoint()
```

## Fixtures

### Available Fixtures

Defined in `tests/conftest.py`:

#### async_engine
Creates an async database engine for testing with in-memory SQLite.

```python
@pytest.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

#### async_session
Provides an async database session for testing.

```python
async def test_url_service(async_session):
    """Test using database session."""
    url = URL(
        original_url="https://example.com",
        short_code="test123"
    )
    async_session.add(url)
    await async_session.commit()
```

#### client
Provides an async HTTP client for API testing.

```python
async def test_api_endpoint(client: AsyncClient):
    """Test API endpoint."""
    response = await client.get("/api/v1/urls/")
    assert response.status_code == 200
```

### Custom Fixtures

Create custom fixtures for common test data:

```python
# tests/conftest.py
@pytest.fixture
async def sample_url(async_session):
    """Create a sample URL for testing."""
    url = URL(
        original_url="https://example.com",
        short_code="abc123",
        clicks=0
    )
    async_session.add(url)
    await async_session.flush()
    await async_session.refresh(url)
    return url

# Use in tests
async def test_get_url_stats(client, sample_url):
    response = await client.get(f"/api/v1/urls/{sample_url.short_code}/stats")
    assert response.status_code == 200
```

## Integration Tests

Test API endpoints end-to-end.

### Example: Testing URL Creation

```python
@pytest.mark.integration
async def test_create_url_success(client: AsyncClient):
    """Test successful URL creation."""
    response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
    assert len(data["short_code"]) == 6  # Default length
    assert data["clicks"] == 0
    assert "created_at" in data
```

### Example: Testing Error Cases

```python
@pytest.mark.integration
async def test_create_url_with_duplicate_custom_code(client: AsyncClient):
    """Test that duplicate custom codes are rejected."""
    # Create first URL
    await client.post(
        "/api/v1/urls/",
        json={"url": "https://example1.com", "custom_code": "duplicate"}
    )

    # Try to create second URL with same code
    response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example2.com", "custom_code": "duplicate"}
    )

    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]
```

### Example: Testing Pagination

```python
@pytest.mark.integration
async def test_list_urls_pagination(client: AsyncClient):
    """Test URL list pagination."""
    # Create multiple URLs
    for i in range(5):
        await client.post(
            "/api/v1/urls/",
            json={"url": f"https://example{i}.com"}
        )

    # Test first page
    response = await client.get("/api/v1/urls/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Test second page
    response = await client.get("/api/v1/urls/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
```

## Unit Tests

Test individual components in isolation.

### Testing Services

```python
@pytest.mark.unit
async def test_generate_short_code():
    """Test short code generation."""
    code = URLService.generate_short_code(length=8)

    assert len(code) == 8
    assert code.isalnum()


@pytest.mark.unit
async def test_create_short_url_service(async_session):
    """Test URL creation through service layer."""
    url_create = URLCreate(url="https://example.com")

    url = await URLService.create_short_url(async_session, url_create)

    assert url.id is not None
    assert url.original_url == "https://example.com"
    assert len(url.short_code) == 6
    assert url.clicks == 0
```

### Testing Validation

```python
@pytest.mark.unit
def test_url_create_schema_validation():
    """Test URLCreate schema validation."""
    # Valid URL
    url_create = URLCreate(url="https://example.com")
    assert str(url_create.url) == "https://example.com/"

    # Invalid custom code
    with pytest.raises(ValidationError):
        URLCreate(
            url="https://example.com",
            custom_code="invalid code with spaces"
        )

    # Too short custom code
    with pytest.raises(ValidationError):
        URLCreate(
            url="https://example.com",
            custom_code="abc"  # Min length is 4
        )
```

## Mocking

Use pytest-mock for mocking external dependencies.

### Install pytest-mock

```bash
uv add --dev pytest-mock
```

### Example: Mocking External Service

```python
async def test_url_service_with_mock(async_session, mocker):
    """Test with mocked random generator."""
    # Mock the random choice to return predictable value
    mocker.patch(
        'random.choices',
        return_value=['a', 'b', 'c', '1', '2', '3']
    )

    code = URLService.generate_short_code()
    assert code == "abc123"
```

## Test Data

### Using Faker

```bash
uv add --dev faker
```

```python
from faker import Faker

fake = Faker()

@pytest.fixture
def random_url():
    """Generate random URL for testing."""
    return fake.url()

async def test_with_random_data(client, random_url):
    """Test with random generated data."""
    response = await client.post(
        "/api/v1/urls/",
        json={"url": random_url}
    )
    assert response.status_code == 201
```

### Using Factory Boy

```bash
uv add --dev factory-boy
```

```python
# tests/factories.py
import factory
from src.models.url import URL

class URLFactory(factory.Factory):
    class Meta:
        model = URL

    original_url = factory.Faker('url')
    short_code = factory.Faker('lexify', text='??????')
    clicks = 0

# Use in tests
async def test_with_factory(async_session):
    """Test with factory-generated data."""
    url = URLFactory.build()
    async_session.add(url)
    await async_session.commit()
```

## Testing Best Practices

### 1. Test Independence

```python
# Good - Each test is independent
async def test_create_url(client):
    response = await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    assert response.status_code == 201

async def test_list_urls(client):
    # Create test data within the test
    await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    response = await client.get("/api/v1/urls/")
    assert response.status_code == 200

# Bad - Tests depend on each other
url_id = None

async def test_create_url(client):
    global url_id
    response = await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    url_id = response.json()["id"]

async def test_get_url(client):
    response = await client.get(f"/api/v1/urls/{url_id}/stats")  # Depends on previous test
```

### 2. Test One Thing

```python
# Good - Tests one specific thing
async def test_create_url_returns_201(client):
    response = await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    assert response.status_code == 201

async def test_create_url_returns_short_code(client):
    response = await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    data = response.json()
    assert "short_code" in data

# Bad - Tests multiple things
async def test_create_url(client):
    response = await client.post("/api/v1/urls/", json={"url": "https://example.com"})
    assert response.status_code == 201
    assert "short_code" in response.json()
    assert response.json()["clicks"] == 0  # Too many assertions
```

### 3. Use Descriptive Assertions

```python
# Good
assert response.status_code == 201, f"Expected 201, got {response.status_code}"
assert data["clicks"] == 0, "New URL should have 0 clicks"

# Better - Use pytest features
from pytest import approx

assert data["clicks"] == 0
assert data["created_at"] is not None
```

### 4. Test Edge Cases

```python
async def test_create_url_with_very_long_url(client):
    """Test URL creation with maximum length URL."""
    long_url = "https://example.com/" + "a" * 2000
    response = await client.post("/api/v1/urls/", json={"url": long_url})
    assert response.status_code == 201

async def test_list_urls_with_empty_database(client):
    """Test listing URLs when database is empty."""
    response = await client.get("/api/v1/urls/")
    assert response.status_code == 200
    assert response.json() == []
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: |
        cd backend
        make dev

    - name: Run tests
      run: |
        cd backend
        make test
        # Note: Adjust coverage format if needed for CI
        # uv run pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./backend/coverage.xml
```

## Debugging Tests

**Advanced pytest debugging options:**

### Run Tests in Verbose Mode

```bash
uv run pytest -vv
```

### Show Print Statements

```bash
uv run pytest -s
```

### Drop into Debugger on Failure

```bash
uv run pytest --pdb
```

### Debug Specific Test

```python
async def test_something(client):
    import pdb; pdb.set_trace()  # Debugger will stop here
    response = await client.get("/api/v1/urls/")
```

## Performance Testing

### Using pytest-benchmark

```bash
uv add --dev pytest-benchmark
```

```python
def test_url_generation_performance(benchmark):
    """Benchmark URL generation."""
    result = benchmark(URLService.generate_short_code)
    assert len(result) == 6
```

## Next Steps

- Review [API Reference](../api/API_REFERENCE.md) for endpoint details
- Check [Setup Guide](SETUP_GUIDE.md) for environment setup
- See [Code Conventions](../../.claude/conventions.md) for coding standards
