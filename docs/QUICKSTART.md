# Quick Start Guide

Get your URL Shortener up and running in 5 minutes!

## Step 1: Install Prerequisites

### Install uv (Python package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or with pip:**
```bash
pip install uv
```

### Install Bun

Download from [bun.sh](https://bun.sh) (v1.0 or higher)

**macOS/Linux:**
```bash
curl -fsSL https://bun.sh/install | bash
```

**Windows:**
```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

## Step 2: Backend Setup

```bash
# Navigate to project root directory
cd url-shortner

# Install dependencies (this will create a virtual environment automatically)
uv sync --all-extras

# Copy environment file
cp .env.example .env

# Create initial database migration
make migration
# When prompted, enter: "Initial migration"

# Apply migrations
make migrate

# Start the backend server
make run
```

The backend will be running at: **http://localhost:8000**

API Documentation: **http://localhost:8000/api/v1/docs**

## Step 3: Frontend Setup (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
bun install

# Start the development server
bun run dev
```

The frontend will be running at: **http://localhost:5173**

## Step 4: Test the API

Open your browser and go to: **http://localhost:8000/api/v1/docs**

Try creating a shortened URL:

1. Click on "POST /api/v1/urls/"
2. Click "Try it out"
3. Enter this JSON:
   ```json
   {
     "url": "https://www.example.com/very/long/url/that/needs/shortening"
   }
   ```
4. Click "Execute"

You should get a response with a shortened URL!

## Using Make Commands (Backend)

For easier development, use these make commands:

```bash
# In the project root directory
make help       # Show all available commands
make dev        # Install all dependencies
make run        # Run the server
make test       # Run tests
make lint       # Lint code
make format     # Format code
make migrate    # Run migrations
make migration  # Create new migration
```

## Quick Test with curl

```bash
# Create a shortened URL
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# List all URLs
curl http://localhost:8000/api/v1/urls/

# Get URL stats (replace SHORT_CODE with actual code from create response)
curl http://localhost:8000/api/v1/urls/SHORT_CODE/stats

# Test redirect (replace SHORT_CODE with actual code)
curl -L http://localhost:8000/api/v1/urls/SHORT_CODE
```

## Troubleshooting

### Backend won't start?

1. Make sure Python 3.12+ is installed: `python --version`
2. Make sure uv is installed: `uv --version`
3. Try reinstalling dependencies: `make dev`

### Database errors?

1. Delete the database: `rm url_shortener.db`
2. Delete migrations: `rm -rf migrations/versions/*.py`
3. Recreate migration: `make migration` (enter "Initial migration" when prompted)
4. Apply migration: `make migrate`

### Frontend won't start?

1. Make sure Bun is installed: `bun --version`
2. Delete node_modules: `rm -rf node_modules`
3. Reinstall: `bun install`

## Next Steps

- Read the [main README](README.md) for detailed documentation
- Check [backend/README.md](backend/README.md) for backend-specific details
- Explore the API documentation at http://localhost:8000/api/v1/docs
- Start building your frontend to consume the API!

## Development Workflow

1. **Make changes** to your code
2. **Format code**: `make format` (in backend)
3. **Run tests**: `make test` (in backend)
4. **Check the API docs** to see your changes reflected
5. **Commit your changes**

Enjoy building with your URL Shortener! 🚀
