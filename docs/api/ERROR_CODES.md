# Error Codes Reference

Complete reference for all error codes returned by the URL Shortener API.

## Exception Handling Architecture

All exception handling is centralized in `src/core/exception_handlers.py`:
- `api_error_handler`: Handles custom `APIError` exceptions
- `validation_exception_handler`: Handles Pydantic `RequestValidationError`
- `generic_exception_handler`: Catches unexpected exceptions

Custom exception classes are defined in `src/core/exceptions.py`.

## Standard Response Format

All API responses follow a standardized format:

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "error_code": null,
  "error_message": null
}
```

### Error Response

```json
{
  "success": false,
  "data": {
    // Additional error context (optional)
  },
  "error_code": "ERROR_CODE_HERE",
  "error_message": "Human-readable error message"
}
```

## Error Codes

### Client Errors (4xx)

#### VALIDATION_ERROR (422)

**Description:** Request validation failed. Input data does not meet the required format or constraints.

**Common Causes:**
- Invalid URL format
- URL too long (>2048 characters)
- URL contains suspicious patterns (XSS, path traversal)
- Custom code doesn't match pattern
- Custom code too short/long
- Tags validation failed
- Missing required fields

**Example Response:**
```json
{
  "success": false,
  "data": {
    "validation_errors": [
      {
        "field": "body.url",
        "message": "URL validation failed: URL contains suspicious pattern: javascript:",
        "type": "value_error"
      }
    ]
  },
  "error_code": "VALIDATION_ERROR",
  "error_message": "Request validation failed"
}
```

**How to Fix:**
- Check field requirements in [VALIDATION.md](VALIDATION.md)
- Ensure URL is valid HTTP/HTTPS
- Remove suspicious patterns from URLs
- Use valid custom code format (4-10 chars, alphanumeric + hyphens/underscores)

---

#### NOT_FOUND (404)

**Description:** The requested resource does not exist.

**Common Causes:**
- Short code doesn't exist
- URL has been deleted
- Invalid endpoint path

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "NOT_FOUND",
  "error_message": "Short URL 'abc123' not found"
}
```

**How to Fix:**
- Verify the short code exists
- Check for typos in the short code
- Use the list endpoint to see available URLs

---

#### CONFLICT (409)

**Description:** The request conflicts with an existing resource.

**Common Causes:**
- Custom short code already taken
- Duplicate URL in bulk operation

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "CONFLICT",
  "error_message": "Short code 'mylink' is already taken"
}
```

**How to Fix:**
- Choose a different custom code
- Let the system generate a random code (omit custom_code)
- Check existing URLs first

---

#### BAD_REQUEST (400)

**Description:** The request is malformed or contains invalid parameters.

**Common Causes:**
- Invalid query parameters
- Malformed JSON
- Invalid data types

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "BAD_REQUEST",
  "error_message": "Invalid request parameters"
}
```

**How to Fix:**
- Check request format
- Ensure JSON is valid
- Verify parameter types

---

#### UNAUTHORIZED (401)

**Description:** Authentication is required but not provided or invalid.

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "UNAUTHORIZED",
  "error_message": "Authentication required"
}
```

**Note:** Currently, the API does not require authentication. This error code is reserved for future use.

---

#### FORBIDDEN (403)

**Description:** The authenticated user doesn't have permission to access this resource.

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "FORBIDDEN",
  "error_message": "Access denied to this resource"
}
```

**Note:** Currently not used. Reserved for future authorization features.

---

#### RATE_LIMIT_EXCEEDED (429)

**Description:** Too many requests sent in a given time window.

**Common Causes:**
- Exceeded per-endpoint rate limit
- Too many requests from same client

**Example Response:**
```json
{
  "success": false,
  "data": {
    "retry_after": 45,
    "current_count": 31,
    "limit": 30
  },
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Rate limit exceeded. Please try again in 45 seconds."
}
```

**Response Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704841845
Retry-After: 45
```

**How to Fix:**
- Wait for the retry_after duration
- Implement exponential backoff
- Reduce request frequency
- See [RATE_LIMITING.md](RATE_LIMITING.md) for limits

---

### Server Errors (5xx)

#### INTERNAL_ERROR (500)

**Description:** An unexpected error occurred on the server.

**Common Causes:**
- Unhandled exception
- Configuration error
- Code bug

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "INTERNAL_ERROR",
  "error_message": "An unexpected error occurred"
}
```

**How to Fix:**
- Retry the request
- If persistent, contact support
- Check API status page

---

#### DATABASE_ERROR (500)

**Description:** Database operation failed.

**Common Causes:**
- Database connection lost
- Query timeout
- Database constraint violation

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "DATABASE_ERROR",
  "error_message": "Database operation failed"
}
```

**How to Fix:**
- Retry the request
- Wait a moment and try again
- If persistent, contact support

---

#### SERVICE_UNAVAILABLE (503)

**Description:** The service is temporarily unavailable.

**Common Causes:**
- Scheduled maintenance
- Server overload
- Dependency failure

**Example Response:**
```json
{
  "success": false,
  "data": null,
  "error_code": "SERVICE_UNAVAILABLE",
  "error_message": "Service temporarily unavailable"
}
```

**How to Fix:**
- Wait and retry
- Check API status page
- Implement retry with exponential backoff

---

## Error Code Summary Table

| Error Code | HTTP Status | Category | Retryable |
|------------|-------------|----------|-----------|
| VALIDATION_ERROR | 422 | Client | No |
| NOT_FOUND | 404 | Client | No |
| CONFLICT | 409 | Client | No |
| BAD_REQUEST | 400 | Client | No |
| UNAUTHORIZED | 401 | Client | No* |
| FORBIDDEN | 403 | Client | No |
| RATE_LIMIT_EXCEEDED | 429 | Client | Yes |
| INTERNAL_ERROR | 500 | Server | Yes |
| DATABASE_ERROR | 500 | Server | Yes |
| SERVICE_UNAVAILABLE | 503 | Server | Yes |

*Retryable after fixing authentication

## Handling Errors in Client Code

### Python Example

```python
import httpx
from typing import Optional

async def create_short_url(url: str, custom_code: Optional[str] = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/urls/",
                json={"url": url, "custom_code": custom_code}
            )
            response.raise_for_status()

            result = response.json()
            if result["success"]:
                return result["data"]
            else:
                print(f"Error: {result['error_code']} - {result['error_message']}")
                return None

        except httpx.HTTPStatusError as e:
            error_data = e.response.json()
            error_code = error_data.get("error_code", "UNKNOWN")
            error_message = error_data.get("error_message", "Unknown error")

            if error_code == "RATE_LIMIT_EXCEEDED":
                retry_after = error_data["data"]["retry_after"]
                print(f"Rate limited. Retry after {retry_after} seconds")
            elif error_code == "VALIDATION_ERROR":
                errors = error_data["data"]["validation_errors"]
                print(f"Validation errors: {errors}")
            else:
                print(f"Error: {error_code} - {error_message}")

            return None
```

### JavaScript Example

```javascript
async function createShortUrl(url, customCode = null) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/urls/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, custom_code: customCode })
    });

    const result = await response.json();

    if (!response.ok) {
      const { error_code, error_message, data } = result;

      switch (error_code) {
        case 'RATE_LIMIT_EXCEEDED':
          const retryAfter = data.retry_after;
          console.error(`Rate limited. Retry after ${retryAfter} seconds`);
          break;
        case 'VALIDATION_ERROR':
          console.error('Validation errors:', data.validation_errors);
          break;
        case 'CONFLICT':
          console.error('Short code already taken');
          break;
        default:
          console.error(`Error: ${error_message}`);
      }
      return null;
    }

    return result.data;
  } catch (error) {
    console.error('Network error:', error);
    return null;
  }
}
```

### cURL Example

```bash
# Make request and capture response
response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}')

# Extract status code and body
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
  echo "Success: $body"
else
  error_code=$(echo "$body" | jq -r '.error_code')
  error_message=$(echo "$body" | jq -r '.error_message')
  echo "Error ($http_code): $error_code - $error_message"
fi
```

## Best Practices

### 1. Always Check Success Field

```python
result = response.json()
if result["success"]:
    # Handle success
    data = result["data"]
else:
    # Handle error
    error_code = result["error_code"]
    error_message = result["error_message"]
```

### 2. Handle Specific Error Codes

Different error codes require different handling strategies:
- **VALIDATION_ERROR**: Fix input and retry
- **RATE_LIMIT_EXCEEDED**: Wait and retry with exponential backoff
- **CONFLICT**: Use different custom code
- **NOT_FOUND**: Don't retry
- **INTERNAL_ERROR**: Retry with backoff

### 3. Implement Retry Logic

```python
import asyncio
from typing import Optional

async def create_url_with_retry(url: str, max_retries: int = 3) -> Optional[dict]:
    """Create URL with automatic retry on retryable errors."""
    for attempt in range(max_retries):
        try:
            response = await client.post("/api/v1/urls/", json={"url": url})
            result = response.json()

            if result["success"]:
                return result["data"]

            error_code = result["error_code"]

            # Don't retry client errors (except rate limit)
            if error_code in ["VALIDATION_ERROR", "NOT_FOUND", "CONFLICT", "BAD_REQUEST"]:
                return None

            # Handle rate limiting
            if error_code == "RATE_LIMIT_EXCEEDED":
                retry_after = result["data"]["retry_after"]
                await asyncio.sleep(retry_after)
                continue

            # Exponential backoff for server errors
            if error_code in ["INTERNAL_ERROR", "DATABASE_ERROR", "SERVICE_UNAVAILABLE"]:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue

            return None

        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise

    return None
```

### 4. Log Error Details

Always log error codes and messages for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def handle_api_error(result: dict):
    logger.error(
        f"API Error: {result['error_code']} - {result['error_message']}",
        extra={
            "error_code": result["error_code"],
            "error_data": result.get("data"),
        }
    )
```

## See Also

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Validation Guide](VALIDATION.md) - Input validation rules
- [Rate Limiting Guide](RATE_LIMITING.md) - Rate limit details
- [Architecture](../architecture/ARCHITECTURE.md) - System architecture
