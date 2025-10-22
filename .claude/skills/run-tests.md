# Run Tests

Execute the test suite for the FastAPI GraphQL application with proper reporting.

## Instructions

1. Check if virtual environment is activated
2. Verify test dependencies are installed
3. Run the appropriate test command based on user's request
4. Display test results with clear formatting
5. If tests fail, analyze failures and suggest fixes

## Test Types

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Specific Test Types
```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e              # End-to-end tests only
```

### Specific Test File
```bash
pytest tests/path/to/test_file.py
```

### Watch Mode (with pytest-watch)
```bash
ptw
```

## Output Handling

1. Show test summary (passed/failed/skipped)
2. For failures, show:
   - Test name and location
   - Error message
   - Relevant code snippet
   - Suggested fix
3. Show coverage percentage if applicable
4. Generate coverage HTML report location

## Common Issues

- Missing dependencies: Suggest `pip install -e ".[dev]"`
- Database not running: Suggest `docker-compose up -d postgres redis`
- Import errors: Check PYTHONPATH and module structure
- Fixture issues: Verify conftest.py setup

## Tips

- Use `-v` for verbose output
- Use `-s` to see print statements
- Use `--lf` to run only last failed tests
- Use `--tb=short` for shorter tracebacks
