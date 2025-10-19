# Documentation Index

Complete documentation for the URL Shortener project.

## 📚 Documentation Structure

```
docs/
├── README.md                           # This file
├── QUICKSTART.md                       # 5-minute setup guide
├── api/
│   └── API_REFERENCE.md               # Complete API documentation
├── development/
│   ├── SETUP_GUIDE.md                 # Development environment setup
│   └── TESTING_GUIDE.md               # Testing practices and guide
├── deployment/
│   └── DEPLOYMENT_GUIDE.md            # Production deployment guide
└── architecture/
    └── ARCHITECTURE.md                # System architecture overview
```

## 🚀 Getting Started

### New to the Project?

1. **Start Here**: [QUICKSTART.md](QUICKSTART.md)
   - 5-minute setup guide
   - Get the application running locally
   - Test the API

2. **Development Setup**: [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md)
   - Detailed environment setup
   - IDE configuration
   - Development tools

3. **API Documentation**: [api/API_REFERENCE.md](api/API_REFERENCE.md)
   - Complete API reference
   - Request/response examples
   - Error handling

## 📖 Documentation by Role

### For Developers

**Getting Started:**
- [Quick Start Guide](QUICKSTART.md) - Set up in 5 minutes
- [Development Setup](development/SETUP_GUIDE.md) - Complete setup guide
- [Testing Guide](development/TESTING_GUIDE.md) - Write and run tests

**Technical Details:**
- [Architecture Overview](architecture/ARCHITECTURE.md) - System design
- [API Reference](api/API_REFERENCE.md) - API endpoints
- [Code Conventions](../.claude/conventions.md) - Coding standards

**Project Context:**
- [Project Knowledge](../.claude/project_knowledge.md) - Project overview
- [Backend README](../backend/README.md) - Backend-specific docs

### For DevOps/SRE

- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md) - Deploy to production
- [Architecture Overview](architecture/ARCHITECTURE.md) - System architecture
- [Backend README](../backend/README.md) - Configuration details

### For API Consumers

- [API Reference](api/API_REFERENCE.md) - Complete API documentation
- [Quick Start](QUICKSTART.md) - Test the API quickly
- Interactive Docs: http://localhost:8000/api/v1/docs (when running)

## 📋 Documentation by Task

### Setting Up Development Environment

1. [QUICKSTART.md](QUICKSTART.md) - Basic setup
2. [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md) - Complete setup
3. [Code Conventions](../.claude/conventions.md) - Code style guide

### Writing Code

1. [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) - Understand the system
2. [Code Conventions](../.claude/conventions.md) - Follow standards
3. [development/TESTING_GUIDE.md](development/TESTING_GUIDE.md) - Test your code

### Testing

1. [development/TESTING_GUIDE.md](development/TESTING_GUIDE.md) - Complete testing guide
2. [Backend README](../backend/README.md) - Run tests

### Deploying

1. [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) - Deploy to production
2. [Backend README](../backend/README.md) - Configuration reference

### Using the API

1. [API Reference](api/API_REFERENCE.md) - Complete API docs
2. Interactive Docs: http://localhost:8000/api/v1/docs
3. [QUICKSTART.md](QUICKSTART.md) - Quick examples

## 📑 Core Documentation Files

### [QUICKSTART.md](QUICKSTART.md)
Get started in 5 minutes. Perfect for first-time setup.

**Contents:**
- Install prerequisites
- Backend setup
- Frontend setup
- Test the API
- Troubleshooting

### [api/API_REFERENCE.md](api/API_REFERENCE.md)
Complete API documentation with examples.

**Contents:**
- All endpoints documented
- Standardized response format
- Request/response schemas
- Error handling with error codes
- Code examples (Python, JavaScript, cURL)
- Rate limiting headers
- Validation requirements

### [api/RATE_LIMITING.md](api/RATE_LIMITING.md)
Comprehensive rate limiting documentation.

**Contents:**
- Rate limit configuration
- Per-endpoint limits
- Rate limit headers
- Error responses (429 Too Many Requests)
- Client identification
- Sliding window algorithm
- Testing and troubleshooting

### [api/VALIDATION.md](api/VALIDATION.md)
Complete input validation documentation.

**Contents:**
- URL validation rules
- Custom code requirements
- Tags validation
- Security checks (XSS, path traversal)
- Error response formats
- Client-side validation examples
- Testing validation

### [api/ERROR_CODES.md](api/ERROR_CODES.md)
Complete error codes reference.

**Contents:**
- All error codes and descriptions
- HTTP status code mapping
- Error response examples
- Client-side error handling patterns
- Retry strategies
- Best practices for error handling

### [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md)
Comprehensive development environment setup.

**Contents:**
- Prerequisites
- Backend setup
- Frontend setup
- Development tools
- Database setup
- IDE configuration
- Troubleshooting

### [development/TESTING_GUIDE.md](development/TESTING_GUIDE.md)
Complete guide for writing and running tests.

**Contents:**
- Testing philosophy
- Running tests
- Writing tests
- Fixtures
- Integration tests
- Unit tests
- Mocking
- Best practices

### [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
Production deployment guide.

**Contents:**
- Pre-deployment checklist
- Environment configuration
- Database setup
- Docker deployment
- Traditional server deployment
- Cloud platform deployment
- Monitoring & logging
- Backup strategy
- Security hardening
- Scaling

### [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md)
System architecture and design decisions.

**Contents:**
- System architecture
- Backend architecture
- Design patterns
- Data flow
- Database design
- Async architecture
- API versioning
- Security considerations
- Scalability
- Technology choices

## 🔧 Project Configuration

### Claude AI Context Files

Located in `.claude/`:
- [project_knowledge.md](../.claude/project_knowledge.md) - Project overview
- [conventions.md](../.claude/conventions.md) - Code conventions

### Backend Documentation

- [backend/README.md](../backend/README.md) - Backend-specific docs
- [backend/pyproject.toml](../backend/pyproject.toml) - Dependencies

### Frontend Documentation

- [frontend/README.md](../frontend/README.md) - Frontend-specific docs
- [frontend/package.json](../frontend/package.json) - Dependencies

## 🎯 Common Tasks

### First Time Setup

```bash
# See: QUICKSTART.md for detailed steps
make dev  # Install dependencies
make migration  # Create initial migration
make migrate  # Apply migrations
make run  # Start server
```

### Running the Application

```bash
# Backend
make run

# Frontend
cd frontend && bun run dev
```

### Running Tests

```bash
# See: development/TESTING_GUIDE.md
make test
```

### Deploying

```bash
# See: deployment/DEPLOYMENT_GUIDE.md
# Docker production deployment
make prod-up
```

### API Usage

```bash
# See: api/API_REFERENCE.md
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 🔍 Finding Information

### By Technology

- **FastAPI**: [Architecture](architecture/ARCHITECTURE.md), [Setup Guide](development/SETUP_GUIDE.md)
- **SQLAlchemy**: [Architecture](architecture/ARCHITECTURE.md), [Backend README](../backend/README.md)
- **uv**: [Setup Guide](development/SETUP_GUIDE.md), [QUICKSTART](QUICKSTART.md)
- **React**: [Frontend README](../frontend/README.md)
- **Testing**: [Testing Guide](development/TESTING_GUIDE.md)
- **Deployment**: [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)

### By Feature

- **URL Shortening**: [API Reference](api/API_REFERENCE.md), [Architecture](architecture/ARCHITECTURE.md)
- **Custom Codes**: [API Reference](api/API_REFERENCE.md), [Validation](api/VALIDATION.md)
- **Click Tracking**: [Architecture](architecture/ARCHITECTURE.md)
- **Database Migrations**: [Setup Guide](development/SETUP_GUIDE.md), [Backend README](../backend/README.md)
- **Rate Limiting**: [Rate Limiting Guide](api/RATE_LIMITING.md)
- **Input Validation**: [Validation Guide](api/VALIDATION.md)

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| QUICKSTART.md | ✅ Complete | 2025-10-12 |
| API_REFERENCE.md | ✅ Complete | 2025-10-12 |
| ERROR_CODES.md | ✅ Complete | 2025-10-12 |
| RATE_LIMITING.md | ✅ Complete | 2025-10-12 |
| VALIDATION.md | ✅ Complete | 2025-10-12 |
| SETUP_GUIDE.md | ✅ Complete | 2025-10-12 |
| TESTING_GUIDE.md | ✅ Complete | 2025-10-12 |
| DEPLOYMENT_GUIDE.md | ✅ Complete | 2025-10-12 |
| ARCHITECTURE.md | ✅ Complete | 2025-10-12 |
| project_knowledge.md | ✅ Complete | 2025-10-12 |
| conventions.md | ✅ Complete | 2025-10-12 |

## 🤝 Contributing to Documentation

When adding new features or making changes:

1. **Update relevant docs** - Keep documentation in sync with code
2. **Follow the structure** - Place docs in appropriate folders
3. **Use examples** - Include code examples where helpful
4. **Keep it current** - Update "Last Updated" dates
5. **Link related docs** - Cross-reference related documentation

### Documentation Style Guide

- Use clear, concise language
- Include code examples
- Add screenshots where helpful
- Use tables for comparisons
- Include troubleshooting sections
- Link to external resources

## 📝 Document Templates

### API Endpoint Documentation

```markdown
### Endpoint Name

Description of what the endpoint does.

**Endpoint:** `METHOD /path`

**Request Body:**
\`\`\`json
{
  "field": "value"
}
\`\`\`

**Success Response (200 OK):**
\`\`\`json
{
  "result": "value"
}
\`\`\`

**Example:**
\`\`\`bash
curl -X METHOD http://localhost:8000/path
\`\`\`
```

### Feature Documentation

```markdown
# Feature Name

## Overview
Brief description of the feature.

## Usage
How to use the feature.

## Configuration
Configuration options.

## Examples
Code examples.

## Troubleshooting
Common issues and solutions.
```

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [React Documentation](https://react.dev/)
- [uv Documentation](https://github.com/astral-sh/uv)

## 💡 Need Help?

1. **Check the docs** - Most answers are here
2. **Interactive API docs** - http://localhost:8000/api/v1/docs
3. **GitHub Issues** - Report bugs or request features
4. **Review code** - Source code has inline documentation

## 📞 Support

For questions or issues:
- Check [Troubleshooting](development/SETUP_GUIDE.md#troubleshooting) sections
- Review [FAQ](QUICKSTART.md#troubleshooting) in Quick Start
- Open a GitHub Issue
- Check project README files
