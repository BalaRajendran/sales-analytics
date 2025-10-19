# Dockerfile for standalone frontend development
FROM oven/bun:1-alpine

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run development server
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
