# Rate Limiting

The URL Shortener API implements comprehensive rate limiting to ensure fair usage and protect against abuse.

## Overview

Rate limiting restricts the number of API requests that can be made within a given time window. This helps:
- Prevent abuse and DoS attacks
- Ensure fair resource allocation
- Maintain API performance and stability
- Protect backend infrastructure

## Rate Limit Headers

Every API response includes rate limit information in the headers:

```http
X-RateLimit-Limit: 100          # Maximum requests allowed per window
X-RateLimit-Remaining: 95       # Requests remaining in current window
X-RateLimit-Reset: 1699564800   # Unix timestamp when limit resets
```

## Default Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| **Default** | 100 requests | per minute |
| `POST /api/v1/urls/` | 30 requests | per minute |
| `POST /api/v1/urls/bulk` | 5 requests | per minute |
| `GET /health` | 1000 requests | per minute |

## Rate Limit Identification

Rate limits are applied based on the following identifiers (in priority order):

1. **User ID** - If authenticated (future feature)
2. **API Key** - From `X-API-Key` header (future feature)
3. **IP Address** - From `X-Forwarded-For` or client IP
4. **User Agent** - Fallback identifier

## Rate Limit Exceeded

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "message": "Too many requests. Limit: 30 requests per minute.",
    "retry_after": 45,
    "current_count": 31,
    "limit": 30
  }
}
```

**Response Headers:**
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699564890
Retry-After: 45
```

## Configuration

Rate limiting can be configured via environment variables:

```env
# Enable/disable rate limiting
RATE_LIMIT_ENABLED=true

# Default limit (requests per minute)
RATE_LIMIT_PER_MINUTE=100

# URL creation endpoint limit
RATE_LIMIT_CREATE_URL=30

# Bulk operations limit
RATE_LIMIT_BULK_OPERATIONS=5
```

## Best Practices

### 1. Monitor Rate Limit Headers

Always check the `X-RateLimit-Remaining` header to track your usage:

```python
import httpx

response = httpx.post("http://localhost:8000/api/v1/urls/", json={"url": "..."})
remaining = int(response.headers.get("X-RateLimit-Remaining", 0))

if remaining < 10:
    print("Warning: Approaching rate limit")
```

### 2. Handle 429 Responses

Implement exponential backoff when hitting rate limits:

```python
import time
import httpx

def create_url_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = httpx.post(
                "http://localhost:8000/api/v1/urls/",
                json={"url": url}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 60))
                if attempt < max_retries - 1:
                    print(f"Rate limited. Retrying after {retry_after}s...")
                    time.sleep(retry_after)
                else:
                    raise
            else:
                raise
```

### 3. Respect Retry-After Header

Always respect the `Retry-After` header value before retrying:

```javascript
async function createURL(url) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/urls/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      console.log(`Rate limited. Retry after ${retryAfter} seconds`);
      // Wait and retry
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      return createURL(url); // Retry
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating URL:', error);
    throw error;
  }
}
```

### 4. Batch Operations

Use bulk endpoints for creating multiple URLs to save on rate limit:

```python
# Bad: Multiple individual requests (uses 10 rate limit slots)
for url in urls:
    create_url(url)

# Good: Single bulk request (uses 1 rate limit slot)
bulk_create_urls(urls)
```

## Rate Limit Algorithms

The API uses a **Sliding Window** algorithm for rate limiting:

- **Window Size**: 60 seconds (1 minute)
- **Request Tracking**: Requests are tracked with timestamps
- **Expiration**: Old requests outside the window are automatically removed
- **Precision**: Sub-second accuracy for fair distribution

### Example Timeline

```
Time:  0s    15s   30s   45s   60s   75s
Limit: 30 requests per 60 seconds

|------ Window 1 (0-60s) ------|
       |------ Window 2 (15-75s) ------|
              |------ Window 3 (30-90s) ------|
```

Requests are counted within a rolling 60-second window, providing smooth rate limiting without sudden resets.

## Exempt Endpoints

The following endpoints are exempt from rate limiting:

- `/docs` - API documentation
- `/redoc` - Alternative API documentation
- `/openapi.json` - OpenAPI specification

## Testing Rate Limits

### Test Default Limit

```bash
# Send 110 requests rapidly
for i in {1..110}; do
  curl -X GET http://localhost:8000/api/v1/urls/ &
done

# After 100 requests, you'll get 429 responses
```

### Test URL Creation Limit

```bash
# Send 35 URL creation requests
for i in {1..35}; do
  curl -X POST http://localhost:8000/api/v1/urls/ \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"https://example.com/${i}\"}" &
done

# After 30 requests, you'll get 429 responses
```

## Future Enhancements

Planned improvements to rate limiting:

1. **Redis Backend**: Distributed rate limiting across multiple servers
2. **User-Based Limits**: Different limits for authenticated users
3. **Tier-Based Limits**: Premium tiers with higher limits
4. **Burst Allowance**: Allow short bursts beyond normal limits
5. **Custom Rate Limits**: Per-user custom rate limit configuration
6. **Rate Limit Dashboard**: Monitor and adjust limits in real-time

## Troubleshooting

### Issue: Rate limit too restrictive

**Solution**: Adjust environment variables and restart:
```env
RATE_LIMIT_PER_MINUTE=200
RATE_LIMIT_CREATE_URL=60
```

### Issue: Getting rate limited unexpectedly

**Possible causes**:
1. Multiple services sharing same IP (check `X-Forwarded-For` handling)
2. Load balancer not passing client IP correctly
3. Browser making parallel requests

**Solution**:
- Enable proper IP forwarding in your load balancer
- Implement client-side request queuing
- Use API keys for accurate identification (when available)

### Issue: Rate limiting not working

**Check**:
1. Is `RATE_LIMIT_ENABLED=true` in .env?
2. Are you in test/debug mode?
3. Check middleware is properly added in `main.py`

## Monitoring

Track rate limiting metrics:

```python
# Log rate limit hits
import logging

logger = logging.getLogger(__name__)

try:
    response = api_call()
except RateLimitError as e:
    logger.warning(
        "Rate limit hit",
        endpoint=e.endpoint,
        limit=e.limit,
        retry_after=e.retry_after
    )
```

## Support

For rate limit increases or custom limits, please contact support or open an issue on GitHub.
