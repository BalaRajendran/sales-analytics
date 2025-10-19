# API Reference

Complete API reference for the URL Shortener API.

## Base URL

```
http://localhost:8000/api/v1
```

## Response Format

**All API endpoints follow a standardized response format:**

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

**Note:** The redirect endpoint (`GET /api/v1/urls/{short_code}`) is an exception and returns a standard HTTP redirect instead of the JSON format above.

See [ERROR_CODES.md](ERROR_CODES.md) for complete error code reference.

## Authentication

Currently, the API does not require authentication. Future versions will support API key authentication.

## Common Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |
| 429 | Too Many Requests (rate limit exceeded) |
| 500 | Internal Server Error |

## Rate Limiting

All API requests are subject to rate limiting. See [RATE_LIMITING.md](RATE_LIMITING.md) for complete details.

**Rate Limit Headers:**
Every response includes rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 45
```

**Rate Limit Response (429 Too Many Requests):**
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

**Default Limits:**
- General endpoints: 100 requests/minute
- Create URL: 30 requests/minute
- Bulk operations: 5 requests/minute

## Input Validation

All requests are validated using Pydantic. See [VALIDATION.md](VALIDATION.md) for complete validation rules.

**Validation Error Response (422 Unprocessable Entity):**
```json
{
  "success": false,
  "data": {
    "validation_errors": [
      {
        "field": "body.custom_code",
        "message": "String should have at least 4 characters",
        "type": "string_too_short"
      }
    ]
  },
  "error_code": "VALIDATION_ERROR",
  "error_message": "Request validation failed"
}
```

## Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "0.1.0",
    "timestamp": "2025-10-12T14:30:00Z"
  },
  "error_code": null,
  "error_message": null
}
```

---

### Create Shortened URL

Create a new shortened URL.

**Endpoint:** `POST /api/v1/urls/`

**Request Body:**
```json
{
  "url": "https://example.com/very/long/url",
  "custom_code": "mycode",  // Optional
  "tags": ["marketing", "campaign-2024"]  // Optional
}
```

**Parameters:**
- `url` (required): The URL to shorten. Must be a valid HTTP/HTTPS URL (max 2048 characters).
- `custom_code` (optional): Custom short code (4-10 characters, alphanumeric, underscores, and hyphens only).
- `tags` (optional): Array of tags (max 10 tags, each 1-50 characters, alphanumeric with hyphens/underscores).

**Validation Rules:**
- URL must use http/https scheme
- URL maximum length: 2048 characters
- URL safety checks prevent XSS, path traversal, and suspicious patterns
- Custom codes cannot use reserved words (api, admin, health, etc.)
- See [VALIDATION.md](VALIDATION.md) for complete validation rules

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "original_url": "https://example.com/very/long/url",
    "short_code": "mycode",
    "short_url": "http://localhost:8000/mycode",
    "clicks": 0,
    "created_at": "2025-10-12T14:30:00Z"
  },
  "error_code": null,
  "error_message": null
}
```

**Conflict Error Response (409 Conflict):**
```json
{
  "success": false,
  "data": null,
  "error_code": "CONFLICT",
  "error_message": "Short code 'mycode' is already taken"
}
```

**Validation Error Response (422 Unprocessable Entity):**
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

**Rate Limit Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 60
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very/long/url",
    "custom_code": "mycode"
  }'
```

---

### List All URLs

Get a paginated list of all shortened URLs.

**Endpoint:** `GET /api/v1/urls/`

**Query Parameters:**
- `skip` (optional, default: 0, min: 0): Number of records to skip
- `limit` (optional, default: 100, min: 1, max: 1000): Maximum number of records to return
- `sort_by` (optional): Sort field (created_at, updated_at, clicks, short_code)
- `sort_order` (optional, default: desc): Sort order (asc, desc)

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "original_url": "https://example.com/page1",
      "short_code": "abc123",
      "short_url": "http://localhost:8000/abc123",
      "clicks": 42,
      "created_at": "2025-10-12T14:30:00Z"
    },
    {
      "id": 2,
      "original_url": "https://example.com/page2",
      "short_code": "def456",
      "short_url": "http://localhost:8000/def456",
      "clicks": 15,
      "created_at": "2025-10-12T15:00:00Z"
    }
  ],
  "error_code": null,
  "error_message": null
}
```

**Example:**
```bash
# Get first page (default)
curl http://localhost:8000/api/v1/urls/

# Get second page with 50 items per page
curl http://localhost:8000/api/v1/urls/?skip=50&limit=50
```

---

### Get URL Statistics

Get detailed statistics for a specific shortened URL.

**Endpoint:** `GET /api/v1/urls/{short_code}/stats`

**Path Parameters:**
- `short_code` (required): The short code to get statistics for

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "original_url": "https://example.com/page",
    "short_code": "abc123",
    "clicks": 42,
    "created_at": "2025-10-12T14:30:00Z",
    "updated_at": "2025-10-12T16:45:00Z"
  },
  "error_code": null,
  "error_message": null
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "data": null,
  "error_code": "NOT_FOUND",
  "error_message": "Short URL 'abc123' not found"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/urls/abc123/stats
```

---

### Redirect to Original URL

Redirect to the original URL and increment click count.

**Endpoint:** `GET /api/v1/urls/{short_code}`

**Path Parameters:**
- `short_code` (required): The short code to redirect

**Success Response (307 Temporary Redirect):**
- Redirects to the original URL
- Increments the click counter
- **Note:** This endpoint returns a redirect, not the standard JSON response format

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "data": null,
  "error_code": "NOT_FOUND",
  "error_message": "Short URL 'abc123' not found"
}
```

**Example:**
```bash
# This will redirect to the original URL
curl -L http://localhost:8000/api/v1/urls/abc123

# To see the redirect without following
curl -I http://localhost:8000/api/v1/urls/abc123
```

---

### Delete URL

Delete a shortened URL permanently.

**Endpoint:** `DELETE /api/v1/urls/{short_code}`

**Path Parameters:**
- `short_code` (required): The short code to delete

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "URL 'abc123' deleted successfully"
  },
  "error_code": null,
  "error_message": null
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "data": null,
  "error_code": "NOT_FOUND",
  "error_message": "Short URL 'abc123' not found"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/urls/abc123
```

---

## Schema Definitions

### URLCreate

Request schema for creating a new URL.

```json
{
  "url": "string (HttpUrl, required, max 2048 chars)",
  "custom_code": "string (optional, 4-10 chars, pattern: ^[a-zA-Z0-9_-]+$)",
  "tags": "array of strings (optional, max 10 tags, each 1-50 chars)"
}
```

**Validation:**
- URL must be valid HTTP/HTTPS URL
- URL undergoes security checks (XSS, path traversal, etc.)
- Custom code must not be reserved (api, admin, health, etc.)
- Tags are deduplicated (case-insensitive)
- See [VALIDATION.md](VALIDATION.md) for complete validation rules

### URLResponse

Response schema for URL operations.

```json
{
  "id": "integer",
  "original_url": "string",
  "short_code": "string",
  "short_url": "string",
  "clicks": "integer",
  "created_at": "datetime (ISO 8601)"
}
```

### URLStats

Response schema for URL statistics.

```json
{
  "id": "integer",
  "original_url": "string",
  "short_code": "string",
  "clicks": "integer",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

## Error Handling

All error responses follow the standardized format:

```json
{
  "success": false,
  "data": {
    // Optional additional error context
  },
  "error_code": "ERROR_CODE",
  "error_message": "Human-readable error description"
}
```

For complete error code reference, see [ERROR_CODES.md](ERROR_CODES.md).

### Common Errors

**400 Bad Request:**
- Custom code already taken
- Database operation failed
- Business logic violation

**404 Not Found:**
- Short code doesn't exist
- Endpoint doesn't exist

**422 Unprocessable Entity:**
- Invalid URL format
- URL too long (>2048 characters)
- URL contains suspicious patterns (XSS, path traversal)
- Custom code doesn't match pattern
- Custom code is reserved
- Custom code too short/long
- Missing required fields
- Tags validation failed

**429 Too Many Requests:**
- Rate limit exceeded
- See Retry-After header for wait time

**500 Internal Server Error:**
- Database connection error
- Could not generate unique short code (rare)
- Unexpected server error

See [VALIDATION.md](VALIDATION.md) for validation error details and [RATE_LIMITING.md](RATE_LIMITING.md) for rate limit information.

## Rate Limiting Details

The API implements comprehensive rate limiting using a sliding window algorithm. See [RATE_LIMITING.md](RATE_LIMITING.md) for complete documentation.

**Quick Reference:**

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/v1/urls/ | 30 requests | 1 minute |
| POST /api/v1/urls/bulk | 5 requests | 1 minute |
| GET /api/v1/urls/ | 100 requests | 1 minute |
| GET /health | 1000 requests | 1 minute |
| Other endpoints | 100 requests | 1 minute |

**Configuration:**
Rate limits can be configured via environment variables:
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_CREATE_URL=30
RATE_LIMIT_BULK_OPERATIONS=5
```

## Pagination

List endpoints support pagination using `skip` and `limit` parameters:

```bash
# First page (items 0-99)
GET /api/v1/urls/?skip=0&limit=100

# Second page (items 100-199)
GET /api/v1/urls/?skip=100&limit=100
```

## Interactive Documentation

For interactive API testing, visit:

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## Code Examples

### Python

```python
import httpx

async with httpx.AsyncClient() as client:
    # Create URL
    response = await client.post(
        "http://localhost:8000/api/v1/urls/",
        json={"url": "https://example.com"}
    )
    result = response.json()

    if result["success"]:
        data = result["data"]
        short_code = data["short_code"]
        print(f"Created: {data['short_url']}")

        # Get stats
        stats_response = await client.get(
            f"http://localhost:8000/api/v1/urls/{short_code}/stats"
        )
        stats = stats_response.json()
        if stats["success"]:
            print(f"Clicks: {stats['data']['clicks']}")
    else:
        print(f"Error: {result['error_code']} - {result['error_message']}")
```

### JavaScript

```javascript
// Create URL
const response = await fetch('http://localhost:8000/api/v1/urls/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com'
  })
});
const result = await response.json();

if (result.success) {
  console.log('Created:', result.data.short_url);
  console.log('Short code:', result.data.short_code);
} else {
  console.error(`Error: ${result.error_code} - ${result.error_message}`);
}
```

### cURL

```bash
# Create URL
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# List URLs
curl http://localhost:8000/api/v1/urls/

# Get stats
curl http://localhost:8000/api/v1/urls/abc123/stats

# Redirect (follow redirects)
curl -L http://localhost:8000/api/v1/urls/abc123

# Delete URL
curl -X DELETE http://localhost:8000/api/v1/urls/abc123
```
