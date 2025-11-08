# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for environment configuration
ARG VITE_CREWAI_RUNNER_API_HOST=http://localhost:8000/api
ARG VITE_CREWAI_API_TOKEN=""

# Set environment variables for build
ENV VITE_CREWAI_RUNNER_API_HOST=${VITE_CREWAI_RUNNER_API_HOST}
ENV VITE_CREWAI_API_TOKEN=${VITE_CREWAI_API_TOKEN}

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Build the application
RUN pnpm build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
