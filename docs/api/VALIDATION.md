# Input Validation

The URL Shortener API implements comprehensive input validation using Pydantic to ensure data integrity and security.

## Overview

All API requests are validated automatically using Pydantic schemas before processing. Invalid requests return a `422 Unprocessable Entity` response with detailed error information.

## URL Validation

### Valid URLs

URLs must meet the following requirements:

- **Scheme**: Must be `http` or `https`
- **Format**: Must be a valid URL format
- **Length**: Maximum 2048 characters
- **Safety**: No suspicious patterns (javascript:, data:, etc.)

**Valid Examples:**
```json
{
  "url": "https://example.com"
}

{
  "url": "https://www.example.com/page?param=value"
}

{
  "url": "http://localhost:3000/test"
}
```

**Invalid Examples:**
```json
{
  "url": "javascript:alert('xss')"
}
// Error: URL contains suspicious pattern

{
  "url": "not-a-url"
}
// Error: Invalid URL format

{
  "url": "https://example.com/" + "a" * 3000
}
// Error: URL is too long (maximum 2048 characters)
```

### URL Safety Checks

The API automatically checks URLs for security concerns:

1. **Suspicious Schemes**: Blocks `javascript:`, `data:`, `vbscript:`, `file:`
2. **XSS Patterns**: Detects `<script`, `onerror=`, `onclick=`
3. **Path Traversal**: Blocks `../`, `..\\`
4. **Null Bytes**: Blocks `%00`, `\x00`
5. **Excessive Encoding**: Limits URL-encoded characters

**Example Error Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "url"],
      "msg": "URL validation failed: URL contains suspicious pattern: javascript:",
      "input": "javascript:alert('xss')"
    }
  ]
}
```

## Custom Code Validation

### Requirements

Custom short codes must meet these requirements:

- **Length**: 4-10 characters
- **Characters**: Alphanumeric, hyphens, and underscores only (`[a-zA-Z0-9_-]`)
- **Reserved**: Cannot use reserved codes
- **Uniqueness**: Must not already exist

**Reserved Codes:**
```
api, docs, admin, health, metrics, static,
assets, favicon, robots, sitemap
```

**Valid Examples:**
```json
{
  "url": "https://example.com",
  "custom_code": "mylink"
}

{
  "url": "https://example.com",
  "custom_code": "summer-2024"
}

{
  "url": "https://example.com",
  "custom_code": "promo_123"
}
```

**Invalid Examples:**
```json
{
  "url": "https://example.com",
  "custom_code": "abc"
}
// Error: Short code must be at least 4 characters

{
  "url": "https://example.com",
  "custom_code": "my link"
}
// Error: Short code contains invalid characters

{
  "url": "https://example.com",
  "custom_code": "admin"
}
// Error: Short code 'admin' is reserved
```

## Tags Validation

Tags are optional metadata for categorizing URLs:

- **Count**: Maximum 10 tags per URL
- **Length**: Each tag must be 1-50 characters
- **Characters**: Alphanumeric, hyphens, and underscores
- **Uniqueness**: Duplicate tags (case-insensitive) are automatically removed

**Valid Examples:**
```json
{
  "url": "https://example.com",
  "tags": ["marketing", "campaign-2024", "social_media"]
}

{
  "url": "https://example.com",
  "tags": ["blog", "tech"]
}
```

**Invalid Examples:**
```json
{
  "url": "https://example.com",
  "tags": ["a" * 60]
}
// Error: Each tag must be 1-50 characters

{
  "url": "https://example.com",
  "tags": ["tag with spaces"]
}
// Error: Tags can only contain alphanumeric characters, hyphens, and underscores
```

## Pagination Validation

### List Parameters

- **limit**: 1-1000 (default: 100)
- **offset**: ≥ 0 (default: 0)
- **sort_by**: One of: `created_at`, `updated_at`, `clicks`, `short_code`
- **sort_order**: `asc` or `desc`

**Valid Examples:**
```
GET /api/v1/urls/?limit=50&offset=0&sort_by=clicks&sort_order=desc
GET /api/v1/urls/?limit=20&offset=100
GET /api/v1/urls/?sort_by=created_at
```

**Invalid Examples:**
```
GET /api/v1/urls/?limit=2000
// Error: limit must be at most 1000

GET /api/v1/urls/?offset=-1
// Error: offset must be at least 0

GET /api/v1/urls/?sort_by=invalid_field
// Error: Invalid sort_by field
```

## Bulk Operations

Bulk URL creation has additional validation:

- **Batch Size**: 1-100 URLs per request
- **Uniqueness**: No duplicate custom codes within batch
- **Individual Validation**: Each URL validated independently

**Valid Example:**
```json
{
  "urls": [
    {"url": "https://example1.com", "custom_code": "link1"},
    {"url": "https://example2.com", "custom_code": "link2"},
    {"url": "https://example3.com"}
  ]
}
```

**Invalid Example:**
```json
{
  "urls": [
    {"url": "https://example1.com", "custom_code": "duplicate"},
    {"url": "https://example2.com", "custom_code": "duplicate"}
  ]
}
// Error: Duplicate custom codes found in batch
```

## Error Response Format

### Validation Error Structure

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "custom_code"],
      "msg": "String should have at least 4 characters",
      "input": "abc",
      "ctx": {"min_length": 4}
    }
  ]
}
```

**Field Explanations:**
- `type`: Error type (e.g., `value_error`, `type_error`)
- `loc`: Location of the error in the request
- `msg`: Human-readable error message
- `input`: The invalid value provided
- `ctx`: Additional context about the error

### Multiple Validation Errors

When multiple fields are invalid, all errors are returned:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "url"],
      "msg": "URL is too long (maximum 2048 characters)",
      "input": "https://..."
    },
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "custom_code"],
      "msg": "String should match pattern '^[a-zA-Z0-9_-]+$'",
      "input": "my code"
    }
  ]
}
```

## Client-Side Validation

### Recommended Pre-Validation

Implement client-side validation to provide immediate feedback:

```javascript
function validateURL(url) {
  // Check length
  if (url.length > 2048) {
    return "URL is too long (max 2048 characters)";
  }

  // Check format
  try {
    new URL(url);
  } catch {
    return "Invalid URL format";
  }

  // Check scheme
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return "URL must use http or https";
  }

  return null; // Valid
}

function validateCustomCode(code) {
  // Check length
  if (code.length < 4) return "Must be at least 4 characters";
  if (code.length > 10) return "Must be at most 10 characters";

  // Check pattern
  if (!/^[a-zA-Z0-9_-]+$/.test(code)) {
    return "Only alphanumeric, hyphens, and underscores allowed";
  }

  // Check reserved
  const reserved = ['api', 'docs', 'admin', 'health', 'metrics'];
  if (reserved.includes(code.toLowerCase())) {
    return `'${code}' is a reserved code`;
  }

  return null; // Valid
}
```

### Form Validation Example

```html
<form id="url-form">
  <input
    type="url"
    id="url-input"
    required
    maxlength="2048"
    placeholder="https://example.com"
  />
  <input
    type="text"
    id="code-input"
    pattern="[a-zA-Z0-9_-]{4,10}"
    minlength="4"
    maxlength="10"
    placeholder="Optional custom code"
  />
  <button type="submit">Shorten</button>
</form>

<script>
document.getElementById('url-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = document.getElementById('url-input').value;
  const customCode = document.getElementById('code-input').value;

  // Validate before submitting
  const urlError = validateURL(url);
  if (urlError) {
    alert(urlError);
    return;
  }

  if (customCode) {
    const codeError = validateCustomCode(customCode);
    if (codeError) {
      alert(codeError);
      return;
    }
  }

  // Submit to API
  try {
    const response = await fetch('/api/v1/urls/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url, custom_code: customCode || undefined})
    });

    if (!response.ok) {
      const error = await response.json();
      alert(`Error: ${error.detail[0].msg}`);
      return;
    }

    const result = await response.json();
    alert(`Success! Short URL: ${result.short_url}`);
  } catch (error) {
    alert(`Network error: ${error.message}`);
  }
});
</script>
```

## Testing Validation

### Valid Request
```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "test123"}'
```

### Invalid URL
```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url"}'

# Response: 422 with validation error
```

### Invalid Custom Code
```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "ab"}'

# Response: 422 - code too short
```

## Best Practices

1. **Always validate client-side first** - Provides immediate feedback
2. **Handle 422 responses gracefully** - Display user-friendly errors
3. **Parse validation errors** - Extract field-specific messages
4. **Log validation failures** - Monitor for patterns of invalid input
5. **Test edge cases** - Verify boundary conditions

## Security Benefits

Proper validation protects against:

- **XSS Attacks**: Blocks JavaScript URLs
- **SQL Injection**: Type-safe parameters
- **Path Traversal**: Validates URL structure
- **DoS Attacks**: Limits input sizes
- **Data Corruption**: Ensures data integrity

## Related Documentation

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Rate Limiting](RATE_LIMITING.md) - API rate limiting details
- [Architecture](../architecture/ARCHITECTURE.md) - System design
