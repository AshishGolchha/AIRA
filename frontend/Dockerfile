# ==============================================================================
# AIRA Production Frontend Dockerfile
# Multi-stage build: Node.js 20 build environment -> Nginx alpine web server.
# ==============================================================================

# Stage 1: Build static assets
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies using cached package definitions
COPY package*.json ./
RUN npm ci

# Copy frontend source files and compile production bundle
COPY . .
RUN npm run build

# Stage 2: Serve production bundle with Nginx
FROM nginx:1.27-alpine AS production

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
